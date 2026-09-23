import { test as check } from "vitest";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
/* Regression for source controls referencing excluded selected-export objects. */
const fs = require("fs"),
  path = require("path"),
  assert = require("assert");
const root = path.resolve(import.meta.dirname, "../../../.."),
  M = require("@wanxiang/runtime/scene-document");
const catalog = {};
for (const kind of ["parts", "assemblies"])
  for (const file of fs.readdirSync(path.join(root, "library", kind))) {
    if (!file.endsWith(".json")) continue;
    const d = JSON.parse(
      fs.readFileSync(path.join(root, "library", kind, file), "utf8"),
    );
    catalog[d.id] = d;
  }
const living = catalog["l4-interior-living"];
check(
  "Excluded furniture controls are not exported with the primary object",
  () => {
    const d = M.subset(living, { ids: ["primary"] }, catalog),
      ids = new Set(d.instances.map((x) => x.id));
    assert(
      (d.metadata.state_controls || []).every(
        (c) => c.node === "root" || ids.has(M.owner(c.node, [...ids])),
      ),
    );
    assert(
      !d.metadata.state_controls.some((c) => c.node.startsWith("secondary.")),
    );
  },
);
check(
  "Retained drawer controls survive and the author source remains unchanged",
  () => {
    const before = JSON.stringify(living),
      d = M.subset(living, { ids: ["secondary"] }, catalog);
    assert(
      d.metadata.state_controls.some((c) => c.node.startsWith("secondary.")),
    );
    assert(
      !d.metadata.state_controls.some((c) => c.node.startsWith("room_item2.")),
    );
    assert.strictEqual(JSON.stringify(living), before);
  },
);
check(
  "Every one of the 120 public L4 scenes exports only controls of retained roots",
  () => {
    const registry = JSON.parse(
      fs.readFileSync(path.join(root, "library/registry.json"), "utf8"),
    ).records;
    const scenes = registry.filter((x) => x.level === 4);
    assert.strictEqual(scenes.length, 120);
    for (const row of scenes) {
      const normalized = M.normalize(catalog[row.id], catalog);
      const selected =
        normalized.instances.find(
          (i) => i.id === "primary" && i.enabled !== false,
        ) || normalized.instances.find((i) => i.enabled !== false);
      const d = M.subset(normalized, { ids: [selected.id] }, catalog),
        ids = d.instances.map((i) => i.id);
      assert(
        (d.metadata.state_controls || []).every(
          (c) => c.node === "root" || ids.includes(M.owner(c.node, ids)),
        ),
        row.id,
      );
    }
  },
);
