import { beforeAll, beforeEach, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LibraryShell } from "../../../src/studio/library/LibraryShell";
import { createStudioStore } from "../../../src/studio/store";
const require = createRequire(import.meta.url);
beforeAll(() => {
  (
    globalThis as unknown as Record<string, unknown>
  ).WXStudioCore = require("@wanxiang/runtime/studio-core");
});
beforeEach(() => localStorage.clear());
function setup() {
  const store = createStudioStore({
    assets: [
      { id: "chair", name: "椅子", level: 3 },
      {
        id: "gate",
        name: "地牢拱门",
        level: 1,
        game_category: "architecture",
        game_expansion: true,
        game_kit: "dungeon",
      },
    ],
    parts: {},
    materials: [{ id: "mat.wood", name: "木纹", record: {} }],
  });
  return { store, onSelect: vi.fn() };
}
it("shows expansion models in ordinary domains without a release collection", async () => {
  const { store, onSelect } = setup();
  store.getState().setFilters({ level: "all" });
  render(<LibraryShell store={store} onSelect={onSelect} />);
  expect(screen.queryByText("游戏新增 · 3.10")).not.toBeInTheDocument();
  expect(document.querySelector("#catalogCount")).toHaveTextContent("2 项资源");
  await userEvent.click(screen.getByRole("button", { name: /建筑与结构/ }));
  expect(store.getState().filters).toMatchObject({
    collection: "all",
    query: "",
    level: "all",
    domain: "architecture",
  });
  expect(document.querySelector("#catalogCount")).toHaveTextContent("1 项资源");
  expect(
    document.querySelector('#catalog .asset-card[data-id="gate"]'),
  ).toBeInTheDocument();
});
it("does not preview a card when a nested favorite control is used with the keyboard", async () => {
  const { store, onSelect } = setup();
  render(<LibraryShell store={store} onSelect={onSelect} />);
  screen.getByRole("button", { name: "收藏 椅子" }).focus();
  await userEvent.keyboard("{Enter}");
  expect(store.getState().prefs.favorites).toContain("chair");
  expect(onSelect).not.toHaveBeenCalled();
});
it("selects an asset without opening the mobile inspector", async () => {
  const { store, onSelect } = setup();
  const onShowInspector = vi.fn();
  render(
    <LibraryShell
      store={store}
      onSelect={onSelect}
      onShowInspector={onShowInspector}
    />,
  );
  await userEvent.click(screen.getByRole("button", { name: "预览 椅子" }));
  expect(onSelect).toHaveBeenCalledWith(
    expect.objectContaining({ id: "chair" }),
  );
  expect(onShowInspector).not.toHaveBeenCalled();
});
it("provides a keyboard reachable scene entry point for L4 assets", async () => {
  const store = createStudioStore({
    assets: [{ id: "scene", name: "测试场景", level: 4 }],
    parts: {},
    materials: [],
  });
  store.getState().setFilters({ level: "4" });
  const onOpenScene = vi.fn();
  render(
    <LibraryShell store={store} onSelect={vi.fn()} onOpenScene={onOpenScene} />,
  );
  const open = screen.getByRole("button", { name: "打开场景" });
  open.focus();
  await userEvent.keyboard("{Enter}");
  expect(onOpenScene).toHaveBeenCalledWith(
    expect.objectContaining({ id: "scene", level: 4 }),
  );
});
it("clears taxonomy, motion, and LOD filters from the empty state", async () => {
  const { store, onSelect } = setup();
  store.getState().setFilters({
    query: "不存在的资产",
    level: "3",
    motion: "moving",
    lod: "yes",
  });
  render(<LibraryShell store={store} onSelect={onSelect} />);
  await userEvent.click(screen.getByRole("button", { name: "查看全部资源" }));
  expect(store.getState().filters).toMatchObject({
    collection: "all",
    level: "all",
    query: "",
    motion: "all",
    lod: "all",
  });
});
it("opens material details through the host bridge", async () => {
  const { store, onSelect } = setup();
  const onMaterial = vi.fn();
  render(
    <LibraryShell store={store} onSelect={onSelect} bridge={{ onMaterial }} />,
  );
  await userEvent.click(screen.getByRole("button", { name: /材质库/ }));
  await userEvent.click(screen.getByRole("button", { name: "查看材质 木纹" }));
  expect(onMaterial).toHaveBeenCalledWith(
    expect.objectContaining({ id: "mat.wood" }),
  );
});
it("opens material details with Enter and Space", async () => {
  const { store, onSelect } = setup();
  const onMaterial = vi.fn();
  render(
    <LibraryShell store={store} onSelect={onSelect} bridge={{ onMaterial }} />,
  );
  await userEvent.click(screen.getByRole("button", { name: /材质库/ }));
  const material = screen.getByRole("button", { name: "查看材质 木纹" });
  material.focus();
  await userEvent.keyboard("{Enter}");
  await userEvent.keyboard(" ");
  expect(onMaterial).toHaveBeenCalledTimes(2);
});
it("returns focus to the command trigger when Escape closes the portal", async () => {
  const { store, onSelect } = setup();
  render(<LibraryShell store={store} onSelect={onSelect} />);
  const trigger = screen.getByRole("button", { name: /搜索资产或命令/ });
  await userEvent.click(trigger);
  expect(
    screen.getByRole("dialog", { name: "搜索资产与命令" }),
  ).toBeInTheDocument();
  expect(screen.getByLabelText("搜索命令与资产")).toHaveFocus();
  await userEvent.keyboard("{Escape}");
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
  expect(trigger).toHaveFocus();
});
it("keeps task dialogs outside a hidden library workspace", () => {
  const { store, onSelect } = setup();
  store.setState({ dialog: "tasks" });
  render(
    <div hidden>
      <LibraryShell store={store} onSelect={onSelect} />
    </div>,
  );
  expect(screen.getByRole("dialog", { name: "构建任务" })).toBeVisible();
});
