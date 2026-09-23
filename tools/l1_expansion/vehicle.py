"""Transport components only: no complete vehicles, rigs, or physics claims."""
from .common import *
from .industry import gear,elbow


def airfoil(span=1.6,chord=.65,sweep=.2,taper=.55,color='l1Slate'):
    # Closed asymmetric aerofoil prism with independently authored root/tip sections.
    section=[[-.5,0],[-.35,.085],[0,.10],[.5,0],[.1,-.035],[-.35,-.025]]
    pts=[[x,y*chord,z*chord] for x in [0] for z,y in section]
    pts += [[span,y*chord*taper,z*chord*taper-sweep] for z,y in section]
    fs=[list(range(5,-1,-1)),list(range(6,12))]
    for i in range(6):fs += [[i,(i+1)%6,(i+1)%6+6,i+6]]
    return topo(pts,fs,color)


def author():
    def put(g,k,n,fs,sz=(1.6,1.1,1.6),**kw):return register('vehicle',g,k,n,fs,sz,material='mat.metal',**kw)
    chassis=names('ladder_rail:阶梯车架纵梁 spine:脊梁式底架片 wishbone:双叉臂叉体 trailing:纵向摆臂体 leafspring:钢板簧片组 strut:悬挂减振壳 axle:整体桥壳 knuckle:转向节体 subframe:副车架结构片 track_frame:履带侧架片')
    for key,name in chassis:
        if key=='ladder_rail':fs=[plate([[-.8,0],[.8,0],[.8,.16],[.5,.16],[.3,.08],[-.3,.08],[-.5,.16],[-.8,.16]],.12,'l1Slate')]
        elif key=='spine':fs=[loft([[0,0,-.75,.14,.16],[0,.02,0,.22,.20],[0,.04,.75,.12,.16]],'l1Slate',8)]
        elif key=='wishbone':fs=[rod([-.5,0,0],[0,.03,.55],.055,'metal'),rod([.5,0,0],[0,.03,.55],.055,'metal')]+[round_tube(.085,.042,.12,'l1Metal',position=[x,0,0]) for x in [-.5,.5]]
        elif key=='trailing':fs=[plate([[-.1,0],[.12,0],[.28,.68],[.15,.78],[-.03,.60]],.12,'metal'),round_tube(.10,.055,.2,'l1Metal',rotation=[90,0,0],position=[0,.1,.1])]
        elif key=='leafspring':fs=[loft([[x,.20-.17*(1-(x/.75)**2)+i*.018,0,.018,.1] for x in [-.75+i*.12,-.4,0,.4,.75-i*.12]],'metal',4) for i in range(4)]
        elif key=='strut':fs=[round_tube(.12,.075,.55,'l1Slate'),rod([0,.4,0],[0,.9,0],.055,'metal'),ring(.20,.08,.045,'l1Metal',position=[0,.35,0])]
        elif key=='axle':fs=[rod([-.8,.2,0],[.8,.2,0],.10,'l1Slate'),ico([.45,.4,.4],'metal',[0,.2,0],detail=1)]
        elif key=='knuckle':fs=[plate([[-.18,0],[.2,0],[.26,.20],[.12,.5],[-.04,.55],[-.16,.3]],.14,'metal'),round_tube(.14,.07,.25,'l1Metal',rotation=[90,0,0],position=[0,.25,.15])]
        elif key=='subframe':fs=[plate([[-.65,0],[-.38,0],[-.28,.55],[.28,.55],[.38,0],[.65,0],[.45,.75],[-.45,.75]],.13,'l1Slate')]
        else:fs=[plate([[-.8,0],[.75,0],[.9,.30],[.7,.5],[-.6,.5],[-.86,.22]],.22,'l1Slate')]+[round_tube(.08,.035,.12,'metal',rotation=[90,0,0],position=[x,.25,.15]) for x in [-.6,-.2,.2,.6]]
        put('chassis',key,name,fs)
    wheels=names('road_tire:公路胎胎体 allterrain_tire:越野胎胎体 tractor_tire:农机胎胎体 solid_tire:实心缓冲胎体 split_rim:分体轮辋 spoke_hub:辐条轮毂 disc_hub:冲压轮毂 track_shoe:履带板单节 idler:导向轮体 caster_fork:脚轮叉体')
    for key,name in wheels:
        if key.endswith('tire'):
            fs=[lathe([[.28,0],[.40,.05],[.43,.12],[.43,.26],[.4,.33],[.28,.38],[.26,.32],[.26,.06]],'l1Rubber',16,closed_profile=True)]
            if key=='road_tire':fs += [ring(.436,.011,.015,'rubber',position=[0,y,0]) for y in [.14,.20,.26]]
            elif key=='allterrain_tire':fs += [box([.11,.12,.045],'rubber',[.43*math.cos(a),y,.43*math.sin(a)],.008,rotation=[0,-a*180/math.pi+90,0]) for y in [.13,.25] for a in [i*math.tau/12 for i in range(12)]]
            elif key=='tractor_tire':fs += [box([.22,.23,.04],'rubber',[.435*math.cos(a),.2,.435*math.sin(a)],.01,rotation=[0,-a*180/math.pi+90,25]) for a in [i*math.tau/10 for i in range(10)]]
            else:fs += [ring(.34,.055,.10,'l1Ochre',position=[0,.19,0])]
        elif key=='split_rim':fs=[round_tube(.29,.23,.28,'l1Metal'),ring(.34,.11,.04,'metal'),ring(.34,.11,.04,'metal',position=[0,.28,0])]
        elif key=='spoke_hub':fs=[ring(.30,.025,.1,'l1Metal'),round_tube(.06,.025,.15,'metal')]+[rod([0,.07,0],[.285*math.cos(a),.05,.285*math.sin(a)],.016,'l1Metal') for a in [i*math.tau/12 for i in range(12)]]
        elif key=='disc_hub':fs=[ring(.32,.055,.18,'l1Metal'),round_tube(.065,.03,.16,'metal')]+[box([.23,.05,.11],'l1Metal',[.16*math.cos(a),.08,.16*math.sin(a)],.015,rotation=[0,-a*180/math.pi,0]) for a in [i*math.tau/5 for i in range(5)]]
        elif key=='track_shoe':fs=[formbox(.45,.06,.23,'metal'),formbox(.45,.045,.06,'l1Slate',y=.06)]+[round_tube(.032,.014,.1,'l1Metal',rotation=[0,0,90],position=[x,.035,z]) for x,z in [(-.20,-.14),(.20,-.14),(0,.14)]]
        elif key=='idler':fs=[ring(.28,.065,.22,'metal'),disk(.22,.05,'l1Slate',y=.09),round_tube(.075,.034,.24,'l1Metal')]
        else:fs=[formbox(.32,.055,.2,'metal')]+[plate([[-.1,0],[.1,0],[.06,.33],[-.06,.33]],.055,'l1Metal',position=[x,.04,0]) for x in [-.15,.15]]
        put('wheel',key,name,fs,(1,.65,1))
    body=names('hood:发动机舱盖片 fender:轮拱翼子板片 grille:进气格栅芯 bumper:保险杠壳 door:车门外板片 sill:侧裙门槛片 roof:车顶弧片 dashboard:仪表台壳 seat_frame:车辆座椅骨架 cargo_floor:货厢底板片')
    for key,name in body:
        if key=='hood':fs=[loft([[0,0,-.55,.6,.035],[0,.13,0,.62,.04],[0,.04,.55,.5,.03]],'l1Slate',6)]
        elif key=='fender':fs=[arc(.48,.085,0,180,color='l1Slate',n=12,center=[0,0,0])];fs=placed(fs,scale=[1,1,2])
        elif key=='grille':fs=frame(1,.4,.06,.06,'l1Metal')+[formbox(.035,.27,.025,'l1Slate',x=x,y=.065) for x in [-.35,-.25,-.15,-.05,.05,.15,.25,.35]]
        elif key=='bumper':fs=[loft([[-.7,0,-.12,.09,.08],[-.55,.02,.03,.1,.08],[.55,.02,.03,.1,.08],[.7,0,-.12,.09,.08]],'l1Slate',6)]
        elif key=='door':fs=[plate([[-.55,0],[.47,0],[.60,.45],[.36,.74],[-.42,.74],[-.55,.52]],.065,'l1Slate'),formbox(.2,.035,.025,'l1Metal',x=.25,y=.55,z=.045)]
        elif key=='sill':fs=[plate([[-.6,0],[.6,0],[.65,.12],[.55,.20],[-.55,.20],[-.65,.12]],.14,'l1Slate')]
        elif key=='roof':fs=[loft([[0,0,-.6,.46,.025],[0,.17,0,.57,.03],[0,.06,.6,.47,.025]],'l1Slate',8)]
        elif key=='dashboard':fs=[plate([[-.65,0],[.65,0],[.62,.22],[.15,.28],[-.05,.42],[-.52,.42],[-.65,.30]],.3,'l1Rubber'),ring(.12,.025,.03,'l1Metal',rotation=[90,0,0],position=[-.31,.26,.16])]
        elif key=='seat_frame':fs=[rod([x,0,.25],[x,.75,-.18],.035,'metal') for x in [-.25,.25]]+[rod([-.25,y,z],[.25,y,z],.03,'metal') for y,z in [(0,.25),(.3,.1),(.75,-.18)]]
        else:fs=[formbox(1.2,.08,1.4,'l1Slate')]+[formbox(.055,.025,1.4,'metal',x=x,y=.08) for x in [-.5,-.3,-.1,.1,.3,.5]]
        put('body',key,name,fs)
    aero=names('wing:直翼外段 swept_wing:后掠翼外段 delta:三角翼板 flap:襟翼段 aileron:副翼段 fin:垂直尾翼芯 inlet:进气唇口 nacelle:发动机短舱壳 prop_blade:螺旋桨叶片 rotor_blade:旋翼桨叶片')
    for key,name in aero:
        if key=='wing':fs=[airfoil()]
        elif key=='swept_wing':fs=[airfoil(sweep=.8,taper=.35),formbox(.045,.12,.28,'metal',x=1.58,y=.03,z=-.8)]
        elif key=='delta':fs=[plate([[0,0],[1.5,.12],[0,1.2]],.055,'l1Slate',rotation=[90,0,0])]
        elif key=='flap':fs=[airfoil(1,.3,0,.85)]+[formbox(.05,.1,.13,'metal',x=x,y=-.03,z=.12) for x in [.18,.82]]
        elif key=='aileron':fs=[airfoil(.85,.27,.1,.6),formbox(.12,.025,.09,'metal',x=.65,z=-.20)]
        elif key=='fin':fs=[plate([[-.4,0],[.4,0],[.10,1.0],[-.13,1.1]],.075,'l1Slate')]
        elif key=='inlet':fs=[lathe([[.40,0],[.45,.12],[.38,.27],[.29,.27],[.33,.1],[.32,0]],'l1Metal',16,closed_profile=True,rotation=[90,0,0])]
        elif key=='nacelle':fs=[lathe([[.33,0],[.42,.15],[.4,.75],[.25,1.1],[.20,1.1],[.34,.7],[.36,.15],[.28,0]],'l1Slate',16,closed_profile=True,rotation=[90,0,0])]
        elif key=='prop_blade':fs=[loft([[0,0,0,.09,.035],[.08,.35,0,.18,.045],[.18,.9,.06,.13,.027],[.20,1.15,.12,.03,.017]],'l1Slate',6)]
        else:fs=[airfoil(2,.24,.15,.8),round_tube(.06,.03,.18,'metal',position=[0,-.07,0])]
        put('aero',key,name,fs,(2.2,1.3,2))
    marine=names('bow:船艏外板片 keel:船底龙骨片 transom:船艉封板舷片 rib:船体肋骨片 rudder:船舵舵叶 propeller:船用推进叶片 oar_blade:桨叶片 cleat:船用系缆角 fairlead:船用导缆孔框')
    for key,name in marine:
        if key=='bow':fs=[topo([[-.55,0,-.55],[.55,0,-.55],[0,.1,.7],[-.6,.6,-.55],[.6,.6,-.55],[0,.7,.7]],[[0,2,1],[3,4,5],[0,1,4,3],[0,3,5,2],[1,2,5,4]],'l1Slate')]
        elif key=='keel':fs=[plate([[-.7,0],[.7,0],[.5,.55],[-.45,.35]],.10,'l1Slate')]
        elif key=='transom':fs=[plate([[-.45,0],[.45,0],[.65,.65],[-.65,.65]],.08,'l1Slate')]
        elif key=='rib':fs=[loft([[-.6,.6,0,.045,.045],[-.5,.2,0,.045,.045],[0,0,0,.045,.045],[.5,.2,0,.045,.045],[.6,.6,0,.045,.045]],'wood',6)]
        elif key=='rudder':fs=[plate([[-.1,0],[.25,0],[.38,.6],[-.12,.75]],.07,'metal'),rod([0,.55,0],[0,1,0],.04,'l1Metal')]
        elif key=='propeller':fs=[loft([[0,0,0,.08,.035],[.18,.20,.04,.20,.055],[.25,.42,.13,.16,.025],[.21,.52,.18,.05,.02]],'copper',7)]
        elif key=='oar_blade':fs=[loft([[0,0,0,.18,.025],[0,.45,0,.16,.025],[0,.67,0,.04,.03]],'wood',6)]
        elif key=='cleat':fs=[formbox(.4,.05,.16,'l1Metal'),rod([0,.05,0],[0,.23,0],.05,'metal'),rod([-.28,.26,0],[.28,.26,0],.04,'l1Metal')]
        else:fs=[plate([[-.36,0],[.36,0],[.36,.05],[-.36,.05]],.16,'l1Metal'),arc(.25,.05,0,180,color='metal',n=10,center=[0,.05,0])]
        put('marine',key,name,fs)
    rails=names('wheel_flange:铁路车轮轮缘 axlebox:铁路轴箱壳 brake_shoe:制动闸瓦芯 coupler:自动车钩头 buffer:车端缓冲盘 bolster:转向架枕梁 pantograph_arm:集电弓臂段 rail_clip:钢轨扣件')
    for key,name in rails:
        if key=='wheel_flange':fs=[lathe([[.34,0],[.4,.035],[.4,.08],[.32,.10],[.31,.23],[.09,.23],[.09,0]],'metal',16,closed_profile=True)]
        elif key=='axlebox':fs=[formbox(.45,.38,.35,'l1Slate'),round_tube(.13,.08,.12,'metal',rotation=[90,0,0],position=[0,.2,.22])]
        elif key=='brake_shoe':fs=[arc(.4,.07,45,130,color='metal',n=7)];fs=placed(fs,scale=[1,1,2])
        elif key=='coupler':fs=[plate([[-.13,0],[.13,0],[.14,.3],[.32,.34],[.34,.57],[.18,.62],[.08,.53],[.18,.5],[.18,.44],[-.08,.44],[-.18,.32]],.22,'metal')]
        elif key=='buffer':fs=[rod([0,0,0],[0,.4,0],.085,'metal'),box([.48,.07,.28],'l1Slate',[0,.435,0],.04)]
        elif key=='bolster':fs=[plate([[-.7,.12],[-.55,0],[.55,0],[.7,.12],[.5,.26],[-.5,.26]],.26,'l1Slate')]
        elif key=='pantograph_arm':fs=[rod([-.5,0,0],[.5,.65,0],.026,'metal'),rod([-.5,0,.12],[.5,.65,.12],.026,'metal')]+[rod([x,y,0],[x,y,.12],.03,'l1Metal') for x,y in [(-.5,0),(0,.325),(.5,.65)]]
        else:fs=[loft([[-.14,0,0,.025,.025],[-.1,.13,0,.025,.025],[.02,.14,0,.025,.025],[.14,.02,0,.025,.025],[.08,0,0,.025,.025]],'metal',8)]
        put('rail',key,name,fs)
    attachments=names('tow_eye:车辆牵引环 rack_foot:车顶架支脚 mirror_arm:后视镜支臂 wiper:雨刷摆臂 mudflap:挡泥帘片 step:登车踏板片')
    for key,name in attachments:
        if key=='tow_eye':fs=[ring(.13,.04,.07,'metal',rotation=[90,0,0],position=[0,.22,0]),formbox(.12,.14,.10,'l1Slate')]
        elif key=='rack_foot':fs=[formbox(.28,.05,.16,'l1Rubber'),plate([[-.06,0],[.08,0],[.16,.3],[.10,.42],[-.06,.4]],.10,'l1Metal',position=[0,.05,0])]
        elif key=='mirror_arm':fs=[rod([0,0,0],[.13,.4,.08],.025,'metal'),rod([.13,.4,.08],[.35,.48,.1],.023,'metal')]
        elif key=='wiper':fs=[rod([0,0,0],[.2,.55,0],.016,'metal'),box([.5,.025,.025],'l1Rubber',[.2,.55,0],.006,rotation=[0,0,20])]
        elif key=='mudflap':fs=[plate([[-.24,0],[.24,0],[.25,.45],[-.25,.45]],.025,'l1Rubber')]+[disk(.018,.012,'metal',rotation=[90,0,0],position=[x,.41,.02]) for x in [-.17,0,.17]]
        else:fs=[formbox(.6,.06,.25,'l1Slate')]+[formbox(.025,.025,.25,'metal',x=x,y=.06) for x in [-.22,-.11,0,.11,.22]]
        put('attachment',key,name,fs)
    finish('vehicle',63)
