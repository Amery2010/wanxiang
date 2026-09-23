"""Versioned module interfaces and authored runtime metadata.

This is not a physics engine. Collider recipes are explicit local-space author
intent; selection bounds never silently become solid world colliders.
"""
from __future__ import annotations
import re
import copy,math
from .util import ROOT,read_json
from .errors import WXError
INTERFACES={
 'terrain.edge.1m.v1':{'group':'terrain','grid':1,'tolerance':.0001},
 'terrain.river.2m.v1':{'group':'river','span':2,'tolerance':.0001},
 'road.lane.3m.v1':{'group':'road','span':3,'tolerance':.0001},
 'road.sidewalk.1m.v1':{'group':'sidewalk','span':1,'tolerance':.0001},
 'rail.standard.v1':{'group':'rail','gauge':1.435,'tolerance':.0001},
 'arch.wall.1m.v1':{'group':'architecture','grid':1,'tolerance':.0001},
 'arch.floor.1m.v1':{'group':'architecture','grid':1,'tolerance':.0001},
 'arch.door.v1':{'group':'door','tolerance':.001},
 'pipe.flange.small.v1':{'group':'pipe','diameter':.10,'tolerance':.0001},
 'pipe.flange.medium.v1':{'group':'pipe','diameter':.25,'tolerance':.0001},
 'vehicle.wheel.v1':{'group':'wheel','tolerance':.001},
 'character.hand.grip.v1':{'group':'grip','tolerance':.001},
 'character.back.mount.v1':{'group':'wear','tolerance':.001},
 'gameplay.trigger.v1':{'group':'trigger','tolerance':.001},
 'fx.emitter.v1':{'group':'fx','tolerance':.001},
}
# L2 root-frame interfaces carry explicit spans/profiles in every recipe. They
# do not imply that arbitrary assemblies in a domain are mechanically compatible.
for domain in ('architecture','interior','nature','terrain','props','vehicle','industry','character','creature','robot','gameplay'):
    for use in ('mount','edge'):
        INTERFACES[f'l2.{domain}.{use}.v1']={'group':domain,'tolerance':.0001}

for k,v in INTERFACES.items():v.update(id=k,version=1,units='m',allowed_scale='none',gender='neutral',normal_rule='opposed',tangent_rule='aligned')

def validate_connector(s):
    from .kit_parts import frame
    # Legacy MeshIR joints expose axis; versioned authored connectors expose normal.
    # Accept that documented alias without mutating a caller's socket dictionary.
    frame({**s,'normal':s.get('normal',s.get('axis')),'tangent':s.get('tangent',[1,0,0])})
    t=s.get('interface','surface')
    if t not in INTERFACES:
        if t.startswith(('terrain.','road.','rail.','arch.','pipe.','vehicle.','character.','gameplay.','fx.','l2.')):raise WXError('RECIPE_INVALID','Unknown versioned interface '+t)
        return True
    if t.startswith('l2.') and (s.get('span') is None or not isinstance(s.get('profile'),list) or len(s['profile'])!=2):raise WXError('RECIPE_INVALID','L2 interfaces require explicit span and two-value profile')
    if s.get('units','m')!='m':raise WXError('RECIPE_INVALID','Versioned interfaces use metres')
    if s.get('allowed_scale','none') not in ('none','uniform'):raise WXError('RECIPE_INVALID','Unknown scale policy')
    for field in ('gauge','diameter','tolerance'):
        if field in s and (not isinstance(s[field],(int,float)) or not math.isfinite(s[field]) or s[field]<=0):raise WXError('RECIPE_INVALID','Invalid interface '+field)
    if s.get('version',INTERFACES[t]['version'])!=INTERFACES[t]['version']:raise WXError('RECIPE_INVALID','Interface version field mismatch')
    if s.get('gender','neutral') not in ('neutral','male','female'):raise WXError('RECIPE_INVALID','Invalid interface gender')
    for k in ['normal','tangent']:
        n=sum(float(x)**2 for x in s[k])
        if abs(n-1)>1e-5:raise WXError('RECIPE_INVALID','Interface axes must be unit length: '+s['id'])
    if abs(sum(a*b for a,b in zip(s['normal'],s['tangent'])))>1e-5:raise WXError('RECIPE_INVALID','Interface tangent must be perpendicular')
    if s.get('span') is not None and (not isinstance(s['span'],(int,float)) or not math.isfinite(s['span']) or s['span']<=0):raise WXError('RECIPE_INVALID','Invalid interface span')
    if s.get('profile') is not None and (not isinstance(s['profile'],list) or len(s['profile'])<2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in s['profile'])):raise WXError('RECIPE_INVALID','Invalid edge profile')
    return True

