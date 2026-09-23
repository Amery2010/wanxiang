"""Foundation contract gates: source composition, boundaries, materials, pivots."""
from pathlib import Path
import copy,json,hashlib,subprocess,sys,itertools
import numpy as np
import pytest
from wanxiang.util import ROOT
from wanxiang.kit_parts import build_part,definition
from wanxiang.kit_assembly import Assembler,get_template,materials_for
from wanxiang.glb import export_glb,read_glb
from wanxiang.mechanics import apply as state
from wanxiang.semantic import assembly as resolve
from wanxiang.errors import WXError
COL=json.loads((ROOT/'library/foundation.json').read_text())
def signature(a):return hashlib.sha256(b''.join(m.vertices.tobytes() for m in a.meshes.values())+json.dumps(a.nodes,sort_keys=True).encode()).hexdigest()
def build(id,p):
 if id in COL['parts']:return build_part(id,params=p)
 s=get_template(id);s['metadata']['parameters']=p;return Assembler().assemble(s)
@pytest.mark.parametrize('id',COL['parts']+COL['assemblies'])
def test_parameters_in_bounds_and_reproducible(id):
 d=definition(id) if id in COL['parts'] else get_template(id);schema=d.get('parameter_schema',d.get('metadata',{}).get('parameter_schema',{}));props=schema.get('properties',{})
 base=build(id,{});assert signature(base)==signature(build(id,{}))
 cases=[]
 for k,p in props.items():
  values=[False,True] if p['type']=='boolean' else [p['minimum'],p['maximum']]
  cases.extend([{k:v} for v in values])
 numeric={k:p for k,p in props.items() if p['type']!='boolean'}
 if numeric:cases.extend([{k:p[end] for k,p in numeric.items()} for end in ['minimum','maximum']])
 for vals in cases:
  a=build(id,vals);assert np.isfinite(a.bounds()).all();assert np.prod(a.bounds()[1]-a.bounds()[0])>0
  for m in a.meshes.values():
   assert np.isfinite(m.vertices).all() and np.isfinite(m.normals).all()
   assert np.allclose(np.linalg.norm(m.normals,axis=1),1,atol=2e-5)
   assert m.faces.max()<len(m.vertices)
  for s in a.sockets:assert np.isfinite(s['position']).all()
 for k,p in numeric.items():
  with pytest.raises((WXError,ValueError)):build(id,{k:p['maximum']+100})

@pytest.mark.parametrize('id',['fnd-wall-kit','fnd-hatchback','fnd-excavator-arm','fnd-terminal'])
def test_rigid_states_do_not_rebuild_meshes_and_rollback(id):
 spec=get_template(id);a=Assembler().assemble(spec);meshbytes={k:m.vertices.tobytes() for k,m in a.meshes.items()}
 controls=spec['metadata']['state_controls'];before=copy.deepcopy(a.nodes)
 for values in itertools.product(*[[c['min'],c.get('default',0),c['max']] for c in controls]):
  report=state(a,spec,dict(zip([c['id'] for c in controls],values)))
  assert all(c['error']<1e-6 for c in report['constraints'])
  assert meshbytes=={k:m.vertices.tobytes() for k,m in a.meshes.items()}
 previous=copy.deepcopy(a.nodes)
 with pytest.raises(WXError):state(a,spec,{controls[0]['id']:10000})
 assert a.nodes==previous
 state(a,spec,{})
 for n in a.nodes:
  expected=next(e for e in before if e['id']==n['id']);np.testing.assert_allclose(n['matrix'],expected['matrix'],atol=1e-10)

def test_compiled_body_has_one_shared_bone_tree():
 for part in ['core.human.body','core.animal.cat.body','core.animal.horse.body']:
  a=build_part(part);meshes=[n for n in a.nodes if n.get('skin')]
  joints=[n['skin']['joints'] for n in meshes];assert joints and all(j==joints[0] for j in joints)
  assert len([n for n in a.nodes if n.get('role')=='bone'])==len(joints[0])
  assert len(a.metadata['anatomy']['dependencies'])>=10

def test_material_roles_not_flattened_and_virtual_derivatives():
 for style in ['lowpoly','toon','voxel']:
  a=build_part('core.vehicle.wheel',style);m=materials_for(a)
  assert len(m)==2
  assert all(x['extras']['wxStyle']==style for x in m.values())
  if style=='lowpoly':assert max(x['metallicFactor'] for x in m.values())>.5
  if style=='voxel':assert all(x['images'] for x in m.values())

def test_openings_are_geometric():
 # Ray intersections at aperture centre: actual hole, not a painted dark rectangle.
 import trimesh
 for ident,origin in [('core.arch.window_wall',[0,1.5,2]),('core.arch.door_wall',[0,1.0,2]),('core.vehicle.body_side',[1.23,.34,2])]:
  a=build_part(ident);m=next(iter(a.meshes.values()));tm=trimesh.Trimesh(m.vertices,m.faces,process=False)
  tri=tm.triangles;v0=tri[:,0];e1=tri[:,1]-v0;e2=tri[:,2]-v0;ray=np.array([0,0,-1.]);h=np.cross(np.tile(ray,(len(tri),1)),e2);det=np.einsum('ij,ij->i',e1,h);ok=np.abs(det)>1e-8;inv=np.divide(1,det,out=np.zeros_like(det),where=ok);s=np.array(origin)-v0;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=inv*(q@ray);t=inv*np.einsum('ij,ij->i',e2,q);hits=ok&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>0)
  assert not hits.any(),ident

