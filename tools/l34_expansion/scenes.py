"""97 source-editable scenes with per-object layers, zones and placement records.

These are curated production dioramas / vertical slices, not navigation-ready
open worlds. No palette, camera or random seed alone creates a new scene ID.
"""
from .common import *
# Each record selects a genuinely different focal structure and a secondary use.
# Theme environments are shared design language, not baked, flattened meshes.
THEMES=[
('urban','现代街区',[
('residential','住宅入口','architecture-building-townhouse','interior-service-coatstand'),('corner_shop','街角商店','architecture-building-shop','props-street-parcel'),('library','图书馆前庭','architecture-building-library','props-street-notice'),('clinic','社区医疗站','architecture-building-clinic','vehicle-road-ambulance'),('office','办公楼入口','architecture-building-office','props-street-bike_rack'),('apartment','公寓共享院','architecture-building-apartment','interior-seat-bench'),('cafe','街边咖啡店','architecture-building-cafe','interior-table-side'),('checkpoint','街区检查站','architecture-building-checkpoint','gameplay-interactive-lever_gate')]),
('heritage','传统街巷',[
('teahouse','临水茶室','architecture-building-tea_house','interior-table-altar'),('temple','祠堂前坪','architecture-building-temple','props-narrative-reliquary'),('gate','院落门庭','architecture-building-courtyard_gate','architecture-shelter-moongate'),('pagoda','楼阁花园','architecture-building-pagoda_house','props-lamp-lanternpost'),('market','传统集市','architecture-shelter-market_stall','props-container-hamper'),('arcade','拱廊街角','architecture-shelter-arcade','props-street-wayfinding'),('shrine','古祠遗址','architecture-ruin-shrine','props-narrative-scroll'),('garden','格栅庭园','architecture-shelter-pergola','interior-service-screen')]),
('interior','完整室内',[
('living','起居室','interior-seat-sofa','interior-storage-media'),('bedroom','卧室','interior-bed-double','interior-storage-wardrobe'),('kitchen','家庭厨房','interior-kitchen-island','interior-appliance-fridge'),('bathroom','卫浴空间','interior-sanitary-bath','interior-sanitary-vanity'),('office','共享办公','interior-table-conference','interior-seat-office'),('library','阅读室','interior-storage-bookcase','interior-table-seminar'),('nursery','儿童房','interior-bed-crib','interior-storage-corner'),('reception','接待大厅','interior-service-reception','interior-seat-armchair')]),
('factory','工业厂区',[
('machine_shop','机加工车间','industry-machine-lathe','industry-machine-mill'),('process','处理工艺区','industry-process-reactor','industry-process-filter'),('power','能源配电区','industry-power-transformer','industry-power-switchgear'),('sorter','分拣线','industry-logistics-sorter','robot-arm-pick'),('welding','焊接工位','industry-machine-welder','robot-arm-weld'),('pump','泵站','industry-process-pump','industry-process-water'),('packing','包装工位','industry-logistics-packing','robot-arm-suction'),('warehouse','装卸仓储','architecture-building-warehouse','vehicle-utility-forklift')]),
('farm','田园农业',[
('farmhouse','农庄院落','architecture-building-farmhouse','vehicle-utility-tractor'),('barn','谷仓装卸','architecture-building-barn','props-container-grain'),('stable','马厩活动区','architecture-building-stable','creature-mammal-pack_donkey'),('greenhouse','温室种植','architecture-building-greenhouse','nature-crop-tomato'),('orchard','果园作业','nature-tree-apple','vehicle-road-pickup'),('rice','水稻田边','nature-crop-rice','terrain-transition-field_road_footpath'),('mill','磨坊水边','architecture-building-millhouse','terrain-river-bend'),('market','农产品市集','architecture-shelter-market_stall','props-container-tote')]),
('harbor','港口海岸',[
('fishing','渔船泊位','vehicle-marine-fishing','architecture-building-boathouse'),('ferry','轮渡码头','vehicle-marine-ferry','architecture-shelter-dock_shelter'),('cargo','货运泊位','vehicle-marine-barge','industry-logistics-gantry'),('lighthouse','灯塔岬角','architecture-tower-lighthouse','terrain-island-headland'),('marina','游艇码头','vehicle-marine-yacht','terrain-bridge-boardwalk'),('tug','拖船作业点','vehicle-marine-tug','props-container-cylinder'),('research','科考泊位','vehicle-marine-research','robot-underwater-rov'),('rescue','海岸救助站','vehicle-marine-patrol','architecture-building-clinic')]),
('transit','交通枢纽',[
('rail_station','铁路站台','architecture-building-station','vehicle-rail-passenger'),('tram','有轨电车站','vehicle-rail-tram','architecture-shelter-bus_stop'),('bus','公交换乘站','vehicle-road-city_bus','architecture-shelter-bus_terminal'),('logistics','公路物流站','architecture-building-depot','vehicle-road-delivery'),('airport','支线机场','vehicle-air-trainer','architecture-building-control_center'),('helipad','直升机停机坪','vehicle-air-helicopter','props-lamp-beacon'),('charging','电动车补能点','industry-power-charger','vehicle-road-estate'),('freight','铁路货运场','vehicle-rail-freight','industry-logistics-ramp')]),
('wildland','自然野外',[
('forest','阔叶林空地','nature-tree-oak','nature-tree-maple'),('pine','针叶林地','nature-tree-pine','nature-tree-spruce'),('marsh','湿地栈道','terrain-bridge-boardwalk','nature-tree-mangrove'),('alpine','高山避难点','architecture-building-mountain_hut','terrain-landform-ridge'),('desert','沙漠绿洲','terrain-transition-desert_oasis_watercourse','nature-tree-palm'),('canyon','峡谷渡口','terrain-landform-canyon','terrain-bridge-rope'),('island','海岛营地','terrain-island-crescent','nature-tree-coconut'),('cave','岩洞探查点','terrain-cave-grotto','props-lamp-tripod')]),
('science','研究前哨',[
('coastal_lab','海岸实验室','architecture-building-research_lab','robot-underwater-auv'),('botany','植物研究区','architecture-building-conservatory','props-device-microscope'),('observatory','山地观测站','architecture-building-observatory','props-device-analyzer'),('field_station','野外调查点','architecture-building-lodge','robot-mobile-agri'),('energy','新能源试验站','industry-power-solar','industry-power-battery'),('robotics','机器人试验区','robot-arm-adaptive','robot-mobile-inspection'),('weather','气象监测站','props-device-sensor','architecture-tower-radio'),('water','水生态试验区','industry-process-water','terrain-river-fork')]),
('scifi','科幻基地',[
('habitat','前哨居住区','architecture-building-habitat','industry-power-battery'),('hangar','穿梭机机坪','vehicle-air-shuttle','robot-mobile-warehouse'),('assembly','自动制造区','industry-machine-printer','robot-arm-soft'),('drone','无人机站','robot-drone-octo','industry-power-charger'),('control','指挥控制区','architecture-building-control_center','props-device-console'),('sensor','雷达观测区','architecture-tower-radio','robot-drone-hex'),('airlock','基地气闸','gameplay-interactive-vault','architecture-building-habitat'),('loading','物资收发区','robot-gantry-cartesian','vehicle-air-tiltrotor')]),
('dungeon','遗迹机关',[
('gate','古堡入口','architecture-ruin-gate','gameplay-interactive-door'),('hall','廊柱大厅','architecture-ruin-colonnade','gameplay-interactive-pressure_gate'),('vault','封印宝库','gameplay-interactive-vault','gameplay-interactive-treasure'),('bridge','机关断桥','architecture-ruin-bridge','gameplay-interactive-bridge'),('spikes','尖刺通道','terrain-cave-tunnel','gameplay-interactive-spike_corridor'),('pendulum','摆锤回廊','architecture-ruin-courtyard','gameplay-interactive-pendulum'),('lift','升降石室','terrain-cave-chamber','gameplay-interactive-lift'),('crystal','晶体祭坛','architecture-ruin-temple','gameplay-interactive-crystal_switch')]),
('community','社区生活',[
('park','社区公园','architecture-shelter-gazebo','interior-table-picnic'),('playground','活动广场','architecture-shelter-bandstand','props-street-fountain'),('school','学校前庭','architecture-building-school','props-street-bike_rack'),('music','露天演奏区','architecture-shelter-bandstand','props-instrument-cello'),('market','周末市场','architecture-shelter-market_stall','props-container-display'),('camp','林间营地','architecture-building-a_frame','props-toolkit-woodcutter'),('workshop','社区工坊','architecture-building-workshop','props-toolkit-craft'),('festival','节庆舞台','architecture-shelter-picnic_shelter','props-lamp-chandelier')])]

