"""Granular, reusable model parts: geometry + local connector frames, not whole props.
All dimensions are metres; +Y up, +Z forward. No script evaluation in JSON.
"""
from __future__ import annotations
from .paths import require_resources
from .paths import require_source
from .paths import code_path, WORKSPACE_ROOT
import copy, math
from pathlib import Path
import numpy as np
from . import geometry as G
from .ir import Mesh, AssetIR, concat
from .util import ROOT, read_json, write_json, safe_id, sha256
from .errors import WXError

PART_DIR=ROOT/'library/parts'
STYLES=('lowpoly','toon','voxel','rounded','pixel')
def canonical_style(style):
    style={'rounded':'toon','pixel':'voxel'}.get(style,style)
    if style not in ('lowpoly','toon','voxel'):raise WXError('RECIPE_INVALID','Style must be lowpoly, toon or voxel')
    return style


def connector(name,position,normal=(0,1,0),tangent=(1,0,0),interface='surface',extent=None):
    return {'id':name,'position':list(position),'normal':list(normal),'tangent':list(tangent),'interface':interface,'extent':extent}


def frame(connector):
    p=np.asarray(connector['position'],float);z=np.asarray(connector['normal'],float);x=np.asarray(connector['tangent'],float)
    if any(a.shape!=(3,) or not np.isfinite(a).all() for a in (p,z,x)) or np.linalg.norm(z)<1e-8:raise WXError('RECIPE_INVALID','Invalid connector frame')
    z/=np.linalg.norm(z);x=x-z*np.dot(x,z)
    if np.linalg.norm(x)<1e-8:raise WXError('RECIPE_INVALID','Connector tangent is parallel to normal')
    x/=np.linalg.norm(x);y=np.cross(z,x);m=np.eye(4);m[:3,:3]=np.column_stack([x,y,z]);m[:3,3]=p;return m


def definition(id):
    require_resources()
    from .retirement import refuse
    refuse(id,'part')
    p=PART_DIR/(safe_id(id)+'.json')
    if not p.is_file():raise WXError('RECIPE_INVALID',f'Part not found: {id}')
    d=read_json(p)
    if d.get('schema')!='wx.part/1.0':raise WXError('RECIPE_INVALID','Unsupported granular part schema')
    return d


