from .common import *

def workpad(s,name,x,z,w,d):
 s.slab(name,w,d,x,z,.06,.045,color='#A1AAA3')
 fs=[]
 for xx in (x-w/2,x+w/2):fs.append(basebox([.075,.008,d],[xx,.108,z],'#C9B979'))
 for zz in (z-d/2,z+d/2):fs.append(basebox([w,.008,.075],[x,.108,zz],'#C9B979'))
 s.marks(name+'_outline',fs)

def factories():
 for key in ['machine_shop','packing','power','process','pump','sorter','warehouse','welding']:
  s=Scene('l4-factory-'+key);s.standard(20,16,ground='#ADB2AB');s.slab('back_wall',20,.18,z=-7.9,y=.06,h=3.2,color='#B7BEB5',layer='structures')
  s.place('toolbench',-6,4.8);s.place('cabinet',-8.6,-5.8);s.place('distribution',8.1,-5.8);s.place('stock',6.6,4.8)
  s.path('walkway',[(-9,2),(9,2)],1.4,y=.064,color='#8C9F9A');s.place('actor',-1,2)
  if key in ('packing','sorter','welding'):
   s.place('primary',.9,-2.6,y=.11);s.origin('secondary',-1.0,.11,-2.6,rot=0)
   workpad(s,'robot_cell',0,-2.6,7.5,5.9)
   s.fence('cell_guard',[(-3.75,.3),(-3.75,-5.55),(3.75,-5.55),(3.75,.3)],h=1.3,y=.11,color='#657A75')
   if key=='welding':
    s.slab('fixture_table',1.4,1.1,-.05,-2.6,.11,.92,color='#7F8D8A',layer='structures')
    s.geometry('workpiece',[basebox([.5,.25,.35],[-.05,1.03,-2.6],'#B5BCB5')],'mat.metal')
   else:s.ref('delivery_tote','l3-props-container-tote',2.8,-.6,y=.11)
  elif key in ('process','pump'):
   s.place('primary',-2.2,-2.4);s.place('secondary',2.5,-2.4);workpad(s,'utility_plinth',0,-2.4,9,6)
   b1,b2=s.bounds('primary'),s.bounds('secondary');p1=[b1[1][0]-.07,.70,-2.4];p2=[b2[0][0]+.07,.70,-2.4]
   s.geometry('process_pipe',[tube([p1,[p1[0]+.35,.7,-2.4],[p1[0]+.35,.7,-.65],[p2[0]-.35,.7,-.65],[p2[0]-.35,.7,-2.4],p2],.11,'#6B9293',10)],'mat.metal')
   s.geometry('pipe_supports',[basebox([.10,.6,.12],[x,.1,-.65],DARK) for x in (-1,0,1)],'mat.metal')
  elif key=='power':
   s.place('primary',-2,-2.7,y=.15);s.place('secondary',3,-2.7,y=.15);workpad(s,'electrical_pad',0,-2.7,10,6)
   s.fence('perimeter_guard',[(-5,0),(-5,-5.7),(5,-5.7),(5,0)],h=1.35,y=.11,color=DARK)
   s.slab('cable_trench',6,.30,.5,-4.9,.11,.08,color=DARK);s.place('distribution',6.8,-2.7)
  elif key=='warehouse':
   s.place('primary',-2.6,-2.65);s.place('secondary',1.5,1.0,rot=180);b=s.bounds('primary')
   s.slab('loading_apron',9,5,-2.5,3.0,.062,.05,color='#929E96');s.place('stock',-3.8,.4,y=.12)
   s.geometry('dock_ramp',[slab_polygon([[-5,.6],[-1,.6],[-1,2.4],[-5,2.4]],.07,.10,STONE)])
   s.path('forklift_lane',[(2,7),(2,2)],2.5,y=.064,color='#C0B898')
  else:
   s.place('primary',-2.7,-2.7);s.place('secondary',2.7,-2.7);workpad(s,'machine_bay',0,-2.7,10,5.6)
   s.slab('tool_carrier',1.0,.6,0,-2.7,.11,.8,color=WOOD,layer='structures')
  s.finish('紧凑布置工位与物料流，按设备工作范围靠拢机器人/工件；分别补齐管线、服务净空、围护、装卸区和可编辑地面标线。')

