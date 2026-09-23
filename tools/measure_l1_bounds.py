"""Refresh placement bounds for L1 parts consumed by the L2 author."""
from pathlib import Path
import argparse, hashlib, json, os, sys

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / 'packages/kit/src'), str(R / 'tools')]
from author_foundation import generate
from wanxiang.live_geometry import build_mesh, stop


def canonical(definition):
    value = dict(definition)
    value.pop('version', None)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', nargs='+', required=True)
    args = parser.parse_args()
    path = R / 'authoring/l1-bounds.json'
    document = json.loads(path.read_text())
    parts = generate(include_l2=False)['parts']
    unknown = set(args.ids) - set(document['assets'])
    if unknown:
        parser.error('Not a measured L1 part: ' + ', '.join(sorted(unknown)))
    try:
        for ident in sorted(set(args.ids)):
            definition = parts[ident]
            mesh = build_mesh(definition, 'lowpoly', {})
            document['assets'][ident] = {
                'bounds': [mesh.vertices.min(axis=0).tolist(), mesh.vertices.max(axis=0).tolist()],
                'canonical_sha256': canonical(definition),
            }
    finally:
        stop()
    pending = path.with_suffix('.pending.json')
    pending.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    os.replace(pending, path)
    print(json.dumps({'updated': sorted(set(args.ids))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
