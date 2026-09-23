"""Nature, timber, seating and architectural opening systems."""
from .common import *
def author():
 # Trees have real connecting branches and a designed crown hierarchy.
 part('core.nature.trunk','阔叶树干 · 根盘与扭转主干','nature',[
  loft([[0,0,0,.25,.22],[.016,.13,.009,.208,.179],[-.04,.62,.012,.132,.119],[-.071,1.15,0,.113,.108],[-.017,1.73,.018,.078,.075],[.064,2.2,.039,.041,.042]],'wood',7),
  *[rod([0,.14,0],[math.cos(a)*.33,.008,math.sin(a)*.30],.103,'woodDark',.013,5) for a in [.2,1.9,3.5,5.1]]
 ],[.7,2.25,.65],material='mat.wood',ports=[port('ground',[0,0,0],(0,-1,0),interface='ground'),port('crown',[.064,2.2,.039],interface='tree.crown.v1')])
 part('core.nature.branch','木质枝干 · 锥缩与分枝接口','nature',[
  loft([[0,0,0,.079,.072],[.02,.34,.007,.062,.058],[-.015,.75,.015,.025,.022]],'wood',6)
 ],[.165,.75,.15],material='mat.wood',ports=[port('mount',[0,0,0],(0,-1,0),interface='tree.branch.v1'),port('tip',[-.015,.75,.015],interface='tree.branch.v1')])
 part('core.nature.crown_cluster','阔叶冠簇 · 大中小切面','nature',[
  ico([1.15,.98,1.03],'leaf',[0,.22,0],detail=1,distort=.09,seed=4),ico([.79,.68,.76],'leafLight',[.14,.69,.024],detail=1,distort=.035,seed=8),ico([.75,.60,.73],'leafDark',[-.13,-.1,.10],detail=0,distort=.08,seed=2)
 ],[1.30,1.24,1.2],anchor='center',material='mat.leaf',ports=[port('stem',[0,-.40,0],(0,-1,0),interface='tree.branch.v1')])
 spread=Q('crown_spread')
 tree=[inst('trunk','core.nature.trunk')]
 for i,(a,b) in enumerate([((0,.98,0),(-.64,1.94,.12)),((-.055,1.37,0),(.59,2.23,.13)),((-.04,1.44,0),(.03,2.25,-.55)),((-.01,1.71,.02),(-.40,2.47,-.31)),((0,1.71,.02),(.15,2.62,.25))]):
  dx,dy,dz=[b[k]-a[k] for k in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz);rx=math.degrees(math.atan2(dz,dy));rz=-math.degrees(math.atan2(dx,math.hypot(dy,dz)))
  tree.append(inst('branch'+str(i),'core.nature.branch',pos=a,rot=[rx,0,rz],scale=[1,length/.75,1]))
 for i,(x,y,z,s) in enumerate([(-.58,2.1,.16,.94),(.59,2.37,.19,.97),(.00,2.55,-.49,1.03),(-.38,2.7,-.22,.98),(.09,2.94,.24,.97),(.00,2.27,.57,.77),(.70,2.45,-.4,.65)]):
  tree.append(inst('crown'+str(i),'core.nature.crown_cluster',pos=[mul(x,spread),y,mul(z,spread)],rot=[0,i*43,0],scale=[mul(s,spread),s,mul(s,spread)]))
 assembly('fnd-oak','阔叶树母版 · 连贯枝干与分层冠簇','nature',tree,params=schema(crown_spread=number(1,.87,1.16,'树冠展开')))
 # Rock planes are authored as strata; no white-noise triangle colour variation.
 rockPts=[[-.59,0,-.37],[.50,0,-.46],[.67,0,.19],[.16,0,.48],[-.54,0,.29],[-.43,.46,-.32],[.29,.58,-.37],[.49,.34,.21],[.08,.41,.40],[-.48,.29,.18],[-.18,.83,-.19],[.20,.80,-.10],[.24,.67,.18],[-.14,.66,.26]]
 rockFaces=[[0,4,3,2,1],[0,1,6,5],[1,2,7,6],[2,3,8,7],[3,4,9,8],[4,0,5,9],[5,6,11,10],[6,7,12,11],[7,8,12],[8,9,13,12],[9,5,10,13],[10,11,12,13]]
 part('core.nature.rock','层理岩块 · 大面与断裂棱线','nature',[poly(rockPts,rockFaces,'stone',colors=[C(c) for c in ['stoneDark','stone','stone','stoneLight','stoneDark','stone','stoneLight','stone','stoneLight','stone','stoneDark','stoneLight']])],[1.26,.83,.94],material='mat.stone',ports=[port('ground',[0,0,0],(0,-1,0),interface='ground')])
 part('core.nature.grass_clump','草簇 · 稀疏折叶','nature',[
  poly([[-.025,0,.025],[.023,0,-.013],[0,.29,.044],[.07,.16,.008]],[[0,1,2],[1,3,2]],'leaf'),
  *poly_blades()
 ],[.28,.29,.25],material='mat.leaf')
 assembly('fnd-rocks','岩组母版 · 清晰断面与地面关系','nature',[
  inst('main','core.nature.rock',scale=[1.4,1.4,1.23]),inst('left','core.nature.rock',pos=[-.83,0,.17],rot=[0,77,0],scale=[.72,.83,.8]),inst('right','core.nature.rock',pos=[.55,0,.47],rot=[0,192,0],scale=[.56,.61,.73]),inst('grass1','core.nature.grass_clump',pos=[-.51,0,.72]),inst('grass2','core.nature.grass_clump',pos=[.35,0,.79],rot=[0,67,0],scale=[.8,.8,.8])])
 # Shared timber set. Parameter changes regenerate board layout rather than stretch hardware.
 length,width,thick=Q('length'),Q('width'),Q('thickness')
 part('core.props.plank','木板 · 可控长宽厚与窄倒角','props',[box([length,width,thick],'wood',[0,0,0],bevel=mul(thick,.18))],[.70,.12,.03],anchor='center',params=schema(length=number(.7,.15,3,'板长',.01,'m'),width=number(.12,.04,.4,'板宽',.01,'m'),thickness=number(.03,.014,.12,'板厚',.002,'m')),material='mat.wood',ports=[port('left',[mul(-.5,length),0,0],(-1,0,0),(0,1,0),interface='timber.end.v1'),port('right',[mul(.5,length),0,0],(1,0,0),(0,1,0),interface='timber.end.v1')])
 part('core.props.post','木柱 · 柱脚与端面','props',[box([.066,Q('height'),.066],'woodLight',[0,mul(.5,Q('height')),0],bevel=.006)],[.066,.7,.066],params=schema(height=number(.7,.2,2.8,'柱高',.01,'m')),material='mat.wood',ports=[port('top',[0,Q('height'),0],interface='timber.post.v1'),port('bottom',[0,0,0],(0,-1,0),interface='timber.post.v1')])
 size=Q('size');edge=sub(size,.055);crate=[]
 for i,(x,z) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)]):crate.append(inst('post'+str(i),'core.props.post',pos=[mul(x*.5,edge),0,mul(z*.5,edge)],params={'height':size}))
 for side,z in [('front',1),('back',-1)]:
  for j in range(4):crate.append(inst(side+str(j),'core.props.plank',pos=[0,mul(size,(j+.5)/4),mul(z*.5,sub(size,.01))],params={'length':sub(size,.018),'width':mul(size,.235),'thickness':.026}))
 for side,x in [('left',-1),('right',1)]:
  for j in range(4):crate.append(inst(side+str(j),'core.props.plank',pos=[mul(x*.5,sub(size,.01)),mul(size,(j+.5)/4),0],rot=[0,90,0],params={'length':sub(size,.04),'width':mul(size,.235),'thickness':.026}))
 for j in range(4):crate.append(inst('floor'+str(j),'core.props.plank',pos=[0,.04,mul(size,(j-1.5)*.24)],rot=[90,0,0],params={'length':sub(size,.05),'width':mul(size,.237),'thickness':.032}))
 for side,z in [('front',1),('back',-1)]:
  for j,rot in enumerate([45,-45]):crate.append(inst(side+'brace'+str(j),'core.props.plank',pos=[0,mul(size,.5),mul(z,.5*1.0 if j==0 else .525)],rot=[0,0,rot],params={'length':mul(size,1.18),'width':.065,'thickness':.025}))
 # Z placement of braces is tied to box size, not a static offset.
 for it in crate:
  if 'brace' in it['id']:it['position'][2]=mul(size,.527 if it['id'].startswith('front') else -.527)
 assembly('kit-crate-body','木箱体总成 · 空腔与真实板件','props',crate,level=2,params=schema(size=number(.72,.58,.9,'木箱边长',.01,'m')))
 lid=[]
 for j in range(4):lid.append(inst('board'+str(j),'core.props.plank',pos=[0,0,mul(size,(j-1.5)*.245)],rot=[90,0,0],params={'length':size,'width':mul(size,.238),'thickness':.037}))
 for z in [-.29,.29]:lid.append(inst('rail'+str(z).replace('.','_').replace('-','n'),'core.props.plank',pos=[0,.028,mul(size,z)],rot=[90,0,0],params={'length':size,'width':.060,'thickness':.035}))
 assembly('kit-crate-lid','木箱盖总成 · 横向压条','props',lid,level=2,params=schema(size=number(.72,.58,.9,'盖板边长',.01,'m')))
 assembly('fnd-crate','木箱母版 · 板件 / 加固 / 可拆盖板','props',[inst('body',assembly='kit-crate-body',params={'size':size}),inst('lid',assembly='kit-crate-lid',pos=[0,add(size,.025),0],params={'size':size})],params=schema(size=number(.72,.58,.9,'木箱边长',.01,'m')))
 # Soft furniture has broad panels, local edge shaping and a clear timber structure.
 w,d,h=Q('width'),Q('depth'),Q('thickness')
 part('core.interior.cushion','软包坐靠垫 · 宽厚与边缘独立控制','interior',[
  profile([[0,0,0,mul(w,.45),mul(d,.45)],[0,mul(h,.15),0,mul(w,.495),mul(d,.495)],[0,mul(h,.72),0,mul(w,.49),mul(d,.49)],[0,h,0,mul(w,.43),mul(d,.43)]],'moss'),
 ],[.58,.16,.58],params=schema(width=number(.58,.34,1.2,'垫宽',.01,'m'),depth=number(.58,.34,.90,'垫深',.01,'m'),thickness=number(.16,.10,.25,'垫厚',.01,'m')),material='mat.fabric',ports=[port('base',[0,0,0],(0,-1,0),interface='seat.pad.v1')])
 part('core.interior.leg','家具支脚 · 木质锥腿','interior',[profile([[0,0,0,.032,.032],[0,.18,0,.041,.041],[0,.22,0,.045,.045]],'woodDark')],[.09,.22,.09],material='mat.wood',ports=[port('top',[0,.22,0],interface='furniture.leg.v1')])
 part('core.interior.armrest','扶手软包 · 保持边厚','interior',[box([.15,.30,.73],'moss',[0,.15,0],bevel=.025)],[.15,.3,.73],material='mat.fabric',ports=[port('base',[0,0,0],(0,-1,0),interface='seat.arm.v1')])
 W=Q('width');seat=sub(W,.27)
 base=[inst('front','core.props.plank',pos=[0,.26,.255],params={'length':sub(W,.06),'width':.115,'thickness':.047}),inst('back','core.props.plank',pos=[0,.26,-.255],params={'length':sub(W,.06),'width':.115,'thickness':.047})]
 for x in [-1,1]:
  base.append(inst('side'+str(x).replace('-','n'),'core.props.plank',pos=[mul(x*.5,sub(W,.12)),.26,0],rot=[0,90,0],params={'length':.59,'width':.12,'thickness':.044}))
  for z in [-.253,.253]:base.append(inst('leg'+str(x).replace('-','n')+str(z).replace('-','n').replace('.','_'),'core.interior.leg',pos=[mul(x*.5,sub(W,.14)),0,z]))
 assembly('kit-seat-frame','座椅木架总成 · 宽度联动四腿','interior',base,level=2,params=schema(width=number(.86,.76,1.10,'座椅外宽',.01,'m')))
 assembly('fnd-armchair','扶手椅母版 · 木架与独立软包','interior',[
  inst('frame',assembly='kit-seat-frame',params={'width':W}),inst('seat','core.interior.cushion',pos=[0,.319,.033],params={'width':seat,'depth':.59,'thickness':.16}),inst('back','core.interior.cushion',pos=[0,.706,-.222],rot=[76,0,0],params={'width':sub(W,.16),'depth':.61,'thickness':.14}),
  inst('armL','core.interior.armrest',pos=[mul(-.5,sub(W,.15)),.31,0]),inst('armR','core.interior.armrest',pos=[mul(.5,sub(W,.15)),.31,0]),inst('pillow','core.interior.cushion',pos=[.063,.608,-.074],rot=[71,0,-9],scale=[.61,.61,.61],params={'width':.50,'depth':.48,'thickness':.18,'palette':{P['moss']:P['yellow']}})
 ],params=schema(width=number(.86,.76,1.10,'座椅外宽',.01,'m')))
 author_architecture()
 author_terminal()
 # Ground modules use immutable edge vertices so neighbouring cells remain watertight.
 part('core.terrain.paving','路面模块 · 固定一米拼接边','terrain',[cube([1,.10,1],'stone',[0,-.05,0]),*[cube([.008,.002,.97],'stoneDark',[x,.001,0]) for x in [-.25,.25]],cube([.98,.002,.008],'stoneDark',[0,.001,0])],[1,.102,1],material='mat.stone',ports=[port('east',[.5,0,0],(1,0,0),(0,0,1),interface='grid.1m.v1'),port('west',[-.5,0,0],(-1,0,0),(0,0,1),interface='grid.1m.v1'),port('north',[0,0,-.5],(0,0,-1),interface='grid.1m.v1'),port('south',[0,0,.5],(0,0,1),interface='grid.1m.v1')])
 part('core.terrain.water','水面模块 · 固定拼接边 / 大切面','terrain',[cube([1,.035,1],'water',[0,-.018,0]),poly([[-.5,.001,-.5],[.5,.001,-.5],[.5,.001,.5],[-.5,.001,.5],[-.08,.001,.035]],[[0,1,4],[1,2,4],[2,3,4],[3,0,4]],'water',colors=['#47BED5','#58C7DC','#52C4D9','#4ABFD5'])],[1,.04,1],material='mat.water',ports=[port('east',[.5,0,0],(1,0,0),(0,0,1),interface='water.1m.v1'),port('west',[-.5,0,0],(-1,0,0),(0,0,1),interface='water.1m.v1')])

