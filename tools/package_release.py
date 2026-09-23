"""Three deterministic releases: GLB-free source, retained reports, optional exports.

Source publishing is allow-listed. A runtime cache is never a source dependency.
Generated outputs are built in a temporary directory and are removed on failure.
"""
from pathlib import Path
import argparse,hashlib,json,zipfile,tempfile,sys
R=Path(__file__).resolve().parents[1]
DIRS={'apps','packages','scripts','authoring','docs','examples','library','operators','schemas','tests','tools','LICENSES'}
FILES={'.gitattributes','.gitignore','.node-version','AGENTS.md','CONTEXT.md','LICENSE','Open_Studio.cmd','README.md','README.zh-CN.md','THIRD_PARTY_NOTICES.md','package.json','pnpm-workspace.yaml','pnpm-lock.yaml','pyproject.toml','requirements-tested.txt','start.sh','tool.manifest.json','wx'}
IGNORE={'__pycache__','.pytest_cache','.git','.venv','node_modules','workspaces','.wx-cache','generated','exports','.rebuild-lock'}
BLOCKED={'.ttf','.otf','.woff','.woff2','.eot'}
def core_files(root=R):
    result=[]
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if not p.is_file() or p.name=='.DS_Store' or any(x in IGNORE or x.startswith('.library-') or x.endswith('.egg-info') for x in rel.parts):continue
        if p.is_symlink():raise ValueError('Source symlinks are not packaged: '+str(rel))
        if rel.parts[0] not in DIRS and str(rel) not in FILES:continue
        if p.suffix.lower() in BLOCKED:raise ValueError('Font binary cannot be packaged: '+str(rel))
        if p.suffix.lower() in ('.glb','.zip'):raise ValueError('Generated binary in source author directory: '+str(rel))
        result.append(p)
    return sorted(result)
def write_archive(out,files,root_name):
    out.parent.mkdir(parents=True,exist_ok=True)
    pending=out.with_suffix(out.suffix+'.building')
    with zipfile.ZipFile(pending,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(root_name+'/'+name,date_time=(2026,9,22,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=((0o100755 if Path(name).name in {'wx','start.sh'} else 0o100644)<<16);z.writestr(info,data,compresslevel=8)
    with zipfile.ZipFile(pending) as z:
        bad=z.testzip()
        if bad:raise ValueError('ZIP CRC failure: '+bad)
    pending.replace(out)
    return {'path':str(out),'bytes':out.stat().st_size,'files':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zip_crc_passed':True}
def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mode',choices=['core','evidence','examples'],default='core');ap.add_argument('--collection',choices=['all','foundation','worlds','expansion','l1','l2','l3','l4'],default='l3');ap.add_argument('--ids',nargs='+');ap.add_argument('--style',choices=['lowpoly','toon'],default='lowpoly');args=ap.parse_args(argv);out=args.out.resolve()
    if out.is_relative_to(R):ap.error('Archive output must be outside the source root')
    if (R/'authoring/.rebuild-lock').exists() or list(R.glob('.library-*')):raise ValueError('Unfinished authoring transaction')
    files={}
    if args.mode=='core':
        files={str(p.relative_to(R)):p.read_bytes() for p in core_files()}
        roster={name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in files.items()}
        manifest={'schema':'wx.source-package/1.0','version':'3.10.0','closed_roster':True,'mode':'core','generated_glb_count':0,'files':roster}
        raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();(R/'WX_MANIFEST.json').write_bytes(raw);files['WX_MANIFEST.json']=raw
    elif args.mode=='evidence':
        folder=R/'docs/game410'
        for p in (folder/name for name in ('index.html','new-assets.csv','new-assets.json')):
            if p.is_file() and p.suffix.lower() not in BLOCKED|{'.glb','.zip'} and not any(x in IGNORE for x in p.relative_to(folder).parts):files[str(p.relative_to(folder))]=p.read_bytes()
        if not files:raise ValueError('No current-release evidence was generated')
    else:
        sys.path.insert(0,str(R/'packages/kit/src'));from asset_jobs import rows,materialized
        from wanxiang.kit_assembly import get_template
        from wanxiang.live_geometry import stop
        try:
            for row in rows(args.collection,args.ids):
                ident=row['id']
                with materialized(ident,args.style) as (p,asset):files[ident+'/asset.glb']=p.read_bytes()
                spec={'schema':'wx.part-build/1.0','id':ident,'part':ident,'style':args.style,'params':{}} if row['kind']=='part' else {**get_template(ident),'style':args.style}
                files[ident+'/recipe.json']=(json.dumps(spec,ensure_ascii=False,indent=2)+'\n').encode()
        finally:stop()
    if args.mode!='core':files['PACKAGE_MANIFEST.json']=(json.dumps({'version':'3.10.0','mode':args.mode,'files':{n:{'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for n,b in files.items()}},ensure_ascii=False,indent=2)+'\n').encode()
    result=write_archive(out,files,R.name if args.mode=='core' else 'Wanxiang3D_3.10.0_'+args.mode);result.update(mode=args.mode,glb_count=sum(n.endswith('.glb') for n in files));print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':main()
