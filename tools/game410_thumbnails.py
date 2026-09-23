"""Render current thumbnails from GLBs and leave valid cached images untouched."""
from __future__ import annotations
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,hashlib,io,json,os,sys,time,traceback
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'packages/kit/src'),str(R/'tools')]
E=R/'generated/verification';STATE=E/'preview-progress.json'
from wanxiang.paths import code_path
def read(p):return json.loads(Path(p).read_text())
def sha(x):return hashlib.sha256(x).hexdigest()
def file_sha(p):return sha(Path(p).read_bytes())
def load_state():
    """The shipped preview index is the durable cache; verification output is disposable."""
    index=R/'library/preview-index.json'
    state={row['id']:row for row in read(index)} if index.exists() else {}
    if STATE.exists():state.update({key:rec for key,rec in read(STATE).items() if '|' not in key})
    return state
def atomic_json(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,p)
def resized(im,size):
    """Premultiplied-alpha resize avoids black/white fringes; never crop."""
    im=im.convert('RGBA')
    return im if im.size==(size,size) else im.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
def encode(im,profile):
    bio=io.BytesIO();im.save(bio,'WEBP',quality=profile['quality'],method=profile['method'],
      alpha_quality=profile['alpha_quality'],exact=False,icc_profile=b'',exif=b'',xmp=b'')
    raw=bio.getvalue()
    with Image.open(io.BytesIO(raw)) as decoded:
        assert decoded.format=='WEBP' and decoded.mode=='RGBA' and decoded.size==im.size
        if decoded.getchannel('A').tobytes()!=im.getchannel('A').tobytes():raise ValueError('Alpha channel changed')
    return raw

def context():
    defs={};hashes={}
    for kind in ('parts','assemblies'):
        for p in (R/'library'/kind).glob('*.json'):
            defs[p.stem]=read(p);hashes[p.stem]=file_sha(p)
    memo={}
    def closure(i,trail=()):
        if i in memo:return memo[i]
        if i in trail:raise ValueError('Reference cycle '+i)
        d=defs[i];refs=[v['part'] for v in d.get('shape_params',{}).get('components',[])]+[v.get('part') or v['assembly'] for v in d.get('instances',[])]
        memo[i]=sha((hashes[i]+''.join(closure(x,(*trail,i)) for x in sorted(set(refs)))).encode());return memo[i]
    kernel=sha(code_path('workers/node/live_geometry.cjs').read_bytes()+code_path('wanxiang/render.py').read_bytes())
    mats=sha(b''.join(p.read_bytes() for p in sorted((R/'library/materials').rglob('*.json'))))
    return defs,hashes,closure,kernel,mats

def source_fp(closure,kernel,mats,ident,style):
    return sha((closure(ident)+kernel+mats+style+'ortho-36-v1').encode())

