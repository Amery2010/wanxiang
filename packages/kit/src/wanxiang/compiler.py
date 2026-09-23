from __future__ import annotations
from .paths import code_path, WORKSPACE_ROOT
import copy
from pathlib import Path
from .catalog import get_recipe
from .operators import REGISTRY,validate_params
from .util import ROOT,digest,sha256,safe_id
from .materials import STYLES
from .errors import WXError
PROFILES={'draft':.5,'standard':1.,'hero':1.3,'lod1':.6,'lod2':.3}
SPEC_KEYS={'id','recipe','preset','params','seed','profile','style','materials','budgets','metadata','host_requests','quality'}

def normalize(spec):
    if not isinstance(spec,dict):raise WXError('RECIPE_INVALID','Asset spec must be an object')
    # Schema validation is followed by semantic graph/port checks below.
    from .util import read_json
    from .operators import validate_params
    validate_params(read_json(code_path('schemas/asset-spec.schema.json')),spec)
    extra=set(spec)-SPEC_KEYS
    if extra:raise WXError('RECIPE_INVALID',f'Unknown spec fields: {sorted(extra)}')
    if not spec.get('recipe'):raise WXError('RECIPE_INVALID','recipe is required')
    rec,_=get_recipe(spec['recipe']);s={'id':safe_id(spec.get('id',rec['id'])),'recipe':spec['recipe'],'preset':'default','params':{},'seed':314159,'profile':'standard','style':'natural','materials':{},'budgets':{},'metadata':{},'host_requests':[]}
    s.update(copy.deepcopy(spec));safe_id(s['id'])
    if type(s['seed']) is not int or not 0<=s['seed']<=4294967295:raise WXError('RECIPE_INVALID','seed must be uint32')
    if s['profile'] not in PROFILES:raise WXError('RECIPE_INVALID','Unknown build profile')
    if s['style'] not in STYLES:raise WXError('RECIPE_INVALID','Unknown style')
    if s.get('quality') is not None and not .25<=s['quality']<=1.5:raise WXError('RECIPE_INVALID','quality outside .25..1.5')
    for k in ('materials','params','metadata','budgets'):
        if not isinstance(s[k],dict):raise WXError('RECIPE_INVALID',f'{k} must be an object')
    allowed={'triangles','vertices','seconds','sdf_bytes','output_bytes'}
    if set(s['budgets'])-allowed:raise WXError('RECIPE_INVALID','Unknown budget field')
    limits={'triangles':200000,'vertices':500000,'seconds':120,'sdf_bytes':512_000_000,'output_bytes':150_000_000};limits.update(s['budgets'])
    for k,v in limits.items():
        if not isinstance(v,(int,float)) or v<=0:raise WXError('RECIPE_INVALID',f'Invalid budget: {k}')
    s['budgets']=limits
    return s

def resolve(value,params,profile):
    if isinstance(value,dict):
        if '$param'in value:
            if set(value)!={'$param'} or value['$param'] not in params:raise WXError('RECIPE_INVALID','Unknown or malformed parameter reference')
            return params[value['$param']]
        if '$profile'in value:
            if value!={'$profile':'quality'}:raise WXError('RECIPE_INVALID','Unknown profile reference')
            return profile
        return {k:resolve(v,params,profile) for k,v in value.items()}
    if isinstance(value,list):return [resolve(x,params,profile) for x in value]
    return value

def compile_spec(spec):
    s=normalize(spec);r,path=get_recipe(s['recipe'])
    if r.get('schema')!='wx.recipe/1.0':raise WXError('RECIPE_INVALID','Executable recipes require wx.recipe/1.0; old specification examples are not silently executed')
    preset=s.get('preset','default')
    if preset not in r.get('presets',{'default':{}}):raise WXError('RECIPE_INVALID',f'Unknown preset {preset}')
    p={**r.get('defaults',{}),**r.get('presets',{}).get(preset,{}),**s['params']};p=validate_params(r['parameter_schema'],p)
    nodes=r.get('nodes',[])
    if not 1<=len(nodes)<=128:raise WXError('RECIPE_INVALID','Recipe must have 1..128 nodes')
    by={}
    for n in nodes:
        safe_id(n['id'])
        if n['id']in by:raise WXError('RECIPE_INVALID','Duplicate recipe node',node=n['id'])
        by[n['id']]=n
        if n.get('operator') not in REGISTRY:raise WXError('RECIPE_INVALID',f'Unknown operator {n.get("operator")}',node=n['id'])
        if n.get('operator_version')!=REGISTRY[n['operator']]['version']:raise WXError('RECIPE_INVALID','Operator version is not available',node=n['id'])
    visiting=set();done=set();ordered=[]
    def visit(id):
        if id not in by:raise WXError('RECIPE_INVALID',f'Missing node {id}')
        if id in visiting:raise WXError('RECIPE_INVALID','Recipe dependency cycle',node=id)
        if id in done:return
        visiting.add(id);n=by[id];reg=REGISTRY[n['operator']];inputs=n.get('inputs',{})
        if set(inputs)!=set(reg['inputs']):raise WXError('RECIPE_INVALID','Input port set mismatch',node=id,details={'expected':list(reg['inputs'])})
        for port,v in inputs.items():
            if not isinstance(v,dict) or set(v)!={'$node'}:raise WXError('RECIPE_INVALID','Input reference must be {$node: id}',node=id)
            dep=v['$node'];visit(dep)
            if REGISTRY[by[dep]['operator']]['output']!=reg['inputs'][port]:raise WXError('RECIPE_INVALID','Port type mismatch',node=id)
        params=validate_params(reg['schema'],resolve(n.get('params',{}),p,s.get('quality',PROFILES[s['profile']])))
        if n['operator']=='geometry.sdf' and params['resolution']**3*48>s['budgets']['sdf_bytes']:raise WXError('BUDGET_EXCEEDED','Estimated SDF working set exceeds budget',node=id)
        ordered.append({**n,'params':params});visiting.remove(id);done.add(id)
    for id in by:visit(id)
    outputs=r.get('outputs',[])
    if not outputs:raise WXError('RECIPE_INVALID','Recipe has no outputs')
    for o in outputs:
        if o not in by or REGISTRY[by[o]['operator']]['output']!='AssetIR':raise WXError('RECIPE_INVALID',f'Output must refer to AssetIR: {o}')
    if s['budgets']['triangles']<12:raise WXError('BUDGET_EXCEEDED','Triangle budget too small for these production recipes')
    code_files=['geometry.py','builders.py','operators.py','ir.py'];implementation=digest({f:sha256(code_path('wanxiang/'+f)) for f in code_files})
    lock={'recipe_sha256':sha256(path),'implementation_sha256':implementation,'operators':{n['operator']:n['operator_version'] for n in ordered},'seed':s['seed']}
    import importlib.metadata
    lock['dependencies']={id:importlib.metadata.version(id) for id in ['numpy','scipy','trimesh','scikit-image','Pillow']}
    return {'schema':'wx.plan/1.0','spec':s,'recipe':r,'params':p,'nodes':ordered,'outputs':outputs,'lock':lock,'plan_hash':digest({'spec':s,'lock':lock}),
       'estimated':{'geometry_nodes':len(nodes),'quality':s.get('quality',PROFILES[s['profile']]),'requires_gpu':False,'requires_blender':False,'host_requests':s['host_requests']}}
