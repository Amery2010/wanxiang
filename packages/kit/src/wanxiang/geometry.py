"""Finite, Y-up mesh operators. No Blender, shell expressions or network access."""
from __future__ import annotations
import math
import numpy as np
from scipy.interpolate import CubicSpline
from .ir import Mesh, concat, transform
from .errors import WXError
TAU=math.tau

def _positive(*xs):
    if any(not np.isfinite(x) or x<=0 for x in xs):raise WXError('RECIPE_INVALID','Dimensions must be positive finite numbers')

def box(size=(1,1,1), bevel=0):
    _positive(*size)
    x,y,z=np.asarray(size)/2;corners=np.array([[-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],[-x,-y,z],[x,-y,z],[x,y,z],[-x,y,z]])
    quads=[[1,0,3,2],[4,5,6,7],[0,4,7,3],[5,1,2,6],[3,7,6,2],[0,1,5,4]]
    vs=[];fs=[];uv=[]
    for q in quads:
        o=len(vs);vs.extend(corners[q]);fs.extend([[o,o+1,o+2],[o,o+2,o+3]])
        a=np.linalg.norm(corners[q[1]]-corners[q[0]]);b=np.linalg.norm(corners[q[3]]-corners[q[0]])
        uv.extend([[0,0],[a,0],[a,b],[0,b]])
    if bevel>0:
        # Rounded-box projection: subdivided cube surfaces projected to the Minkowski sum.
        r=min(float(bevel),min(size)*.45);inner=np.array(size)/2-r
        vs=[];fs=[];uv=[];norm=[]
        for axis in range(3):
            others=[a for a in range(3) if a!=axis]
            for sign in [-1,1]:
                coords=[np.unique([-size[a]/2,-inner[a],0,inner[a],size[a]/2]) for a in others];o=len(vs)
                for b in coords[1]:
                    for a in coords[0]:
                        p=np.zeros(3);p[axis]=sign*size[axis]/2;p[others]=[a,b]
                        c=np.clip(p,-inner,inner);n=p-c;n=n/max(np.linalg.norm(n),1e-8)
                        vs.append(c+n*r);norm.append(n);uv.append([a,b])
                na=len(coords[0]);nb=len(coords[1])
                for j in range(nb-1):
                    for i in range(na-1):
                        ids=[o+j*na+i,o+j*na+i+1,o+(j+1)*na+i+1,o+(j+1)*na+i]
                        for f in [[ids[0],ids[1],ids[2]],[ids[0],ids[2],ids[3]]]:
                            if np.dot(np.cross(np.array(vs[f[1]])-vs[f[0]],np.array(vs[f[2]])-vs[f[0]]),norm[f[0]])<0:f=f[::-1]
                            fs.append(f)
        return Mesh(vs,fs,norm,uv)
    return Mesh(vs,fs,uv=uv)

def lathe(profile, segments=32, cap=True):
    p=np.asarray(profile,float);segments=int(segments)
    if p.ndim!=2 or p.shape[1]!=2 or len(p)<2 or segments<3 or segments>512:raise WXError('RECIPE_INVALID','Invalid lathe profile or segments')
    if not np.isfinite(p).all() or np.any(p[:,0]<0):raise WXError('RECIPE_INVALID','Invalid radius')
    vs=[];uv=[];faces=[];s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    for j,(r,y) in enumerate(p):
        for i in range(segments+1):
            a=i/segments*TAU;vs.append([r*np.cos(a),y,r*np.sin(a)]);uv.append([i/segments,s[j]])
    for j in range(len(p)-1):
        for i in range(segments):
            a=j*(segments+1)+i;b=a+segments+1
            faces.extend([[a,b,a+1],[a+1,b,b+1]])
    if cap:
        for j,rev in [(0,False),(len(p)-1,True)]:
            if p[j,0]<=1e-9:continue
            idx=len(vs);vs.append([0,p[j,1],0]);uv.append([.5,.5])
            for i in range(segments):
                a=j*(segments+1)+i;faces.append([idx,a+1,a] if rev else [idx,a,a+1])
    v=np.array(vs);f=np.array(faces);ok=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10
    return Mesh(v,f[ok],uv=uv)