def scifi():
 for key in ['airlock','assembly','control','drone','habitat','hangar','loading','sensor']:
  s=Scene('l4-scifi-'+key);s.standard(20,16,ground='#7B8988');s.drop_prefix('equipment_pad','power_pad');
  s.place('solar',-7,4);s.place('storage',-3,5.7);s.place('console',6,4);s.place('maintenance',3,4)
  s.path('equipment_access',[(0,6),(0,.2)],1.2,y=.065,color='#ADC1B7')
  s.path('service_walk',[(-8,6),(7,6)],1.35,y=.062,color='#ADC1B7')
  if key=='airlock':
   s.place('secondary',0,-4.2);s.place('primary',0,-.4)
   s.geometry('airlock_tunnel',[basebox([.15,2.6,1.7],[-1.3,.06,-2.0],METAL),basebox([.15,2.6,1.7],[1.3,.06,-2.0],METAL),basebox([2.75,.15,1.7],[0,2.66,-2.0],METAL),basebox([2.6,.10,1.7],[0,.06,-2.0],METAL)],'mat.metal')
   s.path('airlock_approach',[(0,6),(0,.5)],2.6,y=.065,color='#B0BCB1')
  elif key=='assembly':
   s.place('primary',1.0,-2.5,y=.11);s.origin('secondary',-1.0,.11,-2.5);workpad(s,'assembly_cell',0,-2.5,8,5.5)
   s.fence('robot_backguard',[(-4,.25),(-4,-5.25),(4,-5.25)],y=.11,color=METAL)
  elif key=='control':
   s.place('primary',-2.5,-3.7);s.place('secondary',-2.3,0);workpad(s,'operator_deck',-2,0,6,3.2)
   s.ref('operator_seat','l3-interior-seat-office',-2.3,1.1,y=.11,rot=180)
   s.path('control_access',[(0,6),(0,2),(-2.3,2)],1.4,y=.065)
  elif key=='drone':
   workpad(s,'drone_pad',-2.2,-2.5,6,6);s.place('primary',-2.2,-2.5,y=.112);s.place('secondary',1.7,-2.5,y=.11,rot=-90)
   s.geometry('charging_lead',[tube([[1.5,.32,-2.4],[.8,.11,-2.4],[.2,.12,-2.4]],.026,DARK,6)],'mat.rubber')
   s.marks('drone_target',[basebox([2.2,.01,.09],[-2.2,.12,-2.5],'#CDD9C6'),basebox([.09,.01,2.2],[-2.2,.12,-2.5],'#CDD9C6')])
  elif key=='habitat':
   s.place('primary',-2,-3.7);s.place('secondary',3,-4);workpad(s,'habitat_terrace',-2,.5,7,3)
   s.path('habitat_access',[(0,6),(0,2),(-2,2),(-2,-2)],1.5,y=.064)
   s.slab('service_cable',.24,5,3,-.6,.065,.08,color=DARK)
  elif key in ('hangar','loading'):
   craft='primary' if key=='hangar' else 'secondary';other='secondary' if key=='hangar' else 'primary'
   s.place(craft,-2,-2.4,y=.11,rot=0);w,_,d=s.dims(craft);pw,pd=max(w+2.5,7),max(d+2.5,8);workpad(s,'landing_pad',-2,-2.4,pw,pd)
   s.place(other,5,-1,rot=-90)
   s.path('cargo_transfer',[(6,6),(6,1),(3,1)],2,y=.064,color='#BAC5AE')
   s.slab('freight_deck',2.3,3,4.8,2,.06,.24,color=METAL,layer='structures')
   s.steps('cargo_steps',4.8,4.1,1.8,.24,1.2,2,y=.06)
   if key=='hangar':
    s.geometry('hangar_frame',[basebox([.20,4.6,.20],[x,.11,z],METAL) for x in (-6.8,2.8) for z in (-6.6,-2.4,1.8)]+[basebox([9.8,.22,.22],[-2,4.65,z],METAL) for z in (-6.6,-2.4,1.8)],'mat.metal')
    s.geometry('hangar_cutaway_roof',[basebox([9.9,.15,4.3],[-2,4.86,-4.45],'#9EB1B1')],'mat.metal',label='机库后半屋顶（前半剖切展示）')
   s.marks('landing_axis',[basebox([2,.014,.13],[-2,.12,-2.4],'#D7DEC6'),basebox([.13,.014,3],[-2,.12,-2.4],'#D7DEC6')])
  else:
   # A radar must carry a coherent antenna, not a bare electricity tower.
   s.place('primary',-3,-2.5,s=.7);top=s.bounds('primary')[1][1]
   profile=[(0,0),(.2,-.02),(.6,.08),(1,.27),(1.4,.57),(1.4,.64),(1,.34),(.6,.15),(.2,.05)]
   s.geometry('radar_dish',[revolve(profile,'#CBD4CE',24,closed=True)],'mat.metal',at=[-3,top,-2.5],rot=[28,15,0])
   s.geometry('radar_feed',[beam([-3,top,-2.5],[-3,top+1.6,-2.5],.07,METAL),ellipsoid([-3,top+1.5,-2.5],[.25,.25,.25],DARK)],'mat.metal')
   workpad(s,'sensor_landing',3,-2.2,4.2,4.2);s.place('secondary',3,-2.2,y=.112)
  s.finish('重建本场景的功能联系：气闸连接舱体、机器人靠近工件、载具/无人机置于有界平台，或为观测塔补真实天线；保留各设备可独立编辑。')

