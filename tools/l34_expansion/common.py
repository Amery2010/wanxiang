"""Production prefab authoring, from retained semantic parts and measured modules.

Author specs are the source of truth. No baked GLB or artwork is an input. One ID
is one topology/function design, never a palette, mirror, seed or LOD variant.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import math, json, hashlib
from foundation.common import PARTS, ASSEMBLIES, MOTIONS, assembly, inst, schema, number, Q, clip
from l1_expansion.common import DOMAIN_NAMES, CATEGORIES
from l2_expansion.common import piece, natural_size, control, port, BOUNDS
from expansion.production import DETAIL, authored_lod
ROOT = Path(__file__).resolve().parents[2]
TARGETS = dict(architecture=83,interior=94,nature=93,terrain=119,props=118,vehicle=64,
               industry=53,character=33,creature=37,robot=25,gameplay=15)
ADDED=[]; SCENES=[]; DESIGNS={}
_MODULE_BOUNDS=json.loads((ROOT/'authoring/l2-bounds.json').read_text())['assets']
BOUNDS.update(json.loads((ROOT/'authoring/l34-legacy-bounds.json').read_text())['assets'])

def reset(): ADDED.clear(); SCENES.clear(); DESIGNS.clear()
def keys(domain,group):return sorted(i.rsplit('.',1)[1] for i in PARTS if i.startswith(f'l1.{domain}.{group}.'))
def l1(domain,group,key):return f'l1.{domain}.{group}.{key}'
def l2(domain,group,key):return f'l2-{domain}-{group}-{key}'
def colormap(ref,color):
    colors=set()
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get('color'),str): colors.add(x['color'])
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(PARTS[ref].get('shape_params',{}))
    return {c:color for c in colors}

def fit(node, ref, size=None, at=(0,0,0), rot=(0,0,0), anchor='bottom', parent=None,
        optional=False, params=None, color=None, material=None, pivot=None):
    """Fit measured default geometry. Animation nodes stay within their subtree."""
    if ref in PARTS:
        ps=deepcopy(params or {})
        dp=PARTS[ref].get('parameter_schema',{}).get('properties',{}).get('detail',{})
        if dp and dp.get('type')!='boolean':ps.setdefault('detail',dp.get('default',1))
        if color:ps['palette']={**ps.get('palette',{}),**colormap(ref,color)}
        if PARTS[ref].get('level')==1:
            return piece(node,ref,size,at,rot,anchor,parent,optional,params=ps,material=material,pivot=pivot)
        # Retained L2 functional components are also legal inputs to a L3 asset.
        # Do not weaken the separate L2 -> L1-only authoring contract.
        record=BOUNDS.get(ref)
        if not record:raise ValueError('Unmeasured retained L2 component '+ref)
        from l2_expansion.common import canonical
        if record['canonical_sha256']!=canonical(PARTS[ref]):raise ValueError('Stale retained L2 bounds '+ref)
        b=record['bounds'];extent=[b[1][j]-b[0][j] for j in range(3)];center=[(b[0][j]+b[1][j])/2 for j in range(3)]
        target=extent if size is None else [v*size for v in extent] if isinstance(size,(int,float)) else size
        anchors={'bottom':[center[0],b[0][1],center[2]],'center':center,'top':[center[0],b[1][1],center[2]],'origin':[0,0,0]}
        if dp and dp.get('type')=='boolean':ps.setdefault('detail',Q('detail'))
        result=inst(node,ref,pos=at,rot=rot,scale=[target[j]/extent[j] for j in range(3)],pivot=pivot or anchors[anchor])
        result['params']=ps
        if parent:result['parent']=parent
        if optional:result['enabled']=Q('detail')
        if material:result['material']=material
        return result
    if ref not in ASSEMBLIES:raise KeyError('Unregistered source '+ref)
    if ref not in _MODULE_BOUNDS:
        if size is not None or anchor not in ('origin','bottom'):raise ValueError('Unmeasured nested assembly '+ref)
        result=inst(node,assembly=ref,pos=at,rot=rot)
    else:
        b=_MODULE_BOUNDS[ref]['bounds'];extent=[b[1][i]-b[0][i] for i in range(3)]
        size=extent if size is None else [v*size for v in extent] if isinstance(size,(int,float)) else size
        center=[(b[0][i]+b[1][i])/2 for i in range(3)]
        anchors={'center':center,'bottom':[center[0],b[0][1],center[2]],'top':[center[0],b[1][1],center[2]],'origin':[0,0,0]}
        result=inst(node,assembly=ref,pos=at,rot=rot,scale=[size[i]/extent[i] for i in range(3)],pivot=pivot or anchors[anchor])
    ps=deepcopy(params or {})
    if 'detail' in ASSEMBLIES[ref].get('metadata',{}).get('parameter_schema',{}).get('properties',{}):ps.setdefault('detail',Q('detail'))
    if ps:result['params']=ps
    if parent:result['parent']=parent
    if optional:result['enabled']=Q('detail')
    return result

def block(node,size,at=(0,0,0),rot=(0,0,0),color='#E4DDCA',material='mat.paint',**kw):
    return fit(node,l1('architecture','stair','closed_tread'),size,at,rot,color=color,material=material,**kw)
def beam(node,a,b,thick=.06,color='#53616A',**kw):
    dx,dy,dz=[b[i]-a[i] for i in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
    if length<1e-7:raise ValueError('Zero beam')
    rot=[-math.degrees(math.asin(dy/length)),math.degrees(math.atan2(dx,dz)),0]
    return block(node,[thick,thick,length],[(a[i]+b[i])/2 for i in range(3)],rot,color=color,anchor='center',**kw)
def legs(w,d,h,t=.06,color='#596974',style='tapered'):
    return [fit(f'leg_{i}',l1('interior','leg',style),[t,h,t],[x,0,z],color=color)
            for i,(x,z) in enumerate(((-w/2,-d/2),(w/2,-d/2),(-w/2,d/2),(w/2,d/2)))]
def radial(ref,n,r,y,size,offset=0,prefix='radial',**kw):
    return [fit(f'{prefix}_{i}',ref,size,[r*math.sin(math.tau*i/n),y,r*math.cos(math.tau*i/n)],
                [0,360*i/n+offset,0],**kw) for i in range(n)]
def inherited_controls(items):
    out=[]
    for it in items:
        if 'assembly' not in it:continue
        for c in ASSEMBLIES[it['assembly']].get('metadata',{}).get('state_controls',[]):
            cc=deepcopy(c);cc['id']=it['id']+'__'+c['id'];cc['node']=it['id']+'.'+c['node']
            if 'nodes' in c:cc['nodes']=[it['id']+'.'+n for n in c['nodes']]
            cc['title']=it['id']+' · '+c['title'];out.append(cc)
    return out

def register(domain,family,key,name,items,size,features,*,controls=(),ports=(),notes=(),rig='none',clip_source=None):
    ident=f'l3-{domain}-{family}-{key}'
    if ident in ASSEMBLIES:raise ValueError('Duplicate '+ident)
    if len(items)<2:raise ValueError('Complete prefab needs constituent parts '+ident)
    if len({i['id'] for i in items})!=len(items):raise ValueError('Repeated node '+ident)
    detail=any('enabled' in i or i.get('params',{}).get('detail')==Q('detail') for i in items)
    controls=[*inherited_controls(items),*deepcopy(controls)]
    rt={'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','origin':'authored-ground-contact',
        'triangle_budget':180000,'collision':{'type':'children'},'lod':authored_lod() if detail else {'levels':[]},
        'selection_bounds_are_colliders':False,'engine_adapter_required':True}
    md={'collection':'l3-3.4','theme':'l3-'+domain,'domain':domain,'quality':{'status':'l3','review_scope':'L3-L4','approval':'authored; see versioned evidence'},
        'source':{'type':'original_production_prefab','authoring':'tools/l34_expansion/'+domain+'.py','revision':'3.4.0','license':'project-authored'},
        'runtime':rt,'state_controls':controls,'production':{'schema':'wx.production-asset/1.0','family':family,
        'purpose':name,'dimensions_design_m':list(size),'footprint_m':[size[0],size[2]],'features':list(features),
        'rig':rig,'notes':list(notes),'counting':'distinct functional topology; excludes palette, scale, handedness, seed and LOD',
        'render_contract':'editable nodes and source references retained; no CAD boolean union',
        'interaction_contract':'rigid and inherited clips are previews; consumer owns physics and gameplay'}}
    assembly(ident,name,CATEGORIES[domain],items,3,schema(detail=deepcopy(DETAIL)) if detail else None,
        ports or [port('ground',[0,0,0],[0,-1,0])],description=name+'；'+ ' / '.join(features),metadata=md)
    ASSEMBLIES[ident].update(version='3.4.0',tags=['L3',domain,family,key,*features])
    if clip_source:
        m=deepcopy(MOTIONS[clip_source]);m['assembly']=ident;MOTIONS[ident]=m
    # Only explicit new controls need local author tracks. Nested module clips
    # are collected by the runtime with their original hierarchy namespaces.
    explicit=[c for c in controls if '__' not in c['id']]
    if explicit and not clip_source:
        cs=[]
        for c in explicit:
            vs=[c.get('default',0),c['max'],c.get('default',0)]
            if c['mode']=='rotation':
                vals=[vs[0]]
                for a,b in zip(vs,vs[1:]):
                    n=max(1,math.ceil(abs(b-a)/60));vals += [a+(b-a)*i/n for i in range(1,n+1)]
                vs=vals
            cs.append({'name':c['id']+'_inspect','duration':3,'tracks':[{'node':n,'axis':c['axis'],'translations' if c['mode']=='translation' else 'degrees':vs} for n in c.get('nodes',[c['node']])]})
        clip(ident,cs)
    ADDED.append(ident);DESIGNS[ident]={'domain':domain,'family':family,'name':name,'size':size,'features':list(features)}
    return ident

def finish(domain):
    n=sum(DESIGNS[i]['domain']==domain for i in ADDED)
    if n!=TARGETS[domain]:raise ValueError(f'{domain} expected {TARGETS[domain]}, authored {n}')
