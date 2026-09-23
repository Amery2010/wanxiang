"""Ground, rail, air and water transport. All dimensions are metres, front +Z."""
from .production import *
D='transport'
def p(k,n,f,s,**kw):return dp('transport.'+k,n,'vehicle',f,s,D,theme=kw.pop('theme','transport'),**kw)
def a(k,n,items,**kw):return da('transport-'+k,n,'vehicle',items,D,theme=kw.pop('theme','transport'),**kw)
def ip(k):return 'exp.transport.'+k
def ia(k):return 'exp-transport-'+k
G=1.435

def wheelset(zs,width=1.78,r=.36,prefix='wheel'):
 return [pi(prefix+str(j)+str(s),ip('wheel'),[s*width/2,r,z],params={'radius':r}) for j,z in enumerate(zs) for s in [-1,1]]
def road_controls():return controls({'id':'steer','title':'前轮转向','nodes':['wheel0-1','wheel01'],'axis':[0,1,0],'min':-25,'max':25,'default':0,'unit':'°'})

def author():
    side=[[-2.12,.42],[-2.12,.96],[-1.2,1.0],[-.78,1.67],[.95,1.67],[1.52,1.07],[2.12,.91],[2.12,.42]]
    for c in [1.27,-1.22]:side += [[c+.43,.42]]+[[c+.43*math.cos(i*math.pi/12),.42+.43*math.sin(i*math.pi/12)] for i in range(13)]+[[c-.43,.42]]
    body=[extrude(side,1.62,'teal',rotation=[0,-90,0]),box([1.36,.065,1.56],'teal',[0,1.685,-.05],bevel=.035),poly([[-.72,1.09,1.48],[.72,1.09,1.48],[.67,1.61,.94],[-.67,1.61,.94]],[[0,1,2,3]],'glass',material='mat.vehicleGlass')]
    for sg in [-1,1]:
        body += [poly([[sg*.817,1.1,.83],[sg*.817,1.59,.82],[sg*.817,1.59,-.71],[sg*.817,1.1,-1.06]],[[0,1,2,3]],'glass',material='mat.vehicleGlass'),formbox(.023,.56,.048,'charcoal',x=sg*.828,y=1.07,z=.03),formbox(.025,.028,.15,'metal',x=sg*.842,y=.99,z=.24)]
    p('utility_body','紧凑SUV车体 · 真实轮拱与高顶轮廓',body,[1.74,1.74,4.24],material='mat.paint',collision={'type':'compound','shapes':[box_collision([1.62,.53,4.24],[0,.72,0]),box_collision([1.48,.7,1.8],[0,1.36,0])]})
    cab=[formbox(1.90,.52,1.52,'linen',y=.55),formbox(1.76,.08,1.32,'linen',y=2.0),formbox(1.82,.96,.06,'linen',y=1.07,z=-.71),poly([[-.91,1.09,.78],[.91,1.09,.78],[.82,1.99,.59],[-.82,1.99,.59]],[[0,1,2,3]],'glass',material='mat.vehicleGlass'),*[beam([s*.94,1.03,.78],[s*.86,2.04,.6],.065,.06,'linen') for s in [-1,1]],*[poly([[s*.947,1.12,-.63],[s*.87,1.95,-.62],[s*.87,1.95,.49],[s*.947,1.12,.62]],[[0,1,2,3]],'glass',material='mat.vehicleGlass') for s in [-1,1]],formbox(.95,.23,.055,'charcoal',y=.76,z=.79),*[formbox(.04,.05,1.23,'linen',x=s*.947,y=1.06,z=-.03) for s in [-1,1]]]
    p('utility_cab','特种作业驾驶室 · 贯通玻璃与立柱',cab,[1.95,2.08,1.64],material='mat.paint',collision=box_collision([1.9,1.5,1.6],[0,1.32,0]))
    r=Q('radius')
    tire=lathe([[mul(r,.68),-.13],[mul(r,.90),-.13],[r,-.07],[r,.07],[mul(r,.90),.13],[mul(r,.68),.13]],'rubber',20,closed_profile=True,rotation=[0,0,90])
    rim=lathe([[mul(r,.65),-.115],[mul(r,.75),-.115],[mul(r,.75),.115],[mul(r,.65),.115]],'metal',16,closed_profile=True,rotation=[0,0,90])
    wf=[tire,rim,disk(mul(r,.20),.26,'steel',[0,0,0],12,rotation=[0,0,90])]
    wf += [rod([0,0,0],[0,mul(r,.70*math.sin(t)),mul(r,.70*math.cos(t))],.038,'metal',sides=6,enabled=Q('detail')) for t in [i*math.tau/6 for i in range(6)]]
    p('wheel','公路车轮 · 空心轮毂与六辐条',wf,[.30,.72,.72],anchor='center',ports=[socket('axle',[0,0,0],[1,0,0],'vehicle.wheel.v1',tangent=[0,0,1])],params=schema(radius=number(.36,.20,.70,'轮胎半径',.01,'m'),detail=DETAIL),material='mat.rubber',lod=authored_lod(),collision={'type':'convex-hull','source':'resolved wheel geometry'})
    p('suspension','实心桥悬架 · 差速器与板簧',[rod([-.86,0,0],[.86,0,0],.055,'steel'),ico([.27,.22,.25],'steel',distort=0),*[beam([s*.60,-.06,-.35],[s*.60,.01,0],.045,.02,'metal') for s in [-1,1]],*[beam([s*.60,.01,0],[s*.60,-.06,.35],.045,.02,'metal') for s in [-1,1]]],[1.72,.24,.70],anchor='center',ports=[socket('left',[-.86,0,0],[-1,0,0],'vehicle.wheel.v1',tangent=[0,0,1]),socket('right',[.86,0,0],[1,0,0],'vehicle.wheel.v1',tangent=[0,0,1])],material='mat.metal')
    p('signal_bar','特种车辆信号组件 · 分区灯罩与支架',[formbox(1.32,.055,.23,'steel'),formbox(.45,.13,.21,'red',x=-.41,y=.055,material='mat.tailLight'),formbox(.45,.13,.21,'blue',x=.41,y=.055,material='mat.light'),formbox(.30,.13,.21,'linen',y=.055),*[formbox(.06,.09,.18,'charcoal',x=x,y=-.09) for x in [-.44,.44]]],[1.32,.28,.23],material='mat.paint')
    p('trailer_deck','低平板拖车 · 双纵梁与三角牵引架',[formbox(2.1,.10,3.9,'oak',y=.64),*[formbox(.11,.21,3.8,'steel',x=x,y=.42) for x in [-.7,.7]],beam([-.68,.51,1.9],[0,.51,3.0],.1,.1,'steel'),beam([.68,.51,1.9],[0,.51,3.0],.1,.1,'steel'),ring(.11,.05,.09,'steel',position=[0,.51,3.08])],[2.1,.75,5.2],material='mat.metal',collision=box_collision([2.1,.16,3.9],[0,.65,0]))
    # I-section rails: 1.435m between their inside faces (head width 0.07m).
    rail_x=(G+.07)/2
    def straight_rail(x,length=4):return [formbox(.14,.025,length,'steel',x=x,y=.17,bevel=0),formbox(.024,.105,length,'metal',x=x,y=.195,bevel=0),formbox(.07,.038,length,'metal',x=x,y=.30,bevel=0)]
    rf=[*[formbox(2.42,.14,.21,'woodDark',z=z) for z in [-1.8,-1.2,-.6,0,.6,1.2,1.8]],*[f for x in [-rail_x,rail_x] for f in straight_rail(x)]]
    p('rail_straight','标准轨直段 · 工字轨与枕木',rf,[2.42,.338,4],theme='rail',material='mat.metal',ports=axis_ports('rail.standard.v1',4,height=.338,gauge=G),collision={'type':'authored-mesh','static_only':True})
    # 12m centreline radius, 30 degree curve. Exact endpoint frames are exported.
    paths=lambda rr:[[12-rr*math.cos(t),.338,rr*math.sin(t)] for t in [i*math.pi/72 for i in range(13)]]
    curve=[strip(paths(12+s*rail_x),.07,'metal',.10,tangents=[[math.sin(i*math.pi/72),0,math.cos(i*math.pi/72)] for i in range(13)]) for s in [-1,1]]
    for j in range(11):
        t=j*math.pi/60;curve.append(box([2.42,.14,.21],'woodDark',[12-12*math.cos(t),.07,12*math.sin(t)],bevel=.008,rotation=[0,math.degrees(t),0]))
    p('rail_curve','标准轨30度曲线 · 连续同心轨面',curve,[3.3,.338,6.6],theme='rail',material='mat.metal',ports=[socket('in',[0,.338,0],[0,0,-1],'rail.standard.v1',gauge=G),socket('out',[12-12*math.cos(math.pi/6),.338,6],[.5,0,math.sqrt(3)/2],'rail.standard.v1',gauge=G,tangent=[math.sqrt(3)/2,0,-.5])],collision={'type':'authored-mesh','static_only':True})
    switch=[*[formbox(2.6+i*.075,.14,.20,'woodDark',x=i*.035,z=-2.7+i*.45) for i in range(13)],*[f for x in [-rail_x,rail_x] for f in straight_rail(x,6)]]
    branch_path=[[0,.338,-3],[.1,.338,-1],[.6,.338,1],[1.5,.338,3]]
    branch_dirs=[endpoint_normal(branch_path[max(0,j-1)],branch_path[min(3,j+1)]) for j in range(4)]
    for sg in [-1,1]:
        line=[[v[0]+sg*rail_x*d[2],v[1],v[2]-sg*rail_x*d[0]] for v,d in zip(branch_path,branch_dirs)]
        switch.append(strip(line,.07,'metal',.10,tangents=branch_dirs))
    p('rail_switch','铁路道岔 · 分支线路与尖轨',switch,[4.3,.338,6],theme='rail',material='mat.metal',ports=[*axis_ports('rail.standard.v1',6,height=.338,gauge=G),socket('branch',[1.5,.338,3],[.410364677,0,.911921506],'rail.standard.v1',gauge=G,tangent=[.911921506,0,-.410364677])],collision={'type':'authored-mesh','static_only':True},description='静态轨道资产与三出口路径；不包含铁路信号联锁逻辑。')
    bogie=[formbox(1.62,.20,1.50,'steel',y=.57),*[rod([-.85,.39,z],[.85,.39,z],.075,'steel') for z in [-.51,.51]]]
    for z in [-.51,.51]:
        for sg in [-1,1]:bogie += [disk(.36,.105,'steel',[sg*.786,.39,z],18,rotation=[0,0,90]),disk(.39,.025,'metal',[sg*.726,.39,z],18,rotation=[0,0,90]),disk(.15,.145,'charcoal',[sg*.793,.39,z],12,rotation=[0,0,90])]
    p('rail_bogie','铁路转向架 · 两轴轮缘与轴箱',bogie,[1.8,.78,1.52],theme='rail',material='mat.metal',anchor='center',collision=box_collision([1.8,.72,1.6]))
    loco=[formbox(2.16,.20,6.4,'steel',y=1.04),formbox(1.47,1.15,3.22,'teal',y=1.24,z=.98),formbox(2.08,1.6,1.72,'teal',y=1.24,z=-1.60),formbox(2.22,.12,1.96,'linen',y=2.84,z=-1.60),*[formbox(.021,.65,1.04,'glass',x=s*1.052,y=2.07,z=-1.6,material='mat.vehicleGlass') for s in [-1,1]],formbox(1.54,.65,.025,'glass',y=2.06,z=-.731,material='mat.vehicleGlass'),*[formbox(.022,.66,.055,'steel',x=s*.75,y=1.53,z=z) for s in [-1,1] for z in [.05,.21,.37,.53,.69,.85,1.01,1.17]],*[rod([s*1.03,1.33,-.64],[s*1.03,1.85,2.82],.025,'metal') for s in [-1,1]],disk(.17,.33,'charcoal',[0,2.55,1.2],12)]
    p('locomotive_body','调车机车上车体 · 短罩与偏置驾驶室',loco,[2.3,3.03,6.4],theme='rail',material='mat.paint',collision=box_collision([2.2,1.9,6.4],[0,2,0]),params=schema(detail=DETAIL),lod=authored_lod())
    PARTS[ip('locomotive_body')]['shape_params']['forms'][8:24]=optional(PARTS[ip('locomotive_body')]['shape_params']['forms'][8:24])
    wagon=[formbox(2.18,.18,6.0,'steel',y=1.04),*[formbox(.095,1.28,6,'red',x=x,y=1.22) for x in [-1.04,1.04]],*[formbox(2,1.28,.095,'red',y=1.22,z=z) for z in [-2.95,2.95]],*[formbox(.065,1.30,.09,'steel',x=s*1.11,y=1.2,z=z) for s in [-1,1] for z in [-2.6,-1.55,-.52,.52,1.55,2.6]]]
    p('freight_body','敞口货运车厢 · 开放装载腔',wagon,[2.3,2.5,6],theme='rail',material='mat.paint',collision={'type':'compound','shapes':[box_collision([2.18,.18,6],[0,1.13,0]),*[box_collision([.095,1.28,6],[x,1.86,0]) for x in [-1.04,1.04]],*[box_collision([2,1.28,.095],[0,1.86,z]) for z in [-2.95,2.95]]]})
    coach=[formbox(2.32,.18,8.6,'steel',y=1.05),formbox(2.40,.18,8.7,'linen',y=3.02),*[formbox(.09,.70,8.6,'indigo',x=s*1.15,y=1.23) for s in [-1,1]],*[formbox(.08,.13,8.6,'linen',x=s*1.15,y=2.90) for s in [-1,1]],*[formbox(2.32,1.82,.07,'indigo',y=1.23,z=z) for z in [-4.25,4.25]]]
    for sg in [-1,1]:
        for i in range(8):coach += [formbox(.08,.98,.105,'linen',x=sg*1.15,y=1.92,z=-3.87+i*1.08),formbox(.018,.84,.86,'glass',x=sg*1.15,y=1.99,z=-3.39+i*1.08,material='mat.vehicleGlass')]
    p('passenger_body','客运车厢 · 窗柱与分段车窗',coach,[2.42,3.22,8.7],theme='rail',material='mat.paint',collision=box_collision([2.42,2.17,8.7],[0,2.13,0]))
    runway=[formbox(24,.12,12,'asphalt',y=-.12),*[formbox(.13,.008,11.8,'line',x=x) for x in [-10.5,10.5]],formbox(.25,.010,3,'line',z=2.0),*[formbox(.55,.011,3,'line',x=x,z=-3.0) for x in [-8,-6.5,-5,-3.5,3.5,5,6.5,8]]]
    p('runway','跑道阈值模块 · 程序标线与端面网格',runway,[24,.132,12],theme='airport',material='mat.stone',ports=axis_ports('arch.floor.1m.v1',12,span=24),collision=box_collision([24,.12,12],[0,-.06,0]))
    cart=[formbox(1.4,.10,2.2,'steel',y=.45),*[formbox(.05,.65,2.2,'safety',x=x,y=.55) for x in [-.66,.66]],tube([[-.66,.52,1],[-.66,1.17,1],[.66,1.17,1],[.66,.52,1]],.025,'steel',8),beam([0,.45,1.1],[0,.40,1.9],.05,.05,'steel'),ring(.075,.028,.035,'steel',position=[0,.40,1.94])]
    p('baggage_cart','航空行李拖车 · 开放装载与牵引环',cart,[1.4,1.22,3.2],theme='airport',material='mat.metal',collision=box_collision([1.4,.13,2.2],[0,.49,0]))
    fuselage=[loft([[0,.98,-2.7,.06,.08],[0,1.06,-2.1,.19,.24],[0,1.17,-.9,.39,.43],[0,1.17,.7,.43,.46],[0,1.10,1.65,.32,.32],[0,1.08,2.28,.065,.08]],'linen',12),box([.62,.35,.78],'glass',[0,1.49,.35],bevel=.13,material='mat.vehicleGlass'),extrude([[-.72,0],[.39,0],[-.14,1.1],[-.6,1.1]],.095,'teal',rotation=[0,90,0],position=[0,1.05,-2.02])]
    p('fuselage','轻型飞机机身 · 收束机尾与垂尾',fuselage,[.88,2.2,5.1],theme='airport',material='mat.paint',collision={'type':'capsule','radius':.42,'segment_start':[0,1.17,-2],'segment_end':[0,1.17,1.6]},params=schema(detail=DETAIL),lod=authored_lod())
    PARTS[ip('fuselage')]['shape_params']['forms'][1]['enabled']=Q('detail')
    wing=topo([[0,-.07,-.64],[3,-.035,-.39],[3,.025,.08],[0,.09,.58],[0,.01,-.64],[3,.035,-.39],[3,.065,.08],[0,.16,.58]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'teal')
    left=deepcopy(wing);left['points']=[[-v[0],v[1],v[2]] for v in wing['points']];left['faces']=[f[::-1] for f in wing['faces']]
    rightmark=rod([.8,.10,-.34],[2.70,.046,-.20],.009,'linen',sides=4)
    leftmark=rod([-.8,.10,-.34],[-2.70,.046,-.20],.009,'linen',sides=4)
    for f in [wing,rightmark]:f['enabled']={'$switch':'side','cases':{'right':True,'left':False}}
    for f in [left,leftmark]:f['enabled']={'$switch':'side','cases':{'right':False,'left':True}}
    p('wing','渐缩机翼 · 左右对称保持相同翼型',[wing,left,rightmark,leftmark],[3.1,.23,1.22],anchor='hinge',theme='airport',material='mat.paint',params=schema(side={'type':'string','enum':['right','left'],'default':'right','title':'安装侧'}),collision={'type':'convex-hull','source':'resolved wing outline; authored mirror is not another catalogue ID'})
    helicopter=[loft([[0,1.1,-.95,.34,.38],[0,1.12,-.2,.67,.56],[0,1.12,.8,.57,.52],[0,1.05,1.28,.20,.23]],'signal',12),ico([1.08,.75,1.0],'glass',[0,1.3,.72],distort=0,material='mat.vehicleGlass'),loft([[0,1.35,-.72,.22,.22],[0,1.45,-2.5,.10,.10],[0,1.56,-3.5,.045,.06]],'signal',8),*[tube([[s*.69,.13,-.8],[s*.69,.13,1.06],[s*.69,.20,1.3]],.035,'steel',8) for s in [-1,1]],*[beam([s*.30,.70,z],[s*.69,.16,z],.035,.035,'steel') for s in [-1,1] for z in [-.55,.73]]]
    p('helicopter_cabin','轻型直升机机体 · 座舱／尾梁／滑橇',helicopter,[1.47,1.75,4.9],theme='airport',material='mat.paint',collision={'type':'compound','shapes':[box_collision([1.2,1.15,2.3],[0,1,.2]),box_collision([.3,.25,2.5],[0,1.43,-2.2])]})
    # Transom to pointed bow. Interior shell made with closed perimeter ring topology.
    sections=[(-2.2,.9),(-1.5,1.04),(.8,1.04),(1.8,.66),(2.5,.08)]
    points=[];faces=[]
    for z,w in sections:
        points += [[-w,.76,z],[-w*.72,.12,z],[w*.72,.12,z],[w,.76,z],[w-.055,.74,z],[max(.02,w*.72-.05),.20,z],[-max(.02,w*.72-.05),.20,z],[-w+.055,.74,z]]
    for j in range(len(sections)-1):
        for i in range(8):faces.append([j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i])
    faces.extend([list(range(7,-1,-1)),list(range(32,40))])
    # The curved shell is topologically closed, while the boat's deck opening remains empty.
    boat=poly(points,faces,'teal')
    p('boat_hull','硬舷机动船体 · V形船底与开放甲板', [boat,*[rod([-w,.78,z],[w,.78,z],.035,'oak') for z,w in [(-2.2,.9)]]],[2.12,.80,4.7],theme='transport',material='mat.paint',collision={'type':'convex-hull','source':'outer hull envelope, not cockpit navigation'})
    p('dock_ramp','码头坡道 · 桥头铰轴与防滑横条',[box([1.8,.14,3.2],'wood',[0,-.07,1.6],bevel=.015),*[box([1.77,.025,.045],'woodDark',[0,.017,z],bevel=.004) for z in [.2,.55,.90,1.25,1.60,1.95,2.30,2.65,3.0]],*[beam([x,0,0],[x,.88,0],.05,.05,'steel') for x in [-.85,.85]],*[beam([x,.88,0],[x,.88,3.15],.05,.05,'steel') for x in [-.85,.85]]],[1.86,1.05,3.2],anchor='hinge',material='mat.wood',collision=box_collision([1.8,.14,3.2],[0,-.07,1.6]))
    # Functional transport subassemblies, not colour variants.
    a('suv_chassis','SUV滚动底盘',[pi('shell',ip('utility_body')),*wheelset([1.27,-1.22]),pi('axleA',ip('suspension'),[0,.36,1.27]),pi('axleB',ip('suspension'),[0,.36,-1.22])],metadata=road_controls())
    a('utility_chassis','通用特种作业底盘',[pi('cab',ip('utility_cab'),[0,0,1.40]),pi('chassis','w.vehicle.truck_chassis',params={'length':5.4}),*wheelset([1.5,-1.75],1.92,.43)],metadata=road_controls())
    a('flatbed_trailer','平板拖车总成 · 独立牵引端',[pi('deck',ip('trailer_deck')),*wheelset([-.8,-1.5],1.98,.34)])
    a('rail_run','标准轨直线组 · 12米接口验证',[pi('first',ip('rail_straight')),mate('second',ip('rail_straight'),'first'),mate('third',ip('rail_straight'),'second')],ports=[exported('first','in','in'),exported('third')],theme='rail')
    a('rail_junction','道岔分支模块 · 三向接轨',[pi('switch',ip('rail_switch')),mate('feed',ip('rail_straight'),'switch','out','in'),mate('through',ip('rail_straight'),'switch'),mate('diverging',ip('rail_straight'),'switch','in','branch')],ports=[exported('feed','in','in'),exported('through'),exported('diverging','out','branch')],theme='rail')
    a('platform','铁路站台段 · 接车高台与引导边',[pi('platform','exp.arch.foundation',[2.8,0,0],scale=[1.3,2.45,1.89]),pi('edge','exp.road.sidewalk',[1.22,1.08,0],rot=[0,90,0]),pi('signal','core.electronics.pedestal',[3,1.08,-1.2],scale=[.38,.65,.38])],theme='rail')
    a('bogie_pair','双转向架承载总成',[pi('front',ip('rail_bogie'),[0,.308,1.98]),pi('back',ip('rail_bogie'),[0,.308,-1.98])],metadata=controls(turn('curve','前转向架回转','front',-18,18)),theme='rail')
    airframe=[pi('body',ip('fuselage')),pi('wingR',ip('wing'),[0,1.02,.15]),pi('wingL',ip('wing'),[0,1.02,.15],params={'side':'left'}),pi('tailR',ip('wing'),[0,1.16,-2],scale=[.38,.7,.55]),pi('tailL',ip('wing'),[0,1.16,-2],params={'side':'left'},scale=[.38,.7,.55]),*wheelset([.20],1.85,.24),pi('tailwheel',ip('wheel'),[0,.20,-1.85],params={'radius':.2})]
    # Reuse the fork-ended actuator rod as a static landing strut. Wheels
    # have real load paths into the belly rather than floating under the wing.
    airframe += [pi('gearstrut'+str(sg),'exp.robot.piston',[sg*.925,.24,.20],rot=[0,0,sg*43.07],scale=[.70,1.75,.70]) for sg in [-1,1]]
    airframe += [pi('tailstrut','exp.robot.piston',[0,.20,-1.85],scale=[.55,.96,.55])]
    a('airframe','轻型机翼身总成 · 渐缩主翼与尾翼',airframe,theme='airport')
    a('rotor','四叶旋翼头 · 径向叶片与铰接轴',[pi('hub','exp.industry.ram',scale=[.22,.38,.22]),*[pi('blade'+str(i),ip('wing'),[0,.35,0],rot=[0,i*90,0],scale=[1.0,.45,.20]) for i in range(4)]],theme='airport')
    a('ground_service','航空地勤拖运组',[pi('cart',ip('baggage_cart')),*wheelset([.72,-.76],1.30,.23),ai('tug',ia('suv_chassis'),[0,0,4.1],scale=[.72,.8,.65])],theme='airport')
    a('boat_deckhouse','机动船上建 · 开放后工作甲板',[pi('hull',ip('boat_hull')),pi('cabin',ip('utility_cab'),[0,.24,.42],scale=[.63,.59,.69]),pi('deck','exp.arch.floor',[0,.29,-.74],scale=[.85,.5,1.13])],theme='transport')
    a('floating_dock','浮动码头 · 三节浮箱与登岸坡道',[*[pi('float'+str(i),'exp.arch.foundation',[0,-.22,z],scale=[1.4,.9,1.15]) for i,z in enumerate([-2.2,0,2.2])],pi('ramp',ip('dock_ramp'),[0,.18,3.4],rot=[-7,0,0])],theme='transport',metadata=controls(turn('tide','坡道角度','ramp',-18,18,[1,0,0])))
    a('ambulance','急救车 · 高顶医疗舱与担架装配',[ai('drive',ia('utility_chassis')),pi('box','w.vehicle.cargo_box',[0,0,-.84],params={'length':3.1,'palette':{C('white'):C('linen')}}),pi('beacon',ip('signal_bar'),[0,2.08,1.4]),pi('bed','exp.interior.hospital_bed',[0,.85,-1],scale=[.80,.80,.9]),pi('rearstep',ip('dock_ramp'),[0,.68,-2.6],rot=[180,0,0],scale=[.72,.5,.25])],level=3)
    a('fire_engine','消防作业车 · 水罐／卷管／车顶梯架',[ai('drive',ia('utility_chassis')),pi('tank','exp.industry.tank',[0,.84,-.8],rot=[90,0,0],scale=[.93,.9,.93]),pi('bed','w.vehicle.open_bed',[0,.30,-1],scale=[1.06,1,1.60]),pi('lamp',ip('signal_bar'),[0,2.08,1.4]),pi('ladder','exp.arch.railing',[0,2.20,-.8],rot=[90,90,0],scale=[1.65,.62,1]),pi('hose','exp.industry.valve',[1.03,1.4,-1.1],rot=[0,90,0])],level=3)
    a('refuse_truck','后装垃圾车 · 料斗／压实上装',[ai('drive',ia('utility_chassis')),pi('body','w.vehicle.cargo_box',[0,0,-.65],params={'length':2.7,'palette':{C('white'):C('teal')}}),pi('hopper','exp.industry.hopper',[0,.85,-2.42],rot=[-32,0,0],scale=[1.42,1.2,1.2]),pi('ram','exp.industry.ram',[0,1.25,-2.45],rot=[90,0,0],scale=[1.6,1.2,1.2])],level=3,metadata=controls(slider('compact','压实装置','ram',0,.35)))
    a('tractor','农业牵引车 · 高后轮与开放驾驶架',[pi('hood',ip('utility_body'),[0,.15,.35],scale=[.63,.58,.60]),pi('seat','p5.rover.seat',[0,.72,-.52],scale=[1.0,1.0,1.0]),pi('cage','p5.rover.roll_cage',[0,0,-.45],scale=[.75,1.1,.7]),*wheelset([1.12],1.4,.34),*wheelset([-.77],1.8,.65,prefix='rear'),pi('hitch',ip('suspension'),[0,.40,-1.42],scale=[.5,.6,.6])],level=3)
    a('shunter','调车机车 · 双转向架与独立回转',[pi('body',ip('locomotive_body')),ai('running',ia('bogie_pair'))],level=3,theme='rail')
    a('freight_wagon','敞口货车 · 可装载车斗',[pi('body',ip('freight_body')),ai('running',ia('bogie_pair'))],level=3,theme='rail')
    a('passenger_coach','客运车厢 · 长车体与两端转向架',[pi('body',ip('passenger_body')),pi('front',ip('rail_bogie'),[0,.308,3.05]),pi('back',ip('rail_bogie'),[0,.308,-3.05])],level=3,theme='rail')
    a('propeller_plane','轻型螺旋桨飞机 · 可动螺旋桨',[ai('airframe',ia('airframe')),ai('propeller',ia('rotor'),[0,1.08,2.30],rot=[90,0,0],scale=[.30,.4,.30])],level=3,theme='airport',metadata=controls(turn('propeller','螺旋桨','propeller',0,360,[0,1,0])))
    motion(ia('propeller_plane'),'propeller',values=[0,90,180,270,360],seconds=1.2,name='Propeller spin')
    a('helicopter','轻型直升机 · 主旋翼与尾桨',[pi('cabin',ip('helicopter_cabin')),ai('rotor',ia('rotor'),[0,1.67,-.15]),ai('tailrotor',ia('rotor'),[.12,1.57,-3.44],rot=[0,0,90],scale=[.20,.24,.20])],level=3,theme='airport',metadata=controls(turn('rotor','主旋翼','rotor',0,360)))
    motion(ia('helicopter'),'rotor',values=[0,90,180,270,360],seconds=1.5,name='Main rotor')
    jet=[pi('body',ip('fuselage'),scale=[1.28,1.1,1.55]),
      *[pi('sweptWing'+str(sg),ip('wing'),[0,1.13,-.18],rot=[0,sg*19,0],scale=[1.28,.8,1.1],params={'side':'right' if sg>0 else 'left'}) for sg in [-1,1]],
      *[pi('highTail'+str(sg),ip('wing'),[0,2.07,-3.15],rot=[0,sg*8,0],scale=[.43,.6,.65],params={'side':'right' if sg>0 else 'left'}) for sg in [-1,1]],
      *[pi('nacelle'+str(sg),'exp.industry.pipe',[sg*.65,1.36,-2.28],scale=[1.7,1.7,1.25]) for sg in [-1,1]],
      *[pi('pylon'+str(sg),'exp.robot.upper_link',[sg*.52,1.30,-2.2],rot=[0,0,sg*90],scale=[.27,.50,.35]) for sg in [-1,1]],
      *wheelset([-.25],2.0,.265),pi('nosewheel',ip('wheel'),[0,.2,2.05],params={'radius':.2})]
    jet += [pi('gearstrut'+str(sg),'exp.robot.piston',[sg*1.0,.265,-.25],rot=[0,0,sg*43.96],scale=[.75,1.813,.75]) for sg in [-1,1]]
    jet += [pi('nosestrut','exp.robot.piston',[0,.20,2.05],scale=[.65,1.39,.65])]
    a('jet','小型喷气机 · 后掠翼／高平尾／双尾吊发动机',jet,level=3,theme='airport')
    a('patrol_boat','沿岸救援艇 · 工作甲板与救援坡道',[ai('boat',ia('boat_deckhouse')),pi('beacon',ip('signal_bar'),[0,1.60,.42],scale=[.7,.8,.8]),pi('ramp',ip('dock_ramp'),[0,.65,-2.22],rot=[0,180,0],scale=[.66,.5,.4])],level=3)
    a('ferry','双体渡船 · 双船体与横向乘客甲板',[pi('hullL',ip('boat_hull'),[-1.32,0,0],scale=[.6,1,1.35]),pi('hullR',ip('boat_hull'),[1.32,0,0],scale=[.6,1,1.35]),pi('deck','exp.arch.floor',[0,.76,-.30],scale=[1.84,1,2.35]),pi('cabin',ip('utility_cab'),[0,.45,1.50],scale=[.8,.7,.8]),*[pi('seat'+str(i),'exp.interior.booth',[x,.77,z],rot=[0,90,0]) for i,(x,z) in enumerate([(-.9,-1.2),(.9,-1.2),(-.9,0),(.9,0)])],pi('ramp',ip('dock_ramp'),[0,.78,-2.65],rot=[0,180,0],scale=[1.2,.75,.65])],level=3)
    finish_counts(D)
