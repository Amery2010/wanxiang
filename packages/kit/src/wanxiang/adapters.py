"""Explicit generic project copy + verified rollback; no claim of engine runtime approval."""
from pathlib import Path
import shutil,uuid
from .util import inside,sha256,file_info,write_json,read_json,atomic_bytes
from .validation import inspect_asset
from .errors import WXError

def admit(asset,project,destination,apply=False,replace=False):
    asset=Path(asset);project=Path(project).resolve();dest=inside(project,destination)
    if dest.suffix.lower()!='.glb':raise WXError('INPUT_INVALID','Destination must be a .glb path')
    report=inspect_asset(asset)
    if not report['passed']:raise WXError('VALIDATION_FAILED','Source asset failed structural checks')
    if dest.exists() and not replace:raise WXError('INPUT_INVALID','Destination exists; explicit --replace is required')
    result={'operation':'copy_asset','source':file_info(asset),'destination':str(dest),'project':str(project),'will_replace':dest.exists(),'applied':False,'engine_runtime_approval':False}
    if not apply:return result
    receipt_id=uuid.uuid4().hex[:12];log=project/'.wanxiang'/receipt_id;log.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        result['previous_sha256']=sha256(dest);atomic_bytes(log/'previous.glb',dest.read_bytes());result['backup']=str(log/'previous.glb')
    atomic_bytes(dest,asset.read_bytes());result.update(applied=True,receipt=str(log/'receipt.json'),copied_sha256=sha256(dest));write_json(log/'receipt.json',result);return result

def rollback(receipt):
    r=read_json(receipt);project=Path(r['project']);dest=inside(project,Path(r['destination']).relative_to(project))
    if not dest.exists() or sha256(dest)!=r['copied_sha256']:raise WXError('OUTPUT_MISMATCH','Destination changed since admission; refusing destructive rollback')
    if r.get('backup'):
        backup=inside(project,Path(r['backup']).relative_to(project))
        if sha256(backup)!=r['previous_sha256']:raise WXError('VALIDATION_FAILED','Backup was modified')
        atomic_bytes(dest,backup.read_bytes())
    else:dest.unlink()
    r['rolled_back']=True;write_json(receipt,r);return r
