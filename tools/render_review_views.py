"""Render actual GLB views for human review; does not classify aesthetic quality.
Usage: python tools/render_review_views.py OUT_DIR [ASSET_ID ...]
No font files or generated GLBs are distributed by this command.
"""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'packages/kit/src'),str(R/'tools')]
from asset_jobs import materialized
from wanxiang.render import prepare,render_prepared
from wanxiang.live_geometry import stop
from PIL import Image,ImageDraw,ImageFont
O=Path(sys.argv[1]);O.mkdir(parents=True,exist_ok=True)
ids=sys.argv[2:] or [r['id'] for r in json.loads((R/'library/registry.json').read_text())['records'] if r['id'].startswith('l3-creature-')]
try:
 f=ImageFont.truetype('DejaVuSans.ttf',12)
except OSError:
 f=ImageFont.load_default()
for start in range(0,len(ids),12):
 sel=ids[start:start+12];sheet=Image.new('RGB',(1400,1060),(231,235,230));draw=ImageDraw.Draw(sheet)
 for j,i in enumerate(sel):
  with materialized(i) as (path,asset):
   data=prepare(path);im,meta=render_prepared(data,330,36,22,antialias=1)
   im.save(O/f'{i}.png')
   x=(j%4)*350;y=(j//4)*353;sheet.paste(im,(x+10,y),im);draw.text((x+7,y+331),i.replace('l3-','')[:43],font=f,fill='#1E3030')
   # two extra diagnostic viewpoints retained for direct inspection.
   for az in (90,180):
    im,_=render_prepared(data,420,az,12);im.save(O/f'{i}--{az}.png')
  print(i,flush=True)
 sheet.save(O/f'contact_{start//12+1:02}.jpg',quality=94)
stop()
