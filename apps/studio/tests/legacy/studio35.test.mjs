import { test as test } from "vitest";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path");
require("@wanxiang/runtime/semantic");
const S = require("@wanxiang/runtime/scene-document"),
  C = require("@wanxiang/runtime/studio-core"),
  root = path.resolve(import.meta.dirname, "../../../.."),
  catalog = {};
for (const dir of ["parts", "assemblies"])
  for (const f of fs.readdirSync(path.join(root, "library", dir)))
    if (f.endsWith(".json")) {
      const x = JSON.parse(fs.readFileSync(path.join(root, "library", dir, f)));
      catalog[x.id] = x;
    }
const src = catalog["l4-interior-living"],
  base = () => S.normalize(src, catalog),
  apply = (d, c) => S.apply(d, c, catalog),
  ins = (d, id) => d.instances.find((i) => i.id === id),
  records = JSON.parse(
    fs.readFileSync(path.join(root, "library/registry.json")),
  ).records;
test("Registry has 3730 formal IDs without duplicates", () => {
  assert.equal(records.length, 3730);
  assert.equal(new Set(records.map((x) => x.id)).size, 3730);
});
test("Taxonomy counts conserve all 3730 records", () => {
  const n = C.counts(records);
  assert.deepEqual(n.levels, { 1: 1600, 2: 1010, 3: 1000, 4: 120 });
  assert.equal(
    Object.values(n.domains).reduce((a, b) => a + b),
    3730,
  );
});
test("Old mechanical category aliases normalize", () => {
  for (const c of ["mechanism", "mech", "machines"])
    assert.equal(C.domain({ category: c }), "industry");
});
test("Twelve scene theme counts account for every L4", () => {
  const scenes = records.filter((x) => x.level === 4);
  assert.equal(scenes.length, 120);
  for (const a of scenes) assert(C.themes[C.sceneTheme(a)]);
});
test("Combined level, domain and keyword search", () => {
  const a = [
    { id: "one", name: "小猫", level: 3, category: "animal" },
    { id: "two", name: "小猫部件", level: 1, category: "animal" },
    { id: "three", name: "桌子", level: 3, category: "interior" },
  ];
  assert.deepEqual(
    C.filter(a, { level: "3", domain: "creature", query: "cat" }).map(
      (x) => x.id,
    ),
    ["one"],
  );
});
test("Favorites preserve current level filter", () =>
  assert(
    C.filter(
      records,
      { level: "3", collection: "favorites" },
      { favorites: records.slice(0, 50).map((x) => x.id) },
    ).every((x) => x.level === 3),
  ));
test("Recents order is deterministic", () => {
  const a = records.slice(0, 4),
    ids = a.map((x) => x.id).reverse();
  assert.deepEqual(
    C.filter(a, { collection: "recent" }, { recent: ids }).map((x) => x.id),
    ids,
  );
});
test("Filter never mutates author registry", () => {
  const before = JSON.stringify(records);
  C.filter(records, { sort: "name" });
  assert.equal(JSON.stringify(records), before);
});
test("UI preference sanitization clamps malformed values", () => {
  assert.equal(C.cleanPrefs({}).rightWidth, 360);
  assert.equal(C.cleanPrefs({ rightWidth: 310 }).rightWidth, 310);
  const p = C.cleanPrefs({
    leftWidth: Infinity,
    rightWidth: -4,
    snapMove: -1,
    snapRotate: 999,
    view: "<script>",
    favorites: ["a", "a", 4],
  });
  assert.equal(p.leftWidth, 224);
  assert.equal(p.rightWidth, 270);
  assert.equal(p.snapMove, 0.001);
  assert.equal(p.snapRotate, 180);
  assert.equal(p.view, "grid");
  assert.deepEqual(p.favorites, ["a"]);
});
test("Unavailable local storage has safe fallback", () => {
  assert.equal(C.storage("missing", "fallback"), "fallback");
  assert.equal(C.save("test", { a: 1 }), false);
});
test("Displayed author strings are escaped", () =>
  assert.equal(C.esc('<img src="x">&'), "&lt;img src=&quot;x&quot;&gt;&amp;"));
