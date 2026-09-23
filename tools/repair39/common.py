"""v3.9 authored silhouettes. Geometry helpers are not aesthetic classifiers.

All units are metres, +Y up/+Z forward. Existing public identifiers, parameter
schemas and sockets survive replacement. Angular profiles use degrees-v1;
legacy ``twist`` radians retain their historical interpretation.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import math, json, hashlib
import numpy as np
from foundation.common import PARTS, ASSEMBLIES, Q, O, C, P, number, choice, mul, add, box, cube, loft, poly, extrude, lathe
from l1_expansion.common import dimensions, placed, orient_poly
from repair37.common import mesh as _legacy_mesh, block, basebox, ellipsoid, profile_z, leaf, tube, beam, slab_polygon, extrude_xy


def mesh(points,faces,color,**kw):
    """Orient the whole closed shell even when individual faces carry colours.

    The older orienter intentionally skips dict faces. Strip only the attributes
    temporarily, orient connected components, then restore attributes verbatim.
    """
    original=deepcopy(faces)
    indices=[f if isinstance(f,list) else f['v'] for f in original]
    result=_legacy_mesh(points,indices,color,**kw)
    result['faces']=[q if isinstance(old,list) else {**old,'v':q} for old,q in zip(original,result['faces'])]
    return result


REV='3.9.0'
ROOT=Path(__file__).resolve().parents[2]
CHANGES=[]
BASELINE={}
FINDINGS={}


def digest(d):
    return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def start():
    # Concrete colour values, never silently pass unknown CSS colour names.
    P.update(metalLight='#B7C3C5', metalDark='#45535A')
    CHANGES.clear(); BASELINE.clear(); FINDINGS.clear()
    FINDINGS.update({r['id']:r for r in json.loads((ROOT/'authoring/repair39-findings.json').read_text())})
    BASELINE.update({i:deepcopy(PARTS[i]) for i in FINDINGS})


def apply(ident, forms, change, *, dimensioned=True, parameters=None, contracts=None, detail=None):
    """Replace in the author graph, not only the generated JSON. No auto-fitting.

    Retaining design size is intentional: it is a parameter unit, not a promise
    that the author's occupied bounds are identical to that design box.
    """
    if ident not in BASELINE: raise KeyError('Unregistered audit target '+ident)
    if any(x['id']==ident for x in CHANGES): raise ValueError('Duplicate repair '+ident)
    d=PARTS[ident]
    fs=deepcopy(forms)
    if not fs: raise ValueError('Empty repair '+ident)
    props=d.get('parameter_schema',{}).get('properties',{})
    if parameters:
        props=d.setdefault('parameter_schema',{'type':'object','additionalProperties':False,'properties':{}})['properties']
        props.update(deepcopy(parameters))
    for k,f in enumerate(fs):
        f.setdefault('roundable',False)
        f.setdefault('name',f'{ident.rsplit(".",1)[-1]}_{k:02d}')
        # Explicit authored normals; a style change cannot secretly change a hole.
        f.setdefault('style_overrides',{'toon':{'smooth_angle':55}})
    if detail:
        if props.get('detail',{}).get('type')!='boolean': raise ValueError('detail requires boolean schema')
        for k in detail: fs[k]['enabled']=Q('detail')
    if dimensioned and all(k in props for k in ('width','height','depth')):
        fs=dimensions(fs,d['size'])
    # Preserve rig/component semantics if present; these audit entries have no rigs.
    if d['shape_params'].get('components') or d['shape_params'].get('rig'):
        raise ValueError('Explicit migration required for composite/rig '+ident)
    before=digest(d['shape_params'])
    d['shape_params']={'forms':fs}
    if before==digest(d['shape_params']): raise ValueError('Repair did not change geometry '+ident)
    d['version']=REV
    import inspect
    module=Path(inspect.currentframe().f_back.f_code.co_filename).name
    d.setdefault('source',{}).update(authoring='tools/repair39/'+module,revision=REV,type='original_structural_lowpoly_rebuild')
    d.setdefault('quality',{})['repair39']={'audit_id':ident,'scope':'authored-geometry; current evidence/v3.9.0','commercial_certification':False}
    d['repair39']={'baseline':'3.8.0','change':change,'stable_public_id':True,
        'connector_contract':'existing named sockets preserved; contact tests in release evidence',
        'contracts':contracts or {},'legacy_geometry_sha256':before,'source_revision':REV}
    d.setdefault('tags',[]).append('Advanced-Lowpoly-3.9')
    CHANGES.append({'id':ident,'name':d['name'],'priority':FINDINGS[ident]['priority'],
        'original_observation':FINDINGS[ident]['observation'],'change':change,'source':d['source']['authoring'],
        'old_geometry_sha256':before,'new_geometry_sha256':digest(d['shape_params']),
        'public_id_retained':True,'visual_review':'pending-manual-render-review',
        'parameter_names_retained':sorted(BASELINE[ident].get('parameter_schema',{}).get('properties',{})),
        'contracts':contracts or {}})


def rect(w,h,c=(0,0),r=0):
    x,y=c
    if r<=0:return [[x-w/2,y-h/2],[x+w/2,y-h/2],[x+w/2,y+h/2],[x-w/2,y+h/2]]
    out=[]
    for cx,cy,a in [(x+w/2-r,y+h/2-r,0),(x-w/2+r,y+h/2-r,90),(x-w/2+r,y-h/2+r,180),(x+w/2-r,y-h/2+r,270)]:
        for j in range(4):
            t=math.radians(a+j*90/3);out.append([cx+r*math.cos(t),cy+r*math.sin(t)])
    return out


def circle(r,c=(0,0),n=24,scale=(1,1)):
    return [[c[0]+r*scale[0]*math.cos(i*math.tau/n),c[1]+r*scale[1]*math.sin(i*math.tau/n)] for i in range(n)]


def plate(outer, depth, color, *, holes=None, at=(0,0,0), **kw):
    return extrude(outer,depth,C(color),holes=holes or [],position=list(at),**kw)


def spin(profile,color,sides=24,at=(0,0,0),**kw):
    """Revolve a CLOSED cross-section, welding axis poles at author time."""
    pp=[];rings=[]
    for r,y in profile:
        if abs(r)<1e-10:
            rings.append([len(pp)]);pp.append([at[0],at[1]+y,at[2]])
        else:
            rings.append(list(range(len(pp),len(pp)+sides)))
            pp.extend([[at[0]+r*math.cos(i*math.tau/sides),at[1]+y,at[2]+r*math.sin(i*math.tau/sides)] for i in range(sides)])
    ff=[]
    for j,A in enumerate(rings):
        B=rings[(j+1)%len(rings)]
        if len(A)==len(B)==1:continue
        for k in range(sides):
            q=[A[k%sides] if len(A)>1 else A[0],A[(k+1)%sides] if len(A)>1 else A[0],B[(k+1)%sides] if len(B)>1 else B[0],B[k%sides] if len(B)>1 else B[0]]
            q=list(dict.fromkeys(q))
            if len(q)>=3:ff.append(q)
    return mesh(pp,ff,C(color),**kw)


def cyl(r,h,color,at=(0,0,0),sides=16,**kw):
    return spin([(0,0),(r,0),(r,h),(0,h)],color,sides,at,**kw)


def bezier(points,n=16):
    ps=np.asarray(points,dtype=float);degree=len(ps)-1
    return [sum(math.comb(degree,j)*(1-t)**(degree-j)*t**j*ps[j] for j in range(degree+1)).tolist() for t in np.linspace(0,1,n)]


def sweep(path, section, color, *, closed_path=False, **kw):
    """Parallel-transport frame, watertight section sweep. Ends are not cylinders.

    section is an explicitly closed polygon, so a U section remains a U section.
    closed_path omits duplicate end rings and adds the final band (no internal caps).
    """
    path=np.asarray(path,float)
    if closed_path and np.linalg.norm(path[0]-path[-1])<1e-8:path=path[:-1]
    n=len(path);sec=np.asarray(section,float);m=len(sec)
    if n<2 or m<3:raise ValueError('Sweep requires path and cross section')
    tang=[]
    for j in range(n):
        t=(path[(j+1)%n]-path[(j-1)%n]) if closed_path else path[min(j+1,n-1)]-path[max(0,j-1)]
        norm=np.linalg.norm(t)
        if norm<1e-10:raise ValueError('Degenerate sweep tangent')
        tang.append(t/norm)
    ref=np.array([1.,0,0]) if abs(tang[0][0])<.85 else np.array([0,0,1.])
    u=ref-tang[0]*np.dot(ref,tang[0]);u/=np.linalg.norm(u)
    pp=[]
    for j,t in enumerate(tang):
        u=u-t*np.dot(u,t);u/=np.linalg.norm(u);v=np.cross(t,u)
        for x,y in sec:pp.append((path[j]+u*x+v*y).tolist())
    ff=[]
    for j in range(n if closed_path else n-1):
        for k in range(m):ff.append([j*m+k,j*m+(k+1)%m,((j+1)%n)*m+(k+1)%m,((j+1)%n)*m+k])
    if not closed_path:ff += [list(range(m-1,-1,-1)),list(range((n-1)*m,n*m))]
    return mesh(pp,ff,C(color),**kw)


def pipe(path,r,wall,color='metal',n=16,**kw):
    """Hollow sweep with annular ends. It never caps the fluid channel."""
    # One C-shaped section with a coincident seam is not needed: explicit rings.
    path=np.asarray(path,float);N=len(path);u=np.array([1.,0,0]);pp=[]
    for j,p in enumerate(path):
        t=path[min(N-1,j+1)]-path[max(0,j-1)];t/=np.linalg.norm(t)
        if abs(np.dot(u,t))>.95:u=np.array([0.,0,1.])
        u-=t*np.dot(u,t);u/=np.linalg.norm(u);v=np.cross(t,u)
        for rad in (r,r-wall):
            for k in range(n):pp.append((p+rad*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n))).tolist())
    ff=[]
    for j in range(N-1):
        for b in (0,n):
            for k in range(n):a=j*2*n+b+k;bb=j*2*n+b+(k+1)%n;ff.append([a,bb,bb+2*n,a+2*n])
    for j in (0,N-1):
        for k in range(n):a=j*2*n+k;b=j*2*n+(k+1)%n;ff.append([a,b,b+n,a+n])
    return mesh(pp,ff,C(color),**kw)


def grid_shell(fn,nu,nv,thickness,color,*,axis=(0,1,0),**kw):
    """Closed thin sheet with shared surface vertices and a continuous perimeter."""
    top=[list(fn(i/nu,j/nv)) for j in range(nv+1) for i in range(nu+1)];N=len(top)
    pp=top+[[p[k]-thickness*axis[k] for k in range(3)] for p in top];ff=[]
    for j in range(nv):
        for i in range(nu):
            a=j*(nu+1)+i;b=a+1;c=b+nu+1;d=a+nu+1
            ff += [[a,b,c,d],[N+d,N+c,N+b,N+a]]
    edge=[i for i in range(nu+1)]+[j*(nu+1)+nu for j in range(1,nv+1)]+[nv*(nu+1)+i for i in range(nu-1,-1,-1)]+[j*(nu+1) for j in range(nv-1,0,-1)]
    for a,b in zip(edge,edge[1:]+edge[:1]):ff.append([a,N+a,N+b,b])
    return mesh(pp,ff,C(color),**kw)


def ring_tube(center,rx,ry,r,color,plane='xy',n=32,sides=8):
    path=[]
    for i in range(n):
        a=i*math.tau/n;v=[rx*math.cos(a),ry*math.sin(a),0]
        if plane=='xz':v=[v[0],0,v[1]]
        if plane=='yz':v=[0,v[0],v[1]]
        path.append([center[k]+v[k] for k in range(3)])
    return sweep(path,circle(r,n=sides),color,closed_path=True)


def organic_profile(stations,color,sides=16,**kw):
    """Y stations (y, half-width, front-depth, back-depth, centre-z).
    Stable rings give separate forehead / cheek / muzzle / jaw controls.
    """
    pp=[]
    for y,w,front,back,z in stations:
        for k in range(sides):
            a=k*math.tau/sides;s=math.sin(a)
            pp.append([w*math.cos(a),y,z+(front if s>=0 else back)*s])
    ff=[]
    for j in range(len(stations)-1):
        for k in range(sides):a=j*sides+k;b=j*sides+(k+1)%sides;ff.append([a,b,b+sides,a+sides])
    ff.extend([list(range(sides-1,-1,-1)),list(range((len(stations)-1)*sides,len(stations)*sides))])
    return mesh(pp,ff,C(color),**kw)


def face_patch(outline,depth,color,at=(0,0,0),**kw):
    return plate(outline,depth,color,at=at,**kw)


def shape_extruded(poly2d,y,thickness,color):
    """Shapely polygon to closed slab, including holes, used only by authors."""
    p=plate(list(poly2d.exterior.coords)[:-1],thickness,color,
            holes=[list(h.coords)[:-1] for h in poly2d.interiors])
    # XY author plane becomes XZ, top at y+thickness, extrusion is centred on Z.
    return placed([p],[0,y+thickness/2,0],[90,0,0])[0]


def finish():
    missing=set(FINDINGS)-{r['id'] for r in CHANGES}
    if missing:raise ValueError('Repair source coverage incomplete: '+', '.join(sorted(missing)))
    for i,old in BASELINE.items():
        new=PARTS[i]
        if new.get('connectors')!=old.get('connectors'):raise ValueError('Socket migration not authorised '+i)
        if new.get('anchor')!=old.get('anchor') or new.get('size')!=old.get('size'):raise ValueError('Design datum changed '+i)


def surface_coordinate(body,uv,axis=2):
    """Ray-project a decoration onto its actual authored supporting shell.

    Projection failure is an authoring error, never a licence to leave a floater.
    Body must be a numeric polygon in its local author space.
    """
    ps=np.asarray(body['points'],float);other=[i for i in range(3) if i!=axis];best=-math.inf
    u,v=uv
    for face in body['faces']:
        indices=face if isinstance(face,list) else face['v']
        for j in range(1,len(indices)-1):
            tri=ps[[indices[0],indices[j],indices[j+1]]];a,b,c=tri[:,other]
            det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(det)<1e-12:continue
            w0=((b[1]-c[1])*(u-c[0])+(c[0]-b[0])*(v-c[1]))/det
            w1=((c[1]-a[1])*(u-c[0])+(a[0]-c[0])*(v-c[1]))/det
            w2=1-w0-w1
            if min(w0,w1,w2)>=-1e-7:best=max(best,float(w0*tri[0,axis]+w1*tri[1,axis]+w2*tri[2,axis]))
    if not math.isfinite(best):raise ValueError(f'Decoration {uv} misses its supporting shell')
    return best


def surface_patch(body,outline,color,offset=.001,axis=2):
    """Clip a patch to every visible supporting triangle before ray projection.

    Merely projecting the boundary creates chords through a faceted skull and
    the familiar floating/splintered decal defect. This function splits along
    *all* source triangle edges, then welds the patch and gives it a thin back.
    """
    from shapely.geometry import Polygon
    from shapely.ops import triangulate
    region=Polygon(outline)
    if not region.is_valid:raise ValueError('Self-intersecting surface patch')
    ps=np.asarray(body['points'],float);other=[i for i in range(3) if i!=axis]
    pp=[];ff=[];keys={};covered=0
    def vertex(uv):
        key=tuple(round(float(x),11) for x in uv)
        if key not in keys:
            p=[0.,0.,0.];p[other[0]],p[other[1]]=uv
            p[axis]=surface_coordinate(body,uv,axis)+offset
            keys[key]=len(pp);pp.append(p)
        return keys[key]
    for face in body['faces']:
        ids=face if isinstance(face,list) else face['v']
        for j in range(1,len(ids)-1):
            tri=ps[[ids[0],ids[j],ids[j+1]]]
            if np.cross(tri[1]-tri[0],tri[2]-tri[0])[axis]<=1e-12:continue
            projected=Polygon(tri[:,other]);cut=region.intersection(projected)
            if cut.is_empty or cut.area<1e-13:continue
            for piece in getattr(cut,'geoms',[cut]):
                if piece.geom_type!='Polygon' or piece.area<1e-13:continue
                covered+=piece.area
                for t in triangulate(piece):
                    if not piece.covers(t.representative_point()):continue
                    uv=list(t.exterior.coords)[:3];ix=[vertex(p) for p in uv]
                    if len(set(ix))==3:ff.append(ix)
    if not ff or abs(covered-region.area)>max(1e-9,region.area*.002):
        raise ValueError(f'Patch does not fit its supporting surface: {covered}/{region.area}')
    n=len(pp);pp += [[p[k]-(.0015 if k==axis else 0) for k in range(3)] for p in pp]
    # Only exposed border edges need side faces; internal triangle boundaries weld.
    edges={}
    for f in ff:
        for a,b in zip(f,f[1:]+f[:1]):
            key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b))
    bottom=[[n+k for k in reversed(f)] for f in ff]
    walls=[[a,b,n+b,n+a] for uses in edges.values() if len(uses)==1 for a,b in uses]
    return mesh(pp,ff+bottom+walls,C(color),name='surface-attached-patch')


def almond(cx,cy,rx,ry,n=16):
    pts=[]
    for j in range(n):
        a=j*math.tau/n;x=math.cos(a);y=math.sin(a)*(.75+.25*abs(math.sin(a)))
        pts.append([cx+rx*x,cy+ry*y])
    return pts


def ear_cup(outline,color='skin',inner='skinShade',depth=.025):
    """One connected ear with rim, recessed concha and closed rear shell."""
    n=len(outline);cen=np.mean(outline,axis=0);pp=[]
    for scale,z in [(1,0),(.86,depth),(.61,depth*.42)]:
        for x,y in outline:pp.append([cen[0]+(x-cen[0])*scale,cen[1]+(y-cen[1])*scale,z])
    ci=len(pp);pp.append([*cen,-depth*.04]);back=len(pp)
    pp.extend([[x,y,-depth*.24] for x,y in outline]);ff=[];cols=[]
    for ring in range(2):
        for j in range(n):ff.append([ring*n+j,ring*n+(j+1)%n,(ring+1)*n+(j+1)%n,(ring+1)*n+j]);cols.append(C(color if ring==0 else inner))
    for j in range(n):ff.append([2*n+j,2*n+(j+1)%n,ci]);cols.append(C(inner))
    ff.append(list(range(back,back+n)));cols.append(C(color))
    for j in range(n):ff.append([j,(j+1)%n,back+(j+1)%n,back+j]);cols.append(C(color))
    return mesh(pp,ff,C(color),colors=cols)
