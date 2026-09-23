"""119 editable environment prefabs. Course topology defines identity, not seed."""
from .common import *
PATHS=[('straight','直线',[(0,-2),(0,2)]),('bend','弯道',[(0,-2),(0,0),(2,0)]),('switchback','回头弯',[(-1.8,-2),(-1.8,1),(1.8,1),(1.8,-2)]),('s_curve','S形道',[(-1.2,-2),(-1.2,-.5),(1.2,.5),(1.2,2)]),('cross','十字',[(0,-2),(0,2),None,(-2,0),(2,0)]),('tee','丁字',[(0,-2),(0,0),None,(-2,0),(2,0)]),('fork','分岔',[(0,-2),(0,0),(-1.8,2),None,(0,0),(1.8,2)]),('loop','环形',[(-1.5,-1.5),(-1.5,1.5),(1.5,1.5),(1.5,-1.5),(-1.5,-1.5)]),('dogleg','错位',[(0,-2),(0,-.5),(1.5,-.5),(1.5,2)]),('crossing','斜交',[(-2,-2),(2,2),None,(-2,2),(2,-2)]),('culdesac','尽端',[(0,-2),(0,1),(-1,1),(0,2),(1,1),(0,1)]),('hairpin','发夹',[(-1.4,-2),(-1.4,1.3),(0,2),(1.4,1.3),(1.4,-2)]),('zigzag','之字',[(-2,-2),(1.5,-.7),(-1.5,.7),(2,2)]),('arc','折线弧',[(-2,-2),(-1.8,0),(-.8,1.5),(1,2)]),('plaza','广场',[(0,-2),(0,2),None,(-2,0),(2,0),None,(-1,-1),(1,1)]),('spur','岔支',[(-2,0),(2,0),None,(0,0),(1,2)]),('diagonal','对角线',[(-2,-2),(2,2)]),('parallel','双道',[(-.9,-2),(-.9,2),None,(.9,-2),(.9,2)]),('grid','双丁字',[(-1,-2),(-1,2),None,(1,-2),(1,2),None,(-1,0),(1,0)]),('serpentine','蛇形',[(-1,-2),(1,-1),(-1,0),(1,1),(-1,2)])]

def segments(path):
    prev=None
    for p in path:
        if p is not None and prev is not None:yield prev,p
        prev=p

def strip(name,a,b,width,y,height,color):
    dx=b[0]-a[0];dz=b[1]-a[1];L=math.hypot(dx,dz)
    return block(name,[width,height,L+.025],[(a[0]+b[0])/2,y,(a[1]+b[1])/2],[0,math.degrees(math.atan2(dx,dz)),0],color=color)