def cylinder(radius=.5,height=1,segments=24,top_radius=None):
    _positive(radius,height);r=radius if top_radius is None else top_radius
    return lathe([[radius,0],[r,height]],segments)

def sphere(radius=1,subdivisions=2,scale=(1,1,1)):
    _positive(radius,*scale)
    import trimesh
    m=trimesh.creation.icosphere(subdivisions=max(0,min(5,int(subdivisions))),radius=radius)
    v=np.asarray(m.vertices)*scale
    # Face-local spherical UV seam split; preserves the diagnostic topology through welding.
    f=np.asarray(m.faces);verts=v[f].reshape(-1,3);normal=m.vertex_normals[f].reshape(-1,3)/np.array(scale)
    raw=m.vertices[f].reshape(-1,3);u=np.arctan2(raw[:,2],raw[:,0])/TAU+.5;vv=np.arccos(np.clip(raw[:,1]/radius,-1,1))/np.pi
    uv=np.column_stack([u,vv]).reshape(-1,3,2)
    for tri in uv:
        if np.ptp(tri[:,0])>.5:tri[tri[:,0]<.5,0]+=1
    return Mesh(verts,np.arange(len(verts)).reshape(-1,3),normal,uv.reshape(-1,2))

def curve(points, samples=24):
    p=np.asarray(points,float)
    if len(p)<2 or not np.isfinite(p).all():raise WXError('RECIPE_INVALID','Curve needs two finite points')
    seg=np.linalg.norm(np.diff(p,axis=0),axis=1)
    if np.any(seg<1e-7):raise WXError('GEOMETRY_INVALID','Zero-length curve segment')
    t=np.r_[0,np.cumsum(seg)];return CubicSpline(t,p,axis=0,bc_type='natural')(np.linspace(0,t[-1],int(samples)))

def sweep(points,radii=.1,segments=10,cap=True):
    p=np.asarray(points,float);segments=int(segments)
    if len(p)<2 or segments<3 or segments>128:raise WXError('RECIPE_INVALID','Invalid sweep sampling')
    seg=np.linalg.norm(np.diff(p,axis=0),axis=1)
    if np.any(seg<1e-8):raise WXError('GEOMETRY_INVALID','Sweep contains zero-length segment')
    r=np.broadcast_to(np.asarray(radii,float),(len(p),))
    _positive(*r)
    tang=np.empty_like(p);tang[0]=p[1]-p[0];tang[-1]=p[-1]-p[-2];tang[1:-1]=p[2:]-p[:-2]
    norms=np.linalg.norm(tang,axis=1)
    if np.min(norms)<1e-8:raise WXError('GEOMETRY_INVALID','Curve reverses through 180 degrees')
    tang/=norms[:,None];axis=np.array([0.,1.,0.]) if abs(tang[0,1])<.9 else np.array([1.,0.,0.])
    a=np.cross(tang[0],axis);a/=np.linalg.norm(a);vs=[];ns=[];uv=[];faces=[];arc=np.r_[0,np.cumsum(seg)]
    for j in range(len(p)):
        if j:
            a=a-np.dot(a,tang[j])*tang[j]
            if np.linalg.norm(a)<1e-7:raise WXError('GEOMETRY_INVALID','Degenerate transport frame')
            a/=np.linalg.norm(a)
        b=np.cross(tang[j],a)
        for i in range(segments+1):
            theta=TAU*i/segments;n=a*np.cos(theta)+b*np.sin(theta)
            vs.append(p[j]+r[j]*n);ns.append(n);uv.append([i/segments,arc[j]/max(2*np.pi*r[0],.1)])
    for j in range(len(p)-1):
        for i in range(segments):
            v=j*(segments+1)+i;w=v+segments+1;faces.extend([[v,v+1,w],[v+1,w+1,w]])
    if cap:
        for j in [0,len(p)-1]:
            c=len(vs);vs.append(p[j]);ns.append(-tang[j] if j==0 else tang[j]);uv.append([.5,.5])
            for i in range(segments):
                a0=j*(segments+1)+i;faces.append([c,a0+1,a0] if j==0 else [c,a0,a0+1])
    return Mesh(vs,faces,ns,uv)