test("Atomic batch applies all transforms", () => {
  const d = apply(base(), {
    type: "batch",
    commands: [
      { type: "transform", id: "primary", position: [1, 2, 3] },
      { type: "transform", id: "secondary", rotation: [0, 90, 0] },
    ],
  });
  assert.deepEqual(ins(d, "primary").position, [1, 2, 3]);
  assert.deepEqual(ins(d, "secondary").rotation, [0, 90, 0]);
});
test("Failed batch leaves original byte-for-byte unchanged", () => {
  const d = base(),
    raw = JSON.stringify(d);
  assert.throws(() =>
    apply(d, {
      type: "batch",
      commands: [
        { type: "transform", id: "primary", position: [1, 2, 3] },
        { type: "transform", id: "ground", position: [1, 2, 3] },
      ],
    }),
  );
  assert.equal(JSON.stringify(d), raw);
});
test("Nested and oversized batches are refused", () => {
  assert.throws(() =>
    apply(base(), {
      type: "batch",
      commands: [{ type: "batch", commands: [] }],
    }),
  );
  assert.throws(() =>
    apply(base(), {
      type: "batch",
      commands: Array(1001).fill({ type: "rename-scene", title: "a" }),
    }),
  );
});
test("Multi transform uses exact per-object values", () => {
  const d = apply(base(), {
    type: "transform-many",
    ids: ["primary", "secondary"],
    values: {
      primary: { rotation: [0, 45, 0] },
      secondary: { scale: [2, 2, 2] },
    },
  });
  assert.deepEqual(ins(d, "primary").rotation, [0, 45, 0]);
  assert.deepEqual(ins(d, "secondary").scale, [2, 2, 2]);
});
test("Multi transform rejects locked selection atomically", () =>
  assert.throws(
    () =>
      apply(base(), {
        type: "transform-many",
        ids: ["primary", "ground"],
        delta: [1, 0, 0],
      }),
    /锁定/,
  ));
test("Non-finite nested command rejected before clone", () =>
  assert.throws(
    () =>
      apply(base(), {
        type: "params",
        id: "primary",
        params: { bad: Infinity },
      }),
    /非有限/,
  ));
test("Positive bounded scales are mandatory", () => {
  for (const scale of [
    [0.00001, 1, 1],
    [101, 1, 1],
    [1, 0, 1],
  ])
    assert.throws(() =>
      apply(base(), { type: "transform", id: "primary", scale }),
    );
});
test("Duplicate a parent copies and rebinds descendants", () => {
  let d = base();
  ins(d, "secondary").parent = "primary.frame";
  d = apply(d, { type: "duplicate", id: "primary", offset: [2, 0, 0] });
  assert.equal(ins(d, "secondary_copy").parent, "primary_copy.frame");
  assert.deepEqual(
    ins(d, "secondary_copy").position,
    ins(d, "secondary").position,
  );
  assert.equal(
    ins(d, "primary_copy").position[0],
    ins(d, "primary").position[0] + 2,
  );
});
test("Duplicate IDs stay unique across repeated batch commands", () => {
  const d = apply(base(), {
    type: "batch",
    commands: Array(10).fill({ type: "duplicate", id: "primary" }),
  });
  assert.equal(new Set(d.instances.map((x) => x.id)).size, d.instances.length);
  assert.equal(d.instances.length, base().instances.length + 10);
});
test("Copy clearing group does not remove original group", () => {
  let d = apply(base(), {
    type: "group",
    ids: ["primary", "secondary"],
    group: "g",
    label: "Set",
  });
  d = apply(d, { type: "duplicate", id: "primary" });
  assert.equal(d.metadata.scene.objects.primary.group, "g");
  assert.equal(d.metadata.scene.objects.primary_copy.group, undefined);
});
test("Group locks protect all member transforms", () => {
  let d = apply(base(), {
    type: "group",
    ids: ["primary", "secondary"],
    group: "g",
  });
  d = apply(d, { type: "group-lock", group: "g", locked: true });
  assert.throws(
    () => apply(d, { type: "transform", id: "primary", position: [0, 0, 0] }),
    /锁定/,
  );
});
test("Group visibility restores independent hidden flags", () => {
  let d = apply(base(), {
    type: "group",
    ids: ["primary", "secondary"],
    group: "g",
  });
  d = apply(d, { type: "visibility", id: "primary", visible: false });
  d = apply(d, { type: "group-visibility", group: "g", visible: false });
  d = apply(d, { type: "group-visibility", group: "g", visible: true });
  assert.equal(ins(d, "primary").enabled, false);
  assert.equal(ins(d, "secondary").enabled, true);
});
test("Ungroup leaves object TRS unchanged", () => {
  let d = apply(base(), {
    type: "group",
    ids: ["primary", "secondary"],
    group: "g",
  });
  const p = ins(d, "primary").position;
  d = apply(d, { type: "ungroup", id: "primary" });
  assert.deepEqual(ins(d, "primary").position, p);
  assert.equal(d.metadata.scene.objects.primary.group, undefined);
});
test("Remove layer reassigns instead of deleting objects", () => {
  let d = apply(base(), { type: "add-layer", layer: "new" });
  d = apply(d, { type: "move-layer", id: "primary", layer: "new" });
  d = apply(d, { type: "remove-layer", layer: "new", target: "furnishings" });
  assert.equal(d.instances.length, base().instances.length);
  assert.equal(d.metadata.scene.objects.primary.layer, "furnishings");
});
test("Cannot move objects into a locked layer", () => {
  let d = apply(base(), {
    type: "layer-lock",
    layer: "furnishings",
    locked: true,
  });
  assert.throws(
    () => apply(d, { type: "move-layer", id: "ground", layer: "furnishings" }),
    /锁定/,
  );
});
test("Insertion automatically chooses unlocked layer", () => {
  let d = base();
  const first = Object.keys(d.metadata.scene.layers)[0];
  d.metadata.scene.layers[first].locked = true;
  d = apply(d, { type: "add", ref: "l3-interior-seat-dining" });
  assert.notEqual(d.metadata.scene.objects[d.instances.at(-1).id].layer, first);
});
test("Insertion refuses all-locked layers", () => {
  let d = base();
  Object.values(d.metadata.scene.layers).forEach((x) => (x.locked = true));
  assert.throws(
    () => apply(d, { type: "add", ref: "l3-interior-seat-dining" }),
    /没有可用/,
  );
});
test("Add accepts legacy ID contract inside batch", () => {
  const d = apply(base(), {
    type: "batch",
    commands: [
      { type: "add", id: "test_chair", ref: "l3-interior-seat-dining" },
    ],
  });
  assert(ins(d, "test_chair"));
});
test("Replace preserves transform and removes obsolete parameters", () => {
  let d = base();
  ins(d, "primary").params = { old: 123 };
  const pos = ins(d, "primary").position;
  d = apply(d, {
    type: "replace",
    id: "primary",
    ref: "l3-interior-seat-dining",
  });
  assert.deepEqual(ins(d, "primary").position, pos);
  assert.equal(ins(d, "primary").params, undefined);
  assert.equal(ins(d, "primary").assembly, "l3-interior-seat-dining");
});
test("Replace refuses parents with live dependents", () => {
  let d = base();
  ins(d, "secondary").parent = "primary";
  assert.throws(
    () =>
      apply(d, {
        type: "replace",
        id: "primary",
        ref: "l3-interior-seat-dining",
      }),
    /依赖/,
  );
});
test("Unknown refs cannot be pasted into scene", () =>
  assert.throws(
    () =>
      apply(base(), {
        type: "paste",
        instances: [{ id: "x", part: "not-existent" }],
        objects: { x: {} },
      }),
    /不存在/,
  ));
