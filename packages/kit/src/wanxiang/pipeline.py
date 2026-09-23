from __future__ import annotations
from .paths import code_path, WORKSPACE_ROOT
import copy,os,time,json,shutil,uuid
from pathlib import Path
from contextlib import contextmanager
import numpy as np
from .compiler import compile_spec,PROFILES
from .operators import execute
from .ir import AssetIR,Mesh
from .glb import export_glb,read_glb,export_gltf
from .materials import load_material,request_material
from .validation import inspect_asset
from .util import ROOT,digest,sha256,write_json,read_json,rng_for,file_info,atomic_bytes,safe_id
from .errors import WXError

DEFAULT_WORKSPACE=WORKSPACE_ROOT/'workspaces/default'

def workspace_path(path=None):
    w=Path(path or DEFAULT_WORKSPACE).resolve();w.mkdir(parents=True,exist_ok=True);return w

@contextmanager
def run_lock(run):
    lock=run/'.build.lock'
    if lock.exists():
        try:pid=int(lock.read_text());os.kill(pid,0)
        except (ProcessLookupError,ValueError):lock.unlink(missing_ok=True)
        else:raise WXError('INPUT_INVALID','Run is already being built by a live process',details={'pid':pid})
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:yield
    finally:lock.unlink(missing_ok=True)

