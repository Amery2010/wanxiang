from __future__ import annotations
import io,json,stat,zipfile,hashlib
from pathlib import Path,PurePosixPath
from .util import sha256,canonical,write_json,atomic_bytes,file_info
from .errors import WXError

MANIFEST='WX_MANIFEST.json'
def _safe_zip_name(name):
    p=PurePosixPath(name)
    if not p.parts or '\x00' in name or p.is_absolute() or '..'in p.parts or '\\'in name or ':'in p.parts[0]:raise WXError('PATH_UNSAFE',f'Unsafe archive member: {name}')
    return name

def package_folder(folder,out,max_part_bytes=300_000_000,exclude=None):
    root=Path(folder).resolve();out=Path(out).resolve();exclude=set(exclude or [])
    if max_part_bytes<4096:raise WXError('BUDGET_EXCEEDED','Part limit must be at least 4096 bytes')
    entries=[]
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise WXError('PATH_UNSAFE',f'Symlink in package source: {p}')
        if not p.is_file() or p==out:continue
        rel=p.relative_to(root).as_posix()
        if rel==MANIFEST or any(part in exclude for part in p.relative_to(root).parts) or rel.endswith('.lock'):continue
        if out.is_relative_to(root) and p.parent==out.parent and p.name.startswith(out.stem):continue
        entries.append((rel,p))
    if not entries:raise WXError('INPUT_INVALID','No files to package')
    def archive(items,part):
        bio=io.BytesIO();roster={name:{'sha256':sha256(path),'bytes':path.stat().st_size} for name,path in items}
        with zipfile.ZipFile(bio,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for name,path in items:z.write(path,name)
            z.writestr(MANIFEST,canonical({'schema':'wx.package/1.0','part':part,'files':roster,'closed_roster':True}))
        return bio.getvalue()
    # Pre-compress members once to estimate split boundaries; recheck the actual finished ZIP.
    import zlib
    groups=[];current=[];size=1600
    for name,path in entries:
        estimate=len(zlib.compress(path.read_bytes(),6))+len(name.encode())*2+320
        if current and size+estimate>max_part_bytes*.98:groups.append(current);current=[];size=1600
        current.append((name,path));size+=estimate
    if current:groups.append(current)
    parts=[];index=1
    while groups:
        items=groups.pop(0);data=archive(items,index)
        if len(data)>max_part_bytes:
            if len(items)==1:raise WXError('BUDGET_EXCEEDED','One compressed file exceeds the requested independent ZIP part limit',details={'file':items[0][0],'bytes':len(data)})
            middle=len(items)//2;groups=[items[:middle],items[middle:],*groups];continue
        target=out if not parts and not groups else out.with_name(f'{out.stem}.part{index:02}.zip')
        # When a later split is needed, all parts use an explicit part suffix.
        atomic_bytes(target,data);verify_package(target);parts.append(file_info(target));index+=1
    if len(parts)>1:
        manifest=out.with_suffix('.parts.json');write_json(manifest,{'schema':'wx.multipart/1.0','parts':parts,'restore':'Each ZIP is independently extractable. Extract all parts into the same empty directory; their relative asset paths do not overlap.'})
    return parts

def verify_package(path):
    p=Path(path)
    if p.is_dir():
        m=json.loads((p/MANIFEST).read_text());expected=set(m['files']);actual=set()
        for x in p.rglob('*'):
            if x.is_symlink():raise WXError('PATH_UNSAFE','Directory contains a symlink')
            if x.is_file() and x.relative_to(p).as_posix()!=MANIFEST:actual.add(x.relative_to(p).as_posix())
        if expected!=actual:raise WXError('VALIDATION_FAILED','Closed directory roster mismatch')
        for rel,info in m['files'].items():
            _safe_zip_name(rel)
            if (p/rel).stat().st_size!=info['bytes'] or sha256(p/rel)!=info['sha256']:raise WXError('VALIDATION_FAILED',f'File hash mismatch: {rel}')
        return {'passed':True,'files':len(expected)}
    with zipfile.ZipFile(p) as z:
        names=[i.filename for i in z.infolist() if not i.is_dir()]
        if len(names)!=len(set(names)):raise WXError('VALIDATION_FAILED','Duplicate ZIP members')
        total=0
        for i in z.infolist():
            _safe_zip_name(i.filename)
            if stat.S_ISLNK(i.external_attr>>16):raise WXError('PATH_UNSAFE','Archive contains a symlink')
            total+=i.file_size
        if total>2_000_000_000:raise WXError('BUDGET_EXCEEDED','ZIP expands beyond verification limit')
        if MANIFEST not in names:raise WXError('VALIDATION_FAILED','Package has no closed manifest')
        roster=json.loads(z.read(MANIFEST));expected=set(roster['files']);actual=set(names)-{MANIFEST}
        if expected!=actual:raise WXError('VALIDATION_FAILED','Closed ZIP roster mismatch',details={'extra':list(actual-expected)[:5],'missing':list(expected-actual)[:5]})
        for name,info in roster['files'].items():
            data=z.read(name)
            if len(data)!=info['bytes'] or hashlib.sha256(data).hexdigest()!=info['sha256']:raise WXError('VALIDATION_FAILED',f'Hash mismatch: {name}')
        if z.testzip() is not None:raise WXError('VALIDATION_FAILED','ZIP CRC failed')
    return {'passed':True,'files':len(expected),'bytes':p.stat().st_size,'sha256':sha256(p)}
