"""53 machine prefabs, with service areas and retained functional modules."""
from .common import *

def author():
    machines=[('lathe','车床','keyshaft','saddle'),('mill','立式铣床','worm','fork_beam'),('drill','台钻','keyshaft','telescopic'),('press','液压压力机','crank','prismatic'),('grinder','台式砂轮机','flywheel','box_beam'),('bandsaw','带锯机','pulley_v','lattice'),('saw','推台锯','flywheel','box_beam'),('cnc','数控加工机','rack','box_beam'),('laser','激光切割台','rack','lattice'),('printer','三维打印机','pulley_timing','box_beam'),('bender','折弯机','worm','fork_beam'),('punch','冲床','crank','prismatic'),('roll','卷板机','coupling','box_beam'),('welder','焊接工位','keyshaft','lattice'),('polisher','抛光机','flywheel','tapered')]
    for j,(key,name,drive,frame) in enumerate(machines):
        items=[block('bed',[1.6,.25,1.0],color='#596F76'),block('cabinet',[1.3,.6,.85],[0,.25,0],color='#89A3A0'),fit('drive',l2('industry','driveunit',drive),[.55,.6,.65],[0,.85,0]),fit('column',l1('robot','joint' if frame=='prismatic' else 'link',frame if frame!='saddle' else 'box_beam'),[.28,1.3,.28],[-.5,.6,-.27]),block('table',[1.15,.1,.7],[0,1,.1])]
        if key in ('cnc','printer','laser'):items.append(fit('guard',l1('interior','case','display'),[1.5,1.1,.95],[0,.85,0]))
        items.append(fit('console',l1('props','device','control_knob'),[.12,.1,.12],[.55,.8,.5],optional=True))
        register('industry','machine',key,name,items,[1.7,2,.95],['接地机座','工作面','传动与服务节点',drive,frame])
    process=[('pump','离心泵站','impeller','elbow90'),('compressor','空压机','separator','flanged'),('filter','双联过滤机','filter','tee'),('mixer','立式混合机','agitator','cap'),('separator','分离器','separator','reducer'),('heater','热交换机','heat_tube','return'),('burner','工业燃烧炉','burner','nozzle'),('hopper','计量料斗','hopper','socket'),('dryer','滚筒干燥机','baffle','bellows'),('reactor','反应釜','agitator','cross'),('water','净水站','filter','elbow45'),('distiller','蒸馏装置','heat_tube','eccentric'),('cyclone','旋风除尘器','separator','hose_end'),('boiler','小型锅炉','burner','threaded'),('chiller','冷水机','heat_tube','flanged')]
    for j,(key,name,core,pipe) in enumerate(process):
        items=[block('skid',[1.8,.18,1.1],color='#677D80'),fit('process',l2('industry','processcore',core),[1.1,1.45,.9],[0,.18,0]),fit('inlet',l2('industry','flowjoint',pipe),[.35,.5,.4],[-.7,.4,0]),fit('outlet',l2('industry','flowjoint','flanged'),[.3,.5,.4],[.7,.6,0])]
        if key in ('filter','water','heater'):items.append(fit('secondary',l2('industry','processcore',core),[.55,1.2,.55],[.6,.18,-.1]))
        items.append(fit('valve',l1('industry','valve','gate' if j%2 else 'ball'),[.26,.4,.22],[-.65,.8,0]))
        register('industry','process',key,name,items,[2,1.8,1.3],['整体撬装底座','主处理机构','可拆管路',core,pipe],notes=['不是承压设备或工艺安全设计'])
    power=[('generator','柴油发电机','coil'),('transformer','配电变压器','transformer_fin'),('switchgear','开关柜','breaker'),('battery','储能柜','plate_stack'),('charger','车辆充电桩','cable_gland'),('solar','太阳能阵列','busbar'),('wind','小型风力发电机','coil'),('substation','紧凑配电站','insulator'),('ups','不间断电源柜','fuse'),('control','电气控制柜','terminal')]
    for key,name,component in power:
        items=[block('base',[1.2,.18,.8],color='#697B7F'),fit('cabinet',l1('interior','case','open_front'),[1,1.4,.7],[0,.18,0]),fit('functional',l1('industry','power',component),[.75,.8,.45],[0,.4,.1])]
        if key=='solar':
            items=[block('base',[1.7,.12,1.5])]
            for i in range(4):items.append(fit('panel'+str(i),'p5.power.solar_panel',[1.2,.08,.9],[(i%2-.5)*1.3,.8+(i//2)*.4,(i//2-.5)*.9],[22,0,0]))
            items.extend([block('support'+str(i),[.09,.9,.09],[s*.6,.12,0]) for i,s in enumerate((-1,1))])
        if key=='wind':items.append(fit('rotor',l2('vehicle','flightmodule','prop_blade'),[2,.25,2],[0,2,.2],[90,0,0]));items.append(block('mast',[.12,2,.12]))
        if key=='charger':items.append(fit('lead',l1('robot','link','cable'),[.35,.7,.2],[.6,.4,0]))
        register('industry','power',key,name,items,[3 if key=='solar' else 2,3 if key=='wind' else 1.8,2],['供电设备外观','结构与检修面',component,key])
    logistics=[('roller','滚筒输送台','roller',4),('belt','皮带输送机','cleated',5),('trough','槽形输送机','trough',5),('chute','下料滑槽','chute',3),('sorter','分流分拣机','roller',6),('elevator','斗式提升机','cleated',7),('turntable','滚筒转台','roller',2),('stacker','升降堆垛机','trough',3),('palletizer','码垛工位','roller',7),('ramp','卸料斜输送机','cleated',4),('gantry','起重龙门架','chute',2),('hoist','链式葫芦架','trough',2),('packing','包装工作线','roller',8)]
    for key,name,module,n in logistics:
        d=1+n*.4;items=legs(.8,d-.2,.65,.09)+[block('frame',[1,.12,d],[0,.65,0],color='#79938D')]
        for i in range(n):items.append(fit('section'+str(i),l2('industry','conveyor',module),[.9,.22,.42],[0,.77,(i-(n-1)/2)*.43]))
        if key in ('gantry','hoist','palletizer','stacker'):
            for i,s in enumerate((-1,1)):items.append(block('upright'+str(i),[.12,2.3,.12],[s*.8,0,0]))
            items.append(block('crossbeam',[1.8,.18,.2],[0,2.3,0]));items.append(fit('hoist',l2('industry','driveunit','pulley_v'),[.4,.45,.4],[0,1.8,0]))
        if key=='sorter':items.append(fit('sidebranch',l2('industry','conveyor','roller'),[1.4,.2,.5],[.9,.77,0],[0,90,0]))
        if key=='packing':items.append(fit('pack',l1('props','container','crate_side'),[.6,.5,.4],[0,1,0],optional=True))
        register('industry','logistics',key,name,items,[2.5,2.7,d+.2],['完整支架','运输面','检修传动',key,str(n)+'段'])
