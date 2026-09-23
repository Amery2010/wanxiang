"""Current L3/L4 contracts; tests do not certify art quality or engine performance."""
import copy,json,subprocess
from collections import Counter
import numpy as np
import pytest
from wanxiang.util import ROOT,read_json
from wanxiang.kit_assembly import Assembler,get_template,materials_for
from wanxiang.rigid_motion import tracks_for,clips_for
from wanxiang.glb import export_glb,read_glb
TARGET={'architecture':83,'interior':94,'nature':93,'terrain':119,'props':118,'vehicle':64,'industry':53,'character':33,'creature':37,'robot':25,'gameplay':15}
L3=read_json(ROOT/'library/l3.json')['assemblies'];L4=read_json(ROOT/'library/l4.json')['assemblies']

def test_actual_counts_and_source_closure():
    records=read_json(ROOT/'library/registry.json')['records'];assert len(records)==3730
    assert Counter(r['level'] for r in records)=={1:1600,2:1010,3:1000,4:120}
    assert len(L3)==len(set(L3))==734 and len(L4)==len(set(L4))==97
    assert Counter(get_template(x)['metadata']['domain'] for x in L3)==TARGET
    for ident in L3+L4:
        s=get_template(ident);assert (ROOT/s['metadata']['source']['authoring']).is_file()
        assert len(s['instances'])>=2 and len({i['id'] for i in s['instances']})==len(s['instances'])
        for i in s['instances']:
            key='parts' if i.get('part') else 'assemblies';ref=i.get('part',i.get('assembly'))
            assert (ROOT/'library'/key/(ref+'.json')).is_file(),(ident,ref)
    assert not list((ROOT/'library').rglob('*.glb'))

def test_scenes_are_references_not_flat_meshes():
    for ident in L4:
        s=get_template(ident);m=s['metadata']['scene'];assert m['schema']=='wx.scene/1.0'
        assert set(m['objects'])=={i['id'] for i in s['instances']}
        assert m['navigation'].startswith('unbaked')
        assert all(i.get('part') or i.get('assembly') for i in s['instances'])
        assert all(o['layer'] in m['layers'] and o['region'] in m['regions'] for o in m['objects'].values())

@pytest.mark.parametrize('domain',list(TARGET))
def test_domain_sample_geometry_and_independent_export(domain,tmp_path):
    import trimesh
    ident=next(i for i in L3 if i.startswith('l3-'+domain+'-'));s=get_template(ident);a=Assembler().assemble(s)
    p=tmp_path/'sample.glb';export_glb(a,materials_for(a),p,animations=tracks_for(a,ident))
    b,_,_=read_glb(p);ind=trimesh.load(p,force='scene',process=False)
    np.testing.assert_allclose(a.bounds(),b.bounds(),atol=1e-4);np.testing.assert_allclose(a.bounds(),ind.bounds,atol=1e-4)
    assert all(np.isfinite(m.vertices).all() for m in a.meshes.values())

@pytest.mark.parametrize('ident',['l3-nature-tree-oak','l3-creature-mammal-saddled_horse','l3-robot-arm-adaptive','l3-gameplay-interactive-lift'])
def test_params_and_nested_motion_regressions(ident):
    s=get_template(ident)
    if s.get('metadata',{}).get('parameter_schema',{}).get('properties',{}).get('detail',{}).get('type')=='boolean':s['metadata']['parameters']={'detail':False}
    a=Assembler().assemble(s);tracks_for(a,ident);assert np.isfinite(a.bounds()).all()

def test_disabled_animated_subassembly_has_no_dangling_clip():
    spec={'schema':'wx.assembly/1.0','id':'test-disabled-motion','instances':[{'id':'visible','part':'l1.architecture.stair.closed_tread'},{'id':'hidden','assembly':'l3-robot-arm-adaptive','enabled':False}]}
    a=Assembler().assemble(spec);assert not clips_for(spec['id'],spec);assert not tracks_for(a,spec['id'])

def test_browser_scene_document_unit_contracts():
    p=subprocess.run(['node','tests/scene_document.test.js'],cwd=ROOT,capture_output=True,text=True,timeout=60)
    assert p.returncode==0,p.stdout+p.stderr
    result=json.loads(p.stdout.strip().splitlines()[-1]);assert result['passed']>=21 and result['failed']==0


def test_all_authored_instance_transforms_respect_runtime_limits():
    for ident in L3+L4:
        for item in get_template(ident)['instances']:
            values=item.get('scale',[1,1,1])
            assert len(values)==3 and all(isinstance(x,(int,float)) and 0<x<=100 for x in values),(ident,item['id'],values)

@pytest.mark.parametrize('ident',['l4-wildland-desert','l4-wildland-island'])
def test_tropical_scene_both_styles_fit_budget(ident):
    for style in ['lowpoly','toon']:
        spec=get_template(ident);spec['style']=style
        a=Assembler(style).assemble(spec)
        assert np.isfinite(a.bounds()).all()
