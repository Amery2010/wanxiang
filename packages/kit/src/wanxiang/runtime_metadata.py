"""Engine-neutral collision / LOD exports. No inferred solid selection boxes.

Author recipes retain metre-space node transforms. Explicit mesh proxies are
cooked only for recipes requesting them, and never for decorative leaves/water.
"""
from __future__ import annotations
import copy
from pathlib import Path
import numpy as np
from .util import ROOT,write_json,read_json,sha256
from .errors import WXError
from .semantic import evaluate,parameter_values

def lod_parameters(ident,kind,level):
    folder='parts' if kind=='part' else 'assemblies';d=read_json(ROOT/'library'/folder/(ident+'.json'))
    md=d.get('runtime',{}) if kind=='part' else d.get('metadata',{}).get('runtime',{})
    levels=md.get('lod',{}).get('levels',[])
    match=next((l for l in levels if l['level']==int(level)),None)
    if match is None:raise WXError('INPUT_INVALID',f'{ident} has no authored LOD {level}')
    return copy.deepcopy(match.get('parameters',{}))

def describe(asset,spec,include_meshes=True):
    from .kit_parts import definition
    worlds=asset.world_matrices();nodes={n['id']:n for n in asset.nodes};rows=[];meshes={}
    instance_ids={entry['instance'] for entry in asset.metadata.get('bom',[])}
    def below(node,parent):
        while node in nodes:
            if node==parent:return True
            if node in instance_ids:return False
            node=nodes[node].get('parent')
        return False
    collision_boundaries=[]
    def boundaries(current,prefix='',depth=0):
        if depth>12:raise WXError('BUDGET_EXCEEDED','Collision policy depth')
        info=current.get('metadata',{});values=parameter_values(info.get('parameter_schema',{}),info.get('parameters',{}));current=evaluate(current,values)
        collision=current.get('metadata',{}).get('runtime',{}).get('collision',{})
        if collision.get('type') not in (None,'children'):collision_boundaries.append((prefix,collision))
        for it in current.get('instances',[]):
            if it.get('enabled',True) is False:continue
            if it.get('assembly'):
                child=read_json(ROOT/'library/assemblies'/(it['assembly']+'.json'))
                if it.get('params'):child.setdefault('metadata',{})['parameters']={**child.get('metadata',{}).get('parameters',{}),**it['params']}
                boundaries(child,prefix+it['id']+'.',depth+1)
    boundaries(spec)
    for entry in asset.metadata.get('bom',[]):
        ident=entry['part'];d=definition(ident);params=entry.get('params',{});vals=parameter_values(d.get('parameter_schema',{}),params)
        md=evaluate(d.get('runtime',{}),vals);recipe=copy.deepcopy(entry.get('collision_override',md.get('collision',{'type':'unspecified','reason':'legacy part: no authored collider'})))
        node=entry['instance']
        parents=[(prefix,col) for prefix,col in collision_boundaries if node.startswith(prefix)]
        if parents:
            prefix,col=min(parents,key=lambda pair:len(pair[0]))
            recipe={'type':'none','reason':'Assembly collision policy replaces children','assembly_node':prefix[:-1] or 'root','assembly_collision_type':col['type']}
        content=nodes.get(node,{}).get('content_node',node);transform=worlds.get(content,np.eye(4));scale=np.asarray(params.get('size',d['size']))/np.asarray(d['size'])
        row={'node':node,'content_node':content,'part':ident,'collision':recipe,'node_world_matrix':transform.tolist(),'parameter_size_scale':scale.tolist(),'lod':md.get('lod',{}),'interaction':md.get('interaction'),'helper_only':md.get('helper_only',False)}
        # Mesh proxies are not substituted for box/capsule recipes. Non-solid
        # water/foliage stays non-solid. Static concave proxies preserve openings.
        if include_meshes and recipe['type'] in ('heightfield','authored-mesh','convex-hull'):
            vertices=[];faces=[];offset=0;inv=np.linalg.inv(transform)
            for n in asset.nodes:
                if not n.get('mesh') or not below(n['id'],node):continue
                material=n.get('material','').split('--')[0]
                if recipe['type']!='convex-hull' and any(t in material for t in ['water','leaf','glass','emissive']):continue
                m=asset.meshes[n['mesh']].transformed(inv@worlds[n['id']]);vertices.extend(m.vertices.tolist());faces.extend((m.faces+offset).tolist());offset+=len(m.vertices)
            if vertices:
                v=np.array(vertices,float);f=np.array(faces,int)
                if recipe['type']=='convex-hull':
                    import trimesh
                    try:mesh=trimesh.Trimesh(v,f,process=True).convex_hull;v,f=mesh.vertices,mesh.faces
                    except Exception as e:raise WXError('GEOMETRY_INVALID','Collider convex hull failed: '+ident) from e
                key='proxy-'+str(len(meshes));meshes[key]={'positions':np.round(v,7).tolist(),'triangles':f.tolist(),'space':'component-local','static_only':recipe['type']!='convex-hull'};row['mesh']=key
        rows.append(row)
    interactions=[];assembly_colliders=[]
    def assembly_hooks(current,prefix='',depth=0):
        if depth>12:raise WXError('BUDGET_EXCEEDED','Interaction dependency depth')
        info=current.get('metadata',{});values=parameter_values(info.get('parameter_schema',{}),info.get('parameters',{}));current=evaluate(current,values)
        md=current.get('metadata',{}).get('runtime',{})
        node=prefix[:-1] if prefix else 'root'
        if md.get('collision',{}).get('type') not in (None,'children'):
            assembly_colliders.append({'node':node,'node_world_matrix':worlds.get(node,np.eye(4)).tolist(),'collision':md['collision'],'child_collision_policy':'replace-children'})
        if md.get('interaction'):
            node=prefix[:-1] if prefix else 'root'
            hook=copy.deepcopy(md['interaction'])
            if isinstance(hook.get('target_node'),str):hook['target_node']=prefix+hook['target_node']
            if isinstance(hook.get('fragments'),list):hook['fragments']=[prefix+i for i in hook['fragments']]
            interactions.append({'node':node,'node_world_matrix':worlds.get(node,np.eye(4)).tolist(),'interaction':hook})
        for it in current.get('instances',[]):
            if it.get('enabled',True) is False:continue
            if it.get('assembly'):
                child=read_json(ROOT/'library/assemblies'/(it['assembly']+'.json'))
                if it.get('params'):child.setdefault('metadata',{})['parameters']={**child.get('metadata',{}).get('parameters',{}),**it['params']}
                assembly_hooks(child,prefix+it['id']+'.',depth+1)
    assembly_hooks(spec)
    return {'schema':'wx.collider-set/1.0','asset':spec.get('id',spec.get('part')),'units':'m','up':'+Y','selection_bounds_are_colliders':False,'engine_adapter_required':True,'instances':rows,'assembly_interactions':interactions,'assembly_colliders':assembly_colliders,'meshes':meshes,'limitations':['Recipes require a target-engine adapter; this file is not a physics engine scene.','Non-uniform capsule scale requires conversion to a supported engine shape.','Unspecified legacy geometry is NOT silently treated as a solid AABB.','Static triangle proxies are not dynamic rigid-body colliders.']}

def export_lods(ident,kind,out,style='lowpoly',review=False):
    from .kit_assembly import build
    d=read_json(ROOT/'library'/('parts' if kind=='part' else 'assemblies')/(ident+'.json'))
    md=d.get('runtime',{}) if kind=='part' else d.get('metadata',{}).get('runtime',{})
    levels=md.get('lod',{}).get('levels',[])
    if not levels:raise WXError('INPUT_INVALID','No authored LODs for '+ident)
    result=[]
    for level in levels:
        r=build(id=ident,part=kind=='part',style=style,params=level['parameters'],out=Path(out)/('LOD'+str(level['level'])),review=review)
        result.append({**level,'triangles':r['triangles'],'sha256':r['sha256'],'glb':str(Path(r['glb']).relative_to(Path(out))),'passed':r['passed']})
    report={'schema':'wx.lod-set/1.0','id':ident,'style':style,'levels':result,'automatic_runtime_switching':False,'passed':all(r['passed'] for r in result)}
    write_json(Path(out)/'lod-set.json',report);return report
