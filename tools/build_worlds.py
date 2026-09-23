"""Generate and verify definitions on demand. No shipped GLB is an input.

Default: validate all Worlds temporarily and write a JSON report only.
--out: explicitly materialise an optional example export directory.
"""
from pathlib import Path
import argparse,hashlib,json,time,sys
from asset_jobs import R,rows,materialized,build
from wanxiang.validation import inspect_asset
from wanxiang.live_geometry import stop

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--include-foundation',action='store_true');p.add_argument('--include-expansion',action='store_true');p.add_argument('--collection',choices=['all','foundation','worlds','expansion','l1','l2','l3','l4']);p.add_argument('--ids',nargs='+');p.add_argument('--styles',nargs='+',choices=['lowpoly','toon','voxel'],default=['lowpoly']);p.add_argument('--out',type=Path);p.add_argument('--report',type=Path,default=R/'generated/verification/catalog-build.json');p.add_argument('--no-images',action='store_true');p.add_argument('--changed-only',action='store_true');args=p.parse_args(argv)
    if args.changed_only and not args.out:p.error('--changed-only requires an explicit --out directory')
    selected=rows(args.collection or 'worlds',args.ids)
    if not args.collection and not args.ids:
        if args.include_foundation:selected+=rows('foundation')
        if args.include_expansion:selected+=rows('expansion')
    selected=list({r['id']:r for r in selected}.values());result=[];start=time.monotonic()
    from wanxiang.build_cache import key_for
    try:
        for row in selected:
            for style in args.styles:
                ident=row['id'];dest=args.out/(ident+'-'+style+'.glb') if args.out else None
                try:
                    definition=json.loads((R/'library'/('parts' if row['kind']=='part' else 'assemblies')/(ident+'.json')).read_text())
                    spec={'schema':'wx.part-build/1.0','id':ident,'part':ident,'style':style,'params':{}} if row['kind']=='part' else {**definition,'style':style}
                    key,_=key_for(spec,mode='examples');stamp=dest.with_suffix('.export.json') if dest else None
                    if args.changed_only and dest.exists() and stamp.exists():
                        old=json.loads(stamp.read_text())
                        if old['build_key']==key and old['sha256']==hashlib.sha256(dest.read_bytes()).hexdigest():result.append({**old,'skipped_unchanged':True});continue
                    with materialized(ident,style) as (path,asset):
                        report=inspect_asset(path,expected=asset,independent=True)
                        if not report['passed']:raise ValueError(str(report['issues']))
                        entry={'id':ident,'style':style,'passed':True,'triangles':report['triangles'],'nodes':report['nodes'],'unique_gltf_meshes':report['unique_gltf_meshes'],'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'build_key':key,'independent_readback':True}
                        if dest:
                            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes());dest.with_suffix('.recipe.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n');stamp.write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
                        result.append(entry)
                        if not args.no_images:
                            from wanxiang.render import prepare,render_prepared
                            im,_=render_prepared(prepare(path),192,36,30,antialias=1);folder=args.report.parent/'thumbnails';folder.mkdir(exist_ok=True,parents=True);im.save(folder/(ident+'-'+style+'.webp'),'WEBP',quality=86)
                except Exception as e:result.append({'id':ident,'style':style,'passed':False,'error':str(e)})
            if len(result)%25==0:print('VERIFIED',len(result),flush=True)
    finally:stop()
    report={'schema':'wx.catalog-build/2.0','version':'3.10.0','temporary_glb_inputs':True,'rows':result,'passed':sum(r['passed'] for r in result),'failed':sum(not r['passed'] for r in result),'seconds':round(time.monotonic()-start,3),'output_mode':'materialized' if args.out else 'temporary'}
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False,indent=2));return bool(report['failed'])
if __name__=='__main__':sys.exit(main())
