"""Creature anatomy and reusable articulated rigs, not random blob scatter.

Rigid anatomical hinges and weighted serpentine/skeletal rigs are explicit. Motion
clips are inspection loops, not navigation, foot locking or physics controllers.
"""
from .production import *
D='creatures'
def p(k,n,f,s,**kw):return dp('creature.'+k,n,kw.pop('category','animal'),f,s,D,theme='wildlife',**kw)
def a(k,n,items,**kw):return da('creature-'+k,n,kw.pop('category','animal'),items,D,theme='wildlife',**kw)
def ip(k):return 'exp.creature.'+k
def ia(k):return 'exp-creature-'+k

def author():
    torso=[loft([[0,.02,-.90,.30,.36],[0,.08,-.55,.43,.50],[0,.07,.18,.48,.54],[0,.19,.63,.43,.57],[0,.23,.94,.24,.30]],'woodDark',12,frame_axis=[0,0,1]),ico([.68,.38,.68],'woodDark',[0,.40,.48],distort=0)]
    p('mammal_torso','重型哺乳动物躯干 · 胸肩与腰腹',torso,[1.0,1.20,1.92],anchor='center',material='mat.fur',collision={'type':'capsule','radius':.45,'segment_start':[0,0,-.55],'segment_end':[0,.1,.60]})
    head=[loft([[0,.04,-.24,.23,.25],[0,.06,-.06,.30,.29],[0,-.015,.19,.24,.19],[0,-.04,.40,.13,.105]],'woodDark',12,frame_axis=[0,0,1]),ico([.23,.12,.12],'charcoal',[0,-.02,.43],distort=0),*[ico([.18,.20,.09],'woodDark',[s*.23,.28,-.09],distort=0) for s in [-1,1]],*[ico([.075,.050,.042],'ink',[s*.23,.10,.19],distort=0) for s in [-1,1]],*[ico([.018,.018,.018],'linen',[s*.235,.113,.212],detail=0,distort=0) for s in [-1,1]]]
    p('bear_head','熊科头部 · 额骨／短吻／圆耳',head,[.69,.60,.80],anchor='hinge',material='mat.fur')
    paw=[loft([[0,0,0,.15,.17],[0,-.21,.035,.13,.15],[0,-.49,.075,.09,.11],[0,-.68,.13,.13,.15]],'woodDark',10),ico([.32,.16,.38],'woodDark',[0,-.68,.18],distort=0),*[rod([x,-.70,.31],[x,-.73,.39],.021,'bone',r2=.007,sides=6) for x in [-.11,-.037,.037,.11]]]
    p('plantigrade_leg','跖行动物腿足 · 踝与趾爪',paw,[.38,.84,.47],anchor='hinge',material='mat.fur',collision={'type':'capsule','radius':.13,'segment_start':[0,-.12,0],'segment_end':[0,-.62,.12]})
    elephant=[loft([[0,0,-.25,.31,.37],[0,.11,-.08,.42,.43],[0,.07,.30,.30,.31],[0,-.04,.42,.18,.22]],'stone',12,frame_axis=[0,0,1]),loft([[0,.02,.4,.16,.16],[0,-.30,.54,.13,.13],[0,-.65,.59,.10,.10],[0,-.86,.72,.067,.067],[0,-.84,.87,.036,.036]],'stone',10),*[ico([.14,.78,.61],'stone',[s*.43,.02,-.05],distort=0) for s in [-1,1]],*[loft([[s*.22,-.18,.29,.036,.036],[s*.26,-.32,.59,.026,.026],[s*.29,-.24,.82,.008,.008]],'bone',8) for s in [-1,1]],*[ico([.055,.047,.039],'ink',[s*.302,.16,.311],distort=0) for s in [-1,1]]]
    p('elephant_head','象头颈 · 厚耳／弯鼻／双牙',elephant,[1.06,1.38,1.26],anchor='hinge',material='mat.skin')
    elephantleg=[profile([[0,0,0,.22,.21],[.015,-.43,0,.19,.19],[.0,-.90,.01,.20,.20],[0,-1.08,.04,.235,.24]],'stone'),*[ico([.095,.10,.05],'linen',[x,-1.055,.24],detail=0,distort=0) for x in [-.14,0,.14]]]
    p('elephant_leg','象腿 · 柱状承重与趾甲',elephantleg,[.50,1.15,.55],anchor='hinge',material='mat.skin',collision={'type':'capsule','radius':.22,'segment_start':[0,-.20,0],'segment_end':[0,-.90,.01]})
    bird=[loft([[0,.05,-.46,.09,.08],[0,.03,-.18,.19,.21],[0,.05,.14,.24,.28],[0,.16,.38,.12,.16]],'woodDark',10,frame_axis=[0,0,1]),loft([[0,.12,.12,.14,.18],[0,.03,-.12,.14,.15],[0,-.04,-.29,.06,.07]],'linen',8,frame_axis=[0,0,-1]),*[extrude([[-.03,0],[.03,0],[.052,-.36],[-.025,-.40]],.012,'woodDark',rotation=[80,0,i*5],position=[i*.04,0,-.40]) for i in [-2,-1,0,1,2]]]
    p('avian_torso','鸟类躯干 · 胸腹与尾羽根',bird,[.52,.57,1.04],anchor='center',category='bird',material='mat.fur')
    wing=[loft([[0,0,0,.12,.12],[.35,.03,-.08,.13,.10],[.65,.01,-.24,.09,.065],[.96,-.02,-.42,.025,.025]],'woodDark',8,frame_axis=[1,0,0])]
    for i in range(8):
        x=.17+i*.11;z=-.1-i*.035
        wing.append(extrude([[0,0],[.11,.025],[.11,-.26-i*.022],[.055,-.36-i*.022],[0,-.25-i*.022]],.018,'linen' if i>4 else 'wood',rotation=[90,0,0],position=[x,-.018,z]))
    p('feather_wing','羽翼 · 肱骨轮廓与独立飞羽',wing,[1.12,.28,.95],anchor='hinge',category='bird',material='mat.fur',params=schema(detail=DETAIL),lod=authored_lod())
    PARTS[ip('feather_wing')]['shape_params']['forms'][2::2]=optional(PARTS[ip('feather_wing')]['shape_params']['forms'][2::2])
    p('raptor_head','猛禽头部 · 钩喙与眉弓',[ico([.30,.32,.34],'linen',[0,.04,.02],distort=0),extrude([[-.09,.09],[.055,.085],[.13,.0],[.115,-.07],[.071,-.09],[.071,-.025],[-.09,-.045]],.09,'productionBrass',rotation=[0,90,0],position=[0,.02,.20]),*[ico([.047,.042,.025],'ink',[s*.134,.080,.12],distort=0) for s in [-1,1]],*[beam([s*.11,.111,.067],[s*.14,.106,.14],.035,.02,'linen') for s in [-1,1]]],[.33,.36,.43],anchor='hinge',category='bird',material='mat.fur')
    claws=[rod([0,0,0],[0,-.19,.02],.018,'productionBrass')]
    for x in [-.055,0,.055]:claws += [tube([[0,-.18,.02],[x,-.22,.12],[x,-.24,.19]],.01,'productionBrass',6),rod([x,-.24,.19],[x,-.265,.205],.008,'charcoal',r2=.002,sides=5)]
    claws += [tube([[0,-.18,0],[0,-.22,-.07],[0,-.26,-.11]],.012,'productionBrass',6)]
    p('talon','鸟爪 · 三前一后握持趾',claws,[.15,.29,.34],anchor='hinge',category='bird',material='mat.hoof')
    reptile=[loft([[0,.0,-1.06,.08,.065],[0,.08,-.64,.29,.16],[0,.09,.1,.41,.21],[0,.09,.68,.31,.17],[0,.08,1,.20,.12]],'pine',10,frame_axis=[0,0,1]),loft([[0,0,-.98,.08,.07],[0,-.025,-1.55,.065,.05],[.16,-.025,-2,.022,.024]],'pine',8,frame_axis=[0,0,-1])]
    reptile += [ico([.10,.11,.14],'leafDark',[s*.12,.24-i*.004,.65-i*.19],detail=0,distort=0) for s in [-1,1] for i in range(9)]
    p('reptile_torso','爬行动物躯干 · 低伏胸腹与尾根',reptile,[.88,.50,3.1],anchor='center',material='mat.skin',params=schema(detail=DETAIL),lod=authored_lod(),collision={'type':'capsule','radius':.32,'segment_start':[0,0,-.6],'segment_end':[0,0,.68]})
    PARTS[ip('reptile_torso')]['shape_params']['forms'][2:]=optional(PARTS[ip('reptile_torso')]['shape_params']['forms'][2:])
    croc=[loft([[0,.045,-.2,.22,.14],[0,.06,.05,.26,.16],[0,.015,.47,.19,.095],[0,0,.90,.12,.07]],'pine',10,frame_axis=[0,0,1]),box([.32,.05,.69],'woodLight',[0,-.083,.46],bevel=.022),*[ico([.07,.045,.05],'yellow',[s*.185,.162,.12],distort=0) for s in [-1,1]],*[ico([.020,.045,.028],'ink',[s*.187,.174,.145],distort=0) for s in [-1,1]],*[rod([s*(.18-.04*i),-.035,.26+i*.18],[s*(.18-.04*i),-.09,.26+i*.18],.015,'bone',r2=.003,sides=5) for s in [-1,1] for i in range(3)]]
    p('reptile_head','鳄形头部 · 扁长吻／眼脊／闭口齿',croc,[.56,.38,1.16],anchor='hinge',material='mat.skin')
    limb=[loft([[0,0,0,.095,.10],[.22,-.06,.07,.09,.10],[.32,-.24,.12,.04,.046],[.42,-.27,.21,.06,.05]],'pine',8),*[tube([[.38,-.26,.17],[.46+j*.012,-.29,.20+j*.04],[.57+j*.015,-.29,.23+j*.04]],.012,'pine',6) for j in [-1,0,1]]]
    p('reptile_leg','外展爬行肢 · 肘踝与分趾',limb,[.67,.37,.38],anchor='hinge',material='mat.skin')
    centers=[[.12*math.sin(j*.72),.12,-1.5+j*.27] for j in range(13)]
    rig=[{'name':'spine'+str(i),'position':centers[i*3],**({'parent':'spine'+str(i-1)} if i else {})} for i in range(5)]
    rings=[]
    for j,c in enumerate(centers):
        b=min(j//3,4);nx=min(b+1,4);mix=(j%3)/3
        rings.append({'c':c,'r':[.09*(.35+min(j,4)/4*.65),.072*(.35+min(j,4)/4*.65)],'weights':{'spine'+str(b):1-mix,'spine'+str(nx):mix} if b!=nx else None,'bone':'spine'+str(b)})
        if rings[-1]['weights'] is None:del rings[-1]['weights']
    snake=[loft(rings,'moss',10,frame_axis=[0,0,1]),ico([.23,.15,.32],'moss',[*centers[-1][:2],centers[-1][2]+.09],distort=0,bone='spine4'),*[ico([.025,.022,.028],'ink',[centers[-1][0]+s*.085,.16,centers[-1][2]+.15],distort=0,bone='spine4') for s in [-1,1]]]
    p('serpent','蛇形脊柱 · 五骨权重连续表面',snake,[.55,.25,3.75],category='animal',material='mat.skin',rig=rig,collision={'type':'capsule','radius':.11,'segment_start':[0,.12,-1.4],'segment_end':[0,.12,1.8]})
    shark=[loft([[0,0,-1.52,.07,.09],[0,.02,-.6,.26,.32],[0,.03,.25,.39,.41],[0,.025,.97,.31,.31],[0,0,1.52,.10,.14]],'steel',12,frame_axis=[0,0,1]),loft([[0,-.13,-.78,.14,.06],[0,-.23,.2,.30,.13],[0,-.12,1.22,.17,.06]],'linen',10,frame_axis=[0,0,1]),extrude([[-.48,0],[.17,0],[-.08,.70],[-.2,.70]],.047,'steel',rotation=[0,90,0],position=[0,.34,-.20]),*[ico([.045,.04,.025],'ink',[s*.282,.11,1.03],distort=0) for s in [-1,1]],*[tube([[s*.36,.17,.42-j*.065],[s*.37,-.12,.42-j*.065]],.008,'charcoal',5) for s in [-1,1] for j in range(4)]]
    shark += [poly([[sg*.26,-.11,.34],[sg*.35,-.08,-.17],[sg*1.02,-.21,-.57],[sg*.75,-.16,.08],[sg*.46,-.09,.18]],[[0,1,2,3,4]],'steel') for sg in [-1,1]]
    p('shark_body','鲨鱼躯干 · 梭形体／背鳍／鳃线',shark,[.82,1.2,3.15],anchor='center',category='aquatic',material='mat.skin',collision={'type':'capsule','radius':.36,'segment_start':[0,0,-.9],'segment_end':[0,0,.9]})
    tail=[extrude([[-.06,.08],[-.07,-.07],[-.48,-.48],[-.58,-.47],[-.40,-.09],[-.36,.15],[-.63,.64],[-.52,.68]],.045,'steel',rotation=[0,90,0]),loft([[0,0,.10,.07,.09],[0,0,-.38,.06,.14]],'steel',8,frame_axis=[0,0,-1])]
    p('fish_tail','鱼类尾鳍 · 非对称新月轮廓',tail,[.10,1.20,.90],anchor='hinge',category='aquatic',material='mat.skin')
    tc=[[0,0,0],[.12,-.11,.06],[.35,-.18,.10],[.58,-.16,.16],[.77,-.04,.24],[.80,.10,.25]]
    trig=[{'name':'root','position':tc[0]},{'name':'mid','parent':'root','position':tc[2]},{'name':'tip','parent':'mid','position':tc[4]}]
    tr=[{'c':c,'r':[r,r],'bone':'root' if j<2 else 'mid' if j<4 else 'tip'} for j,(c,r) in enumerate(zip(tc,[.10,.088,.065,.047,.025,.01]))]
    # Blend the inter-joint rings; the anatomical joint rings themselves stay shared.
    for j,w in {1:{'root':.65,'mid':.35},2:{'root':.20,'mid':.80},3:{'mid':.65,'tip':.35},4:{'mid':.20,'tip':.80}}.items():tr[j]['weights']=w
    tentacle=[loft(tr,'red',10),*[disk(.018,.012,'linen',[c[0],c[1]-.055,c[2]],8,bone='root' if j<2 else 'mid' if j<4 else 'tip') for j,c in enumerate(tc[1:5],1)]]
    p('tentacle','弯曲触手 · 三骨架与吸盘',tentacle,[.92,.44,.40],anchor='hinge',category='aquatic',material='mat.skin',rig=trig)
    slime=[lathe([[.34,.02],[.45,.09],[.49,.28],[.37,.56],[.16,.73],[0,.76]],'leafLight',16,cap=True),*[ico([.075,.11,.04],'ink',[s*.16,.37,.404],distort=0) for s in [-1,1]],*[ico([.023,.03,.012],'white',[s*.16-.013,.392,.425],distort=0,detail=0) for s in [-1,1]],ico([.10,.027,.026],'leafDark',[0,.255,.448],distort=0)]
    p('slime','史莱姆核心 · 水滴体与面部识别',slime,[1,.80,.96],category='animal',material='mat.water',collision={'type':'sphere','radius':.42,'center':[0,.4,0]})
    # Anatomical skeletal rig uses named bones and non-overlapping rigid bone sections.
    positions={'pelvis':[0,.91,0],'chest':[0,1.25,0],'head':[0,1.624,0]}
    parents={'chest':'pelvis','head':'chest'}
    sk=[rod([0,.94,0],[0,1.46,0],.026,'bone',bone='chest'),ring(.15,.035,.07,'bone',position=[0,.91,0],scale=[1,.8,.72],bone='pelvis')]
    for sg,label in [(-1,'L'),(1,'R')]:
        for name,pos,parent in [('thigh',[sg*.128,.91,0],'pelvis'),('knee',[sg*.128,.51,.012],'thigh'+label),('foot',[sg*.128,.15,.012],'knee'+label),('arm',[sg*.235,1.37,0],'chest'),('elbow',[sg*.3246,1.094,0],'arm'+label),('hand',[sg*.3725,.822,.008],'elbow'+label)]:
            positions[name+label]=pos;parents[name+label]=parent
        for one,two,bone in [('thigh','knee','thigh'),('knee','foot','knee'),('arm','elbow','arm'),('elbow','hand','elbow')]:
            aa=positions[one+label];bb=positions[two+label]
            sk += [rod(aa,bb,.026 if bone in ['thigh','knee'] else .020,'bone',sides=8,bone=bone+label),ico([.073,.073,.073],'bone',aa,detail=0,distort=0,bone=bone+label)]
        sk += [box([.09,.045,.20],'bone',[sg*.128,.10,.06],bevel=.018,bone='foot'+label)]
        for j in range(5):
            y=1.1+j*.062;ww=.17+(.035 if j<3 else 0)
            sk.append(tube([[0,y,.12],[sg*ww,y-.02,.08],[sg*ww,y+.015,-.04],[0,y+.03,-.08]],.016,'bone',8,bone='chest'))
    sk += [ico([.24,.27,.21],'bone',[0,1.67,0],distort=0,bone='head'),*[ico([.055,.060,.025],'charcoal',[s*.064,1.695,.091],distort=0,bone='head') for s in [-1,1]],box([.14,.045,.095],'bone',[0,1.55,.035],bevel=.013,bone='head'),*[rod([x,1.547,.082],[x,1.579,.09],.006,'linen',sides=5,bone='head') for x in [-.05,-.025,0,.025,.05]]]
    sr=[{'name':n,'position':q,**({'parent':parents[n]} if n in parents else {})} for n,q in positions.items()]
    p('skeleton','骷髅骨架 · 肋骨／颅骨／分段长骨',sk,[.88,1.85,.34],material='mat.matte',rig=sr,collision={'type':'capsule','radius':.24,'segment_start':[0,.24,0],'segment_end':[0,1.55,0]})
    dragonhead=[loft([[0,.05,-.28,.18,.22],[0,.07,0,.25,.25],[0,.01,.37,.15,.12],[0,0,.55,.08,.09]],'teal',10,frame_axis=[0,0,1]),*[loft([[s*.19,.19,-.13,.055,.055],[s*.26,.46,-.24,.035,.035],[s*.31,.59,-.38,.008,.008]],'bone',8) for s in [-1,1]],*[ico([.07,.047,.024],'yellow',[s*.203,.155,.20],distort=0) for s in [-1,1]],*[ico([.018,.046,.014],'ink',[s*.204,.155,.22],distort=0) for s in [-1,1]],*[extrude([[0,0],[.13,-.08],[.06,.12]],.015,'teal',rotation=[0,s*35,0],position=[s*.22,.1,-.18]) for s in [-1,1]]]
    p('dragon_head','幼龙头部 · 角冠／颊鳍／长吻',dragonhead,[.66,.84,.99],anchor='hinge',material='mat.skin')
    joints=[[0,0,0],[.44,.25,0],[.75,.40,-.14],[1.55,.20,-.29],[1.04,.05,-.67],[.70,-.06,-.97],[.24,-.11,-.57]]
    wingforms=[poly(joints,[[0,1,2],[0,2,6],[2,3,4],[2,4,6],[4,5,6]],'teal',material='mat.skin')]
    wingforms += [rod(joints[u],joints[v],.025,'woodDark',r2=.009,sides=8) for u,v in [(0,1),(1,2),(2,3),(2,4),(2,5),(0,6)]]
    p('membrane_wing','膜翼 · 指骨支架与连贯翼膜',wingforms,[1.62,.58,1.05],anchor='hinge',material='mat.skin',description='翼膜为合理开放曲面；不作为闭合实体错误。')
    # Ten anatomical/function rigs.
    def quadruped(leg,ys,xs,zs,scale=None):return [pi('leg'+str(i),ip(leg),[x,ys,z],scale=scale) for i,(x,z) in enumerate([(s*xs,z) for z in zs for s in [-1,1]])]
    bearitems=[pi('body',ip('mammal_torso'),[0,.95,0]),*quadruped('plantigrade_leg',.76,.34,[-.57,.59])]
    a('bear_body','熊科承重骨架 · 躯干与四肢',bearitems,metadata=controls(*[turn('leg'+str(i),'腿部摆动','leg'+str(i),-14,14,[1,0,0]) for i in range(4)]))
    a('elephant_body','象类承重骨架 · 宽躯干与柱腿',[pi('body',ip('mammal_torso'),[0,1.65,0],scale=[1.70,1.52,1.45],params={'palette':{C('woodDark'):C('stone')}}),*quadruped('elephant_leg',1.13,.52,[-.80,.80])])
    a('flight_rig','鸟类飞行骨架 · 躯干与双翼',[pi('body',ip('avian_torso'),[0,.45,0]),pi('wingR',ip('feather_wing'),[.18,.55,.10]),pi('wingL',ip('feather_wing'),[-.18,.55,.10],rot=[0,0,180]),pi('footL',ip('talon'),[-.11,.28,.03]),pi('footR',ip('talon'),[.11,.28,.03])],category='bird',metadata=controls(turn('wingR','右翼','wingR',-30,35,[0,0,1]),turn('wingL','左翼','wingL',-35,30,[0,0,1])))
    clip(ia('flight_rig'),[{'name':'Wingbeat inspection','duration':1.2,'tracks':[track('wingR',[0,0,1],[-20,30,-20]),track('wingL',[0,0,1],[20,-30,20])]}])
    a('reptile_body','爬行体段 · 外展四肢与尾部',[pi('body',ip('reptile_torso'),[0,.33,0]),*[pi('leg'+str(i),ip('reptile_leg'),[s*.25,.30,z],rot=[0,0,0] if s>0 else [0,180,0]) for i,(s,z) in enumerate([(s,z) for z in [-.45,.55] for s in [-1,1]])]])
    a('serpent_rig','蛇形游动骨架 · 五骨权重',[pi('body',ip('serpent'))])
    clip(ia('serpent_rig'),[{'name':'Serpentine inspection','duration':2,'tracks':[track('body.rig.spine'+str(j),[0,1,0],[v,-v,v]) for j,v in enumerate([5,-13,16,-13,8])]}])
    a('shark_tail_rig','鲨尾与连续身体运动组',[pi('tail',ip('fish_tail')),pi('body',ip('shark_body'),[0,0,1.45])],category='aquatic')
    a('tentacle_crown','八触腕运动架 · 每肢三骨',[*[pi('arm'+str(i),ip('tentacle'),[.12*math.sin(i*math.tau/8),.30,.12*math.cos(i*math.tau/8)],rot=[0,i*45,0]) for i in range(8)]],category='aquatic')
    clip(ia('tentacle_crown'),[{'name':'Tentacle wave','duration':2.8,'tracks':[track('arm'+str(i)+'.rig.mid',[0,0,1],[12*(-1)**i,-12*(-1)**i,12*(-1)**i]) for i in range(8)]}])
    a('skeleton_guard','骷髅守卫骨架 · 权重蒙皮与握持道具',[pi('skin',ip('skeleton')),pi('sword','exp.wear.sword',parent='skin.rig.handR'),pi('shield','exp.wear.shield',parent='skin.rig.handL')],metadata={'motion_scope':'inspection; no physics or AI'})
    mo=deepcopy(MOTIONS['fnd-adult']);mo['assembly']=ia('skeleton_guard');MOTIONS[ia('skeleton_guard')]=mo
    a('dragon_body','幼龙躯体 · 承重四肢与膜翼',[pi('body',ip('reptile_torso'),[0,.75,0],scale=[.8,1.6,.7],params={'palette':{C('pine'):C('teal')}}),*quadruped('plantigrade_leg',.73,.27,[-.4,.4],scale=[.65,.88,.65]),pi('wingR',ip('membrane_wing'),[.20,.94,.20]),pi('wingL',ip('membrane_wing'),[-.2,.94,.2],rot=[0,0,180])],metadata=controls(turn('right','右翼','wingR',-25,30,[0,0,1]),turn('left','左翼','wingL',-30,25,[0,0,1])))
    a('slime_core','史莱姆运动核心 · 跃动根节点',[pi('core',ip('slime'))],metadata=controls(slider('bounce','跳跃高度','core',0,.40)))
    motion(ia('slime_core'),'core',values=[0,.18,.4,.18,0],seconds=1.2,mode='translation',name='Slime hop')
    # Six complete wildlife/fantasy figures, kept distinct from anatomy kits.
    a('bear','棕熊 · 承重四肢与可动颈部',[ai('anatomy',ia('bear_body')),pi('head',ip('bear_head'),[0,1.21,.93])],level=3,metadata=controls(turn('look','头部转向','head',-25,25)))
    clip(ia('bear'),[{'name':'Bear step inspection','duration':2,'tracks':[track('anatomy.leg'+str(i),[1,0,0],[v,-v,v]) for i,v in enumerate([9,-9,-9,9])]+[track('head',[0,1,0],[-10,10,-10])]}])
    a('elephant','象 · 长鼻／宽耳／柱状四肢',[ai('anatomy',ia('elephant_body')),pi('head',ip('elephant_head'),[0,1.95,1.25],scale=[1.18,1.18,1.18])],level=3,metadata=controls(turn('look','头部转向','head',-18,18)))
    motion(ia('elephant'),'head',values=[-9,9,-9],seconds=3,name='Elephant head')
    a('eagle','鹰 · 完整羽翼与握爪',[ai('anatomy',ia('flight_rig')),pi('head',ip('raptor_head'),[0,.68,.33])],level=3,category='bird')
    # Eagle inherits the flight rig clips through their stable anatomy namespace.
    a('crocodile','鳄鱼 · 长吻／甲脊／低伏步态',[ai('anatomy',ia('reptile_body')),pi('head',ip('reptile_head'),[0,.42,1])],level=3,metadata=controls(turn('head','头部转向','head',-15,15)))
    a('shark','鲨鱼 · 梭形躯干与摆尾',[pi('body',ip('shark_body'),[0,.62,0]),pi('tail',ip('fish_tail'),[0,.62,-1.45])],level=3,category='aquatic',metadata=controls(turn('tail','尾鳍摆动','tail',-22,22)))
    motion(ia('shark'),'tail',values=[-18,18,-18],seconds=1.5,name='Shark swim inspection')
    a('dragon','幼年飞龙 · 角冠与指骨膜翼',[ai('anatomy',ia('dragon_body')),pi('head',ip('dragon_head'),[0,1,.78])],level=3,metadata=controls(turn('head','头部转向','head',-25,25)))
    clip(ia('dragon'),[{'name':'Dragon wing inspection','duration':2,'tracks':[track('anatomy.wingR',[0,0,1],[-15,25,-15]),track('anatomy.wingL',[0,0,1],[15,-25,15]),track('head',[0,1,0],[-10,10,-10])]}])
    finish_counts(D)
