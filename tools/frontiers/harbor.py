"""Open boat shells, rigging, coastal structures and readable nautical silhouettes."""
from .common import *

def author():
 L,W=Q('length'),Q('beam')
 # Longitudinal stations carry keel and sheer. Inner planks form a real cavity;
 # gunwales bridge the inner/outer lips but never span the passenger opening.
 stations=[(-.50,.24,.20,.69),(-.40,.73,.06,.61),(-.20,.98,.00,.58),(.10,1.0,.00,.61),(.32,.76,.10,.77),(.47,.30,.31,.98),(.50,.025,.56,1.055)]
 hull=[]
 for side in (-1,1):
  outer=[];inner=[]
  for z,wide,bottom,top in stations:
   xs=mul(side*.5*wide,W)
   outer.append([[0,bottom,mul(z,L)],[mul(.60,xs),bottom+(top-bottom)*.18,mul(z,L)],[mul(.87,xs),bottom+(top-bottom)*.49,mul(z,L)],[xs,top,mul(z,L)]])
   inner.append([[0,bottom+.085,mul(z,L)],[mul(.49,xs),bottom+(top-bottom)*.22+.06,mul(z,L)],[mul(.79,xs),bottom+(top-bottom)*.52+.035,mul(z,L)],[mul(.91,xs),top-.026,mul(z,L)]])
  for k in range(len(stations)-1):
   for band in range(3):
    a,b=outer[k],outer[k+1];f=poly([a[band],b[band],b[band+1],a[band+1]],[[0,1,2,3]] if side>0 else [[3,2,1,0]],['darkwood','hull','cedar'][band]);hull.append(f)
    a,b=inner[k],inner[k+1];hull.append(poly([a[band],b[band],b[band+1],a[band+1]],[[3,2,1,0]] if side>0 else [[0,1,2,3]],'hull' if band==0 else 'woodLight'))
   hull.append(poly([outer[k][3],outer[k+1][3],inner[k+1][3],inner[k][3]],[[0,1,2,3]],'darkwood'))
  for k in [0,len(stations)-1]:
   a,b=outer[k],inner[k]
   for j in range(3):hull.append(poly([a[j],a[j+1],b[j+1],b[j]],[[0,1,2,3]],'cedar'))
 # Close only stern transom, leaving the deck open.
 _,wide,bottom,top=stations[0]
 hull += [poly([[-.5*wide,0,0],[.5*wide,0,0],[.5*wide,.48,0],[-.5*wide,.48,0]],[[0,1,2,3]],'cedar',scale=[W,1,1],position=[0,.20,mul(-.5,L)])]
 fp('p5.boat.open_hull','木船开口船壳 · 舷弧/内壁/实厚船沿','vessel',hull,[1.7,1.1,3.9],theme='harbor',params=schema(length=number(3.9,3.2,5.6,'船长',.05,'m'),beam=number(1.7,1.35,2.3,'船宽',.05,'m')),material='mat.wood',level=2,
    ports=[port('mast',[0,.17,mul(.06,L)],interface='nautical.mast.v1'),port('stern',[0,.51,mul(-.5,L)],(0,0,-1),interface='nautical.rudder.v1')])
 fp('p5.boat.bench','木船横凳 · 拱边支持件','props',[box([W,.065,.29],'woodLight',[0,0,0],bevel=.01),*[box([.07,.23,.16],'cedar',[mul(side*.34,W),-.12,0],bevel=.008) for side in [-1,1]]],[1.35,.30,.3],anchor='center',theme='harbor',params=schema(beam=number(1.35,1.0,1.85,'凳宽',.05,'m')),material='mat.wood')
 fp('p5.boat.oar','木桨 · 桨杆与菱弧叶面','props',[rod([0,0,-1.02],[0,0,.70],.022,'woodLight',sides=7),loft([[0,0,.56,.023,.023],[0,0,.73,.073,.018],[0,0,1.11,.096,.016],[0,0,1.19,.029,.013]],'cedar',8,frame_axis=[0,0,1])],[.21,.065,2.22],anchor='center',theme='harbor',material='mat.wood',ports=[port('grip',[0,0,-.75],interface='hand-grip.v1')])
 fa('world-rowboat','木划艇 · 开放座舱与双桨','vessel',[pi('hull','p5.boat.open_hull'),pi('frontSeat','p5.boat.bench',[0,.48,.58]),pi('backSeat','p5.boat.bench',[0,.44,-.72]),pi('oarLeft','p5.boat.oar',[-.70,.70,-.06],rot=[0,-55,-12]),pi('oarRight','p5.boat.oar',[.70,.70,-.06],rot=[0,55,12])],'harbor',metadata={'waterline_m':.31,'buoyancy_model':False})
 # Ship mast and shrouds are independent reusable parts, with no flat billboard rope.
 fp('p5.rig.mast','船桅 · 缩径木杆与箍带','props',[rod([0,0,0],[0,4.15,0],.057,'cedar',r2=.035,sides=9),*[disk(.064,.045,'brass',[0,y,0],10,material='mat.metal') for y in [.26,1.28,2.6,3.87]]],[.14,4.2,.14],theme='harbor',material='mat.wood')
 fp('p5.rig.sail','纵帆 · 弯曲帆腹与加强帆角','props',[
  poly([[0,.14,0],[0,3.20,0],[0,.14,-2.07],[.28,1.10,-.84],[.18,2.06,-.52]],[[0,3,2],[0,4,3],[0,1,4],[1,2,4],[2,3,4]],'sail'),
  tube([[0,.14,0],[0,3.20,0]],.010,'ivory'),tube([[0,3.20,0],[.10,1.70,-1.04],[0,.14,-2.07]],.009,'ivory'),tube([[0,.14,-2.07],[0,.14,0]],.009,'ivory'),
  *[poly([[0,.14,0],[0,.34,0],[0,.14,-.20]],[[0,1,2]],'woodLight',position=p) for p in [[0,0,0]]]
 ],[.31,3.3,2.14],anchor='hinge',theme='harbor',material='mat.fabric')
 fp('p5.rig.boom','帆横杆与帆脚索','props',[rod([0,0,.08],[0,0,-2.18],.026,'cedar',sides=7),tube([[0,0,-1.97],[.14,-.22,-1.32],[0,-.42,-.52]],.011,'ivory')],[.22,.48,2.31],anchor='hinge',theme='harbor',material='mat.wood')
 fa('kit-sail-rig','帆装子总成 · 桅轴、帆腹与帆脚','props',[pi('mast','p5.rig.mast'),pi('sail','p5.rig.sail',[.025,.82,.0]),pi('boom','p5.rig.boom',[.025,.95,0])],'harbor',level=2)
 fp('p5.rig.shrouds','桅索组 · 前支索与左右侧支索','props',[tube(a,.013,'ivory') for a in [ [[0,3.95,0],[-.83,.24,-.10]],[[0,3.95,0],[.83,.24,-.10]],[[0,4.10,0],[0,.80,2.37]],[[0,3.67,0],[0,.52,-1.78]] ]],[1.72,4.2,4.2],theme='harbor',material='mat.fabric')
 fp('p5.boat.rudder','船舵 · 铰轴/舵叶/舵柄','vessel',[extrude([[-.04,.18],[.35,.10],[.51,-.50],[.28,-.73],[-.04,-.58]],.062,'cedar',rotation=[0,90,0]),rod([0,-.58,0],[0,.41,0],.036,'darkwood',sides=8),rod([0,.40,0],[0,.41,.66],.028,'woodLight',sides=7)],[.10,1.22,.8],anchor='hinge',theme='harbor',material='mat.wood')
 sail=[pi('hull','p5.boat.open_hull',params={'length':5.3,'beam':2.15}),pi('seatRear','p5.boat.bench',[0,.51,-1.10],params={'beam':1.71}),pi('seatFront','p5.boat.bench',[0,.60,1.26],params={'beam':1.5}),ai('rig','kit-sail-rig',[0,.22,.35]),pi('shrouds','p5.rig.shrouds',[0,.22,.35]),pi('rudder','p5.boat.rudder',[0,.40,-2.67])]
 fa('world-sailboat','沿岸帆船 · 真实船舱与独立帆装','vessel',sail,'harbor',metadata=controls({'id':'sheet','title':'帆面与帆杆联动','nodes':['rig.sail','rig.boom'],'axis':[0,1,0],'min':-35,'max':35,'default':0},turn('rudder','船舵角度','rudder',-30,30)))
 # Cargo skiff shares hull standards but changes functional layout, not just a paint tint.
 fp('p5.boat.canopy','货舟遮篷 · 木支柱/横梁/绷紧布面','vessel',[
  *[beam([x,0,z],[x,1.50,z],.055,.055,'cedar') for x in [-.68,.68] for z in [-.73,.67]],
  poly([[-.82,1.48,-.9],[.82,1.48,-.9],[.82,1.48,.83],[-.82,1.48,.83],[0,1.62,-.9],[0,1.62,.83]],[[0,4,5,3],[4,1,2,5]],'sail'),
  *[beam([-.83,1.48,z],[.83,1.48,z],.045,.045,'darkwood') for z in [-.9,.83]]
 ],[1.72,1.70,1.82],theme='harbor',material='mat.wood',level=2)
 fa('world-cargo-skiff','港湾货舟 · 载物区与遮篷','vessel',[pi('hull','p5.boat.open_hull',params={'length':4.4,'beam':2.05}),pi('canopy','p5.boat.canopy',[0,.35,-.15]),pi('seat','p5.boat.bench',[0,.47,1.12],params={'beam':1.52}),ai('barrel','world-barrel',[-.34,.21,-.90],scale=[.85,.85,.85]),ai('crate','fnd-crate',[.31,.25,-.30],scale=[.63,.63,.63])],'harbor')
 # Square dock tiles, one explicit snap interface for every shore connector.
 L=Q('length')
 dock=[box([1.94,.095,div(L,8)],'woodLight',[0,0,add(mul(-.5,L),mul((i+.5)/8,L))],bevel=.01) for i in range(8)]
 dock += [box([.16,.23,L],'darkwood',[x,-.13,0],bevel=.012) for x in [-.69,.69]]
 fp('p5.dock.deck','码头面板 · 桥接板与承重梁','props',dock,[2,.28,2.0],theme='harbor',anchor='center',params=schema(length=number(2,1.6,3.6,'节段长度',.2,'m')),material='mat.wood',ports=[port('back',[0,0,mul(-.5,L)],(0,0,-1),interface='dock.deck2.v1'),port('front',[0,0,mul(.5,L)],(0,0,1),interface='dock.deck2.v1'),port('left',[-1,0,0],(-1,0,0),interface='dock.deck2.v1'),port('right',[1,0,0],(1,0,0),interface='dock.deck2.v1')])
 fp('p5.dock.piling','码头木桩 · 水位色带与桩帽','props',[rod([0,-.82,0],[0,.78,0],.103,'darkwood',r2=.090,sides=9),disk(.11,.055,'woodLight',[0,.78,0],9),disk(.111,.070,'brass',[0,.40,0],9,material='mat.metal')],[.24,1.68,.24],theme='harbor',anchor='center',material='mat.wood')
 fa('world-dock','标准码头节段 · 可吸附四向接口','props',[pi('deck','p5.dock.deck'),*[pi('pile'+str(i),'p5.dock.piling',[x,0,z]) for i,(x,z) in enumerate([(-.85,-.82),(.85,-.82),(-.85,.82),(.85,.82)])]],'harbor')
 fp('p5.dock.rope_rail','绳栏节段 · 松弛曲线与系结','props',[tube([[-.85,.45,0],[-.43,.32,0],[0,.27,0],[.43,.32,0],[.85,.45,0]],.028,'ivory')],[1.78,.30,.08],anchor='center',theme='harbor',material='mat.fabric')
 fp('p5.dock.bollard','系船柱 · 双角与固定底盘','props',[box([.40,.08,.24],'steel',[0,.04,0],bevel=.018),rod([0,.04,0],[0,.26,0],.07,'steel',sides=8),rod([-.16,.23,0],[.16,.23,0],.041,'steel',sides=8)],[.43,.31,.27],theme='harbor',material='mat.metal')
 fa('world-mooring','系船柱与绳圈','props',[pi('bollard','p5.dock.bollard'),pi('coil','p5.rope.coil',[.47,0,0])],'harbor') if 'p5.rope.coil' in PARTS else None
 coil=[]
 for j in range(3):coil.append(tube([[math.cos(a)*(.22+j*.045),.035+j*.019,math.sin(a)*(.22+j*.045)] for a in [k*math.pi/10 for k in range(21)]],.022,'ivory'))
 fp('p5.rope.coil','缆绳圈 · 真实多边形绳索','props',coil,[.68,.13,.68],theme='harbor',material='mat.fabric')
 fa('world-mooring','系船柱与盘绳','props',[pi('bollard','p5.dock.bollard'),pi('coil','p5.rope.coil',[.51,0,0])],'harbor')
 net=[]
 for i in range(7):
  x=-.64+i*.213;net.append(tube([[x,.0,0],[x,.47,.08],[x,.97,.0]],.012,'ivory',5))
 for j in range(6):
  y=j*.19;net.append(tube([[-.64,y,0],[0,y,.09],[.64,y,0]],.012,'ivory',5))
 net += [ico([.075,.07,.072],'woodLight',[x,.0,.0],0,distort=0) for x in [-.64,-.21,.21,.64]]
 fp('p5.dock.fishing_net','挂网 · 透空网格与木浮子','props',net,[1.40,1.1,.18],theme='harbor',material='mat.fabric',level=2)
 single('anchor','铁锚 · 环/锚干/弯爪','props',[lathe([[.072,-.017],[.11,-.017],[.11,.017],[.072,.017]],'steel',12,closed_profile=True,rotation=[90,0,0],position=[0,1.03,0]),box([.064,.80,.05],'steel',[0,.56,0],bevel=.01),rod([-.32,.73,0],[.32,.73,0],.032,'steel',sides=7),extrude([[-.39,.31],[-.31,.06],[0,0],[.31,.06],[.39,.31],[.23,.20],[.22,.12],[.045,.11],[.03,.24],[-.03,.24],[-.045,.11],[-.22,.12],[-.23,.20]],.055,'steel')],[.85,1.16,.09],'harbor',material='mat.metal')
 # Lighthouse has a real gallery, posts, lens and rail; no painted window rectangle.
 tower=[lathe([[.72,0],[.72,.14],[.57,.22],[.43,3.14],[.61,3.22],[.61,3.40]],'ivory',10,cap=True),extrude([[-.14,0],[.14,0],[.14,.53],[.08,.61],[-.08,.61],[-.14,.53]],.04,'cedar',position=[0,.05,.69]),*[box([.14,.27,.023],'glass',[0,y,z],bevel=.013,material='mat.vehicleGlass') for y,z in [(1.41,.536),(2.32,.486)]],*[rod([math.cos(a)*.55,3.33,math.sin(a)*.55],[math.cos(a)*.55,4.10,math.sin(a)*.55],.033,'brass',sides=7,material='mat.metal') for a in [i*math.pi/3 for i in range(6)]],lathe([[.69,4.08],[.12,4.58]],'red',8,cap=True),disk(.23,.36,'yellow',[0,3.71,0],12,material='mat.emissive.amber')]
 for j in range(12):
  a=j*math.pi/6;tower.append(rod([math.cos(a)*.78,3.27,math.sin(a)*.78],[math.cos(a)*.78,3.68,math.sin(a)*.78],.017,'steel',sides=5,material='mat.metal'))
 tower.append(lathe([[.762,3.67],[.80,3.67],[.80,3.70],[.762,3.70]],'steel',24,closed_profile=True,material='mat.metal'))
 single('lighthouse','海岸灯塔 · 回廊与六角灯室','arch',tower,[1.62,4.62,1.62],'harbor',material='mat.plaster')
 fp('p5.coast.palm_trunk','棕榈树干 · 生长弯曲与叶柄冠','nature',[loft([[0,0,0,.18,.17],[.16,1.0,0,.14,.14],[.29,2.18,-.05,.11,.12],[.24,2.97,-.1,.085,.09]],'cedar',9),*[lathe([[r,y],[r+.01,y+.035]],'darkwood',9,cap=True,position=[x,0,z]) for y,r,x,z in [(.42,.17,.07,0),(.98,.149,.158,0),(1.55,.127,.22,-.022),(2.1,.12,.28,-.047),(2.57,.099,.27,-.083)]]],[.62,3.08,.4],theme='harbor',material='mat.wood')
 leaves=[]
 for i in range(9):
  a=i*math.pi*2/9;u,v=math.cos(a),math.sin(a);central=[[0,0,0],[u*.38,.21,v*.38],[u*.95,.07,v*.95],[u*1.44,-.51,v*1.44]]
  pts=[]
  for j,c in enumerate(central):
   width=[.01,.22,.20,.008][j];pts += [[c[0]-v*width,c[1]-.026,c[2]+u*width],c,[c[0]+v*width,c[1]-.026,c[2]-u*width]]
  leaves.append(poly(pts,[[j*3,(j+1)*3,(j+1)*3+1,j*3+1] for j in range(3)]+[[j*3+1,(j+1)*3+1,(j+1)*3+2,j*3+2] for j in range(3)],'leafDark' if i%3 else 'leaf'))
 fp('p5.coast.palm_crown','棕榈叶冠 · 沿叶脉折面的九叶组','nature',leaves,[3,.8,3],anchor='center',theme='harbor',material='mat.leaf',level=2)
 fa('world-palm','海岸棕榈 · 弯干与折面叶冠','nature',[pi('trunk','p5.coast.palm_trunk'),pi('crown','p5.coast.palm_crown',[.24,2.96,-.10])],'harbor')
 fp('p5.coast.rock_arch','海蚀石拱 · 真正贯穿洞口','terrain',[extrude([[-1.5,0],[-1.45,1.02],[-1.02,1.78],[-.35,2.02],[.63,1.98],[1.34,1.50],[1.55,.5],[1.47,0],[.71,0],[.73,.90],[.37,1.30],[-.30,1.27],[-.68,.88],[-.75,0]],.84,'stone',bevel=.0),*[ico([.65,.55,.71],'stoneLight',[x,.14,.46],0,seed=j) for j,x in enumerate([-1.22,1.15])]], [3.4,2.10,1.25],theme='harbor',material='mat.stone',level=2)
 fa('world-rock-arch','海岸石拱','terrain',[pi('arch','p5.coast.rock_arch')],'harbor')
 treasure()
 people_and_birds()

