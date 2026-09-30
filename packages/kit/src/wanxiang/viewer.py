"""Self-contained HTML catalog. No CDN, fetch of local models, or UI build tooling."""
from __future__ import annotations
from .paths import code_path, WORKSPACE_ROOT
import base64,json
from pathlib import Path
from .util import read_json,atomic_bytes,sha256
from .materials import DEFINITIONS
from .live_viewer import _materials

def b64(path):return base64.b64encode(Path(path).read_bytes()).decode()

def create_viewer(runs,out,title='万象工坊 3D · 资产工作台'):
    items=[]
    for run in runs:
        r=Path(run)
        if not (r/'job.json').is_file() or not (r/'review/inspection.json').is_file():continue
        j=read_json(r/'job.json');glb=r/'release/asset.glb'
        if not glb.exists():continue
        recipe=read_json(r/'source/recipe.json');report=read_json(r/'review/inspection.json')
        def image(name):
            p=r/'review'/name;return 'data:image/png;base64,'+b64(p) if p.exists() else ''
        items.append({'id':j['id'],'name':recipe.get('name',j['id']),'category':recipe.get('category','custom'),'family':recipe.get('family','custom'),'tags':recipe.get('tags',[]),
           'glb':b64(glb),'sha256':sha256(glb),'bytes':glb.stat().st_size,'hero':image('hero.png'),'views':[image(f'view_{i}.png') for i in range(4)],
           'spec':j['spec'],'recipe':recipe,'report':report,'status':j['state'],'cache_hits':j.get('cache_hits',0),'kit':read_json(r/'source/kit-spec.json') if (r/'source/kit-spec.json').exists() else None,'provenance':read_json(r/'release/provenance.json') if (r/'release/provenance.json').exists() else {},'bom':read_json(r/'release/bom.json') if (r/'release/bom.json').exists() else []})
    mats=_materials()
    data={'version':'1.1.0','title':title,'assets':items,'materials':mats,'architecture':'CLI builds; this HTML inspects and exports real existing assets.','offline':True}
    text=(code_path('web/viewer.html')).read_text();data_json=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028')
    text=text.replace('/*__THREE__*/',(code_path('vendor/three-0.186.0-with-addons.global.js')).read_text().replace('</script','<\\/script'))
    text=text.replace('/*__DATA__*/',f'window.WX_DATA={data_json};')
    manifest=read_json(code_path('runtime/source-manifest.json'))
    code='\n'.join(code_path('runtime/'+name).read_text() for name in [*manifest['kernel'],*manifest['browser']])+'\n'+code_path('web/app.js').read_text()
    text=text.replace('/*__APP__*/',code.replace('</script','<\\/script'))
    atomic_bytes(out,text.encode());return {'path':str(out),'assets':len(items),'bytes':Path(out).stat().st_size,'self_contained':True}
