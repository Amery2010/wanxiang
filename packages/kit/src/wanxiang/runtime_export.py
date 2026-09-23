"""Safe optional game-runtime static batching; editable source is never mutated.

Keeps animated/skinned/constraint/transparent subtrees, node IDs and sockets.
Each merged triangle range maps back to a source mesh node. This reduces potential
opaque draw submissions, not polygon count; memory and coarse culling may increase.
"""
from __future__ import annotations
from pathlib import Path
import copy,json
import numpy as np
from .ir import AssetIR,Mesh
from .kit_assembly import get_template,Assembler,apply_build_parameters,materials_for
from .materials import ensure_material
from .util import ROOT,read_json,write_json
from .glb import export_glb
from .rigid_motion import tracks_for
from .validation import inspect_asset
from .errors import WXError


def protected_nodes(asset:AssetIR,spec:dict)->set[str]:
    protected=set();children={n['id']:[] for n in asset.nodes}
    for n in asset.nodes:
        if n.get('parent'):children[n['parent']].append(n['id'])
    def mark(i):
        if i not in children:return
        protected.add(i)
        for c in children[i]:mark(c)
    # Skin bind nodes and bone descendants (including hats/gear) cannot be baked.
    for n in asset.nodes:
        if n.get('skin') or n.get('role')=='bone':mark(n['id'])
    def visit(s,prefix='',depth=0):
        if depth>12:raise WXError('BUDGET_EXCEEDED','Runtime dependency depth')
        md=s.get('metadata',{})
        for fragment in md.get('runtime_fragment_nodes',[]):mark(prefix+fragment)
        for c in md.get('state_controls',[]):
            for ident in c.get('nodes',[c.get('node')]):
                if ident:mark(prefix+ident)
        for c in md.get('struts',[]):
            for ident in [c['node'],c['from']['node'],c['to']['node']]:mark(prefix+ident)
        motion=ROOT/'library/motions'/(s.get('id','')+'.json')
        if motion.is_file():
            for clip in read_json(motion).get('clips',[]):
                for track in clip.get('tracks',[]):mark(prefix+track['node'])
        for it in s.get('instances',[]):
            if 'assembly' in it:visit(get_template(it['assembly']),prefix+it['id']+'.',depth+1)
            elif it.get('part'):
                from .kit_parts import definition
                if definition(it['part']).get('runtime',{}).get('helper_only'):mark(prefix+it['id'])
    visit(spec)
    return protected


