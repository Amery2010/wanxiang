"""L2 release contracts. Tests are engineering evidence, not art/device certification."""
from collections import Counter
from pathlib import Path
import copy,hashlib,json,subprocess
import numpy as np
import pytest
from wanxiang.util import ROOT,read_json
from wanxiang.kit_assembly import Assembler,get_template,materials_for
from wanxiang.kit_parts import build_part,definition
from wanxiang.mechanics import apply as state
from wanxiang.rigid_motion import tracks_for
from wanxiang.glb import export_glb,read_glb
from wanxiang.contracts import validate_connector,compatibility,world_socket
from wanxiang.runtime_metadata import describe
from wanxiang.errors import WXError
CAT=read_json(ROOT/'library/l2.json');IDS=CAT['assemblies']
TARGET={'architecture':94,'interior':82,'nature':95,'terrain':39,'props':106,'vehicle':51,'industry':45,'character':60,'creature':33,'robot':37,'gameplay':62}
FIXES={'l1.industry.drive.bearing','l1.industry.pipe.eccentric','l1.industry.pipe.hose_end','l1.industry.drive.bevel','l1.architecture.stair.spiral_tread'}
SAMPLES=[next(i for i in IDS if i.startswith('l2-'+d+'-')) for d in TARGET]
MOVING=['l2-robot-end-parallel_finger','l2-robot-joint-prismatic','l2-interior-drawercartridge-file','l2-gameplay-platform-hinge_plate','l2-creature-specialized-jaw_pincers','l2-vehicle-flightmodule-inlet','l2-industry-driveunit-rack']
def canonical(d):
    d=dict(d);d.pop('version',None)
    return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def built(ident,detail=None):
    s=get_template(ident)
    if detail is not None:s['metadata']['parameters']={'detail':detail}
    return s,Assembler().assemble(s)
def test_counts_and_baseline_preservation():
    rows=[r for r in read_json(ROOT/'library/registry.json')['records'] if not r['id'].startswith(('l3-','l4-'))];assert len(rows)==len({r['id'] for r in rows})==2899
    assert Counter(r['level'] for r in rows)=={1:1600,2:1010,3:266,4:23}
    assert Counter(r['kind'] for r in rows)=={'part':1761,'assembly':1138}
    assert len(IDS)==len(set(IDS))==704
    assert Counter(get_template(i)['metadata']['domain'] for i in IDS)==TARGET
    base=read_json(ROOT/'authoring/l2-baseline.json')['assets'];assert len(base)==2065
    changed=set()
    for key,sig in base.items():
        p=ROOT/'library'/(key+'.json');assert p.exists()
        if canonical(read_json(p))!=sig:changed.add(p.stem)
    version=read_json(ROOT/'tool.manifest.json')['version']
    if version in ('3.9.0','3.10.0'):
        from baseline39_helpers import assert_only_audited_changes
        assert_only_audited_changes(allow_game410=version=='3.10.0')
    else:assert changed==FIXES

def test_source_closure_unique_functional_recipes_and_ports():
    signatures=set();bounds=read_json(ROOT/'authoring/l1-bounds.json')['assets']
    for ident in IDS:
        s=get_template(ident);m=s['metadata'];assert m['level']==2 and (ROOT/m['source']['authoring']).is_file()
        assert len(s['instances'])<=128 and len({i['part'] for i in s['instances']})>=2
        for i in s['instances']:
            assert definition(i['part'])['level']==1
            if read_json(ROOT/'tool.manifest.json')['version'] in ('3.9.0','3.10.0'):
                from baseline39_helpers import assert_reference_current
                assert_reference_current(i['part'],definition(i['part']))
            else:assert canonical(definition(i['part']))==bounds[i['part']]['canonical_sha256']
        sig=json.dumps([s['instances'],m['state_controls']],sort_keys=True)
        assert sig not in signatures,ident;signatures.add(sig)
        for p in s['exports']:assert validate_connector(p)
    assert not list((ROOT/'library').rglob('*.glb'))
    assert not list((ROOT/'examples').rglob('*.glb'))

