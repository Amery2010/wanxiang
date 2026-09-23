# On-demand examples

No pre-generated catalogue GLBs are shipped. Authoritative sources are under `library/parts/`, `library/assemblies/`, their original author modules, and persistent overrides.

```bash
python wx kit build --assembly exp-scene-forest --out exports/forest
python tools/build_worlds.py --collection expansion --ids exp-birch exp-road-straight --out generated/examples --no-images
python tools/package_release.py --mode examples --ids exp-birch exp-road-straight --out ../Optional_examples.zip
```

`build_worlds.py` without `--out` builds temporary GLBs, independently verifies them, and removes them. It does not require `examples/worlds/*.glb` or `examples/foundation/*.glb` to exist. Historical JSON job examples elsewhere in this folder remain optional source examples, not prebuilt binaries.
