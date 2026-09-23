"""Typed operator registry. Recipes only call named, versioned operators."""
from __future__ import annotations
from .paths import code_path, WORKSPACE_ROOT
import subprocess,json,copy
import numpy as np
from . import geometry as g,builders as b
from .ir import AssetIR,Mesh,transform,concat
from .util import ROOT,canonical
from .errors import WXError
N=lambda default,lo=.01,hi=100:{'type':'number','minimum':lo,'maximum':hi,'default':default}
I=lambda default,lo=1,hi=256:{'type':'integer','minimum':lo,'maximum':hi,'default':default}
A=lambda default:{'type':'array','default':default,'maxItems':2048}
S=lambda default,enum=None:{'type':'string','default':default,**({'enum':enum} if enum else {})}
B=lambda default:{'type':'boolean','default':default}
REGISTRY={}

def register(name,props,fn,inputs=None,output='AssetIR',description='',required=None):
    REGISTRY[name]={'id':name,'version':'1.0.0','schema':{'type':'object','properties':props,'additionalProperties':False,'required':required or []},'inputs':inputs or {},'output':output,'description':description,'fn':fn}

def wrap(mesh,material='stone'):
    a=AssetIR();a.add('surface',mesh,material);return a

def geometry_fn(name):
    def run(p,seed,inputs):
        p=dict(p);mat=p.pop('material','stone');return wrap(getattr(g,name)(**p),mat)
    return run

MAT={'material':S('stone')}
register('geometry.box',{'size':A([1,1,1]),'bevel':N(0,0,1),**MAT},geometry_fn('box'),description='Box with optional rounded Minkowski corners and explicit face UVs.')
register('geometry.cylinder',{'radius':N(.5),'height':N(1),'segments':I(24,3,256),**MAT},geometry_fn('cylinder'))
register('geometry.cone',{'radius':N(.5),'height':N(1),'segments':I(24,3,256),**MAT},lambda p,s,i:wrap(g.cylinder(p['radius'],p['height'],p['segments'],0),p['material']))
register('geometry.sphere',{'radius':N(1),'subdivisions':I(2,0,4),'scale':A([1,1,1]),**MAT},geometry_fn('sphere'))
register('geometry.capsule',{'radius':N(.3),'height':N(1),**MAT},lambda p,s,i:wrap(concat([g.cylinder(p['radius'],p['height']),g.sphere(p['radius']).transformed(transform([0,p['height'],0])),g.sphere(p['radius'])]),p['material']),description='Assembled capsule components; intersecting surfaces, not boolean union.')
register('geometry.extrude',{'outline':A([[-1,0],[1,0],[1,2],[-1,2]]),'holes':A([]),'depth':N(.3),**MAT},geometry_fn('extrude'),description='Constrained triangulation with actual polygon holes.')
register('geometry.lathe',{'profile':A([[.5,0],[.6,.5],[.45,1]]),'segments':I(32,3,256),'cap':B(True),**MAT},geometry_fn('lathe'))
register('geometry.sweep',{'points':A([[0,0,0],[0,1,0]]),'radii':{'default':.1,'oneOf':[{'type':'number','exclusiveMinimum':0},{'type':'array','items':{'type':'number','exclusiveMinimum':0},'minItems':2,'maxItems':2048}]},'segments':I(10,3,128),'cap':B(True),**MAT},geometry_fn('sweep'),description='Parallel-transport variable-radius sweep, arclength UVs, rejects reversing frames.')
register('geometry.loft',{'sections':A([]),**MAT},geometry_fn('loft'))
register('geometry.heightfield',{'size':N(8,.1,200),'resolution':I(40,4,384),'origin':A([0,0]),'kind':S('hills',['hills','river','road','terrace']),'amplitude':N(1,0,20),**MAT},lambda p,s,i:wrap(g.heightfield(**{k:v for k,v in p.items() if k!='material'},seed=s),p['material']))
register('geometry.sdf',{'shapes':A([]),'resolution':I(48,16,160),'bounds':A([[-2,-2,-2],[2,2,2]]),'smooth':N(.15,0,2),**MAT},geometry_fn('sdf'))

def change(p,s,inputs,mode):
    a=copy.deepcopy(inputs['source'])
    for id,mesh in a.meshes.items():
        if mode=='bend':a.meshes[id]=g.bend(mesh,p['amount'],p['axis'])
        elif mode=='taper':a.meshes[id]=g.taper(mesh,p['top'])
        elif mode=='normals':a.meshes[id]=Mesh(mesh.vertices,mesh.faces,uv=mesh.uv)
        elif mode=='hard_edges':a.meshes[id]=Mesh(mesh.vertices[mesh.faces].reshape(-1,3),np.arange(mesh.faces.size).reshape(-1,3),uv=mesh.uv[mesh.faces].reshape(-1,2))
        elif mode=='uv':
            q=mesh.copy();q.uv=q.vertices[:,p['axes']]*p['scale'];a.meshes[id]=q
        elif mode=='displace':
            v=mesh.vertices.copy();h=p['amount']*np.sin(v[:,0]*p['frequency']+s)*np.cos(v[:,2]*p['frequency']);v+=mesh.normals*h[:,None];a.meshes[id]=Mesh(v,mesh.faces,uv=mesh.uv)
    return a
