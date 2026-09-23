from .common import *

def seat_group(s,x,z,prefix='cafe'):
 s.ref(prefix+'_table','l3-interior-table-side',x,z,y=.12)
 for i,(dx,dz,rot) in enumerate([(-.72,0,90),(.72,0,-90)]):s.ref(prefix+'_chair'+str(i),'l3-interior-seat-dining',x+dx,z+dz,y=.12,rot=rot)

def urban():
 for key in ['apartment','cafe','checkpoint','clinic','corner_shop','library','office','residential']:
  s=Scene('l4-urban-'+key);s.standard(ground='#909B89')
  s.place('primary',-4,-4.1);s.place('neighbour',6,-4.1,rot=0);s.place('frontage',7.5,4.25,rot=180)
  s.slab('street',28,4.7,0,8.65,.06,.04,color='#667779');s.slab('sidewalk',28,2.0,0,5.3,.06,.09,color=PAVING)
  s.path('entry_path',[(-4,4.4),(-4,-2.1)],2.0,y=.062);s.path('cross_court',[(-9,1.3),(9,1.3)],1.65,y=.062)
  s.place('tree2',-13,4.2,y=.06);s.place('light0',-12,5.5,y=.15);s.place('light1',12,5.5,y=.15)
  s.place('parked_car',8.0,8.1,y=.11,rot=90);s.place('actor',-3.1,4.6,y=.15)
  for i,x in enumerate((-8,-.7,3.8)):s.place('front_planter'+str(i),x,3.4,y=.1)
  s.marks('road_centerline',[basebox([2.0,.009,.09],[x,.109,8.65],'#E1D6AB') for x in (-12,-8,-4,0,4,8,12)])
  # Provide a deliberate crossing free of parked vehicles.
  s.marks('crossing',[basebox([1.65,.01,.32],[-4,.112,6.55+i*.6],'#E4E4D4') for i in range(7)])
  if key=='apartment':
   s.place('secondary',-1.15,.1,rot=-90,y=.10);s.slab('garden_court',4.5,3,1.4,-.6,.06,.07,color=PAVING)
   s.ref('second_bench','l3-interior-seat-bench',3.25,-.5,y=.13,rot=90)
  elif key=='cafe':
   s.slab('cafe_terrace',6.5,3.8,-4,.0,.06,.06,color='#B8AB8C');s.place('secondary',-5.7,.2,y=.12)
   for i,(x,z,rot) in enumerate([(-6.4,.2,90),(-5,.2,-90)]):s.ref('cafe_seat'+str(i),'l3-interior-seat-dining',x,z,y=.12,rot=rot)
   seat_group(s,-2.7,.2,'cafe2')
  elif key=='checkpoint':
   s.place('primary',-5.7,-1.7);s.place('secondary',0,2.0)
   s.slab('checkpoint_drive',3.2,15,0,-1.0,.063,.04,color='#728180')
   s.fence('controlled_boundary_left',[(-13,2),(-2.0,2)],h=1.6,y=.06,color=METAL)
   s.fence('controlled_boundary_right',[(2.0,2),(13,2)],h=1.6,y=.06,color=METAL)
   s.drop('cross_court');s.place('front_planter1',-7,3.4)
  elif key=='clinic':
   s.place('secondary',-4,2.3,y=.11,rot=0);s.slab('ambulance_bay',3.6,6,-4,2.3,.065,.04,color='#8CABA5')
   s.marks('ambulance_mark',[basebox([.15,.01,5.8],[-5.8,.116,2.3],'#E7EBDD'),basebox([.15,.01,5.8],[-2.2,.116,2.3],'#E7EBDD')])
   s.path('patient_walk',[(-7,5.2),(-7,-1.8),(-4,-1.8)],1.6,y=.067);s.place('front_planter0',-9,3.4)
  elif key=='residential':
   # Keep the coat rack but put it under an actual protected entry porch.
   s.place('secondary',-5.9,-1.05);s.geometry('entry_canopy',[basebox([4.8,.12,2.0],[-4,2.5,-.9],'#718C88'),basebox([.13,2.44,.13],[-6.25,.06,-.1],WOOD),basebox([.13,2.44,.13],[-1.75,.06,-.1],WOOD)],'mat.wood')
  else:
   s.place('secondary',-1.5,-.5,y=.10,rot=-25 if key=='library' else 0)
   if key=='library':s.ref('reading_bench','l3-interior-seat-bench',-7,.4,y=.1,rot=90)
  s.finish('将入口前庭、人行道、车道和辅助设施重新组织为相互连接的街区；针对急救车位、咖啡座、检查通道或有遮护住宅入口作专门修复。')

