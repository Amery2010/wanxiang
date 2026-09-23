import sys,importlib.util,json,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
resource.setrlimit(resource.RLIMIT_CPU,(25,25))
# Address-space limits are intentionally not mistaken for complete filesystem/network isolation.
from wanxiang.ir import AssetIR
from wanxiang.materials import load_material
from wanxiang.glb import export_glb
from wanxiang.validation import inspect_asset
src,case,out=map(Path,sys.argv[1:]);spec=importlib.util.spec_from_file_location('wx_user_candidate',src);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
j=json.loads(case.read_text());asset=module.build(j['params'],j['seed'])
if not isinstance(asset,AssetIR):raise TypeError('Candidate must return AssetIR')
asset.save(out);mats={n['material']:load_material(n['material']) for n in asset.nodes if n.get('mesh')};export_glb(asset,mats,out/'asset.glb');r=inspect_asset(out/'asset.glb');print(json.dumps({'passed':r['passed'],'triangles':r['triangles']}));sys.exit(0 if r['passed'] else 6)