for name,props in [('bend',{'amount':N(.2,-10,10),'axis':I(0,0,2)}),('taper',{'top':N(.3,.01,10)}),('normals',{}),('hard_edges',{}),('uv',{'axes':A([0,2]),'scale':N(1,.001,100)}),('displace',{'amount':N(.1,0,5),'frequency':N(4,.1,100)})]:
    register('surface.'+name,props,lambda p,s,i,mode=name:change(p,s,i,mode),{'source':'AssetIR'})

def assemble_transform(p,s,i):
    a=copy.deepcopy(i['source']);m=transform(p['translation'],p['rotation'],p['scale'])
    for n in a.nodes:
        if not n.get('parent'):n['matrix']=(m@np.asarray(n['matrix'])).tolist()
    return a
register('assembly.transform',{'translation':A([0,0,0]),'rotation':A([0,0,0]),'scale':A([1,1,1])},assemble_transform,{'source':'AssetIR'})

def array(p,s,inp):
    a=AssetIR()
    for k in range(p['count']):
        src=copy.deepcopy(inp['source'])
        if p['mode']=='radial':
            angle=k*math.tau/p['count'];m=transform([p['radius']*math.cos(angle),0,p['radius']*math.sin(angle)],[0,-angle,0])
        else:m=transform(np.asarray(p['step'])*k)
        for n in src.nodes:
            if not n.get('parent'):n['matrix']=(m@np.asarray(n['matrix'])).tolist()
        a.extend(src,f'i{k:03}_')
    return a
import math
register('assembly.array',{'count':I(6,1,256),'mode':S('linear',['linear','radial']),'step':A([1,0,0]),'radius':N(2)},array,{'source':'AssetIR'})

def attach(p,s,i):
    base=copy.deepcopy(i['base']);part=copy.deepcopy(i['part'])
    def socket(a,id):
        matches=[x for x in a.sockets if x['id']==id]
        if not matches:raise WXError('RECIPE_INVALID',f'Socket missing: {id}')
        return matches[0]
    bs=socket(base,p['base_socket']);ps=socket(part,p['part_socket'])
    if bs['interface']!=ps['interface']:raise WXError('GEOMETRY_INVALID','Socket interface mismatch')
    def frame(a,s):
        from scipy.spatial.transform import Rotation
        axis=np.asarray(s.get('axis',[0,1,0]),float);axis/=np.linalg.norm(axis);y=np.array([0,1,0]);c=np.cross(y,axis);dot=np.clip(np.dot(y,axis),-1,1)
        r=np.eye(3) if dot>.9999 else Rotation.from_rotvec(np.array([math.pi,0,0]) if dot<-.9999 else c/np.linalg.norm(c)*math.acos(dot)).as_matrix()
        m=np.eye(4);m[:3,:3]=r;m[:3,3]=s['position'];return a.world_matrices()[s['node']]@m
    m=frame(base,bs)@np.linalg.inv(frame(part,ps))
    for n in part.nodes:
        if not n.get('parent'):n['matrix']=(m@np.asarray(n['matrix'])).tolist()
    base.extend(part,p['prefix']);return base
register('assembly.attach',{'base_socket':S(''),'part_socket':S(''),'prefix':S('attached_')},attach,{'base':'AssetIR','part':'AssetIR'})

def merge(p,s,i):
    a=AssetIR()
    for k,src in i.items():a.extend(copy.deepcopy(src),k+'_')
    return a
register('assembly.merge',{},merge,{'a':'AssetIR','b':'AssetIR'})

GROW={'species':S('pine',['pine','fir','oak','birch','willow']),'height':N(6,.5,20),'crown':N(1.7,.2,6),'density':N(1,.3,2),'lean':N(.18,-2,2)}
register('botany.growth',GROW,lambda p,s,i:b.growth(p,s),output='Skeleton',description='Deterministic species-aware scaffold with stable branch IDs.')
register('botany.wood',{'quality':N(1,.25,1.5)},b.tree_wood,{'skeleton':'Skeleton'})
register('botany.foliage',{'quality':N(1,.25,1.5),'leaf_density':N(1,.2,2)},b.tree_foliage,{'skeleton':'Skeleton'})

