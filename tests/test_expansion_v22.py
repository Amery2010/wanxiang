"""A-C release contracts. Counts are pinned to the approved scope, not recolours."""
import copy,json,hashlib,sys,subprocess
from pathlib import Path
import numpy as np
import pytest
from wanxiang.util import ROOT,read_json
from wanxiang.errors import WXError
from wanxiang.kit_parts import build_part,definition
from wanxiang.kit_assembly import Assembler,get_template,build
from wanxiang.live_geometry import build_mesh
from wanxiang.contracts import INTERFACES,validate_connector,compatibility,compatible_parts
from wanxiang.runtime_metadata import describe,lod_parameters
sys.path.insert(0,str(ROOT/'tools'))
from audit_model_quality import form_metrics
CAT=read_json(ROOT/'library/expansion.json');PARTS=[i for i in CAT['parts'] if definition(i).get('quality',{}).get('review_scope')=='A-C'];ASSEMBLIES=[i for i in CAT['assemblies'] if get_template(i).get('metadata',{}).get('quality',{}).get('review_scope')=='A-C']


def test_scope_and_source_closure():
    rows=read_json(ROOT/'library/registry.json')['records']
    defined={kind+':'+path.stem for kind,folder in [('part','parts'),('assembly','assemblies')] for path in (ROOT/'library'/folder).glob('*.json')}
    # Pin this suite's original A-C roster, independently of later catalogue additions.
    scope=set(PARTS+ASSEMBLIES)
    rows=[row for row in rows if row['id'] in scope]
    assert len(rows)==110 and len(PARTS)==62 and len(ASSEMBLIES)==48 and len([i for i in CAT['scenes'] if i in ASSEMBLIES])==6
    assert sum(r['level']==2 for r in rows if r['id'] in ASSEMBLIES)==28
    assert sum(r['level']==3 for r in rows if r['id'] in ASSEMBLIES)==14
    assert all(dependency in defined for row in rows for dependency in row['dependencies'])
    assert {r['id'] for r in rows}==scope
    assert all(not list((ROOT/f).rglob('*.glb')) for f in ['library','examples','authoring'])
    assert all((ROOT/'library/thumbnails'/(r['id']+'.webp')).exists() for r in rows)

@pytest.mark.parametrize('ident',PARTS)
@pytest.mark.parametrize('style',['lowpoly','toon'])
def test_new_forms_closed_where_authored_and_consistent(ident,style):
    m=build_mesh(definition(ident),style,{})
    for group in m.anatomy.get('materialGroups',[]):
        a=group['start'];b=a+group['count'];r=form_metrics(m.vertices[a:b],m.normals[a:b])
        assert r['finite']
        assert not any(r[k] for k in ['degenerate_triangles','duplicate_triangles','nonmanifold_edges','inconsistent_edges','inverted_closed','bad_normals']),r

PARAM_CASES=[]
for ident in PARTS:
    for key,p in definition(ident).get('parameter_schema',{}).get('properties',{}).items():
        for value in p.get('enum',[p.get('minimum'),p.get('maximum')]):
            if value is not None:PARAM_CASES.append((ident,key,value))
@pytest.mark.parametrize('ident,key,value',PARAM_CASES)
def test_each_declared_parameter_endpoint_and_enum(ident,key,value):
    a=build_part(ident,'lowpoly',{key:value});assert a.meshes and np.isfinite(a.bounds()).all()
    for port in a.sockets:validate_connector(port)

@pytest.mark.parametrize('ident',ASSEMBLIES)
def test_every_new_assembly_resolves_reusable_sources(ident):
    a=Assembler().assemble(get_template(ident))
    assert a.metadata['bom'] and np.isfinite(a.bounds()).all()
    assert a.metadata['runtime']['schema']=='wx.runtime-metadata/1.0'
    for row in a.metadata.get('attachments',[]):assert row['position_error_m']<1e-5 and row['normal_dot']<-0.99999

@pytest.mark.parametrize('ident',[i for i in PARTS if i.startswith('exp.terrain.') and definition(i).get('connectors') and i not in ['exp.terrain.cave_arch','exp.terrain.river_bank','exp.terrain.water_channel','exp.terrain.waterfall']])
@pytest.mark.parametrize('relief',[.25,1.5])
def test_terrain_edge_samples_exist_in_actual_mesh(ident,relief):
    a=build_part(ident,params={'relief':relief});v=np.vstack([m.vertices for m in a.meshes.values()])
    for s in a.sockets:
        if s.get('interface')!='terrain.edge.1m.v1':continue
        for t,h in zip(np.linspace(-s['span']/2,s['span']/2,len(s['profile'])),s['profile']):
            point=np.asarray(s['position'])+np.asarray(s['tangent'])*t+np.array([0,h,0])
            assert np.min(np.linalg.norm(v-point,axis=1))<1e-5,(ident,s['id'],point)

