"""Traversable geometry and climbing hardware; no invisible collision stand-ins."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,**kw):return emit('traversal','gameplay',key,name,fs,size,**kw)
    fs=[wedge_xz([[-.8,-.8],[.8,-.8],[.8,-.35],[-.35,-.35],[-.35,.8],[-.8,.8]],0,.18,'gSteel')]
    fs += [detail(basebox([.9,.024,.035],[-.2,.18,-.71],C('gAmber'),bevel=.004)),detail(basebox([.035,.024,.9],[-.71,.18,-.2],C('gAmber'),bevel=.004))]
    put('inner_corner_deck','内凹直角跳台',fs,[1.6,.204,1.6],purpose='保留中心缺口的 L 形平台，适用于内转角路线')
    fs=[arc_slab(0.08,.9,0,90,0,.17,'gSteel'),detail(arc_slab(.79,.825,4,86,.17,.012,'gAmber'))]
    put('quarter_round_deck','外弧四分之一跳台',fs,[.9,.182,.9],purpose='连续外弧踏面，适用于路线外转角')
    fs=[plate([[-.72,0],[.72,0],[.82,.14],[.82,.95],[.64,1.12],[-.64,1.12],[-.82,.95],[-.82,.14]],.1,'gSteel')]
    for y in (.2,.42,.64,.86):fs.append(detail(block([1.35,.028,.026],[0,y,.062],C('gCloth'),.006)))
    fs += [plate([[-.14,.40],[.14,.56],[-.14,.72]],.018,'gAmber',at=(.30,0,.063))]
    put('wallrun_panel','壁跑接触面板',fs,[1.64,1.12,.128],purpose='有方向几何标记的壁跑外观模块',ports=[port('wall',[0,.56,-.05],[0,0,-1])])
    fs=[plate([[-.17,0],[.17,0],[.20,.09],[.10,.18],[-.10,.18],[-.20,.09]],.065,'gStoneWarm',holes=[circle(.019,(0,.07),10)]),
        block([.27,.046,.13],[0,.13,.075],C('gAmber'),.014)]
    put('crimp_hold','岩壁指尖攀点',fs,[.4,.18,.172],purpose='带固定孔与上沿窄抓面的攀爬点',collision='convex-hull',ports=[port('wall',[0,.07,-.0325],[0,0,-1]),port('grip',[0,.153,.1],[0,1,0])])
    outer=[[-.15,0],[.15,0],[.22,.14],[.18,.31],[.08,.40],[-.08,.40],[-.18,.31],[-.22,.14]]
    fs=[plate(outer,.085,'gCloth',holes=[circle(.072,(0,.25),12,scale=(1.45,1))]),detail(block([.21,.04,.12],[0,.39,.01],C('gAmber'),.01))]
    put('jug_hold','镂空大把手攀点',fs,[.44,.43,.12],purpose='有真实指握空间的抓握攀点',collision='authored-mesh',ports=[port('wall',[0,.16,-.0425],[0,0,-1]),port('grip',[0,.34,0],[0,1,0])])
    fs=[]
    for z in (-.085,.085):
        fs.append(plate([[-.23,.12],[.23,.12],[.28,.27],[.20,.37],[-.20,.37],[-.28,.27]],.026,'gSteel',holes=[circle(.062,(x,.275),16) for x in (-.15,.15)],at=(0,0,z)))
    for x in (-.15,.15):fs.append(placed([spin([(.01,0),(.082,0),(.082,.065),(.061,.072),(.061,.094),(.082,.10),(.082,.155),(.01,.155)],'gMetal',16)],position=(x,.275,-.0775),rotation=(90,0,0))[0])
    fs.append(plate(rect(.18,.18,(0,.075),.035),.08,'gCopper',holes=[circle(.045,(0,.065),16)]))
    put('zipline_trolley','双滑轮索道小车壳',fs,[.56,.40,.2],purpose='轮槽与悬挂孔分离的索道小车外观',ports=[port('rope',[0,.34,0],[1,0,0],[0,1,0]),port('hang',[0,.065,0],[0,-1,0])])
    fs=[basebox([.6,.10,.38],[0,0,0],C('gSteel'))]
    for x in (-.19,.19):fs.append(placed([plate([[-.15,.05],[.15,.05],[.13,.42],[-.10,.42]],.075,'gSteel',holes=[circle(.055,(0,.31),12)])],position=(x,0,0),rotation=(0,90,0))[0])
    fs.append(beam([-.27,.11,.12],[.27,.11,.12],.032,C('gAmber')))
    put('zipline_anchor','索道锚固双耳支架',fs,[.6,.42,.38],purpose='承接钢索端点的独立锚固件',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('rope',[0,.31,0],[1,0,0],[0,1,0])])
    fs=[profile_z([[-1, .22,.17,.18],[-.86,.23,.20,.19],[.76,.22,.19,.18],[1,.20,.16,.16]],C('gWood'),10)]
    for z in (-.68,.68):fs.append(detail(placed([ring_y(.212,0,.10,.028,'gLeather',12)],position=(0,.22,z-.05),rotation=(90,0,0))[0]))
    put('balance_log','平衡木踏梁',fs,[.44,.43,2],purpose='窄落脚面与两端支承截面的独木桥梁',collision='convex-hull')
    fs=[basebox([.6,.08,.28],[0,0,0],C('gSteel'))]
    for x in (-.24,-.12,0,.12,.24):fs.append(detail(basebox([.064,.016,.26],[x,.08,0],C('gCloth'),bevel=.006)))
    for z in (-.16,.16):fs.append(placed([annulus_xy(.06,.026,.48,'gMetal')],position=(0,.035,z),rotation=(0,90,0))[0])
    put('conveyor_tread','铰接传送带踏节',fs,[.6,.096,.44],purpose='可重复排列的传送带单节；具备前后铰接位置',ports=[port('front',[0,.035,.16],[0,0,1]),port('back',[0,.035,-.16],[0,0,-1])])
    fs=[annulus_xy(.32,.245,.072,'gCopper',center=(0,.43)),basebox([.24,.2,.16],[0,0,0],C('gSteel')),
        block([.12,.13,.10],[0,.23,0],C('gSteel'))]
    fs.append(detail(plate([[-.05,.74],[0,.80],[.05,.74]],.075,'gGlow')))
    put('grapple_ring','钩索目标穿环',fs,[.64,.80,.16],purpose='有清晰穿环空间和安装底座的钩索目标',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('target',[0,.43,0],[0,0,1])])
    fs=[plate([[-.32,0],[.32,0],[.32,.07],[-.23,.62],[-.32,.62]],.085,'gSteel',holes=[[[-.21,.18],[.14,.08],[-.21,.48]]]),
        block([.68,.08,.21],[0,.65,0],C('gMetal'),.01)]
    put('folding_ledge_bracket','折叠踏板三角托架',fs,[.68,.69,.21],purpose='轻量化镂空三角承托；转轴由父级设置',ports=[port('wall',[-.32,.31,0],[-1,0,0],[0,1,0]),port('deck',[0,.69,0],[0,1,0])])
    fs=[wedge_xz([[-.43,-.7],[.43,-.7],[.29,.7],[-.29,.7]],0,.055,'gWoodDark')]
    for x in (-.27,.27):
        fs += [beam([x,.10,-.68],[x,.10,.68],.042,C('gMetal')),
               beam([x,.10,-.68],[-x,.10,.68],.042,C('gMetal'))]
    put('rail_crossing_frog','矿车交叉辙芯',fs,[.86,.15,1.4],purpose='单独的交叉轨心几何，用于矿车岔道外观')
