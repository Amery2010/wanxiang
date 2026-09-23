import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { createStudioStore } from "../../src/studio/store";
import { createSession } from "../../src/studio/session";
import type { Asset, Runtime, Spec } from "../../src/studio/types";
import type { PreparedAsset } from "../../src/runtime/types";
const require = createRequire(import.meta.url);
beforeAll(() => {
  require("@wanxiang/runtime/studio-core");
  require("@wanxiang/runtime/scene-document");
});
const asset: Asset = {
  id: "chair",
  name: "Chair",
  level: 3,
  kit: { id: "chair", style: "lowpoly" },
};
function setup() {
  const store = createStudioStore({ assets: [asset], parts: {} });
  const runtime = {
    prepare: vi.fn(async (a: Asset, spec?: Spec) => ({
      asset: { ...a, kit: spec },
      token: Symbol(),
    })),
    commit: vi.fn(),
    discard: vi.fn(),
  } as unknown as Runtime;
  return { store, runtime, session: createSession(store, runtime) };
}
describe("studio transaction", () => {
  beforeEach(() => vi.restoreAllMocks());
  it("keeps the previous asset and history when preparation fails", async () => {
    const { store, runtime, session } = setup();
    await session.select(asset);
    const current = store.getState().current;
    vi.mocked(runtime.prepare).mockRejectedValueOnce(Error("invalid geometry"));
    expect(await session.apply({ id: "bad" })).toBe(false);
    expect(store.getState().current).toBe(current);
    expect(store.getState().history).toEqual([]);
    expect(store.getState().spec).toEqual(asset.kit);
    expect(store.getState().busy).toBe(false);
  });
  it("does not commit a late asset selection", async () => {
    const { store, runtime, session } = setup();
    let finish!: (p: PreparedAsset) => void;
    vi.mocked(runtime.prepare).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const old = session.select(asset);
    const latest = { ...asset, id: "latest" };
    await session.select(latest);
    const prepared = { asset, token: Symbol() };
    finish(prepared);
    expect(await old).toBe(false);
    expect(runtime.discard).toHaveBeenCalledWith(prepared);
    expect(store.getState().current?.id).toBe("latest");
    expect(runtime.commit).toHaveBeenCalledTimes(1);
  });
  it("cancels without replacing the valid model", async () => {
    const { store, runtime, session } = setup();
    await session.select(asset);
    let finish!: (p: PreparedAsset) => void;
    vi.mocked(runtime.prepare).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const pending = session.apply({ id: "changed" });
    session.cancel();
    finish({ asset: { ...asset, id: "changed" }, token: Symbol() });
    expect(await pending).toBe(false);
    expect(store.getState().current?.id).toBe(asset.id);
    expect(store.getState().busy).toBe(false);
  });
  it("updates history only after runtime commit and supports undo and redo", async () => {
    const { store, runtime, session } = setup();
    await session.select(asset);
    const changed = { id: "chair", style: "toon" };
    vi.mocked(runtime.commit).mockImplementationOnce(() =>
      expect(store.getState().spec).toEqual(asset.kit),
    );
    await session.apply(changed);
    expect(store.getState().history).toEqual([asset.kit]);
    await session.undo();
    expect(store.getState().spec).toEqual(asset.kit);
    expect(store.getState().future).toEqual([changed]);
    await session.redo();
    expect(store.getState().spec).toEqual(changed);
    expect(store.getState().future).toEqual([]);
  });
  it("does not commit history when runtime commit throws", async () => {
    const { store, runtime, session } = setup();
    await session.select(asset);
    vi.mocked(runtime.commit).mockImplementationOnce(() => {
      throw Error("commit rejected");
    });
    expect(await session.apply({ id: "changed" })).toBe(false);
    expect(store.getState().spec).toEqual(asset.kit);
    expect(store.getState().history).toEqual([]);
  });
  it("maps the retired game expansion collection to the complete catalogue", () => {
    const { store } = setup();
    store.getState().setFilters({
      query: "chair",
      level: "4",
      domain: "interior",
      motion: "moving",
      page: 3,
    });
    store.getState().setFilters({ collection: "game410" });
    expect(store.getState().filters).toMatchObject({
      query: "",
      level: "all",
      domain: "all",
      motion: "all",
      page: 1,
      collection: "all",
    });
  });
  it("retains edited sources and history after visiting another asset", async () => {
    const { store, session } = setup();
    await session.select(asset);
    await session.apply({ id: "chair", style: "toon" });
    await session.select({ ...asset, id: "table" });
    await session.select(asset);
    expect(store.getState().spec?.style).toBe("toon");
    expect(store.getState().history).toHaveLength(1);
    expect(store.getState().dirty).toBe(true);
  });
  it("uses all levels for GLB review documents without an author catalog", () => {
    expect(
      createStudioStore({ assets: [{ id: "review", glb: "AA==" }] }).getState()
        .filters.level,
    ).toBe("all");
  });
});

