"""Orbital modules use compatible real openings, never a recoloured house shell."""
from .common import *
from worlds.industry import linear

def author():
 # Eight-sided pressure cabin: six glazed panels, one solid service panel and
 # one true walk-through opening. Door and windows have actual perimeter depth.
 frame=[[-.68,0],[.68,0],[.68,1.44],[.52,1.70],[-.52,1.70],[-.68,1.44]]
 aperture=[[-.49,.05],[.49,.05],[.49,1.36],[.36,1.51],[-.36,1.51],[-.49,1.36]]
 fp('p5.habitat.door_panel','基地舱入口壁 · 压力壳与标准净开口','arch',[extrude(frame,.105,'space',holes=[aperture]),*[box([.052,1.27,.023],'amber',[x,.77,.068],bevel=.007) for x in [-.568,.568]]],[1.38,1.72,.15],theme='space',material='mat.paint',ports=[port('interface',[0,0,.052],(0,0,1),interface='habitat.hatch.1m.v1')])
 fp('p5.habitat.window_panel','舱壁窗单元 · 厚框/舷窗/底裙','arch',[
  extrude(frame,.09,'space',holes=[[[-.46,.53],[.46,.53],[.46,1.31],[.35,1.46],[-.35,1.46],[-.46,1.31]]]),
  extrude([[-.49,.50],[.49,.50],[.49,1.33],[.36,1.50],[-.36,1.50],[-.49,1.33]],.028,'alloy',holes=[[[-.42,.59],[.42,.59],[.42,1.30],[.32,1.41],[-.32,1.41],[-.42,1.30]]],position=[0,0,.066]),
  poly([[-.418,.59,.070],[.418,.59,.070],[.418,1.30,.070],[.32,1.407,.070],[-.32,1.407,.070],[-.418,1.30,.070]],[[0,1,2,3,4,5]],'glass',material='mat.vehicleGlass'),
  box([.88,.077,.026],'amber',[0,.23,.062],bevel=.01)
 ],[1.38,1.73,.14],theme='space',material='mat.paint')
 fp('p5.habitat.roof','舱顶 · 径向大切面与设备接口','arch',[lathe([[1.67,.0],[1.65,.16],[1.22,.53],[.50,.69],[.50,.79]],'space',8,cap=True),lathe([[.52,.70],[.52,.81]],'alloy',12,cap=True),box([.19,.047,1.17],'amber',[0,.48,.85],bevel=.008,rotation=[-21,0,0])],[3.4,.84,3.4],theme='space',material='mat.paint')
 fp('p5.habitat.floor','舱底 · 八角平台与下部保护裙','arch',[lathe([[1.63,0],[1.77,.16],[1.73,.32]],'alloy',8,cap=True),lathe([[1.69,.31],[1.69,.38]],'space',8,cap=True),*[box([.20,.16,.31],'amber',[math.sin(a)*1.62,.19,math.cos(a)*1.62],bevel=.013,rotation=[0,i*45,0]) for i,a in enumerate([i*math.pi/4 for i in range(8)])]],[3.6,.41,3.6],theme='space',material='mat.paint',level=2)
 fp('p5.habitat.air_tank','生命支持瓶组 · 护架/气瓶/阀门','props',[
  *[lathe([[.12,0],[.17,.1],[.17,.74],[.12,.86],[.065,.89]],'space',10,cap=True,position=[x,0,0]) for x in [-.215,.215]],
  *[lathe([[.176,y],[.176,y+.09]],'alloy',10,cap=True,position=[x,0,0]) for x in [-.215,.215] for y in [.17,.65]],box([.70,.08,.44],'shadow',[0,.04,0],bevel=.018),*[disk(.062,.022,'amber',[x,.927,0],8) for x in [-.215,.215]]
 ],[.78,.95,.46],theme='space',material='mat.paint',level=2)
 fp('p5.space.antenna','科考天线 · 稳固基座与多频振子','props',[box([.48,.19,.48],'alloy',[0,.095,0],bevel=.026),rod([0,.15,0],[0,2.15,0],.032,'alloy',r2=.018,sides=7),*[box([.085,.76,.10],'space',[x,y,0],bevel=.015) for x,y in [(-.19,1.19),(.19,1.48)]],disk(.035,.062,'amber',[0,2.2,0],10,material='mat.emissive.amber'),*[rod([-.21,y,0],[.21,y,0],.013,'alloy',sides=6) for y in [.66,.92,1.80]]],[.58,2.27,.51],theme='space',material='mat.metal',level=2)
 room=[pi('floor','p5.habitat.floor'),pi('roof','p5.habitat.roof',[0,2.06,0])]
 for i in range(8):
  a=i*math.pi/4;room.append(pi('wall'+str(i),'p5.habitat.door_panel' if i==0 else 'p5.habitat.window_panel',[math.sin(a)*1.55,.38,math.cos(a)*1.55],rot=[0,i*45,0]))
 room.append(pi('antenna','p5.space.antenna',[0,2.86,0],scale=[.55,.55,.55]))
 fa('world-habitat','八角居住舱 · 舷窗与标准对接舱口','arch',room,'space')
 ASSEMBLIES['world-habitat']['exports']=[{'id':'port','node':'wall0','socket':'interface'}]
 # Corridor mouth and base line are expressed in the exact same dock frame.
 fp('p5.airlock.tube','气闸通道 · 连续内壁与贯通口','arch',[extrude(frame,1.35,'space',holes=[aperture]),*[extrude(frame,.046,'alloy',holes=[aperture],position=[0,0,z]) for z in [-.696,.696]],*[box([.075,.42,1.38],'amber',[x,.80,0],bevel=.01) for x in [-.723,.723]],box([.91,.044,1.40],'alloy',[0,.059,0],bevel=.008)],[1.51,1.74,1.46],theme='space',material='mat.paint',level=2,ports=[port('back',[0,0,-.719],(0,0,-1),interface='habitat.hatch.1m.v1'),port('front',[0,0,.719],(0,0,1),interface='habitat.hatch.1m.v1')])
 fp('p5.airlock.door_leaf','气密滑门 · 半扇门与边缘锁扣','arch',[extrude([[0,.045],[.478,.045],[.478,1.35],[.35,1.5],[0,1.5]],.050,'alloy'),box([.09,.37,.031],'amber',[.20,.81,.04],bevel=.012),box([.22,.09,.02],'cyan',[.23,1.22,.038],bevel=.006,material='mat.display')],[.5,1.51,.1],theme='space',material='mat.paint',anchor='hinge')
 fp('p5.airlock.door_left','气闸左门 · 镜像控制点','arch',[],[.5,1.51,.1],theme='space',anchor='hinge',components=[component('leaf','p5.airlock.door_leaf',mirror='x')],material='mat.paint')
 fp('p5.space.steps','模块入口踏步 · 网格踏面/双侧护边','props',[box([1.16,.12,.34],'alloy',[0,.06,.57],bevel=.009),box([1.16,.23,.34],'alloy',[0,.115,.24],bevel=.009),box([1.16,.35,.34],'alloy',[0,.175,-.09],bevel=.009),*[box([.047,.05,1.04],'amber',[x,.055,.25],bevel=.007) for x in [-.59,.59]],*[box([.94,.008,.015],'space',[0,y,z],bevel=.002) for y,z in [(.124,.51),(.234,.18),(.354,-.14)]]],[1.25,.38,1.08],theme='space',material='mat.metal',level=2)
 fa('kit-airlock','气闸子装配 · 双滑门与两端插槽','arch',[pi('tube','p5.airlock.tube'),pi('left','p5.airlock.door_left',[0,0,.756]),pi('right','p5.airlock.door_leaf',[0,0,.756])],'space',level=2,metadata=controls(linear('left','左门开度','left',-.52,0,(1,0,0)),linear('right','右门开度','right',0,.52,(1,0,0))))
 ASSEMBLIES['kit-airlock']['exports']=[{'id':'back','node':'tube','socket':'back'},{'id':'front','node':'tube','socket':'front'}]
 fa('world-airlock','独立气闸模块','arch',[ai('airlock','kit-airlock',[0,.38,0]),pi('steps','p5.space.steps',[0,0,1.07])],'space',metadata=controls(linear('left','左门开度','airlock.left',-.52,0,(1,0,0)),linear('right','右门开度','airlock.right',0,.52,(1,0,0))))
 # Real socket placement demonstrates interface reuse: no hidden hand-aligned offset.
 station=[ai('room','world-habitat'),ai('lock','kit-airlock',attach={'target':'room','socket':'port','own':'back','mode':'opposed'})]
 fa('world-habitat-docked','居住舱＋气闸 · 实际接口吸附示例','arch',station,'space',metadata=controls(linear('left','左气闸门','lock.left',-.52,0,(1,0,0)),linear('right','右气闸门','lock.right',0,.52,(1,0,0))))
 # Laboratory panels are a distinct taller viewing wall, with interior benches.
 fp('p5.lab.workbench','实验台 · 设备盒/操作台/样品位','interior',[box([1.20,.11,.49],'alloy',[0,.80,0],bevel=.021),*[box([.085,.77,.32],'space',[x,.385,0],bevel=.012) for x in [-.49,.49]],box([.41,.37,.16],'shadow',[.27,1.04,-.13],bevel=.022),box([.33,.23,.016],'cyan',[.27,1.065,-.037],bevel=.007,material='mat.display'),*[lathe([[.043,0],[.047,.21],[.031,.24]],'space',8,cap=True,position=[x,.86,.08]) for x in [-.41,-.27,-.13]]],[1.24,1.28,.59],theme='space',material='mat.paint',level=2)
 lab=[pi('floor','p5.habitat.floor'),pi('roof','p5.habitat.roof',[0,2.24,0],scale=[1,1,1]),pi('labA','p5.lab.workbench',[-.54,.38,-.72],rot=[0,-30,0]),pi('labB','p5.lab.workbench',[.64,.38,-.63],rot=[0,30,0])]
 for i in [0,1,2,3,4,5,6,7]:
  a=i*math.pi/4;lab.append(pi('panel'+str(i),'p5.habitat.door_panel' if i==0 else 'p5.habitat.window_panel',[math.sin(a)*1.55,.38,math.cos(a)*1.55],rot=[0,i*45,0],scale=[1,1.105,1]))
 fa('world-laboratory','观测实验舱 · 大窗壁与内部实验台','arch',lab,'space')
 fp('p5.power.solar_panel','太阳能板 · 边框/背板/分块电池','props',[box([1.76,.045,1.20],'alloy',[0,0,0],bevel=.016),*[box([.257,.011,.35],'solar',[x,.030,z],bevel=.003) for x in [-.70,-.42,-.14,.14,.42,.70] for z in [-.39,0,.39]],*[box([.008,.002,1.07],'space',[x,.037,0],bevel=.0006) for x in [-.58,-.30,-.02,.26,.54]]],[1.80,.08,1.24],theme='space',anchor='center',material='mat.panel_solar',ports=[port('hinge',[0,0,0],interface='solar.hinge.v1')])
 fp('p5.power.solar_stand','光伏支架 · 稳定三角撑','props',[*[beam([x,0,-.40],[x,.70,0],.045,.045,'alloy') for x in [-.64,.64]],*[beam([x,0,.4],[x,.70,0],.045,.045,'alloy') for x in [-.64,.64]],rod([-.70,.70,0],[.70,.70,0],.031,'alloy',sides=8)],[1.45,.75,.85],theme='space',material='mat.metal')
 fa('world-solar-array','太阳能阵列 · 可调俯仰面板','props',[pi('stand','p5.power.solar_stand'),pi('panel','p5.power.solar_panel',[0,.75,0],rot=[30,0,0])],'space',metadata=controls(turn('tilt','太阳能板俯仰','panel',-20,35,(1,0,0))))
 fp('p5.space.dish','远程通信碟 · 凹面/馈源/边圈','mech',[lathe([[0,0],[.35,.04],[.67,.19],[.94,.40],[.95,.46],[.65,.24],[.33,.09],[0,.035]],'space',16,closed_profile=True),*[rod([math.sin(a)*.75,.22,math.cos(a)*.75],[0,1.05,0],.018,'alloy',sides=6) for a in [0,2.0944,4.1888]],disk(.076,.18,'amber',[0,1.0,0],10)],[1.97,1.2,1.97],theme='space',anchor='center',material='mat.paint',level=2)
 fa('world-space-dish','月面通信碟 · 含俯仰支架','mech',[pi('base','w.outpost.radar_base',params={'palette':{P['moss']:P['space']}}),pi('dish','p5.space.dish',[0,1.40,0],rot=[50,0,0],parent='base')],'space',metadata=controls(turn('azimuth','方位角','base',-180,180),turn('tilt','俯仰微调','dish',-22,22,(1,0,0))))
 fp('p5.space.beacon','航标灯 · 三脚架/发光柱/防护笼','props',[lathe([[.14,.26],[.14,.67]],'alloy',10,cap=True),*[beam([0,.40,0],[math.sin(a)*.30,0,math.cos(a)*.30],.055,.055,'alloy') for a in [0,2.0944,4.1888]],box([.16,.40,.16],'amber',[0,.87,0],bevel=.028,material='mat.emissive.amber'),lathe([[.16,1.07],[.16,1.12]],'space',10,cap=True),*[rod([x,.65,z],[x,1.10,z],.013,'alloy',sides=5) for x in [-.105,.105] for z in [-.105,.105]]],[.68,1.16,.66],theme='space',material='mat.paint',level=2)
 fa('world-space-beacon','科考航标灯','props',[pi('lamp','p5.space.beacon')],'space')
 single('supply-crate','科考物资箱 · 护角与锁扣','props',[box([.95,.54,.65],'space',[0,.29,0],bevel=.039),box([1.01,.08,.69],'alloy',[0,.59,0],bevel=.017),*[box([.045,.50,.035],'amber',[x,.32,.344],bevel=.006) for x in [-.30,.30]],box([.16,.09,.024],'shadow',[0,.37,.349],bevel=.01),*[box([.068,.22,.048],'alloy',[x,.5,.364],bevel=.007) for x in [-.35,.35]]],[1.07,.68,.75],'space',material='mat.paint')
 fa('world-oxygen-tanks','生命支持气瓶组','props',[pi('tanks','p5.habitat.air_tank')],'space')
 single('landing-pad','月面着陆平台 · 厚度/航标/降落识别','terrain',[box([4.40,.20,4.20],'alloy',[0,.10,0],bevel=.08),box([4.21,.024,4.01],'shadow',[0,.215,0],bevel=.07),lathe([[1.47,0],[1.54,0],[1.54,.006],[1.47,.006]],'amber',32,closed_profile=True,position=[0,.232,0]),box([.13,.006,1.13],'space',[-.37,.237,0],bevel=.003),box([.13,.006,1.13],'space',[.37,.237,0],bevel=.003),box([.67,.006,.13],'space',[0,.237,0],bevel=.003),*[disk(.095,.07,'amber',[x,.25,z],10,material='mat.emissive.amber') for x in [-1.90,1.90] for z in [-1.81,1.81]]],[4.5,.34,4.3],'space',material='mat.paint')
 fp('p5.terrain.crater','月面陨坑 · 低洼坑底与非圆整唇缘','terrain',crater(),[2.84,.40,2.67],theme='space',material='mat.stone',level=2)
 fa('world-crater','月面陨坑','terrain',[pi('crater','p5.terrain.crater')],'space')
 vehicles();crew()

