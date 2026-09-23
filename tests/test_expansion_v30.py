"""D/E/F production gates: real geometry, connections, motion and engine recipes."""
import copy,json,subprocess,sys
from pathlib import Path
import numpy as np
import pytest
from wanxiang.util import ROOT,read_json
from wanxiang.errors import WXError
from wanxiang.kit_parts import definition,build_part
from wanxiang.kit_assembly import Assembler,get_template,materials_for
from wanxiang.semantic import evaluate,parameter_values,assembly as resolve
from wanxiang.contracts import validate_runtime,validate_connector
from wanxiang.glb import export_glb,unpack,read_glb
from wanxiang.rigid_motion import tracks_for,clips_for
from wanxiang.runtime_metadata import describe
from wanxiang.runtime_export import batch_static,protected_nodes
from wanxiang.mechanics import apply as apply_state
from wanxiang.skinning import pose_glb
sys.path.insert(0,str(ROOT/'tools'))
from audit_model_quality import form_metrics
from wanxiang.live_geometry import build_mesh
CAT=read_json(ROOT/'library/expansion.json')
PARTS=[i for i in CAT['parts'] if definition(i).get('quality',{}).get('review_scope')=='D-E']
ASMS=[i for i in CAT['assemblies'] if get_template(i).get('metadata',{}).get('quality',{}).get('review_scope')=='D-E']
DOMAINS={'architecture':(36,18,6),'interiors':(22,14,6),'industry':(18,12,6),'transport':(20,12,12),'characters':(24,16,8),'creatures':(20,10,6),'gameplay':(18,8,4),'robotics':(10,6,4)}


def assembled(ident,params=None,style='lowpoly'):
 s=get_template(ident);s['style']=style
 if params:s.setdefault('metadata',{})['parameters']=params
 return Assembler(style).assemble(s),s


def test_exact_scope_without_style_mirror_or_lod_padding():
 assert len(PARTS)==168 and len(ASMS)==154 and len(CAT['parts'])==230 and len(CAT['assemblies'])==202
 r=read_json(ROOT/'library/registry.json')['records']
 # Keep the original D-E roster distinct from later public catalogue additions.
 scope=set(PARTS+ASMS)
 r=[row for row in r if row['id'] in scope]
 assert len(r)==322 and {x['id'] for x in r}==scope
 assert sum(x['kind']=='part' for x in r)==168
 defined={kind+':'+path.stem for kind,folder in [('part','parts'),('assembly','assemblies')] for path in (ROOT/'library'/folder).glob('*.json')}
 assert all(dependency in defined for row in r for dependency in row['dependencies'])
 for domain,counts in DOMAINS.items():
  p=[i for i in PARTS if definition(i)['quality']['domain']==domain]
  a=[get_template(i) for i in ASMS if get_template(i)['metadata']['domain']==domain]
  assert (len(p),sum(x['metadata']['level']==2 for x in a),sum(x['metadata']['level']==3 for x in a))==counts
 assert len([i for i in ASMS if get_template(i)['metadata']['level']==4])==6
 assert len(CAT['scenes'])==12
 assert all((ROOT/'library/thumbnails'/(x['id']+'.webp')).is_file() for x in r)


@pytest.mark.parametrize('ident',PARTS)
@pytest.mark.parametrize('style',['lowpoly','toon'])
def test_default_forms_closed_consistent_and_finite(ident,style):
 m=build_mesh(definition(ident),style,{})
 for group in m.anatomy.get('materialGroups',[]):
  start=group['start'];end=start+group['count'];r=form_metrics(m.vertices[start:end],m.normals[start:end])
  assert r['finite']
  assert not any(r[k] for k in ('degenerate_triangles','duplicate_triangles','nonmanifold_edges','inconsistent_edges','inverted_closed','bad_normals')),r

PARAMS=[]
for i in PARTS+ASMS:
 d=definition(i) if i in PARTS else get_template(i).get('metadata',{})
 for key,p in d.get('parameter_schema',{}).get('properties',{}).items():
  for value in ([False,True] if p.get('type')=='boolean' else p.get('enum',[p.get('minimum'),p.get('maximum')])):
   if value is not None:PARAMS.append((i,key,value))
@pytest.mark.parametrize('ident,key,value',PARAMS)
def test_each_parameter_boundary_changes_valid_geometry_not_source(ident,key,value):
 if ident in PARTS:
  d=definition(ident);before=json.dumps(d,sort_keys=True);a=build_part(ident,'lowpoly',{key:value});assert json.dumps(definition(ident),sort_keys=True)==before
 else:a,_=assembled(ident,{key:value})
 assert np.isfinite(a.bounds()).all()
 for m in a.meshes.values():
  assert m.faces.min()>=0 and m.faces.max()<len(m.vertices)
  assert np.isfinite(m.normals).all() and np.allclose(np.linalg.norm(m.normals,axis=1),1,atol=1e-4)
 for s in a.sockets:validate_connector(s)