test("Paste preserves nodes and remaps internal parents", () => {
  const d = base(),
    a = JSON.parse(JSON.stringify(ins(d, "primary"))),
    b = JSON.parse(JSON.stringify(ins(d, "secondary")));
  b.parent = "primary";
  const n = apply(d, {
    type: "paste",
    instances: [a, b],
    objects: {
      primary: d.metadata.scene.objects.primary,
      secondary: d.metadata.scene.objects.secondary,
    },
  });
  assert.equal(ins(n, "secondary_paste").parent, "primary_paste");
  assert.equal(n.instances.length, d.instances.length + 2);
});
test("L4 cannot be introduced by replace or paste", () => {
  assert.throws(
    () =>
      apply(base(), {
        type: "replace",
        id: "primary",
        ref: "l4-interior-living",
      }),
    /L1–L3/,
  );
  assert.throws(
    () =>
      apply(base(), {
        type: "paste",
        instances: [{ id: "x", assembly: "l4-interior-living" }],
        objects: {},
      }),
    /L1–L3/,
  );
});
test("Hidden parent disables descendants and restores them", () => {
  let d = base();
  ins(d, "secondary").parent = "primary";
  d = apply(d, { type: "visibility", id: "primary", visible: false });
  assert.equal(ins(d, "secondary").enabled, false);
  d = apply(d, { type: "visibility", id: "primary", visible: true });
  assert.equal(ins(d, "secondary").enabled, true);
});
test("Subset includes multiple ancestor levels", () => {
  let d = base();
  ins(d, "secondary").parent = "primary";
  const third = d.instances.find(
    (i) => !["ground", "primary", "secondary"].includes(i.id),
  );
  third.parent = "secondary";
  d = S.subset(d, { ids: [third.id] }, catalog);
  assert(ins(d, "primary"));
  assert(ins(d, "secondary"));
});
test("Over-deep object structure is refused", () => {
  const d = base();
  let o = d.metadata;
  for (let i = 0; i < 60; i++) o = o.deep = {};
  assert.throws(() => S.normalize(d, catalog), /过深/);
});
test("Unknown layer, region, group cannot be smuggled in", () => {
  for (const k of ["layer", "region", "group"]) {
    let d = base();
    d.metadata.scene.objects.primary[k] = "missing";
    assert.throws(() => S.normalize(d, catalog));
  }
});
test("Historic metadata.scene=true remains editable", () => {
  let d = base();
  d.metadata.scene = true;
  assert(S.normalize(d, catalog).metadata.scene.layers);
});
test("Object reorder preserves data and moves targeted IDs", () => {
  const d = apply(base(), {
    type: "reorder",
    ids: ["secondary"],
    before: "primary",
  });
  assert(
    d.instances.findIndex((i) => i.id === "secondary") <
      d.instances.findIndex((i) => i.id === "primary"),
  );
  assert.equal(d.instances.length, base().instances.length);
});
test("Saved JSON including groups round-trips deterministically", () => {
  let d = apply(base(), {
    type: "group",
    ids: ["primary", "secondary"],
    group: "g",
    label: "我的组",
  });
  d = apply(d, { type: "rename-scene", title: "重构场景" });
  assert.deepEqual(S.normalize(JSON.parse(JSON.stringify(d)), catalog), d);
});