def build_part(id,style='lowpoly',params=None,material=None):
    d=definition(id);params=dict(params or {});style=canonical_style(style)
    if style not in STYLES:raise WXError('RECIPE_INVALID','Style must be lowpoly, toon or voxel')
    from .semantic import parameter_values
    from .semantic import evaluate
    from .contracts import validate_runtime
    resolved_runtime=evaluate(d.get('runtime',{}),parameter_values(d.get('parameter_schema',{}),params))
    validate_runtime(resolved_runtime)
    size=np.asarray(params.get('size',d['size']),float)
    if size.shape!=(3,) or not np.isfinite(size).all() or np.any(size<=0) or np.any(size>100):raise WXError('BUDGET_EXCEEDED','Part size must be finite, positive and <=100m per axis')
    from .live_geometry import build_mesh
    me=build_mesh(d,style,params)
    base=d.get('material','mat.matte'); styled=base+('' if style=='lowpoly' else '--'+style)
    mat=material or (styled if base.startswith('mat.') or (ROOT/'library/materials'/styled/'material.json').is_file() else base)
    # Any material must be locally present; do not accept remote resource indirection.
    from .materials import ensure_material
    ensure_material(safe_id(mat))
    a=AssetIR();a.group('root',role='part_root')
    if me.rig:
        by={b['name']:b for b in me.rig}
        if len(by)!=len(me.rig):raise WXError('GEOMETRY_INVALID','Duplicate bone names')
        for bone in me.rig:
            parent=bone.get('parent')
            if parent and parent not in by:raise WXError('GEOMETRY_INVALID','Missing bone parent')
            position=np.asarray(bone['position'])-(np.asarray(by[parent]['position']) if parent else 0)
            a.group('rig.'+bone['name'],'rig.'+parent if parent else 'root',translation=position,role='bone')
    # Consolidate all forms sharing a material role. One common skeleton, not a rig per limb.
    ranges=me.anatomy.get('materialGroups',[]); groups={}
    for r in ranges:groups.setdefault(material or r.get('material') or mat,[]).extend(range(r['start'],r['start']+r['count']))
    if not groups:groups={mat:list(range(len(me.vertices)))}
    for index,(role,ids) in enumerate(groups.items()):
        role_style=role+('' if style=='lowpoly' else '--'+style)
        if (style!='lowpoly' and role.startswith('mat.') and not role.endswith(('--toon','--voxel'))) or (ROOT/'library/materials'/role_style/'material.json').is_file():role=role_style
        ensure_material(safe_id(role))
        name='surface' if index==0 else 'surface_'+str(index)
        if len(groups)==1:mesh=me
        else:
            ids=np.array(ids,dtype=np.int32)
            mesh=Mesh(me.vertices[ids],np.arange(len(ids),dtype=np.int32).reshape(-1,3),me.normals[ids],me.uv[ids],None if me.colors is None else me.colors[ids],None if me.skin_indices is None else me.skin_indices[ids],None if me.skin_weights is None else me.skin_weights[ids],copy.deepcopy(me.rig),{**me.anatomy,'materialGroups':[]})
        a.add(name,mesh,role,parent='root',role=d['category']+'_part')
        if me.rig:a.nodes[-1]['skin']={'joints':['rig.'+b['name'] for b in me.rig]}
    if me.anatomy:a.metadata['anatomy']=me.anatomy
    for n in a.nodes:n['part_id']=id
    scale=size/np.asarray(d['size']);lo=me.vertices.min(0);hi=me.vertices.max(0);mid=(lo+hi)/2
    con=[connector('mount',[0,0,0],(0,-1,0)),connector('top',[mid[0],hi[1],mid[2]]),connector('bottom',[mid[0],lo[1],mid[2]],(0,-1,0)),
         connector('left',[lo[0],mid[1],mid[2]],(-1,0,0),(0,1,0)),connector('right',[hi[0],mid[1],mid[2]],(1,0,0),(0,1,0)),
         connector('front',[mid[0],mid[1],hi[2]],(0,0,1)),connector('back',[mid[0],mid[1],lo[2]],(0,0,-1))]
    for c in me.anatomy.get('connectors',[]):
        c=copy.deepcopy(c);con=[x for x in con if x['id']!=c['id']];con.append(c)
    for c in con:
        from .contracts import validate_connector
        validate_connector(c);frame(c);a.socket(c['id'],'root',c['position'],c['normal'],c['interface']);a.sockets[-1].update({k:copy.deepcopy(v) for k,v in c.items() if k not in ('node','id')})
    for b in me.rig:
        a.socket('joint.'+b['name'],'rig.'+b['name'],[0,0,0],[0,1,0],'joint');a.sockets[-1].update(tangent=[1,0,0],extent=None)
    a.metadata={**a.metadata,'runtime':resolved_runtime,'part_id':id,'name':d['name'],'style':style,'level':d.get('level',1),'geometry_kernel':'shared-three-1.8','definition_sha256':sha256(PART_DIR/(id+'.json')),'size':size.tolist(),'anchor':d.get('anchor','base'),'connectors':con,'source':d.get('source',{'type':'original_procedural','license':'project-authored'}),'limitations':['No claim that unrelated external models can be automatically reverse-engineered into semantic parts.','This part is a game mesh, not an engineering/manufacturing specification.']}
    return a


def install_catalog():
    """Re-author the active faceted catalogue, never restore retired models."""
    import subprocess, sys
    subprocess.run([sys.executable,str(require_source()/'tools/rebuild_library.py'),'--overwrite'],check=True)
    return {'parts':len(list(PART_DIR.glob('*.json'))),'style':'faceted-only'}
