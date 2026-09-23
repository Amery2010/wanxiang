"""D/E production vocabulary: authored profiles, real apertures and joint pivots.

Registry counts measure semantic definitions, never palettes, mirrored instances or
LOD outputs. Helpers do not write files; rebuild_library owns the transaction.
"""
from .common import *
from worlds.common import turn, controls, paint
from frontiers.common import tube
from .terrain import prism_xz
from collections import Counter

DOMAINS={
 'architecture':(36,18,6), 'interiors':(22,14,6), 'industry':(18,12,6),
 'transport':(20,12,12), 'characters':(24,16,8), 'creatures':(20,10,6),
 'gameplay':(18,8,4), 'robotics':(10,6,4)}
D_PARTS=[];D_ASSEMBLIES=[]
# Namespaced new shades never overwrite legacy palette keys. In particular,
# replacing the shared 'brass' entry would recolour older assets on the second
# authoring call inside one Python process.
P.update({'copper':'#AD7653','tile':'#9C5745','stucco':'#E4D4B4',
          'oak':'#926C45','charcoal':'#374348','linen':'#E4DEC9',
          'mortar':'#626E6A','signal':'#D7A647','medical':'#9DBBB0',
          'indigo':'#5A6886','productionBrass':'#B49858','bone':'#DAD3B6',
          'coal':'#404447','safety':'#DEA842','sandstone':'#AD9D7E'})
THEMES.update(medieval='中世纪村镇',castle='城堡庭院',dungeon='地下城遗迹',
              public='室内与公共设施',industrial='工业能源',rail='铁路货运',
              airport='航空地勤',transport='公路与水运',adventure='角色与装备',
              wildlife='野生与幻想生物',gameplay='关卡机关',robotics='机器人与机械')

def dp(id,name,cat,forms,size,domain,theme=None,material='mat.matte',ports=(),
       params=None,collision=None,lod=None,budget=5000,rig=None,components=None,
       anchor='base',tags=(),description=''):
    """Register one independently authored semantic part, preserving its pivot."""
    ident=ep(id,name,cat,forms,size,theme or domain,material,ports,
             params or schema(),collision,lod,budget,
             tags=('D-E',domain,*tags),description=description)
    d=PARTS[ident];d['anchor']=anchor
    if rig:d['shape_params']['rig']=rig
    if components:d['shape_params']['components']=components
    d['version']='3.0.0';d['quality'].update(review_scope='D-E',domain=domain)
    d['source'].update(revision='3.0.0',authoring='tools/expansion/'+domain+'.py')
    d['runtime']['origin']='authored-joint-pivot' if anchor in ('hinge','center') else 'authored-ground-contact'
    d['runtime']['coordinate_contract']='metres, Y-up, Z-forward; no implicit normalization'
    D_PARTS.append(ident);return ident

def da(id,name,cat,items,domain,theme=None,level=2,ports=None,params=None,
       metadata=None,collision=None,lod=None,budget=None,tags=(),description=''):
    ident=ea(id,name,cat,items,theme or domain,level,ports,params,collision,lod,
      metadata={'stage':'D' if domain in ('architecture','interiors','industry') else 'E',
                'domain':domain,**(metadata or {})},tags=('D-E',domain,*tags),description=description)
    d=ASSEMBLIES[ident];d['version']='3.0.0';d['metadata']['collection']='expansion-3.0'
    d['metadata']['quality'].update(review_scope='D-E',domain=domain)
    if budget:d['metadata']['runtime']['triangle_budget']=budget
    D_ASSEMBLIES.append(ident);return ident

def formbox(w,h,d,color='oak',x=0,y=0,z=0,bevel=.015,**kw):
    if bevel==0:return cube([w,h,d],color,[x,add(y,mul(h,.5)),z],**kw)
    return box([w,h,d],color,[x,add(y,mul(h,.5)),z],bevel,**kw)

def round_tube(r=.12,inner=.09,length=1,color='steel',sides=12,**kw):
    """Hollow Y-axis tube with annular end faces, not capped across its bore."""
    return lathe([[r,0],[r,length],[inner,length],[inner,0]],color,sides,
                 closed_profile=True,**kw)

def ring(r=.25,thickness=.045,depth=.06,color='metal',**kw):
    return lathe([[r,-depth/2],[r,depth/2],[r-thickness,depth/2],[r-thickness,-depth/2]],color,12,closed_profile=True,**kw)

def frame(w,h,depth=.16,t=.10,color='wood',bottom=True):
    fs=[formbox(t,h,depth,color,-(w-t)/2),formbox(t,h,depth,color,(w-t)/2),
        formbox(w-2*t,t,depth,color,0,h-t)]
    if bottom:fs.append(formbox(w-2*t,t,depth,color))
    return fs

def opening_collision(w,h,d,t=.16,base=0):
    return {'type':'compound','shapes':[box_collision([t,h,d],[-(w-t)/2,base+h/2,0]),
      box_collision([t,h,d],[(w-t)/2,base+h/2,0]),box_collision([w-2*t,t,d],[0,base+h-t/2,0])]}

