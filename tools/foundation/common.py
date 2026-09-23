"""Small authoring vocabulary. Expressions are JSON data, never executable code."""
from __future__ import annotations
from copy import deepcopy
import math
P={'skin':'#DDAA85','skinShade':'#CA9371','cream':'#EFE3CB','white':'#F8F3E7','ink':'#293339','hair':'#4F3527','hairLight':'#674530','wood':'#A77143','woodLight':'#C38F55','woodDark':'#634530','leaf':'#72A53B','leafLight':'#93BE43','leafDark':'#417F40','pine':'#397248','stone':'#9A9C96','stoneLight':'#BFC0B6','stoneDark':'#777E7E','blue':'#57778D','navy':'#354C60','red':'#B95343','yellow':'#E8AA32','teal':'#367A76','orange':'#D0783C','rubber':'#2B3031','metal':'#A3ACAA','steel':'#53616A','glass':'#4E727B','cyan':'#55D2E5','moss':'#707952','soil':'#856544','water':'#43BAD1'}
PARTS={};ASSEMBLIES={};MOTIONS={}
def C(s):return P.get(s,s)
def Q(k):return {'$param':k}
def O(op,*args):
 if all(isinstance(a,(float,int)) for a in args):
  if op=='add':return sum(args)
  if op=='mul':return math.prod(args)
  if op=='sub':return args[0]-args[1]
  if op=='div':return args[0]/args[1]
 return {'$op':op,'args':list(args)}
def add(*a):return O('add',*a)
def mul(*a):return O('mul',*a)
def sub(a,b):return O('sub',a,b)
def div(a,b):return O('div',a,b)
def neg(a):return mul(-1,a)
def choice(k,cases,default=None):return {'$switch':k,'cases':cases,'default':default}
def number(default,lo,hi,title,step=.01,unit=None):return {'type':'number','default':default,'minimum':lo,'maximum':hi,'title':title,'step':step,**({'unit':unit} if unit else {})}
def schema(**props):return {'type':'object','additionalProperties':False,'properties':props}
def port(id,pos,normal=(0,1,0),tangent=(1,0,0),interface='surface'):
 return {'id':id,'position':list(pos),'normal':list(normal),'tangent':list(tangent),'interface':interface}
def poly(points,faces,color='cream',**kw):return {'kind':'poly','points':points,'faces':faces,'color':C(color),'roundable':False,**kw}
def box(size,color='cream',pos=(0,0,0),bevel=.01,**kw):
 # Bounded, designed bevels instead of a blanket subdivision modifier.
 return {'kind':'bevelbox','size':size,'bevel':O('min',bevel,*[mul(.44,v) for v in size]),'position':list(pos),'color':C(color),'roundable':False,**kw}
def cube(size,color='cream',pos=(0,0,0),**kw):
 x,y,z=[mul(.5,a) for a in size]
 ps=[[mul(a,x),mul(b,y),mul(c,z)] for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return poly(ps,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],color,position=list(pos),**kw)
def loft(rings,color='cream',sides=8,bone=None,**kw):
 rs=[]
 for r in rings:
  rs.append(r if isinstance(r,dict) else {'c':r[:3],'r':r[3:]})
 return {'kind':'loft','rings':rs,'color':C(color),'sides':sides,**({'bone':bone} if bone else {}),**kw}
OCT=[[1,.62],[.62,1],[-.62,1],[-1,.62],[-1,-.62],[-.62,-1],[.62,-1],[1,-.62]]
def profile(rings,color='cream',bone=None,**kw):return loft(rings,color,8,bone,outline=OCT,**kw)
def rod(a,b,r,color='wood',r2=None,sides=8,**kw):return loft([list(a)+[r,r],list(b)+[r2 if r2 is not None else r,r2 if r2 is not None else r]],color,sides,**kw)
def ico(size,color='leaf',pos=(0,0,0),detail=1,**kw):return {'kind':'ico','size':size,'position':list(pos),'detail':detail,'color':C(color),'distort':.04,'roundable':False,**kw}
def lathe(profile_points,color='metal',sides=16,**kw):return {'kind':'lathe','profile':profile_points,'sides':sides,'color':C(color),'roundable':False,**kw}
def extrude(outline,depth,color='cream',**kw):return {'kind':'extrude','outline':outline,'depth':depth,'color':C(color),'roundable':False,**kw}
def part(id,name,category,forms=None,size=(1,1,1),ports=(),params=None,components=None,rig=None,anchor='base',level=1,material='mat.matte',description='',tags=()):
 d={'schema':'wx.part/1.0','id':id,'name':name,'version':'1.8.0','level':level,'category':category,'shape':'faceted','size':list(size),'anchor':anchor,'material':material,'connectors':list(ports),'shape_params':{'forms':forms or []},'source':{'type':'original_authored_modular_profiles','license':'project-authored','revision':'1.8.0','authoring':'tools/foundation/'},'status':'implemented','quality':{'status':'foundation','review_scope':'P1-P2','approval':'assistant-review-not-user-approval'},'tags':['Foundation',category,*tags],'description':description}
 if params:d['parameter_schema']=params
 if components:d['shape_params']['components']=components
 if rig:d['shape_params']['rig']=rig
 PARTS[id]=d;return id

def component(id,part,position=(0,0,0),rotation=None,scale=None,**kw):return {'id':id,'part':part,'position':list(position),**({'rotation':list(rotation)} if rotation else {}),**({'scale':list(scale)} if scale else {}),**kw}
def inst(id,part=None,assembly=None,pos=None,rot=None,scale=None,**kw):return {'id':id,**({'part':part} if part else {'assembly':assembly}),**({'position':list(pos)} if pos is not None else {}),**({'rotation':list(rot)} if rot else {}),**({'scale':list(scale)} if scale else {}),**kw}
def assembly(id,name,category,items,level=3,params=None,ports=None,description='',metadata=None):
 md={'level':level,'collection':'foundation-1.8','quality':{'status':'foundation','review_scope':'P1-P2'},'art_direction':'designed-faceted-surfaces','units':'metres',**(metadata or {})}
 if params:md['parameter_schema']=params;md['parameters']={}
 ASSEMBLIES[id]={'schema':'wx.assembly/1.0','id':id,'name':name,'version':'1.8.0','category':category,'style':'lowpoly','tags':['Foundation',category,name],'description':description,'metadata':md,'instances':items,**({'exports':ports} if ports else {})};return id

def clip(id,clips):MOTIONS[id]={'schema':'wx.rigid-motion/1.0','binding':'weighted_skin_or_rigid','assembly':id,'clips':clips}
def track(node,axis,degrees):return {'node':node,'axis':axis,'degrees':degrees}
