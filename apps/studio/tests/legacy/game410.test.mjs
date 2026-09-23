import { test as test } from "vitest";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path");
const C = require("@wanxiang/runtime/studio-core"),
  R = path.resolve(import.meta.dirname, "../../../.."),
  game = JSON.parse(
    fs.readFileSync(path.join(R, "library/game-expansion.json")),
  ),
  records = JSON.parse(
    fs.readFileSync(path.join(R, "library/registry.json")),
  ).records;
const ids = new Set([...game.parts, ...game.assemblies]),
  byKit = Object.fromEntries(
    Object.entries(game.kits).flatMap(([k, v]) =>
      [...v.parts, v.assembly].map((i) => [i, k]),
    ),
  ),
  assets = records.map((a) => ({
    ...a,
    game_expansion: ids.has(a.id),
    game_kit: byKit[a.id],
  }));
test("All additive models and examples are discoverable", () =>
  assert.equal(
    C.filter(assets, { collection: "game410", level: "all" }).length,
    130,
  ));
for (const kit of Object.keys(game.kits))
  test("Kit / " + kit, () => {
    assert.equal(
      C.filter(assets, { collection: "game410", gameKit: kit }).length,
      13,
    );
    assert.equal(
      C.filter(assets, { collection: "game410", gameKit: kit, level: "1" })
        .length,
      12,
    );
    assert.equal(
      C.filter(assets, { collection: "game410", gameKit: kit, level: "2" })
        .length,
      1,
    );
  });
test("Game filters do not leak into other collections", () =>
  assert.equal(
    C.filter(assets, { collection: "all", gameKit: "dungeon" }).length,
    3730,
  ));
test("Search works inside game collection", () =>
  assert.equal(
    C.filter(assets, { collection: "game410", query: "corn_husk" }).length,
    1,
  ));
test("Favorites can retain more than the former 3600 cap", () =>
  assert.equal(
    C.cleanPrefs({ favorites: assets.map((a) => a.id) }).favorites.length,
    3730,
  ));
test("Filtering and sorting never mutate canonical records", () => {
  const a = JSON.stringify(assets);
  C.filter(assets, { collection: "game410", sort: "name" });
  assert.equal(JSON.stringify(assets), a);
});
