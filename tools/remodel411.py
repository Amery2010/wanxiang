"""Apply the exact imported editable model definitions after historical authors."""
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def definitions():
    manifest = json.loads((ROOT / 'authoring/remodel411-manifest.json').read_text())
    raw = (ROOT / 'authoring/remodel411-definitions.json.gz').read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest['sha256']:
        raise ValueError('Remodeled definition archive checksum mismatch')
    return json.loads(gzip.decompress(raw))


def author():
    from foundation.common import PARTS, ASSEMBLIES, MOTIONS
    imported = definitions()
    for kind, target in [('parts', PARTS), ('assemblies', ASSEMBLIES), ('motions', MOTIONS)]:
        target.update(imported[kind])
