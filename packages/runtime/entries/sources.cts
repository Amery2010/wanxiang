import { readFileSync } from "node:fs";
import { join } from "node:path";

export interface SourceManifest {
  schema: number;
  vendor: string;
  kernel: string[];
  browser: string[];
  worker: string;
  nodeWorkers: { geometry: string; liveGeometry: string };
}

// This entry is bundled into the root of the compatibility resource tree.
export const manifest: SourceManifest = JSON.parse(
  readFileSync(join(__dirname, "source-manifest.json"), "utf8"),
);
export function sourcePath(relative: string): string {
  return join(__dirname, relative);
}
export function readSources(paths: string[]): string {
  return paths.map((file) => readFileSync(sourcePath(file), "utf8")).join("\n");
}
export function workerSource(): string {
  // The worker is self-contained, compiled from the same TypeScript modules.
  return readSources([manifest.worker]);
}
export function browserSource(): string {
  return (
    readSources([manifest.vendor, ...manifest.kernel, ...manifest.browser]) +
    "\nwindow.WX_WORKER_SOURCE=" +
    JSON.stringify(workerSource()).replaceAll("<", "\\u003c") +
    ";"
  );
}