def poly_blades():
 return [poly([[0,0,0],[sg*.13,.19,.034],[sg*.075,.07,.052]],[[0,1,2]],'leafDark' if sg<0 else 'leafLight') for sg in [-1,1]]

def author_architecture():
 W,H,OW,OH=Q('width'),Q('height'),Q('opening_width'),Q('opening_height');a=mul(.5,W);b=mul(.5,OW)
 part('core.arch.door_wall','门洞墙板 · 真实贯穿 U 形开口','arch',[extrude([[neg(a),0],[neg(b),0],[neg(b),OH],[b,OH],[b,0],[a,0],[a,H],[neg(a),H]],.22,'cream')],[1.75,2.7,.22],params=schema(width=number(1.75,1.45,2.3,'墙板宽',.01,'m'),height=number(2.7,2.45,3.2,'墙高',.01,'m'),opening_width=number(.91,.78,1.1,'门洞宽',.01,'m'),opening_height=number(2.11,1.98,2.25,'门洞高',.01,'m')),material='mat.plaster',ports=[port('left',[neg(a),0,0],(-1,0,0),(0,1,0),interface='wall.edge.v1'),port('right',[a,0,0],(1,0,0),(0,1,0),interface='wall.edge.v1'),port('hinge',[neg(b),0,.035],interface='door.hinge.v1')])
 part('core.arch.window_wall','窗洞墙板 · 有厚度的真实洞口','arch',[extrude([[neg(a),0],[a,0],[a,H],[neg(a),H]],.22,'cream',holes=[[[neg(b),.99],[neg(b),add(.99,OH)],[b,add(.99,OH)],[b,.99]]])],[1.75,2.7,.22],params=schema(width=number(1.75,1.5,2.3,'墙板宽',.01,'m'),height=number(2.7,2.45,3.2,'墙高',.01,'m'),opening_width=number(1.06,.85,1.2,'窗洞宽',.01,'m'),opening_height=number(1.05,.9,1.2,'窗洞高',.01,'m')),material='mat.plaster',ports=[port('left',[neg(a),0,0],(-1,0,0),(0,1,0),interface='wall.edge.v1'),port('right',[a,0,0],(1,0,0),(0,1,0),interface='wall.edge.v1'),port('window',[0,.99,0],interface='window.1m.v1')])
 w,h=Q('width'),Q('height')
 part('core.arch.trim','建筑实木框条 · 统一窄倒角','arch',[box([w,h,.115],'wood',[0,mul(h,.5),0],bevel=.009)],[.08,2.2,.115],params=schema(width=number(.08,.025,1.5,'条宽',.01,'m'),height=number(2.2,.055,3,'条高',.01,'m')),material='mat.wood')
 part('core.arch.glass','建筑玻璃板 · 独立透明材质','arch',[cube([w,h,.012],'white',[0,mul(h,.5),0])],[.43,.94,.012],params=schema(width=number(.43,.2,1.3,'玻璃宽',.01,'m'),height=number(.94,.3,1.8,'玻璃高',.01,'m')),material='mat.glass')
 doorw=Q('width');doorh=Q('height')
 part('core.arch.door','木门扇 · 门框 / 凹板 / 铰轴','arch',[
  box([doorw,doorh,.065],'woodDark',[mul(.5,doorw),mul(.5,doorh),0],bevel=.01),
  *[box([sub(doorw,.12),mul(doorh,.39),.014],'wood',[mul(.5,doorw),mul(doorh,y),.04],bevel=.007) for y in [.25,.72]],
  box([sub(doorw,.16),.018,.025],'woodLight',[mul(.5,doorw),mul(.916,doorh),.05],bevel=.004),
  *[lathe([[.018,-.051],[.018,.051]],'metal',10,cap=True,position=[0,mul(doorh,y),0]) for y in [.16,.82]],
  box([.035,.14,.018],'steel',[sub(doorw,.095),mul(doorh,.49),.053],bevel=.005,material='mat.metal'),box([.12,.021,.025],'metal',[sub(doorw,.13),mul(doorh,.5),.08],bevel=.005,material='mat.metal')
 ],[.88,2.06,.14],anchor='hinge',params=schema(width=number(.88,.76,1.05,'门宽',.01,'m'),height=number(2.06,1.95,2.20,'门高',.01,'m')),material='mat.wood',ports=[port('hinge',[0,0,0],interface='door.hinge.v1')])
 window=[inst('left','core.arch.trim',pos=[mul(-.5,w),0,0],params={'width':.074,'height':h}),inst('right','core.arch.trim',pos=[mul(.5,w),0,0],params={'width':.074,'height':h}),inst('bottom','core.arch.trim',pos=[0,0,0],params={'width':add(w,.10),'height':.074}),inst('top','core.arch.trim',pos=[0,sub(h,.074),0],params={'width':add(w,.10),'height':.074}),inst('mullion','core.arch.trim',pos=[0,.058,.008],params={'width':.041,'height':sub(h,.116)}),inst('glassL','core.arch.glass',pos=[mul(-.25,w),.072,-.013],params={'width':sub(mul(.5,w),.065),'height':sub(h,.145)}),inst('glassR','core.arch.glass',pos=[mul(.25,w),.072,-.013],params={'width':sub(mul(.5,w),.065),'height':sub(h,.145)})]
 assembly('kit-window','木窗总成 · 框 / 中梃 / 独立玻璃','arch',window,level=2,params=schema(width=number(1.06,.85,1.2,'窗宽',.01,'m'),height=number(1.05,.9,1.2,'窗高',.01,'m')))
 wallW=Q('panel_width');floor=[]
 floor=[inst('doorWall','core.arch.door_wall',pos=[mul(-.5,wallW),0,0],params={'width':wallW}),inst('windowWall','core.arch.window_wall',pos=[mul(.5,wallW),0,0],params={'width':wallW}),inst('door','core.arch.door',pos=[sub(mul(-.5,wallW),.446),.018,.043],joint={'axis':[0,1,0],'limits':[-100,0]},angle=0),inst('window',assembly='kit-window',pos=[mul(.5,wallW),.99,.035]),inst('header','core.arch.trim',pos=[0,2.62,.06],params={'width':mul(2,wallW),'height':.095})]
 # Use a long timber beam for the lintel; trim width schema deliberately stays local.
 floor[-1]=inst('header','core.props.plank',pos=[0,2.67,.131],params={'length':mul(2,wallW),'width':.11,'thickness':.05})
 # Header length allowed up to five metres, a semantic board not scaled hardware.
 PARTS['core.props.plank']['parameter_schema']['properties']['length']['maximum']=5
 for x in [-1,1]:floor.append(inst('jamb'+('L' if x<0 else 'R'),'core.arch.trim',pos=[add(mul(-.5,wallW),x*.481),0,.115],params={'width':.08,'height':2.17}))
 floor += [inst('lintel','core.arch.trim',pos=[mul(-.5,wallW),2.10,.115],params={'width':1.05,'height':.081}),inst('sill','core.props.plank',pos=[mul(.5,wallW),.97,.18],rot=[90,0,0],params={'length':1.25,'width':.25,'thickness':.049})]
 assembly('fnd-wall-kit','门窗墙母版 · 真实洞口与门铰链','arch',floor,params=schema(panel_width=number(1.75,1.55,2.2,'单墙板宽',.01,'m')),metadata={'state_controls':[{'id':'door_open','title':'开门角度','node':'door','axis':[0,1,0],'min':-100,'max':0,'default':0,'unit':'°'}]})
 clip('fnd-wall-kit',[{'name':'Door open','duration':3,'tracks':[track('door',[0,1,0],[0,-90,0])]}])

