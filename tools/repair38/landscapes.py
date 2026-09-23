from .common import *
from repair37.scenes import path_surface

def farms():
 for key in ['barn','farmhouse','greenhouse','market','mill','orchard','rice','stable']:
  s=Scene('l4-farm-'+key);s.standard();s.place('primary',-5,-3.7)
  s.path('farm_access',[(-4,11),(-4,1),(-5,-1.2)],2.8,y=.065,color='#B4A281')
  s.path('field_headland',[(-4,2),(10,2),(10,10)],1.2,y=.065,color='#B4A281')
  s.path('store_access',[(-9,4),(-9,2.5),(-4,2.5)],1.25,y=.066,color='#B4A281')
  s.place('actor',-2.9,6.5,y=.1)
  s.place('store',-9,5.8);s.place('farm_barrel',-7,4.7)
  for i,(x,z) in enumerate([(2,5),(5,5),(8,5),(2,8),(5,8),(8,8)]):
   if s.get('cropbed'+str(i)):s.place('cropbed'+str(i),x,z,y=.16)
   if s.get('soilbed'+str(i)):s.slab('soilbed'+str(i),2.3,2,x,z,.06,.10,color='#81715B')
  if key=='barn':
   s.slab('barn_apron',7,4,-5,.3,.06,.055,color='#B5AD95');s.place('secondary',-6.8,-.7,y=.115)
   s.ref('grain_trolley','l3-props-container-pallet',-3.5,.5,y=.115)
  elif key=='farmhouse':
   s.place('secondary',-4.3,5.4,y=.11,rot=0);s.slab('tractor_bay',3.2,5.2,-4.3,5.4,.065,.04,color='#A89B7E')
   s.path('house_walk',[(-7,11),(-7,1),(-5,1),(-5,-1.2)],1.25,y=.066,color=PAVING)
  elif key=='greenhouse':
   s.place('secondary',-6.2,-2.5,y=.25,s=.72)
   for i,(x,z) in enumerate([(-6.2,-4.7),(-3.8,-4.7),(-3.8,-2.5)]):s.ref('greenhouse_crop'+str(i),'l3-nature-crop-tomato',x,z,y=.25,s=.72,layer='nature')
   s.path('greenhouse_walk',[(-5,1),(-5,3),(-4,3)],1.5,y=.065)
  elif key=='market':
   s.place('secondary',-5,-3.2,y=.94,s=.62);s.ref('produce_stall','l3-architecture-shelter-market_stall',1,-3.5,y=.11)
   s.slab('market_pad',13,7,-2,-2.3,.06,.05,color=PAVING);s.place('farm_barrel',-8.0,-3.1,y=.11)
  elif key=='mill':
   s.origin('primary',-6,.06,-4)
   stream=LineString([(-9.1,-11),(-9.1,2),(-9.8,11)]).buffer(.64,quad_segs=5,cap_style=2)
   land=polygon_box(-14,-11,14,11).difference(stream)
   s.geometry('ground',solid_shape(land,-.22,.06,GRASS),layer='ground')
   s.geometry('millrace',solid_shape(stream,-.13,.035,WATER),'mat.water',layer='ground')
   s.place('store',-5.3,6);s.place('farm_barrel',-7.1,6)
   s.slab('mill_footbridge',2.3,1.35,-9.1,2.8,.085,.12,color=WOOD,layer='structures')
   s.path('mill_service',[(-14,2.8),(-10.3,2.8)],1.1,y=.065);s.path('mill_service2',[(-8,2.8),(-4,2.8)],1.1,y=.065)
  elif key=='orchard':
   s.drop_prefix('orchard_tree');s.place('primary',-7.5,-5.8,s=.80)
   for i,(x,z) in enumerate([(-2,-5.8),(3.5,-5.8),(-7.5,-.6),(-2,-.6),(3.5,-.6)]):s.ref('orchard_tree'+str(i),'l3-nature-tree-apple',x,z,y=.06,s=.8,layer='nature')
   s.place('secondary',-3.5,5.4,rot=0);s.path('orchard_lane',[(-12,2),(8,2)],2.0,y=.065)
  elif key=='rice':
   s.drop('secondary');s.place('primary',1.6,5,y=.17,s=.65)
   for i,(x,z) in enumerate([(2,5),(5,5),(8,5),(2,8),(5,8),(8,8)]):
    s.slab('paddybase'+str(i),2.65,2.6,x,z,.06,.12,color='#827B57')
    s.slab('paddywater'+str(i),2.3,2.24,x,z,.17,.025,color=WATER,material='mat.water')
    s.place('cropbed'+str(i),x,z,y=.19)
   s.path('paddy_connection',[(-4,2),(10,2)],1.1,y=.066,color='#A69875')
   s.geometry('irrigation',[basebox([.25,.05,7],[10.6,.10,6.5],WATER)],'mat.water',layer='ground')
  else:
   s.place('secondary',2.5,-3.4,y=.065);s.slab('paddock',10,8,3,-3,.06,.035,color='#AFA17F')
   s.fence('paddock_rails',[(-1.8,.8),(8,.8),(8,-6.8),(-1.8,-6.8),(-1.8,-1.3)],h=1.35,y=.10)
   s.geometry('water_trough',[basebox([1.5,.35,.65],[5,.095,-5.4],'#8B948B'),basebox([1.27,.025,.43],[5,.445,-5.4],WATER)],'mat.stone')
   s.path('stable_gate',[(-5,-1.3),(-1.8,-1.3),(1,-1.3)],1.5,y=.065)
  s.finish('补齐农庄作业入口、田间通道与装卸/采收区；水磨坊刻出连续水道并加桥，温室作物回到温室内，水田设田埂，马厩设置独立围场与饮水设施。')

