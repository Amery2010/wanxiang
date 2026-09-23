"""Safe JSON parameter expressions. Geometry stays in the shared JS kernel."""
from __future__ import annotations
import copy, math
from .errors import WXError
RESERVED={'size','uv_scale','palette','roundness','voxel_resolution','seed'}
def fail(message):raise WXError('RECIPE_INVALID','SEMANTIC_INVALID: '+message)
def parameter_values(schema, supplied):
    if not isinstance(supplied,dict):fail('Parameters must be an object')
    props=schema.get('properties',{});values={}
    if len(props)>32:fail('Parameter budget')
    if set(supplied)-RESERVED-set(props):fail('Unknown parameter: '+str(set(supplied)-RESERVED-set(props)))
    for key,p in props.items():
        v=supplied.get(key,p.get('default'))
        if key in {'__proto__','constructor','prototype'}:fail('Reserved parameter')
        if 'enum' in p:
            if v not in p['enum']:fail(key+' is outside declared choices')
        elif p.get('type')=='boolean':
            if not isinstance(v,bool):fail(key+' must be boolean')
        elif isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or (p.get('type')=='integer' and v!=int(v)) or v<p.get('minimum',-math.inf) or v>p.get('maximum',math.inf):fail(key+' outside range')
        values[key]=v
    return values

def evaluate(value,values,depth=0,budget=None):
    if budget is None:budget=[0]
    budget[0]+=1
    if depth>48 or budget[0]>100000:fail('Expression budget')
    ev=lambda v:evaluate(v,values,depth+1,budget)
    if isinstance(value,list):return [ev(v) for v in value]
    if not isinstance(value,dict):return value
    if '$param' in value:
        if value['$param'] not in values:fail('Unknown parameter reference')
        return values[value['$param']]
    if '$switch' in value:
        key=values.get(value['$switch']);key=str(key).lower() if isinstance(key,bool) else str(key)
        return ev(value.get('cases',{}).get(key,value.get('default')))
    if '$op' in value:
        a=ev(value.get('args'))
        if not isinstance(a,list) or not 1<=len(a)<=8 or any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) for x in a):fail('Numeric expression arguments')
        op=value['$op']
        if op in ('sub','div') and len(a)!=2:fail('Binary expression arity')
        if op=='div' and abs(a[1])<1e-10:fail('Division by zero')
        f={'add':lambda:sum(a),'mul':lambda:math.prod(a),'sub':lambda:a[0]-a[1],'div':lambda:a[0]/a[1],'min':lambda:min(a),'max':lambda:max(a),'sin':lambda:math.sin(math.radians(a[0])),'cos':lambda:math.cos(math.radians(a[0])),'sqrt':lambda:math.sqrt(a[0]),'neg':lambda:-a[0],'abs':lambda:abs(a[0])}
        if op not in f:fail('Unknown expression operation')
        try:v=f[op]()
        except (ValueError,ZeroDivisionError):fail('Invalid numeric expression')
        if not math.isfinite(v) or abs(v)>1e6:fail('Non-finite expression')
        return v
    if any(k in value for k in ('__proto__','constructor','prototype')):fail('Unsafe object key')
    return {k:ev(v) for k,v in value.items()}

def assembly(spec):
    schema=spec.get('metadata',{}).get('parameter_schema')
    if not schema:return copy.deepcopy(spec)
    values=parameter_values(schema,spec.get('metadata',{}).get('parameters',{}))
    result=evaluate(spec,values);result['metadata']['resolved_parameters']=values
    return result
