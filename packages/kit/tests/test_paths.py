import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SOURCE = Path(__file__).resolve().parents[1] / 'src'


def probe(code, source=SOURCE, **settings):
    env = {key: value for key, value in os.environ.items() if key not in ('WX_RESOURCE_ROOT', 'WX_WORKSPACE_ROOT', 'WX_CACHE_DIR')}
    env.update(settings, PYTHONPATH=str(source))
    return subprocess.run([sys.executable, '-c', code], env=env, text=True, capture_output=True)


def test_external_resources_cannot_supply_code(tmp_path):
    result = probe("from wanxiang.paths import *; import json; print(json.dumps([str(RESOURCE_ROOT), str(code_path('web/geometry.js')),str(code_path('workers/node/live_geometry.cjs'))]))", WX_RESOURCE_ROOT=str(tmp_path))
    assert result.returncode == 0, result.stderr
    data, geometry, worker = json.loads(result.stdout)
    assert data == str(tmp_path)
    assert str(tmp_path) not in geometry and str(tmp_path) not in worker


def test_workspace_and_cache_are_separate_from_assets(tmp_path):
    result = probe("from wanxiang.pipeline import DEFAULT_WORKSPACE; from wanxiang.build_cache import home; print(DEFAULT_WORKSPACE);print(home())", WX_RESOURCE_ROOT=str(tmp_path/'assets'), WX_WORKSPACE_ROOT=str(tmp_path/'work space'))
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [str(tmp_path/'work space/workspaces/default'), str(tmp_path/'work space/.wx-cache')]
    result = probe("from wanxiang.build_cache import home;print(home())", WX_WORKSPACE_ROOT=str(tmp_path/'workspace'), WX_CACHE_DIR=str(tmp_path/'cache'))
    assert result.stdout.strip() == str(tmp_path/'cache')


def test_installed_defaults_and_missing_assets(tmp_path):
    installed = tmp_path/'site-packages'
    shutil.copytree(SOURCE/'wanxiang', installed/'wanxiang', ignore=shutil.ignore_patterns('__pycache__'))
    result = probe("from wanxiang.paths import *; print(SOURCE_ROOT); print(WORKSPACE_ROOT);print(code_path('web/geometry.js'))", source=installed)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ['None', str(Path.home()/'.wanxiang'), str(installed/'wanxiang/_resources/runtime/src/geometry.js')]
    result = probe("from wanxiang.cli import main; raise SystemExit(main(['kit','list']))", source=installed, WX_RESOURCE_ROOT=str(tmp_path/'missing'))
    assert result.returncode != 0
    assert 'RESOURCE_ROOT_INVALID' in result.stdout
    result = probe("from wanxiang.cli import main; raise SystemExit(main(['--version']))", source=installed)
    assert result.returncode == 0 and '3.10.0' in result.stdout
    result = probe("from wanxiang.paths import require_source; require_source()", source=installed)
    assert result.returncode != 0 and 'source checkout' in result.stderr


def test_resource_version_is_validated(tmp_path):
    (tmp_path/'library/parts').mkdir(parents=True)
    (tmp_path/'library/assemblies').mkdir()
    (tmp_path/'library/registry.json').write_text('{"records": []}')
    (tmp_path/'authoring').mkdir()
    (tmp_path/'authoring/thumbnail-policy.json').write_text('{"schema":"wx.thumbnail-policy/1.0","version":"0.0.0"}')
    result = probe("from wanxiang.paths import require_resources;require_resources()", WX_RESOURCE_ROOT=str(tmp_path))
    assert result.returncode != 0 and 'Incompatible resource schema/version' in result.stderr


