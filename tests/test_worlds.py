"""P3-P4 recovery gates. These exercise generated geometry, not catalogue counts alone."""
from pathlib import Path
import copy,hashlib,itertools,json,subprocess
import numpy as np
import pytest
from wanxiang.util import ROOT
from wanxiang.errors import WXError
from wanxiang.kit_parts import build_part,definition
from wanxiang.kit_assembly import Assembler,get_template
from wanxiang.mechanics import apply as apply_state
from wanxiang.live_viewer import bundle_data

CAT=json.loads((ROOT/'library/worlds.json').read_text())
DEFS=CAT['parts']+CAT['assemblies']
MOVING=[i for i in CAT['assemblies'] if get_template(i).get('metadata',{}).get('state_controls')]

def build(i,p=None):
 if i in CAT['parts']:return build_part(i,params=p or {})
 s=get_template(i);s.setdefault('metadata',{})['parameters']=p or {};return Assembler().assemble(s)

def sig(a):
 return hashlib.sha256(b''.join(m.vertices.tobytes()+m.faces.tobytes() for m in a.meshes.values())+json.dumps(a.nodes,sort_keys=True).encode()).hexdigest()

@pytest.mark.parametrize('ident',DEFS)
def test_default_geometry_and_semantic_limits(ident):
 d=definition(ident) if ident in CAT['parts'] else get_template(ident)
 params=d.get('parameter_schema',d.get('metadata',{}).get('parameter_schema',{})).get('properties',{})
 numeric={k:p for k,p in params.items() if p['type']=='number'}
 cases=[{}]+[{k:p[x]} for k,p in numeric.items() for x in ['minimum','maximum']]
 if len(numeric)>1:cases += [{k:p[x] for k,p in numeric.items()} for x in ['minimum','maximum']]
 for vals in cases:
  a=build(ident,vals);bounds=a.bounds();assert np.isfinite(bounds).all() and (bounds[1]>bounds[0]).all(),(ident,vals,bounds)
  for m in a.meshes.values():
   assert np.isfinite(m.vertices).all() and np.isfinite(m.normals).all()
   assert np.allclose(np.linalg.norm(m.normals,axis=1),1,atol=3e-5)
   assert m.faces.max()<len(m.vertices)
   t=m.vertices[m.faces];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)
   assert (area>1e-12).all(),(ident,vals,'degenerate')
 for k,p in numeric.items():
  with pytest.raises((WXError,ValueError)):build(ident,{k:p['maximum']+99})

@pytest.mark.parametrize('ident',MOVING)
def test_motion_extremes_preserve_mesh_and_rollback(ident):
 spec=get_template(ident);a=Assembler().assemble(spec);cs=spec['metadata']['state_controls'];mesh={k:m.vertices.tobytes() for k,m in a.meshes.items()}
 for values in itertools.product(*[[c['min'],c.get('default',0),c['max']] for c in cs]):
  report=apply_state(a,spec,dict(zip([c['id'] for c in cs],values)))
  assert all(r['error']<1e-6 for r in report['constraints'])
  assert mesh=={k:m.vertices.tobytes() for k,m in a.meshes.items()}
 before=copy.deepcopy(a.nodes)
 for bad in [{cs[0]['id']:1e6},{'not-a-control':1},{cs[0]['id']:float('nan')}]:
  with pytest.raises(WXError):apply_state(a,spec,bad)
  assert before==a.nodes
 apply_state(a,spec,{})

@pytest.mark.parametrize('ident',CAT['scenes'])
def test_scene_uses_only_current_registered_quality_sources(ident):
 graph=json.loads((ROOT/'library/dependency-graph.json').read_text())['nodes']
 f=json.loads((ROOT/'library/foundation.json').read_text());allowed={'part:'+i for i in CAT['parts']+f['parts']}|{'assembly:'+i for i in CAT['assemblies']+f['assemblies']};seen=set()
 # Scene repairs add authored internal helpers without adding public catalogue IDs.
 for path in (ROOT/'library/parts').glob('*.json'):
  part=json.loads(path.read_text())
  if part.get('internal') and part.get('quality',{}).get('status')=='foundation':allowed.add('part:'+part['id'])
 def visit(i):
  if i in seen:return
  assert i in allowed,i;seen.add(i)
  for child in graph[i]:visit(child)
 visit('assembly:'+ident)
 assert len(seen)>20 and get_template(ident)['metadata']['level']==4

