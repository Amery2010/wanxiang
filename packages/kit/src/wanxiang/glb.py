"""Self-contained glTF 2.0 writer and strict uncompressed static / skinned rest-pose reader.
Reader is deliberately bounded. Unsupported compression/remote URIs fail explicitly.
"""
from __future__ import annotations
import io,json,struct,base64
from pathlib import Path
import numpy as np
from PIL import Image
from .ir import AssetIR,Mesh
from .util import atomic_bytes,write_json,canonical,inside
from .errors import WXError
from . import __version__

def export_glb(asset:AssetIR,materials:dict,path,animations=None):
    doc={'asset':{'version':'2.0','generator':f'Wanxiang3D/{__version__} (shared live geometry; no Blender)'},'scene':0,'scenes':[{'nodes':[]}],
         'nodes':[],'meshes':[],'materials':[],'accessors':[],'bufferViews':[],'buffers':[],
         'extras':{'wx':{'units':'m','up':'+Y','front':'+Z','sockets':asset.sockets,'metadata':asset.metadata}}}
    blob=bytearray();image_cache={};mesh_cache={}
    def view(data,target=None):
        while len(blob)%4:blob.append(0)
        o=len(blob);blob.extend(data);r={'buffer':0,'byteOffset':o,'byteLength':len(data)}
        if target:r['target']=target
        doc['bufferViews'].append(r);return len(doc['bufferViews'])-1
    def accessor(array,type,ctype=5126,target=None):
        dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[ctype];a=np.asarray(array,dtype=dtype)
        idx=view(a.tobytes(),target);entry={'bufferView':idx,'componentType':ctype,'count':len(a),'type':type}
        if type=='VEC3':entry.update(min=a.min(0).tolist(),max=a.max(0).tolist())
        if type=='SCALAR':entry.update(min=[float(a.min())] if ctype==5126 else [int(a.min())],max=[float(a.max())] if ctype==5126 else [int(a.max())])
        doc['accessors'].append(entry);return len(doc['accessors'])-1
    def texture(im,wrap=(10497,10497),filters=(9729,9987)):
        b=io.BytesIO();im.save(b,format='PNG');data=b.getvalue()
        import hashlib
        h=(hashlib.sha256(data).hexdigest(),wrap,filters)
        if h in image_cache:return image_cache[h]
        doc.setdefault('images',[]).append({'bufferView':view(data),'mimeType':'image/png'})
        sam={'magFilter':filters[0],'minFilter':filters[1],'wrapS':wrap[0],'wrapT':wrap[1]};samplers=doc.setdefault('samplers',[])
        if sam not in samplers:samplers.append(sam)
        doc.setdefault('textures',[]).append({'sampler':samplers.index(sam),'source':len(doc['images'])-1})
        i=len(doc['textures'])-1;image_cache[h]=i;return i
    mids={}
    for name,mat in materials.items():
        m={'name':name,'pbrMetallicRoughness':{'baseColorFactor':mat.get('baseColorFactor',[1,1,1,1]),'metallicFactor':mat.get('metallicFactor',0),'roughnessFactor':mat.get('roughnessFactor',1)},
           'alphaMode':mat.get('alphaMode','OPAQUE'),'doubleSided':mat.get('doubleSided',False),'extras':{**mat.get('extras',{}),'source':mat.get('source',{}),'placeholder':mat.get('placeholder',False),'limitations':mat.get('limitations',[])}}
        imgs=mat.get('images',{});sam=mat.get('sampler',{});wrap=tuple(33071 if sam.get(k)=='CLAMP_TO_EDGE' else 10497 for k in ('wrapS','wrapT'));filters=(sam.get('magFilter',9729),sam.get('minFilter',9987))
        if 'basecolor'in imgs:m['pbrMetallicRoughness']['baseColorTexture']={'index':texture(imgs['basecolor'],wrap,filters)}
        if 'normal'in imgs:m['normalTexture']={'index':texture(imgs['normal'],wrap,filters),'scale':mat.get('normalScale',.65)}
        if 'orm'in imgs:
            idx=texture(imgs['orm'],wrap,filters);m['pbrMetallicRoughness']['metallicRoughnessTexture']={'index':idx};m['occlusionTexture']={'index':idx,'strength':1}
        if 'emissive' in imgs:m['emissiveTexture']={'index':texture(imgs['emissive'],wrap,filters)}
        if m['alphaMode']=='MASK':m['alphaCutoff']=mat.get('alphaCutoff',.45)
        if any(mat.get('emissiveFactor',[0,0,0])):m['emissiveFactor']=mat['emissiveFactor']
        mids[name]=len(doc['materials']);doc['materials'].append(m)
    nids={n['id']:i for i,n in enumerate(asset.nodes)}
    for n in asset.nodes:
        m=np.asarray(n['matrix'],float)
        rec={'name':n['id'],'matrix':m.T.ravel().tolist(),'extras':{'wx_role':n.get('role','surface'),'wx_topology':n.get('topology','closed')}}
        for extra in ('part_id','kit_instance','joint'):
            if extra in n:rec['extras'][extra]=n[extra]
        if n.get('mesh'):
            me=asset.meshes[n['mesh']];key=(n['mesh'],n['material'])
            if key not in mesh_cache:
                attrs={'POSITION':accessor(me.vertices,'VEC3',target=34962),'NORMAL':accessor(me.normals,'VEC3',target=34962),'TEXCOORD_0':accessor(me.uv,'VEC2',target=34962)}
                if me.colors is not None:attrs['COLOR_0']=accessor(me.colors,'VEC3',target=34962)
                if me.skin_weights is not None:
                    attrs['JOINTS_0']=accessor(me.skin_indices,'VEC4',5123,34962)
                    attrs['WEIGHTS_0']=accessor(me.skin_weights,'VEC4',target=34962)
                comp=5123 if len(me.vertices)<65536 else 5125
                prim={'attributes':attrs,'indices':accessor(me.faces.ravel(),'SCALAR',comp,34963),'material':mids[n['material']],'mode':4}
                mesh_cache[key]=len(doc['meshes']);doc['meshes'].append({'name':n['mesh'],'primitives':[prim]})
            rec['mesh']=mesh_cache[key]
        doc['nodes'].append(rec)
    for n in asset.nodes:
        i=nids[n['id']]
        if n.get('parent'):doc['nodes'][nids[n['parent']]].setdefault('children',[]).append(i)
        else:doc['scenes'][0]['nodes'].append(i)
    worlds=asset.world_matrices()
    for n in asset.nodes:
        if not n.get('skin'):continue
        joints=n['skin']['joints'];me=asset.meshes[n['mesh']]
        if not joints or any(x not in nids for x in joints) or me.skin_indices is None or me.skin_indices.max()>=len(joints):raise WXError('GEOMETRY_INVALID','Invalid skeleton binding')
        # Source vertices are in mesh-local space. IBM maps that bind space to each joint.
        if 'inverse_bind_matrices' in n['skin']:
            existing=np.asarray(n['skin']['inverse_bind_matrices'],float)
            if existing.shape!=(len(joints),4,4) or not np.isfinite(existing).all():raise WXError('GEOMETRY_INVALID','Invalid inverse bind matrices')
            ibm=[matrix.T.ravel() for matrix in existing]
        else:ibm=[(np.linalg.inv(worlds[x])@worlds[n['id']]).T.ravel() for x in joints]
        skin={'name':n['id']+'_skeleton','joints':[nids[x] for x in joints],'inverseBindMatrices':accessor(ibm,'MAT4')}
        doc['nodes'][nids[n['id']]]['skin']=len(doc.setdefault('skins',[]));doc['skins'].append(skin)
    # Bone and rigid-node clips use standard glTF rotation or translation channels.
    if animations:
        from scipy.spatial.transform import Rotation
        clips={}
        for anim in animations:
            if anim['node'] not in nids:raise WXError('INPUT_INVALID','Animation targets missing node')
            node=nids[anim['node']];rec=doc['nodes'][node]
            if 'matrix' in rec:
                matrix=np.array(rec.pop('matrix')).reshape(4,4).T
                scales=np.linalg.norm(matrix[:3,:3],axis=0)
                if np.any(scales<1e-12):raise WXError('INPUT_INVALID','Singular animated transform')
                if np.linalg.det(matrix[:3,:3])<0:scales[0]*=-1
                rec.update(translation=matrix[:3,3].tolist(),rotation=Rotation.from_matrix(matrix[:3,:3]/scales).as_quat().tolist(),scale=scales.tolist())
            rotation='rotations' in anim;translation='translations' in anim
            if rotation==translation:raise WXError('INPUT_INVALID','Animation requires exactly one channel')
            times=np.asarray(anim['times'],float)
            values=np.asarray(anim['rotations'] if rotation else anim['translations'],float)
            width=4 if rotation else 3
            if times.ndim!=1 or len(times)<2 or not np.isfinite(times).all() or times[0]<0 or values.shape!=(len(times),width) or not np.isfinite(values).all() or not np.all(np.diff(times)>0):
                raise WXError('INPUT_INVALID','Malformed animation keys')
            if rotation and not np.allclose(np.linalg.norm(values,axis=1),1,atol=1e-5):raise WXError('INPUT_INVALID','Non-unit animation quaternion')
            ts=accessor(times,'SCALAR');vs=accessor(values,'VEC4' if rotation else 'VEC3')
            name=anim.get('name','motion');clip=clips.setdefault(name,{'name':name,'samplers':[],'channels':[]})
            si=len(clip['samplers']);clip['samplers'].append({'input':ts,'output':vs,'interpolation':'LINEAR'})
            clip['channels'].append({'sampler':si,'target':{'node':node,'path':'rotation' if rotation else 'translation'}})
        doc['animations']=list(clips.values())
    doc['buffers']=[{'byteLength':len(blob)}];j=canonical(doc);j+=b' '*((-len(j))%4);blob+=b'\0'*((-len(blob))%4)
    data=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(blob))+struct.pack('<II',len(j),0x4E4F534A)+j+struct.pack('<II',len(blob),0x004E4942)+blob
    atomic_bytes(path,data);return doc

