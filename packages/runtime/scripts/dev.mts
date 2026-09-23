import { createServer } from "vite";
import { watch, type FSWatcher } from "node:fs";
import { spawn, type ChildProcess } from "node:child_process";
import { resolve } from "node:path";

const runtime = resolve(import.meta.dirname, "..");
let building: ChildProcess | undefined;
let closing = false;
function compile(): Promise<void> {
  return new Promise((resolveBuild, reject) => {
    const child = spawn(
      process.execPath,
      [resolve(runtime, "scripts/build.mts")],
      {
        stdio: "inherit",
      },
    );
    building = child;
    child.once("error", reject);
    child.once("exit", (code) => {
      building = undefined;
      if (code === 0) resolveBuild();
      else reject(new Error(`Runtime build exited with code ${code}`));
    });
  });
}
await compile();
const server = await createServer({
  configFile: resolve(runtime, "../../apps/studio/vite.config.mts"),
});
await server.listen();
server.printUrls();
let dirty = false;
let rebuilding = false;
let timer: ReturnType<typeof setTimeout> | undefined;
async function rebuild() {
  dirty = true;
  if (rebuilding || closing) return;
  rebuilding = true;
  try {
    while (dirty && !closing) {
      dirty = false;
      try {
        await compile();
        server.ws.send({ type: "full-reload" });
      } catch (error) {
        if (!closing) console.error(error);
      }
    }
  } finally {
    rebuilding = false;
  }
}
const watchers: FSWatcher[] = [];
for (const path of [
  "src",
  "workers",
  "entries",
  "scripts",
  "source-manifest.json",
  "tsconfig.json",
  "tsconfig.cjs.json",
  "tsconfig.esm.json",
]) {
  watchers.push(
    watch(
      resolve(runtime, path),
      { recursive: !path.endsWith(".json") },
      () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          void rebuild();
        }, 100);
      },
    ),
  );
}
async function close() {
  if (closing) return;
  closing = true;
  clearTimeout(timer);
  for (const watcher of watchers) watcher.close();
  building?.kill("SIGTERM");
  await server.close();
}
process.once("SIGINT", () => {
  void close();
});
process.once("SIGTERM", () => {
  void close();
});
