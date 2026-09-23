"""Crafting resources and wearable camp containers with intentional silhouettes."""
from .common import *
from .common import author as emit
from repair39.common import surface_patch

def author():
    def put(key,name,fs,size,**kw):return emit('survival','props',key,name,fs,size,**kw)
    fs=[profile_z([[-.09,.21,.18,.14],[0,.23,.23,.18],[.08,.22,.20,.15],[.18,.20,.16,.025]],C('gStone'),8)]
    fs.append(detail(surface_patch(fs[0],[[-.12,.21],[-.07,.31],[.005,.36],[-.025,.27]],'gStoneLight',offset=.001,axis=2)))
    put('knapped_axe_head','打制石斧头',fs,[.46,.42,.27],purpose='收窄刃口与厚背分离的原始工具头',collision='convex-hull')
    outline=[[0,0],[.035,.065],[.11,.07],[.05,.16],[0,.36],[-.05,.16],[-.11,.07],[-.035,.065]]
    ps=[[x,y,0] for x,y in outline]+[[0,.15,.025],[0,.15,-.025]];n=len(outline)
    fs=[mesh(ps,[[n,k,(k+1)%n] for k in range(n)]+[[n+1,(k+1)%n,k] for k in range(n)],C('gStoneDark'))]
    put('flint_arrowhead','菱脊燧石箭头',fs,[.22,.36,.05],purpose='两面汇脊并带绑扎茎的箭头坯',collision='convex-hull')
    fs=[beam([x,0,0],[x,1.1,0],.055,C('gWood')) for x in (-.38,.38)]
    fs += [beam([-.43,y,0],[.43,y,0],.055,C('gWood')) for y in (.06,1.03)]
    hide=[[-.19,.16],[.17,.16],[.25,.35],[.19,.61],[.25,.83],[.07,.91],[-.17,.86],[-.24,.68],[-.19,.4],[-.25,.3]]
    fs.append(plate(hide,.014,'gLeather'))
    for x,y in hide:fs.append(tube([[x,y,0],[.365 if x>0 else -.365,y,0]],.007,C('gCream'),6))
    put('hide_stretcher','系绳兽皮绷框',fs,[.92,1.13,.06],purpose='皮片与绷绳独立可见的制革框')
    fs=[tube([[0,0,0],[.015,.75,0],[-.17,1.05,0]],[.063,.045,.025],C('gWood'),9),
        tube([[.015,.72,0],[.2,1.02,0]],[.045,.025],C('gWood'),8)]
    fs.append(detail(ring_y(.065,.63,.035,.012,'gLeather',12)))
    put('forked_rack_post','晾晒架叉口立柱',fs,[.4,1.1,.14],purpose='自然 Y 形承托，可接独立横杆')
    fs=[profile_z([[-.45,.15,.15,.12],[-.20,.15,.17,.14],[.27,.15,.14,.13],[.48,.13,.13,.11]],C('gWoodDark'),8)]
    for a in (-.075,0,.072):
        outline=[[a-.012,-.34],[a+.018,-.18],[a-.014,.18],[a+.014,.34],[a-.026,.20],[a+.002,-.18]]
        fs.append(detail(surface_patch(fs[0],outline,'gStoneDark',offset=.001,axis=1)))
    put('charred_log','焦化劈柴段',fs,[.34,.3,.96],purpose='营火用半劈木块，保留可读裂口与焦化面')
    fs=[]
    for k in range(7):
        a=k*math.tau/7;fs.append(tube([[.085*math.cos(a),.07,.36],[.092*math.cos(a),.10+.07*math.sin(a),-.38]],.024,C('gWood') if k%2 else C('gWoodDark'),6))
    for z in (-.14,.16):fs.append(detail(ring_tube([0,.10,z],.13,.08,.012,C('gCream'),'xy',20,6)))
    put('kindling_bundle','绑扎引火细枝束',fs,[.3,.21,.8],purpose='可拾取生火资源；两条绑绳约束枝束')
    fs=[]
    for k in range(5):
        x=(k-2)*.042;fs.append(tube([[0,0,0],[x,.35,0],[x*1.3,.57,.025]],.008,C('gLeafDark'),6))
        for j in range(3):
            y=.20+j*.105
            fs.append(flattened_leaf([x*y/.35,y,0],[x*y/.35+(.09 if j%2 else -.09),y+.08,.018],.03,'gLeaf'))
    fs.append(detail(ring_tube([0,.18,0],.056,.03,.012,C('gCream'),'xz',16,6)))
    put('herb_bundle','系扎草药束',fs,[.32,.65,.1],purpose='药材采集物的茎叶束轮廓',collision='convex-hull')
    fs=[profile_z([[-.09,.30,.19,.28],[0,.31,.23,.30],[.09,.30,.18,.28]],C('gLeather'),12),
        cyl(.047,.10,'gCopper',at=(.04,.56,0),sides=12),cyl(.035,.05,'gWoodDark',at=(.04,.65,0),sides=10)]
    fs.append(tube_curve([[.04,.69,0],[.35,.65,0],[.32,.17,0],[.08,.04,0]],.012,'gCream',n=18))
    put('waterskin','软皮水囊体',fs,[.56,.70,.18],purpose='柔性囊体、收口和系绳的生存容器',collision='convex-hull')
    fs=[ring_y(.14,.34,.06,.025,'gSteel',16)]
    for a in (0,120,240):
        c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
        fs.append(beam([c*.30,0,s*.30],[c*.11,.37,s*.11],.035,C('gSteel')))
    fs.append(detail(ring_tube([0,.31,0],.065,.06,.015,C('gCopper'),'xy',16,6)))
    put('tripod_crown','三脚炊架吊锅冠座',fs,[.64,.40,.64],purpose='炊具吊点与三条支腿接口，不含火焰')
    fs=[spin([(.26,0),(.30,.48),(.14,.62),(.055,.32),(.074,.31),(.16,.61),(.32,.48),(.28,0)],'gWood',16)]
    for y,r in ((.10,.29),(.44,.315)):
        fs.append(detail(ring_y(r,y,.023,.009,'gWoodDark',16)))
    put('fishtrap_funnel','鱼笼内收漏斗口',fs,[.64,.62,.64],purpose='带内收通道的鱼笼口，水流空间真实开放')
    fs=[spin([(0,.03),(.31,.04),(.42,.51),(.41,.56),(.375,.56),(.28,.08),(0,.08)],'gWood',16)]
    for y,r in ((.18,.34),(.31,.371),(.44,.405)):
        fs.append(detail(ring_y(r,y,.018,.012,'gWoodDark',16)))
    fs.append(tube([[.42*math.cos(math.pi*k/20),.52+.32*math.sin(math.pi*k/20),0] for k in range(21)],.023,C('gWoodDark'),8))
    put('basket_body','开放编筐壳体',fs,[.9,.87,.84],purpose='有壁厚、筐底和拱形提梁的资源篮')
    fs=[placed([spin([(0,0),(.19,0),(.21,.10),(.21,.64),(.19,.70),(0,.70)],'gCloth',14)],position=(0,.215,-.35),rotation=(90,0,0))[0]]
    for z in (-.22,.22):fs.append(detail(ring_tube([0,.215,z],.225,.222,.023,C('gLeather'),'xy',20,6)))
    fs.append(detail(plate(rect(.075,.06,(0,.41),.01),.024,'gCopper',at=(0,0,.22))))
    put('bedroll','双带卷铺盖',fs,[.50,.46,.70],purpose='营地睡具和背包挂载用卷状部件',collision='convex-hull')
