"""Wheels, an actual wheel-arch car body, pin joints and telescoping cylinders."""
from .common import *
def author():
 r,w=Q('radius'),Q('width')
 tyre=[lathe([[mul(r,.53),mul(w,-.5)],[mul(r,.84),mul(w,-.5)],[mul(r,.97),mul(w,-.37)],[r,mul(w,-.20)],[r,mul(w,.20)],[mul(r,.97),mul(w,.37)],[mul(r,.84),mul(w,.5)],[mul(r,.53),mul(w,.5)]],'rubber',16,closed_profile=True)]
 # Low, wide tread grooves are geometry; not a high-frequency photographic texture.
 for i in range(16):
  a=i*22.5;tyre.append(box([mul(r,.36),mul(w,.86),.009],'rubber',[mul(r,math.sin(math.radians(a))),0,mul(r,math.cos(math.radians(a)))],bevel=.002,rotation=[0,a,0]))
 tire_params=schema(radius=number(.34,.26,.50,'轮胎半径',.01,'m'),width=number(.22,.15,.32,'轮胎宽',.01,'m'))
 part('core.vehicle.tire','轮胎 · 中空侧壁与低频胎面','vehicle',tyre,[.68,.22,.68],anchor='center',params=tire_params,material='mat.rubber',ports=[port('axle',[0,0,0],interface='axle.v1')])
 hub=[lathe([[mul(r,.47),mul(w,-.49)],[mul(r,.62),mul(w,-.49)],[mul(r,.63),mul(w,.49)],[mul(r,.47),mul(w,.49)]],'metal',16,closed_profile=True),lathe([[mul(r,.20),mul(w,-.58)],[mul(r,.20),mul(w,.58)]],'steel',10,cap=True)]
 for sg in [-1,1]:
  for i in range(5):
   a=i*72;hub.append(box([mul(r,.39),.019,.049],'metal',[mul(r,.37*math.cos(math.radians(a))),mul(w,sg*.50),mul(r,.37*math.sin(math.radians(a)))],bevel=.003,rotation=[0,-a,0]))
 part('core.vehicle.hub','轮毂 · 镂空辐条与轴心','vehicle',hub,[.44,.255,.44],anchor='center',params=tire_params,material='mat.metal',ports=[port('axle',[0,0,0],interface='axle.v1')])
 part('core.vehicle.wheel','轮组总成 · 胎 / 毂分材质','vehicle',size=[.26,.69,.69],anchor='center',components=[component('tire','core.vehicle.tire',rotation=[0,0,90],params={'radius':r,'width':w}),component('hub','core.vehicle.hub',rotation=[0,0,90],params={'radius':r,'width':w})],level=2,params=tire_params,material='mat.rubber',ports=[port('axle',[0,0,0],(1,0,0),(0,1,0),interface='axle.v1'),port('contact',[0,neg(r),0],(0,-1,0),interface='ground')])
 trackw=Q('track');assembly('kit-axle','轮轴总成 · 轮距与轮径联动','vehicle',[inst('left','core.vehicle.wheel',pos=[mul(-.5,trackw),r,0],params={'radius':r,'width':.22}),inst('right','core.vehicle.wheel',pos=[mul(.5,trackw),r,0],params={'radius':r,'width':.22})],level=2,params=schema(radius=number(.34,.28,.42,'轮胎半径',.01,'m'),track=number(1.53,1.42,1.67,'轮距',.01,'m')))
 base=Q('wheelbase');rad=Q('wheel_radius');half=mul(.5,base);end=add(half,.63);arc=add(rad,.056);ycenter=rad
 outline=[[neg(end),.33],[neg(end),.85],[add(neg(end),.20),.99],[.56,.99],[sub(end,.18),.86],[end,.68],[end,.33]]
 for center in [half,neg(half)]:
  outline.append([add(center,arc),.33])
  for i in range(9):
   a=i*math.pi/8;outline.append([add(center,mul(arc,math.cos(a))),add(ycenter,mul(arc,math.sin(a)))])
  outline.append([sub(center,arc),.33])
 # Concave extrusion preserves the wheel wells instead of drawing black circles on a block.
 car_params=schema(wheelbase=number(2.46,2.25,2.65,'轴距',.01,'m'),wheel_radius=number(.34,.29,.39,'轮胎半径',.01,'m'))
 part('core.vehicle.body_side','汽车侧围 · 真实前后轮拱','vehicle',[extrude(outline,.075,'blue')],[3.74,.69,.075],anchor='center',params=car_params,material='mat.paint')
 body=[box([1.28,.35,mul(2,end)],'navy',[0,.52,0],bevel=.028,material='mat.rubber'),
  # Hood and rear deck follow distinct heights and overhangs.
  poly([[-.867,.96,.56],[.867,.96,.56],[-.863,.827,end],[.863,.827,end],[-.85,.88,.56],[.85,.88,.56],[-.85,.76,end],[.85,.76,end]],[[0,1,3,2],[0,2,6,4],[1,5,7,3],[2,3,7,6],[4,6,7,5],[0,4,5,1]],'blue'),
  box([1.70,.37,sub(end,.93)],'blue',[0,.80,mul(-.5,add(end,.93))],bevel=.032),
  box([1.78,.155,.14],'navy',[0,.40,add(end,.025)],bevel=.025,material='mat.rubber'),box([1.78,.145,.14],'navy',[0,.40,sub(neg(end),.01)],bevel=.023,material='mat.rubber'),
  box([.69,.115,.023],'ink',[0,.615,add(end,.051)],bevel=.01,material='mat.rubber'),
  *[box([.64,.01,.027],'steel',[0,y,add(end,.067)],bevel=.002,material='mat.metal') for y in [.59,.615,.641]],
  *[box([.28,.14,.034],'cream',[sg*.66,.707,add(end,.019)],bevel=.026,material='mat.light') for sg in [-1,1]],
  *[box([.26,.13,.031],'red',[sg*.658,.734,sub(neg(end),.032)],bevel=.022,material='mat.tailLight') for sg in [-1,1]],
  box([.32,.094,.020],'white',[0,.49,add(end,.105)],bevel=.009),box([.32,.094,.020],'white',[0,.56,sub(neg(end),.06)],bevel=.009)
 ]
 for sg in [-1,1]:
  body += [box([.017,.023,.198],'steel',[sg*.914,.902,-.11],bevel=.004,material='mat.metal'),box([.02,.022,.16],'steel',[sg*.905,.883,-.72],bevel=.004,material='mat.metal')]
 part('core.vehicle.body_center','汽车车身总成 · 底盘 / 机盖 / 灯具','vehicle',body,[1.80,1.02,3.88],level=2,params=car_params,material='mat.paint')
 cabin=[box([1.466,.086,1.36],'blue',[0,1.543,-.368],bevel=.029),
  poly([[-.808,.987,.60],[.808,.987,.60],[.706,1.513,.28],[-.706,1.513,.28]],[[0,1,2,3]],'glass',material='mat.vehicleGlass'),
  poly([[-.82,.995,-1.22],[.82,.995,-1.22],[.707,1.50,-1.035],[-.707,1.50,-1.035]],[[0,3,2,1]],'glass',material='mat.vehicleGlass'),
 ]
 for sg in [-1,1]:
  x=sg*.862;xt=sg*.735
  cabin += [poly([[x,.993,.51],[xt,1.49,.224],[xt,1.49,-.222],[x,1.006,-.235]],[[0,1,2,3]],'glass',material='mat.vehicleGlass'),
   poly([[x,1.006,-.283],[xt,1.49,-.280],[xt,1.49,-.988],[x,1.008,-1.155]],[[0,1,2,3]],'glass',material='mat.vehicleGlass'),
   rod([x,.985,.572],[xt,1.523,.27],.023,'blue',sides=4),rod([x,.985,-1.211],[xt,1.518,-1.025],.026,'blue',sides=4),rod([x,1.003,-.254],[xt,1.51,-.25],.029,'navy',sides=4),
   box([.089,.024,1.63],'blue',[sg*.856,.992,-.334],bevel=.004),
   box([.16,.095,.177],'blue',[sg*.945,1.044,.479],bevel=.022),box([.011,.064,.134],'glass',[sg*1.03,1.046,.481],bevel=.004,material='mat.vehicleGlass')]
 part('core.vehicle.cabin','乘用车座舱 · 倾斜风挡 / 立柱 / 侧窗','vehicle',cabin,[2.08,1.6,1.87],level=2,material='mat.paint')
 items=[inst('body','core.vehicle.body_center',params={'wheelbase':base,'wheel_radius':rad}),inst('sideL','core.vehicle.body_side',pos=[-.866,0,0],rot=[0,-90,0],params={'wheelbase':base,'wheel_radius':rad}),inst('sideR','core.vehicle.body_side',pos=[.866,0,0],rot=[0,-90,0],params={'wheelbase':base,'wheel_radius':rad}),inst('cabin','core.vehicle.cabin'),inst('front',assembly='kit-axle',pos=[0,0,half],params={'radius':rad,'track':1.62}),inst('rear',assembly='kit-axle',pos=[0,0,neg(half)],params={'radius':rad,'track':1.62})]
 assembly('fnd-hatchback','乘用车母版 · 轮拱 / 轮组 / 清晰座舱','vehicle',items,params=car_params,metadata={'state_controls':[{'id':'steering','title':'前轮转向','nodes':['front.left','front.right'],'axis':[0,1,0],'min':-22,'max':22,'default':0,'unit':'°'}]})
 author_excavator()

