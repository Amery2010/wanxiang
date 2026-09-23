"""P5 geometry interfaces and P6 safe retirement/runtime contracts."""
import copy,hashlib,json,subprocess
from pathlib import Path
import numpy as np
import pytest
from wanxiang.util import ROOT,read_json
from wanxiang.errors import WXError
from wanxiang.kit_parts import build_part,definition
from wanxiang.kit_assembly import Assembler,get_template,materials_for
from wanxiang.mechanics import apply as state
from wanxiang.glb import export_glb,read_glb
from wanxiang.runtime_export import batch_static,protected_nodes
from wanxiang.skinning import pose_glb
from wanxiang.rigid_motion import tracks_for

RET=json.loads((ROOT/'library/retired.json').read_text())['entries']
SCENES=json.loads((ROOT/'library/worlds.json').read_text())['scenes']

def rays(asset,origin,direction):
    result=[];world=asset.world_matrices();o=np.array(origin);ray=np.array(direction,float)
    for n in asset.nodes:
        if not n.get('mesh'):continue
        m=asset.meshes[n['mesh']].transformed(world[n['id']]);tri=m.vertices[m.faces];a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a
        h=np.cross(np.tile(ray,(len(tri),1)),e2);det=np.einsum('ij,ij->i',e1,h);good=np.abs(det)>1e-9;inv=np.divide(1,det,out=np.zeros_like(det),where=good)
        s=o-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=inv*(q@ray);t=inv*np.einsum('ij,ij->i',e2,q)
        mask=good&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>1e-7)
        result.extend(t[mask].tolist())
    return sorted(result)

@pytest.mark.parametrize('row',RET,ids=[r['kind']+':'+r['id'] for r in RET])
def test_every_old_id_is_an_explicit_tombstone(row):
    fn=definition if row['kind']=='part' else get_template
    with pytest.raises(WXError)as ex:fn(row['id'])
    assert ex.value.code=='ASSET_RETIRED' and ex.value.details['automatic_redirect'] is False
    for suggested in row['suggested_current_ids']:
        assert (ROOT/'library/parts'/(suggested+'.json')).exists() or (ROOT/'library/assemblies'/(suggested+'.json')).exists()
    folder='parts' if row['kind']=='part' else 'assemblies'
    assert not (ROOT/'library'/folder/(row['id']+'.json')).exists()


def test_retirement_closure_and_no_hidden_legacy_geometry():
    assert len(RET)==731 and len({(r['kind'],r['id'])for r in RET})==731
    assert not (ROOT/'authoring/baseline-v17.json').exists()
    assert not (ROOT/'authoring/baseline-assets').exists()
    assert not (ROOT/'authoring/overrides/assemblies/sw-astronaut.json').exists()
    assert json.loads((ROOT/'library/aliases.json').read_text())=={}
    reg=json.loads((ROOT/'library/registry.json').read_text())['records']
    public_parts={p.stem for p in (ROOT/'library/parts').glob('*.json') if not read_json(p).get('internal')}
    assemblies={p.stem for p in (ROOT/'library/assemblies').glob('*.json') if not read_json(p).get('internal')}
    assert {(r['kind'],r['id']) for r in reg}=={('part',ident) for ident in public_parts}|{('assembly',ident) for ident in assemblies}
    assert all(r['definition_status']=='authored-current' for r in reg)
    mats=[p.parent.name for p in (ROOT/'library/materials').glob('*/material.json')]
    assert mats and all(m.startswith('mat.') for m in mats)
    assert len(list((ROOT/'library').rglob('*.png')))==1

@pytest.mark.parametrize('length,beam',[(3.2,1.35),(4.35,1.75),(5.6,2.3)])
def test_open_hull_has_actual_interior_not_a_dark_cap(length,beam):
    a=build_part('p5.boat.open_hull',params={'length':length,'beam':beam})
    # A ray from the middle of the boat cavity must escape upward unimpeded.
    assert not rays(a,[0,.66,0],[0,1,0])
    # A downward ray meets the floor; lateral rays meet both side shells.
    assert rays(a,[0,1.7,0],[0,-1,0])
    assert rays(a,[0,.38,0],[1,0,0]) and rays(a,[0,.38,0],[-1,0,0])

