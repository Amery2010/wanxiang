"""Semantic author vocabulary. Every catalogue entry has an actual use and level."""
from foundation.common import *
from foundation import common as F
THEMES={'camp':'奇幻营地','farm':'乡村农场','city':'城市街道','home':'家居室内','construction':'工业施工','depot':'交通维修站','outpost':'军事前哨'}
def wp(id,name,cat,forms=None,size=(1,1,1),theme='shared',**kw):
 ident=F.part(id,name,cat,forms,size,**kw);d=PARTS[ident];d.update(version='1.9.1',tags=['Worlds',theme,cat]);d['quality']={'status':'worlds','review_scope':'P3-P4','approval':'development-review-not-user-approval'};d['source'].update(revision='1.9.1',authoring='tools/worlds/');d['theme']=theme;return ident

def wa(id,name,cat,items,theme='shared',**kw):
 ident=F.assembly(id,name,cat,items,**kw);d=ASSEMBLIES[ident];d.update(version='1.9.1',tags=['Worlds',theme,cat]);d['metadata'].update(collection='worlds-1.9',theme=theme,quality={'status':'worlds','review_scope':'P3-P4'});return ident

def ai(id,target,pos=(0,0,0),rot=None,scale=None,**kw):return inst(id,assembly=target,pos=pos,rot=rot,scale=scale,**kw)
def pi(id,target,pos=(0,0,0),rot=None,scale=None,**kw):return inst(id,part=target,pos=pos,rot=rot,scale=scale,**kw)
def controls(*rows):return {'state_controls':list(rows)}
def turn(id,title,node,lo,hi,axis=(0,1,0)):return {'id':id,'title':title,'node':node,'axis':list(axis),'min':lo,'max':hi,'default':0,'unit':'°'}
def paint(**mapping):return {'palette':{C(k):C(v) for k,v in mapping.items()}}
def beam(a,b,w=.09,d=.09,color='wood',**kw):
 # Rectangular, orthogonally framed beam. Polygon tubes preserve structural faces.
 return loft([list(a)+[w*.5,d*.5],list(b)+[w*.5,d*.5]],color,sides=4,outline=[[1,1],[-1,1],[-1,-1],[1,-1]],**kw)
def disk(r,h,color,pos=(0,0,0),sides=16,**kw):return lathe([[r,-h*.5],[r,h*.5]],color,sides,cap=True,position=list(pos),**kw)
def simple(id,name,cat,forms,size,theme='shared',material='mat.matte',level=2):
 # Multi-form functional units are L2, not misleading L1 micro-components.
 p=wp('w.'+id+'.module',name+' · 结构总成',cat,forms,size,theme=theme,material=material,level=level)
 return wa('world-'+id,name,cat,[pi('module',p)],theme=theme)


def label_forms(text, width, height, color='white', position=(0,0,0), depth=.008):
 """Compact original 5x7 glyphs, merged per row. Geometry only; no font assets."""
 glyphs={
 'A':['01110','10001','10001','11111','10001','10001','10001'],
 'B':['11110','10001','10001','11110','10001','10001','11110'],
 'C':['01111','10000','10000','10000','10000','10000','01111'],
 'E':['11111','10000','10000','11110','10000','10000','11111'],
 'F':['11111','10000','10000','11110','10000','10000','10000'],
 'I':['11111','00100','00100','00100','00100','00100','11111'],
 'O':['01110','10001','10001','10001','10001','10001','01110'],
 'P':['11110','10001','10001','11110','10000','10000','10000'],
 'S':['01111','10000','10000','01110','00001','00001','11110'],
 'T':['11111','00100','00100','00100','00100','00100','00100'],
 'U':['10001','10001','10001','10001','10001','10001','01110'],
 'X':['10001','10001','01010','00100','01010','10001','10001'],
 '0':['01110','10011','10101','10101','11001','10001','01110'],
 '1':['00100','01100','00100','00100','00100','00100','01110'],
 ' ':['00000']*7}
 if any(c not in glyphs for c in text):raise ValueError('Unsupported authored sign glyph')
 px=width/(len(text)*6-1);py=height/7;out=[]
 for k,c in enumerate(text):
  for row,bits in enumerate(glyphs[c]):
   i=0
   while i<5:
    if bits[i]!='1':i+=1;continue
    start=i
    while i<5 and bits[i]=='1':i+=1
    x=position[0]-width/2+(k*6+(start+i)/2)*px;y=position[1]+height/2-(row+.5)*py
    out.append(box([(i-start)*px,py,depth],color,[x,y,position[2]],bevel=.0005))
 return out
