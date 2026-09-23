"""14 transport parts, 14 reusable modules, 8 real site recipes (54 with terrain)."""
from .common import *
from .terrain import prism_xz

def lane_ports(length=4):
    return [socket('north',[0,0,-length/2],[0,0,-1],'road.lane.3m.v1',span=3,profile=[0,0]),socket('south',[0,0,length/2],[0,0,1],'road.lane.3m.v1',span=3,profile=[0,0])]
def arc(angle=90,radius=6,width=3):
    n=12 if angle==90 else 6;points=[];faces=[]
    for i in range(n+1):
        a=math.radians(angle*i/n)
        for off,y in [(-width/2,0),(width/2,0),(-width/2,-.12),(width/2,-.12)]:points.append([mul(add(radius,off),math.cos(a)),y,mul(add(radius,off),math.sin(a))])
    for i in range(n):
        a=4*i;b=a+4;faces +=[[a,b,b+1,a+1],[a+2,a+3,b+3,b+2],[a,a+2,b+2,b],[a+1,b+1,b+3,a+3]]
    faces += [[0,1,3,2],[4*n,4*n+2,4*n+3,4*n+1]]
    return poly(points,faces,'asphalt')
def road_export(node='lane'):
    return [{'id':n,'node':node,'socket':n} for n in ['north','south']]

