"""45 industrial service modules. Geometry is illustrative, not manufacturing CAD."""
from .common import *
D='industry'

def author():
    for key in ids(D,'pipe'):
        items=[p('flow',D,'pipe',key,[.32,.70,.32],[0,.14,0]),
               p('saddle',D,'structure','saddle',[.42,.18,.32]),
               p('clamp',D,'structure','clamp',[.35,.14,.35],[0,.18,0]),
               *fasteners('footFix',[[-.16,.03,0],[.16,.03,0]],.04)]
        if key not in ('elbow90','elbow45','return','cap','nozzle'):
            items.append(p('collar',D,'pipe','flanged',[.30,.12,.30],[0,.76,0]))
        if key in ('tee','cross'):
            items.append(p('handwheel','gameplay','trigger','wheel',[.26,.06,.26],[.26,.66,0]))
        register(D,'flowjoint',key,label(pid(D,'pipe',key))+'支承接口组',items,[.52,.92,.42],mount=[.42,.32],
                 notes=['安装基准不等同于压力管路认证。三通/四通保留组合管壁，未做内部布尔清除。'])
    for key in ids(D,'drive'):
        items=[p('bearingA',D,'drive','bearing',.8,[0,.30,-.36],pivot=[0,.25,0]),
               p('bearingB',D,'drive','bearing',.8,[0,.30,.36],pivot=[0,.25,0]),
               p('shaft',D,'drive','keyshaft',[.075,.98,.075],[0,.30,0],[90,0,0],pivot=[0,.375,0],moving=True),
               p('transmission',D,'drive',key,[.48,.13,.48],[0,0,0],anchor='center',parent='shaft'),
               plate('base',[.65,.10,1.0]),*fasteners('basebolt',[[x,.1,z] for x in [-.24,.24] for z in [-.35,.35]],.045)]
        if key=='rack':
            items[3]=p('transmission',D,'drive','rack',[.72,.09,.12],[0,.12,.08],moving=True)
            items.append(p('pinion',D,'drive','spur',[.20,.07,.20],[0,0,0],anchor='center',parent='shaft'))
        register(D,'driveunit',key,label(pid(D,'drive',key))+'支承传动组',items,[.65,.60,1.0],mount=[.48,.70],
                 controls=([control('slide','transmission','齿条滑移',.25,axis=(1,0,0),mode='translation')] if key=='rack' else [])+[control('rotate','shaft','输入轴旋转',360,axis=(0,1,0))],
                 function='轴、支座和传动件的可维护单元；不计算齿面啮合/强度，不宣称正确传动比。')
    for key in ids(D,'process'):
        if key in ('impeller','agitator'):
            items=[plate('mount',[.38,.09,.38]),p('bearing',D,'drive','bearing',[.22,.24,.14],[0,.09,0]),
                   p('shaft',D,'drive','keyshaft',[.06,.64,.06],[0,.2,0],moving=True),p('work',D,'process',key,[.5,.16,.5],[0,.46,0],parent='shaft'),
                   p('collar',D,'drive','coupling',[.14,.10,.14],[0,.2,0])];sz=[.52,.90,.52];ctrl=[control('spin','shaft','转子旋转',360)]
        elif key in ('filter','separator','hopper'):
            items=[p('process',D,'process',key,[.70,.9,.70],[0,.12,0]),p('outlet',D,'pipe','flanged',[.21,.16,.21]),
                   p('supportA',D,'structure','foot',[.16,.25,.16],[-.32,0,0]),p('supportB',D,'structure','foot',[.16,.25,.16],[.32,0,0]),
                   p('service','props','handle','u_pull',[.20,.055,.055],[0,.64,.36])];sz=[.86,1.02,.76];ctrl=[]
        else:
            items=[p('core',D,'process',key,[.66,.70,.34],[0,.1,0]),plate('frame',[.78,.10,.46]),p('inlet',D,'pipe','flanged',[.14,.18,.14],[-.25,.64,0]),
                   p('outlet',D,'pipe','flanged',[.14,.18,.14],[.25,.64,0]),*fasteners('bolt',[[-.29,.08,.16],[.29,.08,.16]],.04)];sz=[.78,.84,.46];ctrl=[]
        register(D,'processcore',key,label(pid(D,'process',key))+'检修模块',items,sz,controls=ctrl,mount=[sz[0]*.75,sz[2]*.75])
    for key in ['insulator','busbar','terminal','coil','fuse','breaker','fan_guard']:
        items=[plate('rail',[.66,.08,.24]),p('unit',D,'power',key,[.34,.38,.19],[0,.08,0],moving=key=='breaker'),
               p('terminalA',D,'power','terminal',[.16,.07,.12],[-.24,.08,0]),p('terminalB',D,'power','terminal',[.16,.07,.12],[.24,.08,0]),
               *fasteners('fix',[[-.28,.03,.10],[.28,.03,.10]],.025)]
        register(D,'electric',key,label(pid(D,'power',key))+'导轨接线组',items,[.70,.46,.24],mount=[.58,.16],
                 controls=[control('toggle','unit','拨杆角',35,axis=(1,0,0))] if key=='breaker' else [],
                 notes=['纯外观接线结构，无带电模拟，无电气额定值。'])
    for key,name in names('roller:滚筒输送托段 trough:槽形输送托段 cleated:挡边皮带托段 chute:导料张紧段'):
        items=[bar('railL',[-.42,.3,-.62],[-.42,.3,.62],.09,section='c'),bar('railR',[.42,.3,-.62],[.42,.3,.62],.09,section='c')]
        for i,z in enumerate([-.48,-.24,0,.24,.48]):
            src={'roller':'roller','trough':'trough_roller','cleated':'belt_cleat','chute':'roller'}[key]
            items.append(p('carrier'+str(i),D,'conveyor',src,[.78,.14,.16],[0,.31,z]))
        for j,(x,z) in enumerate([(-.36,-.5),(.36,-.5),(-.36,.5),(.36,.5)]):
            items.extend([post('leg'+str(j),.31,[x,0,z],.055),p('foot'+str(j),D,'structure','foot',[.13,.07,.13],[x,0,z])])
        items.append(p('tension',D,'conveyor','tensioner',[.30,.12,.18],[0,.24,-.67]))
        if key=='chute':items.append(p('chute',D,'conveyor','chute',[.76,.3,.5],[0,.32,-.60]))
        register(D,'conveyor',key,name,items,[.93,.62,1.55],edge=True,mount=[.72,1.0])