def crater():
 rings=[]
 for r,y in [(1.36,.0),(1.08,.24),(.83,.19),(.48,-.18),(.09,-.20)]:
  rings.append([[math.sin(a)*r*(1+.04*math.sin(i*3.1)),y+(.027*math.cos(i*2.7) if r>.1 else 0),math.cos(a)*r] for i,a in enumerate([k*math.pi/8 for k in range(16)])])
 ps=sum(rings,[]);faces=[]
 for j in range(4):
  for i in range(16):faces.append([j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i])
 faces.append(list(range(64,80)))
 return [poly(ps,faces,'stone')]

def vehicles():
 fp('p5.rover.chassis','月球车底盘 · 中央箱梁与开放踏板','vehicle',[box([1.15,.19,2.05],'alloy',[0,.54,0],bevel=.035),box([1.11,.25,.73],'space',[0,.76,.64],bevel=.065),box([1.13,.33,.53],'space',[0,.83,-.81],bevel=.045),*[box([.32,.06,.83],'alloy',[x,.56,-.07],bevel=.018) for x in [-.66,.66]],box([.76,.16,.055],'shadow',[0,.80,1.026],bevel=.014),*[box([.17,.11,.032],'cyan',[x,.89,1.024],bevel=.014,material='mat.display') for x in [-.41,.41]],box([.30,.02,.36],'amber',[0,.90,.63],bevel=.01)],[1.72,1.03,2.10],theme='space',material='mat.paint',level=2)
 fp('p5.rover.seat','科考车座椅 · 一体软垫与金属靠背','vehicle',[box([.42,.12,.42],'shadow',[0,.06,0],bevel=.04),box([.41,.49,.10],'shadow',[0,.33,-.19],bevel=.034,rotation=[-8,0,0]),box([.31,.022,.14],'alloy',[0,-.023,0],bevel=.01)],[.46,.63,.48],theme='space',material='mat.rubber')
 fp('p5.rover.suspension','月球车摆臂 · 主梁与轮毂铰接','vehicle',[beam([0,.54,0],[.65,.41,0],.09,.08,'alloy'),disk(.08,.17,'amber',[.62,.41,0],10,rotation=[0,0,90],material='mat.paint')],[.76,.26,.20],theme='space',material='mat.metal')
 fp('p5.rover.wheel','越野月面轮 · 斜肩/宽胎/辐毂','vehicle',[lathe([[.31,-.16],[.39,-.12],[.40,.10],[.33,.16],[.19,.16],[.19,-.16]],'rubber',16,closed_profile=True,rotation=[0,0,90],material='mat.rubber'),disk(.215,.34,'alloy',sides=12,rotation=[0,0,90]),disk(.08,.361,'amber',sides=10,rotation=[0,0,90],material='mat.paint'),*[box([.28,.025,.067],'shadow',[0,math.cos(a)*.397,math.sin(a)*.397],bevel=.004,rotation=[i*22.5,0,0]) for i,a in enumerate([i*math.pi/8 for i in range(16)])]],[.38,.83,.83],theme='space',anchor='center',material='mat.metal',level=2)
 fp('p5.rover.controls','驾驶操纵件 · 仪表屏/把手/天线','vehicle',[rod([0,0,0],[0,.39,-.08],.032,'alloy',sides=7),box([.35,.15,.045],'shadow',[0,.39,-.08],bevel=.016,rotation=[-18,0,0]),box([.27,.078,.015],'cyan',[0,.40,-.048],bevel=.005,rotation=[-18,0,0],material='mat.display'),rod([-.19,.29,-.015],[.19,.29,-.015],.021,'shadow',sides=7),rod([.48,0,.38],[.48,1.26,.38],.014,'alloy',sides=6),box([.024,.085,.02],'amber',[.48,1.28,.38],bevel=.005)],[.74,1.35,.48],theme='space',material='mat.metal',level=2)
 rover=[pi('chassis','p5.rover.chassis'),pi('seatL','p5.rover.seat',[-.26,.68,-.25]),pi('seatR','p5.rover.seat',[.26,.68,-.25]),pi('controls','p5.rover.controls',[0,.80,.46])]
 for i,z in enumerate([-.77,.70]):
  for sg in [-1,1]:
   rover += [pi('arm'+str(i)+str(sg),'p5.rover.suspension',[0,0,z],rot=[0,0 if sg>0 else 180,0]),pi('wheel'+str(i)+str(sg),'p5.rover.wheel',[sg*.79,.40,z])]
 fa('world-moon-rover','双座月球车 · 四轮独立摆臂与开放车架','vehicle',rover,'space',metadata=controls({'id':'steering','title':'前轮转向','nodes':['wheel11','wheel1-1'],'axis':[0,1,0],'min':-25,'max':25,'default':0}))
 buggy=deepcopy(rover)
 roll=[*[rod([sg*.57,.64,z],[sg*.57,1.60,z],.035,'alloy',sides=7) for sg in [-1,1] for z in [-.71,.40]],*[rod([-.57,1.60,z],[.57,1.60,z],.035,'alloy',sides=7) for z in [-.71,.40]],*[box([.093,.072,.10],'amber',[x,1.65,.40],bevel=.012,material='mat.emissive.amber') for x in [-.25,0,.25]],box([.75,.045,.53],'alloy',[0,1.57,-.25],bevel=.017)]
 fp('p5.rover.roll_cage','勘探车防滚架 · 顶灯与头部保护','vehicle',roll,[1.24,1.74,1.24],theme='space',material='mat.metal',level=2)
 buggy.append(pi('cage','p5.rover.roll_cage'));buggy.append(ai('case','world-supply-crate',[0,.84,-.73],scale=[.68,.68,.68]))
 fa('world-exploration-buggy','野外勘探车 · 防滚架与采样载具','vehicle',buggy,'space',metadata={'variant_of':'world-moon-rover','variant_not_new_geometry_family':True})
 bot=[pi('body','p5.rover.chassis',scale=[.72,.73,.74]),ai('cargo','world-supply-crate',[0,.61,-.14]),pi('sensor','p5.robot.sensor',[0,.81,.56])]
 for i,z in enumerate([-.63,0,.63]):
  for sg in [-1,1]:bot.append(pi('wheel'+str(i)+str(sg),'p5.rover.wheel',[sg*.59,.27,z],scale=[.76,.67,.67]))
 # Shared sensor and ducted propulsion also used by the cyber quadruped and delivery bot.
 fp('p5.robot.sensor','机器人传感头 · 独立转轴与镜头','robot',[box([.30,.24,.22],'space',[0,.08,0],bevel=.03),box([.21,.15,.021],'shadow',[0,.10,.125],bevel=.014),disk(.051,.023,'cyan',[0,.10,.15],12,rotation=[90,0,0],material='mat.display'),disk(.069,.13,'alloy',[0,-.11,0],10)],[.34,.34,.29],theme='space',anchor='center',material='mat.paint')
 fa('world-cargo-bot','六轮物资机器人 · 平台/载荷/扫描头','robot',bot,'space',metadata=controls(turn('sensor','传感器旋转','sensor',-100,100)))
 fp('p5.drone.duct','导管旋翼 · 空心涵道与三叶桨','robot',[lathe([[.17,-.045],[.21,-.045],[.21,.045],[.17,.045]],'space',16,closed_profile=True),*[poly([[0,.006,0],[.15,.006,-.02],[.16,.006,.025],[.042,.006,.035]],[[0,1,2,3]],'alloy',rotation=[0,i*120,0]) for i in range(3)],disk(.041,.045,'amber',[0,.03,0],10)],[.44,.12,.44],theme='space',anchor='center',material='mat.metal')
 fp('p5.drone.body','公用无人机体 · 菱面躯壳/支臂/脚架','robot',[profile([[0,-.03,0,.14,.18],[0,.13,0,.19,.22],[0,.23,-.04,.12,.15]],'space'),*[beam([sg*.10,.09,z*.3],[sg*.39,.12,z],.044,.037,'alloy') for sg in [-1,1] for z in [-.33,.33]],*[rod([sg*.13,0,0],[sg*.20,-.22,0],.018,'alloy',sides=6) for sg in [-1,1]]],[.84,.48,.74],theme='space',anchor='center',material='mat.paint',level=2)
 fa('world-utility-drone','科考无人机 · 四涵道旋翼与云台','robot',[pi('body','p5.drone.body'),pi('sensor','p5.robot.sensor',[0,-.07,.21],scale=[.68,.68,.68]),*[pi('rotor'+str(i),'p5.drone.duct',[x,.12,z]) for i,(x,z) in enumerate([(-.39,-.33),(.39,-.33),(-.39,.33),(.39,.33)])]],'space',metadata=controls(turn('sensor','云台角度','sensor',-85,85)))

