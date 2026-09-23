"""62 reusable gameplay mechanisms. Hooks are contracts, not a game engine."""
from .common import *
D='gameplay'

def event_contract(kind,action,node,*,trigger=False):
    return {'schema':'wx.interaction/1.0','kind':kind,'action':action,'event':action,'authority':'consumer-game','target_node':node,
            'events':['activate','release','reset'],'consumer_implemented':True,
            'trigger':{'shape':'box','size':[.8,.5,.6],'center':[0,.25,0],'sensor':True} if trigger else {'shape':'none'}}

def author():
    for key in ids(D,'lock'):
        items=[plate('mount',[.44,.045,.28]),p('case',D,'lock','padlock_body',[.20,.20,.12],[0,.045,0]),
               p('mechanism',D,'lock',key,[.24,.12,.10],[0,.19,0],moving=True),
               p('keeper',D,'lock','keeper',[.12,.14,.11],[.16,.15,0]),*fasteners('fix',[[-.16,.04,-.085],[.16,.04,.085]],.025)]
        if key in ('combination','cam','warded_key','keyway','seal'):
            ctr=[control('turn','mechanism','锁芯转角',90)]
        else:ctr=[control('release','mechanism','锁件退出',.12,axis=(-1,0,0),mode='translation')]
        if key=='combination':
            items.extend(p('wheel'+str(i),D,'lock','combination',[.07,.06,.07],[x,.11,.084],[90,0,0],optional=True) for i,x in enumerate([-.07,0,.07]))
        elif key=='socket':items.append(p('rune',D,'pickup','crystal',[.09,.12,.08],[0,.24,0],optional=True))
        register(D,'lock',key,label(pid(D,'lock',key))+'锁止机构组',items,[.49,.38,.34],mount=[.32,.20],controls=ctr,
                 interaction=event_contract('lock','unlock','mechanism'),notes=['演示节点状态；密码校验、钥匙权限和持久化必须在游戏侧实现。'])
    for key in ids(D,'trigger'):
        items=[plate('base',[.58,.075,.40]),p('housing','industry','structure','saddle',[.25,.14,.21],[0,.075,0]),
               p('actuator',D,'trigger',key,[.32,.24,.26],[0,.17,0],moving=True),*fasteners('fix',[[-.22,.07,-.13],[.22,.07,.13]],.028)]
        if key in ('button','pressure','sensor_plate'):
            ctr=[control('press','actuator','压下行程',.055,axis=(0,-1,0),mode='translation')]
        elif key in ('wheel','crank','pulley','dial'):
            ctr=[control('turn','actuator','转动角',360)]
        elif key=='tripwire':
            items.extend([post('anchor',.24,[.31,.075,0],.035),bar('wire',[0,.26,0],[.32,.26,0],.007,section='bulb')]);ctr=[]
        else:ctr=[control('pull','actuator','扳动角',45,-25,axis=(1,0,0))]
        register(D,'trigger',key,label(pid(D,'trigger',key))+'信号触发组',items,[.72,.48,.46],mount=[.44,.26],controls=ctr,
                 interaction=event_contract('trigger','activate','actuator',trigger=True))
    for key in ids(D,'trap'):
        items=[plate('mount',[.8,.12,.62]),p('carrier','industry','structure','saddle',[.36,.22,.30],[0,.12,0]),
               p('hazard',D,'trap',key,[.50,.32,.40],[0,.34,0],moving=True),
               *fasteners('fix',[[x,.11,z] for x in [-.31,.31] for z in [-.21,.21]],.045)]
        if key in ('saw','blade'):
            ctr=[control('spin','hazard','旋转相位',360)]
            items.append(p('shaft','industry','drive','keyshaft',[.07,.36,.07],[0,.18,0]))
        elif key=='pendulum':
            items[2]['pivot']=bounds(pid(D,'trap',key))[1].copy();items[2]['pivot'][0]=0;items[2]['pivot'][2]=0
            items.append(post('support',.82,[0,.12,-.20],.09));items[2]['position']=[0,.89,0]
            items.append(bar('arm',[0,.89,0],[0,.55,0],.06))
            ctr=[control('swing','hazard','摆动角',55,-55,axis=(0,0,1))]
        elif key in ('crusher','spike'):
            ctr=[control('stroke','hazard','触发行程',.35,axis=(0,1,0),mode='translation')]
            items.append(p('guide',D,'platform','lift_shoe',[.18,.4,.18],[0,.12,-.24]))
        elif key=='jaw':
            items.append(p('otherJaw',D,'trap','jaw',[.50,.32,.40],[0,.34,-.10],[0,180,0],moving=True))
            ctr=[control('close','hazard','第一夹颚',55,axis=(1,0,0)),control('opposite','otherJaw','第二夹颚',55,axis=(-1,0,0))]
        else:
            ctr=[];items.append(p('fxSocket',D,'fx','emitter_cup',[.12,.12,.12],[0,.50,0],collision={'type':'none'}))
        register(D,'trap',key,label(pid(D,'trap',key))+'机关模块',items,[.90,1.03,.72],mount=[.62,.42],controls=ctr,
                 interaction=event_contract('hazard','fire','hazard',trigger=True),notes=['只提供视觉机构与触发契约；伤害判定、发射物和特效由游戏实现。'])
    for key in ids(D,'platform'):
        items=[plate('foundation',[1.0,.12,.74]),p('mechanism',D,'platform',key,[.5,.18,.42],[0,.13,0]),
               plate('deck',[.88,.10,.64],[0,.34,0],moving=True),
               p('edge','architecture','section','l',[.86,.055,.06],[0,.10,.28],parent='deck'),
               *fasteners('fix',[[-.35,.115,-.25],[.35,.115,.25]],.04)]
        if key=='hinge_plate':
            items[2]=plate('deck',[.88,.10,.64],[0,.34,-.32],anchor='back',moving=True)
            ctr=[control('tilt','deck','翻板角',90,axis=(1,0,0))]
        elif key in ('moving_bracket','rail_stop','retracting','bridge_lock'):
            items.append(bar('rail',[-.55,.24,0],[.55,.24,0],.06));ctr=[control('travel','deck','横移行程',.38,axis=(1,0,0),mode='translation')]
        else:
            items.append(p('guide',D,'platform','lift_shoe',[.14,.46,.14],[0,.12,-.3]));ctr=[control('lift','deck','升降行程',.38,axis=(0,1,0),mode='translation')]
        register(D,'platform',key,label(pid(D,'platform',key))+'承载运动组',items,[1.12,.95,.8],mount=[.8,.5],controls=ctr,
                 interaction=event_contract('platform','move','deck'),notes=['碰撞代理随 deck 的刚体节点运动；没有乘员运输逻辑或真实弹簧仿真。'])
    for key in ids(D,'pickup'):
        items=[p('ring',D,'fx','ring',[.38,.07,.38],collision={'type':'none'}),
               p('display',D,'pickup',key,[.23,.24,.18],[0,.14,0],moving=True,collision={'type':'none'}),
               p('mount',D,'fx','emitter_cup',[.13,.08,.13],[0,.04,0],collision={'type':'none'})]
        if key in ('capsule','cartridge'):items.append(p('latch','props','fastener','clasp',[.035,.045,.025],[0,.12,.098],parent='display',optional=True))
        elif key=='crystal':items.append(p('shard',D,'pickup','crystal',[.06,.09,.055],[.11,.02,.025],parent='display',optional=True))
        elif key=='key':items.append(p('keyring','props','handle','ring_pull',[.10,.04,.1],[0,.24,0],parent='display',optional=True))
        register(D,'pickup',key,label(pid(D,'pickup',key))+'拾取展示组',items,[.42,.45,.42],mount=[.22,.22],
                 controls=[control('spin','display','展示转角',360)],collision={'type':'none'},interaction=event_contract('pickup','collect','display',trigger=True),
                 notes=['不烘焙发光，不包含粒子；游戏侧处理得分、资源奖励与拾取消失。'])
    for key in ids(D,'cover'):
        items=[p('panel',D,'cover',key,[1.20,.80,.22],[0,.12,0]),
               p('footL',D,'cover','barricade_leg',[.18,.35,.58],[-.44,0,0]),
               p('footR',D,'cover','barricade_leg',[.18,.35,.58],[.44,0,0]),
               bar('braceL',[-.46,.12,-.24],[-.46,.70,0],.065),bar('braceR',[.46,.12,-.24],[.46,.70,0],.065)]
        if key=='sandbag':items.append(p('topbag',D,'cover','sandbag',[.75,.24,.30],[0,.80,0]))
        elif key=='gabion':items.append(p('rubble','terrain','cliff','boulder' if pid('terrain','cliff','boulder') in PARTS else ids('terrain','cliff')[0],[.92,.48,.18],[0,.22,0]))
        elif key in ('viewport','bullet_slot'):items.append(plate('sill',[.8,.06,.35],[0,.40,0]))
        register(D,'cover',key,label(pid(D,'cover',key))+'部署支承组',items,[1.25,1.07,.64],mount=[.88,.48],edge=True,
                 notes=['是否可射穿与掩体导航由消费者定义；开孔网格不使用实心选择框作为碰撞。'])
    for key in ids(D,'destruction')+['reinforced_crate']:
        if key=='reinforced_crate':
            items=[p('base','props','container','crate_base',[.85,.08,.65])]
            for i,(x,z,ry) in enumerate([(-.38,0,90),(.38,0,90),(0,-.28,0),(0,.28,0)]):
                items.append(p('fragment'+str(i),'props','container','crate_side',[.72,.44,.045],[x,.08,z],[0,ry,0],moving=True))
            items.append(p('band','props','container','crate_lid',[.83,.04,.64],[0,.52,0],moving=True))
            ctr=[control('break','band','顶盖弹出',.5,axis=(0,1,0),mode='translation')]
        else:
            items=[plate('frame',[1.02,.08,.45])]
            for i,(x,y) in enumerate([(-.24,.08),(.24,.08),(-.20,.44),(.20,.44)]):
                items.append(p('fragment'+str(i),D,'destruction',key,[.47,.37,.24],[x,y,0],rot=[0,i*90,0],moving=True))
            items.append(p('connector',D,'destruction','hinge_remnant' if key!='hinge_remnant' else 'plate_fragment',[.15,.16,.09],[0,.35,.11],optional=True))
            ctr=[control('separate','fragment0','首块位移',.5,axis=(-1,0,0),mode='translation')]
        ident=register(D,'breakable',key,'加固木箱可拆结构' if key=='reinforced_crate' else label(pid(D,'destruction',key))+'可拆分结构',items,[1.05,.88,.68],controls=ctr,
                 interaction=event_contract('breakable','break','fragment0'),notes=['预制可拆片，不是闭合 Voronoi 断裂体；按片层级与命名交给物理/销毁逻辑。'])

        # Every detachable piece must survive static runtime batching, not only
        # the first piece used by the demonstration state control.
        fragments=[i['id'] for i in items if i['id'].startswith('fragment') or i['id']=='band']
        ASSEMBLIES[ident]['metadata']['runtime_fragment_nodes']=fragments
        ASSEMBLIES[ident]['metadata']['runtime']['interaction']['fragments']=fragments
