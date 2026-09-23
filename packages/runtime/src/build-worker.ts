/* Dedicated offline worker; every job owns its geometry and export resources. */
import { Library } from "./runtime.js";
import { buildAndExport } from "./build-export.js";
import type { WorkerRequest, WorkerResponse } from "./build-tasks.js";
interface WorkerScope {
  onmessage: ((event: MessageEvent<WorkerRequest>) => void) | null;
  postMessage(message: WorkerResponse, transfer?: Transferable[]): void;
}
const scope = self as unknown as WorkerScope;
let library: Library | undefined;
const message = (error: unknown) =>
  error instanceof Error ? error.message : String(error);
scope.onmessage = async ({ data: m }) => {
  if (m.type === "init") {
    try {
      library = new Library(m.data);
      scope.postMessage({ type: "ready" });
    } catch (error) {
      scope.postMessage({ type: "init-error", error: message(error) });
    }
    return;
  }
  if (m.type !== "build") return;
  try {
    if (!library) throw Error("Worker has not been initialized");
    const result = await buildAndExport(library, m.spec, {
      noTextures: true,
      phase: (phase) =>
        scope.postMessage({ type: "progress", id: m.id, phase }),
    });
    scope.postMessage(
      {
        type: "result",
        id: m.id,
        buffer: result.glb,
        bom: result.bom,
        report: result.report,
      },
      [result.glb],
    );
  } catch (error) {
    scope.postMessage({ type: "error", id: m.id, error: message(error) });
  }
};
