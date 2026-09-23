"""Assemble self-contained Python distributions without modifying package sources."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys
import tempfile


def main():
    package = Path(__file__).resolve().parents[1]
    root = package.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', '--out', type=Path, default=root / 'generated/dist/python')
    args = parser.parse_args()
    args.outdir = args.outdir.resolve()
    scratch = root / 'generated'
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='kit-build-', dir=scratch) as temporary:
        stage = Path(temporary)
        for name in ('pyproject.toml', 'MANIFEST.in'):
            shutil.copy2(package / name, stage / name)
        shutil.copytree(package / 'src', stage / 'src', ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.egg-info'))
        resources = stage / 'src/wanxiang/_resources'
        shutil.copytree(root / 'schemas', resources / 'schemas')
        runtime = root / 'packages/runtime/dist/compat'
        if not (runtime / 'source-manifest.json').is_file():
            raise SystemExit('Runtime artifacts are missing; run pnpm build before packaging Python.')
        shutil.copytree(runtime, resources / 'runtime', ignore=shutil.ignore_patterns('node_modules'))
        studio = resources / 'studio'
        studio.mkdir()
        shutil.copy2(root / 'apps/studio/artifacts/app.js', studio / 'app.js')
        shutil.copy2(root / 'apps/studio/templates/viewer.html', studio / 'viewer.html')
        subprocess.run([sys.executable, '-m', 'build', '--outdir', str(args.outdir), str(stage)], check=True)


if __name__ == '__main__':
    main()