ASSEMBLY_PROPS={
 'shrub':{'height':N(1.3,.3,3),'radius':N(.9,.2,2),'density':N(1,.3,1.6)},
 'palm':{'height':N(5,1,10)},'bamboo':{'height':N(4,1,8),'stems':I(5,1,12)},'cactus':{'height':N(2.8,.5,6)},
 'rock':{'size':N(2,.3,5),'kind':S('boulder',['boulder','basalt','cliff']),'quality':N(1,.25,1.5)},
 'terrain':{'size':N(8,2,32),'kind':S('hills',['hills','river','road','terrace']),'quality':N(1,.25,1.5),'origin':A([0,0]),'amplitude':N(1,0,4)},
 'crate':{'size':N(1.2,.4,3),'planks':I(5,3,12)},'barrel':{'radius':N(.48,.2,1),'height':N(1.25,.5,2.5),'staves':I(16,8,32)},
 'lamp':{'height':N(3.2,1.5,6)},'house':{'width':N(3.4,2.7,7),'depth':N(2.8,2,7),'height':N(2.2,1.8,4),'roof_rise':N(1.1,.5,2)},
 'arch':{'radius':N(1.25,.7,3),'height':N(1.65,.6,4),'depth':N(.65,.3,2)},'bridge':{'length':N(5,2,12),'width':N(2,1,4),'rise':N(.55,0,1.5)},
 'wall':{'length':N(4,2,10),'height':N(2,1,4)},'tower':{'height':N(4.8,2,10),'radius':N(1.2,.8,3)},
 'fence':{'length':N(4,1,10),'posts':I(5,2,12)},
 'chassis':{'length':N(3.2,2,6),'width':N(1.7,1.2,3),'tracked':B(False),'quality':N(1,.3,1.5)},
 'turret':{'radius':N(.86,.4,1.5),'barrel_length':N(2.1,.6,4)},
 'industrial':{'kind':S('tank',['tank','silo','pipe','crane']),'height':N(3.2,1.5,8),'radius':N(.85,.5,2)},
 'fountain':{'radius':N(1.4,.8,3)},'windmill':{'height':N(4,2.5,7)}
}
for properties in ASSEMBLY_PROPS.values():properties.setdefault('quality',N(1,.25,1.5))
for name,fn in b.ASSEMBLERS.items():register('model.'+name,ASSEMBLY_PROPS[name],lambda p,s,i,fn=fn:b.construct(fn,p,s),description='Semantic construction with named subparts and procedural surface coordinates.')

def node_worker(p,s,i,op):
    import shutil
    if not shutil.which('node'):raise WXError('CAPABILITY_MISSING','Node.js is required for this operator')
    payload=canonical({'op':op,'params':p})
    try:
        proc=subprocess.run(['node',str(code_path('workers/node/geometry.mjs'))],input=payload,capture_output=True,timeout=45)
        out=json.loads(proc.stdout)
    except subprocess.TimeoutExpired:raise WXError('BUDGET_EXCEEDED','Node worker exceeded 45 seconds')
    except Exception as e:raise WXError('GEOMETRY_INVALID',f'Node worker error: {e}')
    if proc.returncode or out.get('status')!='ok':raise WXError('GEOMETRY_INVALID',out.get('error','Node worker failed'))
    return wrap(Mesh(np.array(out['positions']).reshape(-1,3),np.array(out['indices']).reshape(-1,3),np.array(out['normals']).reshape(-1,3),np.array(out['uv']).reshape(-1,2)))
for name,props in [('extrude',{'outline':A([[-1,0],[1,0],[1,2],[-1,2]]),'holes':A([]),'depth':N(.3),'bevel':N(.03,0,.5)}),('lathe',{'profile':A([[.5,0],[.7,1],[.5,2]]),'segments':I(32,3,128)}),('tube',{'points':A([[0,0,0],[.5,1,0],[0,2,1]]),'radius':N(.1),'samples':I(32,3,256),'segments':I(10,3,32)}),('torus',{'radius':N(1),'tube':N(.12),'radial':I(12,3,32),'segments':I(48,3,128)})]:
    register('three.'+name,props,lambda p,s,i,name=name:node_worker(p,s,i,name),description='Offline Three.js r186 CPU worker; no browser or GPU required.')

def describe(name):
    if name not in REGISTRY:raise WXError('RECIPE_INVALID',f'Unknown operator {name}')
    return {k:v for k,v in REGISTRY[name].items() if k!='fn'}

def validate_params(schema,params):
    import jsonschema
    result={k:v['default'] for k,v in schema.get('properties',{}).items() if 'default'in v};result.update(params)
    errors=sorted(jsonschema.Draft202012Validator(schema).iter_errors(result),key=lambda e:str(e.path))
    if errors:
        e=errors[0];raise WXError('RECIPE_INVALID',e.message,details={'pointer':'/'+('/'.join(str(x) for x in e.path))})
    return result

def execute(name,params,seed,inputs):
    if name not in REGISTRY:raise WXError('RECIPE_INVALID',f'Unknown operator {name}')
    r=REGISTRY[name];p=validate_params(r['schema'],params)
    return r['fn'](p,seed,inputs)