def beam(a,b,width=.1,depth=None,bevel=0):
    a=np.asarray(a,float);b=np.asarray(b,float);d=b-a;length=np.linalg.norm(d);_positive(length)
    y=d/length;x=np.cross([0,0,1] if abs(y[2])<.95 else [1,0,0],y);x/=np.linalg.norm(x);z=np.cross(x,y)
    m=np.eye(4);m[:3,:3]=np.column_stack([x,y,z]);m[:3,3]=(a+b)/2
    return box([width,length,depth or width],bevel).transformed(m)

def extrude(outline,depth=.2,holes=None):
    from shapely.geometry import Polygon
    from shapely import constrained_delaunay_triangles
    poly=Polygon(outline,holes)
    if not poly.is_valid or poly.area<1e-8:raise WXError('GEOMETRY_INVALID','Self-intersecting or empty polygon')
    _positive(depth);vs=[];fs=[];uv=[]
    def tri(points,tex):
        o=len(vs);vs.extend(points);uv.extend(tex);fs.append([o,o+1,o+2])
    for g in constrained_delaunay_triangles(poly).geoms:
        xy=np.array(g.exterior.coords)[:3]
        if (xy[1,0]-xy[0,0])*(xy[2,1]-xy[0,1])-(xy[1,1]-xy[0,1])*(xy[2,0]-xy[0,0])<0:xy=xy[::-1]
        tri([[x,y,depth/2] for x,y in xy],xy.tolist())
        tri([[x,y,-depth/2] for x,y in xy[::-1]],xy[::-1].tolist())
    from shapely.geometry.polygon import orient
    poly=orient(poly,sign=1)
    for ring in [poly.exterior,*poly.interiors]:
        xy=np.array(ring.coords)
        for a,b in zip(xy[:-1],xy[1:]):
            u=np.linalg.norm(b-a);pts=[[a[0],a[1],-depth/2],[b[0],b[1],-depth/2],[b[0],b[1],depth/2],[a[0],a[1],depth/2]]
            tri([pts[0],pts[1],pts[2]],[[0,0],[u,0],[u,depth]])
            tri([pts[0],pts[2],pts[3]],[[0,0],[u,depth],[0,depth]])
    return Mesh(vs,fs,uv=uv)

def loft(sections):
    a=np.asarray(sections,float)
    if a.ndim!=3 or a.shape[0]<2 or a.shape[1]<3 or a.shape[2]!=3:raise WXError('RECIPE_INVALID','Loft sections need equal vertex counts')
    v=a.reshape(-1,3);faces=[];count=a.shape[1]
    for j in range(len(a)-1):
        for i in range(count):
            n=(i+1)%count;f=j*count+i;g=j*count+n;faces.extend([[f,g,g+count],[f,g+count,f+count]])
    return Mesh(v,faces)

def heightfield(size=8,resolution=40,origin=(0,0),kind='hills',seed=0,amplitude=1):
    n=int(resolution)
    if not 4<=n<=384:raise WXError('BUDGET_EXCEEDED','Heightfield resolution outside 4..384')
    xs=np.linspace(-size/2,size/2,n+1)+origin[0];zs=np.linspace(-size/2,size/2,n+1)+origin[1];x,z=np.meshgrid(xs,zs)
    # Global-coordinate periodic field: adjacent tiles share exact edge samples.
    h=amplitude*(.42*np.sin(x*.73+seed*.03)*np.cos(z*.53)+.19*np.sin(x*1.43+z*.44)+.07*np.sin(x*3.1-z*2.1))
    if kind=='river':
        center=.55*np.sin(z*.65);dist=np.abs(x-center);blend=np.clip((dist-.65)/.75,0,1);blend=blend*blend*(3-2*blend);h=(-.72)*(1-blend)+(h+.32)*blend
    elif kind=='road':
        dist=np.abs(x-.4*np.sin(z*.5));blend=np.clip((dist-.85)/.7,0,1);h=h*blend+.12*(1-blend)
    elif kind=='terrace':h=np.floor(h*3)/3
    h+=.5
    v=np.column_stack([x.ravel(),h.ravel(),z.ravel()]);faces=[]
    for j in range(n):
        for i in range(n):
            a=j*(n+1)+i;faces.extend([[a,a+n+1,a+1],[a+1,a+n+1,a+n+2]])
    return Mesh(v,faces,uv=np.column_stack([x.ravel()/2,z.ravel()/2]))

