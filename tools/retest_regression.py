"""Re-run named failures without overwriting or inflating full-run evidence."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,default=R/'generated/verification');a=p.parse_args();E=a.evidence
 initial=json.loads((E/'regression-shards/summary.json').read_text());plan=json.loads((E/'regression-shards/collection.json').read_text());allids=sum(plan['shards'],[])
 if not initial['coverage_complete'] or initial['collected']!=len(allids):raise ValueError('Initial collection is incomplete')
 failures=[]
 for case in ET.parse(E/'python-regression.xml').getroot().iter('testcase'):
  if case.find('failure') is not None or case.find('error') is not None:
   ident=case.attrib['classname'].replace('.','/')+'.py::'+case.attrib['name']
   if ident not in allids:raise ValueError('Failed case not in original collection: '+ident)
   failures.append(ident)
 if not failures:print(json.dumps({'version':'3.10.0','retest_count':0,'reason':'Full regression has no failures; nothing rerun.'}));return 0
 if len(failures)!=initial['failures']+initial['errors']:raise ValueError('Failure roster mismatch')
 (E/'retests').mkdir(exist_ok=True);cmd=[sys.executable,'-m','pytest','-q',*failures,'--junitxml='+str(E/'retests/failed-cases.xml')]
 with (E/'retests/failed-cases.log').open('w') as log:r=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,timeout=600)
 doc=ET.parse(E/'retests/failed-cases.xml').getroot();counts={k:sum(int(s.get(k,'0')) for s in doc.iter('testsuite')) for k in ('tests','failures','errors','skipped')}
 if counts['tests']!=len(failures):raise ValueError('Incomplete retest coverage')
 passed=counts['tests']-counts['failures']-counts['errors']-counts['skipped'];resolved=r.returncode==0 and passed==len(failures)
 report={'version':'3.10.0','method':'Complete initial collection plus named failure resolution; never sum overlapping independent full runs.','collected':initial['collected'],'initial':initial,'retest':{'ids':failures,'command':cmd[1:],'exit_code':r.returncode,**counts,'passed':passed,'test_source_sha256':{s.split('::')[0]:hashlib.sha256((R/s.split('::')[0]).read_bytes()).hexdigest() for s in failures}},'unique_cases_finally_passed':initial['passed']+passed,'unresolved_cases':len(failures)-passed,'coverage_complete':True,'all_resolved':resolved}
 (E/'final-regression.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));return int(not resolved)
if __name__=='__main__':sys.exit(main())
