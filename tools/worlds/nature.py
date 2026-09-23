"""Clean camp and farm ecology, with planted rather than random composition."""
from .common import *
def author():
 wp('w.nature.pine_tier','针叶冠层 · 有厚度的非对称冠缘','nature',[loft([[0,0,0,.68,.63],[.03,.045,-.02,.76,.70],[.01,.67,0,.075,.064],[0,.77,.01,.012,.012]],'pine',8,variation=.02,frame_axis=[0,1,0])],[1.52,.78,1.4],material='mat.leaf')
 wa('world-pine','分层针叶树','nature',[pi('trunk','core.nature.trunk',scale=[.7,1.18,.7]),*[pi('crown'+str(i),'w.nature.pine_tier',[0,1.0+i*.58,0],rot=[0,i*21,0],scale=[s,s,s]) for i,s in enumerate([1.18,1,.76,.53])]],theme='camp')
 wp('w.nature.grass','草丛 · 克制的宽叶组','nature',[poly([[x,0,z],[x+.048,.10+h,z+.02],[x+.009,.03,z+.055]],[[0,1,2]],'leafLight' if i%2 else 'leafDark') for i,(x,z,h) in enumerate([(-.09,0,.10),(0,.015,.15),(.09,0,.09),(-.01,-.065,.20),(.06,.07,.08)])],[.24,.3,.19],material='mat.leaf')
 wp('w.nature.flower','野花组 · 茎叶与花盘','nature',[rod([0,0,0],[.025,.33,0],.009,'leafDark',sides=5),poly([[0,.10,0],[-.12,.21,.008],[0,.15,.02],[.12,.19,.01]],[[0,1,2],[0,2,3]],'leaf'),*[ico([.075,.035,.072],'yellow',[.025+math.cos(a)*.047,.34,math.sin(a)*.047],0) for a in [i*math.pi/3 for i in range(6)]]], [.19,.37,.19],material='mat.leaf')
 wp('w.nature.mushroom','蘑菇 · 柄与厚伞缘','nature',[lathe([[.033,0],[.039,.17],[.055,.19]],'cream',8,cap=True),lathe([[.02,.28],[.067,.263],[.13,.185],[.125,.17],[.031,.185]],'red',10,closed_profile=True),*[ico([.028,.013,.025],'cream',[x,.235,z],0) for x,z in [(-.047,0),(.035,.031),(.01,-.049)]]],[.27,.28,.27],material='mat.matte')
 wa('world-mushrooms','林下蘑菇簇','nature',[pi('large','w.nature.mushroom'),pi('small','w.nature.mushroom',[.19,0,.03],scale=[.7,.7,.7]),pi('grass','w.nature.grass',[-.15,0,0])],theme='camp')
 wp('w.nature.log','原木 · 树皮与切面年轮','nature',[lathe([[.20,-.60],[.215,-.35],[.20,.60]],'woodDark',9,cap=True,position=[0,.22,0],rotation=[90,0,0]),*[disk(.174,.015,'woodLight',[0,.22,sg*.609],9,rotation=[90,0,0]) for sg in [-1,1]],*[lathe([[.105,-.005],[.12,-.005],[.12,.005],[.105,.005]],'wood',9,closed_profile=True,position=[0,.22,sg*.62],rotation=[90,0,0]) for sg in [-1,1]]],[.44,.45,1.25],material='mat.wood')
 wa('world-log','林地倒木','nature',[pi('log','w.nature.log')],theme='camp')
 wp('w.nature.stump','树桩 · 根盘与截面','nature',[loft([[0,0,0,.34,.32],[0,.14,0,.24,.25],[.035,.47,0,.195,.20]],'woodDark',9),disk(.18,.018,'woodLight',[.035,.48,0],9),*[rod([0,.1,0],[math.cos(a)*.40,.01,math.sin(a)*.38],.09,'woodDark',.018,5) for a in [.1,1.7,3.5,5.0]]],[.81,.5,.81],material='mat.wood')
 wa('world-stump','伐木树桩','nature',[pi('stump','w.nature.stump')],theme='camp')
 wp('w.camp.tent_shell','帐篷篷布 · 双坡厚边与敞开入口','props',[poly([[-1,0,-1.2],[0,1.47,-1.2],[1,0,-1.2],[-1,0,1.2],[0,1.47,1.2],[1,0,1.2]],[[0,3,4,1],[1,4,5,2],[0,1,2]],'cream'),poly([[-1,0,1.205],[0,1.47,1.205],[-.62,.14,1.27]],[[0,1,2]],'woodLight'),poly([[1,0,1.205],[.62,.14,1.27],[0,1.47,1.205]],[[0,1,2]],'woodLight')],[2,1.5,2.47],material='mat.fabric',level=2)
 tent=[pi('canopy','w.camp.tent_shell')]
 for z in [-1.2,1.2]:tent+=[pi('pole'+str(z).replace('-','n').replace('.','_'),'w.timber.post',[0,0,z],params={'height':1.54},scale=[.5,1,.5])]
 wp('w.camp.tent_rope','帐篷拉绳与地钉','props',[rod([0,1.4,0],[0,.04,.75],.012,'woodLight',sides=5),rod([0,0,.78],[0,.17,.73],.018,'woodDark',sides=5)],[.04,1.42,.81],material='mat.fabric')
 tent += [pi('rope','w.camp.tent_rope',[0,0,1.24]),pi('ropeBack','w.camp.tent_rope',[0,0,-1.24],rot=[0,180,0])]
 wa('world-tent','冒险者帐篷','props',tent,theme='camp')
 wp('w.camp.flame','营火焰芯 · 非随机折面','props',[loft([[0,0,0,.16,.15],[.02,.18,0,.14,.13],[-.03,.34,.025,.07,.07],[.06,.57,0,.005,.005]],'orange',6),loft([[0,.02,.05,.08,.07],[-.03,.21,.05,.075,.06],[0,.4,.04,.005,.005]],'yellow',5)],[.32,.57,.3],material='mat.emissive.amber')
 fire=[pi('log'+str(i),'w.nature.log',[0,.035,0],rot=[0,i*60,0],scale=[.43,.43,.70]) for i in range(3)]
 fire += [pi('stone'+str(i),'core.nature.rock', [math.cos(i*math.pi/5)*.5,.025,math.sin(i*math.pi/5)*.5],scale=[.24,.23,.24]) for i in range(10)] if 'core.nature.rock' in PARTS else []
 if not fire[3:]:
  wp('w.camp.fire_ring','营火石圈 · 排列围护石','props',[ico([.24,.20,.22],'stone',[math.cos(i*math.pi/5)*.49,.08,math.sin(i*math.pi/5)*.49],0,seed=i) for i in range(10)],[1.22,.2,1.22],material='mat.stone',level=2);fire.append(pi('ring','w.camp.fire_ring'))
 fire.append(pi('flame','w.camp.flame',[0,.20,0]));wa('world-campfire','石圈营火','props',fire,theme='camp')
 # A deck with repeated registered boards, rails and piers; no painted plank texture.
 bridge=[]
 for i in range(10):bridge.append(pi('deck'+str(i),'core.props.plank',[0,.32,-1.4+i*.30],rot=[90,0,0],params={'length':1.6,'width':.275,'thickness':.09}))
 for x in [-.66,.66]:
  bridge.append(pi('beam'+str(x).replace('.','_').replace('-','n'),'core.props.plank',[x,.22,0],rot=[0,90,0],params={'length':3.0,'width':.16,'thickness':.20}))
  for z in [-1.45,1.45]:bridge.append(pi('post'+str(x)+str(z),'w.timber.post',[x,0,z],params={'height':1.0}))
 for side in [-1,1]:bridge.append(pi('rail'+str(side),'w.timber.rail',[side*.74,.86,0],rot=[0,90,0],scale=[1.46,1,1]))
 wa('world-bridge','木栈桥 · 桥板与下承梁','props',bridge,theme='camp')
 # Low-frequency agriculture assets.
 wp('w.farm.crop_plant','蔬菜株 · 叶柄与宽叶','nature',[rod([0,0,0],[0,.26,0],.018,'leafDark',sides=5),*[poly([[0,.09,0],[math.cos(a)*.20,.25,math.sin(a)*.20],[math.cos(a+.35)*.16,.14,math.sin(a+.35)*.16]],[[0,1,2]],'leaf' if i%2 else 'leafLight') for i,a in enumerate([i*math.pi/3 for i in range(6)])]],[.44,.3,.44],material='mat.leaf')
 wp('w.farm.crop_soil','菜畦 · 垄沟与边沿','terrain',[box([2.5,.16,1.7],'soil',[0,.08,0],bevel=.07),*[box([.20,.065,1.50],'woodDark',[x,.177,0],bevel=.027) for x in [-.92,-.31,.31,.92]]],[2.5,.22,1.7],material='mat.stone')
 patch=[pi('soil','w.farm.crop_soil')]
 for x in [-.92,-.31,.31,.92]:
  for z in [-.54,0,.54]:patch.append(pi('plant'+str(x)+str(z),'w.farm.crop_plant',[x,.20,z],rot=[0,x*32+z*22,0]))
 wa('world-vegetable-patch','蔬菜畦','nature',patch,theme='farm')
 wp('w.farm.wheat_cluster','成熟麦簇 · 茎秆与饱满麦穗','nature',[* [rod([x,0,z],[x,.68,z],.009,'yellow',sides=4) for x,z in [(-.10,0),(0,.08),(.10,0),(0,-.07)]],*[loft([[x,.56,z,.035,.029],[x,.75,z,.046,.031],[x+.02,.84,z,.009,.009]],'yellow',6) for x,z in [(-.10,0),(0,.08),(.10,0),(0,-.07)]]],[.27,.86,.24],material='mat.leaf')
 wa('world-wheat-patch','成熟麦田模块','nature',[pi('soil','w.farm.crop_soil'),*[pi('w'+str(i)+str(j),'w.farm.wheat_cluster',[-1.02+i*.29,.16,-.6+j*.30]) for i in range(8) for j in range(5)]],theme='farm')
 wp('w.farm.hay_bale','方形草捆 · 压实层与捆绳','props',[box([.82,.48,.49],'yellow',[0,.24,0],bevel=.047),*[box([.034,.492,.505],'woodLight',[x,.246,0],bevel=.008) for x in [-.23,.23]],*[box([.775,.008,.012],'#D19B33',[0,y,.252],bevel=.003) for y in [.10,.18,.30,.38]]],[.83,.50,.515],material='mat.fabric')
 wa('world-hay-bales','堆放草捆','props',[pi('a','w.farm.hay_bale',[-.40,0,0]),pi('b','w.farm.hay_bale',[.43,0,0]),pi('c','w.farm.hay_bale',[.02,.50,0])],theme='farm')
 wp('w.farm.fruit','树果 · 低频果实与果蒂','nature',[ico([.16,.18,.16],'red',[0,0,0],1),rod([0,.07,0],[.012,.11,0],.009,'woodDark',sides=4)],[.16,.2,.16],material='mat.leaf',anchor='center')
 wa('world-fruit-tree','果树','nature',[ai('tree','fnd-oak',scale=[.85,.85,.85]),*[pi('apple'+str(i),'w.farm.fruit',p,scale=[1.1,1.1,1.1]) for i,p in enumerate([[-.55,1.8,.52],[.5,2.14,.49],[.08,2.7,.37],[-.35,2.42,.32],[.6,2.35,-.29]])]],theme='farm')
 wp('w.nature.planter','花池 · 中空围边与土层','nature',[box([1.28,.43,.73],'stone',[0,.215,0],bevel=.045),box([1.14,.015,.59],'soil',[0,.435,0],bevel=.025)],[1.28,.45,.73],material='mat.stone')
 wa('world-planter','街道种植池','nature',[pi('base','w.nature.planter'),pi('leaves','core.nature.crown_cluster',[0,.79,0],scale=[.78,.51,.55]),pi('flowers','w.nature.flower',[-.37,.44,.19]),pi('flowers2','w.nature.flower',[.31,.44,.19])],theme='city')
