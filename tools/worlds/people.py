"""Role-driven outfits on one stitched skeleton. Accessories are real reusable parts."""
from .common import *
def author():
 wp('w.wear.hardhat','工程安全帽 · 帽壳与帽檐','wear',[lathe([[.147,.053],[.152,.102],[.134,.194],[.087,.24],[.025,.25]],'yellow',12,cap=True),box([.34,.025,.38],'yellow',[0,.068,.019],bevel=.04),box([.027,.031,.22],'yellow',[0,.22,0],bevel=.012)],[.34,.26,.38],anchor='center',material='mat.paint')
 wp('w.wear.strawhat','草编宽檐帽 · 帽冠与分色帽带','wear',[lathe([[.29,.066],[.305,.078],[.153,.103],[.144,.235],[.09,.265],[.02,.265]],'woodLight',12,cap=True),lathe([[.15,.098],[.15,.127]],'woodDark',12,cap=True)],[.61,.28,.61],anchor='center',material='mat.fabric')
 wp('w.wear.cap','工作便帽 · 帽顶与前帽檐','wear',[profile([[0,.049,0,.137,.12],[0,.13,-.01,.136,.122],[.01,.205,-.025,.077,.085]],'red'),box([.23,.019,.20],'red',[0,.070,.13],bevel=.031)],[.28,.22,.34],anchor='center',material='mat.fabric')
 wp('w.wear.driver_hat','司机制服帽 · 帽徽与帽檐','wear',[profile([[0,.046,0,.14,.12],[0,.097,0,.15,.135],[0,.155,-.015,.142,.12]],'navy'),box([.24,.019,.19],'ink',[0,.057,.127],bevel=.029),box([.042,.039,.012],'yellow',[0,.103,.128],bevel=.006)],[.30,.17,.33],anchor='center',material='mat.fabric')
 wp('w.wear.helmet','防护头盔 · 包覆外壳与面罩','wear',[profile([[0,-.10,-.02,.141,.115],[0,.04,-.02,.164,.143],[0,.15,-.03,.137,.12],[0,.20,-.037,.077,.074]],'ink'),box([.255,.101,.061],'glass',[0,.02,.13],bevel=.025,material='mat.vehicleGlass'),box([.29,.037,.013],'red',[0,.146,.117],bevel=.013)],[.33,.30,.36],anchor='center',material='mat.paint')
 wp('w.wear.safety_vest','反光马甲 · 前襟与反光带','wear',[
  *[profile([[sg*.115,-.23,.02,.099,.133],[sg*.132,.08,.01,.11,.15],[sg*.14,.19,.005,.094,.139]],'orange') for sg in [-1,1]],
  *[box([.04,.37,.013],'white',[sg*.122,-.004,.163],bevel=.004) for sg in [-1,1]],
  box([.405,.038,.014],'white',[0,-.154,.167],bevel=.004),box([.05,.11,.018],'ink',[-.14,.038,.178],bevel=.005)
 ],[.51,.45,.35],anchor='center',material='mat.fabric',level=2)
 wp('w.wear.overall_bib','工装背带 · 护胸、肩带与口袋','wear',[box([.31,.33,.037],'navy',[0,-.06,.159],bevel=.025),*[beam([sg*.11,.09,.165],[sg*.17,.24,0],.038,.018,'navy') for sg in [-1,1]],box([.17,.10,.025],'blue',[0,-.045,.19],bevel=.007),*[disk(.014,.014,'yellow',[sg*.105,.061,.19],8,rotation=[90,0,0]) for sg in [-1,1]]],[.4,.51,.23],anchor='center',material='mat.fabric')
 wp('w.wear.field_vest','野外背心 · 口袋与肩片','wear',[profile([[0,-.22,0,.19,.135],[0,.04,0,.24,.16],[0,.20,-.025,.22,.13]],'woodDark'),*[box([.125,.12,.052],'wood',[sg*.115,-.065,.158],bevel=.016) for sg in [-1,1]],box([.03,.35,.01],'cream',[0,-.026,.177],bevel=.003)],[.49,.44,.39],anchor='center',material='mat.fabric')
 wp('w.wear.tactical_vest','防护背心 · 胸板 / 装备袋','wear',[profile([[0,-.21,0,.193,.145],[0,.11,0,.247,.157],[0,.21,-.02,.215,.129]],'moss'),box([.29,.22,.03],'woodDark',[0,.055,.166],bevel=.018),*[box([.073,.16,.075],'moss',[x,-.155,.180],bevel=.012) for x in [-.135,-.045,.045,.135]]],[.50,.46,.43],anchor='center',material='mat.fabric',level=2)
 wp('w.wear.field_helmet','野战头盔 · 帽壳与束带','wear',[lathe([[.159,-.01],[.168,.056],[.151,.17],[.092,.21],[.02,.215]],'moss',12,cap=True),*[box([.024,.16,.03],'woodDark',[sg*.128,-.051,.012],bevel=.006) for sg in [-1,1]]],[.34,.30,.34],anchor='center',material='mat.paint')
 wp('w.wear.backpack','旅行背包 · 主袋、侧袋和卷毯','wear',[box([.36,.42,.19],'woodDark',[0,0,-.09],bevel=.052),box([.27,.18,.06],'wood',[0,-.12,-.211],bevel=.025),*[box([.075,.24,.14],'wood',[sg*.202,-.09,-.08],bevel=.025) for sg in [-1,1]],lathe([[.082,-.235],[.085,.235]],'moss',10,cap=True,position=[0,.261,-.08],rotation=[0,0,90]),*[box([.029,.42,.026],'woodLight',[sg*.118,0,-.229],bevel=.006) for sg in [-1,1]]],[.5,.57,.3],anchor='center',material='mat.fabric',level=2)
 wp('w.wear.cape','巡林披风 · 肩覆与不对称下摆','wear',[poly([[-.245,.20,0],[.245,.20,0],[.28,.10,-.10],[-.28,.1,-.1],[-.30,-.5,-.13],[.33,-.46,-.13],[.16,-.42,-.28],[-.17,-.47,-.29],[0,.25,-.10]],[[0,3,8],[8,2,1],[3,4,7,8],[8,7,6,2],[2,6,5],[3,2,8]],'pine'),rod([-.20,.19,.035],[.20,.19,.035],.015,'woodDark',sides=6)],[.65,.78,.33],anchor='center',material='mat.fabric')
 wp('w.wear.ponytail','扎发 · 后脑发束','wear',[profile([[0,.07,-.025,.141,.126],[0,.145,-.025,.125,.118],[0,.19,-.022,.068,.067]],'hair'),loft([[0,.10,-.13,.05,.046],[.02,-.08,-.20,.06,.054],[.03,-.22,-.19,.03,.039]],'hair',7)],[.29,.44,.29],anchor='center',material='mat.hair')
 wp('w.wear.tie','领带 · 打结与垂片','wear',[poly([[-.025,.17,.16],[.025,.17,.16],[.023,.125,.178],[-.023,.125,.178],[-.012,.125,.18],[.012,.125,.18],[.027,-.12,.176],[0,-.157,.179],[-.027,-.12,.176]],[[0,1,2,3],[4,5,6,7,8]],'navy')],[.055,.33,.04],anchor='center',material='mat.fabric')
 wp('w.wear.toque','厨师高帽 · 帽带与分瓣帽冠','wear',[lathe([[.133,.06],[.135,.16],[.16,.20],[.167,.28],[.13,.33],[.015,.34]],'white',10,cap=True),*[box([.019,.14,.018],'cream',[math.cos(a)*.14,.247,math.sin(a)*.14],bevel=.006) for a in [i*math.pi/5 for i in range(10)]]],[.34,.35,.34],anchor='center',material='mat.fabric')
 wp('w.wear.weld_mask','焊接面罩 · 深色视窗与护颈','wear',[box([.30,.31,.19],'steel',[0,.004,.09],bevel=.041),box([.205,.075,.026],'ink',[0,.059,.20],bevel=.008,material='mat.vehicleGlass')],[.31,.32,.31],anchor='center',material='mat.paint')
 wp('w.tool.briefcase','公文包 · 箱体与提手','props',[box([.32,.25,.105],'woodDark',[0,-.12,0],bevel=.022),rod([-.063,.01,0],[-.063,.07,0],.012,'ink',sides=5),rod([.063,.01,0],[.063,.07,0],.012,'ink',sides=5),rod([-.063,.07,0],[.063,.07,0],.012,'ink',sides=5),box([.038,.035,.012],'yellow',[0,-.035,.06],bevel=.004)],[.33,.33,.12],anchor='top',material='mat.leather')
 wp('w.tool.clipboard','夹板 · 纸张与金属夹','props',[box([.22,.30,.025],'wood',[0,0,0],bevel=.008),box([.185,.258,.006],'white',[0,0,.018],bevel=.004),box([.076,.028,.016],'metal',[0,.13,.025],bevel=.004,material='mat.metal')],[.22,.31,.045],anchor='center',material='mat.wood')
 wp('w.tool.wrench','维修扳手 · 开口与套环','props',[box([.039,.25,.021],'metal',[0,-.08,0],bevel=.009),lathe([[.033,-.015],[.064,-.015],[.064,.015],[.033,.015]],'metal',10,closed_profile=True,position=[0,.09,0],rotation=[90,0,0]),box([.075,.055,.026],'metal',[0,-.21,0],bevel=.009)],[.13,.35,.035],anchor='center',material='mat.metal')
 wp('w.tool.pitchfork','农用草叉 · 木柄与三齿叉头','props',[rod([0,-.62,0],[0,.63,0],.021,'wood',sides=8),beam([-.14,.63,0],[.14,.63,0],.043,.027,'metal',material='mat.metal'),*[rod([x,.63,0],[x,.94,.012],.014,'metal',r2=.006,sides=6,material='mat.metal') for x in [-.13,0,.13]]],[.30,1.57,.055],anchor='center',material='mat.wood',level=2,theme='farm')
 wp('w.tool.rifle','游戏步枪道具 · 低模外形','props',[box([.068,.085,.39],'ink',[0,0,0],bevel=.01),box([.048,.18,.048],'ink',[0,-.10,-.06],bevel=.007,rotation=[-15,0,0]),box([.08,.12,.24],'woodDark',[0,-.025,-.29],bevel=.014),rod([0,.018,.15],[0,.018,.5],.018,'steel',sides=8),box([.025,.033,.24],'steel',[0,.062,.06],bevel=.004)],[.1,.28,.93],anchor='center',material='mat.metal')
 wp('w.tool.medkit','医疗包 · 绿色急救识别','props',[box([.29,.24,.13],'white',[0,-.11,0],bevel=.023),box([.10,.033,.014],'pine',[0,-.1,.076],bevel=.003),box([.033,.1,.014],'pine',[0,-.1,.077],bevel=.003),beam([-.045,.01,0],[.045,.01,0],.024,.025,'steel')],[.3,.26,.16],anchor='top',material='mat.fabric')
 wp('w.tool.pan','平底锅 · 浅锅壁与握柄','props',[lathe([[.10,0],[.125,.018],[.124,.035],[.113,.035],[.11,.012],[.01,.012]],'ink',16,closed_profile=True),rod([0,.014,-.11],[0,.014,-.36],.019,'woodDark',sides=6)],[.25,.04,.50],anchor='center',material='mat.metal')
 wp('w.tool.bow','巡林短弓 · 弯弓与弓弦','props',[loft([[0,-.43,0,.018,.018],[.08,-.24,0,.022,.022],[.105,0,0,.025,.025],[.08,.24,0,.022,.022],[0,.43,0,.018,.018]],'wood',6),rod([0,-.43,0],[0,.43,0],.004,'cream',sides=4)],[.14,.89,.05],anchor='center',material='mat.wood')
 roles=[
  ('ranger','巡林者','camp','pine','moss','w.wear.cape',None,'w.tool.bow',1.02,False),
  ('traveler','旅行者','camp','cream','woodDark','w.wear.backpack',None,None,1.02,True),
  ('farmer','农夫','farm','red','navy','w.wear.overall_bib','w.wear.strawhat','w.tool.pitchfork',1.04,False),
  ('rancher','牧场主','farm','cream','navy','w.wear.field_vest','w.wear.strawhat',None,1.12,True),
  ('gardener','园丁','farm','moss','moss','core.wear.apron','w.wear.strawhat','w.tool.clipboard',.95,False),
  ('market-villager','乡村商贩','farm','cream','red','core.wear.apron',None,'w.tool.briefcase',1.04,True),
  ('office-worker','上班族','city','white','navy','w.wear.tie',None,'w.tool.briefcase',.98,False),
  ('courier','快递员','city','red','ink','w.wear.backpack','w.wear.cap',None,.99,False),
  ('police','街道警员','city','navy','navy','w.wear.tactical_vest','w.wear.driver_hat',None,1.10,False),
  ('street-vendor','街头摊主','city','white','navy','core.wear.apron','w.wear.cap',None,1.04,False),
  ('chef','厨师','home','white','ink','core.wear.apron','w.wear.toque','w.tool.pan',1.06,False),
  ('remote-worker','居家工作者','home','cream','moss',None,None,'w.tool.clipboard',.95,True),
  ('construction-worker','施工工人','construction','blue','navy','w.wear.safety_vest','w.wear.hardhat','core.tool.hammer',1.10,False),
  ('engineer','现场工程师','construction','moss','woodDark','w.wear.safety_vest','w.wear.hardhat','w.tool.clipboard',.96,True),
  ('welder','焊工','construction','woodDark','navy','core.wear.apron','w.wear.weld_mask','w.tool.wrench',1.16,False),
  ('foreman','施工主管','construction','ink','navy','w.wear.safety_vest','w.wear.hardhat','w.tool.clipboard',1.12,False),
  ('driver','公交司机','depot','blue','navy','w.wear.tie','w.wear.driver_hat',None,1.00,False),
  ('mechanic','维修工','depot','cream','navy','w.wear.overall_bib',None,'w.tool.wrench',1.16,True),
  ('biker','摩托骑手','depot','ink','ink',None,'w.wear.helmet',None,.98,False),
  ('logistics-worker','物流工','depot','ink','woodDark','w.wear.safety_vest','w.wear.cap','w.tool.briefcase',1.05,True),
  ('rifleman','步兵','outpost','moss','moss','w.wear.tactical_vest','w.wear.field_helmet','w.tool.rifle',1.07,False),
  ('scout','侦察兵','outpost','moss','woodDark','w.wear.backpack','w.wear.field_helmet',None,.97,False),
  ('medic','医疗兵','outpost','moss','moss','w.wear.tactical_vest','w.wear.field_helmet','w.tool.medkit',1.02,True),
  ('commander','指挥员','outpost','moss','woodDark','w.wear.field_vest','w.wear.driver_hat','w.tool.clipboard',1.13,False),
 ]
 for id,name,theme,shirt,trousers,vest,hat,tool,b,female in roles:
  H=div(Q('height'),1.82);B=Q('build')
  items=[pi('skin','core.human.body',params={'height':Q('height'),'build':B,'grip':bool(tool),'palette':{P['cream']:C(shirt),P['moss']:C(trousers),P['white']:C(shirt)}}),pi('head','core.human.head',parent='skin.rig.head',scale=[H,H,H],params={'jaw_width':.91 if female else 1.01,'face_width':.96 if female else 1}),pi('hair','w.wear.ponytail' if female else 'core.human.hair.short',parent='skin.rig.head',scale=[H,H,H]),pi('belt','core.wear.belt',pos=[0,mul(.986,H),0],scale=[B,H,B])]
  if hat:
   if hat in ['w.wear.helmet','w.wear.weld_mask']:items=[i for i in items if i['id']!='hair']
   items.append(pi('hat',hat,pos=[0,mul(.038 if hat=='w.wear.strawhat' else .018,H),0],rot=[-7,0,0] if hat=='w.wear.strawhat' else None,parent='skin.rig.head',scale=[H,H,H]))
  if vest:
   back=vest=='w.wear.backpack';off=[0,-.02,-.19] if back else [0,-.28,0] if vest=='core.wear.apron' else [0,0,0]
   items.append(pi('outfit',vest,pos=off,parent='skin.rig.chest',scale=[B,H,B],**({'params':paint(wood='cream',woodDark='white')} if id=='chef' else {})))
  if tool:items.append(pi('tool',tool,pos=[0,-.02,.025],parent='skin.rig.handR',rot=[-90,0,0] if tool=='w.tool.rifle' else [0,0,-12]))
  if id in ['rancher','mechanic','commander']:items.append(pi('beard','core.human.beard',parent='skin.rig.head',scale=[H,H,H]))
  wa('world-'+id,name,'body',items,theme=theme,params=schema(height=number(1.74 if female else 1.82,1.64,1.98,'身高',.01,'m'),build=number(b,.92,1.18,'体格')))
  motion=deepcopy(MOTIONS['fnd-adult']);motion['assembly']='world-'+id;MOTIONS['world-'+id]=motion
 # Child is a specific proportion preset with larger head, smaller jaw and a school pack.
 wa('world-child','儿童 · 大头身比与书包','body',[pi('skin','core.human.body',params={'height':1.64,'build':.94,'palette':{P['cream']:P['yellow'],P['moss']:P['navy']}},scale=[.70,.70,.70]),pi('head','core.human.head',parent='skin.rig.head',scale=[1.16,1.16,1.16],params={'jaw_width':.9,'nose_length':.90}),pi('hair','core.human.hair.short',parent='skin.rig.head',scale=[1.16,1.16,1.16]),pi('pack','w.wear.backpack',parent='skin.rig.chest',pos=[0,-.04,-.16],scale=[.77,.77,.77])],theme='home')
 motion=deepcopy(MOTIONS['fnd-adult']);motion['assembly']='world-child';MOTIONS['world-child']=motion