def heritage():
 for key in ['arcade','garden','gate','market','pagoda','shrine','teahouse','temple']:
  s=Scene('l4-heritage-'+key);s.standard();s.place('primary',-3,-3.8);s.place('neighbour',6,5.6,rot=180,s=.85);s.place('frontage',-7,5.8,rot=180)
  s.path('courtyard_axis',[(-3,11),(-3,-3)],2.1,y=.065,color='#BDBAA6');s.path('crosscourt',[(-10,2),(10,2)],1.6,y=.065,color='#BDBAA6')
  s.slab('forecourt',8,5.1,-3,-.2,.06,.055,color='#B9B59E')
  for i,x in enumerate((-9,1.7,4)):s.place('front_planter'+str(i),x,3.4,y=.10)
  s.place('secondary',0,-.5,y=.12)
  if key=='teahouse':
   pond=Point(6,-4).buffer(1,resolution=24);pond=Polygon([(6+(x-6)*4.5,-4+(z+4)*3.5) for x,z in pond.exterior.coords])
   s.geometry('pond_bank',solid_shape(pond.difference(pond.buffer(-.30)),.06,.15,'#929A83'),layer='ground');s.geometry('pond',solid_shape(pond.buffer(-.30),.10,.125,WATER),'mat.water',layer='ground')
   s.slab('waterside_deck',3.2,5,1.2,-3.6,.07,.18,color=WOOD,layer='structures');s.place('secondary',.8,-3.2,y=.25)
   s.fence('deck_rail',[(2.7,-6.1),(2.7,-1.1)],y=.25,color=WOOD)
   s.path('deck_access',[(-3,-1.1),(.8,-1.1)],1.5,y=.065)
  elif key=='gate':
   s.geometry('primary',[basebox([.55,2.6,.8],[x,.06,-3.6],STONE) for x in (-4.5,-1.5)]+[basebox([4.3,.28,1.2],[-3,2.66,-3.6],WOOD)]+[dict(f,position=[-3,0,-3.6]) for f in roof(4.8,1.7,2.93,.65,'#687D72')])
   s.place('secondary',4,-.4,y=.10)
   s.geometry('courtyard_walls',[basebox([5.2,1.75,.3],[-7.4,.06,-3.6],'#D0C8AC'),basebox([5.8,1.75,.3],[2,.06,-3.6],'#D0C8AC')])
  elif key=='pagoda':
   forms=[]
   for j,(w,base) in enumerate([(4.2,.06),(3.4,3.0),(2.65,5.65)]):
    forms.append(basebox([w,.2,w],[-3,base,-4],STONE))
    for dx in (-w/2+.22,w/2-.22):
     for dz in (-w/2+.22,w/2-.22):forms.append(basebox([.17,2.2,.17],[-3+dx,base+.2,-4+dz],WOOD))
    forms.append(basebox([w-.8,1.35,w-.8],[-3,base+.35,-4],'#D5C8A5'))
    a=w/2+.35;b=w*.18;y=base+2.3
    p=[[-3-a,y,-4-a],[-3+a,y,-4-a],[-3+a,y,-4+a],[-3-a,y,-4+a],[-3-b,y+.7,-4-b],[-3+b,y+.7,-4-b],[-3+b,y+.7,-4+b],[-3-b,y+.7,-4+b]]
    forms.append(mesh(p,[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7],[3,2,1,0]],'#667F70'))
   s.geometry('primary',forms,'mat.wood');s.steps('pagoda_steps',-3,-1.5,1.8,.2,.7,2,y=.06);s.place('secondary',.0,-3.8,y=.12)
  elif key=='market':
   s.place('secondary',-3,-3.35,y=.98,s=.65);s.ref('stall_east','l3-architecture-shelter-market_stall',3,-3.8,y=.12,rot=0)
   s.slab('market_square',14,5,0,-1,.064,.04,color='#BBB198')
  elif key=='garden':
   s.place('secondary',-3,-5.4,y=.06);s.geometry('garden_water',solid_shape(Point(4,-3).buffer(2.0,resolution=24),.063,.095,WATER),'mat.water',layer='ground')
   s.path('garden_path',[(-3,2),(1,2),(4,0),(7,-1)],1.2,y=.065)
  elif key=='arcade':
   s.place('secondary',-.2,.5,y=.12);s.path('arcade_walk',[(-8,-2),(-3,-2),(0,-2),(0,2)],1.7,y=.065)
  else:
   s.place('secondary',-3,-3.8,y=.65,s=.7);s.slab('ritual_pedestal',1.2,1.0,-3,-3.8,.06,.58,color=STONE,layer='structures')
  s.finish('修复传统场景的入口轴线、廊道和庭院联系，移走无关道路布局；分别补足临水平台、通透门庭、层叠楼阁、仪式台或集市陈列支承。')