def build(spec,workspace=None,out=None,review=True,resume=False,plan=None):
    start=time.perf_counter();w=workspace_path(workspace);plan=plan or compile_spec(spec);s=plan['spec']
    raw=Path(out) if out else w/'runs'/safe_id(s['id'])
    if raw.is_symlink():raise WXError('PATH_UNSAFE','Run path cannot be a symlink')
    run=raw.resolve()
    run.mkdir(parents=True,exist_ok=True)
    if run.is_symlink():raise WXError('PATH_UNSAFE','Run path cannot be a symlink')
    if (run/'job.json').exists():
        old=read_json(run/'job.json')
        if old.get('plan_hash')!=plan['plan_hash']:raise WXError('INPUT_INVALID','Run already contains a different spec; use revise or a new output directory')
    if resume:(run/'cancel.json').unlink(missing_ok=True)
    job={'schema':'wx.job/1.0','id':s['id'],'state':'building','plan_hash':plan['plan_hash'],'spec':s,'workspace':str(w),'run':str(run),'completed':[],'node_log':[]}
    def checkpoint(state,step=None):
        job['state']=state
        if step and step not in job['completed']:job['completed'].append(step)
        job['elapsed_seconds']=round(time.perf_counter()-start,3);write_json(run/'job.json',job)
        if (run/'cancel.json').exists():raise WXError('CANCELLED','Local job cancelled; host requests are not cancelled')
        if time.perf_counter()-start>s['budgets']['seconds']:raise WXError('BUDGET_EXCEEDED','Wall time exceeded configured budget')
    with run_lock(run):
        try:
            checkpoint('building');write_json(run/'source/spec.json',s);write_json(run/'source/recipe.json',plan['recipe']);write_json(run/'source/plan.json',plan);write_json(run/'source/dependencies.lock.json',plan['lock'])
            for request in s.get('host_requests',[]):
                request_material(w,request['id'],request['prompt'],request.get('semantic','stone'),request.get('size',1024))
            node_outputs={};keys={}
            for node in plan['nodes']:
                checkpoint('building');id=node['id'];params=node['params'];input_keys={k:keys[v['$node']] for k,v in node['inputs'].items()}
                seed=int(rng_for(s['seed'],id).integers(0,2**32-1));key=digest({'operator':node['operator'],'version':node['operator_version'],'params':params,'seed':seed,'inputs':input_keys,'implementation':plan['lock']['implementation_sha256'],'deps':plan['lock']['dependencies']})
                cache=w/'cache'/key;cached=False;output=None
                if (cache/'complete.json').exists():
                    try:
                        info=read_json(cache/'complete.json')
                        if info['type']=='AssetIR':output=AssetIR.load(cache)
                        else:
                            if sha256(cache/'value.json')!=info['sha256']:raise ValueError('Cache hash mismatch')
                            output=read_json(cache/'value.json')
                        cached=True
                    except Exception:output=None
                elapsed=time.perf_counter()
                if output is None:
                    inputs={k:node_outputs[v['$node']] for k,v in node['inputs'].items()}
                    # Reject known multiplicative explosions before allocating copies.
                    source_tri=sum(sum(len(m.faces) for m in ir.meshes.values()) for ir in inputs.values() if isinstance(ir,AssetIR))
                    if node['operator']=='assembly.array':source_tri*=params['count']
                    if source_tri>s['budgets']['triangles']:raise WXError('BUDGET_EXCEEDED','Input expansion exceeds the triangle budget',node=id)
                    try:output=execute(node['operator'],params,seed,inputs)
                    except WXError as e:e.node=id;raise
                    except Exception as e:raise WXError('GEOMETRY_INVALID',str(e),node=id) from e
                    temp=w/'cache'/('.tmp-'+uuid.uuid4().hex);temp.mkdir(parents=True,exist_ok=True)
                    if isinstance(output,AssetIR):
                        count=sum(len(m.faces) for m in output.meshes.values())
                        if count>s['budgets']['triangles']:raise WXError('BUDGET_EXCEEDED','Node exceeds triangle budget',node=id,details={'triangles':count})
                        output.save(temp);write_json(temp/'complete.json',{'type':'AssetIR','key':key})
                    else:write_json(temp/'value.json',output);write_json(temp/'complete.json',{'type':'Skeleton','key':key,'sha256':sha256(temp/'value.json')})
                    import fcntl
                    guard=w/'cache'/('.guard-'+key)
                    with open(guard,'a') as fh:
                        fcntl.flock(fh,fcntl.LOCK_EX)
                        if cache.exists() and (cache/'complete.json').exists():
                            # Another writer may have completed the same immutable key.
                            # Revalidate it before choosing to reuse rather than replace.
                            try:
                                ci=read_json(cache/'complete.json')
                                if ci['type']=='AssetIR':AssetIR.load(cache)
                                elif sha256(cache/'value.json')!=ci['sha256']:raise ValueError('corrupt cache')
                                shutil.rmtree(temp)
                            except Exception:
                                shutil.rmtree(cache);os.replace(temp,cache)
                        else:
                            if cache.exists():shutil.rmtree(cache)
                            os.replace(temp,cache)
                        fcntl.flock(fh,fcntl.LOCK_UN)
                node_outputs[id]=output;keys[id]=key;job['node_log'].append({'node':id,'operator':node['operator'],'cache_hit':cached,'key':key,'seconds':round(time.perf_counter()-elapsed,4)})
                checkpoint('building',f'node:{id}')
            asset=AssetIR()
            for id in plan['outputs']:asset.extend(node_outputs[id],id+'_')
            # Stable sockets come from the recipe or explicit component origin.
            if plan['recipe'].get('socket_template'):
                sock=plan['recipe']['socket_template'];asset.socket(sock['id'],asset.nodes[0]['id'],sock['position'],sock['axis'],sock['interface'])
            asset.metadata={'asset_id':s['id'],'recipe_id':plan['recipe']['id'],'recipe_version':plan['recipe']['version'],'seed':s['seed'],'style':s['style'],'profile':s['profile'],'plan_hash':plan['plan_hash'],'assembly_method':'semantic intersecting_parts unless explicitly sdf_fused','user_metadata':s['metadata']}
            asset.save(run/'intermediate');checkpoint('building','geometry')
            materials={};waiting=[];bindings={}
            for slot in sorted({n['material'] for n in asset.nodes if n.get('mesh')}):
                ref=s['materials'].get(slot,slot)
                if not isinstance(ref,str):raise WXError('RECIPE_INVALID','Material bindings must be material IDs or host:<request-id>')
                if ref.startswith('host:'):
                    id=safe_id(ref[5:]);reqpath=w/'host_requests'/f'{id}.json';req=read_json(reqpath) if reqpath.exists() else None
                    if req and req.get('status')=='ready':material=load_material(req['receipt']['material_id'],w,s['style'])
                    else:
                        waiting.append({'id':id,'request_file':str(reqpath),'status':'waiting_host'});material=load_material(slot,w,s['style']);material['placeholder']=True
                else:material=load_material(safe_id(ref),w,s['style'])
                materials[slot]=material;bindings[slot]={k:v for k,v in material.items() if k!='images'}
            write_json(run/'source/material-bindings.json',bindings);checkpoint('building','materials' if not waiting else 'placeholder_materials')
            glb=run/'release/asset.glb';export_glb(asset,materials,glb);checkpoint('inspecting','export')
            report=inspect_asset(glb,expected=asset,budgets=s['budgets']);checkpoint('inspecting','glb_reread')
            if review:
                from .render import multi_view
                multi_view(glb,run/'review');report['evidence']['cpu_preview']=True;checkpoint('inspecting','cpu_preview')
            write_json(run/'review/inspection.json',report)
            job['inspection']={k:report[k] for k in ['passed','triangles','vertices','nodes','materials','textures','evidence']};job['artifacts']=[file_info(glb)];job['waiting_host']=waiting;job['cache_hits']=sum(n['cache_hit'] for n in job['node_log']);job['node_executions']=len(job['node_log'])-job['cache_hits']
            state='waiting_host' if waiting else ('ready' if report['passed'] else 'needs_revision');checkpoint(state,'inspection')
            if review:
                from .viewer import create_viewer
                create_viewer([run],run/'review/index.html',title=f"{plan['recipe']['name']} · 资产审查")
                job['artifacts'].append(file_info(run/'review/index.html'));checkpoint(state,'html_review')
            return job
        except WXError as e:
            job.update(state='cancelled' if e.code=='CANCELLED' else 'budget_blocked' if e.code=='BUDGET_EXCEEDED' else 'failed',error=e.to_dict(),elapsed_seconds=round(time.perf_counter()-start,3));write_json(run/'job.json',job);raise
        except Exception as e:
            job.update(state='failed',error={'code':'INTERNAL_ERROR','message':str(e)});write_json(run/'job.json',job);raise

