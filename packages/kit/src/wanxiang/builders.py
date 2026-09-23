"""Semantic assemblies. Distinct construction methods, not renamed random seeds."""
from __future__ import annotations
import math
import numpy as np
from . import geometry as g
from .ir import AssetIR,Mesh,concat,transform
from .util import rng_for
from .errors import WXError
TAU=math.tau
from contextvars import ContextVar
BUILD_QUALITY=ContextVar("wx_build_quality",default=1.)

def construct(fn,params,seed):
    token=BUILD_QUALITY.set(params.get("quality",1.))
    try:return fn(params,seed)
    finally:BUILD_QUALITY.reset(token)

class Builder:
    def __init__(self):self.asset=AssetIR()
    def add(self,id,mesh,mat='stone',pos=(0,0,0),rot=(0,0,0),scale=(1,1,1),parent=None,role='surface',topology='closed'):
        return self.asset.add(id,mesh,mat,parent=parent,matrix=transform(pos,rot,scale),role=role,topology=topology)
    def box(self,id,size,pos,mat='stone',bevel=.02,**kw):return self.add(id,g.box(size,bevel if BUILD_QUALITY.get()>=.75 else 0),mat,pos,**kw)
    def cyl(self,id,r,h,pos,mat='metal',segments=24,**kw):return self.add(id,g.cylinder(r,h,max(6,int(segments*min(1,BUILD_QUALITY.get())))),mat,pos,**kw)
    def beam(self,id,a,b,w,mat='wood',d=None,**kw):return self.add(id,g.beam(a,b,w,d,min(w*.13,.025)),mat,**kw)

def leaf_mesh(center,direction,length,width,roll=0):
    d=np.asarray(direction,float);d/=max(np.linalg.norm(d),1e-8)
    ref=[0,1,0] if abs(d[1])<.85 else [1,0,0];x=np.cross(d,ref);x/=np.linalg.norm(x);n=np.cross(x,d)
    xx=x*math.cos(roll)+n*math.sin(roll);nn=np.cross(xx,d);c=np.asarray(center,float)
    v=[c-d*length/2,c-xx*width/2,c+nn*width*.12,c+xx*width/2,c+d*length/2]
    f=[[0,1,2],[0,2,3],[1,4,2],[2,4,3]];uv=[[.5,1],[0,.5],[.5,.5],[1,.5],[.5,0]]
    return Mesh(v,f,uv=uv)

def growth(p,seed):
    """Shared deterministic branch scaffold consumed independently by wood and leaf stages."""
    species=p.get('species','pine');h=float(p.get('height',6));density=p.get('density',1);radius=p.get('crown',1.7)
    rng=rng_for(seed,'skeleton.'+species);branches=[];lean=float(p.get('lean',.18))
    main=np.column_stack([np.linspace(0,lean,12)**1.05,np.linspace(0,h,12),np.sin(np.linspace(0,2,12))*.09])
    if species in ('pine','fir'):
        layers=max(4,int(8*density));last=.2
        for j in range(layers):
            t=.25+.68*j/layers+rng.uniform(-.018,.018);y=h*t;count=int(rng.integers(5,8));base_angle=j*2.399
            for k in range(count):
                a=base_angle+k*TAU/count+rng.uniform(-.2,.2);length=radius*(1-t)*1.25*rng.uniform(.8,1.12)
                start=np.array([lean*t,y,.09*np.sin(t*2)]);end=start+np.array([math.cos(a)*length,-length*.12,math.sin(a)*length])
                mid=start+(end-start)*.62+[0,-length*.12,0];end+=np.array([0,length*.08,0])
                pts=g.curve([start,mid,end],7);branches.append({'id':f'b{j:02}_{k:02}','points':pts.tolist(),'radius':h*.009*(1-t*.65),'tip':end.tolist(),'angle':a,'length':length})
    else:
        count=max(8,int(17*density))
        for j in range(count):
            t=.34+.53*(j/(count-1));a=j*2.399+rng.uniform(-.35,.35);length=radius*(.75+.3*np.sin(j*.7))*rng.uniform(.85,1.18)
            start=np.array([lean*t,h*t,.08*np.sin(t*2)]);end=start+[math.cos(a)*length,h*.12,math.sin(a)*length]
            mid=start+(end-start)*.5+[0,.25,0];pts=g.curve([start,mid,end],9)
            branches.append({'id':f'b{j:02}','points':pts.tolist(),'radius':h*.012*(1-t*.55),'tip':end.tolist(),'angle':a,'length':length})
            for q in [-1,1]:
                st=pts[5];az=a+q*.65;tip=end+[math.cos(az)*length*.36,.15+length*.1,math.sin(az)*length*.36]
                pts2=g.curve([st,(st+tip)*.5+[0,.1,0],tip],6)
                branches.append({'id':f'b{j:02}t{q+1}','points':pts2.tolist(),'radius':h*.0048,'tip':tip.tolist(),'angle':az,'length':length*.5})
    return {'species':species,'height':h,'main':main.tolist(),'branches':branches,'seed':seed}

