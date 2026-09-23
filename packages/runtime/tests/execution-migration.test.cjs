"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const Pipeline = require("@wanxiang/runtime/pipeline");
const { Tasks } = require("@wanxiang/runtime/modules/build-tasks").default;
const { Cache } = require("@wanxiang/runtime/modules/build-cache").default;

function glb(
  document = { asset: { version: "2.0" }, scenes: [{ nodes: [] }], scene: 0 },
) {
  const json = Buffer.from(JSON.stringify(document));
  const length = Math.ceil(json.length / 4) * 4;
  const result = new ArrayBuffer(20 + length);
  const view = new DataView(result);
  view.setUint32(0, 0x46546c67, true);
  view.setUint32(4, 2, true);
  view.setUint32(8, result.byteLength, true);
  view.setUint32(12, length, true);
  view.setUint32(16, 0x4e4f534a, true);
  const bytes = new Uint8Array(result, 20);
  bytes.fill(32);
  bytes.set(json);
  return result;
}
const output = () => ({ buffer: glb(), bom: [], report: {} });

test("prepared GLB owns validated bytes and public loads still reject external resources", async () => {
  const input = glb();
  const prepared = Pipeline.prepare(input);
  assert.equal(prepared.inspection.triangles, 0);
  new Uint8Array(input).fill(0);
  const loaded = await prepared.load();
  assert.equal(loaded.scene.children.length, 0);
  assert.throws(() => Pipeline.inspect(input), /GLB_INVALID/);
  await assert.rejects(Pipeline.load(input), /GLB_INVALID/);
  const external = glb({
    asset: { version: "2.0" },
    images: [{ uri: "https://example.invalid/image.png" }],
  });
  assert.throws(() => Pipeline.prepare(external), /external/);
  await assert.rejects(Pipeline.load(external), /external/);
  assert.throws(
    () =>
      Pipeline.inspect(
        glb({ asset: { version: "2.0" }, nodes: [{ children: [0] }] }),
      ),
    /cycle/,
  );
});

test("memory cache clones transfer buffers and discards corrupt entries", async () => {
  const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
  const cache = new Cache(
    { assets: [], parts: {}, assemblies: {}, motions: {} },
    hash,
  );
  cache.disabled = true;
  const spec = { id: "test.asset" },
    key = cache.key(spec),
    built = output();
  await cache.put(key, spec, built.buffer, { bom: [], report: {} });
  new Uint8Array(built.buffer).fill(0);
  const hit = await cache.get(key);
  assert.equal(hit.cacheSource, "memory");
  assert.equal(Pipeline.inspect(hit.buffer).triangles, 0);
  new Uint8Array(hit.buffer).fill(0);
  assert.ok(await cache.get(key));
  new Uint8Array(cache.memory.get(key).buffer).fill(0);
  assert.equal(await cache.get(key), null);
  assert.equal(cache.memory.has(key), false);
});

test("queue cancellation frees slots and failed main builds do not stall later jobs", async () => {
  let release;
  const tasks = new Tasks({ assets: [] }, (spec) =>
    spec.id === "hold"
      ? new Promise((resolve) => {
          release = resolve;
        })
      : spec.id === "bad"
        ? Promise.reject(Error("build failed"))
        : Promise.resolve(output()),
  );
  tasks.setConcurrency(1);
  const first = tasks.submit({ id: "hold" });
  const cancelled = tasks.submit({ id: "cancel" });
  const rejected = assert.rejects(cancelled, { name: "AbortError" });
  tasks.cancel(2);
  await rejected;
  const failed = tasks.submit({ id: "bad" });
  const failedCheck = assert.rejects(failed, /build failed/);
  const last = tasks.submit({ id: "last" });
  release(output());
  await first;
  await failedCheck;
  await last;
  assert.equal(tasks.snapshot().active.length, 0);
  assert.equal(tasks.snapshot().queued.length, 0);
});

test("dedicated worker cancellation terminates it and denied workers fall back", async () => {
  const original = globalThis.Worker;
  const workers = [];
  let mainCalls = 0;
  class WorkerStub {
    constructor() {
      this.messages = [];
      workers.push(this);
    }
    postMessage(message) {
      this.messages.push(message);
    }
    terminate() {
      this.terminated = true;
    }
  }
  globalThis.Worker = WorkerStub;
  try {
    const tasks = new Tasks(
      { assets: [], aliases: { "legacy.asset": "current.asset" } },
      async () => {
        mainCalls++;
        return output();
      },
      () => {},
      () => "worker source",
    );
    const cancelled = tasks.submit({ id: "cancel" }, { forceWorker: true });
    assert.deepEqual(workers[0].messages[0].data.aliases, {
      "legacy.asset": "current.asset",
    });
    assert.equal("assets" in workers[0].messages[0].data, false);
    const check = assert.rejects(cancelled, { name: "AbortError" });
    tasks.cancel(1);
    await check;
    assert.equal(workers[0].terminated, true);
    const fallback = tasks.submit({ id: "fallback" }, { forceWorker: true });
    workers[1].onmessage({ data: { type: "init-error", error: "blocked" } });
    await fallback;
    assert.equal(workers[1].terminated, true);
    assert.equal(mainCalls, 1);
    assert.equal(tasks.workersAllowed, false);
  } finally {
    globalThis.Worker = original;
  }
});

