"""Articulated machinery and functional site infrastructure. Original authored geometry."""
from .common import *
from .vehicles import wheels, wheel_controls

def linear(id,title,node,lo,hi,axis=(0,1,0)):
 return {'id':id,'title':title,'node':node,'axis':list(axis),'min':lo,'max':hi,'default':0,'mode':'translation','unit':'m','step':.02}

def author():
 # A single reusable track assembly with an actual open interior, not black blocks.
 track=[extrude([[-1.36,.02],[1.36,.02],[1.55,.21],[1.55,.48],[1.35,.69],[-1.35,.69],[-1.55,.49],[-1.55,.22]],.37,'rubber',holes=[[[-1.26,.16],[-1.39,.29],[-1.39,.41],[-1.23,.55],[1.23,.55],[1.39,.40],[1.39,.30],[1.26,.16]]],rotation=[0,90,0],material='mat.rubber')]
 for z in [-1.18,-.70,-.23,.23,.70,1.18]:
  track += [disk(.245,.34,'steel',[0,.345,z],12,rotation=[0,0,90]),disk(.11,.384,'metal',[0,.345,z],10,rotation=[0,0,90],material='mat.metal')]
 for z in [-1.28+i*.23 for i in range(12)]:
  track += [box([.42,.035,.10],'steel',[0,.017,z],bevel=.006),box([.42,.035,.10],'steel',[0,.697,z],bevel=.006)]
 wp('w.mech.track','履带总成 · 开口带体与负重轮','mech',track,[.45,.72,3.13],material='mat.metal',level=2)
 wp('w.mech.excavator_deck','挖掘机上车体 · 配重与发动机箱','mech',[box([1.71,.19,2.31],'yellow',[0,.09,0],bevel=.055),box([1.76,.75,.66],'yellow',[0,.43,-.88],bevel=.14),box([.77,.53,.88],'yellow',[.52,.35,-.25],bevel=.06),*[box([.025,.032,.53],'ink',[.926,.29+i*.08,-.30],bevel=.005,material='mat.rubber') for i in range(4)],rod([.63,.58,-.65],[.63,1.11,-.65],.040,'steel',sides=8),disk(.61,.15,'steel',[0,-.095,0],16,material='mat.metal')],[1.90,1.15,2.4],material='mat.paint',level=2)
 cab=[box([.81,.18,1.2],'yellow',[0,.09,0],bevel=.06),box([.83,.10,1.03],'yellow',[0,1.20,-.03],bevel=.025),box([.78,1.05,.065],'yellow',[0,.65,-.58],bevel=.02),poly([[-.39,.19,.59],[.39,.19,.59],[.38,1.18,.48],[-.38,1.18,.48]],[[0,1,2,3]],'glass',material='mat.vehicleGlass')]
 for sg in [-1,1]:
  cab += [poly([[sg*.398,.22,-.48],[sg*.398,.22,.53],[sg*.384,1.15,.44],[sg*.384,1.15,-.48]],[[0,1,2,3]],'glass',material='mat.vehicleGlass'),beam([sg*.39,.16,.58],[sg*.385,1.22,.47],.045,.045,'yellow'),beam([sg*.39,.16,-.53],[sg*.385,1.22,-.53],.043,.043,'yellow')]
 cab += [box([.43,.12,.40],'ink',[0,.50,-.1],bevel=.03),box([.42,.47,.08],'ink',[0,.74,-.25],bevel=.03)]
 wp('w.mech.operator_cab','工程机械驾驶室 · 薄壁框架与斜玻璃','mech',cab,[.87,1.27,1.24],material='mat.paint',level=2)
 wp('w.mech.undercarriage','工程机械中央底盘','mech',[box([1.75,.29,2.21],'steel',[0,.43,0],bevel=.04),disk(.64,.22,'steel',[0,.64,0],16)],[1.8,.79,2.25],material='mat.metal',level=2)
 xs=[pi('under','w.mech.undercarriage'),pi('trackL','w.mech.track',[-1.0,0,0]),pi('trackR','w.mech.track',[1.0,0,0]),pi('deck','w.mech.excavator_deck',[0,.86,0]),pi('cab','w.mech.operator_cab',[-.45,.16,.11],parent='deck'),ai('arm','fnd-excavator-arm',[.47,.16,.55],rot=[0,-90,0],parent='deck')]
 md=deepcopy(ASSEMBLIES['fnd-excavator-arm']['metadata'])
 for c in md['state_controls']:c['node']='arm.'+c['node']
 for c in md['struts']:
  c['node']='arm.'+c['node'];c['from']['node']='arm.'+c['from']['node'];c['to']['node']='arm.'+c['to']['node']
 md['state_controls'].insert(0,turn('slew','上车体回转','deck',-100,100))
 wa('world-excavator','履带挖掘机 · 可回转上车与双液压','mech',xs,theme='construction',metadata=md)
 # Forklift carriage translates along mast local Y. The fork and load are not scaled.
 wp('w.mech.forklift_body','叉车车体 · 后配重与驾驶位','mech',[box([1.22,.47,1.88],'yellow',[0,.66,-.08],bevel=.13),box([1.22,.78,.46],'yellow',[0,.80,-.85],bevel=.10),box([.48,.11,.40],'ink',[0,1.01,-.3],bevel=.03),box([.46,.47,.08],'ink',[0,1.23,-.48],bevel=.03),*[beam([sg*.54,.85,z],[sg*.54,2.07,z],.065,.065,'steel') for sg in [-1,1] for z in [-.71,.30]],box([1.19,.085,1.17],'steel',[0,2.07,-.22],bevel=.025),*[box([.05,.035,.99],'steel',[x,2.09,-.21],bevel=.007) for x in [-.38,0,.38]],rod([0,.91,.26],[0,1.44,.07],.03,'steel',sides=8),lathe([[.12,0],[.15,0],[.15,.025],[.12,.025]],'ink',12,closed_profile=True,position=[0,1.47,.07],rotation=[25,0,0])],[1.26,2.13,1.97],level=2,material='mat.paint')
 wp('w.mech.forklift_mast','叉车门架 · 双槽钢滑轨','mech',[*[box([.115,1.94,.13],'steel',[x,.97,0],bevel=.012) for x in [-.44,.44]],box([.99,.11,.14],'steel',[0,1.88,0],bevel=.01),box([.94,.14,.16],'steel',[0,.10,0],bevel=.01),rod([0,.10,.01],[0,1.81,.01],.024,'metal',sides=8,material='mat.metal')],[1.04,1.97,.18],material='mat.metal',level=2)
 wp('w.mech.fork_carriage','货叉滑架 · 整体刚性 L 形叉齿','mech',[box([.96,.52,.09],'steel',[0,.28,.02],bevel=.018),*[poly([[x-.055,0,.04],[x+.055,0,.04],[x+.055,0,1.07],[x-.055,0,1.07],[x-.055,.064,.04],[x+.055,.064,.04],[x+.055,.027,1.07],[x-.055,.027,1.07]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[3,7,6,2],[0,4,7,3]],'steel') for x in [-.32,.32]]], [1.0,.55,1.09],material='mat.metal',level=2)
 fx=[pi('body','w.mech.forklift_body'),pi('mast','w.mech.forklift_mast',[0,.36,.89]),pi('fork','w.mech.fork_carriage',[0,.035,.13],parent='mast')];wheels(fx,[.58,-.65],width=1.21,r=.29)
 wa('world-forklift','工业叉车 · 门架倾斜与货叉升降','mech',fx,theme='construction',metadata=wheel_controls([turn('tilt','门架倾斜','mast',-6,6,(1,0,0)),linear('lift','货叉升高','fork',0,1.18)]))
 # Mixer drum is a separate node, so rotating the drum never regenerates geometry.
 wp('w.mech.mixer_drum','混凝土搅拌筒 · 环带与锥形进料口','mech',[lathe([[.17,-1.39],[.49,-1.12],[.79,-.76],[.88,-.23],[.87,.33],[.64,.78],[.35,1.11],[.28,1.25]],'cream',16,cap=True,rotation=[78,0,0]),*[lathe([[r,y-.16],[r,y+.16]],'red',16,rotation=[78,0,0]) for y,r in [(-.65,.818),(-.07,.887),(.47,.80)]]], [1.82,1.82,2.91],anchor='center',material='mat.paint',level=2)
 mixer=[pi('frame','w.vehicle.truck_chassis',params={'length':5.15}),pi('cab','w.vehicle.truck_cab',[0,0,1.95]),pi('drum','w.mech.mixer_drum',[0,1.77,-.64]),pi('rear','w.timber.rail',[0,1,-2.4],params={'length':1.9},scale=[1,1,1])]
 # The rear support is metal; it reuses a beam only as an internal geometry dependency.
 mixer[-1]['params']={'palette':{P['wood']:P['steel']}}
 wheels(mixer,[1.93,-.87,-1.91],r=.44)
 wa('world-mixer-truck','混凝土搅拌运输车','mech',mixer,theme='construction',metadata=wheel_controls([turn('drum_rotation','搅拌筒旋转','drum',0,360,(0,math.cos(math.radians(78)),math.sin(math.radians(78))))]))
 wp('w.mech.crane_turret','移动起重机转台与配重','mech',[box([1.98,.43,2.3],'yellow',[0,.23,0],bevel=.065),box([2.04,.53,.5],'yellow',[0,.52,-1.01],bevel=.085),disk(.65,.16,'steel',[0,-.05,0],16)],[2.12,.85,2.37],material='mat.paint',level=2)
 wp('w.mech.crane_boom','起重机主臂 · 箱梁与端部滑轮座','mech',[box([.43,.46,3.35],'yellow',[0,0,1.58],bevel=.045),box([.48,.50,.24],'steel',[0,0,3.20],bevel=.025),*[box([.026,.13,2.82],'orange',[x,.11,1.63],bevel=.006) for x in [-.23,.23]]],[.51,.53,3.49],anchor='hinge',material='mat.paint',level=2)
 wp('w.mech.crane_inner','起重机伸缩臂节','mech',[box([.29,.32,2.72],'yellow',[0,0,1.30],bevel=.02),box([.34,.38,.32],'steel',[0,0,2.58],bevel=.02)],[.36,.40,2.87],anchor='hinge',material='mat.paint',level=2)
 wp('w.mech.crane_hook','起重吊钩 · 开口钩体与滑轮组','mech',[box([.34,.35,.21],'yellow',[0,0,0],bevel=.025),*[poly([[-.16,y,.11],[.16,y-.14,.11],[.16,y-.20,.11],[-.16,y-.06,.11]],[[0,1,2,3]],'red') for y in [.13,-.01]],extrude([[-.05,-.16],[.05,-.16],[.05,-.39],[.15,-.48],[.22,-.41],[.19,-.32],[.27,-.40],[.24,-.52],[.13,-.57],[-.02,-.51],[-.05,-.41]],.08,'steel')],[.53,.76,.26],anchor='center',material='mat.metal',level=2)
 crane=[pi('frame','w.vehicle.truck_chassis',params={'length':5.8}),pi('cab','w.vehicle.truck_cab',[0,0,2.12]),pi('turret','w.mech.crane_turret',[0,.93,-.79]),pi('operator','w.mech.operator_cab',[-.57,.49,.31],parent='turret'),pi('boom','w.mech.crane_boom',[.42,.79,.26],rot=[-33,0,0],parent='turret'),pi('extension','w.mech.crane_inner',[0,0,2.1],parent='boom')]
 wp('w.mech.crane_cable','吊钩垂绳 · 可定长直线索','mech',[rod([0,0,0],[0,neg(Q('length')),0],.012,'steel',sides=6)],[.03,1.1,.03],anchor='center',params=schema(length=number(1.1,.2,4,'绳长',.02,'m')),material='mat.metal')
 crane += [pi('cable','w.mech.crane_cable',[0,0,2.69],rot=[33,0,0],parent='extension'),pi('hook','w.mech.crane_hook',[0,-1.14,0],parent='cable')]
 for sg in [-1,1]:
  for z in [-2.02,.50]:
   wp_id='w.mech.outrigger'
   if wp_id not in PARTS:wp(wp_id,'起重机支腿 · 横梁与支脚','mech',[box([1.36,.15,.16],'yellow',[.60,.62,0],bevel=.022),box([.15,.62,.16],'steel',[1.19,.31,0],bevel=.015),disk(.19,.045,'steel',[1.19,.025,0],10)],[1.42,.72,.42],material='mat.paint',level=2)
   crane += [pi('support'+str(sg)+str(z),wp_id,[sg*.68,0,z],rot=[0,0 if sg==1 else 180,0])]
 wheels(crane,[1.94,.90,-1.18,-2.14],r=.44)
 wa('world-mobile-crane','移动起重机 · 回转与伸缩吊臂','mech',crane,theme='construction',metadata=wheel_controls([turn('slew','吊臂回转','turret',-45,45),linear('extension','臂节伸出','extension',0,1.25,(0,0,1))]),description='吊臂俯仰固定为33°，伸缩与水平回转可调，垂绳保持垂直；不是吊装物理仿真。')
 props()

