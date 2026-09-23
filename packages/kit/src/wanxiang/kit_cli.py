"""CLI surface for the granular component/assembly system."""
from pathlib import Path
import copy
from .util import ROOT,read_json,write_json,safe_id
from .errors import WXError

def add_parser(sub):
    q=sub.add_parser('kit',help='Granular parts, nested assemblies, BOM, explode, split and revisions')
    m=q.add_subparsers(dest='action',required=True)
    r=m.add_parser('list');r.add_argument('--kind',choices=['part','assembly'],default='part');r.add_argument('--query',default='');r.add_argument('--limit',type=int,default=1000)
    r.add_argument('--theme');r.add_argument('--level',type=int);r.add_argument('--interface');r.add_argument('--collision',choices=['yes','no']);r.add_argument('--lod',choices=['yes','no']);r.add_argument('--category');r.add_argument('--tag');r.add_argument('--motion',choices=['static','rigid','skinned']);r.add_argument('--max-triangles',type=int)
    r=m.add_parser('interfaces',help='List versioned metre-space connector contracts')
    r=m.add_parser('compatible',help='Dimension and edge-profile compatible default parts');r.add_argument('--part',required=True);r.add_argument('--socket',required=True);r.add_argument('--params',default='{}')
    r=m.add_parser('export-lods',help='Generate real authored geometry LODs');g=r.add_mutually_exclusive_group(required=True);g.add_argument('--part');g.add_argument('--assembly');r.add_argument('--style',choices=['lowpoly','toon'],default='lowpoly');r.add_argument('--out',required=True)
    r=m.add_parser('retired',help='Inspect retired IDs; never load legacy geometry');r.add_argument('--query',default='')
    r=m.add_parser('export-runtime',help='Safe static opaque batching with source map');r.add_argument('--assembly',required=True);r.add_argument('--out',required=True);r.add_argument('--params',default='{}')
    r=m.add_parser('show');r.add_argument('id');r.add_argument('--kind',choices=['part','assembly'],default='part')
    r=m.add_parser('build');g=r.add_mutually_exclusive_group(required=True);g.add_argument('--part');g.add_argument('--assembly');g.add_argument('--spec');r.add_argument('--style',choices=['lowpoly','toon','voxel','rounded','pixel']);r.add_argument('--params',default='{}');r.add_argument('--material');r.add_argument('--out');r.add_argument('--no-review',action='store_true');r.add_argument('--no-cache',action='store_true');r.add_argument('--lod',type=int)
    r=m.add_parser('batch');r.add_argument('--jobs');r.add_argument('--out',required=True);r.add_argument('--no-review',action='store_true');r.add_argument('--theme');r.add_argument('--category');r.add_argument('--tag');r.add_argument('--level',type=int);r.add_argument('--ids',nargs='+');r.add_argument('--style',choices=['lowpoly','toon'],default='lowpoly');r.add_argument('--changed-only',action='store_true')
    r=m.add_parser('bom');r.add_argument('--run',required=True);r.add_argument('--out')
    r=m.add_parser('split');r.add_argument('--run',required=True);r.add_argument('--out',required=True);r.add_argument('--unique',action='store_true')
    r=m.add_parser('explode');r.add_argument('--run',required=True);r.add_argument('--out',required=True);r.add_argument('--amount',type=float,default=.35);r.add_argument('--level',choices=['part','assembly'],default='part')
    r=m.add_parser('revise');r.add_argument('--run',required=True);r.add_argument('--patch',required=True);r.add_argument('--out',required=True);r.add_argument('--no-review',action='store_true')

def apply_patch(spec,patch):
    spec=copy.deepcopy(spec)
    if set(patch)-{'style','instances','add','remove','params','material'}:raise WXError('RECIPE_INVALID','Unknown kit patch field')
    if 'style' in patch:spec['style']=patch['style']
    if spec.get('schema')=='wx.part-build/1.0':
        if any(k in patch for k in ('instances','add','remove')):raise WXError('RECIPE_INVALID','Part builds have no assembly instances')
        for key in ('params','material'):
            if key in patch:spec[key]=patch[key]
        return spec
    if 'material' in patch:raise WXError('RECIPE_INVALID','Set materials on named assembly instances')
    if 'params' in patch:
        from .kit_assembly import apply_build_parameters
        spec=apply_build_parameters(spec,patch['params'])
    by={it['id']:it for it in spec['instances']}
    for id,changes in patch.get('instances',{}).items():
        if id not in by:raise WXError('RECIPE_INVALID','Patch target not present at this assembly level: '+id)
        if 'id' in changes:raise WXError('RECIPE_INVALID','Cannot change stable id in place')
        by[id].update(changes)
    remove=set(patch.get('remove',[]))
    if remove-set(by):raise WXError('RECIPE_INVALID','Removal target does not exist')
    spec['instances']=[it for it in spec['instances'] if it['id'] not in remove]+patch.get('add',[])
    return spec