@pytest.mark.parametrize('id',['p5.habitat.door_panel','p5.airlock.tube'])
def test_pressure_hatch_remains_physically_open(id):
    a=build_part(id)
    assert not rays(a,[0,.86,3],[0,0,-1])
    assert rays(a,[.60,.86,3],[0,0,-1])


def test_habitat_airlock_uses_declared_mating_frames():
    a=Assembler().assemble(get_template('world-habitat-docked'))
    report=a.metadata['attachments'];assert report and all(r['position_passed']for r in report)
    assert all(abs(r['normal_dot']+1.0)<1e-7 for r in report)

@pytest.mark.parametrize('id',SCENES+['world-scene-cross-theme','world-sailboat','world-service-robot','world-butterfly','world-astronaut','world-habitat-docked'])
def test_runtime_pack_preserves_geometry_bones_and_source_nodes(id,tmp_path):
    spec=get_template(id);a=Assembler().assemble(spec);before=copy.deepcopy(a.nodes);mesh_bytes={k:m.vertices.tobytes()+m.faces.tobytes() for k,m in a.meshes.items()}
    optimized,report=batch_static(a,spec)
    assert a.nodes==before and mesh_bytes=={k:m.vertices.tobytes()+m.faces.tobytes() for k,m in a.meshes.items()}
    assert report['triangles_before']==report['triangles_after']
    np.testing.assert_allclose(a.bounds(),optimized.bounds(),atol=4e-5)
    assert {n['id'] for n in a.nodes}<={n['id'] for n in optimized.nodes}
    by={n['id']:n for n in optimized.nodes};protected=protected_nodes(a,spec)
    for n in a.nodes:
        if n.get('skin') or n['id'] in protected:
            assert n==by[n['id']]
    for group in report['batches']:
        assert sum(r['triangle_count']for r in group['sources'])==group['triangles']
        assert group['material']!='mat.glass'
    clips=tracks_for(a,id);path=tmp_path/'runtime.glb';export_glb(optimized,materials_for(optimized),path,animations=clips);again,_,doc=read_glb(path)
    np.testing.assert_allclose(again.bounds(),a.bounds(),atol=4e-5)
    if clips and doc.get('skins'):
        # A scene can now export a door/lift clip before a character clip.
        # Test actual skin deformation on a channel that targets a skin joint,
        # never assert that every unrelated rigid mechanism deforms the body.
        joints={j for skin in doc['skins'] for j in skin['joints']}
        skinned=[i for i,clip in enumerate(doc['animations']) if any(c['target']['node'] in joints for c in clip['channels'])]
        assert skinned, 'Skinned source lost all joint-targeted clips'
        pose,_,_,r=pose_glb(path,skinned[0],.27);assert r['max_skin_displacement_m']>1e-4
    if spec.get('metadata',{}).get('state_controls'):
        values={c['id']:c['max'] for c in spec['metadata']['state_controls']};state(optimized,spec,values);state(a,spec,values)
        np.testing.assert_allclose(a.bounds(),optimized.bounds(),atol=4e-5)


def test_multi_axis_control_is_composed_and_bad_state_is_transactional():
    from wanxiang.ir import AssetIR
    a=AssetIR();a.group('root');a.group('hinge','root')
    spec={'metadata':{'state_controls':[{'id':'a','node':'hinge','axis':[1,0,0],'min':-90,'max':90,'default':0},{'id':'b','node':'hinge','axis':[0,1,0],'min':-90,'max':90,'default':0}]}}
    state(a,spec,{'a':30,'b':45});one=copy.deepcopy(a.nodes);state(a,spec,{'a':30,'b':45});assert one==a.nodes
    from scipy.spatial.transform import Rotation
    expect=Rotation.from_rotvec([np.pi/6,0,0]).as_matrix()@Rotation.from_rotvec([0,np.pi/4,0]).as_matrix()
    np.testing.assert_allclose(np.array(a.nodes[1]['matrix'])[:3,:3],expect,atol=1e-12)
    bad=copy.deepcopy(spec);bad['metadata']['state_controls'][1]['axis']=[float('nan'),0,0]
    with pytest.raises(WXError):state(a,bad,{'a':-30})
    assert a.nodes==one


