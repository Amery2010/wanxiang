"""33 anatomical appendage assemblies. Static/rigid, no fictitious skinning."""
from .common import *
D='creature'
NO={'type':'none'}

def soft(node,size,at=(0,0,0),**kw):
    return p(node,D,'foot','paw',size,at,**kw)

def author():
    for key in ids(D,'horn'):
        items=[p('horn',D,'horn',key,[.28,.50,.24],[0,.08,0]),
               soft('root_mass',[.22,.14,.20]),p('basefold',D,'ear','ungulate',[.12,.08,.17],[.05,.06,-.035],optional=True)]
        if key=='frill':items.append(p('edge',D,'horn','rhino',[.09,.14,.08],[0,.52,0],rot=[0,0,0],optional=True))
        register(D,'hornroot',key,label(pid(D,'horn',key))+'角根安装组',items,[.34,.66,.29],mount=[.2,.18],collision=NO,
                 notes=['单侧附属器官；角根软组织作为过渡片，消费者负责和头骨融合。'])
    for key in ids(D,'mouth'):
        items=[p('upper',D,'mouth',key,[.22,.24,.32],[0,.12,0]),
               p('lower',D,'mouth','beak_filter' if key=='beak_hook' else ('beak_hook' if key=='beak_filter' else key),[.20,.10,.28],[0,.12,-.08],anchor='back',moving=True,collision=NO),
               soft('hingeroot',[.23,.16,.18],[0,.075,-.13])]
        register(D,'jaw',key,label(pid(D,'mouth',key))+'口器关节组',items,[.3,.4,.5],controls=[control('gape','lower','下颚开合',42,axis=(1,0,0))],mount=[.18,.16],collision=NO,
                 notes=['局部颚部刚体摆动，无牙齿咬合或软组织变形认证。'])
    for key in ids(D,'foot'):
        items=[p('foot',D,'foot',key,[.28,.15,.34]),soft('ankle',[.17,.22,.16],[0,.10,-.075]),
               p('skin',D,'ear','feline',[.18,.055,.10],[0,.15,.03],optional=True)]
        if key in ('talon','paw'):
            for i,x in enumerate([-.075,0,.075]):items.append(p('claw'+str(i),D,'mouth','tusk',[.035,.065,.08],[x,.018,.18],[65,0,0],optional=True))
        elif key=='cloven':items.append(p('dewclaw',D,'horn','rhino',[.06,.055,.06],[0,.11,-.16],optional=True))
        else:items.append(p('webedge',D,'wing','fin_ray',[.24,.04,.10],[0,.065,.12],optional=True))
        register(D,'anklefoot',key,label(pid(D,'foot',key))+'踝足组合',items,[.32,.36,.43],mount=[.15,.14],collision=NO)
    for key in ids(D,'wing'):
        if key=='primary_feather':
            items=[soft('root_mass',[.12,.15,.12])]
            for i in range(7):items.append(p('feather'+str(i),D,'wing',key,[.075,.48-i*.02,.03],[(i-3)*.048,.1,0],[0,0,(i-3)*-9]))
        elif key=='bat_membrane':
            items=[p('membrane',D,'wing',key,[.64,.30,.045],[.25,.08,0]),soft('wrist',[.11,.13,.12]),
                   p('spar',D,'horn','ibex',[.065,.48,.045],[0,.07,0],[0,0,-60])]
        elif key=='fin_ray':
            items=[p('fin',D,'wing',key,[.48,.30,.055],[0,.08,0]),soft('root_mass',[.36,.09,.08])]
            items.extend(p('ray'+str(i),D,'horn','rhino',[.015,.23,.02],[(i-2)*.07,.085,0],optional=True) for i in range(5))
        else:
            items=[p('shell',D,'wing',key,[.22,.46,.07],[0,.09,0]),p('underwing',D,'wing','bat_membrane',[.30,.40,.02],[.05,.08,-.028]),soft('hinge',[.12,.1,.09])]
        register(D,'wingroot',key,label(pid(D,'wing',key))+'翼根组合',items,[.75,.65,.15],mount=[.1,.1],collision=NO,notes=['翼根安装框，不是自动绑定翅膀；羽片与膜的运动需由下游骨架驱动。'])
    for key in ids(D,'ear'):
        items=[p('outer',D,'ear',key,[.16,.28,.07],[0,.075,0],moving=True,collision=NO),
               p('inner',D,'ear','feline' if key!='feline' else 'canine',[.10,.21,.022],[0,.022,.025],parent='outer'),
               soft('base',[.18,.1,.10])]
        register(D,'earroot',key,label(pid(D,'ear',key))+'耳根组合',items,[.2,.4,.14],controls=[control('twitch','outer','耳廓转动',25,-25,axis=(0,0,1))],mount=[.14,.09],collision=NO)
    # Eleven more distinct functional structures, not mirrored pairs.
    specials=[('antler_crown','鹿角冠枝', 'horn','antler'),('ceratopsian','角盾头饰组','horn','frill'),
      ('ram_crown','盘角颞侧组','horn','ram'),('tusk_socket','獠牙齿槽组','mouth','tusk'),
      ('raptor_grip','抓握趾爪组','foot','talon'),('web_paddle','蹼足划水组','foot','webbed'),
      ('tail_fan','尾羽展开组','wing','primary_feather'),('gill_fan','鳃鳍展开组','wing','fin_ray'),
      ('insect_collar','鞘翅胸环组','wing','insect_elytron'),('nose_horn','双鼻角根组','horn','rhino'),
      ('jaw_pincers','节肢成对口器组','mouth','mandible')]
    for key,title,group,src in specials:
        if key in ('antler_crown','ram_crown'):
            items=[soft('crown',[.36,.12,.22])]
            for i,x in enumerate([-.14,.14]):items.append(p('horn'+str(i),D,group,src,[.23,.43,.22],[x,.085,0],[0,i*180,(-1 if i else 1)*12]))
        elif key=='ceratopsian':
            items=[p('shield',D,'horn','frill',[.48,.40,.08],[0,.08,-.08]),soft('root_mass',[.26,.15,.28])]
            items.extend(p('horn'+str(i),D,'horn','rhino',[.10,.22,.10],[x,.22,.06],[-45,0,0]) for i,x in enumerate([-.1,.1]))
        elif key in ('tusk_socket','nose_horn'):
            items=[soft('socket',[.32,.14,.35])]
            for i,z in enumerate([-.08,.09]):items.append(p('horn'+str(i),D,group,src,[.11,.30-i*.10,.13],[0,.09,z]))
        elif key in ('raptor_grip','web_paddle'):
            items=[soft('ankle',[.14,.25,.14],[0,.18,0]),p('foot',D,group,src,[.32,.14,.38])]
            if key=='raptor_grip':items.extend(p('toe'+str(i),D,'mouth','tusk',[.04,.1,.15],[x,.045,.16],[55,0,0]) for i,x in enumerate([-.09,0,.09]))
            else:items.extend(p('ray'+str(i),D,'wing','fin_ray',[.09,.05,.24],[x,.08,.02]) for i,x in enumerate([-.10,.10]))
        elif key in ('tail_fan','gill_fan'):
            items=[soft('root_mass',[.20,.10,.12])]
            for i in range(9 if key=='tail_fan' else 5):
                count=9 if key=='tail_fan' else 5;j=i-(count-1)/2
                items.append(p('blade'+str(i),D,group,src,[.085,.45,.025],[j*.032,.075,0],[0,0,-j*12]))
        elif key=='insect_collar':
            items=[soft('thorax',[.26,.18,.20]),p('left',D,group,src,[.15,.45,.075],[-.075,.12,0],[0,0,30]),
                   p('right',D,group,src,[.15,.45,.075],[.075,.12,0],[0,180,-30]),p('membrane',D,'wing','bat_membrane',[.4,.3,.018],[0,.14,-.028])]
        else:
            items=[soft('socket',[.28,.14,.18]),p('jawL',D,group,src,[.13,.28,.12],[-.10,.08,0],[0,0,18],moving=True,collision=NO),
                   p('jawR',D,group,src,[.13,.28,.12],[.10,.08,0],[0,180,-18],moving=True,collision=NO)]
        controls=[control('left','jawL','左口器',45,axis=(0,0,1)),control('right','jawR','右口器',0,-45,axis=(0,0,1))] if key=='jaw_pincers' else []
        register(D,'specialized',key,title,items,[.8,.7,.6],controls=controls,mount=[.22,.18],collision=NO,
                 notes=['复用现有角、爪、膜和软组织几何；不是解剖精度模型，需与目标生物比例匹配。'])
