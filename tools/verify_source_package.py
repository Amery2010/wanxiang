"""Cold-unpack source verification; never needed for saving a checkpoint."""
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,os,subprocess,sys,tempfile,zipfile

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();archive=args.archive.resolve()
    report={'schema':'wx.cold-source-validation/1.0','archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'checks':[],'passed':False}
    def check(name,condition,detail=None):
        report['checks'].append({'name':name,'passed':bool(condition),'detail':detail})
        if not condition:raise RuntimeError(name)
    try:
        with tempfile.TemporaryDirectory(prefix='wx-cold-source-') as folder,zipfile.ZipFile(archive) as z:
            names=z.namelist();check('ZIP CRC',z.testzip() is None);check('No duplicate ZIP paths',len(names)==len(set(names)))
            check('Safe relative archive paths',all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n for n in names))
            roots={n.split('/')[0] for n in names};check('Single source root',len(roots)==1);prefix=next(iter(roots))+'/'
            manifest=json.loads(z.read(prefix+'WX_MANIFEST.json'));roster=manifest['files'];check('Closed source file roster',set(names)=={prefix+p for p in roster}|{prefix+'WX_MANIFEST.json'})
            for name,info in roster.items():
                b=z.read(prefix+name)
                if len(b)!=info['bytes'] or hashlib.sha256(b).hexdigest()!=info['sha256']:raise RuntimeError('File mismatch '+name)
            check('Every manifest file size and SHA-256',True,{'files':len(roster)})
            check('No baked GLB or font binaries',not any(Path(n).suffix.lower() in {'.glb','.ttf','.otf','.ttc','.woff','.woff2','.eot'} for n in names))
            z.extractall(folder);source=Path(folder)/prefix.rstrip('/');work=Path(folder)/'outputs';work.mkdir()
            def run(label,cmd):
                r=subprocess.run(cmd,cwd=source,env={**os.environ,'PYTHONPATH':str(source/'packages/kit/src'),'WX_RESOURCE_ROOT':str(source),'WX_WORKSPACE_ROOT':str(source)},capture_output=True,text=True,timeout=120)
                check(label,r.returncode==0,{'command':cmd,'returncode':r.returncode,'stdout':r.stdout[-4500:],'stderr':r.stderr[-1500:]})
            run('Cold CLI version',[sys.executable,'wx','--version'])
            for ident,kind,name in [
                ('l1.nature.game_farming.corn_husk','part','new-corn'),
                ('l1.architecture.game_scifi.cryopod_shell','part','new-open-cryopod'),
                ('l2-game410-automation','assembly','new-clamp'),
                ('l2-game410-dungeon','assembly','new-dungeon')]:
                run('Cold new asset build '+ident,[sys.executable,'wx','kit','build','--'+kind,ident,'--out',str(work/name),'--no-cache'])
            run('Cold nested L3 build and GLB export',[sys.executable,'wx','kit','build','--assembly','l3-robot-arm-adaptive','--out',str(work/'robot'),'--no-cache'])
            edited=work/'edited.scene.json';subset=work/'east.scene.json'
            run('Cold editable scene command',['node','tools/scene_ops.js','library/assemblies/l4-interior-living.json','--command','examples/l34/move-sofa.command.json','--out',str(edited)])
            run('Cold edited L4 build',[sys.executable,'wx','kit','build','--spec',str(edited),'--out',str(work/'living'),'--no-cache'])
            run('Cold region source export',['node','tools/scene_ops.js','library/assemblies/l4-harbor-fishing.json','--subset','examples/l34/east-region.selection.json','--out',str(subset)])
            run('Cold region GLB build',[sys.executable,'wx','kit','build','--spec',str(subset),'--out',str(work/'east'),'--no-cache'])
            glbs=list(work.rglob('*.glb'));check('Seven independent GLB outputs',len(glbs)==7,{'files':[p.name for p in glbs]})
            for p in glbs:
                code="from pathlib import Path;from wanxiang.validation import inspect_asset;import json;d=inspect_asset(Path("+repr(str(p))+"),independent=True);print(json.dumps(d));assert d['passed']"
                run('Cold independent readback '+p.parent.name,[sys.executable,'-c',code])
            report.update(passed=True,source_files=len(roster),archive_entries=len(names),temporary_builds_removed=True)
    except Exception as e:report['error']=str(e)
    finally:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
