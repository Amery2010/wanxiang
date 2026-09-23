"""Machine-first Linux CLI. All completed commands emit wx.result/1.0 JSON."""
from __future__ import annotations
from .paths import require_resources, require_source
from .paths import code_path, WORKSPACE_ROOT
import argparse,json,sys,os,subprocess,importlib.util,importlib.metadata,shutil,platform
from pathlib import Path
from . import __version__
from .errors import WXError,EXIT_CODES
from .util import ROOT,read_json,write_json,result,canonical,file_info


def parser():
    p=argparse.ArgumentParser(prog='wx',description='万象工坊 3D · LLM-first offline asset production')
    p.add_argument('--version',action='version',version=f'Wanxiang3D {__version__}')
    # Common flags are accepted anywhere by main(), without ambiguous argparse inheritance.
    sub=p.add_subparsers(dest='command',required=True)
    def cmd(name,help):return sub.add_parser(name,help=help)
    def specopts(q):
        q.add_argument('--spec');q.add_argument('--recipe');q.add_argument('--params',default='{}');q.add_argument('--id');q.add_argument('--seed',type=int,default=314159);q.add_argument('--profile',default='standard');q.add_argument('--style',default='natural');q.add_argument('--preset',default='default')
    def runopts(q):q.add_argument('--run',required=True)
    def assetopts(q):q.add_argument('--run');q.add_argument('--asset')
    q=cmd('doctor','Discover actual available capabilities');q.add_argument('--deep',action='store_true')
    cmd('capabilities','List registered operations and implemented library counts')
    q=cmd('operators','List/describe typed modeling operators');q.add_argument('action',choices=['list','describe'],nargs='?',default='list');q.add_argument('name',nargs='?')
    q=cmd('search','Search recipes, components, styles, materials and patterns');q.add_argument('query',nargs='?',default='');q.add_argument('--kind',choices=['recipe','component','material','style','pattern','part','assembly']);q.add_argument('--limit',type=int,default=20)
    q=cmd('catalog','Browse or rebuild the local catalog index');q.add_argument('action',choices=['list','reindex'],nargs='?',default='list');q.add_argument('--kind')
    q=cmd('recipe','Read or validate an executable recipe');q.add_argument('action',choices=['show','validate']);q.add_argument('name')
    q=cmd('plan','Compile and validate a build plan without executing geometry');specopts(q);q.add_argument('--out')
    q=cmd('build','Build real geometry, export, re-read, inspect and preview');specopts(q);q.add_argument('--plan');q.add_argument('--out');q.add_argument('--no-review',action='store_true')
    q=cmd('batch','Build/recover a JSON or JSONL batch');q.add_argument('--jobs',required=True);q.add_argument('--concurrency',type=int,default=1);q.add_argument('--no-review',action='store_true');q.add_argument('--no-resume',action='store_true')
    for name in ['resume','cancel']:
        q=cmd(name,f'{name} a durable run');runopts(q)
        if name=='resume':q.add_argument('--no-review',action='store_true')
    q=cmd('inspect','Inspect actual exported bytes, transforms, budgets and hierarchy');assetopts(q);q.add_argument('--report');q.add_argument('--profile',default='headless');q.add_argument('--full',action='store_true')
    q=cmd('render-cpu','Render actual GLB without WebGL');assetopts(q);q.add_argument('--out',required=True);q.add_argument('--size',type=int,default=640);q.add_argument('--azimuth',type=float,default=40);q.add_argument('--elevation',type=float,default=25);q.add_argument('--wire',action='store_true')
    q=cmd('review','Create self-contained HTML for a real run');runopts(q);q.add_argument('--out');q.add_argument('--format',default='html',choices=['html']);q.add_argument('--self-contained',action='store_true')
    for name in ['gallery','compare']:
        q=cmd(name,'Create an offline HTML asset browser');q.add_argument('--runs',nargs='*');q.add_argument('--out',required=True);q.add_argument('--title',default='万象工坊 3D · 资产工坊')
    q=cmd('revise','Create an immutable revision and reuse unchanged nodes');runopts(q);q.add_argument('--patch',required=True);q.add_argument('--out');q.add_argument('--no-review',action='store_true')
    q=cmd('material','Material catalog and host image handshake');m=q.add_subparsers(dest='action',required=True)
    m.add_parser('list')
    r=m.add_parser('request');r.add_argument('--id',required=True);r.add_argument('--prompt',required=True);r.add_argument('--semantic',default='stone');r.add_argument('--size',type=int,default=1024)
    r=m.add_parser('ingest');r.add_argument('--id',required=True);r.add_argument('--image',required=True);r.add_argument('--source',default='user_provided');r.add_argument('--seamless',action='store_true')
    r=m.add_parser('validate');r.add_argument('--image',required=True)
    r=m.add_parser('atlas');r.add_argument('--images',nargs='+',required=True);r.add_argument('--out',required=True);r.add_argument('--size',type=int,default=1024);r.add_argument('--padding',type=int,default=8)
    q=cmd('lod','Rebuild parametric quality levels (not generic retopology)');runopts(q);q.add_argument('--levels',default='0.6,0.3');q.add_argument('--no-review',action='store_true')
    q=cmd('collision','Export an explicit convex collision proxy');runopts(q);q.add_argument('--kind',choices=['box','hull'],default='box')
    q=cmd('turntable','Render genuine 3D camera angles to a fixed-scale sprite atlas');assetopts(q);q.add_argument('--out',required=True);q.add_argument('--frames',type=int,default=32);q.add_argument('--size',type=int,default=192);q.add_argument('--elevation',type=float,default=30)
    q=cmd('export','Export GLB/glTF, or geometry-only OBJ/PLY');runopts(q);q.add_argument('--out',required=True);q.add_argument('--format',choices=['glb','gltf','obj','ply'],default='glb')
    q=cmd('package','Build verified independent ZIP packages');q.add_argument('--run');q.add_argument('--folder');q.add_argument('--out',required=True);q.add_argument('--max-part-bytes',type=int,default=300_000_000)
    q=cmd('verify','Verify a closed manifest and actual package hashes');q.add_argument('path')
    q=cmd('candidate','Register and test trusted extension code');m=q.add_subparsers(dest='action',required=True)
    r=m.add_parser('add');r.add_argument('--id',required=True);r.add_argument('--source',required=True);r.add_argument('--schema',required=True);r.add_argument('--tests',required=True)
    r=m.add_parser('test');r.add_argument('--id',required=True);r.add_argument('--allow-code',action='store_true')
    q=cmd('promote','Promote tested code only with explicit review evidence');q.add_argument('--id',required=True);q.add_argument('--review',required=True);q.add_argument('--allow-code',action='store_true')
    q=cmd('project','Dry-run or explicitly admit an asset into a project');m=q.add_subparsers(dest='action',required=True)
    r=m.add_parser('admit');r.add_argument('--asset',required=True);r.add_argument('--project',required=True);r.add_argument('--destination',required=True);r.add_argument('--apply',action='store_true');r.add_argument('--replace',action='store_true')
    r=m.add_parser('rollback');r.add_argument('--receipt',required=True)
    q=cmd('tests','Run bundled source tests');q.add_argument('action',choices=['run']);q.add_argument('--path',default=str(ROOT/'tests'))
    q=cmd('serve','Serve an existing viewer on loopback; no server-side execution API');q.add_argument('--dir',default=str(ROOT));q.add_argument('--port',type=int,default=8765)
    q=cmd('cache','Inspect or remove disposable on-demand build cache'); q.add_argument('action',choices=['stats','clean']); q.add_argument('--stale',action='store_true'); q.add_argument('--asset')
    from .kit_cli import add_parser
    add_parser(sub)
    return p


