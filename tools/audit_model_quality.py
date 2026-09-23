"""Reproducible per-form topology/normal audit; open foliage is NOT a closed solid.
No aesthetic score is inferred from polygon count. Reports cover each current ID,
with direct geometry errors distinguished from dependency impact on assemblies.
Use --root to run the exact same checks on an immutable earlier release.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, sys, time
from pathlib import Path
import numpy as np

def form_metrics(v, n):
    v=np.asarray(v,np.float64); n=np.asarray(n,np.float64)
    if not len(v): return {'triangles':0,'empty':True}
    # Absolute 1e-7m positional weld, strictly within the authored form.
    _, ix=np.unique(np.round(v,7),axis=0,return_inverse=True)
    faces=ix.reshape(-1,3); tri=v.reshape(-1,3,3)
    cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); area=np.linalg.norm(cross,axis=1)
    edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    undirected=np.sort(edges,axis=1); ue,rev,cts=np.unique(undirected,axis=0,return_inverse=True,return_counts=True)
    winding=np.bincount(rev,weights=np.where(edges[:,0]<edges[:,1],1.,-1.),minlength=len(cts))
    _,duplicates=np.unique(np.sort(faces,axis=1),axis=0,return_counts=True)
    centered=tri-v.mean(axis=0);volume=float(np.einsum('ij,ij->i',centered[:,0],np.cross(centered[:,1],centered[:,2])).sum()/6)
    finite=bool(np.isfinite(v).all() and np.isfinite(n).all())
    normal_lengths=np.linalg.norm(n,axis=1)
    closed=bool(np.all(cts==2))
    lengths=np.stack([np.sum((tri[:,0]-tri[:,1])**2,axis=1),np.sum((tri[:,1]-tri[:,2])**2,axis=1),np.sum((tri[:,2]-tri[:,0])**2,axis=1)],axis=1).sum(1)
    q=2*np.sqrt(3)*area/np.maximum(lengths,1e-25)
    return dict(triangles=len(faces),position_vertices=int(len(np.unique(ix))),finite=finite,
        degenerate_triangles=int(np.sum(area<1e-15)),duplicate_triangles=int(np.maximum(duplicates-1,0).sum()),
        boundary_edges=int(np.sum(cts==1)),nonmanifold_edges=int(np.sum(cts>2)),
        inconsistent_edges=int(np.sum((cts==2)&(np.abs(winding)>0))),closed=closed,
        inverted_closed=bool(closed and volume< -1e-12),signed_volume=round(volume,12),
        bad_normals=int(np.sum((normal_lengths<.99)|(normal_lengths>1.01))),
        sliver_triangles=int(np.sum(q<.01)))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--out',type=Path);p.add_argument('--styles',nargs='+',default=['lowpoly','toon']);p.add_argument('--allow-failures',action='store_true',help='Write baseline diagnostics without a failing process status');args=p.parse_args()
    root=args.root.resolve();sys.path.insert(0,str(root/'packages/kit/src'))
    from wanxiang.live_geometry import build_mesh,stop
    records=json.loads((root/'library/registry.json').read_text())['records']
    parts={f.stem:json.loads(f.read_text()) for f in (root/'library/parts').glob('*.json')}
    assemblies={f.stem:json.loads(f.read_text()) for f in (root/'library/assemblies').glob('*.json')}
    out=args.out or root/'generated/verification/quality-audit.json';out.parent.mkdir(parents=True,exist_ok=True)
    rows=[];start=time.monotonic()
    for ident,d in sorted(parts.items()):
        styles={}
        for style in args.styles:
            try:
                m=build_mesh(d,style,{})
                ranges=m.anatomy.get('materialGroups') or [dict(start=0,count=len(m.vertices))]
                forms=[]
                for j,r in enumerate(ranges):
                    a=r['start'];b=a+r['count'];fm=form_metrics(m.vertices[a:b],m.normals[a:b]);fm.update(index=j,source_part=r.get('source_part'),source_path=r.get('source_path'))
                    forms.append(fm)
                errors=[f for f in forms if any(f.get(k,0) for k in ['empty','degenerate_triangles','duplicate_triangles','nonmanifold_edges','inconsistent_edges','inverted_closed','bad_normals']) or f.get('finite') is False]
                styles[style]=dict(triangles=len(m.faces),form_count=len(forms),bad_forms=len(errors),passed=not errors,
                    totals={k:sum(f.get(k,0) for f in forms) for k in ['boundary_edges','nonmanifold_edges','inconsistent_edges','inverted_closed','degenerate_triangles','duplicate_triangles','bad_normals','sliver_triangles']},forms=forms)
            except Exception as e: styles[style]=dict(passed=False,error=str(e))
        rows.append(dict(id=ident,kind='part',name=d['name'],category=d['category'],source_sha256=hashlib.sha256((root/'library/parts'/(ident+'.json')).read_bytes()).hexdigest(),styles=styles))
        if len(rows)%25==0: print('AUDIT',len(rows),'/',len(parts),flush=True)
    by={r['id']:r for r in rows}
    def deps(d,seen=None):
        seen=set() if seen is None else seen
        for it in d.get('instances',[]):
            if it.get('part') in parts:seen.add(it['part'])
            elif it.get('assembly') in assemblies:deps(assemblies[it['assembly']],seen)
        return seen
    for ident,d in sorted(assemblies.items()):
        ds=sorted(deps(d));styles={s:dict(passed=all(by[i]['styles'][s]['passed'] for i in ds),affected_parts=[i for i in ds if not by[i]['styles'][s]['passed']]) for s in args.styles}
        rows.append(dict(id=ident,kind='assembly',name=d['name'],category=d.get('category'),dependencies=ds,styles=styles,scope='transitive constituent audit; assembled export tested separately'))
    result=dict(schema='wx.model-quality/1.0',source_version=json.loads((root/'tool.manifest.json').read_text()).get('version'),styles=args.styles,seconds=round(time.monotonic()-start,3),
        source_kernel={'workers/node/live_geometry.cjs':hashlib.sha256((root/'packages/runtime/dist/compat/workers/node/live_geometry.cjs').read_bytes()).hexdigest()},
        method='Per authored form, position weld 1e-7m; no cross-form welding. Open surfaces reported, not failed. Aesthetic review separate.',
        summary={s:{'parts':len(parts),'assemblies':len(assemblies),'parts_with_errors':sum(not r['styles'][s]['passed'] for r in rows if r['kind']=='part'),'assemblies_with_affected_dependencies':sum(not r['styles'][s]['passed'] for r in rows if r['kind']=='assembly'),'build_errors':sum('error' in r['styles'][s] for r in rows if r['kind']=='part')} for s in args.styles},rows=rows)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');stop();print(json.dumps(result['summary'],ensure_ascii=False,indent=2),flush=True)
    return 0 if args.allow_failures else int(any(v['parts_with_errors'] for v in result['summary'].values()))
if __name__=='__main__':sys.exit(main())
