"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { runInNewContext } = require("node:vm");
const sources = require("@wanxiang/runtime/sources");
function runtime() {
  const context = { ArrayBuffer };
  context.window = context;
  runInNewContext(sources.browserSource(), context);
  return context;
}
const socket = {
  id: "port",
  interface: "arch.wall.1m.v1",
  version: 1,
  position: [0, 0, 0],
  normal: [0, 1, 0],
  tangent: [1, 0, 0],
};
function data(version = 1) {
  return {
    parts: {
      "test.box": {
        id: "test.box",
        shape: "faceted",
        size: [1, 1, 1],
        material: "mat.matte",
        shape_params: {
          forms: [{ kind: "bevelbox", size: [1, 1, 1], bevel: 0.1 }],
        },
      },
    },
    assemblies: {},
    materials: [{ id: "mat.matte", record: { kind: "palette" } }],
    interfaces: { "arch.wall.1m.v1": { version, tolerance: 0.0001 } },
  };
}
const spec = {
  schema: "wx.assembly/1.0",
  id: "test.assembly",
  instances: [{ id: "box", part: "test.box" }],
  exports: [socket],
};

test("private nested assemblies build without weakening assembly validation", () => {
  const wx = runtime(), input = data();
  input.assemblies["test.private"] = { ...spec, id: "test.private", internal: true };
  const library = new wx.WXRuntime.Library(input);
  const built = library.buildSync({ ...spec, instances: [{ id: "private", assembly: "test.private" }] }, { noTextures: true });
  assert.ok(built.report.triangles > 0);
  wx.WXBuildExport.disposeBuild(built.root);
  assert.throws(() => library.buildSync({ ...spec, internal: "yes" }), /internal flag must be boolean/);
  assert.throws(() => library.buildSync({ ...spec, unexpected: true }), /Unknown assembly field/);
});

test("Library registries are isolated from construction and legacy singleton mutation", () => {
  const wx = runtime(),
    input = data(),
    first = new wx.WXRuntime.Library(input),
    second = new wx.WXRuntime.Library(data(2));
  input.interfaces["arch.wall.1m.v1"].version = 9;
  wx.WXContracts.setRegistry({ "arch.wall.1m.v1": { version: 3 } });
  const built = first.buildSync(spec, { noTextures: true });
  assert.ok(built.report.triangles > 0);
  wx.WXBuildExport.disposeBuild(built.root);
  assert.throws(
    () => second.buildSync(spec, { noTextures: true }),
    /Interface version field mismatch/,
  );
  assert.equal(first.contracts.registry()["arch.wall.1m.v1"].version, 1);
  assert.equal(wx.WXContracts.registry()["arch.wall.1m.v1"].version, 3);
  const detached = first.contracts.registry();
  detached["arch.wall.1m.v1"].version = 8;
  assert.equal(first.contracts.registry()["arch.wall.1m.v1"].version, 1);
});

test("shared build/export retains texture policy, phase checks and releases on failure", async () => {
  const wx = runtime(),
    calls = [],
    root = new wx.THREE.Group(),
    glb = new ArrayBuffer(12);
  const library = {
    async build(spec, options) {
      calls.push(["build", options.noTextures]);
      return { root, bom: [], report: { triangles: 1 }, spec };
    },
    clips() {
      return [];
    },
  };
  const result = await wx.WXBuildExport.buildAndExport(library, spec, {
    noTextures: true,
    phase: (p) => calls.push(["phase", p]),
    check: () => calls.push(["check"]),
    exporter: {
      async parseAsync(value, options) {
        assert.equal(value, root);
        assert.equal(options.binary, true);
        assert.equal(options.onlyVisible, false);
        assert.equal(options.maxTextureSize, 4096);
        assert.equal(options.trs, undefined);
        return glb;
      },
    },
    dispose: (value) => calls.push(["dispose", value === root]),
  });
  assert.equal(result.glb, glb);
  assert.deepEqual(calls, [
    ["check"],
    ["phase", "geometry"],
    ["build", true],
    ["check"],
    ["phase", "export"],
    ["check"],
    ["dispose", true],
  ]);
  let disposed = 0;
  await assert.rejects(
    wx.WXBuildExport.buildAndExport(library, spec, {
      exporter: {
        async parseAsync() {
          throw Error("export failed");
        },
      },
      dispose() {
        disposed++;
      },
    }),
    /export failed/,
  );
  assert.equal(disposed, 1);
  let checks = 0;
  await assert.rejects(
    wx.WXBuildExport.buildAndExport(library, spec, {
      check() {
        if (++checks === 2) throw Error("cancelled");
      },
      exporter: {
        async parseAsync() {
          assert.fail("cancelled build must not export");
        },
      },
      dispose() {
        disposed++;
      },
    }),
    /cancelled/,
  );
  assert.equal(disposed, 2);
});

test("shared disposal releases reused textures and geometry once", () => {
  const wx = runtime(),
    root = new wx.THREE.Group(),
    geometry = new wx.THREE.BoxGeometry(),
    material = new wx.THREE.MeshStandardMaterial(),
    texture = new wx.THREE.Texture();
  material.map = texture;
  material.emissiveMap = texture;
  root.add(
    new wx.THREE.Mesh(geometry, material),
    new wx.THREE.Mesh(geometry, material),
  );
  const disposed = { geometry: 0, material: 0, texture: 0 };
  geometry.addEventListener("dispose", () => disposed.geometry++);
  material.addEventListener("dispose", () => disposed.material++);
  texture.addEventListener("dispose", () => disposed.texture++);
  wx.WXBuildExport.disposeBuild(root);
  assert.deepEqual(disposed, { geometry: 1, material: 1, texture: 1 });
});

test("module consumers can pack and dispose scenes from another Three instance", () => {
  const foreign = require("@wanxiang/runtime/vendor/three-0.186.0-with-addons.global.js");
  const pipeline = require("@wanxiang/runtime/modules/pipeline").default;
  const pack = require("@wanxiang/runtime/modules/runtime-pack").default;
  const root = new foreign.Group(),
    material = new foreign.MeshStandardMaterial(),
    texture = new foreign.Texture();
  material.map = texture;
  for (let i = 0; i < 2; i++) {
    const geometry = new foreign.BoxGeometry();
    geometry.clearGroups();
    const mesh = new foreign.Mesh(geometry, material);
    mesh.name = "box" + i;
    mesh.position.x = i * 2;
    root.add(mesh);
  }
  const packed = pack.pack(
    { scene: root, parser: { associations: new Map(), json: { nodes: [] } } },
    { id: "test.foreign" },
    { assets: [] },
  );
  assert.equal(packed.report.potential_draws_before, 2);
  assert.equal(packed.report.potential_draws_after, 1);
  packed.cleanup();
  let disposed = 0;
  texture.addEventListener("dispose", () => disposed++);
  pipeline.dispose(root);
  assert.equal(disposed, 1);
});