test("offline worker exports a real untextured GLB through its typed protocol", async () => {
  const { runInNewContext } = require("node:vm");
  const sources = require("@wanxiang/runtime/sources");
  const messages = [];
  class FileReader {
    readAsArrayBuffer(blob) {
      blob.arrayBuffer().then((buffer) => {
        this.result = buffer;
        this.onloadend?.();
      });
    }
  }
  const context = {
    ArrayBuffer,
    Blob,
    TextEncoder,
    FileReader,
    postMessage(message, transfer) {
      messages.push({ message, transfer });
    },
  };
  context.self = context;
  runInNewContext(sources.workerSource(), context);
  await context.onmessage({
    data: {
      type: "init",
      data: {
        parts: {
          box: {
            id: "box",
            shape: "faceted",
            size: [1, 1, 1],
            material: "mat.test",
            shape_params: {
              forms: [{ kind: "bevelbox", size: [1, 1, 1], bevel: 0.1 }],
            },
          },
        },
        assemblies: {
          current: {
            schema: "wx.assembly/1.0",
            id: "current",
            instances: [{ id: "box", part: "box" }],
          },
        },
        aliases: { legacy: "current" },
        materials: [
          {
            id: "mat.test",
            preview: "data:image/png;base64,unused",
            record: { kind: "pbr" },
          },
        ],
      },
    },
  });
  assert.equal(messages[0].message.type, "ready");
  await context.onmessage({
    data: {
      type: "build",
      id: 7,
      spec: {
        schema: "wx.assembly/1.0",
        id: "test.worker",
        instances: [{ id: "item", assembly: "legacy" }],
      },
    },
  });
  const last = messages.at(-1);
  assert.equal(last.message.type, "result", last.message.error);
  assert.equal(last.message.id, 7);
  assert.equal(last.transfer[0], last.message.buffer);
  const inspected = Pipeline.inspect(last.message.buffer);
  assert.ok(inspected.triangles > 0);
  assert.equal(inspected.doc.images?.length || 0, 0);
  assert.equal(last.message.report.textures, 0);
});

test("worker timeouts distinguish unavailable initialization from a failed build", async (t) => {
  const workers = [];
  let timeout,
    mainCalls = 0;
  t.mock.method(globalThis, "setTimeout", (callback, milliseconds) => {
    assert.equal(milliseconds, 60000);
    timeout = callback;
    return 0;
  });
  const original = globalThis.Worker;
  globalThis.Worker = class {
    constructor() {
      workers.push(this);
    }
    postMessage() {}
    terminate() {
      this.terminated = true;
    }
  };
  try {
    const tasks = new Tasks(
      { assets: [] },
      async () => {
        mainCalls++;
        return output();
      },
      () => {},
      () => "worker source",
    );
    const initializing = tasks.submit(
      { id: "init-timeout" },
      { forceWorker: true },
    );
    timeout();
    await initializing;
    assert.equal(workers[0].terminated, true);
    assert.equal(mainCalls, 1);
    assert.equal(tasks.workersAllowed, false);

    tasks.workersAllowed = true;
    const building = tasks.submit(
      { id: "build-timeout" },
      { forceWorker: true },
    );
    workers[1].onmessage({ data: { type: "ready" } });
    workers[1].onmessage({
      data: { type: "progress", id: 2, phase: "export" },
    });
    assert.equal(tasks.snapshot().active[0].phase, "export");
    const failed = assert.rejects(building, /Worker build timed out/);
    timeout();
    await failed;
    assert.equal(workers[1].terminated, true);
    assert.equal(mainCalls, 1);
    assert.equal(tasks.workersAllowed, true);
    const next = tasks.submit({ id: "recovery" }, { forceWorker: true });
    workers[2].onmessage({ data: { type: "result", id: 3, ...output() } });
    assert.equal((await next).worker, true);
    assert.equal(tasks.snapshot().active.length, 0);
  } finally {
    globalThis.Worker = original;
  }
});

test("persistent cache hits validate bytes and persistence failures retain valid memory builds", async () => {
  const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
  const cache = new Cache({ assets: [] }, hash);
  // Exercise the persistence seam in Node without claiming browser IndexedDB evidence.
  const stores = { assets: new Map(), "asset-meta": new Map() };
  cache.transaction = async (name, _mode, operate) => {
    const store = stores[name];
    return operate({
      get: (key) => structuredClone(store.get(key)),
      put: (row) => store.set(row.key, structuredClone(row)),
      delete: (key) => store.delete(key),
      getAll: () => [...store.values()].map((row) => structuredClone(row)),
    });
  };
  cache.storeRow = async (row) => {
    stores.assets.set(row.key, structuredClone(row));
    stores["asset-meta"].set(row.key, cache.metadata(row));
  };
  const spec = { id: "test.disk" },
    key = cache.key(spec);
  await cache.put(key, spec, glb(), { bom: [], report: {} });
  cache.memory.clear();
  const hit = await cache.get(key);
  assert.equal(hit.cacheSource, "disk");
  assert.equal(Pipeline.prepare(hit.buffer).inspection.triangles, 0);
  cache.memory.clear();
  new Uint8Array(stores.assets.get(key).buffer).fill(0);
  assert.equal(await cache.get(key), null);
  assert.equal(stores.assets.has(key), false);
  assert.equal(stores["asset-meta"].has(key), false);
  cache.storeRow = async () => {
    throw new DOMException("Disk full", "QuotaExceededError");
  };
  await cache.put(key, spec, glb(), { bom: [], report: {} });
  assert.equal(cache.disabled, true);
  assert.equal((await cache.get(key)).cacheSource, "memory");
});
