"""Expansion author vocabulary. Geometry, interfaces and collision share metres.

No frozen meshes, random scatter soups or colour-only duplicate catalogue IDs.
"""
from foundation.common import *
from foundation import common as F
from worlds.common import pi,ai,beam,disk
from copy import deepcopy
THEMES={'forest':'温带森林','desert':'沙漠绿洲','snow':'雪原冻土','swamp':'沼泽湿地','mountain':'山地峡谷','cave':'洞穴晶体'}
P.update({'earth':'#82664C','earthSide':'#66513E','grassland':'#718D4B','birch':'#E0D9BE','birchMark':'#514B40','sand':'#D7B67C','sandShade':'#AC8250','snow':'#E4EFF0','ice':'#98CBCD','mud':'#646651','river':'#5AADB2','wetstone':'#586E6D','asphalt':'#535C5D','line':'#EFE2AD','crystal':'#79BCC8','basalt':'#626572'})
NEW_PARTS=[];NEW_ASSEMBLIES=[]
def socket(id,pos,normal,interface='terrain.edge.1m.v1',span=None,profile=None,tangent=None,**kw):
    if tangent is None:tangent=[0,0,1] if abs(normal[0])>.5 else [1,0,0]
    s=port(id,pos,normal,tangent,interface)
    s.update(version=1,tolerance=.0001,gender='neutral',allowed_scale='none',**kw)
    if span is not None:s['span']=span
    if profile is not None:s['profile']=list(profile)
    return s

def ground_ports(size=4,height=0):
    h=size/2
    return [socket('west',[-h,height,0],[-1,0,0],span=size,profile=[0]*9),socket('east',[h,height,0],[1,0,0],span=size,profile=[0]*9),socket('north',[0,height,-h],[0,0,-1],span=size,profile=[0]*9),socket('south',[0,height,h],[0,0,1],span=size,profile=[0]*9)]

def runtime(collision=None,budget=3000,lod=None,**kw):
    return {'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','origin':'authored-ground-contact','collision':collision or {'type':'none','reason':'decorative, non-solid geometry'},'triangle_budget':budget,'lod':lod or {'levels':[],'reason':'small asset: LOD disabled'},**kw}

def ep(id,name,category,forms,size,theme='shared',material='mat.stone',ports=(),params=None,collision=None,lod=None,budget=3000,tags=(),description=''):
    ident=F.part('exp.'+id,name,category,forms,size,ports=ports,params=params,material=material,level=1,tags=tags,description=description)
    d=PARTS[ident];d.update(theme=theme,version='2.2.0',tags=['Expansion',theme,category,*tags],runtime=runtime(collision,budget,lod));d['quality']={'status':'expansion','review_scope':'A-C','approval':'development-review-not-user-approval'};d['source'].update(authoring='tools/expansion/',revision='2.2.0')
    NEW_PARTS.append(ident);return ident

def ea(id,name,category,items,theme='shared',level=2,ports=None,params=None,collision=None,lod=None,metadata=None,tags=(),description=''):
    md={'collection':'expansion-2.2','theme':theme,'quality':{'status':'expansion','review_scope':'A-C'},'runtime':runtime(collision or {'type':'children','source':'authored child collider recipes'},250000 if level==4 else 25000,lod),'interfaces':[],**(metadata or {})}
    ident=F.assembly('exp-'+id,name,category,items,level=level,params=params,ports=ports,metadata=md,description=description)
    ASSEMBLIES[ident].update(tags=['Expansion',theme,category,*tags],version='2.2.0');NEW_ASSEMBLIES.append(ident);return ident

def box_collision(size,center=None):return {'type':'box','size':list(size),'center':list(center or [0,size[1]/2,0])}
def trunk_collision(height=3,radius=.18):return {'type':'capsule','radius':radius,'segment_start':[0,radius,0],'segment_end':[0,height-radius,0],'static_only':False}
def topo(points,faces,color='stone',**kw):
    """Orient a closed authored polyhedron outward once, not via double-sided light."""
    # Convex and star-shaped forms only. For terrain walls use explicit order.
    c=[sum(p[k] for p in points)/len(points) for k in range(3)];out=[]
    for f in faces:
        a,b,d=[points[j] for j in f[:3]];u=[b[k]-a[k] for k in range(3)];v=[d[k]-a[k] for k in range(3)]
        n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];fc=[sum(points[i][k] for i in f)/len(f)-c[k] for k in range(3)]
        out.append(f if sum(n[k]*fc[k] for k in range(3))>=0 else f[::-1])
    return poly(points,out,color,**kw)

def terrain_grid(size=4,n=8,fn=None,top='grassland',side='earthSide',param_height=False):
    """Closed heightfield, un-bevelled exact grid borders, coherent interior relief."""
    fn=fn or (lambda u,v:0);points=[];faces=[];colors=[]
    for z in range(n+1):
        for x in range(n+1):
            h=fn(x/n,z/n);points.append([(x/n-.5)*size,mul(h,Q('relief')) if param_height else h,(z/n-.5)*size])
    for z in range(n):
        for x in range(n):
            a=z*(n+1)+x;b=a+1;c=a+n+1;d=c+1
            faces.extend([[a,c,b],[b,c,d]]);colors.extend([C(top),C(top)])
    border=[x for x in range(n+1)]+[z*(n+1)+n for z in range(1,n+1)]+[n*(n+1)+x for x in range(n-1,-1,-1)]+[z*(n+1) for z in range(n-1,0,-1)]
    lower=[]
    for a in border:lower.append(len(points));points.append([points[a][0],-.30,points[a][2]])
    for i in range(len(border)):
        j=(i+1)%len(border);faces.append([border[i],border[j],lower[j],lower[i]]);colors.append(C(side))
    # Border follows clockwise when seen from +Y; lower cap points toward -Y.
    faces.append(lower);colors.append(C(side))
    f=poly(points,faces,top,colors=colors);return f

def strip(points,width,color='asphalt',depth=.12,material=None,tangents=None):
    """Continuous horizontal ribbon with shared cross sections, no overlap at corners."""
    verts=[]
    for i,p in enumerate(points):
        prev=points[max(0,i-1)];nxt=points[min(len(points)-1,i+1)];dx=nxt[0]-prev[0];dz=nxt[2]-prev[2];l=math.hypot(dx,dz);nx,nz=dz/l,-dx/l
        if tangents is not None:
            dx,_,dz=tangents[i];l=math.hypot(dx,dz);nx,nz=dz/l,-dx/l
        verts.extend([[p[0]+nx*width/2,p[1],p[2]+nz*width/2],[p[0]-nx*width/2,p[1],p[2]-nz*width/2],[p[0]+nx*width/2,p[1]-depth,p[2]+nz*width/2],[p[0]-nx*width/2,p[1]-depth,p[2]-nz*width/2]])
    faces=[]
    for i in range(len(points)-1):
        a=i*4;b=a+4;faces +=[[a,a+1,b+1,b],[a+2,b+2,b+3,a+3],[a,b,b+2,a+2],[a+1,a+3,b+3,b+1]]
    faces += [[0,2,3,1],[len(verts)-4,len(verts)-3,len(verts)-1,len(verts)-2]]
    return poly(verts,faces,color,**({'material':material} if material else {}))
