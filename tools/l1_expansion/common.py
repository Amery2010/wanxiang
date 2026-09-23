"""Original L1 author vocabulary. Dimensions, datums and collider intent are data.

No frozen GLBs, no renamed colour variants, no random decoration used as identity.
Global metre parameters scale author-space frames (including translations), so
model dimensions and datums cannot silently diverge.
"""
from __future__ import annotations
from copy import deepcopy
import math
from foundation.common import (PARTS, part, box, cube, poly, loft, rod, lathe,
    extrude, ico, Q, O, mul, div, add, number, schema, port, C, P)
from expansion.production import formbox, frame, round_tube, ring, optional, authored_lod, DETAIL
from expansion.common import topo

ADDED=[]
DOMAIN_NAMES={'architecture':'建筑与模块化结构','interior':'室内与家具','nature':'自然与植被',
    'terrain':'地形与环境','props':'道具与场景杂物','vehicle':'车辆与交通','industry':'工业与工程设备',
    'character':'角色与穿戴','creature':'生物与生态','robot':'机器人与无人机','gameplay':'玩法交互组件'}
CATEGORIES={'architecture':'architecture','interior':'interior','nature':'nature','terrain':'terrain',
    'props':'props','vehicle':'vehicle','industry':'mechanism','character':'wear','creature':'animal',
    'robot':'robot','gameplay':'gameplay'}
TARGETS={'architecture':174,'interior':118,'nature':133,'terrain':58,'props':252,'vehicle':63,
    'industry':70,'character':38,'creature':22,'robot':35,'gameplay':69}
P.update(l1Slate='#566775',l1Ivory='#E5DCC8',l1Ochre='#BB8A4D',l1Terracotta='#A75F4C',
    l1Leaf='#70904D',l1LeafDark='#3F6547',l1Petal='#D9B2B0',l1Metal='#849598',l1Rubber='#303B40')


