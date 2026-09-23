"""Offline procedural PBR and an explicit, resumable host-image handshake."""
from __future__ import annotations
import io, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter, distance_transform_edt
from .util import ROOT, digest, rng_for, write_json, read_json, safe_id, atomic_bytes, sha256
from .errors import WXError

DEFINITIONS = {
 'bark': ('纵裂树皮','organic',[99,70,44],.91,0),
 'birch':('白桦树皮','organic',[207,202,175],.88,0),
 'wood':('切削木材','wood',[157,105,57],.76,0),
 'darkwood':('深色旧木','wood',[79,56,37],.9,0),
 'leaf':('阔叶叶片','leaf',[80,126,46],.72,0),
 'needle':('针叶绿','leaf',[64,111,61],.83,0),
 'palm':('棕榈叶','leaf',[66,112,52],.7,0),
 'stone':('风化岩石','stone',[131,128,115],.94,0),
 'sandstone':('层状砂岩','stone',[174,134,91],.91,0),
 'slate':('深灰板岩','stone',[76,86,91],.88,0),
 'brick':('烧制砖墙','brick',[146,76,51],.9,0),
 'plaster':('石灰抹面','stone',[210,200,173],.89,0),
 'roof':('陶制屋瓦','brick',[120,62,43],.85,0),
 'metal':('裸露钢材','metal',[130,145,151],.37,1),
 'paint':('橄榄防护漆','paint',[91,108,79],.62,0),
 'navy':('海军蓝涂层','paint',[49,76,87],.58,0),
 'copper':('铜合金','metal',[168,105,53],.4,1),
 'rubber':('磨损橡胶','rubber',[30,34,36],.89,0),
 'concrete':('水泥混凝土','stone',[151,152,139],.96,0),
 'soil':('森林土壤','stone',[89,78,49],.98,0),
 'grass':('草地基底','organic',[101,121,58],.96,0),
 'sand':('干燥砂地','stone',[189,165,114],.98,0),
 'water':('不透明浅水近似','water',[57,120,127],.21,0),
 'light':('灯罩发光表面','light',[249,202,111],.3,0),
}
STYLES={
 'lowpoly':{'name':'清爽低面数','saturation':1.,'brightness':1.,'bevel':0.,'detail':.45},
 'rounded':{'name':'圆滑卡通','saturation':1.,'brightness':1.,'bevel':2.,'detail':.6},
 'natural': {'name':'自然沙盘','saturation':.9,'brightness':1.0,'bevel':1.,'detail':1.},
 'storybook':{'name':'柔和绘本','saturation':1.14,'brightness':1.12,'bevel':1.8,'detail':.82},
 'industrial':{'name':'工业旧化','saturation':.72,'brightness':.91,'bevel':.75,'detail':1.1},
}

def _png(image):
    b=io.BytesIO();image.save(b,format='PNG',optimize=False);return b.getvalue()

