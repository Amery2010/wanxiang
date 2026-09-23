from .common import *

def ladder(s,name,x,z,height,y=.02,width=.65,lean=.35):
 fs=[beam([x+dx,y,z+lean],[x+dx,y+height,z],.06,WOOD) for dx in (-width/2,width/2)]
 for i in range(1,max(2,int(height/.27))):
  h=i*.27;zz=z+lean*(1-h/height);fs.append(beam([x-width/2,y+h,zz],[x+width/2,y+h,zz],.055,WOOD))
 s.geometry(name,fs,'mat.wood')

def expansion():
 for key in ['airport','castle','cave','desert','dungeon','forest','industrial','medieval','mountain','swamp']:
  s=Scene('exp-scene-'+key)
  if key=='airport':
   s.drop('threshold','apron');s.slab('runway',7.2,34,12,0,y=.011,h=.035,color='#6D7875')
   s.slab('apron',21.5,34,-3.3,0,y=.01,h=.033,color='#A5ACA0')
   s.place('terminal',-12,-11,y=.046,rot=0);s.place('plane',-6.6,0,y=.046,rot=0);s.place('jet',1,-3.5,y=.046,rot=0)
   s.place('helicopter',-.5,11,y=.046,rot=0);s.place('service',-10.5,9.5,y=.046);s.place('pilot',-9,3.6,y=.046)
   s.marks('runway_center',[basebox([.12,.01,2.2],[12,.052,z],'#E5E6D6') for z in range(-14,16,5)]+[basebox([.23,.01,2],[x,.052,z],'#E5E6D6') for x in (9.5,10.3,11.1,12.9,13.7,14.5) for z in (-14,14)])
   s.path('taxiway',[(3,-5),(7,-5),(8.4,-5)],2.5,y=.046,color='#BDAD78');s.place('signal',7,-8,y=.05)
   s.fence('terminal_boundary',[(-17,-6),(-10,-6)],y=.05,color=METAL)
  elif key=='castle':
   b=s.bounds('gate');left,right=b[0][0],b[1][0]
   fs=[]
   for a,bx in [(-8.5,left+.05),(right-.05,8.5)]:
    fs.append(basebox([bx-a,3.0,.65],[(a+bx)/2,.02,-7.1],'#9DA18F'))
    for j in range(max(1,int((bx-a)/.7))):fs.append(basebox([.4,.38,.8],[a+.35+j*.7,3.02,-7.1],'#A6A997'))
   s.geometry('gate_wall_links',fs)
   # Close-up review: inherited L-stair upper flight was disconnected and
   # ended in mid-air. Rebuild only the two L4 tower instances and their access.
   for name,x,side in [('towerL',-7.5,-1),('towerR',7.5,1)]:
    s.drop(name)
    forms=[basebox([2.3,3.04,2.3],[0,.04,0],'#9D9C89'),basebox([2.48,.16,2.48],[0,2.92,0],'#B2B3A1')]
    for z in (-1.13,1.13):
     forms.append(basebox([2.48,.62,.20],[0,3.08,z],'#A4A590'))
     for xx in (-.94,0,.94):forms.append(basebox([.40,.32,.24],[xx,3.7,z],'#B8B6A0'))
    forms.append(basebox([.20,.76,2.1],[-side*1.13,3.08,0],'#A4A590'))
    for xx in (-1.03,1.03):
     for zz in (-1.03,1.03):forms.append(basebox([.13,2.25,.13],[xx,3.08,zz],'#706B56'))
    forms+=roof(2.9,2.9,5.12,.85,'#985A45')
    s.geometry(name,forms,at=[x,0,-6.9],label='可登临角楼')
    s.slab(name+'_stair_base',1.44,4.55,x+side*1.9,-4.83,-.14,.18,color='#9C9B87')
    s.steps(name+'_steps',x+side*1.9,-4.8,1.2,3.04,4.2,15,y=.04)
    s.slab(name+'_landing',1.55,1.25,x+side*1.75,-7.3,2.90,.18,color='#B2B3A1')
    s.geometry(name+'_landing_support',[basebox([.18,2.88,.18],[x+side*2.35,.02,z],'#767C6E') for z in (-7.78,-6.82)])
    s.fence(name+'_landing_guard',[(x+side*1.05,-7.91),(x+side*2.47,-7.91),(x+side*2.47,-6.72)],h=.92,y=3.08,color=WOOD)
    s.geometry(name+'_stair_rail',[beam([x+side*2.47,1.00,-2.72],[x+side*2.47,4.02,-6.87],.085,WOOD)]+[basebox([.085,.9,.085],[x+side*2.47,.04+3.04*t,-2.72-4.15*t],WOOD) for t in (0,.25,.5,.75,1)])
   s.slab('tower_stair_apron',24,4.8,0,-7.7,-.20,.24,color='#9C9B87')
   s.slab('gate_approach',4.2,4.5,0,-10.6,-.2,.24,color='#9C9B87');s.path('courtyard_path',[(0,-6.5),(0,8)],2.3,y=.04)
  elif key=='cave':
   s.drop('wallL','wallR');s.geometry('rock_shell',[ellipsoid([-5.8,1.8,-4],[5.5,5.4,5.2],'#798C87',9,5),ellipsoid([5.7,1.7,-4],[5.4,5.2,5.6],'#819188',9,5),ellipsoid([0,3.1,-6.5],[11,4.0,4.5],'#788880',10,5),ellipsoid([0,1.7,-7.1],[9,5.2,3.8],'#7D8C84',10,5)])
  elif key=='desert':
   s.place('watch',5.7,-5.3);ladder(s,'watch_ladder',5.7,-4.45,2.05)
   s.path('camp_path',[(-4.5,8),(-4.5,2),(-3,-1)],.9,y=.035,color='#C0AA83')
  elif key=='dungeon':
   s.geometry('entry_sidewalls',[basebox([.55,3.0,4.6],[x,.015,-5.8],'#909787') for x in (-3.45,3.45)])
   s.path('dungeon_route',[(0,8),(0,0),(0,-5)],1.85,y=.04,color='#A1A38B');s.place('gatekeeper',2.6,-1.3)
  elif key=='forest':
   s.drop_prefix('path');s.path('camp_trail',[(-2,8),(-1.4,4),(.4,2),(1,0),(2.4,-.4)],.85,y=.035,color='#B1A081')
   s.path('fire_branch',[(.4,2),(1.6,2.5)],.7,y=.035,color='#B1A081')
  elif key=='industrial':
   s.path('walkway',[(-10,2),(10,2)],1.25,y=.04,color='#C2BB94')
   s.slab('robot_bay',6,5,6,4.4,.032,.014,color='#98AAA1');s.slab('utility_bay',20,6,0,-6.5,.032,.014,color='#A3ACA2')
   s.fence('plant_safety',[(-3,-9),(-3,-4.3)],h=1.15,y=.03,color=METAL)
  elif key=='medieval':
   s.path('village_axis',[(0,8.8),(0,4),(2.2,1),(2.2,-2),(0,-4)],1.6,y=.045,color='#C2B59A')
   s.path('market_walk',[(-5,1),(5,1)],1.3,y=.045,color='#C2B59A')
   s.path('house_walk',[(-5.8,-2),(5.6,-2)],1.15,y=.045,color='#C2B59A')
  elif key=='mountain':
   # Remove only generated ground tiles under the cut and replace with actual cut land.
   s.drop_prefix('ground');s.drop('water','ravine_head')
   stream=LineString([(-1,-8),(-1,8)]).buffer(.72,cap_style=2)
   s.geometry('ground',solid_shape(polygon_box(-8,-8,8,8).difference(stream),-.3,.035,'#9E9E83'),layer='ground')
   s.geometry('water',solid_shape(stream,-.27,-.17,WATER),'mat.water',layer='ground')
   s.path('west_mine_route',[(-8,2.7),(-3.3,2.7)],1.2,y=.045);s.path('east_mine_route',[(1.3,2.7),(7.9,2.7)],1.2,y=.045)
   s.steps('west_bridge_steps',-3.6,3.3,1.2,.6,1.5,5,y=.035)
   s.drop('cliff','slope')
   s.geometry('mine_outcrop',[ellipsoid([5,1.1,-4.5],[5.8,4.4,5.5],'#858C81',8,5),ellipsoid([3.5,.8,-5.4],[3.6,3.2,4.0],'#93988A',8,5)])
  else:
   s.place('mangrove2',6,-4.0,y=0,s=.85);s.place('crate',4.7,.8,y=.88,s=.7)
   s.path('dry_approach',[(2.3,8),(2.3,6.0)],1.25,y=.035,color=WOOD)
   s.steps('boardwalk_steps',2.3,6.1,1.25,.82,2,7,y=.035)
  s.finish('保留原场景主体与编辑节点，针对人工发现的断接/碰撞修复入口、围护、桥下水道、施工/瞭望梯具或区域动线；未用随机装饰替代问题修复。')

