"""Furniture construction, real cavities and hinge-local doors."""
from .common import *
def author():
 W,H,D=Q('width'),Q('height'),Q('depth')
 wp('w.interior.carcass','柜体框架 · 开口内腔与踢脚','interior',[
  *[box([.055,H,D],'wood',[mul(sg*.5,sub(W,.055)),mul(H,.5),0],bevel=.01) for sg in [-1,1]],
  box([W,.065,D],'woodLight',[0,sub(H,.0325),0],bevel=.01),box([W,.065,D],'wood',[0,.067,0],bevel=.01),
  box([sub(W,.07),sub(H,.12),.035],'woodDark',[0,mul(H,.51),mul(-.5,sub(D,.035))],bevel=.005),box([sub(W,.13),.10,sub(D,.12)],'woodDark',[0,.05,0],bevel=.01)
 ],[1,1,.5],params=schema(width=number(1,.45,2.4,'柜宽',.01,'m'),height=number(1,.25,2.3,'柜高',.01,'m'),depth=number(.5,.28,1.0,'柜深',.01,'m')),material='mat.wood',level=2)
 wp('w.interior.cabinet_door','柜门 · 左边铰轴与内凹板','interior',[box([W,H,.045],'wood',[mul(W,.5),mul(H,.5),0],bevel=.012),box([sub(W,.08),sub(H,.08),.016],'woodLight',[mul(W,.5),mul(H,.5),.031],bevel=.01),box([.018,.15,.022],'steel',[sub(W,.07),mul(H,.5),.059],bevel=.005,material='mat.metal')],[.47,.9,.08],anchor='hinge',params=schema(width=number(.47,.20,1.2,'门宽',.01,'m'),height=number(.9,.35,2.1,'门高',.01,'m')),material='mat.wood')
 cabinet=[pi('shell','w.interior.carcass',params={'width':1.2,'height':2.05,'depth':.59}),pi('leftDoor','w.interior.cabinet_door',[-.58,.13,.32],params={'width':.572,'height':1.85}),pi('rightDoor','w.interior.cabinet_door',[.58,.13,.32],rot=[0,180,0],params={'width':.572,'height':1.85})]
 # Right leaf has a true mirrored hinge-local layout, not a 180-degree back-facing panel.
 right=deepcopy(PARTS['w.interior.cabinet_door']);right['id']='w.interior.cabinet_door_right';right['name']='柜门 · 右边铰轴';right['shape_params']={'components':[component('leaf','w.interior.cabinet_door',mirror='x',params={'width':W,'height':H})],'forms':[]};PARTS[right['id']]=right
 cabinet[-1]=pi('rightDoor','w.interior.cabinet_door_right',[.58,.13,.32],params={'width':.572,'height':1.85})
 wa('world-wardrobe','双门衣柜','interior',cabinet,theme='home',metadata=controls(turn('open_left','左门','leftDoor',-110,0),turn('open_right','右门','rightDoor',0,110)))
 books=[]
 for i in range(7):books.append(box([.052,.20+.018*(i%3),.16],['navy','red','cream','moss'][i%4],[-.21+i*.07,.1,0],bevel=.005))
 wp('w.interior.books','书籍组 · 大小与封面节奏','interior',books,[.5,.27,.17],material='mat.fabric')
 shelves=[pi('shell','w.interior.carcass',params={'width':.86,'height':1.86,'depth':.37})]
 for i,y in enumerate([.41,.83,1.25,1.66]):
  shelves += [pi('shelf'+str(i),'core.props.plank',[0,y,.015],rot=[90,0,0],params={'length':.79,'width':.35,'thickness':.033}),pi('books'+str(i),'w.interior.books',[-.065,y+.035,.02],rot=[0,0,0])]
 wa('world-bookshelf','开放书柜','interior',shelves,theme='home')
 wp('w.interior.tabletop','实木桌面 · 圆钝边与拼板','interior',[box([W,.085,D],'woodLight',[0,0,0],bevel=.025),*[box([.003,.002,D],'wood',[mul(W,x),.044,0],bevel=.0005) for x in [-.27,0,.27]]],[1.3,.09,.75],anchor='center',params=schema(width=number(1.3,.5,2.3,'台面宽',.01,'m'),depth=number(.75,.35,1.25,'台面深',.01,'m')),material='mat.wood')
 def table(id,name,w,d,h=.77):
  items=[pi('top','w.interior.tabletop',[0,h,0],params={'width':w,'depth':d})]
  for sx in [-1,1]:
   for sz in [-1,1]:items.append(pi('leg'+str(sx)+str(sz),'w.timber.post',[sx*(w*.5-.10),0,sz*(d*.5-.10)],params={'height':h},scale=[.62,1,.62]))
  return wa('world-'+id,name,'interior',items,theme='home')
 table('dining-table','餐桌',1.4,.86);table('desk','书桌',1.3,.68);table('coffee-table','矮茶几',1.0,.56,.38)
 wp('w.interior.chair_frame','餐椅木架 · 后腿与靠背','interior',[
  *[beam([x,0,z],[x,.49,z],.043,.043,'woodDark') for x in [-.20,.20] for z in [-.19,.19]],
  *[beam([x,.45,-.19],[x,1.0,-.245],.05,.045,'wood') for x in [-.20,.20]],
  box([.43,.19,.055],'wood',[0,.91,-.233],bevel=.015),box([.46,.046,.46],'wood',[0,.47,0],bevel=.015)
 ],[.47,1.02,.49],material='mat.wood',level=2)
 wa('world-chair','餐椅','interior',[pi('frame','w.interior.chair_frame'),pi('pad','core.interior.cushion',[0,.497,.002],params={'width':.44,'depth':.43,'thickness':.06,'palette':{P['moss']:P['cream']}})],theme='home')
 wp('w.interior.sofa_shell','沙发底座与背围 · 承托软包','interior',[box([1.98,.25,.79],'cream',[0,.305,0],bevel=.045),box([1.98,.58,.15],'cream',[0,.58,-.335],bevel=.034),*[box([.20,.43,.84],'cream',[x,.445,0],bevel=.035) for x in [-.91,.91]],*[box([.075,.19,.075],'woodDark',[x,.095,z],bevel=.009) for x in [-.83,.83] for z in [-.28,.28]]],[2.02,.9,.84],material='mat.fabric',level=2,theme='home')
 sofa=[pi('base','w.interior.sofa_shell')]
 for i,x in enumerate([-.43,.43]):sofa += [pi('seat'+str(i),'core.interior.cushion',[x,.36,.07],params={'width':.83,'depth':.67,'thickness':.18,'palette':{P['moss']:P['cream']}}),pi('back'+str(i),'core.interior.cushion',[x,.70,-.33],rot=[76,0,0],params={'width':.83,'depth':.65,'thickness':.17,'palette':{P['moss']:P['cream']}})]
 sofa.append(pi('pillow','core.interior.cushion',[-.53,.62,.01],rot=[77,0,-12],params={'width':.34,'depth':.38,'thickness':.11,'palette':{P['moss']:P['orange']}}))
 wa('world-sofa','双人沙发 · 独立软包','interior',sofa,theme='home')
 bed=[pi('frame','w.interior.carcass',params={'width':1.5,'height':.32,'depth':.7},scale=[1,1,2.9]),pi('headboard','w.interior.tabletop',[0,.73,-.99],rot=[90,0,0],params={'width':1.53,'depth':.93}),pi('mattress','core.interior.cushion',[0,.36,0],params={'width':1.4,'depth':.70,'thickness':.17,'palette':{P['moss']:P['white']}},scale=[1,1,2.85]),pi('blanket','core.interior.cushion',[0,.54,.35],params={'width':1.44,'depth':.69,'thickness':.11},scale=[1,1,1.89])]
 for x in [-.35,.35]:bed.append(pi('pillow'+str(x),'core.interior.cushion',[x,.56,-.69],params={'width':.61,'depth':.40,'thickness':.12,'palette':{P['moss']:P['white']}}))
 wa('world-bed','双人床 · 床架与床品','interior',bed,theme='home')
 wp('w.interior.lamp_shade','织物灯罩 · 内外壳与下口','interior',[lathe([[.25,0],[.19,.36],[.173,.36],[.231,0]],'cream',12,closed_profile=True)],[.51,.36,.51],material='mat.fabric')
 wp('w.interior.lamp_tripod','落地灯三脚架','interior',[*[beam([math.cos(a)*.27,0,math.sin(a)*.27],[0,1.21,0],.037,.04,'woodDark') for a in [0,2.0944,4.1888]],disk(.04,.17,'yellow',[0,1.26,0],10,material='mat.emissive.amber')],[.56,1.36,.5],material='mat.wood',level=2)
 wa('world-floor-lamp','三脚落地灯','interior',[pi('stand','w.interior.lamp_tripod'),pi('shade','w.interior.lamp_shade',[0,1.25,0])],theme='home')
 wp('w.interior.plant_pot','陶盆 · 真正开口与泥土','interior',[lathe([[.14,0],[.18,.27],[.163,.27],[.128,.025]],'white',10,closed_profile=True),disk(.15,.016,'soil',[0,.245,0],10)],[.37,.28,.37],material='mat.matte')
 leaves=[]
 for i,a in enumerate([0,1.3,2.6,3.9,5.2]):
  x,z=math.cos(a),math.sin(a);height=.45+(i%2)*.19;leaves += [rod([0,0,0],[x*.12,height*.75,z*.12],.009,'leafDark',sides=5),poly([[0,.08,0],[x*.12-z*.065,height*.53,z*.12+x*.065],[x*.28,height,z*.28],[x*.12+z*.065,height*.53,z*.12-x*.065]],[[0,1,2],[0,2,3]],'leaf' if i%2 else 'leafDark')]
 wp('w.interior.plant_leaves','观叶植物 · 大叶与支脉','nature',leaves,[.59,.68,.59],material='mat.leaf')
 wa('world-houseplant','室内观叶盆栽','interior',[pi('pot','w.interior.plant_pot'),pi('leaves','w.interior.plant_leaves',[0,.25,0])],theme='home')
 wp('w.interior.laptop','笔记本电脑 · 屏幕与键盘','interior',[box([.31,.014,.215],'steel',[0,.008,.025],bevel=.008),box([.285,.012,.19],'ink',[0,.019,.024],bevel=.007),box([.31,.20,.014],'steel',[0,.115,-.105],bevel=.009,rotation=[-12,0,0]),box([.272,.164,.008],'blue',[0,.117,-.087],bevel=.005,rotation=[-12,0,0],material='mat.display')],[.32,.23,.24],material='mat.metal',level=2)
 wa('world-laptop','笔记本电脑','interior',[pi('laptop','w.interior.laptop')],theme='home')
 wp('w.interior.sinktop','水槽台面 · 下凹水盆与龙头','interior',[extrude([[-.50,-.30],[.50,-.30],[.50,.30],[-.50,.30]],.038,'white',holes=[[[-.34,-.20],[-.34,.20],[.14,.20],[.14,-.20]]],rotation=[90,0,0]),box([.49,.034,.41],'steel',[-.10,-.11,0],bevel=.025,material='mat.metal'),*[box([.022,.13,.40],'metal',[x,-.054,0],bevel=.008,material='mat.metal') for x in [-.344,.144]],*[box([.49,.13,.022],'metal',[-.10,-.054,z],bevel=.008,material='mat.metal') for z in [-.194,.194]],loft([[.04,0,-.23,.018,.018],[.04,.26,-.23,.018,.018],[.04,.3,-.17,.018,.018],[.04,.25,-.10,.018,.018]],'metal',8,material='mat.metal')],[1,.43,.60],anchor='center',material='mat.matte',level=2)
 kitchen=[pi('shell','w.interior.carcass',params={'width':1,'height':.88,'depth':.57,'palette':{P['wood']:P['moss'],P['woodLight']:P['moss'],P['woodDark']:P['moss']}}),pi('left','w.interior.cabinet_door',[-.475,.11,.30],params={'width':.464,'height':.69,'palette':{P['wood']:P['moss'],P['woodLight']:'#939D7D'}}),pi('right','w.interior.cabinet_door_right',[.475,.11,.30],params={'width':.464,'height':.69,'palette':{P['wood']:P['moss'],P['woodLight']:'#939D7D'}}),pi('sink','w.interior.sinktop',[0,.90,0])]
 wa('world-sink-unit','厨房水槽柜','interior',kitchen,theme='home',metadata=controls(turn('left_open','左柜门','left',-105,0),turn('right_open','右柜门','right',0,105)))
 stove=[box([.70,.87,.59],'steel',[0,.435,0],bevel=.022),box([.62,.46,.027],'ink',[0,.33,.31],bevel=.019,material='mat.vehicleGlass'),box([.46,.025,.024],'metal',[0,.60,.34],bevel=.005),box([.72,.045,.62],'white',[0,.90,0],bevel=.009),*[disk(.107,.014,'ink',[x,.93,z],12) for x in [-.19,.19] for z in [-.17,.17]],*[disk(.025,.018,'ink',[x,.77,.31],10,rotation=[90,0,0]) for x in [-.22,-.075,.075,.22]]]
 simple('stove','厨房灶台与烤箱','interior',stove,[.73,.95,.64],theme='home',material='mat.paint')
 fridge=[box([.72,1.78,.68],'metal',[0,.89,0],bevel=.045),box([.66,1.18,.05],'white',[0,.70,.355],bevel=.025),box([.66,.38,.05],'white',[0,1.52,.355],bevel=.025),*[box([.025,.23,.027],'steel',[-.24,y,.403],bevel=.007) for y in [.83,1.50]]]
 simple('fridge','双门冰箱','interior',fridge,[.73,1.8,.72],theme='home',material='mat.paint')
 wp('w.interior.rug','织物地毯 · 平整几何与边框','interior',[box([2.4,.009,1.7],'cream',[0,.005,0],bevel=.003),*[box([2.28,.003,.04],'moss',[0,.011,z],bevel=.001) for z in [-.67,.67]],*[box([.04,.003,1.38],'moss',[x,.011,0],bevel=.001) for x in [-1.12,1.12]]],[2.4,.014,1.7],material='mat.fabric')
 wa('world-rug','客厅地毯','interior',[pi('rug','w.interior.rug')],theme='home')
 simple('vacuum-robot','扫地机器人','interior',[lathe([[.15,0],[.18,.025],[.18,.075],[.15,.10]],'ink',20,cap=True),disk(.064,.012,'steel',[0,.11,0],16),box([.04,.007,.02],'cyan',[.085,.103,0],bevel=.004,material='mat.emissive.cyan')],[.38,.125,.38],theme='home',material='mat.paint')
