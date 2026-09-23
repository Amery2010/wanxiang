"""Eighteen true terrain families: exact borders, coherent relief, open portals."""
from .common import *
SURFACES={'forest':'#718D4B','desert':'#D7B67C','snow':'#E4EFF0','swamp':'#646651','mountain':'#9B9788','cave':'#777888'}
SURFACE_SCHEMA={'type':'string','enum':list(SURFACES),'default':'forest','title':'地表环境'}
def prism_xz(outline,depth=.2,color='stone',top=0):
    n=len(outline);points=[[x,top,z] for x,z in outline]+[[x,sub(top,depth),z] for x,z in outline]
    faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    return poly(points,faces,color)
def surface_form(fn,top='grassland',side='earthSide',n=8):
    f=terrain_grid(4,n,fn,top,side,param_height=True)
    f['colors']=[choice('surface',SURFACES) if c==C(top) else c for c in f['colors']]
    return f

def author():
    params=schema(surface=SURFACE_SCHEMA,relief=number(1,.25,1.5,'地势起伏',.05))
    gentle=lambda u,v:.028*math.sin(math.pi*u)*math.sin(math.pi*v)*(math.sin(u*6+v*3)+.5)
    ep('terrain.flat','四米地形 · 连续平地','terrain',[surface_form(gentle)],[4,.34,4],ports=ground_ports(),params=params,collision={'type':'heightfield','static_only':True,'source':'authored-surface','resolution':[9,9],'base_y':-.3},tags=['地形','可拼接','ground'])
    kinds=[('slope','平缓直坡',lambda u,v:v),('steps','阶梯坡',lambda u,v:(math.floor(v*4+1e-6)/4)),('corner_in','内凹汇坡',lambda u,v:min(u,v)),('corner_out','外凸分水坡',lambda u,v:max(u,v)),('cliff_straight','直线崖壁',lambda u,v:2.5*max(0,min(1,(.72-v)*3.8))),('cliff_inner','内湾崖壁',lambda u,v:2.4*max(0,min(1,(max(abs(u-.5),abs(v-.5))-.16)*4))),('cliff_outer','突出崖角',lambda u,v:2.5*max(0,min(1,(.85-max(u,v))*3.2))),('plateau','台地平台',lambda u,v:1.8*max(0,min(1,(min(u,1-u,v,1-v)-.03)*6))),('gully','沟壑切口',lambda u,v:.60*max(0,min(1,(abs(u-.5)-.12)*4)))]
    for key,name,fn in kinds:
        # Author exact sampled edge profiles, evaluated with the same relief parameter.
        ports=[]
        for edge,normal,p0,p1 in [('north',[0,0,-1],(0,0),(1,0)),('south',[0,0,1],(0,1),(1,1)),('west',[-1,0,0],(0,0),(0,1)),('east',[1,0,0],(1,0),(1,1))]:
            heights=[fn(p0[0]+(p1[0]-p0[0])*i/8,p0[1]+(p1[1]-p0[1])*i/8) for i in range(9)]
            mid=heights[4];pos=[(p0[0]+p1[0]-1)*2,mul(mid,Q('relief')),(p0[1]+p1[1]-1)*2]
            ports.append(socket(edge,pos,normal,span=4,profile=[mul(v-mid,Q('relief')) for v in heights]))
        f=surface_form(fn,n=8);ep('terrain.'+key,name+' · 四米模块','terrain',[f],[4,3,4],ports=ports,params=params,collision={'type':'heightfield','static_only':True,'source':'authored-surface','resolution':[9,9]},tags=['地形','坡地','可拼接'],budget=1000)
    # Open arch: no invisible wall in the opening. Structure deliberately not rounded.
    outline=[(-2,0),(-1.25,0),(-1.22,1.6),(-.78,2.18),(0,2.40),(.78,2.18),(1.22,1.6),(1.25,0),(2,0),(2.15,2.0),(1.2,3.02),(0,3.28),(-1.2,3.02),(-2.15,2.0)]
    arch=extrude(outline,.95,'stoneDark')
    ep('terrain.cave_arch','岩壁洞口 · 可穿越石拱','terrain',[arch,ico([1.0,1.2,1.25],'stone',[-1.78,.50,0],0),ico([.9,.8,1.15],'stone',[1.77,.32,0],0)],[4.7,3.3,1.3],ports=[socket('portal',[0,0,.48],[0,0,1],'arch.door.v1',span=2.4)],collision={'type':'compound','shapes':[box_collision([.9,2.5,1.1],[-1.7,1.25,0]),box_collision([.9,2.5,1.1],[1.7,1.25,0]),box_collision([4.2,.7,1.1],[0,2.93,0])]},tags=['洞穴','通道','arch'])
    # Bank cross-section meets the water at exactly x = 0, y = 0.
    bank=prism_xz([(-1,-2),(0,-2),(0,2),(-1,2)],.28,'earth')
    bank['points']=[[-1,.16,-2],[0,0,-2],[0,0,2],[-1,.16,2],[-1,-.28,-2],[0,-.28,-2],[0,-.28,2],[-1,-.28,2]]
    ep('terrain.river_bank','缓坡河岸 · 直段','terrain',[bank],[1,.45,4],ports=[socket('river',[0,0,0],[1,0,0],'terrain.river.2m.v1',span=4)],collision={'type':'authored-mesh','static_only':True,'source':'authored-bank'},tags=['河岸','泥岸','过渡'])
    # Curved bank is a continuous radial strip, not interpenetrating rock boxes.
    pts=[[3*math.cos(a),.12,3*math.sin(a)] for a in [i*math.pi/16 for i in range(9)]]
    ep('terrain.river_bend_bank','缓坡河岸 · 九十度内湾','terrain',[strip(pts,1,'earth',.28)],[4,.4,4],collision={'type':'authored-mesh','static_only':True,'source':'authored-bank'},tags=['河岸','弯道'])
    shapes={'straight':[(-1,-2),(1,-2),(1,2),(-1,2)],'bend':[(-1,-2),(1,-2),(1,-1),(2,-1),(2,1),(-1,1)],'t':[(-1,-2),(1,-2),(1,-1),(2,-1),(2,1),(-2,1),(-2,-1),(-1,-1)],'y':[(-1,-2),(1,-2),(1,-.15),(2.2071067812,.7928932188),(.7928932188,2.2071067812),(0,.7),(-.7928932188,2.2071067812),(-2.2071067812,.7928932188),(-1,-.15)]}
    forms={k:prism_xz(v,.16,'river') for k,v in shapes.items()}
    f=deepcopy(forms['straight']);f['points']=choice('layout',{k:v['points'] for k,v in forms.items()});f['faces']=choice('layout',{k:v['faces'] for k,v in forms.items()});f['material']='mat.water'
    ports=[socket('north',[0,0,-2],[0,0,-1],'terrain.river.2m.v1',span=2,profile=[0,0]),socket('south',[0,0,2],[0,0,1],'terrain.river.2m.v1',span=2,profile=[0,0],enabled=choice('layout',{'straight':True,'bend':False,'t':False,'y':False})),socket('east',[2,0,0],[1,0,0],'terrain.river.2m.v1',span=2,profile=[0,0],enabled=choice('layout',{'straight':False,'bend':True,'t':True,'y':False})),socket('west',[-2,0,0],[-1,0,0],'terrain.river.2m.v1',span=2,profile=[0,0],enabled=choice('layout',{'straight':False,'bend':False,'t':True,'y':False}))]
    for name,x in [('south-east',1.5),('south-west',-1.5)]:
        sign=1 if x>0 else -1;rt=math.sqrt(.5)
        ports.append(socket(name,[x,0,1.5],[sign*rt,0,rt],'terrain.river.2m.v1',span=2,profile=[0,0],tangent=[rt,0,-sign*rt],enabled=choice('layout',{'y':True},False)))
    ep('terrain.water_channel','河道水体 · 直线／弯道／T／Y 汇流','terrain',[f],[4,.16,4],material='mat.water',ports=ports,params=schema(layout={'type':'string','enum':list(shapes),'default':'straight','title':'河道结构'}),collision={'type':'none','reason':'water volume is a gameplay trigger, not solid ground'},tags=['河流','水面','汇流'],budget=300)
    # One continuous waterfall sheet with a visible lip and plunge basin.
    waterfall=strip([[0,1.8,-.7],[0,1.8,-.2],[0,1.60,.02],[0,.16,.20],[0,.04,.60]],2,'river',.055,material='mat.water')
    ep('terrain.waterfall','瀑布边缘 · 落水与跌水潭','terrain',[waterfall,ico([2.6,.09,1.5],'water',[0,.02,.64],1,material='mat.water')],[2.65,1.88,2.1],material='mat.water',ports=[socket('lip',[0,1.8,-.7],[0,0,-1],'terrain.river.2m.v1',span=2,profile=[0,0])],tags=['瀑布','水源'],budget=800)
    shore_params=schema(relief=number(1,.3,1.5,'岸坡高度',.05))
    for key,name,color,fn,extra in [('beach','沙滩海岸','sand',lambda u,v:.25*max(0,(u-.30)/.7),[]),('rock','岩石海岸','wetstone',lambda u,v:.75*max(0,(u-.25)/.75),[ico([.9,.7,.8],'stone',[1.36,.60,1.1],0),ico([.5,.4,.9],'stoneDark',[.68,.40,-1.1],0)]),('ice','冰缘海岸','snow',lambda u,v:.32*max(0,(u-.36)/.64),[prism_xz([(-.5,-1.2),(.35,-1.12),(.2,-.58),(-.42,-.68)],.16,'ice',.05)])]:
        f=terrain_grid(4,8,lambda u,v:fn(u,v)-.055 if u<.3 else fn(u,v),color,'earthSide',True)
        water=prism_xz([(-2,-2),(-.85,-2),(-.85,2),(-2,2)],.08,'river',.012);water['material']='mat.water'
        ep('terrain.shore_'+key,name+' · 水陆过渡','terrain',[f,water,*extra],[4,1,4],params=shore_params,collision={'type':'heightfield','static_only':True,'source':'land-only','water_is_solid':False},tags=['海岸','过渡'])