def tree_wood(p,seed,inputs):
    s=inputs['skeleton'];h=s['height'];b=Builder();mat='birch' if s['species']=='birch' else 'bark';quality=p.get('quality',1)
    main=np.array(s['main']);b.add('trunk',g.sweep(main,np.linspace(h*.055,h*.004,len(main)),max(6,int(14*quality))),mat,role='trunk')
    for i in range(7):
        a=i*TAU/7+.3;r=h*.13;points=g.curve([[math.cos(a)*r,.035,math.sin(a)*r],[math.cos(a)*r*.38,.18,math.sin(a)*r*.38],[0,h*.14,0]],8)
        b.add(f'root_{i}',g.sweep(points,np.linspace(h*.003,h*.030,8),6),mat,role='root')
    for branch in s['branches']:
        pts=np.array(branch['points']);b.add(branch['id'],g.sweep(pts,np.linspace(branch['radius'],.006,len(pts)),max(5,int(8*quality))),mat,role='branch')
    b.asset.socket('ground','trunk',[0,0,0],interface='ground_anchor');return b.asset

def tree_foliage(p,seed,inputs):
    s=inputs['skeleton'];b=Builder();species=s['species'];quality=p.get('quality',1);leaves_density=p.get('leaf_density',1)
    for branch in s['branches']:
        rng=rng_for(s['seed'],'foliage.'+branch['id']);meshes=[];end=np.array(branch['tip']);pts=np.array(branch['points']);a=branch['angle']
        if species in ('pine','fir'):
            # Needled sprays follow the actual branch path rather than filling a cone.
            for j in range(2,len(pts)):
                t=j/(len(pts)-1);center=pts[j]
                for q in [-1,1]:
                    az=a+q*.65;direction=np.array([math.cos(az),.18,math.sin(az)])
                    for k in range(max(3,int(12*quality*leaves_density))):
                        v=k/max(1,int(12*quality*leaves_density)-1);pos=center+direction*v*branch['length']*.42
                        spin=q*.45+v*.7;d=direction*.4+np.array([math.cos(az+spin),.4,math.sin(az+spin)])
                        meshes.append(leaf_mesh(pos,d,.43*(1-v*.35),.16,rng.uniform(-.35,.35)))
        else:
            count=max(8,int(43*quality*leaves_density));rad=.39 if species=='birch' else .53
            for k in range(count):
                y=1-2*(k+.5)/count;theta=k*2.39996;rr=math.sqrt(max(0,1-y*y));offset=np.array([rr*math.cos(theta),y*.8,rr*math.sin(theta)])*rad*rng.uniform(.45,1.15)
                pos=end+offset;direction=np.array([math.cos(theta),.4+rng.random(),math.sin(theta)])
                meshes.append(leaf_mesh(pos,direction,.3 if species=='birch' else .4,.19 if species=='birch' else .25,rng.uniform(-1,1)))
            if species=='willow':
                for strand in range(3):
                    off=rng.normal(0,.15,3);base=end+off;tip=base+[.15,-s['height']*.28,.12];line=g.curve([base,(base+tip)/2+[.16,0,0],tip],12)
                    for k,pos in enumerate(line):meshes.append(leaf_mesh(pos,[.15,-1,.1],.32,.075,rng.uniform(-1,1)))
        if meshes:b.add('canopy_'+branch['id'],concat(meshes),'needle' if species in ('pine','fir') else 'leaf',role='foliage',topology='open')
    return b.asset

def shrub(p,seed):
    b=Builder();rng=rng_for(seed,'shrub');h=p.get('height',1.3);radius=p.get('radius',.9);density=p.get('density',1);leaves=[]
    for i in range(12):
        a=i*2.399;r=radius*rng.uniform(.2,.85);tip=np.array([r*math.cos(a),h*rng.uniform(.65,1),r*math.sin(a)])
        points=g.curve([[0,0,0],tip*[.35,.7,.35],tip],7);b.add(f'stem_{i}',g.sweep(points,np.linspace(.035,.009,7),5),'bark')
        for j in range(int(50*density)):
            off=rng.normal(0,1,3);off/=np.linalg.norm(off);off*=rng.uniform(.1,.32);pos=tip+off
            leaves.append(leaf_mesh(pos,off+[0,.4,0],.27,.18,rng.uniform(-1,1)))
    b.add('leaf_cluster',concat(leaves),'leaf',role='foliage',topology='open');return b.asset

def palm(p,seed):
    b=Builder();h=p.get('height',5);rng=rng_for(seed,'palm');pts=g.curve([[0,0,0],[.18,h*.5,0],[.65,h,0]],22)
    b.add('trunk',g.sweep(pts,np.linspace(.23,.13,len(pts)),12),'bark')
    for i in range(16):
        t=i/15;pos=pts[min(len(pts)-1,int(t*(len(pts)-1)))];b.add(f'trunk_ring_{i}',g.lathe([[.17+(1-t)*.07,-.035],[.19+(1-t)*.07,0],[.17+(1-t)*.07,.035]],12),'darkwood',pos)
    crown=pts[-1];leaves=[]
    for i in range(12):
        a=i*2.399;length=rng.uniform(1.6,2.3);d=np.array([math.cos(a),0,math.sin(a)]);end=crown+d*length+[0,-.6,0]
        spine=g.curve([crown,crown+d*.9+[0,.65,0],end],15);b.add(f'frond_stem_{i}',g.sweep(spine,np.linspace(.032,.007,15),5),'grass')
        side=np.array([-d[2],0,d[0]])
        for j in range(2,15):
            t=j/14;w=.65*np.sin(t*math.pi)*(.7 if i>8 else 1)
            for q in [-1,1]:
                direction=(side*q-d*.18+[0,-.2,0]);leaves.append(leaf_mesh(spine[j]+direction*w*.43,direction,w*1.48+.08,.23,.18*q))
    b.add('fronds',concat(leaves),'palm',role='foliage',topology='open');return b.asset