def author_terminal():
 part('core.electronics.pedestal','终端机座 · 厚边外壳与检修面','gameplay',[
  box([.66,.085,.50],'steel',[0,.045,0],bevel=.022),profile([[0,.08,-.03,.25,.175],[0,.22,-.023,.23,.163],[0,.70,-.088,.19,.139],[0,.89,-.12,.18,.128]],'steel'),
  box([.27,.22,.011],'navy',[0,.325,.117],bevel=.012),box([.12,.044,.016],'yellow',[0,.333,.127],bevel=.005),
  *[cube([.03,.13,.008],'ink',[x,.60,.101]) for x in [-.075,-.0375,0,.0375,.075]],
  box([.05,.48,.020],'yellow',[-.184,.515,.021],bevel=.01),box([.05,.48,.020],'yellow',[.184,.515,.021],bevel=.01)
 ],[.66,.90,.51],material='mat.paint',ports=[port('screen',[0,.89,-.12],interface='terminal.screen.v1')])
 part('core.electronics.screen','终端显示模块 · 外壳 / 玻璃 / 发光信息','gameplay',[
  box([.54,.67,.11],'steel',[0,.335,0],bevel=.021),box([.452,.559,.022],'ink',[0,.363,.067],bevel=.013,material='mat.display'),
  # Information hierarchy is actual geometry. No poster image masquerades as a model.
  *[box([w,.022,.011],'cyan',[-.012,y,.084],bevel=.003,material='mat.emissive.cyan') for w,y in [(.295,.565),(.35,.514),(.27,.469),(.34,.221)]],
  *[box([.053,h,.008],'cyan',[x,.285+h*.5,.084],bevel=.003,material='mat.emissive.cyan') for x,h in [(-.14,.078),(-.058,.118),(.027,.155),(.114,.098)]],
  *[box([.016,.546,.009],'cyan',[x,.356,.086],bevel=.003,material='mat.emissive.cyan') for x in [-.242,.242]],
  box([.1,.029,.012],'yellow',[.15,.06,.068],bevel=.006,material='mat.emissive.amber')
 ],[.54,.67,.14],material='mat.paint',ports=[port('hinge',[0,0,0],interface='terminal.screen.v1')])
 part('core.electronics.keypad','输入键盘 · 护边与独立按键','gameplay',[
  box([.43,.072,.26],'steel',[0,0,0],bevel=.018),
  *[box([.058,.018,.052],'metal',[x,.045,z],bevel=.005,material='mat.metal') for x in [-.12,-.04,.04,.12] for z in [-.06,.03]],
  box([.031,.022,.13],'cyan',[-.187,.039,0],bevel=.006,material='mat.emissive.cyan')
 ],[.43,.106,.26],anchor='center',material='mat.paint')
 assembly('fnd-terminal','终端母版 · 机座 / 可调屏幕 / 发光分区','gameplay',[inst('base','core.electronics.pedestal'),inst('screen','core.electronics.screen',pos=[0,.89,-.12],rot=[-14,0,0]),inst('keypad','core.electronics.keypad',pos=[0,.77,.15],rot=[14,0,0])],metadata={'state_controls':[{'id':'screen_tilt','title':'屏幕倾角','node':'screen','axis':[1,0,0],'min':-10,'max':12,'default':0,'unit':'°'}]})