def test_mating_accepts_matching_edges_and_rejects_span_profile():
    ports=build_part('exp.road.lane').sockets;a=next(s for s in ports if s['id']=='north');b=copy.deepcopy(a)
    assert compatibility(a,b)['compatible'];b['span']=2;assert not compatibility(a,b)['compatible']
    b=copy.deepcopy(a);b['profile']=[0,.1];assert not compatibility(a,b)['compatible']
    assert all(r['id'].startswith('exp.road.') for r in compatible_parts('exp.road.lane','north'))
    s={'schema':'wx.assembly/1.0','id':'test-mating','style':'lowpoly','instances':[{'id':'a','part':'exp.road.lane'},{'id':'b','part':'exp.road.lane','attach':{'target':'a','socket':'south','own':'north','mode':'opposed'}}]}
    asset=Assembler().assemble(s);assert asset.metadata['attachments'][0]['position_error_m']<1e-8
    s['instances'][1]['scale']=[.5,1,1]
    with pytest.raises(WXError):Assembler().assemble(s)
    hills=Assembler().assemble(get_template('exp-site-forest-path'))
    assert len(hills.metadata['attachments'])==5
    s=get_template('exp-site-forest-path');s['instances'][2]['params']['relief']=.6
    with pytest.raises(WXError):Assembler().assemble(s)

@pytest.mark.parametrize('interface',list(INTERFACES))
def test_contract_versions_axes_and_gender(interface):
    p={'id':'port','interface':interface,'position':[0,0,0],'normal':[0,0,1],'tangent':[1,0,0],'gender':'neutral','version':1}
    if interface.startswith('l2.'):
        p.update(span=1,profile=[0,0])
    assert validate_connector(p)
    for change in [{'version':2},{'normal':[0,0,2]},{'tangent':[0,0,1]},{'gender':'invalid'}]:
        with pytest.raises((WXError,ValueError)):validate_connector({**p,**change})
    assert not compatibility({**p,'gender':'male'},{**p,'gender':'male'})['compatible']
    assert compatibility({**p,'gender':'male'},{**p,'gender':'female'})['compatible']

@pytest.mark.parametrize('layout',['straight','bend','t','y'])
def test_water_ports_measure_actual_opening_width(layout):
    a=build_part('exp.terrain.water_channel',params={'layout':layout});v=np.vstack([m.vertices for m in a.meshes.values()]);ports=[s for s in a.sockets if s.get('interface')=='terrain.river.2m.v1']
    assert len(ports)=={'straight':2,'bend':2,'t':3,'y':3}[layout]
    for s in ports:
        for sign in [-1,1]:
            point=np.array(s['position'])+np.array(s['tangent'])*s['span']/2*sign
            assert np.linalg.norm(v-point,axis=1).min()<1e-5
    if layout in ['t','y']:
        s=get_template('exp-river-confluence');s['metadata']['parameters']={'layout':layout};a=Assembler().assemble(s);assert len([x for x in a.sockets if x.get('interface')=='terrain.river.2m.v1' and x.get('node')=='root'])==3

@pytest.mark.parametrize('ident',[r['id'] for r in read_json(ROOT/'library/registry.json')['records'] if r.get('runtime',{}).get('lod')])
def test_lod_changes_real_geometry_and_preserves_pivot(ident):
    part=(ROOT/'library/parts'/(ident+'.json')).is_file();assets=[]
    for level in [0,1]:
        params=lod_parameters(ident,'part' if part else 'assembly',level)
        if part:a=build_part(ident,params=params)
        else:s=get_template(ident);s['metadata']['parameters']=params;a=Assembler().assemble(s)
        assets.append(a)
    counts=[sum(len(m.faces) for m in a.meshes.values()) for a in assets];assert counts[1]<counts[0]
    np.testing.assert_allclose(assets[0].nodes[0]['matrix'],assets[1].nodes[0]['matrix'])
    assert not list((ROOT/'library').rglob(ident+'*.glb'))