def normal_from_height(height,strength=1.8):
    h=np.asarray(height,float);gx=(np.roll(h,-1,axis=1)-np.roll(h,1,axis=1))*strength;gy=(np.roll(h,-1,axis=0)-np.roll(h,1,axis=0))*strength
    n=np.stack([-gx,gy,np.ones_like(h)],axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
    return np.clip((n*.5+.5)*255,0,255).astype(np.uint8)

def procedural(id,size=256,seed=7):
    """Retired: noise-generated PBR must never quietly reappear in the active library."""
    raise WXError('MATERIAL_RETIRED','Procedural noise textures were removed in v1.2. Use a registered palette or ingest a real source image.')


LEGACY_ALIASES = {k:('mat.'+{'bark':'wood','birch':'wood','darkwood':'wood','needle':'leaf','palm':'leaf','sandstone':'stone','slate':'stone','brick':'stone','roof':'paint','navy':'paint','copper':'metal','concrete':'stone','soil':'stone','grass':'leaf','sand':'stone'}.get(k,k)) for k in DEFINITIONS}

def ensure_material(id,folder=None,size=256):
    """Resolve old semantic IDs to vetted art or palette. Never resurrect retired textures."""
    base=Path(folder or ROOT/'library/materials')
    if id.startswith('mat.') and id.endswith(('--toon','--voxel')):
        raw,derived=id.rsplit('--',1);record,source_folder=ensure_material(raw,folder,size);record=dict(record)
        record['id']=id;record['extras']={**record.get('extras',{}),'wxStyle':derived,'derived_from':raw}
        if derived=='voxel':
            texture,pixel_folder=ensure_material('mat.voxel_chart',folder,size)
            record.update(channels=texture['channels'],sampler=texture['sampler'],roughnessFactor=1.,metallicFactor=0.,kind='stylized',alphaMode='OPAQUE',baseColorFactor=[1,1,1,1]);source_folder=pixel_folder
        return record,source_folder
    target=LEGACY_ALIASES.get(id,id);path=base/safe_id(target)
    if not (path/'material.json').is_file():
        # A scratch workspace may use the curated, read-only shipped library.
        path=ROOT/'library/materials'/safe_id(target)
    if not (path/'material.json').is_file():raise WXError('INPUT_INVALID',f'Material not registered: {id}')
    return read_json(path/'material.json'),path

def load_material(id,workspace=None,style='natural'):
    if style not in STYLES:raise WXError('RECIPE_INVALID',f'Unknown style {style}')
    custom=Path(workspace)/'materials'/id if workspace else None
    if custom and (custom/'material.json').is_file():record=read_json(custom/'material.json');folder=custom
    else:record,folder=ensure_material(id)
    out=dict(record);out['images']={}
    from .util import inside
    for k,c in record['channels'].items():
        path=inside(folder,c['file'])
        if sha256(path)!=c['sha256']:raise WXError('VALIDATION_FAILED',f'Texture hash mismatch: {id}/{k}')
        if k in ('basecolor','normal','orm','emissive'):out['images'][k]=Image.open(path).copy()
    if style!='natural' and 'basecolor' in out['images']:
        image=out['images']['basecolor'];a=np.asarray(image).copy();rgb=a[:,:,:3].astype(float);gray=rgb.mean(2,keepdims=True)
        s=STYLES[style];a[:,:,:3]=np.clip((gray+(rgb-gray)*s['saturation'])*s['brightness'],0,255).astype(np.uint8);out['images']['basecolor']=Image.fromarray(a)
    return out

def request_material(workspace,id,prompt,semantic='stone',size=1024):
    safe_id(id)
    if type(size) is not int or not 32<=size<=2048 or not isinstance(prompt,str) or not prompt.strip() or len(prompt)>20000:raise WXError('INPUT_INVALID','Material requests require non-empty prompt <=20000 chars and size 32..2048')
    if semantic not in DEFINITIONS:raise WXError('INPUT_INVALID','Unknown material semantic')
    p=Path(workspace)/'host_requests'/f'{id}.json'
    req={'schema':'wx.host-material/1.0','id':id,'status':'waiting_host','semantic':semantic,'size':size,'prompt':prompt,
      'requirements':{'view':'flat surface only','lighting':'diffuse, no cast shadows, no highlights','seamless':True,'channels_requested':['basecolor'],'maximum_generated_pixels':1573352},
      'host_action':{'tool':'image_generation','method':'host invocation, not callable from this CLI'},'receipt':None}
    req['request_hash']=digest({k:v for k,v in req.items() if k not in ('status','receipt')})
    if p.exists():
        old=read_json(p)
        if old['request_hash']!=req['request_hash']:raise WXError('INPUT_INVALID','Request ID already exists with different content; use a new ID')
        return old,p
    write_json(p,req);return req,p

def inspect_texture(image):
    im=np.asarray(image.convert('RGBA'),float)/255
    return {'width':image.width,'height':image.height,'has_alpha':bool(np.any(im[:,:,3]<1)),
      'opaque_fraction':float(np.mean(im[:,:,3]>.5)),
      'edge_difference_lr':float(np.mean(np.abs(im[:,0,:3]-im[:,-1,:3]))),
      'edge_difference_tb':float(np.mean(np.abs(im[0,:,:3]-im[-1,:,:3]))),
      'note':'Edge statistics do not prove semantic tiling or correct albedo lighting.'}

def ingest(workspace,id,image_path,source='user_provided',make_seamless=False):
    safe_id(id);w=Path(workspace);reqpath=w/'host_requests'/f'{id}.json'
    if not reqpath.exists():raise WXError('INPUT_INVALID','Create a material request first')
    req=read_json(reqpath);p=Path(image_path)
    if not p.is_file():raise WXError('HOST_ASSET_MISSING','A readable image file is required')
    if p.stat().st_size>64_000_000:raise WXError('BUDGET_EXCEEDED','Image exceeds 64MB')
    try:
        with Image.open(p) as img:
            if img.width*img.height>16_777_216:raise WXError('BUDGET_EXCEEDED','Image exceeds 16 megapixels')
            img.load();im=img.convert('RGBA' if 'A'in img.getbands() else 'RGB')
    except WXError:raise
    except Exception as e:raise WXError('INPUT_INVALID',f'Cannot decode image: {e}')
    original_sha=sha256(p)
    if req.get('receipt'):
        if req['receipt']['source_sha256']!=original_sha:raise WXError('INPUT_INVALID','Request already fulfilled by different bytes')
        return req
    dest=w/'materials'/id;dest.mkdir(parents=True,exist_ok=True)
    atomic_bytes(dest/f'source{p.suffix.lower()}',p.read_bytes())
    size=min(int(req.get('size',1024)),2048);im=im.resize((size,size),Image.Resampling.LANCZOS)
    if make_seamless:
        arr=np.array(im).astype(float);band=max(2,size//32)
        # Periodic boundary adjustment only; report its limits explicitly.
        for i in range(band):
            a=(band-i)/band*.5;l=arr[:,i].copy();r=arr[:,-1-i].copy();arr[:,i]=(1-a)*l+a*r;arr[:,-1-i]=a*l+(1-a)*r
            t=arr[i].copy();b=arr[-1-i].copy();arr[i]=(1-a)*t+a*b;arr[-1-i]=a*t+(1-a)*b
        im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8))
    if im.mode=='RGBA':
        arr=np.array(im);mask=arr[:,:,3]==0
        if mask.any() and (~mask).any():
            _,inds=distance_transform_edt(mask,return_indices=True);arr[mask,:3]=arr[inds[0][mask],inds[1][mask],:3];im=Image.fromarray(arr)
    images={'basecolor':im}  # Only the real supplied image; never fabricate normal/ORM/height.
    for k,img in images.items():atomic_bytes(dest/f'{k}.png',_png(img))
    rec=load_material(req['semantic']);rec.pop('images');rec.update(id=id,name=f'宿主素材 · {id}',resolution=[size,size],source={'type':source,'sha256':original_sha,'request_hash':req['request_hash']},
      alphaMode='MASK' if im.mode=='RGBA' else 'OPAQUE',doubleSided=im.mode=='RGBA',baseColorFactor=[1,1,1,1],normalScale=0.)
    rec['channels']={k:{'file':f'{k}.png','sha256':sha256(dest/f'{k}.png'),'colorspace':'sRGB' if k=='basecolor' else 'linear'} for k in images}
    rec['limitations']=['Base color ingested from real source bytes; roughness/metallic are authored scalar parameters.','No normal, ORM or height reconstructed from color. No AO bake.']
    rec['texture_check']=inspect_texture(im);write_json(dest/'material.json',rec)
    req.update(status='ready',receipt={'source_sha256':original_sha,'material_id':id,'source_type':source});write_json(reqpath,req);return req

