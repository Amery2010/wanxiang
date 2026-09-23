"""Physical puzzle props use geometry for keys/holes, not painted placeholders."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,**kw):return emit('puzzle','gameplay',key,name,fs,size,**kw)
    fs=[annulus_xy(.45,.30,.11,'gStoneDark')]
    for k in range(8):
        a=k*math.tau/8
        # Unlettered geometric markers, not embedded text.
        f=plate([[0,.335],[.038,.382],[0,.426],[-.038,.382]],.022,'gCopper',at=(0,0,.067))
        fs += [detail(x) for x in placed([f],rotation=(0,0,k*45))]
    put('rune_rotor','八标记符环转盘',fs,[.90,.90,.155],purpose='具有中心通孔和几何刻度的机关旋转环',anchor='center',ports=[port('axis',[0,0,0],[0,0,1])])
    outline=[[0,.36],[-.16,.05],[.16,.05]]
    fs=[plate(outline,.18,'gGlow'),detail(plate([[0,.28],[-.095,.095],[.095,.095]],.02,'gMetal',at=(0,0,.10)))]
    put('tri_key','三角晶钥实体',fs,[.32,.36,.22],purpose='轮廓明确、可匹配三角插槽的实体钥匙',collision='convex-hull')
    outer=rect(.59,.57,(0,.285),.06);hole=[[0,.445],[-.19,.09],[.19,.09]]
    fs=[plate(outer,.22,'gStoneDark',holes=[hole])]
    fs.append(detail(plate(rect(.31,.025,(0,.52),.006),.018,'gCopper',at=(0,0,.121))))
    put('tri_receiver','三角晶钥贯通槽座',fs,[.59,.57,.258],purpose='与三角晶钥匹配且保留装配间隙的贯通槽')
    fs=[spin([(0,0),(.26,0),(.29,.05),(.20,.17),(0,.17)],'gStoneDark',12)]
    for s in (-1,1):fs.append(beam([s*.17,.13,0],[s*.12,.40,0],.044,C('gCopper')))
    fs.append(plate([[-.15,.22],[.15,.22],[0,.49]],.16,'gGlow'))
    put('beam_splitter','三角分光晶座',fs,[.58,.49,.58],purpose='光路解谜用棱镜与稳定支架，不含光线追踪行为')
    fs=[annulus_xy(.31,.25,.056,'gCopper',center=(0,.4)),plate(circle(.245,(0,.4),24),.018,'gMetal')]
    fs += [beam([s*.19,0,0],[s*.32,.4,0],.035,C('gStoneDark')) for s in (-1,1)]
    fs.append(basebox([.45,.07,.29],[0,0,0],C('gStoneDark')))
    put('mirror_disc','双耳枢轴反射镜盘',fs,[.72,.73,.29],purpose='分离反射面、镜框与旋转支承的解谜镜座')
    fs=[spin([(0,.07),(.25,.07),(.39,.26),(.41,.30),(.38,.315),(.22,.105),(0,.105)],'gCopper',18)]
    for k in range(3):
        a=k*math.tau/3
        fs.append(tube([[.37*math.cos(a),.29,.37*math.sin(a)],[0,.79,0]],.008,C('gSteel'),6))
    fs.append(detail(ring_tube([0,.83,0],.04,.055,.012,C('gSteel'),'xy',12,6)))
    put('scale_pan','三索天平托盘',fs,[.82,.91,.82],purpose='凹盘与三条汇顶吊索的称重谜题部件')
    fs=[arc_slab(.27,.39,0,90,0,.10,'gSteel')]
    for k in range(5):
        a=math.radians(8+k*18);cs,sn=math.cos(a),math.sin(a)
        fs.append(block([.085,.1,.10],[.43*cs,.05,.43*sn],C('gMetal'),.006,rot=(0,-math.degrees(a),0)))
    put('gear_arc','四分之一齿圈片',fs,[.54,.10,.54],purpose='用于旋转机关的可组合扇形齿段')
    fs=[plate([[0,0],[.24,.03],[.39,.28],[.20,.47],[-.06,.21]],.024,'gSteel',holes=[circle(.033,(.07,.12),12)])]
    fs.append(detail(plate([[.05,.18],[.26,.15],[.30,.28],[.17,.38]],.012,'gCopper',at=(0,0,.022))))
    put('iris_petal','虹膜快门单叶',fs,[.45,.47,.054],purpose='带枢轴孔的机关虹膜叶片，不伪装为完整快门')
    fs=[spin([(0,0),(.32,0),(.36,.06),(.32,.10),(.29,.10),(.29,.53),(.33,.55),(.33,.62),(0,.62)],'gStone',8)]
    for k in range(4):
        f=plate([[-.07,.24],[0,.16],[.07,.24],[0,.43]],.024,'gGlow',at=(0,0,.275))
        fs += [detail(x) for x in placed([f],rotation=(0,k*90,0))]
    put('rune_drum','独立符柱转鼓',fs,[.72,.62,.72],purpose='可堆叠并绕竖轴旋转的八面符柱段')
    fs=[spin([(0,0),(.11,0),(.17,.11),(.13,.21),(0,.21)],'gCopper',10),
        profile_z([[-.055,.36,.045,.15],[0,.42,.10,.25],[.065,.36,.04,.13]],C('gPurple'),6)]
    for s in (-1,1):fs.append(detail(tube([[s*.13,.10,0],[s*.115,.28,0]],[.022,.011],C('gCopper'),6)))
    put('socketed_crystal','卡座式法力晶核',fs,[.34,.68,.14],purpose='晶体与卡爪连为可拆装的能量源外观')
    fs=[spin([(.18,0),(.43,0),(.52,.10),(.51,.23),(.39,.25),(.35,.19),(.20,.15),(.18,.15)],'gStone',20)]
    for k in range(4):
        a=k*math.tau/4
        fs.append(detail(cyl(.027,.025,'gCopper',at=(.44*math.cos(a),.235,.44*math.sin(a)),sides=8)))
    put('altar_basin','中央凹槽祭坛顶盘',fs,[1.04,.26,1.04],purpose='真实凹陷、带边沿的祭坛上部承载盘')
    fs=[spin([(.12,0),(.25,0),(.29,.055),(.25,.12),(.18,.38),(.14,.45),(.10,.47),(.11,.43),(.15,.35),(.21,.11),(.235,.045),(.12,.035)],'gCopper',18),
        tube([[0,.40,0],[0,.07,0]],[.016,.022],C('gSteel'),8),ellipsoid([0,.10,0],[.085,.10,.085],C('gSteel'),10,5)]
    fs.append(ring_tube([0,.51,0],.045,.055,.013,C('gSteel'),'xy',16,6))
    put('bell_clapper','空心钟体与钟舌',fs,[.58,.58,.58],purpose='可读钟口和内部钟舌的声音机关外观')