def batch_static(asset:AssetIR,spec:dict,min_group=2):
    if min_group<2:raise WXError('INPUT_INVALID','Batch minimum must be at least two meshes')
    out=copy.deepcopy(asset);world=out.world_matrices();protected=protected_nodes(out,spec)
    groups={};unchanged=[]
    for n in out.nodes:
        if not n.get('mesh'):continue
        material,_=ensure_material(n['material'])
        m=out.meshes[n['mesh']]
        if n['id'] in protected or m.skin_weights is not None or material.get('alphaMode','OPAQUE')!='OPAQUE':
            unchanged.append(n['id']);continue
        groups.setdefault(n['material'],[]).append(n)
    batches=[];sources=[];before_meshes=sum(bool(n.get('mesh')) for n in out.nodes)
    before_tri=sum(len(out.meshes[n['mesh']].faces) for n in out.nodes if n.get('mesh'))
    serial=0
    for material,nodes in sorted(groups.items()):
        if len(nodes)<min_group:
            unchanged.extend(n['id'] for n in nodes);continue
        name='runtime.batch.'+str(serial);serial+=1
        while any(n['id']==name for n in out.nodes):name+='x'
        vv=[];ff=[];nn=[];uu=[];cc=[];vbase=0;tbase=0;ranges=[]
        for n in nodes:
            mesh=out.meshes[n['mesh']].transformed(world[n['id']]);nv=len(mesh.vertices);nt=len(mesh.faces)
            row={'source_node':n['id'],'source_mesh':n['mesh'],'batch_node':name,'vertex_start':vbase,'vertex_count':nv,'triangle_start':tbase,'triangle_count':nt,'world_aabb':[mesh.vertices.min(0).tolist(),mesh.vertices.max(0).tolist()]}
            ranges.append(row);sources.append(row)
            vv.append(mesh.vertices);ff.append(mesh.faces+vbase);nn.append(mesh.normals);uu.append(mesh.uv);cc.append(mesh.colors if mesh.colors is not None else np.ones_like(mesh.vertices));vbase+=nv;tbase+=nt
            # Keep semantic node, local transform and children for tools/sockets.
            n['runtime_source_mesh']=n.pop('mesh');n['runtime_batch']=name
            n.pop('material',None);n.pop('topology',None)
        mesh=Mesh(np.vstack(vv),np.vstack(ff),np.vstack(nn),np.vstack(uu),np.vstack(cc))
        out.add(name,mesh,material=material,parent=None,role='runtime_static_batch',topology='source-surfaces')
        batches.append({'node':name,'material':material,'source_meshes':len(nodes),'triangles':tbase,'sources':ranges})
    used={n['mesh'] for n in out.nodes if n.get('mesh')};out.meshes={k:v for k,v in out.meshes.items() if k in used}
    after_meshes=sum(bool(n.get('mesh')) for n in out.nodes);after_tri=sum(len(out.meshes[n['mesh']].faces) for n in out.nodes if n.get('mesh'))
    if before_tri!=after_tri or not np.allclose(out.bounds(),asset.bounds(),atol=3e-5):raise WXError('OUTPUT_MISMATCH','Runtime batching changed geometric bounds/count')
    report={'schema':'wx.runtime-map/1.0','version':'2.0.0','strategy':'opaque static-only, semantic nodes retained, world-space batches','potential_draws_before':before_meshes,'potential_draws_after':after_meshes,'draws_saved':before_meshes-after_meshes,'triangles_before':before_tri,'triangles_after':after_tri,'unchanged_mesh_nodes':unchanged,'protected_nodes':sorted(protected),'batches':batches,'source_mutated':False,'limitations':['Potential submissions, not a hardware FPS measurement.','Shared instance geometry becomes batch-local copies; file/memory size may grow.','Batches have coarser culling boundaries. Transparent and movable nodes remain unbatched.','AABB output is a selection/broad-phase index, not automatic solid-room or boat collision.']}
    out.metadata=copy.deepcopy(out.metadata);out.metadata['runtime_export']={k:v for k,v in report.items() if k not in ('batches','protected_nodes','unchanged_mesh_nodes')}
    for n in out.nodes:
        if n.get('runtime_batch'):n['runtime_source_kind']='geometry moved to immutable batch; original node retained'
    return out,report


def export_runtime(ident:str,outdir:str|Path,params=None):
    target=Path(outdir)
    if target.exists() and any(target.iterdir()):raise WXError('INPUT_INVALID','Use a new runtime-export directory')
    target.mkdir(parents=True,exist_ok=True)
    spec=apply_build_parameters(get_template(ident),params or {});original=Assembler().assemble(spec)
    batched,report=batch_static(original,spec)
    clips=tracks_for(original,ident)
    p=target/'runtime.glb';export_glb(batched,materials_for(batched),p,animations=clips)
    checks=inspect_asset(p,expected=batched,independent=True)
    if not checks['passed']:raise WXError('VALIDATION_FAILED','Runtime GLB failed validation',details=checks)
    write_json(target/'runtime-map.json',report);write_json(target/'source.assembly.json',spec);write_json(target/'inspection.json',checks)
    # Original source mesh boxes include holes/cavities; mark their purpose explicitly.
    world=original.world_matrices();bounds=[]
    for n in original.nodes:
        if not n.get('mesh'):continue
        m=original.meshes[n['mesh']].transformed(world[n['id']]);bounds.append({'node':n['id'],'aabb':[m.vertices.min(0).tolist(),m.vertices.max(0).tolist()]})
    write_json(target/'selection-bounds.json',{'schema':'wx.broadphase/1.0','solid_collision_approved':False,'purpose':'selection and broad-phase only; replace with authored colliders in a physics project','boxes':bounds})
    return {'id':ident,'path':str(p),'passed':True,'bytes':p.stat().st_size,'triangles':checks['triangles'],'draws_before':report['potential_draws_before'],'draws_after':report['potential_draws_after'],'runtime_map':str(target/'runtime-map.json'),'static_only':True,'source_preserved':True}
