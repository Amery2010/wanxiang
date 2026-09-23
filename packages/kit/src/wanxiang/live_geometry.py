"""Portable, bounded JSON-lines geometry worker shared with the offline browser.
A dedicated pipe reader provides a real deadline on Windows as well as POSIX.
A failed transaction destroys its process; its late reply can never contaminate
the next request. Successful meshes are cached, returned as independent copies.
"""
from __future__ import annotations
from .paths import code_path, WORKSPACE_ROOT
import atexit, json, subprocess, threading, queue, os
from functools import lru_cache
import numpy as np
from .util import ROOT, sha256
from .ir import Mesh, AssetIR
from .errors import WXError
_worker = None
_worker_kernel = None
_replies = None
_lock = threading.RLock()
MAX_REQUEST = 4 * 1024 * 1024
MAX_REPLY = 28 * 1024 * 1024
TIMEOUT = 25.0

def stop():
    global _worker, _replies
    with _lock:
        proc, _worker, _replies = _worker, None, None
        if proc is None:
            return
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
        finally:
            # Do not close stdout while its reader holds the stream lock.
            if proc.stdin:
                try: proc.stdin.close()
                except (BrokenPipeError, OSError): pass

def _read_responses(proc, replies):
    try:
        while True:
            line = proc.stdout.readline(MAX_REPLY + 1)
            if not line:
                replies.put_nowait(RuntimeError('Geometry worker exited'))
                return
            if len(line) > MAX_REPLY or not line.endswith(b'\n'):
                replies.put_nowait(RuntimeError('Worker reply exceeds the protocol budget'))
                return
            replies.put_nowait(line)
    except (OSError, ValueError, queue.Full) as exc:
        try: replies.put_nowait(RuntimeError(str(exc)))
        except queue.Full: pass
    finally:
        proc.stdout.close()

def _start(kernel):
    global _worker, _worker_kernel, _replies
    try:
        _worker = subprocess.Popen(['node', str(code_path('workers/node/live_geometry.cjs'))],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            bufsize=0, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except OSError as exc:
        raise WXError('DEPENDENCY_MISSING', 'Node.js could not start: ' + str(exc)) from exc
    _worker_kernel = kernel
    _replies = queue.Queue(maxsize=2)
    threading.Thread(target=_read_responses, args=(_worker, _replies), daemon=True,
                     name='wanxiang-geometry-reader').start()

atexit.register(stop)

@lru_cache(maxsize=96)
def _get(payload):
    data = (payload + '\n').encode('utf8')
    if len(data) > MAX_REQUEST:
        raise WXError('BUDGET_EXCEEDED', 'Geometry request exceeds 4 MiB')
    with _lock:
        kernel = json.loads(payload).get('kernel_sha256')
        if _worker is None or _worker.poll() is not None or _worker_kernel != kernel:
            stop()
            _start(kernel)
        # Writing a very large pipe can block too: bound the complete write/read
        # transaction, not merely the wait for the first byte of stdout.
        sent = queue.Queue(maxsize=1)
        proc = _worker
        def send():
            try:
                view = memoryview(data)
                while view:
                    n = proc.stdin.write(view)
                    if not n: raise BrokenPipeError('worker pipe closed')
                    view = view[n:]
                sent.put(None)
            except (OSError, ValueError) as exc: sent.put(exc)
        threading.Thread(target=send, daemon=True, name='wanxiang-geometry-write').start()
        import time
        deadline = time.monotonic() + TIMEOUT
        try:
            err = sent.get(timeout=TIMEOUT)
            if err: raise err
            line = _replies.get(timeout=max(.001, deadline - time.monotonic()))
            if isinstance(line, Exception): raise line
            out = json.loads(line)
        except queue.Empty as exc:
            stop()
            raise WXError('BUDGET_EXCEEDED', 'Geometry worker timed out; process was reset') from exc
        except (OSError, ValueError, RuntimeError) as exc:
            stop()
            raise WXError('GEOMETRY_INVALID', 'Geometry worker reset: ' + str(exc)) from exc
        if not isinstance(out, dict) or not isinstance(out.get('ok'), bool):
            stop()
            raise WXError('GEOMETRY_INVALID', 'Invalid worker response envelope')
        if not out['ok']:
            raise WXError('GEOMETRY_INVALID', out.get('error', 'Shared kernel failed'))
        try:
            d = out['result']
            return Mesh(np.array(d['vertices']).reshape(-1, 3), np.array(d['faces']).reshape(-1, 3),
                np.array(d['normals']).reshape(-1, 3), np.array(d['uv']).reshape(-1, 2),
                d.get('colors'), d.get('skin_indices'), d.get('skin_weights'), d.get('rig', []), d.get('anatomy') or {})
        except (KeyError, TypeError, ValueError) as exc:
            stop()
            raise WXError('GEOMETRY_INVALID', 'Malformed mesh reply') from exc

def build_mesh(definition,style,params):
    d=dict(definition)
    if d.get('imported_mesh'):
        p=(ROOT/d['imported_mesh']).resolve()
        if not p.is_relative_to((ROOT/'library/external').resolve()) or sha256(p)!=d['imported_sha256']:raise WXError('VALIDATION_FAILED','Imported geometry hash/path mismatch')
        m=next(iter(AssetIR.load(p.parent).meshes.values()))
        d['mesh_data']={'vertices':m.vertices.ravel().tolist(),'faces':m.faces.ravel().tolist(),'normals':m.normals.ravel().tolist(),'uv':m.uv.ravel().tolist()}
    return _get(json.dumps({'definition':d,'style':style,'params':params,'registry':component_registry(d),'kernel_sha256':sha256(code_path('workers/node/live_geometry.cjs'))},sort_keys=True,separators=(',',':'))).copy()


def component_registry(definition):
    """Read transitive semantic source dependencies. Runtime never evaluates code."""
    from .util import safe_id, read_json
    result = {}
    def visit(d, chain=()):
        if d['id'] in chain or len(chain)>8: raise WXError('RECIPE_INVALID','Cyclic semantic composition')
        for c in d.get('shape_params',{}).get('components',[]):
            ident = safe_id(c['part'])
            path = ROOT/'library/parts'/(ident+'.json')
            if not path.is_file(): raise WXError('RECIPE_INVALID','Component not found: '+ident)
            child = read_json(path)
            if ident not in result:
                result[ident]=child
                visit(child, (*chain, d['id']))
            elif ident in (*chain,d['id']):
                raise WXError('RECIPE_INVALID','Cyclic semantic composition')
    visit(definition)
    return result
