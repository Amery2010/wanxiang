import { beforeAll, beforeEach, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SceneDialogs } from "../../src/studio/SceneDialogs";
import { createStudioStore } from "../../src/studio/store";
import { createSession } from "../../src/studio/session";
import {
  sceneAPI,
  type Runtime,
  type Asset,
  type Spec,
} from "../../src/studio/types";
const require = createRequire(import.meta.url);
beforeAll(() => {
  const globals = globalThis as unknown as Record<string, unknown>;
  globals.WXStudioCore = require("@wanxiang/runtime/studio-core");
  globals.WXSceneDocument = require("@wanxiang/runtime/scene-document");
});
beforeEach(() => localStorage.clear());
function fixture(dialog: string) {
  const catalog = {
    chair: { id: "chair", name: "椅子" },
    "exp.arch.floor": { id: "exp.arch.floor", name: "两米楼板" },
  };
  const spec = sceneAPI().normalize(
    {
      schema: "wx.assembly/1.0",
      id: "room",
      instances: [{ id: "a", part: "chair" }],
    },
    catalog,
  );
  const asset = { id: "room", level: 4, kit: spec };
  const store = createStudioStore({ assets: [asset], parts: catalog });
  store.setState({ spec, current: asset, selection: ["a"], dialog });
  const runtime = {
    prepare: vi.fn(async (value: Asset, source?: Spec) => ({
      asset: { ...value, kit: source },
      token: Symbol(),
    })),
    commit: vi.fn(),
    discard: vi.fn(),
  } as unknown as Runtime;
  return { session: createSession(store, runtime), store, runtime, spec };
}
it("creates a named local scene even when no current document exists", async () => {
  const { session, store } = fixture("new-scene");
  store.setState({ current: null, spec: null });
  render(<SceneDialogs session={session} />);
  const user = userEvent.setup();
  await user.clear(screen.getByLabelText("场景名称"));
  await user.type(screen.getByLabelText("场景名称"), "我的工坊");
  await user.click(screen.getByRole("button", { name: "创建场景" }));
  await waitFor(() => expect(store.getState().dialog).toBeNull());
  expect(store.getState().current).toMatchObject({
    name: "我的工坊",
    local: true,
    level: 4,
  });
  expect(store.getState().filters.workspace).toBe("scene");
});
it("creates a ground scene without a scene template asset", async () => {
  const { session, store } = fixture("new-scene");
  store.setState((state) => ({
    data: { ...state.data, assets: [] },
    current: null,
    spec: null,
  }));
  render(<SceneDialogs session={session} />);
  const create = screen.getByRole("button", { name: "创建场景" });
  expect(create).not.toBeDisabled();
  expect(screen.getAllByText("基础地台").length).toBeGreaterThan(0);
  await userEvent.click(create);
  await waitFor(() => expect(store.getState().dialog).toBeNull());
  expect(store.getState().spec?.instances).toMatchObject([
    { id: "ground", part: "exp.arch.floor" },
  ]);
  expect(store.getState().current?.local).toBe(true);
});
it("rejects oversized sources before reading or building", () => {
  const { session, runtime } = fixture("scene-source");
  render(<SceneDialogs session={session} />);
  const file = new File(["x".repeat(1_000_001)], "large.json", {
    type: "application/json",
  });
  fireEvent.change(screen.getByLabelText("载入场景 JSON"), {
    target: { files: [file] },
  });
  expect(screen.getByRole("alert")).toHaveTextContent("超过 1 MB");
  expect(runtime.prepare).not.toHaveBeenCalled();
});
it("retains current scene and recovery dialog when a draft build fails", async () => {
  const { session, store, runtime, spec } = fixture("scene-source");
  localStorage.setItem(
    "wanxiang.scene.v35.room",
    JSON.stringify({
      schema: "wx.scene-draft/1.0",
      saved: new Date().toISOString(),
      source: { ...spec, name: "draft" },
    }),
  );
  vi.mocked(runtime.prepare).mockRejectedValueOnce(Error("geometry rejected"));
  render(<SceneDialogs session={session} />);
  await userEvent.click(screen.getByRole("button", { name: "恢复最新草稿" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "geometry rejected",
  );
  expect(store.getState().spec).toBe(spec);
  expect(store.getState().dialog).toBe("scene-source");
  expect(store.getState().history).toEqual([]);
});
it("recovers a draft through the transaction with undo history", async () => {
  const { session, store, spec } = fixture("scene-source");
  localStorage.setItem(
    "wanxiang.scene.v35.room",
    JSON.stringify({
      schema: "wx.scene-draft/1.0",
      saved: new Date().toISOString(),
      source: { ...spec, name: "draft" },
    }),
  );
  render(<SceneDialogs session={session} />);
  await userEvent.click(screen.getByRole("button", { name: "恢复最新草稿" }));
  await waitFor(() => expect(store.getState().dialog).toBeNull());
  expect(store.getState().spec?.name).toBe("draft");
  expect(store.getState().history).toEqual([spec]);
});
it("closes dialogs with Escape", async () => {
  const { session, store } = fixture("scene-source");
  render(<SceneDialogs session={session} />);
  await userEvent.keyboard("{Escape}");
  expect(store.getState().dialog).toBeNull();
});

it("keeps subset export open when model generation fails", async () => {
  const { session, store, runtime } = fixture("scene-export");
  vi.mocked(runtime.prepare).mockRejectedValueOnce(
    Error("export build rejected"),
  );
  render(<SceneDialogs session={session} />);
  await userEvent.click(
    screen.getByRole("button", { name: "导出 GLB + JSON" }),
  );
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "export build rejected",
  );
  expect(store.getState().dialog).toBe("scene-export");
});

it("creates a named selection group without introducing transform parents", async () => {
  const { session, store } = fixture("name-group");
  render(<SceneDialogs session={session} />);
  fireEvent.change(screen.getByLabelText("选择组名称"), {
    target: { value: "家具组合" },
  });
  fireEvent.click(screen.getByRole("button", { name: "创建选择组" }));
  await waitFor(() => expect(store.getState().dialog).toBeNull());
  const doc = sceneAPI().normalize(store.getState().spec!, session.catalog);
  expect(Object.values(doc.metadata.scene.groups)[0].label).toBe("家具组合");
  expect(doc.instances[0].parent).toBeUndefined();
});
it("canceling a large deletion clears the pending request and preserves the scene", () => {
  const { session, store, spec } = fixture("delete-scene");
  spec.instances = Array.from({ length: 13 }, (_, index) => ({
    ...spec.instances[0],
    id: "item_" + index,
  }));
  const doc = sceneAPI().normalize(spec, session.catalog);
  store.setState({
    spec: doc,
    selection: doc.instances.map((item) => item.id),
    dialog: null,
  });
  session.requestDelete();
  render(<SceneDialogs session={session} />);
  expect(screen.getByText(/将删除 13 个对象/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "取消" }));
  expect(session.getPendingDelete()).toBeNull();
  expect(store.getState().spec?.instances).toHaveLength(13);
  expect(store.getState().dialog).toBeNull();
});

it("confirms large deletions once and closes the confirmation after commit", async () => {
  const { session, store, spec } = fixture("delete-scene");
  spec.instances = Array.from({ length: 13 }, (_, index) => ({
    ...spec.instances[0],
    id: "item_" + index,
  }));
  const doc = sceneAPI().normalize(spec, session.catalog);
  store.setState({
    spec: doc,
    selection: doc.instances.map((item) => item.id),
    dialog: null,
  });
  session.requestDelete();
  render(<SceneDialogs session={session} />);
  fireEvent.click(screen.getByRole("button", { name: "确认删除" }));
  await waitFor(() => expect(store.getState().dialog).toBeNull());
  expect(store.getState().spec?.instances).toHaveLength(0);
  expect(session.getPendingDelete()).toBeNull();
  expect(store.getState().history).toHaveLength(1);
});
