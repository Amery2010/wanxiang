from __future__ import annotations
import hashlib, json, os, re, tempfile, time
from pathlib import Path
from typing import Any
import numpy as np
from .errors import WXError
from .paths import RESOURCE_ROOT as ROOT

def canonical(value: Any) -> bytes:
    def default(x):
        if isinstance(x, np.ndarray): return x.tolist()
        if isinstance(x, np.generic): return x.item()
        if isinstance(x, Path): return str(x)
        raise TypeError(type(x).__name__)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False, default=default).encode()

def digest(value): return hashlib.sha256(canonical(value)).hexdigest()
def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def atomic_bytes(path, data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.wx-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(data);f.flush()
            # Sandboxed filesystems can reject fsync even when bytes are readable.
            # Opt-in fallback does NOT assert power-loss durability.
            if os.environ.get('WX_DURABILITY','strict')!='readback':os.fsync(f.fileno())
        if os.environ.get('WX_DURABILITY')=='readback' and Path(tmp).read_bytes()!=data:
            raise WXError('VALIDATION_FAILED','Temporary file readback differs from written bytes')
        os.replace(tmp,path)
        if os.environ.get('WX_DURABILITY')=='readback' and path.read_bytes()!=data:
            raise WXError('VALIDATION_FAILED','Committed file readback differs from written bytes')
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def write_json(path,value): atomic_bytes(path,json.dumps(json.loads(canonical(value)),ensure_ascii=False,indent=2).encode()+b'\n')
def read_json(path): return read_data(path)
def read_data(path, max_bytes=8_000_000):
    p=Path(path)
    if not p.is_file():raise WXError('INPUT_INVALID',f'File not found: {p}')
    if p.stat().st_size>max_bytes:raise WXError('BUDGET_EXCEEDED','Input document too large')
    text=p.read_text('utf-8')
    try:
        if p.suffix.lower() in ('.yaml','.yml'):
            import yaml
            value=yaml.safe_load(text)
        else:value=json.loads(text)
        # Serializing also rejects recursive YAML aliases and non-JSON values.
        canonical(value)
        def depth(v,n=0):
            if n>32:raise ValueError('Nested input exceeds 32 levels')
            if isinstance(v,dict):
                for x in v.values():depth(x,n+1)
            elif isinstance(v,list):
                for x in v:depth(x,n+1)
        depth(value)
        return value
    except (Exception,) as e:
        if isinstance(e,WXError):raise
        raise WXError('RECIPE_INVALID',f'Invalid JSON/YAML: {str(e)[:240]}') from e

def safe_id(text):
    if not isinstance(text,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}',text) or '..' in text:
        raise WXError('INPUT_INVALID',f'Unsafe identifier: {str(text)[:100]}')
    return text

def inside(root,rel):
    root=Path(root).resolve(); p=(root/rel).resolve()
    if p!=root and root not in p.parents:raise WXError('PATH_UNSAFE',f'Path escapes root: {rel}')
    return p

def rng_for(seed,node):return np.random.default_rng(int(hashlib.sha256(f'{int(seed)}:{node}'.encode()).hexdigest()[:16],16))
def result(status='ok',**kw):return {'protocol':'wx.result/1.0','status':status,**kw}
def file_info(path):
    p=Path(path);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha256(p)}
def timer():return time.perf_counter()
def finite(a,name):
    a=np.asarray(a)
    if not np.isfinite(a).all():raise WXError('GEOMETRY_INVALID',f'{name} contains non-finite values')
    return a
