"""83 inhabitable shells, open structures, utility towers and ruins."""
from .common import *

# key, label, span bays, depth bays, storeys, roof type, programme.
BUILDINGS=[
('cottage','山麓石屋',2,2,1,'pitched','chimney'),('rowhouse','联排住宅',2,2,2,'pitched','balcony'),
('townhouse','坡屋顶街屋',2,3,3,'pitched','balcony'),('villa','庭院别墅',3,3,2,'hip','porch'),
('bungalow','平层花园住宅',3,2,1,'hip','porch'),('a_frame','林间尖顶小屋',2,2,1,'steep','porch'),
('shop','街角商铺',3,2,1,'flat','awning'),('bakery','烟囱面包房',2,3,2,'pitched','chimney'),
('cafe','玻璃咖啡馆',3,2,1,'flat','terrace'),('inn','带廊乡村旅店',4,3,2,'hip','balcony'),
('library','社区图书馆',4,2,2,'flat','porch'),('clinic','社区诊所',3,3,1,'flat','sign'),
('school','乡村校舍',5,2,2,'pitched','porch'),('office','阶梯办公楼',3,3,4,'flat','terrace'),
('apartment','阳台公寓',3,3,4,'flat','balcony'),('museum','采光展览馆',4,3,1,'sawtooth','skylight'),
('workshop','机械修理车间',3,3,1,'sawtooth','workshop'),('warehouse','双跨仓库',4,4,1,'pitched','loading'),
('depot','货运集散站',5,2,1,'sawtooth','loading'),('station','铁路候车站房',5,2,1,'hip','awning'),
('firehouse','消防车库',4,3,2,'flat','garage'),('boathouse','水岸船库',2,4,1,'pitched','loading'),
('greenhouse','透明育苗温室',3,4,1,'glass','skylight'),('conservatory','八窗植物展厅',4,3,2,'glass','porch'),
('barn','高顶谷仓',3,4,1,'gambrel','loading'),('stable','带隔栏马厩',5,2,1,'pitched','stable'),
('farmhouse','双层农庄主屋',3,3,2,'gambrel','chimney'),('millhouse','水轮磨坊房',3,2,2,'pitched','mill'),
('temple','抬梁式祠堂',3,3,1,'hip','traditional'),('tea_house','临水茶室',3,2,1,'hip','traditional'),
('courtyard_gate','院落门房',3,1,1,'hip','traditional'),('pagoda_house','双檐楼阁',2,2,3,'hip','traditional'),
('guardhouse','值守岗亭',1,1,1,'flat','sign'),('checkpoint','双通道检查站',4,1,1,'flat','awning'),
('lodge','高脚湿地木屋',2,2,1,'pitched','stilt'),('mountain_hut','高山避难所',2,2,1,'steep','chimney'),
('desert_house','内凹屋顶沙漠民居',3,2,1,'flat','parapet'),('research_lab','海岸研究实验室',4,2,2,'flat','solar'),
('habitat','行星前哨居住舱',3,2,1,'barrel','airlock'),('control_center','工业控制楼',2,2,3,'flat','antenna'),
('power_house','变电所值班室',3,2,1,'flat','vents'),('observatory','圆顶观测站',2,2,2,'dome','telescope')]

