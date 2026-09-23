"""Deterministic rigid controls and translated telescoping rods (no mesh rebuild)."""
from __future__ import annotations
import math,copy
import numpy as np
from scipy.spatial.transform import Rotation
from .errors import WXError

def apply(asset,spec,state=None):
    state={} if state is None else state
    if not isinstance(state,dict):raise WXError('RECIPE_INVALID','State must be an object')
    md=spec.get('metadata',{});controls=md.get('state_controls',[]);struts=md.get('struts',[])
    if len(controls)>24 or len(struts)>24:raise WXError('RECIPE_INVALID','Constraint budget')
    unknown=set(state)-{c['id'] for c in controls}
    if unknown:raise WXError('RECIPE_INVALID','Unknown state control: '+', '.join(sorted(unknown)))
    by={n['id']:n for n in asset.nodes};original_rest={k:copy.deepcopy(n.get('control_rest_matrix')) for k,n in by.items()};saved={k:np.array(v['matrix'],float).copy() for k,v in by.items()};report=[]
    def node(k):
        if k not in by:raise WXError('RECIPE_INVALID','Linkage node missing: '+k)
        return by[k]
    try:
        changes={}
        for c in controls:
            value=state.get(c['id'],c.get('default',0))
            if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not c['min']<=value<=c['max']:raise WXError('RECIPE_INVALID','State outside range: '+c['id'])
            axis=np.array(c['axis'],float)
            if axis.shape!=(3,) or not np.isfinite(axis).all() or np.linalg.norm(axis)<1e-12:raise WXError('RECIPE_INVALID','Degenerate control axis')
            axis/=np.linalg.norm(axis);r=np.eye(4)
            if c.get('mode','rotation')=='translation':r[:3,3]=axis*value
            elif c.get('mode','rotation')=='rotation':r[:3,:3]=Rotation.from_rotvec(axis*math.radians(value)).as_matrix()
            else:raise WXError('RECIPE_INVALID','Unknown control mode')
            for k in c.get('nodes',[c.get('node')]):
                n=node(k);rest=n.setdefault('control_rest_matrix',saved[k].tolist());changes[k]=changes.get(k,np.array(rest))@r
        for k,m in changes.items():by[k]['matrix']=m.tolist()
        for c in struts:
            n=node(c['node']);rod=node(c['node']+'.'+c['rod']);world=asset.world_matrices();parent=n.get('parent','root');inv=np.linalg.inv(world[parent])
            start=(inv@world[c['from']['node']]@np.r_[c['from']['point'],1])[:3];end=(inv@world[c['to']['node']]@np.r_[c['to']['point'],1])[:3]
            delta=end-start;length=float(np.linalg.norm(delta))
            if not math.isfinite(length) or not c['min_length']-1e-6<=length<=c['max_length']+1e-6:raise WXError('RECIPE_INVALID',f"{c['node']}: cylinder travel exceeded ({length:.5f} m)")
            direction=delta/length;axis=np.cross([0,1,0],direction);cos=float(direction[1]);mat=np.eye(4)
            if np.linalg.norm(axis)>1e-8:mat[:3,:3]=Rotation.from_rotvec(axis/np.linalg.norm(axis)*math.acos(np.clip(cos,-1,1))).as_matrix()
            elif cos<0:mat[:3,:3]=Rotation.from_euler('x',180,degrees=True).as_matrix()
            mat[:3,3]=start;n['matrix']=mat.tolist();r=np.eye(4);r[1,3]=length-c['rod_length'];rod['matrix']=r.tolist()
            world=asset.world_matrices();tip=(world[rod['id']]@np.array([0,c['rod_length'],0,1]))[:3];target=(world[c['to']['node']]@np.r_[c['to']['point'],1])[:3]
            report.append({'node':c['node'],'length':length,'error':float(np.linalg.norm(tip-target))})
        return {'state':state.copy(),'constraints':report}
    except BaseException:
        for k,m in saved.items():
            by[k]['matrix']=m.tolist()
            if original_rest[k] is None:by[k].pop('control_rest_matrix',None)
            else:by[k]['control_rest_matrix']=original_rest[k]
        raise
