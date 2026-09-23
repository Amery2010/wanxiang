"""L2 original authoring vocabulary: measured L1 fits and isolated rigid frames.

No mesh duplication, packed GLBs, colour-counting, negative-scale mirroring or
invisible base cubes. A part instance references an existing semantic L1 ID.
"""
from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import math,json,hashlib
from foundation.common import PARTS,ASSEMBLIES,MOTIONS,assembly,clip,number,schema,Q,O,mul,add,sub,div,inst
from l1_expansion.common import DOMAIN_NAMES,CATEGORIES
from expansion.production import DETAIL,authored_lod
R=Path(__file__).resolve().parents[2]
BOUNDS=json.loads((R/'authoring/l1-bounds.json').read_text())['assets']
TARGETS={'architecture':94,'interior':82,'nature':95,'terrain':39,'props':106,'vehicle':51,
         'industry':45,'character':60,'creature':33,'robot':37,'gameplay':62}
ADDED=[]
VALIDATED_BOUNDS=set()
def canonical(d):
    d=dict(d);d.pop('version',None)
    return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def names(text):return [tuple(v.split(':',1)) for v in text.split()]
def ids(domain,group):return sorted(k.rsplit('.',1)[1] for k in PARTS if k.startswith(f'l1.{domain}.{group}.'))
def pid(domain,group,key):return f'l1.{domain}.{group}.{key}'
def label(part):return PARTS[part]['name']
def bounds(part):
    if part not in PARTS or PARTS[part]['level']!=1:raise ValueError('L2 must consume L1: '+part)
    if part not in BOUNDS:raise ValueError('Missing measured placement bounds: '+part)
    if part not in VALIDATED_BOUNDS:
        if canonical(PARTS[part])!=BOUNDS[part]['canonical_sha256']:
            raise ValueError('Stale L1 placement bounds: '+part+'; run python tools/measure_l1_bounds.py --ids '+part)
        VALIDATED_BOUNDS.add(part)
    return BOUNDS[part]['bounds']
def natural_size(part):
    b=bounds(part);return [b[1][j]-b[0][j] for j in range(3)]

def piece(node,part,size=None,at=(0,0,0),rot=(0,0,0),anchor='bottom',parent=None,
          optional=False,moving=False,params=None,material=None,pivot=None,collision=None):
    b=bounds(part);extent=natural_size(part)
    if min(extent)<=0:raise ValueError('Degenerate placement bounds '+part)
    if size is None:size=extent
    if isinstance(size,(int,float)):size=[x*size for x in extent]
    scale=[div(size[j],extent[j]) for j in range(3)]
    center=[(b[0][j]+b[1][j])/2 for j in range(3)]
    anchors={'center':center,'bottom':[center[0],b[0][1],center[2]],
        'top':[center[0],b[1][1],center[2]],'left':[b[0][0],center[1],center[2]],
        'right':[b[1][0],center[1],center[2]],'back':[center[0],center[1],b[0][2]],
        'front':[center[0],center[1],b[1][2]],'origin':[0,0,0]}
    if anchor not in anchors:raise ValueError('Unknown anchor '+anchor)
    p=deepcopy(params or {})
    if 'detail' in PARTS[part].get('parameter_schema',{}).get('properties',{}):p.setdefault('detail',Q('detail'))
    it={'id':node,'part':part,'position':list(at),'rotation':list(rot),'scale':scale,
        'pivot':list(pivot if pivot is not None else anchors[anchor]),'params':p,
        'role':'moving_subpart' if moving else 'functional_subpart'}
    if parent:it['parent']=parent
    if optional:it['enabled']=Q('detail')
    if material:it['material']=material
    if moving:it['collision']={'type':'convex-hull','static_only':False,'intent':'rigid moving solid; inspect hollow geometry before physics use'}
    if collision is not None:it['collision']=deepcopy(collision)
    return it

def p(node,domain,group,key,*args,**kw):return piece(node,pid(domain,group,key),*args,**kw)

def bar(node,a,b,thick=.06,depth=None,section='i',optional=False,parent=None,material=None):
    """Place a section whose local +Z is its run axis; ends remain exact."""
    v=[b[j]-a[j] for j in range(3)];length=math.sqrt(sum(x*x for x in v))
    if length<1e-5:raise ValueError('Zero-length beam')
    yaw=math.degrees(math.atan2(v[0],v[2]));pitch=-math.degrees(math.asin(v[1]/length))
    return p(node,'architecture','section',section,[depth or thick,thick,length],
        [(a[j]+b[j])/2 for j in range(3)],[pitch,yaw,0],anchor='center',optional=optional,parent=parent,material=material)

def plate(node,size,at=(0,0,0),rot=(0,0,0),**kw):
    return p(node,'architecture','floor','plank',size,at,rot,**kw)

def post(node,height,at=(0,0,0),thick=.08,**kw):
    return bar(node,at,[at[0],at[1]+height,at[2]],thick,**kw)

def fasteners(prefix,positions,size=.045,part='hex_bolt'):
    return [p(prefix+str(i),'props','fastener',part,[size,size*.9,size],at,optional=True) for i,at in enumerate(positions)]

def control(key,node,title,maximum=90,minimum=0,axis=(0,1,0),mode='rotation',default=0,nodes=None):
    d={'id':key,'title':title,'node':node,'axis':list(axis),'mode':mode,'min':minimum,
       'max':maximum,'default':default,'unit':'m' if mode=='translation' else 'deg','step':.01 if mode=='translation' else 1}
    if nodes:d['nodes']=nodes
    return d

