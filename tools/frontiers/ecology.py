"""Curated replacements for the retired aquatic/insect/contraption categories."""
from .common import *

def author():
 # Fish bodies have one continuous trunk surface. Fins and tail use geometry,
 # never decals. The tail is an independent rotation node.
 fp('p6.fish.body','鱼体 · 连续梭形截面与鳃部','aquatic',[loft([[0,0,-.41,.024,.032],[0,.013,-.25,.061,.112],[0,.029,.0,.105,.157],[0,.027,.24,.102,.132],[0,.0,.41,.035,.046]],'solar',10,frame_axis=[0,0,1]),*[ico([.019,.020,.016],'ink',[sg*.080,.071,.265],0,distort=0) for sg in [-1,1]],*[poly([[sg*.077,-.015,.055],[sg*.24,-.12,-.075],[sg*.086,-.087,-.17]],[[0,1,2]],'alloy') for sg in [-1,1]],poly([[0,.15,-.10],[0,.35,-.16],[0,.27,.03],[0,.15,.14]],[[0,1,2,3]],'alloy'),*[tube([[sg*.089,.098,.16],[sg*.106,.02,.17],[sg*.080,-.08,.14]],.005,'ivory',5) for sg in [-1,1]]],[.49,.5,.85],theme='shared',anchor='center',material='mat.fur',level=2)
 fp('p6.fish.tail','鱼尾 · 分叉鳍面与尾柄','aquatic',[loft([[0,0,0,.025,.03],[0,0,-.08,.025,.045]],'solar',8,frame_axis=[0,0,1]),poly([[0,0,-.07],[0,.23,-.24],[0,.08,-.29],[0,0,-.21],[0,-.08,-.29],[0,-.23,-.24]],[[0,1,2,3],[0,3,4,5]],'alloy')],[.06,.48,.34],theme='shared',anchor='center',material='mat.fur')
 fa('world-reef-fish','近岸海鱼 · 摆尾游动母版','aquatic',[pi('body','p6.fish.body'),pi('tail','p6.fish.tail',[0,0,-.41])],'shared',metadata=controls(turn('tail','摆尾','tail',-25,25)))
 clip('world-reef-fish',[{'name':'Tail swimming','duration':.9,'tracks':[track('tail',[0,1,0],[-18,18,-18])]}])
 fp('p6.turtle.shell','海龟甲壳 · 放射甲片与腹甲','aquatic',[lathe([[.0,0],[.22,.0],[.39,.10],[.37,.24],[.23,.40],[.07,.44]],'moss',10,cap=True,scale=[1,1,1.32]),lathe([[.35,-.011],[.38,.051]],'ivory',10,cap=True,scale=[1,1,1.32]),*[tube([[math.sin(a)*r,y,math.cos(a)*r*1.32] for r,y in [(.36,.15),(.28,.34),(.08,.43)]],.008,'darkwood',5) for a in [i*math.pi/5 for i in range(10)]]],[.81,.5,1.09],theme='shared',material='mat.fur',level=2)
 fp('p6.turtle.flipper','龟鳍肢 · 宽扁轮廓与根部','aquatic',[loft([[0,0,0,.10,.05],[.24,-.02,.04,.09,.025],[.45,-.07,-.12,.04,.020],[.50,-.09,-.19,.006,.008]],'lichen',8,frame_axis=[1,0,0])],[.65,.18,.31],theme='shared',anchor='hinge',material='mat.fur')
 single('turtle-head','海龟头颈 · 伸出甲壳的连接件','aquatic',[loft([[0,.13,.35,.10,.07],[0,.15,.58,.12,.087],[0,.13,.73,.055,.059]],'lichen',8,frame_axis=[0,0,1]),*[ico([.014,.016,.012],'ink',[sg*.081,.205,.61],0,distort=0) for sg in [-1,1]]],[.25,.21,.46],'shared',material='mat.fur')
 turtle=[pi('shell','p6.turtle.shell'),ai('head','world-turtle-head')]
 for i,(sg,z) in enumerate([(-1,.23),(1,.23),(-1,-.31),(1,-.31)]):turtle.append(pi('flipper'+str(i),'p6.turtle.flipper',[sg*.29,.086,z],rot=[0,0 if sg>0 else 180,0],scale=[1 if z>0 else .7,1,1]))
 fa('world-sea-turtle','海龟 · 甲壳/头颈/四鳍肢','aquatic',turtle,'shared',metadata=controls({'id':'stroke','title':'前鳍划水','nodes':['flipper0','flipper1'],'axis':[0,0,1],'min':-16,'max':16,'default':0}))
 # Beetle: shell elytra, prothorax and six bent legs, at realistic display scale.
 fp('p6.insect.beetle_shell','甲虫壳体 · 鞘翅中缝与胸盾','insect',[ico([.12,.085,.17],'teal',[0,.075,-.025],1,distort=0),box([.003,.015,.14],'shadow',[0,.117,-.02],bevel=.0004),ico([.105,.058,.073],'shadow',[0,.082,.076],1,distort=0),ico([.058,.041,.061],'teal',[0,.074,.124],1,distort=0)],[.13,.12,.25],theme='shared',material='mat.paint')
 legs=[]
 for sg in [-1,1]:
  for z in [-.07,.0,.07]:legs.append(tube([[sg*.047,.07,z],[sg*.09,.056,z-.025],[sg*.14,.0,z+.036]],.0055,'shadow',5))
  legs.append(tube([[sg*.018,.086,.133],[sg*.041,.10,.16],[sg*.05,.088,.192]],.0032,'shadow',5))
 fp('p6.insect.beetle_legs','甲虫六足与触角 · 分节轮廓','insect',legs,[.30,.115,.31],theme='shared',material='mat.fur')
 fa('world-beetle','林地甲虫 · 六足完整结构','insect',[pi('shell','p6.insect.beetle_shell'),pi('legs','p6.insect.beetle_legs')],'shared')
 fp('p6.insect.butterfly_body','蝴蝶胸腹 · 头部与触角','insect',[loft([[0,.015,-.065,.006,.009],[0,.027,0,.012,.015],[0,.029,.051,.009,.012]],'shadow',7,frame_axis=[0,0,1]),*[tube([[sg*.005,.03,.046],[sg*.018,.068,.081],[sg*.03,.074,.087]],.0019,'shadow',5) for sg in [-1,1]]],[.068,.079,.16],theme='shared',material='mat.fur')
 # Give the wing a narrow root band and real membrane thickness. A single
 # zero-area root vertex disappears edge-on even when the hinge touches the body.
 outline=[[0,0,.038],[.07,0,.094],[.156,.006,.082],[.125,.009,.011],[.167,.004,-.058],[.08,.003,-.075],[.022,0,-.038],[0,0,-.035]]
 n=len(outline);points=outline+[[x,y-.0024,z] for x,y,z in outline]
 top=[[0,1,2,3],[0,3,4,5,6,7]]
 faces=top+[[i+n for i in reversed(face)]for face in top]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
 wing=[poly(points,faces,'orange'),poly([[.029,.003,.016],[.078,.003,.073],[.133,.01,.072],[.102,.011,.022]],[[0,1,2,3]],'amber'),poly([[.052,.004,-.012],[.105,.013,-.018],[.139,.008,-.049],[.081,.007,-.058]],[[0,1,2,3]],'shadow')]
 fp('p6.insect.butterfly_wing','蝴蝶单侧双翼 · 翼脉分区','insect',wing,[.172,.014,.177],theme='shared',anchor='hinge',material='mat.fur')
 fp('p6.insect.butterfly_wing_left','蝴蝶左翼 · 镜像保留前后缘','insect',[],[.172,.014,.177],components=[component('wing','p6.insect.butterfly_wing',mirror='x')],theme='shared',anchor='hinge',material='mat.fur')
 fa('world-butterfly','林地蝴蝶 · 独立翅根与扇动','insect',[pi('body','p6.insect.butterfly_body'),pi('wingR','p6.insect.butterfly_wing',[.006,.029,0]),pi('wingL','p6.insect.butterfly_wing_left',[-.006,.029,0])],'shared',metadata=controls({'id':'right_flap','title':'右翼上抬','node':'wingR','axis':[0,0,1],'min':0,'max':65,'default':0},{'id':'left_flap','title':'左翼上抬','node':'wingL','axis':[0,0,-1],'min':0,'max':65,'default':0}))
 clip('world-butterfly',[{'name':'Wing flutter','duration':.4,'tracks':[track('wingR',[0,0,1],[10,58,10]),track('wingL',[0,0,1],[-10,-58,-10])]}])
 fp('p6.mechanism.lever_base','机关底座 · 转轴/轴承/限位','mech',[box([.54,.09,.41],'alloy',[0,.045,0],bevel=.017),*[box([.083,.29,.21],'shadow',[x,.18,0],bevel=.023) for x in [-.12,.12]],disk(.08,.32,'amber',[0,.26,0],10,rotation=[0,0,90])],[.58,.36,.45],theme='shared',material='mat.metal')
 fp('p6.mechanism.lever','扳杆 · 局部铰轴与防滑握柄','mech',[rod([0,0,0],[0,.58,0],.028,'alloy',sides=8),box([.11,.21,.10],'rust',[0,.54,0],bevel=.032)],[.15,.7,.14],theme='shared',anchor='hinge',material='mat.metal')
 fa('world-lever','通用扳杆机关 · 双向转动','mech',[pi('base','p6.mechanism.lever_base'),pi('lever','p6.mechanism.lever',[0,.26,0])],'shared',metadata=controls(turn('angle','扳杆角度','lever',-40,40,(1,0,0))))
 fp('p6.mechanism.pressure_base','踏板外框 · 真正活动件开口','mech',[extrude([[-.58,-.45],[.58,-.45],[.58,.45],[-.58,.45]],.15,'alloy',holes=[[[-.48,-.35],[.48,-.35],[.48,.35],[-.48,.35]]],rotation=[90,0,0],position=[0,.08,0]),box([1.12,.032,.82],'shadow',[0,.022,0],bevel=.011)],[1.18,.18,.92],theme='shared',material='mat.metal')
 fp('p6.mechanism.pressure_top','压力踏板 · 刚性移动面与凹槽','mech',[box([.91,.055,.63],'amber',[0,0,0],bevel=.013),*[box([.66,.005,.019],'shadow',[0,.031,z],bevel=.003) for z in [-.21,-.10,0,.10,.21]]],[.95,.069,.67],theme='shared',anchor='center',material='mat.paint')
 fa('world-pressure-plate','通用压力板 · 可控压下行程','mech',[pi('base','p6.mechanism.pressure_base'),pi('top','p6.mechanism.pressure_top',[0,.18,0])],'shared',metadata=controls({'id':'press','title':'踏板行程','node':'top','mode':'translation','axis':[0,1,0],'min':-.07,'max':0,'default':0,'unit':'m','step':.005}))