@pytest.mark.parametrize('ident',PARTS+ASMS)
def test_runtime_recipes_are_well_typed_and_authored(ident):
 d=definition(ident) if ident in PARTS else get_template(ident)['metadata']
 md=evaluate(d['runtime'],parameter_values(d.get('parameter_schema',{}),{}))
 assert validate_runtime(md)
 assert md['collision']['type']!='unspecified'


@pytest.mark.parametrize('ident',ASMS)
def test_every_assembly_resolves_and_meets_default_visible_budget(ident):
 a,s=assembled(ident)
 assert a.metadata['bom'] and np.isfinite(a.bounds()).all()
 count=sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
 assert count<=s['metadata']['runtime']['triangle_budget'],(ident,count)
 for p in a.metadata.get('attachments',[]):
  assert p['position_error_m']<1e-5 and p['normal_dot']<-.99999


@pytest.mark.parametrize('ident',[
 'exp-arch-roller_door','exp-industry-conveyor_lift','exp-industry-press_cell',
 'exp-game-platform_lift','exp-robot-linear_drive','exp-game-platform_puzzle',
 'exp-industry-production_line'])
def test_real_translations_survive_glb_export_and_pose_readback(ident,tmp_path):
 a,s=assembled(ident);tracks=tracks_for(a,ident);moving=[t for t in tracks if 'translations' in t]
 assert moving,(ident,tracks)
 p=tmp_path/'animated.glb';export_glb(a,materials_for(a),p,animations=tracks)
 _,_,doc=read_glb(p);names={n['name']:n for n in doc['nodes']}
 for track in moving:
  n=names[track['node']];assert 'matrix' not in n and len(n['translation'])==3
  clip=next(c for c in doc['animations'] if c['name']==track['name'])
  channels=[ch for ch in clip['channels'] if ch['target']['path']=='translation']
  assert channels
  assert all(doc['accessors'][clip['samplers'][ch['sampler']]['output']]['type']=='VEC3' for ch in channels)
 first=moving[0];t1=first['times'][int(np.argmax(np.linalg.norm(np.array(first['translations'])-first['translations'][0],axis=1)))]
 rest,_,_,_=pose_glb(p,first['name'],0);moved,_,_,_=pose_glb(p,first['name'],t1)
 base=next(n for n in a.nodes if n['id']==first['node'])
 # At least one descendant mesh, not merely a semantic node, must actually move.
 a0={n['id']:rest.meshes[n['mesh']].vertices for n in rest.nodes if n.get('mesh')}
 assert any(np.max(np.abs(moved.meshes[n['mesh']].vertices-a0[n['id']]))>.01 for n in moved.nodes if n.get('mesh'))


def test_translation_respects_rotated_scaled_local_frame():
 a,s=assembled('exp-robot-linear_drive');node=next(n for n in a.nodes if n['id']=='piston');m=np.array(node['matrix']);m[:3,:3]=np.array([[0,-2,0],[1,0,0],[0,0,1]]);node['matrix']=m.tolist()
 t=next(t for t in tracks_for(a,s['id']) if 'translations' in t)
 clip=next(c for c in clips_for(s['id']) if c['name']==t['name']);tr=next(x for x in clip['tracks'] if 'translations' in x)
 axis=np.array(tr['axis'],float);axis/=np.linalg.norm(axis)
 np.testing.assert_allclose(t['translations'],m[:3,3]+np.array(tr['translations'])[:,None]*(m[:3,:3]@axis))


@pytest.mark.parametrize('ident',['exp-scene-industrial','exp-scene-airport','exp-robot-biped','exp-character-firefighter'])
def test_nested_animation_targets_are_unique_real_nodes(ident):
 a,s=assembled(ident);tracks=tracks_for(a,ident);assert tracks
 assert len({(t['name'],t['node'],'translation' if 'translations'in t else 'rotation') for t in tracks})==len(tracks)
 ids={n['id'] for n in a.nodes};assert all(t['node'] in ids for t in tracks)
 assert any('.' in t['node'] for t in tracks)


@pytest.mark.parametrize('ident,count',[('exp-game-breakable_crate',6),('exp-game-breakable_wall',12)])
def test_breakable_fragments_are_not_destroyed_by_static_batching(ident,count):
 a,s=assembled(ident);frags=s['metadata']['runtime_fragment_nodes'];assert len(frags)==count
 kept=protected_nodes(a,s);assert set(frags)<=kept
 packed,report=batch_static(a,s)
 assert not any(r['source_node'].startswith(tuple(f+'.' for f in frags)) for b in report['batches'] for r in b['sources'])
 for f in frags:assert any(n.get('mesh') and (n['id']==f or n['id'].startswith(f+'.')) for n in packed.nodes)
 info=describe(a,s,False);hook=info['assembly_interactions'][0]['interaction'];assert set(hook['fragments'])==set(frags)


