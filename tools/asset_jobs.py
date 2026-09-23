"""Common on-demand materialisation boundary for evidence, exports and tests."""
from pathlib import Path
from contextlib import contextmanager
import json,tempfile,sys
R=Path(__file__).resolve().parents[1]
if str(R/'packages/kit/src') not in sys.path:sys.path.insert(0,str(R/'packages/kit/src'))
from wanxiang.kit_parts import build_part
from wanxiang.kit_assembly import Assembler,get_template,materials_for
from wanxiang.glb import export_glb
from wanxiang.rigid_motion import tracks_for

def rows(collection='all',ids=None):
    records=json.loads((R/'library/registry.json').read_text())['records']
    if ids:
        wanted=set(ids);selected=[r for r in records if r['id'] in wanted]
        if wanted-{r['id'] for r in selected}:raise ValueError('Unknown asset IDs: '+str(sorted(wanted-{r['id'] for r in selected})))
        return selected
    if collection!='all':
        c=json.loads((R/'library'/(collection+'.json')).read_text());wanted=set(c['parts']+c['assemblies']);records=[r for r in records if r['id'] in wanted]
    return records

def build(ident,style,out):
    ispart=(R/'library/parts'/(ident+'.json')).is_file()
    if ispart:asset=build_part(ident,style)
    else:
        spec=get_template(ident);spec['style']=style;asset=Assembler(style).assemble(spec)
    export_glb(asset,materials_for(asset),Path(out),animations=[] if ispart else tracks_for(asset,ident))
    return asset

@contextmanager
def materialized(ident,style='lowpoly'):
    """Transient GLB outside the source tree; always removed on context exit."""
    with tempfile.TemporaryDirectory(prefix='wx-asset-') as folder:
        path=Path(folder)/(ident+'.glb');asset=build(ident,style,path)
        yield path,asset