def author():
    lane=ep('road.lane','三米车道 · 精确端面','terrain',[cube([3,.12,4],'asphalt',[0,-.06,0]),cube([.065,.006,1.2],'line',[-1.43,.006,0])],[3,.126,4],ports=lane_ports(),collision=box_collision([3,.12,4],[0,-.06,0]),tags=['道路','单车道','可拼接'])
    for ang in [45,90]:
        r=Q('radius');ports=[socket('in',[r,0,0],[0,0,-1],'road.lane.3m.v1',span=3,profile=[0,0]),socket('out',[mul(math.cos(math.radians(ang)),r),0,mul(math.sin(math.radians(ang)),r)],[-math.sin(math.radians(ang)),0,math.cos(math.radians(ang))],'road.lane.3m.v1',span=3,profile=[0,0],tangent=[math.cos(math.radians(ang)),0,math.sin(math.radians(ang))])]
        ep(f'road.curve{ang}',f'三米车道 · {ang}°连续转弯','terrain',[arc(ang,r)],[9,.12,9],ports=ports,params=schema(radius=number(6,4,12,'转弯半径',.5,'m')),collision={'type':'authored-mesh','static_only':True,'source':'continuous-road-surface'},tags=['道路','弯道'])
    layouts={'t':[(-1.5,-3),(1.5,-3),(1.5,-1.5),(3,-1.5),(3,1.5),(-3,1.5),(-3,-1.5),(-1.5,-1.5)],'cross':[(-1.5,-3),(1.5,-3),(1.5,-1.5),(3,-1.5),(3,1.5),(1.5,1.5),(1.5,3),(-1.5,3),(-1.5,1.5),(-3,1.5),(-3,-1.5),(-1.5,-1.5)]}
    for key,outline in layouts.items():
        ports=[socket('north',[0,0,-3],[0,0,-1],'road.lane.3m.v1',span=3,profile=[0,0]),socket('west',[-3,0,0],[-1,0,0],'road.lane.3m.v1',span=3,profile=[0,0]),socket('east',[3,0,0],[1,0,0],'road.lane.3m.v1',span=3,profile=[0,0])]
        if key=='cross':ports.append(socket('south',[0,0,3],[0,0,1],'road.lane.3m.v1',span=3,profile=[0,0]))
        ep('road.junction_'+key,'T 字路口实体' if key=='t' else '十字路口实体','terrain',[prism_xz(outline,.12,'asphalt')],[6,.12,6],ports=ports,collision={'type':'authored-mesh','static_only':True,'source':'authored-road-intersection'},tags=['道路','交叉路口'])
    # Ring has no duplicated first/last wedge and no internal caps.
    ep('road.roundabout','环岛路面 · 环形实孔','terrain',[lathe([[3,-.12],[6,-.12],[6,0],[3,0]],'asphalt',32,closed_profile=True)],[12,.12,12],collision={'type':'authored-mesh','static_only':True,'source':'road-ring'},tags=['道路','环岛'])
    side=prism_xz([(-.5,-2),(.5,-2),(.5,2),(-.5,2)],.16,'stoneLight',.16)
    for i,p in enumerate(side['points']):p[1]=add(p[1],mul(Q('rise'),(p[2]+2)/4))
    ep('road.sidewalk','一米人行道 · 平台／坡道','terrain',[side,*[cube([.99,.004,.022],'stone',[0,add(.163,mul(Q('rise'),(z+2)/4)),z]) for z in [-1,0,1]]],[1,.66,4],ports=[socket('north',[0,.16,-2],[0,0,-1],'road.sidewalk.1m.v1',span=1),socket('south',[0,add(.16,Q('rise')),2],[0,0,1],'road.sidewalk.1m.v1',span=1)],params=schema(rise=number(0,0,.5,'无障碍抬升',.05,'m')),collision={'type':'authored-mesh','static_only':True,'source':'inclined-walkable-slab'},tags=['人行道','坡道'])
    ep('road.sidewalk_corner','人行道转角 · 留出内侧道路','terrain',[prism_xz([(-1,-1),(1,-1),(1,0),(0,0),(0,1),(-1,1)],.16,'stoneLight',.16)],[2,.16,2],ports=[socket('north',[.5,.16,-1],[0,0,-1],'road.sidewalk.1m.v1',span=1),socket('south',[-.5,.16,1],[0,0,1],'road.sidewalk.1m.v1',span=1)],collision={'type':'authored-mesh','static_only':True,'source':'L-walkway'},tags=['人行道','转角'])
    ep('road.curb','路缘排水石 · 三段接缝','terrain',[box([.20,.22,.97],'stoneLight',[0,.11,z],bevel=.018) for z in [-1,0,1]],[.2,.22,2.97],collision=box_collision([.2,.22,3]),tags=['路缘','排水'])
    ep('road.median','中央隔离带 · 花槽与端头','terrain',[box([.65,.22,3.9],'stoneLight',[0,.11,0],bevel=.1),box([.48,.018,3.45],'earth',[0,.23,0],bevel=.045),*[ico([.48,.34,.64],'leafDark',[0,.33,z],0) for z in [-1.35,-.45,.45,1.35]]],[.65,.55,3.9],collision=box_collision([.65,.22,3.9]),tags=['道路','隔离带'])
    outlines={'arrow':[(-.18,-1.2),(.18,-1.2),(.18,.3),(.6,.3),(0,1.2),(-.6,.3),(-.18,.3)],'parking':[(-1.25,-2),(1.25,-2),(1.25,2),(1.19,2),(1.19,-1.94),(-1.19,-1.94),(-1.19,2),(-1.25,2)],'stripe':[(-1.35,-.18),(1.35,-.18),(1.35,.18),(-1.35,.18)]}
    shapes={k:prism_xz(o,.005,'line',.010) for k,o in outlines.items()};f=deepcopy(shapes['arrow']);f['points']=choice('marking',{k:v['points'] for k,v in shapes.items()});f['faces']=choice('marking',{k:v['faces'] for k,v in shapes.items()})
    ep('road.marking','道路标线 · 箭头／停车框／斑马条','terrain',[f],[2.7,.01,4],material='mat.paint',params=schema(marking={'type':'string','enum':list(shapes),'default':'arrow','title':'标线类型'}),tags=['标线','斑马线','停车'])
    steel=[*[box([.095,.8,.095],'steel',[0,.4,z],.005) for z in [-1.8,0,1.8]],box([.065,.24,4],'metal',[0,.68,0],.025),*[box([.015,.085,.16],'line',[.04,.70,z],.004) for z in [-1.78,1.78]]]
    rope=[*[box([.13,1,.13],'woodDark',[0,.5,z],.016) for z in [-1.8,0,1.8]],loft([[0,.90,-2,.035,.035],[0,.73,-1,.035,.035],[0,.90,0,.035,.035],[0,.73,1,.035,.035],[0,.90,2,.035,.035]],'#AD8B61',7),*[ico([.12,.12,.12],'#AD8B61',[0,.9,z],0) for z in [-1.8,1.8]]]
    for form in rope:form['material']='mat.wood'
    ep('road.guardrail','路侧护栏 · 钢护栏／垂索栏','terrain',[choice('kind',{'steel':a,'rope':b}) for a,b in zip(steel,rope)],[.16,1.02,4],material='mat.metal',params=schema(kind={'type':'string','enum':['steel','rope'],'default':'steel','title':'护栏构型'}),collision={'type':'compound','shapes':[box_collision([.16,1,4])]},tags=['交通','安全设施','绳桥'])
    ep('road.boardwalk','木栈道板组 · 梁与防滑板','terrain',[*[box([2,.09,.27],'woodLight',[0,.18,-1.83+i*.305],.008) for i in range(13)],*[box([.15,.22,4],'woodDark',[x,.055,0],.006) for x in [-.72,.72]]],[2,.235,4],material='mat.wood',ports=[socket('north',[0,.225,-2],[0,0,-1],'road.sidewalk.1m.v1',span=2),socket('south',[0,.225,2],[0,0,1],'road.sidewalk.1m.v1',span=2)],collision=box_collision([2,.09,4],[0,.18,0]),tags=['栈道','木桥'])
    ep('road.bridge_abutment','桥台接口 · 侧翼与支承台','terrain',[prism_xz([(-1.5,-.6),(1.5,-.6),(1.8,.6),(-1.8,.6)],.9,'stone',.9),box([2.65,.18,.72],'stoneLight',[0,.99,-.08],.02)],[3.6,1.08,1.2],collision={'type':'compound','shapes':[box_collision([3,.9,1.2]),box_collision([2.65,.18,.72],[0,.99,-.08])]},tags=['桥台','支承'])
    # L2 — 14 modules, distinct infrastructure functions and connectivity.
    ea('road-straight','双向道路 · 双车道与步道','terrain',[pi('left',lane,[-1.5,0,0]),pi('right',lane,[1.5,0,0],rot=[0,180,0]),pi('walkL','exp.road.sidewalk',[-3.5,0,0]),pi('walkR','exp.road.sidewalk',[3.5,0,0])],ports=[{'id':side+'-'+port,'node':side,'socket':port} for side in ['left','right'] for port in ['north','south']],tags=['道路','城市'])
    for ang in [45,90]:ea('road-bend'+str(ang),f'双向道路 · {ang}°弯道','terrain',[pi('inner',f'exp.road.curve{ang}',params={'radius':4.5}),pi('outer',f'exp.road.curve{ang}',params={'radius':7.5})],ports=[{'id':side+'-'+port,'node':side,'socket':port} for side in ['inner','outer'] for port in ['in','out']],tags=['道路','弯道'])
    for key in ['t','cross']:
        items=[pi('paving','exp.road.junction_'+key),pi('arrow','exp.road.marking',[0,0,-2],params={'marking':'arrow'},scale=[.55,1,.5])]
        for i in range(4):items.append(pi('crossing'+str(i),'exp.road.marking',[-2.25+i*.5,0,.8],rot=[0,90,0],scale=[.7,1,.7],params={'marking':'stripe'}))
        ea('road-'+key,'T 字路口 · 交通标线' if key=='t' else '十字路口 · 行人过街','terrain',items,ports=[{'id':p['id'],'node':'paving','socket':p['id']} for p in PARTS['exp.road.junction_'+key]['connectors']],tags=['道路','交叉路口'])
    ea('road-roundabout','环岛 · 低矮景观中心','terrain',[pi('ring','exp.road.roundabout'),pi('island','exp.terrain.flat',scale=[1.02,1,1.02]),pi('center','core.nature.rock',[0,0,0],scale=[1.2,.7,1.0])],tags=['道路','环岛'])
    ea('sidewalk-ramp','无障碍步道 · 坡道与护栏','terrain',[pi('ramp','exp.road.sidewalk',params={'rise':.35}),pi('rail','exp.road.guardrail',[.55,.20,0],rot=[-5,0,0])],ports=road_export('ramp'),tags=['人行道','无障碍'])
    ea('river-straight','直线河段 · 水面与双侧岸','terrain',[pi('water','exp.terrain.water_channel'),pi('bankL','exp.terrain.river_bank',[-1,0,0]),pi('bankR','exp.terrain.river_bank',[1,0,0],rot=[0,180,0])],ports=road_export('water'),tags=['河流','可拼接'])
    ea('river-bend','弯曲河段 · 岩岸入口','terrain',[pi('water','exp.terrain.water_channel',params={'layout':'bend'}),pi('bank','exp.terrain.river_bend_bank',[-1,.015,-2],scale=[.67,1,.67])],ports=[{'id':n,'node':'water','socket':n} for n in ['north','east']],tags=['河流','弯道'])
    ea('river-confluence','汇流河段 · T／Y 合流','terrain',[pi('water','exp.terrain.water_channel',params={'layout':Q('layout')}),pi('bank','exp.terrain.river_bank',[0,0,-2],rot=[0,90,0])],params=schema(layout={'type':'string','enum':['t','y'],'default':'t','title':'汇流方向'}),ports=[{'id':'north','node':'water','socket':'north'},{'id':'branch-right','node':'water','socket':choice('layout',{'t':'east','y':'south-east'})},{'id':'branch-left','node':'water','socket':choice('layout',{'t':'west','y':'south-west'})}],tags=['河流','汇流'])
    ea('river-source','山泉跌水 · 瀑布与岩台','terrain',[pi('falls','exp.terrain.waterfall',[0,0,.3]),pi('rockL','core.nature.rock',[-1.25,.55,-.3],scale=[1,1.8,.9]),pi('rockR','core.nature.rock',[1.25,.45,-.2],scale=[.8,1.6,.8])],theme='mountain',tags=['水源','瀑布'])
    ea('boardwalk-run','抬升栈道 · 四米木道与桩基','terrain',[pi('deck','exp.road.boardwalk',[0,.55,0]),*[pi('pier'+str(i),'w.timber.post',p,params={'height':.9}) for i,p in enumerate([[-.72,-.3,-1.8],[.72,-.3,-1.8],[-.72,-.3,1.8],[.72,-.3,1.8]])]],ports=road_export('deck'),tags=['栈道','沼泽'])
    ea('rope-bridge','峡谷绳桥 · 栈板、垂索与端桩','terrain',[pi('deck','exp.road.boardwalk'),*[pi('rope'+str(i),'exp.road.guardrail',[x,0,0],params={'kind':'rope'}) for i,x in enumerate([-1.03,1.03])]],ports=road_export('deck'),tags=['桥梁','峡谷'])
    ea('river-shallows','河滩浅水 · 踏石与过水道','terrain',[ai('stream','exp-river-straight'),*[pi('stone'+str(i),'core.nature.rock',[x,.08,z],scale=[.50,.32,.42]) for i,(x,z) in enumerate([(-.8,0),(-.3,.17),(.3,-.12),(.8,.04)])]],tags=['浅滩','涉水'])
    # L3 site kits. Streets use authored roads instead of fixed coloured backgrounds.
    ground=lambda surf='forest',width=3:[pi('ground'+str(x)+str(z),'exp.terrain.flat',[(x-(width-1)/2)*4,-.04,(z-(width-1)/2)*4],params={'surface':surf}) for x in range(width) for z in range(width)]
    ea('site-city-cross','城市十字路口 · 步道、标线与路口设施','terrain',[*ground('mountain'),ai('cross','exp-road-cross'),pi('north','exp.road.lane',[0,0,-5]),pi('south','exp.road.lane',[0,0,5]),pi('east','exp.road.lane',[5,0,0],rot=[0,90,0]),pi('west','exp.road.lane',[-5,0,0],rot=[0,90,0]),*[pi('corner'+str(i),'exp.road.sidewalk_corner',p,rot=[0,i*90,0]) for i,p in enumerate([[-2.5,0,-2.5],[2.5,0,-2.5],[2.5,0,2.5],[-2.5,0,2.5]])]],level=3,tags=['城市','道路套件'])
    ea('site-suburban-t','郊区 T 字路口 · 路缘与隔离带','terrain',[*ground(),ai('t','exp-road-t'),pi('approach','exp.road.lane',[0,0,-5]),pi('curbL','exp.road.curb',[-1.65,0,-4.5]),pi('median','exp.road.median',[0,0,2.2]),pi('curbR','exp.road.curb',[1.65,0,-4.5])],level=3,tags=['郊区','道路套件'])
    ea('site-river-valley','河谷道路 · 沿河护栏与连续水道','terrain',[*ground(),*[ai('water'+str(i),'exp-river-straight',[-2,0,-4+i*4]) for i in range(3)],*[pi('road'+str(i),'exp.road.lane',[2,0,-4+i*4]) for i in range(3)],pi('rail','exp.road.guardrail',[.4,0,0]),ai('source','exp-river-source',[-2,0,-5])],theme='mountain',level=3,tags=['河谷','道路套件'])
    ea('site-canyon-pass','峡谷通道 · 崖壁与绳桥','terrain',[pi('left','exp.terrain.cliff_straight',[-4,0,0],rot=[0,90,0],params={'surface':'mountain'}),pi('right','exp.terrain.cliff_straight',[4,0,0],rot=[0,-90,0],params={'surface':'mountain'}),ai('bridge','exp-rope-bridge',[0,.9,0],rot=[0,90,0]),pi('abutL','exp.road.bridge_abutment',[-2.3,0,0],rot=[0,90,0]),pi('abutR','exp.road.bridge_abutment',[2.3,0,0],rot=[0,-90,0])],theme='mountain',level=3,tags=['峡谷','通道'])
    # A real six-tile seam fixture: matching sampled profiles, no buried overlay
    # terrain. It is also an editable uphill forest approach in the catalogue.
    hill=[pi('base','exp.terrain.flat',params={'surface':'forest','relief':.4}),
          pi('inner','exp.terrain.corner_in',params={'surface':'forest','relief':.4},attach={'target':'base','socket':'east','own':'west','mode':'opposed'}),
          pi('outer','exp.terrain.corner_out',params={'surface':'forest','relief':.4},attach={'target':'inner','socket':'south','own':'north','mode':'opposed'}),
          pi('slope','exp.terrain.slope',params={'surface':'forest','relief':.4},attach={'target':'base','socket':'south','own':'north','mode':'opposed'}),
          pi('steps','exp.terrain.steps',params={'surface':'forest','relief':.4},attach={'target':'slope','socket':'south','own':'north','mode':'opposed'}),
          pi('plateau','exp.terrain.plateau',params={'surface':'forest','relief':.4},attach={'target':'steps','socket':'south','own':'north','mode':'opposed'})]
    hill += [ai('oak','fnd-oak',[-1.2,0,.1],scale=[.55,.55,.55]),ai('pine','world-pine',[4.3,.23,3.5],scale=[.65,.65,.65]),ai('upper_pine','world-pine',[-.8,1.52,12],scale=[.6,.6,.6]),pi('path0','exp.nature.rock_slab',[.2,.015,0],scale=[.3,.1,.45]),pi('path1','exp.nature.rock_slab',[.2,.16,3.5],scale=[.3,.1,.45]),pi('path2','exp.nature.rock_slab',[.2,.35,5.5],scale=[.3,.1,.45])]
    ea('site-forest-path','林间上坡路 · 精确拼接到台地','terrain',hill,theme='forest',level=3,tags=['森林','步道','接口验收'],metadata={'seam_fixture':'six authored tiles; five attachments; corner_in.south matches corner_out.north'})
    ea('site-coast-road','海岸公路 · 连续沙滩与护栏','terrain',[*[pi('shore'+str(i),'exp.terrain.shore_beach',[-1.5,0,-4+i*4]) for i in range(3)],*[pi('road'+str(i),'exp.road.lane',[2,0,-4+i*4]) for i in range(3)],pi('rail','exp.road.guardrail',[.4,0,0]),pi('rocks','exp.terrain.shore_rock',[-2,0,7])],level=3,tags=['海岸','道路'])
    ea('site-city-block','城市街区基底 · 停车、环岛入口与步道','terrain',[*ground('mountain',4),ai('road','exp-road-straight',[0,0,-5]),ai('arc','exp-road-bend45',[-5,0,-3]),pi('parking','exp.road.marking',[-5,0,3],params={'marking':'parking'}),pi('parking2','exp.road.marking',[-2,0,3],params={'marking':'parking'}),ai('ramp','exp-sidewalk-ramp',[5,0,3]),pi('median','exp.road.median',[2,0,3])],level=3,tags=['城市','街区'])
    ea('site-river-crossing','河流穿越 · 架桥与四向岸路','terrain',[*ground(),*[ai('water'+str(i),'exp-river-straight',[0,0,-4+i*4]) for i in range(3)],ai('bridge','exp-rope-bridge',[0,.35,0],rot=[0,90,0]),pi('west','exp.road.boardwalk',[-4,.35,0],rot=[0,90,0]),pi('east','exp.road.boardwalk',[4,.35,0],rot=[0,90,0])],level=3,tags=['河流','桥梁'])
