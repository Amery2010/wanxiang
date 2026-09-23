"""Silhouette-led environment profiles, with watercourses left visibly open."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,domain='terrain',**kw):return emit('waterland',domain,key,name,fs,size,**kw)
    fs=[arc_slab(.54,.78,0,90,0,.23,'gSoil'),arc_slab(1.25,1.51,0,90,0,.25,'gSoil'),
        detail(arc_slab(.56,.78,0,90,.23,.025,'gLeafDark')),detail(arc_slab(1.25,1.49,0,90,.25,.025,'gLeafDark'))]
    put('stream_bend_bank','弯河双岸模块',fs,[1.51,.275,1.51],purpose='0.47 m 净河道的九十度弯岸，中心不以实体填充')
    fs=[]
    for x in (-.49,.49):
        fs.append(wedge_xz([[x-.14,-.70],[x+.14,-.70],[x+.14,-.26],[x-.14,-.26]],0,.18,'gSoil'))
    fs.append(wedge_xz([[-.68,.26],[.68,.26],[.68,.60],[-.68,.60]],0,.19,'gSoil'))
    put('stream_junction_bank','T形溪流岸块',fs,[1.36,.19,1.30],purpose='三向开放的溪流汇合岸边，不含流体')
    fs=[profile_z([[-.45,.25,.74,.20],[-.2,.24,.78,.22],[.20,.21,.72,.20],[.35,.27,.67,.13]],C('gStone'),10)]
    fs.append(detail(block([1.18,.06,.11],[0,.38,.31],C('gStoneLight'),.022)))
    put('waterfall_lip','浅槽瀑布岩唇',fs,[1.56,.48,.80],purpose='用于瀑布水面落差处的横向岩石唇口')
    outline=[[-.35,-.18],[-.21,-.31],[.17,-.30],[.37,-.08],[.30,.22],[.02,.30],[-.30,.21]]
    fs=[wedge_xz(outline,0,.15,'gStone'),detail(wedge_xz([[x*.86,z*.85] for x,z in outline],.15,.023,'gStoneLight'))]
    put('stepping_stone','八面渡溪踏石',fs,[.72,.173,.61],purpose='顶面平稳、边缘不规则的渡溪落脚石',collision='convex-hull')
    path=[[-.61,0,0],[-.54,.46,.025],[-.25,.73,0],[.10,.82,-.01],[.43,.58,.015],[.61,0,0]]
    fs=[tube(path,[.14,.16,.14,.10,.12,.16],C('gStoneWarm'),10)]
    for k,(x,y) in enumerate([(-.31,.58),(0,.67),(.27,.53)]):fs.append(detail(tube([[x,y,0],[x+.02,y-.20-.06*k,0]],[.04,.007],C('gStoneLight'),7)))
    put('dripstone_arch','垂石洞穴桥拱',fs,[1.55,.98,.34],purpose='连续承重石拱与下垂钟乳尖端')
    fs=[]
    for x,z,h in [(-.19,-.13,.64),(.12,-.19,.90),(.28,.08,.52),(0,.19,.78),(-.27,.17,.41)]:
        fs.append(placed([spin([(0,0),(.19,0),(.19,h),(0,h)],'gStoneDark',6)],position=(x,0,z))[0])
        fs.append(detail(placed([cyl(.183,.025,'gStone',sides=6)],position=(x,h,z))[0]))
    put('basalt_columns','错落六棱玄武岩簇',fs,[.93,.925,.77],purpose='具有不同高度与平整断面的六棱柱状节理')
    outer=[[-.65,-.39],[-.22,-.58],[.38,-.53],[.69,-.13],[.54,.40],[.11,.56],[-.48,.42],[-.72,.03]]
    inner=[[x*.67,z*.63] for x,z in outer]
    # XY extrusion rotated onto XZ retains an actual basin opening.
    fs=placed([plate(outer,.20,'gStone',holes=[inner])],rotation=(90,0,0),position=(0,.11,0))
    put('tidepool_rim','潮池环形岩缘',fs,[1.41,.22,1.14],purpose='不规则而贯通的潮池岩石边缘，池底可单独搭配')
    fs=[spin([(.36,0),(.80,0),(.70,.17),(.52,.36),(.34,.48),(.25,.43),(.33,.29),(.36,.08)],'gStoneDark',14),
        detail(ring_y(.28,.37,.028,.028,'gRed',14))]
    put('lava_vent','内凹熔岩喷口',fs,[1.60,.48,1.60],purpose='有内壁和火口空间的低矮火山口')
    fs=[]
    for x,y,z,w in [(-.18,.16,0,.37),(.08,.35,.03,.42),(-.09,.56,-.03,.29)]:
        out=[[-w,0],[-w*.70,w*.48],[0,w*.64],[w*.70,w*.46],[w,0],[w*.44,-w*.09],[-w*.5,-w*.09]]
        fs.append(placed([plate(out,.07,'gWood')],rotation=(90,0,0),position=(x,y,z))[0])
        fs.append(detail(tube([[x-w*.65,y-.035,z+.10],[x,y-.045,z+.20],[x+w*.65,y-.035,z+.10]],.012,C('gCream'),6)))
    put('shelf_fungus','层叠木生菌盖',fs,[1.02,.65,.38],domain='nature',purpose='可贴附树干的扇形菌盖簇',collision='none')
    fs=[tube([[-.51,.94,0],[-.34,.74,.04],[-.16,.39,.035],[.1,.16,0],[.35,.05,.04]],[.052,.045,.030,.018,.004],C('gBark'),8),
        tube([[-.34,.74,.04],[.04,.74,.08],[.28,.93,0]],[.03,.025,.008],C('gBark'),8)]
    fs.append(detail(tube([[.04,.73,.08],[.19,.51,.10],[.17,.27,.09]],[.019,.012,.003],C('gBark'),7)))
    put('hanging_root','分叉下垂根须',fs,[.96,1.02,.20],domain='nature',purpose='沿悬崖和洞穴顶端附着的连贯分叉根须',collision='none')
    fs=[]
    fs.append(tube([[0,0,0],[0,.22,0]],.024,C('gCopper'),7))
    for k in range(7):
        a=math.radians(-65+k*130/6);tip=[math.sin(a)*.53,.25+math.cos(a)*.59,.015*math.sin(k)]
        fs.append(tube([[0,.18,0],[tip[0]*.48,.45,0],tip],[.021,.013,.004],C('gRed'),6))
        for j in (1,2):
            # Branch starts are interpolated on the actual second parent segment.
            t=j/3;p=[tip[0]*(.48+.52*t),.45+(tip[1]-.45)*t,tip[2]*t]
            fs.append(detail(tube([p,[p[0]+(.13 if k>3 else -.13),p[1]+.08,p[2]]],[.009,.003],C('gRed'),5)))
    put('sea_fan','扇状珊瑚骨枝',fs,[1.08,.87,.07],domain='nature',purpose='具有分枝层次与透空轮廓的海扇珊瑚',collision='none')
    fs=[grid_shell(lambda u,v:[(u-.5)*1.25,.22+.15*math.cos((u-.5)*2.8)+.11*math.sin(v*math.pi),v*.75-.38],8,6,.16,C('gCream'))]
    for x in (-.44,-.08,.35):fs.append(detail(tube([[x,.29,.28],[x+.025,.06,.31]],[.043,.006],C('gStoneLight'),7)))
    put('snow_cornice','悬檐积雪唇边',fs,[1.25,.55,.80],purpose='连续厚雪面与少量下垂冰尖，适合屋檐或岩缘')
