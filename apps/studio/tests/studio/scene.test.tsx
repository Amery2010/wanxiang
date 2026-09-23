import { beforeAll, describe, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { render, screen, fireEvent } from "@testing-library/react";
import {
  SceneProperties,
  SceneTree,
  Shelf,
  SceneTools,
} from "../../src/studio/Scene";
import { AssetPicker } from "../../src/studio/AssetPicker";
import { Inspector } from "../../src/studio/Inspector";
import { createStudioStore } from "../../src/studio/store";
import { createSession } from "../../src/studio/session";
import {
  sceneAPI,
  type Runtime,
  type SceneDocument,
} from "../../src/studio/types";
const require = createRequire(import.meta.url);
beforeAll(() => {
  const globals = globalThis as unknown as Record<string, unknown>;
  globals.WXStudioCore = require("@wanxiang/runtime/studio-core");
  globals.WXSceneDocument = require("@wanxiang/runtime/scene-document");
});
function fixture() {
  const catalog = { chair: { id: "chair", name: "椅子" } },
    spec = sceneAPI().normalize(
      {
        schema: "wx.assembly/1.0",
        id: "room",
        instances: [
          { id: "a", part: "chair", position: [0, 0, 0] },
          { id: "b", part: "chair", position: [2, 0, 0] },
        ],
      },
      catalog,
    ),
    store = createStudioStore({ assets: [], parts: catalog });
  store.setState({
    spec,
    current: { id: "room", level: 4, kit: spec },
    selection: ["a", "b"],
  });
  const session = createSession(store, {
    motionInfo: () => [],
  } as unknown as Runtime);
  session.command = vi.fn(async () => true);
  return { session, store };
}
describe("scene React controls", () => {
  it("explains an empty asset shelf", () => {
    const { session } = fixture();
    render(<Shelf session={session} />);
    expect(screen.getByRole("status")).toHaveTextContent("没有匹配的资产");
  });
  it("applies relative multi-selection transform through one transaction", () => {
    const { session } = fixture();
    render(<SceneProperties session={session} />);
    const input = screen.getByLabelText("position X");
    fireEvent.change(input, { target: { value: "3" } });
    fireEvent.blur(input);
    expect(session.command).toHaveBeenCalledWith({
      type: "transform-many",
      ids: ["a", "b"],
      values: { a: { position: [3, 0, 0] }, b: { position: [5, 0, 0] } },
    });
  });
  it("keeps selection when the object visibility button is clicked", () => {
    const { session, store } = fixture();
    render(<SceneTree session={session} />);
    fireEvent.click(screen.getByRole("button", { name: "隐藏 a" }));
    expect(store.getState().selection).toEqual(["a", "b"]);
    expect(session.command).toHaveBeenCalledWith({
      type: "visibility",
      id: "a",
      visible: false,
    });
  });
  it("supports keyboard selection in the scene tree", () => {
    const { session, store } = fixture();
    render(<SceneTree session={session} />);
    const rows = screen.getAllByRole("treeitem");
    fireEvent.keyDown(rows[1], { key: "Enter" });
    expect(store.getState().selection).toEqual(["b"]);
  });
  it("keeps the tree mounted when a layer toggles", () => {
    const { session } = fixture();
    const { container } = render(<SceneTree session={session} />);
    const layer = container.querySelector("details");
    expect(layer).not.toBeNull();
    layer!.open = false;
    fireEvent(layer!, new Event("toggle"));
    expect(
      screen.getByRole("tree", { name: "场景对象树" }),
    ).toBeInTheDocument();
  });
  it("moves focus between visible tree rows with arrow keys", () => {
    const { session } = fixture();
    render(<SceneTree session={session} />);
    const rows = screen.getAllByRole("treeitem");
    rows[0].focus();
    fireEvent.keyDown(rows[0], { key: "ArrowDown" });
    expect(rows[1]).toHaveFocus();
    fireEvent.keyDown(rows[1], { key: "ArrowUp" });
    expect(rows[0]).toHaveFocus();
  });
  it("announces an empty filtered layer", () => {
    const { session } = fixture();
    render(<SceneTree session={session} />);
    fireEvent.change(screen.getByLabelText("搜索场景对象"), {
      target: { value: "不存在的对象" },
    });
    expect(screen.getAllByRole("status")[0]).toHaveTextContent(
      "没有匹配的场景对象",
    );
  });
  it("associates the inspector tab with its visible tabpanel", () => {
    const { session } = fixture();
    render(<Inspector session={session} />);
    const tab = screen.getByRole("tab", { name: "参数" });
    const panel = screen.getByRole("tabpanel");
    expect(tab).toHaveAttribute("aria-controls", "inspector-panel-parameters");
    expect(panel).toHaveAttribute(
      "aria-labelledby",
      "inspector-tab-parameters",
    );
  });
});

it("selects a range with Shift Alt and keeps ordinary Shift as toggle", () => {
  const { session, store } = fixture();
  const spec = store.getState().spec as SceneDocument;
  spec.instances.push({ ...spec.instances[0], id: "c" });
  spec.metadata.scene.objects.c = {
    ...spec.metadata.scene.objects.a,
    label: "c",
  };
  render(<SceneTree session={session} />);
  fireEvent.click(screen.getByRole("treeitem", { name: "a" }));
  fireEvent.click(screen.getByRole("treeitem", { name: "c" }), {
    shiftKey: true,
    altKey: true,
  });
  expect(store.getState().selection).toEqual(["a", "b", "c"]);
  fireEvent.click(screen.getByRole("treeitem", { name: "b" }), {
    shiftKey: true,
  });
  expect(store.getState().selection).toEqual(["a", "c"]);
});
it("selects a named group and exposes inherited locks", () => {
  const { session, store } = fixture();
  const spec = store.getState().spec as SceneDocument;
  spec.metadata.scene.groups.furniture = {
    label: "家具组",
    locked: true,
    hidden: false,
  };
  for (const object of Object.values(spec.metadata.scene.objects))
    object.group = "furniture";
  render(<SceneTree session={session} />);
  fireEvent.click(screen.getByRole("button", { name: /家具组/ }));
  expect(store.getState().selection).toEqual(["a", "b"]);
  expect(screen.getByRole("button", { name: "继承锁定 a" })).toBeDisabled();
  expect(screen.getByRole("treeitem", { name: "a" })).toHaveClass("is-locked");
});
it("hides a mixed selection and resets pose without resetting position", () => {
  const { session, store } = fixture();
  const spec = store.getState().spec as SceneDocument;
  spec.metadata.scene.objects.a.hidden = true;
  spec.instances[0].enabled = false;
  render(<SceneProperties session={session} />);
  fireEvent.click(screen.getByRole("button", { name: "隐藏" }));
  expect(session.command).toHaveBeenLastCalledWith({
    type: "visibility",
    ids: ["a", "b"],
    visible: false,
  });
  fireEvent.click(screen.getByRole("button", { name: "重置姿态" }));
  expect(session.command).toHaveBeenLastCalledWith({
    type: "transform-many",
    ids: ["a", "b"],
    values: {
      a: { rotation: [0, 0, 0], scale: [1, 1, 1] },
      b: { rotation: [0, 0, 0], scale: [1, 1, 1] },
    },
  });
});
it("applies the default scene style through the transaction", () => {
  const { session, store } = fixture();
  store.setState({ selection: [] });
  session.apply = vi.fn(async () => true);
  render(<SceneProperties session={session} />);
  expect(screen.getByText("可见对象")).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("场景默认风格"), {
    target: { value: "toon" },
  });
  expect(session.apply).toHaveBeenCalledWith(
    expect.objectContaining({ style: "toon" }),
  );
});
it("renames the scene and exposes snap, settings and focus controls", () => {
  const { session, store } = fixture();
  render(<SceneTools session={session} />);
  fireEvent.change(screen.getByLabelText("重命名场景"), {
    target: { value: "工坊" },
  });
  fireEvent.blur(screen.getByLabelText("重命名场景"));
  expect(session.command).toHaveBeenCalledWith({
    type: "rename-scene",
    title: "工坊",
  });
  fireEvent.change(screen.getByLabelText("移动吸附步长"), {
    target: { value: "0.5" },
  });
  expect(store.getState().prefs.snapMove).toBe(0.5);
  fireEvent.click(screen.getByLabelText("编辑设置"));
  expect(store.getState().dialog).toBe("scene-settings");
  fireEvent.click(screen.getByLabelText("专注模式"));
  expect(store.getState().focusMode).toBe(true);
});
it("filters and collapses the shelf and inserts at the ground center", () => {
  const { session, store } = fixture();
  session.runtime.groundCenter = vi.fn(() => [10, 0, 20]);
  const kit = { id: "chair" };
  store.setState((state) => ({
    data: {
      ...state.data,
      assets: [
        { id: "chair", name: "椅子", level: 3, domain: "interior", kit },
      ],
    },
    prefs: { ...state.prefs, favorites: [] },
  }));
  render(<Shelf session={session} />);
  fireEvent.click(screen.getByRole("button", { name: "插入 椅子" }));
  expect(session.command).toHaveBeenCalledWith({
    type: "add",
    ref: "chair",
    position: [10, 0, 20],
    layer: "default",
  });
  fireEvent.click(screen.getByLabelText("仅收藏资产"));
  expect(
    screen.queryByRole("button", { name: "插入 椅子" }),
  ).not.toBeInTheDocument();
  fireEvent.click(screen.getByLabelText("折叠资产架"));
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
  expect(screen.getByLabelText("展开资产架")).toHaveAttribute(
    "aria-expanded",
    "false",
  );
});
it("inserts picker assets at the viewport center using the selected editable layer", () => {
  const { session, store } = fixture();
  session.runtime.groundCenter = vi.fn(() => [10, 0, 20]);
  const doc = store.getState().spec as SceneDocument;
  doc.metadata.scene.layers.furniture = { label: "家具", visible: true };
  doc.metadata.scene.objects.a.layer = "furniture";
  store.setState((state) => ({
    dialog: "scene-picker",
    data: {
      ...state.data,
      assets: [{ id: "chair", name: "椅子", level: 3, kit: { id: "chair" } }],
    },
  }));
  render(<AssetPicker session={session} />);
  fireEvent.click(screen.getByRole("button", { name: "椅子" }));
  fireEvent.click(screen.getByRole("button", { name: "插入所选 (1)" }));
  expect(session.command).toHaveBeenCalledWith({
    type: "batch",
    commands: [
      { type: "add", ref: "chair", position: [10, 0, 20], layer: "furniture" },
    ],
  });
});
