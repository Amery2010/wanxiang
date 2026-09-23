"""Current-release baseline gate; earlier releases are retained as historical data."""
import json,hashlib
from functools import lru_cache
from wanxiang.util import ROOT

@lru_cache(maxsize=None)
def saved(name):return json.loads((ROOT/'authoring'/name).read_text())

def canonical(d):
 d=dict(d);d.pop('version',None)
 return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def assert_only_audited_changes(*, allow_game410=False):
 base=saved('repair39-baseline-hashes.json')['definitions']
 expected={'parts/'+r['id'] for r in saved('repair39-findings.json')}|{'assemblies/exp-creature-flight_rig'}
 allowed=set(base)
 if allow_game410:
  roster=json.loads((ROOT/'library/game-expansion.json').read_text())
  allowed|={'parts/'+ident for ident in roster['parts']}|{'assemblies/'+ident for ident in roster['assemblies']}
 actual={str(p.relative_to(ROOT/'library').with_suffix('')) for k in ('parts','assemblies') for p in (ROOT/'library'/k).glob('*.json')}
 assert actual==allowed,'Definition IDs added or removed outside the approved release scope'
 changed={key for key,sig in base.items() if canonical(json.loads((ROOT/'library'/(key+'.json')).read_text()))!=sig}
 assert changed==expected,(changed-expected,expected-changed)
def assert_reference_current(ident,d):
 base=saved('repair39-baseline-hashes.json')['definitions']
 audited={r['id'] for r in saved('repair39-findings.json')}
 if ident in audited:
  assert d['repair39']['source_revision']=='3.9.0' and d['source']['authoring'].startswith('tools/repair39/')
  old=saved('repair39-contracts.json')[ident]
  for k in ('id','size','anchor','connectors'):assert d.get(k)==old.get(k)
 else:assert canonical(d)==base['parts/'+ident]
