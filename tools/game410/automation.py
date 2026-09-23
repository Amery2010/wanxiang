"""Mechanical module profiles with explicitly hollow bores and mating centres."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,**kw):return emit('automation','robot',key,name,fs,size,**kw)
    fs=[teeth_disc(.39,.315,12,.12,'gSteel',.09),detail(annulus_xy(.24,.13,.15,'gCopper'))]
    for k in range(6):
        a=k*math.tau/6;fs.append(detail(plate(circle(.024,(.25*math.cos(a),.25*math.sin(a)),8),.14,'gMetal')))
    put('track_sprocket','履带主动链轮',fs,[.78,.78,.15],purpose='十二齿主动轮与贯通轴孔',anchor='center',ports=[port('axle',[0,0,0],[0,0,1])])
    fs=[basebox([.52,.075,.21],[0,0,0],C('gSteel'))]
    for x in (-.17,0,.17):fs.append(block([.10,.035,.16],[x,.09,0],C('gCloth'),.008))
    for z in (-.13,.13):fs.append(placed([pipe([[0,0,0],[.45,0,0]],.034,.015,C('gMetal'),10)],position=(-.225,.026,z))[0])
    put('rubber_track_link','橡胶履带单节',fs,[.52,.107,.33],purpose='可沿路径重复排列的带销孔履带节')
    fs=[spin([(.07,0),(.20,0),(.25,.06),(.25,.19),(.20,.25),(.07,.25)],'gSteel',12)]
    for k in range(8):
        a=k*45;rad=math.radians(a)
        fs.append(placed([ellipsoid([0,0,0],[.095,.24,.095],C('gCloth'),10,5)],position=(.265*math.cos(rad),.125,.265*math.sin(rad)),rotation=(0,-a,38))[0])
    put('mecanum_hub','斜辊全向轮外观',fs,[.73,.43,.73],purpose='倾斜滚子可读的机器人轮模块；未实现全向轮物理')
    fs=[spin([(0,0),(.055,0),(.085,.035),(.10,.12),(.085,.21),(.055,.25),(0,.25)],'gCloth',12)]
    fs += [cyl(.025,.04,'gMetal',at=(0,y,0),sides=10) for y in (-.035,.245)]
    put('omni_roller','全向轮鼓形滚子',fs,[.2,.325,.2],purpose='两端轴颈与鼓形胎面的独立轮缘滚子',collision='convex-hull')
    outline=[[-.10,.1],[-.10,.9],[-.06,1.0],[.06,1.0],[.10,.9],[.10,.1],[.06,0],[-.06,0]]
    fs=[plate(outline,.055,'gSteel',holes=[circle(.047,(0,y),16) for y in (.1,.5,.9)])]
    fs.append(detail(plate(rect(.075,.22,(0,.7),.025),.025,'gMetal',at=(0,0,.04))))
    put('scissor_link','三孔剪叉升降连杆',fs,[.20,1.0,.08],purpose='两个端轴孔与中央枢孔共面的剪叉臂',ports=[port('pivot.lower',[0,.1,0],[0,0,1]),port('pivot.center',[0,.5,0],[0,0,1]),port('pivot.upper',[0,.9,0],[0,0,1])])
    fs=[plate([[-.07,0],[.07,0],[.07,.30],[.18,.47],[.15,.55],[.035,.43],[-.07,.31]],.065,'gSteel',holes=[circle(.025,(0,.065),12)]),
        block([.11,.09,.085],[.135,.49,0],C('gCloth'),.018)]
    put('threejaw_finger','三爪夹具弯指',fs,[.25,.55,.085],purpose='弯指和接触垫分离，可旋转复制成三指夹具')
    fs=[annulus_xy(.31,.235,.075,'gSteel')]
    for x in (-.325,.325):fs.append(placed([cyl(.045,.11,'gCopper',sides=10)],position=(x-.055,0,0),rotation=(0,0,-90))[0])
    put('gimbal_ring','双轴传感器环架',fs,[.84,.62,.10],purpose='通光开口及两侧枢轴的独立环形架',anchor='center',ports=[port('axis.x',[0,0,0],[1,0,0],[0,1,0]),port('lens',[0,0,0],[0,0,1])])
    fs=[basebox([.33,.065,.22],[0,0,0],C('gSteel'))]
    for x in (-.078,.078):
        fs.append(plate([[x-.037,.055],[x+.037,.055],[x+.037,.19],[x+.018,.23],[x-.018,.23],[x-.037,.19]],.042,'gCopper'))
    put('charging_contacts','双片回充触点座',fs,[.33,.23,.22],purpose='电气隔离的双触点外观；无充电逻辑')
    fs=[basebox([.68,.06,.38],[0,0,-.09],C('gSteel'))]
    for k in range(8):fs.append(basebox([.047,.045,.27],[-.294+k*.084,.06,.155],C('gMetal'),bevel=.005))
    put('transfer_comb','传送线过渡梳板',fs,[.68,.105,.55],purpose='从输送带到台面的梳齿形过渡件')
    fs=[basebox([.44,.32,.34],[0,0,0],C('gSteel'),bevel=.04)]
    for x in (-.14,.14):
        fs.append(pipe([[x,.32,0],[x,.50,0]],.062,.017,C('gMetal'),12))
        fs.append(pipe([[x,.15,.15],[x,.15,.34]],.062,.017,C('gMetal'),12))
    put('fourport_block','四接口配管歧座',fs,[.44,.50,.60],purpose='四个独立可见孔口的管线外观分配块；非流体求解网格')
    fs=[spin([(.046,0),(.074,0),(.074,.035),(.055,.055),(.055,.17),(.071,.17),(.071,.22),(.052,.26),(.037,.26),(.037,0)],'gCopper',12)]
    fs.append(detail(ring_y(.078,.12,.05,.024,'gSteel',12)))
    put('quick_coupler','中空气路快接头',fs,[.156,.26,.156],purpose='管路连接用六角／环套相间的空心接头')
    path=bezier([[-.31,0,0],[-.31,.38,0],[.31,.38,0],[.31,0,0]],16)
    fs=[pipe(path,.043,.014,C('gCloth'),10)]
    for x in (-.31,.31):fs.append(placed([ring_y(.067,0,.11,.026,'gCopper',12)],position=(x,-.025,0))[0])
    put('hydraulic_hose_loop','U形液压软管',fs,[.755,.37,.135],purpose='可见内孔及两端套箍的弯曲软管')
