"""Verify the single WebP tier and current geometry provenance."""
from pathlib import Path
import json,sys,io
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'packages/kit/src'),str(R/'tools')]
from game410_thumbnails import context,source_fp,read,sha,atomic_json,load_state

def verify():
    state=load_state();rows=read(R/'library/registry.json')['records'];policy=read(R/'authoring/thumbnail-policy.json');ph=sha(json.dumps(policy,sort_keys=True).encode());defs,hashes,closure,kernel,mats=context()
    errors=[];grids=0;alpha=0
    expected={r['id'] for r in rows}
    if set(state)!=expected:errors.append({'error':'Preview roster mismatch','missing':sorted(expected-set(state)),'extra':sorted(set(state)-expected)})
    index={x['id']:x for x in read(R/'library/preview-index.json')}
    if set(index)!={r['id'] for r in rows}:errors.append({'error':'Index roster mismatch'})
    def image(rec,edge):
        nonlocal alpha
        path=R/'library'/rec['image'];raw=path.read_bytes()
        assert len(raw)==rec['bytes'] and sha(raw)==rec['sha256'],'Image byte/hash mismatch'
        assert Path(rec['image']).suffix=='.webp'
        with Image.open(io.BytesIO(raw)) as im:
            im.load();assert im.format=='WEBP' and im.mode=='RGBA' and im.size==(edge,edge),(im.format,im.mode,im.size)
            a=im.getchannel('A');assert a.getbbox() and a.getextrema()[0]==0,'Lost alpha background';alpha+=1
    for r in rows:
        ident=r['id']
        try:
            rec=state[ident];assert rec['style']=='lowpoly' and rec['source_sha256']==source_fp(closure,kernel,mats,ident,'lowpoly'),'Stale source fingerprint';assert rec['policy_sha256']==ph,'Stale compression policy'
            assert rec['image']=='thumbnails/'+ident+'.webp' and not {'small','styles'} & rec.keys(),'Unexpected thumbnail tier'
            image(rec,policy['profiles']['grid']['edge']);grids+=1
            assert index[ident]['sha256']==rec['sha256'],'Index stale'
        except Exception as e:errors.append({'id':ident,'error':str(e)})
    report={'version':'3.10.0','public_assets':len(rows),'grid_images_verified':grids,'alpha_images_verified':alpha,'errors':errors,'integrity_passed':not errors,'visual_certification':False,'policy':policy}
    atomic_json(R/'generated/verification/preview-verification.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(2)
    return report
if __name__=='__main__':verify()
