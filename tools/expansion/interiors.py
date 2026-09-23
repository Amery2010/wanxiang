"""Human-scale interiors: usable voids, supported worktops and themed work cells."""
from .production import *
D='interiors'
def p(k,n,f,s,**kw):return dp('interior.'+k,n,'interior',f,s,D,theme='public',**kw)
def a(k,n,items,**kw):return da('interior-'+k,n,'interior',items,D,theme='public',**kw)
def ip(k):return 'exp.interior.'+k
def ia(k):return 'exp-interior-'+k

def author():
    p('base_cabinet','厨房地柜 · 踢脚与双门',[*cabinet(1.2,.82,.6,'medical'),formbox(1.06,.10,.47,'charcoal',y=-.10)],[1.2,.92,.65],material='mat.paint',collision=box_collision([1.2,.92,.6],[0,.36,0]))
    p('wall_cabinet','吊柜 · 分隔层板与背挂件',[*cabinet(.8,.68,.34,'linen',True),formbox(.68,.035,.30,'linen',y=.34),*[formbox(.08,.10,.045,'steel',x=x,y=.58,z=-.19) for x in [-.28,.28]]],[.8,.68,.39],material='mat.paint',collision=box_collision([.8,.68,.34]))
    p('worktop','转角备餐台面 · 独立L形轮廓',[extrude([[-.9,-.65],[.9,-.65],[.9,-.05],[.3,-.05],[.3,.65],[-.9,.65]],.065,'stoneLight',rotation=[90,0,0],position=[0,.0325,0]),formbox(1.8,.08,.04,'stone',y=.065,z=-.66)],[1.8,.145,1.34],material='mat.stone',collision={'type':'authored-mesh','static_only':True})
    basin=lathe([[.33,.05],[.33,.24],[.29,.25],[.265,.20],[.20,.055],[.0,.055],[.0,0],[.25,0]],'white',20,closed_profile=True,scale=[1.35,1,.9])
    p('basin','水槽与弯颈龙头 · 内凹盆腔',[basin,tube([[.31,.22,-.18],[.31,.50,-.18],[.16,.55,-.18],[.11,.47,-.18]],.022,'metal',8),disk(.025,.009,'steel',[0,.063,0],8)],[.90,.58,.60],material='mat.ceramic',collision={'type':'authored-mesh','static_only':True})
    tub=lathe([[.62,.06],[.69,.52],[.66,.57],[.58,.57],[.52,.45],[.43,.14],[0,.14],[0,.06]],'white',20,closed_profile=True,scale=[.70,1,1.40])
    p('bathtub','独立浴缸 · 椭圆内腔',[tub,*legs(.54,1.24,.13,'metal',.09),tube([[.32,.40,-.55],[.32,.78,-.55],[.13,.78,-.55]],.025,'metal',8)],[1.0,.83,2.0],material='mat.ceramic',collision={'type':'authored-mesh','static_only':True})
    p('toilet','坐便器 · 开口坐圈与水箱',[lathe([[.19,0],[.16,.12],[.22,.28],[.29,.38],[.29,.43],[.225,.44],[.17,.30],[.08,.26],[.08,.10],[.10,0]],'white',18,closed_profile=True,scale=[.82,1,1.22]),ring(.28,.056,.025,'linen',position=[0,.445,0],scale=[.86,1,1.24]),formbox(.43,.42,.17,'white',y=.34,z=-.38),formbox(.46,.025,.20,'linen',y=.76,z=-.38),disk(.025,.013,'metal',[.10,.787,-.38],8)],[.50,.81,.94],material='mat.ceramic',collision=box_collision([.5,.8,.94]))
    p('shower_screen','淋浴屏 · 透明隔断与可见骨架',[*frame(.90,1.98,.04,.035,'steel'),formbox(.81,1.89,.016,'glass',y=.045,material='mat.glass'),tube([[.35,.75,-.04],[.35,1.22,-.04]],.016,'metal',8)],[.90,1.98,.10],material='mat.metal',collision=box_collision([.9,1.98,.04]))
    locker=[*cabinet(.46,1.85,.48,'indigo'),*[formbox(.22,.012,.012,'charcoal',y=1.43+j*.06,z=.27) for j in range(4)],formbox(.09,.06,.012,'linen',y=1.7,z=.275)]
    p('locker','更衣储物柜 · 通风槽与铭牌',locker,[.46,1.85,.56],material='mat.paint',collision=box_collision([.46,1.85,.54]))
    p('retail_rack','商业货架 · 开放层板与后撑',[*legs(1.10,.38,1.65,'steel',.045),*[formbox(1.17,.045,.44,'linen',y=y) for y in [.14,.60,1.07,1.60]],beam([-.55,.12,-.18],[.55,1.55,-.18],.026,.026,'steel'),beam([.55,.12,-.18],[-.55,1.55,-.18],.026,.026,'steel'),*[formbox(1.17,.035,.03,'safety',y=y,z=.23) for y in [.18,.64,1.11]]],[1.2,1.68,.49],material='mat.paint',collision={'type':'compound','shapes':[box_collision([1.18,1.68,.46])]},params=schema(detail=DETAIL),lod=authored_lod())
    # Barcode scanner and display are independent silhouettes on the checkout shell.
    p('checkout','收银台 · 收银终端与输送台',[*cabinet(.85,.87,.65,'teal'),formbox(1.65,.06,.74,'charcoal',x=-.3,y=.87),formbox(.08,.32,.08,'steel',x=.26,y=.93,z=-.17),box([.33,.22,.055],'steel',[.26,1.26,-.16],rotation=[-15,0,0]),box([.28,.17,.012],'cyan',[.26,1.26,-.118],rotation=[-15,0,0]),formbox(.20,.045,.20,'glass',x=-.23,y=.933),*legs(.6,.5,.86,'steel',.055)],[1.66,1.40,.74],material='mat.paint',collision=box_collision([1.66,.95,.74],[-.3,.475,0]))
    p('refrigerator','玻璃冷藏展示柜 · 隔层与制冷机仓',[*cabinet(.88,1.86,.60,'white',True),formbox(.75,.26,.54,'charcoal',y=.07),*[formbox(.75,.025,.47,'metal',y=y) for y in [.53,.91,1.29,1.67]],formbox(.74,1.42,.018,'glass',y=.36,z=.313,material='mat.glass'),rod([.30,.9,.355],[.30,1.40,.355],.014,'metal',sides=8)],[.88,1.86,.74],material='mat.paint',collision=box_collision([.88,1.86,.66]))
    p('booth','餐厅卡座 · 坐垫／靠背／基座',[formbox(1.35,.30,.59,'oak',y=.06),box([1.39,.15,.64],'red',[0,.425,.02],bevel=.06),box([1.39,.66,.14],'red',[0,.72,-.27],bevel=.05,rotation=[-6,0,0]),formbox(1.12,.065,.49,'charcoal')],[1.4,1.07,.70],material='mat.fabric',collision={'type':'compound','shapes':[box_collision([1.4,.5,.65]),box_collision([1.4,.66,.15],[0,.74,-.27])]})
    p('dining_table','餐桌 · 斜撑与完整桌面',[formbox(1.20,.055,.76,'oak',y=.72),*legs(.97,.55,.72,'woodDark',.055),beam([-.46,.32,-.25],[.46,.59,-.25],.035,.04,'woodDark')],[1.2,.775,.76],material='mat.wood',collision={'type':'compound','shapes':[box_collision([1.2,.055,.76],[0,.7475,0]),*[box_collision([.06,.72,.06],[x,.36,z]) for x in [-.485,.485] for z in [-.275,.275]]]})
    bed=[formbox(.90,.085,1.98,'steel',y=.40),box([.84,.14,1.91],'linen',[0,.51,0],bevel=.04),box([.70,.13,.40],'white',[0,.65,-.66],bevel=.04),box([.86,.025,1.07],'medical',[0,.594,.37],bevel=.008),*[formbox(.045,.75,.045,'metal',x=x,z=z) for x in [-.47,.47] for z in [-.96,.96]],*[tube([[x,.58,-.72],[x,.82,-.70],[x,.82,.7],[x,.58,.73]],.021,'metal',8) for x in [-.48,.48]],*[disk(.067,.055,'rubber',[x,.095,z],10,rotation=[0,0,90]) for x in [-.43,.43] for z in [-.89,.89]],formbox(.82,.28,.045,'medical',y=.67,z=-1)]
    p('hospital_bed','护理病床 · 护栏／脚轮／床垫',bed,[1.04,1.02,2.10],material='mat.fabric',collision=box_collision([1.04,.86,2.10]),params=schema(detail=DETAIL),lod=authored_lod())
    iv=[rod([0,.10,0],[0,1.85,0],.014,'metal'),tube([[-.25,1.74,0],[-.22,1.89,0],[.22,1.89,0],[.25,1.74,0]],.012,'metal',8),box([.17,.28,.035],'medical',[-.16,1.61,0],bevel=.025),tube([[-.16,1.48,0],[-.14,.98,0],[.15,.87,.10]],.005,'white',6)]
    iv += [rod([0,.12,0],[.29*math.sin(i*math.tau/5),.055,.29*math.cos(i*math.tau/5)],.017,'steel',sides=6) for i in range(5)]
    p('iv_stand','输液架 · 五脚底盘与软管',iv,[.60,1.91,.60],material='mat.metal',collision={'type':'capsule','radius':.03,'segment_start':[0,.04,0],'segment_end':[0,1.85,0]})
    p('medical_cart','医疗推车 · 双层托盘与推柄',[*legs(.54,.35,.82,'metal',.025),*[formbox(.65,.045,.45,'medical',y=y) for y in [.20,.65]],tube([[-.27,.65,-.18],[-.27,.90,-.18],[.27,.90,-.18],[.27,.65,-.18]],.018,'metal',8),*[disk(.042,.035,'rubber',[x,.048,z],8,rotation=[0,0,90]) for x in [-.27,.27] for z in [-.175,.175]]],[.68,.93,.47],material='mat.metal',collision=box_collision([.68,.9,.47]))
    p('school_desk','单人课桌 · 抽屉与脚踏横梁',[formbox(.62,.045,.44,'oak',y=.70),formbox(.52,.12,.34,'indigo',y=.53),*legs(.48,.30,.70,'steel',.028),beam([-.24,.15,.15],[.24,.15,.15],.027,.027,'steel')],[.62,.745,.44],material='mat.wood',collision=box_collision([.62,.74,.44]))
    p('blackboard','课堂黑板 · 粉笔槽与支架',[*frame(2.15,1.1,.08,.055,'oak'),formbox(2.04,.99,.028,'pine',y=.055,z=.047),formbox(2.14,.03,.12,'woodDark',y=-.03,z=.09),*[formbox(.05,.65,.06,'steel',x=x,y=-.65) for x in [-.85,.85]]],[2.15,1.78,.22],anchor='center',material='mat.wood',collision=box_collision([2.15,1.1,.10],[0,.55,0]))
    p('workbench','钳工工作台 · 厚台面／台钳／横撑',[formbox(1.6,.10,.70,'oak',y=.86),*legs(1.3,.5,.86,'steel',.075),formbox(1.35,.06,.52,'woodDark',y=.19),formbox(.23,.10,.20,'steel',x=-.50,y=.96,z=.16),formbox(.21,.15,.045,'metal',x=-.50,y=1.02,z=.30),rod([-.5,1.02,.25],[-.5,1.02,.45],.024,'metal'),rod([-.60,1.02,.45],[-.40,1.02,.45],.015,'charcoal')],[1.6,1.19,.84],material='mat.wood',collision=box_collision([1.6,.96,.7]))
    p('queue_barrier','排队栏杆 · 双柱及悬链',[*[disk(.15,.04,'steel',[x,.02,0],12) for x in [-.55,.55]],*[rod([x,.04,0],[x,.95,0],.027,'metal') for x in [-.55,.55]],tube([[-.55,.91,0],[-.28,.80,0],[0,.77,0],[.28,.80,0],[.55,.91,0]],.016,'red',6)],[1.4,.98,.30],material='mat.metal',collision={'type':'none','reason':'visual queue guide; gameplay supplies crowd constraints'})
    p('service_counter','无障碍服务柜台 · 高低双台面',[*cabinet(1.15,1.04,.62,'teal'),formbox(1.24,.045,.71,'linen',y=1.04),formbox(.90,.045,.67,'linen',x=.99,y=.75),formbox(.065,.75,.56,'teal',x=1.38),formbox(.38,.22,.035,'indigo',y=1.10,z=-.16)],[2.03,1.34,.71],material='mat.paint',collision={'type':'compound','shapes':[box_collision([1.24,1.085,.71]),box_collision([.9,.045,.67],[.99,.7725,0])]})
    tools=[formbox(1.4,1.05,.045,'oak'),*[formbox(.025,.70,.025,'charcoal',x=x,y=.18,z=.038) for x in [-.48,-.16,.16,.48]]]
    for i,x in enumerate([-.48,-.16,.16,.48]):
        tools += [rod([x,.18,.083],[x,.65,.083],.022,'woodLight',sides=6),formbox(.19,.075,.045,'steel',x=x,y=.65,z=.083)]
    p('toolboard','工具墙 · 挂钩与独立手工具',tools,[1.4,1.05,.15],material='mat.wood',collision=box_collision([1.4,1.05,.05]))
    # LOD genuinely removes optional non-structural details, without sealing open furniture.
    PARTS[ip('retail_rack')]['shape_params']['forms'][-3:]=optional(PARTS[ip('retail_rack')]['shape_params']['forms'][-3:])
    PARTS[ip('hospital_bed')]['shape_params']['forms'][-5:-1]=optional(PARTS[ip('hospital_bed')]['shape_params']['forms'][-5:-1])
    a('kitchen_station','洗涤备餐站',[pi('base',ip('base_cabinet')),pi('top',ip('worktop'),[.25,.83,.15]),pi('sink',ip('basin'),[-.20,.91,0]),pi('wall',ip('wall_cabinet'),[0,1.50,-.23])])
    a('bathroom_suite','紧凑卫浴套组',[pi('tub',ip('bathtub'),[-.8,0,0]),pi('screen',ip('shower_screen'),[-.24,0,0],rot=[0,90,0]),pi('toilet',ip('toilet'),[.65,0,-.5]),pi('basin',ip('basin'),[.7,.65,.70]),pi('cabinet',ip('wall_cabinet'),[.7,0,.7],scale=[1,.9,1.3])])
    a('retail_aisle','双面零售货架通道',[pi('left',ip('retail_rack'),[-.8,0,0],rot=[0,90,0]),pi('right',ip('retail_rack'),[.8,0,0],rot=[0,-90,0]),pi('end',ip('refrigerator'),[0,0,-1.1])])
    a('checkout_lane','收银与排队出口',[pi('till',ip('checkout')),pi('barrier',ip('queue_barrier'),[-1.4,0,.25],rot=[0,90,0])])
    a('drink_corner','冷藏饮料角',[pi('cold',ip('refrigerator'),[-.5,0,0]),pi('shelf',ip('retail_rack'),[.65,0,0]),pi('cab',ip('base_cabinet'),[0,0,.8])])
    a('restaurant_table','餐厅双卡座餐位',[pi('table',ip('dining_table')),pi('seatA',ip('booth'),[0,0,-.78]),pi('seatB',ip('booth'),[0,0,.78],rot=[0,180,0])])
    a('hospital_station','床旁护理单元',[pi('bed',ip('hospital_bed')),pi('iv',ip('iv_stand'),[.78,0,-.6]),pi('cart',ip('medical_cart'),[.87,0,.55]),pi('locker',ip('locker'),[-.82,0,-.70])])
    a('waiting_row','候诊长排座位',[pi('seatA',ip('booth'),[-.73,0,0]),pi('seatB',ip('booth'),[.73,0,0]),pi('barrier',ip('queue_barrier'),[0,0,1.1])])
    a('nurse_station','护士服务站',[pi('counter',ip('service_counter')),pi('drug',ip('wall_cabinet'),[-.25,1.15,-.75]),pi('cart',ip('medical_cart'),[.75,0,-.7])])
    a('classroom_row','两人学习单元',[pi('deskA',ip('school_desk'),[-.38,0,0]),pi('deskB',ip('school_desk'),[.38,0,0]),pi('seat',ip('booth'),[0,0,.52],rot=[0,180,0],scale=[.94,.76,.7])])
    a('teacher_station','讲台与演示黑板',[pi('counter',ip('service_counter')),pi('board',ip('blackboard'),[0,1.20,-.95])])
    a('public_service','公共服务等候区',[pi('service',ip('service_counter'),[0,0,-1]),ai('waiting',ia('waiting_row'),[0,0,1]),pi('guide',ip('queue_barrier'),[-1.7,0,0],rot=[0,90,0])])
    a('workbench_cell','工坊工具工位',[pi('bench',ip('workbench')),pi('tools',ip('toolboard'),[0,1.1,-.37]),pi('locker',ip('locker'),[1.13,0,-.05])])
    a('warehouse_bay','仓储周转货架',[pi('rackA',ip('retail_rack'),[-.62,0,0],scale=[1,1.35,1.3]),pi('rackB',ip('retail_rack'),[.62,0,0],scale=[1,1.35,1.3]),pi('pack',ip('workbench'),[0,0,1.35])])
    def flooritems(w=3,d=3):return [pi('floor'+str(i),'exp.arch.floor',[x*2,0,z*2]) for i,(x,z) in enumerate(( (x,z) for x in range(w) for z in range(d))) ]
    a('kitchen','完整厨房 · 洗涤／冷藏／备餐',[*flooritems(2,2),ai('wet',ia('kitchen_station'),[0,0,-.50]),pi('cold',ip('refrigerator'),[1.7,0,-.50]),pi('island',ip('base_cabinet'),[.5,0,1.2]),pi('top',ip('worktop'),[.8,.83,1.2]),pi('locker',ip('locker'),[2.4,0,-.5])],level=3)
    a('shop','小型商店 · 陈列通道与收银出口',[*flooritems(),ai('aisle',ia('retail_aisle'),[1,0,.3]),ai('cold',ia('drink_corner'),[3.6,0,0]),ai('checkout',ia('checkout_lane'),[2.9,0,3.5])],level=3)
    a('restaurant','餐厅角落 · 双卡座与服务边柜',[*flooritems(),ai('tableA',ia('restaurant_table'),[.3,0,1]),ai('tableB',ia('restaurant_table'),[2.2,0,1]),pi('sideboard',ip('base_cabinet'),[3.8,0,-.5]),pi('counter',ip('service_counter'),[3.7,0,3.5])],level=3)
    a('ward','双床病房 · 中央护理通道',[*flooritems(),ai('bedA',ia('hospital_station'),[.2,0,.3]),ai('bedB',ia('hospital_station'),[3,0,.3]),ai('nurse',ia('nurse_station'),[2,0,3.7])],level=3)
    a('classroom','教室 · 教学面与四组课桌',[*flooritems(3,4),ai('teacher',ia('teacher_station'),[2,0,-.2]),*[ai('row'+str(i),ia('classroom_row'),[x,0,z]) for i,(x,z) in enumerate([(0.6,2),(3,2),(.6,4),(3,4)])],*[pi('locker'+str(i),ip('locker'),[4.5,0,i*.52],rot=[0,-90,0]) for i in range(4)]],level=3)
    a('workshop','工坊工作区 · 加工与周转分离',[*flooritems(),ai('workA',ia('workbench_cell'),[0,0,0]),ai('workB',ia('workbench_cell'),[2.5,0,0]),ai('storage',ia('warehouse_bay'),[2,0,3])],level=3)
    finish_counts(D)
