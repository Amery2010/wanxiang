"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const { runInNewContext } = require("node:vm");
const { tmpdir } = require("node:os");
const sources = require("@wanxiang/runtime/sources");

function runWorker(entry, input) {
  return spawnSync(process.execPath, [require.resolve(entry)], {
    input,
    encoding: "utf8",
    cwd: tmpdir(),
    maxBuffer: 8 * 1024 * 1024,
  });
}

test("the scene entry resolves semantic parameters in a fresh consumer", () => {
  const entry = require.resolve("@wanxiang/runtime/scene-document");
  const source = {
    schema: "wx.assembly/1.0",
    id: "test.scene",
    metadata: {
      parameter_schema: {
        properties: { offset: { type: "number", default: 2 } },
      },
    },
    instances: [
      { id: "box", part: "test.box", position: [{ $param: "offset" }, 0, 0] },
    ],
  };
  const result = spawnSync(
    process.execPath,
    [
      "-e",
      `console.log(JSON.stringify(require(${JSON.stringify(entry)}).normalize(${JSON.stringify(source)})))`,
    ],
    { cwd: tmpdir(), encoding: "utf8" },
  );
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout).instances[0].position, [2, 0, 0]);
});

test("public sources boot the complete browser runtime and worker without a repository", () => {
  const context = {};
  context.window = context;
  runInNewContext(sources.browserSource(), context);
  assert.equal(typeof context.WXRuntime.Library, "function");
  assert.equal(typeof context.WXGeometry.part, "function");
  assert.equal(typeof context.WXSceneDocument.normalize, "function");
  assert.equal(typeof context.prepareCPUShadows, "function");
  assert.equal(typeof context.cpuShadowVisibility, "function");
  assert.equal(context.WX_WORKER_SOURCE, sources.workerSource());
  const worker = { self: {} };
  runInNewContext(sources.workerSource(), worker);
  assert.equal(typeof worker.self.onmessage, "function");
  assert.equal(
    require("@wanxiang/runtime").sceneDocument,
    require("@wanxiang/runtime/scene-document"),
  );
});

test("browser module retains legacy CPU shadow globals", () => {
  const entry = require.resolve("@wanxiang/runtime/browser");
  const result = spawnSync(
    process.execPath,
    [
      "--input-type=module",
      "-e",
      `import { pathToFileURL } from "node:url";
     await import(pathToFileURL(${JSON.stringify(entry)}));
     if (typeof globalThis.prepareCPUShadows !== "function" ||
         typeof globalThis.cpuShadowVisibility !== "function") process.exit(1);`,
    ],
    { cwd: tmpdir(), encoding: "utf8" },
  );
  assert.equal(result.status, 0, result.stderr);
});

test("CPU worker succeeds and preserves its oversized request failure protocol", () => {
  const good = runWorker(
    "@wanxiang/runtime/workers/geometry",
    JSON.stringify({ op: "torus" }),
  );
  assert.equal(good.status, 0, good.stderr);
  const geometry = JSON.parse(good.stdout);
  assert.equal(geometry.status, "ok");
  assert.ok(geometry.positions.length > 0);
  const oversized = runWorker(
    "@wanxiang/runtime/workers/geometry",
    " ".repeat(4000001),
  );
  assert.equal(oversized.status, 5);
  assert.match(JSON.parse(oversized.stdout).error, /Input too large/);
  for (const op of ["lathe", "tube"]) {
    const missing = runWorker(
      "@wanxiang/runtime/workers/geometry",
      JSON.stringify({ op }),
    );
    assert.equal(missing.status, 5);
    assert.equal(JSON.parse(missing.stdout).status, "failed");
  }
});

test("live worker builds geometry, rejects an oversized line, and recovers for the next request", () => {
  const definition = {
    id: "test.box",
    shape: "faceted",
    size: [1, 1, 1],
    shape_params: {
      forms: [{ kind: "bevelbox", size: [1, 1, 1], color: "#aaaaaa" }],
    },
  };
  const request = JSON.stringify({ definition });
  const result = runWorker(
    "@wanxiang/runtime/workers/live-geometry",
    request + "\n" + " ".repeat(4 * 1024 * 1024 + 1) + "\n" + request + "\n",
  );
  assert.equal(result.status, 0, result.stderr);
  const [first, failed, recovered] = result.stdout
    .trim()
    .split("\n")
    .map(JSON.parse);
  assert.equal(first.ok, true, first.error);
  assert.ok(first.result.vertices.length > 0);
  assert.equal(failed.ok, false);
  assert.match(failed.error, /REQUEST_BUDGET/);
  assert.deepEqual(recovered, first);
});
