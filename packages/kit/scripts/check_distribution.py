"""Exercise an installed wheel from outside the checkout; no browser/E2E checks."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wheel', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='installed-kit-', dir=root/'generated') as scratch:
        scratch = Path(scratch)
        installed = scratch/'read only site'
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps', '--target', str(installed), str(args.wheel.resolve())], check=True, stdout=subprocess.DEVNULL)
        env = {**os.environ, 'PYTHONPATH':str(installed), 'PYTHONDONTWRITEBYTECODE':'1', 'WX_RESOURCE_ROOT':str(root), 'WX_WORKSPACE_ROOT':str(scratch/'work space')}
        files = [path for path in installed.rglob('*') if path.is_file()]
        for path in files: path.chmod(0o444)
        directories = [path for path in installed.rglob('*') if path.is_dir()]
        for path in directories: path.chmod(0o555)
        installed.chmod(0o555)
        try:
            code = '''
import json
from pathlib import Path
from wanxiang.paths import SOURCE_ROOT, WORKSPACE_ROOT, code_path
from wanxiang.cli import doctor
from wanxiang.kit_assembly import build
from wanxiang.live_viewer import bundle_data
from wanxiang.validation import inspect_asset
from wanxiang.render import render_cpu
assert SOURCE_ROOT is None
assert '_resources' in str(code_path('workers/node/live_geometry.cjs'))
diagnostic = doctor(True)
assert diagnostic['glb_roundtrip']['passed'] and diagnostic['three_node_probe']['passed']
result = build('l1.architecture.column.fluted', part=True, review=False)
assert result['passed'] and inspect_asset(result['glb'])['passed']
render_cpu(result['glb'], WORKSPACE_ROOT/'probe.png', 64)
catalogue = bundle_data(thumbnails=False)
assert len(catalogue['assets']) == 3730
print(json.dumps({'glb':result, 'catalogue_assets':len(catalogue['assets']), 'doctor_node':diagnostic['three_node_probe']}))
'''
            result = subprocess.run([sys.executable, '-c', code], env=env, cwd=tempfile.gettempdir(), text=True, capture_output=True)
            if result.returncode: raise RuntimeError(result.stderr)
            print(result.stdout)
            assert {path for path in installed.rglob('*') if path.is_file()} == set(files), 'Runtime wrote inside the installation'
            missing_env = {**env, 'WX_RESOURCE_ROOT':str(scratch/'missing')}
            for command in (['--version'], ['doctor']):
                subprocess.run([sys.executable, '-m', 'wanxiang', *command], env=missing_env, cwd=tempfile.gettempdir(), check=True, stdout=subprocess.DEVNULL)
        finally:
            installed.chmod(0o755)
            for path in directories: path.chmod(0o755)
            for path in files: path.chmod(0o644)


if __name__ == '__main__':
    main()
