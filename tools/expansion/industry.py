"""Industrial cells with dimensioned flow paths, hollow flanges and moving tools."""
from .production import *
D='industry'
def p(k,n,f,s,**kw):return dp('industry.'+k,n,'mech',f,s,D,theme='industrial',**kw)
def a(k,n,items,**kw):return da('industry-'+k,n,'mech',items,D,theme='industrial',**kw)
def ip(k):return 'exp.industry.'+k
def ia(k):return 'exp-industry-'+k
F='pipe.flange.medium.v1'

def author():
    roller=[formbox(.055,.18,2,'steel',x=x,y=.71) for x in [-.42,.42]]
    roller += [disk(.064,.78,'metal',[0,.81,-.91+i*.14],10,rotation=[0,0,90]) for i in range(14)]
    roller += legs(.75,1.70,.72,'steel',.055)
    p('roller_conveyor','滚筒输送线 · 独立辊轴与机架',roller,[.90,.89,2],ports=axis_ports('arch.floor.1m.v1',2,height=.87,span=.9),material='mat.metal',collision={'type':'compound','shapes':[box_collision([.9,.18,2],[0,.8,0])]},params=schema(detail=DETAIL),lod=authored_lod())
    PARTS[ip('roller_conveyor')]['shape_params']['forms'][4::2]=optional(PARTS[ip('roller_conveyor')]['shape_params']['forms'][4::2])
    # Radial rollers follow the real quarter-turn flow; not a rotated straight belt.
    cf=[]
    for i in range(12):
        ang=math.pi*i/22;x=math.sin(ang);z=math.cos(ang)
        cf.append(rod([x*.57,.8,z*.57],[x*1.37,.8,z*1.37],.058,'metal',sides=8))
    for r in [.52,1.42]:cf += [beam([r*math.sin(i*math.pi/22),.77,r*math.cos(i*math.pi/22)],[r*math.sin((i+1)*math.pi/22),.77,r*math.cos((i+1)*math.pi/22)],.04,.12,'steel') for i in range(11)]
    cf += [formbox(.06,.74,.06,'steel',x=x,z=z) for x,z in [(.1,.7),(.1,1.25),(.7,.1),(1.25,.1),(.9,.9)]]
    p('conveyor_corner','90度弧形滚筒输送线',cf,[1.48,.88,1.48],material='mat.metal',collision={'type':'authored-mesh','static_only':True})
    p('lift_frame','输送升降机架 · 双导轨与横撑',[formbox(1.10,.12,1.25,'steel'),*[formbox(.10,2.2,.11,'steel',x=x,y=.12,z=-.48) for x in [-.44,.44]],formbox(1,.10,.15,'safety',y=2.25,z=-.48),rod([0,.16,-.48],[0,2.20,-.48],.024,'metal'),formbox(1,.10,1.05,'teal',y=.16)],[1.1,2.35,1.25],material='mat.metal',collision=box_collision([1.1,.12,1.25]))
    p('diverter','分拣挡臂 · 轴座与柔性挡板',[disk(.12,.13,'steel',[0,.065,0],12),formbox(.075,.22,.82,'safety',y=.08,z=.40),formbox(.035,.15,.72,'rubber',x=.055,y=.05,z=.40)],[.25,.32,.9],anchor='hinge',material='mat.metal',collision=box_collision([.1,.3,.82],[0,.15,.4]))
    hopper=lathe([[.22,0],[.22,.20],[.61,.87],[.62,.99],[.57,.99],[.56,.88],[.17,.21],[.17,0]],'steel',8,closed_profile=True,position=[0,Q('elevation'),0])
    p('hopper','料斗 · 开口漏斗与卸料颈',[hopper,*legs(.83,.83,add(.75,Q('elevation')),'steel',.075),ring(.27,.10,.05,'metal',position=[0,add(.02,Q('elevation')),0])],[1.24,1.02,1.24],material='mat.metal',params=schema(elevation=number(0,0,1.5,'卸料高度',.05,'m')),collision={'type':'authored-mesh','static_only':True})
    p('pipe','直管 · 中型空心法兰接口',[swept_pipe([[0,0,-.5],[0,0,.5]],.125,.093),*[ring(.19,.097,.055,'metal',position=[0,0,z],rotation=[90,0,0]) for z in [-.4725,.4725]]],[.38,.38,1],anchor='center',ports=axis_ports(F,1,diameter=.25),material='mat.metal',collision={'type':'capsule','radius':.125,'segment_start':[0,0,-.5],'segment_end':[0,0,.5]})
    arc=[[.5-.5*math.cos(i*math.pi/20),0,-.5+.5*math.sin(i*math.pi/20)] for i in range(11)]
    p('elbow','90度空心弯管 · 连续截面与法兰',[swept_pipe(arc,tangents=[[math.sin(i*math.pi/20),0,math.cos(i*math.pi/20)] for i in range(11)]),ring(.19,.097,.055,'metal',position=[0,0,-.5],rotation=[90,0,0]),ring(.19,.097,.055,'metal',position=[.5,0,0],rotation=[0,0,90])],[.9,.38,.9],anchor='center',ports=[socket('in',[0,0,-.5],[0,0,-1],F,diameter=.25),socket('out',[.5,0,0],[1,0,0],F,diameter=.25,tangent=[0,0,1])],material='mat.metal',collision={'type':'authored-mesh','static_only':True})
    p('tee','T形分流管 · 三向法兰',[swept_pipe([[0,0,-.5],[0,0,.5]]),swept_pipe([[0,0,0],[.5,0,0]]),*[ring(.19,.097,.055,'metal',position=[0,0,z],rotation=[90,0,0]) for z in [-.5,.5]],ring(.19,.097,.055,'metal',position=[.5,0,0],rotation=[0,0,90])],[.9,.38,1.38],anchor='center',ports=[*axis_ports(F,1,diameter=.25),socket('branch',[.5,0,0],[1,0,0],F,diameter=.25,tangent=[0,0,1])],material='mat.metal',description='分支有独立法兰和工程壳体；非流体仿真内腔布尔体。')
    p('valve','闸阀 · 手轮／阀杆／阀体',[formbox(.28,.22,.40,'teal',y=-.11),swept_pipe([[0,0,-.30],[0,0,.30]]),rod([0,.08,0],[0,.44,0],.021,'metal'),ring(.20,.032,.035,'red',position=[0,.45,0]),rod([-.18,.45,0],[.18,.45,0],.015,'red'),rod([0,.45,-.18],[0,.45,.18],.015,'red')],[.4,.59,.6],anchor='center',ports=axis_ports(F,.6,diameter=.25),material='mat.metal')
    p('pump','离心泵 · 蜗壳／电机／底座',[formbox(.72,.08,.42,'steel'),disk(.22,.16,'teal',[-.20,.30,0],16,rotation=[0,0,90]),disk(.15,.44,'indigo',[.10,.24,0],12,rotation=[0,0,90]),*[ring(.156,.009,.017,'steel',position=[x,.24,0],rotation=[0,0,90]) for x in [-.02,.04,.10,.16,.22]],swept_pipe([[-.35,.30,0],[-.50,.30,0]],.125,.093),rod([-.2,.43,0],[-.2,.60,0],.11,'teal')],[1,.73,.44],ports=[socket('intake',[-.5,.3,0],[-1,0,0],F,diameter=.25,tangent=[0,0,1]),socket('outlet',[-.2,.60,0],[0,1,0],F,diameter=.25)],material='mat.metal',collision=box_collision([1,.65,.5]))
    p('tank','立式储罐 · 碟形罐顶与巡检梯',[lathe([[.50,.20],[.68,.38],[.68,2.10],[.54,2.32],[.24,2.40],[0,2.40]],'metal',20,cap=True),*legs(.85,.85,.4,'steel',.10),*[rod([x,.15,.73],[x,2.2,.73],.019,'steel') for x in [-.15,.15]],*[rod([-.15,y,.73],[.15,y,.73],.016,'steel',sides=6) for y in [.22,.45,.68,.91,1.14,1.37,1.60,1.83,2.06]]],[1.4,2.4,1.6],material='mat.metal',collision={'type':'capsule','radius':.68,'segment_start':[0,.65,0],'segment_end':[0,1.75,0]},params=schema(detail=DETAIL),lod=authored_lod())
    PARTS[ip('tank')]['shape_params']['forms'][-9:]=optional(PARTS[ip('tank')]['shape_params']['forms'][-9:])
    p('press','冲压机架 · 开放加工窗口',[formbox(1.15,.24,.85,'steel'),*[formbox(.20,1.64,.70,'teal',x=x,y=.24) for x in [-.47,.47]],formbox(1.16,.31,.84,'teal',y=1.88),formbox(.71,.12,.61,'metal',y=.55),*[rod([x,.74,.18],[x,1.95,.18],.035,'metal') for x in [-.30,.30]],formbox(.13,.30,.12,'safety',x=.68,y=1.18)],[1.50,2.2,.85],material='mat.metal',collision=opening_collision(1.16,2.2,.84,.20))
    p('ram','机床压头 · 独立线性行程',[formbox(.69,.20,.61,'safety'),formbox(.18,.60,.18,'metal',y=.20),formbox(.31,.12,.32,'steel',y=-.12)],[.69,.92,.61],anchor='hinge',material='mat.metal',collision=box_collision([.69,.20,.61]))
    p('transformer','配电变压器 · 散热片与瓷套管',[formbox(.95,1.05,.75,'steel',y=.18),*legs(.68,.48,.18,'steel',.08),*[formbox(.04,.89,.94,'metal',x=x,y=.23) for x in [-.54,-.45,.45,.54]],*[lathe([[.035,0],[.065,.05],[.035,.08],[.065,.13],[.035,.17],[.035,.25]],'linen',8,position=[x,1.24,0],cap=True) for x in [-.30,0,.30]]],[1.16,1.53,.94],material='mat.metal',collision=box_collision([1.16,1.24,.94]))
    p('switchgear','配电柜 · 仪表／把手／通风片',[*cabinet(.85,1.72,.52,'linen'),formbox(.24,.15,.025,'glass',x=-.16,y=1.27,z=.29),*[disk(.025,.013,col,[x,1.1,.30],8,rotation=[90,0,0]) for x,col in [(-.22,'red'),(-.12,'leaf')]],*[formbox(.61,.015,.015,'steel',y=.18+i*.06,z=.29) for i in range(4)]],[.85,1.72,.62],material='mat.paint',collision=box_collision([.85,1.72,.60]))
    p('cooling_tower','冷却塔壳 · 双曲轮廓与空心排气口',[lathe([[.90,.25],[.84,.50],[.63,1.40],[.64,1.80],[.78,2.38],[.72,2.38],[.58,1.80],[.57,1.40],[.78,.50],[.84,.25]],'stoneLight',20,closed_profile=True),*legs(1.12,1.12,.40,'stoneDark',.14)],[1.8,2.4,1.8],material='mat.stone',collision={'type':'authored-mesh','static_only':True})
    p('treatment_pool','水处理槽 · 清空水池体',[formbox(2.7,.16,2.2,'stone'),*[formbox(.16,.82,2.2,'stoneLight',x=x,y=.16) for x in [-1.27,1.27]],*[formbox(2.38,.82,.16,'stoneLight',y=.16,z=z) for z in [-1.02,1.02]],formbox(2.36,.025,1.86,'water',y=.53,material='mat.water'),beam([-1.2,.98,0],[1.2,.98,0],.08,.28,'steel')],[2.7,.98,2.2],material='mat.stone',collision={'type':'compound','shapes':[box_collision([2.7,.16,2.2]),box_collision([.16,.82,2.2],[-1.27,.57,0]),box_collision([.16,.82,2.2],[1.27,.57,0]),box_collision([2.38,.82,.16],[0,.57,-1.02]),box_collision([2.38,.82,.16],[0,.57,1.02])]})
    p('drill_head','采矿钻具 · 螺旋切削冠',[lathe([[.24,0],[.26,.12],[.20,.23],[.17,.42],[.11,.58],[.04,.70]],'metal',12,cap=True),*[box([.10,.08,.13],'steel',[.22*math.cos(i*.85),.06+i*.055,.22*math.sin(i*.85)],bevel=.008,rotation=[0,-math.degrees(i*.85),0]) for i in range(10)]],[.62,.72,.62],anchor='hinge',material='mat.metal',collision={'type':'capsule','radius':.26,'segment_start':[0,.15,0],'segment_end':[0,.43,0]})
    a('conveyor_run','直线滚筒链 · 三段精确接口',[pi('first',ip('roller_conveyor')),mate('next',ip('roller_conveyor'),'first'),mate('last',ip('roller_conveyor'),'next')],ports=[exported('first','in','in'),exported('last')])
    a('conveyor_bend','转弯输送工位',[pi('bend',ip('conveyor_corner')),pi('feed',ip('roller_conveyor'),[0,0,2.42]),pi('out',ip('roller_conveyor'),[2.42,0,0],rot=[0,90,0])])
    a('conveyor_lift','升降输送台 · 带平移动画',[pi('frame',ip('lift_frame')),pi('platform',ip('roller_conveyor'),[0,-.59,0],scale=[1,1,.46])],metadata=controls(slider('lift','升降行程','platform',0,1.5)))
    motion(ia('conveyor_lift'),'platform',values=[0,0,1.5,1.5,0],mode='translation',name='Conveyor lift')
    a('sorting_gate','输送分拣挡臂',[pi('line',ip('roller_conveyor')),pi('gate',ip('diverter'),[-.40,.87,-.3])],metadata=controls(turn('sort','分拣方向','gate',0,58)))
    a('pipe_run','管线测试段 · 直管与弯头法兰吸附',[pi('straight',ip('pipe'),[0,1,0]),mate('bend',ip('elbow'),'straight'),mate('out',ip('pipe'),'bend')],ports=[exported('straight','in','in'),exported('out')])
    a('valve_manifold','三通阀组 · 三向分流接口',[pi('tee',ip('tee'),[0,1,0]),mate('inlet',ip('valve'),'tee','out','in'),mate('outlet',ip('valve'),'tee'),mate('branch',ip('valve'),'tee','in','branch')],ports=[exported('inlet','in','in'),exported('outlet'),exported('branch','out','branch')])
    a('pump_skid','双泵基座与阀组',[pi('pumpA',ip('pump'),[0,0,-.6]),pi('pumpB',ip('pump'),[0,0,.6]),ai('manifold',ia('valve_manifold'),[-.8,-.7,0])])
    a('press_cell','冲压工位 · 开口机架与移动压头',[pi('frame',ip('press')),pi('ram',ip('ram'),[0,1.25,0]),pi('power',ip('switchgear'),[1.25,0,-.4])],metadata=controls(slider('press','压头下行','ram',-.6,0)))
    motion(ia('press_cell'),'ram',values=[0,-.6,-.6,0],mode='translation',name='Press cycle')
    a('power_bay','变电单元 · 柜体与变压器',[pi('transformer',ip('transformer')),pi('cab',ip('switchgear'),[1.25,0,0])])
    a('cooling_cell','储罐冷却单元',[pi('tank',ip('tank'),[-1,0,0]),pi('cooler',ip('cooling_tower'),[1.2,0,0]),ai('pump',ia('pump_skid'),[0,0,1.9])])
    a('filter_cell','池槽过滤单元',[pi('pool',ip('treatment_pool')),pi('tank',ip('tank'),[2.4,0,0]),pi('pump',ip('pump'),[1.8,0,1.25])])
    a('drill_rig','钻探机架 · 独立钻具与送料斗',[pi('mast',ip('lift_frame')),pi('spindle',ip('drill_head'),[0,.9,.05],rot=[180,0,0]),pi('feed',ip('hopper'),[1.25,0,0])],metadata=controls(turn('spin','钻具旋转','spindle',0,360),slider('depth','钻进深度','spindle',-.5,.5)))
    motion(ia('drill_rig'),'spindle',values=[0,90,180,270,360],seconds=2,name='Drill spin')
    a('production_line','小型生产线 · 送料／加工／分拣',[pi('hopper',ip('hopper'),[0,0,-3.7],params={'elevation':1.0}),ai('feed',ia('conveyor_run')),ai('machine',ia('press_cell'),[1.8,0,1.8]),ai('sort',ia('sorting_gate'),[0,0,4])],level=3)
    a('substation','配电站 · 安全间距与维护通道',[*[ai('bay'+str(i),ia('power_bay'),[x,0,0]) for i,x in enumerate([-2.5,0,2.5])],*[pi('barrier'+str(i),'exp.interior.queue_barrier',[x,0,2]) for i,x in enumerate([-2.5,-1.1,.3,1.7,3.1])]],level=3)
    a('pump_station','泵站 · 双泵与储罐管线',[ai('pumps',ia('pump_skid')),pi('tank',ip('tank'),[0,0,-2]),ai('pipes',ia('pipe_run'),[-1.1,0,-.7]),pi('controls',ip('switchgear'),[1.5,0,.3])],level=3)
    a('water_treatment','水处理模块 · 双池与过滤罐',[ai('filter',ia('filter_cell')),pi('second',ip('treatment_pool'),[0,0,3]),ai('cool',ia('cooling_cell'),[4.8,0,1.4])],level=3)
    a('mining_face','采矿工作面 · 钻探／落料／转运',[ai('rig',ia('drill_rig'),[-1,0,-1]),pi('hopper',ip('hopper'),[1.4,0,-1],params={'elevation':1.0}),ai('belt',ia('conveyor_bend'),[1.4,0,0]),pi('power',ip('switchgear'),[-2.2,0,1])],level=3)
    a('loading_dock','仓库装卸工位 · 升降衔接与货架',[ai('lift',ia('conveyor_lift'),[0,0,2.4]),ai('line',ia('conveyor_run'),[0,0,-1]),ai('storage','exp-interior-warehouse_bay',[2.8,0,0]),pi('power',ip('switchgear'),[-1.2,0,1.6])],level=3)
    finish_counts(D)