def test_effect_helpers_can_still_be_hidden_after_runtime_batching():
 spec={'schema':'wx.assembly/1.0','id':'fx-test','instances':[{'id':'a','part':'exp.game.fx_socket'},{'id':'b','part':'exp.game.fx_socket','position':[2,0,0]}]}
 a=Assembler().assemble(spec);p,r=batch_static(a,spec)
 assert not r['batches'];assert {'a','b'}<=set(r['protected_nodes'])
 info=describe(a,spec,False);assert all(row['helper_only'] for row in info['instances'])


@pytest.mark.parametrize('ident',['exp-arch-wall_run','exp-arch-sewer_run','exp-industry-pipe_run','exp-industry-valve_manifold','exp-transport-rail_run','exp-transport-rail_junction'])
def test_connected_modules_have_actual_mated_edges(ident):
 a,_=assembled(ident);rows=a.metadata['attachments'];assert len(rows)>=2
 assert all(r['position_error_m']<1e-6 and r['normal_dot']<-.99999 for r in rows)


@pytest.mark.parametrize('ident',['exp.transport.rail_straight','exp.transport.rail_curve','exp.transport.rail_switch'])
def test_track_gauge_is_present_in_geometry_at_every_exported_endpoint(ident):
 a=build_part(ident);v=np.vstack([m.vertices for m in a.meshes.values()])
 for port in a.sockets:
  if port.get('interface')!='rail.standard.v1':continue
  center=np.array(port['position']);tan=np.array(port['tangent'])
  for sign in [-1,1]:
   point=center+tan*(1.435/2)*sign
   assert np.linalg.norm(v-point,axis=1).min()<1e-5,(ident,port['id'],point)


def test_left_wing_preserves_camber_instead_of_flipping_upside_down():
 a=build_part('exp.transport.wing',params={'side':'right'});b=build_part('exp.transport.wing',params={'side':'left'})
 av=np.vstack([m.vertices for m in a.meshes.values()]);bv=np.vstack([m.vertices for m in b.meshes.values()]);av[:,0]*=-1
 # Rod winding/sample ordering is irrelevant: compare the mirrored spatial sets.
 from scipy.spatial import cKDTree
 assert cKDTree(bv).query(av)[0].max()<1e-5
 np.testing.assert_allclose(a.bounds()[:,1:],b.bounds()[:,1:],atol=1e-5)


@pytest.mark.parametrize('height',[1.64,1.82,1.98])
def test_character_capsule_and_nested_export_resolve_parameter_height(height):
 a,s=assembled('exp-character-firefighter',{'height':height})
 d=describe(a,s,False);root=d['assembly_colliders'][0]
 assert root['child_collision_policy']=='replace-children' and root['node']=='root'
 assert root['collision']['segment_end'][1]==pytest.approx(height-.29)
 assert any(n.get('skin') for n in a.nodes)
 assert any(n.get('parent')=='skin.rig.handR' for n in a.nodes)
 for m in a.meshes.values():
  if m.skin_weights is not None:np.testing.assert_allclose(m.skin_weights.sum(1),1,atol=1e-5)


@pytest.mark.parametrize('ident',['exp.creature.serpent','exp.creature.tentacle'])
def test_weighted_creatures_use_continuous_normalized_skinning(ident):
 a=build_part(ident);meshes=[m for m in a.meshes.values() if m.skin_weights is not None];assert meshes
 assert any(np.any((m.skin_weights>0).sum(1)>1) for m in meshes)
 assert all(np.allclose(m.skin_weights.sum(1),1,atol=1e-6) for m in meshes)


@pytest.mark.parametrize('bad',[{'fragments':'bad'},{'fragments':[{}]},{'fragments':['x','x']},{'trigger':{'shape':'box','size':[1,0,1]}},{'trigger':{'shape':'sphere','radius':float('nan')}},{'event':'bad event'},{'authority':'tool-decides'}])
def test_bad_interaction_recipes_fail_closed(bad):
 md=copy.deepcopy(definition('exp.game.checkpoint_flag')['runtime']);md['interaction'].update(bad)
 with pytest.raises(WXError):validate_runtime(md)


def test_failed_mechanism_edit_preserves_last_good_state():
 a,s=assembled('exp-game-platform_lift');controls=s['metadata']['state_controls'];c=controls[0]
 apply_state(a,s,{c['id']:c['max']});before=copy.deepcopy(a.nodes)
 with pytest.raises(WXError):apply_state(a,s,{c['id']:float('nan')})
 assert a.nodes==before