def unpack(path):
    p=Path(path)
    if p.stat().st_size>512_000_000:raise WXError('BUDGET_EXCEEDED','Model exceeds 512MB')
    data=p.read_bytes()
    if data[:4]!=b'glTF':raise WXError('FORMAT_UNSUPPORTED','Reader requires a GLB 2.0 file')
    if len(data)<20:raise WXError('VALIDATION_FAILED','Truncated GLB')
    magic,version,length=struct.unpack_from('<4sII',data)
    if version!=2 or length!=len(data):raise WXError('VALIDATION_FAILED','Invalid GLB header or length')
    chunks={};offset=12
    while offset<len(data):
        if offset+8>len(data):raise WXError('VALIDATION_FAILED','Truncated chunk header')
        size,kind=struct.unpack_from('<II',data,offset);offset+=8
        if size%4 or offset+size>len(data):raise WXError('VALIDATION_FAILED','Bad GLB chunk bounds/alignment')
        if kind in chunks:raise WXError('VALIDATION_FAILED','Duplicate GLB chunk')
        chunks[kind]=data[offset:offset+size];offset+=size
    try:doc=json.loads(chunks[0x4E4F534A]);blob=chunks.get(0x004E4942,b'')
    except Exception as e:raise WXError('VALIDATION_FAILED',f'Invalid GLB JSON: {e}')
    return doc,blob

