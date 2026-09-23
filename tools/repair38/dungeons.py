from .common import *

def control(ident,node,title,mode,axis,minimum,maximum,unit):
 return {'id':ident,'node':node,'title':title,'mode':mode,'axis':axis,'min':minimum,'max':maximum,'default':0,'step':1 if mode=='rotation' else .01,'unit':unit}

def author():
 for key in ['bridge','crystal','gate','hall','lift','pendulum','spikes','vault']:
  s=Scene('l4-dungeon-'+key);s.standard(20,16,ground='#7C8077')
  s.drop_prefix('column','oil','light','sconce');s.drop('back_wall','left_wall','reward')
  s.geometry('boundary',[basebox([.6,2.7,16],[-9.7,.06,0],'#85877E'),basebox([.6,2.7,16],[9.7,.06,0],'#85877E'),basebox([20,2.7,.6],[0,.06,-7.7],'#85877E')])
  s.path('stone_route',[(0,8),(0,-5.7)],2.8,y=.063,color='#A4A494');s.place('actor',.65,6)
  for i,(x,z) in enumerate([(-3,4),(3,4),(-3,-4),(3,-4)]):
   s.geometry('column'+str(i),[basebox([.7,.2,.7],[x,.06,z],STONE),basebox([.38,2.7,.38],[x,.26,z],'#9E9E90'),basebox([.75,.2,.75],[x,2.96,z],STONE)])
  if key=='bridge':
   s.drop('ground','stone_route','primary','secondary')
   s.slab('ground',20,16,y=-1.85,h=.18,color='#485653')
   for n,z in [('near',5.25),('far',-5.25)]:s.slab('bank_'+n,20,5.5,0,z,-1.67,1.73,color='#85877E')
   s.slab('ravine_water',18.8,4.9,0,0,-1.60,.06,color=WATER,material='mat.water')
   s.geometry('boundary_footings',[basebox([.6,1.73,5.0],[x,-1.67,0],'#747D76') for x in (-9.7,9.7)])
   # Vertices are authored around the far-bank hinge, not around the deck centre.
   forms=[basebox([2.6,.14,.245],[0,0,.125+i*.25],WOOD) for i in range(20)]
   forms += [basebox([.12,.17,5],[x,-.11,2.5],DARK) for x in (-1.08,1.08)]
   s.geometry('secondary',forms,'mat.wood',at=[0,.06,-2.5],label='可抬升吊桥桥面')
   s.geometry('hinge_bearings',[basebox([.22,.32,.30],[x,.06,-2.5],METAL) for x in (-1.4,1.4)],'mat.metal')
   s.controls.append(control('secondary__mechanism__tilt','secondary','吊桥抬升角','rotation',[-1,0,0],0,80,'deg'))
   s.path('approach',[(0,8),(0,2.5)],2.8,y=.065);s.path('departure',[(0,-2.5),(0,-7)],2.8,y=.065)
   for z,n in ((2.5,'near'),(-2.5,'far')):
    for side in (-1,1):s.fence('gap_rail_'+n+str(side),[(side*1.65,z),(side*9.3,z)],y=.06,color='#7F796A')
  elif key=='lift':
   s.drop('primary','secondary','stone_route')
   s.geometry('secondary',[basebox([2.8,.16,2],[0,0,0],METAL)]+[basebox([.08,1.05,.08],[x,.16,z],DARK) for x in (-1.3,1.3) for z in (-.85,.85)]+[basebox([.08,.08,1.85],[x,1.15,0],DARK) for x in (-1.3,1.3)],'mat.metal',at=[0,.06,0],label='可升降平台与随动护栏')
   s.controls.append(control('secondary__mechanism__lift','secondary','升降平台行程','translation',[0,1,0],0,1.94,'m'))
   s.slab('upper_floor',9.5,6.0,0,-4.8,.06,2.1,color='#8D8E82')
   s.slab('upper_landing',2.8,.8,0,-1.4,2.0,.16,color=METAL,layer='structures')
   s.geometry('lift_frame',[basebox([.22,4.8,.22],[x,.06,z],DARK) for x in (-1.55,1.55) for z in (-1.12,1.12)]+[basebox([3.32,.22,2.5],[0,4.72,0],DARK)],'mat.metal')
   s.path('lift_approach',[(0,8),(0,1.1)],2.6,y=.064)
   s.steps('maintenance_stairs',-6,-2.7,1.3,2.1,4,12,y=.06)
   s.slab('stair_top_landing',1.8,1.2,-5.45,-4.6,2.0,.16,color=STONE,layer='structures')
   s.fence('upper_guard',[(-4.7,-1.8),(-1.55,-1.8)],y=2.16,color='#7B786A');s.fence('upper_guard_r',[(1.55,-1.8),(4.7,-1.8)],y=2.16,color='#7B786A')
  elif key in ('gate','vault','hall'):
   if key=='vault':s.place('primary',0,-3.5);s.place('secondary',0,-6,rot=0)
   else:s.place('secondary',0,-.5);s.place('primary',0,-5.5)
   target='primary' if key=='vault' else 'secondary';b=s.bounds(target);z=(b[0][2]+b[1][2])/2
   s.geometry('gate_flanks',[basebox([8.28,2.9,.6],[-5.56,.06,z],'#93968A'),basebox([8.28,2.9,.6],[5.56,.06,z],'#93968A')])
  elif key in ('spikes','pendulum'):
   s.place('secondary',0,0);s.place('primary',0,-5.6,s=.8)
   for side in (-1,1):s.geometry('passage_side'+str(side),[basebox([.38,1.4,8.5],[side*(3.3 if key=='pendulum' else 2.25),.06,.9],'#93968A')])
   if key=='pendulum':
    s.geometry('secondary',[beam([0,0,0],[0,-2.65,0],.12,DARK),ellipsoid([0,-3.0,0],[1.08,1.0,.62],METAL,10,5)],'mat.metal',at=[0,4.0,0],label='悬挂摆锤（顶部转轴）')
    s.geometry('pendulum_frame',[basebox([.28,4.0,.32],[x,.06,0],DARK) for x in (-3.1,3.1)]+[basebox([6.5,.28,.36],[0,4,0],DARK)],'mat.metal')
    s.controls.append(control('secondary__mechanism__swing','secondary','摆锤摆角','rotation',[0,0,1],-45,45,'deg'))
  elif key=='crystal':
   s.place('primary',0,-4.8,s=.8);s.place('secondary',0,0)
   forms=[]
   for i,(x,z,h) in enumerate([(-1.8,-4.5,1.3),(1.8,-4.4,1.8),(-1.4,-5.3,.8),(1.3,-5.6,1.1)]):
    forms.append(revolve([(0,0),(.28,0),(.33,h*.72),(0,h)],'#83B9BD',sides=6,at=[x,.5,z]))
   s.geometry('crystal_growth',forms,'mat.ceramic')
  s.finish('以连贯石质动线重组遗迹，移除现代道路杂物；机关置于真实通行/高差位置，补齐沟壑、门墙、井道、护栏与晶体。吊桥/升降台/摆锤为独立运动节点，保留控制ID并修正转轴、行程及侧向净空。')