def worlds():
 for key in ['camp','city','construction','cross-theme','cyber','depot','farm','harbor','home','outpost','space']:
  s=Scene('world-scene-'+key);s.w=16;s.depth=14;s.floor=.022
  if key=='camp':
   s.place('horse',4.2,-.9,y=.022,rot=-15,s=.85);s.place('deer',3.5,-3.5,y=.022,s=.8);s.place('dog',-.4,3.4,y=.022)
   s.path('bridge_approach',[(-4.8,1.1),(-.05,1.1)],.8,y=.034,color='#B4A077')
   s.path('east_approach',[(2.8,1.1),(4.95,1.1)],.8,y=.034,color='#B4A077')
  elif key=='city':
   s.origin('crossing',0,.11,3.1);s.place('taxi',-4.0,3.95,y=.1,rot=90);s.place('van',4.2,2.1,y=.1,rot=-90)
   s.place('scooter',-2.7,.8,y=.14,rot=90);s.place('light',-1.25,1.0,y=.14)
  elif key=='construction':
   s.steps('access_stairs_lower',-.65,-3.8,1.1,2.64,4.0,13,y=.03)
   s.geometry('stair_landing',[basebox([2.6,.13,1.15],[-1.35,2.54,-5.35],METAL)],'mat.metal')
   s.geometry('upper_ladder',[beam([-.25,2.68,-5.35],[-1.72,5.3,-5.35],.07,METAL),beam([.35,2.68,-5.35],[-1.12,5.3,-5.35],.07,METAL)]+[beam([-.25-1.47*t,2.68+2.62*t,-5.35],[.35-1.47*t,2.68+2.62*t,-5.35],.06,METAL) for t in (.1,.2,.3,.4,.5,.6,.7,.8,.9)],'mat.metal')
   s.fence('stair_guard',[(-1.25,-5.8),(-1.25,-1.8)],h=1.0,y=.03,color=METAL)
   s.path('pedestrian_access',[(1,7),(1,3),(2,3)],1.0,y=.037,color='#C5B698')
  elif key=='cross-theme':
   s.slab('display_floor',11,8,0,0,.015,.015,color='#929E99')
   for n,ref in [('rowboat','rowboat'),('rover','rover'),('robot','robot')]:
    b=s.bounds(n);x=(b[0][0]+b[1][0])/2;z=(b[0][2]+b[1][2])/2;w=b[1][0]-b[0][0]+.3;d=b[1][2]-b[0][2]+.3
    s.slab(n+'_display',w,d,x,z,.03,.06,color='#AFBBB4');s.place(n,x,z,y=.09)
   s.geometry('scale_marks',[basebox([.025,.01,.16],[x*.25,.044,3.6],'#E8E7D2') for x in range(-18,19)],'mat.paint',layer='ground')
  elif key=='cyber':
   s.slab('pedestrian_strip',11.85,.60,0,-.25,.104,.015,color='#637C7C')
   s.path('vehicle_lane',[(-5.85,3.5),(5.85,3.5)],2.85,y=.104,color='#4B666A')
   # Keep neon architecture and decorated tiles; add just the legible space division.
   s.marks('street_edge',[basebox([11.8,.008,.045],[0,.123,.08],'#83BCB8')])
  elif key=='depot':
   s.path('drive_lane',[(0,6),(0,1.2),(-3,1.2),(-3,-6)],2.1,y=.034,color='#8B9990')
   s.path('exit_lane',[(4,-6),(4,6)],2.0,y=.034,color='#8B9990')
   # Reposition only cars, leaving fixed pumps and canopies attached to their bays.
   if s.get('taxi'):s.place('taxi',-3,2.7,y=.04,rot=0)
  elif key=='farm':
   s.fence('animal_paddock',[(-6.8,-.8),(-.8,-.8),(-.8,5.6),(-6.8,5.6)],h=.9,y=.03)
   for n in list(s.items):
    it=s.items[n];ref=it.get('assembly','')
    if any(word in ref for word in ('pig','sheep','goat','cow','horse','donkey')):
     old=it.get('position',[0,0,0]);s.place(n,min(-1.6,max(-5.8,old[0])),min(4.8,max(.1,old[2])),y=.022)
   s.path('crop_access',[(0,6),(0,0),(4,0)],1.1,y=.033,color='#A99C77')
  elif key=='harbor':
   # Existing pier is kept; small boats are moved away from contact overlaps.
   for n,it in s.items.items():
    if 'rowboat' in it.get('assembly',''):
     old=it.get('position',[0,0,0]);s.place(n,1.65,4.75,y=-.08,rot=90,s=.72)
   s.geometry('boarding_planks',[basebox([1.25,.08,.48],[-2.5,.43,2.2],WOOD),basebox([1.05,.08,.48],[2.2,.43,2.9],WOOD)],'mat.wood')
  elif key=='home':
   s.geometry('bedroom_partition',[basebox([.12,1.45,2.35],[-1.25,.14,-1.8],'#C4B89C'),basebox([2.7,1.18,.12],[-2.65,.14,-.6],'#C4B89C')],'mat.plaster')
  elif key=='outpost':
   ladder(s,'tower_access',-4.95,-2.85,2.76,y=.022)
   s.path('access_road',[(-1.2,6.4),(-1.2,.8),(4.4,.8),(4.4,5.8)],2.05,y=.034,color='#BAA078')
   s.path('camp_walk',[(-3.7,-2.6),(-2,-2.6),(-2,.8)],.9,y=.035,color='#C0AC8D')
  else:
   # Rigid sealed corridor between docking-capable modules; roof is removable as a named source object.
   s.geometry('habitat_link',[basebox([4.0,.12,1.15],[.0,.38,-2.7],METAL),basebox([4.0,1.25,.12],[0,.5,-3.28],'#B5C1BC'),basebox([4.0,1.25,.12],[0,.5,-2.12],'#B5C1BC')],'mat.metal')
   s.geometry('habitat_link_roof',[basebox([4.15,.13,1.34],[0,1.75,-2.7],'#C8D0C5')],'mat.metal')
   s.place('solarA',-.8,-5.3,y=.03,rot=0);s.place('solarB',1.1,-5.3,y=.03,rot=0)
   s.path('moon_service_route',[(-3.5,1.9),(2,1.9),(5,1)],1.15,y=.041,color='#AEB6AC')
  s.finish('保留高密度世界场景的原始主体，按所见问题局部调整：让出桥头/斑马线、增加实际梯具/隔断/舱间连接，或补足农牧分区与服务动线。')

def author():expansion();worlds()
