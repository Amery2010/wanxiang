import { createRequire } from "node:module";
import { performance } from "node:perf_hooks";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import type Pipeline from "../src/pipeline.js";

const require = createRequire(import.meta.url);
const pipeline = require("@wanxiang/runtime/pipeline") as typeof Pipeline;
const json = Buffer.from(
  JSON.stringify({
    asset: { version: "2.0" },
    extras: { padding: "x".repeat(1_000_000) },
  }),
);
const size = Math.ceil(json.length / 4) * 4;
const buffer = new ArrayBuffer(20 + size);
const view = new DataView(buffer);
view.setUint32(0, 0x46546c67, true);
view.setUint32(4, 2, true);
view.setUint32(8, buffer.byteLength, true);
view.setUint32(12, size, true);
view.setUint32(16, 0x4e4f534a, true);
const bytes = new Uint8Array(buffer, 20);
bytes.fill(32);
bytes.set(json);
let sink = 0;
function previousPreparation() {
  pipeline.inspect(buffer); // Cache acceptance or generated-result check.
  pipeline.inspect(buffer); // Report fields.
  const encoded = Buffer.from(buffer).toString("base64");
  const decoded = Uint8Array.from(Buffer.from(encoded, "base64")).buffer;
  pipeline.inspect(decoded); // Before load.
  pipeline.inspect(decoded); // Previous load's own validation.
  sink += encoded.length;
}
function currentPreparation() {
  const prepared = pipeline.prepare(buffer);
  const encoded = Buffer.from(buffer).toString("base64");
  sink += encoded.length + prepared.inspection.triangles;
}
function sample(operation: () => void) {
  for (let i = 0; i < 5; i++) operation();
  const runs = [];
  for (let round = 0; round < 7; round++) {
    const start = performance.now();
    for (let i = 0; i < 30; i++) operation();
    runs.push((performance.now() - start) / 30);
  }
  return runs.sort((a, b) => a - b)[3];
}
const report = {
  scope:
    "Node CPU preparation microbenchmark; excludes GLTF parsing, GPU, browser and real asset build time",
  node: process.version,
  bytes: buffer.byteLength,
  iterations: "5 warmups; median of 7 batches of 30",
  before: {
    inspections: 4,
    base64Encodes: 1,
    base64Decodes: 1,
    medianMs: sample(previousPreparation),
  },
  after: {
    inspections: 1,
    base64Encodes: 1,
    base64Decodes: 0,
    snapshotCopies: 1,
    medianMs: sample(currentPreparation),
  },
};
if (!sink) throw Error("Benchmark did not consume prepared data");
const folder = resolve(import.meta.dirname, "../../../generated/performance");
await mkdir(folder, { recursive: true });
await writeFile(
  resolve(folder, "runtime-preparation.json"),
  JSON.stringify(report, null, 2) + "\n",
);
console.log(JSON.stringify(report, null, 2));
