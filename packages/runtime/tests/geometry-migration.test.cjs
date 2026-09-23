"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const { runInNewContext } = require("node:vm");
const sources = require("@wanxiang/runtime/sources");

// Captured from the original JavaScript kernel before the TypeScript migration.
// Hash all arrays and anatomy, not just vertex counts, to detect numeric drift.
const expected = [
  "c7a92ddba9c86fe26d7d39691c14143dd4b0852a431fb95d31a330230721d1a9",
  "dfdd532cadf3111b515f9b78dd6f3018f3bd8df100349c67c4e9fdb2669992ba",
  "389d0305cd86fc21224501d0a312cca4ec67f1b4bb69cc4f1c7675860484f470",
  "b03b2dc95199d7c772ecd8c1795901e2af040f95a40948c728f1da659e5e3839",
  "272f2adc9dde008c0c76681381f5bae83c721607cc70cbe5af6d740e18a1f7e1",
  "f4e1e872aa61f6b8cd9cce78d92cd33b3a1a4f2a4b27650bab73efe29d67b052",
  "df7946d1e28b19e376c5cc96225c18d803fff0d16ce731b20bf3e7a90bd7a6ba",
  "45b655a9dec33eb60f216a300cfb473f79f23f03fadeb4ed8dda1f0edcd299f4",
  "7d3148fbba4603c9d663104b9e3768dbc9ad1b954291597d184b07f2b5a0f140",
  "34d9e2c6930caf2f1d086f9e4d11ad276a3d1b6ccb809d49d8182724040d48e6",
  "2eb405d3196e0f12ba5650986df04d29297aa1c1f5c515472ff781689287cdc8",
  "041fc3976de588ddf08ae0469f7b48e5a4a079d865861d0d1adb85548d1be894",
];
const forms = [
  { kind: "bevelbox", size: [1, 0.7, 0.9], bevel: 0.08, color: "#a87132" },
  {
    kind: "loft",
    rings: [
      { c: [0, 0, 0], r: [0.3, 0.2] },
      { c: [0.1, 0.7, 0.2], r: [0.2, 0.15] },
      { c: [0.2, 1, 0.3], r: [0.1, 0.1] },
    ],
    sides: 8,
    color: "#349abc",
  },
  {
    kind: "lathe",
    profile: [
      [0, 0],
      [0.4, 0],
      [0.3, 0.6],
      [0, 0.7],
    ],
    sides: 8,
    color: "#112233",
  },
  {
    kind: "extrude",
    outline: [
      [0, 0],
      [1, 0],
      [1, 0.4],
      [0.4, 0.4],
      [0.4, 1],
      [0, 1],
    ],
    depth: 0.2,
    color: "#ccaa88",
  },
];

test("geometry migration preserves authored geometry across all three styles", () => {
  const context = {};
  context.window = context;
  runInNewContext(sources.browserSource(), context);
  let index = 0;
  for (const form of forms)
    for (const style of ["lowpoly", "toon", "voxel"]) {
      const geometry = context.WXGeometry.part(
        {
          id: "test.numeric",
          shape: "faceted",
          size: [1, 1, 1],
          shape_params: { forms: [form] },
        },
        style,
      );
      try {
        const result = context.WXGeometry.arrays(geometry);
        assert.equal(
          createHash("sha256").update(JSON.stringify(result)).digest("hex"),
          expected[index++],
          `${form.kind}/${style}`,
        );
      } finally {
        geometry.dispose();
      }
    }
});
