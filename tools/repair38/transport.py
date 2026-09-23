from .common import *

def dock(s,name,x0,x1,z,width=1.5,y=.34):
 length=abs(x1-x0);x=(x0+x1)/2
 forms=[basebox([length,.14,width],[x,y-.14,z],WOOD)]
 for xx in [x0+(x1-x0)*i/max(1,math.ceil(length/2.4)) for i in range(math.ceil(length/2.4)+1)]:
  for zz in (z-width*.36,z+width*.36):forms.append(basebox([.15,y+.5,.15],[xx,-.5,zz],DARK))
 for j in range(max(1,int(length/.24))):forms.append(basebox([.017,.004,width],[min(x0,x1)+.12+j*.24,y,z],'#8A775D',bevel=0))
 s.geometry(name,forms,'mat.wood')

def harbor():
 for key in ['cargo','ferry','fishing','lighthouse','marina','rescue','research','tug']:
  s=Scene('l4-harbor-'+key);s.floor=.34;s.w=28;s.depth=22
  s.drop('finger_pier');s.drop_prefix('mooring_post');s.place('actor',1.7,2.7,y=.34);s.place('light0',2,7,y=.34);s.place('light1',9.4,7,y=.34)
  s.place('harbor_cart',5,4.8,y=.34,rot=180)
  s.path('quay_walk',[(1.1,10),(1.1,-9)],1.4,y=.343,color='#C1B9A2')
  s.slab('service_lane',3.2,20,11.6,0,.345,.03,color='#84928F')
  if key=='lighthouse':
   s.drop('harbor_cart');island=Point(-6,-2).buffer(2.9,resolution=18)
   s.geometry('secondary',solid_shape(island,-.6,.50,'#879C8D'))
   s.place('primary',-6,-2,y=.5,s=.8)
   dock(s,'access_jetty',1.25,-6,1.4,width=1.6,y=.50)
   s.geometry('islet_landing',[basebox([1.55,.14,2.1],[-6,.385,.35],WOOD)]+[basebox([.15,1,.15],[x,-.5,1.1],DARK) for x in (-6.6,-5.4)],'mat.wood')
   s.steps('quay_steps',.6,2.7,1.4,.16,1.0,2,y=.34)
   s.fence('islet_guard',[(-8.4,-3.5),(-8.5,-1),(-7.7,.4)],h=.85,y=.5)
  else:
   s.items['primary']['rotation']=[0,0,0];w=s.dims('primary')[0];bx=-1.1-w/2
   s.place('primary',bx,-3.5,y=-.26)
   dock(s,'finger_pier',0,-6.8,2.4,width=1.7)
   # An explicit berth-side gangway bridges the water gap to the vessel deck.
   s.geometry('boarding_gangway',[basebox([1.70,.08,.80],[-.70,.30,-2.8],WOOD)],'mat.wood')
   for i,z in enumerate((-5.8,-1.2,5.2)):
    s.geometry('bollard'+str(i),[basebox([.35,.08,.35],[.25,.34,z],DARK),basebox([.18,.40,.18],[.25,.42,z],DARK)],'mat.metal')
   if key=='cargo':
    s.place('primary',-3.2,-3.7,y=-.26);dock(s,'crane_wharf',.5,-2,-3.7,width=5.2)
    s.place('secondary',-.3,-3.8,y=.34,rot=90)
    for i,(x,z) in enumerate([(4,-4),(4,-1),(5.5,-7)]):s.ref('cargo_pallet'+str(i),'l3-props-container-pallet',x,z,y=.34)
    s.geometry('boarding_gangway',[basebox([1.25,.08,.75],[-2.10,.30,-3.0],WOOD)],'mat.wood')
   elif key=='marina':
    s.drop('secondary','pontoon_link');dock(s,'secondary',-5.4,.35,-6.5,width=1.5)
    # Two shore-connected fingers leave the west waterway open for departure.
   elif key=='research':
    s.place('secondary',-3,2.4,y=.34,s=.8)
    s.geometry('rov_hoist',[basebox([.15,2.0,.15],[-4.8,.34,2.4],METAL),beam([-4.8,2.34,2.4],[-3,2.34,2.4],.13,METAL)],'mat.metal')
   elif key=='tug':s.place('secondary',2.5,-6,y=.34)
   else:s.place('secondary',4.6,-4.2,y=.34)
   # The upstream hollow U-section leaves open ends. Add editable, parented
   # physical transom caps without changing shared L3 geometry or its IDs.
   primary=s.items['primary'];ship=ASSEMBLIES[primary['assembly']]
   hull_node=next(i for i in ship['instances'] if i['id']=='hull')
   hull=PARTS[hull_node['part']]['shape_params']['forms'][0]
   pts=hull['points'];caps=[]
   for offset,sign in ((0,-1),(len(pts)-10,1)):
    ring=pts[offset:offset+5];z=ring[0][2];z0,z1=(z-.006,z+.020) if sign<0 else (z-.020,z+.006)
    vertices=[[p[0],p[1],zz] for zz in (z0,z1) for p in ring]
    faces=[list(reversed(range(5))),list(range(5,10))]+[[i,(i+1)%5,(i+1)%5+5,i+5] for i in range(5)]
    caps.append(mesh(vertices,faces,hull.get('color','#7F9B9D')))
   # Closed raised foredeck and bow plating: the original thin deck can
   # clip the strongly tapered, triangulated bow side in close views.
   # Keep this a real solid reinforcement, parented to the editable vessel.
   rings=[pts[-20:-15],pts[-10:-5]];vertices=[]
   for j,ring in enumerate(rings):
    for x,y,z in ring:vertices.append([x+(.012 if x>0 else -.012 if x<0 else 0),y,z+(-.018 if j==0 else .018)])
   faces=[list(reversed(range(5))),list(range(5,10))]+[[i,(i+1)%5,(i+1)%5+5,i+5] for i in range(5)]
   caps.append(mesh(vertices,faces,hull.get('color','#7F9B9D')))
   cap=s.geometry('vessel_bulkheads',caps,'mat.metal',label='随船移动的水密封板与艏部加强壳');cap['parent']='primary'

  s.finish('船艇移入可实际登乘的泊位，重做岸线与栈桥接合、登船跳板、系泊点和桩基；灯塔以有连接栈桥的独立岬角承托，设备不再悬空或远离作业水域。')