def author():
    for j,(key,label,path) in enumerate(PATHS):
        items=[fit('ground','exp.terrain.flat',[6,.2,6],[0,-.2,0])]
        for i,(a,b) in enumerate(segments(path)):
            items.append(strip('carriageway'+str(i),a,b,.95,.005,.045,'#596770'))
            dx=b[0]-a[0];dz=b[1]-a[1];ll=math.hypot(dx,dz);ox=dz/ll*.54;oz=-dx/ll*.54
            for s in (-1,1):items.append(strip(f'kerb{i}_{s}',(a[0]+s*ox,a[1]+s*oz),(b[0]+s*ox,b[1]+s*oz),.09,.005,.1,'#B8B7A8'))
            if i%2==0:items.append(strip('mark'+str(i),a,b,.035,.052,.005,'#E7DFB5'))
        if key in ('plaza','culdesac'):items.append(fit('centerpiece',l1('architecture','floor','octagonal'),[1,.08,1],[0,.008,0]))
        register('terrain','road',key,label+'路段预制块',items,[6,.3,6],['道路与路缘分离','真实折线轨迹',key],notes=['拐角路缘未做道路工程级圆角布尔；中心线可用于路径编辑'])
    for j,(key,label,path) in enumerate(PATHS):
        items=[fit('bed','exp.terrain.flat',[6,.18,6],[0,-.18,0],params={'surface':'swamp'})]
        for i,(a,b) in enumerate(segments(path)):
            items.append(strip('water'+str(i),a,b,1.1,.002,.035,'#5596AA'));items[-1]['material']='mat.water'
            dx=b[0]-a[0];dz=b[1]-a[1];ll=math.hypot(dx,dz);ox=dz/ll*.68;oz=-dx/ll*.68
            for s in (-1,1):items.append(strip(f'bank{i}_{s}',(a[0]+s*ox,a[1]+s*oz),(b[0]+s*ox,b[1]+s*oz),.24,-.01,.16,'#899667'))
        items.append(fit('bank_detail',l1('terrain','edge','riprap' if j%2 else 'marsh'),[.6,.24,.8],[-2.1,.01,-1.3],optional=True))
        register('terrain','river',key,label+'水道预制块',items,[6,.4,6],['独立水面','两侧河岸','分段流向',key],notes=['水面为静态几何；流体与动态湿边由消费者实现'])
    forms=[('mesa','孤立台地','plateau'),('escarpment','单侧断崖','cliff_straight'),('inner_cliff','内凹崖','cliff_inner'),('outer_cliff','外凸崖','cliff_outer'),('gorge','峡谷','gully'),('terraces','阶地','steps'),('ramp','天然坡道','slope'),('saddle','鞍部','corner_in'),('ridge','脊线','corner_out'),('canyon','双壁峡谷','cliff_straight'),('butte','石柱孤峰','plateau'),('bowl','环壁盆地','corner_in'),('notch','崖壁豁口','cliff_straight'),('overhang','岩檐','cliff_inner'),('talus','崩积坡','slope'),('arch','天然石拱','plateau'),('columnar','柱状节理群','cliff_outer'),('volcanic','火山口台地','corner_in'),('icefall','冰崖','cliff_straight'),('sinkhole','塌陷坑口','gully')]
    for j,(key,name,shape) in enumerate(forms):
        items=[fit('mass','exp.terrain.'+shape,[5,2.4,5],[0,0,0])]
        feature=['notch','overhang','pinnacle','talus','columnar','buttress','arch_foot'][j%7]
        for i in range(2+j%4):items.append(fit('outcrop'+str(i),l1('terrain','cliff',feature),[1,1.2,.8],[(i%3-1)*1.25,.1,(i//3-.5)*2],[0,90*(i%4),0]))
        if key in ('gorge','canyon','icefall'):items.append(fit('waterfall','exp.terrain.waterfall',[1.2,2.6,1.4],[0,0,1]))
        if key=='arch':items.append(fit('arch','exp.terrain.cave_arch',[3.2,2.5,.9],[0,1,0]))
        register('terrain','landform',key,name,items,[5,3.8,5],['主地貌网格','附属岩体',shape,feature])
    islands=[('atoll','环礁',6,'beach'),('crescent','新月岛',5,'beach'),('delta','三角洲',3,'marsh'),('rocky','礁岩岛',4,'riprap'),('sandbar','沙洲',5,'beach'),('volcano','火山岛',7,'split'),('fjord','峡湾岛',6,'straight'),('mangrove','红树湿地岛',8,'root'),('iceberg','浮冰岛',4,'snow'),('archipelago','三岛群',3,'riprap'),('headland','岬角',4,'convex'),('lagoon','潟湖',8,'concave'),('spit','沙嘴',6,'beach'),('tidal','潮汐滩',7,'marsh'),('terraced','梯田岛',5,'stair')]
    for key,name,n,edge in islands:
        items=[fit('water','core.terrain.water',[7,.05,7],[0,-.1,0])]
        for i in range(n):
            a=math.tau*i/n;r=1.5 if key in ('atoll','lagoon') else 1.0
            x=r*math.sin(a);z=r*math.cos(a)
            if key in ('sandbar','spit'):x=(i-(n-1)/2)*.65;z=math.sin(i*.8)*.4
            if key=='archipelago':r=2;x=r*math.sin(a);z=r*math.cos(a)
            items.append(fit('shore'+str(i),l1('terrain','edge',edge),[1.8,.55,1.8],[x,0,z],[0,360*i/n,0]))
        if key in ('volcano','headland','terraced'):items.append(fit('center','exp.terrain.plateau',[2,2,2],[0,0,0]))
        register('terrain','island',key,name,items,[7,2.3,7],['独立水域','多片岸线',key,edge])
    caves=[('arch','岩拱洞口',1,'stalactite'),('tunnel','双拱隧道',3,'rib'),('fork','分叉洞室',4,'stalagmite'),('grotto','滴水岩洞',2,'flowstone'),('mine','支护矿洞',3,'ledge'),('fissure','裂隙洞',1,'fissure'),('ice','冰洞',2,'stalactite'),('lava','熔岩管道',4,'rib'),('chamber','宽阔石室',5,'stalagmite'),('sump','积水洞室',2,'flowstone'),('ruin','遗迹地下通道',3,'ledge'),('sink','落水洞',4,'fissure')]
    for key,name,n,detail in caves:
        items=[fit('floor','exp.terrain.flat',[5,.15,5],[0,-.15,0],params={'surface':'cave'})]
        for i in range(n):items.append(fit('vault'+str(i),'exp.terrain.cave_arch',[3,2.2,.65],[(i%2)*.8,0,(i-(n-1)/2)*.8],[0,30*(i%2) if key=='fork' else 0,0]))
        for i in range(4):items.append(fit('formation'+str(i),l1('terrain','cave',detail),[.6,1,.6],[(-1 if i%2 else 1)*1.45,0,(i//2-.5)*1.2]))
        if key=='sump':items.append(fit('pool','core.terrain.water',[2.5,.04,1.5],[0,.01,0]))
        register('terrain','cave',key,name,items,[5,2.5,5],['可通行洞口','独立底面',detail,key])
    bridges=[('beam','简支梁桥',2,False),('arch','石拱桥',3,False),('suspension','悬索步桥',6,True),('truss','钢桁架桥',4,True),('boardwalk','湿地栈桥',5,False),('rope','绳索桥',7,True),('draw','吊桥',2,True),('pontoon','浮桥',4,False),('covered','廊桥',5,True),('viaduct','高架桥',6,False),('stepping','踏步石桥',8,False),('culvert','涵桥',2,False)]
    for key,name,n,rails in bridges:
        length=4.8;h=.65;items=[]
        if key=='stepping':
            for i in range(n):items.append(fit('stone'+str(i),'exp.nature.rock_slab',[.8,.3,.5],[0,0,(i/(n-1)-.5)*length]))
        else:
            items.append(block('deck',[1.5,.14,length],[0,h,0],color='#8D795C'))
            for i in range(n):
                z=(i/max(1,n-1)-.5)*length
                for s in (-1,1):items.append(block(f'pier{i}_{s}',[.15,h,.15],[s*.6,0,z]))
                if rails:items.append(fit('rail'+str(i),l1('architecture','railing','cable' if key in ('rope','suspension') else 'cross'),[1,.75,.06],[.72,h,z],[0,90,0]))
            if key in ('arch','culvert'):items.append(fit('arch','exp.terrain.cave_arch',[2,h+.2,1.4],[0,0,0],[0,90,0]))
            if key=='covered':items.append(fit('roof','exp.arch.pitched_roof',[2,.6,length+.2],[0,h+1.6,0]))
        register('terrain','bridge',key,name,items,[2,2.8,length+.2],['桥面','真实支点',key,'护栏' if rails else '开放侧边'])
    # Ten explicit transition boundary geometries, each with its own crossing.
    transitions=[('beach_dune','海滩—沙丘','beach','dune'),('forest_marsh','森林—湿地','root','hummock'),('rock_snow','山岩—积雪','snow','bedrock'),('field_road','田地—道路','straight','furrow'),('lava_rock','熔岩—岩地','split','lava'),('stream_grass','溪流—草地','concave','ripple'),('cliff_scree','悬崖—碎石','stair','scree'),('desert_oasis','沙漠—绿洲','convex','basin'),('mud_stone','泥地—铺石','riprap','rutted'),('terrace_meadow','梯田—草甸','stair','terrace')]
    for key,name,edge,surface in transitions:
        for crossing in ('footpath','watercourse'):
            items=[fit('left',l1('terrain','surface',surface),[2.5,.3,5],[-1.25,0,0]),fit('boundary',l1('terrain','edge',edge),[1.2,.45,5],[0,0,0]),fit('right','exp.terrain.flat',[2.5,.2,5],[1.25,0,0]),block('crossing',[5,.06,.8],[0,.32,0],color='#7F9EAA' if crossing=='watercourse' else '#B8A580')]
            if crossing=='watercourse':items[-1]['material']='mat.water'
            else:items.append(fit('marker',l1('props','sign','milestone'),[.2,.6,.2],[-2,.3,.65]))
            register('terrain','transition',key+'_'+crossing,name+('涉水口' if crossing=='watercourse' else '步行口'),items,[5,.95,5],['双环境边界','独立跨界通道',edge,surface,crossing])