def crew():
 fp('p5.suit.helmet','宇航头盔 · 护颈/外壳/镜面罩','wear',[profile([[0,-.15,0,.13,.126],[0,-.08,-.01,.19,.174],[0,.09,-.025,.202,.184],[0,.23,-.033,.147,.135],[0,.27,-.035,.074,.077]],'space'),box([.31,.245,.105],'shadow',[0,.02,.159],bevel=.068,material='mat.vehicleGlass'),*[disk(.061,.030,'amber',[sg*.206,.045,-.011],10,rotation=[0,0,90],material='mat.paint') for sg in [-1,1]],lathe([[.14,-.20],[.14,-.151]],'alloy',12,cap=True)],[.48,.48,.44],theme='space',anchor='center',material='mat.paint')
 fp('p5.suit.chest','宇航服控制胸甲 · 面板/连接口/护肩','wear',[box([.40,.41,.075],'space',[0,-.01,.159],bevel=.045),box([.23,.16,.025],'alloy',[0,.057,.211],bevel=.015),box([.13,.064,.014],'cyan',[0,.079,.229],bevel=.006,material='mat.display'),*[disk(.031,.025,'amber',[x,-.12,.218],8,rotation=[90,0,0]) for x in [-.103,.103]],*[box([.14,.065,.27],'space',[x,.18,.005],bevel=.025) for x in [-.22,.22]]],[.58,.47,.40],theme='space',anchor='center',material='mat.paint')
 fp('p5.suit.pack','宇航生命保障包 · 瓶体/接口/腰管','wear',[box([.36,.42,.16],'space',[0,0,-.10],bevel=.034),*[lathe([[.058,-.19],[.074,-.14],[.074,.17],[.045,.23]],'space',10,cap=True,position=[x,0,-.20]) for x in [-.102,.102]],box([.27,.064,.021],'amber',[0,.10,-.279],bevel=.012),tube([[-.14,-.16,-.20],[-.23,-.30,-.15],[-.26,-.33,.03],[-.15,-.21,.20]],.019,'alloy',7)],[.59,.62,.55],theme='space',anchor='center',material='mat.paint')
 fp('p5.suit.boot','宇航靴套 · 护踝/强化鞋面/踏底','wear',[profile([[0,-.12,.08,.084,.14],[0,-.01,.07,.085,.145],[0,.10,0,.078,.075]],'space'),box([.177,.038,.29],'shadow',[0,-.145,.073],bevel=.015),box([.17,.04,.10],'amber',[0,.071,.01],bevel=.01)],[.18,.28,.31],theme='space',anchor='center',material='mat.paint')
 suit=[('p5.suit.chest',[0,0,0],[1,1,1],'chest'),('p5.suit.pack',[0,0,-.17],[1,1,1],'chest')]
 mono_role('world-astronaut','舱外宇航员 · 密封头盔与生命保障包','space',suit,'p5.suit.helmet',None,{P['cream']:P['space'],P['white']:P['space'],P['moss']:P['space'],P['skin']:P['shadow'],P['woodDark']:P['shadow']},1.06)
 a=ASSEMBLIES['world-astronaut'];a['instances']=[i for i in a['instances'] if i['id'] not in ['head','hair','beard']]
 for sg in ['L','R']:a['instances'].append(pi('boot'+sg,'p5.suit.boot',parent='skin.rig.foot'+sg))
 # The engineer's open helmet is a separate design from the sealed astronaut.
 mono_role('world-space-engineer','基地工程师 · 科考工装与记录板','space',[('p5.suit.chest',[0,0,0],[1,1,1],'chest')],'w.wear.hardhat','w.tool.clipboard',{P['cream']:P['amber'],P['white']:P['amber'],P['moss']:P['amber']},1.03)
 mono_role('world-space-scientist','科研人员 · 实验制服与采样记录','space',[('w.wear.overall_bib',[0,0,0],[1,1,1],'chest')],None,'w.tool.clipboard',{P['cream']:P['space'],P['white']:P['space'],P['moss']:P['space']},.96)
 mono_role('world-space-security','基地安保 · 封闭护盔与装甲制服','space',[('w.wear.tactical_vest',[0,0,0],[1,1,1],'chest')],'p5.suit.helmet','w.tool.rifle',{P['cream']:P['rust'],P['white']:P['shadow'],P['moss']:P['shadow']},1.10)
 a=ASSEMBLIES['world-space-security'];a['instances']=[i for i in a['instances'] if i['id'] not in ['head','hair','beard']]