def wildlands():
 for key in ['alpine','canyon','cave','island','marsh']:
  s=Scene('l4-wildland-'+key);s.w=24;s.depth=19
  if key=='alpine':
   fn=lambda x,z:.25+1.5*max(0,(-z-1)/8)+.8*max(0,(abs(x)-5)/7)
   s.geometry('trail',path_surface([(-2,9.5),(-2,5),(-4,4.5)],fn,.95),layer='ground')
   s.steps('hut_steps',-4,3.75,1.45,.27,1.05,3,y=.25)
   s.path('terrace_entry',[(-4,3.25),(-4,2.1)],1.4,y=.52)
   s.place('actor',-2,5,y=fn(-2,5))
  elif key=='canyon':
   fn=lambda x,z:.10+2.8*min(1,max(0,(abs(x+.12*math.sin(z))-.80)*1.55))
   # Broad level abutments meet the high banks; a light editable plank bridge spans the real channel.
   s.drop('bridge');forms=[]
   for i in range(19):forms.append(basebox([.23,.10,1.25],[-2.3+i*.255,2.835,0],WOOD))
   for z in (-.70,.70):
    forms += [tube([[-2.6,3.85,z],[0,3.35,z],[2.6,3.85,z]],.04,'#807862',8)]
    for x in (-2.6,2.6):forms.append(basebox([.14,1.0,.14],[x,2.9,z],WOOD))
   s.geometry('bridge',forms,'mat.wood')
   s.slab('abutment_w',1.2,1.6,-2.8,0,2.76,.175,color=STONE);s.slab('abutment_e',1.2,1.6,2.8,0,2.76,.175,color=STONE)
   s.geometry('trail',path_surface([(-11.9,3),(-6,2),(-2.9,0)],fn,.95),layer='ground')
   s.geometry('east_trail',path_surface([(2.9,0),(7,-2),(11.9,-3)],fn,.95),layer='ground');s.place('actor',-4.3,1.2,y=fn(-4.3,1.2))
  elif key=='cave':
   # Keep the opening, mask artificial exterior joins with coherent asymmetric rock masses.
   forms=[]
   for x,y,z,dx,dy,dz in [(-4.9,1.5,-3.6,5.5,4.6,7),(4.8,1.7,-3.5,5.4,5.0,7.5),(0,3.5,-5.0,10,4.2,6),(0,1.9,-7.2,8.4,5.4,3.8),(-3.8,1.2,.5,3,3.7,3.5),(4.0,1.0,.3,3.4,3.5,3.8)]:forms.append(ellipsoid([x,y,z],[dx,dy,dz],'#858E86',9,5))
   s.geometry('rock_envelope',forms)
   s.place('inspection_lamp',2.5,4.8,y=.1)
  elif key=='island':
   s.place('boat',5.5,4.5,y=.08,rot=-48,s=.8)
   s.slab('boat_support_front',.8,.12,5.4,4.25,.073,.04,color=WOOD)
   s.path('camp_path',[(-1.8,3),(-.5,4),(2.3,3.6)],.8,y=.342,color='#B3A589')
  else:
   # Match the bridge's deck top at .46 to dry access islands and short ramps.
   for side in (-1,1):
    poly=Point(side*10.6,0).buffer(1.55,resolution=18)
    s.geometry('landing'+str(side),solid_shape(poly,-.22,.42,'#91A082'))
    s.slab('landing_deck'+str(side),2.3,1.8,side*10.6,0,.40,.09,color=WOOD,layer='structures')
    s.path('shore_approach'+str(side),[(side*12,0),(side*10,0)],1.35,y=.44,color=WOOD)
  s.finish('针对真实地表修正步道/台阶、桥头高差和站立位置；洞口与岩体融合、独木舟从岸面埋藏状态抬起，湿地栈道增加干地登陆端。')

def author():farms();wildlands()