def test_default_foundation_collection_honest_and_complete():
 assert len(COL['anchors'])==12
 assert len(set(COL['parts']))==len(COL['parts'])
 retirement=json.loads((ROOT/'library/retired.json').read_text());assert len(retirement['entries'])==731
 assert not (ROOT/'authoring/baseline-v17.json').exists()
 assert len(COL['parts'])==65
 graph=json.loads((ROOT/'library/dependency-graph.json').read_text())['nodes']
 assert all(j in graph for nodes in graph.values() for j in nodes)
 for old in ['demo-astronaut','demo-knight','demo-mage']:
  with pytest.raises(WXError) as err:get_template(old)
  assert err.value.code=='ASSET_RETIRED'
  assert not (ROOT/'library/assemblies'/(old+'.json')).exists()

def test_foundation_python_browser_transform_parity(tmp_path):
 from wanxiang.live_viewer import bundle_data
 specs=[get_template(i) for i in COL['anchors']]
 for i in ['fnd-adult','fnd-artisan','fnd-hatchback','fnd-wall-kit','fnd-armchair']:
  s=get_template(i);s['metadata']['parameters']={k:p['maximum'] for k,p in s['metadata']['parameter_schema']['properties'].items() if p['type']=='number'};specs.append(s)
 inp=tmp_path/'in.json';out=tmp_path/'out.json';inp.write_text(json.dumps({'data':bundle_data(False),'specs':specs}))
 subprocess.run(['node',str(ROOT/'tools/runtime_parity.cjs'),str(inp),str(out)],check=True,timeout=90)
 for spec,row in zip(specs,json.loads(out.read_text())):
  assert 'error' not in row,row
  a=Assembler().assemble(spec)
  assert row['triangles']==sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
  for ident,m in a.world_matrices().items():
   assert ident in row['nodes'],(spec['id'],ident)
   np.testing.assert_allclose(m,np.array(row['nodes'][ident]).reshape(4,4).T,atol=5e-6)

def test_declarative_semantics_reject_nonfinite_and_unknown():
 s=get_template('fnd-adult');before=copy.deepcopy(s);s['metadata']['parameters']={'height':float('nan')}
 with pytest.raises((ValueError,WXError)):resolve(s)
 assert before['metadata']['parameters']=={}
 s['metadata']['parameters']={'unregistered':2}
 with pytest.raises((ValueError,WXError)):resolve(s)

@pytest.mark.parametrize('height',[1.64,1.82,1.98])
@pytest.mark.parametrize('id',['fnd-adult','fnd-artisan'])
def test_declared_height_is_world_height_and_sole_origin(id,height):
 a=build(id,{'height':height});lo,hi=a.bounds()
 assert abs(lo[1])<1e-6
 assert abs((hi-lo)[1]-height)<2e-5

def test_assembly_cli_parameters_and_revisions_are_effective(tmp_path):
 from wanxiang.kit_assembly import build as publish
 from wanxiang.kit_cli import apply_patch
 out=tmp_path/'adult';r=publish(id='fnd-adult',params={'height':1.94},out=out,review=False)
 assert r['passed']
 a,_,_=read_glb(out/'release/asset.glb');assert abs((a.bounds()[1]-a.bounds()[0])[1]-1.94)<2e-5
 saved=json.loads((out/'source/kit-spec.json').read_text());assert saved['metadata']['parameters']['height']==1.94
 changed=apply_patch(saved,{'params':{'height':1.68}});assert changed['metadata']['parameters']['height']==1.68
 assert saved['metadata']['parameters']['height']==1.94
 with pytest.raises(WXError):publish(id='fnd-adult',params={'heightt':1.85},out=tmp_path/'bad',review=False)
 lock=json.loads((out/'source/dependency-lock.json').read_text());assert 'library/parts/core.human.forearm.json' in lock['parts']

def test_rigid_state_python_js_world_frame_parity(tmp_path):
 from wanxiang.live_viewer import bundle_data
 specs=[get_template(i) for i in ['fnd-hatchback','fnd-wall-kit','fnd-terminal','fnd-excavator-arm']]
 states=[{c['id']:c['max'] for c in s['metadata']['state_controls']} for s in specs]
 src=tmp_path/'in.json';dst=tmp_path/'out.json';src.write_text(json.dumps({'data':bundle_data(False),'specs':specs,'states':states}))
 subprocess.run(['node',str(ROOT/'tools/runtime_parity.cjs'),str(src),str(dst)],check=True,timeout=60)
 for s,v,row in zip(specs,states,json.loads(dst.read_text())):
  assert 'error' not in row,row
  a=Assembler().assemble(s);state(a,s,v)
  for ident,m in a.world_matrices().items():np.testing.assert_allclose(m,np.array(row['nodes'][ident]).reshape(4,4).T,atol=5e-6)
