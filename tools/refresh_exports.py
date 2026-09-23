"""Refresh measurements from transient GLBs. No legacy example files required."""
import sys,subprocess,argparse
from pathlib import Path
from asset_jobs import rows
R=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--force-images',nargs='*',default=[]);p.add_argument('--collection',choices=['all','foundation','worlds','expansion','l1','l2','l3','l4'],default='all');a=p.parse_args()
    subprocess.run([sys.executable,str(R/'tools/build_worlds.py'),'--collection',a.collection,'--no-images'],check=True)
    cmd=[sys.executable,str(R/'tools/game410_thumbnails.py')]
    if a.force_images:
        cmd+=['--ids',','.join(a.force_images)]
    elif a.collection!='all':
        cmd+=['--ids',','.join(r['id'] for r in rows(a.collection))]
    subprocess.run(cmd,check=True)
if __name__=='__main__':main()