@pytest.mark.parametrize('ident',SAMPLES)
@pytest.mark.parametrize('style',['lowpoly','toon'])
def test_independent_sample_roundtrip(ident,style,tmp_path):
    import trimesh
    s=get_template(ident);s['style']=style;a=Assembler(style).assemble(s)
    out=tmp_path/'asset.glb';tracks=tracks_for(a,ident);export_glb(a,materials_for(a),out,animations=tracks)
    native,_,doc=read_glb(out);independent=trimesh.load(out,force='scene',process=False)
    np.testing.assert_allclose(a.bounds(),native.bounds(),atol=4e-5)
    np.testing.assert_allclose(a.bounds(),independent.bounds,atol=4e-5)
    assert bool(doc.get('animations'))==bool(tracks)
    assert len(a.metadata['bom'])>=2

@pytest.mark.parametrize('ident',MOVING)
def test_rigid_states_lod_reset_and_clips(ident):
    s,a=built(ident);rest=a.world_matrices();cs=s['metadata']['state_controls'];assert cs
    for limit in ['min','max']:
        state(a,s,{c['id']:c[limit] for c in cs});assert np.isfinite(a.bounds()).all()
    state(a,s,{})
    for n,m in a.world_matrices().items():np.testing.assert_allclose(m,rest[n],atol=1e-8)
    old=copy.deepcopy(a.nodes)
    with pytest.raises(WXError):state(a,s,{cs[0]['id']:1e9})
    assert a.nodes==old
    for c in cs:
        for node in c.get('nodes',[c['node']]):
            transform=np.asarray(next(n for n in a.nodes if n['id']==node)['matrix'])
            np.testing.assert_allclose(np.linalg.norm(transform[:3,:3],axis=0),1,atol=1e-8)
    if s['metadata']['runtime']['lod']['levels']:
        low,la=built(ident,False)
        assert sum(len(la.meshes[n['mesh']].faces) for n in la.nodes if n.get('mesh'))<sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
        assert tracks_for(la,ident)
    assert tracks_for(a,ident)

def test_both_gripper_fingers_open_outwards():
    s,a=built('l2-robot-end-parallel_finger');before=a.world_matrices()
    state(a,s,{'openL':.08,'openR':.08});after=a.world_matrices()
    assert after['finger0'][0,3]<before['finger0'][0,3]-.079
    assert after['finger1'][0,3]>before['finger1'][0,3]+.079
    assert after['pad0'][0,3]>after['finger0'][0,3]
    assert after['pad1'][0,3]<after['finger1'][0,3]

def test_translating_port_is_anchored_and_units_unscaled():
    s,a=built('l2-robot-joint-prismatic');p=next(p for p in a.sockets if p['id']=='output');assert p['node']=='output'
    w=a.world_matrices();before=(w[p['node']]@np.r_[p['position'],1])[:3]
    state(a,s,{'stroke':.22});w=a.world_matrices();after=(w[p['node']]@np.r_[p['position'],1])[:3]
    np.testing.assert_allclose(after-before,[0,.22,0],atol=1e-8)
    pp=next(p for p in s['exports'] if p['id']=='mount')
    assert compatibility(pp,pp)['compatible']
    assert not compatibility(pp,{**pp,'span':pp['span']+.01})['compatible']
    bad={k:v for k,v in pp.items() if k!='profile'}
    with pytest.raises(WXError):validate_connector(bad)

def nested_spec():
    return {'schema':'wx.assembly/1.0','id':'l2-test-nested','name':'Nested modules','instances':[
        {'id':'actuator','assembly':'l2-robot-joint-prismatic'},
        {'id':'tool','assembly':'l2-robot-end-parallel_finger','parent':'actuator.output','attach':{'target':'actuator','socket':'output','own':'mount','mode':'opposed'}}],
        'metadata':{'state_controls':[{'id':'stroke','node':'actuator.output','min':0,'max':.22,'default':0,'axis':[0,1,0],'mode':'translation'}]}}

def test_nested_modules_socket_mating_and_collider_frames():
    s=nested_spec();a=Assembler().assemble(s)
    assert a.metadata['attachments'] and all(i['position_passed'] for i in a.metadata['attachments'])
    before=a.world_matrices();state(a,s,{'stroke':.2});after=a.world_matrices()
    np.testing.assert_allclose(after['tool'][0:3,3]-before['tool'][0:3,3],[0,.2,0],atol=1e-7)
    report=describe(a,s,include_meshes=False)
    for row in report['instances']:
        assert row['content_node'] in after
        np.testing.assert_allclose(row['node_world_matrix'],after[row['content_node']],atol=1e-8)
    assert next(r for r in report['instances'] if r['node']=='tool.finger0')['collision']['type']=='convex-hull'
    assert any(r['content_node']=='tool.finger0.__content' for r in report['instances'])

