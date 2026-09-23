"""Run every collected pytest item exactly once, in independent read-only shards.

All file outputs made by the tests use pytest temporary directories. No xdist
plugin or additional dependency is required; pytest argument files require >=8.2.
Results are merged only after exact collection coverage has been checked.
"""
from pathlib import Path
import argparse, concurrent.futures, json, os, subprocess, sys, time
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workers', type=int, default=4)
    args=ap.parse_args(); workers=max(1,min(args.workers,4))
    out=R/'generated/verification/regression-shards'; out.mkdir(parents=True,exist_ok=True)
    work=R/'workspaces/regression-shards'; work.mkdir(parents=True,exist_ok=True)
    collected=subprocess.run([sys.executable,'-m','pytest','--collect-only','-q'],cwd=R,capture_output=True,text=True,check=True)
    ids=[line for line in collected.stdout.splitlines() if line.startswith(('tests/','packages/kit/tests/')) and '::' in line]
    if not ids or len(ids)!=len(set(ids)):raise RuntimeError('Empty or duplicate pytest collection')
    chunks=[ids[i::workers] for i in range(workers)]
    assert set(sum(chunks,[]))==set(ids) and sum(map(len,chunks))==len(ids)
    plan={'version':'3.10.0','test_items':len(ids),'workers':workers,'coverage':'all collected item IDs exactly once','shards':chunks}
    (out/'collection.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    def run(i):
        argfile=work/f'shard-{i}.txt';argfile.write_text('\n'.join(chunks[i])+'\n')
        start=time.monotonic()
        cmd=[sys.executable,'-m','pytest','-q','@'+str(argfile),'--junitxml='+str(out/f'shard-{i}.xml')]
        with (out/f'shard-{i}.log').open('w') as log:
            result=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,timeout=1200,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','WX_CACHE_DIR':str(work/f'cache-{i}')})
        return {'shard':i,'exit_code':result.returncode,'seconds':round(time.monotonic()-start,3),'collected':len(chunks[i])}
    start=time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        reports=list(pool.map(run,range(workers)))
    merged=ET.Element('testsuites'); seen=0; counts={k:0 for k in ('tests','failures','errors','skipped')}
    for i in range(workers):
        doc=ET.parse(out/f'shard-{i}.xml').getroot(); suites=list(doc.iter('testsuite'))
        cases=sum(len(s.findall('testcase')) for s in suites)
        if cases!=len(chunks[i]):raise RuntimeError(f'Shard {i}: incomplete collection coverage {cases}/{len(chunks[i])}')
        seen+=cases
        for suite in suites:
            suite.set('name',f'pytest-shard-{i}')
            for k in counts:counts[k]+=int(suite.get(k,'0'))
            merged.append(suite)
    assert seen==len(ids)==counts['tests']
    summary={'version':'3.10.0','command':'python tools/run_release_regression.py --workers '+str(workers),'collected':len(ids),**counts,'passed':counts['tests']-counts['failures']-counts['errors']-counts['skipped'],'wall_seconds':round(time.monotonic()-start,3),'workers':workers,'shards':reports,'coverage_complete':True,'test_outputs':'independent pytest tmp directories; collection shares only read-only project source'}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    ET.indent(merged);ET.ElementTree(merged).write(R/'generated/verification/python-regression.xml',encoding='utf-8',xml_declaration=True)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    return int(any(r['exit_code'] for r in reports) or counts['failures'] or counts['errors'])

if __name__=='__main__':sys.exit(main())
