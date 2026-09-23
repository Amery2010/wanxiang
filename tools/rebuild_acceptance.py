"""Exercise the real authoring transaction on an isolated source copy (stdlib only)."""
from pathlib import Path
import os, sys, shutil, subprocess, tempfile, json, hashlib
R=Path(__file__).resolve().parents[1]; rows=[]
def check(name,ok,detail=None):
 rows.append({'name':name,'passed':bool(ok),**({'detail':detail} if detail is not None and not ok else {})})
 if not ok:raise AssertionError(name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='wx-rebuild-') as td:
 T=Path(td)/'source';shutil.copytree(R,T,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache','.git','.venv','node_modules','workspaces','.wx-cache','generated','exports','evidence','WX_MANIFEST.json'))
 env={**os.environ,'PYTHONPATH':str(T/'packages/kit/src'),'WX_RESOURCE_ROOT':str(T),'WX_WORKSPACE_ROOT':str(T)}
 def run(*args):return subprocess.run([sys.executable,'tools/rebuild_library.py','--overwrite',*args],cwd=T,env=env,capture_output=True,text=True,timeout=90)
 def state():return json.loads((T/'authoring/generated-index.json').read_text())['files']
 def corehash():return {str(p.relative_to(T)):sha(p) for p in (T/'library').rglob('*') if p.is_file()}
 try:
  a=run('--discard-generated');check('current author sources rebuild without old geometry',a.returncode==0,a.stderr[-1000:])
  lock=T/'authoring/.rebuild-lock';lock.mkdir();before=corehash();res=run();check('held writer lock rejects a concurrent rebuild without mutations',res.returncode==2 and before==corehash() and lock.exists());lock.rmdir()
  first=state();b=run();check('second clean rebuild is byte-identical',b.returncode==0 and first==state())
  check('canonical binary texture included in generated guard',any(k.endswith('.png') for k in first))
  part=T/'library/parts/core.human.head.json';part.write_text(part.read_text()+' ');before=corehash();res=run();check('generated JSON edits rejected without side effects',res.returncode==2 and before==corehash())
  run('--discard-generated');aliases_file=T/'library/aliases.json';aliases_file.write_text('{"sw-astronaut":"fnd-adult"}');before=corehash();res=run();check('generated alias metadata edits rejected',res.returncode==2 and before==corehash())
  run('--discard-generated');texture=T/'library/materials/mat.voxel_chart/basecolor.png';texture.write_bytes(b'not a png');before=corehash();res=run();check('generated binary tampering rejected without side effects',res.returncode==2 and before==corehash())
  run('--discard-generated');d=json.loads(part.read_text());d['name']='Persistent override acceptance';override=T/'authoring/overrides/parts/core.human.head.json';override.parent.mkdir(parents=True,exist_ok=True);override.write_text(json.dumps(d));res=run();check('persistent author override applied',res.returncode==0 and json.loads(part.read_text())['name']==d['name']);saved=state();res=run();check('override survives repeated rebuild',res.returncode==0 and saved==state())
  before=corehash();bad=T/'authoring/overrides/parts/core.invalid.json';broken=json.loads(part.read_text());broken['id']='core.invalid';broken['shape_params']['components']=[{'part':'missing.component'}];bad.write_text(json.dumps(broken));res=run();check('missing dependency aborts before commit',res.returncode==2 and before==corehash());bad.unlink()
  # Authoring-only restore: remove all generated library bytes deliberately.
  shutil.rmtree(T/'library');res=run('--discard-generated');check('author sources restore a missing library',res.returncode==0 and saved==state())
  aliases=json.loads((T/'library/aliases.json').read_text());retired=json.loads((T/'library/retired.json').read_text())['entries'];check('all 731 retired IDs remain metadata only',len(retired)==731 and aliases=={} and all(not(T/'library'/('parts' if r['kind']=='part' else 'assemblies')/(r['id']+'.json')).exists() for r in retired))
  before=corehash();bad=T/'authoring/overrides/parts/body.head.json';broken=json.loads(part.read_text());broken['id']='body.head';bad.write_text(json.dumps(broken));res=run();check('retired ID cannot be resurrected by an override',res.returncode==2 and before==corehash());bad.unlink()
  check('no historical source geometry is required to rebuild',not(T/'authoring/baseline-v17.json').exists() and not(T/'authoring/baseline-assets').exists())
  # Inject a companion manifest I/O failure AFTER directory swap and verify rollback.
  before=corehash();pre_companion={p:sha(T/p) for p in ('tool.manifest.json','authoring/generated-index.json')}
  code="""import sys;sys.path.insert(0,'tools');import rebuild_library as r
original=r.put
def fail(p,d):
 if p==r.R/'tool.manifest.json':raise OSError('injected manifest write error')
 return original(p,d)
r.put=fail
try:r.rebuild()
except OSError:sys.exit(37)
sys.exit(1)
"""
  res=subprocess.run([sys.executable,'-c',code],cwd=T,env=env,capture_output=True,text=True,timeout=90)
  check('post-swap failure restores library and companion manifests',res.returncode==37 and before==corehash() and pre_companion=={p:sha(T/p) for p in pre_companion})
  check('no orphan staging or backup after rollback',not list(T.glob('.library-stage-*')) and not (T/'.library-backup').exists())
 except Exception as ex:rows.append({'name':'unexpected','passed':False,'detail':str(ex)})
result={'version':'3.10.0','isolation':'temporary source copy; delivered project untouched','checks':rows,'passed':sum(x['passed'] for x in rows),'failed':sum(not x['passed'] for x in rows)}
out=R/'generated/verification/rebuild-acceptance.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['failed']))
