"""Measure geometry submission changes; never a hardware-FPS benchmark."""
from pathlib import Path
import argparse,json,sys,tempfile,time
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'packages/kit/src'))
from asset_jobs import materialized
from wanxiang.runtime_export import export_runtime
from wanxiang.live_geometry import stop

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ids',nargs='+');p.add_argument('--out',type=Path,default=R/'generated/verification/runtime');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[]
    ids=a.ids or json.loads((R/'library/expansion.json').read_text())['scenes']
    try:
        for ident in ids:
            with tempfile.TemporaryDirectory(prefix='wx-runtime-') as temp,materialized(ident) as (source,_):
                start=time.monotonic();result=export_runtime(ident,temp);report=json.loads((Path(temp)/'runtime-map.json').read_text());row={'id':ident,'triangles':result['triangles'],'source_bytes':source.stat().st_size,'runtime_bytes':result['bytes'],'potential_draws_before':result['draws_before'],'potential_draws_after':result['draws_after'],'seconds':round(time.monotonic()-start,3),'independent_readback':True};rows.append(row);(a.out/(ident+'-map.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(row,flush=True)
    finally:stop()
    (a.out/'benchmark.json').write_text(json.dumps({'version':'3.10.0','hardware_fps_test':False,'rows':rows,'limitations':['Static batching may increase memory and reduce culling granularity.','Skinned, moving and transparent meshes stay separate.']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
