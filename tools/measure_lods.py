"""Measure actual authored LOD0/LOD1 geometry in both supported review styles."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'packages/kit/src'))
from wanxiang.kit_parts import build_part
from wanxiang.kit_assembly import get_template,Assembler
from wanxiang.runtime_metadata import lod_parameters
from wanxiang.live_geometry import stop

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();rows=[]
 try:
  for r in json.loads((R/'library/registry.json').read_text())['records']:
   if not r.get('runtime',{}).get('lod'):continue
   for style in ('lowpoly','toon'):
    counts=[]
    for level in (0,1):
     params=lod_parameters(r['id'],r['kind'],level)
     if r['kind']=='part':asset=build_part(r['id'],style,params)
     else:
      spec=get_template(r['id']);spec['style']=style;spec.setdefault('metadata',{})['parameters']=params;asset=Assembler(style).assemble(spec)
     # Expanded visible triangles, accounting for reused meshes through nodes.
     counts.append(sum(len(asset.meshes[n['mesh']].faces) for n in asset.nodes if n.get('mesh')))
    rows.append({'id':r['id'],'style':style,'LOD0':counts[0],'LOD1':counts[1],'passed':0<counts[1]<counts[0]})
 finally:stop()
 report={'version':'3.0.0','method':'Actual expanded author-LOD geometry, not metadata estimates; no LOD GLB retained','comparisons':len(rows),'asset_count':len({r['id'] for r in rows}),'passed':sum(r['passed'] for r in rows),'failed':sum(not r['passed'] for r in rows),'rows':rows};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'}));return int(report['failed']>0)
if __name__=='__main__':raise SystemExit(main())
