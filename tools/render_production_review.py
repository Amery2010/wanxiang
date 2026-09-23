"""Render D/E review images from transient GLB exports (no frozen models).

Every L3 is shown in Lowpoly and Toon. Motion plates sample actual exported
animation channels at three times with one fixed camera envelope. Presentation
uses the CPU review renderer, not a claim of hardware/GPU PBR equivalence.
"""
from pathlib import Path
import argparse,json,sys,time
import numpy as np
from PIL import Image,ImageDraw
from asset_jobs import R,rows,materialized
from wanxiang.beauty import render
from wanxiang.render import prepare
from wanxiang.live_geometry import stop

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--style',choices=['lowpoly','toon'],default='lowpoly');ap.add_argument('--motion',action='store_true');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);records=[];start=time.monotonic()
 try:
  selected=[]
  for r in rows('expansion'):
   if r['level']!=3:continue
   d=json.loads((R/'library/assemblies'/(r['id']+'.json')).read_text())
   if d.get('metadata',{}).get('quality',{}).get('review_scope')=='D-E':selected.append(r)
  if a.motion:
   selected=[{'id':i} for i in ['exp-arch-roller_door','exp-game-platform_puzzle','exp-character-firefighter','exp-creature-serpent_rig','exp-creature-tentacle_crown','exp-robot-workcell']]
  for index,row in enumerate(selected):
   ident=row['id']
   with materialized(ident,a.style) as (p,asset):
    if a.motion:
     import struct
     raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);an=g.get('animations',[])
     if not an:raise ValueError('Animation missing: '+ident)
     clip=next((i for i,c in enumerate(an) if 'walk' in c.get('name','').lower()),0)
     duration=max(float(g['accessors'][sampler['input']].get('max',[1])[-1]) for sampler in an[clip]['samplers']);times=[0,round(duration*.32,4),round(duration*.64,4)];views=[prepare(p,clip=clip,time=t) for t in times];v=np.concatenate([x['vertices'] for x in views]);lo=v.min(0);hi=v.max(0);pad=np.maximum((hi-lo)*.04,.01);bounds=np.array([lo-pad,hi+pad]);plate=Image.new('RGB',(1200,434),'#eceeea');draw=ImageDraw.Draw(plate)
     for j,t in enumerate(times):
      frame=a.out/(ident+f'-frame-{j}.png');meta=render(p,frame,400,36,24,style=a.style,clip=clip,time=t,framing_bounds=bounds);im=Image.open(frame).convert('RGBA');plate.paste(im,(j*400,0),im);draw.text((j*400+12,411),f't = {t:.2f} s',fill='#24332c');frame.unlink()
     plate.save(a.out/(ident+'-motion.webp'),'WEBP',quality=90,method=4);records.append({'id':ident,'clip':an[clip].get('name',clip),'times':times,'source':'actual-exported-glb','camera_envelope':bounds.tolist(),'animation_targets':[g['nodes'][c['target']['node']].get('name') for c in an[clip]['channels']]})
    else:
     meta=render(p,a.out/(ident+'-'+a.style+'.webp'),512,36,24,style=a.style);records.append({'id':ident,**meta})
   print('REVIEW',index+1,len(selected),ident,round(time.monotonic()-start,2),flush=True)
 finally:stop()
 (a.out/('motion-manifest.json' if a.motion else a.style+'-manifest.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
