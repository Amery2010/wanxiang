"""Game-ready visual/kinematic mechanisms with explicit trigger and event recipes.

No game rules execute while browsing the catalogue. Runtime consumers decide
ownership, cooldowns, damage and physics; these assets export the agreed hooks.
"""
from .production import *
D='gameplay'
def p(k,n,f,s,**kw):return dp('game.'+k,n,'gameplay',f,s,D,theme='gameplay',**kw)
def a(k,n,items,**kw):return da('game-'+k,n,'gameplay',items,D,theme='gameplay',**kw)
def ip(k):return 'exp.game.'+k
def ia(k):return 'exp-game-'+k

def hook(id,kind,event,trigger=None,**kw):
    record=PARTS.get(id) or ASSEMBLIES[id]
    md=record.get('runtime',record.get('metadata',{}).get('runtime'))
    md['interaction']={'schema':'wx.interaction/1.0','kind':kind,'event':event,'authority':'consumer-game','trigger':trigger or {'shape':'none'},**kw}

def author():
    p('spawn_pad','出生平台 · 方位缺口与中心标记',[disk(.82,.10,'steel',[0,.05,0],16),ring(.74,.055,.018,'teal',position=[0,.11,0]),formbox(.10,.019,.42,'line',y=.114,z=.05),extrude([[-.17,0],[0,.24],[.17,0]],.021,'line',rotation=[90,0,0],position=[0,.125,.29])],[1.65,.16,1.65],material='mat.metal',ports=[socket('spawn',[0,.14,0],[0,1,0],'gameplay.trigger.v1')],collision=box_collision([1.64,.10,1.64]))
    p('checkpoint_flag','检查点旗 · 旗杆与弧面旗布',[disk(.25,.08,'stoneDark',[0,.04,0],12),rod([0,.08,0],[0,2.2,0],.025,'woodDark'),ico([.09,.10,.09],'productionBrass',[0,2.25,0],detail=0,distort=0),poly([[0,1.40,0],[.30,1.45,.08],[.61,1.40,.06],[.89,1.49,-.03],[.89,2.1,-.03],[.61,2.01,.06],[.30,2.10,.08],[0,2.04,0]],[[0,1,6,7],[1,2,5,6],[2,3,4,5]],'teal')],[1.18,2.31,.5],material='mat.fabric',ports=[socket('checkpoint',[0,0,0],[0,1,0],'gameplay.trigger.v1')],collision={'type':'capsule','radius':.03,'segment_start':[0,.08,0],'segment_end':[0,2.2,0]})
    capture=[]
    for i in range(12):
        aa=i*math.tau/12;bb=(i+.86)*math.tau/12
        outline=[[r*math.cos(t),r*math.sin(t)] for r,ts in [(1.45,[aa,(aa+bb)/2,bb]),(1.28,[bb,(aa+bb)/2,aa])] for t in ts]
        capture.append(extrude(outline,.05,'teal' if i%3 else 'productionBrass',rotation=[90,0,0],position=[0,.025,0]))
    p('capture_ring','占领区环 · 分段刻度与清空中心',capture,[2.92,.05,2.92],material='mat.paint',ports=[socket('zone',[0,.05,0],[0,1,0],'gameplay.trigger.v1')],collision={'type':'none','reason':'walk-through objective visual'})
    p('switch_box','机关开关座 · 嵌入按钮和护环',[formbox(.36,.25,.30,'steel'),disk(.070,.026,'red',[0,.273,.03],12),ring(.11,.025,.02,'productionBrass',position=[0,.271,.03]),formbox(.24,.055,.015,'charcoal',y=.11,z=.162)],[.36,.31,.34],material='mat.metal',collision=box_collision([.36,.30,.34]))
    p('lever','机关拉杆 · 根轴与球柄',[disk(.065,.18,'metal',[0,0,0],12,rotation=[90,0,0]),rod([0,0,0],[0,.45,0],.027,'metal'),ico([.12,.10,.10],'red',[0,.48,0],distort=0)],[.19,.62,.19],anchor='hinge',material='mat.metal')
    key=[ring(.075,.027,.025,'productionBrass',position=[0,.10,0],rotation=[90,0,0]),formbox(.030,.27,.025,'productionBrass',y=-.19),formbox(.08,.029,.025,'productionBrass',x=.026,y=-.17),formbox(.062,.029,.025,'productionBrass',x=.018,y=-.11)]
    p('key','机关钥匙 · 镂空匙环与齿形',key,[.16,.40,.035],anchor='center',material='mat.metal',ports=[socket('grip',[0,0,0],[0,0,-1],'character.hand.grip.v1',span=.04)])
    keyhole=[[-.025,-.048],[.025,-.048],[.013,.004],[.033,.03],[.02,.056],[-.02,.056],[-.033,.03],[-.013,.004]]
    p('lock','机关锁座 · 真正开口锁眼',[extrude([[-.13,-.13],[.13,-.13],[.15,.10],[.09,.16],[-.09,.16],[-.15,.10]],.060,'productionBrass',holes=[keyhole]),*[disk(.011,.010,'steel',[x,.105,.035],8,rotation=[90,0,0]) for x in [-.092,.092]]],[.33,.32,.08],anchor='center',material='mat.metal')
    panel=[*[formbox(.197,.055,1.0,'oak',x=-.4+i*.2) for i in range(5)],*[formbox(.065,.036,1.02,'woodDark',x=x,y=.055) for x in [-.38,.38]],*[disk(.012,.006,'metal',[x,.095,z],6) for x in [-.38,.38] for z in [-.40,.40]]]
    p('crate_panel','可破坏木箱面板 · 可独立拆分节点',panel,[1.04,.10,1.04],material='mat.wood',collision=box_collision([1,.09,1]))
    frag=extrude([[-.48,0],[-.12,.03],[.05,0],[.49,.02],[.46,.26],[.49,.49],[.14,.47],[-.03,.50],[-.49,.47]],.26,'stone',position=[0,0,0])
    p('wall_fragment','破碎墙块 · 可实例化裂缝单元',[frag],[1,.52,.26],material='mat.stone',collision={'type':'convex-hull','source':'authored fragment hull'})
    barrel=[lathe([[.34,0],[.39,.12],[.41,.48],[.39,.87],[.34,.96]],'red',16,cap=True),*[ring(.412,.025,.065,'steel',position=[0,y,0]) for y in [.15,.77]],disk(.052,.013,'steel',[.15,.975,0],10),extrude([[-.12,0],[0,.21],[.12,0]],.007,'yellow',position=[0,.40,.410]),formbox(.023,.082,.007,'charcoal',y=.43,z=.419)]
    p('hazard_barrel','危险桶道具 · 桶箍与警示铭牌',barrel,[.85,1.00,.85],material='mat.paint',collision={'type':'capsule','radius':.39,'segment_start':[0,.39,0],'segment_end':[0,.58,0]})
    spikes=[formbox(1.20,.09,1.2,'steel'),*[lathe([[.066,0],[.067,.055],[.008,.43]],'metal',8,cap=True,position=[x,.09,z]) for x in [-.4,0,.4] for z in [-.4,0,.4]]]
    p('spike_plate','地刺板 · 单独平移的刺组',spikes,[1.2,.53,1.2],anchor='hinge',material='mat.metal',collision=box_collision([1.2,.53,1.2]))
    pend=[rod([0,0,0],[0,-1.35,0],.024,'steel'),ico([.56,.60,.56],'steel',[0,-1.49,0],detail=0,distort=0)]
    for i in range(8):
        t=i*math.tau/8;pend += [rod([.20*math.sin(t),-1.49,.20*math.cos(t)],[.42*math.sin(t),-1.49,.42*math.cos(t)],.048,'metal',r2=.006,sides=6)]
    p('pendulum','摆锤陷阱 · 吊点与配重锤',pend,[.90,1.86,.90],anchor='hinge',material='mat.metal',collision={'type':'sphere','radius':.35,'center':[0,-1.49,0]})
    trap=[*[formbox(.234,.085,1.45,'oak',x=-.60+i*.24,y=-.085,z=.72) for i in range(6)],*[beam([x,-.13,.06],[x,-.13,1.39],.065,.065,'steel') for x in [-.51,.51]],*[disk(.055,.20,'metal',[x,0,0],10,rotation=[0,0,90]) for x in [-.5,.5]]]
    p('trapdoor','翻板门 · 板端铰轴与背面加劲',trap,[1.48,.22,1.5],anchor='hinge',material='mat.wood',collision=box_collision([1.46,.085,1.45],[0,-.0425,.72]))
    deck=[extrude([[-.82,-1.05],[.82,-1.05],[1.05,-.82],[1.05,.82],[.82,1.05],[-.82,1.05],[-1.05,.82],[-1.05,-.82]],.18,'steel',rotation=[90,0,0],position=[0,-.09,0]),*[box([.40,.015,.09],'yellow',[x,.013,z],bevel=.004,rotation=[0,45,0]) for x,z in [(-.7,-.78),(.7,-.78),(-.7,.78),(.7,.78)]],formbox(1.5,.025,1.5,'charcoal',y=.002)]
    p('moving_deck','移动平台 · 斜切角与防滑区',deck,[2.13,.24,2.13],anchor='hinge',material='mat.metal',ports=[socket('platform',[0,.05,0],[0,1,0],'gameplay.trigger.v1')],collision=box_collision([2.1,.18,2.1],[0,-.09,0]))
    arch=[extrude([[-1.25,0],[-.96,0],[-.95,1.9],[-.55,2.48],[0,2.65],[.55,2.48],[.95,1.9],[.96,0],[1.25,0],[1.25,2.0],[.73,2.77],[0,2.98],[-.73,2.77],[-1.25,2.0]],.34,'stoneDark'),*[ico([.15,.19,.10],'cyan',[x,y,.205],detail=0,distort=0,material='mat.emissive.cyan') for x,y in [(-1.1,.53),(-1.1,1.1),(-1.09,1.68),(-.68,2.56),(0,2.80),(.68,2.56),(1.09,1.68),(1.1,1.1),(1.1,.53)]]]
    p('portal_arch','传送门框 · 开放通道与独立符石',arch,[2.54,3.01,.49],material='mat.stone',collision={'type':'authored-mesh','static_only':True},ports=[socket('portal',[0,1.25,0],[0,0,1],'gameplay.trigger.v1'),socket('fx',[0,1.35,0],[0,0,1],'fx.emitter.v1')])
    spring=[[.32*math.sin(j*math.tau/12),.07+j*.005,.32*math.cos(j*math.tau/12)] for j in range(49)]
    p('jump_pad','弹跳板 · 可见弹簧与踏面',[formbox(1.10,.09,1.1,'steel'),tube(spring,.017,'metal',6),disk(.55,.065,'teal',[0,.35,0],16),extrude([[-.14,-.14],[0,.12],[.14,-.14]],.011,'line',rotation=[90,0,0],position=[0,.39,0])],[1.14,.41,1.14],material='mat.metal',collision=box_collision([1.1,.41,1.1]))
    gem=topo([[0,.5,0],[-.14,.19,-.14],[.14,.19,-.14],[.14,.19,.14],[-.14,.19,.14],[0,-.18,0]],[[0,1,2],[0,2,3],[0,3,4],[0,4,1],[1,5,2],[2,5,3],[3,5,4],[4,5,1]],'cyan')
    p('pickup','拾取物核心 · 六面晶石',[gem,ring(.26,.012,.02,'productionBrass',position=[0,-.16,0])],[.54,.70,.54],anchor='center',material='mat.emissive.cyan',ports=[socket('pickup',[0,0,0],[0,1,0],'gameplay.trigger.v1')])
    p('fx_socket','特效定位代理 · 发射方向与标定轴',[ring(.15,.016,.012,'steel'),rod([0,0,0],[0,.35,0],.009,'cyan'),lathe([[.031,.27],[.004,.37]],'cyan',8,cap=True)],[.34,.39,.34],material='mat.metal',ports=[socket('emitter',[0,0,0],[0,1,0],'fx.emitter.v1')],description='编辑器可视代理；运行时按helper_only标记隐藏，不导出模拟粒子。')
    PARTS[ip('fx_socket')]['runtime']['helper_only']=True
    hook(ip('spawn_pad'),'spawn','spawn.request',{'shape':'sphere','radius':.8,'center':[0,.5,0]})
    hook(ip('checkpoint_flag'),'checkpoint','checkpoint.enter',{'shape':'sphere','radius':1,'center':[0,.7,0]})
    hook(ip('capture_ring'),'capture','capture.occupancy',{'shape':'sphere','radius':1.4,'center':[0,.3,0]})
    hook(ip('key'),'key','key.collect',{'shape':'sphere','radius':.3,'center':[0,0,0]},key_id='default')
    hook(ip('lock'),'lock','lock.interact',{'shape':'sphere','radius':.6,'center':[0,0,0]},key_id='default')
    hook(ip('hazard_barrel'),'breakable','barrel.destroyed',{'shape':'none'},fragment_policy='consumer-generated',damage_policy='consumer-only')
    hook(ip('jump_pad'),'jump','jump.activate',{'shape':'box','size':[1.1,.3,1.1],'center':[0,.5,0]},direction=[0,1,0])
    hook(ip('pickup'),'pickup','pickup.collect',{'shape':'sphere','radius':.35,'center':[0,.15,0]})
    hook(ip('fx_socket'),'emitter','fx.emit',helper_only=True)
    a('lever_switch','拉杆开关 · 实际转轴',[pi('base',ip('switch_box')),pi('lever',ip('lever'),[0,.32,0])],metadata=controls(turn('lever','开关角度','lever',-40,40,[1,0,0])))
    hook(ia('lever_switch'),'switch','switch.changed',{'shape':'sphere','radius':.6,'center':[0,.4,0]},state_control='lever')
    motion(ia('lever_switch'),'lever',axis=[1,0,0],values=[-40,-40,40,40,-40],seconds=3,name='Switch toggle')
    a('trapdoor_mechanism','陷阱翻板 · 边框与铰接门叶',[pi('frame','exp.arch.window_opening',[0,0,.7],rot=[90,0,0],scale=[1.28,1.18,1.4]),pi('leaf',ip('trapdoor')),pi('lock',ip('lock'),[0,.02,1.12],rot=[90,0,0])],metadata=controls(turn('open','翻板开启','leaf',0,90,[1,0,0])))
    motion(ia('trapdoor_mechanism'),'leaf',axis=[1,0,0],values=[0,0,85,85,0],name='Trapdoor drop')
    a('spike_trap','伸缩地刺 · 防护座与移动刺组',[*[pi('border'+str(j),'exp.arch.beam',[x,0,z],rot=[0,angle,0],scale=[.77,.5,.65]) for j,(x,z,angle) in enumerate([(0,-.69,0),(0,.69,0),(-.69,0,90),(.69,0,90)])],pi('spikes',ip('spike_plate'),[0,-.42,0])],metadata=controls(slider('extend','地刺伸出','spikes',0,.42)))
    hook(ia('spike_trap'),'hazard','hazard.contact',{'shape':'box','size':[1.2,.45,1.2],'center':[0,.22,0]},state_control='extend',active_threshold=.25)
    motion(ia('spike_trap'),'spikes',values=[0,0,.42,.42,0],mode='translation',name='Spike cycle')
    a('pendulum_trap','摆锤机关 · 开放承重门架',[pi('frame','exp.arch.arch_opening',scale=[1.3,1.2,.7]),pi('hammer',ip('pendulum'),[0,3.18,0])],metadata=controls(turn('swing','摆动角度','hammer',-48,48,[0,0,1])))
    motion(ia('pendulum_trap'),'hammer',axis=[0,0,1],values=[-42,0,42,0,-42],seconds=2.5,name='Pendulum swing')
    pieces=[pi('bottom',ip('crate_panel')),pi('top',ip('crate_panel'),[0,1,0]),pi('front',ip('crate_panel'),[0,.5,.50],rot=[90,0,0]),pi('back',ip('crate_panel'),[0,.5,-.5],rot=[90,0,0]),pi('left',ip('crate_panel'),[-.5,.5,0],rot=[0,0,90]),pi('right',ip('crate_panel'),[.5,.5,0],rot=[0,0,90])]
    a('breakable_crate','可拆分木箱 · 六个独立面板节点',pieces,metadata={'runtime_fragment_nodes':[i['id'] for i in pieces]})
    hook(ia('breakable_crate'),'breakable','crate.break',fragments=[i['id'] for i in pieces])
    wall=[pi('fragment'+str(j*3+i),ip('wall_fragment'),[(i-1),j*.50,0]) for j in range(4) for i in range(3)]
    a('breakable_wall','可拆分石墙 · 十二个独立裂块',wall,metadata={'runtime_fragment_nodes':[i['id'] for i in wall]})
    hook(ia('breakable_wall'),'breakable','wall.break',fragments=[i['id'] for i in wall])
    a('platform_lift','升降平台 · 导向架与独立地板',[pi('guide','exp.industry.lift_frame',[0,0,-.70],scale=[1.6,1.45,1]),pi('deck',ip('moving_deck'),[0,.22,0])],metadata=controls(slider('height','平台高度','deck',0,2.55)))
    motion(ia('platform_lift'),'deck',values=[0,0,2.55,2.55,0],seconds=5,mode='translation',name='Platform lift')
    hook(ia('platform_lift'),'platform','platform.move',state_control='height')
    a('teleporter','传送平台 · 门框／触发区／发射挂点',[pi('arch',ip('portal_arch')),pi('base',ip('spawn_pad'),[0,0,.2]),pi('fx',ip('fx_socket'),[0,1.2,0],rot=[90,0,0])])
    hook(ia('teleporter'),'portal','portal.enter',{'shape':'box','size':[1.75,2.25,.75],'center':[0,1.15,0]},destination='set-by-consumer')
    a('checkpoint_station','检查点站 · 出生／旗帜／奖励',[pi('pad',ip('spawn_pad')),pi('flag',ip('checkpoint_flag'),[-1.05,0,-.3]),pi('reward',ip('pickup'),[.95,.50,0]),ai('supply',ia('breakable_crate'),[1.1,0,-1.4])],level=3)
    a('capture_objective','占领目标 · 圈域与解锁终端',[pi('zone',ip('capture_ring')),ai('switch',ia('lever_switch')),pi('lock',ip('lock'),[0,.13,.18]),pi('key',ip('key'),[1.25,.30,0]),pi('fx',ip('fx_socket'),[0,.65,0])],level=3)
    a('trap_course','机关走廊 · 分离触发的连续挑战',[*[pi('floor'+str(i),'exp.arch.floor',[0,0,z]) for i,z in enumerate([-4,-2,0])],ai('spikes',ia('spike_trap'),[0,0,-3]),ai('swing',ia('pendulum_trap'),[0,0,0]),ai('door',ia('trapdoor_mechanism'),[0,0,2.5]),pi('barrel',ip('hazard_barrel'),[1.7,0,3.5]),ai('wall',ia('breakable_wall'),[0,0,5.4])],level=3)
    a('platform_puzzle','平台关卡套组 · 弹跳／升降／传送',[pi('spawn',ip('spawn_pad'),[-2,0,-2]),pi('jump',ip('jump_pad'),[-.6,0,0]),ai('lift',ia('platform_lift'),[2.1,0,1]),ai('exit',ia('teleporter'),[2.1,2.78,3.8]),pi('landing','exp.arch.floor',[2.1,2.78,3.8],scale=[1.4,1,1.2]),pi('supportA','exp.arch.column',[1.15,0,4.45],scale=[.65,.88,.65]),pi('supportB','exp.arch.column',[3.05,0,4.45],scale=[.65,.88,.65]),pi('reward',ip('pickup'),[2.1,3.4,3])],level=3)
    finish_counts(D)
