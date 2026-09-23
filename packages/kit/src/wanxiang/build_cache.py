"""Verified content-addressed build cache, bounded LRU, disposable and local.

The dependency key includes author sources, semantic definitions, parameters,
style, materials, motions, export mode and the shared kernel. No cache entry is
an author input. Publication is atomic; a disk/quota failure cannot invalidate
an otherwise successful uncached build.
"""
from __future__ import annotations
from pathlib import Path
import copy,hashlib,json,os,re,shutil,tempfile
from .util import ROOT,write_json,digest
from .errors import WXError
from .paths import code_path, runtime_code_files, PACKAGE_ROOT, SOURCE_ROOT, WORKSPACE_ROOT
SCHEMA='wx.asset-build-key/1.0'
BUDGET=256*1024*1024

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def canonical(value):
    if isinstance(value,dict):return {k:canonical(v) for k,v in sorted(value.items())}
    if isinstance(value,list):return [canonical(v) for v in value]
    if isinstance(value,float) and value.is_integer():return int(value)
    return value

def encoded(value):return json.dumps(canonical(value),ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def sha(data):return hashlib.sha256(data).hexdigest()
def home():return Path(os.environ.get('WX_CACHE_DIR',str(WORKSPACE_ROOT/'.wx-cache'))).expanduser().resolve()
def engine_info(root=ROOT):
    if Path(root).resolve() != ROOT.resolve():
        paths = [*root.joinpath('packages/runtime/dist/compat').rglob('*.js'), *root.joinpath('packages/runtime/dist/compat').rglob('*.cjs'), *root.joinpath('packages/runtime/dist/compat').rglob('*.mjs'), *root.joinpath('packages/runtime/dist/compat').rglob('*.json'), *root.joinpath('packages/kit/src/wanxiang').glob('*.py'), *root.joinpath('apps/studio/artifacts').glob('*.js')]
        return sha(encoded({str(p.relative_to(root)):sha(p.read_bytes()) for p in sorted(paths) if 'node_modules' not in p.parts}))
    paths = {f'wanxiang/{p.name}': p for p in PACKAGE_ROOT.glob('*.py')}
    paths.update(runtime_code_files())
    paths['studio/app.js'] = code_path('web/app.js')
    return sha(encoded({name: sha(path.read_bytes()) for name, path in sorted(paths.items())}))
def source_info(root=ROOT):
    paths=[]
    author_root = SOURCE_ROOT if Path(root).resolve() == ROOT.resolve() else root
    if author_root is not None:
        paths=[author_root/'tools/author_foundation.py',author_root/'tools/rebuild_library.py']
    for name in ['foundation','worlds','frontiers','refinement','expansion','l1_expansion','l2_expansion']:
        if author_root is not None:paths.extend(author_root.joinpath('tools',name).glob('*.py'))
    paths.extend(root.joinpath('authoring/overrides').rglob('*.json'))
    return sha(encoded({(str(p.relative_to(SOURCE_ROOT)) if SOURCE_ROOT and p.is_relative_to(SOURCE_ROOT) else str(p.relative_to(root))):sha(p.read_bytes()) for p in sorted(paths) if p.is_file()}))
def build_context(root=ROOT):
    mats={}
    for p in sorted((root/'library/materials').glob('*/material.json')):
        d=read(p);mats[p.parent.name]={'definition':d,'textures':{k:sha((p.parent/v['file']).read_bytes()) for k,v in d.get('channels',{}).items() if v.get('file') and (p.parent/v['file']).is_file()}}
    return {'kernel':engine_info(root),'authors':source_info(root),'materials':sha(encoded(mats)),'exporter':'wx-python-glb-3.0','schema':SCHEMA}
def dependency_closure(spec,root=ROOT):
    out={};visiting=set()
    def add(kind,ident):
        if not isinstance(ident,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+',ident) or '..' in ident:raise WXError('RECIPE_INVALID','Unsafe cache dependency')
        key=kind+':'+ident
        if key in visiting:raise WXError('RECIPE_INVALID','Cyclic cache dependency: '+ident)
        if key in out:return
        file=root/'library'/('parts' if kind=='part' else 'assemblies')/(ident+'.json')
        if not file.exists():out[key]={'missing':True};return
        visiting.add(key);d=read(file);out[key]=d
        children=d.get('shape_params',{}).get('components',[]) if kind=='part' else d.get('instances',[])
        for c in children:add('part' if 'part' in c else 'assembly',c.get('part') or c.get('assembly'))
        motion=root/'library/motions'/(ident+'.json')
        if motion.exists():out['motion:'+ident]=read(motion)
        visiting.remove(key)
    if spec.get('part'):add('part',spec['part'])
    for c in spec.get('instances',[]):add('part' if 'part' in c else 'assembly',c.get('part') or c.get('assembly'))
    motion=root/'library/motions'/((spec.get('id') or spec.get('part'))+'.json')
    if motion.exists():out['motion:'+motion.stem]=read(motion)
    return out

def key_for(spec,mode='author',review=False,root=ROOT):
    body={'schema':SCHEMA,'context':build_context(root),'sources':dependency_closure(spec,root),'spec':spec,'mode':mode,'review':review}
    return sha(encoded(body)),body

def _entries():
    folder=home()/'builds'
    if not folder.is_dir():return []
    return [p for p in folder.iterdir() if p.is_dir() and not p.is_symlink() and re.fullmatch('[a-f0-9]{64}',p.name)]
def stats():
    entries=[]
    try:
        for p in _entries():
            size=sum(x.stat().st_size for x in p.rglob('*') if x.is_file())
            try:
                d=read(p/'cache.json');entries.append({'key':p.name,'asset':d.get('asset'),'bytes':size,'last_used':p.stat().st_mtime,'context':d.get('context'),'spec':d.get('spec'),'review':d.get('review',False),'mode':d.get('mode','author')})
            except (OSError,ValueError,KeyError):entries.append({'key':p.name,'bytes':size,'corrupt':True,'last_used':0})
        return {'schema':'wx.cache-stats/1.0','path':str(home()),'entries':entries,'count':len(entries),'bytes':sum(x['bytes'] for x in entries),'budget_bytes':BUDGET,'available':True}
    except OSError:return {'schema':'wx.cache-stats/1.0','path':str(home()),'entries':[],'count':0,'bytes':0,'budget_bytes':BUDGET,'available':False}
def clean(stale=False,asset=None):
    data=stats();removed=[]
    for e in data['entries']:
        if asset and e.get('asset')!=asset:continue
        if stale and not e.get('corrupt'):
            try:
                current,_=key_for(e['spec'],mode=e['mode'],review=e['review'])
                if current==e['key']:continue
            except (ValueError,KeyError,OSError,WXError):pass
        path=home()/'builds'/e['key']
        try:shutil.rmtree(path);removed.append(e['key'])
        except OSError:pass
    return {'removed':len(removed),'keys':removed,'remaining':stats()['count']}
def prune():
    data=stats();total=data['bytes']
    for e in sorted(data['entries'],key=lambda x:x['last_used']):
        if total<=BUDGET:break
        try:shutil.rmtree(home()/'builds'/e['key']);total-=e['bytes']
        except OSError:pass

def _valid(entry):
    try:
        d=read(entry/'cache.json')
        if d.get('key')!=entry.name:return None
        for rel,sig in d['files'].items():
            p=(entry/'payload'/rel).resolve()
            if not p.is_relative_to((entry/'payload').resolve()) or not p.is_file() or sha(p.read_bytes())!=sig:return None
        if 'release/asset.glb' not in d['files']:return None
        return d
    except (KeyError,ValueError,OSError):return None

def cached_build(spec,out,review,build):
    out=Path(out);key,body=key_for(spec,review=review);entry=home()/'builds'/key
    if (out/'source/kit-spec.json').exists() and digest(read(out/'source/kit-spec.json'))!=digest(spec):
        raise WXError('INPUT_INVALID','Output belongs to a different specification; choose a new run directory')
    meta=_valid(entry)
    if meta:
        # Cache reads are also non-essential: fall back when policy denies access.
        try:
            out.mkdir(parents=True,exist_ok=True);shutil.copytree(entry/'payload',out,dirs_exist_ok=True)
            try:os.utime(entry,None)
            except OSError:pass
            result={**meta['result'],'id':out.name,'run':str(out),'glb':str(out/'release/asset.glb'),'cache_hit':True,'build_key':key}
            job=read(out/'job.json');job.update(id=out.name,cache_hits=1);write_json(out/'job.json',job)
            return result
        except OSError:pass
    result=build();result.update(cache_hit=False,build_key=key)
    if not result.get('passed'):return result
    stage=None
    try:
        if entry.exists():shutil.rmtree(entry)
        parent=entry.parent;parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.pending-',dir=parent))
        shutil.copytree(out,stage/'payload')
        files={str(p.relative_to(stage/'payload')):sha(p.read_bytes()) for p in (stage/'payload').rglob('*') if p.is_file()}
        write_json(stage/'cache.json',{'schema':'wx.build-cache/1.0','key':key,'asset':spec.get('id') or spec.get('part'),'context':body['context'],'spec':spec,'mode':'author','review':review,'files':files,'result':result})
        if not entry.exists():os.replace(stage,entry)
        prune()
    except (OSError,WXError):result['cache_warning']='Cache unavailable; valid uncached output retained.'
    finally:
        if stage and stage.exists():shutil.rmtree(stage,ignore_errors=True)
    return result
