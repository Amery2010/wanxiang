"""Linux subprocess supervision for CLI/batch jobs. This is not a security sandbox."""
from __future__ import annotations
import os,signal,subprocess,sys,json,time
from pathlib import Path
from .util import ROOT,canonical,read_json,write_json
from .errors import WXError


def guarded_build(spec,workspace=None,out=None,review=True,resume=False,plan=None):
    from .compiler import compile_spec
    plan=plan or compile_spec(spec);seconds=float(plan['spec']['budgets']['seconds'])
    payload={'spec':plan['spec'],'workspace':str(workspace) if workspace else None,'out':str(out) if out else None,'review':review,'resume':resume,'plan_hash':plan['plan_hash']}
    env=dict(os.environ);env['PYTHONPATH']=str(Path(__file__).resolve().parent.parent)+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    process=subprocess.Popen([sys.executable,'-m','wanxiang.runtime'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,start_new_session=True)
    try:
        # Import/startup grace is explicit; in-job checkpoints enforce the requested seconds.
        stdout,stderr=process.communicate(canonical(payload),timeout=seconds+5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid,signal.SIGKILL);stdout,stderr=process.communicate()
        from .pipeline import workspace_path
        run=Path(out) if out else workspace_path(workspace)/'runs'/plan['spec']['id']
        jobfile=run/'job.json'
        if jobfile.is_file():
            job=read_json(jobfile);job.update(state='budget_blocked',error={'code':'BUDGET_EXCEEDED','message':'Parent watchdog killed the job process group','requested_seconds':seconds,'startup_grace_seconds':5});write_json(jobfile,job)
        raise WXError('BUDGET_EXCEEDED','Hard watchdog timeout; worker group stopped and durable checkpoints retained',details={'requested_seconds':seconds,'startup_grace_seconds':5})
    if stderr and os.environ.get('WX_DEBUG'):sys.stderr.buffer.write(stderr)
    try:record=json.loads(stdout)
    except Exception:raise WXError('GEOMETRY_INVALID','Worker stopped without a complete protocol response',details={'returncode':process.returncode,'stderr':stderr.decode(errors='replace')[-800:]})
    if record.get('error'):
        e=record['error'];raise WXError(e['code'],e['message'],details=e.get('details'),node=e.get('node'))
    if process.returncode:raise WXError('GEOMETRY_INVALID','Model worker exited unsuccessfully')
    return record['job']


def worker():
    try:
        from .pipeline import build
        from .compiler import compile_spec
        q=json.load(sys.stdin);plan=compile_spec(q['spec'])
        if plan['plan_hash']!=q['plan_hash']:raise WXError('VALIDATION_FAILED','Dependencies changed between planning and worker startup')
        # CPU time cap is defense-in-depth; address space is not confused with actual resident memory.
        import resource,math
        cpu=max(2,math.ceil(q['spec']['budgets']['seconds'])+5);resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu+1))
        j=build(q['spec'],q['workspace'],q['out'],q['review'],q['resume'],plan)
        sys.stdout.buffer.write(canonical({'job':j}));return 0
    except WXError as e:sys.stdout.buffer.write(canonical({'error':e.to_dict()}));return 1
    except Exception as e:sys.stdout.buffer.write(canonical({'error':{'code':'GEOMETRY_INVALID','message':str(e)}}));return 1

if __name__=='__main__':raise SystemExit(worker())