def test_external_worker_is_never_executed(tmp_path):
    external = tmp_path/'workers/node'
    external.mkdir(parents=True)
    marker = tmp_path/'executed'
    (external/'geometry.mjs').write_text(f"import fs from 'node:fs'; fs.writeFileSync({json.dumps(str(marker))}, 'bad');")
    code = "from wanxiang.paths import code_path; import subprocess,json; r=subprocess.run(['node',str(code_path('workers/node/geometry.mjs'))],input=json.dumps({'op':'torus','params':{}}),text=True,capture_output=True);assert r.returncode==0,r.stderr"
    result = probe(code, WX_RESOURCE_ROOT=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert not marker.exists()


def test_registry_version_is_validated(tmp_path):
    (tmp_path/'library/parts').mkdir(parents=True)
    (tmp_path/'library/assemblies').mkdir()
    (tmp_path/'library/registry.json').write_text('{"schema":"wx.registry/2.0","version":"0.0.0","records": []}')
    (tmp_path/'authoring').mkdir()
    (tmp_path/'authoring/thumbnail-policy.json').write_text('{"schema":"wx.thumbnail-policy/1.0","version":"3.10.0"}')
    result = probe("from wanxiang.paths import require_resources;require_resources()", WX_RESOURCE_ROOT=str(tmp_path))
    assert result.returncode != 0 and 'Incompatible resource schema/version' in result.stderr


def test_incomplete_resources_fail_before_catalogue_loading(tmp_path):
    (tmp_path/'library/parts').mkdir(parents=True)
    (tmp_path/'library/assemblies').mkdir()
    (tmp_path/'library/registry.json').write_text('{"schema":"wx.registry/2.0","version":"3.10.0","records": []}')
    (tmp_path/'authoring').mkdir()
    (tmp_path/'authoring/thumbnail-policy.json').write_text('{"schema":"wx.thumbnail-policy/1.0","version":"3.10.0"}')
    result = probe("from wanxiang.cli import main; raise SystemExit(main(['kit','list']))", WX_RESOURCE_ROOT=str(tmp_path))
    assert result.returncode != 0
    assert 'RESOURCE_ROOT_INVALID' in result.stdout
    assert 'library/materials/' in result.stdout and 'library/l1.json' in result.stdout
    assert 'INTERNAL_ERROR' not in result.stdout


def test_source_runtime_paths_resolve_compiled_resources():
    names = ['web/geometry.js', 'vendor/three/build/three.module.js',
             'workers/node/live_geometry.cjs', 'runtime/sources.cjs']
    code = f"from wanxiang.paths import code_path;import json;print(json.dumps([str(code_path(n)) for n in {names!r}]))"
    result = probe(code)
    assert result.returncode == 0, result.stderr
    compiled = SOURCE.parents[1] / 'runtime/dist/compat'
    assert json.loads(result.stdout) == [str(compiled / name) for name in
        ['src/geometry.js', 'vendor/three/build/three.module.js',
         'workers/node/live_geometry.cjs', 'sources.cjs']]


def test_runtime_fingerprint_includes_dependency_and_worker(tmp_path, monkeypatch):
    from wanxiang import paths, build_cache
    runtime = tmp_path / 'runtime'
    runtime.mkdir()
    (runtime / 'source-manifest.json').write_text('{}')
    for name in ['src/geometry.js', 'workers/node/live_geometry.cjs',
                 'vendor/three/examples/jsm/loaders/GLTFLoader.js']:
        file = runtime / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('original')
    studio = tmp_path / 'app.js'
    studio.write_text('studio')
    monkeypatch.setattr(paths, 'code_path', lambda name: runtime / 'source-manifest.json')
    monkeypatch.setattr(build_cache, 'code_path', lambda name: studio)
    before = build_cache.engine_info()
    (runtime / 'vendor/three/examples/jsm/loaders/GLTFLoader.js').write_text('changed dependency')
    after_dependency = build_cache.engine_info()
    (runtime / 'workers/node/live_geometry.cjs').write_text('changed worker')
    assert before != after_dependency != build_cache.engine_info()


def test_source_snapshot_keeps_typescript_and_optional_artifacts(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('package_release', SOURCE.parents[2] / 'tools/package_release.py')
    release = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(release)
    source = tmp_path / 'packages/runtime/src/geometry.ts'
    source.parent.mkdir(parents=True)
    source.write_text('export const geometry = {};')
    assert release.core_files(tmp_path) == [source]
    compiled = tmp_path / 'packages/runtime/dist/compat/workers/node/live_geometry.cjs'
    compiled.parent.mkdir(parents=True)
    compiled.write_text('module.exports = {};')
    assert set(release.core_files(tmp_path)) == {source, compiled}


def test_alternate_runtime_fingerprint_includes_package_metadata(tmp_path):
    from wanxiang.build_cache import engine_info
    runtime = tmp_path / 'packages/runtime/dist/compat'
    runtime.mkdir(parents=True)
    package = runtime / 'package.json'
    package.write_text('{"type":"commonjs"}')
    before = engine_info(tmp_path)
    package.write_text('{"type":"module"}')
    assert engine_info(tmp_path) != before
