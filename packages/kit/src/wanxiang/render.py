"""Orthographic CPU rasterizer with a true depth buffer and alpha-tested textures.
Rendering inputs ALWAYS come from the exported GLB reader. This is diagnostic
Lambert/hemisphere shading, not a claim of path-traced or WebGL PBR acceptance.
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .glb import read_glb
from .util import atomic_bytes,write_json
try:
    from numba import njit
except ImportError:
    def njit(*args,**kwargs):
        def dec(fn):return fn
        return dec

@njit(cache=True)
def raster(screen,world_normals,uv,colors,faces,matids,textures,factors,emissive,cutoffs,wraps,width,height,wire=False):
    image=np.zeros((height,width,4),np.uint8);depth=np.full((height,width),-1e30,np.float32)
    l1=np.array([.48,.76,.45]);l1=l1/np.sqrt((l1*l1).sum());l2=np.array([-.65,.25,-.55]);l2=l2/np.sqrt((l2*l2).sum())
    for fidx in range(len(faces)):
        i0,i1,i2=faces[fidx];p0,p1,p2=screen[i0],screen[i1],screen[i2]
        minx=max(0,int(math.floor(min(p0[0],p1[0],p2[0]))));maxx=min(width-1,int(math.ceil(max(p0[0],p1[0],p2[0]))))
        miny=max(0,int(math.floor(min(p0[1],p1[1],p2[1]))));maxy=min(height-1,int(math.ceil(max(p0[1],p1[1],p2[1]))))
        area=(p1[1]-p2[1])*(p0[0]-p2[0])+(p2[0]-p1[0])*(p0[1]-p2[1])
        if abs(area)<1e-8:continue
        mi=matids[fidx];size=textures.shape[1]
        for y in range(miny,maxy+1):
            for x in range(minx,maxx+1):
                a=((p1[1]-p2[1])*(x+.5-p2[0])+(p2[0]-p1[0])*(y+.5-p2[1]))/area
                b=((p2[1]-p0[1])*(x+.5-p2[0])+(p0[0]-p2[0])*(y+.5-p2[1]))/area;c=1-a-b
                if a<0 or b<0 or c<0:continue
                z=a*p0[2]+b*p1[2]+c*p2[2]
                if z<=depth[y,x]+1e-7:continue
                u=a*uv[i0,0]+b*uv[i1,0]+c*uv[i2,0];v=a*uv[i0,1]+b*uv[i1,1]+c*uv[i2,1]
                u=min(1,max(0,u)) if wraps[mi,0] else u-math.floor(u);v=min(1,max(0,v)) if wraps[mi,1] else v-math.floor(v)
                tx=int(u*(size-1));ty=int(v*(size-1));tex=textures[mi,ty,tx]
                alpha=tex[3]/255*factors[mi,3]
                if alpha<cutoffs[mi]:continue
                nx=a*world_normals[i0,0]+b*world_normals[i1,0]+c*world_normals[i2,0]
                ny=a*world_normals[i0,1]+b*world_normals[i1,1]+c*world_normals[i2,1]
                nz=a*world_normals[i0,2]+b*world_normals[i1,2]+c*world_normals[i2,2]
                length=math.sqrt(nx*nx+ny*ny+nz*nz)+1e-10;nx/=length;ny/=length;nz/=length
                shade=.28+.15*(ny*.5+.5)+.65*max(0,nx*l1[0]+ny*l1[1]+nz*l1[2])+.17*max(0,nx*l2[0]+ny*l2[1]+nz*l2[2])
                previous0=int(image[y,x,0]);previous1=int(image[y,x,1]);previous2=int(image[y,x,2]);previous_a=image[y,x,3]/255.0
                if wire and min(a,b,c)<.045:
                    image[y,x,0]=102;image[y,x,1]=210;image[y,x,2]=187
                else:
                    for k in range(3):
                        # Linear-light diffuse computation, sRGB display transfer.
                        vc=a*colors[i0,k]+b*colors[i1,k]+c*colors[i2,k]
                        val=(tex[k]/255)**2.2*factors[mi,k]*vc*shade+emissive[mi,k]*.14
                        image[y,x,k]=int(min(255,max(0,val**(1/2.2)*255)))
                if alpha>=.995:
                    image[y,x,3]=255;depth[y,x]=z
                else:
                    out_a=alpha+previous_a*(1-alpha)
                    for k in range(3):
                        previous=previous0 if k==0 else previous1 if k==1 else previous2
                        image[y,x,k]=int((image[y,x,k]*alpha+previous*previous_a*(1-alpha))/max(out_a,1e-8))
                    image[y,x,3]=int(out_a*255)
    return image

def prepare(path,tex_size=192,*,clip=None,time=0.0):
    from .skinning import pose_glb
    a,mats,doc,pose_report=pose_glb(path,clip,time);vs=[];ns=[];uv=[];colors=[];faces=[];matids=[];offset=0;matnames=list(mats);matindex={id:i for i,id in enumerate(matnames)};world=a.world_matrices()
    for node in a.nodes:
        if not node.get('mesh'):continue
        m=a.meshes[node['mesh']].transformed(world[node['id']]);vs.append(m.vertices);ns.append(m.normals);uv.append(m.uv);colors.append(m.colors if m.colors is not None else np.ones_like(m.vertices));faces.append(m.faces+offset);matids.extend([matindex[node['material']]]*len(m.faces));offset+=len(m.vertices)
    textures=[];factors=[];em=[];cut=[];wraps=[]
    for name in matnames:
        mat=mats[name];wraps.append([mat.get('sampler',{}).get(k)=='CLAMP_TO_EDGE' for k in ('wrapS','wrapT')]);im=mat.get('images',{}).get('basecolor',Image.new('RGBA',(1,1),(255,255,255,255)))
        textures.append(np.asarray(im.convert('RGBA').resize((tex_size,tex_size),Image.Resampling.BILINEAR)));factors.append(mat.get('baseColorFactor',[1,1,1,1]));em.append(mat.get('emissiveFactor',[0,0,0]));cut.append(mat.get('alphaCutoff',.45) if mat.get('alphaMode')=='MASK' else .001)
    return {'vertices':np.vstack(vs),'normals':np.vstack(ns),'uv':np.vstack(uv),'colors':np.vstack(colors),'faces':np.vstack(faces).astype(np.int32),'matids':np.array(matids,np.int32),'textures':np.array(textures),'factors':np.array(factors,np.float32),'emissive':np.array(em,np.float32),'cutoffs':np.array(cut,np.float32),'wraps':np.array(wraps,np.bool_),'asset':a,'pose':pose_report}

def camera_basis(azimuth,elevation):
    a=math.radians(azimuth);e=math.radians(elevation);d=np.array([math.sin(a)*math.cos(e),math.sin(e),math.cos(a)*math.cos(e)])
    right=np.array([math.cos(a),0,-math.sin(a)]);up=np.cross(d,right);return np.column_stack([right,up,d])

def render_prepared(data,size=512,azimuth=40,elevation=25,*,fixed_scale=None,target=None,wire=False,antialias=1):
    v=data['vertices'];lo=v.min(0);hi=v.max(0);target=np.asarray(target if target is not None else (lo+hi)/2)
    basis=camera_basis(azimuth,elevation);view=(v-target)@basis
    if fixed_scale:
        span=float(fixed_scale)
    else:
        mid=(view[:,:2].min(0)+view[:,:2].max(0))/2
        target=target+basis[:,0]*mid[0]+basis[:,1]*mid[1]
        view=(v-target)@basis
        span=max(float(np.ptp(view[:,:2],axis=0).max())*1.16,.025)
    s=size*antialias
    screen=np.empty_like(view);screen[:,0]=view[:,0]/span*s+s/2;screen[:,1]=-view[:,1]/span*s+s/2;screen[:,2]=view[:,2]
    faces=data['faces'];matids=data['matids']
    blend=data['factors'][matids,3]<.995
    if np.any(blend):
        opaque_ids=np.flatnonzero(~blend);transparent_ids=np.flatnonzero(blend)
        depth_order=np.mean(view[faces[transparent_ids],2],axis=1)
        order=np.concatenate([opaque_ids,transparent_ids[np.argsort(depth_order,kind='stable')]])
        faces=faces[order];matids=matids[order]
    image=raster(screen.astype(np.float32),data['normals'].astype(np.float32),data['uv'].astype(np.float32),data['colors'].astype(np.float32),faces,matids,data['textures'],data['factors'],data['emissive'],data['cutoffs'],data['wraps'],s,s,wire)
    im=Image.fromarray(image)
    if antialias>1:im=im.resize((size,size),Image.Resampling.LANCZOS)
    # Project semantic origin; does NOT use minimum visible pixel as a substitute.
    anchor=(np.array([0,0,0])-target)@camera_basis(azimuth,elevation)
    return im,{'azimuth':azimuth,'elevation':elevation,'world_span':float(span),'target':target.tolist(),'anchor_px':[float(anchor[0]/span*size+size/2),float(-anchor[1]/span*size+size/2)],'alpha_bounds':im.getbbox(),'renderer':'cpu_textured_lambert_alpha_v37','limitations':['No normal-map, IBL, shadow-map or transmission evaluation.']}

def render_cpu(path,out,size=512,azimuth=40,elevation=25,wire=False):
    data=prepare(path);im,meta=render_prepared(data,size,azimuth,elevation,wire=wire,antialias=2 if size<=512 else 1);Path(out).parent.mkdir(parents=True,exist_ok=True);im.save(out);write_json(str(out)+'.json',meta);return meta

def multi_view(path,folder,size=360):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);data=prepare(path);views=[]
    for i,angle in enumerate([40,130,220,310]):
        im,meta=render_prepared(data,size,angle,25,antialias=1);file=folder/f'view_{i}.png';im.save(file);meta['file']=file.name;views.append(meta)
    hero,meta=render_prepared(data,640,40,25);hero.save(folder/'hero.png')
    sheet=Image.new('RGB',(size*2,size*2+48),(24,31,34));draw=ImageDraw.Draw(sheet)
    for i in range(4):
        im=Image.open(folder/f'view_{i}.png');sheet.paste(im,((i%2)*size,(i//2)*size),im)
    draw.text((16,size*2+14),'CPU / EXPORTED GLB / TEXTURED DIAGNOSTIC',fill=(176,197,194));sheet.save(folder/'contact_sheet.png')
    write_json(folder/'views.json',{'renderer':'cpu_textured_lambert_alpha_v37','from_actual_glb':True,'views':views,'hero':meta});return views

def turntable(path,folder,frames=32,size=192,elevation=30):
    if frames not in [4,8,16,32,64]:raise ValueError('frames must be 4, 8, 16, 32 or 64')
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);data=prepare(path);v=data['vertices'];target=(v.min(0)+v.max(0))/2;span=np.linalg.norm(np.ptp(v,axis=0))*1.06
    cols=8 if frames>=8 else 4;rows=math.ceil(frames/cols);atlas=Image.new('RGBA',(cols*size,rows*size));records=[]
    for i in range(frames):
        angle=i*360/frames;im,meta=render_prepared(data,size,angle,elevation,target=target,fixed_scale=span)
        name=f'frame_{i:02}.png';im.save(folder/name);atlas.paste(im,((i%cols)*size,(i//cols)*size));meta.update(file=name,rect=[i%cols*size,i//cols*size,size,size]);records.append(meta)
    atlas.save(folder/'atlas.png');write_json(folder/'atlas.json',{'renderer':'cpu_textured_lambert_alpha_v37','camera':'fixed orthographic, actual 3D orbit','columns':cols,'rows':rows,'frames':records,'pivot':'projected semantic origin','production_approved':False});return records
