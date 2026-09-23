import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { access, readFile } from "node:fs/promises";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolve } from "node:path";

import { browserSource } from "@wanxiang/runtime/sources";
const root = resolve(import.meta.dirname, "../..");
const execute = promisify(execFile);

function developmentData(): Plugin {
  let data: Promise<string> | undefined;
  let definitions: Promise<string> | undefined;
  let catalog: Promise<string> | undefined;
  const assets = new Map<string, Promise<string>>();
  const load = async (expression: string, args: string[] = []) => {
    const local = resolve(root, ".venv/bin/python");
    const python =
      process.env.WX_PYTHON ||
      (await access(local).then(
        () => local,
        () => "python3",
      ));
    const { stdout } = await execute(python, ["-c", expression, ...args], {
      cwd: root,
      env: { ...process.env, PYTHONPATH: resolve(root, "packages/kit/src") },
      maxBuffer: 256 * 1024 * 1024,
    });
    return stdout;
  };
  return {
    name: "wanxiang-development-data",
    apply: "serve",
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        if (!req.url?.startsWith("/__wanxiang/")) return next();
        try {
          if (req.url.startsWith("/__wanxiang/thumbnails/")) {
            const id = req.url
              .slice("/__wanxiang/thumbnails/".length)
              .replace(/\.webp$/, "");
            if (!/^[a-zA-Z0-9._-]+$/.test(id) || !req.url.endsWith(".webp")) {
              res.statusCode = 404;
              res.end("Not found");
              return;
            }
            res.setHeader("Content-Type", "image/webp");
            res.end(
              await readFile(resolve(root, "library/thumbnails", `${id}.webp`)),
            );
          } else if (req.url.startsWith("/__wanxiang/assets/")) {
            const match =
              /^\/__wanxiang\/assets\/([A-Za-z0-9][A-Za-z0-9._-]{0,95})\.json$/.exec(
                req.url,
              );
            const id = match?.[1];
            if (!id || id.includes("..")) {
              res.statusCode = 404;
              res.end("Not found");
              return;
            }
            if (!assets.has(id)) {
              const exists = await Promise.all(
                ["parts", "assemblies"].map((kind) =>
                  access(resolve(root, "library", kind, `${id}.json`)).then(
                    () => true,
                    () => false,
                  ),
                ),
              );
              if (!exists.some(Boolean)) {
                res.statusCode = 404;
                res.end("Unknown asset");
                return;
              }
              // Recheck after I/O so concurrent requests share one Python build.
              if (!assets.has(id))
                assets.set(
                  id,
                  load(
                    'import json,sys; from wanxiang.live_viewer import asset_data; print(json.dumps(asset_data(sys.argv[1]),ensure_ascii=False,separators=(",",":")))',
                    [id],
                  ).catch((error: unknown) => {
                    assets.delete(id);
                    throw error;
                  }),
                );
            }
            res.setHeader("Content-Type", "application/json; charset=utf-8");
            res.end(await assets.get(id));
          } else if (req.url === "/__wanxiang/catalog.json") {
            if (!catalog) {
              catalog = load(
                'import json; from wanxiang.live_viewer import catalog_data; print(json.dumps(catalog_data(),ensure_ascii=False,separators=(",",":")))',
              ).catch((error: unknown) => {
                catalog = undefined;
                throw error;
              });
            }
            res.setHeader("Content-Type", "application/json; charset=utf-8");
            res.end(await catalog);
          } else if (req.url === "/__wanxiang/definitions.json") {
            if (!definitions) {
              definitions = load(
                'import json; from wanxiang.live_viewer import bundle_data; print(json.dumps(bundle_data(False),ensure_ascii=False,separators=(",",":")))',
              ).catch((error: unknown) => {
                definitions = undefined;
                throw error;
              });
            }
            res.setHeader("Content-Type", "application/json; charset=utf-8");
            res.end(await definitions);
          } else if (req.url === "/__wanxiang/data.json") {
            if (!data) {
              data = load(
                'import json; from wanxiang.live_viewer import bundle_data; print(json.dumps(bundle_data(),ensure_ascii=False,separators=(",",":")))',
              ).catch((error: unknown) => {
                data = undefined;
                throw error;
              });
            }
            res.setHeader("Content-Type", "application/json; charset=utf-8");
            res.end(await data);
          } else if (req.url === "/__wanxiang/runtime.js") {
            res.setHeader("Content-Type", "text/javascript; charset=utf-8");
            res.end(browserSource());
          } else {
            res.statusCode = 404;
            res.end("Not found");
          }
        } catch (error) {
          res.statusCode = 500;
          res.setHeader("Content-Type", "text/plain; charset=utf-8");
          res.end(
            error instanceof Error
              ? error.message
              : "Unable to load studio data",
          );
        }
      });
    },
  };
}

export default defineConfig(({ command }) => ({
  root: import.meta.dirname,
  define:
    command === "build"
      ? { "process.env.NODE_ENV": JSON.stringify("production") }
      : {},
  plugins: [react(), tailwindcss(), developmentData()],
  resolve: { alias: { "@": resolve(import.meta.dirname, "src") } },
  cacheDir: resolve(root, "generated/frontend/vite-cache"),
  build: {
    outDir: resolve(root, "generated/frontend/build"),
    emptyOutDir: true,
    target: "es2022",
    lib: {
      entry: resolve(import.meta.dirname, "src/main.tsx"),
      name: "WanxiangStudio",
      formats: ["iife"],
      fileName: () => "app.js",
    },
  },
}));
