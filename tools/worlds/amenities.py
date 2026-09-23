"""Street furniture, farm utilities and depots share scale and material roles."""
from .common import *

def author():
 bench=[box([1.67,.045,.105],'woodLight',[0,.48,z],bevel=.009,material='mat.wood') for z in [-.15,-.025,.10]]
 bench += [box([1.67,.095,.037],'woodLight',[0,.64+i*.115,-.21],bevel=.009,material='mat.wood') for i in range(3)]
 for x in [-.63,.63]:
  bench += [beam([x,0,.17],[x,.48,.12],.053,.053,'steel'),beam([x,0,-.23],[x,.91,-.235],.053,.053,'steel'),beam([x,.45,-.24],[x,.45,.19],.055,.07,'steel'),beam([x,.66,-.21],[x,.66,.20],.045,.045,'steel')]
 simple('bench','街道长椅 · 独立木条与金属腿架','interior',bench,[1.71,.95,.52],theme='city',material='mat.metal')
 lamp=[box([.30,.24,.30],'stoneDark',[0,.12,0],bevel=.035),loft([[0,.16,0,.075,.075],[0,2.8,0,.040,.040],[0,3.23,.13,.040,.040],[0,3.28,.50,.034,.034]],'steel',8),box([.30,.13,.50],'steel',[0,3.25,.56],bevel=.045),box([.23,.016,.37],'cream',[0,3.176,.56],bevel=.014,material='mat.light')]
 simple('street-lamp','城市路灯','props',lamp,[.39,3.37,.96],theme='city',material='mat.metal')
 traffic=[box([.29,.16,.29],'stoneDark',[0,.08,0],bevel=.02),rod([0,.15,0],[0,2.72,0],.045,'steel',sides=8),box([.29,.81,.23],'ink',[0,2.38,.04],bevel=.034)]
 for col,y in [('red',2.64),('yellow',2.39),('leaf',2.14)]:
  traffic += [disk(.081,.022,col,[0,y,.175],12,rotation=[90,0,0],material='mat.light'),extrude([[-.10,0],[-.10,.10],[.10,.10],[.10,0],[.077,0],[.077,.071],[-.077,.071],[-.077,0]],.17,'ink',position=[0,y,.22])]
 simple('traffic-light','三色交通信号灯','props',traffic,[.35,2.87,.37],theme='city',material='mat.paint')
 wp('w.city.shelter_frame','候车亭骨架 · 立柱与承雨顶','arch',[*[box([.075,2.17,.075],'steel',[x,1.085,z],bevel=.011) for x in [-1.34,1.34] for z in [-.57,.46]],box([2.90,.11,1.36],'steel',[0,2.2,-.055],bevel=.03),*[box([.05,.026,1.25],'metal',[x,2.266,-.055],bevel=.005,material='mat.metal') for x in [-.80,0,.80]]],[2.96,2.32,1.43],material='mat.metal',level=2)
 wp('w.city.shelter_glass','候车亭薄玻璃与端部地图板','arch',[box([2.61,1.90,.018],'glass',[0,1.10,-.564],bevel=.005,material='mat.glass'),box([.018,1.88,.98],'glass',[1.34,1.10,-.035],bevel=.005,material='mat.glass'),box([.027,1.55,.73],'cream',[-1.30,1.21,-.04],bevel=.013),*[beam([-1.279,.64+i*.18,-.25],[-1.279,.85+i*.17,.20],.014,.025,'blue') for i in range(4)]],[2.76,2.08,1.12],material='mat.glass',level=2)
 wa('world-bus-shelter','城市候车亭','arch',[pi('frame','w.city.shelter_frame'),pi('panels','w.city.shelter_glass'),ai('bench','world-bench',[0,0,-.24],scale=[1.20,1,1])],theme='city')
 wp('w.city.bin_body','街道垃圾桶 · 投口与外壳','props',[box([.48,.82,.46],'steel',[0,.43,0],bevel=.045),extrude([[-.25,-.245],[.25,-.245],[.25,.245],[-.25,.245]],.05,'metal',holes=[[[-.13,-.11],[-.13,.11],[.13,.11],[.13,-.11]]],rotation=[90,0,0],position=[0,.88,0]),box([.37,.57,.018],'stoneDark',[0,.42,.24],bevel=.018)],[.53,.94,.53],material='mat.metal',level=2)
 wa('world-trash-bin','街道分类垃圾桶','props',[pi('body','w.city.bin_body')],theme='city')
 mail=[box([.49,.66,.39],'blue',[0,.85,0],bevel=.05),box([.38,.035,.02],'ink',[0,1.0,.21],bevel=.006),*[box([.055,.58,.055],'steel',[x,.29,z],bevel=.008,material='mat.metal') for x in [-.17,.17] for z in [-.11,.11]],box([.24,.12,.012],'cream',[0,.77,.204],bevel=.007),rod([-.12,.83,.216],[0,.76,.216],.005,'blue',sides=4),rod([0,.76,.216],[.12,.83,.216],.005,'blue',sides=4)]
 simple('mailbox','邮政投递箱','props',mail,[.55,1.23,.46],theme='city',material='mat.paint')
 vending=[box([.87,1.84,.71],'red',[0,.92,0],bevel=.045),box([.59,1.14,.020],'ink',[-.075,1.17,.368],bevel=.015),box([.38,.13,.02],'ink',[-.10,.25,.368],bevel=.01),box([.12,.23,.02],'steel',[.325,.93,.37],bevel=.01)]
 for j in range(3):
  vending += [box([.54,.025,.034],'metal',[-.075,.71+j*.32,.395],bevel=.004,material='mat.metal')]
  for i in range(4):
   c=['yellow','teal','blue','cream'][(i+j)%4]
   vending += [lathe([[.035,0],[.035,.13],[.021,.15],[.021,.18]],c,8,cap=True,position=[-.28+i*.137,.73+j*.32,.392])]
 simple('vending-machine','饮料自动售货机','props',vending,[.94,1.89,.80],theme='city',material='mat.paint')
 cafe=[disk(.52,.052,'woodLight',[0,.73,0],20,material='mat.wood'),rod([0,.03,0],[0,.72,0],.041,'steel',sides=8),*[rod([0,.17,0],[math.cos(a)*.35,.025,math.sin(a)*.35],.026,'steel',sides=7) for a in [0,2.094,4.188]]]
 simple('cafe-table','咖啡厅圆桌','interior',cafe,[1.08,.78,1.08],theme='city',material='mat.metal')
 umbrella=[rod([0,.60,0],[0,2.16,0],.019,'metal',sides=8,material='mat.metal')]
 for i in range(8):
  a,b=i*math.pi/4,(i+1)*math.pi/4
  umbrella.append(poly([[0,2.2,0],[math.cos(a)*.77,1.95,math.sin(a)*.77],[math.cos(b)*.77,1.95,math.sin(b)*.77]],[[0,1,2]],'red' if i%2 else 'cream'))
 wp('w.city.parasol','摊车遮阳伞 · 分片篷布','props',umbrella,[1.58,2.24,1.58],material='mat.fabric',level=2)
 cart=[box([1.09,.67,.60],'steel',[0,.70,0],bevel=.045),box([1.18,.057,.70],'metal',[0,1.066,0],bevel=.018,material='mat.metal'),box([.57,.30,.018],'red',[0,.69,.318],bevel=.012),*[disk(.22,.09,'rubber',[x,.23,.0],16,rotation=[0,0,90],material='mat.rubber') for x in [-.57,.57]],*[lathe([[.027,0],[.036,.03],[.033,.15],[.016,.17],[.016,.20]],c,8,cap=True,position=[x,1.095,.02]) for x,c in [(-.23,'red'),(-.08,'yellow')]]]
 wp('w.city.food_cart','移动餐车 · 不锈钢台与储物柜','props',cart,[1.31,1.32,.74],material='mat.metal',level=2)
 wa('world-food-cart','街头餐饮推车','props',[pi('cart','w.city.food_cart'),pi('umbrella','w.city.parasol',[.28,0,0])],theme='city')
 trough=[box([1.77,.06,.68],'woodDark',[0,.18,0],bevel=.012),*[box([1.85,.37,.065],'wood',[0,.36,z],bevel=.015) for z in [-.33,.33]],*[box([.065,.37,.61],'wood',[x,.36,0],bevel=.015) for x in [-.87,.87]],*[box([.085,.30,.085],'woodDark',[x,.15,z],bevel=.012) for x in [-.74,.74] for z in [-.26,.26]],box([1.68,.017,.53],'water',[0,.37,0],bevel=.004,material='mat.water')]
 simple('water-trough','牲畜饮水槽','props',trough,[1.94,.59,.75],theme='farm',material='mat.wood')
 milk=[lathe([[.18,0],[.20,.035],[.20,.48],[.12,.58],[.12,.66]],'metal',12,cap=True),disk(.14,.035,'steel',[0,.68,0],12),*[rod([sg*.12,.59,0],[sg*.26,.55,0],.025,'metal',sides=6) for sg in [-1,1]]]
 simple('milk-can','金属奶罐','props',milk,[.58,.74,.44],theme='farm',material='mat.metal')
 wp('w.farm.cart_wheel','木车轮 · 轮缘与径向辐条','props',[lathe([[.28,-.047],[.34,-.047],[.34,.047],[.28,.047]],'woodDark',16,closed_profile=True,rotation=[0,0,90]),*[rod([0,0,0],[0,math.cos(i*math.pi/4)*.29,math.sin(i*math.pi/4)*.29],.022,'woodLight',sides=5) for i in range(8)],disk(.072,.15,'wood',[0,0,0],10,rotation=[0,0,90])],[.17,.70,.70],anchor='center',material='mat.wood',level=2)
 bed=[box([1.02,.063,1.63],'wood',[0,.58,0],bevel=.016)]
 for y in [.73,.91,1.09]:
  for sg in [-1,1]:bed+=[box([1.04,.15,.045],'wood',[0,y,sg*.81],bevel=.015),box([.045,.15,1.62],'wood',[sg*.515,y,0],bevel=.015)]
 for sg in [-1,1]:bed+=[beam([sg*.40,.51,.61],[sg*.48,.26,2.21],.045,.060,'woodDark')]
 wp('w.farm.cart_bed','木车斗 · 独立围板与拉杆','props',bed,[1.09,1.2,3.05],material='mat.wood',level=2)
 wa('world-wooden-cart','农用木车','props',[pi('bed','w.farm.cart_bed'),*[pi('wheel'+str(i),'w.farm.cart_wheel',[x,.35,z]) for i,(x,z) in enumerate([(-.59,-.51),(.59,-.51),(-.59,.51),(.59,.51)])]],theme='farm')
 # Reusable rectangular canopy, not a separate hand-built scene roof.
 wp('w.depot.canopy','加油站雨棚 · 薄顶与四柱','arch',[box([4.5,.21,2.75],'blue',[0,3.09,0],bevel=.055),box([4.31,.033,2.58],'cream',[0,2.963,0],bevel=.013),*[box([.15,2.97,.15],'stoneLight',[x,1.48,z],bevel=.018) for x in [-1.91,1.91] for z in [-.96,.96]]],[4.63,3.26,2.87],material='mat.paint',level=2)
 wa('world-fuel-canopy','加油站雨棚','arch',[pi('canopy','w.depot.canopy')],theme='depot')