def house(key,name,bx,bz,floors,roof,programme):
    bay=1.7;w=bx*bay;d=bz*bay;fh=2.65;lift=.9 if programme=='stilt' else 0;items=[]
    if lift:
        for i,(x,z) in enumerate(((-w/2+.2,-d/2+.2),(w/2-.2,-d/2+.2),(-w/2+.2,d/2-.2),(w/2-.2,d/2-.2))):items.append(block('stilt'+str(i),[.24,lift,.24],[x,0,z],color='#72614A'))
    items.append(block('foundation',[w+.18,.18,d+.18],[0,lift,0],color='#849295'))
    wallmat='mat.glass' if roof=='glass' else 'mat.plaster';wallcolor='#A7C8CD' if roof=='glass' else '#DED3B8'
    for f in range(floors):
        y=lift+.18+f*fh
        if f:items.append(block('slab'+str(f),[w,.12,d],[0,y,0],color='#9D9788'))
        # Continuous rear and side walls; window apertures are actual framed bays,
        # not dark decals laid over an opaque wall.
        for side,run,rot in [('left',bz,90),('right',bz,90),('back',bx,0)]:
            for j in range(run):
                x=(-w/2 if side=='left' else w/2) if side!='back' else (j-(run-1)/2)*bay
                z=(j-(run-1)/2)*bay if side!='back' else -d/2
                items.append(fit(f'{side}{f}_{j}',l2('architecture','wallbay','cavity'),[bay,fh,.2],[x,y,z],[0,rot,0]))
        for j in range(bx):
            x=(j-(bx-1)/2)*bay
            if f==0 and j==bx//2:
                # Wide ground portal with free passage and a controllable leaf.
                items += [block('doorpierL',[.14,fh,.22],[x-bay/2+.07,y,d/2],color=wallcolor),block('doorpierR',[.14,fh,.22],[x+bay/2-.07,y,d/2],color=wallcolor),block('lintel',[bay,.38,.22],[x,y+fh-.38,d/2],color=wallcolor)]
                items.append(fit('entrance','p5.habitat.door_panel',[bay-.3,fh-.4,.14],[x,y,d/2]))
            else:items.append(fit(f'front{f}_{j}',l2('architecture','wallbay','grid' if roof=='glass' else 'pilaster'),[bay,fh,.18],[x,y,d/2]))
        if programme in ('balcony','terrace') and f>0:
            items.append(block('balcony'+str(f),[w+.5,.15,1.1],[0,y-.1,d/2+.4]))
            items.append(fit('balustrade'+str(f),l2('architecture','railing','baluster'),[w+.5,.8,.12],[0,y,d/2+.9]))
    top=lift+.18+floors*fh;rh=.9 if roof not in ('steep','gambrel') else 1.9
    if roof in ('flat','glass'):
        items.append(block('roof',[w+.4,.22,d+.4],[0,top,0],color='#536571',material='mat.glass' if roof=='glass' else 'mat.paint'))
    elif roof in ('pitched','steep'):
        items.append(fit('roof','exp.arch.pitched_roof',[w+.6,rh,d+.6],[0,top,0]))
    else:
        rk={'hip':'hip_corner','sawtooth':'sawtooth','gambrel':'gambrel','barrel':'barrel','dome':'conical'}[roof]
        items.append(fit('roof',l1('architecture','roof',rk),[w+.6,rh,d+.6],[0,top,0]))
    if programme=='chimney':items+=[block('chimney',[.48,1.4,.48],[w*.25,top-.2,-d*.2],color='#9B6555'),fit('chimneycap',l1('architecture','trim','coping'),[.65,.16,.65],[w*.25,top+1.15,-d*.2])]
    if programme in ('porch','awning','loading','garage','traditional','stable','airlock'):
        items.append(block('porchroof',[w+.5,.16,1.7],[0,2.65+lift,d/2+.65],color='#657B72'))
        for i,x in enumerate([-w/2,w/2]):items.append(fit('porchpost'+str(i),l1('architecture','column','tuscan'),[.22,2.65+lift,.22],[x,0,d/2+1.3]))
        if programme=='loading':items.append(block('loadingdock',[w+.4,.65,1.8],[0,0,d/2+.7],color='#929996'))
    if programme=='traditional':
        for j in range(bx):items.append(fit('bracket'+str(j),l2('architecture','traditional','gong'),[.8,.55,.7],[(j-(bx-1)/2)*bay,top-.45,d/2]))
    if programme=='solar':
        for j in range(3):items.append(fit('solar'+str(j),'p5.power.solar_panel',[1.3,.08,1.1],[(j-1)*1.5,top+.25,0],[12,0,0],optional=True))
    if programme in ('antenna','telescope','vents','sign','skylight','workshop','mill','parapet','terrace'):
        ref={'antenna':l1('robot','sensor','antenna'),'telescope':l1('props','device','lens_barrel'),'vents':l1('industry','power','fan_guard'),'sign':l1('props','sign','round'),'skylight':l1('architecture','roof','barrel'),'workshop':l1('industry','pipe','elbow90'),'mill':l1('industry','drive','flywheel'),'parapet':l1('architecture','wall','castellated'),'terrace':l1('architecture','railing','glass')}[programme]
        items.append(fit('programme',ref,[1.2,1.2,.6],[0,top+.22,0],optional=True))
    return register('architecture','building',key,name,items,[w+.6,top+rh,d+2],['可进入围护结构','分层楼板','独立屋顶',programme,roof],notes=['墙体模块保留构造孔隙；不含导航网格或内部楼梯认证'])