def job(j):
    ident,level,policy,fp=j;start=time.monotonic();style='lowpoly'
    target=R/'library/thumbnails'/(ident+'.webp');target.parent.mkdir(parents=True,exist_ok=True)
    try:
        old_bytes=target.stat().st_size if target.exists() else 0
        from asset_jobs import materialized
        from wanxiang.render import prepare,render_prepared
        import numpy as np
        with materialized(ident,style) as (path,asset):
            data=prepare(path,tex_size=64);vertices=data['vertices']
            if not np.isfinite(vertices).all():raise ValueError('Non-finite geometry')
            source,meta=render_prepared(data,512,36,34 if level==4 else 24,antialias=2)
            if not source.getchannel('A').getbbox():raise ValueError('Empty model')
            triangles=len(data['faces']);bounds=[vertices.min(0).tolist(),vertices.max(0).tolist()];renderer=meta['renderer']
            ev=E/'game-models';ev.mkdir(parents=True,exist_ok=True)
            source.save(ev/(ident+'.webp'),'WEBP',quality=90,method=5)
            views=[source.resize((320,320),Image.Resampling.LANCZOS)]
            for az,el in [(90,12),(180,12)]:
                image,_=render_prepared(data,320,az,el,antialias=1);views.append(image)
            sheet=Image.new('RGB',(960,348),(235,238,232))
            from PIL import ImageDraw
            draw=ImageDraw.Draw(sheet)
            for k,image in enumerate(views):
                sheet.paste(image,(k*320,0),image);draw.text((k*320+10,325),['ISO','SIDE','REAR'][k],fill=(40,55,58))
            sheet.save(ev/(ident+'-views.webp'),'WEBP',quality=86,method=5)
        provenance={'kind':'current-GLB-render','source_rgba_sha256':sha(source.tobytes()),'renderer':renderer}
        profile=policy['profiles']['grid'];grid=resized(source,profile['edge']);raw=encode(grid,profile)
        temp=target.with_suffix('.pending.webp');temp.write_bytes(raw);os.replace(temp,target)
        rec={'id':ident,'style':style,'image':str(target.relative_to(R/'library')),'width':grid.width,'height':grid.height,
             'bytes':len(raw),'sha256':sha(raw),'source_sha256':fp,'policy_sha256':sha(json.dumps(policy,sort_keys=True).encode()),
             'renderer':renderer,'triangles':triangles,'bounds':bounds,'alpha_bounds':list(grid.getchannel('A').getbbox()),
             'previous_image_bytes':old_bytes,'provenance':provenance,'visual_review':'render success is not aesthetic approval'}
        rec['seconds']=round(time.monotonic()-start,3);return rec
    except Exception as e:return {'id':ident,'style':style,'error':str(e),'traceback':traceback.format_exc()}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workers',type=int,default=3);ap.add_argument('--ids',default='');ap.add_argument('--render-all',action='store_true');args=ap.parse_args()
    policy=read(R/'authoring/thumbnail-policy.json');assert policy['styles']==['lowpoly'];ps=sha(json.dumps(policy,sort_keys=True).encode())
    _,_,closure,kernel,mats=context();state=load_state();rows=read(R/'library/registry.json')['records']
    selected=set(args.ids.split(',')) if args.ids else None
    if selected and selected-{r['id'] for r in rows}:raise ValueError('Unknown requested ID')
    jobs=[]
    for row in rows:
        if selected and row['id'] not in selected:continue
        ident=row['id'];fp=source_fp(closure,kernel,mats,ident,'lowpoly');rec=state.get(ident,{})
        if not args.render_all and rec.get('source_sha256')==fp and rec.get('policy_sha256')==ps and (R/'library'/rec.get('image','__missing')).exists() and file_sha(R/'library'/rec['image'])==rec.get('sha256'):continue
        jobs.append((ident,row['level'],policy,fp))
    print('THUMBNAIL JOBS',len(jobs),'fresh renders',len(jobs),flush=True)
    failures=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for n,f in enumerate(as_completed([pool.submit(job,j) for j in jobs]),1):
            rec=f.result();key=rec['id']
            if rec.get('error'):failures.append(rec);print('ERROR',key,rec['error'],flush=True)
            else:state[key]=rec
            if n%40==0 or n==len(jobs):atomic_json(STATE,state);print('DONE',n,'/',len(jobs),'errors',len(failures),flush=True)
    index=[state[row['id']] for row in rows if row['id'] in state]
    if jobs:atomic_json(R/'library/preview-index.json',index)
    atomic_json(E/'thumbnail-errors.json',failures)
    report={'version':'3.10.0','registered_assets':len(rows),'expected_grid_images':len(rows),'grid_images':len(state),
            'grid_bytes':sum(x['bytes'] for x in state.values()),
            'baseline_grid_bytes':sum(x.get('previous_image_bytes',0) for x in state.values() if x['provenance']['kind']=='once-transcoded-v39-cache'),
            'compressed_baseline_grid_bytes':sum(x['bytes'] for x in state.values() if x['provenance']['kind']=='once-transcoded-v39-cache'),
            'migrated_images':sum(x['provenance']['kind']=='once-transcoded-v39-cache' for x in state.values()),
            'fresh_images':sum(x['provenance']['kind']=='current-GLB-render' for x in state.values()),'errors':len(failures),'policy':policy}
    atomic_json(E/'thumbnail-summary.json',report);print(json.dumps(report,ensure_ascii=False),flush=True)
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