def port(key,position,normal=(0,1,0),interface='surface',span=None,profile=None):
    tangent=[0,0,1] if abs(normal[0])>.5 else [1,0,0]
    d={'id':key,'position':list(position),'normal':list(normal),'tangent':tangent,
       'interface':interface,'version':1,'units':'m','tolerance':.0001,'allowed_scale':'none','gender':'neutral'}
    if span is not None:d['span']=span
    if profile is not None:d['profile']=list(profile)
    return d

def mounted_port(key,node,position,normal=(0,1,0),interface='l2.robot.mount.v1',span=.22,profile=(.22,.22)):
    return {**port(key,position,normal,interface,span,profile),'frame_node':node}

def ports(domain,size,mount=None,edge=False):
    w,h,d=size;mw,md=(mount or [w,d])
    out=[port('mount',[0,0,0],[0,-1,0],f'l2.{domain}.mount.v1',mw,[mw,md])]
    if edge:
        out.extend([port('west',[-w/2,0,0],[-1,0,0],f'l2.{domain}.edge.v1',d,[0,h]),
                    port('east',[w/2,0,0],[1,0,0],f'l2.{domain}.edge.v1',d,[0,h])])
    out.append(port('service',[0,h,0],[0,1,0],f'l2.{domain}.mount.v1',mw,[mw,md]))
    return out

def register(domain,family,key,name,items,size,*,controls=(),params=None,ports_=None,
             edge=False,mount=None,collision=None,interaction=None,function='',notes=(),animation=True):
    ident=f'l2-{domain}-{family}-{key}'
    if ident in ASSEMBLIES:raise ValueError('Duplicate stable ID '+ident)
    if len(items)<2 or len({i.get('part') for i in items})<2:raise ValueError('L2 requires genuinely different semantic L1 inputs '+ident)
    if len(items)>128:raise ValueError('Subassembly instance budget '+ident)
    for it in items:
        if it.get('part') not in PARTS:raise ValueError('Unresolved reference '+str(it))
    props={'detail':deepcopy(DETAIL),**(params or {})}
    ports_=ports_ or ports(domain,size,mount,edge)
    has_detail=any('enabled' in it or 'detail' in it.get('params',{}) for it in items)
    rt={'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z',
        'origin':'authored-functional-mount','triangle_budget':95000,'collision':collision or {'type':'children','source':'L1 collider recipes; moving-node overrides explicit'},
        'lod':authored_lod() if has_detail else {'levels':[],'reason':'No detachable secondary features'},
        'selection_bounds_are_colliders':False,'engine_adapter_required':True}
    if interaction:rt['interaction']=interaction
    md={'collection':'l2-3.2','theme':'l2-'+domain,'domain':domain,'quality':{'status':'l2','review_scope':'L2','approval':'implemented; not external production certification'},
        'source':{'type':'original_functional_recipe','authoring':'tools/l2_expansion/'+domain+'.py','revision':'3.2.0','license':'project-authored'},
        'runtime':rt,'interfaces':ports_,'state_controls':list(controls),
        'functional':{'schema':'wx.functional-assembly/1.0','family':family,'purpose':function or name,
          'dimensions_m':list(size),'mount_dimensions_m':mount or [size[0],size[2]],
          'assembly_order':[i['id'] for i in items],'serviceable_nodes':[c['node'] for c in controls],
          'counting':'One functional module; style, material, scale, handedness and LOD are not new assets',
          'consumer_responsibility':'Mount frame and rigid state only; physics, gameplay and rigging belong to consumer',
          'notes':list(notes)},'source_bounds':'authoring/l1-bounds.json'}
    if not has_detail:props.pop('detail',None)
    assembly(ident,name,CATEGORIES[domain],items,level=2,params=schema(**props) if props else None,
        ports=ports_,metadata=md,description=(function or name)+'；L1 实例组合，保留 BOM、维护节点和米制安装接口。')
    ASSEMBLIES[ident].update(version='3.2.0',tags=['L2-Expansion',domain,family,key,'functional-subassembly'])
    if animation and controls:
        clips=[]
        for c in controls:
            v=[c['default'],c['max'],c['default']] if c['min']==0 else [c['default'],c['min'],c['max'],c['default']]
            if c['mode']=='rotation':
                # Quaternion keys at 0 and 360 are identical. Subdivide turns
                # before conversion so exported clips actually rotate.
                keys=[v[0]]
                for start,end in zip(v,v[1:]):
                    steps=max(1,math.ceil(abs(end-start)/60))
                    keys.extend(start+(end-start)*j/steps for j in range(1,steps+1))
                v=keys
            tracks=[{'node':n,'axis':c['axis'],'translations' if c['mode']=='translation' else 'degrees':v} for n in c.get('nodes',[c['node']])]
            clips.append({'name':c['id']+'_cycle','duration':3,'tracks':tracks})
        clip(ident,clips)
    ADDED.append(ident);return ident

def finish(domain):
    count=sum(ASSEMBLIES[i]['metadata']['domain']==domain for i in ADDED)
    if count!=TARGETS[domain]:raise ValueError(f'{domain}: {count} instead of {TARGETS[domain]}')
