import BuildExport from "@wanxiang/runtime/modules/build-export";
import { createRequire } from "node:module";
import { describe, it, expect, vi, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import type {
  RuntimeGlobals,
  BuildResult,
  RuntimeSpec,
  ThreeGlobal,
  RuntimeAsset,
} from "../../src/runtime/types";
import { createStudioRuntime } from "../../src/runtime";
import {
  sha256Bytes,
  from64,
  to64,
  zipStore,
  closedManifest,
} from "../../src/runtime/archive";
import {
  cpuRaster,
  prepareCPUShadows,
  type CPUData,
} from "../../src/runtime/cpu";
const require = createRequire(import.meta.url);
let T: ThreeGlobal;
beforeAll(() => {
  const context: { THREE?: ThreeGlobal } = {};
  runInNewContext(
    readFileSync(
      require.resolve("@wanxiang/runtime/vendor/three-0.186.0-with-addons.global.js"),
      "utf8",
    ),
    context,
  );
  T = context.THREE!;
});
function fixture() {
  const roots: GLTF[] = [];
  const load = vi.fn(async (_buffer?: ArrayBuffer) => {
    void _buffer;
    const scene = new T.Group();
    const result = {
      scene,
      scenes: [scene],
      animations: [],
      cameras: [],
      asset: { version: "2.0" },
      parser: { associations: new Map(), json: { nodes: [] } },
      userData: {},
    } as unknown as GLTF;
    roots.push(result);
    return result;
  });
  const dispose = vi.fn();
  const globals: RuntimeGlobals = {
    THREE: T,
    WXPipeline: {
      inspect: () => ({ doc: { nodes: [] } }),
      prepare: () => ({ inspection: { doc: { nodes: [] } }, load }),
      load,
      dispose,
    },
  };
  const asset: RuntimeAsset = {
    id: "example",
    glb: to64(new Uint8Array([1, 2, 3]).buffer),
    report: { triangles: 0 },
  };
  const runtime = createStudioRuntime({ assets: [asset] }, {}, globals);
  return { runtime, asset, load, dispose, roots, globals };
}
describe("runtime prepare / commit ownership", () => {
  it("keeps source assets immutable and commits a model only once", async () => {
    const f = fixture(),
      before = JSON.stringify(f.asset),
      prepared = await f.runtime.prepare(f.asset);
    expect(f.runtime.getModel()).toBeNull();
    expect(JSON.stringify(f.asset)).toBe(before);
    f.runtime.commit(prepared);
    expect(f.runtime.getModel()).toBe(f.roots[0].scene);
    expect(() => f.runtime.commit(prepared)).toThrow("no longer available");
    f.runtime.dispose();
    expect(f.dispose).toHaveBeenCalledWith(f.roots[0].scene);
  });
  it("retains the last committed model if the replacement fails to decode", async () => {
    const f = fixture();
    f.runtime.commit(await f.runtime.prepare(f.asset));
    const old = f.runtime.getModel();
    f.load.mockRejectedValueOnce(Error("corrupt GLB"));
    await expect(
      f.runtime.prepare({ ...f.asset, id: "broken" }),
    ).rejects.toThrow("corrupt");
    expect(f.runtime.getModel()).toBe(old);
    expect(f.dispose).not.toHaveBeenCalled();
    f.runtime.dispose();
  });
  it("discards stale prepared models without replacing the current asset", async () => {
    const f = fixture();
    const stale = await f.runtime.prepare(f.asset);
    const active = await f.runtime.prepare({ ...f.asset, id: "active" });
    f.runtime.commit(active);
    f.runtime.discard(stale);
    f.runtime.discard(stale);
    expect(f.runtime.snapshot()?.id).toBe("active");
    expect(
      f.dispose.mock.calls.filter(([root]) => root === f.roots[0].scene),
    ).toHaveLength(1);
    f.runtime.dispose();
  });
  it("aborts a pending decode and releases its eventual model", async () => {
    const f = fixture(),
      controller = new AbortController();
    let finish!: (value: GLTF) => void;
    const decoded = await f.load();
    f.load.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const pending = f.runtime.prepare(f.asset, undefined, controller.signal);
    controller.abort();
    finish(decoded);
    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
    expect(f.dispose).toHaveBeenCalledWith(decoded.scene);
    expect(f.runtime.getModel()).toBeNull();
    f.runtime.dispose();
  });
  it("releases in-flight decode after runtime disposal", async () => {
    const f = fixture();
    let finish!: (value: GLTF) => void;
    const decoded = await f.load();
    f.load.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const pending = f.runtime.prepare(f.asset);
    f.runtime.dispose();
    finish(decoded);
    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
    expect(f.dispose).toHaveBeenCalledWith(decoded.scene);
  });
  it("ordinary export uses immutable GLB bytes after presentation changes", async () => {
    const f = fixture();
    f.runtime.commit(await f.runtime.prepare(f.asset));
    f.runtime.getModel()!.position.set(100, 100, 100);
    f.runtime.setLighting("neutral");
    f.runtime.setWire(true);
    const buffer = await f.runtime.exportGLB();
    expect([...new Uint8Array(buffer)]).toEqual([1, 2, 3]);
    f.runtime.dispose();
  });
});
describe("offline byte helpers", () => {
  it("hashes SHA-256 without secure-context APIs and roundtrips binary", () => {
    const bytes = new TextEncoder().encode("abc");
    expect(sha256Bytes(bytes)).toBe(
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    );
    expect(from64(to64(bytes.buffer))).toEqual(bytes);
  });
  it("produces a ZIP with UTF-8 entries and a closed hash roster", async () => {
    const files: [string, string][] = [["模型.json", '{"a":1}']];
    const manifest = JSON.parse(closedManifest(files));
    expect(manifest.files["模型.json"].bytes).toBe(7);
    const blob = zipStore(files),
      buffer = await blob.arrayBuffer();
    expect(new DataView(buffer).getUint32(0, true)).toBe(0x04034b50);
    expect(new DataView(buffer).getUint16(6, true)).toBe(0x800);
    expect(blob.type).toBe("application/zip");
  });
});
describe("actual CPU geometry raster", () => {
  function triangle(): CPUData {
    return {
      vertices: new Float32Array([-1, 0, 0, 1, 0, 0, 0, 1, 0]),
      normals: new Float32Array([0, 0, 1, 0, 0, 1, 0, 0, 1]),
      uv: new Float32Array(6),
      colors: new Float32Array(9).fill(1),
      faces: new Uint32Array([0, 1, 2]),
      matids: new Uint16Array([0]),
      materials: [
        {
          style: "lowpoly",
          texture: new Uint8ClampedArray([255, 255, 255, 255]),
          size: 1,
          color: [1, 0.2, 0.1],
          emissive: [0, 0, 0],
          cutoff: 0.001,
          repeatS: false,
          repeatT: false,
        },
      ],
      center: [0, 0.5, 0],
      span: 3,
    };
  }
  it("draws actual triangle pixels and responds to view rotation", () => {
    const data = triangle(),
      opt = {
        width: 64,
        height: 64,
        az: 0,
        el: 0,
        zoom: 1,
        wire: false,
        lighting: "studio",
      },
      front = cpuRaster(data, opt),
      side = cpuRaster(data, { ...opt, az: 90 });
    expect(
      front.filter((_, i) => i % 4 === 3 && front[i] > 0).length,
    ).toBeGreaterThan(100);
    expect(side.filter((_, i) => i % 4 === 3 && side[i] > 0).length).toBe(0);
  });
  it("rasterizes a real shadow depth map and respects alpha masking", () => {
    const data = prepareCPUShadows(triangle());
    expect(data.shadow?.depth.some((value) => value > -1e20)).toBe(true);
    data.materials[0].texture[3] = 0;
    data.shadow = null;
    expect(
      cpuRaster(data, {
        width: 32,
        height: 32,
        az: 0,
        el: 0,
        zoom: 1,
        wire: false,
        lighting: "studio",
      }).every((value) => value === 0),
    ).toBe(true);
  });
});

describe("build cache and task adapter seam", () => {
  function dynamicFixture() {
    const f = fixture();
    f.runtime.dispose();
    const remove = vi.fn(async (_key: string) => {
        void _key;
      }),
      put = vi.fn(
        async (
          _key: string,
          _spec: RuntimeSpec,
          _buffer: ArrayBuffer,
          _payload: unknown,
        ) => {
          void [_key, _spec, _buffer, _payload];
        },
      ),
      build = vi.fn(async () => ({
        root: new T.Group(),
        bom: [],
        report: { triangles: 0 },
      }));
    const get = vi.fn(async () => ({
      buffer: new Uint8Array([0]).buffer,
      payload: { bom: [], report: { triangles: 0 } },
      cacheSource: "memory",
    }));
    const libraryParts: string[][] = [];
    const sharedData: unknown[] = [];
    class Library {
      constructor(data: { parts?: Record<string, unknown> }) {
        libraryParts.push(Object.keys(data.parts || {}));
      }
      build = build;
      clips() {
        return [];
      }
    }
    class Cache {
      constructor(data: unknown) {
        sharedData.push(data);
      }
      key() {
        return "source-sensitive-key";
      }
      get = get;
      put = put;
      remove = remove;
      async stats() {
        return {};
      }
      async clean() {
        return 0;
      }
      async markExported() {}
      async wasExported() {
        return false;
      }
    }
    class Tasks {
      constructor(
        _data: unknown,
        private mainBuild: (
          spec: RuntimeSpec,
          signal?: AbortSignal,
        ) => Promise<BuildResult>,
      ) {
        sharedData.push(_data);
      }
      submit(spec: Record<string, unknown>, options: { signal?: AbortSignal }) {
        return this.mainBuild(spec, options.signal);
      }
      cancel() {}
      cancelAll() {}
      snapshot() {
        return {};
      }
    }
    const Exporter = class {
      async parseAsync() {
        return new Uint8Array([1, 2, 3]).buffer;
      }
    } as unknown as ThreeGlobal["GLTFExporter"];
    const prepare = vi.fn((buffer: ArrayBuffer) => {
      if (new Uint8Array(buffer)[0] === 0) throw Error("invalid cached GLB");
      return {
        inspection: { doc: { nodes: [], materials: [] } },
        load: () => f.load(buffer),
      };
    });
    const globals: RuntimeGlobals = {
      ...f.globals,
      THREE: { ...T, GLTFExporter: Exporter },
      WXRuntime: { Library },
      WXBuildExport: BuildExport,
      WXBuildCache: { Cache },
      WXBuildTasks: {
        Tasks,
      },
      WXPipeline: {
        ...f.globals.WXPipeline,
        prepare,
      },
    };
    const asset = {
        ...f.asset,
        dynamic: true,
        kit: { id: f.asset.id, part: "part.example" },
      },
      runtime = createStudioRuntime(
        { assets: [asset], parts: {}, assemblies: {} },
        {},
        globals,
      );
    return {
      runtime,
      asset,
      get,
      put,
      remove,
      build,
      libraryParts,
      sharedData,
      prepare,
      load: f.load,
    };
  }
  it("refreshes snapshot definition maps while retaining task/cache data and the committed model", async () => {
    const f = dynamicFixture();
    const cache = f.runtime.cache,
      tasks = f.runtime.tasks;
    const prepared = await f.runtime.prepare(f.asset);
    f.runtime.commit(prepared);
    const current = f.runtime.snapshot();
    f.runtime.mergeDefinitions?.({
      assets: [],
      parts: { added: { id: "added" } },
      assemblies: {},
      motions: {},
    });
    expect(f.libraryParts).toEqual([[], ["added"]]);
    expect(f.sharedData[0]).toBe(f.sharedData[1]);
    expect(f.sharedData[0]).toMatchObject({
      parts: { added: { id: "added" } },
    });
    expect(f.runtime.cache).toBe(cache);
    expect(f.runtime.tasks).toBe(tasks);
    expect(f.runtime.snapshot()).toEqual(current);
    f.runtime.dispose();
  });
  it("invalid cache bytes are evicted and the task rebuild is validated before commit", async () => {
    const f = dynamicFixture(),
      original = JSON.stringify(f.asset);
    const prepared = await f.runtime.prepare(f.asset);
    expect(f.remove).toHaveBeenCalledWith("source-sensitive-key");
    expect(f.build).toHaveBeenCalledTimes(1);
    expect(f.put).toHaveBeenCalledTimes(1);
    expect(prepared.asset.cacheSource).toBe("generated");
    expect(JSON.stringify(f.asset)).toBe(original);
    f.runtime.commit(prepared);
    expect(f.runtime.snapshot()?.sha256).toBe(
      sha256Bytes(new Uint8Array([1, 2, 3])),
    );
    f.runtime.dispose();
  });
  it("loads valid cached bytes directly with one inspection and no build", async () => {
    const f = dynamicFixture();
    const buffer = new Uint8Array([4, 5, 6]).buffer;
    f.get.mockResolvedValueOnce({
      buffer,
      payload: { bom: [], report: { triangles: 0 } },
      cacheSource: "memory",
    });
    const prepared = await f.runtime.prepare(f.asset);
    expect(f.prepare).toHaveBeenCalledExactlyOnceWith(buffer);
    expect(f.load.mock.calls[0][0]).toBe(buffer);
    expect(prepared.asset.glb).toBe(to64(buffer));
    expect(f.build).not.toHaveBeenCalled();
    expect(f.remove).not.toHaveBeenCalled();
    f.runtime.discard(prepared);
    f.runtime.dispose();
  });
  it("inspects rebuilt bytes once after rejecting cache corruption", async () => {
    const f = dynamicFixture();
    const prepared = await f.runtime.prepare(f.asset);
    expect(f.prepare).toHaveBeenCalledTimes(2);
    const builtBuffer = f.prepare.mock.calls[1][0];
    expect(f.load.mock.calls[0][0]).toBe(builtBuffer);
    expect(f.put.mock.calls[0][2]).toBe(builtBuffer);
    f.runtime.discard(prepared);
    f.runtime.dispose();
  });
  it("cancellation while cache lookup is pending prevents subsequent geometry building", async () => {
    const f = dynamicFixture(),
      controller = new AbortController();
    let finish!: (result: Awaited<ReturnType<typeof f.get>>) => void;
    f.get.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const pending = f.runtime.prepare(f.asset, undefined, controller.signal);
    controller.abort();
    finish({
      buffer: new Uint8Array([0]).buffer,
      payload: { bom: [], report: { triangles: 0 } },
      cacheSource: "memory",
    });
    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
    expect(f.build).not.toHaveBeenCalled();
    expect(f.put).not.toHaveBeenCalled();
    f.runtime.dispose();
  });
});
