# Wanxiang Studio

`apps/studio` owns the React/Vite workbench and its UI tests. The source entry is `src/main.tsx`; the development page is `index.html`. The app consumes the shared geometry and scene runtime from `packages/runtime` and calls the Python kit for catalogue data.

## Development and build

Use Node 24.18.0 and pnpm 11.23.0. Install dependencies once from the repository root:

```sh
pnpm install
```

Run the app directly with a workspace filter or use the equivalent root command:

| Command | Behavior |
| --- | --- |
| `pnpm --filter ./apps/studio dev` | Start Vite on 127.0.0.1 |
| `pnpm --filter ./apps/studio build` | Build the React bundle and atomically update `artifacts/app.js` |
| `pnpm --filter ./apps/studio typecheck` | Run strict TypeScript checks |
| `pnpm --filter ./apps/studio lint` | Run ESLint and React Hooks checks |
| `pnpm --filter ./apps/studio test` | Run the Node and jsdom Vitest projects |
| `pnpm --filter ./apps/studio test:watch` | Run Vitest in watch mode; stop it when finished |

The development server chooses the Python interpreter from `WX_PYTHON`, the repository `.venv`, then `python3`. Install `packages/kit[test,build]` in that environment before running `pnpm dev`. The build only compiles the UI bundle. Build caches and verification logs belong under ignored `generated/` paths. Do not edit generated `artifacts/app.js` directly; edit `src/` or the source template instead.

The development page loads only list metadata and shared runtime context from `/__wanxiang/catalog.json`. This reuses `library/registry.json` and `library/preview-index.json`; no duplicate metadata file is maintained. Card images use individual `/__wanxiang/thumbnails/<id>.webp` requests. The home page does not automatically select or build a model.

Selecting a model requests `/__wanxiang/assets/<id>.json`, containing its source configuration and transitive parts, assemblies, and motions. Scene insertion, source restoration, batch export, and explicit compatibility searches load the configurations they need through the same loader. Successful requests are reused; concurrent consumers share requests, cancelled selections cannot replace the current model, and failures can be retried. Loading new definitions preserves the viewport and editing history. `/__wanxiang/definitions.json` and `/__wanxiang/data.json` remain compatibility endpoints; the home page no longer requests them. Self-contained Python review HTML retains embedded data for offline use.

For the current 3,730-model catalogue, compact JSON measurements are 3.11 MB for metadata/shared context, versus the previous 72.44 MB full definition response. A cottage selection needs about 41 KB of configuration; the living-room scene needs about 246 KB. These figures exclude runtime JavaScript, thumbnails, and generated GLB data; they measure payload size, not page-load timing. Server responses are cached for the current development-server session; restart it after changing authored definitions. An already-started Python read may finish after its browser request is cancelled.

## Module responsibilities

- `src/studio/store.ts` owns navigation, preferences, selection, and UI task state. Asset filters derive from read-only data and preserve the existing `wanxiang.studio.preferences.v35` and draft formats.
- `src/studio/session.ts` owns command validation, prepare, cancellation and expiry, commit, history, and drafts through one transaction entry. Failed commands do not commit a document, and switching assets preserves each editing history.
- `src/runtime/` adapts the shared runtime for the workbench. Geometry, Three.js resources, CPU fallback, viewport interaction, and GLB export do not enter Zustand.
- `src/studio/library/` owns navigation, filters, favourites, comparison, the command panel, tasks, and cache management.
- `src/ui/` owns shadcn controls; color tokens live in `src/styles.css` and workbench layout styles live with the Studio sources.

The library and scene workbench share one viewport node. StrictMode and hot reload must pair resource acquisition and release. Diagnostic globals are compatibility adapters; the store, session, and runtime remain authoritative.

`templates/viewer.html` supplies the Python asset review reports with data, Three.js, and script placeholders; it is not the development entry. The obsolete UI compatibility slots have been removed. Shared geometry and scene logic comes from `packages/runtime/src/`; Node workers live under `packages/runtime/workers/node/`, and Python code lives under `packages/kit/src/wanxiang/`.

## Verification boundary

`tests/legacy/` retains the original compatibility assertions. The Studio tests exercise the actual generated bundle and bundle startup contract in jsdom; they do not provide visual, physical GPU, mobile-device, target-engine, or production evidence. Root JavaScript compatibility launchers keep their JSON summary, report location, and failure exit code for Python callers.

Asset definitions are not changed by frontend development. Source packaging remains a root operation and is not gated on every test passing. Browser and E2E checks are separate and require explicit authorization.
