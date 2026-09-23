"""Render current catalogue contact sheets and scene evidence from recipes."""
from pathlib import Path
import argparse,json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=R/'generated/verification');p.add_argument('--collection',choices=['all','expansion','worlds','foundation','l1','l2','l3','l4'],default='expansion');args=p.parse_args();E=args.out;E.mkdir(parents=True,exist_ok=True)
    from asset_jobs import rows
    records=rows(args.collection)
    for start in range(0,len(records),30):
        subset=records[start:start+30];board=Image.new('RGB',(1350,1350),'#F6F8F3');d=ImageDraw.Draw(board);font=ImageFont.load_default(size=12)
        d.text((20,15),'WANXIANG 3.10 / ACTUAL GENERATED GEOMETRY / '+args.collection.upper(),fill='#334537',font=font)
        for j,r in enumerate(subset):
            im=Image.open(R/'library/thumbnails'/(r['id']+'.webp')).convert('RGBA').resize((200,200));x=j%6*225;y=55+j//6*255;board.paste(im,(x+12,y),im);d.text((x+10,y+205),r['id'],fill='#334537',font=font);d.text((x+10,y+225),'L'+str(r['level'])+' / '+r['category'],fill='#61735B',font=font)
        board.save(E/f'catalog-{start//30:02}.jpg',quality=90)
    for style in ['lowpoly','toon']:subprocess.run([sys.executable,str(R/'tools/render_previews.py'),'--collection',args.collection,'--style',style,'--out',str(E/'previews'),'--size','1000'],check=True)
if __name__=='__main__':main()
