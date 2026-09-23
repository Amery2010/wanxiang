"""Robot building blocks, unrigged and without simulated actuator behavior."""
from .common import *
from .industry import gear,flange


def author():
    def put(g,k,n,fs,sz=(.8,.8,.8),**kw):return register('robot',g,k,n,fs,sz,material='mat.metal',**kw)
    joints=names('revolute:单轴旋转关节壳 spherical:球形关节壳 universal:万向关节十字芯 prismatic:直线关节滑体 compliant:柔性关节梁 crossed:交叉轴关节架 differential:差动关节壳 wrist:中空腕轴壳')
    for key,name in joints:
        if key=='revolute':fs=[round_tube(.2,.105,.22,'l1Slate'),ring(.235,.13,.045,'l1Metal'),ring(.235,.13,.045,'l1Metal',position=[0,.22,0])]
        elif key=='spherical':fs=[ico([.38,.38,.38],'l1Metal',[0,.2,0],detail=1),round_tube(.075,.04,.25,'metal',position=[0,.35,0])]
        elif key=='universal':fs=[rod([-.25,.15,0],[.25,.15,0],.07,'l1Metal'),rod([0,.15,-.25],[0,.15,.25],.07,'l1Metal'),formbox(.17,.16,.17,'l1Slate',y=.07)]
        elif key=='prismatic':fs=[formbox(.30,.16,.45,'l1Slate')]+[formbox(.06,.06,.45,'l1Metal',x=x,y=.16) for x in [-.12,.12]]
        elif key=='compliant':fs=[formbox(.4,.08,.18,'l1Slate',y=y) for y in [0,.4]]+[formbox(.022,.32,.14,'l1Metal',x=x,y=.08) for x in [-.15,-.05,.05,.15]]
        elif key=='crossed':fs=[round_tube(.22,.16,.08,'l1Slate'),round_tube(.18,.12,.10,'l1Metal',rotation=[90,0,0],position=[0,.04,0])]
        elif key=='differential':fs=[formbox(.45,.3,.36,'l1Slate'),round_tube(.095,.05,.62,'l1Metal',rotation=[0,0,90],position=[.31,.15,0]),round_tube(.08,.04,.18,'metal',rotation=[90,0,0],position=[0,.15,.24])]
        else:fs=[lathe([[.23,0],[.23,.1],[.16,.32],[.10,.32],[.10,0]],'l1Slate',12,closed_profile=True)]+placed(flange(.19,.1),[0,.31,0])
        put('joint',key,name,fs)
    links=names('box_beam:箱形机械臂段 fork_beam:叉形机械臂段 tapered:收分机械臂段 lattice:桁架机械臂段 offset:偏置机械臂段 telescopic:伸缩臂套段 cable:电缆拖链单节')
    for key,name in links:
        if key=='box_beam':fs=[plate([[-.13,0],[.13,0],[.13,.75],[-.13,.75]],.18,'l1Slate')]+[round_tube(.075,.04,.20,'l1Metal',rotation=[90,0,0],position=[0,y,.10]) for y in [.10,.65]]
        elif key=='fork_beam':fs=[formbox(.4,.07,.2,'l1Slate')]+[formbox(.075,.6,.2,'l1Slate',x=x,y=.07) for x in [-.16,.16]]
        elif key=='tapered':fs=[loft([[0,0,0,.18,.14],[0,.65,0,.09,.08]],'l1Slate',6),ring(.19,.1,.05,'l1Metal')]
        elif key=='lattice':fs=[rod([x,0,z],[x,.75,z],.025,'l1Metal') for x in [-.12,.12] for z in [-.08,.08]]+[rod([-.12,y,-.08],[.12,y+.24,.08],.018,'l1Slate') for y in [0,.25,.5]]
        elif key=='offset':fs=[plate([[-.1,0],[.1,0],[.10,.25],[.35,.45],[.35,.75],[.15,.75],[.15,.53],[-.1,.3]],.18,'l1Slate')]
        elif key=='telescopic':fs=[round_tube(.15,.105,.72,'l1Slate',8),ring(.18,.075,.07,'l1Metal',position=[0,.65,0])]
        else:fs=[formbox(.28,.035,.19,'l1Slate')]+[formbox(.035,.13,.19,'l1Slate',x=x,y=.035) for x in [-.122,.122]]+[rod([-.17,.10,0],[.17,.10,0],.025,'l1Metal')]
        put('link',key,name,fs,(.9,1,.65))
    ends=names('parallel_finger:平行夹爪指体 adaptive_finger:自适应夹爪指节 suction:吸盘末端片 magnet:磁吸末端盘 tool_flange:工具快换法兰 probe:接触探针芯 cutter:剪切末端刃片 soft_pad:柔性夹爪衬垫')
    for key,name in ends:
        if key=='parallel_finger':fs=[plate([[-.04,0],[.08,0],[.08,.46],[-.02,.46],[-.02,.35],[-.04,.35]],.11,'l1Metal')]+[formbox(.02,.12,.10,'l1Rubber',x=-.03,y=.30)]
        elif key=='adaptive_finger':fs=[plate([[-.07,0],[.07,0],[.1,.25],[.03,.40],[-.04,.4],[-.08,.2]],.10,'l1Slate')]+[round_tube(.045,.02,.12,'l1Metal',rotation=[90,0,0],position=[0,y,.06]) for y in [.08,.3]]
        elif key=='suction':fs=[lathe([[.2,0],[.2,.035],[.075,.18],[.05,.24],[.028,.24],[.047,.16],[.17,.025],[.17,0]],'l1Rubber',14,closed_profile=True)]
        elif key=='magnet':fs=[disk(.23,.09,'l1Slate'),ring(.21,.055,.025,'l1Metal',position=[0,.09,0]),disk(.08,.025,'metal',y=.09)]
        elif key=='tool_flange':fs=flange(.24,.11)+[formbox(.06,.05,.065,'l1Ochre',y=.03,z=.20)]
        elif key=='probe':fs=[rod([0,0,0],[0,.35,0],.018,'l1Metal'),ico([.065,.065,.065],'l1Ivory',[0,.38,0],detail=1),round_tube(.065,.032,.12,'l1Slate')]
        elif key=='cutter':fs=[plate([[-.06,0],[.1,0],[.16,.15],[.02,.45],[-.04,.50],[.02,.22],[-.06,.14]],.04,'metal')]
        else:fs=[formbox(.14,.035,.30,'l1Rubber')]+[formbox(.14,.02,.025,'rubber',y=.035,z=z) for z in [-.12,-.06,0,.06,.12]]
        put('end',key,name,fs,(.6,.7,.6))
    sensors=names('lidar_dome:激光扫描罩体 stereo:双目相机前罩 depth:深度相机前罩 proximity:接近传感头 imu:惯导模块壳 antenna:通信天线座')
    for key,name in sensors:
        if key=='lidar_dome':fs=[lathe([[.18,0],[.20,.06],[.20,.20],[.13,.29],[.035,.32]],'l1Slate',16,cap=True),ring(.204,.015,.06,'glass',position=[0,.16,0])]
        elif key=='stereo':fs=[formbox(.55,.15,.15,'l1Slate')]+[round_tube(.057,.035,.05,'l1Metal',rotation=[90,0,0],position=[x,.075,.10]) for x in [-.18,.18]]
        elif key=='depth':fs=[formbox(.32,.2,.18,'l1Slate'),round_tube(.063,.04,.05,'l1Metal',rotation=[90,0,0],position=[-.07,.11,.115]),formbox(.065,.055,.03,'glass',x=.08,y=.065,z=.11)]
        elif key=='proximity':fs=[lathe([[.065,0],[.065,.25],[.08,.28],[.08,.32]],'l1Metal',12,cap=True),disk(.07,.012,'l1Rubber',y=.32)]
        elif key=='imu':fs=[formbox(.25,.075,.22,'l1Slate')]+[disk(.016,.01,'metal',y=.075,position=[x,0,z]) for x in [-.095,.095] for z in [-.08,.08]]
        else:fs=[formbox(.14,.045,.14,'l1Slate'),rod([0,.045,0],[0,.5,0],.022,'l1Rubber',r2=.009),ring(.035,.013,.04,'metal',position=[0,.06,0])]
        put('sensor',key,name,fs,(.7,.6,.6))
    housings=names('battery:机器人电池托壳 compute:计算单元散热壳 servo:舵机外壳 drone_arm:无人机臂壳 rotor_guard:旋翼保护圈 bumper:移动底盘防撞片')
    for key,name in housings:
        if key=='battery':fs=[formbox(.42,.04,.55,'l1Slate')]+[formbox(.035,.20,.55,'l1Slate',x=x) for x in [-.193,.193]]+[formbox(.35,.09,.035,'l1Rubber',y=.04,z=-.255)]
        elif key=='compute':fs=[formbox(.5,.16,.35,'l1Slate')]+[formbox(.025,.065,.35,'metal',x=x,y=.16) for x in [-.2,-.12,-.04,.04,.12,.2]]
        elif key=='servo':fs=[formbox(.28,.3,.18,'l1Slate'),round_tube(.07,.03,.07,'l1Metal',position=[0,.3,0]),formbox(.42,.04,.1,'metal',y=.2)]
        elif key=='drone_arm':fs=[loft([[0,0,0,.08,.045],[0,.55,0,.055,.035]],'l1Slate',6),ring(.10,.045,.04,'metal',position=[0,.58,0])]
        elif key=='rotor_guard':fs=[ring(.36,.028,.07,'l1Slate')]+[rod([0,0,0],[.33*math.cos(a),0,.33*math.sin(a)],.025,'metal') for a in [0,math.tau/3,math.tau*2/3]]
        else:fs=[arc(.42,.06,20,160,axis='xz',color='l1Rubber',n=10),formbox(.45,.045,.12,'l1Slate')]
        put('housing',key,name,fs)
    finish('robot',35)
