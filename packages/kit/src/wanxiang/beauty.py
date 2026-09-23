"""Deterministic presentation renderer for the shipped opaque, vertex-coloured kits.
Uses the actual exported GLB; orthographic CPU rasterization, PCF shadow mapping,
and a display-only ground plane. Not Blender/Cycles, path tracing or GPU PBR.
The ground / lights are never inserted into the exported model.
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from PIL import Image
from numba import njit
from .render import prepare,camera_basis

@njit(cache=True)
def shadow_buffer(v,f,basis,center,span,res):
    p=(v-center)@basis
    out=np.full((res,res),-1e20,np.float32)
    for k in range(len(f)):
        a,b,c=f[k];x0=p[a,0]/span*res+res*.5;y0=-p[a,1]/span*res+res*.5;x1=p[b,0]/span*res+res*.5;y1=-p[b,1]/span*res+res*.5;x2=p[c,0]/span*res+res*.5;y2=-p[c,1]/span*res+res*.5
        area=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(area)<1e-9:continue
        for y in range(max(0,int(math.floor(min(y0,y1,y2)))),min(res-1,int(math.ceil(max(y0,y1,y2))))+1):
            for x in range(max(0,int(math.floor(min(x0,x1,x2)))),min(res-1,int(math.ceil(max(x0,x1,x2))))+1):
                aa=((y1-y2)*(x+.5-x2)+(x2-x1)*(y+.5-y2))/area;bb=((y2-y0)*(x+.5-x2)+(x0-x2)*(y+.5-y2))/area;cc=1-aa-bb
                if aa<0 or bb<0 or cc<0:continue
                z=aa*p[a,2]+bb*p[b,2]+cc*p[c,2]
                if z>out[y,x]:out[y,x]=z
    return out

@njit(cache=True)
def beauty_raster(v,n,colors,f,matids,factors,shadow,basis,light_basis,light_center,light_span,center,span,width,height,style,ground_start):
    p=(v-center)@basis
    image=np.zeros((height,width,4),np.uint8);depth=np.full((height,width),-1e20,np.float32)
    ss=shadow.shape[0];l=light_basis[:,2]
    for k in range(len(f)):
        a,b,c=f[k];x0=p[a,0]/span*height+width*.5;y0=-p[a,1]/span*height+height*.5;x1=p[b,0]/span*height+width*.5;y1=-p[b,1]/span*height+height*.5;x2=p[c,0]/span*height+width*.5;y2=-p[c,1]/span*height+height*.5
        area=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(area)<1e-9:continue
        mat=factors[matids[k]];floor=k>=ground_start
        for y in range(max(0,int(math.floor(min(y0,y1,y2)))),min(height-1,int(math.ceil(max(y0,y1,y2))))+1):
            for x in range(max(0,int(math.floor(min(x0,x1,x2)))),min(width-1,int(math.ceil(max(x0,x1,x2))))+1):
                aa=((y1-y2)*(x+.5-x2)+(x2-x1)*(y+.5-y2))/area;bb=((y2-y0)*(x+.5-x2)+(x0-x2)*(y+.5-y2))/area;cc=1-aa-bb
                if aa<0 or bb<0 or cc<0:continue
                z=aa*p[a,2]+bb*p[b,2]+cc*p[c,2]
                if z<=depth[y,x]:continue
                nx=aa*n[a,0]+bb*n[b,0]+cc*n[c,0];ny=aa*n[a,1]+bb*n[b,1]+cc*n[c,1];nz=aa*n[a,2]+bb*n[b,2]+cc*n[c,2];le=max(1e-12,math.sqrt(nx*nx+ny*ny+nz*nz));nx/=le;ny/=le;nz/=le
                world=aa*v[a]+bb*v[b]+cc*v[c];lp=(world-light_center)@light_basis;sx=lp[0]/light_span*ss+ss*.5;sy=-lp[1]/light_span*ss+ss*.5
                nd=max(0.,nx*l[0]+ny*l[1]+nz*l[2]);bias=light_span/ss*(1.4+2.4*(1-nd));shade=0.
                if sx>=2 and sx<ss-2 and sy>=2 and sy<ss-2:
                    for iy in range(-1,2):
                        for ix in range(-1,2):
                            shade += .0 if shadow[int(sy)+iy,int(sx)+ix]>lp[2]+bias else 1.
                    shade/=9.
                else:shade=1.
                band=(.13 if nd<.25 else .50 if nd<.65 else .97) if style==1 and not floor else nd
                lighting=.35+.12*(ny*.5+.5)+.68*band*(.18+.82*shade)+.10*max(0,-nx*.68+ny*.26-nz*.60)
                for ch in range(3):
                    col=(aa*colors[a,ch]+bb*colors[b,ch]+cc*colors[c,ch])*mat[ch]*lighting
                    col=max(0,min(1.,col))
                    out=col*12.92 if col<=.0031308 else 1.055*col**(1/2.4)-.055
                    image[y,x,ch]=int(min(255,max(0,out*255+.5)))
                image[y,x,3]=255;depth[y,x]=z
    return image

def render(path: str | Path, out: str | Path, size=1000, azimuth=36, elevation=28, *, style=None, ground=True, clip=None, time=0.0, antialias=1, width=None, framing_bounds=None):
    d=prepare(path,clip=clip,time=time);v=d['vertices'].astype(np.float64);n=d['normals'].astype(np.float64);cols=d['colors'].astype(np.float64);f=d['faces'];matids=d['matids'];factors=d['factors'].astype(np.float64)
    lo=v.min(0);hi=v.max(0)
    # Optional shared envelope makes before/after comparisons camera-identical.
    if framing_bounds is not None:
        envelope=np.asarray(framing_bounds,dtype=np.float64)
        if envelope.shape!=(2,3) or not np.isfinite(envelope).all() or np.any(envelope[1]<=envelope[0]):
            raise ValueError('framing_bounds must contain finite increasing 3D bounds')
        lo,hi=envelope
    center=(lo+hi)*.5;diag=max(.05,float(np.linalg.norm(hi-lo)));basis=camera_basis(azimuth,elevation);lp=camera_basis(-38,57);lspan=diag*1.2
    res=640 if size<300 else 1280 if size<800 else 2048
    shadow=shadow_buffer(v,f,lp,center,lspan,res)
    frame_vertices=v if framing_bounds is None else np.array([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])])
    projected=(frame_vertices-center)@basis;w=width or size;span=max(float(np.ptp(projected[:,1]))*1.25,float(np.ptp(projected[:,0]))*size/w*1.28,.03)
    center=center-basis[:,1]*span*.045
    floor_start=len(f)
    if ground:
        extent=diag*5;y=lo[1]-diag*.0015;n0=len(v);cx=center[0];cz=center[2]
        floor=np.array([[cx-extent,y,cz-extent],[cx+extent,y,cz-extent],[cx+extent,y,cz+extent],[cx-extent,y,cz+extent]])
        v=np.vstack([v,floor]);n=np.vstack([n,[[0,1,0]]*4]);cols=np.vstack([cols,[[.91,.915,.9]]*4]);f=np.vstack([f,[[n0,n0+2,n0+1],[n0,n0+3,n0+2]]]).astype(np.int32);matids=np.r_[matids,[len(factors)]*2].astype(np.int32);factors=np.vstack([factors,[1,1,1,1]])
    if style is None:style=d['asset'].metadata.get('style','lowpoly')
    im=Image.fromarray(beauty_raster(v,n,cols,f,matids,factors,shadow,basis,lp,(lo+hi)*.5,lspan,center,span,w*antialias,size*antialias,1 if style in ['toon','rounded'] else 0,floor_start))
    if antialias>1:im=im.resize((w,size),Image.Resampling.LANCZOS)
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    if Path(out).suffix.lower() in ('.jpg','.jpeg'):
        bg=Image.new('RGB',im.size,'#FAFBF8');bg.paste(im,mask=im.getchannel('A'));bg.save(out,quality=94)
    else:im.save(out)
    return {'renderer':'CPU orthographic + actual GLB + PCF shadow map','presentation_ground':ground,'ground_exported':False,'framing_bounds':None if framing_bounds is None else np.asarray(framing_bounds).tolist(),'style':style,'size':[w,size],'triangles':floor_start,'clip':clip,'time':time,'limits':['Opaque vertex-coloured library materials; not path tracing or full GPU PBR.']}
