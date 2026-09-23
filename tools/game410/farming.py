"""Harvest-scale crops, irrigation pieces and garden construction profiles."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,domain='nature',**kw):return emit('farming',domain,key,name,fs,size,**kw)
    fs=[wedge_xz([[-.5,-.5],[.5,-.5],[.5,.5],[-.5,.5]],0,.08,'gSoil')]
    for x in (-.34,0,.34):
        fs.append(grid_shell(lambda u,v,x=x:[x+(u-.5)*.28,.08+.09*math.sin(u*math.pi),v-0.5],6,4,.045,C('gSoil')))
    put('tilled_furrow','三垄耕地拼块',fs,[1,.17,1],domain='terrain',purpose='一米地块上的连续垄沟，可重复拼接')
    fs=[]
    for k in range(7):
        a=k*math.tau/7;root=[.055*math.cos(a),0,.055*math.sin(a)];tip=[.15*math.cos(a),.62-.04*(k%3),.15*math.sin(a)]
        fs.append(tube([root,tip,[tip[0]+.05,.57,tip[2]]],[.008,.005,.003],C('gLeafDark'),6))
        fs.append(flattened_leaf([root[0],.14,root[2]],[tip[0]*1.7,.41,tip[2]*1.7],.022,'gLeaf'))
        for j in range(3):fs.append(detail(ellipsoid([tip[0]+.01*j,tip[1]-.025*j,tip[2]],[.025,.04,.025],C('gAmber'),8,4)))
    put('rice_clump','成熟水稻丛',fs,[.54,.67,.54],purpose='有弯穗和狭叶的水田成熟作物',collision='none')
    fs=[ellipsoid([0,.26,0],[.16,.42,.16],C('gAmber'),12,8)]
    for a in (0,120,240):
        cs,sn=math.cos(math.radians(a)),math.sin(math.radians(a));fs.append(flattened_leaf([0,.02,0],[cs*.20,.40,sn*.20],.095,'gLeaf'))
    for j in range(9):
        y=.095+j*.037;rad=.079*math.sqrt(max(.01,1-((y-.26)/.21)**2))
        for k in range(8):
            a=k*math.tau/8+(j%2)*.035
            kernel=ellipsoid([0,0,0],[.048,.041,.027],C('gKernel' if (j+k)%3 else 'gAmber'),8,4)
            fs += [detail(x) for x in placed([kernel],position=(rad*math.sin(a),y,rad*math.cos(a)),rotation=(0,math.degrees(a),0))]
    put('corn_husk','带苞叶玉米穗',fs,[.43,.50,.43],purpose='可从植株分离的玉米收获物',collision='convex-hull')
    fs=[]
    for k in range(5):
        a=k*math.tau/5;tip=[.20*math.cos(a),.35,.20*math.sin(a)]
        fs.append(tube([[0,0,0],tip],.009,C('gLeafDark'),6))
        for j in (0,1):fs.append(flattened_leaf([tip[0]*.5,.18,tip[2]*.5],[tip[0]+(.10 if j else -.10),.34,tip[2]+.08],.08,'gLeaf'))
        fs.append(detail(ellipsoid([tip[0],.36,tip[2]],[.075,.045,.075],C('gCream'),8,4)))
    put('potato_foliage','马铃薯叶簇',fs,[.67,.40,.60],purpose='低矮复叶冠层，可与地下块茎道具组合',collision='none')
    fs=[]
    for k in range(6):
        a=k*math.tau/6;tip=[.23*math.cos(a),.17,.23*math.sin(a)]
        fs.append(flattened_leaf([0,.02,0],tip,.10,'gLeaf'))
    for x,z in [(-.13,.17),(.16,.09),(.02,-.16)]:
        fs += [ellipsoid([x,.105,z],[.08,.13,.08],C('gRed'),10,5),detail(flattened_leaf([x,.18,z],[x+.04,.19,z],.035,'gLeafDark'))]
    put('strawberry_crown','结果草莓冠丛',fs,[.56,.21,.56],purpose='贴地草莓叶冠与可读红果组合',collision='none')
    fs=[tube([[0,.38,0],[0,.48,0],[.06,.53,0]],.012,C('gWoodDark'),6)]
    for j in range(4):
        count=5-j;r=.095-.02*j
        for k in range(count):
            a=k*math.tau/count+.4*j;fs.append(ellipsoid([r*math.cos(a),.35-j*.07,r*math.sin(a)],[.092,.10,.092],C('gPurple'),8,5))
    fs.append(detail(flattened_leaf([0,.45,0],[.17,.53,.03],.10,'gLeaf')))
    put('grape_cluster','垂挂葡萄果串',fs,[.34,.55,.30],purpose='由宽肩收束到尾端的采收果串',collision='convex-hull')
    fs=[tube([[0,0,0],[0,.24,0],[.08,.42,0]],[.055,.052,.023],C('gBark'),9),tube([[0,.22,0],[-.09,.42,0]],[.027,.018],C('gBark'),8)]
    for y in (.19,.22,.25,.28):fs.append(detail(ring_y(.059,y,.019,.009,'gCream',12)))
    put('orchard_graft','果树嫁接分枝节',fs,[.22,.45,.12],purpose='有绑扎层与双枝方向的嫁接节点')
    fs=[basebox([.50,.035,.08],[0,0,0],C('gWoodDark')),basebox([.50,.035,.08],[0,.48,0],C('gWoodDark'))]
    fs += [basebox([.035,.48,.06],[x,.025,0],C('gWood')) for x in (-.215,.215)]
    # Thin honeycomb sheet: openings are real, not painted black circles.
    for row in range(5):
        for col in range(5):
            x=-.164+col*.082+(row%2)*.02;y=.087+row*.083
            fs.append(plate(circle(.043,(x,y),6),.022,'gAmber',holes=[circle(.033,(x,y),6)]))
    put('beehive_frame','蜂箱可抽巢框',fs,[.50,.515,.08],domain='props',purpose='有贯通六角孔格的可抽取蜂巢框')
    outer=[[-.38,.33],[-.29,.04],[.29,.04],[.38,.33],[.32,.35],[.24,.10],[-.24,.10],[-.32,.35]]
    fs=[plate(outer,.11,'gStoneWarm')]
    put('trough_end','饲料槽端口弧片',fs,[.76,.35,.11],domain='props',purpose='开放槽形接口，配合连续槽身使用')
    fs=[basebox([.51,.46,.045],[0,0,0],C('gWood'))]
    for y in (.10,.36):fs.append(detail(block([.55,.045,.067],[0,y,0],C('gSteel'),.007)))
    fs.append(ring_tube([0,.50,0],.08,.07,.016,C('gSteel'),'xy',16,6))
    put('sluice_board','农渠提拉闸板',fs,[.55,.585,.067],domain='props',purpose='可独立竖直移动的灌溉闸板；不含流体模拟')
    fs=[]
    for k in range(9):
        x=(k-4)*.016;fs.append(tube([[0,0,0],[x,.14,0],[x*2,.27+.04*(k%2),0]],[.012,.010,.004],C('gAmber'),5))
    fs.append(detail(ring_y(.05,.10,.03,.01,'gLeather',10)))
    put('straw_hand','稻草人散束手端',fs,[.29,.32,.11],purpose='从绑束到散开草梗的角色替代手部',collision='none')
    fs=[beam([-.42,.12,0],[.42,.12,0],.033,C('gWoodDark')),beam([-.55,.80,0],[.55,.80,0],.032,C('gWoodDark'))]
    for x in (-.52,-.26,0,.26,.52):fs.append(beam([0,0,0],[x,1.22,0],.027,C('gWood')))
    put('fan_trellis','扇形攀藤格架',fs,[1.15,1.25,.04],domain='props',purpose='花园与菜园用扇形重复支架')
