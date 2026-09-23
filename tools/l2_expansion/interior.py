"""82 furniture/cabinet submodules, not furnished-room or full asset duplicates."""
from .common import *
D='interior'

def author():
    # Work surfaces with purpose-specific mounting, not freestanding complete tables.
    for key in ids(D,'tabletop'):
        items=[p('top',D,'tabletop',key,[1.2,.075,.70],[0,.13,0]),
               bar('railA',[-.44,.08,-.21],[.44,.08,-.21],.06),bar('railB',[-.44,.08,.21],[.44,.08,.21],.06),
               p('bracketL',D,'shelf','cantilever',[.10,.18,.32],[-.39,-.06,0]),
               p('bracketR',D,'shelf','cantilever',[.10,.18,.32],[.39,-.06,0]),
               *fasteners('screw',[[x,.09,z] for x in [-.39,.39] for z in [-.21,.21]],.028,'wood_screw')]
        ctrl=[]
        if key=='drop_leaf':
            items[0]['moving']=True;items[0]['collision']={'type':'convex-hull','static_only':False}
            ctrl=[control('fold','top','折叶角',70,axis=(1,0,0))]
            items[0].pop('moving')
        register(D,'worksurface',key,label(pid(D,'tabletop',key))+'承托模块',items,[1.2,.205,.7],controls=ctrl,mount=[.78,.42])
    seat_back={'scoop':'back_shell','bucket':'back_shell','slatted':'back_ladder','tractor':'back_spindle',
               'saddle':'back_shell','mesh_pan':'back_spindle','upholstered':'back_shell','kneeling':'back_shell'}
    for key in ids(D,'seat'):
        main=key if key in seat_back else 'upholstered'
        back=seat_back.get(key,key if key.startswith('back') else 'back_shell')
        items=[p('seat',D,'seat',main,[.56,.12,.51],[0,.08,0]),
               p('back',D,'seat',back,[.54,.57,.10],[0,.19,-.225],moving=True),
               plate('mount',[.24,.08,.22]),
               *fasteners('fix',[[-.085,.08,0],[.085,.08,0]],.035)]
        if key.startswith('back'):
            items=[p('back',D,'seat',key,[.54,.57,.10],[0,.12,0],moving=True),plate('mount',[.24,.08,.15]),
                   p('hingeL',D,'fixture','hinge_leaf',[.075,.08,.055],[-.16,.08,0]),p('hingeR',D,'fixture','hinge_leaf',[.075,.08,.055],[.16,.08,0]),
                   bar('brace',[-.21,.11,-.05],[.21,.11,-.05],.06)]
        if key.startswith('arm'):
            items.extend([p('armL',D,'seat',key,[.09,.26,.44],[-.30,.18,0]),p('armR',D,'seat',key,[.09,.26,.44],[.30,.18,0])])
        if key=='kneeling':items.append(p('kneepad',D,'seat','kneeling',[.46,.10,.24],[0,-.22,.34]))
        register(D,'seatpack',key,label(pid(D,'seat',key))+'座背组件',items,[.69,.80,.68],mount=[.24,.22],
                 controls=[control('recline','back','靠背角',24,minimum=-5,axis=(1,0,0))],function='座面、靠背与安装盘；不包含桌椅底座。')
    for key in ids(D,'case'):
        items=[p('carcase',D,'case',key,[.90,1.0,.50]),
               p('runnerL',D,'fixture','runner',[.028,.045,.41],[-.37,.34,.025]),
               p('runnerR',D,'fixture','runner',[.028,.045,.41],[.37,.34,.025]),
               p('tray',D,'drawer','tray',[.70,.12,.39],[0,.38,.035],moving=True),
               p('handle', 'props','handle','u_pull',[.18,.05,.055],[0,.06,.22],parent='tray'),
               *fasteners('hingeFix',[[x,.90,.24] for x in [-.36,.36]],.03)]
        register(D,'carcase',key,label(pid(D,'case',key))+'抽拉柜芯',items,[.90,1.0,.50],mount=[.82,.42],
                 controls=[control('pull','tray','抽拉行程',.30,axis=(0,0,1),mode='translation')],
                 notes=['抽拉托盘属于柜芯；柜门、外饰面及整套家具由 L3 配置。'])
    for key in ids(D,'drawer'):
        items=[p('runnerL',D,'fixture','runner',[.025,.045,.42],[-.345,.08,0]),
               p('runnerR',D,'fixture','runner',[.025,.045,.42],[.345,.08,0]),
               p('drawer',D,'drawer',key,[.65,.18,.40],[0,.07,0],moving=True),
               p('handle','props','handle','u_pull',[.18,.045,.05],[0,.095,.22],parent='drawer'),
               plate('bridge',[.74,.05,.08],[0,.02,-.18]),*fasteners('fix',[[-.345,.08,-.14],[.345,.08,-.14]],.023)]
        if key in ('curved_front','inset_pull','finger_pull'):
            items.append(p('box',D,'drawer','box',[.62,.16,.37],[0,0,-.035],parent='drawer'))
            items[2]['scale']=[div(v,e) for v,e in zip([.65,.18,.035],natural_size(pid(D,'drawer',key)))];items[2]['position']=[0,.07,.20]
        elif key=='tambour':
            items[2]['rotation']=[0,0,90]
            items.append(p('channel',D,'fixture','conduit',[.70,.045,.04],[0,.3,0]))
        elif key in ('file','cutlery','divided'):items.append(p('label','props','merch','label_tag',[.09,.04,.015],[0,.13,.21],parent='drawer',optional=True))
        register(D,'drawercartridge',key,label(pid(D,'drawer',key))+'导轨抽拉模块',items,[.76,.40,.52],mount=[.69,.32],
                 controls=[control('pull','drawer','抽出行程',.30,axis=(0,0,1),mode='translation')],
                 notes=['独立抽屉与导轨，不包含外柜壳；卷片门当前为整体刚性演示，不含逐片卷曲。'])
    for key in ids(D,'bed'):
        if key in ('slat','rail','cleat'):
            items=[bar('railA',[-.44,0,-.65],[-.44,0,.65],.07,section='c'),bar('railB',[.44,0,-.65],[.44,0,.65],.07,section='c')]
            items.extend([p('slat'+str(i),D,'bed','slat',[.92,.045,.09],[0,.015,-.54+i*.18]) for i in range(7)])
            items.append(p('connector',D,'bed',key,[.20,.08,.18],[.40,-.055,.59]))
            sz=[.98,.14,1.3]
        else:
            items=[p('panel',D,'bed',key,[.94,.66,.12],[0,.10,0]),post('sideL',.86,[-.49,0,0],.07),post('sideR',.86,[.49,0,0],.07),
                   p('bracketL',D,'bed','cleat',[.12,.12,.12],[-.39,.05,.08]),p('bracketR',D,'bed','cleat',[.12,.12,.12],[.39,.05,.08])]
            sz=[1.05,.86,.20]
        register(D,'bedmodule',key,label(pid(D,'bed',key))+'锁接床架模块',items,sz,mount=[.88,.12])
    for key in ids(D,'shelf'):
        items=[p('deck',D,'shelf',key,[1.0,.16,.36],[0,.08,0]),
               p('bracketL',D,'shelf','cantilever',[.06,.24,.32],[-.38,-.16,0]),p('bracketR',D,'shelf','cantilever',[.06,.24,.32],[.38,-.16,0]),
               p('backrail',D,'fixture','conduit',[.88,.07,.06],[0,.07,-.18]),
               *fasteners('mountFix',[[-.38,.04,-.16],[.38,.04,-.16]],.028)]
        register(D,'shelfbay',key,label(pid(D,'shelf',key))+'挂装层架',items,[1,.40,.42],mount=[.76,.07])
    for key in ids(D,'bath'):
        if key in ('basin','pedestal'):
            items=[p('basin',D,'bath','basin',[.64,.22,.46],[0,.16,0]),p('support',D,'bath','pedestal',[.18,.16,.18]),
                   p('tapDeck',D,'kitchen','backsplash',[.28,.035,.085],[0,.352,-.20]),
                   p('tap',D,'kitchen','faucet_spout',[.055,.25,.20],[0,.38,-.205],pivot=[0,0,0])];sz=[.7,.63,.50]
            if key=='basin':items[1]=p('support',D,'shelf','cantilever',[.42,.18,.35],[0,.02,-.04])
        elif key in ('shower_tray','drain_grate','bathtub_rim'):
            items=[p('tray',D,'bath',key,[.92,.12,.84]),p('drain',D,'bath','drain_grate',[.10,.022,.10],[.26,.115,.20]),
                   p('seal',D,'kitchen','backsplash',[.92,.075,.045],[0,.12,-.41])];sz=[.92,.195,.84]
        elif key=='shower_head':
            items=[p('spray',D,'bath',key,[.26,.06,.26],[0,.65,.16],rot=[25,0,0],moving=True),
                   bar('pipe',[0,0,0],[0,.70,0],.04,section='bulb'),bar('neck',[0,.70,0],[0,.70,.16],.04,section='bulb'),p('wallplate',D,'fixture','switch_plate',[.14,.14,.035],[0,.3,0])];sz=[.26,.75,.30]
        elif key=='towel_rail':
            items=[p('rail',D,'bath',key,[.72,.10,.11],[0,.18,0]),p('left',D,'fixture','hook',[.07,.13,.09],[-.30,.07,-.04]),
                   p('right',D,'fixture','hook',[.07,.13,.09],[.30,.07,-.04])];sz=[.72,.28,.15]
        else:
            items=[p('seat',D,'bath',key,[.4,.06,.5],[0,.04,0],moving=True),p('hingeL',D,'fixture','hinge_leaf',[.04,.05,.06],[-.1,0,-.2]),p('hingeR',D,'fixture','hinge_leaf',[.04,.05,.06],[.1,0,-.2])];sz=[.4,.12,.5]
        register(D,'wetfixture',key,label(pid(D,'bath',key))+'安装组件',items,sz,mount=[.16,.10])
    for key,name in names('switch:墙壁开关组 outlet:插座接线组 hood:排风滤芯组 sink:水槽台面开口组 hob:灶台承托组 curtain:窗帘轨道组'):
        if key in ('switch','outlet'):
            part='switch_plate' if key=='switch' else 'outlet_plate'
            items=[p('face',D,'fixture',part,[.16,.16,.04],[0,.06,.025]),plate('rear',[.14,.14,.04],[0,.07,-.02]),
                   p('conduit',D,'fixture','conduit',[.05,.23,.04],[0,.2,-.02])];sz=[.16,.43,.09]
        elif key=='hood':
            items=[p('filter',D,'kitchen','hood_filter',[.70,.09,.46]),p('frame',D,'case','open_front',[.78,.28,.50],[0,.05,0]),p('grill',D,'fixture','vent',[.38,.14,.035],[0,.18,.26])];sz=[.78,.33,.54]
        elif key=='sink':
            items=[p('rim',D,'kitchen','worktop_cutout',[.80,.06,.60],[0,.27,0]),p('bowl',D,'kitchen','sink_bowl',[.62,.27,.43]),p('tap',D,'kitchen','faucet_spout',[.055,.27,.17],[.28,.32,-.24],pivot=[0,0,0])];sz=[.8,.59,.60]
        elif key=='hob':
            items=[plate('base',[.78,.06,.52])]+[p('ring'+str(i),D,'kitchen','hob_ring',[.20,.065,.20],[x,.06,z]) for i,(x,z) in enumerate([(-.21,-.12),(.21,-.12),(-.21,.12),(.21,.12)])]+[p('grate',D,'kitchen','cooker_grate',[.67,.055,.42],[0,.11,0])];sz=[.78,.165,.52]
        else:
            items=[bar('track',[-.8,.8,0],[.8,.8,0],.045,section='c'),p('drape',D,'soft','curtain_fold',[.70,.76,.08],[-.43,0,0],moving=True),
                   p('valance',D,'soft','valance',[1.6,.18,.12],[0,.68,0])];sz=[1.6,.86,.12]
        ctrl=[control('slide','drape','开帘行程',.62,axis=(1,0,0),mode='translation')] if key=='curtain' else []
        register(D,'service',key,name,items,sz,controls=ctrl)