def test_bootable_release_uses_current_modules_only():
    from wanxiang.paths import code_path
    for f in ['web/runtime-pack.js','web/seams.js','web/mechanics.js','web/app.js']:
        subprocess.run(['node','--check',str(code_path(f))],check=True,capture_output=True,timeout=30)
    from wanxiang.live_viewer import bundle_data
    d=bundle_data(False);assert len(d['worlds']['themes'])==10
    assert d['version']==__import__('wanxiang').__version__ and len(d['retired']['entries'])==731
    # The public catalogue now also includes formal L1/L2/L3/L4 expansions.
    # Membership is defined by the registry, not three historical flags.
    public={r['id'] for r in json.loads((ROOT/'library/registry.json').read_text())['records']}
    assert {a['id'] for a in d['assets']}==public


def test_browser_static_pack_matches_python_submissions(tmp_path):
    from wanxiang.live_viewer import bundle_data
    ids=['world-sailboat','world-habitat-docked','world-service-robot','world-astronaut','world-neon-kiosk']
    items=[];expected={}
    for ident in ids:
        spec=get_template(ident);a=Assembler().assemble(spec);path=tmp_path/(ident+'.glb');export_glb(a,materials_for(a),path)
        _,report=batch_static(a,spec);expected[ident]=report
        items.append({'id':ident,'spec':spec,'glb':str(path)})
    src=tmp_path/'jobs.json';dst=tmp_path/'results.json';src.write_text(json.dumps({'items':items,'data':bundle_data(False)}))
    subprocess.run(['node',str(ROOT/'tools/runtime_parity_pack.cjs'),str(src),str(dst)],check=True,timeout=60)
    for row in json.loads(dst.read_text()):
        assert 'error' not in row,row
        py=expected[row['id']];js=row['report']
        for k in ['triangles_before','triangles_after','potential_draws_before','potential_draws_after']:assert py[k]==js[k],(row['id'],k,py[k],js[k])


def test_harbor_water_does_not_fill_boat_cavities_or_hide_rowboat():
    s=get_template('world-scene-harbor');it={x['id']:x for x in s['instances']}
    for ident in ['sailboat','cargo']:
        assert it[ident]['position'][1]+.085>.02
    assert it['rowboat']['position'][0]>1.5 and it['rowboat']['position'][2]>4.5


def test_jpeg_review_renders_composite_alpha(tmp_path):
    from wanxiang.beauty import render
    from PIL import Image
    a=build_part('p5.dock.bollard');f=tmp_path/'bollard.glb';export_glb(a,materials_for(a),f)
    out=tmp_path/'review.jpg';render(f,out,160,antialias=1)
    im=Image.open(out);assert im.mode=='RGB' and im.size==(160,160)


def test_solar_panel_front_faces_daylight_review_camera():
    a=Assembler().assemble(get_template('world-solar-array'))
    world=a.world_matrices()['panel'];normal=world[:3,:3]@np.array([0.,1.,0.])
    camera=np.array([.5,.45,.74]);camera/=np.linalg.norm(camera)
    assert np.dot(normal,camera)>.6


def test_butterfly_root_has_a_real_membrane_band_and_retains_hinge_attachment():
    a=build_part('p6.insect.butterfly_wing')
    # A ray near the thorax meets the wing at both front and rear root, rather
    # than a fan that converges to one invisible point. Both skins have thickness.
    for z in [-.024,.025]:
        distances=rays(a,[.005,.1,z],[0,-1,0])
        assert len(distances)>=2
    spec=get_template('world-butterfly');asset=Assembler().assemble(spec)
    for angle in [0,35,65]:
        state(asset,spec,{'right_flap':angle,'left_flap':angle})
        for side in ['wingR','wingL']:
            np.testing.assert_allclose(asset.world_matrices()[side][:3,3],[.006 if side=='wingR' else -.006,.029,0],atol=1e-12)