def read_glb(path):
    doc,blob=unpack(path)
    if doc.get('asset',{}).get('version')!='2.0':raise WXError('FORMAT_UNSUPPORTED','Unsupported glTF version')
    if doc.get('extensionsRequired'):raise WXError('FORMAT_UNSUPPORTED','Strict CPU reader does not support required extensions',details={'extensions':doc['extensionsRequired']})
    for buf in doc.get('buffers',[]):
        if 'uri'in buf:raise WXError('FORMAT_UNSUPPORTED','External buffers are disabled')
        if buf.get('byteLength',0)>len(blob):raise WXError('VALIDATION_FAILED','Buffer exceeds BIN chunk')
    if len(doc.get('accessors',[]))>200000:raise WXError('BUDGET_EXCEEDED','Too many accessors')
    for view in doc.get('bufferViews',[]):
        if view.get('buffer',0)!=0 or view.get('byteOffset',0)<0 or view.get('byteLength',0)<0 or view.get('byteOffset',0)+view['byteLength']>len(blob):raise WXError('VALIDATION_FAILED','Invalid bufferView')
    def access(index):
        try:
            a=doc['accessors'][index]
            if 'sparse'in a:raise WXError('FORMAT_UNSUPPORTED','Sparse accessor not supported by CPU reader')
            v=doc['bufferViews'][a['bufferView']];ct=a['componentType'];dtype=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'}[ct]);cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
            count=a['count'];stride=v.get('byteStride',cols*dtype.itemsize);start=v.get('byteOffset',0)+a.get('byteOffset',0)
            end=a.get('byteOffset',0)+(count-1)*stride+cols*dtype.itemsize
            if count<=0 or count>5_000_000 or end>v['byteLength'] or stride<cols*dtype.itemsize:raise WXError('VALIDATION_FAILED','Accessor range invalid')
            arr=np.ndarray((count,cols),dtype=dtype,buffer=blob,offset=start,strides=(stride,dtype.itemsize)).copy()
            if a.get('normalized') and ct!=5126:arr=np.maximum(arr.astype(float)/np.iinfo(dtype).max,-1)
            if not np.isfinite(arr).all():raise WXError('GEOMETRY_INVALID','Accessor contains non-finite values')
            return arr[:,0] if cols==1 else arr
        except WXError:raise
        except Exception as e:raise WXError('VALIDATION_FAILED',f'Invalid accessor {index}: {e}') from e
    for i in range(len(doc.get('accessors',[]))):access(i)
    images=[]
    for im in doc.get('images',[]):
        if 'uri'in im:raise WXError('FORMAT_UNSUPPORTED','Remote or external images are disabled in strict reader')
        v=doc['bufferViews'][im['bufferView']];o=v.get('byteOffset',0)
        try:
            with Image.open(io.BytesIO(blob[o:o+v['byteLength']])) as src:
                if src.width*src.height>16_777_216:raise WXError('BUDGET_EXCEEDED','Texture dimensions exceed limit')
                src.load();images.append(src.copy())
        except WXError:raise
        except Exception as e:raise WXError('VALIDATION_FAILED',f'Corrupt embedded image: {e}')
    mats={};matnames=[]
    def texture(ref):return images[doc['textures'][ref['index']]['source']]
    for i,m in enumerate(doc.get('materials',[])):
        name=m.get('name',f'material_{i}')
        if name in mats:name=f'{name}_{i}'
        p=m.get('pbrMetallicRoughness',{});imgs={}
        if 'baseColorTexture'in p:imgs['basecolor']=texture(p['baseColorTexture'])
        if 'metallicRoughnessTexture'in p:imgs['orm']=texture(p['metallicRoughnessTexture'])
        if 'normalTexture'in m:imgs['normal']=texture(m['normalTexture'])
        if 'emissiveTexture'in m:imgs['emissive']=texture(m['emissiveTexture'])
        ref=p.get('baseColorTexture',{});ss=doc.get('samplers',[]);tx=doc.get('textures',[]);sam=ss[tx[ref['index']]['sampler']] if 'index'in ref and 'sampler'in tx[ref['index']] else {}
        mats[name]={**m,'sampler':{**{k:'CLAMP_TO_EDGE' if sam.get(k)==33071 else 'REPEAT' for k in ('wrapS','wrapT')},'magFilter':sam.get('magFilter',9729),'minFilter':sam.get('minFilter',9987)},'baseColorFactor':p.get('baseColorFactor',[1,1,1,1]),'roughnessFactor':p.get('roughnessFactor',1),'metallicFactor':p.get('metallicFactor',1),'images':imgs};matnames.append(name)
    if not matnames:mats['default']={'images':{},'baseColorFactor':[.7,.7,.7,1]};matnames=['default']
    asset=AssetIR();wx=doc.get('extras',{}).get('wx',{});asset.sockets=wx.get('sockets',[]);asset.metadata=wx.get('metadata',{})
    parents={};nodes=doc.get('nodes',[]);ids=[]
    for i,n in enumerate(nodes):
        name=n.get('name',f'node_{i}');ids.append(name if name not in ids else f'{name}_{i}')
        for c in n.get('children',[]):
            if c in parents or not 0<=c<len(nodes):raise WXError('VALIDATION_FAILED','Invalid scene parent relationship')
            parents[c]=i
    for i,n in enumerate(nodes):
        if 'matrix'in n:m=np.array(n['matrix']).reshape(4,4).T
        else:
            from scipy.spatial.transform import Rotation
            m=np.eye(4);m[:3,:3]=Rotation.from_quat(n.get('rotation',[0,0,0,1])).as_matrix()@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0])
        id=ids[i];parent=ids[parents[i]] if i in parents else None;extra=n.get('extras',{});asset.group(id,parent,matrix=m,role=extra.get('wx_role','surface'))
        for k in ('part_id','kit_instance','joint'):
            if k in extra:asset.nodes[-1][k]=extra[k]
        if 'mesh'not in n:continue
        for j,prim in enumerate(doc['meshes'][n['mesh']]['primitives']):
            if prim.get('mode',4)!=4 or prim.get('targets'):raise WXError('FORMAT_UNSUPPORTED','Only static triangle primitives supported')
            if prim.get('extensions'):raise WXError('FORMAT_UNSUPPORTED','Primitive extensions require a registered reader')
            a=prim['attributes'];v=access(a['POSITION']);idx=access(prim['indices']) if 'indices'in prim else np.arange(len(v))
            if len(idx)%3:raise WXError('VALIDATION_FAILED','Triangle index length is not divisible by 3')
            mesh=Mesh(v,idx.reshape(-1,3),access(a['NORMAL']) if 'NORMAL'in a else None,access(a['TEXCOORD_0']) if 'TEXCOORD_0'in a else None,access(a['COLOR_0'])[:,:3] if 'COLOR_0' in a else None,access(a['JOINTS_0']) if 'JOINTS_0' in a else None,access(a['WEIGHTS_0']) if 'WEIGHTS_0' in a else None)
            material=matnames[prim.get('material',0)]
            if j==0:asset.nodes[-1].update(mesh=id,material=material,topology=extra.get('wx_topology','unspecified'));asset.meshes[id]=mesh
            else:asset.add(f'{id}_primitive_{j}',mesh,material,parent=id,topology='unspecified')
    for i,n in enumerate(nodes):
        if 'skin' not in n:continue
        if not isinstance(n['skin'],int) or not 0<=n['skin']<len(doc.get('skins',[])):raise WXError('VALIDATION_FAILED','Invalid skin reference')
        skin=doc['skins'][n['skin']];joints=skin.get('joints',[])
        if not joints or len(joints)>256 or len(set(joints))!=len(joints) or any(not isinstance(j,int) or not 0<=j<len(ids) for j in joints):raise WXError('VALIDATION_FAILED','Invalid skin joints')
        matrices=access(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1) if 'inverseBindMatrices' in skin else np.repeat(np.eye(4)[None],len(joints),axis=0)
        if len(matrices)!=len(joints):raise WXError('VALIDATION_FAILED','Inverse bind count mismatch')
        for rec in asset.nodes:
            if rec['id']==ids[i] or rec.get('parent')==ids[i] and rec['id'].startswith(ids[i]+'_primitive_'):
                if 'mesh' not in rec:continue
                me=asset.meshes[rec['mesh']]
                if me.skin_weights is None or me.skin_indices.max()>=len(joints):raise WXError('VALIDATION_FAILED','Missing/invalid skin attributes')
                rec['skin']={'joints':[ids[j] for j in joints],'inverse_bind_matrices':matrices.tolist()}
    asset.world_matrices();return asset,mats,doc

def export_gltf(glb_path,out):
    """Lossless container split: glTF JSON + a self-contained binary buffer."""
    doc,blob=unpack(glb_path);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    doc['buffers'][0]['uri']='asset.bin';atomic_bytes(out/'asset.bin',blob);write_json(out/'asset.gltf',doc)
    return [out/'asset.gltf',out/'asset.bin']