it("rejects static review edits without changing the GLB or source", async () => {
  const { runtime } = setup();
  const store = createStudioStore({ assets: [asset] });
  store.setState({ current: asset, spec: asset.kit || null });
  const session = createSession(store, runtime);
  expect(await session.apply({ id: "chair", style: "toon" })).toBe(false);
  expect(runtime.prepare).not.toHaveBeenCalled();
  expect(store.getState().spec).toEqual(asset.kit);
});

it("retries the failed input without replacing the current document or history", async () => {
  const { store, runtime, session } = setup();
  await session.select(asset);
  const changed = { id: asset.id, style: "toon" };
  vi.mocked(runtime.prepare).mockRejectedValueOnce(Error("worker failed"));
  expect(await session.apply(changed)).toBe(false);
  const current = store.getState().current;
  await session.retryFailed();
  expect(runtime.prepare).toHaveBeenLastCalledWith(
    current,
    changed,
    expect.any(AbortSignal),
  );
  expect(runtime.discard).toHaveBeenCalledTimes(1);
  expect(runtime.commit).toHaveBeenCalledTimes(1);
  expect(store.getState().spec).toEqual(asset.kit);
  expect(store.getState().history).toEqual([]);
  await session.retryFailed();
  expect(runtime.prepare).toHaveBeenCalledTimes(3);
});

it("requires a fresh confirmation after the scene changes", async () => {
  const { store, session } = setup();
  const spec = {
    schema: "wx.assembly/1.0",
    id: "scene",
    instances: Array.from({ length: 13 }, (_, index) => ({
      id: `item${index}`,
      part: "chair",
    })),
  };
  store.setState({
    current: { id: "scene", level: 4, kit: spec },
    spec,
    selection: spec.instances.map((item) => item.id),
  });
  const command = vi.spyOn(session, "command").mockResolvedValue(true);
  session.requestDelete();
  expect(store.getState().dialog).toBe("delete-scene");
  expect(session.getPendingDelete()?.count).toBe(13);
  expect(command).not.toHaveBeenCalled();
  store.setState({ spec: structuredClone(spec) });
  expect(await session.confirmDelete()).toBe(false);
  expect(command).not.toHaveBeenCalled();
  session.requestDelete();
  expect(await session.confirmDelete()).toBe(true);
  expect(command).toHaveBeenCalledWith({
    type: "remove-many",
    ids: spec.instances.map((item) => item.id),
  });
});

it("does not erase a newer failure when an older retry finishes", async () => {
  const { session, runtime } = setup();
  await session.select(asset);
  vi.mocked(runtime.prepare).mockRejectedValueOnce(Error("old failure"));
  await session.apply({ id: asset.id, style: "toon" });
  let finish!: (prepared: PreparedAsset) => void;
  vi.mocked(runtime.prepare).mockImplementationOnce(
    () =>
      new Promise((resolve) => {
        finish = resolve;
      }),
  );
  const retry = session.retryFailed();
  vi.mocked(runtime.prepare).mockRejectedValueOnce(Error("new failure"));
  await session.apply({ id: asset.id, style: "voxel" });
  finish({ asset, token: Symbol() });
  await retry;
  expect(session.retryableCount()).toBe(1);
  await session.retryFailed();
  expect(runtime.prepare).toHaveBeenLastCalledWith(
    expect.objectContaining({ id: asset.id }),
    { id: asset.id, style: "voxel" },
    expect.any(AbortSignal),
  );
  expect(session.retryableCount()).toBe(0);
});