@pytest.mark.parametrize('height',[1.64,1.82,1.98])
@pytest.mark.parametrize('width',[.90,1.18])
def test_registered_human_ports_remain_matched_after_parameters(height,width):
 a=build_part('core.human.body',params={'height':height,'build':width});seams=a.metadata['anatomy']['seams']
 assert len(seams)==6 and {s['id'] for s in seams}=={'elbowL','elbowR','handL','handR','kneeL','kneeR'}
 assert all(s['max_output_gap']==0 and s['shared_weights'] and s['removed_caps']==2 for s in seams)
 assert not build_part('core.human.forearm').metadata['anatomy']['seams']


def test_actual_horizontal_board_orientation():
 # Prevent the initial visually discovered vertical deck/shelf regression.
 for ident,key in [('world-bridge','deck0'),('world-pallet','deck0'),('world-bookshelf','shelf0')]:
  a=build(ident);w=a.world_matrices();nodes=[n for n in a.nodes if n.get('mesh') and (n['id']==key or n['id'].startswith(key+'.'))];assert nodes
  for n in nodes:
   m=a.meshes[n['mesh']];v=np.c_[m.vertices,np.ones(len(m.vertices))]@w[n['id']].T;dim=np.ptp(v[:,:3],axis=0)
   assert dim[1]<.105 and dim[0]>.70 and dim[2]>.15,(ident,dim)


def test_shared_child_palette_is_not_lost_in_composition():
 a=build('w.fauna.cow.body');b=build('w.fauna.sheep.body')
 # A palette override changes vertex colours while keeping geometry deterministic.
 from wanxiang.kit_parts import definition
 d=definition('core.human.body')
 r=build_part('core.human.body',params={'palette':{'#C9BB99':'#E53F35'}})
 base=build_part('core.human.body')
 # General palette is also tested using the actual source colour, not a guessed key.
 child=definition('core.human.upperarm')['shape_params']['forms'][0]['color']
 x=build_part('core.human.body',params={'palette':{child:'#E53F35'}})
 assert any(not np.array_equal(m.colors,x.meshes[k].colors) for k,m in base.meshes.items())


def test_python_js_controls_and_scene_node_parity(tmp_path):
 ids=['world-excavator','world-forklift','world-mobile-crane','world-repair-lift','world-barn','world-radar','world-bus','world-scene-home']
 specs=[get_template(i) for i in ids];states=[{c['id']:c['max'] for c in s.get('metadata',{}).get('state_controls',[])} for s in specs]
 src=tmp_path/'input.json';dst=tmp_path/'output.json';src.write_text(json.dumps(dict(data=bundle_data(False),specs=specs,states=states)))
 subprocess.run(['node',str(ROOT/'tools/runtime_parity.cjs'),str(src),str(dst)],check=True,timeout=120)
 rows=json.loads(dst.read_text());assert len(rows)==len(specs)
 for spec,values,row in zip(specs,states,rows):
  assert 'error' not in row,row
  a=Assembler().assemble(spec);apply_state(a,spec,values)
  assert row['triangles']==sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
  for ident,m in a.world_matrices().items():np.testing.assert_allclose(m,np.array(row['nodes'][ident]).reshape(4,4).T,atol=8e-6)


def test_worlds_catalogue_is_separate_and_variants_are_declared():
 f=json.loads((ROOT/'library/foundation.json').read_text());assert not set(DEFS)&set(f['parts']+f['assemblies'])
 assert len(CAT['themes'])==10 and len(CAT['scenes'])==10
 assert len(set(DEFS))==len(DEFS)
 assert CAT['release_policy'] and len(CAT['validation_scenes'])==1


def test_explicit_seam_compiler_contract():
 p=subprocess.run(['node',str(ROOT/'tools/seam_contract.cjs')],check=True,capture_output=True,text=True,timeout=30)
 r=json.loads(p.stdout);assert r['failed']==0 and r['passed']==10
