"""Export fixed IDs from a chosen source tree for reproducible before/after review.
Only current public APIs; no modification of the compared source directory.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.root/'packages/kit/src'))
from wanxiang.kit_parts import build_part
from wanxiang.kit_assembly import Assembler,get_template,materials_for
from wanxiang.glb import export_glb
from wanxiang.rigid_motion import tracks_for
from wanxiang.live_geometry import stop
ids=['core.arch.door','core.human.head','core.human.hair.short','core.human.hand','core.animal.cat.head','w.fauna.dog.head','w.fauna.fox.head','p6.turtle.shell','p6.insect.butterfly_wing','p6.insect.beetle_shell','p5.cyber.overhead_cable','w.wear.cape','fnd-adult','fnd-cat','world-dog','world-fox','world-butterfly','world-sea-turtle','world-beetle','world-service-robot','fnd-armchair']
rows=[];a.out.mkdir(parents=True,exist_ok=True)
for ident in ids:
 for style in ['lowpoly','toon']:
  ispart=(a.root/'library/parts'/(ident+'.json')).is_file()
  if ispart:asset=build_part(ident,style)
  else:
   s=get_template(ident);s['style']=style;asset=Assembler(style).assemble(s)
  out=a.out/(ident+'--'+style+'.glb');export_glb(asset,materials_for(asset),out,animations=[] if ispart else tracks_for(asset,ident))
  lo,hi=asset.bounds();rows.append(dict(id=ident,style=style,bounds=[lo.tolist(),hi.tolist()],triangles=sum(len(asset.meshes[n['mesh']].faces) for n in asset.nodes if n.get('mesh')),file=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
  print('SAMPLE',ident,style,flush=True)
(a.out/'samples.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');stop()
