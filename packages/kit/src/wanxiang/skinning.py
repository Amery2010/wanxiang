"""Bounded glTF skin/animation evaluation for diagnostic CPU acceptance.

Reads actual exported GLB, interpolates LINEAR/STEP TRS tracks, and bakes a
selected pose into a new static MeshIR. Not IK, retargeting or morph animation.
The original file, skeleton and source asset are never mutated.
"""
from __future__ import annotations
import copy
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
from .glb import read_glb, unpack
from .ir import Mesh
from .errors import WXError


def pose_glb(path, clip: str | int | None = None, time: float = 0.0):
    asset, materials, doc = read_glb(path)
    if not np.isfinite(time):
        raise WXError('INPUT_INVALID', 'Pose time must be finite')
    _, blob = unpack(path)
    # read_glb has already validated each accessor's bounds and finite content.
    def access(index):
        a = doc['accessors'][index]; v = doc['bufferViews'][a['bufferView']]
        dtype = np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'}[a['componentType']])
        n = {'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]
        offset = v.get('byteOffset',0) + a.get('byteOffset',0)
        return np.ndarray((a['count'],n), dtype=dtype, buffer=blob, offset=offset,
            strides=(v.get('byteStride',n*dtype.itemsize),dtype.itemsize)).copy().astype(float)
    # Reader preserves original node order (extra primitive children are skipped).
    ids=[]
    for i,n in enumerate(doc.get('nodes',[])):
        name=n.get('name',f'node_{i}'); ids.append(name if name not in ids else f'{name}_{i}')
    by_id={n['id']:n for n in asset.nodes}
    rest=asset.world_matrices()
    duration=0.; active=None
    if clip is not None:
        clips=doc.get('animations',[])
        if isinstance(clip,str): active=next((c for c in clips if c.get('name')==clip),None)
        elif isinstance(clip,int) and 0<=clip<len(clips): active=clips[clip]
        if active is None: raise WXError('INPUT_INVALID',f'Animation not found: {clip}')
        duration=max(float(access(s['input'])[-1,0]) for s in active['samplers'])
        # Explicit endpoint is preserved; negative and oversized times are clamped.
        t=float(np.clip(time,0,duration)); trs={}
        for ch in active['channels']:
            target=ch['target']; ni=target['node']; path_name=target['path']; sampler=active['samplers'][ch['sampler']]
            interp=sampler.get('interpolation','LINEAR')
            if interp not in ('LINEAR','STEP') or path_name not in ('translation','rotation','scale'):
                raise WXError('FORMAT_UNSUPPORTED','CPU pose supports LINEAR/STEP TRS, not cubic/morph tracks')
            times=access(sampler['input']).ravel(); values=access(sampler['output'])
            if len(times)!=len(values) or len(times)<1 or not np.all(np.diff(times)>0):
                raise WXError('VALIDATION_FAILED','Malformed animation sampler')
            if ni not in trs:
                matrix=np.asarray(by_id[ids[ni]]['matrix']); scales=np.linalg.norm(matrix[:3,:3],axis=0)
                if np.any(scales<1e-10):raise WXError('GEOMETRY_INVALID','Singular animated transform')
                trs[ni]={'translation':matrix[:3,3].copy(),'rotation':Rotation.from_matrix(matrix[:3,:3]/scales).as_quat(),'scale':scales}
            x=float(np.clip(t,times[0],times[-1])); k=max(0,min(len(times)-1,int(np.searchsorted(times,x,side='right')-1)))
            if interp=='STEP' or k==len(times)-1 or len(times)==1: val=values[k]
            elif path_name=='rotation': val=Slerp(times[k:k+2],Rotation.from_quat(values[k:k+2]))([x]).as_quat()[0]
            else: val=values[k]+(values[k+1]-values[k])*((x-times[k])/(times[k+1]-times[k]))
            trs[ni][path_name]=val
        for ni, tr in trs.items():
            matrix=np.eye(4);matrix[:3,:3]=Rotation.from_quat(tr['rotation']).as_matrix()@np.diag(tr['scale']);matrix[:3,3]=tr['translation']
            by_id[ids[ni]]['matrix']=matrix.tolist()
    posed_world=asset.world_matrices(); out=copy.deepcopy(asset); out.meshes={}; displacement=0.; skin_count=0
    for n in out.nodes:
        if not n.get('mesh'):continue
        source=asset.meshes[n['mesh']]; skin=n.pop('skin',None)
        if skin:
            skin_count+=1; joints=skin['joints']; ibm=np.asarray(skin['inverse_bind_matrices'],float)
            matrices=np.array([posed_world[j]@ibm[k] for k,j in enumerate(joints)])
            bind_matrices=np.array([rest[j]@ibm[k] for k,j in enumerate(joints)])
            blend=np.sum(matrices[source.skin_indices]*source.skin_weights[:,:,None,None],axis=1)
            bind_blend=np.sum(bind_matrices[source.skin_indices]*source.skin_weights[:,:,None,None],axis=1)
            h=np.column_stack([source.vertices,np.ones(len(source.vertices))]); p=np.einsum('nij,nj->ni',blend,h)[:,:3]
            bp=np.einsum('nij,nj->ni',bind_blend,h)[:,:3]; displacement=max(displacement,float(np.linalg.norm(p-bp,axis=1).max()))
            # Inverse-transpose of the weighted linear transform also handles
            # nonuniform scale. Singular poses fail, rather than fake normals.
            try: normal_m=np.linalg.inv(blend[:,:3,:3]).transpose(0,2,1)
            except np.linalg.LinAlgError as exc:raise WXError('GEOMETRY_INVALID','Singular skin pose') from exc
            normals=np.einsum('nij,nj->ni',normal_m,source.normals);normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
            baked=Mesh(p,source.faces.copy(),normals,source.uv.copy(),None if source.colors is None else source.colors.copy())
        else:baked=source.transformed(posed_world[n['id']])
        # Bake into world coordinates in an independent mesh; do not share a
        # buffer between instances animated by different bones.
        meshid=n['id']+'__pose';out.meshes[meshid]=baked;n['mesh']=meshid
        n['parent']=None;n['matrix']=np.eye(4).tolist()
    out.sockets=[]
    report={'source':'actual-glb','clip':active.get('name') if active else None,'time':float(time),'duration':duration,'skins':skin_count,'max_skin_displacement_m':displacement,'baked_static':True}
    return out,materials,doc,report
