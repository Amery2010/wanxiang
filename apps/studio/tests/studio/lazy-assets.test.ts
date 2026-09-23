import { afterEach, beforeAll, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { createStudioStore } from "../../src/studio/store";
import { createSession } from "../../src/studio/session";
import type { Asset, Data, Runtime, Spec } from "../../src/studio/types";
import type { LoadAsset } from "../../src/studio/asset-loader";
const require = createRequire(import.meta.url);
beforeAll(() => {
  require("@wanxiang/runtime/studio-core");
  require("@wanxiang/runtime/scene-document");
});
afterEach(() => vi.unstubAllGlobals());
const metadata: Asset[] = ["chair", "table", "room"].map((id) => ({
  id,
  dynamic: true,
  level: id === "room" ? 4 : 3,
}));
function patch(id: string): Data {
  const kit: Spec = {
    id,
    schema: "wx.assembly/1.0",
    instances: id === "room" ? [{ id: "seat", assembly: "chair" }] : [],
  };
  return {
    assets: [{ ...metadata.find((a) => a.id === id)!, kit }],
    assemblies: {
      [id]: kit,
      ...(id === "room" ? { chair: { id: "chair", instances: [] } } : {}),
    },
    parts: {},
  };
}
function setup(load: LoadAsset = vi.fn(async (id) => patch(id))) {
  const store = createStudioStore({
    assets: metadata.map((a) => ({ ...a })),
    parts: {},
    assemblies: {},
  });
  const runtime = {
    prepare: vi.fn(async (asset: Asset, spec?: Spec) => ({
      asset: { ...asset, kit: spec, glb: btoa("binary") },
      token: Symbol(),
    })),
    commit: vi.fn(),
    discard: vi.fn(),
    mergeDefinitions: vi.fn(),
    runtimeSidecar: vi.fn(() => ({})),
  } as unknown as Runtime;
  return { store, runtime, load, session: createSession(store, runtime, load) };
}
it("loads only a selected asset, then reuses its config", async () => {
  const { session, load, store } = setup();
  expect(load).not.toHaveBeenCalled();
  expect(store.getState().current).toBeNull();
  await session.select(metadata[0]);
  await session.select(metadata[0]);
  expect(load).toHaveBeenCalledTimes(1);
  expect(vi.mocked(load).mock.calls[0][0]).toBe("chair");
  expect(store.getState().spec?.id).toBe("chair");
});
it("ignores a late click, aborts unused requests and retries configuration failures", async () => {
  let finish!: (data: Data) => void;
  const load = vi
    .fn<LoadAsset>()
    .mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    )
    .mockRejectedValueOnce(Error("offline"))
    .mockImplementation(async (id) => patch(id));
  const { session, store, runtime } = setup(load);
  const old = session.select(metadata[0]);
  expect(await session.select(metadata[1])).toBe(false);
  expect(store.getState().error).toBe("offline");
  expect(await session.select(metadata[1])).toBe(true);
  finish(patch("chair"));
  expect(await old).toBe(false);
  expect(load.mock.calls[0][1]?.aborted).toBe(true);
  expect(store.getState().current?.id).toBe("table");
  expect(runtime.commit).toHaveBeenCalledTimes(1);
});
it("deduplicates concurrent selections of the same model", async () => {
  let finish!: (data: Data) => void;
  const load = vi.fn<LoadAsset>(
    () =>
      new Promise((resolve) => {
        finish = resolve;
      }),
  );
  const { session, runtime } = setup(load);
  const a = session.select(metadata[0]);
  const b = session.select(metadata[0]);
  finish(patch("chair"));
  expect(await a).toBe(false);
  expect(await b).toBe(true);
  expect(load).toHaveBeenCalledTimes(1);
  expect(runtime.commit).toHaveBeenCalledTimes(1);
});
it("loads scene closure and new references before validation, without changing selection", async () => {
  const { session, load, store } = setup();
  expect(await session.select(metadata[2])).toBe(true);
  expect(load).toHaveBeenCalledTimes(1);
  expect(await session.command({ type: "add", ref: "table" })).toBe(true);
  expect(store.getState().spec?.instances).toHaveLength(2);
  expect(store.getState().current?.id).toBe("room");
  expect(load).toHaveBeenCalledTimes(2);
  // A dependency definition is not a full root catalogue configuration.
  await session.select(metadata[0]);
  expect(load).toHaveBeenCalledTimes(3);
});
it("loads source imports and template configs on demand", async () => {
  const { session, store, load } = setup();
  expect(await session.newScene("我的房间", "room")).toBe(true);
  expect(load).toHaveBeenCalledTimes(1);
  const spec = {
    ...store.getState().spec!,
    instances: [{ id: "new", assembly: "table" }],
  };
  expect(await session.apply(spec)).toBe(true);
  expect(load).toHaveBeenCalledTimes(2);
});
it("loads batch metadata before constructing source exports", async () => {
  const { session, store, load, runtime } = setup();
  const url = vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:test");
  vi.stubGlobal("document", { createElement: () => ({ click: vi.fn() }) });
  vi.stubGlobal("setTimeout", () => 0);
  store.setState({ batch: ["chair", "table"] });
  await session.exportBatch();
  expect(load).toHaveBeenCalledTimes(2);
  expect(runtime.prepare).toHaveBeenCalledTimes(2);
  expect(
    vi.mocked(runtime.prepare).mock.calls.map((call) => call[1]?.id),
  ).toEqual(["chair", "table"]);
  expect(store.getState().current).toBeNull();
  url.mockRestore();
});

it("updates session interface definitions as lazy assets arrive", async () => {
  const { session, store, runtime } = setup(async (id) => ({
    ...patch(id),
    interfaces: { [id]: { version: 1 } },
  }));
  await session.select(metadata[0]);
  expect(store.getState().data.interfaces).toEqual({ chair: { version: 1 } });
  await session.select(metadata[1]);
  expect(store.getState().data.interfaces).toEqual({ table: { version: 1 } });
  expect(runtime.mergeDefinitions).toHaveBeenLastCalledWith(
    expect.objectContaining({ interfaces: { table: { version: 1 } } }),
  );
});
