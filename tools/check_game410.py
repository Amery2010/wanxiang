"""Real shared-kernel checks for the new authored game assets, not aesthetic scores."""
from pathlib import Path
import json,hashlib,sys,time,traceback
import numpy as np
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'packages/kit/src'),str(R/'tools')]
from wanxiang.live_geometry import build_mesh
from wanxiang.semantic import evaluate,parameter_values
from asset_jobs import materialized
from wanxiang.render import prepare
from game410_thumbnails import atomic_json
out=R/'generated/verification';out.mkdir(parents=True,exist_ok=True)
def load(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
roster=load(R/'library/game-expansion.json');results=[];failures=[];hashes={};start=time.time()
def check(name,fn):
    try:
        extra=fn();results.append({'name':name,'passed':True,'detail':extra})
    except Exception as e:failures.append({'name':name,'error':str(e),'traceback':traceback.format_exc()});results.append({'name':name,'passed':False,'error':str(e)});print('FAIL',name,str(e),flush=True)
def need(v,msg='Assertion failed'):
    if not v:raise AssertionError(msg)
def baseline():
    b=load(R/'authoring/game410-baseline.json');bad=[p for p,s in b['definitions'].items() if not (R/p).exists() or digest(R/p)!=s]
    need(not bad,str(bad[:20]));return {'unchanged_definitions':len(b['definitions'])}
check('All legacy definitions remain byte-identical',baseline)
def catalogue():
    rows=load(R/'library/registry.json')['records'];levels={str(k):sum(x['level']==k for x in rows) for k in range(1,5)}
    need(levels=={'1':1600,'2':1010,'3':1000,'4':120},str(levels));need(len(set(x['id'] for x in rows))==3730)
    need(len(roster['parts'])==120 and len(roster['assemblies'])==10)
    for kit,k in roster['kits'].items():need(len(k['parts'])==12,kit)
    return levels
check('Distinct public assets and all ten game kits',catalogue)
for n,ident in enumerate(roster['parts']):
    d=load(R/'library/parts'/(ident+'.json'));props=d['parameter_schema']['properties'];default={k:p['default'] for k,p in props.items()}
    def base(d=d,ident=ident,default=default):
        m=build_mesh(d,'lowpoly',default);v=m.vertices;need(np.isfinite(v).all() and np.isfinite(m.normals).all(),'non-finite buffers');need(len(m.faces)>0 and len(m.faces)<=d['runtime']['triangle_budget'],str(len(m.faces)));need((np.ptp(v,axis=0)>1e-5).all(),'collapsed axis');need(m.faces.min()>=0 and m.faces.max()<len(v));need((np.linalg.norm(m.normals,axis=1)>.1).all(),'zero normals')
        hashes[ident]=hashlib.sha256(v.tobytes()+m.faces.tobytes()).hexdigest()
        return {'triangles':len(m.faces),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'forms':len(d['shape_params']['forms'])}
    check(ident+' / default lowpoly',base)
    for style,params,label in [('toon',default,'toon'),('lowpoly',{k:p.get('minimum',p['default']) for k,p in props.items()},'all-min'),('lowpoly',{k:p.get('maximum',p['default']) for k,p in props.items()},'all-max')]+([('lowpoly',{**default,'detail':False},'detail-off')] if 'detail' in props else []):
        def varied(d=d,style=style,params=params):
            m=build_mesh(d,style,params);need(np.isfinite(m.vertices).all() and np.isfinite(m.normals).all());need(0<len(m.faces)<=d['runtime']['triangle_budget']);need((np.ptp(m.vertices,axis=0)>1e-5).all());return {'triangles':len(m.faces)}
        check(ident+' / '+label,varied)
    def dimensions(d=d,default=default,props=props):
        v=build_mesh(d,'lowpoly',default).vertices
        # Anisotropic extremes exercise each axis independently, not just scale all.
        changed={**default,'width':props['width']['minimum'],'height':props['height']['maximum']}
        w=build_mesh(d,'lowpoly',changed).vertices
        scale=np.array([changed[k]/default[k] for k in ('width','height','depth')]);expected=v*scale
        # Ear clipping may reorder/duplicate triangles after anisotropic scaling.
        # Compare bidirectional vertex-set distances, not buffer order or count.
        need(max(cKDTree(expected).query(w)[0].max(),cKDTree(w).query(expected)[0].max())<3e-5,'dimension contract diverged')
        a=evaluate(d['connectors'],parameter_values(d['parameter_schema'],default));b=evaluate(d['connectors'],parameter_values(d['parameter_schema'],changed))
        for x,y in zip(a,b):need(np.allclose(y['position'],np.array(x['position'])*scale),'datum does not co-scale');need(abs(np.linalg.norm(x['normal'])-1)<1e-6,'invalid normal');need(abs(np.dot(x['normal'],x['tangent']))<1e-6,'nonorthogonal tangent')
        return {'connectors':len(a),'axes':'nonuniform x/y with fixed z'}
    check(ident+' / independent dimensions and datums',dimensions)
    if n%12==11:print('PARTS CHECKED',n+1,flush=True);atomic_json(out/'geometry-check-progress.json',{'results':results,'failures':failures})
check('No identical default geometry counted as new assets',lambda:need(len(set(hashes.values()))==120))
for ident in roster['assemblies']:
    for style in ('lowpoly','toon'):
        def asm(ident=ident,style=style):
            with materialized(ident,style) as (p,a):
                data=prepare(p,tex_size=16);need(np.isfinite(data['vertices']).all());need(len(data['faces'])>0);need(p.read_bytes()[:4]==b'glTF');return {'triangles':len(data['faces']),'glb_bytes':p.stat().st_size}
        check(ident+' / GLB '+style,asm)
report={'version':'3.10.0','results':results,'passed':sum(x['passed'] for x in results),'failed':len(failures),'failures':failures,'seconds':round(time.time()-start,2),'limitations':'Geometry, dimensional contracts and real static assembly export only; no aesthetic certification, rig, physics, mobile GPU or animation acceptance.'}
atomic_json(out/'geometry-checks.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('results','failures')},ensure_ascii=False),flush=True)
if failures:raise SystemExit(1)