def sdf(shapes,resolution=48,bounds=((-2,-2,-2),(2,2,2)),smooth=.15):
    from skimage.measure import marching_cubes
    n=int(resolution)
    if not 16<=n<=160:raise WXError('BUDGET_EXCEEDED','SDF resolution must be within 16..160')
    lo,hi=np.asarray(bounds,float);_positive(*(hi-lo));coords=[np.linspace(lo[i],hi[i],n,dtype=np.float32) for i in range(3)]
    x,y,z=np.meshgrid(*coords,indexing='ij',sparse=True);d=None
    if not shapes or len(shapes)>64:raise WXError('RECIPE_INVALID','SDF needs 1..64 shapes')
    for s in shapes:
        c=np.asarray(s.get('center',[0,0,0]));q=[x-c[0],y-c[1],z-c[2]];kind=s.get('kind','sphere')
        if kind=='sphere':v=np.sqrt(q[0]**2+q[1]**2+q[2]**2)-s.get('radius',1)
        elif kind=='ellipsoid':
            r=np.array(s.get('radii',[1,1,1]));_positive(*r);v=(np.sqrt(sum((q[i]/r[i])**2 for i in range(3)))-1)*r.min()
        elif kind=='box':
            b=np.array(s.get('half_size',[1,1,1]));qq=[np.abs(q[i])-b[i] for i in range(3)]
            v=np.sqrt(sum(np.maximum(t,0)**2 for t in qq))+np.minimum(np.maximum(np.maximum(qq[0],qq[1]),qq[2]),0)
        else:raise WXError('RECIPE_INVALID',f'Unknown SDF primitive {kind}')
        v=np.broadcast_to(v,(n,n,n)).astype(np.float32)
        if d is None:d=v
        elif s.get('operation')=='subtract':d=np.maximum(d,-v)
        elif smooth>0:
            h=np.maximum(smooth-np.abs(d-v),0)/smooth;d=np.minimum(d,v)-h*h*smooth*.25
        else:d=np.minimum(d,v)
    if d.min()>=0 or d.max()<=0:raise WXError('GEOMETRY_INVALID','SDF has no zero crossing')
    v,f,norm,_=marching_cubes(d,0,spacing=(hi-lo)/(n-1),gradient_direction='ascent');v+=lo
    # Dominant-axis, per-triangle UV charts; avoids unsupported triplanar shaders.
    v3=v[f].reshape(-1,3);nn=norm[f].reshape(-1,3);uv=[]
    for face in f:
        pts=v[face];axis=np.argmax(np.abs(np.cross(pts[1]-pts[0],pts[2]-pts[0])));axes=[i for i in range(3) if i!=axis];uv.extend(pts[:,axes])
    return Mesh(v3,np.arange(len(v3)).reshape(-1,3),nn,np.array(uv))

def bend(mesh,amount=.2,axis=0):
    m=mesh.copy();v=m.vertices.copy();h=np.ptp(v[:,1])
    if h<1e-8:raise WXError('GEOMETRY_INVALID','Cannot bend zero-height mesh')
    v[:,axis]+=amount*((v[:,1]-v[:,1].min())/h)**2
    return Mesh(v,m.faces,uv=m.uv)

def taper(mesh,top=.3):
    _positive(top);v=mesh.vertices.copy();t=(v[:,1]-v[:,1].min())/max(np.ptp(v[:,1]),1e-8);v[:,[0,2]]*=((1-t)+t*top)[:,None]
    return Mesh(v,mesh.faces,uv=mesh.uv)
