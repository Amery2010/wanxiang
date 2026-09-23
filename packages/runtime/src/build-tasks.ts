/* Bounded task queue, transferable binary results, cancellable dedicated jobs.
 * Workers are terminated on cancellation; tiny main-thread builds can only be
 * cancelled between phases. A denied Blob worker falls back explicitly. */
import type {
  RuntimeData,
  RuntimeSpec,
  BomEntry,
  BuildReport,
  RuntimeLibraryData,
} from "./types.js";
export interface TaskResult {
  buffer: ArrayBuffer;
  bom: BomEntry[];
  report: BuildReport;
  worker?: boolean;
}
export interface TaskStatus {
  id: number;
  asset?: string;
  phase: string;
  worker?: boolean;
  milliseconds?: number;
  bytes?: number;
  error?: string;
}
export interface TaskSnapshot {
  limit: number;
  queued: TaskStatus[];
  active: TaskStatus[];
  history: TaskStatus[];
}
export interface TaskOptions {
  asset?: string;
  level?: number;
  signal?: AbortSignal;
  forceWorker?: boolean;
}
interface Job extends TaskStatus {
  spec: RuntimeSpec;
  level: number;
  signal?: AbortSignal;
  forceWorker: boolean;
  resolve: (result: TaskResult) => void;
  reject: (error: unknown) => void;
  started: number;
  cancel: () => void;
  cancelled?: boolean;
  workerHandle?: Worker;
  workerReject?: (error: unknown) => void;
}
export type WorkerRequest =
  | { type: "init"; data: RuntimeLibraryData }
  | { type: "build"; id: number; spec: RuntimeSpec };
export type WorkerResponse =
  | { type: "ready" }
  | { type: "init-error"; error: string }
  | { type: "progress"; id: number; phase: string }
  | ({ type: "result"; id: number } & TaskResult)
  | { type: "error"; id: number; error: string };
const message = (e: unknown) => (e instanceof Error ? e.message : String(e));
const named = (e: unknown, name: string) =>
  e instanceof Error && e.name === name;
const abort = () => new DOMException("Cancelled", "AbortError");
export class Tasks {
  data: RuntimeData;
  mainBuild: (spec: RuntimeSpec, signal?: AbortSignal) => Promise<TaskResult>;
  onChange: (snapshot: TaskSnapshot) => void;
  limit: number;
  queue: Job[];
  active: Map<number, Job>;
  history: TaskStatus[];
  serial: number;
  workersAllowed: boolean;
  workerSource: () => string | undefined;