def bamboo(p,seed):
    b=Builder();rng=rng_for(seed,'bamboo');h=p.get('height',4);leaves=[]
    for k in range(int(p.get('stems',5))):
        x,z=rng.uniform(-.7,.7,2);height=h*rng.uniform(.65,1);seg=height/9
        for j in range(9):
            b.cyl(f'culm_{k}_{j}',.065,seg*.94,[x,j*seg,z],'grass',segments=10)
            b.add(f'joint_{k}_{j}',g.lathe([[.065,0],[.079,.012],[.079,.035],[.063,.04]],10),'darkwood',[x,j*seg,z])
            if j>3:
                a=j*2.399+k;end=np.array([x+math.cos(a)*.5,j*seg+.1,z+math.sin(a)*.5]);b.beam(f'twig_{k}_{j}',[x,j*seg,z],end,.017,'grass')
                for t in range(10):leaves.append(leaf_mesh(end+rng.uniform(-.18,.18,3),[math.cos(a+t*.3),.1,math.sin(a+t*.3)],.35,.065))
    b.add('leaves',concat(leaves),'leaf',topology='open');return b.asset

def cactus(p,seed):
    b=Builder();h=p.get('height',2.8);b.cyl('stem',.25,h,[0,0,0],'grass',segments=16);b.add('top',g.sphere(.25,2,scale=[1,1,1]),'grass',[0,h,0])
    for i,sign in enumerate([-1,1]):
        tip=h*(.6 if sign<0 else .84);pts=g.curve([[0,h*.42,0],[sign*.6,h*.42,0],[sign*.72,h*.55,0],[sign*.72,tip,0]],18)
        b.add(f'arm_{i}',g.sweep(pts,.14,10),'grass');b.add(f'arm_cap_{i}',g.sphere(.14,1),'grass',pts[-1])
    for i in range(12):
        a=i*TAU/12
        b.cyl(f'rib_{i}',.022,h*.95,[math.cos(a)*.25,.03,math.sin(a)*.25],'grass',segments=5)
    return b.asset

def rock(p,seed):
    b=Builder();rng=rng_for(seed,'rock');scale=p.get('size',2);kind=p.get('kind','boulder');q=p.get('quality',1)
    if kind=='basalt':
        for i in range(11):
            a=i*2.399;r=.28*math.sqrt(i);h=scale*rng.uniform(.65,1.65);x,z=r*math.cos(a),r*math.sin(a)
            b.cyl(f'column_{i}',.32,h,[x,0,z],'slate',segments=6)
    elif kind=='cliff':
        for i in range(6):
            h=scale*.3;x=(i%3-1)*scale*.5;y=i//3*h*.9
            m=g.box([scale*.63,h,scale*.7],.07);v=m.vertices.copy();v[:,0]+=.09*np.sin(v[:,1]*10+seed);v[:,2]+=.08*np.cos(v[:,0]*7)
            b.add(f'layer_{i}',Mesh(v,m.faces,uv=m.uv),'sandstone',[x,y+h/2,0],rot=[0,.08*(i-2),0])
    else:
        shapes=[]
        for i in range(5):
            c=rng.uniform(-.4,.4,3)*scale;c[1]=rng.uniform(.3,.6)*scale
            shapes.append({'kind':'ellipsoid','center':c.tolist(),'radii':(rng.uniform(.4,.65,3)*scale).tolist()})
        m=g.sdf(shapes,max(20,int(40*q)),[[-scale,-scale*.5,-scale],[scale,scale*1.4,scale]],.19*scale)
        m.vertices[:,1]-=m.vertices[:,1].min();b.add('fused_stone',m,'stone' if kind=='boulder' else 'sandstone',role='sdf_fused')
    return b.asset