def run_workspace(run,explicit=None):
    """Derive workspace from actual on-disk location, never from a stale absolute receipt."""
    if explicit:return workspace_path(explicit)
    path=Path(run).resolve()
    for parent in path.parents:
        if parent.name=='runs':return workspace_path(parent.parent)
    return workspace_path()

def resume_run(run,review=True,workspace=None):
    job=read_json(Path(run)/'job.json')
    from .runtime import guarded_build
    return guarded_build(job['spec'],run_workspace(run,workspace),run,review,resume=True)

def revise(run,patch,workspace=None,out=None,review=True):
    run=Path(run);job=read_json(run/'job.json');old=copy.deepcopy(job['spec']);spec=copy.deepcopy(old)
    if not isinstance(patch,dict) or set(patch)-{'params','materials','style','profile','metadata','quality'}:raise WXError('RECIPE_INVALID','Patch supports params/materials/style/profile/metadata/quality only')
    for k,v in patch.items():
        if isinstance(v,dict):spec[k].update(v)
        else:spec[k]=v
    suffix=digest(patch)[:8];spec['id']=safe_id((old['id'][:72]+'-r-'+suffix));w=run_workspace(run,workspace);dest=Path(out) if out else w/'runs'/spec['id']
    result=build(spec,w,dest,review);write_json(dest/'source/revision.json',{'parent':str(run),'patch':patch,'old_plan_hash':job['plan_hash']});return result

