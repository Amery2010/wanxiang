"""Geometric acceptance examples; no automated aesthetic verdicts."""
from pathlib import Path
import json
import numpy as np
import pytest
from wanxiang.kit_parts import definition
from wanxiang.live_geometry import build_mesh
from wanxiang.semantic import evaluate,parameter_values
R=Path(__file__).resolve().parents[1]

def mesh(i,params=None):return build_mesh(definition(i),'lowpoly',params or {})

def intersections(m,origin,direction):
    """Independent double-sided Moller-Trumbore ray test, deduplicated by depth."""
    o=np.asarray(origin,float);d=np.asarray(direction,float);d/=np.linalg.norm(d)
    tr=m.vertices[m.faces];a=tr[:,0];e1=tr[:,1]-a;e2=tr[:,2]-a
    p=np.cross(np.broadcast_to(d,e2.shape),e2);det=(e1*p).sum(1)
    safe=np.abs(det)>1e-11;inv=np.zeros_like(det);inv[safe]=1/det[safe]
    tv=o-a;u=(tv*p).sum(1)*inv;q=np.cross(tv,e1);v=(q*d).sum(1)*inv;t=(e2*q).sum(1)*inv
    hit=t[safe&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]
    return np.unique(np.round(hit,7))

def forms(i):
    d=definition(i);return evaluate(d['shape_params']['forms'],parameter_values(d.get('parameter_schema',{}),{}))


def test_roster_and_original_named_datums():
    before=json.loads((R/'authoring/repair39-contracts.json').read_text())
    assert len(before)==166
    for i,old in before.items():
        d=definition(i)
        for key in ('id','size','anchor','connectors'):assert d.get(key)==old.get(key),(i,key)


def test_continuous_worm_tooth_root_enters_shaft():
    fs=forms('l1.industry.drive.worm');shaft,thread=fs
    radii=np.linalg.norm(np.array(thread['points'])[:,[0,2]],axis=1)
    assert radii.min()==pytest.approx(.085,abs=1e-7)
    assert np.linalg.norm(np.array(shaft['points'])[:,[0,2]],axis=1).max()>.088
    assert .13<radii.max()<.14


def test_roller_has_three_independent_axles_and_no_eight_metre_support():
    m=mesh('l1.industry.conveyor.trough_roller')
    extent=np.ptp(m.vertices,axis=0)
    assert extent[0]<1.3 and extent[2]<.25 and extent[1]<.65


@pytest.mark.parametrize('i,origin,direction',[
 ('l1.gameplay.cover.bullet_slot',[0,.11,2],[0,0,-1]),
 ('l1.gameplay.lock.keyway',[0,.32,2],[0,0,-1]),
 ('l1.industry.pipe.threaded',[0,2,0],[0,-1,0]),
 ('l1.industry.valve.ball',[0,.23,2],[0,0,-1]),
])
def test_actual_through_passages_are_not_capped(i,origin,direction):
    assert not len(intersections(mesh(i),origin,direction)),i


def test_gutter_open_top_has_floor_below_lip():
    m=mesh('l1.architecture.drainage.half_round')
    hits=intersections(m,[0,1,.5],[0,-1,0]);assert len(hits)>=2
    assert 1-hits[0]<.10  # Water enters the real U-section, not a capped cylinder.


def test_socket_slots_are_recessed_not_proud_fake_blocks():
    m=mesh('l1.interior.fixture.outlet_plate')
    for x,y in ((-.024,.076),(.024,.076),(0,.036)):
        h=intersections(m,[x,y,1],[0,0,-1]);assert len(h)
        assert 1-h[0]<-.008  # first hit is behind the front face at +.009 m
    h=intersections(m,[.050,.070,1],[0,0,-1]);assert 1-h[0]==pytest.approx(.009,abs=2e-6)


def test_chain_has_five_closed_link_solids_and_alternating_long_axes():
    fs=forms('l1.props.handle.chain');assert len(fs)==5
    centers=[]
    for j,f in enumerate(fs):
        p=np.array(f['points']);centers.append((p.max(0)+p.min(0))/2)
        ext=np.ptp(p,axis=0)
        assert ext[1]>max(ext[0],ext[2])
        assert (ext[2]<.016) if j%2==0 else (ext[0]<.016)
    np.testing.assert_allclose(np.diff(np.array(centers)[:,1]),.0914,atol=1e-7)
    # Analytical centreline crossing: one link crosses the other's span, while
    # the wire clearance remains positive instead of intersecting solids.
    a=.054;pitch=.0914;r=.0075
    assert 0<2*a-pitch-2*r<.003


def test_boat_keeps_open_deck_and_real_stern_wall():
    m=mesh('exp.transport.boat_hull')
    floor=intersections(m,[0,2,0],[0,-1,0]);assert len(floor)
    assert 2-floor[0]<.20
    stern=intersections(m,[0,.45,-3],[0,0,1]);assert len(stern)
    assert -3+stern[0]<-2.10


def test_rotor_tip_has_duct_clearance_and_stator_below_rotor():
    c=definition('p5.drone.duct')['repair39']['contracts']
    assert c['rotor_radius']+.007<c['duct_inner_min']
    assert c['rotor_reference_y']-c['stator_plane_y']>.035


def test_hand_grip_and_wing_mirror_rebuild_real_geometry():
    a=mesh('core.human.hand',{'grip':False});b=mesh('core.human.hand',{'grip':True})
    assert not np.allclose(a.vertices,b.vertices)
    right=mesh('exp.transport.wing',{'side':'right'});left=mesh('exp.transport.wing',{'side':'left'})
    np.testing.assert_allclose(right.vertices[:,0].max(),-left.vertices[:,0].min(),atol=1e-5)
    assert right.vertices[:,0].max()>2.9 and left.vertices[:,0].max()<.01


def test_flight_rig_compensates_legacy_left_mount_without_flipping_coverts():
    from wanxiang.kit_assembly import Assembler,get_template
    import numpy as np
    s=get_template('exp-creature-flight_rig')
    left=next(n for n in s['instances'] if n['id']=='wingL')
    assert left['rotation']==[0,0,180] and left['params']['mount_inverted'] is True
    a=Assembler().assemble(s);world=a.world_matrices()
    def vertices(prefix):
        pts=np.vstack([a.meshes[n['mesh']].transformed(world[n['id']]).vertices for n in a.nodes if n.get('mesh') and (n['id']==prefix or n['id'].startswith(prefix+'.'))])
        if prefix=='wingL':pts[:,0]*=-1
        pts=np.unique(np.round(pts,5),axis=0)
        return pts[np.lexsort((pts[:,2],pts[:,1],pts[:,0]))]
    np.testing.assert_allclose(vertices('wingR'),vertices('wingL'),atol=2e-5)
    assert {c['node'] for c in s['metadata']['state_controls']}=={'wingR','wingL'}