def props():
 # Cross-theme equipment has one canonical definition and a small shared palette.
 gen=[box([1.15,.88,.73],'yellow',[0,.48,0],bevel=.045),box([1.21,.11,.79],'steel',[0,.09,0],bevel=.026),*[box([.34,.026,.012],'ink',[-.30,.28+i*.061,.373],bevel=.004) for i in range(8)],box([.28,.31,.018],'steel',[.31,.64,.38],bevel=.01),box([.16,.065,.018],'cyan',[.31,.70,.397],bevel=.006,material='mat.display'),rod([.44,.89,-.2],[.44,1.12,-.2],.032,'steel',sides=8)]
 simple('generator','移动发电机','mech',gen,[1.24,1.15,.82],theme='construction',material='mat.paint')
 chest=[box([.77,.87,.48],'red',[0,.52,0],bevel=.02),box([.83,.06,.53],'steel',[0,.97,0],bevel=.012),*[box([.67,.023,.036],'metal',[0,.27+i*.14,.259],bevel=.005,material='mat.metal') for i in range(5)],*[disk(.075,.048,'rubber',[x,.083,z],10,rotation=[0,0,90],material='mat.rubber') for x in [-.31,.31] for z in [-.16,.16]]]
 simple('tool-chest','移动工具柜','interior',chest,[.86,1.01,.56],theme='depot',material='mat.paint')
 scaffold=[*[rod([x,0,z],[x,2.35,z],.03,'metal',sides=7) for x in [-.72,.72] for z in [-.50,.50]]]
 for y in [.18,1.1,2.15]:
  for z in [-.5,.5]:scaffold+=[rod([-.77,y,z],[.77,y,z],.025,'metal',sides=7)]
  for x in [-.72,.72]:scaffold+=[rod([x,y,-.55],[x,y,.55],.025,'metal',sides=7)]
 for z in [-.5,.5]:scaffold+=[rod([-.72,.18,z],[.72,2.15,z],.021,'metal',sides=7),rod([.72,.18,z],[-.72,2.15,z],.021,'metal',sides=7)]
 scaffold+=[box([1.47,.055,.94],'woodLight',[0,1.19,0],bevel=.009,material='mat.wood')]
 simple('scaffold','模块脚手架','arch',scaffold,[1.59,2.4,1.16],theme='construction',material='mat.metal')
 wp('w.site.concrete_block','混凝土砌块 · 双孔实体','arch',[extrude([[-.24,-.12],[.24,-.12],[.24,.12],[-.24,.12]],.23,'stoneLight',holes=[[[-.19,-.075],[-.04,-.075],[-.04,.075],[-.19,.075]],[[.04,-.075],[.19,-.075],[.19,.075],[.04,.075]]],rotation=[90,0,0],position=[0,.12,0])],[.5,.25,.25],material='mat.stone')
 wa('world-concrete-stack','托盘混凝土砌块','props',[ai('pallet','world-pallet'),*[pi('block'+str(i),'w.site.concrete_block',[(i%2-.5)*.50,.16+(i//6)*.24,((i//2)%3-1)*.26]) for i in range(18)]],theme='construction')
 wp('w.site.pipe','预制管 · 真实中空截面','arch',[lathe([[.12,-.63],[.17,-.63],[.17,.63],[.12,.63]],'stoneLight',12,closed_profile=True,rotation=[90,0,0])],[.35,.35,1.27],anchor='center',material='mat.stone')
 wa('world-pipe-stack','预制混凝土管堆','props',[pi('pipe'+str(i),'w.site.pipe',[x,y,0]) for i,(x,y) in enumerate([(-.35,.18),(0,.18),(.35,.18),(-.175,.49),(.175,.49)])],theme='construction')
 wp('w.site.steel_beam','工字钢 · 真实工字截面','arch',[extrude([[-.12,-.14],[.12,-.14],[.12,-.095],[.035,-.095],[.035,.095],[.12,.095],[.12,.14],[-.12,.14],[-.12,.095],[-.035,.095],[-.035,-.095],[-.12,-.095]],2.2,'steel')],[.25,.3,2.21],anchor='center',material='mat.metal')
 wa('world-steel-stack','工字钢料堆','props',[pi('beam'+str(i),'w.site.steel_beam',[(i%3-1)*.26,.16+(i//3)*.30,0]) for i in range(6)],theme='construction')
 wp('w.site.brick','砖块 · 保留硬边的轻倒角','arch',[box([.26,.12,.13],'red',[0,.06,0],bevel=.007)],[.27,.13,.14],material='mat.stone')
 wa('world-brick-stack','托盘砖垛','props',[ai('pallet','world-pallet'),*[pi('brick'+str(i),'w.site.brick',[(i%4-1.5)*.27,.18+(i//20)*.13,((i//4)%5-2)*.15]) for i in range(60)]],theme='construction')
 ladder=[beam([x,0,z],[x,1.65,0],.06,.07,'metal') for x in [-.29,.29] for z in [-.40,.4]]+[beam([-.30,.27+i*.28,.40*(1-(.27+i*.28)/1.65)],[.30,.27+i*.28,.40*(1-(.27+i*.28)/1.65)],.065,.1,'metal') for i in range(5)]+[box([.65,.06,.25],'yellow',[0,1.66,0],bevel=.015)]
 simple('stepladder','折叠检修梯','props',ladder,[.72,1.73,.86],theme='construction',material='mat.metal')
 flood=[rod([0,.1,0],[0,2.34,0],.035,'steel',sides=8),*[rod([0,.5,0],[math.cos(a)*.51,.02,math.sin(a)*.51],.035,'steel',sides=7) for a in [0,2.094,4.188]],rod([-.43,2.25,0],[.43,2.25,0],.031,'steel',sides=7)]
 for x in [-.30,.30]:flood += [box([.42,.30,.10],'yellow',[x,2.38,0],bevel=.025),box([.34,.23,.02],'cream',[x,2.38,.062],bevel=.015,material='mat.light')]
 simple('floodlight','双头工地照明灯','props',flood,[1.12,2.56,1.03],theme='construction',material='mat.paint')
 # Airport-style refuelling and charging infrastructure; generic and unbranded.
 pump=[box([.61,.90,.41],'red',[0,.47,0],bevel=.055),box([.66,.66,.44],'cream',[0,1.23,0],bevel=.045),box([.42,.28,.012],'ink',[0,1.31,.23],bevel=.011),box([.29,.075,.015],'cyan',[0,1.37,.244],bevel=.006,material='mat.display'),box([.85,.075,.64],'stoneLight',[0,.035,0],bevel=.02,material='mat.stone'),*[rod(a,b,.022,'rubber',sides=7,material='mat.rubber') for a,b in zip([[.32,1.34,0],[.48,1.21,0],[.49,.44,0],[.42,.27,.02],[.35,.41,.12]],[[.48,1.21,0],[.49,.44,0],[.42,.27,.02],[.35,.41,.12],[.36,1.04,.12]])],box([.065,.18,.13],'steel',[.36,1.12,.12],bevel=.016)]
 simple('fuel-pump','加油机 · 枪座与软管','props',pump,[1.0,1.60,.67],theme='depot',material='mat.paint')
 ev=[box([.62,1.70,.31],'cream',[0,.88,0],bevel=.09),box([.52,1.43,.02],'pine',[0,.88,.17],bevel=.055),box([.34,.33,.025],'ink',[0,1.26,.193],bevel=.016),box([.27,.22,.028],'cyan',[0,1.27,.21],bevel=.01,material='mat.display'),box([.79,.075,.53],'stoneLight',[0,.038,0],bevel=.025),*[rod(a,b,.021,'rubber',sides=7,material='mat.rubber') for a,b in zip([[.34,1.43,0],[.52,1.23,0],[.51,.40,0],[.39,.32,0]],[[.52,1.23,0],[.51,.40,0],[.39,.32,0],[.35,1.13,.1]])]]
 simple('charging-station','电动车充电桩','props',ev,[1.02,1.77,.56],theme='depot',material='mat.paint')
 lift=[box([.57,.08,.62],'blue',[0,.04,0],bevel=.014),box([.23,2.61,.25],'blue',[0,1.35,0],bevel=.018),box([.09,2.41,.045],'metal',[0,1.3,.148],bevel=.006,material='mat.metal')]
 wp('w.depot.lift_column','维修举升机立柱与滑轨','mech',lift,[.60,2.72,.65],material='mat.paint',level=2)
 wp('w.depot.lift_arm','举升机托臂 · 整体刚性结构','mech',[box([1.0,.09,.11],'yellow',[.48,0,0],bevel=.013),disk(.10,.035,'rubber',[.95,.045,0],10,material='mat.rubber')],[1.09,.13,.24],anchor='hinge',material='mat.paint',level=2)
 lifts=[pi('left','w.depot.lift_column',[-1.4,0,0]),pi('right','w.depot.lift_column',[1.4,0,0]),pi('armL','w.depot.lift_arm',[-1.4,.37,.1]),pi('armR','w.depot.lift_arm',[1.4,.37,.1],rot=[0,180,0])]
 wa('world-repair-lift','双柱汽车举升机','mech',lifts,theme='depot',metadata=controls({'id':'lift','title':'托臂升高','nodes':['armL','armR'],'axis':[0,1,0],'mode':'translation','min':0,'max':1.9,'default':0,'unit':'m','step':.02}))
 # Outpost kit, not ballistic or engineering simulation.
 wp('w.outpost.sandbag','单个沙袋 · 收口与鼓腹截面','props',[loft([[-.34,.11,0,.085,.09],[-.24,.12,0,.14,.17],[.21,.12,0,.15,.165],[.34,.11,0,.09,.095]],'woodLight',8,frame_axis=[1,0,0])],[.70,.28,.34],material='mat.fabric')
 wa('world-sandbags','交错沙袋掩体','props',[pi('bag'+str(i),'w.outpost.sandbag',[(i%3-1)*.68+(i//3%2)*.14,(i//3)*.245,0]) for i in range(9)],theme='outpost')
 tower=[*[beam([x,0,z],[x*.82,2.5,z*.82],.13,.13,'woodDark') for x in [-.73,.73] for z in [-.73,.73]],box([1.50,.10,1.50],'wood',[0,2.39,0],bevel=.014),*[box([1.43,.65,.055],'wood',[0,2.78,sg*.70],bevel=.01) for sg in [-1,1]],*[box([.055,.65,1.39],'wood',[sg*.70,2.78,0],bevel=.01) for sg in [-1,1]],*[beam([x,2.4,z],[x,3.72,z],.085,.085,'woodDark') for x in [-.69,.69] for z in [-.69,.69]],poly([[-.93,3.74,-.93],[.93,3.74,-.93],[.93,3.74,.93],[-.93,3.74,.93],[0,4.13,0]],[[0,4,1],[1,4,2],[2,4,3],[3,4,0]],'woodDark')]
 for y in [.23+i*.27 for i in range(9)]:tower+=[beam([-.28,y,.86],[.28,y,.86],.045,.075,'wood')]
 tower += [beam([x,0,.94],[x,2.55,.83],.065,.065,'woodDark') for x in [-.32,.32]]
 simple('watchtower','木制瞭望塔','arch',tower,[1.92,4.17,2.03],theme='outpost',material='mat.wood')
 wp('w.outpost.dish','扇瓣雷达抛物面 · 凹形薄壳','mech',[lathe([[.0,0],[.23,.014],[.47,.07],[.71,.17],[.94,.32],[.97,.30],[.73,.135],[.49,.035],[.23,-.022],[0,-.03]],'moss',16,closed_profile=True),*[rod([math.cos(a)*.74,.18,math.sin(a)*.74],[0,.70,0],.018,'steel',sides=6,material='mat.metal') for a in [0,2.094,4.188]],box([.12,.21,.12],'steel',[0,.68,0],bevel=.015)],[2,.83,2],anchor='center',material='mat.paint',level=2)
 wp('w.outpost.radar_base','雷达支架与回转台','mech',[box([.84,.57,.83],'moss',[0,.29,0],bevel=.07),disk(.32,.11,'steel',[0,.61,0],12),box([.17,.68,.22],'steel',[0,.96,0],bevel=.025)],[.92,1.36,.92],material='mat.paint',level=2)
 wa('world-radar','可转向雷达天线','mech',[pi('base','w.outpost.radar_base'),pi('dish','w.outpost.dish',[0,1.40,0],rot=[50,0,0])],theme='outpost',metadata=controls(turn('azimuth','方位旋转','base',-180,180),turn('elevation','俯仰微调','dish',-12,12,(1,0,0))))
 # Azimuth root must parent the dish so both move together.
 ASSEMBLIES['world-radar']['instances'][1]['parent']='base'
 mast=[*[rod([x,0,z],[x*.12,3.8,z*.12],.025,'steel',sides=6) for x,z in [(-.3,-.2),(.3,-.2),(0,.32)]],*[rod([-.30*(1-y/4),y,-.2*(1-y/4)],[.30*(1-(y+.5)/4),y+.5,-.2*(1-(y+.5)/4)],.014,'steel',sides=5) for y in [.15+i*.5 for i in range(7)]],rod([0,3.7,0],[0,4.35,0],.025,'steel',sides=8),disk(.32,.06,'cream',[.13,2.65,.13],12,rotation=[90,0,0])]
 simple('communications-mast','前哨通信桅杆','mech',mast,[.67,4.39,.64],theme='outpost',material='mat.metal')
 bunker=[extrude([[-1.12,0],[1.12,0],[1.12,.9],[.85,1.27],[-.85,1.27],[-1.12,.9]],.14,'stone',holes=[[[-.80,.60],[.80,.60],[.80,.76],[-.80,.76]]],position=[0,0,.81]),box([2.02,.18,1.59],'stone',[0,1.24,0],bevel=.07),*[box([.20,1.15,1.64],'stone',[sg*1.03,.575,0],bevel=.045) for sg in [-1,1]],box([2.12,1.13,.20],'stone',[0,.565,-.78],bevel=.06)]
 simple('bunker','混凝土掩体 · 真实观察孔','arch',bunker,[2.30,1.39,1.78],theme='outpost',material='mat.stone')
 simple('ammo-box','前哨储运箱','props',[box([.83,.41,.47],'moss',[0,.23,0],bevel=.025),box([.87,.085,.51],'moss',[0,.47,0],bevel=.016),*[box([.075,.075,.025],'metal',[x,.37,.25],bevel=.008,material='mat.metal') for x in [-.28,.28]],*[box([.045,.26,.027],'yellow',[x,.22,.25],bevel=.007) for x in [-.08,0,.08]]],[.9,.53,.54],theme='outpost',material='mat.paint')
