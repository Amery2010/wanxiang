import { test as check } from "vitest";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
/* Explicit sweep-angle contracts; legacy radians must retain their meaning. */
const assert = require("node:assert/strict"),
  fs = require("node:fs"),
  vm = require("node:vm");
for (const file of [
  "@wanxiang/runtime/vendor/three-0.186.0-with-addons.global.js",
  "@wanxiang/runtime/src/primitives.js",
])
  vm.runInThisContext(fs.readFileSync(require.resolve(file), "utf8"));

function near(a, b) {
  assert.equal(a.length, b.length);
  a.forEach((x, i) => assert.ok(Math.abs(x - b[i]) < 1e-10, `${a} != ${b}`));
}
const rings = [
  { c: [0, 0, 0], r: [1, 1] },
  { c: [0, 1, 0], r: [1, 1] },
  { c: [0, 4, 0], r: [1, 1] },
];
const point = (f, j, k = 0) =>
  globalThis.WXPrimitives.loftSection(f, f.rings[j], j, k);
check("total degrees distributed by path length, not ring count", () => {
  const f = { rings, sides: 8, twist_degrees: 180 };
  near(point(f, 0), [1, 0]);
  near(point(f, 1), [Math.SQRT1_2, Math.SQRT1_2]);
  near(point(f, 2), [-1, 0]);
});
check("phase degrees are independent from progressive twist", () => {
  const f = { rings, sides: 8, phase_degrees: 90, twist_degrees: 90 };
  near(point(f, 0), [0, 1]);
  near(point(f, 2), [-1, 0]);
});
check("legacy global radians are a constant phase", () => {
  const f = { rings, sides: 8, twist: Math.PI / 2 };
  for (let j = 0; j < 3; j++) near(point(f, j), [0, 1]);
});
check("legacy per-ring radians still work", () => {
  const rs = rings.map((r, j) => ({ ...r, twist: j * 0.1 }));
  near(point({ rings: rs, sides: 8, twist: 0.2 }, 2), [
    Math.cos(0.4),
    Math.sin(0.4),
  ]);
});
check("custom outline rotates in degree contract", () => {
  const f = {
    rings,
    sides: 4,
    outline: [
      [2, 0],
      [0, 1],
      [-2, 0],
      [0, -1],
    ],
    twist_degrees: 90,
  };
  near(point(f, 0), [2, 0]);
  near(point(f, 2), [0, 2]);
});
check("legacy custom outline behaviour is unchanged", () => {
  const f = {
    rings,
    sides: 4,
    outline: [
      [2, 0],
      [0, 1],
      [-2, 0],
      [0, -1],
    ],
    twist: 100,
  };
  near(point(f, 2), [2, 0]);
});
check("radian and degree controls cannot be silently mixed", () =>
  assert.throws(
    () => point({ rings, sides: 8, twist: 0, phase_degrees: 0 }, 0),
    /mix/,
  ),
);
check("invalid degree input is rejected", () => {
  for (const v of [NaN, Infinity, 3601, -3601, "90"])
    assert.throws(
      () => point({ rings, sides: 8, twist_degrees: v }, 0),
      /finite/,
    );
});
check("facets and seam paths use the same section operator", () => {
  const context = {};
  context.window = context;
  vm.runInNewContext(
    require("@wanxiang/runtime/sources").browserSource(),
    context,
  );
  const original = context.WXPrimitives.loftSection;
  let calls = 0;
  context.WXPrimitives.loftSection = (...args) => {
    calls++;
    return original(...args);
  };
  const first = { kind: "loft", sides: 8, rings: rings.slice(0, 2) };
  const geometry = context.WXFacets.build({ forms: [first] }, {}, "lowpoly");
  try {
    assert.ok(calls > 0);
  } finally {
    geometry.dispose();
  }
  calls = 0;
  const joined = context.WXSeams.compile({
    forms: [
      { ...first, join_end: "joint" },
      { ...first, join_start: "joint", position: [0, 1, 0] },
    ],
  });
  assert.ok(calls > 0);
  assert.equal(joined.report.length, 1);
  assert.equal(joined.report[0].max_output_gap, 0);
});