def treasure():
 fp('p5.chest.base','宝箱底座 · 实厚开口箱腔','props',[box([1.04,.07,.64],'cedar',[0,.08,0],bevel=.015),*[box([1.05,.40,.065],'cedar',[0,.28,z],bevel=.011) for z in [-.30,.30]],*[box([.065,.40,.56],'cedar',[x,.28,0],bevel=.009) for x in [-.492,.492]],*[box([.07,.405,.016],'brass',[x,.28,.342],bevel=.006,material='mat.metal') for x in [-.34,.34]],box([.12,.11,.032],'brass',[0,.435,.353],bevel=.008,material='mat.metal')],[1.1,.53,.72],theme='harbor',material='mat.wood',level=2)
 pts=[];faces=[]
 for x in [-.52,.52]:
  for j in range(9):a=j*math.pi/8;pts.append([x,math.sin(a)*.32,.32+.32*math.cos(a)])
 for j in range(8):faces.append([j,j+1,10+j,9+j])
 faces += [list(range(8,-1,-1)),list(range(9,18))]
 lid=[poly(pts,faces,'cedar')]
 for x in [-.34,.34]:lid.append(tube([[x,math.sin(a)*.327,.32+.327*math.cos(a)] for a in [j*math.pi/12 for j in range(13)]],.022,'brass',6,material='mat.metal'))
 fp('p5.chest.lid','宝箱拱盖 · 後缘铰轴','props',lid,[1.1,.36,.67],anchor='hinge',theme='harbor',material='mat.wood')
 coins=[disk(.062,.012,'brass',[x,.16+(i%3)*.032,z],10,material='mat.metal',rotation=[0,i*30,i%4*6]) for i,(x,z) in enumerate([(-.3,-.1),(-.18,0),(-.06,.1),(.06,-.07),(.22,.08),(.31,-.05),(-.18,.13),(.04,.15),(.23,-.13),(-.30,.1),(.13,.02)])]
 fp('p5.chest.treasure','宝藏内容 · 分散金币和切面宝石','props',coins+[ico([.11,.13,.10],'cyan',[.13,.21,.04],0,distort=0,material='mat.metal'),ico([.08,.09,.10],'red',[-.15,.19,-.05],0,distort=0,material='mat.metal')],[.78,.30,.47],theme='harbor',material='mat.metal')
 fa('world-treasure-chest','宝箱 · 可开合拱盖与真实内部','props',[pi('base','p5.chest.base'),pi('lid','p5.chest.lid',[0,.48,-.31]),pi('gold','p5.chest.treasure',[0,.17,0])],'harbor',metadata=controls(turn('open','宝箱开盖','lid',-95,0,(1,0,0))))
 barrel=[lathe([[.075,-.57],[.098,-.46],[.13,.10],[.13,.39],[.092,.57],[.06,.57],[.06,.46]],'steel',14,closed_profile=True,rotation=[90,0,0]),*[lathe([[r-.01,y],[r,y],[r,y+.04],[r-.01,y+.04]],'brass',14,closed_profile=True,rotation=[90,0,0],material='mat.metal') for y,r in [(-.42,.11),(.32,.144)]],box([.53,.16,.86],'cedar',[0,-.24,0],bevel=.025),*[disk(.18,.08,'darkwood',[sg*.31,-.25,z],12,rotation=[0,0,90]) for sg in [-1,1] for z in [-.24,.24]]]
 single('harbor-cannon','港口礼炮 · 空心炮口与木轮炮架','props',barrel,[.74,.62,1.18],'harbor',material='mat.metal')
 single('buoy','航道浮标 · 吃水体/指示柱/顶标','props',[lathe([[.12,-.34],[.32,-.14],[.34,.20],[.22,.36],[.15,.64],[.09,.86]],'red',10,cap=True),lathe([[.31,.24],[.23,.36]],'white',10,cap=True),rod([0,.78,0],[0,1.12,0],.026,'steel',sides=6),poly([[0,1.14,0],[0,1.36,0],[.30,1.30,0]],[[0,1,2]],'red')],[.72,1.75,.72],'harbor',material='mat.paint')
 # Same stall can sell coastal supplies, but is a bespoke dock-side assembly.
 stall=[box([1.6,.12,.74],'cedar',[0,.87,0],bevel=.014),*[box([.085,1.66,.085],'darkwood',[x,.83,z],bevel=.007) for x in [-.71,.71] for z in [-.28,.28]],box([1.49,.74,.035],'cedar',[0,.45,.31],bevel=.015)]
 for i in range(8):
  x=-.84+i*.21;stall.append(poly([[x,1.74,-.45],[x+.21,1.74,-.45],[x+.21,1.62,.54],[x,1.62,.54]],[[0,1,2,3]],'red' if i%2 else 'sail',material='mat.fabric'))
 single('harbor-stall','码头补给摊 · 遮棚与货台','props',stall,[1.8,1.80,1.10],'harbor',material='mat.wood')

