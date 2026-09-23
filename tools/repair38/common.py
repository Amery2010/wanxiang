"""L4 scene authoring from individually reviewed evidence, in metres.

Bounds inform placement only; visual findings are human-authored in the TSV ledger.
No appearance scoring, asset flattening, or hidden transforms are used here.
"""
from pathlib import Path
from copy import deepcopy
import math,json,hashlib
from repair37.common import (PARTS,ASSEMBLIES,MOTIONS,inst,schema,block,basebox,ellipsoid,
                             tube,beam,mesh,roof,arch,revolve,slab_polygon)
from repair37.landscape import solid_shape,heightfield
from shapely.geometry import LineString,Point,Polygon,box as polygon_box
ROOT=Path(__file__).resolve().parents[2]
BOUNDS={}; LEDGER={}; CHANGES=[]
STONE='#B2B2A5'; PAVING='#B6B4A7'; GRASS='#859673'; WOOD='#AE926D'; DARK='#566465'; WATER='#619AA6'; METAL='#657775'

def start():
 BOUNDS.clear(); BOUNDS.update(json.loads((ROOT/'authoring/l4-reference-bounds.json').read_text()))
 rows=json.loads((ROOT/'authoring/l4-review-inventory.json').read_text())
 LEDGER.clear();CHANGES.clear()
 for line in (ROOT/'authoring/l4-visual-findings.tsv').read_text().splitlines():
  n,p,observation=line.split('\t',2);LEDGER[rows[int(n)-1]['id']]={'ordinal':int(n),'priority':p,'observation':observation}

def local_bounds(it):
 b=BOUNDS.get(it.get('assembly',''))
 if not b:return [[-.5,0,-.5],[.5,1,.5]]
 scale=it.get('scale',[1,1,1]);ang=math.radians(it.get('rotation',[0,0,0])[1]);cs,sn=math.cos(ang),math.sin(ang)
 points=[]
 for x in (b['min'][0],b['max'][0]):
  for y in (b['min'][1],b['max'][1]):
   for z in (b['min'][2],b['max'][2]):
    x1,z1=x*scale[0],z*scale[2];points.append([cs*x1+sn*z1,y*scale[1],-sn*x1+cs*z1])
 return [[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]]