def compatibility(a,b):
    ia,ib=a.get('interface','surface'),b.get('interface','surface')
    if ia!=ib:
        # Legacy generic surface matching remains compatible only for legacy ports.
        if 'surface' in (ia,ib) and ia not in INTERFACES and ib not in INTERFACES:return {'compatible':True,'reason':'legacy-surface'}
        return {'compatible':False,'reason':'interface/version mismatch'}
    if ia not in INTERFACES:return {'compatible':True,'reason':'legacy-interface'}
    validate_connector(a);validate_connector(b);tol=min(INTERFACES[ia]['tolerance'],a.get('tolerance',float('inf')),b.get('tolerance',float('inf')))
    ga,gb=a.get('gender','neutral'),b.get('gender','neutral')
    if ga!='neutral' and ga==gb:return {'compatible':False,'reason':'connector gender mismatch'}
    for port in (a,b):
        scale=port.get('world_scale',[1,1,1]);policy=port.get('allowed_scale',INTERFACES[ia]['allowed_scale'])
        if len(scale)!=3 or any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in scale):return {'compatible':False,'reason':'invalid world scale'}
        if policy=='none' and any(abs(v-1)>tol for v in scale):return {'compatible':False,'reason':'interface forbids transformed scale; resize authored geometry instead'}
        if policy=='uniform' and max(scale)-min(scale)>tol:return {'compatible':False,'reason':'interface allows uniform scale only'}
    for key in ('span','gauge','diameter'):
        va=a.get(key,INTERFACES[ia].get(key));vb=b.get(key,INTERFACES[ia].get(key))
        if va is not None and vb is not None and abs(va-vb)>tol:return {'compatible':False,'reason':key+' mismatch'}
    if a.get('profile') is not None and b.get('profile') is not None:
        pa,pb=a['profile'],b['profile']
        if len(pa)!=len(pb) or any(abs(x-y)>tol for x,y in zip(pa,pb)):return {'compatible':False,'reason':'edge profile mismatch'}
    return {'compatible':True,'reason':'matched version, dimensions and edge profile','tolerance_m':tol}

