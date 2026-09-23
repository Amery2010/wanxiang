/* Bounded memory + IndexedDB cache. A failed persistence operation never turns
 * a valid export into a failed build. Buffers are cloned before transferring. */
import type { RuntimeData, RuntimeSpec, BuildResult } from "./types.js";
type Payload = Omit<BuildResult, "buffer">;
export interface CacheRow {
  key: string;
  asset?: string;
  spec: RuntimeSpec;
  mode: string;
  context: string;
  buffer: ArrayBuffer;
  bytes: number;
  lastUsed: number;
  sha256: string;
  payload: Payload;
}
type Metadata = Omit<CacheRow, "buffer" | "payload" | "sha256">;
interface Receipt {
  key: string;
  time: number;
}
const clone = <V>(x: V): V => structuredClone(x);
export const canonical = (v: unknown): unknown =>
  Array.isArray(v)
    ? v.map(canonical)
    : v && typeof v === "object"
      ? Object.fromEntries(
          Object.keys(v)
            .sort()
            .map((k) => [k, canonical((v as Record<string, unknown>)[k])]),
        )
      : Object.is(v, -0)
        ? 0
        : v;
export const json = (x: unknown): string => JSON.stringify(canonical(x));
const enc = (x: unknown) => new TextEncoder().encode(json(x));
const errorName = (e: unknown) => (e instanceof Error ? e.name : String(e));
export class Cache {
  data: RuntimeData;
  hash: (bytes: Uint8Array) => string;
  memory: Map<string, CacheRow>;
  memoryBudget: number;
  diskBudget: number;
  disabled: boolean;
  reason: string;
  hits: { memory: number; disk: number; miss: number };
  openPromise: Promise<IDBDatabase | null> | null;
  exported: Map<string, number>;