def atlas(paths,out,padding=8,size=1024):
    """Uniform atlas with edge dilation. Preserves alpha; returns normalized UV rectangles."""
    if not paths or len(paths)>256:raise WXError('INPUT_INVALID','Atlas accepts 1..256 images')
    cols=math.ceil(math.sqrt(len(paths)));rows=math.ceil(len(paths)/cols);cell=size//max(cols,rows)
    if cell<=padding*2:raise WXError('BUDGET_EXCEEDED','Atlas padding leaves no image area')
    canvas=Image.new('RGBA',(size,size));rects=[]
    for i,path in enumerate(paths):
        im=Image.open(path).convert('RGBA');im.thumbnail((cell-2*padding,cell-2*padding),Image.Resampling.LANCZOS)
        x=i%cols*cell+padding;y=i//cols*cell+padding
        padded=np.pad(np.array(im),((padding,padding),(padding,padding),(0,0)),mode='edge');canvas.paste(Image.fromarray(padded),(x-padding,y-padding))
        rects.append({'source':str(path),'xywh':[x,y,im.width,im.height],'uv':[x/size,y/size,im.width/size,im.height/size]})
    atomic_bytes(out,_png(canvas));write_json(str(out)+'.json',{'size':size,'padding':padding,'rects':rects});return rects
