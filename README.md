# Wanxiang3D

Wanxiang3D is a local modular Lowpoly workbench for semantic asset authoring, scene assembly, and live GLB export. Run `pnpm dev` from the repository root to preview the Studio. The public catalogue contains 3,730 assets: L1 1,600, L2 1,010, L3 1,000, and L4 120. `library/game-expansion.json` adds 120 L1 parts and 10 separately counted L2 composition examples.

## Monorepo layout

| Module | Responsibility |
| --- | --- |
| `apps/studio` | React/Vite workbench, UI tests, and the compiled UI bundle |
| `packages/runtime` | Strict TypeScript geometry, scene operations, browser runtime, package-managed Three.js, and Node workers |
| `packages/kit` | Python `wanxiang` package and `wx` CLI; reads code from the installed package and assets from an external resource root |

The root keeps `tools/`, `schemas/`, `authoring/`, and `library/` as authoring and data sources. The runtime package is independent of the Studio and Python package. The Studio, Node workers, and Python kit consume one ordered runtime source list so path and loading changes have one place to update.

## Set up

Use Node **24.18.0**, pnpm **11.23.0**, and Python **3.11 or newer** (Python 3.13 is recommended). The repository already supports `WX_PYTHON` when more than one Python interpreter is installed.

```sh
corepack prepare pnpm@11.23.0 --activate
pnpm install
python -m venv .venv
WX_PYTHON=.venv/bin/python
"$WX_PYTHON" -m pip install -e './packages/kit[test,build]'
```

Run workspace commands from the repository root:

```sh
pnpm dev
pnpm build
pnpm typecheck
pnpm lint
pnpm test
pnpm pack:runtime
pnpm pack:python
pnpm pack:source
pnpm verify:authoring
```

`pack:runtime` prepares an npm tarball; `pack:python` prepares a wheel and sdist; and `pack:source` creates a complete source ZIP outside the repository. These commands prepare artifacts only; publishing requires a separate, explicit action. Runtime and Python packaging build runtime artifacts first. The source ZIP is not gated on tests or a successful build: it includes TypeScript inputs and any available compiled runtime artifacts.

To consume the generated packages from a separate project:

```sh
npm install /path/to/wanxiang/generated/distributions/wanxiang-runtime-3.10.0.tgz
python -m pip install /path/to/wanxiang/generated/distributions/python/wanxiang3d_agent_kit-3.10.0-py3-none-any.whl
export WX_RESOURCE_ROOT="/path/to/resource root"
export WX_WORKSPACE_ROOT="/path/to/writable workspace"
wx kit list
```

The Python wheel and sdist include self-contained compiled JavaScript, Three.js with its license, and the precompiled asset review UI; it needs Node for geometry workers but does not need npm or pnpm. Extracting the complete source ZIP provides a compatible external resource root.

## Resources and writable state

The lightweight Python package does not include the complete asset library. Set `WX_RESOURCE_ROOT` to an external resource root containing `library/` and the applicable authoring policy files, including `authoring/thumbnail-policy.json`. In a source checkout, the repository is the default resource root. An installed package requires an explicit resource root for catalogue queries and builds; it never downloads missing data.

`WX_WORKSPACE_ROOT` selects the writable base for implicit workspaces, candidates, and state. A source checkout defaults to the repository; an installed package defaults to `~/.wanxiang`. `--workspace` takes precedence for a command that accepts it. `WX_CACHE_DIR` remains the cache override and takes precedence over its default cache location. `--out` selects an explicit export destination.

`pnpm dev` rebuilds runtime changes and serves the Studio through Vite, reading local catalogue data through Python. `pnpm build` compiles runtime first, then updates the Studio artifact `apps/studio/artifacts/app.js`; it does not generate a standalone HTML page. Run it before invoking Python geometry or author tools directly in a fresh checkout. Runtime outputs include typed ESM/CommonJS modules and a self-contained `packages/runtime/dist/compat` resource tree. Three.js is pinned in `package.json`; legacy vendor paths are generated from that dependency. The CPU fallback and live GLB export remain available.

Studio starts with list metadata only. Model configurations and their referenced parts, assemblies, and animations load when a model is selected or used in a scene/export operation; the home page no longer downloads the full definition library. See [Studio loading](apps/studio/README.md) for the API and offline-viewer boundary.

## Authoring and verification

Edit author modules in `tools/` and current overrides in `authoring/overrides/`; do not edit generated `library/` JSON as the source of truth. New game profiles belong in `tools/game410/` after repair39 in the atomic author pipeline. Models use metres, +Y up, and +Z forward. Collision metadata describes consumer intent; it is not a physics implementation.

The current thumbnail policy keeps one 256×256 Q80 Lowpoly WebP per public asset in `library/thumbnails/`. Geometry changes require a fresh GLB render. Do not reuse historical thumbnail generation options or transcode an earlier compressed output.

The known isolated rebuild issue is a stale `authoring/l1-bounds.json` fingerprint, first reported at `l1.architecture.column.fluted`. Keep delivered definitions intact and reconcile the author source with the measured-bound baseline before regenerating the library.

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for package boundaries and distribution, [docs/API.md](docs/API.md) for the Python/CLI interface, [docs/AUTHORING.md](docs/AUTHORING.md) for authoring and new components, [docs/USAGE.md](docs/USAGE.md) for the workbench, and [docs/LIMITATIONS.md](docs/LIMITATIONS.md) for evidence limits. Geometry contracts are in [docs/MODELING_STANDARDS.zh-CN.md](docs/MODELING_STANDARDS.zh-CN.md), [docs/COMPONENT_INTERFACES.zh-CN.md](docs/COMPONENT_INTERFACES.zh-CN.md), and [docs/SEAM_CONTRACT.md](docs/SEAM_CONTRACT.md). Runtime integration is described in [docs/PRODUCTION_RUNTIME.zh-CN.md](docs/PRODUCTION_RUNTIME.zh-CN.md) and [docs/RUNTIME_EXPORT.md](docs/RUNTIME_EXPORT.md).

The project does not claim mobile-device, physical-GPU, target-engine, Cloud, deployment, or production certification from local/static checks. Browser and E2E checks are separate and require explicit authorization.
