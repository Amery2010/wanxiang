"""Render real before/after GLBs with one shared camera envelope and lighting.
The common CPU renderer isolates geometry/normal changes, not legacy shader fidelity.
"""
from pathlib import Path
import argparse,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'packages/kit/src'))
from wanxiang.beauty import render

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True)
    p.add_argument('--out',type=Path,default=R/'generated/verification/comparisons');args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    sets=[json.loads((d/'samples.json').read_text()) for d in [args.before,args.after]]
    lookup=[{(s['id'],s['style']):s for s in rows} for rows in sets];ids=list(dict.fromkeys(s['id'] for s in sets[1]));manifest=[]
    for ident in ids:
        records=[lookup[k][(ident,style)] for style in ['lowpoly','toon'] for k in [0,1]]
        lo=np.min([r['bounds'][0] for r in records],axis=0);hi=np.max([r['bounds'][1] for r in records],axis=0);bounds=np.stack([lo-.00001,hi+.00001])
        az,el=(35,23)
        if 'butterfly' in ident:az,el=15,72
        if 'hair' in ident:az,el=35,30
        if 'cable' in ident:az,el=25,38
        if ident=='core.human.hand':az,el=25,26
        if ident=='fnd-adult':az,el=20,15
        row=Image.new('RGB',(1920,560),'#fafbf8');d=ImageDraw.Draw(row);d.text((18,10),ident,font=ImageFont.load_default(size=22),fill='#172b22')
        for j,rec in enumerate(records):
            root=[args.before,args.after][j%2];temp=args.out/(ident+'--'+str(j)+'.png')
            render(root/rec['file'],temp,size=480,azimuth=az,elevation=el,style=rec['style'],antialias=2,framing_bounds=bounds)
            im=Image.open(temp).convert('RGBA');row.paste(im,(j*480,42),im);temp.unlink()
            d.text((j*480+18,530),f"{'BEFORE' if j%2==0 else 'AFTER'}  |  {rec['style'].upper()}  |  {rec['triangles']:,} tris",font=ImageFont.load_default(size=16),fill='#334c41')
        dst=args.out/(ident+'.webp');row.save(dst,quality=93)
        manifest.append(dict(id=ident,image=dst.name,camera=dict(azimuth=az,elevation=el,framing_bounds=bounds.tolist()),sources=records))
        print('COMPARE',ident,flush=True)
    (args.out/'manifest.json').write_text(json.dumps(dict(renderer='actual GLB / common CPU orthographic + PCF / shared framing; not GPU PBR',rows=manifest),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