class Scene:
 def __init__(self,ident):
  self.id=ident;self.d=ASSEMBLIES[ident];self.before=deepcopy(self.d)
  self.items={it['id']:deepcopy(it) for it in self.d['instances']};self.actions=[];self.object_meta={};self.controls=[]
  self.floor=0.;self.w=28;self.depth=22
 def get(self,name):return self.items.get(name)
 def drop(self,*names):
  for name in names:self.items.pop(name,None)
 def drop_prefix(self,*prefixes):
  for name in list(self.items):
   if name.startswith(prefixes):self.items.pop(name)
 def geometry(self,name,forms,material='mat.stone',at=None,rot=None,layer='structures',label=None):
  pid='r38.'+self.id+'.'+name
  PARTS[pid]={'schema':'wx.part/1.0','id':pid,'name':label or name,'version':'3.8.0','level':1,'internal':True,
    'category':'props','shape':'faceted','size':[1,1,1],'anchor':'origin','material':material,'connectors':[],
    'shape_params':{'forms':deepcopy(forms)},'parameter_schema':schema(),
    'source':{'type':'original_scene_repair','authoring':'tools/repair38/__init__.py','revision':'3.8.0','license':'project-authored'},
    'quality':{'status':'foundation','review_scope':'L4 scene repair; individual visual ledger'},
    'description':'Editable source geometry for '+self.id,'tags':['scene-repair-internal'],
    'runtime':{'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','origin':'authored','triangle_budget':30000,'collision':{'type':'authored-mesh','static_only':True},'lod':{'levels':[]}}}
  self.items[name]=inst(name,pid,pos=at,rot=rot)
  self.object_meta[name]={'label':label or name,'layer':layer,'region':'site','locked':name=='ground'}
  return self.items[name]
 def slab(self,name,w,d,x=0,z=0,y=0,h=.06,color=PAVING,layer='ground',material='mat.stone'):
  return self.geometry(name,[basebox([w,h,d],[x,y,z],color,bevel=min(.012,h/4))],material,layer=layer)
 def ref(self,name,ref,x,z,y=None,rot=0,s=1,layer='props'):
  assert ref in ASSEMBLIES,(self.id,name,ref)
  self.items[name]=inst(name,assembly=ref,pos=[0,0,0],rot=[0,rot,0],scale=[s]*3)
  self.object_meta[name]={'label':ASSEMBLIES[ref]['name'],'layer':layer,'region':'site','locked':False}
  return self.place(name,x,z,y,rot=rot)
 def place(self,name,x,z,y=None,rot=None,s=None):
  it=self.get(name)
  if not it:return
  if rot is not None:it['rotation']=[0,rot,0]
  if s is not None:it['scale']=[s]*3 if isinstance(s,(int,float)) else list(s)
  b=local_bounds(it);y=self.floor if y is None else y
  it['position']=[round(x-(b[0][0]+b[1][0])/2,6),round(y-b[0][1],6),round(z-(b[0][2]+b[1][2])/2,6)]
  return it
 def origin(self,name,x,y,z,rot=None,s=None):
  it=self.get(name)
  if not it:return
  it['position']=[x,y,z]
  if rot is not None:it['rotation']=[0,rot,0]
  if s is not None:it['scale']=[s]*3
  return it
 def bounds(self,name):
  it=self.get(name);b=local_bounds(it);p=it.get('position',[0,0,0]);return [[b[i][k]+p[k] for k in range(3)] for i in range(2)]
 def dims(self,name):
  b=local_bounds(self.items[name]);return [b[1][i]-b[0][i] for i in range(3)]
 def path(self,name,points,width=1.4,y=.02,color=PAVING):
  poly=LineString(points).buffer(width/2,quad_segs=4,cap_style=2,join_style=2)
  return self.geometry(name,solid_shape(poly,y,y+.035,color),layer='ground')
 def fence(self,name,points,h=1.05,y=.06,color=WOOD,posts=.95):
  forms=[]
  for a,b in zip(points,points[1:]):
   dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);count=max(1,math.ceil(length/posts))
   for j in range(count+1):
    x,z=a[0]+dx*j/count,a[1]+dz*j/count;forms.append(basebox([.10,h,.10],[x,y,z],color))
   for hh in (.4,.86):forms.append(beam([a[0],y+hh*h,a[1]],[b[0],y+hh*h,b[1]],.08,color))
  return self.geometry(name,forms,'mat.wood')
 def steps(self,name,x,z,width,rise,run,count=4,y=0):
  return self.geometry(name,[basebox([width,rise*(i+1)/count,run/count],[x,y,z+run/2-(i+.5)*run/count],STONE) for i in range(count)])
 def marks(self,name,forms):return self.geometry(name,forms,'mat.paint',layer='ground')
 def standard(self,w=28,d=22,ground=GRASS):
  self.w=w;self.depth=d;self.floor=.06
  self.slab('ground',w,d,y=-.18,h=.24,color=ground)
  self.drop('access_lane','wayfinding');self.drop_prefix('safety_mark','sleeper','rail_','landing_mark','apron')
  # Existing lamps and actors become edge elements, not obstacles through the new route.
  self.place('light0',-w/2+1.2,d/2-2.5);self.place('light1',w/2-1.2,d/2-2.5)
  self.place('wayfinding',w/2-2,d/2-1.2);self.place('actor',.9,d/2-3)
 def finish(self,description):
  oldroots=set(self.items)
  # Drop inherited controls and rebind from actual current children, retaining local controls only when targets survive.
  md=self.d.setdefault('metadata',{});controls=[]
  for c in self.before.get('metadata',{}).get('state_controls',[]):
   targets=[c.get('node','')]+c.get('nodes',[])
   if '__' not in c['id'] and all(not t or t.split('.')[0] in oldroots for t in targets):controls.append(deepcopy(c))
  for n,it in self.items.items():
   if not it.get('assembly'):continue
   for c in ASSEMBLIES[it['assembly']].get('metadata',{}).get('state_controls',[]):
    cc=deepcopy(c);cc['id']=n+'__'+c['id'];cc['title']=n+' · '+c.get('title',c['id'])
    if c.get('node'):cc['node']=n+'.'+c['node']
    if c.get('nodes'):cc['nodes']=[n+'.'+t for t in c['nodes']]
    controls.append(cc)
  controls.extend(deepcopy(self.controls))
  md['state_controls']=list({c['id']:c for c in controls}.values());self.d['instances']=list(self.items.values());self.d['version']='3.8.0'
  if not isinstance(md.get('scene'),dict):md['scene']={'schema':'wx.scene/1.0','layers':{},'regions':{'site':{'label':'场景'}},'objects':{}}
  scene=md['scene'];old=scene.get('objects',{});scene['objects']={n:deepcopy(self.object_meta.get(n,old.get(n,{'label':n,'layer':'props','region':'site','locked':False}))) for n in self.items}
  layers=scene.setdefault('layers',{})
  if isinstance(layers,dict):
   for v in scene['objects'].values():layers.setdefault(v['layer'],{'label':v['layer'],'visible':True})
  scene['revision']='3.8.0';scene['groundY']=self.floor
  # Explicit design envelope is not a physical bounding-box certification.
  scene['spawn_points']=[{'id':'visitor','position':[0,self.floor,self.depth/2-1.2],'forward':[0,0,-1]}]
  md.setdefault('source',{}).update(authoring='tools/repair38/__init__.py',revision='3.8.0')
  finding=LEDGER[self.id];md['repair38']={'baseline':'3.7.1','problem':finding['observation'],'change':description,
    'old_root_nodes':sorted({i['id'] for i in self.before['instances']}),'retained_root_nodes':sorted({i['id'] for i in self.before['instances']}&set(self.items)),
    'evidence':'evidence/l4-v3.8.0','visual_status':'see human review ledger; not asserted by authoring code'}
  CHANGES.append({'id':self.id,**finding,'change':description,'new_root_nodes':len(self.items),'source':'tools/repair38'})