def community():
 for key in ['camp','festival','market','music','park','playground','production_hub','school','workshop']:
  s=Scene('l4-community-'+key);s.standard();s.place('primary',-3,-3.2);s.place('secondary',1.6,-1.2)
  s.path('main_walk',[(0,11),(0,1),(-3,1),(-3,-2)],1.8,y=.065)
  s.path('social_walk',[(-9,5),(9,5)],1.5,y=.065)
  for i,x in enumerate((-7,0,7)):s.place('social_table'+str(i),x,7,y=.11)
  s.place('service_stall',8,-4.2);s.slab('service_court',7,6,7,-3.2,.06,.05,color=PAVING)
  s.path('service_access',[(0,1),(7,1),(7,-1.5)],1.4,y=.065)
  s.place('actor',.95,4.0,y=.11)
  s.slab('social_terrace',24,5.3,0,7.2,.06,.045,color='#B5AD94')
  if key in ('festival','music'):
   s.slab('stage_deck',6.5,5.5,-3,-3.0,.06,.42,color=WOOD,layer='structures');s.place('primary',-3,-3,y=.48)
   if key=='festival':
    s.place('secondary',-3,-3.8,y=2.65,s=.65)
    top=s.bounds('secondary')[1][1]
    s.geometry('light_suspension',[beam([-3,top,-3.8],[-3,3.7,-3.8],.025,METAL),beam([-3,3.7,-3.8],[-3,3.7,-4.3],.045,METAL)],'mat.metal')
    s.geometry('light_bar',[basebox([.12,3.3,.12],[x,.48,-4.3],METAL) for x in (-5.7,-.3)]+[basebox([5.6,.12,.12],[-3,3.7,-4.3],METAL)],'mat.metal')
   else:s.place('secondary',-3,-2.4,y=.64,s=.95)
   s.steps('stage_steps',-3,.3,2,.42,1.1,3,y=.06)
   for i,z in enumerate((2,3.4)):s.ref('audience_bench'+str(i),'l3-interior-seat-bench',-3,z,y=.11,rot=180)
  elif key=='playground':
   s.slab('play_surface',9,7,-3,-2.0,.06,.065,color='#B8A78A');s.place('secondary',3.2,-1.8,y=.12)
   # A separate A-frame swing with attached chains gives the activity plaza an actual play function.
   fs=[]
   for x in (-6.8,-3.8):
    fs += [beam([x,.125,-2],[x,2.7,-3.2],.14,WOOD),beam([x,.125,-4.4],[x,2.7,-3.2],.14,WOOD)]
   fs.append(beam([-6.9,2.7,-3.2],[-3.7,2.7,-3.2],.15,WOOD))
   for x in (-5.7,-4.9):fs.append(tube([[x,2.64,-3.2],[x,.62,-3.2]],.016,METAL,6))
   fs.append(basebox([1.1,.09,.42],[-5.3,.53,-3.2],WOOD));s.geometry('swing',fs,'mat.wood')
   s.place('primary',-3,1.1,s=.7,y=.125)
   s.geometry('secondary',[revolve([(.91,0),(1.12,0),(1.12,.36),(.91,.36)],STONE,24),revolve([(0,0),(.32,0),(.22,.95),(.4,1.02),(0,1.02)],STONE,18)],at=[3.2,.12,-1.8])
   s.geometry('fountain_water',[revolve([(0,0),(.91,0),(.91,.025),(0,.025)],WATER,24)],'mat.water',at=[3.2,.4,-1.8])
  elif key=='production_hub':
   s.place('secondary',3,-2.4,y=.14);s.slab('production_pad',8,7,3,-2.4,.06,.08,color='#A5AEAA')
   s.fence('production_guard',[(7,-5.9),(7,1.1),(.0,1.1)],y=.14,color=METAL)
   s.path('loading_walk',[(10,-8),(10,-2),(7,-2)],2.2,y=.065)
  elif key in ('workshop','school'):
   s.place('secondary',.3,-1.4,y=.14);s.slab('front_apron',9,4,-3,-.2,.06,.08,color=PAVING)
   if key=='workshop':s.slab('craft_bench',1.8,.9,.3,-1.4,.06,.85,color=WOOD);s.place('secondary',.3,-1.4,y=.91)
  elif key=='market':
   s.place('secondary',-3,-2.8,y=.15);s.ref('market_stall2','l3-architecture-shelter-market_stall',3,-3.1,y=.11)
   s.slab('market_square',14,7,0,-2.5,.06,.05,color=PAVING)
  elif key=='camp':
   s.place('secondary',-5,-.8,y=.11);s.geometry('fire_ring',[revolve([(.62,0),(.76,0),(.76,.2),(.62,.2)],'#85877A',16,at=[2.8,.06,-1.6])])
   s.ref('camp_bench','l3-interior-seat-bench',2.8,.1,y=.11,rot=180)
   s.path('camp_loop',[(-3,0),(-3,2),(3,2),(3,-.4)],1.2,y=.065)
  else:s.place('secondary',-3,-3.1,y=.24)
  s.finish('由散放模型重组为有连续步道的活动空间；演奏/节庆补舞台与观众区，游乐补可辨识器械，生产与公共活动分区，并校正道具工作面高度。')

def author():urban();heritage();community()