def author_excavator():
 # Pin components and axial ports are shared by the boom, stick, bucket and cylinders.
 part('core.mech.pin','机械铰轴 · 端帽与钢轴','mech',[
  lathe([[.06,-.19],[.06,.19]],'steel',12,cap=True,rotation=[90,0,0]),
  *[lathe([[.103,-.017],[.103,.017]],'metal',12,cap=True,position=[0,0,sg*.194],rotation=[90,0,0]) for sg in [-1,1]]
 ],[.21,.21,.43],anchor='center',material='mat.metal',ports=[port('axis',[0,0,0],(0,0,1),interface='mechanical.pin.v1')])
 part('core.mech.boom','挖掘机动臂 · 转折箱梁与加强面','mech',[
  extrude([[-.13,-.03],[.10,-.09],[.26,.66],[.20,1.23],[.095,1.72],[-.10,1.76],[-.168,1.48],[-.053,.71]],.25,'yellow'),
  extrude([[-.118,.14],[-.006,.18],[.135,.78],[.099,1.12],[.006,1.13],[.035,.75]],.267,'orange'),
  box([.020,.45,.020],'steel',[.20,.56,.143],bevel=.004,rotation=[0,0,-11],material='mat.metal')
 ],[.44,1.85,.28],material='mat.paint',ports=[port('base',[0,0,0],(0,0,1),interface='mechanical.pin.v1'),port('tip',[0,1.70,0],(0,0,1),interface='mechanical.pin.v1'),port('lift_pin',[.055,.91,.23],(0,0,1),interface='mechanical.pin.v1')])
 part('core.mech.stick','挖掘机小臂 · 收束截面与下铰点','mech',[
  extrude([[-.12,-.08],[.11,-.06],[.18,.27],[.098,.90],[.075,1.39],[-.078,1.40],[-.14,.85]],.22,'yellow'),
  extrude([[-.115,.02],[-.067,.04],[-.067,.90],[-.103,.93]],.236,'orange'),
 ],[.33,1.49,.24],material='mat.paint',ports=[port('base',[0,0,0],(0,0,1),interface='mechanical.pin.v1'),port('tip',[0,1.34,0],(0,0,1),interface='mechanical.pin.v1')])
 # Bucket is an open scoop: two cheeks, curved back and separate cutting teeth.
 cheek=[[-.12,.11],[.10,.13],[.40,-.04],[.46,-.24],[.16,-.30],[-.14,-.20]]
 forms=[extrude(cheek,.034,'steel',position=[0,0,sg*.217]) for sg in [-1,1]]
 for i,(a,b) in enumerate(zip(cheek[-2:]+cheek[:1],cheek[-1:]+cheek[:2])):
  # The rear/bottom walls follow the scoop, leaving the forward mouth visibly open.
  forms.append(poly([[a[0],a[1],-.22],[b[0],b[1],-.22],[b[0],b[1],.22],[a[0],a[1],.22]],[[0,1,2,3]],'steel'))
 forms += [poly([[-.12,.11,-.22],[.10,.13,-.22],[.10,.13,.22],[-.12,.11,.22]],[[0,1,2,3]],'steel')]
 for z in [-.16,-.055,.055,.16]:forms.append(extrude([[.34,-.20],[.51,-.263],[.49,-.302],[.34,-.276]],.064,'metal',position=[0,0,z]))
 part('core.mech.bucket','铲斗 · 开口斗腔 / 侧板 / 斗齿','mech',forms,[.66,.44,.49],anchor='center',material='mat.metal',ports=[port('hinge',[0,0,0],(0,0,1),interface='mechanical.pin.v1')])
 L=Q('length')
 part('core.mech.cylinder_barrel','液压缸体 · 缸筒 / 密封端 / 底耳','mech',[
  lathe([[.073,.058],[.073,sub(L,.04)]],'yellow',12,cap=True),lathe([[.085,sub(L,.065)],[.085,sub(L,.033)]],'metal',12,cap=True,material='mat.metal'),
  lathe([[.041,-.071],[.078,-.071],[.078,.071],[.041,.071]],'yellow',12,closed_profile=True,rotation=[90,0,0]),
  box([.024,mul(L,.60),.025],'steel',[.07,mul(L,.45),0],bevel=.004,material='mat.metal')
 ],[.18,.60,.18],params=schema(length=number(.58,.22,.9,'缸体基准长度',.01,'m')),material='mat.paint',ports=[port('base',[0,0,0],(0,0,1),interface='mechanical.pin.v1')])
 part('core.mech.cylinder_rod','液压活塞杆 · 刚性杆与连接耳','mech',[
  lathe([[.027,0],[.027,sub(L,.055)]],'metal',12,cap=True),lathe([[.035,-.058],[.065,-.058],[.065,.058],[.035,.058]],'steel',12,closed_profile=True,position=[0,L,0],rotation=[90,0,0])
 ],[.135,.70,.13],params=schema(length=number(.67,.27,1.0,'杆长',.01,'m')),material='mat.metal',ports=[port('tip',[0,L,0],(0,0,1),interface='mechanical.pin.v1')])
 assembly('kit-hydraulic-cylinder','液压缸总成 · 缸筒与活塞杆独立','mech',[inst('barrel','core.mech.cylinder_barrel',params={'length':Q('barrel_length')}),inst('piston','core.mech.cylinder_rod',pos=[0,.22,0],params={'length':Q('rod_length')})],level=2,params=schema(barrel_length=number(.58,.22,.9,'缸体长度',.01,'m'),rod_length=number(.67,.27,1.0,'活塞杆长度',.01,'m')))
 part('core.mech.pivot_base','动臂检验基座 · 转台与双耳支座','mech',[
  box([.84,.11,.73],'steel',[0,.061,0],bevel=.025,material='mat.metal'),lathe([[.27,.112],[.27,.19]],'steel',12,cap=True,material='mat.metal'),lathe([[.32,.19],[.32,.26]],'yellow',12,cap=True),
  *[extrude([[-.21,.25],[.22,.25],[.18,.63],[0,.78],[-.18,.61]],.077,'yellow',position=[0,0,sg*.21]) for sg in [-1,1]],
  box([.34,.14,.37],'yellow',[.16,.41,0],bevel=.019)
 ],[.84,.79,.73],material='mat.paint',ports=[port('pivot',[0,.64,0],(0,0,1),interface='mechanical.pin.v1')])
 items=[inst('base','core.mech.pivot_base'),inst('boom','core.mech.boom',pos=[0,.64,0],rot=[0,0,-58]),inst('pinBase','core.mech.pin',pos=[0,.64,0]),inst('stick','core.mech.stick',parent='boom',pos=[0,1.70,0],rot=[0,0,-92]),inst('pinElbow','core.mech.pin',parent='boom',pos=[0,1.70,0]),inst('bucket','core.mech.bucket',parent='stick',pos=[0,1.34,0],rot=[0,0,115]),inst('pinBucket','core.mech.pin',parent='stick',pos=[0,1.34,0],scale=[.75,.75,1.15]),inst('lift',assembly='kit-hydraulic-cylinder',params={'barrel_length':.58,'rod_length':.67}),inst('curl',assembly='kit-hydraulic-cylinder',params={'barrel_length':.52,'rod_length':.62})]
 struts=[{'node':'lift','from':{'node':'base','point':[.18,.40,.235]},'to':{'node':'boom','point':[.055,.91,.235]},'rod':'piston','rod_length':.67,'min_length':.63,'max_length':1.20},{'node':'curl','from':{'node':'boom','point':[.008,1.03,-.235]},'to':{'node':'stick','point':[0,.59,-.235]},'rod':'piston','rod_length':.62,'min_length':.58,'max_length':1.13}]
 controls=[{'id':'boom_raise','title':'动臂角度','node':'boom','axis':[0,0,1],'min':-8,'max':10,'default':0,'unit':'°'},{'id':'stick_fold','title':'小臂折叠','node':'stick','axis':[0,0,1],'min':-12,'max':12,'default':0,'unit':'°'}]
 assembly('fnd-excavator-arm','动臂母版 · 枢轴与双液压实时联动','mech',items,metadata={'struts':struts,'state_controls':controls},description='真实开放铲斗与伸缩油缸。运行状态只更新节点变换，不重建网格；导出保留默认装配和端点约束元数据。')
