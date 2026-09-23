"""25 complete robots, retaining articulated L2 output frames."""
from .common import *

def arm(base='arm',end='parallel_finger',axes=3,at=(0,.2,0)):
    items=[fit(base+'_base',l2('robot','joint','revolute'),None,at)]
    parent=base+'_base.output'
    for j in range(axes-1):
        name=base+'_link'+str(j);joint=base+'_joint'+str(j)
        items.append(fit(name,l2('robot','link','box_beam' if j==0 else 'tapered'),None,[0,.04,0],[0,0,25 if j==0 else -55],parent=parent))
        items.append(fit(joint,l2('robot','joint','wrist' if j==axes-2 else 'revolute'),None,[0,.76,0],parent=name))
        parent=joint+'.output'
    items.append(fit(base+'_tool',l2('robot','end',end),None,[0,.06,0],parent=parent))
    return items

def author():
    mobile=[('courier','室内配送机器人','battery','stereo'),('warehouse','仓储搬运机器人','compute','lidar_dome'),('inspection','巡检机器人','servo','depth'),('cleaner','清洁机器人','bumper','proximity'),('security','值守机器人','compute','stereo'),('agri','田间巡检车','battery','depth'),('rescue','搜救履带车','servo','antenna'),('telepresence','远程临场机器人','compute','stereo')]
    for j,(key,name,housing,sensor) in enumerate(mobile):
        items=[fit('body',l2('robot','housing',housing),[.75,.45,.8],[0,.18,0])]
        for i,(x,z) in enumerate(((-.38,-.25),(.38,-.25),(-.38,.25),(.38,.25))):items.append(fit('wheel'+str(i),l1('vehicle','wheel','solid_tire'),[.3,.10,.3],[x,.15,z],[0,0,90],anchor='center'))
        h=.95 if key=='telepresence' else .55
        items.append(block('mast',[.07,h,.07],[0,.45,-.15]));items.append(fit('sensor',l2('robot','sensor',sensor),[.3,.25,.3],[0,h+.4,-.15]))
        if key in ('courier','warehouse'):items.append(fit('cargo',l1('interior','drawer','box'),[.65,.42,.55],[0,.62,.07]))
        if key=='cleaner':
            for i,s in enumerate((-1,1)):items.append(fit('brush'+str(i),l1('props','toolhead','brush'),[.35,.12,.35],[s*.35,.02,.3]))
        if key=='rescue':items+=arm('manipulator','parallel_finger',2,[0,.63,.1])
        if key=='telepresence':items.append(fit('display',l1('props','device','screen_bezel'),[.45,.35,.055],[0,1.2,-.1]))
        register('robot','mobile',key,name,items,[1,2.4 if key=='rescue' else 1.7,1],['移动底盘','感知组件',housing,sensor,key],rig='rigid-hierarchy')
    for j,(key,name,end,axes) in enumerate([('pick','拾放机械臂','parallel_finger',3),('suction','真空搬运臂','suction',3),('weld','焊接作业臂','probe',4),('inspection','接触测量臂','probe',3),('cut','剪切加工臂','cutter',4),('magnetic','电磁分拣臂','magnet',3),('soft','柔性夹持臂','soft_pad',3),('adaptive','自适应抓取臂','adaptive_finger',4)]):
        items=[block('plinth',[.8,.22,.8],color='#708B8C'),*arm('arm',end,axes)]
        items.append(fit('controller',l1('robot','housing','compute'),[.45,.35,.4],[.5,0,-.25]))
        register('robot','arm',key,name,items,[2.5,3.8,2],['控制柜','层级关节','输出端跟随挂接',end,str(axes)+'轴'],rig='rigid-hierarchy',notes=['刚性节点运动，不提供逆运动学或真实接触抓取'])
    drones=[('quad','四旋翼巡检机',4,'stereo'),('hex','六旋翼测绘机',6,'lidar_dome'),('octo','八旋翼货运机',8,'depth'),('ducted','涵道巡检机',2,'proximity'),('tilt','倾转物流机',4,'antenna')]
    for key,name,n,sensor in drones:
        items=[fit('body',l2('robot','housing','drone_arm'),[.5,.3,.5],[0,.2,0]),fit('sensor',l2('robot','sensor',sensor),[.2,.2,.2],[0,0,.2])]
        for i in range(n):
            a=math.tau*i/n;x=.65*math.sin(a);z=.65*math.cos(a)
            items.append(beam('arm'+str(i),[0,.3,0],[x,.3,z],.07))
            items.append(fit('rotor'+str(i),l2('vehicle','flightmodule','rotor_blade'),[.55,.10,.55],[x,.34,z]))
            if key=='ducted':items.append(fit('guard'+str(i),l1('robot','housing','rotor_guard'),[.65,.16,.65],[x,.31,z]))
        for i,s in enumerate((-1,1)):items.append(fit('skid'+str(i),l1('interior','leg','sled'),[.06,.2,.6],[s*.22,0,0]))
        if key=='octo':items.append(fit('cargo',l1('props','container','case_foam'),[.35,.2,.35],[0,.03,0]))
        register('robot','drone',key,name,items,[2.1,.6,2.1],['完整机身','旋翼支臂','起落架',str(n)+'旋翼',sensor],rig='rigid-hierarchy')
    for key,name,n in [('rov','系留水下机器人',4),('auv','自主调查潜航器',3),('crawler','海床爬行机器人',6)]:
        items=[fit('hull',l1('vehicle','aero','nacelle'),[.65,.6,1.3],[0,.2,0]),fit('camera',l2('robot','sensor','stereo'),[.3,.2,.2],[0,.35,.7])]
        for i in range(n):
            x=.5*math.sin(i*math.tau/n);z=.7*math.cos(i*math.tau/n)
            items.append(fit('thruster'+str(i),l2('vehicle','flightmodule','inlet'),[.3,.3,.3],[x,.35,z],[0,360*i/n,0]))
        items.append(fit('skid',l1('interior','leg','sled'),[.9,.2,1.3]))
        if key=='rov':items+=arm('arm','parallel_finger',2,[0,.4,.6])
        if key=='crawler':items.extend([fit('leg'+str(i),l1('robot','link','offset'),[.25,.35,.35],[s*.4,0,z]) for i,(s,z) in enumerate([(-1,-.4),(1,-.4),(-1,.4),(1,.4)])])
        register('robot','underwater',key,name,items,[1.8,2 if key=='rov' else 1,2],['水密外壳造型','推进器','观察传感器',key],rig='rigid-hierarchy')
    items=[block('bed',[2.4,.15,1.5])]
    for i,s in enumerate((-1,1)):items.append(block('tower'+str(i),[.15,1.8,.15],[s*1.05,.15,0]))
    items.append(block('crossbeam',[2.3,.15,.25],[0,1.9,0]));items.append(fit('carriage',l2('robot','joint','prismatic'),None,[0,1.55,0],[0,0,90]));items.append(fit('head',l2('robot','end','suction'),None,[0,.04,0],parent='carriage.output'))
    register('robot','gantry','cartesian','三轴龙门取放装置',items,[2.6,2.2,1.5],['固定门架','移动滑台','跟随吸附端'],rig='rigid-hierarchy')