def science():
 for key in ['botany','coastal_lab','energy','field_station','observatory','robotics','water','weather']:
  s=Scene('l4-science-'+key);s.standard();s.drop_prefix('pad');s.place('primary',-4,-3.6);s.place('secondary',3,-3.5)
  s.place('solar',-8,6);s.place('storage',-3,6);s.place('console',5,6);s.place('maintenance',2,6)
  s.path('research_walk',[(0,11),(0,1),(-4,1),(-4,-1.6)],1.6,y=.065)
  if key=='botany':
   s.slab('sample_table',1.35,.9,1,-1.2,.06,.86,color=WOOD,layer='structures');s.place('secondary',1,-1.2,y=.92)
   for i,z in enumerate((-4,-1)):s.slab('sample_bed'+str(i),3.2,1.4,5.5,z,.06,.15,color='#7F775E');s.ref('samples'+str(i),'l3-nature-crop-tomato',5.5,z,y=.21,s=.85,layer='nature')
   s.path('sample_walk',[(0,1),(3,1),(3,-5)],1.3,y=.065)
  elif key=='coastal_lab':
   s.drop('ground');s.slab('ground',28,22,y=-.7,h=.3,color='#848D80')
   s.slab('sea',10,22,9,0,-.12,.09,color=WATER,material='mat.water');s.slab('land',18,22,-5,0,-.4,.46,color=GRASS)
   s.slab('launch_pier',7,2.2,5,-3.5,y=.02,h=.2,color=WOOD,layer='structures');s.place('secondary',7,-3.5,y=.23)
   s.geometry('pier_piles',[basebox([.15,.72,.15],[x,-.5,z],DARK) for x in (2,5,8) for z in (-4.4,-2.6)],'mat.wood')
   s.fence('shore_rail',[(3.8,10),(3.8,-2.2)],y=.06);s.fence('shore_rail2',[(3.8,-4.8),(3.8,-10)],y=.06)
   s.place('console',2,3);s.place('light1',2.9,8.5);s.place('tree1',1.8,-9,y=.06)
   s.path('pier_approach',[(-4,-1.4),(0,-1.4),(0,-3.5),(2,-3.5)],1.35,y=.065)
  elif key=='energy':
   s.place('primary',-2.5,-3.5);s.place('secondary',2.5,-3.5);workpad(s,'energy_plinth',0,-3.5,10,6)
   s.slab('cable_duct',5,.23,0,-3.5,.11,.10,color=DARK);s.fence('plant_guard',[(-5,-.5),(-5,-6.5),(5,-6.5),(5,-.5)],y=.11,color=METAL)
  elif key=='field_station':
   s.path('cabin_approach',[(-4,-1.4),(-4,1),(0,1)],1.8,y=.065);s.place('secondary',2,-.5)
   s.slab('field_equipment_pad',4,3,2,-.5,.06,.06,color=PAVING)
  elif key=='observatory':
   s.slab('observatory_terrace',9,9,-4,-3.4,.06,.70,color='#939E92');s.place('primary',-4,-3.4,y=.76)
   s.steps('terrace_stairs',-4,2.2,2.2,.70,2.2,5,y=.06);s.path('terrace_walk',[(-4,3.3),(-4,5),(0,5)],1.7,y=.065)
   s.slab('instrument_bench',1.4,.9,3,-3.5,.06,.88,color=WOOD);s.place('secondary',3,-3.5,y=.94)
   # Low faceted shoulder landforms support the raised station, without covering its entrance.
   s.geometry('hillside',[ellipsoid([-8,-.4,-6],[9,2,7],'#8A9589'),ellipsoid([-2,-.5,-8],[8,2.2,5],'#919B8C')])
  elif key=='robotics':
   s.origin('primary',-1.4,.13,-2.7);s.place('secondary',2,-2.7,y=.13);workpad(s,'robot_testbed',0,-2.7,8,5.6)
   s.fence('robot_test_guard',[(-4,.1),(-4,-5.5),(4,-5.5)],y=.11,color=METAL)
   s.slab('test_fixture',1.3,.9,.5,-2.7,.11,.82,color=STONE)
  elif key=='water':
   s.drop('secondary');s.place('primary',-5,-4)
   lines=[[(3,-11),(3,-3),(2,2),(3,11)],[(3,-3),(9,-8),(14,-8)]]
   geom=LineString(lines[0]).buffer(1).union(LineString(lines[1]).buffer(.65)).intersection(polygon_box(-14,-11,14,11))
   s.geometry('ground',solid_shape(polygon_box(-14,-11,14,11).difference(geom),-.45,.06,GRASS),layer='ground')
   s.place('maintenance',-1.2,6,y=.06);s.place('console',5.5,6,y=.06)
   s.geometry('stream_bed',solid_shape(geom,-.44,-.39,'#758D81'),layer='ground');s.geometry('stream',solid_shape(geom,-.30,-.09,WATER),'mat.water',layer='ground')
   s.geometry('sampling_pipe',[tube([[-3.9,.65,-4],[1.8,.65,-4],[2.3,-.07,-4]],.08,METAL,10)],'mat.metal')
   s.slab('footbridge',4.1,1.7,3,4.5,.12,.14,color=WOOD,layer='structures');s.path('sampling_walk',[(0,11),(0,4.5),(1,4.5)],1.4,y=.064)
   s.path('east_sampling_walk',[(5.1,4.5),(6,4.5),(6,6)],1.2,y=.064)
  else:
   s.place('secondary',-3,-3.8,s=.65);s.place('primary',2,-3,y=1.15)
   s.geometry('instrument_stand',[basebox([1.1,.14,1.1],[2,.06,-3],STONE),basebox([.14,.95,.14],[2,.2,-3],METAL)],'mat.metal')
   top=s.bounds('secondary')[1][1]
   s.geometry('weather_mast',[basebox([.08,1.1,.08],[-3,top,-3.8],METAL),beam([-3.7,top+.7,-3.8],[-2.3,top+.7,-3.8],.05,METAL),ellipsoid([-3.7,top+.72,-3.8],[.25,.12,.25],'#E3E4D9'),ellipsoid([-2.3,top+.72,-3.8],[.25,.12,.25],'#E3E4D9')],'mat.metal')
   s.fence('weather_enclosure',[(-6,0),(-6,-7),(5,-7),(5,0)],h=.9,y=.06,color='#9CA999')
  s.finish('按研究用途设置样品工作面、设备基座、服务动线与环境联系；分别补足海岸/水系、山地台阶、仪器安装支架或试验区围护。')

def author():
 factories();scifi();science()
