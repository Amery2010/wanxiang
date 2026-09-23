from pathlib import Path
import numpy as np
from .glb import read_glb
from .util import file_info,write_json
from .errors import WXError

def inspect_asset(path,expected=None,budgets=None,independent=True):
    asset,mats,doc=read_glb(path);issues=[];tri=0;vertices=0;mesh_stats=[];bounds=asset.bounds();budgets=budgets or {}
    for n in asset.nodes:
        if not n.get('mesh'):continue
        m=asset.meshes[n['mesh']];tri+=len(m.faces);vertices+=len(m.vertices);v=m.vertices;f=m.faces
        areas=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
        bad=int(np.sum(areas<1e-12))
        if bad:issues.append({'severity':'error','code':'DEGENERATE_TRIANGLES','node':n['id'],'count':bad,'suggestion':'Rebuild the producing operator; do not hide degenerate faces.'})
        missing_uv=len(m.uv)!=len(v)
        if missing_uv:issues.append({'severity':'error','code':'UV_MISSING','node':n['id']})
        mesh_stats.append({'node':n['id'],'triangles':len(f),'vertices':len(v),'topology_policy':n.get('topology','unspecified'),'material':n['material']})
    if tri>budgets.get('triangles',float('inf')):raise WXError('BUDGET_EXCEEDED','Actual triangle count exceeds budget',details={'actual':tri,'limit':budgets['triangles']})
    if vertices>budgets.get('vertices',float('inf')):raise WXError('BUDGET_EXCEEDED','Actual vertex count exceeds budget')
    if Path(path).stat().st_size>budgets.get('output_bytes',float('inf')):raise WXError('BUDGET_EXCEEDED','Export exceeds byte budget')
    expected_check=None
    if expected:
        et=sum(len(expected.meshes[n['mesh']].faces) for n in expected.nodes if n.get('mesh'));eb=expected.bounds();node_ids={n['id'] for n in expected.nodes}
        expected_check={'triangles_match':et==tri,'bounds_match':bool(np.allclose(eb,bounds,atol=2e-5)),'nodes_match':node_ids=={n['id'] for n in asset.nodes}}
        if not all(expected_check.values()):raise WXError('OUTPUT_MISMATCH','GLB differs from source MeshIR',details=expected_check)
    independent_result={'status':'not_run'}
    if independent:
        try:
            import trimesh
            scene=trimesh.load_scene(path,process=False);count=sum(len(g.faces) for g in scene.geometry.values() if hasattr(g,'faces'))
            independent_result={'reader':'trimesh','status':'passed','geometry_triangles':count,'bounds_match':bool(np.allclose(scene.bounds,bounds,atol=2e-5))}
            if not independent_result['bounds_match']:issues.append({'severity':'error','code':'INDEPENDENT_BOUNDS_MISMATCH'})
        except Exception as e:independent_result={'reader':'trimesh','status':'failed','error':str(e)};issues.append({'severity':'error','code':'INDEPENDENT_IMPORT_FAILED'})
    for name,mat in mats.items():
        if mat.get('extras',{}).get('placeholder'):issues.append({'severity':'warning','code':'PLACEHOLDER_MATERIAL','material':name})
    issues.append({'severity':'info','code':'ASSEMBLY_NOT_BOOLEAN','message':'Separate components may intersect. No global manifold union is claimed.'})
    report={'schema':'wx.inspection/1.0','asset':file_info(path),'passed':not any(i['severity']=='error' for i in issues),'triangles':tri,'vertices':vertices,'nodes':len(asset.nodes),'meshes':len(asset.meshes),'unique_gltf_meshes':len(doc.get('meshes',[])),'mesh_instances':sum(bool(n.get('mesh')) for n in asset.nodes),'materials':len(mats),'textures':len(doc.get('images',[])),
      'bounds':bounds.tolist(),'dimensions':np.ptp(bounds,axis=0).tolist(),'sockets':asset.sockets,'expected_comparison':expected_check,'independent_reader':independent_result,'issues':issues,'mesh_stats':mesh_stats,
      'evidence':{'build':True,'strict_glb_reader':True,'khronos_validator':False,'independent_reader':independent_result['status']=='passed','cpu_preview':False,'webgl_runtime':False,'artistic_approval':False,'target_project_approval':False},
      'limitations':['Built-in structural validation is not the complete Khronos Validator.','No global self-intersection or manifold guarantee.','CPU diagnostic shading does not certify PBR appearance.']}
    return report