def catalog_metadata(d,kind,parts=None,assemblies=None,seen=None):
    md=d.get('runtime',{}) if kind=='part' else d.get('metadata',{}).get('runtime',{})
    ports=d.get('connectors',[]) if kind=='part' else d.get('metadata',{}).get('interfaces',[])
    types=set(p['interface'] for p in ports if p.get('interface') in INTERFACES)
    if kind=='assembly' and parts is not None:
        seen=set(seen or ());seen.add(d['id'])
        nodes={i['id']:i for i in d.get('instances',[])}
        def exported_socket(obj,name,path):
            if 'shape_params' in obj:
                if not isinstance(name,str):
                    # A conditional export is indexed by all allowed interface types.
                    names=set(name.get('cases',{}).values()) if isinstance(name,dict) else set()
                    return next((p for p in obj.get('connectors',[]) if p['id'] in names),None)
                return next((p for p in obj.get('connectors',[]) if p['id']==name),None)
            if obj['id'] in path:return None
            ex=next((e for e in obj.get('exports',[]) if e['id']==name),None)
            if not ex:return None
            if 'position' in ex:return ex
            node=next((i for i in obj.get('instances',[]) if i['id']==ex['node']),None)
            if not node:return None
            child=(parts if 'part' in node else assemblies).get(node.get('part',node.get('assembly')))
            return exported_socket(child,ex['socket'],path|{obj['id']}) if child else None
        for e in d.get('exports',[]):
            p=exported_socket(d,e['id'],set())
            if p and p.get('interface') in INTERFACES:types.add(p['interface'])
    collision=md.get('collision',{})
    def motion_type(obj,trail=None):
        trail=set(trail or ())
        if obj['id'] in trail:return 'static'
        trail.add(obj['id'])
        if obj.get('shape_params',{}).get('rig'):return 'skinned'
        types={'rigid' if obj.get('metadata',{}).get('state_controls') else 'static'}
        for child in obj.get('shape_params',{}).get('components',[])+obj.get('instances',[]):
            target=(parts or {}).get(child.get('part')) or (assemblies or {}).get(child.get('assembly'))
            if target:types.add(motion_type(target,trail))
        return 'skinned' if 'skinned' in types else 'rigid' if 'rigid' in types else 'static'
    return {'interfaces':sorted(types),'collision':bool(collision and collision.get('type')!='none'),'collision_type':collision.get('type','unspecified'),'lod':bool(md.get('lod',{}).get('levels')),'lod_levels':md.get('lod',{}).get('levels',[]),'motion':motion_type(d),'styles':['lowpoly','toon','voxel'],'budget':md.get('triangle_budget'),'tags':d.get('tags',[])}

def search(interface=None,theme=None,level=None,collision=None,lod=None,kind=None,query=''):
    records=read_json(ROOT/'library/registry.json')['records'];result=[]
    for r in records:
        rt=r.get('runtime',{})
        if interface and interface not in rt.get('interfaces',[]):continue
        if theme and r['theme']!=theme:continue
        if level and r['level']!=int(level):continue
        if collision is not None and rt.get('collision',False)!=collision:continue
        if lod is not None and rt.get('lod',False)!=lod:continue
        if kind and r['kind']!=kind:continue
        if query.lower() not in (r['id']+' '+r['name']+' '+' '.join(rt.get('tags',[]))).lower():continue
        result.append(r)
    return result

