# Persistent current author overrides

Write a complete current definition to `parts/<id>.json`, `assemblies/<id>.json`, `materials/<id>.json`, or `motions/<id>.json`. To retire a current ID, write `{"id":"...","removed":true}`; dependency validation still has to pass.

The author pipeline builds from current Python author modules and these overrides. The metadata-only `retired-v1.json` reserves retired IDs; an override cannot resurrect one. Re-author an old recipe explicitly with current IDs and contracts instead of relying on an automatic redirect.

Do not edit generated `library/` files as the source of truth. Record a deliberate replacement here or in the original author module, then run the authoring verification and rebuild flow described in [docs/AUTHORING.md](../../docs/AUTHORING.md).
