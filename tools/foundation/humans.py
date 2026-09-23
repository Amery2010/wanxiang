"""Matched human interface rings and a single, shared skeleton per compiled body."""
from .common import *
def author():
 B=Q('build');H=div(Q('height'),1.82)
 # Head includes readable face planes rather than microscopic catalogue entries.
 fw=Q('face_width');jaw=Q('jaw_width');nose=Q('nose_length')
 forms=[profile([[0,-.145,.015,mul(.076,jaw),.073],[0,-.113,.005,mul(.108,jaw),.092],[0,-.043,0,mul(.127,fw),.112],[0,.041,-.003,mul(.134,fw),.115],[0,.114,-.012,mul(.125,fw),.103],[0,.16,-.019,.091,.08]],'skin'),
  # Broad, short wedge nose with bridge, tip and nostril plane.
  poly([[-.023,.046,.112],[.023,.046,.112],[-.029,-.022,mul(.155,nose)],[.029,-.022,mul(.155,nose)],[-.021,-.046,.129],[.021,-.046,.129]],[[0,1,3,2],[2,3,5,4],[0,2,4],[1,5,3],[0,4,5,1]],'skin'),
  box([.058,.006,.007],'skinShade',[0,-.076,.109],bevel=.001),
 ]
 for sg in [-1,1]:
  forms += [profile([[mul(sg*.136,fw),-.048,-.01,.025,.021],[mul(sg*.147,fw),.01,-.008,.023,.026],[mul(sg*.138,fw),.053,-.012,.016,.017]],'skin'),
    box([.039,.019,.009],'white',[mul(sg*.054,fw),.016,.114],bevel=.003),box([.016,.019,.011],'ink',[mul(sg*.054,fw),.016,.120],bevel=.003),box([.047,.011,.012],'hair',[mul(sg*.056,fw),.052,.112],bevel=.002,rotation=[0,0,sg*3])]
 part('core.human.head','成人头部 · 颧面 / 短鼻 / 下颌','body',forms,[.32,.31,.30],anchor='center',params=schema(face_width=number(1,.9,1.13,'脸宽'),jaw_width=number(1,.86,1.12,'下颌宽'),nose_length=number(1,.88,1.12,'鼻部长度')),ports=[port('neck',[0,-.125,0],(0,-1,0),interface='human.neck.v1'),port('hair',[0,.055,0],interface='human.hair.v1')],material='mat.skin',tags=['头','人物母版'])
 part('core.human.hair.short','短发 · 完整发帽 / 非重叠折面','body',[
  profile([{'c':[0,.055,-.025],'r':[.139,.122]},{'c':[0,.121,-.023],'r':[.136,.122]},{'c':[.010,.176,-.025],'r':[.108,.102]},{'c':[.025,.196,-.032],'r':[.050,.058]}],'hair',frame_axis=[0,1,0]),
  # Temple locks are below the cap, with only hidden overlap at their roots.
  *[box([.023,.065,.038],'hair',[sg*.126,.027,-.043],bevel=.006) for sg in [-1,1]]
 ],[.285,.235,.25],anchor='center',ports=[port('mount',[0,.055,0],(0,-1,0),interface='human.hair.v1')],material='mat.hair')
 part('core.human.beard','短胡须 · 下颌包覆','body',[
  poly([[-.109,-.041,.075],[-.083,-.106,.087],[0,-.151,.096],[.083,-.106,.087],[.109,-.041,.075],[.076,-.070,.122],[0,-.099,.13],[-.076,-.070,.122]],[[0,1,7],[1,2,6,7],[2,3,5,6],[3,4,5]],'hair'),
  box([.076,.018,.012],'hair',[0,-.051,.132],bevel=.003)
 ],[.22,.11,.14],anchor='center',material='mat.hair')
 # Torso tapers at waist, broadens through chest; collar is constructed, not painted.
 part('core.human.torso','衬衣躯干 · 肩胸 / 领口','body',[
  profile([{'c':[0,0,0],'r':[.165,.111],'bone':'pelvis'},{'c':[0,.16,0],'r':[.17,.124],'weights':{'pelvis':.4,'chest':.6}},{'c':[0,.35,-.003],'r':[.218,.139],'bone':'chest'},{'c':[0,.45,-.008],'r':[.232,.126],'bone':'chest'},{'c':[0,.52,-.01],'r':[.095,.074],'bone':'chest'}],'cream'),
  profile([[0,.50,-.005,.070,.066],[0,.62,-.004,.068,.064]],'skin',bone='head',material='mat.skin'),
  poly([[-.074,.527,.065],[-.027,.444,.137],[-.112,.473,.116],[-.131,.506,.099]],[[0,1,2,3]],'white',bone='chest'),
  poly([[.074,.527,.065],[.027,.444,.137],[.112,.473,.116],[.131,.506,.099]],[[0,3,2,1]],'white',bone='chest'),
  box([.012,.33,.007],'white',[0,.24,.137],bevel=.002,bone='chest'),
  *[box([.012,.012,.011],'woodDark',[0,y,.144],bevel=.002,bone='chest') for y in [.1,.20,.3,.395]],
  box([.089,.081,.01],'cream',[-.107,.31,.137],bevel=.004,bone='chest'),box([.095,.012,.012],'white',[-.107,.351,.145],bevel=.002,bone='chest')
 ],[.464,.62,.28],ports=[port('waist',[0,0,0],(0,-1,0),interface='human.waist.v1'),port('neck',[0,.59,0],interface='human.neck.v1'),port('shoulderR',[.235,.5,0],(1,0,0),(0,1,0),interface='human.arm.v1')],material='mat.fabric')
 part('core.human.pelvis','长裤胯部 · 腰带下衔接','body',[profile([[0,-.075,0,.166,.11],[0,.015,0,.179,.116],[0,.07,0,.167,.11]],'moss',bone='pelvis')],[.36,.145,.235],anchor='center',material='mat.fabric',ports=[port('waist',[0,.07,0],interface='human.waist.v1')])
 part('core.human.upperarm','卷袖上臂 · 肩与肘过渡','body',[
  profile([{'c':[0,.033,0],'r':[.040,.048],'bone':'arm'},{'c':[0,-.045,0],'r':[.096,.094],'bone':'arm'},{'c':[0,-.18,0],'r':[.080,.080],'bone':'arm'}],'cream',preserve_ends=True),
  profile([[0,-.157,0,.093,.092],[0,-.189,0,.097,.096],[0,-.206,0,.086,.085]],'white',bone='arm'),
  profile([{'c':[0,-.177,0],'r':[.074,.072],'bone':'arm'},{'c':[0,-.257,0],'r':[.067,.065],'bone':'arm'},{'c':[0,-.29,0],'r':[.063,.063],'weights':{'arm':.5,'elbow':.5}}],'skin',preserve_ends=True,cap=False,material='mat.skin')
 ],[.216,.318,.204],anchor='top',ports=[port('shoulder',[0,0,0],interface='human.arm.v1'),port('elbow',[0,-.29,0],(0,-1,0),interface='human.elbow.v1')],material='mat.fabric')
 part('core.human.forearm','前臂 · 肘腕连续截面','body',[profile([{'c':[0,0,0],'r':[.063,.063],'weights':{'arm':.5,'elbow':.5}},{'c':[0,-.06,.002],'r':[.073,.063],'bone':'elbow'},{'c':[0,-.19,.006],'r':[.052,.047],'bone':'elbow'},{'c':[0,-.276,.008],'r':[.039,.037],'weights':{'elbow':.65,'hand':.35}}],'skin',preserve_ends=True)],[.145,.276,.13],anchor='top',ports=[port('elbow',[0,0,0],interface='human.elbow.v1'),port('wrist',[0,-.276,.008],(0,-1,0),interface='human.wrist.v1')],material='mat.skin')
 part('core.human.hand','手掌 · 放松 / 握持','body',[
  profile([[0,0,0,.040,.036],[0,-.048,.01,.046,.033],[.002,choice('grip',{'false':-.11,'true':-.077}),choice('grip',{'false':.025,'true':.042}),.032,.032],[.002,choice('grip',{'false':-.132,'true':-.095}),choice('grip',{'false':.033,'true':.028}),.020,.024]],'skin',bone='hand'),
  profile([[-.034,-.019,.012,.020,.020],[-.050,-.049,.038,.021,.020],[-.039,-.079,.049,.014,.014]],'skin',bone='hand')
 ],[.11,.132,.1],anchor='top',params=schema(grip={'type':'boolean','default':False,'title':'握持手型'}),ports=[port('wrist',[0,0,0],interface='human.wrist.v1'),port('grip',[0,-.061,.042],(0,0,1),interface='hand.tool.v1')],material='mat.skin')
 part('core.human.thigh','裤装大腿 · 匹配膝环','body',[profile([{'c':[0,.04,0],'r':[.10,.115],'bone':'thigh'},{'c':[0,-.15,.002],'r':[.107,.105],'bone':'thigh'},{'c':[0,-.31,.006],'r':[.077,.077],'bone':'thigh'},{'c':[0,-.4,.012],'r':[.072,.07],'weights':{'thigh':.5,'knee':.5}}],'moss',preserve_ends=True)],[.215,.44,.23],anchor='top',material='mat.fabric',ports=[port('hip',[0,0,0],interface='human.hip.v1'),port('knee',[0,-.4,.012],(0,-1,0),interface='human.knee.v1')])
 part('core.human.shin','裤装小腿 · 膝踝收束','body',[profile([{'c':[0,0,0],'r':[.072,.07],'weights':{'thigh':.5,'knee':.5}},{'c':[0,-.13,-.012],'r':[.076,.077],'bone':'knee'},{'c':[0,-.285,-.002],'r':[.051,.061],'bone':'knee'},{'c':[0,-.36,0],'r':[.045,.054],'bone':'foot'}],'moss',preserve_ends=True)],[.154,.36,.155],anchor='top',material='mat.fabric',ports=[port('knee',[0,0,0],interface='human.knee.v1'),port('ankle',[0,-.36,0],(0,-1,0),interface='human.ankle.v1')])
 part('core.human.boot','短靴 · 鞋楦 / 靴筒 / 鞋底','wear',[
  box([.162,.038,.295],'rubber',[0,.019,.050],bevel=.012,bone='foot',material='mat.rubber'),
  profile([[0,.038,.05,.076,.14],[0,.079,.052,.077,.13],[0,.12,.014,.062,.074],[0,.225,.003,.061,.065],[0,.237,.003,.067,.072]],'woodDark',bone='foot'),
  *[box([.071,.009,.01],'woodLight',[0,.115+i*.020,.079],bevel=.002,bone='foot') for i in range(3)]
 ],[.164,.238,.296],ports=[port('ankle',[0,.14,0],interface='human.ankle.v1'),port('sole',[0,0,0],(0,-1,0),interface='ground')],material='mat.leather')
 rig=[{'name':'pelvis','position':[0,mul(.91,H),0]},{'name':'chest','parent':'pelvis','position':[0,mul(1.25,H),0]},{'name':'head','parent':'chest','position':[0,mul(1.624,H),0]}]
 comps=[component('torso','core.human.torso',[0,mul(.91,H),0],frame_scale=[B,H,B]),component('hips','core.human.pelvis',[0,mul(.91,H),0],frame_scale=[B,H,B])]
 # Matched seams are transformed by the same parent frames, avoiding independent rigs.
 for sg,s in [(-1,'L'),(1,'R')]:
  armx=.235;army=1.37;angle=18;elx=armx+math.sin(math.radians(angle))*.29;ely=army-math.cos(math.radians(angle))*.29
  wrx=elx+math.sin(math.radians(10))*.276;wry=ely-math.cos(math.radians(10))*.276
  positions={'thigh':[sg*.128,.91,0],'knee':[sg*.128,.51,.012],'foot':[sg*.128,.15,.012],'arm':[sg*armx,army,0],'elbow':[sg*elx,ely,0],'hand':[sg*wrx,wry,.008]}
  for k,parent in [('thigh','pelvis'),('knee','thigh'+s),('foot','knee'+s),('arm','chest'),('elbow','arm'+s),('hand','elbow'+s)]:
   pos=positions[k];rig.append({'name':k+s,'parent':parent,'position':[mul(pos[0],B),mul(pos[1],H),mul(pos[2],B)]})
  bind={n:n+s for n in ['thigh','knee','foot','arm','elbow','hand']}
  comps += [component('upperarm'+s,'core.human.upperarm',[mul(sg*armx,B),mul(army,H),0],rotation=[0,0,sg*18],frame_scale=[B,H,B],bind=bind),component('forearm'+s,'core.human.forearm',[mul(sg*elx,B),mul(ely,H),0],rotation=[0,0,sg*10],frame_scale=[B,H,B],bind=bind),component('hand'+s,'core.human.hand',[mul(sg*wrx,B),mul(wry,H),mul(.008,B)],rotation=[0,0,sg*10],frame_scale=[B,H,B],mirror='x' if sg<0 else None,bind=bind,params={'grip':Q('grip')}),component('thigh'+s,'core.human.thigh',[mul(sg*.128,B),mul(.91,H),0],frame_scale=[B,H,B],bind=bind),component('shin'+s,'core.human.shin',[mul(sg*.128,B),mul(.51,H),mul(.012,B)],frame_scale=[B,H,B],bind=bind),component('boot'+s,'core.human.boot',[mul(sg*.128,B),0,mul(.012,B)],frame_scale=[B,H,B],bind=bind)]
 # Remove absent mirror flags; JSON remains compact and explicit.
 for c in comps:
  if c.get('mirror') is None:c.pop('mirror',None)
 body_params=schema(height=number(1.82,1.64,1.98,'成人身高',.01,'m'),build=number(1,.9,1.18,'体格'),grip={'type':'boolean','default':False,'title':'握持手型'})
 part('core.human.body','成人身体总成 · 统一骨架与可替换源部件','body',size=[.92,1.56,.35],components=comps,rig=rig,level=2,params=body_params,ports=[port('neck',[0,mul(1.51,H),0],interface='human.neck.v1'),port('equipment.waist',[0,mul(.99,H),mul(.13,B)],(0,0,1),interface='human.waist.equipment.v1')],material='mat.fabric',description='语义作者层由躯干、上下臂、手、胯、腿和靴组成；编译为同一骨架的材质分组网格。')
 part('core.wear.belt','皮带 · 带扣与带圈','wear',[profile([[0,-.024,0,.176,.122],[0,.024,0,.176,.122]],'woodDark'),box([.07,.046,.018],'yellow',[0,0,.13],bevel=.006,material='mat.metal'),box([.038,.025,.022],'woodDark',[0,0,.132],bevel=.003)], [.36,.05,.285],anchor='center',material='mat.leather')
 part('core.wear.apron','工匠围裙 · 肩带 / 腰袋 / 下摆','wear',[
  profile([[0,-.30,.092,.22,.052],[0,-.10,.102,.20,.046],[0,.10,.122,.162,.034]],'wood'),
  poly([[-.155,.11,.154],[.155,.11,.154],[.129,.425,.159],[-.129,.425,.159],[-.163,.105,.17],[.163,.105,.17],[.131,.425,.174],[-.131,.425,.174]],[[0,1,2,3],[4,7,6,5],[0,3,7,4],[1,5,6,2],[3,2,6,7]],'wood'),
  box([.20,.103,.025],'woodDark',[0,.193,.182],bevel=.01),box([.207,.017,.029],'woodLight',[0,.245,.186],bevel=.004),
  rod([-.12,.414,.148],[-.195,.524,.015],.018,'woodDark',sides=5),rod([.12,.414,.148],[.195,.524,.015],.018,'woodDark',sides=5),
  *[box([.027,.025,.016],'yellow',[sg*.103,.392,.18],bevel=.004,material='mat.metal') for sg in [-1,1]]
 ],[.45,.84,.25],anchor='center',material='mat.leather',ports=[port('waist',[0,0,0],interface='human.waist.equipment.v1')])
 part('core.tool.hammer','工匠锤 · 木柄 / 楔形锤头','props',[
  profile([[0,-.31,0,.018,.022],[0,-.17,0,.022,.025],[0,.07,0,.02,.023]],'woodLight'),box([.22,.073,.077],'steel',[0,.07,0],bevel=.009,material='mat.metal'),box([.054,.078,.086],'metal',[-.1,.07,0],bevel=.006,material='mat.metal')
 ],[.265,.42,.09],anchor='center',ports=[port('grip',[0,-.12,0],(0,0,1),interface='hand.tool.v1')],material='mat.wood')
 # Two genuinely different outfits use the same rig/hand/leg sources.
 for ident,name,worker in [('fnd-adult','成人母版 · 自然比例便装',False),('fnd-artisan','工匠母版 · 工作围裙与锤',True)]:
  b=Q('build');params=schema(height=number(1.82,1.64,1.98,'身高',.01,'m'),build=number(1.14 if worker else 1,.92,1.18,'体格'))
  hs=div(Q('height'),1.82)
  items=[inst('skin','core.human.body',params={'height':Q('height'),'build':b,'grip':worker,**({'palette':{P['cream']:P['blue'],P['white']:P['navy'],P['moss']:'#424E57'}} if worker else {})}),inst('head','core.human.head',parent='skin.rig.head',scale=[hs,hs,hs]),inst('hair','core.human.hair.short',parent='skin.rig.head',scale=[hs,hs,hs]),inst('beard','core.human.beard',parent='skin.rig.head',scale=[hs,mul(.93 if worker else .76,hs),hs]),inst('belt','core.wear.belt',pos=[0,mul(.986,hs),0],scale=[b,1,b])]
  if worker:items += [inst('apron','core.wear.apron',pos=[0,mul(.965,hs),0],scale=[b,hs,b]),inst('hammer','core.tool.hammer',parent='skin.rig.handR',pos=[0,.057,.05],rot=[0,0,-12])]
  assembly(ident,name,'body',items,params=params,description='非换色复制：便装与工匠共享解剖母版，工匠具有独立围裙、口袋、装备与握持手型。')
  tracks=[]
  for s,sg in [('L',1),('R',-1)]:
   tracks += [track('skin.rig.thigh'+s,[1,0,0],[sg*15,-sg*15,sg*15]),track('skin.rig.knee'+s,[1,0,0],[0,23,0] if sg==1 else [23,0,23]),track('skin.rig.arm'+s,[1,0,0],[-sg*10,sg*10,-sg*10])]
  clip(ident,[{'name':'Walk inspection','duration':1.2,'tracks':tracks},{'name':'Arm inspection','duration':2.4,'tracks':[track('skin.rig.armR',[0,0,1],[0,-45,0]),track('skin.rig.elbowR',[1,0,0],[0,-45,0])]}])
