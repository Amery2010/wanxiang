"""Locate trusted executable resources separately from external asset data."""
from pathlib import Path
from functools import lru_cache
import json
import os
from .errors import WXError

PACKAGE_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = next((parent for parent in PACKAGE_ROOT.parents if (parent / 'packages/kit/src/wanxiang').resolve() == PACKAGE_ROOT and (parent / 'schemas').is_dir() and (parent / 'pnpm-workspace.yaml').is_file()), None)
WORKSPACE_ROOT = Path(os.environ.get('WX_WORKSPACE_ROOT', str(SOURCE_ROOT or Path.home() / '.wanxiang'))).expanduser().resolve()
RESOURCE_ROOT = Path(os.environ.get('WX_RESOURCE_ROOT', str(SOURCE_ROOT or WORKSPACE_ROOT))).expanduser().resolve()


def require_source():
    if SOURCE_ROOT is None:
        raise WXError('SOURCE_REQUIRED', 'This command requires a Wanxiang source checkout.')
    return SOURCE_ROOT


def code_path(relative):
    """Resolve a legacy logical code path; never search WX_RESOURCE_ROOT."""
    path = Path(relative)
    if not path.parts or path.is_absolute() or '..' in path.parts:
        raise ValueError('Code resources must be relative paths')
    if path.parts[0] == 'wanxiang':
        return PACKAGE_ROOT.joinpath(*path.parts[1:])
    if path.as_posix() == 'tools/candidate_worker.py':
        return PACKAGE_ROOT / 'candidate_worker.py'
    if SOURCE_ROOT is None:
        resources = PACKAGE_ROOT / '_resources'
        if path.parts[0] in ('vendor', 'workers'):
            return resources / 'runtime' / path
        if path.parts[0] == 'web':
            if path.name in ('app.js', 'viewer.html'):
                return resources / 'studio' / path.name
            return resources / 'runtime/src' / path.name
        return resources / path
    if path.parts[0] in ('vendor', 'workers'):
        return SOURCE_ROOT / 'packages/runtime/dist/compat' / path
    if path.parts[0] == 'web':
        name = path.name
        if name == 'app.js':
            return SOURCE_ROOT / 'apps/studio/artifacts/app.js'
        if name == 'viewer.html':
            return SOURCE_ROOT / 'apps/studio/templates/viewer.html'
        return SOURCE_ROOT / 'packages/runtime/dist/compat/src' / name
    if path.parts[0] == 'runtime':
        return SOURCE_ROOT / 'packages/runtime/dist/compat' / Path(*path.parts[1:])
    return SOURCE_ROOT / path


@lru_cache(maxsize=1)
def require_resources():
    from . import __version__
    required = ('library/registry.json', 'library/parts', 'library/assemblies', 'authoring/thumbnail-policy.json')
    if any(not (RESOURCE_ROOT / name).exists() for name in required):
        raise WXError('RESOURCE_ROOT_INVALID', 'Set WX_RESOURCE_ROOT to a Wanxiang resource root containing library/ and authoring/thumbnail-policy.json.')
    try:
        policy = json.loads((RESOURCE_ROOT / 'authoring/thumbnail-policy.json').read_text())
        registry = json.loads((RESOURCE_ROOT / 'library/registry.json').read_text())
        if policy.get('schema') != 'wx.thumbnail-policy/1.0' or policy.get('version') != __version__ or registry.get('schema') != 'wx.registry/2.0' or registry.get('version') != __version__ or not isinstance(registry.get('records'), list):
            raise ValueError('Incompatible resource schema/version')
    except (OSError, ValueError, AttributeError) as error:
        raise WXError('RESOURCE_ROOT_INVALID', f'Invalid Wanxiang resource root: {error}') from error
    directories = ('parts', 'assemblies', 'motions', 'materials', 'thumbnails')
    indexes = ('game-expansion', 'l1', 'l2', 'l3', 'l4', 'aliases', 'retired', 'foundation', 'worlds', 'expansion', 'interfaces', 'preview-index')
    missing = [f'library/{name}/' for name in directories if not (RESOURCE_ROOT / 'library' / name).is_dir()]
    missing.extend(f'library/{name}.json' for name in indexes if not (RESOURCE_ROOT / 'library' / f'{name}.json').is_file())
    if missing:
        raise WXError('RESOURCE_ROOT_INVALID', 'Incomplete Wanxiang resource root; missing: ' + ', '.join(missing))
    return RESOURCE_ROOT


def runtime_code_files():
    """Enumerate packaged execution inputs, including bundled dependencies."""
    root = code_path('runtime/source-manifest.json').parent
    if not (root / 'source-manifest.json').is_file():
        raise WXError('DEPENDENCY_MISSING', 'Runtime artifacts are missing; run pnpm build in the source checkout before using Python geometry.')
    return {f'runtime/{path.relative_to(root).as_posix()}': path
            for path in sorted(root.rglob('*'))
            if path.is_file() and path.suffix in ('.js', '.cjs', '.mjs', '.json')}
