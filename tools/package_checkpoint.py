"""Atomically save a recoverable source snapshot; tests never gate this command."""
from pathlib import Path
import argparse, json, os, sys, hashlib
from package_release import core_files, write_archive
R=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve()
    if out.is_relative_to(R):ap.error('Use an output outside the source root')
    files={str(p.relative_to(R)):p.read_bytes() for p in core_files(R)}
    roster={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for n,b in files.items()}
    manifest={'schema':'wx.source-package/1.0','version':'3.10.0-work-in-progress','mode':'core',
        'closed_roster':True,'generated_glb_count':0,'files':roster}
    raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    files['WX_MANIFEST.json']=raw
    temp=out.with_name(out.stem+'.partial.zip')
    result=write_archive(temp,files,R.name)
    os.replace(temp,out);(R/'WX_MANIFEST.json').write_bytes(raw)
    result.update(path=str(out),atomic_commit=True)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
