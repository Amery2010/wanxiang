"""Rebuild the complete current Lowpoly library from authors and persistent overrides.

Legacy v1 geometry is excluded: only an explicit, metadata-only retirement ledger remains.

The historical chain is deliberately NOT invoked: it could regress v1.7 sculpting.
Generated edits are refused unless --discard-generated is explicit. Work on a sibling
staging library, validate references and budgets, then commit with rollback.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import argparse,copy,hashlib,json,os,re,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'packages/kit/src'));sys.path.insert(0,str(R/'tools'))
from author_foundation import generate
KINDS=('parts','assemblies','motions','materials','styles')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def encode(d):return (json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def put(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encode(d))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshots(base):
    files=[p for k in KINDS for p in sorted((base/k).rglob('*')) if p.is_file()]
    files += [base/n for n in ('foundation.json','worlds.json','aliases.json','retired.json','dependency-graph.json','curation.json','registry.json','expansion.json','interfaces.json','l1.json','l2.json','l3.json','l4.json','game-expansion.json') if (base/n).is_file()]
    return {str(p.relative_to(base)):sha(p) for p in sorted(files)}
def dependencies(data):
    parts=data['parts'];assemblies=data['assemblies'];mats=data['materials'];graph={}
    def valid(i):return isinstance(i,str) and bool(re.fullmatch(r'[a-zA-Z0-9_.-]+',i)) and '..' not in i
    for ident,d in parts.items():
        if not valid(ident) or d['id']!=ident:raise ValueError('Invalid part ID '+str(ident))
        deps=[c['part'] for c in d['shape_params'].get('components',[])]
        for dep in deps:
            if dep not in parts:raise ValueError(f'{ident}: missing component {dep}')
        roles={d['material']}|{f['material'] for f in d['shape_params'].get('forms',[]) if 'material' in f}
        if roles-set(mats):raise ValueError(f'{ident}: unregistered material {roles-set(mats)}')
        graph['part:'+ident]=['part:'+x for x in deps]
    for ident,d in assemblies.items():
        if not valid(ident) or d['id']!=ident:raise ValueError('Invalid assembly ID '+str(ident))
        deps=[];instance_ids=[x['id'] for x in d.get('instances',[])]
        if len(set(instance_ids))!=len(instance_ids) or 'root' in instance_ids:raise ValueError(f'{ident}: duplicate/reserved instance ID')
        for it in d.get('instances',[]):
            kind='part' if 'part' in it else 'assembly';target=it[kind]
            if target not in (parts if kind=='part' else assemblies):raise ValueError(f'{ident}: missing {kind} {target}')
            deps.append(kind+':'+target)
        fragment_ids=d.get('metadata',{}).get('runtime_fragment_nodes',[])
        if any(i not in instance_ids for i in fragment_ids):raise ValueError(f'{ident}: unknown independently breakable node')
        graph['assembly:'+ident]=deps
    visiting=set();done=set()
    def visit(i):
        if i in visiting:raise ValueError('Dependency cycle at '+i)
        if i in done:return
        visiting.add(i)
        for j in graph.get(i,[]):visit(j)
        visiting.remove(i);done.add(i)
    for i in graph:visit(i)
    return graph

def _rebuild(discard=False):
    output=R/'authoring/generated-index.json'
    if output.exists() and not discard:
        expected=read(output)['files'];actual=snapshots(R/'library')
        changed=sorted(set(expected)^set(actual)|{k for k in set(actual)&set(expected) if actual[k]!=expected[k]})
        if changed:raise ValueError('Generated files modified; move full definitions to authoring/overrides first, or use --discard-generated: '+', '.join(changed[:8]))
    retired=read(R/'authoring/retired-v1.json')
    retired_ids={(r['kind'],r['id']) for r in retired['entries']}
    new=generate();data={k:copy.deepcopy(new.get(k,{})) for k in KINDS}
    data['styles']=read(R/'authoring/styles.json')
    aliases={}
    # Simple semantic colours use one shared authored pixel chart for the
    # optional voxel derivative. There is no legacy art or noisy texture input.
    import io
    from PIL import Image
    chart=Image.new('RGBA',(16,16),(255,255,255,255))
    for y in range(16):
        for x in range(16):
            v=255 if (x//4+y//4)%2==0 else 246;chart.putpixel((x,y),(v,v,v,255))
    bio=io.BytesIO();chart.save(bio,'PNG',optimize=False);chart_bytes=bio.getvalue()
    pixel_id='mat.voxel_chart'
    data['materials'][pixel_id]={'schema':'wx.material/1.0','id':pixel_id,'name':'Optional voxel sampling chart','version':'3.4.0','kind':'palette','displayColor':'#F6F6F6','baseColorFactor':[1,1,1,1],'roughnessFactor':1,'metallicFactor':0,'doubleSided':True,'alphaMode':'OPAQUE','channels':{'basecolor':{'file':'basecolor.png','sha256':hashlib.sha256(chart_bytes).hexdigest()}},'sampler':{'magFilter':9728,'minFilter':9728,'wrapS':10497,'wrapT':10497},'extras':{'wxStyle':'voxel','purpose':'optional shader sampling; not an asset'},'source':{'type':'original neutral 16px chart','license':'project-authored'}}
    overrides=[]
    for kind in KINDS:
        for p in sorted((R/'authoring/overrides'/kind).glob('*.json')):
            d=read(p);ident=d['id']
            if (kind[:-1] if kind!='assemblies' else 'assembly',ident) in retired_ids and not d.get('removed'):raise ValueError('Retired ID cannot be resurrected by override: '+ident)
            if d.get('removed'):data[kind].pop(ident,None)
            else:data[kind][ident]=d
            overrides.append(str(p.relative_to(R)))
    for k,kind in [('parts','part'),('assemblies','assembly')]:
        for ident,d in data[k].items():
            if (kind,ident) in retired_ids:raise ValueError('Retired source present: '+ident)
            status=d.get('quality',d.get('metadata',{}).get('quality',{})).get('status')
            if status not in ('foundation','worlds','expansion','l1','l2','l3','l4'):raise ValueError('Unapproved pool in formal release: '+ident)
    graph=dependencies(data)
    # Remove truly unused materials, including old derivatives. Part-local forms
    # and explicit component/instance overrides are part of the reference closure.
    used_mats={pixel_id}
    for d in data['parts'].values():
        used_mats.add(d['material'])
        for f in d['shape_params'].get('forms',[]):
            if f.get('material'):used_mats.add(f['material'])
        for c in d['shape_params'].get('components',[]):
            if c.get('material'):used_mats.add(c['material'])
    for d in data['assemblies'].values():
        for c in d['instances']:
            if c.get('material'):used_mats.add(c['material'])
    data['materials']={i:d for i,d in data['materials'].items() if i in used_mats}
    for i,d in data['motions'].items():
        if i not in data['assemblies'] or d.get('assembly',i)!=i:raise ValueError('Orphaned motion: '+i)
    for r in retired['entries']:
        r['suggested_current_ids']=[i for i in r['suggested_current_ids'] if i in data['parts'] or i in data['assemblies']]
    foundation_parts=[d for d in data['parts'].values() if d.get('quality',{}).get('status')=='foundation' and not d.get('internal')]
    foundation_asms=[d for d in data['assemblies'].values() if d.get('metadata',{}).get('collection')=='foundation-1.8']
    collection={'schema':'wx.collection/1.0','version':'3.10.0','name':'Foundation · 质量基线','parts':[d['id'] for d in foundation_parts],'assemblies':[d['id'] for d in foundation_asms],'anchors':[d['id'] for d in foundation_asms if d['metadata']['level']==3],'parts_by_level':dict(Counter(d['level'] for d in foundation_parts)),'status':'current-authored-library'}
    from worlds.common import THEMES
    world_parts=[d for d in data['parts'].values() if d.get('quality',{}).get('status')=='worlds']
    world_asms=[d for d in data['assemblies'].values() if d.get('metadata',{}).get('collection') in ('worlds-1.9','worlds-2.0')]
    worlds={'schema':'wx.collection/1.0','version':'3.10.0','name':'Worlds · 十大主题','parts':[d['id'] for d in world_parts],'assemblies':[d['id'] for d in world_asms], 'scenes':[d['id'] for d in world_asms if d['metadata']['level']==4 and not d['metadata'].get('validation_scene')], 'validation_scenes':[d['id'] for d in world_asms if d['metadata'].get('validation_scene')], 'themes':THEMES, 'parts_by_level':dict(Counter(d['level'] for d in world_parts)), 'assemblies_by_level':dict(Counter(d['metadata']['level'] for d in world_asms)), 'variants':[d['id'] for d in world_asms if d['metadata'].get('variant_not_new_geometry_family') or d['metadata'].get('variant_of')],'baseline':'Verified user-uploaded v1.9.1, continued original authors','release_policy':'No review geometry remains; retired IDs require explicit manual migration.'}
    from expansion.common import THEMES as EXP_THEMES
    from wanxiang.contracts import INTERFACES, catalog_metadata, validate_runtime
    ep=[d for d in data['parts'].values() if d.get('quality',{}).get('status')=='expansion']
    ea=[d for d in data['assemblies'].values() if d.get('metadata',{}).get('quality',{}).get('status')=='expansion']
    expansion={'schema':'wx.collection/1.0','version':'3.10.0','name':'Expansion · 场景构建组件','parts':[d['id'] for d in ep],'assemblies':[d['id'] for d in ea],'scenes':[d['id'] for d in ea if d['metadata']['level']==4],'themes':EXP_THEMES,'parts_by_level':dict(Counter(d['level'] for d in ep)),'assemblies_by_level':dict(Counter(d['metadata']['level'] for d in ea)),'stage':'A-F'}
    l1parts=[d for d in data['parts'].values() if d.get('quality',{}).get('status')=='l1']
    from l1_expansion.common import DOMAIN_NAMES, TARGETS
    l1={'schema':'wx.collection/1.0','version':'3.10.0','name':'L1 语义基础部件拓展','parts':[d['id'] for d in l1parts],'assemblies':[], 'themes':{'l1-'+k:v for k,v in DOMAIN_NAMES.items()},'targets':TARGETS,'domains':dict(Counter(d['quality']['domain'] for d in l1parts))}
    l2asms=[d for d in data['assemblies'].values() if d.get('metadata',{}).get('collection')=='l2-3.2']
    from l2_expansion.common import TARGETS as L2_TARGETS
    l2={'schema':'wx.collection/1.0','version':'3.10.0','name':'L2 功能子装配拓展','parts':[], 'assemblies':[d['id'] for d in l2asms], 'themes':{'l2-'+k:v for k,v in DOMAIN_NAMES.items()}, 'targets':L2_TARGETS, 'domains':dict(Counter(d['metadata']['domain'] for d in l2asms))}
    l3asms=[d for d in data['assemblies'].values() if d.get('metadata',{}).get('collection')=='l3-3.4']
    l4asms=[d for d in data['assemblies'].values() if d.get('metadata',{}).get('collection')=='l4-3.4']
    from l34_expansion.common import TARGETS as L3_TARGETS
    from l34_expansion.scenes import THEMES as SCENE_THEMES
    l3={'schema':'wx.collection/1.0','version':'3.10.0','name':'L3 完整生产资产拓展','parts':[],'assemblies':[d['id'] for d in l3asms],'themes':{'l3-'+k:v for k,v in DOMAIN_NAMES.items()},'targets':L3_TARGETS,'domains':dict(Counter(d['metadata']['domain'] for d in l3asms))}
    l4={'schema':'wx.collection/1.0','version':'3.10.0','name':'L4 可编辑场景拓展','parts':[],'assemblies':[d['id'] for d in l4asms],'scenes':[d['id'] for d in l4asms],'themes':{'l4-'+t[0]:t[1] for t in SCENE_THEMES},'new_scenes':97,'editor_schema':'wx.scene/1.0'}
    for d in [*ep,*ea,*l1parts,*l2asms,*l3asms,*l4asms]:
        from wanxiang.semantic import parameter_values,evaluate
        md=d.get('metadata',{});values=parameter_values(d.get('parameter_schema',md.get('parameter_schema',{})),md.get('parameters',{}))
        validate_runtime(evaluate(d.get('runtime',md.get('runtime',{})),values))
    used_by={i:[] for i in graph}
    for parent,children in graph.items():
        for child in children:used_by[child].append(parent)
    registry=[]
    for kind,values in [('part',data['parts']),('assembly',data['assemblies'])]:
        for ident,d in sorted(values.items()):
            if d.get('internal'):continue
            md=d.get('metadata',{});registry.append({'id':ident,'kind':kind,'name':d['name'],'category':d['category'],'level':d.get('level',md.get('level')),'theme':d.get('theme',md.get('theme','shared')),'dependencies':graph[kind+':'+ident],'used_by':sorted(set(used_by[kind+':'+ident])),'source_sha256':hashlib.sha256(encode(d)).hexdigest(),'runtime':catalog_metadata(d,kind,data['parts'],data['assemblies']),'definition_status':'authored-current','author_visual_approval':'See versioned L3/L4 evidence; prior evidence applies only to unchanged definitions'})
    from game410.common import ADDED as GAME_PARTS, DEMOS as GAME_DEMOS, KITS as GAME_KITS
    game={'schema':'wx.collection/1.0','version':'3.10.0','name':'Game Kits · 游戏部件拓展',
          'parts':list(GAME_PARTS),'assemblies':list(GAME_DEMOS),
          'kits':{k:{'name':v[0],'use':v[1],'parts':[i for i in GAME_PARTS if data['parts'][i]['game_expansion']['kit']==k],
                     'assembly':'l2-game410-'+k} for k,v in GAME_KITS.items()},
          'counting':'120 distinct authored profiles; 10 separately counted composition examples; no palette or size variants',
          'source':'tools/game410','physics_implemented':False,'rig_implemented':False}
    l1['game_expansion_parts']=list(GAME_PARTS)
    l1['targets_note']='targets describe the original L1 expansion only; game_expansion_parts are additive'
    curation={'schema':'wx.curation/2.0','version':'3.10.0','formal_assets':len(registry),'review_pool_assets':0,'retired_ids':len(retired_ids),'decisions':{'retire_legacy':len(retired_ids),'current_source':len(registry)},'note':'Legacy entries deliberately deleted, not all remodelled. Full original names and source hashes are in retired.json, without legacy geometry.'}
    manifest={'schema':'wx.toolkit/1.0','id':'wanxiang3d','version':'3.10.0','command':'./wx','agent_instructions':'AGENTS.md','protocol':'wx.result/1.0','no_automatic_network':True,'requires_blender':False,'requires_gpu_for_build':False,'geometry_kernel':['packages/runtime/src/semantic.ts','packages/runtime/src/primitives.ts','packages/runtime/src/seams.ts','packages/runtime/src/facets.ts','packages/runtime/src/geometry.ts'],'library':{'parts':len(data['parts']),'public_parts':sum(not p.get('internal') for p in data['parts'].values()),'internal_parts':sum(bool(p.get('internal')) for p in data['parts'].values()),'assembly_specs':len(data['assemblies']),'motion_presets':len(data['motions']),'materials':len(data['materials']),'style_profiles':len(data['styles']),'image_textures':1,'foundation_parts':len(foundation_parts),'foundation_assemblies':len(foundation_asms),'quality_anchors':len(collection['anchors']),'worlds_parts':len(world_parts),'worlds_assemblies':len(world_asms),'worlds_scenes':len(worlds['scenes']),'validation_scenes':len(worlds['validation_scenes']),'legacy_review_parts':0,'retired_ids':len(retired_ids),'canonical_aliases':0,'categories':dict(sorted(Counter(p['category'] for p in data['parts'].values() if not p.get('internal')).items()))},'delivery':{'studio':'pnpm dev','prebuilt_catalog_models':0,'examples':'on-demand: python tools/build_worlds.py --out generated/examples','source_glb_policy':'zero prebuilt GLB','cache':'local ignored .wx-cache, content-addressed'},'authoring':{'foundation':'tools/foundation','worlds':'tools/worlds','frontiers':'tools/frontiers','expansion':'tools/expansion','l1':'tools/l1_expansion','l2':'tools/l2_expansion','l3_l4':'tools/l34_expansion','recovery_3_7_1':'tools/repair37','l4_visual_3_8_0':'tools/repair38','advanced_lowpoly_3_9_0':'tools/repair39','game_expansion_3_10_0':'tools/game410','retirement':'authoring/retired-v1.json','overrides':'authoring/overrides','rebuild':'python tools/rebuild_library.py --overwrite'},'limitations':'docs/LIMITATIONS.md'}
    manifest['library']['definition_revision']='3.11.0'
    manifest['authoring']['aesthetic_refinement']='authoring/remodel411-definitions.json.gz'
    stage=Path(tempfile.mkdtemp(prefix='.library-stage-',dir=R));backup=R/'.library-backup'
    try:
        # Existing preview assets are not author inputs. Keep only those with live IDs.
        if (R/'library/thumbnails').exists():shutil.copytree(R/'library/thumbnails',stage/'thumbnails')
        for p in (stage/'thumbnails').glob('*'):
            if p.stem not in data['parts'] and p.stem not in data['assemblies']:p.unlink()
        for name in ('preview-index.json',):
            p=R/'library'/name
            if p.exists():
                value=read(p)
                if name=='preview-index.json':value=[row for row in value if row['id'] in data['parts'] or row['id'] in data['assemblies']]
                put(stage/name,value)
        for kind in KINDS:
            (stage/kind).mkdir(exist_ok=True)
            for ident,d in sorted(data[kind].items()):put(stage/kind/(ident+'/material.json' if kind=='materials' else ident+'.json'),d)
        chart_path=stage/'materials'/pixel_id/'basecolor.png';chart_path.parent.mkdir(parents=True,exist_ok=True);chart_path.write_bytes(chart_bytes)
        put(stage/'retired.json',retired);put(stage/'registry.json',{'schema':'wx.registry/2.0','version':'3.10.0','records':registry})
        put(stage/'foundation.json',collection);put(stage/'worlds.json',worlds);put(stage/'aliases.json',aliases)
        put(stage/'dependency-graph.json',{'schema':'wx.dependency-graph/1.0','nodes':graph})
        put(stage/'curation.json',curation)
        put(stage/'game-expansion.json',game);put(stage/'l3.json',l3);put(stage/'l4.json',l4);put(stage/'l2.json',l2);put(stage/'l1.json',l1);put(stage/'expansion.json',expansion);put(stage/'interfaces.json',{'schema':'wx.interfaces/1.0','interfaces':INTERFACES})
        index={'schema':'wx.generated-index/1.0','version':'3.10.0','files':snapshots(stage),'author_override_files':overrides}
        if backup.exists():raise ValueError('Unresolved .library-backup; inspect before rebuilding')
        # Library plus companion manifests form one recoverable transaction.
        old_companions={p:p.read_bytes() if p.exists() else None for p in (R/'tool.manifest.json',output)}
        had_library=(R/'library').exists()
        if had_library:os.replace(R/'library',backup)
        try:
            os.replace(stage,R/'library')
            put(R/'tool.manifest.json',manifest);put(output,index)
        except BaseException:
            if (R/'library').exists():shutil.rmtree(R/'library')
            if had_library and backup.exists():os.replace(backup,R/'library')
            for p,b in old_companions.items():
                if b is None:p.unlink(missing_ok=True)
                else:p.write_bytes(b)
            raise
        if backup.exists():shutil.rmtree(backup)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return manifest

def rebuild(discard=False):
    """Exclusive writer guard, including validation and manifest commit."""
    lock=R/'authoring/.rebuild-lock'
    try:lock.mkdir()
    except FileExistsError:raise ValueError('Rebuild writer lock exists. Another build may be active; inspect authoring/.rebuild-lock before removing a stale lock.')
    try:
        (lock/'owner.json').write_text(json.dumps({'pid':os.getpid(),'operation':'rebuild-library'}))
        return _rebuild(discard)
    finally:
        shutil.rmtree(lock)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--overwrite',action='store_true');ap.add_argument('--discard-generated',action='store_true');ap.add_argument('--thumbnails',action='store_true');args=ap.parse_args()
    if not args.overwrite:ap.error('Use --overwrite; generated edits remain protected unless --discard-generated')
    try:manifest=rebuild(args.discard_generated)
    except (ValueError,KeyError) as e:ap.exit(2,str(e)+'\n')
    print(json.dumps(manifest['library'],ensure_ascii=False,indent=2),flush=True)
    if args.thumbnails:subprocess.run([sys.executable,str(R/'tools/game410_thumbnails.py')],cwd=R,check=True)
