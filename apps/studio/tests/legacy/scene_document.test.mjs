import { test as test } from "vitest";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path");
require("@wanxiang/runtime/semantic");
const S = require("@wanxiang/runtime/scene-document"),
  R = path.resolve(import.meta.dirname, "../../../.."),
  catalog = {};
for (const dir of ["parts", "assemblies"])
  for (const f of fs.readdirSync(path.join(R, "library", dir)))
    if (f.endsWith(".json")) {
      const x = JSON.parse(fs.readFileSync(path.join(R, "library", dir, f)));
      catalog[x.id] = x;
    }
const source = catalog["l4-interior-living"],
  original = JSON.stringify(source),
  norm = () => S.normalize(source, catalog);
test("All 120 L4 sources can enter document editor", () => {
  const scenes = Object.values(catalog).filter((d) => d.metadata?.level === 4);
  assert.equal(scenes.length, 120);
  for (const d of scenes) S.normalize(d, catalog);
});
test("Normalisation preserves the author source", () => {
  norm();
  assert.equal(JSON.stringify(source), original);
});
test("Atomic numeric TRS command", () => {
  const a = S.apply(
    source,
    {
      type: "transform",
      id: "primary",
      position: [1, 2, 3],
      rotation: [0, 35, 0],
      scale: [1, 1, 1],
    },
    catalog,
  );
  assert.deepEqual(
    a.instances.find((i) => i.id === "primary").position,
    [1, 2, 3],
  );
  assert.equal(JSON.stringify(source), original);
});
test("Locked object refuses edits", () =>
  assert.throws(
    () =>
      S.apply(
        source,
        { type: "transform", id: "ground", position: [1, 0, 0] },
        catalog,
      ),
    /锁定/,
  ));
test("Explicit unlock then transform", () => {
  let a = S.apply(
    source,
    { type: "lock", id: "ground", locked: false },
    catalog,
  );
  a = S.apply(
    a,
    { type: "transform", id: "ground", position: [0, -0.3, 0] },
    catalog,
  );
  assert.equal(a.instances[0].position[1], -0.3);
});
test("Duplicate has a unique editable identity", () => {
  const a = S.apply(source, { type: "duplicate", id: "primary" }, catalog);
  assert.equal(a.instances.length, source.instances.length + 1);
  assert.equal(a.instances.at(-1).id, "primary_copy");
  assert.equal(a.metadata.scene.objects.primary_copy.locked, false);
});
test("Remove selected does not remove unrelated objects", () => {
  const a = S.apply(source, { type: "remove", id: "primary" }, catalog);
  assert.equal(a.instances.length, source.instances.length - 1);
  assert(!a.metadata.scene.objects.primary);
});
test("Visibility preference survives layer toggle", () => {
  let a = S.apply(
    source,
    { type: "visibility", id: "primary", visible: false },
    catalog,
  );
  const layer = a.metadata.scene.objects.primary.layer;
  a = S.apply(a, { type: "layer-visibility", layer, visible: false }, catalog);
  a = S.apply(a, { type: "layer-visibility", layer, visible: true }, catalog);
  assert.equal(a.instances.find((i) => i.id === "primary").enabled, false);
});
test("Add a L3 reference without baking geometry", () => {
  const a = S.apply(
    source,
    {
      type: "add",
      id: "new_chair",
      ref: "l3-interior-seat-dining",
      layer: "furnishings",
      region: "site",
    },
    catalog,
  );
  assert.equal(a.instances.at(-1).assembly, "l3-interior-seat-dining");
  assert(!a.instances.at(-1).mesh);
});
test("Reject insertion of another L4", () =>
  assert.throws(
    () => S.apply(source, { type: "add", ref: "l4-interior-bedroom" }, catalog),
    /L1–L3/,
  ));
test("Reject unknown asset", () =>
  assert.throws(
    () => S.apply(source, { type: "add", ref: "invented" }, catalog),
    /不存在/,
  ));
test("Reject zero scale, NaN and negative scale", () => {
  for (const x of [0, NaN, -1])
    assert.throws(() =>
      S.apply(
        source,
        { type: "transform", id: "primary", scale: [x, 1, 1] },
        catalog,
      ),
    );
});
test("Reject duplicate object ID", () => {
  const d = norm();
  d.instances.push({ ...d.instances[1] });
  assert.throws(() => S.normalize(d, catalog), /重复/);
});
test("Reject dangerous object keys", () => {
  const d = JSON.parse('{"__proto__":{"polluted":true}}');
  assert.throws(() => S.normalize(d, catalog), /不安全/);
  assert.equal({}.polluted, undefined);
});
test("Region subset keeps source and world coordinates", () => {
  const d = S.subset(source, { region: "east" }, catalog);
  assert(d.instances.length < source.instances.length);
  for (const i of d.instances)
    assert.deepEqual(
      i.position,
      norm().instances.find((x) => x.id === i.id).position,
    );
});
test("Hidden object export cannot silently include invisible meshes", () => {
  const a = S.apply(
    source,
    { type: "visibility", id: "primary", visible: false },
    catalog,
  );
  assert.throws(() => S.subset(a, { ids: ["primary"] }, catalog), /没有/);
});
test("Dependency-aware subset includes parent", () => {
  let a = norm();
  a.instances.find((i) => i.id === "secondary").parent = "primary";
  a.metadata.scene.objects.secondary.region = "east";
  const b = S.subset(a, { ids: ["secondary"] }, catalog);
  assert(b.instances.some((x) => x.id === "primary"));
});
test("Parent removal cascades, refusing locked dependents", () => {
  let a = norm();
  a.instances.find((i) => i.id === "secondary").parent = "primary";
  const b = S.apply(a, { type: "remove", id: "primary" }, catalog);
  assert(!b.instances.some((x) => x.id === "secondary"));
  a.metadata.scene.objects.secondary.locked = true;
  assert.throws(
    () => S.apply(a, { type: "remove", id: "primary" }, catalog),
    /锁定/,
  );
});
test("Reject hierarchy cycles", () => {
  let a = norm();
  a.instances.find((i) => i.id === "primary").parent = "secondary";
  a.instances.find((i) => i.id === "secondary").parent = "primary";
  assert.throws(() => S.normalize(a, catalog), /成环/);
});
test("JSON save/reload is deterministic", () => {
  const a = norm(),
    b = S.normalize(JSON.parse(JSON.stringify(a)), catalog);
  assert.deepEqual(a, b);
});
test("Add layer and move object", () => {
  let a = S.apply(
    source,
    { type: "add-layer", layer: "review", label: "审核对象" },
    catalog,
  );
  a = S.apply(
    a,
    { type: "move-layer", id: "primary", layer: "review" },
    catalog,
  );
  assert.equal(a.metadata.scene.objects.primary.layer, "review");
});
test("Dotted instance names resolve to the longest parent prefix", () => {
  let a = norm();
  let i = a.instances.find((x) => x.id === "primary");
  i.id = "room.sofa";
  a.metadata.scene.objects[i.id] = a.metadata.scene.objects.primary;
  delete a.metadata.scene.objects.primary;
  a.instances.find((x) => x.id === "secondary").parent = "room.sofa.frame";
  a = S.normalize(a, catalog);
  const b = S.subset(a, { ids: ["secondary"] }, catalog);
  assert(b.instances.some((x) => x.id === "room.sofa"));
  const c = S.apply(a, { type: "remove", id: "room.sofa" }, catalog);
  assert(!c.instances.some((x) => x.id === "secondary"));
});
