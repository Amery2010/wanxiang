"""Dressed masonry profiles with open holes, visible thickness and useful datums."""
from .common import *

def author():
    kit='dungeon';d='architecture'
    # One vault bay: two crossing arched ribs. Lower boundary is a mating datum.
    fs=[]
    for axis in (0,1):
        pts=[]
        for k in range(17):
            a=math.pi*k/16;x=math.cos(a);y=.10+math.sin(a)*.78
            pts.append([x,y,0] if axis==0 else [0,y,x])
        fs.append(sweep(pts,rect(.16,.14),C('gStoneLight')))
    fs.append(detail(block([.24,.13,.24],[0,.86,0],C('gCopper'),.025)))
    author_part=lambda key,name,forms,size,**kw:author_profile(kit,d,key,name,forms,size,**kw)
    author_part('rib_vault_cell','交叉拱肋顶格',fs,[2.16,.99,2.16],purpose='2 m 方格廊道的独立拱肋顶格',
      ports=[port('datum.mount',[0,.1,0],[0,-1,0]),port('rib.xneg',[-1,.1,0],[-1,0,0],[0,1,0]),port('rib.xpos',[1,.1,0],[1,0,0],[0,1,0]),port('rib.zneg',[0,.1,-1],[0,0,-1]),port('rib.zpos',[0,.1,1],[0,0,1])])
    # Horseshoe pointed arch outline, not a dark plane pretending to be a hole.
    outer=[[-.91,0],[-.91,1.70],[-.69,2.12],[-.38,2.40],[0,2.65],[.38,2.40],[.69,2.12],[.91,1.70],[.91,0], [.64,0],[.64,1.65],[.47,1.94],[.25,2.17],[0,2.34],[-.25,2.17],[-.47,1.94],[-.64,1.65],[-.64,0]]
    fs=[plate(outer,.36,'gStone'),basebox([.43,.18,.52],[-.78,0,0],C('gStoneDark')),basebox([.43,.18,.52],[.78,0,0],C('gStoneDark'))]
    for sign in (-1,1):
        for y in (.65,1.22,1.66):fs.append(detail(block([.28,.045,.39],[sign*.775,y,0],C('gStoneLight'),.008)))
    author_part('pointed_portal','尖拱通道框',fs,[2,2.65,.52],purpose='具有真实通道开口的尖拱门框',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('passage.center',[0,1.17,0],[0,0,1])])
    fs=[]
    for x in (-.54,-.36,-.18,0,.18,.36,.54):
        fs += [basebox([.047,1.8,.055],[x,.12,0],C('gSteel'),bevel=.005),plate([[x-.04,.14],[x,.0],[x+.04,.14]],.055,'gSteel')]
    for y in (.38,1.12,1.71):fs.append(block([1.18,.075,.065],[0,y,0],C('gSteel'),.007))
    fs.append(detail(block([.18,.1,.095],[0,1.8,0],C('gCopper'),.009)))
    author_part('portcullis_leaf','升降栅门叶',fs,[1.18,1.92,.095],purpose='独立升降门叶；垂直运动由父装配实现',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('lift',[0,1.85,0],[0,1,0])])
    fs=[wedge_xz([[-.52,-.52],[.52,-.52],[.52,.52],[-.52,.52]],0,.11,'gStoneDark')]
    # Separate border and actual slat openings; remove solid filler beneath slots.
    fs=[basebox([.10,.11,1.04],[x,0,0],C('gStoneDark')) for x in (-.47,.47)]
    fs += [basebox([.84,.11,.10],[0,0,z],C('gStoneDark')) for z in (-.47,.47)]
    fs += [basebox([.06,.08,.86],[x,.015,0],C('gSteel'),bevel=.005) for x in (-.34,-.17,0,.17,.34)]
    fs += [detail(basebox([.84,.035,.035],[0,.05,z],C('gMetal'),bevel=.004)) for z in (-.25,.25)]
    author_part('floor_grate_tile','地牢排水格栅砖',fs,[1.04,.11,1.04],purpose='有贯通孔隙的方形地面排水单元')
    fs=[arc_slab(.36,.72,0,90,0,.10,'gStoneDark'),arc_slab(.31,.38,0,90,0,.24,'gStone'),arc_slab(.70,.77,0,90,0,.24,'gStone')]
    author_part('trough_corner','四分之一转角排水槽',fs,[.77,.24,.77],purpose='开放槽底与双侧墙的 90° 排水转角',ports=[port('inlet',[.54,.10,0],[0,0,-1]),port('outlet',[0,.10,.54],[-1,0,0],[0,1,0])])
    outside=rect(1.0,1.3,(0,.65));hole=[[-.055,.35],[.055,.35],[.055,.66],[.20,.66],[.20,.76],[.055,.76],[.055,1.1],[-.055,1.1],[-.055,.76],[-.20,.76],[-.20,.66],[-.055,.66]]
    fs=[plate(outside,.34,'gStone',holes=[hole]),detail(block([1.04,.09,.39],[0,1.25,0],C('gStoneLight'),.012))]
    author_part('cross_arrow_slit','十字箭孔墙芯',fs,[1.04,1.3,.39],purpose='十字箭孔贯通的石墙嵌块')
    fs=[basebox([w,h,z],[0,y,0],C(col),bevel=.018) for w,h,z,y,col in [(.62,.3,.88,0,'gStoneDark'),(.47,.7,.66,.3,'gStone'),(.33,.8,.43,1.,'gStone'),(.42,.12,.53,1.8,'gStoneLight')]]
    author_part('stepped_buttress','收分阶梯扶壁',fs,[.62,1.92,.88],purpose='城堡墙根的阶梯收分侧向承托')
    fs=[]
    for k in range(4):fs.append(arc_slab(.12,.88,k*22.5,(k+1)*22.5,0,.13*(k+1),'gStoneLight' if k%2 else 'gStone'))
    author_part('winder_stair_quarter','四步转角楔形阶梯',fs,[.88,.52,.88],purpose='环绕内柱的四步 90° 转角踏面')
    fs=[basebox([.64,.15,.49],[0,0,0],C('gStoneDark'))]
    for x in (-.25,.25):fs.append(placed([annulus_xy(.17,.073,.085,'gSteel',center=(0,.28))],position=(x,0,0),rotation=(0,90,0))[0])
    fs.append(detail(basebox([.42,.03,.24],[0,.15,0],C('gCopper'),bevel=.006)))
    author_part('drawbridge_hinge_seat','吊桥双耳铰轴座',fs,[.64,.45,.49],purpose='带真实销孔的吊桥地台支座',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('axle',[0,.28,0],[1,0,0],[0,1,0])])
    fs=[plate(rect(.34,.44,(0,.22),.045),.035,'gSteel',holes=[circle(.025,(x,y),8) for x in (-.115,.115) for y in (.08,.36)])]
    fs.append(ring_tube([0,.23,.12],.085,.11,.019,C('gCopper'),'xy',20,6))
    fs.append(block([.12,.12,.09],[0,.23,.04],C('gSteel'),.016))
    author_part('chain_anchor','四孔拉环墙锚',fs,[.34,.44,.155],purpose='链条和绳索的墙体附着环',ports=[port('wall',[0,.22,-.0175],[0,0,-1]),port('tie',[0,.23,.12],[0,0,1])])
    fs=[plate(rect(.15,.45,(0,.225),.035),.05,'gSteel'),beam([0,.12,.015],[0,.32,.31],.045,C('gSteel')),
        placed([spin([(.10,0),(.12,.06),(.16,.17),(.14,.18),(.09,.06)],'gCopper',12)],position=(0,.31,.30))[0]]
    author_part('torch_sconce','开放杯形火炬壁托',fs,[.32,.51,.49],purpose='可插入独立火炬或粒子火焰的空心壁托',ports=[port('wall',[0,.225,-.025],[0,0,-1]),port('flame',[0,.49,.30],[0,1,0])])
    fs=[wedge_xz([[-.62,-.2],[.62,-.2],[.57,.20],[-.62,.2]],0,.24,'gStoneDark'),
        plate([[-.62,.22],[.62,.22],[.62,.58],[.33,.52],[.25,.75],[.12,.65],[-.03,.89],[-.30,.79],[-.41,1.03],[-.62,.97]],.32,'gStone')]
    author_part('broken_parapet','断口雉堞墙片',fs,[1.24,1.03,.4],purpose='非随机碎面堆叠的残损城垛轮廓')

# Avoid shadowing the public module entrypoint with the shared author function.
from .common import author as author_profile