  constructor(
    data: RuntimeData,
    mainBuild: (spec: RuntimeSpec, signal?: AbortSignal) => Promise<TaskResult>,
    onChange: (snapshot: TaskSnapshot) => void = () => {},
    workerSource: () => string | undefined = () =>
      (globalThis as { WX_WORKER_SOURCE?: string }).WX_WORKER_SOURCE,
  ) {
    this.workerSource = workerSource;
    this.data = data;
    this.mainBuild = mainBuild;
    this.onChange = onChange;
    this.limit = 2;
    this.queue = [];
    this.active = new Map();
    this.history = [];
    this.serial = 0;
    this.workersAllowed = true;
  }
  setConcurrency(n: number) {
    this.limit = Math.max(1, Math.min(3, Math.floor(n) || 1));
    this.emit();
    this.pump();
  }
  emit() {
    this.onChange(this.snapshot());
  }
  snapshot(): TaskSnapshot {
    return {
      limit: this.limit,
      queued: this.queue.map((j) => ({
        id: j.id,
        asset: j.asset,
        phase: "queued",
      })),
      active: [...this.active.values()].map((j) => ({
        id: j.id,
        asset: j.asset,
        phase: j.phase,
        worker: !!j.workerHandle,
      })),
      history: this.history.slice(-16),
    };
  }
  submit(
    spec: RuntimeSpec,
    { asset, level = 1, signal, forceWorker = false }: TaskOptions = {},
  ): Promise<TaskResult> {
    return new Promise<TaskResult>((resolve, reject) => {
      const job: Job = {
        id: ++this.serial,
        spec: structuredClone(spec),
        asset: asset || spec.id,
        level,
        signal,
        forceWorker,
        resolve,
        reject,
        phase: "queued",
        started: performance.now(),
        cancel: () => {},
      };
      if (signal?.aborted) return reject(abort());
      job.cancel = () => this.cancel(job.id);
      signal?.addEventListener("abort", job.cancel, { once: true });
      this.queue.push(job);
      this.emit();
      this.pump();
    });
  }
  cancel(id: number) {
    const queued = this.queue.find((j) => j.id === id);
    if (queued) {
      this.queue = this.queue.filter((j) => j !== queued);
      queued.signal?.removeEventListener("abort", queued.cancel);
      queued.reject(abort());
      this.history.push({ id, asset: queued.asset, phase: "cancelled" });
      this.emit();
      return;
    }
    const job = this.active.get(id);
    if (job) {
      job.cancelled = true;
      job.workerHandle?.terminate();
      job.workerReject?.(abort());
      this.emit();
    }
  }
  cancelAll() {
    for (const j of [...this.queue, ...this.active.values()]) this.cancel(j.id);
  }
  pump() {
    while (this.active.size < this.limit && this.queue.length) {
      const job = this.queue.shift()!;
      this.active.set(job.id, job);
      this.run(job);
    }
  }
  async run(j: Job) {
    try {
      if (j.signal?.aborted || j.cancelled) throw abort();
      j.phase = "building";
      this.emit();
      let result;
      if (
        (j.level >= 3 || j.forceWorker) &&
        j.spec.style !== "voxel" &&
        this.workersAllowed &&
        this.workerSource()
      ) {
        try {
          result = await this.workerBuild(j);
        } catch (e) {
          if (named(e, "WorkerUnavailable")) {
            j.workerHandle?.terminate();
            j.workerHandle = undefined;
            this.workersAllowed = false;
            j.phase = "main-thread fallback";
            this.emit();
            result = await this.mainBuild(j.spec, j.signal);
          } else throw e;
        }
      } else result = await this.mainBuild(j.spec, j.signal);
      if (j.cancelled || j.signal?.aborted) throw abort();
      this.history.push({
        id: j.id,
        asset: j.asset,
        phase: "complete",
        milliseconds: performance.now() - j.started,
        bytes: result.buffer.byteLength,
        worker: result.worker === true,
      });
      j.resolve(result);
    } catch (e) {
      this.history.push({
        id: j.id,
        asset: j.asset,
        phase: named(e, "AbortError") ? "cancelled" : "failed",
        error: message(e),
      });
      j.reject(e);
    } finally {
      j.signal?.removeEventListener("abort", j.cancel);
      j.workerHandle?.terminate();
      this.active.delete(j.id);
      this.history = this.history.slice(-24);
      this.emit();
      this.pump();
    }
  }
  workerBuild(j: Job): Promise<TaskResult> {
    return new Promise((resolve, reject) => {
      let url: string | undefined,
        worker: Worker,
        ready = false;
      const unavailable = (m: string) =>
        Object.assign(Error(m), { name: "WorkerUnavailable" });
      try {
        url = URL.createObjectURL(
          new Blob([this.workerSource() || ""], { type: "text/javascript" }),
        );
        worker = new Worker(url);
        URL.revokeObjectURL(url);
        j.workerHandle = worker;
        j.workerReject = reject;
      } catch (e) {
        if (url) URL.revokeObjectURL(url);
        reject(unavailable(message(e)));
        return;
      }
      const timeout = setTimeout(() => {
        worker.terminate();
        reject(
          ready
            ? Error("Worker build timed out")
            : unavailable("Worker initialization timed out"),
        );
      }, 60000);
      const done = <V>(fn: (value: V) => void, v: V) => {
        clearTimeout(timeout);
        fn(v);
      };
      j.workerReject = (e) => done(reject, e);
      worker.onerror = (e) =>
        done(reject, ready ? Error(e.message) : unavailable(message(e)));
      worker.onmessage = (e) => {
        const m = e.data as WorkerResponse;
        if (m.type === "ready") {
          ready = true;
          worker.postMessage({
            type: "build",
            id: j.id,
            spec: j.spec,
          } satisfies WorkerRequest);
        } else if (m.type === "init-error") done(reject, unavailable(m.error));
        else if (m.type === "progress") {
          j.phase = m.phase;
          this.emit();
        } else if (m.type === "result")
          done(resolve, {
            buffer: m.buffer,
            bom: m.bom,
            report: m.report,
            worker: true,
          });
        else if (m.type === "error") done(reject, Error(m.error));
      };
      const {
        parts,
        assemblies,
        motions,
        materials,
        retired,
        interfaces,
        aliases,
      } = this.data;
      worker.postMessage({
        type: "init",
        data: {
          parts,
          assemblies,
          motions,
          materials,
          retired,
          interfaces,
          aliases,
        },
      } satisfies WorkerRequest);
    });
  }
}
export default { Tasks };
