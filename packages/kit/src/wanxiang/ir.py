"""Versioned JSON + NPZ MeshIR. Never pickle or execute an asset definition."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import io
import numpy as np
from .util import write_json, read_json, atomic_bytes, sha256, finite
from .errors import WXError

@dataclass
class Mesh:
    vertices: np.ndarray
    faces: np.ndarray
    normals: np.ndarray | None = None
    uv: np.ndarray | None = None
    colors: np.ndarray | None = None
    skin_indices: np.ndarray | None = None
    skin_weights: np.ndarray | None = None
    rig: list = field(default_factory=list)
    anatomy: dict = field(default_factory=dict)
    def __post_init__(self):
        self.vertices=np.asarray(self.vertices,dtype=np.float32).reshape(-1,3)
        self.faces=np.asarray(self.faces,dtype=np.int32).reshape(-1,3)
        finite(self.vertices,'positions')
        if len(self.vertices)==0 or len(self.faces)==0:raise WXError('GEOMETRY_INVALID','Empty mesh')
        if self.faces.min()<0 or self.faces.max()>=len(self.vertices):raise WXError('GEOMETRY_INVALID','Index out of bounds')
        if self.normals is None:
            v=self.vertices;f=self.faces
            face=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
            ns=np.zeros_like(v)
            for i in range(3):np.add.at(ns,f[:,i],face)
            mag=np.linalg.norm(ns,axis=1,keepdims=True);self.normals=ns/np.maximum(mag,1e-12)
            self.normals[mag[:,0]<1e-12]=[0,1,0]
        else:
            self.normals=np.asarray(self.normals,dtype=np.float32)
            self.normals/=np.maximum(np.linalg.norm(self.normals,axis=1,keepdims=True),1e-12)
        if self.uv is None:self.uv=self.vertices[:,[0,2]].copy()
        self.uv=np.asarray(self.uv,dtype=np.float32).reshape(-1,2)
        if self.normals.shape!=self.vertices.shape or len(self.uv)!=len(self.vertices):raise WXError('GEOMETRY_INVALID','Attribute shape mismatch')
        finite(self.normals,'normals');finite(self.uv,'uv')
        if self.colors is not None:
            self.colors=np.asarray(self.colors,np.float32).reshape(-1,3)
            finite(self.colors,'vertex colors')
            if self.colors.shape!=self.vertices.shape or np.any(self.colors<0) or np.any(self.colors>1):raise WXError('GEOMETRY_INVALID','Invalid vertex colors')
        if (self.skin_indices is None)!=(self.skin_weights is None):raise WXError('GEOMETRY_INVALID','Both skin attributes required')
        if self.skin_weights is not None:
            raw=np.asarray(self.skin_indices)
            if not np.isfinite(raw).all() or np.any(raw<0) or np.any(raw>65535) or not np.all(raw==np.floor(raw)):raise WXError('GEOMETRY_INVALID','Invalid skin indices')
            self.skin_indices=raw.astype(np.uint16).reshape(-1,4)
            self.skin_weights=np.asarray(self.skin_weights,np.float32).reshape(-1,4)
            finite(self.skin_weights,'skin weights')
            if len(self.skin_weights)!=len(self.vertices) or self.skin_indices.shape!=self.skin_weights.shape or np.any(self.skin_weights<0) or not np.allclose(self.skin_weights.sum(1),1,atol=2e-5):raise WXError('GEOMETRY_INVALID','Skin weights must be nonnegative and sum to one')
            if self.rig and self.skin_indices.max()>=len(self.rig):raise WXError('GEOMETRY_INVALID','Skin joint out of range')
    def transformed(self,matrix):
        m=np.asarray(matrix,float);v=self.vertices@m[:3,:3].T+m[:3,3]
        if abs(np.linalg.det(m[:3,:3]))<1e-12:raise WXError('GEOMETRY_INVALID','Singular transform')
        n=self.normals@np.linalg.inv(m[:3,:3]);f=self.faces.copy()
        if np.linalg.det(m[:3,:3])<0:f=f[:,[0,2,1]]
        return Mesh(v,f,n,self.uv.copy(),self.colors.copy() if self.colors is not None else None)
    def copy(self):
        import copy
        return Mesh(self.vertices.copy(),self.faces.copy(),self.normals.copy(),self.uv.copy(),None if self.colors is None else self.colors.copy(),None if self.skin_indices is None else self.skin_indices.copy(),None if self.skin_weights is None else self.skin_weights.copy(),copy.deepcopy(self.rig),copy.deepcopy(self.anatomy))

@dataclass
class AssetIR:
    nodes: list = field(default_factory=list)
    meshes: dict = field(default_factory=dict)
    sockets: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    def group(self,id,parent=None,translation=(0,0,0),matrix=None,role='assembly'):
        if any(n['id']==id for n in self.nodes):raise WXError('GEOMETRY_INVALID',f'Duplicate node: {id}')
        m=np.eye(4) if matrix is None else np.asarray(matrix,float).copy();m[:3,3]+=translation
        self.nodes.append({'id':id,'parent':parent,'matrix':m.tolist(),'role':role})
        return id
    def add(self,id,mesh,material='stone',parent=None,translation=(0,0,0),matrix=None,role='surface',topology='closed'):
        self.group(id,parent,translation,matrix,role); self.nodes[-1].update(mesh=id,material=material,topology=topology)
        self.meshes[id]=mesh
        return id
    def socket(self,id,node,position=(0,0,0),axis=(0,1,0),interface='fixed',limits=None):
        self.sockets.append({'id':id,'node':node,'position':list(position),'axis':list(axis),'interface':interface,'limits':limits})
    def extend(self,other,prefix=''):
        for n in other.nodes:
            c=dict(n);c['id']=prefix+c['id'];c['parent']=prefix+c['parent'] if c.get('parent') else None
            if 'mesh'in c:c['mesh']=prefix+c['mesh']
            if 'skin'in c:c['skin']={**c['skin'],'joints':[prefix+x for x in c['skin']['joints']]}
            if any(x['id']==c['id'] for x in self.nodes):raise WXError('GEOMETRY_INVALID',f'Duplicate node {c["id"]}')
            self.nodes.append(c)
        self.meshes.update({prefix+k:v for k,v in other.meshes.items()})
        self.sockets.extend([{**s,'id':prefix+s['id'],'node':prefix+s['node']} for s in other.sockets])
    def world_matrices(self):
        by={n['id']:n for n in self.nodes};done={};visiting=set()
        def get(id):
            if id in done:return done[id]
            if id in visiting:raise WXError('GEOMETRY_INVALID','Scene graph cycle')
            if id not in by:raise WXError('GEOMETRY_INVALID',f'Missing parent: {id}')
            visiting.add(id);n=by[id];m=np.asarray(n['matrix'],float)
            if n.get('parent'):m=get(n['parent'])@m
            done[id]=m;visiting.remove(id);return m
        for n in self.nodes:get(n['id'])
        return done
    def bounds(self):
        matrices=self.world_matrices();vs=[m.transformed(matrices[n['id']]).vertices for n in self.nodes if (m:=self.meshes.get(n.get('mesh'))) is not None]
        if not vs:raise WXError('GEOMETRY_INVALID','Scene contains no geometry')
        return np.stack([np.min([v.min(0) for v in vs],0),np.max([v.max(0) for v in vs],0)])
    def save(self,folder):
        p=Path(folder);p.mkdir(parents=True,exist_ok=True);arrays={}; entries={}
        for i,(id,m) in enumerate(self.meshes.items()):
            for k,a in [('v',m.vertices),('f',m.faces),('n',m.normals),('uv',m.uv)]:arrays[f'm{i}_{k}']=a
            entries[id]={'key':f'm{i}','vertices':len(m.vertices),'triangles':len(m.faces),'rig':m.rig,'anatomy':m.anatomy}
            for k,a in [('colors',m.colors),('skin_indices',m.skin_indices),('skin_weights',m.skin_weights)]:
                if a is not None:arrays[f'm{i}_{k}']=a;entries[id][k]=True
        stream=io.BytesIO();np.savez_compressed(stream,**arrays);atomic_bytes(p/'arrays.npz',stream.getvalue())
        write_json(p/'asset.ir.json',{'schema':'wx.meshir/1.0','units':'m','up':'+Y','front':'+Z','nodes':self.nodes,'meshes':entries,'sockets':self.sockets,'metadata':self.metadata,'arrays_sha256':sha256(p/'arrays.npz')})
    @classmethod
    def load(cls,folder):
        p=Path(folder);j=read_json(p/'asset.ir.json')
        if sha256(p/'arrays.npz')!=j['arrays_sha256']:raise WXError('VALIDATION_FAILED','MeshIR array checksum mismatch')
        with np.load(p/'arrays.npz',allow_pickle=False) as a:
            meshes={id:Mesh(a[e['key']+'_v'],a[e['key']+'_f'],a[e['key']+'_n'],a[e['key']+'_uv'],*(a[e['key']+'_'+k] if e.get(k) else None for k in ('colors','skin_indices','skin_weights')),e.get('rig',[]),e.get('anatomy',{})) for id,e in j['meshes'].items()}
        return cls(j['nodes'],meshes,j['sockets'],j['metadata'])

def concat(meshes):
    meshes=list(meshes)
    if not meshes:raise WXError('GEOMETRY_INVALID','Cannot concatenate empty list')
    vs=[];fs=[];ns=[];uv=[];o=0
    for m in meshes:vs.append(m.vertices);fs.append(m.faces+o);ns.append(m.normals);uv.append(m.uv);o+=len(m.vertices)
    return Mesh(np.vstack(vs),np.vstack(fs),np.vstack(ns),np.vstack(uv))

def transform(translation=(0,0,0),rotation=(0,0,0),scale=(1,1,1)):
    from scipy.spatial.transform import Rotation
    m=np.eye(4);m[:3,:3]=Rotation.from_euler('xyz',rotation).as_matrix()@np.diag(scale);m[:3,3]=translation;return m