def test_non_solid_assembly_policy_and_fragment_retention():
    s,a=built('l2-nature-leafybranch-aloe');report=describe(a,s,include_meshes=False)
    assert report['assembly_colliders'][0]['collision']['type']=='none'
    assert all(r['collision']['type']=='none' for r in report['instances'])
    for ident in [i for i in IDS if i.startswith('l2-gameplay-breakable')]:
        s=get_template(ident);fragments=s['metadata']['runtime_fragment_nodes'];assert len(fragments)>=4
        assert fragments==s['metadata']['runtime']['interaction']['fragments']
        assert set(fragments)<=set(i['id'] for i in s['instances'])

def test_full_turn_motion_has_intermediate_rotations():
    ident='l2-vehicle-flightmodule-inlet';s,a=built(ident);tracks=tracks_for(a,ident)
    rotations=[np.asarray(t['rotations']) for t in tracks if 'rotations' in t];assert rotations
    assert any(len(q)>4 and np.max(np.abs(q[:,0:3]))>.5 for q in rotations)

@pytest.mark.parametrize('ident',sorted(FIXES))
def test_repaired_l1_axial_bores_are_open(ident):
    # Two-sided Moller-Trumbore ray test: any cap in the bore fails the check.
    a=build_part(ident);w=a.world_matrices();xy=(-.5,-.5) if ident.endswith('spiral_tread') else (.05,0) if ident.endswith('eccentric') else (0,0)
    origin=np.array([xy[0],-5,xy[1]]);direction=np.array([0.,1.,0.]);hits=[]
    if ident.endswith('.bearing'):origin=np.array([0,.13,-5.]);direction=np.array([0.,0.,1.])
    for n in a.nodes:
        if not n.get('mesh'):continue
        m=a.meshes[n['mesh']];v=(np.c_[m.vertices,np.ones(len(m.vertices))]@w[n['id']].T)[:,:3];t=v[m.faces]
        e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,p);valid=np.abs(det)>1e-9;inv=np.zeros_like(det);inv[valid]=1/det[valid]
        tv=origin-t[:,0];u=np.einsum('ij,ij->i',tv,p)*inv;q=np.cross(tv,e1);vv=q@direction*inv;distance=np.einsum('ij,ij->i',e2,q)*inv
        hits.extend(distance[valid&(u>-1e-7)&(vv>-1e-7)&(u+vv<1+1e-7)&(distance>0)].tolist())
    assert hits==[],(ident,hits)

@pytest.mark.parametrize('edit',[{'pivot':[float('nan'),0,0]},{'pivot':[20000,0,0]},{'enabled':1},{'pivot':[0,0,0],'attach':{'target':'base','own':'mount'}}])
def test_invalid_instance_contracts(edit):
    s={'schema':'wx.assembly/1.0','id':'bad-test','instances':[{'id':'base','part':'l1.robot.end.tool_flange'},{'id':'bad','part':'l1.robot.end.parallel_finger',**edit}]}
    with pytest.raises((WXError,ValueError)):Assembler().assemble(s)

def test_python_browser_node_and_control_parity(tmp_path):
    from wanxiang.live_viewer import bundle_data
    specs=[get_template(i) for i in MOVING]+[nested_spec()]
    states=[{c['id']:c['max'] for c in s.get('metadata',{}).get('state_controls',[])} for s in specs]
    inp=tmp_path/'in.json';out=tmp_path/'out.json';inp.write_text(json.dumps({'data':bundle_data(False),'specs':specs,'states':states}))
    subprocess.run(['node',str(ROOT/'tools/runtime_parity.cjs'),str(inp),str(out)],check=True,timeout=90)
    rows=read_json(out)
    for s,values,row in zip(specs,states,rows):
        assert 'error' not in row,row
        a=Assembler().assemble(s);state(a,s,values)
        assert row['triangles']==sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
        for n,m in a.world_matrices().items():np.testing.assert_allclose(m,np.array(row['nodes'][n]).reshape(4,4).T,atol=8e-6)