def author():
    for row in BUILDINGS:house(*row)
    # Each open structure has a different load path / roof / access arrangement.
    shelters=[('gazebo','六柱休憩亭',6,'conical',False),('pergola','横梁花架',4,'flat_tile',True),('bandstand','八角音乐亭',8,'hip_corner',False),('bus_stop','单侧候车棚',2,'barrel',False),('market_stall','四柱集市棚',4,'gambrel',False),('arcade','连续拱廊',6,'barrel',True),('torii','横梁鸟居',2,'flat_tile',True),('moongate','月洞门',2,'hip_corner',True),('pump_shelter','水泵防雨棚',3,'standing_seam',False),('dock_shelter','码头遮阳棚',4,'butterfly',False),('picnic_shelter','野餐雨棚',6,'sawtooth',False),('solar_carport','太阳能停车棚',4,'flat_tile',False),('garden_gate','花园格栅门',2,'hyperbolic',True),('bus_terminal','双跨公交站棚',8,'butterfly',False),('colonnade','柱式步行廊',10,'barrel',True)]
    for key,name,n,roof,openroof in shelters:
        w=3.6 if n<6 else 5.6;d=2.8;h=2.5;items=[block('pad',[w+.4,.12,d+.4],[0,0,0],color='#959E91')]
        for i in range(n):
            x=(-w/2 if i%2==0 else w/2);z=(i//2/max(1,n//2-1)-.5)*d
            items.append(fit('column'+str(i),l1('architecture','column','tuscan'),[.2,h,.2],[x,.12,z]))
        if openroof:
            for j in range(6):items.append(block('crossbeam'+str(j),[w+.5,.15,.12],[0,h,(j/5-.5)*(d+.4)],color='#8D704E'))
        else:items.append(fit('canopy',l1('architecture','roof',roof),[w+.7,.7,d+.7],[0,h,0]))
        if key in ('torii','moongate','garden_gate'):items.append(fit('portal',l1('architecture','traditional','moon_gate' if key=='moongate' else 'lattice'),[w,h,.2],[0,0,0]))
        if key=='solar_carport':items.extend([fit('panel'+str(i),'p5.power.solar_panel',[1.6,.08,2.5],[(i-.5)*1.7,h+.75,0]) for i in range(2)])
        register('architecture','shelter',key,name,items,[w+.7,h+.8,d+.7],['独立支撑柱','开放通行区',roof,'格栅顶' if openroof else '实体顶'])
    towers=[('watch','开放瞭望塔',4,'platform'),('lighthouse','灯塔',6,'lantern'),('water','高架水塔',4,'tank'),('silo','筒仓',3,'vessel'),('clock','钟楼',5,'clock'),('bell','钟亭塔',3,'bell'),('radio','无线电塔',6,'antenna'),('windmill','风车塔',4,'wind'),('cooling','工业冷却塔',5,'cooling'),('pagoda','层檐宝塔',5,'pagoda'),('chimney','烟囱塔',7,'chimney'),('gate','城门哨塔',3,'battlement'),('beacon','海岸信标架',2,'beacon'),('crane','固定起重塔',5,'crane')]
    for key,name,levels,topkind in towers:
        h=levels*1.2;w=2.1;items=[]
        if topkind in ('antenna','wind','crane','platform','tank'):
            for i,(x,z) in enumerate(((-.8,-.8),(.8,-.8),(-.8,.8),(.8,.8))):items.append(block('upright'+str(i),[.18,h,.18],[x,0,z],color='#6A7880'))
            for j in range(levels):
                for s,z in enumerate([-.8,.8]):items.append(beam(f'brace{j}_{s}',[-.8,j*1.2,z],[.8,(j+1)*1.2,z],.1))
        else:items.append(fit('shaft',l1('architecture','column','tapered'),[w,h,w],[0,0,0],color='#B0A58A'))
        items.append(block('deck',[w+.6,.18,w+.6],[0,h,0],color='#74888B'))
        ref={'lantern':l1('props','lamp','lantern_frame'),'tank':l1('props','vessel','churn'),'vessel':l1('props','vessel','bottle'),'clock':l1('props','narrative','watch_case'),'bell':l1('props','musical','bell'),'antenna':l1('robot','sensor','antenna'),'wind':l1('vehicle','aero','prop_blade'),'cooling':l1('props','vessel','crucible'),'pagoda':l1('architecture','roof','hip_corner'),'chimney':l1('industry','pipe','socket'),'battlement':l1('architecture','wall','castellated'),'beacon':l1('props','lamp','cage'),'crane':l1('robot','link','lattice'),'platform':l1('architecture','railing','cable')}[topkind]
        items.append(fit('crown',ref,[w+1,1.4,w+1],[0,h+.18,0]))
        if topkind=='pagoda':
            for j in range(1,levels):items.append(fit('eave'+str(j),ref,[w+1-j*.1,.45,w+1-j*.1],[0,j*1.2,0]))
        register('architecture','tower',key,name,items,[w+1,h+1.6,w+1],['基础承重体','检修平台',topkind])
    ruins=[('gate','残破城门', 'broken_arch',3),('colonnade','断柱遗址','fractured_column',5),('bridge','断桥桥头','collapsed_lintel',4),('bunker','废弃掩体','exposed_rebar',3),('wall','破损城墙','chipped_brick',7),('temple','古庙遗址','eroded_cornice',6),('courtyard','残垣庭院','cracked_slab',8),('tower','断塔基座','fractured_column',4),('aqueduct','废弃水道','broken_arch',6),('stair','塌落阶梯','rubble_wedge',5),('factory','厂房残架','exposed_rebar',7),('shrine','风化神龛','eroded_cornice',3)]
    for key,name,kind,n in ruins:
        items=[block('footing',[4,.16,3],[0,0,0],color='#9B9C89')]
        for i in range(n):
            x=(i%3-1)*1.2;z=(i//3-1)*1.15
            items.append(fit('remnant'+str(i),l1('architecture','ruin',kind),[1.05,.6+(i%3)*.6,.55],[x,.16,z],[0,(i%2)*90,0]))
        items.append(fit('debris',l1('architecture','ruin','rubble_wedge'),[1.7,.28,1.2],[0,.16,1],optional=True))
        register('architecture','ruin',key,name,items,[4,2.3,3.8],['结构性断口','独立残片','可拆地基',kind])