def input_json(value):
    if value is None:return None
    if value.lstrip().startswith(('{','[')):
        try:return json.loads(value)
        except Exception as e:raise WXError('RECIPE_INVALID',f'Invalid inline JSON: {e}')
    return read_json(value)


def makespec(a):
    if a.spec:return read_json(a.spec)
    if not a.recipe:raise WXError('INPUT_INVALID','--spec, --recipe or --plan is required')
    s={'recipe':a.recipe,'params':input_json(a.params),'seed':a.seed,'profile':a.profile,'style':a.style,'preset':a.preset}
    if a.id:s['id']=a.id
    return s


def actual_asset(a):
    if a.asset:return Path(a.asset)
    if a.run:return Path(a.run)/'release/asset.glb'
    raise WXError('INPUT_INVALID','--asset or --run is required')


def brief(job):
    return {k:job[k] for k in ['id','state','run','elapsed_seconds','cache_hits','node_executions','inspection','waiting_host','artifacts'] if k in job}


def doctor(deep=False):
    dependencies={}
    for name in ['numpy','scipy','trimesh','scikit-image','Pillow','shapely','PyYAML','jsonschema','numba','pytest']:
        try:dependencies[name]={'available':True,'version':importlib.metadata.version(name)}
        except importlib.metadata.PackageNotFoundError:dependencies[name]={'available':False}
    node=shutil.which('node');record={'python':sys.version.split()[0],'platform':platform.platform(),'dependencies':dependencies,'node':node,'blender_required':False,'gpu_required':False,'browser_webgl':{'status':'not_tested','reason':'Doctor does not infer GPU support from executable presence'},'host_image_generation':{'status':'host_mediated','local_api':False},'offline_vendor':{'three_module':(code_path('vendor/three/build/three.module.js')).is_file(),'GLTFLoader':(code_path('vendor/three/examples/jsm/loaders/GLTFLoader.js')).is_file(),'GLTFExporter':(code_path('vendor/three/examples/jsm/exporters/GLTFExporter.js')).is_file()},'paths':{'root':str(ROOT)}}
    if node:
        record['node_version']=subprocess.run([node,'--version'],capture_output=True,text=True,timeout=5).stdout.strip()
    if deep:
        from .ir import AssetIR
        from .geometry import box
        from .glb import export_glb
        from .validation import inspect_asset
        import tempfile
        with tempfile.TemporaryDirectory(prefix='wx-doctor-') as td:
            a=AssetIR();a.add('doctor_box',box(),'stone');out=Path(td)/'probe.glb';export_glb(a,{'stone':{'images':{},'baseColorFactor':[.5,.5,.5,1]}},out);r=inspect_asset(out,expected=a);record['glb_roundtrip']={'passed':r['passed'],'triangles':r['triangles'],'evidence':r['evidence']}
            if node:
                p=subprocess.run([node,str(code_path('workers/node/geometry.mjs'))],input=json.dumps({'op':'torus','params':{'radius':1,'tube':.2,'radialSegments':8,'tubularSegments':16},'export_path':str(Path(td)/'node.glb')}),capture_output=True,text=True,timeout=30)
                record['three_node_probe']={'passed':p.returncode==0,'error':p.stderr[-300:] if p.returncode else None}
    record['durability']={'mode':os.environ.get('WX_DURABILITY','strict'),'readback_mode_note':'Opt-in readback checks bytes but does not guarantee power-loss persistence'}
    record['shared_geometry_kernel']={'browser':True,'node_required':True,'source':'@wanxiang/runtime/src/geometry.js'}
    try:
        require_resources()
        record['resources']={'available':True,'root':str(ROOT)}
    except WXError as error:
        record['resources']={'available':False,'root':str(ROOT),'error':error.to_dict()}
    record['core_ready']=bool(node) and all(dependencies[n]['available'] for n in ['numpy','scipy','trimesh','scikit-image','Pillow','shapely','PyYAML','jsonschema'])
    return record


