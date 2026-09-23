"""Explicit filtered export batches, resumable by key AND verified output hash."""
from pathlib import Path
from .util import safe_id,read_json,write_json,sha256
from .errors import WXError

def run_batch(jobs,out,review=False,changed_only=False):
    from . import kit_assembly as K
    from .build_cache import key_for
    if not isinstance(jobs,list) or not 1<=len(jobs)<=256:raise WXError('INPUT_INVALID','Kit batch requires 1..256 jobs')
    seen=set();prepared=[]
    for job in jobs:
        if not isinstance(job,dict) or ('part' in job)==('assembly' in job):raise WXError('INPUT_INVALID','Each job needs exactly one part or assembly')
        ident=safe_id(job.get('id') or job.get('part') or job.get('assembly') or '')
        if ident in seen:raise WXError('INPUT_INVALID','Duplicate batch output id')
        seen.add(ident);source=job.get('part') or job.get('assembly');style=job.get('style','lowpoly')
        spec={'schema':'wx.part-build/1.0','id':source,'part':source,'params':job.get('params',{}),'style':style} if 'part' in job else K.apply_build_parameters(K.get_template(source),job.get('params',{}));spec['style']=style
        prepared.append((ident,spec))
    out=Path(out);out.mkdir(parents=True,exist_ok=True);results=[];cancelled=False
    try:
        for ident,spec in prepared:
            target=out/ident;stamp=target/'export-stamp.json';key,_=key_for(spec,review=review);glb=target/'release/asset.glb'
            try:
                # Publish rejects overwriting a different source spec: use a new
                # revision directory rather than silently destroy previous work.
                if (target/'source/kit-spec.json').exists() and K.digest(read_json(target/'source/kit-spec.json'))!=K.digest(spec):target=out/(ident+'-'+key[:12]);glb=target/'release/asset.glb';stamp=target/'export-stamp.json'
                old=read_json(stamp) if stamp.exists() else {}
                if changed_only and old.get('key')==key and glb.exists() and old.get('sha256')==sha256(glb):results.append({'id':ident,'status':'unchanged','passed':True,'key':key,'glb':str(glb)});continue
                res=K.build(spec=spec,out=target,review=review);write_json(stamp,{'key':key,'sha256':res['sha256'],'spec':spec})
                results.append({'id':ident,'status':'exported',**res})
            except Exception as e:results.append({'id':ident,'status':'failed','passed':False,'error':str(e)})
            finally:write_json(out/'batch-results.json',results)
    except KeyboardInterrupt:cancelled=True
    report={'count':len(results),'requested':len(prepared),'passed':not cancelled and all(r['passed'] for r in results),'cancelled':cancelled,'results':results}
    write_json(out/'batch-report.json',report);return report
