"""Thirty semantic nature parts, fourteen organisms and six habitat recipes.
Shapes are deliberately composed, deterministic and parameterised, not random scatter.
"""
from .common import *
from .terrain import prism_xz
DETAIL=schema(detail={'type':'integer','minimum':0,'maximum':1,'default':1,'title':'轮廓精度'})
LOD={'levels':[{'level':0,'parameters':{'detail':1},'screen_height':.15},{'level':1,'parameters':{'detail':0},'screen_height':.04}],'method':'authored-silhouette','preserves_pivot':True}

def branch(points,r=.14,color='woodDark'):
    return loft([list(p)+[r*(1-i/(len(points)+.4)),r*(1-i/(len(points)+.4))] for i,p in enumerate(points)],color,8,roundness=.15,style_overrides={'toon':{'smooth_angle':48}})
def leafblade(a,b,w=.12,color='leaf'):
    # Closed six-point leaf, with a central ridge and a tapered but non-zero tip.
    dx,dz=b[0]-a[0],b[2]-a[2];ln=math.hypot(dx,dz) or 1;nx,nz=dz/ln*w,-dx/ln*w
    m=[(a[k]+b[k])*.5 for k in range(3)]
    points=[a,[m[0]+nx,m[1],m[2]+nz],b,[m[0]-nx,m[1],m[2]-nz],[m[0],m[1]+w*.25,m[2]],[m[0],m[1]-w*.16,m[2]]]
    return topo(points,[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[1,0,5],[2,1,5],[3,2,5],[0,3,5]],color)
def crown_forms(color='leaf',broad=True):
    return [ico(s,color if i%3 else 'leafLight',p,Q('detail'),distort=.035,style_overrides={'toon':{'smooth_angle':54}}) for i,(s,p) in enumerate([
        ([2.5,1.65,2.0],[0,.5,0]),([1.55,1.35,1.55],[-.9,.38,.3]),([1.6,1.5,1.5],[.78,.54,-.14]),([1.8,1.4,1.6],[.0,1.12,-.16]),([1.7,1.25,1.5],[.05,.36,.88])])]