def dispatch(a,workspace):
    if a.command not in ("doctor", "tests", "cache", "serve", "operators"):
        require_resources()
    if a.command=="cache":
        from . import build_cache
        return build_cache.stats() if a.action=="stats" else build_cache.clean(a.stale,a.asset)
    if a.command=="kit":
        from .kit_cli import dispatch as kit_dispatch
        return kit_dispatch(a)
    from . import pipeline as pipe
    from .catalog import search,records,index,get_recipe
    from .compiler import compile_spec
    from .operators import describe,REGISTRY
    c=a.command
    if c=='doctor':return doctor(a.deep)
    if c=='capabilities':return {'version':__version__,'operators':len(REGISTRY),'recipes':len(records('recipe')),'components':len(records('component')),'granular_parts':len(records('part')),'assemblies':len(records('assembly')),'materials':len(records('material')),'styles':len(records('style')),'interfaces':['Linux CLI','Python API','bounded Node worker','self-contained HTML'],'requires_blender':False,'requires_gpu':False,'native_image_tool':'host request/ingest protocol','pipeline_evidence_levels':['built','strict_glb_reread','independent_trimesh_reread','cpu_preview','conditional_webgl','explicit_visual_review']}
    if c=='operators':
        if a.action=='describe':
            if a.name not in REGISTRY:raise WXError('INPUT_INVALID','Unknown operator name')
            return describe(a.name)
        return [describe(k) for k in REGISTRY]
    if c=='search':return search(a.query,a.kind,a.limit)
    if c=='catalog':return index(pipe.workspace_path(workspace)) if a.action=='reindex' else search('',a.kind,200)
    if c=='recipe':
        recipe,path=get_recipe(a.name)
        if a.action=='show':return recipe
        plan=compile_spec({'recipe':a.name});return {'valid':True,'path':str(path),'nodes':len(plan['nodes']),'recipe':recipe['id']}
    if c=='plan':
        plan=compile_spec(makespec(a))
        if a.out:write_json(a.out,plan);return {'plan':file_info(a.out),'plan_hash':plan['plan_hash'],'estimated':plan['estimated']}
        return plan
    if c=='build':
        plan=None
        if a.plan:
            saved=read_json(a.plan);plan=compile_spec(saved['spec'])
            if plan['plan_hash']!=saved['plan_hash']:raise WXError('VALIDATION_FAILED','Saved plan dependencies changed; explicitly re-plan')
            spec=plan['spec']
        else:spec=makespec(a)
        from .runtime import guarded_build
        return brief(guarded_build(spec,workspace,a.out,not a.no_review,plan=plan))
    if c=='batch':
        path=Path(a.jobs)
        if path.suffix=='.jsonl':jobs=[json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        else:jobs=read_json(path);jobs=jobs.get('jobs') if isinstance(jobs,dict) else jobs
        if not isinstance(jobs,list) or not 1<=len(jobs)<=512:raise WXError('BUDGET_EXCEEDED','Batch accepts 1..512 job specs')
        return pipe.batch(jobs,workspace,a.concurrency,not a.no_review,not a.no_resume)
    if c=='resume':return brief(pipe.resume_run(a.run,not a.no_review,workspace))
    if c=='cancel':
        r=Path(a.run)
        if not (r/'job.json').is_file():raise WXError('INPUT_INVALID','Run not found')
        write_json(r/'cancel.json',{'cancel':True});return {'state':'cancel_requested','run':str(r),'host_requests_cancelled':False}
    if c=='inspect':
        from .validation import inspect_asset
        r=inspect_asset(actual_asset(a))
        if a.report:write_json(a.report,r)
        if a.full:return r
        return {k:r[k] for k in ['passed','triangles','vertices','nodes','materials','textures','bounds','evidence','issues'] if k in r}
    if c=='render-cpu':
        from .render import render_cpu
        if not 64<=a.size<=2048:raise WXError('BUDGET_EXCEEDED','Render size must be 64..2048')
        return render_cpu(actual_asset(a),a.out,a.size,a.azimuth,a.elevation,wire=a.wire)
    if c in ('review','gallery','compare'):
        from .viewer import create_viewer
        if c=='review':runs=[Path(a.run)];out=a.out or str(Path(a.run)/'review/index.html');title='万象工坊 3D · 资产审查'
        else:runs=[Path(r) for r in a.runs] if a.runs else sorted((pipe.workspace_path(workspace)/'runs').glob('*'));out=a.out;title=a.title
        return create_viewer(runs,out,title)
    if c=='revise':return brief(pipe.revise(a.run,input_json(a.patch),workspace,a.out,not a.no_review))
    if c=='material':
        from .materials import request_material,ingest,inspect_texture,atlas
        w=pipe.workspace_path(workspace)
        if a.action=='list':return search('','material',200)
        if a.action=='request':return request_material(w,a.id,a.prompt,a.semantic,a.size)
        if a.action=='ingest':return ingest(w,a.id,a.image,a.source,a.seamless)
        if a.action=='validate':
            from PIL import Image
            with Image.open(a.image) as im:return inspect_texture(im)
        if a.action=='atlas':return atlas(a.images,a.out,a.padding,a.size)
    if c=='lod':return [brief(r)|{'reduction':r['reduction']} for r in pipe.lod(a.run,[float(x) for x in a.levels.split(',')],not a.no_review)]
    if c=='collision':return pipe.collision(a.run,a.kind)
    if c=='turntable':
        from .render import turntable
        if a.frames not in (4,8,16,32,64) or not 64<=a.size<=1024:raise WXError('BUDGET_EXCEEDED','Turntable limits: 4/8/16/32/64 views, 64..1024 pixels per view')
        return turntable(actual_asset(a),a.out,a.frames,a.size,a.elevation)
    if c=='export':return [file_info(p) for p in pipe.export_format(a.run,a.out,a.format)]
    if c=='package':
        from .packaging import package_folder
        if not(a.folder or a.run):raise WXError('INPUT_INVALID','--folder or --run is required')
        return package_folder(a.folder or a.run,a.out,a.max_part_bytes)
    if c=='verify':
        from .packaging import verify_package
        return verify_package(a.path)
    if c=='candidate':
        from .extensions import add_candidate,test_candidate
        return add_candidate(a.id,a.source,read_json(a.schema),read_json(a.tests)) if a.action=='add' else test_candidate(a.id,a.allow_code)
    if c=='promote':
        from .extensions import promote
        return promote(a.id,a.review,a.allow_code)
    if c=='project':
        from .adapters import admit,rollback
        return admit(a.asset,a.project,a.destination,a.apply,a.replace) if a.action=='admit' else rollback(a.receipt)
    if c=='tests':
        p=subprocess.run([sys.executable,'-m','pytest',a.path,'-q'],cwd=require_source(),capture_output=True,text=True)
        return {'passed':p.returncode==0,'returncode':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-3000:]}
    if c=='serve':
        from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
        from .util import inside
        directory=Path(a.dir).resolve()
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(directory),**kwargs)
            def translate_path(self,path):
                from urllib.parse import unquote,urlsplit
                rel=unquote(urlsplit(path).path).lstrip('/')
                try:return str(inside(directory,rel))
                except WXError:return str(directory/'__DENIED__')
        server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
        print(json.dumps(result(data={'serving':f'http://127.0.0.1:{a.port}','directory':str(directory),'execution_api':False}),ensure_ascii=False),flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.server_close()
        return {'state':'stopped'}
    raise WXError('INPUT_INVALID','Unsupported command')


def main(argv=None):
    args=list(sys.argv[1:] if argv is None else argv);workspace=None
    # Common flags may precede or follow subcommands. --json is explicit but JSON is always the default.
    for flag in ('--json','--quiet'):
        while flag in args:args.remove(flag)
    for i,x in list(enumerate(args)):
        if x.startswith('--workspace='):workspace=x.split('=',1)[1];args.pop(i);break
    if '--workspace' in args:
        i=args.index('--workspace')
        if i+1>=len(args):print(json.dumps(result('error',error={'code':'INPUT_INVALID','message':'--workspace needs a path'})));return 2
        workspace=args[i+1];del args[i:i+2]
    try:
        a=parser().parse_args(args);data=dispatch(a,workspace);status='ok'
        if isinstance(data,dict):
            if data.get('state')=='waiting_host':status='waiting_host'
            elif data.get('state') in ('needs_revision','failed','budget_blocked') or data.get('passed') is False:status='failed'
            elif data.get('counts',{}).get('failed',0):status='partial'
        print(canonical(result(status,data=data)).decode(),flush=True)
        return 7 if status=='waiting_host' else 6 if status in ('failed','partial') else 0
    except WXError as e:
        print(canonical(result('error',error=e.to_dict())).decode(),flush=True);return EXIT_CODES.get(e.code,1)
    except KeyboardInterrupt:
        print(canonical(result('error',error={'code':'CANCELLED','message':'Interrupted; durable run and caches are retained.'})).decode(),flush=True);return 130
    except Exception as e:
        if os.environ.get('WX_DEBUG'):
            import traceback;traceback.print_exc(file=sys.stderr)
        print(canonical(result('error',error={'code':'INTERNAL_ERROR','message':str(e),'type':type(e).__name__})).decode(),flush=True);return 1
