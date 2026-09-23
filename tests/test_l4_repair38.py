"""Scene contracts, not automated visual judgement.

Appearance observations live in authoring/l4-visual-findings.tsv and the
human-authored final review ledger. These checks protect editing and motion.
"""
import json
from collections import Counter
from pathlib import Path
import numpy as np
import pytest
from wanxiang.kit_assembly import Assembler, get_template
from wanxiang.mechanics import apply

R = Path(__file__).resolve().parents[1]
INVENTORY = json.loads((R/'authoring/l4-review-inventory.json').read_text())
IDS = [r['id'] for r in INVENTORY]
PRIORITY = {IDS[int(n)-1]: p for n,p,_ in
            (line.split('\t',2) for line in (R/'authoring/l4-visual-findings.tsv').read_text().splitlines())}


def test_public_catalogue_ids_and_levels_retained():
    rows = json.loads((R/'library/registry.json').read_text())['records']
    assert len(rows) == len({r['id'] for r in rows}) == 3730
    assert Counter(r['level'] for r in rows) == {1:1600,2:1010,3:1000,4:120}
    assert {r['id'] for r in rows if r['level']==4} == set(IDS)
    assert not any(r['id'].startswith('r38.') for r in rows)
    assert Counter(PRIORITY.values()) == {'P1':81,'P2':34,'PASS':5}


@pytest.mark.parametrize('ident', IDS)
def test_each_scene_keeps_explicit_editable_objects_and_valid_references(ident):
    spec = get_template(ident)
    instances = spec['instances']; names = {i['id'] for i in instances}
    assert len(names) == len(instances) and len(names) > 5
    scene = spec['metadata']['scene']
    assert set(scene['objects']) == names
    for entry in scene['objects'].values():
        assert entry['layer'] in scene['layers']
        assert entry['region'] in scene['regions']
    for item in instances:
        if item.get('parent'): assert item['parent'] in names
        key = 'assembly' if item.get('assembly') else 'part'
        folder = 'assemblies' if key=='assembly' else 'parts'
        assert (R/'library'/folder/(item[key]+'.json')).is_file()
        for prop in ('position','rotation','scale'):
            if prop in item: assert np.isfinite(item[prop]).all()
    controls = spec['metadata'].get('state_controls',[])
    assert len(controls) == len({c['id'] for c in controls})
    for c in controls:
        assert c['min'] <= c.get('default',0) <= c['max']
        for target in [c.get('node','')]+c.get('nodes',[]):
            if target: assert target.split('.')[0] in names
    repair = spec['metadata'].get('repair38')
    assert bool(repair) == (PRIORITY[ident]!='PASS')
    if repair:
        assert (R/spec['metadata']['source']['authoring']).is_file()
        assert repair['problem'] and repair['change']
        assert set(repair['retained_root_nodes']).issubset(names)


def bounds(asset, root):
    matrices = asset.world_matrices()
    vertices = [asset.meshes[n['mesh']].transformed(matrices[n['id']]).vertices
                for n in asset.nodes if n.get('mesh') and n['id'].split('.')[0]==root]
    v = np.vstack(vertices)
    return np.asarray([v.min(0),v.max(0)])


@pytest.mark.parametrize('style',['lowpoly','toon'])
@pytest.mark.parametrize('kind,control,values',[
 ('bridge','secondary__mechanism__tilt',[0,45,80]),
 ('lift','secondary__mechanism__lift',[0,.97,1.94]),
 ('pendulum','secondary__mechanism__swing',[-45,0,45])])
def test_repaired_motion_matches_its_real_pivot_and_endpoints(style,kind,control,values):
    spec=get_template('l4-dungeon-'+kind);spec['style']=style
    actual=next(c for c in spec['metadata']['state_controls'] if c['id']==control)
    assert actual['node']=='secondary'
    asset=Assembler(style).assemble(spec); seen=[]
    for value in values:
        apply(asset,spec,{control:value});b=bounds(asset,'secondary');seen.append(b)
        assert np.isfinite(b).all()
        if kind=='lift':assert b[0,1]==pytest.approx(.06+value,abs=1e-5)
        if kind=='bridge':assert b[0,1]>-.09
        if kind=='pendulum':assert b[0,1]>.4 and b[0,0]>-3.05 and b[1,0]<3.05
    assert not np.allclose(seen[0],seen[1])


@pytest.mark.parametrize('key',['cargo','ferry','fishing','marina','rescue','research','tug'])
def test_boat_end_panels_follow_parent_and_boarding_access_exists(key):
    d=get_template('l4-harbor-'+key); items={i['id']:i for i in d['instances']}
    panel=items['vessel_bulkheads'];assert panel['parent']=='primary'
    part=json.loads((R/'library/parts'/(panel['part']+'.json')).read_text())
    assert len(part['shape_params']['forms'])==3
    assert 'boarding_gangway' in items


def test_marina_has_an_open_outer_water_exit():
    d=get_template('l4-harbor-marina');names={i['id'] for i in d['instances']}
    assert 'pontoon_link' not in names
    assert 'secondary' in names and 'vessel_bulkheads' in names


def test_castle_replaces_disconnected_stair_with_named_components():
    d=get_template('exp-scene-castle');items={i['id']:i for i in d['instances']}
    for prefix in ('towerL','towerR'):
        assert items[prefix]['part'].startswith('r38.')
        assert all(prefix+suffix in items for suffix in
                   ('_steps','_landing','_stair_base','_landing_support','_stair_rail'))
