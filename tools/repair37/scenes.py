"""Curated environmental layouts; source geometry is sampled for contact heights."""
from .common import *
from .landscape import heightfield,solid_shape,polar_land
from shapely.geometry import Point,LineString,Polygon
from l1_expansion.common import placed
GRASS='#8E9B72'; SAND='#C3B18A'; ROCK='#969C93'; WATER='#639FAB'

def source_ref(ident,name,ref,at,scale=1,rot=0):
    v=inst(name,assembly=ref,pos=at,rot=[0,rot,0],scale=[scale]*3)
    if 'detail' in ASSEMBLIES[ref].get('metadata',{}).get('parameter_schema',{}).get('properties',{}):v['params']={'detail':False}
    return v

def path_surface(points,fn,width=.65,color='#B4A580'):
    strip=LineString(points).buffer(width/2,quad_segs=5,join_style=1,cap_style=2);forms=solid_shape(strip,-.10,.05,color)
    for f in forms:
        for p in f['points']:
            y=fn(p[0],p[2]);p[1]=y+(.032 if p[1]>.0 else .016)
    return forms

def wildland(key):
    ident='l4-wildland-'+key;items=[];w=24.;d=19.;objects={};fn=lambda x,z:.12+.10*math.sin(x*.4)*math.cos(z*.5)
    def add(name,ref,x,z,y=None,s=1,rot=0,layer='nature'):
        items.append(source_ref(ident,name,ref,[x,fn(x,z) if y is None else y,z],s,rot));objects[name]={'label':ASSEMBLIES[ref]['name'],'layer':layer,'region':'site','locked':False}
    def geometry(name,forms,mat='mat.stone',layer='ground'):
        items.append(node(ident,name,forms,material=mat));objects[name]={'label':name,'layer':layer,'region':'site','locked':name=='ground'}
    if key=='island':
        geometry('sea',[basebox([w,.10,d],[0,-.20,0],WATER)],'mat.water')
        # An actual water-surrounded island, not an island tile placed on a grass board.
        ring=Point(0,0).buffer(1,resolution=48);outline=[]
        for xx,zz in list(ring.exterior.coords)[:-1]:outline.append([xx*7.8*(1+.04*math.sin(zz*8)),zz*6.4])
        coast=Polygon(outline);inner=coast.buffer(-1.1)
        geometry('shore',solid_shape(coast,-.15,.08,SAND));geometry('ground',solid_shape(inner,.07,.34,GRASS))
        fn=lambda x,z:.34
        for i,(x,z) in enumerate([(-4,-2),(-2,-3.7),(1,-3.8),(4,-2.8),(4,2.2)]):add('palm'+str(i),'l3-nature-tree-coconut',x,z,s=.83,rot=i*43)
        add('camp','l3-architecture-building-a_frame',-1.8,1.2,s=.60,layer='structures');add('boat','l3-vehicle-marine-canoe',4.8,4.3,y=-.17,s=.8,rot=-50,layer='props')
        add('supply','l3-props-container-chest',.1,2.7,s=.7,layer='props')
    elif key=='marsh':
        geometry('ground',[basebox([w,.20,d],[0,-.22,0],'#87917E')]);geometry('wetland',[basebox([w-.1,.07,d-.1],[0,-.06,0],WATER)],'mat.water')
        for i,(x,z) in enumerate([(-8,-4),(-3,-5),(5,-4),(8,5),(-7,5)]):geometry('hummock'+str(i),[ellipsoid([x,-.04,z],[4.4,.48,3.5],GRASS,16,5)])
        fn=lambda x,z:.20
        for i,(x,z) in enumerate([(-8,-4),(-3,-5),(5,-4),(8,5),(-7,5)]):add('mangrove'+str(i),'l3-nature-tree-mangrove',x,z,s=.85)
        for i in range(4):add('walkway'+str(i),'l3-terrain-bridge-boardwalk',-7.5+i*5,0,y=-.47,rot=90,layer='structures')
        for i,(x,z) in enumerate([(-4,2),(0,-2),(3,2.4)]):add('waterlily'+str(i),'l3-nature-crop-waterlily',x,z,y=.012,s=1.2)
    elif key=='canyon':
        fn=lambda x,z:.10+2.8*min(1,max(0,(abs(x+.12*math.sin(z))-.80)*1.55))
        geometry('ground',[heightfield(w,d,fn,ROCK,32)]);geometry('stream',solid_shape(LineString([(0,-9.5),(0,9.5)]).buffer(.42,cap_style=2),.11,.14,WATER),'mat.water')
        add('bridge','l3-terrain-bridge-rope',0,0,y=1.84,s=1.1,rot=90,layer='structures')
        for i,(x,z) in enumerate([(-7,-5),(-6,6),(6,-5),(8,4)]):add('scrub'+str(i),'l3-nature-shrub-juniper',x,z,s=.9)
        geometry('trail',path_surface([(-11,3),(-5,2),(-2.2,0)],fn,.85))
    elif key=='desert':
        fn=lambda x,z:.08+.65*(1-math.exp(-((x/7)**2+(z/6)**2)))+.24*math.sin(x*.4+z*.3)**2-.30*math.exp(-((x-1)**2/10+(z+1)**2/6))
        geometry('ground',[heightfield(w,d,fn,SAND,32)]);lake=Point(1,-1).buffer(1,resolution=30)
        # Scale the oval lake without adding a rectangular patch.
        lake=Polygon([(x*2.6-1.6,z*1.75+.75) for x,z in lake.exterior.coords]);geometry('oasis',solid_shape(lake,-.20,-.015,WATER),'mat.water')
        for i,(x,z) in enumerate([(-1,-3.7),(3,-3.7),(4.5,-1),(2.7,2.0)]):add('palm'+str(i),'l3-nature-tree-palm',x,z,s=.84,rot=i*54)
        for i,(x,z) in enumerate([(-7,4),(7,3),(-5,-5)]):add('succulent'+str(i),'l3-nature-shrub-agave',x,z,s=1.15)
    elif key=='alpine':
        fn=lambda x,z:.25+1.5*max(0,(-z-1)/8)+.8*max(0,(abs(x)-5)/7)
        geometry('ground',[heightfield(w,d,fn,'#959E91',30)]);geometry('terrace',[basebox([4.8,.35,4.4],[-4,fn(-4,1)-.08,1],ROCK)])
        add('shelter','l3-architecture-building-mountain_hut',-4,1,y=fn(-4,1)+.27,s=.66,layer='structures')
        for i,(x,z) in enumerate([(5,-4),(7,-6),(-7,-5),(-7,5),(6,5)]):add('conifer'+str(i),'l3-nature-tree-pine',x,z,s=.72,rot=i*30)
        geometry('trail',path_surface([(-3,8),(-1,4),(-3,1)],fn,.75))
    elif key=='cave':
        fn=lambda x,z:.12+.07*math.cos(x*.6)*math.cos(z*.8)
        geometry('ground',[heightfield(w,d,fn,'#939B82',24)])
        add('grotto','l3-terrain-cave-grotto',0,-2,s=2.1,layer='structures');add('inspection_lamp','l3-props-lamp-tripod',3,2.7,s=.9,layer='props')
        for i,(x,z) in enumerate([(-6,-5),(6,-5),(-7,3),(7,4)]):add('tree'+str(i),'l3-nature-tree-oak',x,z,s=.90)
        geometry('trail',path_surface([(1,8),(0,4),(0,0)],fn,.9))
    else:
        geometry('ground',[heightfield(w,d,fn,GRASS,28)])
        kinds=('pine','spruce') if key=='pine' else ('oak','maple','birch')
        positions=[(-8,-6),(-4,-6),(1,-6),(6,-6),(9,-3),(-9,-1),(-8,4),(-5,6),(4,6),(8,4)]
        for i,(x,z) in enumerate(positions):add('tree'+str(i),'l3-nature-tree-'+kinds[i%len(kinds)],x,z,s=.87+.05*(i%3),rot=i*37)
        for i,(x,z) in enumerate([(-6,-2),(5,-3),(-4,4),(6,3)]):add('fern'+str(i),'l3-nature-shrub-fern',x,z,s=1.1)
        add('mushrooms','l3-nature-fungus-porcini',-6,-1,s=1.3)
        geometry('trail',path_surface([(-1,9),(-2,4),(1,0),(2,-3),(3,-8)],fn,.95))
    # Keep all sources editable and actors safely grounded; no urban lamp row in wilderness.
    if key not in ('marsh','island'):add('actor','l3-character-profession-ranger',-1,5,s=1,layer='actors')
    replace(ident,items,'自然场景把主题地貌当作小摆件放在大草地上，水陆和场景主题不成立。','重建连续地表、水域和可解释的主题空间；对象按实际地表高度接地，移除无关城市灯具。')
    m=ASSEMBLIES[ident]['metadata']['scene'];m['objects']=objects;m['bounds_design']=[[-w/2,-.25,-d/2],[w/2,12,d/2]]
    m['spawn_points']=[{'id':'visitor','position':[0,fn(0,7),7],'forward':[0,0,-1]}];m['groundY']=0;m['revision']='3.7.1'