@pytest.mark.parametrize('ident',['exp.terrain.cave_arch','exp.road.roundabout','exp.terrain.water_channel','exp.nature.boulder','exp.terrain.shore_beach','exp.nature.crystal_cluster'])
def test_explicit_colliders_are_not_selection_bounds(ident,tmp_path,monkeypatch):
    monkeypatch.setenv('WX_CACHE_DIR',str(tmp_path/'cache'));out=tmp_path/'out';r=build(id=ident,part=True,out=out,review=False)
    data=read_json(out/'release/colliders.json');assert data['selection_bounds_are_colliders'] is False
    row=data['instances'][0];c=row['collision']
    if ident.endswith('cave_arch'):
        assert c['type']=='compound' and len(c['shapes'])==3
        assert all(not (abs(s['center'][0])<s['size'][0]/2 and abs(1-s['center'][1])<s['size'][1]/2) for s in c['shapes'])
    if ident.endswith('water_channel'):assert c['type']=='none' and not data['meshes']
    if ident.endswith('roundabout'):
        m=data['meshes'][row['mesh']];v=np.array(m['positions']);assert np.linalg.norm(v[:,[0,2]],axis=1).min()>2.9
    if ident.endswith('crystal_cluster'):assert row.get('mesh') in data['meshes']
    assert r['passed']

def test_cache_hit_corruption_invalidates_and_readonly_falls_back(tmp_path,monkeypatch):
    from wanxiang import build_cache as cache
    monkeypatch.setenv('WX_CACHE_DIR',str(tmp_path/'cache'))
    a=build(id='exp.terrain.flat',part=True,out=tmp_path/'a',review=False);b=build(id='exp.terrain.flat',part=True,out=tmp_path/'b',review=False)
    assert not a['cache_hit'] and b['cache_hit'] and a['sha256']==b['sha256']
    entry=Path(cache.home())/'builds'/a['build_key'];(entry/'payload/release/asset.glb').write_bytes(b'broken')
    c=build(id='exp.terrain.flat',part=True,out=tmp_path/'c',review=False);assert not c['cache_hit'] and c['sha256']==a['sha256']
    # A file at the cache root simulates a filesystem which cannot create folders.
    blocked=tmp_path/'blocked';blocked.write_text('not a directory');monkeypatch.setenv('WX_CACHE_DIR',str(blocked))
    d=build(id='exp.terrain.flat',part=True,out=tmp_path/'d',review=False);assert d['passed'] and not d['cache_hit']

def test_cache_key_includes_author_kernel_material_motion_and_options(tmp_path):
    from wanxiang.build_cache import key_for
    root=tmp_path
    for folder in ['library/parts','library/materials/mat.test','library/motions','tools/expansion','packages/runtime/dist/compat/src','packages/kit/src/wanxiang','packages/runtime/dist/compat/vendor']:(root/folder).mkdir(parents=True,exist_ok=True)
    files={'library/parts/p.json':{'id':'p','shape_params':{'forms':[]}},'library/materials/mat.test/material.json':{'id':'mat.test'},'library/motions/p.json':{'version':1}}
    for name,obj in files.items():(root/name).write_text(json.dumps(obj))
    for name in ['packages/runtime/dist/compat/src/geometry.js','tools/expansion/common.py']:(root/name).write_text('original')
    spec={'schema':'wx.part-build/1.0','id':'p','part':'p','style':'lowpoly','params':{}};baseline=key_for(spec,root=root)[0]
    for name in [*files,'packages/runtime/dist/compat/src/geometry.js','tools/expansion/common.py']:
        p=root/name;old=p.read_text();p.write_text(json.dumps({**json.loads(old),'changed':True}) if name in files else old+' changed');assert key_for(spec,root=root)[0]!=baseline;p.write_text(old)
    assert key_for({**spec,'style':'toon'},root=root)[0]!=baseline
    assert key_for(spec,root=root,mode='runtime')[0]!=baseline
    assert key_for(spec,root=root,review=True)[0]!=baseline
    assert key_for({**spec,'params':{'size':[1,1,1]}},root=root)[0]==key_for({**spec,'params':{'size':[1.0,1.0,1.0]}},root=root)[0]

def test_batch_changed_only_verifies_real_existing_output(tmp_path,monkeypatch):
    from wanxiang.batch import run_batch
    monkeypatch.setenv('WX_CACHE_DIR',str(tmp_path/'cache'));jobs=[{'part':'exp.road.lane'}]
    a=run_batch(jobs,tmp_path/'exports');assert a['passed'] and a['results'][0]['status']=='exported'
    b=run_batch(jobs,tmp_path/'exports',changed_only=True);assert b['results'][0]['status']=='unchanged'
    (tmp_path/'exports/exp.road.lane/release/asset.glb').write_bytes(b'corrupt')
    c=run_batch(jobs,tmp_path/'exports',changed_only=True);assert c['passed'] and c['results'][0]['status']=='exported'

