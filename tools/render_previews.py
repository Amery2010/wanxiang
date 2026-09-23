"""Render scene evidence from transient actual GLBs."""
from pathlib import Path
import argparse,json,sys,time
from asset_jobs import R,rows,materialized
from wanxiang.beauty import render
from wanxiang.live_geometry import stop

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--id');p.add_argument('--collection',choices=['all','foundation','worlds','expansion','l1','l2','l3','l4'],default='all');p.add_argument('--style',default='lowpoly',choices=['lowpoly','toon','voxel']);p.add_argument('--out',type=Path,default=R/'generated/verification/previews');p.add_argument('--size',type=int,default=900);p.add_argument('--scratch',help='Deprecated; scratch GLBs now use self-cleaning temporary directories');args=p.parse_args(argv)
    args.out.mkdir(parents=True,exist_ok=True);selected=rows(args.collection,[args.id] if args.id else None);start=time.monotonic()
    if not args.id:selected=[r for r in selected if r['level']==4]
    try:
        for i,row in enumerate(selected):
            ident=row['id']
            with materialized(ident,args.style) as (path,asset):
                meta=render(path,args.out/(ident+'-'+args.style+'.png'),args.size,36,32 if row['level']==4 else 24,style=args.style,antialias=1)
                (args.out/(ident+'-'+args.style+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
            print('RENDERED',i+1,len(selected),ident,round(time.monotonic()-start,1),flush=True)
    finally:stop()
if __name__=='__main__':main()
