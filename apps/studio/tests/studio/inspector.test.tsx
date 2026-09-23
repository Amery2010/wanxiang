import { fireEvent, render, screen } from "@testing-library/react";
import { beforeAll, describe, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { createStudioStore } from "../../src/studio/store";
import { createSession } from "../../src/studio/session";
import type { Runtime } from "../../src/studio/types";
import {
  SemanticParameterFields,
  sourcePartNodes,
} from "../../src/studio/inspector-utils";
import {
  RuntimeInspector,
  AdvancedParameters,
  SourcePartTree,
} from "../../src/studio/AdvancedInspector";

const require = createRequire(import.meta.url);
beforeAll(() => {
  (
    globalThis as unknown as Record<string, unknown>
  ).WXStudioCore = require("@wanxiang/runtime/studio-core");
  require("@wanxiang/runtime/src/contracts.js");
  require("@wanxiang/runtime/semantic");
});

describe("inspector controls", () => {
  it("shows enumNames and commits a range only after the interaction ends", () => {
    const onCommit = vi.fn();
    render(
      <SemanticParameterFields
        properties={{
          height: {
            type: "number",
            title: "高度",
            minimum: 1,
            maximum: 3,
            step: 0.5,
            unit: "m",
          },
          quality: {
            type: "string",
            enum: ["draft", "hero"],
            enumNames: ["草模", "高精度"],
          },
        }}
        values={{ height: 1, quality: "draft" }}
        idPrefix="param"
        onCommit={onCommit}
      />,
    );

    const range = screen.getByRole("slider", { name: "高度" });
    fireEvent.change(range, { target: { value: "2.5" } });
    expect(onCommit).not.toHaveBeenCalled();
    fireEvent.mouseUp(range);
    expect(onCommit).toHaveBeenCalledWith("height", 2.5);
    expect(screen.getByText("2.50 m")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "草模" })).toBeInTheDocument();
  });

  it("walks nested source parts once and keeps the authored order", () => {
    const parts = {
      root: {
        id: "root",
        name: "根部件",
        shape_params: { components: [{ part: "child" }, { part: "child" }] },
      },
      child: {
        id: "child",
        name: "子部件",
        shape_params: { components: [{ part: "leaf" }] },
      },
      leaf: { id: "leaf", name: "叶部件" },
    };
    expect(sourcePartNodes(["root"], parts)).toEqual([
      { id: "root", name: "根部件", level: 1, depth: 0 },
      { id: "child", name: "子部件", level: 1, depth: 1 },
      { id: "leaf", name: "叶部件", level: 1, depth: 2 },
    ]);
  });

  it("selects a recursive source part through the session", () => {
    const root = {
        id: "root",
        name: "根部件",
        level: 3,
        dynamic: true,
        kit: { schema: "wx.part-build/1.0", id: "root", part: "root" },
      },
      store = createStudioStore({
        assets: [root],
        parts: {
          root: {
            id: "root",
            name: "根部件",
            shape_params: { components: [{ part: "child" }] },
          },
          child: { id: "child", name: "子部件" },
        },
      });
    store.setState({ current: root, spec: root.kit });
    const session = createSession(store, {} as Runtime);
    vi.spyOn(session, "select").mockResolvedValue(true);

    render(<SourcePartTree session={session} />);
    fireEvent.click(screen.getByRole("button", { name: /子部件/ }));
    expect(session.select).toHaveBeenCalledWith(
      expect.objectContaining({ id: "child", dynamic: true }),
    );
  });

  it("uses the contract matcher and submits LOD parameters through the session", () => {
    const interfaceId = "road.lane.3m.v1",
      port = {
        id: "mount",
        interface: interfaceId,
        position: [0, 0, 0],
        normal: [0, 1, 0],
        tangent: [1, 0, 0],
      };
    const asset = {
        id: "root-asset",
        name: "根资产",
        level: 3,
        dynamic: true,
        kit: {
          schema: "wx.part-build/1.0",
          id: "root-asset",
          part: "root",
          params: { detail: 0 },
        },
        runtime: {
          interfaces: [interfaceId],
          lod_levels: [
            { level: 0, name: "高", parameters: { detail: 0 } },
            { level: 1, name: "低", parameters: { detail: 1 } },
          ],
        },
        report: { sockets: [port] },
      },
      candidate = {
        id: "candidate",
        name: "候选部件",
        level: 3,
        runtime: { interfaces: [interfaceId] },
        kit: { schema: "wx.part-build/1.0", part: "candidate" },
      },
      store = createStudioStore({
        assets: [asset, candidate],
        parts: {
          root: {
            id: "root",
            shape_params: { forms: [] },
            connectors: [port],
          },
          candidate: {
            id: "candidate",
            shape_params: { forms: [] },
            connectors: [port],
          },
        },
      });
    store.setState({ current: asset, spec: asset.kit });
    const session = createSession(store, {
      runtimeSidecar: vi.fn(() => ({})),
    } as unknown as Runtime);
    vi.spyOn(session, "apply").mockResolvedValue(true);

    render(<RuntimeInspector session={session} />);
    fireEvent.click(screen.getByText("游戏接口 · 碰撞 · LOD"));
    fireEvent.change(screen.getByLabelText("源连接点"), {
      target: { value: "mount" },
    });
    fireEvent.click(screen.getByRole("button", { name: "查找可拼接部件" }));
    expect(store.getState().filters).toMatchObject({
      workspace: "library",
      level: "all",
      collision: "all",
      budget: "all",
      interface: "all",
      tag: "",
    });
    expect(
      (store.getState().filters as unknown as { compatibleIds: string[] })
        .compatibleIds,
    ).toEqual(["root-asset", "candidate"]);
    fireEvent.change(screen.getByLabelText("LOD 层级"), {
      target: { value: "1" },
    });
    expect(session.apply).toHaveBeenCalledWith(
      expect.objectContaining({ params: { detail: 1 } }),
    );
  });
});

it("lists unloaded public components alongside loaded internal parts", () => {
  const current = { id: "house", kit: { id: "house", instances: [] } };
  const store = createStudioStore({
    assets: [
      current,
      {
        id: "unloaded-part",
        name: "尚未加载的组件",
        family: "part",
        dynamic: true,
      },
    ],
    parts: { internal: { id: "internal", name: "内部组件" } },
  });
  store.setState({ current, spec: current.kit });
  const session = createSession(store, {
    motionInfo: () => [],
  } as unknown as Runtime);
  const apply = vi.spyOn(session, "apply").mockResolvedValue(true);
  render(<AdvancedParameters session={session} />);
  expect(
    screen.getByRole("option", { name: "尚未加载的组件", hidden: true }),
  ).toHaveValue("unloaded-part");
  expect(
    screen.getByRole("option", { name: "内部组件", hidden: true }),
  ).toHaveValue("internal");
  fireEvent.change(screen.getByLabelText("插入组件"), {
    target: { value: "unloaded-part" },
  });
  fireEvent.click(
    screen.getByRole("button", { name: "插入并预览", hidden: true }),
  );
  expect(apply).toHaveBeenCalledWith(
    expect.objectContaining({
      instances: [expect.objectContaining({ part: "unloaded-part" })],
    }),
  );
});
