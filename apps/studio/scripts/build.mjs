import { build } from "vite";
import { copyFile, mkdir, rename } from "node:fs/promises";
import { resolve } from "node:path";
const studio = resolve(import.meta.dirname, "..");
await build({ configFile: resolve(studio, "vite.config.mts") });
await mkdir(resolve(studio, "artifacts"), { recursive: true });
await copyFile(
  resolve(studio, "../../generated/frontend/build/app.js"),
  resolve(studio, "artifacts/app.js.pending"),
);
await rename(
  resolve(studio, "artifacts/app.js.pending"),
  resolve(studio, "artifacts/app.js"),
);
console.log("Updated Studio artifact: apps/studio/artifacts/app.js");
