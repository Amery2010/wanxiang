"""Topology defects must not regress behind plausible double-sided rendering."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
import pytest
from wanxiang.util import ROOT
from wanxiang.live_geometry import build_mesh
from wanxiang.kit_parts import definition
sys.path.insert(0,str(ROOT/'tools'))
from audit_model_quality import form_metrics

@pytest.mark.parametrize('style',['lowpoly','toon'])
@pytest.mark.parametrize('id',[
    'core.arch.door','core.human.head','core.human.hand','core.human.body',
    'core.animal.cat.head','core.nature.rock','core.vehicle.body_center',
    'w.fauna.dog.head','w.fauna.fox.head','w.mech.fork_carriage','w.wear.cape',
    'w.nature.mushroom','w.outpost.dish','p6.fish.tail','p6.turtle.shell',
    'p6.insect.butterfly_wing','p6.insect.butterfly_wing_left',
    'p5.cyber.overhead_cable','p5.dock.rope_rail','p5.neon.glyph'])
def test_rebuilt_forms_are_oriented_manifold_or_intentional_sheets(id,style):
    m=build_mesh(definition(id),style,{})
    for r in m.anatomy['materialGroups']:
        a=r['start'];b=a+r['count'];q=form_metrics(m.vertices[a:b],m.normals[a:b])
        assert q['finite']
        assert not any(q[k] for k in ['degenerate_triangles','duplicate_triangles','nonmanifold_edges','inconsistent_edges','inverted_closed','bad_normals']),(id,style,q)

@pytest.mark.parametrize('value',[0,.54,1])
@pytest.mark.parametrize('id',['core.human.body','core.animal.cat.body','core.animal.horse.body'])
def test_toon_roundness_limits_keep_all_declared_seams_coincident(id,value):
    m=build_mesh(definition(id),'toon',{'roundness':value})
    assert np.isfinite(m.vertices).all()
    assert all(s['max_output_gap']==0 for s in m.anatomy['seams'])
    if m.skin_weights is not None:assert np.allclose(m.skin_weights.sum(1),1,atol=1e-6)

def test_production_kernel_geometry_and_shading_contracts(tmp_path):
    p=subprocess.run(['node',str(ROOT/'tools/quality_contract.cjs')],cwd=ROOT,capture_output=True,text=True,timeout=90)
    assert p.returncode==0,p.stdout+'\n'+p.stderr
    report=json.loads(p.stdout)
    assert report['failed']==0 and report['passed']>=30

def test_rebuild_refinement_is_deterministic_and_not_a_generated_only_patch():
    from author_foundation import generate
    from refinement import REBUILT
    a=generate();b=generate();assert a==b and len(REBUILT)>=18
    for ident in REBUILT:
        assert a['parts'][ident]['shape_params']==definition(ident)['shape_params']
        assert definition(ident)['source']['revision']==('3.9.0' if definition(ident).get('repair39') else '2.1.0')

@pytest.mark.parametrize('style',['lowpoly','toon'])
def test_butterfly_decal_facing_and_depth(style):
    """Open patches may legally be open, but must face out and never share depth."""
    import numpy as np
    from wanxiang.live_geometry import build_mesh
    d=json.loads((ROOT/'library/parts/p6.insect.butterfly_wing.json').read_text())
    m=build_mesh(d,style,{})
    groups=m.anatomy['materialGroups'];heights=[]
    for j,g in enumerate(groups[1:]):
        v=m.vertices[g['start']:g['start']+g['count']]
        n=m.normals[g['start']:g['start']+g['count']]
        sign=1 if j%2==0 else -1
        assert np.min(n[:,1]*sign)>.99
        assert np.ptp(v[:,1])<1e-7
        heights.append(float(v[0,1]))
    assert heights[4]>heights[0]+.0001
    assert heights[5]<heights[1]-.0001
