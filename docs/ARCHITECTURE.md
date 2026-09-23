# Wanxiang monorepo architecture

This repository has one data and authoring root with three distributable modules. The root owns the catalogue and the tools that produce it; the modules own reusable runtime code, the workbench, and the Python interface.

## Modules and dependency direction

```text
root data and authoring
├── schemas/ authoring contracts
├── authoring/ current policies, overrides, and baselines
├── tools/ author modules and verification
└── library/ generated catalogue and thumbnails

packages/runtime  ───────► apps/studio
       │                         │
       └──────────────► packages/kit
                         │
                         └── external resource root
```

| Module | Owns | Does not own |
| --- | --- | --- |
| `packages/runtime` | `@wanxiang/runtime`, strict TypeScript geometry and scene operations, browser runtime, ordered compatibility source list, package-managed Three.js, and Node workers | React state, Python imports, or the asset catalogue |
| `apps/studio` | React/Vite UI, workbench state, UI tests, and the compiled UI bundle | Python implementation or a second geometry kernel |
| `packages/kit` | `wanxiang3d-agent-kit`, Python imports, `wx` CLI, resource resolution, GLB assembly, and asset review reports | the complete asset library or pnpm installation |

The runtime module is the shared seam. It has no dependency on Studio or Python, so a Node worker, a browser bundle, and the Python kit can use the same geometry and scene contracts. Studio-specific state stays in Studio; Python-specific path and file handling stays in the kit. Keep this direction acyclic.

## Source and generated data

The authoritative inputs are the root `tools/` author modules, `authoring/overrides/`, `schemas/`, and the uploaded source material. `library/` is generated output. A new component is authored in the appropriate tool module or override, validated, rebuilt, and then previewed from a real GLB. Editing generated JSON or an old report does not change the source of truth.

The public thumbnail contract is one 256×256 Q80 Lowpoly WebP per public asset under `library/thumbnails/`. The policy and source fingerprints are authoritative; a geometry change requires a fresh render. `apps/studio/index.html` is the Vite development entry. Preview the workbench with `pnpm dev`; the repository does not generate a root standalone HTML page.

## Runtime compilation and compatibility source list

Runtime implementation uses explicit TypeScript imports/exports and generates declarations. Three.js is pinned through package.json, with addons imported through package paths. Only compatibility adapters install WX globals. The runtime package owns the ordered logical source list required by the browser and Python kit; its schema and legacy src/*.js names map to compiled artifacts. Consumers ask the runtime package for that list and for the corresponding packaged files; they do not reconstruct it from the current working directory or from duplicated path conventions.

The list separates code sources from external data:

- typed ESM/CommonJS runtime modules and bundled Node workers are packaged with `@wanxiang/runtime`;
- npm module consumers use the declared Three.js dependency; offline compatibility resources bundle the required implementation and copy legacy vendor paths from that dependency, retaining its license;
- Python code is loaded from `packages/kit` in a checkout or from the installed wheel;
- the catalogue, thumbnails, and thumbnail policy are resolved through `WX_RESOURCE_ROOT`; schemas are trusted package resources.

`dist/compat` is the self-contained execution resource tree. Python source checkouts and author tools resolve resources there; wheel/sdist assembly copies it to `wanxiang/_resources/runtime`. No installed Python operation needs npm or pnpm. Changing the list is a compatibility change. Update the consumer contract and the relevant tests together, and keep source hashes meaningful by hashing code and resource roots separately. Cache and toolchain fingerprints include every packaged executable and JSON resource. The live worker fingerprint covers its standalone bundle, including dependency implementation, and changes restart the process.

## Resource and workspace resolution

`WX_RESOURCE_ROOT` points to an external data root containing `library/` and the applicable authoring policy files. In a source checkout it defaults to the repository. An installed Python package does not assume that the repository exists and requires a configured resource root for catalogue queries and builds; it does not download assets.

`WX_WORKSPACE_ROOT` is the writable base for implicit exports, candidate operations, and state. A source checkout uses the repository by default; an installed package uses `~/.wanxiang`. An explicit `--workspace` wins for commands that accept it. `WX_CACHE_DIR` controls the cache and takes precedence over its default. `--out` always selects the command's explicit output destination.

This keeps package code and asset data independent. Normal installed operation never writes into `site-packages`, and a missing resource root produces a clear configuration error while help, version, and diagnostics remain usable.

## Interfaces

The JavaScript package preserves the existing CommonJS-compatible and browser-global behavior at its compatibility entries while exposing stable package exports for new consumers. Its public surfaces are:

- browser runtime and scene operations;
- the ordered packaged source list and resource lookup;
- the geometry worker and live-geometry worker entrypoints.

The Python package preserves the `wanxiang` import namespace, the `wx` command, existing JSON result and worker protocols, scene formats, preference storage, CPU fallback, and live GLB export. The kit may be installed without pnpm; only authoring and source-rebuild workflows require the repository tools.

Each Library owns its connection registry, so creating or updating another Library cannot alter its geometry contracts. Main-thread and worker adapters share the build/export implementation while retaining their texture policies. Asset preparation keeps binary GLB buffers and reuses its inspection result within that operation; public inspection/load validation remains active.

The Studio consumes the runtime exports and produces the compiled UI bundle. It does not silently change the asset definitions when filters, selections, or view state change. The one hero image is sized by the UI and reused across grids, pickers, lists, command results, source cards, and shelf items.

## Build and distribution flow

From the root, pnpm orchestrates the JavaScript workspace and calls the Python kit for package assembly:

1. `pnpm install` installs the workspace lockfile and package dependencies.
2. `pnpm build` compiles runtime and declarations first, then builds the Studio artifact. Development watches runtime inputs and rebuilds compatibility resources.
3. `pnpm pack:runtime` prepares an `@wanxiang/runtime` tarball.
4. `pnpm pack:python` prepares the Python wheel and sdist.
5. `pnpm pack:source` writes a complete source ZIP outside the repository, including TypeScript inputs and any available compiled resources. It does not force a build or require passing tests.

The npm tarball and Python artifacts are prepared for independent installation; this workflow does not publish them. The Python sdist must be able to rebuild its wheel without the original checkout. The packaged kit includes code, schemas, runtime files, workers, and the precompiled asset review UI, but not the complete asset catalogue.

## Change and verification boundaries

Use `apps/studio` checks for UI and bundle behavior, runtime checks for the shared geometry and worker seam, and Python tests for resource resolution, assembly, GLB round trips, and the CLI. Use the authoring checks for root source and generated library invariants. Local/static tests do not establish browser, E2E, physical mobile, GPU, target-engine, Cloud, deployment, or production evidence.

Keep the current CPU fallback, live GLB export, asset IDs, schema contracts, local file behavior, thumbnail policy, and source ZIP rules stable unless a task explicitly changes them. Do not add output-size budget gates. Do not commit, publish, deploy, or run browser/E2E checks without explicit authorization.
