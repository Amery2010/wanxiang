"""Regression checks for repaired shapes, not automatic visual quality grading."""
from pathlib import Path
import json
import numpy as np
import pytest
from wanxiang.util import ROOT
from wanxiang.kit_assembly import Assembler, get_template, materials_for
from wanxiang.glb import export_glb, read_glb
from wanxiang.rigid_motion import tracks_for

KEYS=[
'l3-creature-aquatic-crocodile','l3-creature-aquatic-turtle','l3-creature-bird-duck',
'l3-creature-bird-heron','l3-creature-bird-owl','l3-vehicle-air-biplane',
'l3-props-container-chest','l3-vehicle-marine-canoe',
'l3-architecture-building-apartment','l3-architecture-building-office',
'l3-industry-power-solar','l3-industry-process-compressor',
'l3-interior-table-drop_leaf','l3-interior-kitchen-sink',
'l3-interior-sanitary-vanity','l3-interior-sanitary-bath',
'l3-terrain-island-crescent','l3-terrain-island-delta','l3-terrain-island-fjord']

@pytest.mark.parametrize('ident',KEYS)
@pytest.mark.parametrize('style',['lowpoly','toon'])
def test_repaired_actual_glb_roundtrip(ident,style,tmp_path):
    import trimesh
    spec=get_template(ident);spec['style']=style;a=Assembler(style).assemble(spec)
    assert a.meshes and len(a.nodes)>=2
    for m in a.meshes.values():
        assert len(m.faces) in range(1,30001)
        assert np.isfinite(m.vertices).all() and np.isfinite(m.normals).all()
        assert (m.faces>=0).all() and m.faces.max()<len(m.vertices)
    path=tmp_path/(ident+'.glb');tracks=tracks_for(a,ident)
    export_glb(a,materials_for(a),path,animations=tracks)
    restored,materials,document=read_glb(path)
    np.testing.assert_allclose(a.bounds(),restored.bounds(),atol=4e-5)
    independent=trimesh.load(path,force='scene',process=False)
    np.testing.assert_allclose(a.bounds(),independent.bounds,atol=4e-5)
    if ident.endswith('container-chest'):assert tracks and document.get('animations')


def test_public_registry_is_not_inflated_by_private_author_parts():
    rows=json.loads((ROOT/'library/registry.json').read_text())['records']
    assert len(rows)==3730 and len({r['id'] for r in rows})==3730
    assert not any(r['id'].startswith('r37.') for r in rows)
    from collections import Counter
    assert dict(Counter(r['level'] for r in rows))=={1:1600,2:1010,3:1000,4:120}


def test_real_hinged_chest_and_budget_groups_keep_transform_inheritance():
    chest=get_template('l3-props-container-chest')
    assert any(c.get('node')=='lid' for c in chest['metadata']['state_controls'])
    for ident in ('l3-architecture-building-apartment','l3-architecture-building-office'):
        spec=get_template(ident);ids={i['id'] for i in spec['instances']}
        children=[i for i in spec['instances'] if '_batch' in i['id']]
        assert children
        for child in children:
            assert child['parent'] in ids
            assert child.get('position',[0,0,0])==[0,0,0]
            assert child.get('rotation',[0,0,0])==[0,0,0]
