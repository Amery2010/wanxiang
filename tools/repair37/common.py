"""Metric, named source geometry used by the v3.7.1 recovery repair.

No baked meshes, random model grading, hidden transforms, or palette-only assets.
Private author parts preserve editable assembly node boundaries and are excluded
from the public catalogue, but remain in the dependency graph and export bundle.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json, math
from foundation.common import PARTS, ASSEMBLIES, MOTIONS, box, cube, loft, lathe, poly, inst, schema, Q
from l1_expansion.common import orient_poly, placed

REV='3.7.1'
REPAIRS=[]
INTERNAL=set()

def reset():
    REPAIRS.clear(); INTERNAL.clear()

def mesh(points, faces, color, **kw):
    f=poly([[float(v) for v in p] for p in points],faces,color,**kw)
    f=orient_poly(f)
    f['roundable']=False
    f.setdefault('style_overrides',{'toon':{'smooth_angle':65}})
    return f

def block(size, at=(0,0,0), color='#BDAF8D', bevel=.015, **kw):
    if 'rot' in kw:kw['rotation']=kw.pop('rot')
    return cube(list(size),color,list(at),**kw) if bevel<=0 else box(list(size),color,list(at),bevel,**kw)

def basebox(size, at=(0,0,0), color='#BDAF8D', **kw):
    return block(size,[at[0],at[1]+size[1]/2,at[2]],color,**kw)

def ellipsoid(at, size, color, segments=12, rings=6, **kw):
    """Watertight non-distorted ellipsoid, one pole vertex per end."""
    x,y,z=at;rx,ry,rz=[v/2 for v in size];p=[[x,y-ry,z]]
    for j in range(1,rings):
        a=-math.pi/2+math.pi*j/rings
        for i in range(segments):
            b=math.tau*i/segments;p.append([x+rx*math.cos(a)*math.cos(b),y+ry*math.sin(a),z+rz*math.cos(a)*math.sin(b)])
    top=len(p);p.append([x,y+ry,z]);f=[]
    for i in range(segments):f.append([0,1+(i+1)%segments,1+i])
    for j in range(rings-2):
        for i in range(segments):
            a=1+j*segments+i;b=1+j*segments+(i+1)%segments;f.append([a,b,b+segments,a+segments])
    for i in range(segments):f.append([top,1+(rings-2)*segments+i,1+(rings-2)*segments+(i+1)%segments])
    return mesh(p,f,color,**kw)

def revolve(profile, color, sides=16, closed=True, at=(0,0,0), **kw):
    """Closed radial profile; source normals are oriented, not double-side masked."""
    p=[]
    for r,y in profile:
        for i in range(sides):
            a=math.tau*i/sides;p.append([at[0]+r*math.cos(a),at[1]+y,at[2]+r*math.sin(a)])
    f=[];m=len(profile)
    for j in range(m if closed else m-1):
        for i in range(sides):f.append([j*sides+i,j*sides+(i+1)%sides,((j+1)%m)*sides+(i+1)%sides,((j+1)%m)*sides+i])
    if not closed:
        f += [list(range(sides-1,-1,-1)),list(range((m-1)*sides,m*sides))]
    return mesh(p,f,color,**kw)

def profile_z(stations,color,sides=12,**kw):
    """Each section: (z, centre_y, half_width, half_height[, centre_x])."""
    ps=[]
    for row in stations:
        z,y,rx,ry=row[:4];x=row[4] if len(row)>4 else 0
        for i in range(sides):
            a=math.tau*i/sides;ps.append([x+rx*math.cos(a),y+ry*math.sin(a),z])
    faces=[]
    for j in range(len(stations)-1):
        for i in range(sides):
            a=j*sides+i;b=j*sides+(i+1)%sides;faces.append([a,b,b+sides,a+sides])
    faces += [list(range(sides-1,-1,-1)),list(range((len(stations)-1)*sides,len(stations)*sides))]
    return mesh(ps,faces,color,**kw)

def tube(points,radii,color,sides=8,**kw):
    if isinstance(radii,(float,int)):radii=[radii]*len(points)
    rr=[]
    for p,r in zip(points,radii):rr.append(list(p)+([r,r] if isinstance(r,(float,int)) else list(r)))
    f=loft(rr,color,sides=min(16,sides),roundable=False,**kw)
    f.setdefault('style_overrides',{'toon':{'smooth_angle':70}})
    return f

def beam(a,b,width,color='#6F7774',depth=None,**kw):
    # A rectangular beam follows the same transported frame as an organic tube.
    return tube([a,b],[(width/2,(depth or width)/2)]*2,color,4,twist=math.pi/4,**kw)

def slab_polygon(outline,y,thickness,color,**kw):
    p=[[x,y,z] for x,z in outline]+[[x,y+thickness,z] for x,z in outline];n=len(outline)
    f=[list(range(n-1,-1,-1)),list(range(n,n*2))]
    f.extend([[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)])
    return mesh(p,f,color,**kw)

def extrude_xy(outline,depth,color,z=0,**kw):
    p=[[x,y,z-depth/2] for x,y in outline]+[[x,y,z+depth/2] for x,y in outline];n=len(outline)
    f=[list(range(n-1,-1,-1)),list(range(n,n*2))]
    f.extend([[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)])
    return mesh(p,f,color,**kw)

def leaf(root,tip,width,color='#6E914B',curve=.12,thickness=.012,**kw):
    """Tapered continuous leaf with midrib ridge and connected underside."""
    dx,dy,dz=[tip[k]-root[k] for k in range(3)];flat=math.hypot(dx,dz)
    side=[-dz/flat,0,dx/flat] if flat>1e-7 else [1,0,0]
    rows=[]
    for t,w in [(0,.015),(.2,.6),(.5,1),(.78,.65),(1,.008)]:
        c=[root[k]+(tip[k]-root[k])*t for k in range(3)];c[1]+=curve*math.sin(math.pi*t)
        rows.append([[c[k]+side[k]*width*w*.5*s+(thickness*.5 if k==1 and s==0 else 0) for k in range(3)] for s in (-1,0,1)])
    p=[p for row in rows for p in row];p += [[x,y-thickness,z] for x,y,z in p];n=15;f=[]
    for j in range(4):
        for i in range(2):
            a=j*3+i;f.extend([[a,a+1,a+4,a+3],[n+a+3,n+a+4,n+a+1,n+a]])
    edge=[0,3,6,9,12,13,14,11,8,5,2,1]
    for a,b in zip(edge,edge[1:]+edge[:1]):f.append([a,b,b+n,a+n])
    return mesh(p,f,color,**kw)

def arch(width,height,depth,thick=.2,color='#A6A49A',at=(0,0,0),segments=16):
    rx=width/2;rise=min(height*.62,rx);spring=height-rise
    outer=[];inner=[]
    for i in range(segments+1):
        a=math.pi-math.pi*i/segments;outer.append([at[0]+rx*math.cos(a),at[1]+spring+rise*math.sin(a)])
        inner.append([at[0]+(rx-thick)*math.cos(a),at[1]+spring+(rise-thick)*math.sin(a)])
    outline=[[at[0]-rx,at[1]],*outer,[at[0]+rx,at[1]],[at[0]+rx-thick,at[1]],*reversed(inner),[at[0]-rx+thick,at[1]]]
    return extrude_xy(outline,depth,color,z=at[2])

def roof(width,depth,y,rise,color='#6C7C80',kind='gable',thick=.12):
    w=width/2
    if kind=='flat':return [basebox([width,thick,depth],[0,y,0],color)]
    if kind=='gambrel':top=[[-w,y],[-w*.56,y+rise*.72],[0,y+rise],[w*.56,y+rise*.72],[w,y]]
    elif kind=='barrel':top=[[-w+width*i/16,y+rise*math.sin(math.pi*i/16)] for i in range(17)]
    else:top=[[-w,y],[0,y+rise],[w,y]]
    bottom=[[x,yy-thick] for x,yy in reversed(top)]
    return [extrude_xy(top+bottom,depth,color)]

def node(ident,name,forms,*,material='mat.matte',at=None,rot=None,parent=None,pivot=None):
    """A private semantic source part, not a new public catalogue asset."""
    pid='r37.'+ident+'.'+name
    forms=deepcopy(forms)
    if not forms:raise ValueError('Empty repair geometry '+pid)
    for f in forms:
        f.setdefault('roundable',False)
    PARTS[pid]={'schema':'wx.part/1.0','id':pid,'name':name,'version':REV,'level':1,
        'internal':True,'category':'props','shape':'faceted','size':[1,1,1],'anchor':'origin','material':material,
        'connectors':[],'shape_params':{'forms':forms},'parameter_schema':schema(),
        'source':{'type':'original_repair_source','authoring':'tools/repair37/common.py','revision':REV,'license':'project-authored'},
        'quality':{'status':'foundation','review_scope':'v3.7.1 authored correction; see repair report'},
        'description':'Private editable semantic geometry for '+ident,'tags':['repair-internal'],
        'runtime':{'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','origin':'authored',
                   'triangle_budget':30000,'collision':{'type':'authored-mesh','static_only':True},'lod':{'levels':[]}}}
    # Keep the bounded declarative evaluator intact. Large semantic groups are
    # made of bounded private components rather than raising its safety budget.
    def cost(value):
        if isinstance(value,dict):return 1+sum(cost(x) for x in value.values())
        if isinstance(value,list):return 1+sum(cost(x) for x in value)
        return 1
    if cost(forms)>65000:
        groups=[];group=[];total=0
        for form in forms:
            n=cost(form)
            if n>65000:raise ValueError('Individual form exceeds authoring evaluation budget '+pid)
            if total+n>60000:groups.append(group);group=[];total=0
            group.append(form);total+=n
        if group:groups.append(group)
        PARTS[pid]['shape_params']={'components':[]}
        for i,group in enumerate(groups):
            child=pid+'.chunk'+str(i);definition=deepcopy(PARTS[pid]);definition['id']=child
            definition['shape_params']={'forms':group};PARTS[child]=definition;INTERNAL.add(child)
            PARTS[pid]['shape_params']['components'].append({'id':'chunk'+str(i),'part':child})
    INTERNAL.add(pid)
    v=inst(name,pid,pos=at,rot=rot)
    if parent:v['parent']=parent
    if pivot is not None:v['pivot']=list(pivot)
    return v

def record(ident,problem,change,scope='structure'):
    if ident not in PARTS and ident not in ASSEMBLIES:raise KeyError(ident)
    REPAIRS.append({'id':ident,'problem':problem,'change':change,'scope':scope,'revision':REV,
                    'visual_status':'pending-render-review','commercial_certification':False})

def replace(ident,items,problem,change,size=None,controls=None):
    d=ASSEMBLIES[ident]
    old_nodes=[n['id'] for n in d.get('instances',[])]
    d['instances']=items;d['version']=REV;md=d.setdefault('metadata',{})
    md.setdefault('source',{}).update(authoring='tools/repair37/__init__.py',revision=REV)
    md['repair37']={'baseline':'3.5.0','source':'tools/repair37','old_root_nodes':old_nodes,
                    'retained_root_nodes':sorted(set(old_nodes)&{i['id'] for i in items}),
                    'geometry_redesigned':True,'prior_visual_claims_not_inherited':True}
    md['state_controls']=controls or []
    if ident in MOTIONS:MOTIONS.pop(ident)
    if size:
        md.setdefault('production',{}).update(dimensions_design_m=list(size),footprint_m=[size[0],size[2]])
    md.setdefault('runtime',{}).setdefault('lod',{'levels':[]})
    record(ident,problem,change)

def rotation_control(name,node_id,title,axis,maximum=95):
    return {'id':name,'title':title,'node':node_id,'axis':list(axis),'mode':'rotation','min':0,'max':maximum,'default':0,'unit':'deg','step':1}

def add_motion(ident,controls):
    if not controls:return
    MOTIONS[ident]={'schema':'wx.rigid-motion/1.0','assembly':ident,'binding':'rigid','clips':[
        {'name':c['id']+'_inspect','duration':3,'tracks':[{'node':c['node'],'axis':c['axis'],'degrees':[0,c['max'],0]}]} for c in controls]}

def retain_editable_groups():
    """Preserve the catalogue's two-node editing contract without adding geometry.

    Multi-form assemblies expose their main volume and detail forms separately.
    A single closed poly exposes its bottom surface as a second editable group;
    all original faces are retained exactly once, with no duplicate/coincident cap.
    The joined asset remains the same solid, not two artificial overlapping solids.
    """
    for ident in {r['id'] for r in REPAIRS}:
        d=ASSEMBLIES.get(ident)
        if not d or len(d['instances'])!=1:continue
        root=d['instances'][0];pid=root.get('part');part=PARTS.get(pid,{})
        if not part.get('internal'):continue
        sp=part['shape_params'];other=deepcopy(part);newpid=pid+'.detail_group';other['id']=newpid
        if len(sp.get('forms',[]))>1:
            forms=sp['forms'];sp['forms']=forms[:1];other['shape_params']={'forms':forms[1:]}
        elif len(sp.get('components',[]))>1:
            comps=sp['components'];sp['components']=comps[:1];other['shape_params']={'components':comps[1:]}
        elif len(sp.get('forms',[]))==1 and sp['forms'][0].get('kind')=='poly':
            form=sp['forms'][0];points=form['points'];faces=form['faces'];bottom=min(p[1] for p in points)
            def ids(face):return face.get('v',[]) if isinstance(face,dict) else face
            lower=[j for j,f in enumerate(faces) if all(points[k][1]<=bottom+1e-7 for k in ids(f))]
            if not lower or len(lower)==len(faces):
                # Closed arch side caps have a different plane from the horizontal base.
                lower=[0]
            keep=[j for j in range(len(faces)) if j not in set(lower)];f1=deepcopy(form);f2=deepcopy(form)
            f1['faces']=[faces[j] for j in keep];f2['faces']=[faces[j] for j in lower]
            if form.get('colors'):
                f1['colors']=[form['colors'][j] for j in keep];f2['colors']=[form['colors'][j] for j in lower]
            sp['forms']=[f1];other['shape_params']={'forms':[f2]}
        else:raise ValueError('Single-node production asset needs authored groups: '+ident)
        PARTS[newpid]=other;INTERNAL.add(newpid)
        item=deepcopy(root);item['id']=root['id']+'_detail';item['part']=newpid;d['instances'].append(item)
        d['metadata']['repair37']['editable_group_split']='same geometry; each original face/form retained exactly once'


def bound_private_instances():
    """Partition large authored groups without changing the shape or safety caps.

    Additional groups are children of the original instance so rigid controls
    and pivot transforms apply once to the entire object, not only its first chunk.
    A conservative maximum-style estimate bounds every part below 30k triangles.
    """
    def forms_of(pid):
        sp=PARTS[pid]['shape_params'];out=list(sp.get('forms',[]))
        for child in sp.get('components',[]):
            if any(k in child for k in ('position','rotation','scale','matrix')):
                raise ValueError('Budget partition requires explicit identity component '+pid)
            out.extend(forms_of(child['part']))
        return out
    def triangles(f):
        kind=f['kind']
        if kind=='bevelbox':return 128
        if kind=='poly':return sum(max(0,len(fc if isinstance(fc,list) else fc['v'])-2) for fc in f['faces'])
        if kind=='loft':
            n=f.get('sides',8);return 2*n*(len(f['rings'])-1)+2*(n-2)
        if kind=='ico':return 80 if f.get('detail') else 20
        raise ValueError('Unestimated repair shape '+kind)
    for aid in sorted({r['id'] for r in REPAIRS}):
        assembly=ASSEMBLIES.get(aid)
        if not assembly:continue
        added=[]
        for instance in list(assembly['instances']):
            pid=instance.get('part');part=PARTS.get(pid,{})
            if not part.get('internal'):continue
            forms=forms_of(pid)
            if sum(triangles(f) for f in forms)<=22000 and len(forms)<=600:continue
            groups=[];group=[];count=0
            for form in forms:
                weight=triangles(form)
                if weight>22000:raise ValueError('Individual form exceeds partition budget '+pid)
                if group and (count+weight>22000 or len(group)>=580):groups.append(group);group=[];count=0
                group.append(form);count+=weight
            if group:groups.append(group)
            # node() also partitions the declarative expression evaluation cost.
            for j,group in enumerate(groups):
                item=node(aid,instance['id'] if j==0 else instance['id']+'_batch'+str(j),group,material=part['material'])
                if j==0:instance['part']=item['part']
                else:item['parent']=instance['id'];added.append(item)
            assembly['metadata']['repair37']['budget_partition']='same authored forms; <=22000 estimated maximum-style triangles per private part'
        assembly['instances'].extend(added)