def terrain(p,seed):
    b=Builder();size=p.get('size',8);q=p.get('quality',1);kind=p.get('kind','hills');n=max(12,int(48*q));origin=p.get('origin',[0,0])
    m=g.heightfield(size,n,origin,kind,seed,p.get('amplitude',1));b.add('ground',m,'grass' if kind in ('hills','river','road') else 'sand',role='terrain',topology='open')
    # Close each boundary down to the base. The heightfield must not float above a separate slab.
    grid=m.vertices.reshape(n+1,n+1,3);edges=[grid[0],grid[-1][::-1],grid[:,0][::-1],grid[:,-1]]
    bottom=min(-.45,float(m.vertices[:,1].min())-.12)
    for k,edge in enumerate(edges):
        v=[];f=[];uv=[]
        for i,pt in enumerate(edge):v.extend([pt,[pt[0],bottom,pt[2]]]);uv.extend([[i/n*size*.5,pt[1]],[i/n*size*.5,bottom]])
        for i in range(n):f.extend([[2*i,2*i+1,2*i+2],[2*i+1,2*i+3,2*i+2]])
        b.add(f'earth_skirt_{k}',Mesh(v,f,uv=uv),'soil',role='terrain_skirt',topology='open')
    b.box('earth_base',[size,.16,size],[origin[0],bottom-.08,origin[1]],'soil',bevel=0)
    if kind in ('river','road'):
        zs=np.linspace(origin[1]-size/2,origin[1]+size/2,70);xs=(.55*np.sin(zs*.65) if kind=='river' else .4*np.sin(zs*.5))
        y=.04 if kind=='river' else .645;half=.66 if kind=='river' else .68
        # Only include strip portions crossing the current tile. No arbitrary global recentering.
        v=[];f=[];uv=[]
        for x,z in zip(xs,zs):
            left=max(origin[0]-size/2,x-half);right=min(origin[0]+size/2,x+half)
            if left>=right:continue
            v.extend([[left,y,z],[right,y,z]]);uv.extend([[0,z*.5],[1,z*.5]])
        for i in range(len(v)//2-1):f.extend([[2*i,2*i+2,2*i+1],[2*i+1,2*i+2,2*i+3]])
        if f:b.add('river_surface' if kind=='river' else 'road_surface',Mesh(v,f,uv=uv),'water' if kind=='river' else 'sand',role=kind,topology='open')
        if kind=='river':
            for i in range(9):
                z=origin[1]-size*.43+i*size*.106;x=.55*math.sin(z*.65)+(-1 if i%2 else 1)*.96
                if origin[0]-size/2<x<origin[0]+size/2:b.add(f'bank_rock_{i}',g.sphere(.24,1,scale=[1.6,.72,1]),'stone',[x,.24,z])
        else:
            b.asset.socket('road_start','ground',[xs[0],y,zs[0]],axis=[0,0,-1],interface='road');b.asset.socket('road_end','ground',[xs[-1],y,zs[-1]],axis=[0,0,1],interface='road')
    return b.asset

def crate(p,seed):
    b=Builder();s=p.get('size',1.2);n=int(p.get('planks',5));w=s/n
    for i in range(n):
        x=-s/2+w*(i+.5);z=x
        for sign in [-1,1]:
            b.box(f'front_plank_{sign}_{i}',[w*.96,s*.82,.085],[x,s*.5,sign*s*.46],'wood',.009)
            b.box(f'side_plank_{sign}_{i}',[.085,s*.82,w*.96],[sign*s*.46,s*.5,z],'wood',.009)
        b.box(f'lid_{i}',[w*.96,.075,s*.88],[x,s*.96,0],'wood',.01)
    for y in [s*.12,s*.88]:
        for sign in [-1,1]:
            b.box(f'rail_f_{y}_{sign}',[s,.14,.12],[0,y,sign*s*.5],'darkwood',.012)
            b.box(f'rail_s_{y}_{sign}',[.12,.14,s],[sign*s*.5,y,0],'darkwood',.012)
    for sign in [-1,1]:
        b.beam(f'brace_{sign}',[-s*.4,s*.22,sign*s*.535],[s*.4,s*.8,sign*s*.535],.105,'wood',.06)
        for x in [-s*.4,s*.4]:
            for y in [s*.13,s*.88]:b.cyl(f'rivet_{sign}_{x}_{y}',.018,.025,[x,y,sign*s*.57],'metal',segments=8,rot=[math.pi/2,0,0])
    return b.asset

def barrel(p,seed):
    b=Builder();r=p.get('radius',.48);h=p.get('height',1.25);n=int(p.get('staves',16))
    for i in range(n):
        a0=(i+.035)*TAU/n;a1=(i+.965)*TAU/n;profile=[]
        for t in np.linspace(0,1,9):
            rad=r*(.85+.15*math.sin(t*math.pi));profile.append([[rad*math.cos(a0),t*h,rad*math.sin(a0)],[rad*math.cos(a1),t*h,rad*math.sin(a1)]])
        v=np.array(profile).reshape(-1,3);f=[]
        for j in range(8):f.extend([[2*j,2*j+2,2*j+1],[2*j+1,2*j+2,2*j+3]])
        b.add(f'stave_{i}',Mesh(v,f,uv=np.array([[0,t*h] for t in np.linspace(0,1,9) for _ in range(2)])+np.tile([[0,0],[.18,0]],(9,1))),'wood',topology='open')
    for i,t in enumerate([.08,.25,.75,.92]):
        rr=r*(.85+.15*math.sin(t*math.pi))+.018
        b.add(f'hoop_{i}',g.lathe([[rr,t*h-.035],[rr+.01,t*h],[rr,t*h+.035]],32,False),'metal',topology='open')
    b.cyl('lid',r*.84,.05,[0,h-.05,0],'wood',segments=32);b.cyl('base',r*.84,.05,[0,0,0],'wood',segments=32)
    b.cyl('bung',.07,.014,[0,h,.12],'darkwood',segments=12);return b.asset

def lamp(p,seed):
    b=Builder();h=p.get('height',3.2);b.add('base',g.lathe([[.36,0],[.36,.08],[.28,.12],[.18,.22],[.15,.4],[.11,.44]],24),'metal')
    b.cyl('pole',.075,h-.45,[0,.4,0],'navy');b.add('collar',g.lathe([[.14,0],[.14,.07],[.09,.09]],20),'copper',[0,h-.1,0])
    arm=g.curve([[0,h-.2,0],[0,h+.15,0],[.58,h+.25,0],[.7,h,0]],18);b.add('curved_arm',g.sweep(arm,.055,8),'navy')
    b.add('shade',g.lathe([[.12,0],[.3,.18],[.32,.2],[.08,.25]],24),'navy',[.7,h-.34,0]);b.add('lamp',g.sphere(.18,2,scale=[1,.6,1]),'light',[.7,h-.22,0])
    b.asset.socket('light_socket','pole',[.7,h-.62,0],axis=[0,-1,0],interface='light');return b.asset

def house(p,seed):
    b=Builder();w=p.get('width',3.4);d=p.get('depth',2.8);h=p.get('height',2.2);roofrise=p.get('roof_rise',1.1)
    b.box('foundation',[w+.2,.26,d+.2],[0,.13,0],'stone',.035)
    # True door/window cutouts, not opaque painted rectangles.
    outline=[[-w/2,.26],[w/2,.26],[w/2,h],[-w/2,h]]
    holes=[[[-.37,.27],[-.37,1.55],[.37,1.55],[.37,.27]],[[w*.25-.3,.95],[w*.25-.3,1.56],[w*.25+.3,1.56],[w*.25+.3,.95]]]
    b.add('front_wall',g.extrude(outline,.15,holes),'plaster',[0,0,d/2]);b.box('back_wall',[w,h-.26,.15],[0,(h+.26)/2,-d/2],'plaster',.01)
    for sign in [-1,1]:
        side=[[-d/2,.26],[d/2,.26],[d/2,h],[-d/2,h]];hole=[[[-.38,.85],[-.38,1.55],[.38,1.55],[.38,.85]]]
        b.add(f'side_{sign}',g.extrude(side,.15,hole),'plaster',[sign*w/2,0,0],rot=[0,math.pi/2,0])
        for yy in [.38,h-.12]:b.box(f'beam_side_{sign}_{yy}',[.19,.14,d+.15],[sign*w/2,yy,0],'darkwood',.008)
        for zz in [-d/2,d/2]:b.box(f'corner_{sign}_{zz}',[.18,h,.18],[sign*w/2,h/2,zz],'darkwood',.008)
    for zz in [-d/2,d/2]:
        b.add(f'gable_{zz}',g.extrude([[-w/2,h],[w/2,h],[0,h+roofrise]],.13),'plaster',[0,0,zz]);b.beam(f'gable_brace_{zz}',[-w/2,h,zz+.08],[0,h+roofrise,zz+.08],.12,'darkwood');b.beam(f'gable_brace2_{zz}',[w/2,h,zz+.08],[0,h+roofrise,zz+.08],.12,'darkwood')
    for sign in [-1,1]:
        slope=math.atan2(roofrise,w/2);length=math.hypot(w/2+.18,roofrise)
        b.box(f'roof_{sign}',[length,.14,d+.5],[sign*w/4,h+roofrise/2+.04,0],'roof',.01,rot=[0,0,-sign*slope])
        for k in range(8):
            z=-d/2-.18+k*(d+.36)/7;b.beam(f'roof_rib_{sign}_{k}',[0,h+roofrise+.16,z],[sign*(w/2+.2),h+.06,z],.065,'roof',.08)
    b.box('ridge',[.16,.16,d+.48],[0,h+roofrise+.17,0],'darkwood',.025)
    b.box('door_leaf',[.64,1.26,.075],[0,.91,d/2+.08],'wood',.01)
    b.box('door_lintel',[.9,.13,.19],[0,1.6,d/2+.07],'darkwood',.015)
    for sign in [-1,1]:b.box(f'door_jamb_{sign}',[.11,1.38,.19],[sign*.43,.9,d/2+.07],'darkwood',.01)
    x=w*.25
    for yy in [.92,1.58]:b.box(f'window_lintel_{yy}',[.78,.085,.22],[x,yy,d/2+.09],'wood',.006)
    for xx in [x-.34,x,x+.34]:b.box(f'window_mullion_{xx}',[.045,.64,.22],[xx,1.25,d/2+.09],'darkwood',.005)
    b.box('chimney',[.48,1.2,.5],[-w*.24,h+roofrise*.8,-d*.22],'brick',.025)
    b.box('chimney_cap',[.58,.12,.6],[-w*.24,h+roofrise*.8+.65,-d*.22],'stone',.025)
    b.asset.socket('door_hinge','door_leaf',[-.32,-.63,0],interface='hinge',limits=[0,110]);return b.asset

def arch(p,seed):
    b=Builder();r=p.get('radius',1.25);height=p.get('height',1.65);depth=p.get('depth',.65);thick=.32
    for sign in [-1,1]:
        for j in range(5):b.box(f'pier_{sign}_{j}',[thick*.98,height/5*.965,depth],[sign*(r+thick/2),(j+.5)*height/5,0],'sandstone',.022)
        b.box(f'foot_{sign}',[thick+.2,.15,depth+.2],[sign*(r+thick/2),.075,0],'stone',.02)
    n=13
    for i in range(n):
        a=i*math.pi/n+.008;c=(i+1)*math.pi/n-.008
        outline=[[r*math.cos(a),height+r*math.sin(a)],[(r+thick)*math.cos(a),height+(r+thick)*math.sin(a)],[(r+thick)*math.cos(c),height+(r+thick)*math.sin(c)],[r*math.cos(c),height+r*math.sin(c)]]
        b.add(f'voussoir_{i}',g.extrude(outline,depth),'sandstone')
    b.asset.socket('passage','pier_-1_0',[r+thick/2,0,0],axis=[0,0,1],interface='passage');return b.asset

def bridge(p,seed):
    b=Builder();length=p.get('length',5);width=p.get('width',2);rise=p.get('rise',.55);n=18
    path=np.array([[-length/2+i*length/n,.55+rise*math.sin(math.pi*i/n),0] for i in range(n+1)])
    for i,pt in enumerate(path):
        b.box(f'plank_{i}',[length/n*.94,.12,width],pt,'wood',.012)
        if i%3==0:
            for sign in [-1,1]:b.box(f'post_{i}_{sign}',[.11,.82,.11],pt+[0,.39,sign*(width/2-.09)],'darkwood',.009)
    for sign in [-1,1]:
        for level in [.32,.78]:b.add(f'rail_{sign}_{level}',g.sweep(path+[0,level,sign*(width/2-.09)],.035,6),'wood')
        b.add(f'support_{sign}',g.sweep(path+[0,-.14,sign*width*.32],.10,8),'darkwood')
        b.box(f'footing_{sign}',[.55,.58,width+.3],[sign*length/2,.29,0],'stone',.025)
    b.asset.socket('start','footing_-1',[0,.26,0],axis=[-1,0,0],interface='road');b.asset.socket('end','footing_1',[0,.26,0],axis=[1,0,0],interface='road');return b.asset

def wall(p,seed):
    b=Builder();length=p.get('length',4);h=p.get('height',2);n=int(length/.55)
    for j in range(max(2,int(h/.34))):
        for i in range(n):
            x=-length/2+(i+.5)*length/n+(j%2)*.15
            b.box(f'block_{j}_{i}',[length/n*.965,.32,.55],[x,j*.34+.16,0],'stone',.016)
    for i in range(0,n,2):b.box(f'merlon_{i}',[.48,.35,.62],[-length/2+(i+.5)*length/n,h+.14,0],'stone',.018)
    return b.asset

def tower(p,seed):
    b=Builder();h=p.get('height',4.8);r=p.get('radius',1.2);n=12;levels=max(4,int(h/.38))
    for j in range(levels):
        for k in range(n):
            a=(k+.5*(j%2))*TAU/n;pos=[math.cos(a)*r,(j+.5)*h/levels,math.sin(a)*r]
            b.box(f'masonry_{j}_{k}',[r*.50,h/levels*.965,.32],pos,'stone',.012,rot=[0,-a+math.pi/2,0])
    for k in range(8):
        a=k*TAU/8;b.box(f'crown_{k}',[.52,.48,.43],[math.cos(a)*r,h+.2,math.sin(a)*r],'sandstone',.025,rot=[0,-a+math.pi/2,0])
    b.cyl('platform',r+.22,.18,[0,h-.08,0],'stone',segments=32);return b.asset

def fence(p,seed):
    b=Builder();length=p.get('length',4);count=int(p.get('posts',5))
    for i in range(count):
        x=-length/2+i*length/(count-1);b.box(f'post_{i}',[.14,1.25,.14],[x,.625,0],'darkwood',.018)
        b.add(f'cap_{i}',g.cylinder(.12,.15,4,0),'wood',[x,1.25,0],rot=[0,math.pi/4,0])
    for y in [.4,.91]:b.box(f'rail_{y}',[length+.1,.115,.07],[0,y,.04],'wood',.01)
    for i in range(count-1):
        a=-length/2+i*length/(count-1);c=a+length/(count-1);b.beam(f'brace_{i}',[a,.36,.085],[c,.98,.085],.07,'wood',.055)
    return b.asset

def wheel(radius=.43,width=.24,quality=1):
    b=Builder();b.add('tire',g.lathe([[radius*.76,-width/2],[radius*.93,-width*.42],[radius,-width*.24],[radius,width*.24],[radius*.93,width*.42],[radius*.76,width/2]],max(12,int(32*quality))), 'rubber',rot=[0,0,math.pi/2])
    b.cyl('hub',radius*.58,width*1.05,[width*.525,0,0],'metal',segments=20,rot=[0,0,math.pi/2])
    for i in range(8):
        a=i*TAU/8;b.cyl(f'bolt_{i}',radius*.052,.025,[-width*.57,math.sin(a)*radius*.38,math.cos(a)*radius*.38],'copper',segments=6,rot=[0,0,-math.pi/2])
    for i in range(max(12,int(24*quality))):
        a=i*TAU/max(12,int(24*quality));b.box(f'tread_{i}',[width*.76,.045,radius*.15],[0,math.cos(a)*(radius+.008),math.sin(a)*(radius+.008)],'rubber',.006,rot=[a,0,0])
    return b.asset

def chassis(p,seed):
    b=Builder();length=p.get('length',3.2);width=p.get('width',1.7);q=p.get('quality',1);tracked=p.get('tracked',False)
    b.box('hull',[width,.44,length],[0,.88,0],'paint',.11);b.box('deck',[width*.87,.18,length*.8],[0,1.18,-.08],'paint',.055)
    for side in [-1,1]:
        if tracked:
            r=.30;zlimit=length*.35;xc=side*(width*.59)
            for i in range(6):
                z=-zlimit+2*zlimit*i/5;b.asset.group(f'wheel_pivot_{side}_{i}',translation=[xc,.45,z],role='rolling_axis')
                wr=wheel(r,.22,q);prefix=f'wheel_{side}_{i}_'
                for n in wr.nodes:
                    if n.get('parent') is None:n['parent']=f'@external@'
                # Attach the hierarchy after prefixing without moving geometry twice.
                for n in wr.nodes:
                    n['id']=prefix+n['id'];n['mesh']=prefix+n['mesh'] if 'mesh'in n else None;n['parent']=f'wheel_pivot_{side}_{i}'
                b.asset.nodes.extend(wr.nodes);b.asset.meshes.update({prefix+k:v for k,v in wr.meshes.items()})
                b.asset.socket(f'axle_{side}_{i}',f'wheel_pivot_{side}_{i}',axis=[1,0,0],interface='axle')
            # Actual capsule loop around end wheels, with independent links.
            pieces=[]
            straight=max(8,int(length*9*q));arc=max(8,int(13*q));path=[]
            for z in np.linspace(-zlimit,zlimit,straight,endpoint=False):path.append((z,.45+r+.065,0))
            for a in np.linspace(math.pi/2,-math.pi/2,arc,endpoint=False):path.append((zlimit+(r+.065)*math.cos(a),.45+(r+.065)*math.sin(a),math.pi/2-a))
            for z in np.linspace(zlimit,-zlimit,straight,endpoint=False):path.append((z,.45-r-.065,math.pi))
            for a in np.linspace(-math.pi/2,-3*math.pi/2,arc,endpoint=False):path.append((-zlimit+(r+.065)*math.cos(a),.45+(r+.065)*math.sin(a),math.pi/2-a))
            for i,(z,y,a) in enumerate(path):b.box(f'track_{side}_{i}',[.35,.09,.16],[xc,y,z],'metal',.01,rot=[a,0,0],role='track_link')
            b.box(f'fender_{side}',[.44,.10,length*1.05],[xc,.96,0],'paint',.025)
        else:
            for i,z in enumerate([-length*.31,length*.31]):
                id=f'wheel_pivot_{side}_{i}';b.asset.group(id,translation=[side*(width*.57),.47,z],role='rolling_axis')
                wr=wheel(.43,.28,q);prefix=f'wheel_{side}_{i}_'
                for n in wr.nodes:n['id']=prefix+n['id'];n['mesh']=prefix+n['mesh'] if 'mesh'in n else None;n['parent']=id
                b.asset.nodes.extend(wr.nodes);b.asset.meshes.update({prefix+k:v for k,v in wr.meshes.items()});b.asset.socket(f'axle_{side}_{i}',id,axis=[1,0,0],interface='axle')
                b.box(f'arch_{side}_{i}',[.4,.12,.94],[side*width*.6,.96,z],'navy',.04)
            b.beam(f'frame_rail_{side}',[side*width*.33,.54,-length*.48],[side*width*.33,.54,length*.48],.11,'metal')
    b.box('front_bumper',[width*1.02,.15,.15],[0,.67,length*.52],'metal',.022)
    for x in [-width*.34,width*.34]:b.box(f'headlight_{x}',[.24,.12,.045],[x,.98,length*.502],'light',.02)
    for i in range(7):b.box(f'engine_louver_{i}',[width*.45,.035,.055],[0,1.29,-length*.28+i*.08],'rubber',.005)
    b.asset.socket('turret_mount','deck',[0,.10,0],interface='turret_ring');return b.asset

def turret(p,seed):
    b=Builder();r=p.get('radius',.86);l=p.get('barrel_length',2.1);b.cyl('bearing',r*.7,.12,[0,0,0],'metal');b.asset.group('yaw',translation=[0,.12,0],role='yaw_pivot')
    b.box('armored_shell',[r*1.9,.48,r*1.7],[0,.28,0],'paint',.14,parent='yaw')
    b.box('mantlet',[r*.66,.38,.31],[0,.28,r*.89],'metal',.09,parent='yaw')
    # Bore uses a revolved annular profile, not a capped cylinder.
    profile=[[.13,0],[.13,l*.25],[.10,l*.27],[.10,l-.2],[.16,l-.18],[.16,l],[.072,l],[.072,l-.25]]
    b.add('barrel',g.lathe(profile,24,False),'metal',[0,.3,r*.84],rot=[math.pi/2,0,0],parent='yaw',role='barrel',topology='open')
    b.cyl('hatch',r*.32,.07,[r*.28,.56,-r*.18],'metal',parent='yaw')
    b.cyl('antenna_base',.05,.14,[-r*.7,.48,-r*.4],'metal',parent='yaw');b.cyl('antenna',.011,.85,[-r*.7,.60,-r*.4],'metal',segments=6,parent='yaw')
    for sign in [-1,1]:
        for i in range(3):b.box(f'cheek_panel_{sign}_{i}',[.06,.22,.3],[sign*r*.97,.3,-r*.5+i*.36],'navy',.014,parent='yaw')
    b.asset.socket('mount','bearing',axis=[0,1,0],interface='turret_ring');b.asset.socket('yaw','yaw',axis=[0,1,0],interface='yaw',limits=[-180,180]);b.asset.socket('muzzle','barrel',[0,l,0],axis=[0,1,0],interface='muzzle');return b.asset

def industrial(p,seed):
    b=Builder();kind=p.get('kind','tank');h=p.get('height',3.2);r=p.get('radius',.85)
    if kind in ('tank','silo'):
        for x in [-r*.6,r*.6]:
            for z in [-r*.6,r*.6]:b.box(f'leg_{x}_{z}',[.12,.62,.12],[x,.31,z],'metal',.014)
        if kind=='silo':profile=[[r*.18,.5],[r,.95],[r,h],[r*.9,h+.14],[0,h+.5]]
        else:profile=[[r*.72,.5],[r,.7],[r,h-.3],[r*.9,h-.12],[r*.5,h],[0,h]]
        b.add('vessel',g.lathe(profile,40),'navy' if kind=='tank' else 'metal')
        for j in range(3):
            y=.9+(h-1.2)*j/2;b.add(f'stiffener_{j}',g.lathe([[r+.012,y-.035],[r+.04,y],[r+.012,y+.035]],40,False),'metal',topology='open')
        b.cyl('hatch',.23,.1,[0,h,0],'metal')
        for side in [-1,1]:b.cyl(f'ladder_rail_{side}',.023,h-.3,[side*.21,.4,r+.16],'metal',segments=8)
        for j in range(int(h/.25)):b.beam(f'rung_{j}',[-.21,.5+j*.25,r+.16],[.21,.5+j*.25,r+.16],.027,'metal')
        pipe=g.curve([[r,.85,0],[r+.5,.85,0],[r+.65,.55,0],[r+.65,.15,0]],14);b.add('outlet',g.sweep(pipe,.1,12),'metal')
        b.cyl('valve_disc',.19,.04,[r+.6,.76,.04],'copper',segments=16,rot=[math.pi/2,0,0]);b.asset.socket('pipe_out','outlet',[r+.65,.15,0],axis=[0,-1,0],interface='pipe')
    elif kind=='pipe':
        pts=g.curve([[-1.6,.4,0],[-.5,.4,0],[0,.8,0],[0,1.8,0],[.5,2.2,0],[1.5,2.2,0]],32);b.add('elbow_pipeline',g.sweep(pts,.21,18),'metal')
        for i,pos in enumerate([pts[0],pts[-1]]):
            b.cyl(f'flange_{i}',.34,.12,pos,'metal',segments=24,rot=[0,0,math.pi/2]);b.asset.socket(f'end_{i}',f'flange_{i}',interface='pipe',axis=[1,0,0])
            for k in range(8):
                a=k*TAU/8;b.cyl(f'bolt_{i}_{k}',.033,.17,pos+[0,math.cos(a)*.28,math.sin(a)*.28],'copper',segments=6,rot=[0,0,math.pi/2])
        b.cyl('valve_stem',.04,.35,[0,1.28,.22],'metal',rot=[math.pi/2,0,0]);b.add('handwheel',g.lathe([[.23,0],[.25,.025],[.23,.05]],24,False),'copper',[0,1.28,.65],rot=[math.pi/2,0,0],topology='open')
    elif kind=='crane':
        for x in [-.4,.4]:
            for z in [-.4,.4]:b.box(f'tower_leg_{x}_{z}',[.10,h,.10],[x,h/2,z],'metal',.015)
        for j in range(int(h/.6)):
            y=j*.6
            for sign in [-1,1]:b.beam(f'diagonal_{j}_{sign}',[-.4,y,sign*.4],[.4,y+.6,sign*.4],.055,'navy')
        b.asset.group('jib_yaw',translation=[0,h,0],role='yaw_pivot')
        for y in [0,.35]:b.box(f'jib_rail_{y}',[4,.07,.12],[.9,y,0],'metal',.012,parent='jib_yaw')
        for i in range(10):b.beam(f'jib_lattice_{i}',[-1+i*.4,0,0],[-.6+i*.4,.35,0],.045,'navy',parent='jib_yaw')
        b.box('counterweight',[.8,.55,.62],[-.7,-.12,0],'concrete',.04,parent='jib_yaw')
        b.cyl('cable',.012,h*.65,[2.65,-h*.65,0],'metal',segments=5,parent='jib_yaw')
        b.add('hook',g.sweep(g.curve([[2.65,-h*.65,0],[2.65,-h*.75,0],[2.87,-h*.77,0],[2.92,-h*.68,0]],16),.037,7),'metal',parent='jib_yaw');b.asset.socket('yaw','jib_yaw',interface='yaw',limits=[-180,180])
    return b.asset

def fountain(p,seed):
    b=Builder();r=p.get('radius',1.4);b.add('basin',g.lathe([[r,0],[r,.2],[r*.92,.34],[r*.83,.34],[r*.83,.15],[0,.15]],48),'stone')
    b.cyl('water',r*.81,.025,[0,.19,0],'water',segments=48)
    b.add('pedestal',g.lathe([[.35,.15],[.35,.25],[.22,.4],[.17,1.2],[.28,1.4]],32),'sandstone')
    b.add('upper_bowl',g.lathe([[.2,1.25],[.63,1.45],[.63,1.55],[.55,1.52],[.22,1.35]],32,False),'stone',topology='open');return b.asset

def windmill(p,seed):
    b=Builder();h=p.get('height',4);b.add('tower',g.lathe([[1.2,0],[.8,h]],32),'plaster');b.add('cap',g.cylinder(1.0,.85,24,0),'roof',[0,h,0])
    b.asset.group('rotor',translation=[0,h*.83,1.0],role='rotor');b.cyl('hub',.21,.22,[0,0,0],'metal',rot=[math.pi/2,0,0],parent='rotor')
    for i in range(4):
        a=i*TAU/4+.45
        b.beam(f'spar_{i}',[0,0,0],[math.cos(a)*2,math.sin(a)*2,0],.09,'darkwood',parent='rotor')
        for j in range(8):
            t=.55+j*.18;pt=np.array([math.cos(a)*t,math.sin(a)*t,0]);side=np.array([-math.sin(a),math.cos(a),0]);b.beam(f'sail_{i}_{j}',pt,pt+side*.47,.09,'wood',.04,parent='rotor')
    b.asset.socket('rotor_axis','rotor',axis=[0,0,1],interface='axle');return b.asset

ASSEMBLERS={'shrub':shrub,'palm':palm,'bamboo':bamboo,'cactus':cactus,'rock':rock,'terrain':terrain,'crate':crate,'barrel':barrel,'lamp':lamp,'house':house,'arch':arch,'bridge':bridge,'wall':wall,'tower':tower,'fence':fence,'chassis':chassis,'turret':turret,'industrial':industrial,'fountain':fountain,'windmill':windmill}
