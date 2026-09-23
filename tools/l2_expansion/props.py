"""106 small functional assemblies: closures, handles, lights and instruments."""
from .common import *
D='props'

def author():
    # Closure/handling modules; lids and bails remain separate service nodes.
    wide={'basin','wok','pan','bowl','tea_bowl','cauldron','mortar','crucible','planter'}
    neck={'amphora','bottle','carboy','flask','inkwell','urn','vase','jug','churn'}
    for key in ids(D,'vessel'):
        w,h=(.54,.24) if key in wide else (.32,.52) if key in neck else (.38,.36)
        lidw=w*.34 if key in neck else w*.91
        items=[p('body',D,'vessel',key,[w,h,w]),
               p('closure',D,'merch','cork' if key in neck else 'jar_lid',[lidw,.045,lidw],[0,h-.012,0],moving=True),
               p('grip',D,'handle','knob',[lidw*.24,.045,lidw*.24],[0,.036,0],parent='closure'),
               p('tag',D,'merch','label_tag',[.07,.10,.012],[w*.34,h*.61,w*.22],rot=[0,28,-12],optional=True)]
        if key in ('bucket','kettle','cauldron','churn'):
            items.append(p('bail',D,'handle','bail',[w*.88,h*.57,.06],[0,h*.78,0],moving=True))
        elif key not in wide and key not in ('bottle','vase','carboy','goblet'):
            items.append(p('handle',D,'handle','c_loop',[.13,.20,.055],[w*.48,h*.31,0],[0,0,0]))
        register(D,'closure',key,label(pid(D,'vessel',key))+'盖柄组件',items,[w*1.25,h+.1,w],mount=[w*.65,w*.65],
                 controls=[control('open','closure','盖体抬升',.13,mode='translation')],
                 function='盛装壳、可移盖和握持件组成的小型功能模块；无容量或流体仿真。')
    long={'shovel','spade','rake','hoe','fork','pick','adze'}
    for key in ids(D,'toolhead'):
        length=.90 if key in long else .35
        headsize=[.34,.18,.13] if key in ('hammer','sledge','mallet','claw') else [.24,.35,.055]
        if key in ('drill','awl','socket'):headsize=[.07,.28,.07]
        items=[p('shaft',D,'handle','wrapped',[.055,length,.055]),
               p('head',D,'toolhead',key,headsize,[0,length-.02,0]),
               p('collar','industry','pipe','socket',[.073,.085,.073],[0,length-.07,0]),
               p('lanyard',D,'fastener','eye_bolt',[.022,.036,.022],[0,.035,.027],optional=True)]
        if key in ('shovel','spade'):items.append(p('grip',D,'handle','d_loop',[.15,.15,.045],[0,-.12,0]))
        if key in ('plier','snip'):
            items[1]['moving']=True;items[1]['collision']={'type':'convex-hull','static_only':False};items[1].pop('moving')
            items.extend([p('opposingHead',D,'toolhead',key,headsize,[0,length-.02,0],[0,180,0],moving=True),
                          p('secondHandle',D,'handle','lever',[.045,length,.045],[.08,0,0]),p('pivot',D,'fastener','clevis_pin',[.045,.045,.09],[0,length+.01,0],[90,0,0])])
        register(D,'tool',key,label(pid(D,'toolhead',key))+'握柄工具组',items,[max(.34,headsize[0]),length+.35,.16],mount=[.055,.055],
                 controls=[control('jaw','opposingHead','剪切张角',25,axis=(0,0,1))] if key in ('plier','snip') else [],
                 notes=['仅游戏美术与握持安装基准；不提供制造或机械安全规格。'])
    for key in ids(D,'lamp'):
        shade=key if key in ('conical_shade','bell_shade','dome_shade','drum_shade','diffuser','reflector','cage','lantern_frame','chimney') else 'conical_shade'
        items=[p('socket',D,'lamp','socket',[.10,.13,.10]),p('shade',D,'lamp',shade,[.40,.30,.40],[0,.08,0]),
               p('light',D,'lamp','bulb',[.11,.18,.11],[0,.12,0],material='mat.emissive.amber',collision={'type':'none'}),
               p('mountplate',D,'lamp','lamp_base',[.17,.06,.17],[0,-.06,0])]
        if key!=shade and key not in ('bulb','socket','lamp_base'):
            items.append(p('fitting',D,'lamp',key,[.20,.22,.15],[0,-.18,0]))
        elif key=='lamp_base':items.append(p('arm',D,'lamp','sconce_arm',[.12,.22,.18],[0,-.22,0]))
        elif key=='socket':items.append(p('seal',D,'merch','seal_band',[.18,.04,.18],[0,.015,0]))
        elif key=='bulb':items.append(p('guard',D,'lamp','cage',[.27,.30,.27],[0,.07,0]))
        register(D,'luminaire',key,label(pid(D,'lamp',key))+'光源承载组件',items,[.42,.60,.42],mount=[.17,.17],
                 function='灯罩、灯座和发光几何分件；真实灯光/阴影由消费项目添加。')
    for key in ids(D,'sign'):
        items=[p('face',D,'sign',key,[.72,.42,.045],[0,.27,0]),
               p('bracket',D,'sign','bracket',[.24,.16,.22],[0,.14,-.08]),
               plate('mount',[.16,.14,.045],[0,.16,-.15]),
               *fasteners('pin',[[-.27,.37,.026],[.27,.37,.026]],.023)]
        if key in ('hanging','scroll','banner','pennant'):
            items.extend([p('loop'+str(i),D,'handle','ring_pull',[.055,.075,.022],[x,.64,0]) for i,x in enumerate([-.26,.26])])
        register(D,'signmount',key,label(pid(D,'sign',key))+'悬挂安装组',items,[.74,.73,.25],mount=[.16,.045],
                 notes=['告示板与标牌不烘焙文字；文字/图标由上层应用提供。'])
    for key,name in names('syringe:注射器外观机构 vial:药瓶封装 ampoule:安瓿防护托 bandage:绷带收纳轴 splint:夹板绑带 stethoscope:听诊头接管 crutch:拐杖腋托连接 tray:器械分隔托盘'):
        ctrl=[]
        if key=='syringe':
            items=[p('barrel',D,'medical','syringe_barrel',[.12,.40,.12]),p('plunger',D,'medical','plunger',[.09,.34,.09],[0,.17,0],moving=True),p('cap',D,'medical','needle_hub',[.06,.12,.06],[0,-.11,0])]
            ctrl=[control('stroke','plunger','外观活塞行程',.12,mode='translation')];sz=[.12,.63,.12]
        elif key in ('vial','ampoule'):
            items=[p('vessel',D,'medical',key,[.16,.30,.16]),p('lid',D,'merch','bottle_cap',[.085,.04,.085],[0,.29,0]),p('label',D,'merch','label_tag',[.07,.09,.01],[0,.10,.082],optional=True)];sz=[.16,.34,.18]
        elif key=='bandage':
            items=[p('roll',D,'medical','bandage_roll',[.19,.12,.19]),p('axle','industry','pipe','socket',[.06,.18,.06]),p('tail',D,'medical','gauze',[.15,.015,.27],[.11,0,0])];sz=[.37,.18,.27]
        elif key=='splint':
            items=[p('plate',D,'medical','splint',[.22,.65,.055])]+[p('strap'+str(i),D,'handle','strap',[.26,.07,.08],[0,y,.025]) for i,y in enumerate([.16,.48])];sz=[.26,.65,.11]
        elif key=='stethoscope':
            items=[p('head',D,'medical','stethoscope',[.17,.08,.17]),p('hose',D,'handle','rope',[.045,.34,.045],[0,.07,0]),p('coupler','industry','pipe','hose_end',[.05,.09,.05],[0,.34,0])];sz=[.17,.43,.17]
        elif key=='crutch':
            items=[p('pad',D,'medical','crutch_pad',[.34,.13,.12],[0,.30,0]),post('shaftA',.30,[-.10,0,0],.035),post('shaftB',.30,[.10,0,0],.035),p('grip',D,'handle','bar_end',[.20,.045,.045],[0,.14,0],[0,0,90])];sz=[.34,.43,.12]
        else:
            items=[p('tray',D,'medical','tray',[.62,.09,.38]),p('insert',D,'container','case_foam',[.55,.04,.31],[0,.045,0]),p('separator',D,'medical','splint',[.03,.07,.31],[0,.025,0])];sz=[.62,.10,.38]
        register(D,'medical',key,name+'模块',items,sz,controls=ctrl,function='虚拟场景中可拆解的医疗外观部件，无医疗或真实操作用途。')
    office=names('book:书页装订组 binder:活页收纳组 scroll:卷轴轴芯 clipboard:写字板夹扣 pen:钢笔笔尖笔杆 pencil:铅笔橡皮连接 tape:胶带切断组 stamp:印章印台组 magnifier:放大镜握柄 scissors:文具剪刀轴组')
    for key,name in office:
        config={
          'book':('book_cover','book_block','book_spine'),'binder':('folder','paper_stack','binder_ring'),
          'scroll':('scroll_core','scroll_core','book_spine'),'clipboard':('clipboard','paper_stack','clip'),
          'pen':('pen_barrel','pen_nib','clip'),'pencil':('pencil_core','eraser','clip'),
          'tape':('tape_spool','stapler_base','ruler'),'stamp':('stamp','inkpad','clip'),
          'magnifier':('magnifier','pen_barrel','clip'),'scissors':('scissors_loop','ruler','clip')}
        a,b,c=config[key]
        if key in ('pen','pencil','magnifier'):
            items=[p('body',D,'office',a,[.12,.38,.055]),p('tip',D,'office',b,[.07,.10,.04],[0,.36,0]),p('clip',D,'office',c,[.025,.09,.016],[.052,.24,.025],optional=True)];sz=[.15,.46,.07]
        else:
            items=[p('base',D,'office',a,[.40,.09,.30]),p('insert',D,'office',b,[.35,.045,.25],[0,.08,0]),p('fitting',D,'office',c,[.09,.065,.13],[-.13,.07,0])];sz=[.4,.15,.3]
        register(D,'office',key,name,items,sz)
    for key in ids(D,'device'):
        items=[p('shell',D,'device',key,[.36,.24,.16]),plate('rear',[.30,.21,.04],[0,.015,-.085]),
               p('port','industry','power','terminal',[.085,.04,.06],[.12,.08,-.11]),
               *fasteners('screw',[[x,y,.085] for x in [-.135,.135] for y in [.04,.20]],.014)]
        if key in ('camera_shell','lens_barrel'):items.append(p('lens',D,'device','lens_barrel',[.13,.14,.13],[0,.13,.08],[90,0,0],anchor='center'))
        else:items.append(p('knob',D,'device','control_knob',[.055,.028,.055],[.11,.18,.09],[90,0,0]))
        register(D,'device',key,label(pid(D,'device',key))+'接线安装组件',items,[.38,.26,.32],mount=[.30,.16])
