"""Build/contract regression for repaired models. This is not aesthetic scoring."""
from pathlib import Path
import json,sys,hashlib,traceback,time,os
from concurrent.futures import ProcessPoolExecutor,as_completed
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'packages/kit/src'))
import numpy as np

def digest_mesh(m):
    return hashlib.sha256(b''.join(np.ascontiguousarray(a).tobytes() for a in (m.vertices,m.faces,m.normals,np.asarray(m.colors) if m.colors is not None else np.array([])))).hexdigest()

def verify_one(ident):
    from wanxiang.kit_parts import definition,build_part
    from wanxiang.live_geometry import build_mesh,stop
    from wanxiang.semantic import parameter_values
    d=definition(ident);rows=[];base=None;errors=[]
    try:
        props=d.get('parameter_schema',{}).get('properties',{})
        cases=[('default-lowpoly','lowpoly',{}),('default-toon','toon',{})]
        for name,p in props.items():
            vals=list(p.get('enum',[]))
            if p.get('type')=='boolean':vals=[False,True]
            elif not vals:vals=[v for v in (p.get('minimum'),p.get('maximum')) if v is not None]
            for v in vals:
                if v!=p.get('default'):cases.append((name+'='+str(v),'lowpoly',{name:v}))
        if {'width','height','depth'}.issubset(props):
            for bound in ('minimum','maximum'):
                cases.append(('dimensions-'+bound,'lowpoly',{k:props[k][bound] for k in ('width','height','depth')}))
        for label,style,params in cases:
            try:
                m=build_mesh(d,style,params)
                assert 0<len(m.faces)<=min(30000,d.get('runtime',{}).get('triangle_budget',30000)), f'Triangle budget exceeded: {len(m.faces)}'
                assert np.isfinite(m.vertices).all() and np.isfinite(m.normals).all()
                assert m.faces.min()>=0 and m.faces.max()<len(m.vertices)
                assert m.vertices.shape==m.normals.shape
                if m.colors is not None:
                    co=np.asarray(m.colors);assert np.isfinite(co).all() and co.min()>=0 and co.max()<=1.00001
                h=digest_mesh(m)
                if label=='default-lowpoly':base=h
                if params and h==base:raise AssertionError('Parameter state does not affect geometry, normals or colours')
                rows.append({'case':label,'style':style,'params':params,'triangles':len(m.faces),'bounds':[m.vertices.min(0).tolist(),m.vertices.max(0).tolist()],'mesh_sha256':h,'passed':True})
            except Exception as e:
                rows.append({'case':label,'params':params,'passed':False,'error':str(e)})
                errors.append({'case':label,'error':str(e)})
        # Use the real public builder too: materials, connectors, sockets and IR.
        for style in ('lowpoly','toon'):
            a=build_part(ident,style)
            assert a.meshes and np.isfinite(a.bounds()).all()
            sockets={x['id'] for x in a.sockets}
            assert {'mount','front','top','bottom'}.issubset(sockets)
        return {'id':ident,'passed':not errors,'cases':rows,'errors':errors,'builder_styles_verified':2}
    except Exception as e:return {'id':ident,'passed':False,'cases':rows,'errors':errors+[{'error':str(e),'traceback':traceback.format_exc()}]}
    finally:stop()

def main():
    findings=json.loads((R/'authoring/repair39-findings.json').read_text());baseline=json.loads((R/'authoring/repair39-contracts.json').read_text())
    ids=[r['id'] for r in findings];contracts=[]
    for i in ids:
        d=json.loads((R/'library/parts'/(i+'.json')).read_text());old=baseline[i]
        for k in ('id','size','anchor','connectors'):
            assert d.get(k)==old.get(k),(i,k,'contract changed')
        oldprops=(old.get('parameter_schema') or {}).get('properties',{})
        newprops=(d.get('parameter_schema') or {}).get('properties',{})
        for k,p in oldprops.items():assert newprops.get(k)==p,(i,k,'old parameter schema changed')
        assert d['repair39']['source_revision']=='3.9.0'
        contracts.append({'id':i,'old_named_parameters':len(oldprops),'id_size_anchor_connectors_preserved':True})
    results=[];t=time.monotonic();print('166 asset contract records verified',flush=True)
    with ProcessPoolExecutor(max_workers=4) as pool:
        for n,f in enumerate(as_completed([pool.submit(verify_one,i) for i in ids]),1):
            r=f.result();results.append(r)
            print(n,len(ids),r['id'],'PASS' if r['passed'] else r['errors'],flush=True)
    from collections import Counter
    rows=json.loads((R/'library/registry.json').read_text())['records']
    assert len(rows)==len({r['id'] for r in rows})==3730
    assert Counter(r['level'] for r in rows)=={1:1600,2:1010,3:1000,4:120}
    report={'version':'3.10.0','source_revision':'3.9.0','seconds':round(time.monotonic()-t,2),'models':len(ids),'case_count':sum(len(r['cases']) for r in results),'passed_cases':sum(c['passed'] for r in results for c in r['cases']),'failed_models':sum(not r['passed'] for r in results),'contracts':contracts,'results':sorted(results,key=lambda x:x['id']),'limitations':'Engineering checks, not visual certification; endpoint parameter samples are not all combinations.'}
    out=R/'generated/verification/repair39-parameter-and-contract-tests.json';out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('results','contracts')},ensure_ascii=False,indent=2),flush=True)
    if report['failed_models']:raise SystemExit(1)
if __name__=='__main__':main()