def harbor(ident):
    d=ASSEMBLIES[ident];key=ident.removeprefix('l4-harbor-');items=[]
    remove={'ground','access_lane','water_basin','quay','finger_pier','wayfinding'}
    for it in deepcopy(d['instances']):
        name=it['id']
        if name in remove:continue
        ref=it.get('assembly','');pos=it.setdefault('position',[0,0,0])
        if ref.startswith('l3-vehicle-marine-'):pos[0]=-5;pos[1]=-.26
        elif ref.startswith('l3-terrain-island-'):pos[:]=[-7,-.08,2];it['scale']=[1.25]*3
        else:
            if name in ('primary','secondary'):pos[0]=6 if name=='secondary' else 5;pos[2]=-4
            if name.startswith('mooring_post'):pos[0]=.7
            if name in ('actor','light0','light1','harbor_cart') or name in ('primary','secondary'):pos[1]=.34
        items.append(it)
    fs=[basebox([28,.2,22],[0,-.23,0],'#90998C')]
    items += [node(ident,'ground',fs,material='mat.stone'),node(ident,'sea',[basebox([14,.075,22],[-7,-.075,0],WATER)],material='mat.water'),node(ident,'quay',[basebox([14,.36,22],[7,-.02,0],'#A9AEA0')],material='mat.stone')]
    pier=[basebox([6.7,.20,1.45],[-2.6,.14,3.7],'#A58F6F')]
    for x in (-5.5,-3,-.5):
        for z in (3.12,4.28):pier.append(basebox([.16,.61,.16],[x,-.20,z],'#7D7460'))
    items.append(node(ident,'finger_pier',pier,material='mat.wood'))
    # The lighthouse actually occupies land on the water side, not a dry display of an island tile.
    if key=='lighthouse':
        for it in items:
            if it['id']=='primary':it['position']=[-7,.65,2];it['scale']=[.80]*3
    replace(ident,items,'泊位水域、岸上建筑和码头标高关系混乱，船体或灯塔落在不合理支承面。','明确水线、码头顶面和岸上建筑坐标，船艇吃水、栈桥桩与码头接合。')

