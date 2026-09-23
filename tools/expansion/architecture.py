"""Sixty structural assets. Apertures are geometry, doors retain their hinges.

The 2m facade system is dimensioned around a 0.9m leaf, 2.1m clear door and
3m floor height. A 1/2/4m wall is one parameter family, not three catalogue IDs.
"""
from .production import *
D='architecture'
def p(k,n,f,s,**kw):return dp('arch.'+k,n,'arch',f,s,D,theme=kw.pop('theme','medieval'),**kw)
def a(k,n,items,**kw):return da('arch-'+k,n,'arch',items,D,theme=kw.pop('theme','medieval'),**kw)
def part_(k):return 'exp.arch.'+k
def asm(k):return 'exp-arch-'+k

def author():
    w=Q('width')
    p('wall','模块墙段 · 1/2/4米同源',[formbox(w,3,.24,'stucco')],[2,3,.24],
      ports=wall_ports(w),params=schema(width={'type':'number','enum':[1,2,4],'default':2,'title':'墙宽（米）'}),
      collision={'type':'authored-mesh','static_only':True,'source':'parameter-resolved wall'},material='mat.plaster')
    p('corner','直角墙角 · L形实截面',[extrude([[-.12,-.12],[1,-.12],[1,.12],[.12,.12],[.12,1],[-.12,1]],3,'stucco',rotation=[90,0,0],position=[0,1.5,0])],[1.12,3,1.12],collision={'type':'authored-mesh','static_only':True},material='mat.plaster')
    p('end_pier','墙端压顶与收口柱',[formbox(.34,2.94,.34,'sandstone'),formbox(.42,.12,.42,'stoneLight',y=2.88)],[.42,3,.42],collision=box_collision([.34,3,.34]),material='mat.stone')
    # Deep jambs + honest lintels leave the passage clear in geometry and collision.
    p('door_opening','标准门洞 · 净宽0.92米',[*frame(1.16,2.32,.28,.12,'sandstone',False)],[1.16,2.32,.28],
      ports=[socket('door',[-.46,.08,.04],[0,0,1],'arch.door.v1',span=.90,tangent=[1,0,0])],
      collision=opening_collision(1.16,2.32,.28,.12),material='mat.stone')
    p('window_opening','窗洞框 · 窗台与滴水口',[*frame(1.36,1.40,.28,.12,'sandstone'),formbox(1.52,.10,.42,'stoneLight',y=-.025,z=.055)],[1.52,1.45,.42],collision={'type':'authored-mesh','static_only':True},material='mat.stone')
    arch_outline=[[-1.2,0],[-.95,0],[-.95,1.4]]+[[.95*math.cos(t),1.4+.95*math.sin(t)] for t in [math.pi-i*math.pi/12 for i in range(13)]]+[[.95,0],[1.2,0],[1.2,2.7],[-1.2,2.7]]
    # Omit the duplicate tangent point at the beginning of the semicircle.
    arch_outline.pop(2)
    p('arch_opening','承重石拱 · 真实弧形开口',[extrude(arch_outline,.50,'sandstone'),*[box([.24,.20,.54],'stoneLight',[1.075*math.cos(t),1.4+1.075*math.sin(t),0],bevel=.02,rotation=[0,0,math.degrees(t)-90]) for t in [i*math.pi/8 for i in range(9)]]],[2.5,2.7,.56],collision={'type':'authored-mesh','static_only':True},material='mat.stone')
    p('floor','两米楼板 · 网格定位',[formbox(2,.18,2,'stoneLight',y=-.18)],[2,.18,2],ports=axis_ports('arch.floor.1m.v1',2,span=2),collision=box_collision([2,.18,2],[0,-.09,0]),material='mat.stone')
    p('foundation','阶梯地基 · 砌体台脚',[formbox(2.12,.20,2.12,'stoneDark'),formbox(2,.24,2,'sandstone',y=.20)],[2.12,.44,2.12],collision=box_collision([2.12,.44,2.12]),material='mat.stone')
    p('column','方柱 · 柱础与柱帽',[formbox(.48,.18,.48,'stoneLight'),formbox(.30,2.56,.30,'sandstone',y=.18),formbox(.48,.26,.48,'stoneLight',y=2.74)],[.48,3,.48],collision=box_collision([.36,3,.36]),material='mat.stone')
    p('beam','横梁 · 承托与榫眼',[formbox(2,.22,.20,'oak'),*[box([.11,.08,.22],'woodDark',[x,.09,0],bevel=.005) for x in [-.83,.83]]],[2,.22,.22],ports=wall_ports(2,.22,.2),collision=box_collision([2,.22,.2]),material='mat.wood')
    roof=topo([[-1.18,0,-1.16],[1.18,0,-1.16],[1.18,0,1.16],[-1.18,0,1.16],[0,1.12,-1.16],[0,1.12,1.16]],[[0,1,4],[3,5,2],[0,4,5,3],[4,1,2,5],[0,3,2,1]],'tile')
    p('pitched_roof','双坡瓦顶 · 分层檐线',[roof,*[box([.045,.035,2.34],'woodDark',[x,1.12*(1-abs(x)/1.18)+.018,0],bevel=.004) for x in [-.85,-.45,0,.45,.85]]],[2.40,1.18,2.36],material='mat.plaster',collision={'type':'authored-mesh','static_only':True})
    p('ridge','屋脊压瓦 · 弧顶截面',[extrude([[-.12,0],[-.12,.09],[0,.16],[.12,.09],[.12,0]],2.4,'tile')],[.24,.16,2.4],material='mat.plaster')
    p('eave','檐口构件 · 斜撑与挑梁',[formbox(2.2,.13,.30,'oak'),*[beam([x,0,-.11],[x,-.28,-.35],.06,.06,'woodDark') for x in [-.8,0,.8]]],[2.2,.45,.5],material='mat.wood')
    p('stairs','直跑楼梯 · 8级防滑踏面',[*[formbox(1.2,.18*(i+1),.28,'sandstone',y=0,z=i*.28+.14) for i in range(8)]],[1.2,1.44,2.24],ports=[socket('bottom',[0,0,0],[0,0,-1],'arch.floor.1m.v1',span=1.2),socket('top',[0,1.44,2.24],[0,0,1],'arch.floor.1m.v1',span=1.2)],collision={'type':'authored-mesh','static_only':True},material='mat.stone')
    p('landing','转向平台 · 开放底部支撑',[formbox(1.44,.16,1.44,'sandstone',y=1.28),*legs(1.2,1.2,1.28,'stoneDark',.12)],[1.44,1.44,1.44],collision={'type':'authored-mesh','static_only':True},material='mat.stone')
    p('balcony_deck','阳台板 · 牛腿支承',[formbox(2,.18,1.2,'sandstone'),*[beam([x,0,-.40],[x,-.6,-.60],.14,.14,'stoneDark') for x in [-.65,.65]]],[2,.8,1.2],collision={'type':'authored-mesh','static_only':True},material='mat.stone')
    p('railing','栏杆 · 真实立柱间隙',[beam([-1,1.0,0],[1,1.0,0],.08,.08,'oak'),beam([-1,.15,0],[1,.15,0],.06,.06,'oak'),*[formbox(.055,1,.055,'oak',x=x) for x in [-.96,-.64,-.32,0,.32,.64,.96]]],[2.08,1.04,.08],collision={'type':'compound','shapes':[box_collision([2,1.05,.1])]},material='mat.wood')
    p('canopy','入口雨棚 · 拱形支架',[box([1.6,.08,.9],'teal',[0,0,.34],bevel=.015,rotation=[10,0,0]),*[beam([x,-.55,0],[x,-.04,.65],.055,.055,'steel') for x in [-.64,.64]]],[1.6,.65,.95],material='mat.paint')
    p('gutter','檐沟 · 开放U形截面',[extrude([[-.10,.08],[-.10,-.04],[-.07,-.08],[.07,-.08],[.10,-.04],[.10,.08],[.075,.08],[.075,-.02],[.05,-.055],[-.05,-.055],[-.075,-.02],[-.075,.08]],2,'copper')],[.20,.16,2],material='mat.metal')
    p('downpipe','雨水落管 · 偏置出水口',[tube([[0,2.6,0],[0,2.3,0],[0,2.1,.13],[0,.3,.13],[0,.14,.3]],.055,'copper',8),*[ring(.067,.014,.045,'steel',position=[0,y,.13]) for y in [.6,1.7]]],[.16,2.7,.42],material='mat.metal')
    door=[formbox(.88,2.12,.065,'oak',x=.44),*[box([.68,.045,.035],'woodDark',[.44,y,.052],bevel=.004) for y in [.15,.72,1.48,1.98]],rod([.75,1.0,.083],[.75,1.14,.083],.014,'productionBrass',sides=6),*[disk(.026,.12,'steel',[.02,y,0],8) for y in [.25,1.82]]]
    p('door_leaf','板门叶 · 左侧铰轴与门把',door,[.91,2.12,.12],ports=[socket('hinge',[0,0,0],[0,0,-1],'arch.door.v1',span=.9)],anchor='hinge',collision=box_collision([.88,2.12,.065],[.44,1.06,0]),material='mat.wood')
    p('roller_leaf','卷帘门叶 · 独立刚性平移',[*[formbox(2.6,.14,.08,'steel',y=i*.15) for i in range(16)],formbox(2.64,.07,.1,'charcoal')],[2.64,2.4,.1],anchor='hinge',collision=box_collision([2.64,2.4,.1]),material='mat.metal')
    p('window_sash','玻璃窗扇 · 中梃与铰轴',[*[dict(f,position=[add(f.get('position',[0,0,0])[0],.55),f.get('position',[0,0,0])[1],f.get('position',[0,0,0])[2]]) for f in frame(1.10,1.13,.055,.06,'oak')],formbox(1.0,1.0,.02,'glass',x=.55,y=.06,material='mat.glass'),formbox(.04,1.01,.06,'oak',x=.55,y=.06)],[1.1,1.13,.08],anchor='hinge',material='mat.wood',collision=box_collision([1.1,1.13,.06],[.55,.565,0]))
    p('louver','百叶遮阳板 · 倾斜叶片',[*frame(.55,1.2,.07,.05,'teal'),*[box([.46,.07,.08],'teal',[0,.12+i*.105,0],bevel=.008,rotation=[-25,0,0]) for i in range(10)]],[.55,1.2,.12],material='mat.paint')
    p('skylight','斜屋面天窗 · 凸缘玻璃',[*frame(.86,.9,.14,.09,'steel'),formbox(.68,.72,.025,'glass',y=.09,z=.03,material='mat.glass')],[.86,.9,.16],material='mat.metal')
    stones=[]
    for y in range(6):
        for x in range(4):stones.append(formbox(.487,.475,.36,'sandstone' if (x+y)%3 else 'stoneLight',x=-.75+x*.5,y=y*.5,bevel=.025))
    p('stone_wall','砌石墙 · 交错砌缝与压顶',[formbox(2,3,.30,'mortar'),*stones],[2,3,.36],ports=wall_ports(2,3,.36),collision=box_collision([2,3,.36]),material='mat.stone')
    p('timber_wall','木骨墙 · 木梁与填充层',[formbox(2,3,.18,'stucco'),*[formbox(.13,3,.24,'woodDark',x=x) for x in [-.93,0,.93]],formbox(2,.14,.24,'woodDark',y=1.3),formbox(2,.14,.24,'woodDark',y=2.86),beam([-.87,.13,.12],[-.1,1.28,.12],.10,.05,'woodDark'),beam([.1,1.44,.12],[.87,2.82,.12],.10,.05,'woodDark')],[2,3,.26],ports=wall_ports(2,3,.24),collision=box_collision([2,3,.24]),material='mat.wood')
    p('battlement','城墙垛口 · 连续走道边',[formbox(2,.45,.40,'stone'),*[formbox(.42,.55,.45,'sandstone',x=x,y=.45) for x in [-.79,0,.79]]],[2,1,.45],collision={'type':'authored-mesh','static_only':True},theme='castle',material='mat.stone')
    p('round_tower','圆塔层 · 空心通行空间',[round_tube(1.45,1.12,3,'sandstone',16),round_tube(1.53,1.12,.15,'stoneLight',16)],[3.06,3,3.06],collision={'type':'authored-mesh','static_only':True},theme='castle',material='mat.stone')
    p('portcullis','升降铁闸 · 竖栅与横箍',[*[rod([x,0,0],[x,2.5,0],.027,'charcoal',sides=6) for x in [-.9,-.6,-.3,0,.3,.6,.9]],*[formbox(2,.075,.09,'steel',y=y) for y in [.45,1.3,2.25]]],[2,2.5,.1],anchor='hinge',collision={'type':'compound','shapes':[box_collision([2,2.5,.1])]},theme='castle',material='mat.metal')
    p('drawbridge','吊桥桥板 · 桥端转轴',[*[formbox(2.2,.16,.21,'oak',y=-.16,z=.11+i*.225) for i in range(14)],*[beam([x,-.22,0],[x,-.22,3.15],.10,.12,'woodDark') for x in [-.84,.84]]],[2.2,.30,3.2],anchor='hinge',collision=box_collision([2.2,.18,3.15],[0,-.09,1.575]),theme='castle',material='mat.wood')
    p('buttress','石扶壁 · 外展基座',[extrude([[-.35,0],[.60,0],[.28,.55],[.10,2.8],[-.35,2.8]],.52,'sandstone')],[.95,2.8,.52],collision={'type':'authored-mesh','static_only':True},theme='castle',material='mat.stone')
    p('carved_column','雕刻柱 · 柱腰与莲瓣柱冠',[lathe([[.28,0],[.29,.12],[.20,.22],[.16,1.9],[.22,2.0],[.30,2.15],[.29,2.24]],'sandstone',10,cap=True),*[box([.075,.07,.56],'stoneLight',[0,y,0],bevel=.015,rotation=[0,ang,0]) for y in [.17,2.10] for ang in [0,60,120]]],[.62,2.24,.62],collision={'type':'capsule','radius':.23,'segment_start':[0,.23,0],'segment_end':[0,2,0]},theme='dungeon',material='mat.stone')
    p('dungeon_wall','地牢墙 · 深砌缝与上缘残损',[formbox(2,2.8,.45,'stoneDark'),*[formbox(.63,.53,.49,'stone',x=-.67+x*.67,y=.02+y*.56,bevel=.02) for y in range(5) for x in range(3)]],[2,2.82,.49],ports=wall_ports(2,2.8,.49),collision=box_collision([2,2.8,.49]),theme='dungeon',material='mat.stone')
    p('sewer','地下水渠 · 不封闭的槽底',[formbox(1.6,.16,2,'stoneDark',y=-.16),formbox(.22,.85,2,'stone',x=-.69),formbox(.22,.85,2,'stone',x=.69)],[1.6,1.01,2],ports=axis_ports('arch.floor.1m.v1',2,span=1.6),collision={'type':'authored-mesh','static_only':True},theme='dungeon',material='mat.stone')
    p('cave_vault','洞厅拱肋 · 独立厚壁弧',[extrude([[-2,0],[-1.70,0],[-1.65,1.8],[-1.15,2.65],[0,3.15],[1.15,2.65],[1.65,1.8],[1.70,0],[2,0],[2.05,1.8],[1.35,3.0],[0,3.5],[-1.35,3.0],[-2.05,1.8]],.6,'stoneDark')],[4.1,3.5,.6],collision={'type':'authored-mesh','static_only':True},theme='dungeon',material='mat.stone')
    # Eighteen functional units. Attachments on the wall and channel runs are solved.
    a('wall_run','可拼接立面 · 三段真实吸附',[pi('left',part_('wall')),mate('middle',part_('wall'),'left','west','east'),mate('right',part_('wall'),'middle','west','east')],ports=[exported('left','west','west'),exported('right','east','east')])
    a('corner_bay','转角开窗间 · 窗洞与端柱',[pi('angle',part_('corner')),pi('window',part_('window_opening'),[.55,1.0,0]),pi('end',part_('end_pier'),[0,0,1])])
    a('hinged_door','单开门 · 门框与真实铰轴',[pi('frame',part_('door_opening')),pi('leaf',part_('door_leaf'),[-.45,.08,.04])],metadata=controls(turn('open','开门','leaf',0,105)))
    motion(asm('hinged_door'),'leaf',values=[0,0,95,95,0],name='Door open / close')
    a('double_door','双扇门 · 对向铰链',[pi('left',part_('door_leaf'),[-.89,0,0]),pi('right',part_('door_leaf'),[.89,0,0],rot=[0,180,0]),pi('lintel',part_('beam'),[0,2.12,0])],metadata=controls(turn('left','左门','left',0,100),turn('right','右门','right',-100,0)))
    a('roller_door','卷帘门 · 平移导轨总成',[pi('leaf',part_('roller_leaf')),pi('postL',part_('column'),[-1.55,0,0]),pi('postR',part_('column'),[1.55,0,0]),pi('canopy',part_('canopy'),[0,2.85,0])],metadata=controls(slider('lift','门叶提升','leaf',0,2.5)),theme='industrial')
    motion(asm('roller_door'),'leaf',values=[0,0,2.5,2.5,0],name='Lift door',mode='translation')
    a('casement','平开窗 · 洞框／玻璃窗扇',[pi('frame',part_('window_opening')),pi('sash',part_('window_sash'),[-.55,.13,.02])],metadata=controls(turn('open','窗扇开启','sash',0,85)))
    a('shutters','百叶双扇窗 · 对向开启',[ai('window',asm('casement')),pi('left',part_('louver'),[-.88,.10,.15]),pi('right',part_('louver'),[.88,.10,.15])])
    a('roof_bay','完整屋顶跨 · 屋脊／檐沟／天窗',[pi('roof',part_('pitched_roof')),pi('ridge',part_('ridge'),[0,1.12,0]),pi('eaveL',part_('eave'),[-1.16,0,0],rot=[0,90,0]),pi('gutter',part_('gutter'),[1.22,0,0]),pi('sky',part_('skylight'),[.63,.56,.1],rot=[0,0,-46]),pi('drain',part_('downpipe'),[1.24,-2.62,-.9])])
    a('stairs_l','L形双跑楼梯 · 休息平台',[pi('lower',part_('stairs')),pi('landing',part_('landing'),[0,0,2.95]),pi('upper',part_('stairs'),[.72,1.44,2.95],rot=[0,90,0])])
    a('stairs_u','U形双跑楼梯 · 反向折返',[pi('lower',part_('stairs')),pi('landing',part_('landing'),[.55,0,2.96],scale=[1.8,1,1]),pi('upper',part_('stairs'),[1.5,1.44,3.65],rot=[0,180,0])])
    a('balcony','带栏阳台 · 开放入口',[pi('deck',part_('balcony_deck')),pi('front',part_('railing'),[0,.18,.56]),pi('left',part_('railing'),[-.94,.18,0],rot=[0,90,0],scale=[.55,1,1]),pi('right',part_('railing'),[.94,.18,0],rot=[0,90,0],scale=[.55,1,1])])
    a('sewer_run','地渠直线 · 三段精确连接',[pi('channel',part_('sewer')),mate('next',part_('sewer'),'channel'),mate('last',part_('sewer'),'next')],ports=[exported('channel','in','in'),exported('last')],theme='dungeon')
    a('fortress_wall','城墙走道段 · 垛口与扶壁',[pi('wall',part_('stone_wall')),pi('battlements',part_('battlement'),[0,3,0]),pi('support',part_('buttress'),[0,0,-.35],rot=[0,90,0]),pi('walkway',part_('floor'),[0,3,-1])],theme='castle')
    a('round_tower','圆塔层组 · 空心楼层与垛口',[pi('base',part_('round_tower')),pi('top',part_('round_tower'),[0,3,0]),*[pi('merlon'+str(i),part_('end_pier'),[1.25*math.sin(i*math.pi/4),6,1.25*math.cos(i*math.pi/4)],scale=[.7,.23,.7]) for i in range(8)]],theme='castle')
    a('square_tower','方塔层组 · 四侧砌体与楼板',[*[pi('wall'+str(i),part_('stone_wall'),[math.sin(i*math.pi/2),0,math.cos(i*math.pi/2)],rot=[0,i*90,0]) for i in range(4)],pi('floor',part_('floor'),[0,3,0]),*[pi('top'+str(i),part_('battlement'),[math.sin(i*math.pi/2),3,math.cos(i*math.pi/2)],rot=[0,i*90,0]) for i in range(4)]],theme='castle')
    a('gate_bridge','城门吊桥 · 闸门与桥端转轴',[pi('arch',part_('arch_opening')),pi('gate',part_('portcullis'),[0,0,-.02]),pi('bridge',part_('drawbridge'),[0,0,.28])],metadata=controls(slider('gate','闸门提升','gate',0,2.5),turn('bridge','吊桥抬升','bridge',-75,0,[1,0,0])),theme='castle')
    a('market_stall','市场摊位 · 柱架／遮棚／台面',[pi('counter','exp.interior.dining_table',[0,0,.28],scale=[1.0,.92,.56]),pi('roof',part_('pitched_roof'),[0,2.05,0],params={'palette':{C('tile'):C('teal')}}),*[pi('post'+str(i),part_('column'),[x,0,z],scale=[.32,.68,.32]) for i,(x,z) in enumerate([(-.9,-.7),(.9,-.7),(-.9,.7),(.9,.7)])]],description='柱架提供真实遮棚结构；陈列货物由使用场景添加。')
    a('dungeon_cell','地牢隔间 · 栅门与开放入口',[pi('back',part_('dungeon_wall'),[0,0,-1]),pi('side',part_('dungeon_wall'),[-1,0,0],rot=[0,90,0]),pi('gate',part_('portcullis'),[0,0,1]),pi('floor',part_('floor'),[0,0,0])],metadata=controls(slider('release','栅门升起','gate',0,2.5)),theme='dungeon')
    # Six complete architectural recipes; the doorway is not backed by a solid wall.
    for key,name,timber in [('residence','模块化平顶民居',False),('timber_house','中世纪木石住宅',True)]:
        wall=part_('timber_wall' if timber else 'wall')
        items=[*[pi('base'+str(i),part_('foundation'),[x,-.44,z]) for i,(x,z) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)])],
               *[pi('back'+str(i),wall,[x,0,-2]) for i,x in enumerate([-1,1])],
               *[pi('side'+str(i),wall,[x,0,z],rot=[0,90,0]) for i,(x,z) in enumerate([(-2,-1),(-2,1),(2,-1),(2,1)])],
               ai('entrance',asm('hinged_door'),[0,0,2]),
               pi('doorheader',wall,[0,2.32,2],scale=[.58,.68/3,1])]
        for sg in [-1,1]:
            x=sg*1.29
            items += [pi('sillwall'+str(sg),wall,[x,0,2],scale=[.71,1.05/3,1]),
                      pi('headwall'+str(sg),wall,[x,2.45,2],scale=[.71,.55/3,1]),
                      ai('window'+str(sg),asm('casement'),[x,1.05,2]),
                      pi('edge'+str(sg),part_('end_pier'),[sg*1.95,0,2],scale=[.27,1,.75])]
        if timber:
            items += [pi('roof',part_('pitched_roof'),[0,3,0],scale=[1.83,1.35,1.84]),
                      pi('ridge',part_('ridge'),[0,4.50,0],scale=[1,1,1.84]),
                      pi('frontbeam',part_('beam'),[0,2.90,2.11],scale=[2.1,1,1]),
                      pi('rear_eave',part_('eave'),[0,3,-2.10],scale=[1.9,1,1]),
                      pi('rain',part_('downpipe'),[2.13,.36,-1.8]),
                      pi('gutter',part_('gutter'),[2.15,3,0],scale=[1,1,2.15])]
        else:
            items += [*[pi('roofslab'+str(i),part_('floor'),[x,3.08,z]) for i,(x,z) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)])],
                      pi('canopy',part_('canopy'),[0,2.39,2.02]),
                      *[pi('parapet'+str(i),part_('wall'),[math.sin(i*math.pi/2)*2,3.08,math.cos(i*math.pi/2)*2],rot=[0,i*90,0],scale=[2,.10,1]) for i in range(4)]]
        a(key,name,items,level=3)
    a('gatehouse','城门楼 · 双塔／闸门／吊桥',[ai('gate',asm('gate_bridge')),ai('left',asm('round_tower'),[-3,0,0]),ai('right',asm('round_tower'),[3,0,0]),pi('bridgebeam',part_('beam'),[0,3,0],scale=[2.1,1.8,4])],level=3,theme='castle')
    a('watchtower','石木瞭望塔 · 登高结构',[ai('tower',asm('square_tower')),ai('steps',asm('stairs_l'),[2,0,-2]),ai('cap',asm('roof_bay'),[0,4.0,0])],level=3,theme='castle')
    a('dungeon_room','地牢房间 · 牢室与石柱通道',[ai('cell',asm('dungeon_cell'),[-1.2,0,-1]),pi('arch',part_('arch_opening'),[1.4,0,1.7]),*[pi('floor'+str(i),part_('floor'),[x,0,z]) for i,(x,z) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)])],pi('column',part_('carved_column'),[2.4,0,-1.3]),pi('rear',part_('dungeon_wall'),[1.2,0,-2])],level=3,theme='dungeon')
    a('cave_hall','洞穴拱厅 · 肋拱与地下水道',[*[pi('vault'+str(i),part_('cave_vault'),[0,0,z]) for i,z in enumerate([-3,0,3])],ai('waterway',asm('sewer_run'),[0,-.15,0]),*[pi('ledge'+str(i),part_('floor'),[x,0,z]) for i,(x,z) in enumerate([(-1.8,-2),(-1.8,0),(-1.8,2),(1.8,-2),(1.8,0),(1.8,2)])]],level=3,theme='dungeon')
    finish_counts(D)
