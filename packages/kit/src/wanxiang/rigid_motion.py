"""Named loopable translation and rotation tracks for both rigid joints and weighted skeleton bones."""
from __future__ import annotations
import numpy as np
from scipy.spatial.transform import Rotation
from .util import ROOT,read_json,safe_id
from .errors import WXError

def clips_for(assembly_id,spec=None):
    """Collect authored clips recursively, namespace clip names and node paths.

    A nested actuator remains animated when exported as part of a vehicle/scene.
    Different clips are alternatives; they are not all played simultaneously.
    """
    import copy
    clips=[]
    def visit(ident,prefix='',stack=(),current=None,params=None):
        if ident in stack or len(stack)>12:raise WXError('RECIPE_INVALID','Animation dependency cycle/depth')
        motion=ROOT/'library/motions'/(safe_id(ident)+'.json')
        if motion.is_file():
            for original in read_json(motion).get('clips',[]):
                c=copy.deepcopy(original);c['name']=prefix+c['name']
                for t in c['tracks']:t['node']=prefix+t['node']
                clips.append(c)
        path=ROOT/'library/assemblies'/(safe_id(ident)+'.json')
        definition=current if current is not None else read_json(path) if path.is_file() else {}
        from .semantic import assembly as resolve_assembly
        definition=copy.deepcopy(definition)
        if params:
            definition.setdefault('metadata',{}).setdefault('parameters',{}).update(params)
        definition=resolve_assembly(definition)
        for it in definition.get('instances',[]):
            if it.get('enabled',True) is False:continue
            if it.get('assembly'):visit(it['assembly'],prefix+it['id']+'.',(*stack,ident),params=it.get('params'))
    visit(assembly_id,current=spec)
    return clips

def tracks_for(asset,assembly_id):
    path=ROOT/'library/motions'/(safe_id(assembly_id)+'.json')
    by={n['id']:n for n in asset.nodes};out=[]
    for clip in clips_for(assembly_id,asset.metadata.get('source_spec')):
        duration=float(clip.get('duration',1))
        if not 0<duration<=120:raise WXError('INPUT_INVALID','Invalid animation duration')
        for t in clip['tracks']:
            if t['node'] not in by:raise WXError('INPUT_INVALID','Animation references missing assembly node: '+t['node'])
            mat=np.asarray(by[t['node']]['matrix'],float)
            axis=np.asarray(t.get('axis'),float)
            if axis.shape!=(3,) or not np.isfinite(axis).all() or np.linalg.norm(axis)<1e-6:
                raise WXError('INPUT_INVALID','Invalid animation axis')
            axis/=np.linalg.norm(axis)
            has_rotation='degrees' in t;has_translation='translations' in t
            if has_rotation==has_translation:raise WXError('INPUT_INVALID','Specify exactly one motion channel')
            values=np.asarray(t['degrees'] if has_rotation else t['translations'],float)
            if values.ndim!=1 or len(values)<2 or len(values)>4096 or not np.isfinite(values).all():
                raise WXError('INPUT_INVALID','Invalid animation keys')
            track={'name':clip['name'],'node':t['node'],'times':np.linspace(0,duration,len(values)).tolist()}
            if has_translation:
                # Match WXMechanics: rest @ local translation, including authored scale.
                direction=mat[:3,:3]@axis
                track['translations']=(mat[:3,3]+values[:,None]*direction).tolist()
            else:
                sc=np.linalg.norm(mat[:3,:3],axis=0)
                if np.any(sc<1e-12):raise WXError('INPUT_INVALID','Singular animated transform')
                if np.linalg.det(mat[:3,:3])<0:sc[0]*=-1
                base=Rotation.from_matrix(mat[:3,:3]/sc)
                track['rotations']=(base*Rotation.from_rotvec(values[:,None]*np.pi/180*axis)).as_quat().tolist()
            out.append(track)
    return out
