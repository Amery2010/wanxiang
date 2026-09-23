import { build, type InlineConfig } from "vite";
import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, basename, resolve } from "node:path";
import { execFileSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const require = createRequire(import.meta.url);
const dist = resolve(root, "dist");
const compat = resolve(dist, "compat");
const manifest = JSON.parse(
  await readFile(resolve(root, "source-manifest.json"), "utf8"),
) as {
  vendor: string;
  kernel: string[];
  browser: string[];
  worker: string;
};
const namespaces: Record<string, string> = {
  styles: "WXStyles",
  surfaces: "WXSurfaces",
  contracts: "WXContracts",
  semantic: "WXSemantic",
  primitives: "WXPrimitives",
  seams: "WXSeams",
  facets: "WXFacets",
  geometry: "WXGeometry",
  mechanics: "WXMechanics",
  runtime: "WXRuntime",
  pipeline: "WXPipeline",
  "runtime-pack": "WXRuntimePack",
  "cpu-shadows": "WXCPUShadows",
  "build-cache": "WXBuildCache",
  "build-tasks": "WXBuildTasks",
  "studio-core": "WXStudioCore",
  "scene-document": "WXSceneDocument",
  "build-export": "WXBuildExport",
};
const virtualPrefix = "\0wanxiang-entry:";
async function bundle(options: {
  name: string;
  source?: string;
  entry?: string;
  output: string;
  format: "iife" | "umd" | "cjs" | "es";
  globals?: boolean;
  externalThree?: boolean;
}) {
  const entry = options.entry ?? virtualPrefix + options.name;
  const externalNames: Record<string, string> = {};
  const config: InlineConfig = {
    configFile: false,
    root,
    logLevel: "error",
    plugins: [
      {
        name: "wanxiang-compat-entry",
        enforce: "pre",
        resolveId(id, importer) {
          if (id === entry && options.source !== undefined) return entry;
          if (
            (options.globals || options.externalThree) &&
            importer &&
            !importer.startsWith(virtualPrefix)
          ) {
            const stem = basename(id).replace(/\.(?:ts|js)$/, "");
            if (stem === "three") {
              const target = "../vendor/three-0.186.0-with-addons.global.js";
              externalNames[target] = options.globals
                ? "THREE"
                : "globalThis.THREE";
              return { id: target, external: true };
            }
            if (
              options.globals &&
              stem in namespaces &&
              stem !== options.name
            ) {
              const target = `./${stem}.js`;
              externalNames[target] = namespaces[stem];
              return { id: target, external: true };
            }
          }
          return null;
        },
        load(id) {
          return id === entry ? options.source : null;
        },
      },
    ],
    build: {
      target: "es2022",
      minify: !options.globals,
      sourcemap: true,
      emptyOutDir: false,
      outDir: dirname(options.output),
      lib: {
        entry,
        name: namespaces[options.name] ?? options.name,
        formats: [options.format],
        fileName: () => basename(options.output),
      },
      rolldownOptions: {
        input: entry,
        external: /^(?:node:)/,
        output: {
          exports: options.format === "umd" ? "default" : "auto",
          globals: (id: string) => externalNames[id] ?? id,
        },
      },
    },
  };
  await build(config);
}

await rm(dist, { recursive: true, force: true });
await mkdir(compat, { recursive: true });
for (const kind of ["cjs", "esm"]) {
  execFileSync(
    process.execPath,
    [
      require.resolve("typescript/bin/tsc"),
      "-p",
      resolve(root, `tsconfig.${kind}.json`),
    ],
    { cwd: root, stdio: "inherit" },
  );
}
await writeFile(resolve(dist, "esm/package.json"), '{"type":"module"}\n');

// Third-party sources are installed dependencies, never maintained vendor code.
const threeRoot = resolve(dirname(require.resolve("three")), "..");
for (const path of ["build", "examples/jsm", "LICENSE", "package.json"]) {
  await mkdir(dirname(resolve(compat, "vendor/three", path)), {
    recursive: true,
  });
  await cp(resolve(threeRoot, path), resolve(compat, "vendor/three", path), {
    recursive: true,
  });
}
await bundle({
  name: "ThreeCompat",
  source: `import * as THREE from ${JSON.stringify(resolve(root, "src/three.ts"))}; Object.assign(globalThis, {THREE}); export default THREE;`,
  output: resolve(compat, manifest.vendor),
  format: "umd",
});
for (const file of [...manifest.kernel, ...manifest.browser]) {
  const name = basename(file, ".js");
  const exposed =
    name === "cpu-shadows"
      ? `...value, ${namespaces[name]}: value`
      : `${namespaces[name]}: value`;
  await bundle({
    name,
    source: `import value from ${JSON.stringify(resolve(root, "src", name + ".ts"))}; Object.assign(globalThis, {${exposed}}); export default value;`,
    output: resolve(compat, file),
    format: "umd",
    globals: true,
  });
  await writeFile(
    resolve(compat, "src", `${name}.d.cts`),
    `import value from "../../cjs/src/${name}.js";\nexport = value;\n`,
  );
}
await bundle({
  name: "BuildWorker",
  entry: resolve(root, "src/build-worker.ts"),
  output: resolve(compat, manifest.worker),
  format: "iife",
});
await bundle({
  name: "GeometryWorker",
  entry: resolve(root, "workers/node/geometry.ts"),
  output: resolve(compat, "workers/node/geometry.mjs"),
  format: "es",
});
await bundle({
  name: "LiveGeometryWorker",
  entry: resolve(root, "workers/node/live_geometry.ts"),
  output: resolve(compat, "workers/node/live_geometry.cjs"),
  format: "cjs",
});
await bundle({
  name: "Sources",
  entry: resolve(root, "entries/sources.cts"),
  output: resolve(compat, "sources.cjs"),
  format: "cjs",
});
await cp(
  resolve(root, "source-manifest.json"),
  resolve(compat, "source-manifest.json"),
);
await writeFile(
  resolve(compat, "index.cjs"),
  'exports.sceneDocument = require("./src/scene-document.js");\nexports.studioCore = require("./src/studio-core.js");\n',
);
await writeFile(
  resolve(compat, "scene-document.cjs"),
  'module.exports = require("./src/scene-document.js");\n',
);
function browserEntry(names: string[], includeThree: boolean) {
  return (
    (includeThree
      ? `import * as THREE from ${JSON.stringify(resolve(root, "src/three.ts"))};\n`
      : "") +
    names
      .map(
        (name) =>
          `import ${namespaces[name]} from ${JSON.stringify(resolve(root, "src", name + ".ts"))};`,
      )
      .join("\n") +
    `\nObject.assign(globalThis, {${includeThree ? "THREE," : ""}${names.map((name) => namespaces[name]).join(",")}${names.includes("cpu-shadows") ? ",...WXCPUShadows" : ""}});`
  );
}
// Browser imports never take the CommonJS adapter branch or install a second Three.
await bundle({
  name: "BrowserCompat",
  source: browserEntry(
    [...manifest.kernel, ...manifest.browser].map((file) =>
      basename(file, ".js"),
    ),
    true,
  ),
  output: resolve(compat, "browser.mjs"),
  format: "iife",
});
await bundle({
  name: "StudioCompat",
  source: browserEntry(
    ["semantic", "studio-core", "scene-document", "pipeline"],
    false,
  ),
  output: resolve(compat, "studio.mjs"),
  format: "iife",
  externalThree: true,
});
const pkg = JSON.parse(
  await readFile(resolve(root, "package.json"), "utf8"),
) as { name: string; version: string; engines: Record<string, string> };
await writeFile(
  resolve(compat, "package.json"),
  JSON.stringify(
    {
      name: pkg.name,
      version: pkg.version,
      type: "commonjs",
      engines: pkg.engines,
      main: "./index.cjs",
      exports: {
        ".": "./index.cjs",
        "./sources": "./sources.cjs",
        "./scene-document": "./scene-document.cjs",
        "./studio-core": "./src/studio-core.js",
        "./semantic": "./src/semantic.js",
        "./pipeline": "./src/pipeline.js",
        "./browser": "./browser.mjs",
        "./studio": "./studio.mjs",
        "./source-manifest.json": "./source-manifest.json",
        "./workers/geometry": "./workers/node/geometry.mjs",
        "./workers/live-geometry": "./workers/node/live_geometry.cjs",
        "./src/*": "./src/*",
        "./vendor/*": "./vendor/*",
        "./package.json": "./package.json",
      },
    },
    null,
    2,
  ) + "\n",
);
console.log(
  "Built runtime modules, declarations and self-contained compatibility resources.",
);
