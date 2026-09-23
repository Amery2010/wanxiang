"""252 small semantic components. Authored profiles, not complete prefab packs."""
from .common import *
from .interior import shell,slab,cushion
from .industry import gear,elbow


def hollow(profile,color='l1Ivory',sides=14,wall=.025):
    # Open lip, finite-thickness body and a closed base. No fake black hole decal.
    inner=[[max(.018,r-wall),max(.035,y)] for r,y in profile[::-1]]
    return lathe(profile+inner,color,sides,closed_profile=True)


def dish(r=.25,h=.10,color='l1Ivory'):
    return hollow([[r*.65,0],[r*.70,.025],[r,h]],color,16,wall=.025)


def tapered_box(w=.5,h=.5,d=.4,color='wood',top=.85):
    return loft([[0,0,0,w/2,d/2],[0,h,0,w*top/2,d*top/2]],color,4,rotation=[0,45,0])


def author():
    def put(g,k,n,fs,sz=(.8,.8,.8),**kw):return register('props',g,k,n,fs,sz,**kw)
    vessels=[
        ('amphora','双耳罐主体',[[.12,0],[.20,.08],[.28,.30],[.20,.5],[.095,.58],[.11,.70]]),
        ('urn','收颈瓮主体',[[.15,0],[.24,.10],[.30,.35],[.22,.53],[.19,.59]]),
        ('bottle','长颈瓶主体',[[.15,0],[.16,.06],[.16,.36],[.06,.46],[.06,.66],[.078,.68]]),
        ('carboy','大肚瓶主体',[[.18,0],[.26,.12],[.27,.35],[.19,.50],[.07,.56],[.07,.65]]),
        ('flask','扁壶主体',[[.16,0],[.24,.18],[.25,.4],[.09,.52],[.09,.61]]),
        ('jug','执壶主体',[[.16,0],[.22,.12],[.23,.37],[.13,.48],[.15,.57]]),
        ('pitcher','敞口水罐主体',[[.15,0],[.20,.12],[.19,.38],[.23,.55]]),
        ('vase','外翻花瓶主体',[[.13,0],[.16,.08],[.12,.25],[.15,.47],[.24,.62]]),
        ('bowl','深碗主体',[[.10,0],[.13,.03],[.24,.16],[.28,.28]]),
        ('goblet','高脚杯主体',[[.14,0],[.14,.03],[.035,.08],[.035,.28],[.12,.30],[.18,.46],[.19,.56]]),
        ('cup','直口杯主体',[[.12,0],[.135,.04],[.14,.28],[.145,.31]]),
        ('tea_bowl','收足茶碗主体',[[.075,0],[.075,.035],[.17,.12],[.18,.22]]),
        ('kettle','水壶主体',[[.16,0],[.23,.06],[.26,.23],[.20,.36],[.12,.40]]),
        ('cauldron','圆腹锅主体',[[.13,0],[.26,.12],[.29,.27],[.26,.40]]),
        ('pan','浅煎锅主体',[[.25,0],[.25,.025],[.3,.095]]),
        ('wok','曲面炒锅主体',[[.08,0],[.18,.06],[.3,.15],[.37,.25]]),
        ('basin','洗盆主体',[[.21,0],[.24,.04],[.32,.20],[.35,.22]]),
        ('planter','锥形花盆主体',[[.15,0],[.22,.40],[.26,.40],[.26,.46],[.22,.46]]),
        ('bucket','水桶主体',[[.16,0],[.18,.04],[.23,.4],[.24,.43]]),
        ('churn','细腰乳桶主体',[[.17,0],[.18,.1],[.16,.4],[.13,.58]]),
        ('oil_lamp','油灯储油主体',[[.13,0],[.19,.05],[.20,.15],[.12,.22],[.045,.24]]),
        ('inkwell','墨水瓶主体',[[.17,0],[.18,.06],[.15,.15],[.075,.18],[.08,.23]]),
        ('crucible','熔埚主体',[[.13,0],[.18,.08],[.20,.38],[.24,.44]]),
        ('mortar','研钵主体',[[.16,0],[.17,.03],[.23,.18],[.23,.28]])]
    for key,name,profile in vessels:
        fs=[hollow(profile,'metal' if key in ('pan','wok','cauldron','kettle','crucible') else 'l1Ivory',12 if key in ('planter','churn') else 16)]
        if key=='flask':fs=placed(fs,scale=[1,1,.5])
        if key=='pitcher':fs += [plate([[0,0],[.14,.03],[.03,.08]],.12,'l1Ivory',position=[.21,.49,0])]
        if key=='amphora':fs += [arc(.09,.018,-60,90,color='l1Ivory',n=7,center=[x,.50,0]) for x in [-.17,.17]]
        if key=='oil_lamp':fs += [round_tube(.045,.025,.20,'l1Ivory',rotation=[0,0,-60],position=[.13,.15,0])]
        if key=='crucible':fs += [formbox(.08,.09,.07,'metal',x=x,y=.32) for x in [-.23,.23]]
        if key=='mortar':fs += [formbox(.12,.06,.05,'l1Ivory',x=x,y=.2) for x in [-.23,.23]]
        put('vessel',key,name,fs,(.9,.85,.9),material='mat.metal' if key in ('pan','wok','cauldron','kettle','crucible') else 'mat.matte')
    containers=names('crate_side:木箱侧片 crate_end:木箱端片 crate_base:木箱底片 crate_lid:木箱盖片 chest_lid:拱顶箱盖片 trunk_shell:行李箱壳片 barrel_stave:桶板单片 barrel_head:木桶端板 pallet_deck:托盘面板 pallet_block:托盘垫块 basket_wall:编篮壁片 basket_base:编篮底片 hamper_lid:藤筐盖片 sack_shell:布袋外壳 pouch_shell:小囊外壳 case_foam:工具箱内衬 ammo_insert:分格盒内衬 bottle_divider:瓶箱分隔片 tote_wall:周转箱壁片 can_body:金属罐体 can_lid:拉环罐盖 tube_body:纸管筒身 tube_cap:纸管端盖 pack_shell:背囊外壳')
    for key,name in containers:
        if key in ('crate_side','crate_end'):
            fs=[formbox(.65,.10,.045,'wood',y=y) for y in [0,.13,.26,.39]]+[formbox(.065,.5,.05,'woodDark',x=x,z=-.05) for x in [-.26,.26]]
            if key=='crate_end':fs += [box([.62,.055,.035],'woodDark',[0,.25,.04],.006,rotation=[0,0,32])]
        elif key=='crate_base':fs=[formbox(.13,.05,.55,'wood',x=x) for x in [-.28,-.14,0,.14,.28]]+[formbox(.7,.05,.06,'woodDark',y=-.05,z=z) for z in [-.2,.2]]
        elif key=='crate_lid':fs=[formbox(.7,.05,.10,'wood',z=z) for z in [-.22,-.11,0,.11,.22]]+[formbox(.06,.025,.55,'metal',x=x,y=.05) for x in [-.25,.25]]
        elif key=='chest_lid':fs=[loft([[x,.15*math.sin((x+.4)/.8*math.pi),0,.045,.28] for x in [-.4,-.3,-.2,-.1,0,.1,.2,.3,.4]],'wood',4)]
        elif key=='trunk_shell':fs=shell(.7,.45,.35,True)
        elif key=='barrel_stave':fs=[loft([[0,0,0,.045,.035],[0,.35,.065,.060,.035],[0,.70,0,.045,.035]],'wood',4)]
        elif key=='barrel_head':fs=[disk(.3,.055,'wood')]+[box([.50,.02,.03],'woodDark',[0,.06,z],.004) for z in [-.14,0,.14]]
        elif key=='pallet_deck':fs=[formbox(.11,.05,.8,'wood',x=x) for x in [-.3,-.15,0,.15,.3]]+[formbox(.70,.065,.07,'woodDark',y=-.065,z=z) for z in [-.3,.3]]
        elif key=='pallet_block':fs=[formbox(.18,.12,.22,'wood'),plate([[-.09,0],[.09,0],[.05,.045],[-.05,.045]],.22,'woodDark',position=[0,.12,0])]
        elif key=='basket_wall':fs=[rod([x,0,0],[x*1.2,.5,.06],.016,'woodLight') for x in [-.24,-.16,-.08,0,.08,.16,.24]]+[rod([-.27,y,0],[.27,y,0],.014,'wood') for y in [.05,.12,.19,.26,.33,.40,.47]]
        elif key=='basket_base':fs=[rod([-.3,.018,z],[.3,.018,z],.014,'wood') for z in [-.24,-.16,-.08,0,.08,.16,.24]]+[rod([x,.04,-.3],[x,.04,.3],.014,'woodLight') for x in [-.24,-.16,-.08,0,.08,.16,.24]]
        elif key=='hamper_lid':fs=[disk(.28,.035,'woodLight'),arc(.08,.023,0,180,color='wood',center=[0,.04,0])]
        elif key=='sack_shell':fs=[loft([[0,0,0,.2,.15],[0,.15,0,.25,.2],[.02,.45,0,.18,.15],[.02,.53,0,.08,.07],[.01,.6,0,.12,.08]],'l1Ochre',8),ring(.09,.02,.035,'woodDark',position=[.02,.52,0])]
        elif key=='pouch_shell':fs=[loft([[0,0,0,.10,.05],[0,.2,0,.16,.08],[0,.3,0,.12,.04]],'woodDark',8),plate([[-.12,.3],[.12,.3],[0,.17]],.035,'wood',position=[0,0,.065])]
        elif key=='case_foam':fs=[formbox(.65,.05,.45,'l1Rubber')]+[formbox(.06,.09,.45,'rubber',x=x,y=.05) for x in [-.29,-.1,.1,.29]]
        elif key=='ammo_insert':fs=[formbox(.60,.05,.4,'l1Slate')]+[round_tube(.04,.027,.12,'l1Rubber',position=[x,.05,z]) for x in [-.22,-.11,0,.11,.22] for z in [-.11,.11]]
        elif key=='bottle_divider':fs=[formbox(.035,.3,.6,'wood',x=x) for x in [-.12,.12]]+[formbox(.6,.3,.035,'wood',z=z) for z in [-.12,.12]]
        elif key=='tote_wall':fs=frame(.65,.4,.07,.07,'l1Slate')+[formbox(.045,.25,.035,'l1Metal',x=x,y=.075) for x in [-.22,-.11,0,.11,.22]]
        elif key=='can_body':fs=[hollow([[.18,0],[.19,.03],[.18,.38],[.19,.41]],'l1Metal',16,.018)]
        elif key=='can_lid':fs=[disk(.19,.015,'l1Metal'),ring(.075,.025,.015,'metal',position=[0,.025,.04])]
        elif key=='tube_body':fs=[round_tube(.13,.11,.65,'l1Ochre',14)]
        elif key=='tube_cap':fs=[disk(.145,.02,'wood'),round_tube(.145,.132,.065,'l1Ochre')]
        else:fs=[box([.45,.6,.22],'woodDark',[0,.3,0],.08),plate([[-.2,.5],[.2,.5],[.15,.3],[-.15,.3]],.04,'wood',position=[0,0,.14])]
        put('container',key,name,fs,material='mat.wood' if key.startswith(('crate','barrel','pallet','basket','hamper')) else 'mat.matte')
    handles=names('c_loop:曲柄握把片 d_loop:D形握把片 t_bar:T形握把片 u_pull:U形拉手片 bail:提桶弓柄片 ring_pull:环形拉手片 rope:绳索握把段 wrapped:缠绕握柄片 pistol:手持工具斜柄 spade:铲柄尾握 loop_grip:剪式工具指环 crank:曲柄手轮握柄 knob:旋转旋钮帽 lever:扳杆握柄片 bar_end:车把端握 cork:软木握柄芯 bamboo:竹节握柄芯 antler:角形握柄片 chain:链节握把段 strap:提带握把片')
    for key,name in handles:
        if key=='c_loop':fs=[arc(.16,.035,-70,70,color='wood',n=10)]
        elif key=='d_loop':fs=[arc(.16,.03,-90,90,color='metal',n=10),rod([0,-.16,0],[0,.16,0],.03,'metal')]
        elif key=='t_bar':fs=[rod([0,0,0],[0,.24,0],.03,'metal'),rod([-.2,.26,0],[.2,.26,0],.055,'wood')]
        elif key=='u_pull':fs=[loft([[-.18,0,0,.025,.025],[-.18,.14,0,.032,.032],[.18,.14,0,.032,.032],[.18,0,0,.025,.025]],'metal',8)]
        elif key=='bail':fs=[arc(.27,.017,0,180,color='metal',n=14),rod([-.10,.26,0],[.10,.26,0],.032,'wood')]
        elif key=='ring_pull':fs=[ring(.12,.026,.033,'copper',rotation=[90,0,0],position=[0,.12,0]),disk(.055,.04,'copper',rotation=[90,0,0],position=[0,.25,.02])]
        elif key=='rope':fs=[loft([[.012*math.cos(j*.8+a),j*.012,.012*math.sin(j*.8+a),.013,.013] for j in range(34)],'woodLight',5) for a in [0,math.pi]]
        elif key=='wrapped':fs=[rod([0,0,0],[0,.4,0],.04,'woodDark')]+[ring(.046,.012,.018,'woodLight',position=[0,y,0]) for y in [.04,.08,.12,.16,.20,.24,.28,.32,.36]]
        elif key=='pistol':fs=[plate([[-.06,0],[.05,0],[.11,.35],[-.06,.38],[-.12,.28]],.10,'woodDark')]
        elif key=='spade':fs=[plate([[-.16,.2],[-.16,.38],[.16,.38],[.16,.2],[.11,.2],[.11,.33],[-.11,.33],[-.11,.2]],.06,'wood'),rod([0,0,0],[0,.22,0],.032,'wood')]
        elif key=='loop_grip':fs=[ring(.13,.025,.055,'l1Rubber',rotation=[90,0,0],scale=[1,.7,1]),rod([0,0,0],[0,.24,0],.025,'metal')]
        elif key=='crank':fs=[lathe([[.035,0],[.055,.06],[.06,.15],[.045,.28],[.025,.31]],'wood',10,cap=True),rod([0,-.07,0],[0,0,0],.022,'metal')]
        elif key=='knob':fs=[lathe([[.035,0],[.035,.055],[.10,.08],[.12,.13],[.10,.18]],'wood',12,cap=True)]
        elif key=='lever':fs=[rod([0,0,0],[0,.2,0],.023,'metal'),loft([[0,.2,0,.04,.03],[.025,.4,0,.06,.05],[.03,.46,0,.03,.025]],'l1Rubber',8)]
        elif key=='bar_end':fs=[round_tube(.045,.025,.28,'l1Rubber'),ring(.055,.025,.035,'metal',position=[0,.25,0])]
        elif key=='cork':fs=[lathe([[.03,0],[.045,.04],[.036,.13],[.043,.24],[.03,.31]],'l1Ochre',12,cap=True)]
        elif key=='bamboo':fs=[rod([0,0,0],[0,.45,0],.035,'woodLight')]+[ring(.043,.012,.028,'wood',position=[0,y,0]) for y in [.05,.23,.4]]
        elif key=='antler':fs=[loft([[0,0,0,.03,.04],[.06,.23,0,.05,.04],[.025,.44,.04,.025,.028]],'l1Ivory',7),rod([.04,.23,0],[-.1,.30,0],.03,'l1Ivory',r2=.007)]
        elif key=='chain':fs=[ring(.058,.016,.022,'metal',rotation=[0 if i%2 else 90,0,0],position=[0,i*.09,0],scale=[.7,1,1]) for i in range(5)]
        else:fs=[plate([[-.18,0],[-.18,.27],[.18,.27],[.18,0],[.13,0],[.13,.21],[-.13,.21],[-.13,0]],.025,'woodDark')]
        put('handle',key,name,fs,(.8,.7,.4))
    tools=names('hammer:平头锤头 claw:羊角锤头 mallet:木槌头 sledge:重锤头 pick:十字镐头 adze:锛刃头 hoe:锄刃头 shovel:平铲刃片 spade:尖铲刃片 rake:耙齿头 fork:叉齿头 trowel:泥刀刃片 chisel:凿刃片 plane:刨刀刃片 file:锉刀工作片 wrench:开口扳手头 socket:套筒头 plier:钳口单片 snip:剪切刃片 brush:刷毛头 scraper:刮片头 awl:锥头 drill:钻头工作芯 saw:手锯刃片')
    for key,name in tools:
        if key in ('hammer','sledge','mallet'):
            fs=[box([.36,.16,.16],'wood' if key=='mallet' else 'metal',[0,.08,0],.025 if key!='sledge' else .008)]
            if key=='hammer':fs += [rod([.18,.08,0],[.27,.08,0],.06,'l1Metal')]
            if key=='sledge':fs += [formbox(.06,.18,.18,'l1Metal',x=x) for x in [-.20,.20]]
            if key=='mallet':fs += [plate([[-.07,0],[.07,0],[.09,.08],[-.09,.08]],.20,'woodDark')]
        elif key=='claw':fs=[box([.22,.13,.13],'metal',[0,.07,0],.02),rod([.11,.07,0],[.21,.07,0],.075,'l1Metal')]+[loft([[-.08,.1,z,.035,.022],[-.22,.16,z,.026,.018],[-.30,.07,z,.007,.012]],'metal',5) for z in [-.035,.035]]
        elif key=='pick':fs=[loft([[-.4,0,0,.008,.01],[-.2,.13,0,.035,.04],[0,.18,0,.07,.055],[.2,.1,0,.032,.045],[.4,0,0,.007,.022]],'metal',6)]
        elif key in ('adze','hoe','scraper'):
            p={'adze':[[-.12,0],[.12,0],[.16,.3],[-.16,.3]],'hoe':[[-.22,0],[.22,0],[.18,.2],[.07,.23],[.06,.38],[-.06,.38],[-.07,.23],[-.18,.2]],'scraper':[[-.23,0],[.23,0],[.23,.08],[.045,.20],[-.045,.20],[-.23,.08]]}[key]
            fs=[plate(p,.035,'metal')]
        elif key in ('shovel','spade','trowel'):
            p={'shovel':[[-.19,0],[.19,0],[.2,.33],[.06,.42],[-.06,.42],[-.2,.33]],'spade':[[0,0],[.19,.15],[.16,.36],[.06,.4],[-.06,.4],[-.16,.36],[-.19,.15]],'trowel':[[0,0],[.14,.25],[.07,.38],[-.07,.38],[-.14,.25]]}[key]
            fs=[lens(p,'l1Metal',.016,.06),round_tube(.038,.022,.12,'metal',position=[0,.35,0])]
        elif key in ('rake','fork'):
            fs=[formbox(.46,.06,.06,'metal',y=.3)]+[rod([x,.30,0],[x,0,.08],.016,'metal',r2=.009) for x in ([-.20,-.15,-.10,-.05,0,.05,.10,.15,.20] if key=='rake' else [-.18,-.06,.06,.18])]
        elif key in ('chisel','plane','file'):
            w=.075 if key=='chisel' else .18 if key=='plane' else .095
            fs=[plate([[-w/2,0],[w/2,0],[w/2,.38],[-w/2,.38]],.025,'metal')]
            if key=='plane':fs += [formbox(.03,.15,.012,'l1Slate',y=.16,z=.02)]
            if key=='file':fs += [box([.09,.008,.009],'l1Slate',[0,y,.018],.001,rotation=[0,0,25]) for y in [.03,.07,.11,.15,.19,.23,.27,.31,.35]]
        elif key=='wrench':fs=[plate([[-.04,0],[.04,0],[.06,.19],[.15,.23],[.16,.36],[.07,.39],[.075,.28],[-.02,.26],[-.075,.35],[-.13,.3],[-.1,.2],[-.04,.17]],.055,'l1Metal')]
        elif key=='socket':fs=[round_tube(.10,.062,.19,'l1Metal',6),round_tube(.08,.04,.12,'metal',8,position=[0,.19,0])]
        elif key in ('plier','snip'):
            p=[[-.03,0],[.07,.02],[.12,.20],[.035,.37],[-.025,.36],[.045,.20],[-.035,.10]] if key=='plier' else [[-.04,0],[.04,0],[.12,.45],[.04,.4],[-.04,.18]]
            fs=[plate(p,.04,'l1Metal')]
        elif key=='brush':fs=[formbox(.25,.08,.09,'wood')]+[rod([x,.08,z],[x,.26,z],.008,'l1Ivory',sides=4) for x in [-.1,-.05,0,.05,.1] for z in [-.026,0,.026]]
        elif key=='awl':fs=[loft([[0,0,0,.006,.006],[0,.32,0,.022,.022],[0,.4,0,.03,.03]],'metal',6)]
        elif key=='drill':fs=[rod([0,0,0],[0,.45,0],.024,'metal')]+[loft([[.028*math.cos(j*.35+a),j*.012,.028*math.sin(j*.35+a),.012,.008] for j in range(30)],'l1Metal',4) for a in [0,math.pi]]
        else:fs=[plate([[-.26,.02]]+[[x,.02 if i%2 else 0] for i,x in enumerate([-.24+j*.025 for j in range(20)])]+[[.26,.08],[-.23,.24]],.014,'metal')]
        put('toolhead',key,name,fs,(1,.7,.5),material='mat.metal')
    fasteners=names('hex_bolt:六角螺栓头 carriage:圆头方颈螺栓翼 wing_nut:蝶形螺母 flange_nut:法兰螺母 lock_nut:自锁螺母 eye_bolt:环眼螺栓 clevis_pin:叉销体 cotter:开口销片 rivet:铆钉头 wood_screw:木螺钉头 washer_flat:平垫圈 washer_spring:开口弹垫 circlip:卡簧片 staple:U形钉片 nail:圆钉头 nail_square:方钉头 hook:挂钩片 buckle:扣环芯 clasp:搭扣片 toggle:绳扣芯')
    for key,name in fasteners:
        if key in ('hex_bolt','carriage','rivet','nail','nail_square','wood_screw'):
            fs=[rod([0,0,0],[0,.25,0],.025 if key not in ('nail','nail_square') else .014,'metal',sides=4 if key=='nail_square' else 8)]
            if key=='hex_bolt':fs += [lathe([[.055,.23],[.055,.29]],'l1Metal',6,cap=True)]
            elif key=='carriage':fs += [formbox(.07,.045,.07,'metal',y=.22),ico([.13,.055,.13],'l1Metal',[0,.275,0],detail=1)]
            elif key=='rivet':fs += [ico([.095,.055,.095],'l1Metal',[0,.26,0],detail=1)]
            elif key=='wood_screw':fs += [lathe([[.025,.21],[.055,.265],[.055,.28]],'metal',10,cap=True),formbox(.065,.006,.009,'l1Slate',y=.28)]
            else:fs += [disk(.031,.013,'metal',y=.24)]
        elif key in ('wing_nut','flange_nut','lock_nut'):
            fs=[round_tube(.06,.028,.07,'metal',6)]
            if key=='wing_nut':fs += [plate([[x*.04,.025],[x*.13,.10],[x*.12,.15],[x*.04,.07]],.024,'l1Metal') for x in [-1,1]]
            elif key=='flange_nut':fs += [ring(.085,.056,.017,'l1Metal')]
            else:fs += [ring(.065,.037,.028,'l1Rubber',position=[0,.08,0])]
        elif key=='eye_bolt':fs=[rod([0,0,0],[0,.18,0],.024,'metal'),ring(.075,.022,.028,'l1Metal',rotation=[90,0,0],position=[0,.25,0])]
        elif key=='clevis_pin':fs=[rod([0,0,0],[0,.28,0],.035,'metal'),disk(.055,.02,'l1Metal',y=.26),round_tube(.020,.009,.08,'metal',rotation=[90,0,0],position=[0,.035,.04])]
        elif key=='cotter':fs=[arc(.033,.011,0,210,color='l1Metal',n=8,center=[0,.25,0]),rod([-.025,.24,0],[-.015,0,0],.011,'metal'),rod([.025,.24,0],[.045,.01,0],.011,'metal')]
        elif key=='washer_flat':fs=[ring(.08,.035,.018,'l1Metal')]
        elif key=='washer_spring':fs=[loft([[.062*math.cos(i*math.tau/18),i*.0013,.062*math.sin(i*math.tau/18),.013,.013] for i in range(18)],'metal',4)]
        elif key=='circlip':fs=[]
        elif key=='staple':fs=[loft([[-.07,0,0,.012,.012],[-.07,.2,0,.014,.014],[.07,.2,0,.014,.014],[.07,0,0,.012,.012]],'metal',6)]
        elif key=='hook':fs=[rod([0,0,0],[0,.18,0],.024,'metal'),arc(.09,.024,0,260,color='l1Metal',center=[.09,.18,0],n=12)]
        elif key=='buckle':fs=frame(.22,.18,.026,.028,'copper')+[rod([0,.025,.025],[0,.16,.025],.012,'copper')]
        elif key=='clasp':fs=[formbox(.16,.20,.025,'metal'),ring(.042,.014,.025,'l1Metal',rotation=[90,0,0],position=[0,.11,.03])]
        else:fs=[loft([[-.15,0,0,.026,.024],[0,.02,0,.045,.035],[.15,0,0,.026,.024]],'wood',8),round_tube(.022,.01,.08,'woodDark',rotation=[90,0,0],position=[0,.02,.04])]
        if key=='circlip':fs=[arc(.09,.014,20,340,color='metal',n=15)]+[round_tube(.021,.009,.018,'l1Metal',rotation=[90,0,0],position=[.08,y,.01]) for y in [-.036,.036]]
        put('fastener',key,name,fs,(.45,.4,.35),material='mat.metal')
    signs=names('arrow:方向箭头底板 round:圆形标牌底板 octagon:八角标牌底板 shield:盾形标牌底板 pennant:三角旗牌底板 scroll:卷边告示底板 plaque:铭牌底板 hanging:悬挂牌底板 blade:街道刀牌底板 milestone:里程标芯 banner:布旗主体 chalkboard:黑板内芯 notice:公告板内芯 bracket:标牌悬臂片 flag_finial:旗杆顶饰 neon_channel:灯带字槽段')
    for key,name in signs:
        if key=='arrow':fs=[plate([[-.35,0],[.10,0],[.1,-.10],[.35,.15],[.1,.4],[.1,.3],[-.35,.3]],.045,'wood')]
        elif key in ('round','octagon'):fs=[disk(.28,.045,'l1Ivory',rotation=[90,0,0]) if key=='round' else lathe([[.28,0],[.28,.045]],'l1Slate',8,cap=True,rotation=[90,0,0])]
        elif key=='shield':fs=[plate([[0,0],[.27,.2],[.27,.55],[-.27,.55],[-.27,.2]],.045,'wood')]
        elif key=='pennant':fs=[plate([[-.3,0],[.3,.23],[-.3,.46]],.025,'l1Terracotta')]
        elif key=='scroll':fs=[formbox(.5,.4,.025,'l1Ivory')]+[rod([-.28,y,0],[.28,y,0],.035,'wood') for y in [0,.4]]
        elif key=='plaque':fs=[box([.55,.3,.045],'copper',[0,.15,0],.05)]+[disk(.012,.007,'metal',rotation=[90,0,0],position=[x,.15,.027]) for x in [-.22,.22]]
        elif key=='hanging':fs=[plate([[-.3,0],[.3,0],[.35,.24],[.28,.38],[-.28,.38],[-.35,.24]],.05,'wood')]+[ring(.028,.01,.014,'metal',rotation=[90,0,0],position=[x,.40,0]) for x in [-.20,.20]]
        elif key=='blade':fs=[plate([[-.4,0],[.36,0],[.43,.1],[.36,.2],[-.4,.2]],.025,'l1Slate'),formbox(.055,.20,.05,'metal',x=-.34)]
        elif key=='milestone':fs=[plate([[-.15,0],[.15,0],[.15,.5],[.1,.59],[-.1,.59],[-.15,.5]],.14,'stone')]
        elif key=='banner':fs=[lens([[-.25,.55],[.25,.55],[.25,0],[0,.12],[-.25,0]],'l1Terracotta',.012,.04)]
        elif key=='chalkboard':fs=[formbox(.50,.40,.03,'ink')]+frame(.57,.47,.035,.035,'wood')
        elif key=='notice':fs=[formbox(.6,.5,.035,'l1Ochre')]+[formbox(.16,.21,.008,'l1Ivory',x=x,y=y,z=.025) for x,y in [(-.13,.18),(.12,.06)]]
        elif key=='bracket':fs=[rod([0,0,0],[0,.55,0],.025,'metal'),rod([0,.5,0],[.5,.5,0],.025,'metal'),rod([0,.12,0],[.4,.5,0],.018,'metal')]
        elif key=='flag_finial':fs=[loft([[0,0,0,.045,.045],[0,.10,0,.10,.07],[0,.3,0,.008,.008]],'copper',6)]
        else:fs=[plate([[-.3,0],[.3,0],[.3,.08],[.27,.08],[.27,.027],[-.27,.027],[-.27,.08],[-.3,.08]],.1,'metal')]
        put('sign',key,name,fs)
    lamps=names('conical_shade:圆锥灯罩 bell_shade:钟形灯罩 drum_shade:鼓形灯罩 dome_shade:穹顶灯罩 lantern_frame:提灯骨框 cage:防护灯笼架 reflector:反光碗芯 diffuser:散光罩芯 bulb:灯泡玻壳 socket:灯泡螺口座 wick:油灯灯芯夹 chimney:油灯烟囱罩 candle_cup:烛托杯芯 sconce_arm:壁灯支臂 lamp_base:台灯底座 spot_yoke:射灯俯仰架')
    for key,name in lamps:
        if key in ('conical_shade','bell_shade','drum_shade','dome_shade'):
            p={'conical_shade':[[.28,0],[.12,.36]],'bell_shade':[[.3,0],[.23,.09],[.14,.30],[.15,.39]],'drum_shade':[[.23,0],[.23,.38]],'dome_shade':[[.28,0],[.27,.12],[.20,.25],[.06,.31]]}[key]
            fs=[hollow(p,'l1Ivory',16,.018)]
        elif key=='lantern_frame':fs=[rod([x,0,z],[x,.5,z],.022,'metal') for x in [-.16,.16] for z in [-.16,.16]]+[formbox(.36,.04,.36,'l1Slate',y=y) for y in [0,.48]]
        elif key=='cage':fs=[ring(.20,.018,.028,'metal',position=[0,y,0]) for y in [0,.4]]+[rod([.19*math.cos(a),0,.19*math.sin(a)],[.19*math.cos(a),.4,.19*math.sin(a)],.015,'metal') for a in [i*math.tau/8 for i in range(8)]]
        elif key=='reflector':fs=[hollow([[.05,0],[.12,.08],[.26,.20]],'l1Metal',16,.015)]
        elif key=='diffuser':fs=[loft([[0,0,0,.23,.23],[0,.14,0,.19,.19],[0,.22,0,.06,.06]],'l1Ivory',16)]
        elif key=='bulb':fs=[loft([[0,0,0,.045,.045],[0,.10,0,.075,.075],[0,.19,0,.11,.11],[0,.29,0,.065,.065],[0,.31,0,.015,.015]],'l1Ivory',12)]
        elif key=='socket':fs=[round_tube(.085,.059,.13,'l1Ivory'),ring(.073,.015,.02,'copper',position=[0,.03,0]),ring(.073,.015,.02,'copper',position=[0,.07,0])]
        elif key=='wick':fs=[round_tube(.065,.033,.12,'copper'),formbox(.11,.025,.07,'metal',y=.12),formbox(.025,.065,.035,'woodDark',y=.14)]
        elif key=='chimney':fs=[hollow([[.09,0],[.13,.12],[.12,.25],[.07,.36],[.07,.48]],'glass',14,.012)]
        elif key=='candle_cup':fs=[dish(.14,.055,'copper'),rod([0,.035,0],[0,.12,0],.018,'metal',r2=.004)]
        elif key=='sconce_arm':fs=[loft([[0,0,0,.028,.028],[.15,0,0,.028,.028],[.3,.2,0,.028,.028],[.3,.3,0,.025,.025]],'copper',8),disk(.10,.04,'copper',y=.3,position=[.3,0,0])]
        elif key=='lamp_base':fs=[lathe([[.23,0],[.25,.045],[.16,.1],[.065,.15]],'l1Slate',16,cap=True)]
        else:fs=[plate([[-.22,.3],[-.22,0],[.22,0],[.22,.3],[.16,.3],[.16,.06],[-.16,.06],[-.16,.3]],.09,'l1Slate')]
        put('lamp',key,name,fs)
    office=names('book_cover:书本封皮片 book_block:书页块 book_spine:书脊片 scroll_core:卷轴纸芯 paper_stack:纸张叠片 folder:文件夹壳 clipboard:写字板芯 clip:纸夹片 binder_ring:活页环件 pen_barrel:笔杆壳 pen_nib:钢笔尖片 pencil_core:铅笔芯杆 eraser:橡皮芯 ruler:尺规板片 stamp:印章底芯 inkpad:印台内芯 tape_spool:胶带卷芯 stapler_base:订书机底片 scissors_loop:文具剪指环 magnifier:放大镜镜框')
    for key,name in office:
        if key=='book_cover':fs=[formbox(.4,.015,.52,'woodDark',y=y) for y in [0,.08]]+[formbox(.02,.095,.52,'woodDark',x=-.20)]
        elif key=='book_block':fs=[formbox(.37,.07,.49,'l1Ivory')]+[formbox(.375,.003,.49,'cream',y=y) for y in [.014,.028,.042,.056]]
        elif key=='book_spine':fs=[loft([[0,0,-.25,.018,.02],[0,.012,0,.06,.025],[0,0,.25,.018,.02]],'woodDark',6)]
        elif key=='scroll_core':fs=[round_tube(.08,.03,.48,'l1Ivory',16,rotation=[0,0,90],position=[.24,.08,0])]
        elif key=='paper_stack':fs=[box([.40,.012,.54],'l1Ivory',[0,i*.013,0],.002,rotation=[0,(i%3-1)*2,0]) for i in range(5)]
        elif key=='folder':fs=[formbox(.42,.013,.55,'l1Ochre'),formbox(.12,.014,.06,'l1Ochre',x=.12,z=-.30),formbox(.42,.013,.55,'woodLight',y=.026)]
        elif key=='clipboard':fs=[formbox(.40,.022,.56,'wood'),formbox(.17,.04,.055,'metal',y=.022,z=-.22)]
        elif key=='clip':fs=[loft([[-.035,0,0,.005,.005],[-.035,.18,0,.005,.005],[.035,.18,0,.005,.005],[.035,.025,0,.005,.005],[-.015,.025,0,.005,.005],[-.015,.14,0,.005,.005]],'metal',6)]
        elif key=='binder_ring':fs=[arc(.09,.012,5,355,color='metal',n=16),formbox(.13,.025,.035,'l1Slate',y=-.03)]
        elif key=='pen_barrel':fs=[round_tube(.019,.012,.30,'l1Slate',12),ring(.023,.011,.025,'copper',position=[0,.25,0])]
        elif key=='pen_nib':fs=[plate([[-.015,0],[.015,0],[.04,.09],[0,.20],[-.04,.09]],.008,'copper')]
        elif key=='pencil_core':fs=[lathe([[.018,0],[.018,.28],[.002,.35]],'woodLight',6,cap=True),rod([0,.325,0],[0,.355,0],.004,'ink',r2=.001,sides=5)]
        elif key=='eraser':fs=[box([.13,.045,.08],'l1Ivory',[0,.025,0],.018)]
        elif key=='ruler':fs=[formbox(.50,.012,.065,'woodLight')]+[formbox(.004,.003,.02 if i%5 else .038,'ink',x=-.23+i*.02,y=.012,z=.015) for i in range(24)]
        elif key=='stamp':fs=[formbox(.20,.055,.15,'wood'),formbox(.18,.015,.13,'l1Rubber',y=-.015),lathe([[.04,.055],[.028,.12],[.055,.2],[.025,.25]],'woodDark',10,cap=True)]
        elif key=='inkpad':fs=[formbox(.24,.025,.17,'l1Slate'),formbox(.20,.018,.13,'ink',y=.025)]
        elif key=='tape_spool':fs=[round_tube(.115,.067,.06,'l1Ochre',16),ring(.12,.022,.008,'l1Ivory')]
        elif key=='stapler_base':fs=[plate([[-.08,0],[.08,0],[.075,.30],[-.075,.30]],.04,'l1Slate',rotation=[90,0,0]),formbox(.075,.012,.045,'metal',y=.025,z=-.20)]
        elif key=='scissors_loop':fs=[ring(.06,.014,.022,'l1Rubber',rotation=[90,0,0],scale=[1,1.3,1]),rod([0,.05,0],[0,.16,0],.012,'metal')]
        else:fs=[ring(.15,.024,.024,'metal',rotation=[90,0,0]),rod([0,-.13,0],[0,-.35,0],.03,'woodDark')]
        put('office',key,name,fs,(.8,.6,.8))
    foods=names('bread:面包主体 baguette:长棍面包主体 bun:圆包主体 loaf_slice:面包切片芯 pie_shell:派皮主体 tart_shell:挞皮主体 dumpling:饺子面皮主体 pasta:弯管面主体 sausage:香肠段 cheese_wedge:奶酪楔块 cheese_wheel:奶酪轮芯 fish_fillet:鱼肉片芯 steak:肉排主体 egg_shell:蛋壳主体 cone:甜筒壳芯 scoop:冰淇淋球芯 cake_layer:蛋糕胚层 cookie:饼干主体 chocolate:巧克力块芯 sushi_rice:寿司饭团芯')
    for key,name in foods:
        if key=='bread':fs=[loft([[0,0,0,.24,.14],[0,.10,0,.29,.18],[0,.23,0,.20,.12]],'woodLight',10)]+[box([.035,.018,.20],'cream',[x,.22,0],.005,rotation=[0,0,12]) for x in [-.12,0,.12]]
        elif key=='baguette':fs=[loft([[-.4,0,0,.03,.03],[-.28,.03,0,.08,.09],[.28,.03,0,.08,.09],[.4,0,0,.025,.025]],'woodLight',8)]+[box([.025,.017,.12],'cream',[x,.10,0],.006,rotation=[0,20,0]) for x in [-.23,-.08,.08,.23]]
        elif key=='bun':fs=[lathe([[.16,0],[.20,.05],[.18,.14],[.10,.22],[.02,.24]],'woodLight',12,cap=True)]+[ico([.016,.01,.012],'cream',[x,.225,z],detail=0) for x,z in [(-.03,0),(.03,0),(0,.03),(0,-.03)]]
        elif key=='loaf_slice':fs=[plate([[-.16,0],[.16,0],[.16,.17],[.20,.23],[.15,.30],[-.15,.30],[-.20,.23],[-.16,.17]],.05,'l1Ivory')]
        elif key in ('pie_shell','tart_shell'):fs=[hollow([[.2,0],[.23,.025],[.28,.10 if key=='pie_shell' else .07]],'woodLight',16,.024)];fs += [ico([.045,.025,.035],'woodLight',[.27*math.cos(a),.1 if key=='pie_shell' else .07,.27*math.sin(a)],detail=0) for a in [i*math.tau/(12 if key=='pie_shell' else 18) for i in range(12 if key=='pie_shell' else 18)]]
        elif key=='dumpling':fs=[loft([[-.18,0,0,.022,.02],[-.1,.09,0,.085,.05],[.1,.09,0,.085,.05],[.18,0,0,.022,.02]],'l1Ivory',8)]+[rod([x,.15,0],[x+.02,.19,0],.012,'cream') for x in [-.1,-.05,0,.05,.1]]
        elif key=='pasta':fs=[elbow(.075,.035,.019,120)];fs[0]['color']=C('cream')
        elif key=='sausage':fs=[loft([[-.23,0,0,.025,.025],[-.15,.04,0,.065,.065],[.14,.05,0,.065,.065],[.23,0,0,.02,.02]],'l1Terracotta',10)]
        elif key=='cheese_wedge':fs=[plate([[0,0],[.33,0],[.23,.20]],.20,'cream',rotation=[90,0,0])]+[ico([.035,.007,.035],'l1Ochre',[x,.108,z],detail=1) for x,z in [(.18,-.08),(.25,-.04)]]
        elif key=='cheese_wheel':fs=[disk(.22,.12,'cream'),ring(.224,.014,.12,'l1Ochre',position=[0,.06,0])]
        elif key=='fish_fillet':fs=[lens([[-.22,0],[-.12,.25],[0,.48],[.15,.23],[.13,0]],'l1Petal',.045,.02)]+[rod([-.11,y,.044],[.07,y+.015,.05],.004,'cream',sides=4) for y in [.08,.14,.20,.26]]
        elif key=='steak':fs=[plate([[-.2,0],[.14,-.02],[.27,.13],[.18,.33],[-.12,.38],[-.24,.18]],.10,'l1Terracotta'),plate([[-.14,.05],[.12,.02],[.20,.15],[.12,.29],[-.10,.31],[-.18,.18]],.013,'l1Petal',position=[0,0,.06])]
        elif key=='egg_shell':fs=[loft([[0,0,0,.03,.03],[0,.045,0,.10,.10],[0,.13,0,.10,.10],[0,.24,0,.055,.055],[0,.27,0,.01,.01]],'l1Ivory',12)]
        elif key=='cone':fs=[hollow([[.01,0],[.15,.38]],'woodLight',12,.015)]
        elif key=='scoop':fs=[ico([.30,.26,.30],'l1Petal',[0,.14,0],detail=1)]+[ico([.065,.045,.065],'l1Petal',[.13*math.cos(a),.04,.13*math.sin(a)],detail=0) for a in [i*math.tau/7 for i in range(7)]]
        elif key=='cake_layer':fs=[disk(.26,.14,'woodLight'),disk(.265,.022,'l1Ivory',y=.14)]
        elif key=='cookie':fs=[lathe([[.13,0],[.16,.025],[.14,.06]],'woodLight',12,cap=True)]+[ico([.035,.012,.025],'woodDark',[x,.056,z],detail=0) for x,z in [(-.06,-.03),(.04,.06),(.08,-.04),(-.05,.07)]]
        elif key=='chocolate':fs=[formbox(.30,.018,.23,'woodDark')]+[box([.085,.027,.09],'hair',[x,.03,z],.01) for x in [-.1,0,.1] for z in [-.057,.057]]
        else:fs=[box([.20,.13,.32],'l1Ivory',[0,.065,0],.055)]+[ico([.022,.012,.018],'cream',[x,.127,z],detail=0) for x,z in [(-.04,-.07),(.04,.03),(-.03,.09),(.035,-.065)]]
        put('food',key,name,fs,collision='none')
    medical=names('vial:药瓶主体 ampoule:安瓿主体 syringe_barrel:注射器筒壳 plunger:注射器活塞片 needle_hub:针座护帽 pill:药片芯 capsule:药囊壳 bandage_roll:绷带卷芯 gauze:纱布叠片 splint:夹板片 forceps:镊片 stethoscope:听诊头芯 thermometer:温度计护壳 tray:医疗托盘壳 mask:防护口罩片 crutch_pad:拐杖腋托芯')
    for key,name in medical:
        if key=='vial':fs=[hollow([[.07,0],[.08,.03],[.08,.2],[.04,.24],[.055,.26]],'glass',12,.012)]
        elif key=='ampoule':fs=[loft([[0,0,0,.045,.045],[0,.15,0,.05,.05],[0,.23,0,.02,.02],[0,.3,0,.024,.024],[0,.34,0,.007,.007]],'glass',12)]
        elif key=='syringe_barrel':fs=[round_tube(.033,.023,.28,'l1Ivory'),formbox(.12,.014,.04,'metal',y=.26),round_tube(.012,.006,.05,'l1Ivory',position=[0,-.05,0])]
        elif key=='plunger':fs=[rod([0,0,0],[0,.35,0],.012,'l1Ivory'),disk(.027,.022,'l1Rubber'),disk(.055,.013,'l1Ivory',y=.34)]
        elif key=='needle_hub':fs=[lathe([[.025,0],[.022,.08],[.014,.10],[.007,.10],[.013,.07],[.015,0]],'l1Slate',10,closed_profile=True)]
        elif key=='pill':fs=[lathe([[.07,0],[.09,.015],[.09,.035],[.07,.05]],'l1Ivory',12,cap=True),formbox(.12,.003,.006,'cream',y=.05)]
        elif key=='capsule':fs=[loft([[0,0,0,.02,.02],[0,.04,0,.045,.045],[0,.15,0,.045,.045],[0,.20,0,.02,.02]],'l1Ivory',12),ring(.046,.006,.014,'l1Slate',position=[0,.10,0])]
        elif key=='bandage_roll':fs=[round_tube(.105,.04,.11,'l1Ivory',16),formbox(.16,.01,.105,'cream',x=.14)]
        elif key=='gauze':fs=[box([.22,.018,.22],'l1Ivory',[0,i*.019,0],.006,rotation=[0,i%2*5,0]) for i in range(4)]
        elif key=='splint':fs=[plate([[-.05,0],[.05,0],[.07,.1],[.05,.48],[-.05,.48],[-.07,.1]],.025,'woodLight'),formbox(.14,.04,.012,'l1Ivory',y=.10,z=.02),formbox(.14,.04,.012,'l1Ivory',y=.34,z=.02)]
        elif key=='forceps':fs=[plate([[-.018,0],[.018,0],[.038,.25],[.015,.40],[0,.42],[.014,.24]],.008,'l1Metal')]
        elif key=='stethoscope':fs=[disk(.07,.025,'l1Metal'),ring(.074,.011,.019,'l1Rubber',position=[0,.012,0]),rod([0,.025,0],[.06,.10,0],.015,'metal')]
        elif key=='thermometer':fs=[plate([[-.027,0],[.027,0],[.038,.07],[.038,.35],[-.038,.35],[-.038,.07]],.025,'l1Ivory'),formbox(.013,.20,.008,'l1Slate',y=.08,z=.02)]
        elif key=='tray':fs=[formbox(.5,.018,.32,'l1Metal')]+[formbox(.015,.062,.32,'l1Metal',x=x,y=.018) for x in [-.2425,.2425]]+[formbox(.47,.062,.015,'l1Metal',z=z,y=.018) for z in [-.1525,.1525]]
        elif key=='mask':fs=[loft([[0,0,0,.07,.025],[0,.10,.05,.14,.055],[0,.20,0,.12,.022]],'l1Ivory',8)]+[rod([-.1,y,.042],[.1,y,.042],.007,'cream') for y in [.055,.105,.15]]
        else:fs=cushion(.32,.085,.10)+[box([.26,.028,.07],'wood',[0,-.014,0],.01)]
        put('medical',key,name,fs,(.7,.7,.6))
    merch=names('box_sleeve:包装纸套片 carton_fold:折叠纸盒坯 blister:吸塑罩片 label_tag:商品吊牌芯 hang_tab:悬挂扣片 bottle_cap:瓶盖芯 cork:瓶塞芯 pump:压泵头 spray:喷雾按头 nozzle:挤出尖嘴 sachet:封袋外壳 tube:软管外壳 jar_lid:广口罐盖 seal_band:封口环片 spool:线轴芯 reel:盘带轴芯')
    for key,name in merch:
        if key=='box_sleeve':fs=[formbox(.4,.014,.3,'l1Ochre',y=y) for y in [0,.25]]+[formbox(.014,.25,.3,'l1Ochre',x=x) for x in [-.193,.193]]
        elif key=='carton_fold':fs=[formbox(.28,.018,.28,'l1Ochre')]+[formbox(.28,.12,.015,'l1Ochre',z=z) for z in [-.147,.147]]+[formbox(.015,.12,.28,'l1Ochre',x=x) for x in [-.147,.147]]
        elif key=='blister':fs=[box([.24,.16,.20],'glass',[0,.08,0],.04),formbox(.34,.008,.30,'l1Ivory')]
        elif key=='label_tag':fs=[plate([[-.07,0],[.07,0],[.07,.18],[.035,.23],[-.035,.23],[-.07,.18]],.008,'l1Ivory'),ring(.012,.004,.007,'copper',rotation=[90,0,0],position=[0,.19,.008])]
        elif key=='hang_tab':fs=[plate([[-.08,0],[.08,0],[.08,.12],[.04,.16],[-.04,.16],[-.08,.12]],.012,'l1Slate'),ring(.035,.012,.015,'metal',rotation=[90,0,0],position=[0,.09,.012])]
        elif key=='bottle_cap':fs=[hollow([[.063,0],[.063,.055],[.057,.065]],'l1Slate',16,.012)];fs=placed(fs,[0,.065,0],[180,0,0])
        elif key=='cork':fs=[lathe([[.035,0],[.04,.11],[.045,.12]],'l1Ochre',12,cap=True)]
        elif key=='pump':fs=[rod([0,0,0],[0,.15,0],.022,'l1Ivory'),formbox(.18,.045,.055,'l1Ivory',x=.045,y=.15),round_tube(.008,.004,.045,'l1Slate',position=[.11,.13,0])]
        elif key=='spray':fs=[lathe([[.05,0],[.05,.10],[.03,.13]],'l1Slate',12,cap=True),round_tube(.014,.007,.03,'metal',rotation=[90,0,0],position=[0,.075,.055])]
        elif key=='nozzle':fs=[lathe([[.06,0],[.06,.025],[.018,.2],[.010,.2],[.045,.025],[.045,0]],'l1Ivory',10,closed_profile=True)]
        elif key=='sachet':fs=[box([.24,.34,.055],'l1Ivory',[0,.17,0],.025),formbox(.24,.025,.026,'l1Slate',y=.315),formbox(.24,.025,.026,'l1Slate')]
        elif key=='tube':fs=[loft([[0,0,0,.09,.015],[0,.08,0,.08,.05],[0,.3,0,.075,.05],[0,.38,0,.025,.023]],'l1Ivory',8),round_tube(.027,.014,.045,'l1Slate',position=[0,.38,0])]
        elif key=='jar_lid':fs=[disk(.145,.022,'l1Slate'),round_tube(.145,.129,.05,'l1Slate',position=[0,-.05,0])]
        elif key=='seal_band':fs=[ring(.09,.010,.04,'l1Ochre'),plate([[0,0],[.035,0],[.05,.07],[.012,.07]],.012,'l1Ochre',position=[.085,0,0])]
        elif key=='spool':fs=[round_tube(.085,.035,.22,'woodLight')]+[ring(.14,.105,.022,'wood',position=[0,y,0]) for y in [0,.22]]
        else:fs=[round_tube(.12,.055,.1,'l1Slate')]+[gear(6,.26,.018, .055)]
        put('merch',key,name,fs,(.7,.65,.7))
    narratives=names('seal_stamp:纹章印面芯 wax_seal:蜡封坯 key_blank:古钥匙坯 compass_case:罗盘壳芯 watch_case:怀表壳芯 locket:坠盒半壳 medallion:圆章坯 scroll_rod:卷轴端杆 chess_pawn:棋子兵坯 chess_rook:棋子城坯 chess_knight:棋子马坯 chess_bishop:棋子象坯 dice:骰子坯 hourglass_cup:沙漏容腔壳 treasure_corner:宝箱包角 relic_shard:遗物断片')
    for key,name in narratives:
        if key=='seal_stamp':fs=[disk(.14,.08,'copper'),formbox(.18,.028,.04,'metal',y=.08),formbox(.04,.028,.18,'metal',y=.08)]
        elif key=='wax_seal':fs=[loft([[0,0,0,.13,.13],[0,.025,0,.16,.15],[0,.055,0,.10,.11]],'l1Terracotta',9),ring(.09,.011,.009,'woodLight',position=[0,.057,0])]
        elif key=='key_blank':fs=[ring(.10,.035,.035,'copper',rotation=[90,0,0],position=[0,.38,0]),rod([0,0,0],[0,.3,0],.022,'copper'),formbox(.13,.025,.035,'copper',x=.045)]
        elif key=='compass_case':fs=[dish(.19,.07,'copper'),round_tube(.01,.005,.055,'metal',position=[0,.025,0])]
        elif key=='watch_case':fs=[dish(.14,.06,'copper'),ring(.035,.01,.025,'metal',position=[0,.04,.17])]
        elif key=='locket':fs=[dish(.12,.05,'copper')];fs=placed(fs,scale=[.75,1,1.1]);fs += [round_tube(.016,.007,.09,'copper',rotation=[0,0,90],position=[.045,.025,.12])]
        elif key=='medallion':fs=[lathe([[.16,0],[.17,.015],[.16,.03]],'copper',12,cap=True),ring(.025,.009,.013,'metal',position=[0,0,.19])]
        elif key=='scroll_rod':fs=[rod([-.30,0,0],[.30,0,0],.026,'wood')]+[ico([.07,.085,.085],'copper',[x,0,0],detail=1) for x in [-.31,.31]]
        elif key.startswith('chess_'):
            fs=[lathe([[.10,0],[.115,.025],[.085,.06],[.045,.15]],'l1Ivory',12,cap=True)]
            if key=='chess_pawn':fs += [ico([.13,.13,.13],'l1Ivory',[0,.21,0],detail=1)]
            elif key=='chess_rook':fs += [disk(.08,.12,'l1Ivory',y=.15)]+[formbox(.035,.045,.035,'l1Ivory',x=.068*math.cos(a),y=.27,z=.068*math.sin(a)) for a in [0,math.pi/2,math.pi,math.pi*1.5]]
            elif key=='chess_knight':fs += [plate([[-.055,.14],[.06,.14],[.08,.27],[.14,.28],[.12,.35],[.02,.40],[-.05,.32]],.085,'l1Ivory')]
            else:fs += [loft([[0,.14,0,.045,.045],[0,.22,0,.07,.065],[.02,.32,0,.014,.018]],'l1Ivory',8),rod([-.045,.255,.03],[.03,.29,.035],.008,'woodDark')]
        elif key=='dice':fs=[box([.18,.18,.18],'l1Ivory',[0,.09,0],.02)]+[disk(.012,.003,'ink',y=.182,position=[x,0,z]) for x,z in [(-.045,-.045),(.045,.045),(0,0)]]
        elif key=='hourglass_cup':fs=[hollow([[.02,0],[.025,.05],[.14,.30],[.14,.38]],'glass',14,.012)]
        elif key=='treasure_corner':fs=[formbox(.18,.025,.18,'copper'),formbox(.025,.18,.18,'copper',x=-.077),formbox(.18,.18,.025,'copper',z=-.077)]
        else:fs=[plate([[-.10,0],[.18,.04],[.12,.19],[.17,.23],[-.02,.36],[-.16,.25]],.08,'stone'),rod([-.06,.08,.045],[.07,.23,.045],.012,'l1Ochre')]
        put('narrative',key,name,fs,(.8,.7,.65))
    musical=names('drum_shell:鼓腔壳 cymbal:铙钹片 bell:钟罩壳 lute_body:鲁特琴音箱片 violin_plate:提琴面板片 guitar_neck:吉他琴颈芯 flute_tube:笛管芯 horn_bell:号口芯 reed:簧片芯 mouthpiece:吹口芯 peg:调音弦轴 bridge:琴桥芯')
    for key,name in musical:
        if key=='drum_shell':fs=[round_tube(.25,.225,.35,'wood',16),ring(.26,.03,.035,'metal'),ring(.26,.03,.035,'metal',position=[0,.35,0])]
        elif key=='cymbal':fs=[lathe([[.04,0],[.08,.045],[.14,.01],[.34,-.025],[.34,-.008],[.14,.028],[.08,.065],[.04,.018]],'copper',20,closed_profile=True)]
        elif key=='bell':fs=[hollow([[.29,0],[.22,.11],[.16,.3],[.10,.4]],'copper',16,.025),ring(.05,.014,.03,'metal',rotation=[90,0,0],position=[0,.43,0])]
        elif key=='lute_body':fs=[loft([[0,0,0,.04,.04],[0,.17,0,.23,.1],[0,.40,0,.20,.08],[0,.58,0,.045,.025]],'wood',12)]
        elif key=='violin_plate':fs=[lens([[-.08,0],[.13,.02],[.18,.15],[.12,.22],[.06,.24],[.12,.33],[.14,.44],[.05,.5],[-.09,.49],[-.15,.4],[-.1,.29],[-.06,.25],[-.14,.19],[-.17,.1]],'woodLight',.028,.02)]
        elif key=='guitar_neck':fs=[formbox(.07,.55,.045,'woodDark'),plate([[-.035,0],[.055,0],[.07,.18],[-.045,.18]],.035,'wood',position=[0,.53,0])]+[formbox(.075,.005,.01,'metal',y=y,z=.027) for y in [.05,.13,.21,.29,.37,.45]]
        elif key=='flute_tube':fs=[round_tube(.038,.025,.55,'wood',14)]+[disk(.009,.005,'ink',rotation=[90,0,0],position=[0,y,.040]) for y in [.12,.19,.26,.33,.4]]
        elif key=='horn_bell':fs=[lathe([[.025,0],[.05,.2],[.13,.36],[.25,.45],[.25,.47],[.12,.38],[.035,.2],[.012,0]],'copper',16,closed_profile=True)]
        elif key=='reed':fs=[plate([[-.018,0],[.018,0],[.025,.20],[.02,.27],[-.02,.27],[-.025,.20]],.006,'woodLight')]
        elif key=='mouthpiece':fs=[lathe([[.015,0],[.019,.15],[.05,.20],[.07,.22],[.07,.24],[.045,.22],[.009,.15],[.006,0]],'l1Metal',12,closed_profile=True)]
        elif key=='peg':fs=[rod([0,0,0],[0,.16,0],.02,'woodDark'),ico([.10,.07,.035],'woodDark',[0,.20,0],detail=1)]
        else:fs=[plate([[-.12,0],[-.08,0],[-.05,.035],[.05,.035],[.08,0],[.12,0],[.11,.14],[-.11,.14]],.03,'woodLight')]
        put('musical',key,name,fs,(.9,.9,.9))
    devices=names('screen_bezel:显示器前框 keyboard_plate:键盘底板 camera_shell:相机机身壳 lens_barrel:镜头筒壳 radio_grille:收音机网罩 speaker_cone:扬声器纸盆 phone_shell:电话听筒壳 control_knob:设备旋钮芯')
    for key,name in devices:
        if key=='screen_bezel':fs=frame(.7,.45,.055,.04,'l1Slate')
        elif key=='keyboard_plate':fs=[formbox(.62,.035,.23,'l1Slate')]+[formbox(.035,.018,.035,'l1Ivory',x=-.25+i*.055,y=.035,z=-.08+j*.05) for i in range(10) for j in range(4)]
        elif key=='camera_shell':fs=[box([.35,.23,.16],'l1Slate',[0,.115,0],.035),formbox(.10,.06,.12,'metal',x=-.09,y=.23),round_tube(.09,.064,.07,'metal',rotation=[90,0,0],position=[.04,.115,.115])]
        elif key=='lens_barrel':fs=[round_tube(.12,.092,.25,'l1Slate',16)]+[ring(.128,.025,.027,'metal',position=[0,y,0]) for y in [.04,.20]]
        elif key=='radio_grille':fs=frame(.40,.22,.026,.025,'l1Slate')+[formbox(.014,.17,.012,'metal',x=x,y=.025) for x in [-.16,-.12,-.08,-.04,0,.04,.08,.12,.16]]
        elif key=='speaker_cone':fs=[lathe([[.23,0],[.20,.035],[.07,.11],[.045,.10],[.06,.095],[.20,.02]],'l1Rubber',16,closed_profile=True),ico([.12,.075,.12],'rubber',[0,.105,0],detail=1)]
        elif key=='phone_shell':fs=[loft([[-.24,0,0,.075,.075],[-.14,.08,0,.055,.05],[.14,.08,0,.055,.05],[.24,0,0,.075,.075]],'l1Slate',8)]
        else:fs=[lathe([[.085,0],[.10,.02],[.10,.085],[.075,.11]],'l1Slate',12,cap=True),formbox(.012,.006,.05,'l1Ivory',y=.112,z=.035)]
        put('device',key,name,fs)
    finish('props',252)