def people_and_birds():
 fp('p5.wear.tricorn','三角船长帽 · 折边与缎带','wear',[lathe([[.15,.02],[.17,.11],[.13,.22],[.035,.25]],'shadow',10,cap=True),poly([[-.29,.07,-.18],[.29,.07,-.18],[0,.04,.31],[-.22,.18,-.13],[.22,.18,-.13],[0,.17,.23]],[[0,1,4,3],[1,2,5,4],[2,0,3,5]],'shadow'),tube([[-.29,.07,-.18],[.29,.07,-.18],[0,.04,.31],[-.29,.07,-.18]],.012,'brass',5,material='mat.metal')],[.6,.27,.56],anchor='center',theme='harbor',material='mat.fabric')
 fp('p5.wear.captain_coat','船长长衣 · 肩襟/下摆/铜扣','wear',[box([.39,.42,.058],'red',[0,-.05,-.16],bevel=.022),*[profile([[sg*.125,-.51,.015,.099,.13],[sg*.129,-.20,.041,.104,.129],[sg*.147,.19,.015,.079,.125]],'red') for sg in [-1,1]],*[box([.025,.045,.015],'brass',[sg*.09,y,.173],bevel=.006,material='mat.metal') for sg in [-1,1] for y in [.06,-.06,-.18]],*[poly([[sg*.02,.19,.15],[sg*.095,.23,.142],[sg*.18,.11,.17],[sg*.06,-.05,.195]],[[0,1,2,3]],'brass') for sg in [-1,1]]],[.5,.79,.39],anchor='center',theme='harbor',material='mat.fabric')
 fp('p5.wear.bandana','水手头巾 · 包头与垂带','wear',[profile([[0,.03,0,.141,.13],[0,.12,-.015,.137,.125],[0,.20,-.018,.089,.08]],'red'),poly([[-.09,.08,-.128],[.09,.08,-.128],[.03,-.19,-.19],[-.045,-.13,-.24]],[[0,1,2,3]],'red')],[.3,.41,.37],anchor='center',theme='harbor',material='mat.fabric')
 fp('p5.tool.chart','航海图板 · 展开的有厚度卷边','props',[box([.43,.31,.012],'sail',[0,0,0],bevel=.007),tube([[-.19,.11,.014],[-.11,.04,.018],[.05,.055,.018],[.15,-.05,.018]],.006,'cedar',4),*[disk(.018,.31,'woodLight',[x,0,.006],8) for x in [-.218,.218]]],[.47,.34,.048],anchor='center',theme='harbor',material='mat.fabric')
 fp('p5.tool.cutlass','弯刀道具 · 刀背曲线与护手','props',[extrude([[-.020,-.11],[.025,-.11],[.023,.25],[.096,.56],[.045,.49],[-.032,.22]],.014,'metal'),box([.025,.16,.032],'darkwood',[0,-.18,0],bevel=.007),tube([[-.06,-.09,0],[.06,-.08,0],[.074,-.20,0],[.02,-.28,0]],.016,'brass',6,material='mat.metal')],[.16,.88,.05],anchor='center',theme='harbor',material='mat.metal')
 mono_role('world-pirate-captain','海盗船长 · 长衣/三角帽/弯刀','harbor',[('p5.wear.captain_coat',[0,0,0],[1,1,1],'chest')],'p5.wear.tricorn','p5.tool.cutlass',{P['cream']:P['ivory'],P['moss']:P['darkwood']},1.08)
 mono_role('world-sailor','水手 · 头巾与实用背带','harbor',[('w.wear.overall_bib',[0,0,0],[1,1,1],'chest')],'p5.wear.bandana',None,{P['cream']:P['blue'],P['white']:P['ivory'],P['moss']:P['darkwood']},1.04)
 mono_role('world-navigator','领航员 · 轻装背心与航海图','harbor',[('w.wear.field_vest',[0,0,0],[1,1,1],'chest')],None,'p5.tool.chart',build=.99)
 mono_role('world-dockworker','码头搬运工 · 围裙与厚工作服','harbor',[('core.wear.apron',[0,-.28,0],[1,1,1],'chest')],'p5.wear.bandana',None,build=1.14)
 bird_parts('gull','海鸥','white','steel','yellow',.32)
 bird_parts('parrot','金刚鹦鹉','red','blue','ink',.30)

