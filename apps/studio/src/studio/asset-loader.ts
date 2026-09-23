import type { Data, Asset, Spec } from "./types";
import type { StudioStore } from "./store";

export type LoadAsset = (id: string, signal?: AbortSignal) => Promise<Data>;
const cancelled = () => new DOMException("Cancelled", "AbortError");
/** Shared requests outlive individual consumers, but stop when nobody needs them. */
export function createAssetLoader(
  store: StudioStore,
  load: LoadAsset,
  merge: (patch: Data) => void,
) {
  const pending = new Map<
    string,
    { controller: AbortController; promise: Promise<void>; users: number }
  >();
  let disposed = false;
  function available(id: string, root = false) {
    const data = store.getState().data;
    return !!(
      (!root && (data.parts?.[id] || data.assemblies?.[id])) ||
      data.assets.find((a) => a.id === id && (a.kit || a.glb))
    );
  }
  async function ensure(
    id: string,
    signal?: AbortSignal,
    root = false,
  ): Promise<void> {
    if (disposed || signal?.aborted) throw cancelled();
    if (available(id, root)) return;
    if (!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$/.test(id) || id.includes(".."))
      throw Error("无效的资产引用");
    let job = pending.get(id);
    if (job?.controller.signal.aborted) job = undefined;
    if (!job) {
      const controller = new AbortController();
      const next = { controller, users: 0, promise: Promise.resolve() };
      next.promise = load(id, controller.signal)
        .then((patch) => {
          if (disposed || controller.signal.aborted) throw cancelled();
          merge(patch);
          if (!available(id)) throw Error(`资产配置缺少引用：${id}`);
        })
        .finally(() => {
          if (pending.get(id) === next) pending.delete(id);
        });
      pending.set(id, next);
      job = next;
    }
    const shared = job;
    shared.users++;
    try {
      await new Promise<void>((resolve, reject) => {
        const stop = () => {
          signal?.removeEventListener("abort", stop);
          reject(cancelled());
        };
        signal?.addEventListener("abort", stop, { once: true });
        shared.promise.then(
          () => {
            signal?.removeEventListener("abort", stop);
            resolve();
          },
          (error) => {
            signal?.removeEventListener("abort", stop);
            reject(error);
          },
        );
      });
      if (disposed || signal?.aborted) throw cancelled();
      if (!available(id, root)) throw Error(`资产配置不完整：${id}`);
    } finally {
      shared.users--;
      queueMicrotask(() => {
        if (!shared.users && pending.get(id) === shared)
          shared.controller.abort();
      });
    }
  }
  async function references(value: unknown, signal?: AbortSignal) {
    const ids = new Set<string>();
    function walk(node: unknown, depth = 0) {
      if (depth > 48) throw Error("资产配置结构过深");
      if (!node || typeof node !== "object") return;
      if (Array.isArray(node)) {
        for (const item of node) walk(item, depth + 1);
        return;
      }
      for (const [key, item] of Object.entries(node)) {
        if (
          ["part", "assembly", "ref"].includes(key) &&
          typeof item === "string"
        )
          ids.add(item);
        else if (typeof item === "object") walk(item, depth + 1);
      }
    }
    walk(value);
    // Keep imported recipes bounded and avoid flooding the local server.
    for (const id of ids) await ensure(id, signal);
  }
  return {
    ensure,
    references,
    async asset(asset: Asset, spec?: Spec, signal?: AbortSignal) {
      if (!asset.kit && !asset.glb && !spec)
        await ensure(asset.id, signal, true);
      const full = store.getState().data.assets.find((a) => a.id === asset.id);
      const result = asset.kit || asset.glb ? asset : { ...asset, ...full };
      await references(spec || result.kit, signal);
      return result;
    },
    dispose() {
      disposed = true;
      for (const job of pending.values()) job.controller.abort();
      pending.clear();
    },
  };
}
