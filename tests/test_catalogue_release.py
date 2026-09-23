"""Current catalogue gates. Counts derive from actual files, not a saved claim."""
from pathlib import Path
import copy,json,hashlib,subprocess
import numpy as np
import pytest
from wanxiang.util import ROOT
from wanxiang.kit_parts import build_part,definition,canonical_style,frame
from wanxiang.kit_assembly import Assembler,get_template,materials_for,build,split_run,explode_asset
from wanxiang.glb import export_glb,read_glb,unpack
from wanxiang.ir import AssetIR
from wanxiang.rigid_motion import tracks_for
from wanxiang.skinning import pose_glb
from wanxiang.errors import WXError

STYLES=('lowpoly','toon','voxel')
PARTS=sorted(p.stem for p in (ROOT/'library/parts').glob('*.json'))
ASSEMBLIES=sorted(p.stem for p in (ROOT/'library/assemblies').glob('*.json'))

def mesh(a):return next(iter(a.meshes.values()))
def signature(m):return hashlib.sha256(m.vertices.tobytes()+m.faces.tobytes()+m.normals.tobytes()+m.colors.tobytes()).hexdigest()
def assembled(id,style):
 s=get_template(id);s['style']=style;return Assembler(style).assemble(s)
def geometry_ok(a):
 world=a.world_matrices();assert world
 for m in a.meshes.values():
  assert 0<len(m.faces)<30001
  assert np.isfinite(m.vertices).all() and np.isfinite(m.normals).all()
  assert m.colors is not None and np.isfinite(m.colors).all()
  assert m.colors.min()>=0 and m.colors.max()<=1.001
  assert m.faces.min()>=0 and m.faces.max()<len(m.vertices)
  assert np.allclose(np.linalg.norm(m.normals,axis=1),1,atol=1e-4)
  t=m.vertices[m.faces];areas=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)
  assert areas.max()>0
  if m.skin_weights is not None:
   assert np.allclose(m.skin_weights.sum(1),1,atol=1e-5)
   assert np.all(m.skin_weights>=0)
 for n in a.nodes:
  if n.get('skin'):
   m=a.meshes[n['mesh']];assert m.skin_indices.max()<len(n['skin']['joints'])
   assert all(j in world for j in n['skin']['joints'])

@pytest.mark.parametrize('style',STYLES)
@pytest.mark.parametrize('id',PARTS)
def test_every_component_has_real_valid_export(id,style,tmp_path):
 d=definition(id);assert d['shape']=='faceted';assert 'imported_mesh' not in d
 a=build_part(id,style);geometry_ok(a)
 p=tmp_path/'part.glb';export_glb(a,materials_for(a),p)
 b,mats,doc=read_glb(p);geometry_ok(b)
 np.testing.assert_allclose(a.bounds(),b.bounds(),atol=2e-5)
 if style in ('voxel',):
  assert doc.get('images') and doc.get('textures')
 else:
  assert not doc.get('images') and not doc.get('textures')
 assert all('COLOR_0' in prim['attributes'] for mm in doc['meshes'] for prim in mm['primitives'])
 assert all(m.get('extras',{}).get('wxStyle')==style for m in doc['materials'])

@pytest.mark.parametrize('style',STYLES)
@pytest.mark.parametrize('id',ASSEMBLIES)
def test_every_assembly_and_animation_roundtrip(id,style,tmp_path):
 import trimesh
 a=assembled(id,style);geometry_ok(a);tracks=tracks_for(a,id)
 p=tmp_path/'assembly.glb';export_glb(a,materials_for(a),p,animations=tracks)
 b,mats,doc=read_glb(p);assert len(b.nodes)>=len(a.nodes)
 assert bool(doc.get('animations'))==bool(tracks)
 assert all(x.get('position_passed',False) for x in a.metadata.get('attachments',[]))
 sc=trimesh.load(p,force='scene',process=False);assert sc.geometry
 np.testing.assert_allclose(a.bounds(),b.bounds(),atol=3e-5)
 if tracks and doc.get('skins'):
  # Nested rigid mechanisms may precede character clips. Only a clip targeting
  # a skin joint can be required to deform that skin. Rigid clips are tested separately.
  joints={j for skin in doc['skins'] for j in skin['joints']}
  skinned=[i for i,clip in enumerate(doc['animations']) if any(c['target']['node'] in joints for c in clip['channels'])]
  if skinned:
   pose,_,_,report=pose_glb(p,skinned[0],.22);assert report['skins']>0
   assert report['max_skin_displacement_m']>0