def farm(ident):
    d=ASSEMBLIES[ident];key=ident.removeprefix('l4-farm-');items=deepcopy(d['instances'])
    if key=='rice':
        items=[it for it in items if not it['id'].startswith('soilbed')]
        for i,(x,z) in enumerate([(2,5),(5,5),(8,5),(2,8),(5,8),(8,8)]):
            fs=[basebox([2.6,.09,2.3],[x,0,z],'#827653')];items.append(node(ident,'paddybase'+str(i),fs,material='mat.stone'))
            items.append(node(ident,'paddywater'+str(i),[basebox([2.25,.025,1.95],[x,.095,z],WATER)],material='mat.water'))
    elif key=='mill':
        # Wheel on negative-X side of the mill; water runs beneath it rather than near an unrelated tile.
        items=[it for it in items if it['id']!='secondary'];fs=solid_shape(LineString([(-9.1,-10),(-9.1,2),(-8,8)]).buffer(.58,quad_segs=6),-.08,.04,WATER)
        items.append(node(ident,'millrace',fs,material='mat.water'))
        for it in items:
            if it['id']=='primary':it['position']=[-6,0,-4]
    elif key=='orchard':
        for i,(x,z) in enumerate([(-9,-6),(-4,-6),(0,-6),(-9,-1),(-4,-1),(0,-1)]):items.append(source_ref(ident,'orchard_tree'+str(i),'l3-nature-tree-apple',[x,0,z],.75))
    if key in ('rice','mill','orchard'):
        replace(ident,items,'农作空间与功能设施关系不足：水田无明确蓄水、磨坊水轮未对准水道。','设置有田埂与水面的稻田、磨坊轮下引水道以及有采收通道的果园。')

def refresh_scene_membership(d):
    m=d.get('metadata',{}).get('scene')
    if not isinstance(m,dict):return
    old=m.get('objects',{});objects={}
    for it in d['instances']:
        ident=it['id'];entry=deepcopy(old.get(ident,{'label':ident,'layer':'ground' if ident in ('ground','sea','quay','finger_pier') or ident.startswith(('paddy','millrace')) else 'nature' if ident.startswith('orchard') else 'props','region':'site','locked':ident=='ground'}));objects[ident]=entry
    m['objects']=objects

def rebind_controls():
    done=set()
    def visit(ident):
        if ident in done:return
        d=ASSEMBLIES[ident];md=d.setdefault('metadata',{});children={i['id']:i['assembly'] for i in d.get('instances',[]) if i.get('assembly')}
        for ref in children.values():visit(ref)
        if not ident.startswith('l4-'):
            done.add(ident);return
        # Preserve local controls, replace inherited controls with the current child contract.
        local=[]
        for c in md.get('state_controls',[]):
            if not any(c.get('node','').startswith(name+'.') for name in children):local.append(c)
        for name,ref in children.items():
            for c in ASSEMBLIES[ref].get('metadata',{}).get('state_controls',[]):
                cc=deepcopy(c);cc['id']=name+'__'+c['id'];cc['title']=name+' · '+c.get('title',c['id'])
                if c.get('node'):cc['node']=name+'.'+c['node']
                if c.get('nodes'):cc['nodes']=[name+'.'+n for n in c['nodes']]
                local.append(cc)
        if local or 'state_controls' in md:md['state_controls']=local
        done.add(ident)
    for ident in ASSEMBLIES:visit(ident)

def author():
    for ident in list(ASSEMBLIES):
        if ident.startswith('l4-wildland-'):wildland(ident.removeprefix('l4-wildland-'))
        elif ident.startswith('l4-harbor-'):harbor(ident)
        elif ident.startswith('l4-farm-'):farm(ident)
    for ident,d in ASSEMBLIES.items():
        if ident.startswith('l4-'):refresh_scene_membership(d)
    rebind_controls()
