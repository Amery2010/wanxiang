"""Cross-theme timber, containers, lighting, fences and signage."""
from .common import *
def author():
 h=Q('height');wp('w.timber.post','立柱 · 柱脚与端头倒角','props',[box([.12,h,.12],'wood',[0,mul(.5,h),0],bevel=.014)],[.12,1,.12],params=schema(height=number(1,.3,4.5,'立柱高度',.05,'m')),material='mat.wood')
 wp('w.timber.rail','护栏横梁 · 标准两米接口','props',[box([2,.10,.07],'woodLight',[0,0,0],bevel=.008)],[2,.10,.07],anchor='center',material='mat.wood',ports=[port('left',[-1,0,0],(-1,0,0),(0,1,0),interface='fence.2m.v1'),port('right',[1,0,0],(1,0,0),(0,1,0),interface='fence.2m.v1')])
 wa('world-fence','乡村木护栏','props',[pi('L','w.timber.post',[-1,0,0]),pi('R','w.timber.post',[1,0,0]),pi('top','w.timber.rail',[0,.78,0]),pi('low','w.timber.rail',[0,.39,0])],theme='farm')
 gate=[pi('railTop','w.timber.rail',[1,.74,0],scale=[.92,1,1]),pi('railLow','w.timber.rail',[1,.30,0],scale=[.92,1,1])]
 for x in [.10,.68,1.28,1.9]:gate.append(pi('p'+str(x).replace('.','_'),'w.timber.post',[x,.12,0],scale=[.8,.84,.8]))
 wp('w.fence.gate_brace','栅门斜撑 · 铰轴局部件','props',[beam([.10,.2,.047],[1.92,.85,.047],.09,.065,'woodDark')],[1.92,.85,.12],material='mat.wood')
 wa('kit-rural-gate-leaf','木栅门扇总成','props',gate+[pi('brace','w.fence.gate_brace')],level=2,theme='farm')
 wa('world-gate','可开合农场栅门','props',[pi('postL','w.timber.post'),pi('postR','w.timber.post',[2,0,0]),ai('gate','kit-rural-gate-leaf')],theme='farm',metadata=controls(turn('open','栅门开度','gate',0,105)))
 # Closed staves and open rim; hoops shared with metal drum variants.
 wp('w.container.barrel_shell','木桶身 · 鼓形桶板与上口','props',[lathe([[.22,0],[.25,.08],[.286,.36],[.26,.66],[.225,.73],[.201,.73],[.233,.66],[.257,.36],[.219,.08],[.19,.05]],'wood',14,closed_profile=True),disk(.197,.035,'woodDark',[0,.052,0],14)],[.574,.73,.574],material='mat.wood')
 wp('w.container.hoop','桶箍 · 中空金属环','props',[lathe([[.25,-.028],[.268,-.028],[.268,.028],[.25,.028]],'steel',14,closed_profile=True)],[.536,.056,.536],anchor='center',material='mat.metal')
 wa('world-barrel','木桶 · 木板与金属箍','props',[pi('staves','w.container.barrel_shell'),pi('bandLow','w.container.hoop',[0,.115,0]),pi('bandTop','w.container.hoop',[0,.62,0])])
 wp('w.container.drum','钢制油桶 · 翻边与加强环','props',[lathe([[.27,0],[.285,.03],[.27,.06],[.27,.24],[.284,.26],[.284,.28],[.27,.3],[.27,.60],[.284,.62],[.284,.65],[.27,.67],[.27,.85],[.287,.87],[.287,.90]],'red',16,cap=True),disk(.044,.014,'metal',[.115,.912,.10],10,material='mat.metal')],[.58,.93,.58],material='mat.paint',level=2)
 wa('world-fuel-drum','油桶','props',[pi('drum','w.container.drum')],theme='outpost')
 pallet=[]
 for i in range(5):pallet.append(pi('deck'+str(i),'core.props.plank',[0,.17,-.43+i*.215],rot=[90,0,0],params={'length':1.2,'width':.175,'thickness':.033}))
 for x in [-.43,0,.43]:pallet.append(pi('runner'+str(x).replace('.','_').replace('-','n'),'core.props.plank',[x,.07,0],rot=[0,90,0],params={'length':1.08,'width':.12,'thickness':.11}))
 wa('world-pallet','物流木托盘','props',pallet,theme='depot')
 wp('w.light.lantern','提灯 · 框架 / 灯芯 / 顶盖','props',[box([.17,.24,.17],'yellow',[0,.20,0],bevel=.024,material='mat.emissive.amber'),disk(.12,.044,'steel',[0,.06,0],8),lathe([[.13,.32],[.025,.40]],'steel',8,cap=True),*[rod([x,.07,z],[x,.34,z],.011,'steel',sides=5) for x in [-.09,.09] for z in [-.09,.09]],lathe([[.039,-.008],[.053,-.008],[.053,.008],[.039,.008]],'steel',10,closed_profile=True,position=[0,.444,0],rotation=[90,0,0])],[.26,.5,.26],material='mat.metal',level=2)
 wa('world-lantern','营地提灯','props',[pi('lantern','w.light.lantern')],theme='camp')
 wp('w.site.cone','交通锥 · 橡胶底座与反光带','props',[box([.34,.055,.34],'rubber',[0,.028,0],bevel=.035,material='mat.rubber'),lathe([ [.132,.055],[.072,.29],[.052,.38],[.023,.50]],'orange',12,cap=True),lathe([[.073,.287],[.064,.329]],'white',12,cap=True),lathe([[.10,.18],[.088,.231]],'white',12,cap=True)],[.34,.51,.34],material='mat.paint')
 wa('world-cone','交通安全锥','props',[pi('cone','w.site.cone')],theme='construction')
 wp('w.site.barrier_body','道路隔离墩 · 梯形截面','props',[extrude([[-.26,0],[.26,0],[.26,.12],[.12,.40],[.12,.70],[-.12,.70],[-.12,.4],[-.26,.12]],1.8,'stone',rotation=[0,90,0]),*[box([.24,.41,.012],'yellow',[x,.46,.135],bevel=.004,rotation=[0,0,-18]) for x in [-.65,-.14,.37]]],[1.8,.70,.52],material='mat.stone',level=2)
 wa('world-roadblock','道路隔离墩','props',[pi('body','w.site.barrier_body')],theme='outpost')
 wp('w.site.sign_post','标识杆 · 立柱与加重底座','props',[box([.30,.06,.30],'stone',[0,.03,0],bevel=.015),rod([0,.06,0],[0,1.9,0],.029,'steel',sides=8,material='mat.metal')],[.3,1.9,.3],material='mat.metal')
 wp('w.site.stop_face','八角停车标识板','props',[disk(.29,.025,'white',sides=8,rotation=[90,0,22.5]),disk(.265,.031,'red',pos=[0,0,.004],sides=8,rotation=[90,0,22.5]),*label_forms('STOP',.395,.123,position=[0,0,.029])],[.58,.58,.05],anchor='center',material='mat.paint')
 wa('world-stop-sign','停车标识','props',[pi('post','w.site.sign_post'),pi('face','w.site.stop_face',[0,1.70,.013])],theme='depot')
 # A modular metal mesh fence. Broad, sparse diamonds avoid tiny noisy triangles.
 forms=[rod([x,0,0],[x,2.1,0],.034,'steel',sides=6) for x in [-1,1]]
 forms += [beam([-1,y,0],[1,y,0],.035,.035,'steel') for y in [.13,1.94]]
 for x in [-1+i*.25 for i in range(9)]:
  end=min(1,x+1.8)
  if end>x+1e-6:forms.append(rod([x,.14,0],[end,.14+(end-x),0],.009,'metal',sides=4))
  end=max(-1,x-1.8)
  if end<x-1e-6:forms.append(rod([x,.14,.009],[end,.14+(x-end),.009],.009,'metal',sides=4))
 wp('w.site.fence_panel','场站围栏 · 金属框与菱形网','props',forms,[2.07,2.1,.09],material='mat.metal',level=2,ports=[port('left',[-1,0,0],(-1,0,0),(0,1,0),interface='fence.2m.v1'),port('right',[1,0,0],(1,0,0),(0,1,0),interface='fence.2m.v1')])
 wa('world-wire-fence','场站围栏','props',[pi('panel','w.site.fence_panel')],theme='depot')
 wp('w.site.gate_arm','道闸抬杆 · 红白段与端帽','props',[box([3,.065,.065],'white',[1.48,0,0],bevel=.009),*[box([.36,.068,.068],'red',[x,0,0],bevel=.008) for x in [.34,1.10,1.86,2.62]]],[3.05,.07,.07],anchor='hinge',material='mat.paint')
 wp('w.site.gate_motor','道闸电机柜 · 底座与状态灯','props',[box([.38,1.0,.32],'yellow',[0,.5,0],bevel=.04),box([.27,.055,.34],'steel',[0,1.02,0],bevel=.012),box([.07,.10,.02],'cyan',[0,.79,.171],bevel=.01,material='mat.emissive.cyan')],[.38,1.05,.34],material='mat.paint')
 wa('world-parking-gate','电动停车道闸','props',[pi('motor','w.site.gate_motor'),pi('arm','w.site.gate_arm',[0,.94,.23])],theme='depot',metadata=controls(turn('open','抬杆角度','arm',0,85,(0,0,1))))