def wall_ports(width=2,height=3,thickness=.24):
    return [socket('west',[mul(width,-.5),0,0],[-1,0,0],'arch.wall.1m.v1',span=thickness,profile=[0,height],tangent=[0,0,1]),
            socket('east',[mul(width,.5),0,0],[1,0,0],'arch.wall.1m.v1',span=thickness,profile=[0,height],tangent=[0,0,1])]

def axis_ports(interface,length=1,axis='z',height=0,**kw):
    if axis=='z':return [socket('in',[0,height,-length/2],[0,0,-1],interface,**kw),socket('out',[0,height,length/2],[0,0,1],interface,**kw)]
    return [socket('in',[-length/2,height,0],[-1,0,0],interface,tangent=[0,0,1],**kw),socket('out',[length/2,height,0],[1,0,0],interface,tangent=[0,0,1],**kw)]

def exported(node,own='out',id='out'):
    return {'id':id,'node':node,'socket':own}

def mate(id,part,target,own='in',socket='out',**kw):
    return inst(id,part=part,attach={'target':target,'own':own,'socket':socket,'mode':'opposed'},**kw)

def motion(id,node,axis=(0,1,0),values=(0,90,0),name='Operate',seconds=3,mode='rotation'):
    track_={'node':node,'axis':list(axis),'degrees' if mode=='rotation' else 'translations':list(values)}
    clip(id,[{'name':name,'duration':seconds,'tracks':[track_]}])

def slider(id,title,node,lo,hi,axis=(0,1,0)):
    return {'id':id,'title':title,'node':node,'axis':list(axis),'mode':'translation',
            'min':lo,'max':hi,'default':0,'unit':'m','step':.01}

def authored_lod():
    return {'levels':[{'level':0,'parameters':{'detail':True},'screen_height':.20},
                      {'level':1,'parameters':{'detail':False},'screen_height':.05}],
            'method':'authored feature removal, not duplicated meshes'}
DETAIL={'type':'boolean','default':True,'title':'轮廓与次级结构细节'}
def optional(forms):
    for f in forms:f['enabled']=Q('detail')
    return forms

def cabinet(w=1,h=1,d=.5,color='oak',open_front=False):
    fs=[formbox(w,.07,d,color,0,0),formbox(w,.07,d,color,0,h-.07),
        formbox(.065,h-.14,d,color,-(w-.065)/2,.07),formbox(.065,h-.14,d,color,(w-.065)/2,.07),
        formbox(w-.13,h-.14,.04,color,0,.07,-d/2+.02)]
    if not open_front:
        for sg in (-1,1):
            fs += [formbox(w/2-.04,h-.17,.04,color,sg*w/4,.08,d/2+.004),
                   rod([sg*.07,h*.5,d/2+.055],[sg*.07,h*.7,d/2+.055],.013,'productionBrass',sides=6)]
    return fs

def legs(w=.9,d=.5,height=.72,color='charcoal',thick=.05):
    return [formbox(thick,height,thick,color,x,0,z) for x in (-w/2,w/2) for z in (-d/2,d/2)]

def endpoint_normal(a,b):
    v=[b[k]-a[k] for k in range(3)];n=math.sqrt(sum(x*x for x in v));return [x/n for x in v]

def finish_counts(domain):
    ps=[i for i in D_PARTS if PARTS[i]['quality']['domain']==domain]
    aa=[i for i in D_ASSEMBLIES if ASSEMBLIES[i]['metadata']['domain']==domain]
    actual=(len(ps),sum(ASSEMBLIES[i]['metadata']['level']==2 for i in aa),sum(ASSEMBLIES[i]['metadata']['level']==3 for i in aa))
    if actual!=DOMAINS[domain]:raise ValueError(f'{domain}: expected {DOMAINS[domain]}, got {actual}')

def swept_pipe(path,outer=.125,inner=.09,color='steel',sides=12,tangents=None):
    """Closed annular sweep along a planar XZ path; ports remain genuinely hollow."""
    pts=[];faces=[];n=len(path)
    for j,c in enumerate(path):
        d=tangents[j] if tangents is not None else [path[min(j+1,n-1)][k]-path[max(0,j-1)][k] for k in range(3)]
        norm=math.hypot(d[0],d[2]);u=[d[2]/norm,0,-d[0]/norm]
        for r in [outer,inner]:
            pts += [[c[0]+r*math.cos(i*math.tau/sides)*u[0],c[1]+r*math.sin(i*math.tau/sides),c[2]+r*math.cos(i*math.tau/sides)*u[2]] for i in range(sides)]
    for j in range(n-1):
        for i in range(sides):
            k=(i+1)%sides;a=j*2*sides+i;b=j*2*sides+k;c=(j+1)*2*sides+i;d=(j+1)*2*sides+k
            faces += [[a,b,d,c],[a+sides,c+sides,d+sides,b+sides]]
    for i in range(sides):
        k=(i+1)%sides;off=(n-1)*2*sides
        faces += [[i+sides,k+sides,k,i],[off+i,off+k,off+k+sides,off+i+sides]]
    # A whole-shell orientation, never a face-by-centre rule (which breaks concavity).
    volume=0
    for face in faces:
        a=pts[face[0]]
        for j in range(1,len(face)-1):
            b=pts[face[j]];c=pts[face[j+1]]
            volume+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
    if volume<0:faces=[f[::-1] for f in faces]
    return poly(pts,faces,color)