def bird_parts(slug,name,body,wing,beak,h):
 forms=[ico([.17,.19,.32],body,[0,.20,0],1,distort=.01),ico([.13,.14,.13],body,[0,.33,.16],1,distort=0),loft([[0,.32,.216,.031,.027],[0,.30,.307,.008,.009]],beak,6,frame_axis=[0,0,1]),*[ico([.015,.017,.012],'ink',[sg*.051,.352,.191],0,distort=0) for sg in [-1,1]],*[rod([x,.01,.04],[x,.15,.04],.009,'yellow',sides=5) for x in [-.034,.034]],*[rod([x,.014,.04],[x+dx,.008,.10],.005,'yellow',sides=4) for x in [-.034,.034] for dx in [-.02,.02]],*[poly([[sg*.064,.27,.08],[sg*.115,.21,-.07],[sg*.05,.13,-.22],[sg*.035,.23,-.07]],[[0,1,2],[0,2,3]],wing) for sg in [-1,1]],poly([[-.055,.22,-.12],[.055,.22,-.12],[.035,.10,-.47],[-.035,.10,-.47]],[[0,1,2,3]],'yellow' if slug=='parrot' else 'steel')]
 if slug=='parrot':
  # Macaw has a shorter hooked bill, pale cheek patch and a much longer tail.
  forms[2]=loft([[0,.338,.215,.030,.03],[0,.325,.273,.035,.033],[0,.286,.28,.019,.014]],'ink',8,frame_axis=[0,0,1])
  forms += [ico([.008,.074,.068],'ivory',[sg*.057,.34,.174],0,distort=0) for sg in [-1,1]]
  forms += [ico([.012,.016,.013],'ink',[sg*.065,.356,.19],0,distort=0) for sg in [-1,1]]
  forms[0]['scale']=[1,1.15,1]
  forms += [poly([[-.03,.21,-.11],[.03,.21,-.11],[.018,-.005,-.58],[-.018,-.005,-.58]],[[0,1,2,3]],'red')]
 single(slug,name+' · 地面停栖姿态','bird',forms,[.25,.43,.83],'harbor',material='mat.fur')