def matmul(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def transform_matrix(form):
    if 'matrix' in form:
        v=form['matrix'];return [[v[c*4+r] for c in range(4)] for r in range(4)]
    x,y,z=[math.radians(a) for a in form.get('rotation',[0,0,0])]
    cx,sx,cy,sy,cz,sz=math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(z),math.sin(z)
    a=[[cz*cy,cz*sy*sx-sz*cx,cz*sy*cx+sz*sx,0],
       [sz*cy,sz*sy*sx+cz*cx,sz*sy*cx-cz*sx,0],[-sy,cy*sx,cy*cx,0],[0,0,0,1]]
    for r in range(3):
        for c in range(3):a[r][c]*=form.get('scale',[1,1,1])[c]
        a[r][3]=form.get('position',[0,0,0])[r]
    return a


def placed(forms,position=(0,0,0),rotation=(0,0,0),scale=(1,1,1)):
    parent=transform_matrix({'position':position,'rotation':rotation,'scale':scale})
    out=[]
    for source in forms:
        f=deepcopy(source);m=matmul(parent,transform_matrix(f))
        for k in ('position','rotation','scale'):f.pop(k,None)
        f['matrix']=[m[r][c] for c in range(4) for r in range(4)];out.append(f)
    return out


def dimensions(forms,size):
    """Compose metre-space resizing outside the existing author transform."""
    factors=[div(Q(k),size[i]) for i,k in enumerate(('width','height','depth'))]
    result=[]
    for src in forms:
        f=deepcopy(src);m=transform_matrix(f)
        for k in ('position','rotation','scale'):f.pop(k,None)
        f['matrix']=[mul(m[r][c],factors[r]) if r<3 else m[r][c] for c in range(4) for r in range(4)]
        result.append(f)
    return result


def orient_poly(f):
    """Repair connected shell winding without a convex-centre assumption.

    No Boolean fusion, cap synthesis, open-surface closure or topology invention.
    Uniformly orient indexed faces; flip only closed positive-volume shells.
    """
    if f.get('kind')!='poly':return f
    from collections import defaultdict,deque
    vertices=f['points'];faces=deepcopy(f['faces'])
    if any(not isinstance(fc,list) for fc in faces):return f
    edges=defaultdict(list)
    for i,fc in enumerate(faces):
        for a,b in zip(fc,fc[1:]+fc[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
    adjacency=defaultdict(list)
    for values in edges.values():
        if len(values)==2:
            (a,x,y),(b,u,v)=values;adjacency[a].append((b,x==u and y==v));adjacency[b].append((a,x==u and y==v))
    seen={};components=[]
    for seed in range(len(faces)):
        if seed in seen:continue
        seen[seed]=False;q=deque([seed]);component=[]
        while q:
            a=q.popleft();component.append(a)
            for b,same in adjacency[a]:
                if b not in seen:seen[b]=seen[a]^same;q.append(b)
        components.append(component)
    for i,flip in seen.items():
        if flip:faces[i].reverse()
    for component in components:
        closed=all(len(edges[tuple(sorted((a,b)))])==2 for i in component for a,b in zip(faces[i],faces[i][1:]+faces[i][:1]))
        if not closed:continue
        volume=0.
        for i in component:
            fc=faces[i];a=vertices[fc[0]]
            for j in range(1,len(fc)-1):
                b=vertices[fc[j]];c=vertices[fc[j+1]]
                volume+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
        if volume<0:
            for i in component:faces[i].reverse()
    f['faces']=faces;return f


def register(domain,group,key,name,forms,size,*,material='mat.matte',description='',
             collision='authored-mesh',ports=None,detail=None,anchor='base',tags=(),purpose=None):
    ident=f'l1.{domain}.{group}.{key}'
    if ident in PARTS:raise ValueError('Duplicate stable ID: '+ident)
    if not forms or len(forms)>160:raise ValueError(f'{ident}: invalid form count {len(forms)}')
    size=list(size)
    if any(not math.isfinite(x) or x<=0 for x in size):raise ValueError('Invalid size')
    forms=[orient_poly(f) for f in deepcopy(forms)]
    roles={}
    for role,keys in {'mat.wood':('wood','woodDark','woodLight','bamboo'),
        'mat.metal':('metal','steel','l1Metal','copper','productionBrass'),
        'mat.rubber':('rubber','l1Rubber'),'mat.skin':('skin','skinShade'),
        'mat.hair':('hair','hairLight'),'mat.stone':('stone','stoneDark','stoneLight'),
        'mat.leaf':('l1Leaf','l1LeafDark','leaf','leafDark','leafLight'),
        'mat.glass':('glass',),'mat.emissive.cyan':('cyan',)}.items():
        for key_ in keys:
            if key_ in P:roles[C(key_)]=role
    for f in forms:
        if f.get('color') in roles:f.setdefault('material',roles[f['color']])
    if detail:
        for i in detail:forms[i]['enabled']=Q('detail')
    has_detail=any(f.get('enabled')==Q('detail') for f in forms)
    props={k:number(v,max(.003,v*.55),min(90,v*1.75),t,.01,'m')
        for k,v,t in zip(('width','height','depth'),size,('横向设计尺寸','竖向设计尺寸','纵深设计尺寸'))}
    if has_detail:props['detail']=DETAIL
    # Datums are explicit author planes, not a claim of physical auto-fit.
    datums=ports if ports is not None else [port('datum.mount',[0,0,0],[0,-1,0],[1,0,0]),
        port('datum.top',[0,size[1],0],[0,1,0],[1,0,0])]
    factors=[div(Q(k),size[i]) for i,k in enumerate(('width','height','depth'))]
    datums=deepcopy(datums)
    for p in datums:
        p['position']=[mul(p['position'][i],factors[i]) for i in range(3)]
        p['role']='author-datum; verify mating dimensions before assembly'
    c={'type':collision}
    if collision=='none':c['reason']='decorative/anatomy component; owning assembly authors collision'
    elif collision=='authored-mesh':c['static_only']=True
    elif collision=='convex-hull':c['static_only']=False
    ident=part(ident,name,CATEGORIES[domain],dimensions(forms,size),size,ports=datums,
        params=schema(**props),material=material,level=1,anchor=anchor,
        description=description or f'{name}；可复用的 {DOMAIN_NAMES[domain]} 语义部件，不包含上层设备行为。',
        tags=('L1-Expansion',domain,group,key,*tags))
    d=PARTS[ident]
    d.update(version='3.1.0',theme='l1-'+domain,quality={'status':'l1','review_scope':'L1-only',
        'approval':'not-user-approved','domain':domain,'visual_review':'pending-or-sampled'})
    d['source'].update(authoring='tools/l1_expansion/'+domain+'.py',revision='3.1.0',
        type='original_semantic_profiles',license='project-authored')
    d['runtime']={'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z',
        'origin':'authored-'+anchor+'-datum','collision':c,'triangle_budget':12000,
        'lod':authored_lod() if has_detail else {'levels':[],'reason':'simple primary silhouette; no redundant LOD'},
        'selection_bounds_are_colliders':False,'engine_adapter_required':True}
    d['semantic']={'domain':domain,'family':group,'profile':key,'purpose':purpose or name,
        'assembly_level':1,'counting':'one functional/structural profile; style, colour, scale and LOD excluded',
        'dimension_contract':'metre-space design dimensions; inspect actual bounds in build report',
        'datums':'orientation and placement references; generic surface ports are not certified snap joints',
        'consumer_example':'examples/l1/'+domain+'.json#'+ident,'status':'implemented-not-production-certified'}
    ADDED.append(ident)
    return ident


def plate(outline,depth=.12,color='l1Slate',**kw):
    return extrude(outline,depth,color,**kw)


def disk(radius=.3,height=.06,color='l1Metal',y=0,**kw):
    return lathe([[radius,y],[radius,y+height]],color,16,cap=True,**kw)


def arc(radius=.4,tube=.045,start=0,end=180,axis='xy',color='l1Metal',n=12,center=(0,0,0)):
    points=[]
    for i in range(n+1):
        a=math.radians(start+(end-start)*i/n);u,v=radius*math.cos(a),radius*math.sin(a)
        p=[u,v,0] if axis=='xy' else [u,0,v]
        points.append([p[j]+center[j] for j in range(3)]+[tube,tube])
    return loft(points,color,8)


def leaf_outline(kind='ovate',count=16):
    """Star-shaped, intentionally authored leaf profiles; no random seed shape."""
    out=[]
    for i in range(count):
        a=2*math.pi*i/count;sy=math.sin(a);cx=math.cos(a)
        if kind=='lanceolate':x=.20*cx*(.62+.38*abs(sy));y=.5+.5*sy
        elif kind=='cordate':x=.46*cx*(.88-.28*sy);y=.5+.42*sy-.14*max(sy,0)**5
        elif kind=='lobed':x=.42*cx*(1+.25*math.cos(a*5));y=.5+.46*sy*(1+.15*math.cos(a*5))
        elif kind=='serrate':x=.39*cx*(1+(.10 if i%2 else -.02));y=.5+.49*sy
        elif kind=='needle':x=.055*cx;y=.5+.5*sy
        elif kind=='fan':x=.46*cx*(.70+.30*sy);y=.5+.48*sy
        elif kind=='triangular':return [[0,0],[.43,.74],[0,1],[-.43,.74]]
        elif kind=='spade':x=.43*cx*(.74+.26*sy);y=.5+.47*sy
        elif kind=='strap':x=.14*cx;y=.5+.49*sy
        else:x=.35*cx;y=.5+.5*sy
        out.append([x,y])
    return out


def lens(outline,color='l1Leaf',thickness=.045,curve=.03):
    # Two face fans share a rim. A closed biconvex leaf has no paper-thin backface.
    n=len(outline);ps=[[x,y,curve*y*y] for x,y in outline]
    cy=sum(y for x,y in outline)/n
    cx=sum(x for x,y in outline)/n;cz=sum(z for x,y,z in ps)/n
    ps += [[cx,cy,cz+thickness],[cx,cy,cz-thickness]]
    fs=[]
    for i in range(n):fs.extend([[n,i,(i+1)%n],[n+1,(i+1)%n,i]])
    return topo(ps,fs,color)


def names(text):
    """Stable English IDs paired with concise Chinese author labels."""
    return [tuple(token.split(':',1)) for token in text.split()]


def finish(domain,expected=None):
    n=sum(PARTS[i]['quality']['domain']==domain for i in ADDED)
    if expected is not None and n!=expected:raise ValueError(f'{domain}: {n}, expected {expected}')
    return n
