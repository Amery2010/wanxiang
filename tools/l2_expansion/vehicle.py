"""51 transport subsystems, independent from complete vehicles."""
from .common import *
D='vehicle'

def wheels(prefix,x=.56,y=.29,z=0,tire='road_tire',r=.50):
    out=[]
    for i,side in enumerate([-1,1]):
        out.extend([p(prefix+'tire'+str(i),D,'wheel',tire,[r,.16,r],[side*x,y,z],[0,0,90],anchor='center',moving=True),
                    p(prefix+'hub'+str(i),D,'wheel','disc_hub',[r*.63,.19,r*.63],[0,0,0],anchor='center',parent=prefix+'tire'+str(i))])
    return out

def author():
    for key in ids(D,'chassis'):
        items=[p('structure',D,'chassis',key,[1.1,.27,1.25],[0,.29,0]),
               p('crossmember',D,'chassis','subframe',[1.15,.13,.34],[0,.38,0]),
               p('bushL','robot','joint','revolute',[.12,.10,.12],[-.46,.53,0]),
               p('bushR','robot','joint','revolute',[.12,.10,.12],[.46,.53,0]),
               *fasteners('mount',[[x,.57,z] for x in [-.4,.4] for z in [-.42,.42]],.045)]
        if key in ('axle','knuckle','wishbone','trailing','leafspring','strut'):
            items.extend(wheels('road',.61,.31,0));ctrl=[control('roll','roadtire0','车轮转角',360,axis=(0,1,0),nodes=['roadtire0','roadtire1'])]
        elif key=='track_frame':
            items.extend([p('wheel'+str(i),D,'wheel','idler',[.30,.12,.30],[0,.26,z],[90,0,0],anchor='center') for i,z in enumerate([-.43,0,.43])]);ctrl=[]
        else:ctrl=[]
        register(D,'runninggear',key,label(pid(D,'chassis',key))+'悬挂承载组',items,[1.42,.65,1.4],controls=ctrl,mount=[.8,.84],
                 function='底架或悬挂功能节；不包含车身、动力与车辆控制器。')
    for key in ids(D,'wheel'):
        if key in ('road_tire','solid_tire','allterrain_tire','tractor_tire'):
            items=[p('wheel',D,'wheel',key,[.60,.22,.60],moving=True),p('hub',D,'wheel','spoke_hub' if key=='tractor_tire' else 'disc_hub',[.37,.25,.37],[0,.10,0],anchor='center',parent='wheel'),
                   p('axle','industry','drive','keyshaft',[.085,.35,.085],[0,.11,0]),*fasteners('stud',[[.11,.26,0],[-.11,.26,0],[0,.26,.11],[0,.26,-.11]],.032)]
        elif key=='track_shoe':
            items=[p('shoe',D,'wheel',key,[.60,.13,.32]),p('hingeA','industry','conveyor','chain_link',[.42,.12,.10],[0,.04,-.17]),p('hingeB','industry','conveyor','chain_link',[.42,.12,.10],[0,.04,.17]),p('pad','gameplay','cover','shield_plate',[.48,.03,.24],[0,.12,0])]
        elif key=='caster_fork':
            items=[p('fork',D,'wheel',key,[.28,.33,.24]),p('tire',D,'wheel','solid_tire',[.24,.10,.24],[0,.14,0],[90,0,0],anchor='center',moving=True),p('bearing','industry','drive','bearing',[.16,.13,.12],[0,.29,0])]
        else:
            items=[p('rim',D,'wheel',key,[.46,.16,.46]),p('tire',D,'wheel','road_tire',[.60,.18,.60]),p('bearing','industry','drive','bearing',[.17,.16,.12],[0,.11,0],[90,0,0])]
        register(D,'wheelhub',key,label(pid(D,'wheel',key))+'轮系组件',items,[.62,.48,.62],mount=[.085,.085],
                 controls=[control('spin','wheel','滚动',360,axis=(0,1,0))] if items[0]['id']=='wheel' else [])
    for key in ids(D,'aero'):
        if key in ('rotor_blade','prop_blade'):
            items=[p('hub','industry','drive','coupling',[.18,.13,.18])]
            for i in range(3):items.append(p('blade'+str(i),D,'aero',key,[.15,.07,.80],[0,.1,0],[0,120*i,0],anchor='back'))
            items.append(p('shaft','industry','drive','keyshaft',[.06,.30,.06],[0,-.24,0]));sz=[1.7,.44,1.7];ctrl=[]
        elif key in ('nacelle','inlet'):
            items=[p('casing',D,'aero','nacelle',[.46,.42,1.0]),p('lip',D,'aero','inlet',[.42,.38,.12],[0,.02,.48]),
                   p('mount',D,'attachment','rack_foot',[.16,.20,.24],[0,.37,0]),p('fan','industry','process','impeller',[.28,.06,.28],[0,.20,.39],[90,0,0],anchor='center',optional=True)];sz=[.46,.57,1.13];ctrl=[]
        elif key in ('flap','aileron'):
            items=[p('control',D,'aero',key,[.86,.055,.24],[0,.12,0],anchor='back',moving=True),
                   bar('hingeBeam',[-.46,.095,0],[.46,.095,0],.05),
                   p('hingeL','interior','fixture','hinge_leaf',[.055,.07,.11],[-.30,.07,0]),p('hingeR','interior','fixture','hinge_leaf',[.055,.07,.11],[.30,.07,0]),
                   p('horn',D,'attachment','rack_foot',[.05,.12,.07],[0,.13,.08],parent='control')]
            ctrl=[control('deflect','control','独立操纵面偏角',30,-20,axis=(1,0,0))];sz=[.94,.34,.32]
        else:
            wing=key if key in ('wing','swept_wing','delta','fin') else 'wing'
            items=[p('structure',D,'aero',wing,[1.3,.12,.60]),p('control',D,'aero','flap' if key in ('wing','flap','delta') else 'aileron',[.70,.035,.16],[.22,.055,.27],anchor='back',moving=True),
                   p('hingeL','interior','fixture','hinge_leaf',[.035,.028,.06],[-.02,.035,.24]),p('hingeR','interior','fixture','hinge_leaf',[.035,.028,.06],[.46,.035,.24])]
            ctrl=[control('deflect','control','操纵面偏角',25,minimum=-15,axis=(1,0,0))];sz=[1.3,.18,.76]
        if key=='inlet':
            items=[p('lip',D,'aero','inlet',[.46,.42,.12],[0,.05,0]),
                   p('fan','industry','process','impeller',[.30,.07,.30],[0,.26,-.04],[90,0,0],anchor='center',moving=True),
                   p('ring','robot','joint','wrist',[.38,.08,.38],[0,.26,-.09],[90,0,0],anchor='center',collision={'type':'none'}),
                   bar('support',[-.24,.05,-.06],[.24,.05,-.06],.05)]
            sz=[.52,.50,.22];ctrl=[control('fan','fan','风扇相位',360)]
        register(D,'flightmodule',key,label(pid(D,'aero',key))+'翼面机匣组',items,sz,controls=ctrl,mount=[.16,.24],
                 notes=['机构演示无空气动力学或推进仿真；不构成飞行器制造设计。'])
    for key in ids(D,'rail'):
        if key in ('wheel_flange','axlebox','bolster','brake_shoe'):
            items=[p('beam',D,'rail','bolster',[1.55,.16,.34],[0,.35,0]),p('axle','industry','drive','keyshaft',[.10,1.7,.10],[0,.30,0],[0,0,90],anchor='center')]
            for i,sg in enumerate([-1,1]):
                items.append(p('wheel'+str(i),D,'rail','wheel_flange',[.58,.11,.58],[sg*.7175,.30,0],[0,0,90],anchor='center',moving=True))
                items.append(p('box'+str(i),D,'rail',key if key!='wheel_flange' else 'axlebox',[.20,.19,.20],[sg*.84,.26,0]))
            sz=[1.9,.61,.58]
        elif key=='pantograph_arm':
            items=[p('armA',D,'rail',key,[.12,.75,.08],[-.24,.12,0],[0,0,-35]),p('armB',D,'rail',key,[.12,.75,.08],[.24,.12,0],[0,0,35]),
                   bar('contact',[-.42,.80,0],[.42,.80,0],.06),p('insulator','industry','power','insulator',[.12,.17,.12])];sz=[.9,.86,.20]
        elif key in ('buffer','coupler'):
            items=[p('head',D,'rail',key,[.30,.25,.42],[0,.10,.23],moving=True),p('shank',D,'chassis','strut',[.12,.12,.50],[0,.12,-.05]),plate('mount',[.42,.34,.075],[0,0,-.34])];sz=[.42,.34,.8]
        else:
            items=[p('clipA',D,'rail','rail_clip',[.13,.10,.15],[-.12,.08,0]),p('clipB',D,'rail','rail_clip',[.13,.10,.15],[.12,.08,0],[0,180,0]),plate('sleeper',[.55,.10,.25]),bar('rail',[0,.19,-.23],[0,.19,.23],.14,section='rail')];sz=[.55,.28,.46]
        if key=='axlebox':
            items=[p('box',D,'rail','axlebox',[.28,.28,.26],[0,.09,0]),
                   p('bearing','industry','drive','bearing',[.22,.19,.16],[0,.16,.05]),
                   p('spring',D,'chassis','strut',[.10,.26,.10],[0,.35,0]),
                   plate('mount',[.44,.09,.38]),*fasteners('stud',[[-.16,.08,-.12],[.16,.08,.12]],.035)]
            sz=[.44,.63,.38]
        register(D,'railunit',key,label(pid(D,'rail',key))+'铁路连接组',items,sz,mount=[.30,.25],
                 controls=[control('compression','head','缓冲行程',.1,axis=(0,0,-1),mode='translation')] if key in ('buffer','coupler') else [])
    for key in ['keel','rib','transom','bow','propeller','rudder','cleat']:
        if key in ('keel','rib','transom','bow'):
            items=[p('structure',D,'marine',key,[1.0,.55,.65]),p('keel',D,'marine','keel',[.09,.16,1.1],[0,-.11,0]),
                   p('seat','architecture','joinery','saddle',[.18,.12,.21],[0,.16,0]),*fasteners('rivet',[[x,.18,.26] for x in [-.36,0,.36]],.025,'rivet')];sz=[1,.71,1.1]
        elif key=='propeller':
            items=[p('boss','industry','drive','coupling',[.15,.18,.15],moving=True)]
            items.extend([p('blade'+str(i),D,'marine','propeller',[.13,.08,.36],[0,.1,0],[0,120*i,0],anchor='back',parent='boss') for i in range(3)])
            items.append(p('shaft','industry','drive','keyshaft',[.065,.55,.065],[0,-.45,0]));sz=[.85,.74,.85]
        elif key=='rudder':
            items=[p('blade',D,'marine','rudder',[.42,.55,.055],moving=True),p('stock','industry','drive','keyshaft',[.055,.38,.055],[0,.46,0]),p('tiller',D,'marine','cleat',[.36,.07,.07],[0,.76,0])];sz=[.42,.84,.12]
        else:
            items=[p('cleat',D,'marine','cleat',[.38,.18,.16]),p('fairlead',D,'marine','fairlead',[.38,.20,.16],[0,.05,.28]),plate('deck',[.62,.08,.60],[0,-.08,.1])];sz=[.62,.33,.60]
        ctrl=[control('rudder','blade','舵角',35,minimum=-35)] if key=='rudder' else [control('spin','boss','桨轴转动',360)] if key=='propeller' else []
        register(D,'marineunit',key,label(pid(D,'marine',key))+'船用功能组',items,sz,controls=ctrl,mount=[.18,.21])
    for key in ids(D,'attachment'):
        items=[p('attachment',D,'attachment',key,[.44,.30,.20],[0,.05,0],moving=key in ('wiper','mirror_arm')),
               plate('base',[.26,.08,.18]),p('adapter','architecture','joinery','clevis',[.12,.13,.15],[0,.035,-.06]),
               *fasteners('bolt',[[-.09,.08,.06],[.09,.08,.06]],.025)]
        register(D,'accessory',key,label(pid(D,'attachment',key))+'安装接头组',items,[.46,.38,.26],mount=[.26,.18],
                 controls=[control('sweep','attachment','摆动角',65,minimum=-20,axis=(0,0,1))] if key=='wiper' else [])