  constructor(
    data: RuntimeData,
    hash: (bytes: Uint8Array) => string,
    { memoryBudget = 32 * 1024 * 1024, diskBudget = 128 * 1024 * 1024 } = {},
  ) {
    this.data = data;
    this.hash = hash;
    this.memory = new Map();
    this.memoryBudget = memoryBudget;
    this.diskBudget = diskBudget;
    this.disabled = false;
    this.reason = "";
    this.hits = { memory: 0, disk: 0, miss: 0 };
    this.openPromise = null;
    this.exported = new Map();
  }
  context() {
    return {
      ...(this.data.build_context as Record<string, unknown> | undefined),
      exporter: "three-r186-GLTFExporter",
      cache_schema: "wx.asset-build-key/1.0",
    };
  }
  key(spec: RuntimeSpec, mode = "author") {
    const sources: Record<string, unknown> = {},
      visiting = new Set<string>(),
      add = (kind: "part" | "assembly", id: string | undefined): void => {
        if (!id) return;
        const k = kind + ":" + id;
        if (visiting.has(k)) throw Error("Cyclic cache dependency");
        if (k in sources) return;
        const d = (kind === "part" ? this.data.parts : this.data.assemblies)?.[
          id
        ];
        sources[k] = d || { missing: true };
        if (!d) return;
        visiting.add(k);
        for (const c of (kind === "part"
          ? this.data.parts?.[id]?.shape_params?.components
          : d.instances) || [])
          add(
            c.part ? "part" : "assembly",
            c.part || ("assembly" in c ? c.assembly : undefined),
          );
        if (this.data.motions?.[id])
          sources["motion:" + id] = this.data.motions?.[id];
        visiting.delete(k);
      };
    if (spec.part) add("part", spec.part);
    for (const c of spec.instances || [])
      add(
        c.part ? "part" : "assembly",
        c.part || ("assembly" in c ? c.assembly : undefined),
      );
    if (this.data.motions?.[spec.id || ""])
      sources["motion:" + spec.id] = this.data.motions?.[spec.id || ""];
    return this.hash(
      enc({
        schema: "wx.asset-build-key/1.0",
        context: this.context(),
        sources,
        spec,
        mode,
      }),
    );
  }
  async db(): Promise<IDBDatabase | null> {
    if (this.disabled) return null;
    if (this.openPromise) return this.openPromise;
    this.openPromise = new Promise<IDBDatabase | null>((resolve) => {
      let req: IDBOpenDBRequest,
        done = false;
      const finish = (db: IDBDatabase | null) => {
          if (done) {
            db?.close();
            return;
          }
          done = true;
          clearTimeout(timer);
          resolve(db);
        },
        timer = setTimeout(() => {
          this.disabled = true;
          this.reason = "数据库打开超时";
          finish(null);
        }, 2000);
      try {
        req = indexedDB.open("wanxiang-on-demand-v1", 2);
        req.onupgradeneeded = () => {
          for (const n of ["assets", "asset-meta", "receipts"])
            if (!req.result.objectStoreNames.contains(n))
              req.result.createObjectStore(n, { keyPath: "key" });
        };
        req.onsuccess = () => {
          const db = req.result;
          db.onversionchange = () => {
            db.close();
            this.disabled = true;
            this.reason = "数据库版本已变更";
          };
          finish(db);
        };
        req.onerror = () => {
          this.disabled = true;
          this.reason = req.error?.name || "本地存储不可用";
          finish(null);
        };
        req.onblocked = () => {
          this.reason = "数据库被其他标签页占用";
        };
      } catch (e) {
        this.disabled = true;
        this.reason = errorName(e);
        finish(null);
      }
    });
    return this.openPromise;
  }
  async transaction<V>(
    store: string,
    mode: IDBTransactionMode,
    fn: (store: IDBObjectStore) => IDBRequest<V>,
  ): Promise<V | null> {
    const db = await this.db();
    if (!db) return null;
    return new Promise((resolve, reject) => {
      try {
        const tx = db.transaction(store, mode),
          req = fn(tx.objectStore(store));
        let result: V | null = null;
        req.onsuccess = () => {
          result = req.result;
        };
        tx.oncomplete = () => resolve(result);
        tx.onerror = () => reject(tx.error || Error("IndexedDB error"));
        tx.onabort = () => reject(tx.error || Error("IndexedDB aborted"));
      } catch (e) {
        reject(e);
      }
    });
  }
  remember(row: CacheRow) {
    if (row.bytes > this.memoryBudget) return;
    this.memory.delete(row.key);
    this.memory.set(row.key, clone(row));
    let size = [...this.memory.values()].reduce((n, r) => n + r.bytes, 0);
    for (const [k, r] of this.memory) {
      if (size <= this.memoryBudget) break;
      this.memory.delete(k);
      size -= r.bytes;
    }
  }
  async get(key: string) {
    let row: CacheRow | null | undefined = this.memory.get(key),
      source: "memory" | "disk" = "memory";
    try {
      if (!row) {
        row = await this.transaction<CacheRow>("assets", "readonly", (s) =>
          s.get(key),
        );
        source = "disk";
      }
    } catch (e) {
      this.reason = errorName(e);
    }
    if (!row) {
      this.hits.miss++;
      return null;
    }
    if (
      !(row.buffer instanceof ArrayBuffer) ||
      row.sha256 !== this.hash(new Uint8Array(row.buffer))
    ) {
      await this.remove(key);
      this.hits.miss++;
      return null;
    }
    row.lastUsed = Date.now();
    this.remember(row);
    if (source === "disk")
      this.transaction("asset-meta", "readwrite", (s) =>
        s.put(this.metadata(row)),
      ).catch(() => {});
    this.hits[source]++;
    return { ...clone(row), cacheSource: source };
  }
  async put(
    key: string,
    spec: RuntimeSpec,
    buffer: ArrayBuffer,
    payload: Payload,
  ) {
    const row = {
      key,
      asset: spec.id || spec.part,
      spec: clone(spec),
      mode: "author",
      context: json(this.context()),
      buffer: buffer.slice(0),
      bytes: buffer.byteLength,
      lastUsed: Date.now(),
      sha256: this.hash(new Uint8Array(buffer)),
      payload: clone(payload),
    };
    this.remember(row);
    try {
      await this.prune(row.bytes);
      await this.storeRow(row);
    } catch (e) {
      this.reason = errorName(e);
      try {
        await this.prune(this.diskBudget / 2);
        await this.storeRow(row);
      } catch {
        this.disabled = true;
        this.reason = "持久缓存不可写，已退回内存缓存";
      }
    }
    return row;
  }
  metadata(row: CacheRow) {
    const {
      buffer: _buffer,
      payload: _payload,
      sha256: _sha256,
      ...meta
    } = row;
    return meta;
  }
  async storeRow(row: CacheRow) {
    const db = await this.db();
    if (!db || row.bytes > this.diskBudget) return;
    return new Promise<void>((resolve, reject) => {
      const tx = db.transaction(["assets", "asset-meta"], "readwrite");
      tx.objectStore("assets").put(row);
      tx.objectStore("asset-meta").put(this.metadata(row));
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });
  }
  async diskRows(): Promise<Metadata[]> {
    try {
      return (
        (await this.transaction<Metadata[]>("asset-meta", "readonly", (s) =>
          s.getAll(),
        )) || []
      );
    } catch (e) {
      this.reason = errorName(e);
      return [];
    }
  }
  async prune(incoming = 0) {
    const rows = await this.diskRows();
    let total = rows.reduce((n, r) => n + r.bytes, 0);
    for (const r of rows.sort((a, b) => a.lastUsed - b.lastUsed)) {
      if (total + incoming <= this.diskBudget) break;
      await this.remove(r.key);
      total -= r.bytes;
    }
  }
  async remove(key: string) {
    this.memory.delete(key);
    try {
      await this.transaction("assets", "readwrite", (s) => s.delete(key));
      await this.transaction("asset-meta", "readwrite", (s) => s.delete(key));
    } catch {
      /* Persistence is best effort. */
    }
  }
  async clean({
    asset,
    stale = false,
  }: { asset?: string; stale?: boolean } = {}) {
    const rows = new Map(
      [...(await this.diskRows()), ...this.memory.values()].map((r) => [
        r.key,
        r,
      ]),
    );
    let count = 0;
    for (const r of rows.values()) {
      if (asset && r.asset !== asset) continue;
      if (
        stale &&
        r.context === json(this.context()) &&
        r.key === this.key(r.spec, r.mode)
      )
        continue;
      await this.remove(r.key);
      count++;
    }
    return count;
  }
  async stats() {
    const disk = await this.diskRows(),
      mem = [...this.memory.values()];
    return {
      mode: this.disabled ? "memory" : "IndexedDB + memory",
      reason: this.reason,
      memory_entries: mem.length,
      memory_bytes: mem.reduce((n, r) => n + r.bytes, 0),
      disk_entries: disk.length,
      disk_bytes: disk.reduce((n, r) => n + r.bytes, 0),
      memory_budget: this.memoryBudget,
      disk_budget: this.diskBudget,
      hits: { ...this.hits },
    };
  }
  async wasExported(key: string) {
    if (this.exported.has(key)) return true;
    try {
      return !!(await this.transaction("receipts", "readonly", (s) =>
        s.get(key),
      ));
    } catch {
      return false;
    }
  }
  async markExported(key: string) {
    this.exported.set(key, Date.now());
    while (this.exported.size > 1024)
      this.exported.delete(this.exported.keys().next().value!);
    try {
      await this.transaction("receipts", "readwrite", (s) =>
        s.put({ key, time: Date.now() }),
      );
      const rows =
        (await this.transaction<Receipt[]>("receipts", "readonly", (s) =>
          s.getAll(),
        )) || [];
      for (const r of rows.sort((a, b) => b.time - a.time).slice(1024))
        await this.transaction("receipts", "readwrite", (s) => s.delete(r.key));
    } catch {
      /* Persistence is best effort. */
    }
  }
}
export default { Cache, canonical, json };