def ref(s):
    ident='l3-'+s
    if ident not in ASSEMBLIES:raise ValueError('Scene missing asset '+ident)
    return ident

def create(theme,key,name,primary,secondary,variant=0):
    ident='l4-'+theme+'-'+key;indoor=theme=='interior';scale=1
    w,d=(7,6) if indoor else ((20,16) if theme in ('factory','scifi','dungeon') else (28,22))
    items=[fit('ground','core.terrain.paving' if indoor or theme in ('urban','factory','transit','scifi','dungeon','harbor') else 'exp.terrain.flat',[w,.2,d],[0,-.2,0])]
    layers={'ground':{'label':'地形与通路','visible':True},'structures':{'label':'主体构筑物','visible':True},'furnishings':{'label':'家具与设备','visible':True},'nature':{'label':'自然装饰','visible':True},'props':{'label':'道具','visible':True},'actors':{'label':'角色与生物','visible':True}}
    objects={'ground':{'label':'独立地面','layer':'ground','region':'site','locked':True}}
    def add(node,asset,x,z,y=0,rot=0,layer='furnishings',region='west',label=None,scale=1):
        ar=ref(asset);it=inst(node,assembly=ar,pos=[x,y,z],rot=[0,rot,0],scale=[scale]*3)
        if 'detail' in ASSEMBLIES[ar].get('metadata',{}).get('parameter_schema',{}).get('properties',{}):it['params']={'detail':False}
        items.append(it);objects[node]={'label':label or ASSEMBLIES[ar]['name'],'layer':layer,'region':region,'locked':False}
    def solid(node,size,pos,color,layer='ground',material='mat.paint'):
        items.append(block(node,size,pos,color=color,material=material));objects[node]={'label':node,'layer':layer,'region':'site','locked':False}
    if indoor:
        for i,(size,pos) in enumerate([([w,2.8,.12],[0,0,-d/2]),([.12,2.8,d],[-w/2,0,0])]):solid('cutaway_wall'+str(i),size,pos,'#D6CDBB','structures')
        add('primary',primary,-1.5,-1,rot=0);add('secondary',secondary,2,-1.7,rot=0,region='east')
        add('light','props-lamp-floor',-2.7,-2.2,layer='props');add('plant','nature-shrub-aloe',2.7,1.8,layer='nature',region='east',scale=.65)
        setups={
            'living':[('interior-table-coffee',-.8,.5,0,0),('interior-seat-armchair',1.4,.8,0,-35),('interior-storage-bookcase',-2.8,1.4,0,90),('props-device-radio',2,-1.7,.95,0)],
            'bedroom':[('interior-table-side',-2.7,-1,0,0),('interior-storage-dresser',2,1.3,0,-90),('interior-service-mirror',-.3,2,0,0)],
            'kitchen':[('interior-kitchen-sink',-.5,-2.5,0,0),('interior-kitchen-stove',1,-2.5,0,0),('interior-seat-stool',-1.2,.4,0,0),('interior-storage-pantry',-2.7,1.3,0,90)],
            'bathroom':[('interior-sanitary-toilet',.2,-2,0,0),('interior-sanitary-shower',-2,1.2,0,0),('interior-sanitary-towel',2,1.2,0,0)],
            'office':[('interior-seat-office',-.8,-.1,0,0),('interior-seat-office',-1.9,-2,0,180),('interior-storage-filing',2,1,0,0),('props-device-radio',-1.5,-1,.72,0)],
            'library':[('interior-storage-bookcase',-2.8,1.2,0,90),('interior-seat-dining',1.8,-.7,0,0),('interior-table-side',.3,1.2,0,0),('interior-seat-armchair',1.6,1.5,0,-45)],
            'nursery':[('interior-storage-bookcase',2,1.2,0,0),('interior-seat-rocker',-.7,1.1,0,25),('interior-table-side',-2.2,1.1,0,0)],
            'reception':[('interior-seat-armchair',1.8,.2,0,-90),('interior-table-coffee',.8,.2,0,0),('interior-storage-display',-2.8,1.5,0,90),('props-device-terminal',-1.5,-1,1.4,0)]}
        for i,(asset,x,z,y,rot) in enumerate(setups[key]):add('room_item'+str(i),asset,x,z,y,rot,region='east' if x>0 else 'west')
        # Threshold and modest rug ground the furniture without merging its nodes.
        solid('threshold',[1.4,.025,.3],[.6,.005,d/2-.15],'#A58E70');solid('rug',[2.3,.015,1.5],[0,.003,.8],'#9CACA7')
    else:
        px,pz=(-5,-3) if w<=20 else (-6,-4);sx,sz=(4,-3) if w<=20 else (6,-4)
        add('primary',primary,px,pz,layer='structures');add('secondary',secondary,sx,sz,rot=0,region='east',layer='structures')
        solid('access_lane',[w,.045,2.3],[0,.005,2.2],'#778589')
        # Set dressing is explicitly authored by use case; never random foliage.
        if theme=='harbor':
            solid('water_basin',[w*.48,.09,d-.2],[-w*.25,.01,0],'#599FA9',material='mat.water')
            solid('quay',[w*.49,.26,d],[w*.255,0,0],'#8F9691')
            for it in items:
                if it['id']=='primary' and primary.startswith('vehicle-marine'):it['position'][1]=-.25
                elif it['id']=='secondary':it['position'][1]=.26
            solid('finger_pier',[7,.25,1.8],[-1,.05,4],'#9C8A6B');
            for i,z in enumerate((-7,-2,4,8)):solid('mooring_post'+str(i),[.24,.75,.24],[1.0,.26,z],'#746C5C','props')
            add('harbor_cart','vehicle-utility-forklift',8,5,y=.26,layer='props',region='east')
        elif theme in ('urban','heritage'):
            neighbour='architecture-building-rowhouse' if theme=='urban' else 'architecture-building-tea_house'
            add('neighbour',neighbour,6,6,rot=180,layer='structures',region='east')
            add('frontage','architecture-shelter-bus_stop' if theme=='urban' else 'architecture-shelter-pergola',-7,6,rot=180,layer='structures')
            for i,x in enumerate((-3.0,0,3.0)):add('front_planter'+str(i),'props-street-planter',x,4,layer='props',region='site')
            if theme=='urban':add('parked_car','vehicle-road-hatch',9,0,rot=90,layer='props',region='east')
        elif theme=='factory':
            solid('back_wall',[w,3,.16],[0,0,-d/2],'#B1BDBA','structures')
            add('toolbench','props-toolkit-mechanic',-5,5,layer='furnishings');add('cabinet','interior-storage-tool',-8,4,layer='furnishings')
            add('distribution','industry-power-switchgear',5,5,layer='furnishings',region='east')
            add('stock','props-container-pallet',8,4,layer='props',region='east')
            for x in (-7,0,7):solid('safety_mark'+str(x).replace('-','n'),[.12,.018,6],[x,.01,-3],'#C5B469')
        elif theme=='farm':
            for i,(x,z) in enumerate([(2,5),(5,5),(8,5),(2,8),(5,8),(8,8)]):
                solid('soilbed'+str(i),[2.3,.1,2],[x,0,z],'#806A4E');add('cropbed'+str(i),'nature-crop-rice' if key=='rice' else 'nature-crop-wheat',x,z,y=.1,layer='nature',region='east')
            add('store','architecture-shelter-pump_shelter',-8,6,layer='structures');add('farm_barrel','props-container-barrel',-4,6,layer='props')
        elif theme=='transit':
            if key in ('rail_station','tram','freight'):
                railx=-5 if primary.startswith('vehicle-rail') else 6
                for x in (railx-.68,railx+.68):solid('rail_'+str(x).replace('.','_').replace('-','n'),[.09,.06,14],[x,0,-1],'#A4ACA9')
                for i,z in enumerate(range(-7,6)):solid('sleeper'+str(i),[1.8,.04,.2],[railx,-.025,z],'#776951')
            elif key in ('airport','helipad'):
                solid('apron',[11,.018,10],[-5,.004,-2],'#919996');solid('landing_mark',[.18,.02,3],[-5,.025,-2],'#E4DDC5')
            add('passenger_shelter','architecture-shelter-bus_stop',-7,6,layer='structures');add('ticket','props-street-ticket',-3,5,layer='props')
            add('luggage','props-container-trunk',3,5,layer='props',region='east')
        elif theme=='wildland':
            plant='nature-tree-palm' if key in ('desert','island') else 'nature-tree-pine' if key in ('pine','alpine') else 'nature-tree-oak'
            forest_positions=[(-10,-8),(0,-8),(10,-8),(-10,7),(7,7),(10,3),(-1,8)]
            # Frond crowns expand under Toon subdivision. Keep the tropical
            # silhouette but spend the 400k scene cap on a sparse grove, not
            # seven repeated high-cost palms. Rock/ground forms remain editable.
            if key in ('desert','island'):forest_positions=[(-10,-8),(-10,7),(7,7)]
            for i,(x,z) in enumerate(forest_positions):add('forest'+str(i),plant,x,z,layer='nature',region='landscape',rot=i*37)
            add('landmark','terrain-landform-talus',4,5,layer='ground',region='east')
            for i,(x,z) in enumerate([(-9,3),(0,5),(5,8)]):add('understory'+str(i),'nature-shrub-fern',x,z,layer='nature',region='landscape')
        elif theme in ('science','scifi'):
            add('solar','industry-power-solar',-6,5,layer='furnishings');add('storage','industry-power-battery',-2,6,layer='furnishings');add('console','props-device-console',5,5,layer='props',region='east')
            add('maintenance','robot-mobile-inspection',1,4,layer='props',region='site')
            for i,x in enumerate((-7,0,7)):solid('pad'+str(i),[3,.018,2],[x,.002,5],'#99A5A7')
        elif theme=='dungeon':
            solid('back_wall',[w,3,.45],[0,0,-d/2],'#7E847B','structures');solid('left_wall',[.45,2.5,d],[-w/2,0,0],'#7E847B','structures')
            for i,x in enumerate((-7,0,7)):
                items.append(fit('column'+str(i),l1('architecture','column','tuscan'),[.65,3.1,.65],[x,0,5]));objects['column'+str(i)]={'label':'独立廊柱','layer':'structures','region':'site','locked':False};add('torch'+str(i),'props-lamp-oil',x,4,layer='props',region='site')
            add('reward','props-narrative-reliquary',6,5,layer='props',region='east')
        else:
            for i,(x,z) in enumerate([(-6,6),(0,6),(6,6)]):add('social_table'+str(i),'interior-table-picnic',x,z,layer='furnishings',region='site')
            add('service_stall','architecture-shelter-market_stall',9,5,layer='structures',region='east')
        if theme not in ('dungeon','scifi','factory','wildland','harbor'):
            plant='nature-tree-maple' if theme=='heritage' else 'nature-tree-birch'
            for i,(x,z) in enumerate([(-w/2+1,-d/2+1),(w/2-1,-d/2+1),(-w/2+1,d/2-1)]):add('tree'+str(i),plant,x,z,layer='nature',region='landscape')
        for i,x in enumerate((3,w/2-2) if theme=='harbor' else (-w/2+2,w/2-2)):add('light'+str(i),'props-lamp-lanternpost' if theme in ('heritage','dungeon') else 'props-lamp-street',x,3.6,layer='props',region='site')
        add('wayfinding','props-street-wayfinding',-1,3.7,layer='props',region='site')
        occupation={'urban':'courier','heritage':'merchant','factory':'mechanic','farm':'farmer','harbor':'fisher','transit':'pilot','wildland':'ranger','science':'botanist','scifi':'technician','dungeon':'guard','community':'gardener'}[theme]
        add('actor','character-profession-'+occupation,1,3.7,layer='actors',region='site')

    if theme=='harbor':
        for it in items:
            if it['id'] in ('actor','wayfinding','light0','light1'):
                it['position'][0]=max(2,it['position'][0]);it['position'][1]+=.26
    md={'collection':'l4-3.4','theme':'l4-'+theme,'domain':'scene','quality':{'status':'l4','review_scope':'L3-L4','approval':'editable scene; see evidence'},
        'runtime':{'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','origin':'site-ground','triangle_budget':400000,'collision':{'type':'children'},'lod':{'levels':[]},'selection_bounds_are_colliders':False,'engine_adapter_required':True},
        'source':{'type':'original_editable_scene','authoring':'tools/l34_expansion/scenes.py','revision':'3.4.0','license':'project-authored'},
        'scene':{'schema':'wx.scene/1.0','title':name,'theme':theme,'units':'m','groundY':0,'layers':layers,'objects':objects,
            'regions':{'site':{'label':'全场地'},'west':{'label':'西侧主区'},'east':{'label':'东侧副区'},'landscape':{'label':'环境边界'}},
            'bounds_design':[[-w/2,-.2,-d/2],[w/2,15,d/2]],'spawn_points':[{'id':'visitor','position':[0,0,d/2-2],'forward':[0,0,-1]}],
            'cameras':[{'id':'overview','position':[w*.85,22,d*.95],'target':[0,1,0]}],
            'edit_contract':'instances own transforms; metadata owns layer and region membership; GLB is derived',
            'navigation':'unbaked; consumer must derive navigation and physics from chosen colliders',
            'lighting':{'environment':'studio','ambient_intent':.6,'realtime_lights_created':False},'max_objects':2500}}
    assembly(ident,name,'scene',items,level=4,metadata=md,description='可编辑主题场景；保存所有对象引用、图层与分区；不含烘焙导航或游戏逻辑。')
    ASSEMBLIES[ident].update(version='3.4.0',max_triangles=400000,tags=['L4',theme,key,'editable-scene'])
    SCENES.append(ident)

def author():
    for theme,label,rows in THEMES:
        for i,(key,name,a,b) in enumerate(rows):create(theme,key,label+' · '+name,a,b,i)
    create('community','production_hub','跨领域生产评审园区','architecture-building-research_lab','robot-gantry-cartesian')
    if len(SCENES)!=97:raise ValueError('Expected 97 new scenes, got '+str(len(SCENES)))
