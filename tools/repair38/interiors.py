from .common import *

def author():
 for key in ['bathroom','bedroom','kitchen','library','living','nursery','office','reception']:
  s=Scene('l4-interior-'+key);s.w=7;s.depth=6;s.floor=.06
  s.slab('ground',7,6,y=-.18,h=.24,color='#AC997D' if key!='bathroom' else '#BCC8C3')
  # A real window opening, not opaque geometry in front of a painted rectangle.
  wall=[basebox([7,.9,.14],[0,.06,-3],'#D7D0C0'),basebox([7,.6,.14],[0,2.3,-3],'#D7D0C0'),
        basebox([2.3,1.34,.14],[-2.35,.96,-3],'#D7D0C0'),basebox([2.3,1.34,.14],[2.35,.96,-3],'#D7D0C0')]
  s.geometry('cutaway_wall0',wall,'mat.plaster');s.geometry('cutaway_wall1',[basebox([.14,2.84,6],[-3.5,.06,0],'#D7D0C0')],'mat.plaster')
  s.geometry('window_frame',[basebox([2.45,.10,.22],[0,.94,-3],'#EAE5D8'),basebox([2.45,.10,.22],[0,2.25,-3],'#EAE5D8'),
    basebox([.08,1.32,.18],[0,.95,-3],'#EAE5D8'),basebox([.08,1.32,.18],[-1.2,.95,-3],'#EAE5D8'),basebox([.08,1.32,.18],[1.2,.95,-3],'#EAE5D8')],'mat.wood')
  s.geometry('window_glass',[basebox([2.3,1.20,.02],[0,1.02,-3],'#A7C5CB')],'mat.glass')
  s.geometry('skirting',[basebox([6.86,.09,.035],[0,.06,-2.91],'#AAA38F'),basebox([.035,.09,5.9],[-3.41,.06,0],'#AAA38F')],'mat.wood')
  s.slab('threshold',1.4,.3,.6,2.85,.06,.025,color='#A58E70');s.slab('rug',2.3,1.5,0,.8,.065,.015,color='#96A9A4')
  s.place('plant',2.9,2.45);s.place('light',-3,-2.55)
  if key=='bathroom':
   s.drop('light','rug');s.place('primary',-2.15,-1.65,rot=90);s.place('secondary',1.7,-2.45)
   s.place('room_item0',.45,-2.4);s.place('room_item1',-2.55,1.55);s.place('room_item2',2.8,-.65,rot=90)
   s.slab('shower_drain',.32,.32,-2.55,1.55,.063,.013,color=DARK)
   s.geometry('wall_light',[basebox([.7,.1,.12],[1.7,2.35,-2.88],'#EFE8C8')],'mat.light')
   s.geometry('tiled_floor_grout',[basebox([.012,.003,5.94],[x,.061,0],'#94AAA6') for x in (-3,-2,-1,0,1,2,3)]+[basebox([6.94,.003,.012],[0,.061,z],'#94AAA6') for z in (-2,-1,0,1,2)],layer='ground')
  elif key=='bedroom':
   s.place('primary',-1.4,-1.3);s.place('secondary',2.55,-1.9);s.place('room_item0',-2.75,-1.45)
   s.place('room_item1',2.7,.4,rot=-90);s.place('room_item2',-2.9,1.05,rot=90)
   s.slab('rug',2.5,1.45,-1.15,1.2,.065,.015,color='#9CAEB0')
  elif key=='kitchen':
   s.drop('light','rug');s.place('primary',-.65,.1);s.place('secondary',2.65,-2.2)
   s.place('room_item0',-.95,-2.55);s.place('room_item1',.8,-2.5);s.place('room_item2',-.65,1.02,rot=180);s.place('room_item3',-3,1.45,rot=90)
   s.geometry('backsplash',[basebox([3.6,.68,.025],[.05,.98,-2.91],'#C1D0C8')],'mat.ceramic')
   s.geometry('extractor',[basebox([.88,.15,.55],[.8,1.90,-2.5],METAL),basebox([.4,.6,.32],[.8,2.03,-2.64],METAL)],'mat.metal')
  elif key=='library':
   s.place('primary',-2.55,-2.5);s.place('room_item0',-3,.1,rot=90);s.place('secondary',.9,-.65)
   s.place('room_item1',.9,.2,rot=180);s.ref('reading_seat','l3-interior-seat-dining',.9,-1.5)
   s.geometry('secondary',[basebox([2.25,.09,1.2],[.9,.80,-.65],WOOD)]+[basebox([.10,.74,.10],[.9+x,.06,-.65+z],WOOD) for x in (-.94,.94) for z in (-.43,.43)],'mat.wood')
   s.place('room_item2',-.8,1.7);s.place('room_item3',-1.65,1.55,rot=50);s.place('light',-2.45,2.2)
  elif key=='living':
   s.place('primary',-.8,1.15,rot=180);s.place('secondary',-.8,-2.5);s.place('room_item0',-.8,-.05)
   s.place('room_item1',1.3,.35,rot=-100);s.place('room_item2',-3,-.7,rot=90)
   b=s.bounds('secondary');s.place('room_item3',-.6,-2.5,y=b[1][1]+.008)
   s.geometry('display_screen',[basebox([1.2,.70,.065],[-.8,1.03,-2.57],DARK),basebox([.5,.03,.3],[-.8,.89,-2.57],METAL),basebox([.065,.14,.065],[-.8,.91,-2.57],METAL)],'mat.display')
  elif key=='nursery':
   s.place('primary',-1.75,-1.45);s.place('secondary',2.6,-2.35,rot=0);s.place('room_item0',-3,.8,rot=90)
   s.place('room_item1',.6,.45,rot=-30);s.place('room_item2',1.5,.1);s.place('light',2.7,1.8)
   s.geometry('secondary',[basebox([1.35,.82,.75],[2.6,.06,-2.35],WOOD),basebox([1.45,.08,.82],[2.6,.88,-2.35],'#C8B38C'),basebox([1.16,.06,.58],[2.6,.96,-2.35],'#E4E1CC')]+[basebox([.055,.14,.82],[x,.96,-2.35],WOOD) for x in (1.90,3.30)]+[basebox([1.4,.14,.055],[2.6,.96,-2.75],WOOD)]+[basebox([1.2,.31,.055],[2.6,y,-1.95],'#B39166') for y in (.13,.5)],'mat.wood')
   s.geometry('wall_shelf',[basebox([1.1,.06,.25],[1.5,1.5,-2.84],WOOD)],'mat.wood')
  elif key=='office':
   s.place('primary',-.6,-.6);s.place('secondary',.05,-1.65);s.place('room_item0',-.0,.44,rot=180);s.place('room_item1',-1.2,-1.65,rot=0)
   s.place('room_item2',2.8,-1.5);s.place('room_item3',-.6,-.6,y=s.bounds('primary')[1][1]+.01)
   s.ref('meeting_seat','l3-interior-seat-office',-1.25,.44,rot=180)
  elif key=='reception':
   s.place('primary',-1.65,-1.45);s.place('secondary',2,-1.6);s.place('room_item0',2,1.1,rot=180);s.place('room_item1',2,-.15)
   s.place('room_item2',-3,1,rot=90);s.place('room_item3',-1.9,-1.45,y=1.05,s=.58)
   # The terminal has a low keyboard: use a real lower working shelf rather than balancing it on the high counter.
   s.geometry('desk_worktop',[basebox([1.4,.06,.62],[-1.72,1.0,-1.45],WOOD)],'mat.wood')
  s.finish('逐件调整家具朝向、靠墙距离和实际接地高度；保留入口通路，增加真实窗洞与收口，并修正本房间的设备支承/家具使用关系。')
