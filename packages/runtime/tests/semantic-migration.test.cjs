const test = require("node:test");
const assert = require("node:assert/strict");
const Semantic = require("../dist/cjs/src/semantic.js").default;
const SceneDocument = require("../dist/cjs/src/scene-document.js").default;
const StudioCore = require("../dist/cjs/src/studio-core.js").default;

test("semantic composition preserves weights, palette, transforms and rejects cycles", () => {
  const child = {
    id: "child",
    size: [1, 1, 1],
    shape_params: {
      forms: [
        {
          kind: "loft",
          bone: { old: 1 },
          color: "#fff",
          rings: [
            { c: [0, 0, 0], r: [1, 1], weights: { old: 1 } },
            { c: [0, 1, 0], r: [1, 1], bone: "old" },
          ],
        },
      ],
    },
  };
  const parent = {
    id: "parent",
    size: [1, 1, 1],
    shape_params: {
      components: [
        {
          part: "child",
          position: [2, 0, 0],
          bind: { old: "new" },
          params: { palette: { "#fff": "#000" } },
        },
      ],
    },
  };
  const original = JSON.stringify({ parent, child });
  const result = Semantic.part(parent, {}, { child });
  const form = result.shape_params.forms[0];
  assert.deepEqual(form.bone, { new: 1 });
  assert.deepEqual(form.rings[0].weights, { new: 1 });
  assert.equal(form.rings[1].bone, "new");
  assert.equal(form.color, "#000");
  assert.equal(form.matrix[12], 2);
  assert.equal(JSON.stringify({ parent, child }), original);
  assert.throws(
    () => Semantic.part(parent, {}, { child: parent }),
    /Missing or cyclic component definition/,
  );
  assert.throws(
    () => Semantic.evaluate({ $op: "div", args: [1, 0] }, {}),
    /Division by zero/,
  );
  assert.throws(
    () => Semantic.evaluate(JSON.parse('{"constructor":1}'), {}),
    /Unsafe object key/,
  );
});

test("scene batches are atomic and selected exports retain required ancestors", () => {
  const source = {
    schema: "wx.assembly/1.0",
    id: "scene",
    instances: [
      { id: "parent", part: "cube" },
      { id: "child", part: "cube", parent: "parent" },
      { id: "other", part: "cube" },
    ],
  };
  const before = JSON.stringify(source);
  assert.throws(
    () =>
      SceneDocument.apply(source, {
        type: "batch",
        commands: [
          { type: "rename", id: "parent", label: "changed" },
          { type: "remove", id: "missing" },
        ],
      }),
    /请选择存在的场景对象/,
  );
  assert.equal(JSON.stringify(source), before);
  assert.deepEqual(
    SceneDocument.subset(source, { ids: ["child"] }).instances.map((x) => x.id),
    ["parent", "child"],
  );
  const locked = SceneDocument.apply(source, {
    type: "lock",
    id: "parent",
    locked: true,
  });
  assert.throws(
    () =>
      SceneDocument.apply(locked, {
        type: "transform",
        id: "parent",
        position: [1, 0, 0],
      }),
    /已锁定/,
  );
});

test("preferences retain strict primitive choices and bounded values", () => {
  const result = StudioCore.cleanPrefs({
    theme: ["dark"],
    view: ["list"],
    favorites: ["one", "one", 2],
    snapMove: -1,
  });
  assert.equal(result.theme, "light");
  assert.equal(result.view, "grid");
  assert.deepEqual(result.favorites, ["one"]);
  assert.equal(result.snapMove, 0.001);
});
