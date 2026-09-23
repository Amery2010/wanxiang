"use strict";
import readline from "node:readline";
import Geometry from "../../src/geometry.js";
import type { Part, Parameters } from "../../src/types.js";
import type { BufferGeometry } from "three";
interface Request {
  definition: Part;
  style?: string;
  params?: Parameters;
  registry?: Record<string, Part>;
}
// This legacy worker deliberately omits connection-contract validation.
const rl = readline.createInterface({
  input: process.stdin,
  crlfDelay: Infinity,
});
rl.on("line", (line) => {
  let geometry: BufferGeometry | undefined;
  try {
    if (Buffer.byteLength(line, "utf8") > 4 * 1024 * 1024)
      throw Error("REQUEST_BUDGET: 4 MiB");
    const d = JSON.parse(line) as Request;
    geometry = Geometry.part(
      d.definition,
      d.style,
      d.params,
      d.registry || {},
      null,
    );
    const result = Geometry.arrays(geometry);
    process.stdout.write(JSON.stringify({ ok: true, result }) + "\n");
  } catch (e) {
    process.stdout.write(
      JSON.stringify({
        ok: false,
        error: String(e instanceof Error ? e.message : e).slice(0, 1000),
      }) + "\n",
    );
  } finally {
    geometry?.dispose();
  }
});
process.stdin.on("error", () => process.exit(0));
process.stdout.on("error", () => process.exit(0));