def test_python_browser_transform_parity_for_production_mechanisms_and_skin(tmp_path):
 from wanxiang.live_viewer import bundle_data
 ids=['exp-arch-roller_door','exp-industry-valve_manifold','exp-transport-rail_junction','exp-character-firefighter','exp-creature-serpent_rig','exp-robot-biped','exp-game-platform_puzzle']
 specs=[get_template(i) for i in ids];inp=tmp_path/'input.json';out=tmp_path/'result.json';inp.write_text(json.dumps({'data':bundle_data(False),'specs':specs}))
 subprocess.run(['node',str(ROOT/'tools/runtime_parity.cjs'),str(inp),str(out)],check=True,timeout=100)
 for spec,row in zip(specs,read_json(out)):
  assert 'error' not in row,row
  a=Assembler().assemble(spec)
  assert row['triangles']==sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
  for node,mat in a.world_matrices().items():np.testing.assert_allclose(np.array(row['nodes'][node]).reshape(4,4).T,mat,atol=2e-5)


def test_skeleton_preserves_rigid_bones_instead_of_bending_bone_geometry():
 a=build_part('exp.creature.skeleton');assert len([n for n in a.nodes if n.get('role')=='bone'])==15
 for m in a.meshes.values():
  if m.skin_weights is not None:
   assert np.all((m.skin_weights>0).sum(1)==1)
   np.testing.assert_allclose(m.skin_weights.sum(1),1,atol=1e-6)


def test_custom_workspace_exports_nested_clips_without_registering_another_asset(tmp_path):
 spec={'schema':'wx.assembly/1.0','id':'custom-production-workspace','instances':[{'id':'elevator','assembly':'exp-game-platform_lift','position':[4,0,0]},{'id':'worker','assembly':'exp-character-miner'}]}
 a=Assembler().assemble(spec);tracks=tracks_for(a,spec['id']);assert tracks
 assert any('translations' in t and t['node'].startswith('elevator.') for t in tracks)
 assert any('rotations' in t and t['node'].startswith('worker.') for t in tracks)
 p=tmp_path/'custom.glb';export_glb(a,materials_for(a),p,animations=tracks)
 assert read_glb(p)[2]['animations']
 assert not (ROOT/'library/assemblies'/(spec['id']+'.json')).exists()


@pytest.mark.parametrize('style',['lowpoly','toon'])
@pytest.mark.parametrize('ident',[r['id'] for r in read_json(ROOT/'library/registry.json')['records'] if r.get('runtime',{}).get('lod') and r['id'].startswith('exp.') and definition(r['id']).get('quality',{}).get('review_scope')=='D-E'])
def test_production_lod_removes_real_geometry_in_both_styles(ident,style):
 from wanxiang.runtime_metadata import lod_parameters
 assets=[build_part(ident,style,lod_parameters(ident,'part',level)) for level in [0,1]]
 counts=[sum(len(m.faces) for m in a.meshes.values()) for a in assets]
 assert 0<counts[1]<counts[0],(ident,style,counts)
 np.testing.assert_allclose(assets[0].nodes[0]['matrix'],assets[1].nodes[0]['matrix'])
 for a in assets:
  for m in a.meshes.values():
   for g in m.anatomy.get('materialGroups',[]):
    r=form_metrics(m.vertices[g['start']:g['start']+g['count']],m.normals[g['start']:g['start']+g['count']])
    assert not any(r.get(k) for k in ['degenerate_triangles','duplicate_triangles','nonmanifold_edges','inconsistent_edges','inverted_closed'])


def test_unresolved_or_nonboolean_form_enabled_rejected():
 d=copy.deepcopy(definition('exp.transport.wheel'));d['shape_params']['forms'][0]['enabled']='false'
 with pytest.raises(WXError):build_mesh(d,'lowpoly',{})


@pytest.mark.parametrize('style',['lowpoly','toon'])
def test_wing_side_gate_has_only_requested_half_not_two_overlapping_wings(style):
 right=build_part('exp.transport.wing',style,{'side':'right'});left=build_part('exp.transport.wing',style,{'side':'left'})
 rv=np.vstack([m.vertices for m in right.meshes.values()]);lv=np.vstack([m.vertices for m in left.meshes.values()])
 assert rv[:,0].min()>-.011 and rv[:,0].max()>2.9
 assert lv[:,0].max()<.011 and lv[:,0].min()<-2.9
 np.testing.assert_allclose(right.bounds()[:,1:],left.bounds()[:,1:],atol=1e-5)


@pytest.mark.parametrize('ident',['exp-transport-airframe','exp-transport-jet'])
def test_aircraft_landing_struts_reach_each_supported_wheel(ident):
 a,s=assembled(ident);by={n['id']:n for n in a.nodes};assert 'gearstrut-1' in by and 'gearstrut1' in by
 assert ('tailstrut' if ident.endswith('airframe') else 'nosestrut') in by
 assert np.isfinite(a.bounds()).all() and a.bounds()[0,1]>-.02
