"""Structural acceptance for game-kit additions and alpha-safe WebP output."""
import sys,json,io,hashlib
from pathlib import Path
import numpy as np,pytest
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from wanxiang.kit_parts import definition
from wanxiang.live_geometry import build_mesh
from game410_thumbnails import resized,encode

def rays(m,origin,direction):
    o=np.asarray(origin,float);d=np.asarray(direction,float);d/=np.linalg.norm(d)
    tr=m.vertices[m.faces];a=tr[:,0];e1=tr[:,1]-a;e2=tr[:,2]-a;p=np.cross(np.broadcast_to(d,e2.shape),e2);det=(e1*p).sum(1);safe=np.abs(det)>1e-11;inv=np.zeros_like(det);inv[safe]=1/det[safe]
    tv=o-a;u=(tv*p).sum(1)*inv;q=np.cross(tv,e1);v=(q*d).sum(1)*inv;t=(e2*q).sum(1)*inv
    return np.unique(np.round(t[safe&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)],7))

@pytest.mark.parametrize('ident,o,d',[
 ('l1.architecture.game_dungeon.pointed_portal',[0,1,2],[0,0,-1]),
 ('l1.architecture.game_dungeon.cross_arrow_slit',[0,.5,2],[0,0,-1]),
 ('l1.architecture.game_dungeon.cross_arrow_slit',[.12,.71,2],[0,0,-1]),
 ('l1.architecture.game_dungeon.floor_grate_tile',[.10,2,.08],[0,-1,0]),
 ('l1.architecture.game_dungeon.drawbridge_hinge_seat',[2,.28,0],[-1,0,0]),
 ('l1.gameplay.game_traversal.jug_hold',[0,.25,2],[0,0,-1]),
 ('l1.architecture.game_scifi.bulkhead_frame',[0,1.1,2],[0,0,-1]),
 ('l1.architecture.game_scifi.service_hatch',[0,.77,2],[0,0,-1]),
 ('l1.architecture.game_scifi.docking_seal',[0,2,0],[0,-1,0]),
 ('l1.architecture.game_scifi.thruster_bell',[0,2,0],[0,-1,0]),
 ('l1.robot.game_automation.track_sprocket',[0,0,2],[0,0,-1]),
 ('l1.robot.game_automation.scissor_link',[0,.5,2],[0,0,-1]),
 ('l1.robot.game_automation.gimbal_ring',[0,0,2],[0,0,-1]),
 ('l1.robot.game_automation.quick_coupler',[0,2,0],[0,-1,0]),
 ('l1.character.game_equipment.boot_cuff',[0,2,0],[0,-1,0]),
 ('l1.gameplay.game_puzzle.tri_receiver',[0,.20,2],[0,0,-1]),
 ('l1.gameplay.game_puzzle.rune_rotor',[0,0,2],[0,0,-1]),
 ('l1.terrain.game_waterland.tidepool_rim',[0,2,0],[0,-1,0]),
])
def test_true_openings(ident,o,d):
    for style in ('lowpoly','toon'):
        assert len(rays(build_mesh(definition(ident),style,{}),o,d))==0,(ident,style)

def test_cryopod_open_top_but_has_floor():
    m=build_mesh(definition('l1.architecture.game_scifi.cryopod_shell'),'lowpoly',{})
    h=rays(m,[0,2,0],[0,-1,0]);assert len(h)>=2
    # Hits the bottom, not a closed roof at the rim (~.64 m).
    assert .16<2-h[0]<.24

def test_open_basket_has_real_bottom():
    h=rays(build_mesh(definition('l1.props.game_survival.basket_body'),'lowpoly',{}),[.10,.40,0],[0,-1,0])
    assert len(h)>=2 and .02<.40-h[0]<.10

def test_tri_key_vertices_fit_receiver_clearance():
    from shapely.geometry import Polygon,Point
    # Check actual public definition vertices, accounting for the sample's y datums.
    d=definition('l1.gameplay.game_puzzle.tri_key');m=build_mesh(d,'lowpoly',{})
    hole=Polygon([[0,.605],[-.19,.25],[.19,.25]])
    for p in m.vertices:assert hole.buffer(1e-6).covers(Point(p[0],p[1]+.20))

def test_alpha_lossless_and_no_metadata():
    policy=json.loads((R/'authoring/thumbnail-policy.json').read_text());assert policy['styles']==['lowpoly']
    edge=policy['profiles']['grid']['edge'];quality=policy['profiles']['grid']['quality']
    im=Image.new('RGBA',(320,320),(255,255,255,0));ar=np.asarray(im).copy();ar[24:285,30:291,:3]=[84,135,76];ar[24:285,30:291,3]=np.arange(261,dtype=np.uint16)[:,None]%256;im=Image.fromarray(ar)
    target=resized(im,edge);raw=encode(target,{'quality':quality,'method':5,'alpha_quality':100})
    with Image.open(io.BytesIO(raw)) as actual:
        assert actual.format=='WEBP' and actual.size==(edge,edge) and actual.mode=='RGBA'
        assert actual.getchannel('A').tobytes()==target.getchannel('A').tobytes()
        assert not actual.info.get('icc_profile') and not actual.info.get('exif') and not actual.info.get('xmp')
        assert actual.getchannel('A').getbbox() is not None

def test_existing_ids_and_definitions_preserved():
    baseline=json.loads((R/'authoring/game410-baseline.json').read_text())
    for p,h in baseline['definitions'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p

def test_generated_authoring_provenance_is_persisted():
    roster=json.loads((R/'library/game-expansion.json').read_text())
    assert len(roster['parts'])==120 and len(roster['assemblies'])==10
    for i in roster['parts']:
        d=definition(i);assert (R/d['source']['authoring']).is_file();assert not d['game_expansion']['rig_implemented'];assert not d['game_expansion']['physics_implemented']
