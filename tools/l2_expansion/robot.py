"""37 rigid robot modules. Units, pivot frames, travel and collisions explicit."""
from .common import *
D='robot'

def flange(node='flange',at=(0,0,0),parent=None):
    return p(node,D,'end','tool_flange',[.22,.07,.22],at,parent=parent,collision={'type':'none'})

def author():
    for key in ids(D,'joint'):
        items=[p('housing',D,'joint',key,[.34,.30,.28],[0,.08,0]),flange('mount'),
               p('output',D,'end','tool_flange',[.23,.055,.23],[0,.38,0],moving=True,collision={'type':'none'}),
               p('cable',D,'link','cable',[.10,.12,.07],[.19,.10,0],optional=True),
               *fasteners('bolt',[[-.11,.09,.075],[.11,.09,-.075]],.027)]
        if key=='prismatic':
            items.append(p('rail',D,'link','telescopic',[.16,.35,.16],[0,.18,0]))
            ctr=[control('stroke','output','直线输出行程',.22,axis=(0,1,0),mode='translation')]
        elif key=='compliant':ctr=[control('deflect','output','刚性端面近似偏转',8,-8,axis=(0,0,1))]
        elif key in ('spherical','universal','crossed'):
            items.append(p('inner',D,'joint','wrist',[.22,.12,.22],[0,.30,0],moving=True,collision={'type':'none'}))
            items[2]['parent']='inner';items[2]['position']=[0,.1,0]
            ctr=[control('pitch','inner','俯仰',50,-50,axis=(1,0,0)),control('yaw','output','输出转角',180,-180)]
        else:ctr=[control('joint','output','输出转角',180,-180)]
        register(D,'joint',key,label(pid(D,'joint',key))+'驱动接口组',items,[.48,.47,.34],mount=[.22,.22],controls=ctr,ports_=[ports(D,[.48,.47,.34],[.22,.22])[0],mounted_port('output','output',[0,.055,0])],
                 notes=['独立刚性关节与行程；不包含伺服动力学、闭链求解或软体形变。'])
    for key in ids(D,'link'):
        items=[flange(),p('link',D,'link',key,[.21,.65,.20],[0,.05,0]),flange('tip',[0,.7,0]),
               p('serviceCable',D,'link','cable',[.055,.56,.055],[.13,.12,0],optional=True),
               *fasteners('bolt',[[-.08,.07,.06],[.08,.07,-.06]],.024)]
        ctr=[]
        if key=='telescopic':
            items.append(p('extension',D,'link','box_beam',[.14,.50,.14],[0,.38,0],moving=True))
            items[2]['parent']='extension';items[2]['position']=[0,.5,0]
            ctr=[control('extension','extension','伸出长度',.32,axis=(0,1,0),mode='translation')]
        elif key=='cable':
            items=[flange(),p('endGuide',D,'housing','servo',[.22,.10,.18],[0,.65,0])]
            for i in range(6):items.append(p('segment'+str(i),D,'link','cable',[.15,.11,.14],[0,.055+i*.10,0]))
        register(D,'link',key,label(pid(D,'link',key))+'法兰线缆组',items,[.29,.9,.27],mount=[.22,.22],controls=ctr)
    for key in ids(D,'end'):
        items=[flange(),p('body',D,'housing','servo',[.30,.16,.21],[0,.06,0])];ctr=[]
        if key in ('parallel_finger','adaptive_finger','soft_pad'):
            src='parallel_finger' if key=='soft_pad' else key
            for i,x in enumerate([-.11,.11]):
                items.extend([p('finger'+str(i),D,'end',src,[.07,.25,.10],[x,.20,0],rot=[0,i*180,0],moving=True),
                              p('pad'+str(i),D,'end','soft_pad',[.025,.1,.08],[.034,.15,0],parent='finger'+str(i))])
            if key=='adaptive_finger':
                for i,x in enumerate([-.11,.11]):items.append(p('knuckle'+str(i),D,'joint','compliant',[.055,.08,.095],[x,.29,0]))
            elif key=='soft_pad':items.append(p('crossbar',D,'link','fork_beam',[.29,.07,.09],[0,.17,0]))
            ctr=[control('openL','finger0','左指张开',.08,axis=(-1,0,0),mode='translation'),control('openR','finger1','右指张开',.08,axis=(-1,0,0),mode='translation')]
        elif key=='cutter':
            items.extend([p('bladeL',D,'end','cutter',[.15,.25,.035],[-.035,.19,0],moving=True),
                          p('bladeR',D,'end','cutter',[.15,.25,.035],[.035,.19,.04],[0,180,0],moving=True),
                          p('pin','props','fastener','clevis_pin',[.045,.15,.045],[0,.23,.02],[90,0,0])])
            ctr=[control('openL','bladeL','左刃张开',30,axis=(0,0,1)),control('openR','bladeR','右刃张开',30,axis=(0,0,-1))]
        elif key=='suction':
            items.extend([p('stem','industry','pipe','hose_end',[.10,.17,.10],[0,.20,0]),p('cup',D,'end',key,[.26,.10,.26],[0,.36,0]),p('port','industry','pipe','elbow90',[.1,.13,.1],[.1,.12,0])])
        elif key=='probe':
            items.extend([p('slide',D,'joint','prismatic',[.13,.2,.13],[0,.19,0]),p('probe',D,'end',key,[.035,.25,.035],[0,.34,0],moving=True)])
            ctr=[control('stroke','probe','探针伸出',.08,axis=(0,1,0),mode='translation')]
        elif key=='magnet':
            items.extend([p('magnet',D,'end',key,[.27,.10,.27],[0,.21,0]),p('switch','props','device','control_knob',[.06,.04,.06],[.12,.17,0]),p('guard',D,'housing','bumper',[.28,.04,.28],[0,.30,0])])
        else:
            items.extend([flange('output',[0,.22,0]),p('lock','gameplay','lock','latch',[.07,.12,.045],[.15,.15,0],moving=True)])
            ctr=[control('release','lock','快换锁舌',.06,axis=(0,1,0),mode='translation')]
        register(D,'end',key,label(pid(D,'end',key))+'末端执行组',items,[.46,.64,.34],mount=[.22,.22],controls=ctr,
                 notes=['刚性开合示例，不具备抓取约束、力反馈、吸附或切割仿真。'])
    for key in ids(D,'sensor'):
        items=[flange(),p('bracket',D,'joint','crossed',[.32,.22,.25],[0,.06,0]),
               p('sensor',D,'sensor',key,[.28,.24,.18],[0,.22,0],moving=True),
               p('connector','industry','power','terminal',[.08,.055,.09],[0,.10,-.12]),*fasteners('fix',[[-.10,.08,.08],[.10,.08,-.08]],.023)]
        if key in ('stereo','depth'):
            for i,x in enumerate([-.075,.075] if key=='stereo' else [0]):items.append(p('lens'+str(i),'props','device','lens_barrel',[.065,.04,.065],[x,.13,.09],[90,0,0],parent='sensor'))
        elif key=='lidar_dome':items.append(p('ring',D,'joint','wrist',[.29,.04,.29],[0,.005,0],parent='sensor',collision={'type':'none'}))
        register(D,'sensor',key,label(pid(D,'sensor',key))+'标定支架组',items,[.36,.50,.35],mount=[.22,.22],
                 controls=[control('aim','sensor','传感器朝向',180,-180)] if key in ('antenna','lidar_dome') else [control('pitch','sensor','俯仰角',45,-45,axis=(1,0,0))],
                 notes=['外观与朝向节点；不提供真实测距/相机标定内参。'])
    for key in ids(D,'housing'):
        items=[p('shell',D,'housing',key,[.45,.22,.34],[0,.06,0]),plate('mountplate',[.40,.06,.30]),
               p('connector','industry','power','terminal',[.13,.05,.1],[0,.16,.17]),*fasteners('fix',[[x,.06,z] for x in [-.16,.16] for z in [-.12,.12]],.027)]
        ctr=[]
        if key in ('battery','compute'):
            items.append(plate('serviceLid',[.36,.035,.26],[0,.285,-.13],anchor='back',moving=True))
            ctr=[control('lid','serviceLid','检修盖开启',100,axis=(1,0,0))]
            if key=='compute':items.append(p('heatsink','industry','power','transformer_fin',[.32,.10,.24],[0,.28,0]))
        elif key=='rotor_guard':items.append(p('hub',D,'joint','wrist',[.16,.10,.16],[0,.16,0]))
        elif key=='servo':items.append(flange('output',[0,.28,0]))
        elif key=='drone_arm':items.append(p('wire',D,'link','cable',[.045,.36,.04],[0,.18,0],[0,0,90]))
        else:items.append(p('sensor',D,'sensor','proximity',[.075,.08,.07],[0,.12,.185]))
        register(D,'housing',key,label(pid(D,'housing',key))+'安装检修组',items,[.49,.42,.40],controls=ctr,mount=[.32,.24])
    items=[flange(),p('yaw',D,'joint','revolute',[.26,.15,.26],[0,.07,0],moving=True),
           p('fork',D,'link','fork_beam',[.30,.25,.13],[0,.16,0],parent='yaw'),
           p('pitch',D,'joint','wrist',[.18,.13,.18],[0,.39,0],[0,0,90],parent='yaw',moving=True,collision={'type':'none'}),
           p('camera',D,'sensor','stereo',[.26,.16,.10],[0,0,0],anchor='center',parent='pitch')]
    register(D,'special','gimbal','两轴相机云台',items,[.40,.6,.33],mount=[.22,.22],controls=[control('yaw','yaw','水平转动',180,-180),control('pitch','pitch','俯仰转动',75,-75)])
    items=[flange(),p('housing',D,'housing','servo',[.36,.14,.24],[0,.07,0]),p('crossbar',D,'link','box_beam',[.08,.48,.08],[0,.24,0],[0,0,90],anchor='center')]
    for i,x in enumerate([-.19,.19]):
        items.extend([p('head'+str(i),D,'end','suction',[.17,.10,.17],[x,.27,0]),p('hose'+str(i),'industry','pipe','hose_end',[.07,.10,.07],[x,.19,0])])
    register(D,'special','dual_suction','双吸盘并联横梁',items,[.57,.40,.28],mount=[.22,.22],notes=['两个独立端头的安装结构，不含真空流体模拟。'])
