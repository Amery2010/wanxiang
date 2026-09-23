"""Fitted equipment and occupational rigs on the existing stitched human skeleton.

Twenty-four real shape families; eight complete characters share skin/animation,
not independent colour-only anatomy copies. Cloth is rigid stylised geometry.
"""
from .production import *
D='characters'
def p(k,n,f,s,**kw):return dp('wear.'+k,n,'wear',f,s,D,theme='adventure',anchor='center',**kw)
def a(k,n,items,**kw):return da('wear-'+k,n,'wear',items,D,theme='adventure',**kw)
def ip(k):return 'exp.wear.'+k
def ia(k):return 'exp-wear-'+k
GRIP=lambda:[socket('grip',[0,0,0],[0,0,-1],'character.hand.grip.v1',span=.04)]
BACK=lambda:[socket('mount',[0,0,0],[0,0,1],'character.back.mount.v1',span=.22)]

def author():
    collar=[poly([[-.06,.20,.135],[-.15,.25,.035],[-.12,.10,.19],[-.025,.15,.175]],[[0,1,2,3]],'linen'),poly([[.06,.20,.135],[.15,.25,.035],[.12,.10,.19],[.025,.15,.175]],[[3,2,1,0]],'linen'),formbox(.027,.33,.018,'linen',y=-.14,z=.176),*[disk(.009,.009,'productionBrass',[0,y,.190],6,rotation=[90,0,0]) for y in [-.09,.0,.09]]]
    p('collar','衬衫领襟 · 翻领与纽扣',collar,[.32,.46,.20],material='mat.fabric')
    coat=[box([.44,.56,.065],'indigo',[0,-.12,-.159],bevel=.035),*[profile([[sg*.145,-.64,.035,.112,.14],[sg*.13,-.20,.02,.105,.148],[sg*.147,.19,.006,.095,.133]],'indigo') for sg in [-1,1]],*[box([.13,.09,.025],'linen',[sg*.14,-.28,.181],bevel=.012) for sg in [-1,1]],rod([-.16,.14,.16],[-.09,.05,.19],.024,'linen'),rod([.16,.14,.16],[.09,.05,.19],.024,'linen')]
    p('winter_coat','分片长风衣 · 开襟与侧摆',coat,[.54,.88,.40],material='mat.fabric',description='胸骨刚性挂载；分片前摆留出腿部活动空间，不宣称布料模拟。')
    padded=[profile([[0,-.27,0,.21,.151],[0,.02,0,.253,.174],[0,.19,-.005,.23,.15]],'safety'),*[box([.43,.021,.011],'charcoal',[0,y,.185],bevel=.003) for y in [-.19,-.08,.04]],formbox(.025,.45,.012,'charcoal',y=-.26,z=.194),*[box([.17,.044,.019],'line',[sg*.14,-.11,.195],bevel=.007) for sg in [-1,1]]]
    p('rescue_jacket','救援防护夹克 · 加厚领肩与反光带',padded,[.55,.48,.41],material='mat.fabric')
    robe=[*[profile([[sg*.175,-.95,.015,.165,.205],[sg*.125,-.40,0,.13,.16],[sg*.125,.17,0,.125,.14]],'indigo') for sg in [-1,1]],profile([[0,-.92,-.10,.26,.10],[0,-.21,-.13,.20,.085],[0,.16,-.09,.22,.09]],'indigo'),*[rod([sg*.044,.16,.153],[sg*.08,-.82,.20],.013,'productionBrass',sides=6) for sg in [-1,1]],box([.45,.06,.035],'woodDark',[0,-.23,.177],bevel=.013)]
    p('robe','施法长袍 · 分叉下摆与织边',robe,[.71,1.16,.48],material='mat.fabric')
    p('leather_armor','皮甲胸背 · 层叠肩片与束带',[profile([[0,-.27,0,.20,.145],[0,.08,0,.24,.17],[0,.19,-.01,.205,.13]],'woodDark'),box([.33,.22,.035],'oak',[0,.015,.181],bevel=.045),*[box([.12,.10,.075],'wood',[sg*.18,-.25,.168],bevel=.018) for sg in [-1,1]],*[beam([sg*.16,.19,.12],[sg*.20,-.22,.17],.038,.015,'woodLight') for sg in [-1,1]]],[.51,.52,.45],material='mat.leather')
    plate=[profile([[0,-.25,0,.185,.141],[0,-.08,.015,.225,.178],[0,.10,0,.248,.176],[0,.19,-.015,.218,.134]],'metal'),box([.026,.32,.017],'productionBrass',[0,-.012,.202],bevel=.007),*[profile([[sg*.17,-.32,.03,.105,.145],[sg*.17,-.23,.02,.12,.152]],'steel') for sg in [-1,1]],*[box([.21,.10,.28],'metal',[sg*.29,.175,0],bevel=.035,rotation=[0,0,sg*-12]) for sg in [-1,1]]]
    p('plate_armor','板甲胸甲 · 护肩／胸脊／腰甲',plate,[.83,.58,.43],material='mat.metal',params=schema(detail=DETAIL),lod=authored_lod())
    PARTS[ip('plate_armor')]['shape_params']['forms'][1]['enabled']=Q('detail')
    firehat=[lathe([[.158,.005],[.17,.07],[.15,.18],[.095,.235],[.015,.25]],'safety',14,cap=True),box([.40,.026,.44],'safety',[0,.015,-.037],bevel=.04),formbox(.055,.095,.018,'productionBrass',y=.052,z=.175),box([.035,.035,.32],'safety',[0,.205,-.025],bevel=.011),*[rod([sg*.136,.01,0],[sg*.11,-.16,.065],.009,'charcoal') for sg in [-1,1]]]
    p('fire_helmet','消防头盔 · 长后檐与束带',firehat,[.40,.43,.44],material='mat.paint')
    helmet=[lathe([[.148,-.04],[.167,.03],[.154,.15],[.08,.222],[.025,.225]],'linen',14,cap=True),*[disk(.045,.045,'charcoal',[sg*.163,-.025,-.006],12,rotation=[0,0,90]) for sg in [-1,1]],box([.265,.075,.045],'glass',[0,.04,.143],bevel=.025,material='mat.vehicleGlass'),tube([[.17,-.035,.018],[.16,-.095,.11],[.045,-.10,.17]],.009,'steel',6)]
    p('pilot_helmet','飞行头盔 · 耳机与通话麦克风',helmet,[.39,.35,.36],material='mat.paint')
    hood=[extrude([[-.175,-.14],[.175,-.14],[.196,.1],[.10,.253],[-.10,.253],[-.196,.1]],.09,'pine',holes=[[[-.115,-.09],[.115,-.09],[.129,.105],[.06,.187],[-.06,.187],[-.129,.105]]],position=[0,0,.095]),profile([[0,-.125,-.09,.163,.08],[0,.11,-.085,.163,.115],[0,.242,-.074,.067,.053]],'pine')]
    p('hood','游侠兜帽 · 真实面部开口',hood,[.42,.42,.34],material='mat.fabric')
    p('wizard_hat','弯尖法师帽 · 连续偏心帽冠',[lathe([[.32,.042],[.34,.065],[.15,.09],[.14,.13]],'indigo',14,cap=True),loft([[0,.09,0,.15,.14],[0,.25,0,.125,.12],[.03,.44,-.012,.085,.08],[.08,.59,.0,.038,.035],[.14,.60,.015,.008,.008]],'indigo',10),ring(.155,.018,.055,'productionBrass',position=[0,.124,0])],[.7,.62,.7],material='mat.fabric')
    longhair=[profile([[0,.09,-.025,.143,.12],[0,.18,-.03,.113,.10],[0,.225,-.025,.040,.040]],'hair'),*[loft([[sg*.115,.12,-.065,.066,.067],[sg*.17,-.10,-.05,.067,.085],[sg*.135,-.38,-.04,.05,.06]],'hair',8) for sg in [-1,1]],profile([[0,.08,-.09,.13,.067],[0,-.25,-.125,.15,.073],[0,-.40,-.09,.13,.045]],'hair')]
    p('long_hair','肩长发 · 发帽与两侧发束',longhair,[.5,.65,.32],material='mat.hair')
    braid=[profile([[0,.085,-.025,.14,.12],[0,.17,-.025,.12,.10],[0,.219,-.03,.044,.04]],'hairLight')]
    for sg in [-1,1]:braid += [ico([.063,.086,.067],'hairLight',[sg*(.13+.012*math.sin(j*2)),.07-j*.065,.04],detail=0,distort=0) for j in range(7)]
    p('braids','双辫发型 · 收束编织轮廓',braid,[.35,.60,.28],material='mat.hair')
    shield=[extrude([[-.24,.27],[.24,.27],[.28,.10],[.17,-.27],[0,-.40],[-.17,-.27],[-.28,.1]],.065,'wood',position=[0,0,.025]),*[beam([x,.22,.068],[x,-.18,.068],.012,.015,'woodDark') for x in [-.14,0,.14]],ico([.19,.19,.085],'metal',[0,.025,.095],distort=0),tube([[-.11,.13,-.025],[-.11,-.06,-.07],[.11,-.06,-.07],[.11,.13,-.025]],.018,'woodDark',8)]
    p('shield','风筝盾 · 木板／盾脐／手带',shield,[.58,.70,.23],ports=GRIP(),material='mat.wood',collision={'type':'convex-hull','source':'shield plate'})
    blade=topo([[-.036,.10,0],[.036,.10,0],[.033,.70,0],[0,.91,0],[-.033,.70,0],[0,.13,.018],[0,.13,-.018],[0,.70,.012],[0,.70,-.012]],[[0,5,7,4],[5,1,2,7],[4,7,3],[7,2,3],[0,4,8,6],[6,8,2,1],[4,3,8],[8,3,2],[0,6,1,5]],'metal')
    p('sword','短剑道具 · 菱形刀身与护手',[blade,rod([0,-.18,0],[0,.10,0],.026,'woodDark'),beam([-.14,.10,0],[.14,.10,0],.036,.035,'productionBrass'),ico([.072,.055,.062],'productionBrass',[0,-.20,0],detail=0,distort=0)],[.32,1.16,.075],ports=GRIP(),material='mat.metal')
    p('axe','单刃斧道具 · 楔刃与握柄',[rod([0,-.44,0],[0,.32,0],.024,'wood'),extrude([[-.04,.15],[.14,.18],[.25,.09],[.25,.38],[.09,.33],[-.04,.33]],.050,'metal'),rod([0,-.40,0],[0,-.12,0],.028,'woodDark')],[.30,.90,.07],ports=GRIP(),material='mat.wood')
    p('spear','长矛道具 · 叶形矛尖与箍口',[rod([0,-.83,0],[0,.72,0],.02,'oak'),extrude([[-.047,.70],[-.057,.81],[0,1.05],[.057,.81],[.047,.70]],.016,'metal'),ring(.030,.011,.085,'productionBrass',position=[0,.71,0])],[.13,1.90,.065],ports=GRIP(),material='mat.wood')
    staff=[loft([[0,-.81,0,.023,.023],[.014,.1,.01,.025,.025],[-.015,.65,0,.040,.04],[.05,.84,0,.070,.06]],'woodDark',8),ico([.14,.22,.12],'cyan',[.05,.86,.018],detail=0,distort=0,material='mat.emissive.cyan'),*[rod([.05+sg*.065,.71,0],[.05+sg*.085,.96,0],.019,'productionBrass',r2=.007) for sg in [-1,1]]]
    p('staff','法杖道具 · 木杖与晶体支架',staff,[.24,1.85,.16],ports=GRIP(),material='mat.wood')
    book=[formbox(.30,.39,.036,'indigo',y=-.20,z=-.057),formbox(.30,.39,.036,'indigo',y=-.20,z=.057),formbox(.265,.35,.085,'linen',y=-.18),formbox(.034,.39,.13,'woodDark',x=-.142,y=-.20),*[formbox(.047,.046,.013,'productionBrass',x=x,y=y,z=.080) for x in [-.11,.11] for y in [-.17,.12]],ring(.063,.012,.011,'productionBrass',position=[0,0,.084],rotation=[90,0,0])]
    p('grimoire','魔法书 · 装帧／书脊／页块',book,[.32,.42,.19],ports=GRIP(),material='mat.leather')
    lantern=[formbox(.18,.04,.18,'steel',y=-.25),formbox(.19,.035,.19,'steel',y=.03),*[rod([x,-.21,z],[x,.03,z],.01,'productionBrass') for x in [-.075,.075] for z in [-.075,.075]],box([.125,.20,.125],'glass',[0,-.10,0],bevel=.01,material='mat.glass'),lathe([[.014,-.21],[.014,-.03],[.006,-.005]],'yellow',8,cap=True,material='mat.emissive.amber'),tube([[-.068,.048,0],[-.063,.16,0],[.063,.16,0],[.068,.048,0]],.009,'productionBrass',8)]
    p('lantern','提灯 · 镂空框架与玻璃灯罩',lantern,[.2,.43,.20],ports=GRIP(),material='mat.metal')
    pack=[box([.31,.45,.10],'charcoal',[0,0,-.06],bevel=.032),*[lathe([[.057,-.23],[.078,-.18],[.078,.20],[.052,.25]],'yellow',12,cap=True,position=[x,0,-.14]) for x in [-.09,.09]],*[rod([x,.22,-.14],[x,.30,-.14],.013,'steel') for x in [-.09,.09]],tube([[.12,.28,-.14],[.24,.18,-.11],[.27,-.14,.01],[.20,-.24,.10]],.014,'charcoal',8)]
    p('breathing_pack','呼吸器背架 · 双气瓶与供气管',pack,[.52,.57,.34],ports=BACK(),material='mat.paint')
    p('medic_bag','医疗挎包 · 折盖与肩带',[box([.32,.26,.14],'medical',[0,-.15,0],bevel=.04),box([.33,.12,.035],'linen',[0,-.075,.076],bevel=.014),*[formbox(.04,.025,.018,'productionBrass',x=x,y=-.19,z=.090) for x in [-.11,.11]],tube([[-.13,-.04,0],[-.09,.21,0],[.12,.21,0],[.14,-.04,0]],.013,'woodDark',8),formbox(.085,.025,.015,'pine',y=-.08,z=.10),formbox(.025,.085,.015,'pine',y=-.11,z=.10)],[.36,.5,.20],ports=GRIP(),material='mat.fabric')
    p('radio','便携无线电 · 旋钮／天线／侧夹',[box([.087,.17,.054],'charcoal',[0,-.035,0],bevel=.012),rod([-.03,.046,0],[-.03,.25,0],.004,'charcoal',sides=6),formbox(.054,.040,.006,'cyan',y=-.028,z=.029,material='mat.display'),*[formbox(.055,.006,.007,'steel',y=-.074+i*.012,z=.031) for i in range(3)],disk(.010,.025,'steel',[.026,.064,0],8)],[.10,.39,.07],ports=GRIP(),material='mat.paint')
    p('tool_case','硬壳工具箱 · 侧锁扣与嵌入提手',[box([.40,.28,.19],'safety',[0,-.17,0],bevel=.034),*[box([.036,.07,.023],'steel',[x,-.08,.102],bevel=.005) for x in [-.145,.145]],tube([[-.071,-.018,0],[-.065,.062,0],[.065,.062,0],[.071,-.018,0]],.016,'charcoal',8),*[formbox(.025,.18,.012,'charcoal',x=x,y=-.27,z=.10) for x in [-.09,0,.09]]],[.43,.4,.23],ports=GRIP(),material='mat.paint')
    bow=[loft([[0,-.54,0,.015,.02],[.105,-.29,0,.024,.025],[.14,0,0,.027,.027],[.105,.29,0,.024,.025],[0,.54,0,.015,.02]],'wood',8),rod([0,-.54,0],[0,.54,0],.003,'linen',sides=4),rod([.14,-.085,0],[.14,.085,0],.031,'woodDark',sides=8),lathe([[.053,-.48],[.075,-.38],[.080,.09],[.067,.11],[.059,-.37],[.04,-.45]],'woodDark',10,closed_profile=True,position=[-.19,0,0]),*[rod([-.19+x,-.25,0],[-.19+x,.36,0],.005,'oak',sides=5) for x in [-.04,0,.04]]]
    p('archery','长弓与箭袋 · 张弦及开放袋口',bow,[.43,1.14,.18],ports=BACK(),material='mat.wood')
    # Sixteen functional equipment kits are displayed as separated inspection layouts.
    kits=[
      ('uniform','制服领襟与通讯挂载',[('collar',[0,.08,0]),('radio',[.27,0,.18])]),
      ('winter','冬装与照明套件',[('winter_coat',[0,.65,0]),('lantern',[.48,.12,0])]),
      ('fire','消防防护套件',[('rescue_jacket',[0,.20,0]),('fire_helmet',[0,.60,0]),('breathing_pack',[0,.2,-.27])]),
      ('rescue','急救随行套件',[('medic_bag',[-.25,.2,0]),('radio',[.10,.16,0]),('tool_case',[.47,.2,0])]),
      ('pilot','飞行防护套件',[('pilot_helmet',[0,.50,0]),('collar',[0,.15,0]),('radio',[.28,.1,0])]),
      ('ranger','游侠防护套件',[('leather_armor',[0,.25,0]),('hood',[0,.62,0]),('archery',[-.44,.40,0])]),
      ('mage','法师长袍套件',[('robe',[0,1,0]),('wizard_hat',[0,1.36,0]),('grimoire',[.5,.40,0])]),
      ('guard','守卫甲具套件',[('plate_armor',[0,.35,0]),('shield',[.55,.4,0])]),
      ('traveller','旅行整备套件',[('winter_coat',[0,.65,0]),('tool_case',[.55,.15,0]),('lantern',[-.45,.22,0])]),
      ('melee','近战道具检视架',[('sword',[-.45,.36,0]),('axe',[0,.54,0]),('spear',[.45,.84,0])]),
      ('shield_loadout','盾剑组合 · 分离握持原点',[('shield',[-.32,.43,0]),('sword',[.34,.25,0])]),
      ('archer_loadout','远程装备组合',[('archery',[-.17,.55,0]),('leather_armor',[.44,.36,0])]),
      ('wayfarer','引路杖与悬灯',[('staff',[0,.83,0]),('lantern',[.29,1.37,0])]),
      ('librarian','书卷与随身包',[('grimoire',[.23,.32,0]),('medic_bag',[-.20,.23,0])]),
      ('hair_caps','肩发与双辫 · 两种独立轮廓检视',[('long_hair',[-.28,.43,0]),('braids',[.28,.43,0])]),
      ('field_tools','野外工具装备',[('axe',[-.34,.47,0]),('tool_case',[.27,.32,0]),('radio',[.59,.22,0])])]
    for key,name,items in kits:
        a(key,name,[pi('item'+str(i),ip(k),pos) for i,(k,pos) in enumerate(items)],metadata={'purpose':'equipment inspection / inventory layout','mounting':'Use individual part grip/back sockets when attaching to a skeleton.'})
    # Rigged characters: unique fitted equipment, inherited walk/idle clips and feet.
    roles=[
      ('firefighter','消防员','rescue_jacket','fire_helmet','axe','breathing_pack',1.86,1.12,'safety','charcoal'),
      ('paramedic','急救人员','collar',None,'medic_bag','radio',1.75,1.00,'medical','indigo'),
      ('miner','矿工','leather_armor',None,'tool_case','radio',1.78,1.16,'wood','charcoal'),
      ('pilot','飞行员','collar','pilot_helmet','radio',None,1.82,1.00,'indigo','navy'),
      ('guard','中世纪守卫','plate_armor',None,'sword',None,1.89,1.12,'steel','woodDark'),
      ('ranger','荒野游侠','leather_armor','hood','spear','archery',1.80,.97,'pine','woodDark'),
      ('wizard','秘术法师','robe','wizard_hat','staff','grimoire',1.90,.98,'indigo','indigo'),
      ('merchant','旅行商人','winter_coat',None,'lantern','tool_case',1.72,1.12,'linen','woodDark')]
    for key,name,outfit,hat,tool,back,height,body,shirt,trousers in roles:
        H=div(Q('height'),1.82);B=Q('build')
        items=[pi('skin','core.human.body',params={'height':Q('height'),'build':B,'grip':True,'palette':{C('cream'):C(shirt),C('moss'):C(trousers),C('white'):C(shirt)}}),
               pi('head','core.human.head',parent='skin.rig.head',scale=[H,H,H],params={'jaw_width':1.03 if key in ['miner','guard'] else .97}),
               pi('outfit',ip(outfit),parent='skin.rig.chest',scale=[B,H,B]),
               pi('tool',ip(tool),parent='skin.rig.handR',pos=[0,-.015,.027],rot=[0,0,-8])]
        if hat:items.append(pi('hat',ip(hat),pos=[0,.017,0],parent='skin.rig.head',scale=[H,H,H]))
        else:items.append(pi('hair',ip('braids' if key=='paramedic' else 'long_hair') if key in ['paramedic','merchant'] else 'core.human.hair.short',parent='skin.rig.head',scale=[H,H,H]))
        if key=='miner':items.append(pi('helmet','w.wear.hardhat',parent='skin.rig.head',scale=[H,H,H]))
        if key=='guard':items.append(pi('shield',ip('shield'),parent='skin.rig.handL',rot=[0,10,0]))
        if back:
            items.append(pi('back',ip(back),pos=[0,0,-.22] if back not in ['radio','grimoire'] else [-.20,-.10,.18],parent='skin.rig.chest',scale=[B,H,B],rot=[0,180,0] if back=='tool_case' else None))
        ident=da('character-'+key,name,'body',items,D,theme='adventure',level=3,
            params=schema(height=number(height,1.64,1.98,'身高',.01,'m'),build=number(body,.92,1.18,'体格')),
            metadata={'skeleton':'core.human.body shared stitched rig','garment_simulation':'rigid bone attachments; no cloth simulation','inventory_kits':[ia(kits[j][0]) for j in range(len(kits)) if j%8==roles.index((key,name,outfit,hat,tool,back,height,body,shirt,trousers))]},
            collision={'type':'capsule','radius':.29,'segment_start':[0,.29,0],'segment_end':[0,sub(Q('height'),.29),0]})
        mo=deepcopy(MOTIONS['fnd-adult']);mo['assembly']=ident;MOTIONS[ident]=mo
    finish_counts(D)