def batch(jobs,workspace=None,concurrency=1,review=True,resume=True):
    w=workspace_path(workspace)
    if not 1<=concurrency<=4:raise WXError('BUDGET_EXCEEDED','Batch concurrency must be 1..4')
    def one(spec):
        try:
            normalized=compile_spec(spec)['spec'];run=w/'runs'/normalized['id']
            if resume and (run/'job.json').exists():
                old=read_json(run/'job.json');release=run/'release/asset.glb'
                if old.get('state')=='ready' and old.get('plan_hash')==compile_spec(spec)['plan_hash'] and release.exists() and old.get('artifacts',[{}])[0].get('sha256')==sha256(release):return {'id':normalized['id'],'state':'ready','resumed_from_complete':True,'run':str(run)}
            from .runtime import guarded_build
            job=guarded_build(spec,w,review=review,resume=resume);return {'id':job['id'],'state':job['state'],'run':job['run'],'cache_hits':job['cache_hits']}
        except Exception as e:return {'id':spec.get('id',spec.get('recipe')),'state':'failed','error':e.to_dict() if isinstance(e,WXError) else str(e)}
    if concurrency==1:results=[one(s) for s in jobs]
    else:
        # Bounded threads; per-key filesystem locks protect immutable node-cache publication.
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=concurrency) as pool:results=list(pool.map(one,jobs))
    record={'schema':'wx.batch/1.0','results':results,'counts':{s:sum(x['state']==s for x in results) for s in ['ready','failed','waiting_host','cancelled']}}
    write_json(w/'last_batch.json',record);return record

def lod(run,levels=(.6,.3),review=True):
    root=Path(run);job=read_json(root/'job.json');results=[]
    if not levels or len(levels)>4 or any(not .25<=float(q)<1 for q in levels):raise WXError('INPUT_INVALID','LOD requires 1..4 quality ratios in [0.25,1)')
    for i,q in enumerate(levels,1):
        spec=copy.deepcopy(job['spec']);spec.update(id=spec['id'][:76]+f'-lod{i}',quality=float(q),profile='lod1' if i==1 else 'lod2');r=build(spec,run_workspace(root),root/'lods'/f'lod{i}',review)
        r['reduction']=1-r['inspection']['triangles']/job['inspection']['triangles'];results.append(r)
    write_json(root/'lods/lods.json',[{'run':r['run'],'triangles':r['inspection']['triangles'],'reduction':r['reduction']} for r in results]);return results

def collision(run,kind='box'):
    from . import geometry as g
    from .ir import transform
    root=Path(run);a,m,d=read_glb(root/'release/asset.glb');bounds=a.bounds();size=np.ptp(bounds,axis=0);center=bounds.mean(0)
    if kind=='box':mesh=g.box(np.maximum(size,.02)).transformed(transform(center))
    elif kind=='hull':
        import trimesh
        w=a.world_matrices();vs=np.vstack([a.meshes[n['mesh']].transformed(w[n['id']]).vertices for n in a.nodes if n.get('mesh')]);h=trimesh.convex.convex_hull(vs);mesh=Mesh(h.vertices,h.faces)
    else:raise WXError('INPUT_INVALID','Collision supports box or hull')
    col=AssetIR();col.add('collision',mesh,'collision',role='collision');col.metadata={'collision_kind':kind,'physics_binding':'engine adapter required','limitation':'Convex proxy fills concave openings; not suitable for walkable arches/bridges without compound proxies.'}
    out=root/'release/collision.glb';export_glb(col,{'collision':{'baseColorFactor':[.25,.8,.62,1],'roughnessFactor':1,'images':{}}},out);write_json(root/'release/collision.json',col.metadata);return file_info(out)

def export_format(run,out,format='glb'):
    run=Path(run);source=run/'release/asset.glb';out=Path(out)
    if format=='glb':atomic_bytes(out,source.read_bytes());return [out]
    if format=='gltf':return export_gltf(source,out)
    if format in ('obj','ply'):
        import trimesh
        a,_,_=read_glb(source);w=a.world_matrices();meshes=[]
        for n in a.nodes:
            if n.get('mesh'):
                m=a.meshes[n['mesh']].transformed(w[n['id']]);meshes.append(trimesh.Trimesh(m.vertices,m.faces,process=False))
        merged=trimesh.util.concatenate(meshes);data=merged.export(file_type=format)
        atomic_bytes(out,data.encode() if isinstance(data,str) else data);write_json(str(out)+'.losses.json',{'losses':['PBR materials','semantic hierarchy','sockets'],'purpose':'geometry exchange only'});return [out]
    raise WXError('FORMAT_UNSUPPORTED',format)