def validate_runtime(md):
    if not md:return True
    if not isinstance(md,dict) or md.get('schema')!='wx.runtime-metadata/1.0':raise WXError('RECIPE_INVALID','Unsupported runtime metadata schema')
    if md.get('units')!='m' or md.get('up')!='+Y' or md.get('forward')!='+Z':raise WXError('RECIPE_INVALID','Runtime metadata must use metre/+Y/+Z coordinates')
    budget=md.get('triangle_budget')
    if budget is not None and (not isinstance(budget,int) or isinstance(budget,bool) or budget<1 or budget>400000):raise WXError('RECIPE_INVALID','Invalid runtime triangle budget')
    def collider(col):
        if not isinstance(col,dict) or col.get('type') not in ('none','box','sphere','capsule','convex-hull','compound','authored-mesh','heightfield','children'):raise WXError('RECIPE_INVALID','Unsupported collision recipe')
        if col.get('type') in ('authored-mesh','heightfield') and col.get('static_only') is not True:raise WXError('RECIPE_INVALID','Concave collision must be static-only')
        def vector(v,positive=False):
            return isinstance(v,list) and len(v)==3 and all(isinstance(n,(int,float)) and math.isfinite(n) and (n>0 if positive else True) for n in v)
        if col['type']=='box' and (not vector(col.get('size'),True) or not vector(col.get('center',[0,0,0]))):raise WXError('RECIPE_INVALID','Invalid box collision recipe')
        if col['type'] in ('sphere','capsule') and (not isinstance(col.get('radius'),(int,float)) or not math.isfinite(col['radius']) or col['radius']<=0):raise WXError('RECIPE_INVALID','Invalid collider radius')
        if col['type']=='sphere' and not vector(col.get('center',[0,0,0])):raise WXError('RECIPE_INVALID','Invalid sphere centre')
        if col['type']=='capsule' and (not vector(col.get('segment_start')) or not vector(col.get('segment_end'))):raise WXError('RECIPE_INVALID','Invalid capsule endpoints')
        if col['type']=='compound':
            if not isinstance(col.get('shapes'),list) or not 1<=len(col['shapes'])<=128:raise WXError('RECIPE_INVALID','Compound collision shape budget')
            for shape in col['shapes']:collider(shape)
    collider(md.get('collision',{'type':'none'}))
    hook=md.get('interaction')
    if hook is not None:
        if not isinstance(hook,dict) or hook.get('schema')!='wx.interaction/1.0' or hook.get('authority')!='consumer-game':
            raise WXError('RECIPE_INVALID','Interaction schema / authority contract')
        for field in ('kind','event'):
            value=hook.get(field)
            if not isinstance(value,str) or not re.fullmatch(r'[a-z][a-z0-9_.-]{0,79}',value):raise WXError('RECIPE_INVALID','Invalid interaction '+field)
        trigger=hook.get('trigger',{'shape':'none'})
        if not isinstance(trigger,dict) or trigger.get('shape') not in ('none','box','sphere'):raise WXError('RECIPE_INVALID','Invalid interaction trigger')
        if trigger['shape']!='none':collider({**trigger,'type':trigger['shape']})
        fragments=hook.get('fragments')
        if fragments is not None and (not isinstance(fragments,list) or len(fragments)>256 or any(not isinstance(i,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,95}',i) for i in fragments) or len(set(fragments))!=len(fragments)):
            raise WXError('RECIPE_INVALID','Invalid independent fragment nodes')
    if 'helper_only' in md and not isinstance(md['helper_only'],bool):raise WXError('RECIPE_INVALID','helper_only must be boolean')
    seen=set()
    for level in md.get('lod',{}).get('levels',[]):
        n=level.get('level')
        if n not in (0,1,2) or n in seen or not isinstance(level.get('parameters',{}),dict):raise WXError('RECIPE_INVALID','Invalid or duplicate LOD level')
        seen.add(n)
        if 'screen_height' in level and not 0<level['screen_height']<=1:raise WXError('RECIPE_INVALID','Invalid LOD screen height')
    return True

def world_socket(s,matrix):
    """Transform an explicit port without dropping its size/profile contract."""
    import numpy as np
    from .kit_parts import frame
    m=np.asarray(matrix,float);f=m@frame(s);out=copy.deepcopy(s)
    tangent=f[:3,0];normal=np.linalg.inv(m[:3,:3]).T@np.asarray(s['normal'],float);sx=float(np.linalg.norm(tangent));sn=float(np.linalg.norm(normal))
    out.update(position=f[:3,3].tolist(),normal=(normal/sn).tolist(),tangent=(tangent/sx).tolist())
    for field in ('span','gauge','diameter'):
        value=s.get(field,INTERFACES.get(s.get('interface'),{}).get(field))
        if value is not None:out[field]=value*sx
    if out.get('profile') is not None:
        sy=float(np.linalg.norm(m[:3,:3]@np.array([0,1,0.])))
        out['profile']=[v*sy for v in out['profile']]
    out['world_scale']=[float(np.linalg.norm(m[:3,k])) for k in range(3)]
    return out

def compatible_parts(source_part,socket_id,params=None):
    """Resolve default candidate parameters; metadata type matches are only a prefilter."""
    from .kit_parts import build_part
    source=build_part(source_part,params=params).sockets
    a=next((s for s in source if s['id']==socket_id),None)
    if not a:raise WXError('RECIPE_INVALID','Source socket does not exist: '+socket_id)
    rows=[]
    for r in search(interface=a.get('interface'),kind='part'):
        candidate=build_part(r['id'])
        matches=[s['id'] for s in candidate.sockets if compatibility(a,s)['compatible']]
        if matches:rows.append({'id':r['id'],'name':r['name'],'sockets':matches,'parameter_scope':'candidate defaults; validate again after editing'})
    return rows