def dispatch(a):
    from . import kit_assembly as K
    from .kit_parts import definition
    from .cli import input_json
    if a.action=='retired':
        from .retirement import lookup
        return {'records':lookup(a.query),'automatic_redirect':False,'geometry_shipped':False}
    if a.action=='export-runtime':
        from .runtime_export import export_runtime
        return export_runtime(a.assembly,a.out,input_json(a.params))
    if a.action=='interfaces':
        from .contracts import INTERFACES
        return {'schema':'wx.interfaces/1.0','interfaces':INTERFACES,'count':len(INTERFACES)}
    if a.action=='compatible':
        from .contracts import compatible_parts
        return compatible_parts(a.part,a.socket,input_json(a.params))
    if a.action=='export-lods':
        from .runtime_metadata import export_lods
        return export_lods(a.part or a.assembly,'part' if a.part else 'assembly',a.out,a.style)
    if a.action=='list':
        from .contracts import search
        records=search(interface=a.interface,theme=a.theme,level=a.level,collision=None if a.collision is None else a.collision=='yes',lod=None if a.lod is None else a.lod=='yes',kind=a.kind,query=a.query)
        records=[r for r in records if (not a.category or r['category']==a.category) and (not a.tag or a.tag.lower() in ' '.join(r.get('runtime',{}).get('tags',[])).lower()) and (not a.motion or r.get('runtime',{}).get('motion')==a.motion) and (not a.max_triangles or (r.get('runtime',{}).get('budget') or float('inf'))<=a.max_triangles)]
        # Keep the original catalog-list response shape for scripts.
        from .catalog import search as legacy_search
        original=legacy_search(a.query,a.kind,a.limit)
        if not any((a.interface,a.theme,a.level,a.collision,a.lod,a.category,a.tag,a.motion,a.max_triangles)):return original
        return {'count':len(records),'records':records[:a.limit]}

    if a.action=='show':return definition(a.id) if a.kind=='part' else K.get_template(a.id)
    if a.action=='build':
        s=input_json(a.spec) if a.spec else None;style=a.style or (s or {}).get('style') or (K.get_template(a.assembly).get('style','lowpoly') if a.assembly else 'lowpoly')
        if a.material:
            if not a.part:raise WXError('INPUT_INVALID','--material is for a single part; edit assembly instance materials in its JSON')
            s={'schema':'wx.part-build/1.0','id':a.part,'part':a.part,'params':input_json(a.params),'material':a.material,'style':style}
        params=input_json(a.params)
        if a.lod is not None:
            from .runtime_metadata import lod_parameters
            if not (a.part or a.assembly):raise WXError('INPUT_INVALID','--lod requires --part or --assembly')
            params={**params,**lod_parameters(a.part or a.assembly,'part' if a.part else 'assembly',a.lod)}
        if s and s.get('schema')=='wx.part-build/1.0' and a.material:s['params']=params
        return K.build(id=a.part or a.assembly,spec=s,style=style,part=bool(a.part),params=params,out=a.out,review=not a.no_review,cache=not a.no_cache)
    if a.action=='batch':
        from .batch import run_batch
        if a.jobs:jobs=input_json(a.jobs)
        else:
            if not any((a.ids,a.theme,a.category,a.tag,a.level)):raise WXError('INPUT_INVALID','Provide --jobs or an explicit catalogue filter')
            from .contracts import search
            rows=search(theme=a.theme,level=a.level)
            if a.ids:
                missing=set(a.ids)-{r['id'] for r in rows}
                if missing:raise WXError('INPUT_INVALID','IDs not found within filters: '+str(sorted(missing)))
            jobs=[{r['kind']:r['id'],'style':a.style} for r in rows if (not a.ids or r['id'] in a.ids) and (not a.category or r['category']==a.category) and (not a.tag or a.tag.lower() in ' '.join(r.get('runtime',{}).get('tags',[])).lower())]
        return run_batch(jobs,a.out,review=not a.no_review,changed_only=a.changed_only)
    if a.action=='bom':
        b=read_json(Path(a.run)/'release/bom.json')
        if a.out:write_json(a.out,b)
        return {'count':len(b),'unique_parts':len({x['part'] for x in b}),'instances':b}
    if a.action=='split':return K.split_run(a.run,a.out,a.unique)
    if a.action=='explode':
        from .ir import AssetIR
        from .glb import export_glb
        from .validation import inspect_asset
        from .render import multi_view
        asset=K.explode_asset(AssetIR.load(Path(a.run)/'intermediate'),a.amount,a.level);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
        export_glb(asset,K.materials_for(asset),out/'exploded.glb');report=inspect_asset(out/'exploded.glb',expected=asset);multi_view(out/'exploded.glb',out/'review',256);write_json(out/'inspection.json',report)
        return {'path':str(out/'exploded.glb'),'passed':report['passed'],'amount':a.amount,'level':a.level,'source_unchanged':True}
    if a.action=='revise':
        src=Path(a.run);spec=read_json(src/'source/kit-spec.json');patch=input_json(a.patch);new=apply_patch(spec,patch)
        if Path(a.out).resolve()==src.resolve():raise WXError('INPUT_INVALID','Revisions must use a new run directory')
        res=K.build(spec=new,style=new.get('style','lowpoly'),out=a.out,review=not a.no_review);write_json(Path(a.out)/'source/revision.json',{'source_spec':spec,'patch':patch});return res