def test_scaffold_is_uninstalled_and_buildable(tmp_path):
    from new_component import scaffold
    from wanxiang.live_geometry import build_mesh
    r=scaffold('custom.module','Author reviewed module',tmp_path);d=read_json(r['definition']);assert not r['installed'];m=build_mesh(d,'lowpoly',{});assert len(m.faces)==12


def test_packaging_whitelist_rejects_baked_sources_and_skips_cache(tmp_path):
    from package_release import core_files
    (tmp_path/'library').mkdir();(tmp_path/'.wx-cache').mkdir();(tmp_path/'README.md').write_text('test');(tmp_path/'.wx-cache/cached.glb').write_bytes(b'cache')
    assert [p.name for p in core_files(tmp_path)]==['README.md']
    (tmp_path/'library/model.glb').write_bytes(b'model')
    with pytest.raises(ValueError):core_files(tmp_path)


def test_batch_changed_recipe_revision_is_resumable(tmp_path,monkeypatch):
    from wanxiang.batch import run_batch
    monkeypatch.setenv('WX_CACHE_DIR',str(tmp_path/'cache'))
    first=run_batch([{'part':'exp.road.lane'}],tmp_path/'batch')
    jobs=[{'part':'exp.road.lane','style':'toon'}]
    second=run_batch(jobs,tmp_path/'batch',changed_only=True)
    third=run_batch(jobs,tmp_path/'batch',changed_only=True)
    assert first['passed'] and second['passed'] and third['passed']
    assert second['results'][0]['status']=='exported' and third['results'][0]['status']=='unchanged'
    assert Path(first['results'][0]['glb']).is_file()
    assert second['results'][0]['glb']!=first['results'][0]['glb']


def test_uniform_interface_policy_and_strict_port_tolerance():
    from wanxiang.contracts import world_socket
    a=next(x for x in build_part('exp.road.lane').sockets if x['id']=='north')
    a['allowed_scale']='uniform'
    assert compatibility(world_socket(a,np.diag([2,2,2,1])),world_socket(a,np.diag([2,2,2,1])))['compatible']
    assert not compatibility(world_socket(a,np.diag([2,1,2,1])),world_socket(a,np.diag([2,1,2,1])))['compatible']
    a['tolerance']=1e-6;b=copy.deepcopy(a);b['span']+=1e-5
    assert not compatibility(a,b)['compatible']


@pytest.mark.parametrize('bad',[{'units':'cm'},{'up':'+Z'},{'triangle_budget':True},{'collision':{'type':'box','size':[0,1,1]}},{'collision':{'type':'heightfield'}},{'collision':{'type':'compound','shapes':[]}},{'lod':{'levels':[{'level':0},{'level':0}]}}])
def test_runtime_metadata_rejects_invalid_contract(bad):
    from wanxiang.contracts import validate_runtime
    md={'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','collision':{'type':'none'}}
    with pytest.raises(WXError):validate_runtime({**md,**bad})


@pytest.mark.parametrize('ident',PARTS)
def test_resolved_runtime_metadata_matches_shipped_schema(ident):
    import jsonschema
    a=build_part(ident);jsonschema.validate(a.metadata['runtime'],read_json(ROOT/'schemas/runtime-metadata.schema.json'))

def test_javascript_interface_contract_matches_python():
    cases=[]
    for ident in INTERFACES:
        a={'id':'test','interface':ident,'position':[0,0,0],'normal':[0,0,1],'tangent':[1,0,0],'span':3,'profile':[0,0]}
        for change in [{},{'span':2},{'version':2},{'units':'cm'},{'profile':[0,.1]},{'world_scale':[2,1,1]},{'gender':'male'}]:
            b={**a,**change}
            try:result=compatibility(a,b)['compatible']
            except (WXError,ValueError):result='rejected'
            cases.append({'a':a,'b':b,'expected':result})
    js="const fs=require('fs'),WXContracts=require('@wanxiang/runtime/src/contracts.js');const data=JSON.parse(fs.readFileSync(0,'utf8'));WXContracts.setRegistry(data.registry);const result=data.cases.map(c=>{try{return WXContracts.compatible(c.a,c.b).compatible}catch(e){return 'rejected'}});console.log(JSON.stringify(result));"
    r=subprocess.run(['node','-e',js],cwd=ROOT,input=json.dumps({'registry':INTERFACES,'cases':cases}),text=True,capture_output=True,check=True)
    assert json.loads(r.stdout)==[c['expected'] for c in cases]
