"""Curated P5 vocabulary layered on the existing semantic author kernel."""
from worlds.common import *
from foundation.common import port as _port

def port(id,pos,normal=(0,1,0),tangent=None,interface='surface'):
 if tangent is None:tangent=(0,1,0) if abs(normal[0])>.8 else (1,0,0)
 return _port(id,pos,normal,tangent,interface)

COL={'ocean':'#46BACB','ivory':'#ECDFC1','brass':'#C49B53','cedar':'#925F37','darkwood':'#583D2B','sail':'#F1E3BE','hull':'#976C43','space':'#E5E8DE','alloy':'#74878F','solar':'#315777','amber':'#E3A354','neon':'#E658B8','cyan':'#51C9D9','panel':'#4D566B','shadow':'#323D4B','rust':'#B76248','lichen':'#86A852'}
for _key,_value in COL.items():P.setdefault(_key,_value)
THEMES.update(harbor='海盗港口',space='太空科考',cyber='赛博街市')

def fp(id,name,cat,forms=None,size=(1,1,1),theme='shared',**kw):
 ident=wp(id,name,cat,forms,size,theme=theme,**kw);d=PARTS[ident]
 d.update(version='2.0.0');d['quality']={'status':'worlds','review_scope':'P5-P6','approval':'development-review-not-user-approval'};d['source'].update(revision='2.0.0',authoring='tools/frontiers/')
 return ident

def fa(id,name,cat,items,theme,**kw):
 ident=wa(id,name,cat,items,theme=theme,**kw);d=ASSEMBLIES[ident];d.update(version='2.0.0');d['metadata'].update(collection='worlds-2.0',quality={'status':'worlds','review_scope':'P5-P6'})
 return ident

def single(id,name,cat,forms,size,theme,material='mat.matte'):
 ident=fp('p5.'+id+'.module',name+' · 结构件',cat,forms,size,theme=theme,material=material,level=2)
 return fa('world-'+id,name,cat,[pi('module',ident)],theme)

def tube(points,r=.013,color='steel',sides=6,**kw):
 return loft([list(p)+[r,r] for p in points],color,sides,**kw)

def mono_role(id,name,theme,garments=(),headgear=None,tool=None,colour=None,build=1.0):
 """A role recipe references registered anatomy; additions remain real parts."""
 base=deepcopy(ASSEMBLIES['fnd-adult']);items=base['instances'];schema_=base['metadata']['parameter_schema'];schema_['properties']['build']['default']=build
 H=div(Q('height'),1.82);B=Q('build')
 skin=next(i for i in items if i['id']=='skin');skin.setdefault('params',{}).update(palette=colour or {},grip=bool(tool))
 if headgear:
  items=[i for i in items if i['id'] not in ['hair','beard'] or headgear not in ('p5.suit.helmet','p5.wear.cyber_hood')]
  items.append(pi('headgear',headgear,parent='skin.rig.head',scale=[H,H,H]))
 for j,g in enumerate(garments):
  part_id,pos,scale,bone=g;items.append(pi('outfit'+str(j),part_id,[mul(v,H) for v in pos],parent='skin.rig.'+bone,scale=[mul(scale[0],B),mul(scale[1],H),mul(scale[2],B)]))
 if tool:items.append(pi('held',tool,[0,-.01,.03],parent='skin.rig.handR'))
 fa(id,name,'body',items,theme,params=schema_,metadata={'shared_anatomy':'core.human.body','role_recipe':True})
 if 'fnd-adult' in MOTIONS:
  motion=deepcopy(MOTIONS['fnd-adult']);motion['assembly']=id;MOTIONS[id]=motion
 return id
