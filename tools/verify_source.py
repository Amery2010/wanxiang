"""Verify every shipped source byte and reject unlisted author-source files."""
from pathlib import Path
import hashlib,json,sys
from package_release import core_files
R=Path(__file__).resolve().parents[1]
def main():
    p=R/'WX_MANIFEST.json'
    if not p.is_file():raise SystemExit('WX_MANIFEST.json is missing')
    doc=json.loads(p.read_text());fail=[]
    for name,rec in doc['files'].items():
        source=(R/name).resolve()
        if not source.is_relative_to(R.resolve()) or not source.is_file():fail.append(name+': missing or unsafe');continue
        b=source.read_bytes()
        if len(b)!=rec['bytes'] or hashlib.sha256(b).hexdigest()!=rec['sha256']:fail.append(name+': mismatch')
    try:actual={str(p.relative_to(R)) for p in core_files(R)}
    except ValueError as e:fail.append(str(e));actual=set()
    fail+=['unlisted source: '+x for x in sorted(actual-set(doc['files']))]
    result={'passed':not fail,'checked':len(doc['files']),'issues':fail,'generated_outputs_excluded':['.wx-cache','workspaces','generated','exports'],'prebuilt_glb_count':sum(n.endswith('.glb') for n in doc['files'])}
    print(json.dumps(result,ensure_ascii=False,indent=2));return bool(fail)
if __name__=='__main__':sys.exit(main())