def test_catalogue_is_replaced_not_side_loaded():
 counts=json.loads((ROOT/'library/collection-manifest.json').read_text()) if (ROOT/'library/collection-manifest.json').exists() else {}
 manifest=json.loads((ROOT/'tool.manifest.json').read_text())['library']
 assert len(PARTS)==manifest['parts'] and len(ASSEMBLIES)==manifest['assembly_specs']
 # Historical definitions keep their original version; new authored definitions
 # must use the actual current release, not a stale hard-coded 1.8 whitelist.
 current=json.loads((ROOT/'tool.manifest.json').read_text())['version']
 version=lambda v:tuple(int(x) for x in v.split('.'))
 assert all(version(definition(p)['version'])<=version(current) for p in PARTS)
 assert all(definition(p)['version']=='3.8.0' for p in PARTS if p.startswith('r38.'))
 assert all(definition(p)['version']=='3.9.0' for p in PARTS if definition(p).get('repair39'))
 assert not (ROOT/'packages/runtime/src/organic.js').exists()
 pngs=list((ROOT/'library').rglob('*.png'))
 assert {p.name for p in pngs}<= {'basecolor.png'}
 assert len(pngs)<=2
 assert not list((ROOT/'library').rglob('*.glb'))
 assert not any('anatomical'==definition(p)['shape'] for p in PARTS)
 thumbs=list((ROOT/'library/thumbnails').glob('*.webp'))
 public={r['id'] for r in json.loads((ROOT/'library/registry.json').read_text())['records']}
 assert {p.stem for p in thumbs}==public
 assert not (ROOT/'library/thumbnails-small').exists() and not (ROOT/'library/thumbnails-toon').exists()
 previews=json.loads((ROOT/'library/preview-index.json').read_text())
 assert {x['id'] for x in previews}==public
 assert all(x['image']==f"thumbnails/{x['id']}.webp" and not {'small','styles'}&x.keys() for x in previews)
 assert not {p for p in PARTS if definition(p).get('internal')}&public

@pytest.mark.parametrize('id',['core.human.head','core.human.body','core.animal.cat.body','w.fauna.fox.body','core.nature.rock','p5.robot.sensor','core.human.boot'])
def test_styles_change_actual_buffers_and_remain_deterministic(id):
 ms=[mesh(build_part(id,s)) for s in STYLES]
 assert len({signature(m) for m in ms})==3
 assert signature(ms[0])==signature(mesh(build_part(id,'lowpoly')))
 assert len(ms[1].faces)>=len(ms[0].faces)

@pytest.mark.parametrize('id',['w.arch.wall','core.arch.window_wall','core.terrain.paving','w.terrain.plinth','core.human.head'])
def test_component_size_and_connectors_stay_stable(id):
 base=build_part(id);old=np.array(definition(id)['size']);requested=np.array([.71,1.31,.37])
 data=[build_part(id,st,{'size':requested.tolist()}) for st in STYLES]
 for a in data:
  np.testing.assert_allclose(a.bounds(),base.bounds()*requested/old,atol=2e-5)
  for c in a.metadata['connectors']:assert np.isfinite(frame(c)).all()
 for a in data[1:]:
  np.testing.assert_allclose(a.bounds(),data[0].bounds(),atol=2e-5)
  assert a.metadata['anchor']==data[0].metadata['anchor']

def test_roundness_palette_and_nested_style_parameters():
 # Subdivision is opt-in per form. New surface-attached heads pin their silhouette;
 # the legacy torso remains an explicit roundable control-mesh fixture.
 a=mesh(build_part('core.human.torso','toon',{'roundness':0}));b=mesh(build_part('core.human.torso','toon',{'roundness':1}))
 assert not np.allclose(a.vertices,b.vertices)
 d=definition('core.human.head');col=next(f['color'] for f in d['shape_params']['forms'] if f.get('color'))
 x=mesh(build_part('core.human.head','lowpoly',{'palette':{col.lower():'#FF2277'}}))
 assert not np.allclose(x.colors,mesh(build_part('core.human.head')).colors)
 s=get_template('world-scene-cross-theme');s['style']='toon';s['metadata']={'roundness':0};a=Assembler('toon').assemble(s)
 s['metadata']['roundness']=1;b=Assembler('toon').assemble(s)
 assert hashlib.sha256(b''.join(m.vertices.tobytes() for m in a.meshes.values())).digest()!=hashlib.sha256(b''.join(m.vertices.tobytes() for m in b.meshes.values())).digest()