def h_mark(s,x,z,y):
 fs=[basebox([.16,.012,2.8],[x-1,y,z],'#EAE6CD'),basebox([.16,.012,2.8],[x+1,y,z],'#EAE6CD'),basebox([2.1,.012,.16],[x,y,z],'#EAE6CD')]
 for a in range(32):
  a0=math.tau*a/32;a1=math.tau*(a+1)/32
  fs.append(beam([x+3.7*math.cos(a0),y+.005,z+3.7*math.sin(a0)],[x+3.7*math.cos(a1),y+.005,z+3.7*math.sin(a1)],.09,'#EAE6CD',depth=.018))
 s.marks('helipad_mark',fs)

def transit():
 for key in ['airport','bus','charging','freight','helipad','logistics','rail_station','tram']:
  s=Scene('l4-transit-'+key);s.standard(ground='#9AA79A');s.place('ticket',.7,5.7,y=.16);s.place('luggage',2.7,5.7,y=.16)
  s.place('passenger_shelter',-1.8,6.5,y=.16);s.place('actor',.6,6.6,y=.16)
  s.slab('public_apron',16,5,0,7.5,.06,.10,color=PAVING)
  if key in ('airport','helipad'):
   s.drop_prefix('tree');s.place('primary',-4,-2.8,y=.12);s.place('secondary',7,-3.5,y=.12)
   s.slab('flight_apron',15,13,-4,-2.8,.06,.06,color='#7E8D89')
   if key=='helipad':h_mark(s,-4,-2.8,.126)
   else:
    s.marks('apron_lines',[basebox([.14,.012,9],[-4,.126,-2.8],'#D8C789'),basebox([6,.012,.13],[-4,.126,-1.3],'#D8C789')])
    s.path('taxiway',[(-4,-9),(-4,-11)],3.5,y=.066,color='#7E8D89')
   s.fence('apron_boundary',[(-12,4),(-6,4)],y=.12,color=METAL);s.fence('apron_boundary_r',[(-2,4),(12,4)],y=.12,color=METAL)
   s.path('boarding_walk',[(-4,4),(-4,6.5),(0,6.5)],1.5,y=.123,color='#B4BFAF')
  elif key in ('rail_station','tram','freight'):
   train='secondary' if key=='rail_station' else 'primary';railx=-4.0
   # Match wheel contact to a continuous dedicated track bed, not generic asphalt.
   s.place(train,railx,-1.3,y=.19,rot=0)
   s.slab('track_ballast',3,22,railx,0,.06,.07,color='#8B8E80')
   s.geometry('track_rails',[basebox([.075,.065,22],[railx+x,.13,0],METAL) for x in (-.68,.68)]+[basebox([1.8,.055,.16],[railx,.095,z],WOOD) for z in range(-10,11)],'mat.metal',layer='ground')
   s.slab('boarding_platform',4.2,14,-.10,-1.3,.06,.42,color=PAVING)
   s.marks('platform_safety',[basebox([.14,.008,13.5],[-2.05,.489,-1.3],'#D3BB79')])
   s.place('passenger_shelter',-.2,3.7,y=.48);s.place('ticket',1,5,y=.48);s.place('luggage',.5,2,y=.48);s.place('actor',-1.1,.5,y=.48)
   s.steps('platform_steps',.0,6.6,2.3,.32,1.5,3,y=.16)
   if key=='rail_station':
    s.place('primary',6,-4,y=.06);s.path('station_entry',[(6,-1.7),(3.3,-1.7),(3.3,7),(1,7)],1.2,y=.065)
   elif key=='tram':s.place('secondary',-.3,-5,y=.48)
   else:
    s.place('secondary',.0,-4.6,y=.48,rot=-90);s.drop('passenger_shelter');s.ref('freight_stack','l3-props-container-pallet',.5,-1,y=.48)
   s.drop('public_apron');s.slab('public_apron',9,4,4,8.8,.06,.10,color=PAVING)
  elif key=='bus':
   s.slab('bus_lane',28,4.0,0,.0,.06,.045,color='#758587');s.place('primary',-3,0,y=.105,rot=90)
   s.slab('bus_platform',14,3.3,-3,-3.7,.06,.2,color=PAVING);s.place('secondary',-3,-3.9,y=.26,rot=0)
   s.path('station_walk',[(5,7.5),(5,-3.7),(2,-3.7)],1.7,y=.063)
   s.marks('bus_bay_line',[basebox([10,.01,.12],[-3,.113,-1.65],'#DEC88D')]);s.place('ticket',3.1,-3.6,y=.26)
  elif key=='charging':
   s.slab('charging_bay',3.7,6.8,-2,-2,.06,.05,color='#9AAD9C');s.place('secondary',-2,-2,y=.11)
   s.place('primary',.8,-3,y=.11,rot=-90)
   s.geometry('charging_cable',[tube([[.7,1,-3],[.2,.4,-3],[-.45,.14,-2.6],[-.7,.75,-2.6]],.027,DARK,8)],'mat.rubber')
   s.marks('parking_lines',[basebox([.10,.009,6.5],[x,.12,-2],'#E5E4CE') for x in (-3.75,-.25)])
   s.path('driveway',[(-2,1.4),(-2,4.5),(14,4.5)],3,y=.063,color='#758587')
  else:
   s.place('primary',-3,-4.0);s.place('secondary',-3,1.4,y=.12,rot=0)
   s.slab('freight_apron',15,11,-2,2,.06,.06,color='#8D9C92');s.slab('loading_dock',5,2.2,-3,-1.5,.06,.8,color=STONE,layer='structures')
   s.geometry('loading_portal',[basebox([.2,3.0,.4],[x,.86,-2.8],METAL) for x in (-5,-1)]+[basebox([4.2,.2,.4],[-3,3.86,-2.8],METAL)],'mat.metal')
   s.slab('loading_threshold',3,.5,-3,-2.3,.86,.10,color=DARK,layer='structures');s.ref('dock_pallet','l3-props-container-pallet',-4,-1.4,y=.86)
   s.path('truck_approach',[(-3,11),(-3,4.5)],3.3,y=.063,color='#718482')
  s.finish('重新建立真实停靠关系和连续通路：机场/直升机场补机位标记和隔离，轨道交通补站台与连续道床，公交贴站、充电柜贴车位、物流车对装卸区。')

def author():harbor();transit()
