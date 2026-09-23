"""Stable tombstones for explicitly removed v1 assets; never silently redirect."""
from functools import lru_cache
from .util import ROOT,read_json
from .errors import WXError

@lru_cache(maxsize=1)
def entries():
    p=ROOT/'library/retired.json'
    if not p.is_file():return {}
    return {(r['kind'],r['id']):r for r in read_json(p)['entries']}

def refuse(ident,kind):
    row=entries().get((kind,ident))
    if row:
        raise WXError('ASSET_RETIRED',f'{kind} {ident} was explicitly retired in 2.0.0. Re-author using a current component; no unsafe automatic remapping.',details={'id':ident,'kind':kind,'decision':row['decision'],'reason':row['reason'],'suggested_current_ids':row.get('suggested_current_ids',[]),'automatic_redirect':False})
    return None

def lookup(ident=None):
    rows=list(entries().values())
    return [r for r in rows if ident is None or ident.lower() in (r['id']+' '+r['name']).lower()]