@pytest.mark.parametrize('params',[{'roundness':-1},{'roundness':1.1},{'roundness':float('nan')},{'palette':{'bad':'red'}},{'size':[0,1,1]},{'size':[101,1,1]},{'size':[1,1]},{'size':[float('inf'),1,1]},{'morph':{}},{'quality':'hero'},{'script':'alert(1)'}])
def test_invalid_parameters_fail_closed(params):
 with pytest.raises((WXError,ValueError,TypeError)):build_part('core.human.head','toon',params)

@pytest.mark.parametrize('id',['../README','nonexistent.part','https://example.invalid/object','/tmp/object'])
def test_unsafe_or_unknown_component_identifiers(id):
 with pytest.raises(WXError):build_part(id)

def test_aliases_map_only_to_supported_derivatives():
 assert canonical_style('rounded')=='toon' and canonical_style('pixel')=='voxel'
 for removed in ['handpainted','painted','clay','photoreal']:
  with pytest.raises(WXError):canonical_style(removed)
 assert signature(mesh(build_part('core.human.head','rounded')))==signature(mesh(build_part('core.human.head','toon')))

def test_invalid_assembly_preserves_input_spec():
 s={'schema':'wx.assembly/1.0','id':'bad','instances':[{'id':'a','part':'core.human.head','parent':'b'},{'id':'b','part':'core.human.head','parent':'a'}]};before=copy.deepcopy(s)
 with pytest.raises(WXError):Assembler().assemble(s)
 assert before==s

def test_skin_motion_does_not_mutate_bind_pose(tmp_path):
 a=assembled('world-ranger','toon');p=tmp_path/'rig.glb';export_glb(a,materials_for(a),p,animations=tracks_for(a,'world-ranger'));before=p.read_bytes()
 _,_,_,r=pose_glb(p,0,.23);assert r['max_skin_displacement_m']>.001;assert p.read_bytes()==before

@pytest.mark.parametrize('corruption',['length','magic','truncate'])
def test_strict_glb_reader_rejects_corrupt_buffers(tmp_path,corruption):
 a=build_part('core.human.head');p=tmp_path/'x.glb';export_glb(a,materials_for(a),p);b=bytearray(p.read_bytes())
 if corruption=='length':b[8:12]=(8).to_bytes(4,'little')
 elif corruption=='magic':b[:4]=b'BAD!'
 else:b=b[:39]
 p.write_bytes(b)
 with pytest.raises((WXError,ValueError)):read_glb(p)

def test_python_node_shared_runtime_parity(tmp_path):
 from wanxiang.live_viewer import bundle_data
 specs=[]
 for id in ['world-ranger','world-scene-camp','world-cafe','world-service-robot','world-astronaut','world-scene-cross-theme']:
  for style in STYLES:
   s=get_template(id);s['style']=style;s['metadata']={**s.get('metadata',{}),'roundness':.4};specs.append(s)
 inp=tmp_path/'in.json';out=tmp_path/'out.json';inp.write_text(json.dumps({'data':bundle_data(False),'specs':specs}))
 subprocess.run(['node',str(ROOT/'tools/runtime_parity.cjs'),str(inp),str(out)],check=True,timeout=180)
 for s,j in zip(specs,json.loads(out.read_text())):
  assert 'error' not in j,j
  a=Assembler(s['style']).assemble(s)
  assert j['triangles']==sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
  for id,mat in a.world_matrices().items():
   assert id in j['nodes'],id
   np.testing.assert_allclose(mat,np.array(j['nodes'][id]).reshape(4,4).T,atol=3e-6)

def test_run_publish_revision_and_subtree_export(tmp_path):
 r=build(id='world-ranger',style='lowpoly',out=tmp_path/'hero',review=False);assert r['passed']
 src=(tmp_path/'hero/release/asset.glb').read_bytes();AssetIR.load(tmp_path/'hero/intermediate')
 out=split_run(tmp_path/'hero',tmp_path/'parts',True);assert out['count']>0
 assert src==(tmp_path/'hero/release/asset.glb').read_bytes()
 a=assembled('world-ranger','lowpoly');b=explode_asset(a,.3);assert b.nodes and a.bounds().shape==(2,3)
 with pytest.raises(WXError):build(id='world-fox',out=tmp_path/'hero',review=False)
