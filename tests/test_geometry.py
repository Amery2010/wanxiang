from pathlib import Path
import numpy as np,pytest
from wanxiang import geometry as g
from wanxiang.ir import AssetIR,Mesh,transform
from wanxiang.glb import export_glb,read_glb
from wanxiang.validation import inspect_asset
from wanxiang.errors import WXError
from wanxiang.operators import execute

@pytest.mark.parametrize('kind,fn',[
 ('box',lambda:g.box()),('beveled_box',lambda:g.box([1,2,3],.1)),
 ('cylinder',lambda:g.cylinder(.4,2,12)),('cone',lambda:g.cylinder(.4,2,12,0)),
 ('sphere',lambda:g.sphere(1,2)),('lathe',lambda:g.lathe([[.5,0],[.8,1],[.2,2]],16)),
 ('sweep',lambda:g.sweep([[0,0,0],[.2,.4,.1],[1,1,.8]],[.2,.15,.05],8)),
 ('loft',lambda:g.loft([[[-1,0,-1],[1,0,-1],[1,0,1],[-1,0,1]],[[-.5,2,-.5],[.5,2,-.5],[.5,2,.5],[-.5,2,.5]]])),
 ('extrude_hole',lambda:g.extrude([[-2,-2],[2,-2],[2,2],[-2,2]],.3,[[[-.6,-.6],[-.6,.6],[.6,.6],[.6,-.6]]])),
 ('heightfield',lambda:g.heightfield(4,8)),
 ('sdf_union',lambda:g.sdf([{'kind':'sphere','center':[0,0,0],'radius':.8},{'kind':'sphere','center':[.6,0,0],'radius':.5}],20)),
 ('sdf_subtract',lambda:g.sdf([{'kind':'box','half_size':[.8,.8,.8]},{'kind':'sphere','center':[.6,.6,.6],'radius':.6,'operation':'subtract'}],20,smooth=0))])
def test_geometry_roundtrip(tmp_path,kind,fn):
    m=fn();a=AssetIR();a.add(kind,m);file=tmp_path/'asset.glb';export_glb(a,{'stone':{'images':{}}},file);r=inspect_asset(file,expected=a)
    assert r['passed'];assert r['triangles']>0;assert r['evidence']['independent_reader']

def test_extrusion_opening_is_not_a_painted_polygon():
    m=g.extrude([[-2,-2],[2,-2],[2,2],[-2,2]],.3,[[[-.6,-.6],[-.6,.6],[.6,.6],[.6,-.6]]])
    v=m.vertices[m.faces];front=np.all(np.abs(v[:,:,2])<1e-6,axis=1)
    centroids=v[front].mean(1)
    assert not np.any((np.abs(centroids[:,0])<.6)&(np.abs(centroids[:,1])<.6))

@pytest.mark.parametrize('kind',['hills','river','road','terrace'])
def test_heightfield_shared_boundaries(kind):
    a=g.heightfield(8,16,[0,0],kind,42).vertices.reshape(17,17,3)
    b=g.heightfield(8,16,[8,0],kind,42).vertices.reshape(17,17,3)
    np.testing.assert_allclose(a[:,-1],b[:,0],atol=1e-6)

@pytest.mark.parametrize('bad',[0,-1,float('nan')])
def test_bad_radius_rejected(bad):
    with pytest.raises((WXError,ValueError)):g.cylinder(bad,1)

def test_malformed_faces_rejected():
    with pytest.raises(WXError):Mesh([[0,0,0],[1,0,0],[0,1,0]],[[0,1,7]])

def test_parent_cycle_rejected():
    a=AssetIR();a.group('a',parent='b');a.group('b',parent='a')
    with pytest.raises(WXError):a.world_matrices()

def test_meshir_hash_roster(tmp_path):
    a=AssetIR();a.add('one',g.box());a.save(tmp_path);AssetIR.load(tmp_path)
    (tmp_path/'arrays.npz').write_bytes(b'corrupt')
    with pytest.raises(WXError):AssetIR.load(tmp_path)

@pytest.mark.parametrize('op,p',[('three.torus',{}),('three.extrude',{'outline':[[-1,0],[1,0],[1,2],[-1,2]],'holes':[[[-.3,.6],[-.3,1.4],[.3,1.4],[.3,.6]]]}),('three.lathe',{}),('three.tube',{})])
def test_actual_three_worker(op,p):
    a=execute(op,p,42,{});assert a.meshes;assert all(np.isfinite(m.vertices).all() for m in a.meshes.values())