def author():
    # Woody structures: all trunks have a true ground pivot and a canopy mount.
    ports=[socket('canopy',[0,2.8,0],[0,1,0],'tree.canopy',tangent=[1,0,0])]
    birch=[branch([[0,0,0],[-.06,.8,.01],[.04,1.7,0],[.10,2.85,.04]],.16,'birch'),branch([[.0,1.4,0],[-.45,2.05,0],[-.85,2.7,.04]],.065,'birch'),branch([[.02,1.9,0],[.5,2.5,-.2],[.72,2.83,-.2]],.055,'birch')]
    for y,x in [(.4,-.025),(.9,-.02),(1.5,.01),(2.2,.06)]:birch.append(box([.12,.045,.018],'birchMark',[x,y,.14],.002))
    ep('nature.birch_trunk','白桦树干 · 分叉与节疤','nature',birch,[1.6,2.9,.4],theme='forest',material='mat.wood',ports=ports,collision=trunk_collision(2.8,.16),tags=['树干','白桦'])
    ep('nature.broadleaf_bough','阔叶树干 · 三叉承重枝','nature',[branch([[0,0,0],[.03,1.0,0],[0,1.9,.1],[.12,3.1,.12]],.27),branch([[0,1.3,0],[-.65,2.1,0],[-1.0,2.8,.15]],.17),branch([[0,1.55,0],[.64,2.15,-.18],[1.1,2.8,-.25]],.16)], [2.4,3.2,.9],theme='forest',material='mat.wood',ports=ports,collision=trunk_collision(3,.25),tags=['阔叶树','分枝'])
    ep('nature.willow_trunk','柳树干 · 弯干与舒展枝','nature',[branch([[0,0,0],[.18,1,0],[.26,1.7,.07],[.1,2.6,.15]],.32),branch([[.2,1.1,0],[-.7,1.9,.2],[-1.4,2.2,.3]],.20),branch([[.22,1.3,0],[.85,1.95,-.14],[1.5,2.25,-.3]],.18)], [3.2,2.8,1],theme='swamp',material='mat.wood',collision=trunk_collision(2.6,.3),tags=['柳树','树干'])
    ep('nature.conifer_trunk','针叶树干 · 收分与枝节','nature',[branch([[0,0,0],[.02,1.3,0],[-.015,2.9,.02],[0,4.4,0]],.19),*[branch([[0,y,0],[math.cos(a)*r,y+.15,math.sin(a)*r]],.06) for y,r in [(1.2,.7),(2.0,.55),(2.8,.35)] for a in [0,2.1,4.2]]],[1.6,4.5,1.6],theme='snow',material='mat.wood',collision=trunk_collision(4.4,.18),tags=['针叶树','树干'])
    ep('nature.acacia_trunk','金合欢树干 · 伞状分枝','nature',[branch([[0,0,0],[.16,1.05,0],[.32,1.8,.05],[.2,2.7,.1]],.24),branch([[.22,1.25,0],[-.8,1.9,0],[-1.6,2.35,.15]],.17),branch([[.22,1.3,0],[1.1,1.95,-.15],[1.8,2.25,-.2]],.17)], [3.8,2.8,1],theme='desert',material='mat.wood',collision=trunk_collision(2.6,.24),tags=['金合欢','树干'])
    baobab=[loft([[0,0,0,.80,.70],[0,.5,0,.65,.57],[.06,1.6,0,.54,.48],[.1,2.65,0,.38,.34]],'wood',10)]
    for a in [0,1.8,3.7,5.2]:baobab.append(branch([[.1,2.1,0],[math.cos(a)*.7,2.75,math.sin(a)*.7],[math.cos(a)*1.25,3.25,math.sin(a)*1.25]],.17,'wood'))
    ep('nature.baobab_trunk','猴面包树干 · 蓄水干与放射枝','nature',baobab,[3.0,3.4,3.0],theme='desert',material='mat.wood',collision={'type':'capsule','radius':.67,'segment_start':[0,.67,0],'segment_end':[0,2.1,0]},tags=['猴面包树','树干'])
    mangrove=[branch([[0,.65,0],[.1,1.7,.06],[.12,2.85,0]],.24)]
    for a in [0,1.25,2.6,3.8,5.05]:mangrove.append(branch([[0,1.2,0],[math.cos(a)*.65,.75,math.sin(a)*.65],[math.cos(a)*1.05,0,math.sin(a)*1.05]],.115))
    ep('nature.mangrove_root','红树林支柱根 · 五向拱根','nature',mangrove,[2.3,3,2.3],theme='swamp',material='mat.wood',collision={'type':'compound','shapes':[trunk_collision(2.85,.24)]},tags=['红树林','支柱根'])
    dead=[branch([[0,0,0],[.06,1.1,0],[-.10,2.1,.06],[.18,3.0,.1]],.25,'stoneDark'),branch([[.04,1.2,0],[-.65,1.8,0],[-.9,2.4,.12]],.14,'stoneDark'),branch([[0,1.8,.03],[.55,2.2,-.2],[.8,2.15,-.32]],.10,'stoneDark')]
    ep('nature.deadwood_trunk','枯树干 · 风折断枝','nature',dead,[1.9,3.1,.9],theme='mountain',material='mat.wood',collision=trunk_collision(3,.23),tags=['枯树','风折树'])
    # Foliage volumes keep a small number of intentional, overlapping silhouette masses.
    ep('nature.leaf_crown','阔叶冠簇 · 五瓣轮廓','nature',crown_forms(),[3.5,2.1,3.2],theme='forest',material='mat.leaf',params=DETAIL,lod=LOD,tags=['叶冠','LOD'])
    maple=crown_forms('orange')
    for i,f in enumerate(maple):f['color']=C(['orange','red','orange','yellow','red'][i])
    ep('nature.maple_crown','枫树冠簇 · 层叠掌状色块','nature',maple,[3.5,2.1,3.2],theme='forest',material='mat.leaf',params=DETAIL,lod=LOD,tags=['枫树','叶冠','LOD'])
    curtain=[]
    for i in range(9):
        a=i*math.tau/9;r=1.3;curtain.append(loft([[math.cos(a)*r,.45,math.sin(a)*r,.25,.24],[math.cos(a)*(r+.2),-.25,math.sin(a)*(r+.2),.33,.25],[math.cos(a)*(r+.17),-1.25-(i%3)*.13,math.sin(a)*(r+.17),.055,.055]],'leaf' if i%3 else 'leafLight',6,frame_axis=[0,-1,0]))
    curtain.append(ico([3.05,1.0,3.05],'leafLight',[0,.52,0],Q('detail')))
    ep('nature.willow_curtain','垂柳叶幕 · 可透视垂枝','nature',curtain,[3.9,2.5,3.9],theme='swamp',material='mat.leaf',params=DETAIL,lod=LOD,tags=['柳树','垂叶'])
    ep('nature.spruce_tier','针叶冠层 · 非重叠锥环','nature',[loft([[0,0,0,1.45,1.32],[0,.3,0,1.10,1.02],[0,1.35,0,.055,.05]],'pine',10,frame_axis=[0,1,0])],[2.9,1.4,2.7],theme='snow',material='mat.leaf',tags=['针叶冠','云杉'])
    ep('nature.cypress_crown','柏树叶冠 · 紧凑柱形','nature',[loft([[0,0,0,.48,.42],[.02,.5,0,.78,.62],[-.015,1.5,.03,.65,.57],[.03,2.3,0,.36,.33],[0,2.75,0,.065,.06]],'pine',10,frame_axis=[0,1,0],style_overrides={'toon':{'smooth_angle':45}})],[1.6,2.8,1.3],theme='forest',material='mat.leaf',tags=['柏树','柱状冠'])
    bamboo=[]
    for i in range(5):bamboo += [rod([0,i*.52,0],[0,(i+1)*.52,0],.075,'leafDark',.07),disk(.082,.035,'leafLight',[0,(i+1)*.52,0],10)]
    for i,y in enumerate([1.2,1.8,2.3]):
        sign=1 if i%2 else -1;bamboo.append(rod([0,y,0],[sign*.55,y+.15,.15],.024,'leafDark',.013,6));bamboo += [leafblade([sign*.22,y+.10,.06],[sign*.7,y+.4,.1],.12),leafblade([sign*.3,y+.12,.09],[sign*.6,y-.13,.45],.1)]
    ep('nature.bamboo_culm','竹秆与披针叶 · 五节','nature',bamboo,[1.4,2.75,.8],theme='forest',material='mat.leaf',collision=trunk_collision(2.6,.075),tags=['竹子','竹节'])
    reeds=[]
    for i,(x,z,h) in enumerate([(-.2,0,1.25),(.0,.18,1.5),(.24,.08,1.1),(.06,-.2,1.35),(-.24,-.2,1.0)]):
        reeds.extend([rod([x,0,z],[x+.045,h,z],.022,'moss',.012,6),loft([[x+.045,h-.13,z,.045,.04],[x+.045,h+.1,z,.045,.04],[x+.045,h+.14,z,.02,.02]],'woodDark',6),leafblade([x,.3,z],[x+.28,.95,z+.12],.08,'moss')])
    ep('nature.reed_cluster','芦苇小簇 · 茎叶与花穗','nature',reeds,[.95,1.7,.7],theme='swamp',material='mat.leaf',tags=['芦苇','湿地'])
    fern=[]
    for j in range(7):
        a=j*math.tau/7;end=[math.cos(a)*.68,.27,math.sin(a)*.68];fern.append(rod([0,.03,0],end,.018,'leafDark',.009,5))
        for t in [.22,.43,.64,.82]:
            m=[end[0]*t,.08+math.sin(t*math.pi)*.27,end[2]*t]
            for s in [-1,1]:fern.append(leafblade(m,[m[0]+math.cos(a)*.12-math.sin(a)*s*.16*(1-t*.5),m[1]-.02,m[2]+math.sin(a)*.12+math.cos(a)*s*.16*(1-t*.5)],.07,'leaf'))
    ep('nature.fern_rosette','蕨类莲座 · 羽状复叶','nature',fern,[1.5,.48,1.5],theme='forest',material='mat.leaf',budget=5000,tags=['蕨类','地被'])
    cactus=[loft([[0,0,0,.28,.25],[0,1.9,0,.29,.25],[0,2.25,0,.18,.16],[0,2.34,0,.035,.035]],'leafDark',10),loft([[-.15,.85,0,.15,.14],[-.61,.98,0,.17,.16],[-.71,1.38,0,.16,.15],[-.70,1.72,0,.035,.035]],'leaf',8),loft([[.14,1.1,0,.14,.13],[.58,1.22,0,.15,.14],[.61,1.72,0,.13,.12],[.6,1.91,0,.035,.035]],'leaf',8)]
    ep('nature.cactus_column','柱形仙人掌 · 双臂分叉','nature',cactus,[1.65,2.4,.6],theme='desert',material='mat.leaf',collision=trunk_collision(2.3,.25),tags=['仙人掌','沙漠'])
    ep('nature.cactus_globe','球形仙人掌 · 棱脊与顶花','nature',[loft([[0,0,0,.34,.34],[0,.20,0,.52,.52],[0,.50,0,.49,.49],[0,.76,0,.28,.28],[0,.80,0,.06,.06]],'leaf',12),*[ico([.12,.10,.20],'yellow',[math.cos(a)*.13,.83,math.sin(a)*.13],0) for a in [0,1.26,2.52,3.78,5.04]]],[1.05,.9,1.05],theme='desert',material='mat.leaf',collision=trunk_collision(.85,.38),tags=['仙人掌','球形'])
    agave=[leafblade([0,.06,0],[math.cos(a)*r,h,math.sin(a)*r],.16,'leafDark' if i%2 else 'leaf') for i,(a,r,h) in enumerate([(i*math.tau/10, .8,.35+(i%2)*.1) for i in range(10)]+[(i*math.tau/5+.2,.4,.82) for i in range(5)])]
    ep('nature.agave_rosette','龙舌兰 · 双层剑叶','nature',agave,[1.7,.95,1.7],theme='desert',material='mat.leaf',tags=['龙舌兰','多肉'])
    lily=[prism_xz([(math.cos(a)*.47,math.sin(a)*.42) for a in [0,.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.3]]+[(0,0)],.018,'leaf',.025)]
    lily += [ico([.12,.10,.24],'cream',[math.cos(a)*.10,.07,math.sin(a)*.10],0,rotation=[0,-math.degrees(a),0]) for a in [0,1.26,2.52,3.78,5.04]]
    ep('nature.water_lily','睡莲 · 缺口浮叶与花','nature',lily,[1,.17,1],theme='swamp',material='mat.leaf',tags=['水草','浮叶'])
    # One family with meaningful shape choices, not separate recolours in the catalogue.
    modes=['grass','bush','flowers','moss','lichen','salt'];forms=[]
    for i in range(7):
        a=i*2.399;x=math.cos(a)*(.1+(i%3)*.13);z=math.sin(a)*(.1+(i%3)*.13)
        shapes={'grass':leafblade([x,0,z],[x+.12*math.cos(a),.35+(i%3)*.09,z+.12*math.sin(a)],.06),'bush':ico([.45,.55,.43],'leafDark',[x,.26,z],0),'flowers':ico([.15,.15,.15],'yellow',[x,.32,z],0),'moss':ico([.45,.09,.42],'moss',[x,.035,z],0),'lichen':ico([.40,.035,.36],'stoneLight',[x,.022,z],0),'salt':ico([.43,.035,.35],'cream',[x,.02,z],0)}
        # Switch within a forms array element is supported by the semantic evaluator.
        forms.append(choice('variant',shapes))
        # Every bloom is attached to a visible stalk. Other modes receive a
        # matching grounded stem/rock fleck instead of floating flower heads.
        stem=branch([[x,0,z],[x,.30,z]],.014,'leafDark')
        base=ico([.06,.035,.06],'earth',[x,.017,z],0)
        forms.append(choice('variant',{'flowers':stem},base))
    ep('nature.undergrowth','地被家族 · 草、灌、花、苔与盐壳','nature',forms,[1,.65,1],material='mat.leaf',params=schema(variant={'type':'string','enum':modes,'default':'grass','title':'生境形态'}),tags=['草丛','灌木','花丛','苔藓','盐碱'])
    vines=[]
    for i in range(5):
        x=(i-2)*.26;h=1.35+(i%2)*.3;vines.append(branch([[x,0,0],[x+.08,-h*.5,.06],[x-.05,-h,.10]],.023,'leafDark'))
        for j in range(5):vines.append(leafblade([x,-j*h/5,0],[x+(.2 if j%2 else -.2),-j*h/5-.17,.1],.085))
    ep('nature.vine_curtain','垂挂藤蔓 · 五条可透光叶链','nature',vines,[1.65,1.9,.35],theme='cave',material='mat.leaf',tags=['藤蔓','垂挂'])
    # Geology: solid volumes, measured lowpoly facets, bounded LOD on boulders only.
    ep('nature.boulder','巨石 · 承重体与偏心轮廓','nature',[ico([2.1,1.6,1.7],'stone',[0,.72,0],Q('detail'),distort=.075),ico([1.1,.85,1.1],'stoneDark',[.58,.33,.32],Q('detail'),distort=.05)],[2.5,1.65,2],theme='mountain',material='mat.stone',params=DETAIL,lod=LOD,collision={'type':'convex-hull','source':'visible-geometry'},tags=['岩石','巨石','LOD'])
    slab=topo([[-1.3,0,-.65],[1.2,0,-.75],[1.0,0,.75],[-1.25,0,.55],[-1.05,.32,-.5],[1.10,.42,-.55],[.9,.33,.53],[-.9,.23,.48]],[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],'stoneLight')
    ep('nature.rock_slab','片状岩 · 分层台面','nature',[slab],[2.6,.45,1.5],theme='mountain',collision={'type':'convex-hull','source':'visible-geometry'},tags=['片岩','踏石'])
    columns=[loft([[x,0,z,.32,.30],[x,h,z,.30,.28]],'basalt',6,frame_axis=[0,1,0]) for x,z,h in [(-.57,0,1.3),(0,0,2.1),(.57,0,1.7),(-.27,.5,.9),(.3,.5,1.35),(.0,-.5,1.55)]]
    ep('nature.basalt_columns','玄武岩柱群 · 六角节理','nature',columns,[1.9,2.2,1.6],theme='mountain',collision={'type':'authored-mesh','static_only':True,'source':'column-solids'},tags=['柱状岩','玄武岩'])
    crystals=[]
    for x,z,h,r,rot in [(0,0,1.6,.22,(0,0,0)),(-.4,.04,1.0,.17,(0,0,18)),(.34,.15,1.25,.18,(0,0,-17)),(.1,-.35,.76,.13,(-12,0,0))]:
        crystals.append(loft([[0,0,0,r,r],[0,h*.74,0,r*.92,r*.92],[0,h,0,.012,.012]],'crystal',6,position=[x,0,z],rotation=list(rot),frame_axis=[0,1,0]))
    ep('nature.crystal_cluster','晶体簇 · 独立六方生长体','nature',crystals,[1.2,1.65,1.1],theme='cave',material='mat.glass',collision={'type':'convex-hull','source':'visible-geometry'},tags=['水晶','冰晶','矿脉'])
    dune=terrain_grid(fn=lambda u,v:max(0,math.sin(math.pi*u)*math.sin(math.pi*v))**1.4*(.75+.28*math.sin(2*math.pi*u)),top='sand',side='sandShade')
    ep('nature.dune','风成沙丘 · 迎风缓坡与背风脊','nature',[dune],[4,1.25,4],theme='desert',collision={'type':'heightfield','static_only':True,'source':'authored-grid','grid':[9,9]},tags=['沙丘','地形'])
    erosion=[loft([[0,0,0,.65,.60],[.03,.4,0,.43,.39],[.11,1.2,.02,.29,.31],[.08,1.85,0,.85,.69],[0,2.1,0,1.02,.80],[0,2.3,0,.80,.65]],'sandShade',8,frame_axis=[0,1,0]),ico([1.9,.35,1.5],'sand',[0,2.20,0],0)]
    ep('nature.wind_eroded_rock','风蚀蘑菇岩 · 窄颈与保护帽','nature',erosion,[2.2,2.45,1.8],theme='desert',collision={'type':'authored-mesh','static_only':True,'source':'neck-and-cap'},tags=['风蚀岩','沙漠'])
    snow=[ico([2.3,.8,1.6],'snow',[0,.25,0],Q('detail'),distort=.05),ico([1.3,.6,1.25],'snow',[.60,.22,.25],Q('detail'),distort=.025)]
    ep('nature.snow_drift','雪堆与覆冰体 · 双瓣积雪','nature',snow,[2.8,.9,2.0],theme='snow',params=DETAIL,lod=LOD,collision={'type':'convex-hull','source':'visible-geometry'},tags=['雪堆','浮冰'])
    pool=[lathe([[.9,-.02],[1.35,-.02],[1.5,.10],[1.15,.20],[.92,.10]],'mud',16,closed_profile=True),disk(.97,.055,'river',[0,.01,0],20,material='mat.water')]
    ep('nature.wetland_pool','泥潭与泉眼 · 内凹环岸','nature',pool,[3,.25,3],theme='swamp',collision={'type':'authored-mesh','static_only':True,'source':'bank-ring','exclude_materials':['mat.water']},tags=['泥潭','泉眼','湿地'])
    # L2 plants: parameters flow to authored leaves; their LOD affects actual geometry.
    for ident,name,trunk,leaf,y,theme,scale in [('birch','白桦','birch_trunk','leaf_crown',2.6,'forest',[.85,.95,.85]),('maple','枫树','broadleaf_bough','maple_crown',2.55,'forest',[1.12,1.1,1.12]),('willow','垂柳','willow_trunk','willow_curtain',2.45,'swamp',[1.1,1.0,1.1]),('acacia','金合欢','acacia_trunk','leaf_crown',2.45,'desert',[1.5,.45,1.05]),('baobab','猴面包树','baobab_trunk','leaf_crown',3.1,'desert',[1.12,.65,1.12]),('mangrove','红树林','mangrove_root','leaf_crown',2.5,'swamp',[1,.65,1])]:
        ea(ident,name+' · 完整植株','nature',[pi('trunk','exp.nature.'+trunk),pi('crown','exp.nature.'+leaf,[0,y,0],scale=scale,params={'detail':Q('detail')})],theme=theme,params=DETAIL,lod=LOD,tags=['树木','LOD'])
    tiers=[pi('tier'+str(i),'exp.nature.spruce_tier',[0,y,0],scale=[s,s,s]) for i,(y,s) in enumerate([(1.0,1),(1.85,.82),(2.55,.65),(3.13,.47)])]
    ea('spruce','云杉 · 四层渐缩树冠','nature',[pi('trunk','exp.nature.conifer_trunk'),*tiers],theme='snow',tags=['针叶树','云杉'])
    ea('cypress','柏树 · 紧凑柱形冠','nature',[pi('trunk','exp.nature.conifer_trunk',scale=[.8,.7,.8]),pi('crown','exp.nature.cypress_crown',[0,.75,0])],theme='forest',tags=['柏树','防风林'])
    ea('dead-tree','风折枯树 · 根部岩屑','nature',[pi('trunk','exp.nature.deadwood_trunk'),pi('slab','exp.nature.rock_slab',[.45,0,.12],scale=[.5,.5,.5])],theme='mountain',tags=['枯树','风折'])
    # The hollow trunk reuses a ring volume, not a capped cylinder. The local
    # ring is authored as an instance of a semantic core shape in the trunk part.
    hollow=lathe([[.28,0],[.45,0],[.46,1.7],[.29,1.7]],'wood',10,closed_profile=True,rotation=[0,0,90],position=[.85,.44,0])
    PARTS['exp.nature.deadwood_trunk']['parameter_schema']=schema(form={'type':'string','enum':['standing','hollow-log','stump'],'default':'standing','title':'枯木结构'})
    original=PARTS['exp.nature.deadwood_trunk']['shape_params']['forms']
    # Entire lists may be selected by the semantic evaluator; keep a forms list
    # for static reference scanning, select individual closed primitives.
    for i,f in enumerate(original):original[i]=choice('form',{'standing':f,'hollow-log':hollow if i==0 else ico([.30,.18,.35],'woodDark',[.75 if i==1 else -.8,.50,.1],0),'stump':lathe([[.28,0],[.45,0],[.40,.65],[.27,.65]],'wood',10,closed_profile=True) if i==0 else ico([.32,.16,.36],'woodDark',[.4 if i==1 else -.4,.1,0],0)})
    ea('fallen-hollow-log','倒木 · 可见树洞与断枝','nature',[pi('log','exp.nature.deadwood_trunk',params={'form':'hollow-log'}),pi('moss','exp.nature.undergrowth',[.1,.66,0],scale=[.7,.5,.6],params={'variant':'moss'})],theme='forest',tags=['倒木','空心树干'])
    ea('bamboo-grove','竹簇 · 五杆错位生长','nature',[pi('culm'+str(i),'exp.nature.bamboo_culm',p,rot=[0,a,0],scale=[s,s,s]) for i,(p,a,s) in enumerate([([0,0,0],0,1),([.45,0,.18],65,.9),([-.38,0,.25],130,1.08),([.1,0,-.38],205,.82),([-.45,0,-.3],290,.88)])],theme='forest',tags=['竹林','植被簇'])
    ea('desert-succulents','沙漠多肉组 · 柱仙人掌与莲座','nature',[pi('tall','exp.nature.cactus_column'),pi('globe','exp.nature.cactus_globe',[.9,0,.4]),pi('agave','exp.nature.agave_rosette',[-1.15,0,.2],scale=[.75,.75,.75])],theme='desert',tags=['沙漠','多肉'])
    snowtiers=[]
    for i,(y,s) in enumerate([(1.3,.86),(2.1,.68),(2.8,.52),(3.33,.32)]):snowtiers.append(pi('snow'+str(i),'exp.nature.spruce_tier',[0,y,0],scale=[s,s*.65,s],params={'palette':{C('pine'):C('snow')}}))
    ea('snow-conifer','覆雪松 · 枝层承雪而非外包白球','nature',[ai('tree','exp-spruce'),*snowtiers],theme='snow',tags=['覆雪松','雪原'])
    ea('cliff-geology','崖面地质组 · 柱岩、层岩和矿脉','nature',[pi('columns','exp.nature.basalt_columns'),pi('slab','exp.nature.rock_slab',[1.05,0,.2],rot=[0,-25,8]),pi('boulder','exp.nature.boulder',[-1.2,0,.15],scale=[.7,.75,.7]),pi('ore','exp.nature.crystal_cluster',[.35,.1,.9],scale=[.55,.5,.55])],theme='mountain',tags=['岩层','矿脉','崖面'])
    # L3 curated habitat patches. No ground planes: they can be placed on a scene
    # without fighting its terrain. Footprints are intentionally open at the front.
    ea('biome-forest','温带森林组 · 冠层、灌层与林下','nature',[ai('birch','exp-birch',[-2.1,0,-.9]),ai('maple','exp-maple',[1.7,0,-1.4]),ai('cypress','exp-cypress',[3.7,0,-1.0]),ai('fallen','exp-fallen-hollow-log',[-.8,0,1.5],rot=[0,20,0]),pi('fern','exp.nature.fern_rosette',[.6,0,.65]),pi('flowers','exp.nature.undergrowth',[-2,0,1.3],params={'variant':'flowers'})],theme='forest',level=3,tags=['生物群落','森林'])
    ea('biome-desert','沙漠绿洲组 · 乔木遮蔽与耐旱层','nature',[ai('acacia','exp-acacia',[-2.0,0,-1.0]),ai('baobab','exp-baobab',[2.8,0,-2.2],scale=[.8,.8,.8]),ai('succulents','exp-desert-succulents',[.6,0,1.2]),pi('eroded','exp.nature.wind_eroded_rock',[-3,0,1.0],scale=[.75,.75,.75]),pi('salt','exp.nature.undergrowth',[2.8,0,.8],params={'variant':'salt'})],theme='desert',level=3,tags=['生物群落','沙漠'])
    ea('biome-swamp','沼泽湿地组 · 支柱根与挺水层','nature',[ai('willow','exp-willow',[-2.2,0,-1.5]),ai('mangrove','exp-mangrove',[2.2,0,-1]),pi('pool','exp.nature.wetland_pool',[0,0,.8]),pi('lily','exp.nature.water_lily',[.1,.05,.8]),*[pi('reed'+str(i),'exp.nature.reed_cluster',p) for i,p in enumerate([[-1.25,0,1.6],[1.3,0,.2],[1.7,0,1.6]])]],theme='swamp',level=3,tags=['生物群落','湿地'])
    ea('biome-snow','雪林组 · 承雪针叶林与风口','nature',[ai('snowA','exp-snow-conifer',[-1.8,0,-.8]),ai('snowB','exp-snow-conifer',[1.4,0,-1.5],scale=[.8,.85,.8]),pi('drift','exp.nature.snow_drift',[.5,0,1.3]),pi('ice','exp.nature.crystal_cluster',[-1.7,0,1.1],scale=[.6,.55,.6]),pi('lichen','exp.nature.undergrowth',[1.5,0,.9],params={'variant':'lichen'})],theme='snow',level=3,tags=['生物群落','雪原'])
    ea('biome-canyon','峡谷岩石组 · 节理与风化残留','nature',[ai('geology','exp-cliff-geology',[-1.3,0,-.7]),ai('dead','exp-dead-tree',[2.3,0,-1.1],scale=[.8,.85,.8]),pi('erosion','exp.nature.wind_eroded_rock',[2.1,0,1],scale=[.65,.65,.65]),pi('slab','exp.nature.rock_slab',[-.2,0,1.6],rot=[0,35,0])],theme='mountain',level=3,tags=['生物群落','峡谷'])
    ea('biome-cave','洞穴晶体组 · 留出探索通道','nature',[pi('basalt','exp.nature.basalt_columns',[-1.3,0,-.7],scale=[1.0,1.25,1.0]),pi('crystalA','exp.nature.crystal_cluster',[1.4,0,-.7]),pi('crystalB','exp.nature.crystal_cluster',[-1.6,0,1],scale=[.7,.6,.7]),pi('slab','exp.nature.rock_slab',[.2,0,1.5],scale=[.8,.7,.8]),pi('vine','exp.nature.vine_curtain',[-1.1,2.6,-.7]),pi('moss','exp.nature.undergrowth',[.6,0,.7],params={'variant':'moss'})],theme='cave',level=3,tags=['生物群落','洞穴'])
