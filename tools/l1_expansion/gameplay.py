"""Visual gameplay parts. Activation/state machines belong to consumer games."""
from .common import *
from .industry import gear


def rune(outline,color='l1Ochre',radius=.24,depth=.035):
    if outline=='diamond':p=[[0,0],[radius,.3],[0,.6],[-radius,.3]]
    elif outline=='bolt':p=[[.08,.6],[-.18,.25],[-.02,.25],[-.12,0],[.2,.36],[.02,.36]]
    elif outline=='cross':p=[[-.07,0],[.07,0],[.07,.2],[.24,.2],[.24,.34],[.07,.34],[.07,.55],[-.07,.55],[-.07,.34],[-.24,.34],[-.24,.2],[-.07,.2]]
    elif outline=='star':p=[[(.25 if i%2==0 else .11)*math.sin(i*math.pi/5),.3+(.25 if i%2==0 else .11)*math.cos(i*math.pi/5)] for i in range(10)]
    else:p=[[-.22,0],[.22,0],[.22,.45],[0,.58],[-.22,.45]]
    return plate(p,depth,color)


def author():
    def put(g,k,n,fs,sz=(.9,.9,.9),**kw):return register('gameplay',g,k,n,fs,sz,**kw)
    locks=names('bolt:门栓滑块 latch:弹簧锁舌 keeper:锁扣受口 padlock_body:挂锁锁体 keyway:钥匙孔面板 warded_key:挡片钥匙坯 cam:偏心锁舌芯 combination:密码轮片 seal:机关封印片 socket:符石插槽框')
    for key,name in locks:
        if key=='bolt':fs=[rod([-.3,.08,0],[.3,.08,0],.05,'metal'),rod([0,.08,0],[0,.23,0],.03,'l1Metal')]
        elif key=='latch':fs=[plate([[-.20,0],[.2,0],[.32,.12],[.2,.20],[-.2,.20]],.09,'l1Metal')]
        elif key=='keeper':fs=[formbox(.25,.04,.2,'l1Metal')]+[formbox(.04,.18,.2,'l1Metal',x=x,y=.04) for x in [-.105,.105]]+[formbox(.25,.04,.2,'l1Metal',y=.22)]
        elif key=='padlock_body':fs=[]
        elif key=='keyway':fs=[ring(.15,.06,.03,'copper',rotation=[90,0,0],position=[0,.32,0])]+[plate([[-.065,0],[-.035,.28],[-.095,.28],[-.13,0]],.03,'copper'),plate([[.065,0],[.13,0],[.095,.28],[.035,.28]],.03,'copper')]
        elif key=='warded_key':fs=[ring(.10,.027,.025,'copper',rotation=[90,0,0],position=[0,.43,0]),rod([0,0,0],[0,.35,0],.024,'copper'),formbox(.11,.04,.025,'copper',x=.04,y=.02),formbox(.07,.035,.025,'copper',x=.023,y=.10)]
        elif key=='cam':fs=[disk(.14,.06,'l1Metal'),formbox(.12,.06,.28,'metal',z=.15),round_tube(.055,.025,.09,'copper')]
        elif key=='combination':fs=[gear(10,.16,.065),round_tube(.07,.045,.08,'copper')]
        elif key=='seal':fs=[disk(.23,.06,'l1Terracotta'),rune('star','l1Ochre',depth=.025,)]
        else:fs=frame(.55,.65,.16,.085,'stoneDark')+[plate([[-.18,0],[.18,0],[.12,.10],[-.12,.10]],.20,'l1Ochre')]
        if key=='padlock_body':fs=[box([.35,.28,.15],'copper',[0,.14,0],.055)]+[round_tube(.035,.021,.16,'metal',position=[x,.24,0]) for x in [-.11,.11]]
        put('lock',key,name,fs)
    triggers=names('pressure:压力踏板芯 lever:拉杆摆臂 button:按钮帽 pulley:绳控滑轮芯 wheel:转盘把轮 crank:手摇曲柄芯 balance:平衡踏板芯 tripwire:绊线挂钩 dial:旋钮指针芯 sensor_plate:触发感应面板')
    for key,name in triggers:
        if key=='pressure':fs=[box([.6,.08,.6],'stone',[0,.04,0],.025),formbox(.14,.08,.14,'metal',y=-.08)]
        elif key=='lever':fs=[rod([0,0,0],[0,.6,.12],.035,'wood'),ico([.13,.13,.13],'l1Terracotta',[0,.63,.125],detail=1)]
        elif key=='button':fs=[lathe([[.14,0],[.18,.07],[.18,.14],[.15,.18]],'l1Terracotta',12,cap=True)]
        elif key=='pulley':fs=[lathe([[.23,0],[.23,.04],[.16,.08],[.23,.12],[.23,.16],[.055,.16],[.055,0]],'l1Metal',14,closed_profile=True)]
        elif key=='wheel':fs=[ring(.3,.035,.055,'wood'),round_tube(.06,.025,.1,'metal')]+[rod([0,.02,0],[.27*math.cos(a),.02,.27*math.sin(a)],.025,'wood') for a in [0,math.pi/2,math.pi,math.pi*1.5]]
        elif key=='crank':fs=[rod([0,0,0],[.3,.05,0],.03,'l1Metal'),rod([.3,.05,0],[.3,.25,0],.04,'wood'),round_tube(.07,.03,.1,'metal')]
        elif key=='balance':fs=[plate([[-.5,.12],[0,0],[.5,.12],[.5,.19],[0,.07],[-.5,.19]],.35,'wood')]
        elif key=='tripwire':fs=[rod([0,0,0],[0,.36,0],.023,'metal'),arc(.065,.018,0,250,color='l1Metal',center=[.065,.36,0])]
        elif key=='dial':fs=[disk(.18,.07,'l1Slate'),plate([[-.04,0],[.04,0],[.025,.17],[0,.24],[-.025,.17]],.03,'l1Ochre',rotation=[90,0,0],position=[0,.09,0])]
        else:fs=[formbox(.45,.045,.45,'l1Slate'),ring(.16,.018,.02,'cyan',position=[0,.055,0])]
        put('trigger',key,name,fs)
    traps=names('spike:机关尖刺芯 jaw:夹合机关齿片 saw:圆锯齿盘芯 dart_port:暗箭出口框 pendulum:摆锤头芯 crusher:压击块面片 flame_port:火焰出口栅 blade:旋刃单叶 coil:电弧线圈座 vent:蒸汽喷口盖')
    for key,name in traps:
        if key=='spike':fs=[loft([[0,0,0,.13,.13],[0,.6,0,.006,.006]],'metal',4),formbox(.25,.05,.25,'l1Slate')]
        elif key=='jaw':fs=[plate([[-.4,0],[.4,0],[.4,.08],[-.4,.08]],.12,'metal')]+[plate([[x-.04,.08],[x+.04,.08],[x,.23]],.07,'l1Metal') for x in [-.3,-.15,0,.15,.3]]
        elif key=='saw':fs=[gear(18,.35,.035),round_tube(.07,.035,.055,'metal')]
        elif key=='dart_port':fs=frame(.25,.30,.15,.045,'stoneDark')+[formbox(.1,.025,.17,'l1Metal',y=.05)]
        elif key=='pendulum':fs=[ico([.5,.5,.5],'stoneDark',[0,.28,0],detail=1),ring(.08,.025,.06,'metal',rotation=[90,0,0],position=[0,.58,0])]
        elif key=='crusher':fs=[formbox(.65,.18,.65,'stone')]+[loft([[x,.18,z,.07,.07],[x,.33,z,.012,.012]],'metal',4) for x in [-.21,0,.21] for z in [-.21,0,.21]]
        elif key=='flame_port':fs=[round_tube(.2,.15,.17,'metal')]+[rod([-.14,.18,z],[.14,.18,z],.018,'l1Slate') for z in [-.10,0,.10]]
        elif key=='blade':fs=[plate([[-.04,0],[.1,0],[.42,.38],[.38,.58],[.27,.42],[.04,.18]],.035,'l1Metal')]
        elif key=='coil':fs=[rod([0,0,0],[0,.55,0],.06,'l1Ivory')]+[ring(.12,.035,.025,'copper',position=[0,y,0]) for y in [.08,.17,.26,.35,.44]]
        else:fs=[disk(.23,.045,'l1Slate')]+[round_tube(.04,.024,.09,'l1Metal',position=[x,.045,z]) for x,z in [(-.1,0),(.1,0),(0,-.1),(0,.1),(0,0)]]
        put('trap',key,name,fs)
    platforms=names('lift_shoe:升降平台导靴 hinge_plate:翻板铰接片 rail_stop:轨道止挡块 floating_core:悬浮平台底芯 moving_bracket:移动平台托架 bridge_lock:桥板搭扣芯 spring_seat:弹跳台弹簧座 retracting:伸缩踏步片')
    for key,name in platforms:
        if key=='lift_shoe':fs=[plate([[-.2,0],[.2,0],[.2,.35],[.12,.35],[.12,.08],[-.12,.08],[-.12,.35],[-.2,.35]],.25,'l1Slate')]
        elif key=='hinge_plate':fs=[formbox(.4,.045,.32,'l1Metal')]+[round_tube(.035,.016,.1,'metal',rotation=[0,0,90],position=[x,.025,.18]) for x in [-.15,0,.15]]
        elif key=='rail_stop':fs=[plate([[-.25,0],[.25,0],[.15,.3],[-.04,.35]],.25,'l1Rubber')]
        elif key=='floating_core':fs=[loft([[0,0,0,.12,.12],[0,.15,0,.35,.35],[0,.3,0,.45,.45]],'l1Slate',6),ring(.25,.025,.035,'cyan',position=[0,.1,0])]
        elif key=='moving_bracket':fs=[plate([[-.3,0],[.3,0],[.3,.06],[-.15,.06],[-.15,.38],[-.3,.38]],.25,'l1Metal')]
        elif key=='bridge_lock':fs=[plate([[-.08,0],[.08,0],[.08,.32],[.20,.36],[.18,.46],[-.08,.42]],.10,'metal')]
        elif key=='spring_seat':fs=[disk(.25,.065,'l1Slate'),ring(.17,.04,.1,'l1Metal',position=[0,.11,0])]
        else:fs=[formbox(.65,.075,.40,'l1Slate')]+[formbox(.055,.06,.60,'l1Metal',x=x,y=.075,z=-.12) for x in [-.24,.24]]
        put('platform',key,name,fs)
    pickups=names('crystal:结晶奖励芯 coin_blank:奖励币坯 medal:徽章底坯 heart:生命标识芯 bolt:能量标识芯 shield:防护标识芯 key:钥匙标识芯 star:星形标识芯 cartridge:补给弹舱芯 capsule:补给胶囊壳')
    for key,name in pickups:
        if key=='crystal':fs=[loft([[0,0,0,.07,.07],[0,.14,0,.18,.15],[0,.48,0,.13,.11],[0,.65,0,.009,.009]],'cyan',6)]
        elif key=='coin_blank':fs=[disk(.23,.035,'l1Ochre'),ring(.205,.012,.012,'copper',position=[0,.04,0])]
        elif key=='medal':fs=[disk(.20,.04,'copper'),formbox(.13,.035,.14,'l1Terracotta',z=.2)]
        elif key=='heart':fs=[lens([[0,0],[.25,.28],[.22,.45],[.1,.51],[0,.42],[-.1,.51],[-.22,.45],[-.25,.28]],'l1Terracotta',.055,0)]
        elif key in ('bolt','shield','star'):fs=[rune(key)]
        elif key=='key':fs=[ring(.13,.04,.045,'l1Ochre',rotation=[90,0,0],position=[0,.48,0]),formbox(.06,.36,.045,'l1Ochre'),formbox(.18,.05,.045,'l1Ochre',x=.06,y=.02)]
        elif key=='cartridge':fs=[lathe([[.1,0],[.1,.06],[.085,.08],[.085,.38],[.05,.48],[.015,.52]],'copper',10,cap=True),ring(.102,.025,.025,'metal',position=[0,.06,0])]
        else:fs=[loft([[0,0,0,.08,.08],[0,.08,0,.15,.15],[0,.38,0,.15,.15],[0,.48,0,.075,.075]],'l1Ivory',10),ring(.155,.02,.055,'l1Slate',position=[0,.25,0])]
        put('pickup',key,name,fs,(.7,.85,.7),collision='none')
    covers=names('sandbag:沙袋表层块 gabion:石笼网片 blast_panel:防爆板片 barricade_leg:路障支腿 bullet_slot:射击孔框 shield_plate:掩体护板 viewport:观察孔框 capstone:胸墙压顶块')
    for key,name in covers:
        if key=='sandbag':fs=[box([.6,.22,.32],'l1Ochre',[0,.11,0],.075),rod([-.27,.12,.15],[.27,.12,.15],.01,'woodLight')]
        elif key=='gabion':fs=[rod([x,0,0],[x,.6,0],.012,'metal') for x in [-.3,-.2,-.1,0,.1,.2,.3]]+[rod([-.3,y,0],[.3,y,0],.012,'metal') for y in [0,.1,.2,.3,.4,.5,.6]]
        elif key=='blast_panel':fs=[formbox(.65,.6,.065,'l1Slate')]+[formbox(.065,.6,.035,'metal',x=x,z=.05) for x in [-.24,0,.24]]
        elif key=='barricade_leg':fs=[rod([-.3,0,0],[.3,.6,0],.055,'wood'),rod([.3,0,0],[-.3,.6,0],.055,'wood')]
        elif key=='bullet_slot':fs=frame(.60,.22,.25,.075,'stoneDark')
        elif key=='shield_plate':fs=[plate([[-.35,0],[.35,0],[.4,.55],[.26,.72],[-.26,.72],[-.4,.55]],.07,'l1Slate')]
        elif key=='viewport':fs=frame(.50,.4,.18,.07,'l1Slate')+[formbox(.4,.04,.27,'metal',y=.38,z=.04)]
        else:fs=[plate([[-.4,0],[.4,0],[.4,.12],[0,.22],[-.4,.12]],.55,'stone')]
        put('cover',key,name,fs)
    effects=names('emitter_cup:粒子喷口底杯 beam_lens:光束透镜芯 ring:环形特效承载圈 decal_frame:地贴承载边框 trail_socket:拖尾发射挂点 impact_disc:命中盘片 spark_prism:火花棱片 fog_card:体积雾片载体')
    for key,name in effects:
        if key=='emitter_cup':fs=[lathe([[.12,0],[.22,.22],[.18,.22],[.085,.04],[.085,0]],'metal',12,closed_profile=True)]
        elif key=='beam_lens':fs=[loft([[0,0,0,.16,.16],[0,.055,0,.2,.2],[0,.09,0,.16,.16]],'glass',14)]
        elif key=='ring':fs=[ring(.3,.035,.045,'cyan')]
        elif key=='decal_frame':fs=frame(.6,.6,.014,.018,'l1Ochre')
        elif key=='trail_socket':fs=[plate([[-.06,0],[.06,0],[.12,.14],[0,.28],[-.12,.14]],.045,'l1Slate'),round_tube(.032,.017,.07,'metal',rotation=[90,0,0],position=[0,.14,.045])]
        elif key=='impact_disc':fs=[plate([[r*math.cos(i*math.pi/6),.3+r*math.sin(i*math.pi/6)] for i in range(12) for r in [.25 if i%2 else .13]],.025,'l1Ochre')]
        elif key=='spark_prism':fs=[topo([[0,0,0],[.08,.2,0],[0,.55,0],[-.08,.2,0],[0,.2,.045],[0,.2,-.045]],[[0,1,4],[0,4,3],[0,3,5],[0,5,1],[2,4,1],[2,3,4],[2,5,3],[2,1,5]],'l1Ochre')]
        else:fs=[plate([[-.4,0],[.4,0],[.4,.45],[-.4,.45]],.008,'l1Ivory')]
        put('fx',key,name,fs,collision='none')
    destruction=names('wall_chunk:墙体断裂块 beam_splinter:木梁断裂片 plate_fragment:金属板断片 hinge_remnant:断裂铰链残件 rubble_corner:瓦砾转角块')
    for key,name in destruction:
        if key=='wall_chunk':fs=[plate([[-.3,0],[.32,.05],[.24,.3],[.08,.24],[-.12,.43],[-.32,.29]],.25,'stone')]
        elif key=='beam_splinter':fs=[plate([[-.09,0],[.1,0],[.12,.52],[.03,.37],[-.02,.72],[-.06,.49],[-.1,.64]],.12,'wood')]
        elif key=='plate_fragment':fs=[plate([[-.3,0],[.25,.04],[.12,.22],[.25,.3],[-.16,.45],[-.11,.2],[-.3,.3]],.025,'l1Metal',rotation=[8,0,0])]
        elif key=='hinge_remnant':fs=[plate([[-.12,0],[.10,.04],[.15,.24],[-.08,.3]],.04,'metal'),round_tube(.04,.022,.18,'l1Metal',position=[-.09,.12,0])]
        else:fs=[plate([[-.35,0],[.34,0],[.34,.15],[-.15,.15],[-.15,.4],[-.35,.45]],.25,'stone')]
        put('destruction',key,name,fs)
    finish('gameplay',69)
