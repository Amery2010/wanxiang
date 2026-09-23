"""User-authorized candidate-code workflow. Resource limits are NOT a security sandbox."""
import os
from .paths import code_path, WORKSPACE_ROOT
from pathlib import Path
import ast,subprocess,sys,json,shutil
from .util import ROOT,sha256,write_json,read_json,safe_id
from .errors import WXError

def add_candidate(id,source,schema,tests):
    safe_id(id);src=Path(source)
    if src.suffix!='.py' or not src.is_file():raise WXError('INPUT_INVALID','Candidate requires a real Python source file')
    tree=ast.parse(src.read_text());functions={n.name for n in tree.body if isinstance(n,ast.FunctionDef)}
    if 'build' not in functions:raise WXError('RECIPE_INVALID','Candidate must define build(params, seed) -> AssetIR')
    path=WORKSPACE_ROOT/'operators/candidates'/id
    if path.exists():raise WXError('INPUT_INVALID','Candidate ID already exists; use a versioned ID')
    path.mkdir(parents=True);shutil.copy(src,path/'operator.py');write_json(path/'candidate.json',{'id':id,'source_sha256':sha256(path/'operator.py'),'schema':schema,'tests':tests,'status':'candidate','trusted_code_required':True});return str(path)

def test_candidate(id,allow_code=False):
    safe_id(id);p=WORKSPACE_ROOT/'operators/candidates'/id
    if not allow_code:raise WXError('INPUT_INVALID','Candidate is executable code. Explicit --allow-code is required; this is not a complete sandbox.')
    rec=read_json(p/'candidate.json')
    if sha256(p/'operator.py')!=rec['source_sha256']:raise WXError('VALIDATION_FAILED','Candidate source changed; re-register a version')
    tests=rec['tests']
    if not {'normal','boundary','negative'}<={t.get('kind') for t in tests}:raise WXError('RECIPE_INVALID','Normal, boundary and negative cases are required')
    results=[]
    for i,test in enumerate(tests):
        spec=p/f'test_{i}.json';write_json(spec,{'params':test.get('params',{}),'seed':test.get('seed',42)})
        args=[sys.executable,str(code_path('tools/candidate_worker.py')),str(p/'operator.py'),str(spec),str(p/f'test_{i}')]
        try:
            out=subprocess.run(args,capture_output=True,text=True,timeout=30,cwd=WORKSPACE_ROOT,env={**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parent.parent)+(os.pathsep+os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else '')});actual=out.returncode==0;expected=test['kind']!='negative';results.append({'kind':test['kind'],'passed':actual==expected,'stdout':out.stdout[-500:],'stderr':out.stderr[-500:]})
        except subprocess.TimeoutExpired:results.append({'kind':test['kind'],'passed':False,'error':'timeout'})
    report={'source_sha256':rec['source_sha256'],'passed':all(r['passed'] for r in results),'tests':results,'sandbox':'host execution environment; subprocess timeout only'};write_json(p/'tests.json',report);return report

def promote(id,review_file,allow_code=False):
    safe_id(id)
    if not allow_code:raise WXError('INPUT_INVALID','Promotion requires explicit trusted-code authorization')
    src=WORKSPACE_ROOT/'operators/candidates'/id;tests=read_json(src/'tests.json');review=read_json(review_file)
    if not tests['passed'] or tests['source_sha256']!=sha256(src/'operator.py'):raise WXError('VALIDATION_FAILED','Current candidate tests have not passed')
    if review.get('source_sha256')!=tests['source_sha256'] or review.get('approved') is not True or not review.get('reviewer') or not review.get('evidence_files'):raise WXError('REVIEW_INCOMPLETE','Signed-off review must identify source hash, reviewer and real evidence files')
    for f in review['evidence_files']:
        if not Path(f).is_file():raise WXError('REVIEW_INCOMPLETE',f'Review evidence missing: {f}')
    dest=WORKSPACE_ROOT/'operators/stable'/id
    if dest.exists():raise WXError('INPUT_INVALID','Stable version already exists')
    shutil.copytree(src,dest);write_json(dest/'review.json',review);r=read_json(dest/'candidate.json');r['status']='reusable';write_json(dest/'candidate.json',r);return {'id':id,'path':str(dest),'status':'reusable','automatic_execution':False,'usage':'Explicit trusted SDK import; no untrusted code is auto-imported by recipes.'}
