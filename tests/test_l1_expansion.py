"""L1 delivery contracts maintained in the complete L1-L4 catalogue. No claim of full production art certification."""
from pathlib import Path
from collections import Counter
import hashlib,json,copy
import numpy as np
import pytest
from wanxiang.util import ROOT,read_json
from wanxiang.kit_parts import build_part,definition
from wanxiang.kit_assembly import Assembler,materials_for
from wanxiang.glb import export_glb,read_glb
from wanxiang.errors import WXError

CAT=read_json(ROOT/'library/l1.json');IDS=CAT['parts']
DOMAINS={'architecture':198,'interior':118,'nature':143,'terrain':68,'props':268,'vehicle':63,'industry':70,'character':50,'creature':34,'robot':47,'gameplay':93}
SAMPLES=[next(i for i in IDS if i.startswith('l1.'+d+'.')) for d in DOMAINS]

def canonical(d):
    d=dict(d);d.pop('version',None)
    return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def test_scope_and_levels():
    rows=read_json(ROOT/'library/registry.json')['records']
    assert len(IDS)==len(set(IDS))==1152
    assert len(rows)==len({r['id'] for r in rows})==3730
    assert Counter(r['level'] for r in rows)=={1:1600,2:1010,3:1000,4:120}
    assert Counter(r['kind'] for r in rows)=={'part':1761,'assembly':1969}
    assert CAT['assemblies']==[]
    assert Counter(definition(i)['semantic']['domain'] for i in IDS)==DOMAINS
    assert all(definition(i)['level']==1 for i in IDS)

def test_baseline_definitions_unchanged_except_release_version():
    version=read_json(ROOT/'tool.manifest.json')['version']
    if version in ('3.9.0','3.10.0'):
        from baseline39_helpers import assert_only_audited_changes
        assert_only_audited_changes(allow_game410=version=='3.10.0');return
    baseline=read_json(ROOT/'authoring/l1-baseline.json')['assets'];assert len(baseline)==1033
    for ident,row in baseline.items():
        assert canonical(read_json(ROOT/row['path']))==row['sha256_except_release_version'],ident

def test_source_and_example_closure():
    rows={r['id']:r for r in read_json(ROOT/'library/registry.json')['records']}
    for ident in IDS:
        d=definition(ident);assert (ROOT/d['source']['authoring']).is_file()
        assert (ROOT/d['semantic']['consumer_example'].split('#')[0]).is_file()
        assert all(u.startswith('assembly:') and u.split(':',1)[1] in rows and rows[u.split(':',1)[1]]['level'] in (2,3,4) for u in rows[ident]['used_by']),'L1 consumers must be genuine registered L2/L3/L4 assets'
        assert d['runtime']['selection_bounds_are_colliders'] is False
    assert not any((ROOT/'library').rglob('*.glb'))
    assert not any((ROOT/'examples').rglob('*.glb'))

@pytest.mark.parametrize('ident',SAMPLES)
@pytest.mark.parametrize('style',['lowpoly','toon'])
def test_independent_gltf_roundtrip(ident,style,tmp_path):
    import trimesh
    a=build_part(ident,style);p=tmp_path/'model.glb';export_glb(a,materials_for(a),p)
    b,_,doc=read_glb(p);np.testing.assert_allclose(a.bounds(),b.bounds(),atol=3e-5)
    scene=trimesh.load(p,force='scene',process=False);assert scene.geometry
    np.testing.assert_allclose(np.asarray(a.bounds()),scene.bounds,atol=3e-5)
    assert doc['asset']['version']=='2.0'
    for mesh in b.meshes.values():
        assert np.isfinite(mesh.vertices).all() and np.isfinite(mesh.normals).all()
        assert len(mesh.faces)>0

@pytest.mark.parametrize('ident',SAMPLES)
def test_parameter_bounds_and_source_immutability(ident):
    d=definition(ident);before=copy.deepcopy(d);props=d['parameter_schema']['properties']
    for key in ('width','height','depth'):
        for v in (props[key]['minimum'],props[key]['maximum']):
            a=build_part(ident,'lowpoly',{key:v});assert np.isfinite(a.bounds()).all()
        with pytest.raises(WXError):build_part(ident,'lowpoly',{key:0})
        with pytest.raises(WXError):build_part(ident,'lowpoly',{key:float('nan')})
    assert definition(ident)==before

LOD=[i for i in IDS if 'detail' in definition(i)['parameter_schema']['properties']][:12]
@pytest.mark.parametrize('ident',LOD)
def test_advertised_lod_removes_geometry(ident):
    a=build_part(ident,'lowpoly',{'detail':True});b=build_part(ident,'lowpoly',{'detail':False})
    assert sum(len(m.faces) for m in b.meshes.values())<sum(len(m.faces) for m in a.meshes.values())

@pytest.mark.parametrize('domain',['robot','character','creature'])
def test_unregistered_inspection_layout_assembles(domain):
    spec=read_json(ROOT/'examples/l1'/(domain+'.json'));assert spec['metadata']['catalogue_counted'] is False
    a=Assembler('lowpoly').assemble(spec);assert a.meshes and np.isfinite(a.bounds()).all()
