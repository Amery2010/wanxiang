import { StrictMode } from "react";
import { beforeAll, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { useStore } from "zustand";
import type { StudioStore } from "../../src/studio/store";
import type { Runtime, Asset, Spec } from "../../src/studio/types";
const instances = vi.hoisted(
  () => [] as { runtime: Runtime; cleanup: ReturnType<typeof vi.fn> }[],
);
vi.mock("../../src/runtime", () => ({
  createStudioRuntime: () => {
    const cleanup = vi.fn(),
      runtime = {
        prepare: vi.fn(async (asset: Asset, spec: Spec) => ({
          asset: { ...asset, kit: spec },
          token: Symbol(),
        })),
        commit: vi.fn(),
        discard: vi.fn(),
        mount: vi.fn(() => cleanup),
        dispose: vi.fn(),
        bindEditor: vi.fn(),
        selectionChanged: vi.fn(),
        motionInfo: () => [],
        getView: () => ({ center: [0, 0, 0], span: 1, az: 0, el: 0, zoom: 1 }),
        getModel: () => null,
        snapshot: () => null,
      } as unknown as Runtime;
    instances.push({ runtime, cleanup });
    return runtime;
  },
}));
vi.mock("../../src/studio/library/LibraryShell", () => ({
  LibraryShell: ({
    store,
    loading,
    onOpenScene,
    onSelect,
  }: {
    store: StudioStore;
    loading?: boolean;
    onOpenScene?: (asset: Asset) => void;
    onSelect?: (asset: Asset) => void;
  }) => {
    const dialog = useStore(store, (state) => state.dialog);
    const assets = useStore(store, (state) => state.data.assets);
    return (
      <div
        id="catalog"
        data-testid="library-dialog"
        data-current-dialog={dialog ?? ""}
      >
        资源列表
        {assets.map((asset) => (
          <button key={asset.id} onClick={() => onSelect?.(asset)}>
            选择 {asset.id}
          </button>
        ))}
        <input id="search" aria-label="搜索资产" />
        {loading && assets[0] && (
          <button onClick={() => onOpenScene?.(assets[0])}>
            加载期打开场景
          </button>
        )}
      </div>
    );
  },
}));
import { StudioApp } from "../../src/studio/StudioApp";
import { preferenceKey } from "../../src/studio/store";
const require = createRequire(import.meta.url);
beforeAll(() => {
  const g = globalThis as unknown as Record<string, unknown>;
  g.WXStudioCore = require("@wanxiang/runtime/studio-core");
  g.WXSceneDocument = require("@wanxiang/runtime/scene-document");
});

it("shows the catalogue before definitions load and keeps the latest scene intent", async () => {
  const asset = {
    id: "lazy-scene",
    name: "延迟场景",
    level: 4,
    hero: "/__wanxiang/thumbnails/lazy-scene.webp",
  };
  let resolveData!: (data: {
    assets: Asset[];
    parts: Record<string, never>;
  }) => void;
  const loadData = vi.fn(
    () =>
      new Promise<{ assets: Asset[]; parts: Record<string, never> }>(
        (resolve) => {
          resolveData = resolve;
        },
      ),
  );
  const before = instances.length;
  const result = render(
    <StrictMode>
      <StudioApp data={{ assets: [asset], parts: {} }} loadData={loadData} />
    </StrictMode>,
  );
  expect(screen.getByText("资源列表")).toBeInTheDocument();
  expect(instances).toHaveLength(before);
  document.getElementById("catalog")!.scrollTop = 123;
  fireEvent.click(screen.getByRole("button", { name: "加载期打开场景" }));
  await waitFor(() => expect(loadData).toHaveBeenCalledTimes(1));
  resolveData({
    assets: [
      {
        ...asset,
        kit: { schema: "wx.assembly/1.0", id: asset.id, instances: [] },
      },
    ],
    parts: {},
  });
  expect(
    await screen.findByRole("tree", { name: "场景对象树" }),
  ).toBeInTheDocument();
  expect(document.getElementById("catalog")?.scrollTop).toBe(123);
  expect(instances.length).toBeGreaterThan(before);
  result.unmount();
  for (const { runtime } of instances.slice(before))
    expect(runtime.dispose).toHaveBeenCalledTimes(1);
});

it("restores the catalogue search focus after live preview becomes ready", async () => {
  const asset = { id: "lazy-asset", name: "延迟资产", level: 3 };
  let resolveData!: (data: {
    assets: Asset[];
    parts: Record<string, never>;
  }) => void;
  const loadData = () =>
    new Promise<{ assets: Asset[]; parts: Record<string, never> }>(
      (resolve) => {
        resolveData = resolve;
      },
    );
  const result = render(
    <StudioApp data={{ assets: [asset], parts: {} }} loadData={loadData} />,
  );
  document.getElementById("search")!.focus();
  await waitFor(() => expect(resolveData).toBeTypeOf("function"));
  resolveData({ assets: [asset], parts: {} });
  expect(await screen.findByLabelText(/三维视口/)).toBeInTheDocument();
  expect(document.getElementById("search")).toHaveFocus();
  result.unmount();
});

it("keeps the catalogue usable when definitions fail and retries the preview", async () => {
  const asset = { id: "retry", name: "可重试资产", level: 3 };
  const loadData = vi
    .fn()
    .mockRejectedValueOnce(new Error("定义加载失败"))
    .mockResolvedValue({ assets: [asset], parts: {} });
  const result = render(
    <StudioApp data={{ assets: [asset], parts: {} }} loadData={loadData} />,
  );
  expect(await screen.findByText("定义加载失败")).toBeInTheDocument();
  expect(screen.getByText("资源列表")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "重试" }));
  expect(await screen.findByLabelText(/三维视口/)).toBeInTheDocument();
  expect(loadData).toHaveBeenCalledTimes(2);
  result.unmount();
});

it("keeps the viewport mount stable across workspaces and cleans StrictMode runtimes", async () => {
  const before = instances.length;
  const data = {
    assets: [
      {
        id: "room",
        name: "测试场景",
        level: 4,
        kit: { schema: "wx.assembly/1.0", id: "room", instances: [] },
      },
    ],
    parts: {},
  };
  const result = render(
    <StrictMode>
      <StudioApp data={data} />
    </StrictMode>,
  );
  await screen.findByRole("button", { name: "在工作台编辑场景" });
  const latest = instances.at(-1)!;
  await waitFor(() => expect(latest.runtime.mount).toHaveBeenCalled());
  const mounts = vi.mocked(latest.runtime.mount).mock.calls.length;
  fireEvent.click(screen.getByRole("button", { name: "在工作台编辑场景" }));
  expect(screen.getByRole("tree", { name: "场景对象树" })).toBeInTheDocument();
  fireEvent.click(
    screen
      .getByRole("navigation", { name: "工作空间" })
      .querySelector("#gotoLibrary")!,
  );
  expect(latest.runtime.mount).toHaveBeenCalledTimes(mounts);
  result.unmount();
  for (const { runtime } of instances.slice(before))
    expect(runtime.dispose).toHaveBeenCalledTimes(1);
  expect(latest.cleanup).toHaveBeenCalledTimes(mounts);
  expect(
    (globalThis as unknown as Record<string, unknown>).WX_LIVE_QA,
  ).toBeUndefined();
});

it("opens the mobile inspector as a modal and returns focus on Escape", async () => {
  const oldWidth = window.innerWidth;
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    value: 390,
  });
  const data = {
    assets: [
      {
        id: "room-mobile",
        name: "手机场景",
        level: 4,
        kit: { schema: "wx.assembly/1.0", id: "room-mobile", instances: [] },
      },
    ],
    parts: {},
  };
  const result = render(<StudioApp data={data} />);
  await screen.findAllByText("手机场景");
  const trigger = screen.getByRole("button", { name: "属性" });
  fireEvent.click(trigger);
  expect(
    await screen.findByRole("dialog", { name: "属性检查器" }),
  ).toBeInTheDocument();
  fireEvent.keyDown(document, { key: "Escape" });
  await waitFor(() =>
    expect(
      screen.queryByRole("dialog", { name: "属性检查器" }),
    ).not.toBeInTheDocument(),
  );
  await waitFor(() => expect(trigger).toHaveFocus());
  result.unmount();
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    value: oldWidth,
  });
});

it("keeps navigation available when the catalog sidebar collapses", async () => {
  const oldWidth = window.innerWidth;
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    value: 872,
  });
  const result = render(
    <StudioApp
      data={{ assets: [{ id: "a", name: "资产", level: 3 }], parts: {} }}
    />,
  );
  const navigation = await screen.findByRole("button", { name: "导航" });
  fireEvent.click(navigation);
  expect(
    await screen.findByRole("dialog", { name: "工作空间导航" }),
  ).toBeInTheDocument();
  result.unmount();
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    value: oldWidth,
  });
});

it("keeps Tab available in the viewport and persists resize only on release", async () => {
  window.localStorage.removeItem(preferenceKey);
  const capture = HTMLElement.prototype.setPointerCapture;
  const release = HTMLElement.prototype.releasePointerCapture;
  HTMLElement.prototype.setPointerCapture = vi.fn();
  HTMLElement.prototype.releasePointerCapture = vi.fn();
  const result = render(
    <StudioApp
      data={{ assets: [{ id: "a", name: "资产", level: 3 }], parts: {} }}
    />,
  );
  const stage = await screen.findByLabelText(/三维视口/);
  expect(fireEvent.keyDown(stage, { key: "Tab" })).toBe(true);
  expect(result.container.querySelector(".studio-app")).not.toHaveClass(
    "focus-mode",
  );
  const handle = screen.getByRole("separator", {
    name: "调整属性面板宽度",
  });
  const write = vi.spyOn(Storage.prototype, "setItem");
  fireEvent.pointerDown(handle, { pointerId: 1, clientX: 800 });
  fireEvent.pointerMove(handle, { pointerId: 1, clientX: 760 });
  expect(
    (
      result.container.querySelector(".studio-app") as HTMLElement
    ).style.getPropertyValue("--right-width"),
  ).toBe("400px");
  expect(write).not.toHaveBeenCalled();
  fireEvent.pointerUp(handle, { pointerId: 1, clientX: 760 });
  expect(write).toHaveBeenCalledTimes(1);
  expect(handle).toHaveAttribute("aria-valuenow", "400");
  fireEvent.keyDown(handle, { key: "ArrowRight" });
  expect(handle).toHaveAttribute("aria-valuenow", "390");
  write.mockRestore();
  result.unmount();
  if (capture) HTMLElement.prototype.setPointerCapture = capture;
  else delete (HTMLElement.prototype as Partial<HTMLElement>).setPointerCapture;
  if (release) HTMLElement.prototype.releasePointerCapture = release;
  else
    delete (HTMLElement.prototype as Partial<HTMLElement>)
      .releasePointerCapture;
  window.localStorage.removeItem(preferenceKey);
});

it("opens the command palette with slash in the scene workspace", async () => {
  const result = render(
    <StudioApp
      data={{
        assets: [
          {
            id: "room-command",
            name: "命令场景",
            level: 4,
            kit: {
              schema: "wx.assembly/1.0",
              id: "room-command",
              instances: [],
            },
          },
        ],
        parts: {},
      }}
    />,
  );
  fireEvent.click(
    await screen.findByRole("button", { name: "在工作台编辑场景" }),
  );
  const stage = screen.getByLabelText(/三维视口/);
  fireEvent.keyDown(stage, { key: "/" });
  expect(screen.getByTestId("library-dialog")).toHaveAttribute(
    "data-current-dialog",
    "command",
  );
  result.unmount();
});

it("starts from metadata without any model requests and loads the clicked card only", async () => {
  const asset = { id: "lazy-chair", name: "按需椅子", dynamic: true, level: 3 };
  const loadAsset = vi.fn(async (_id: string, _signal?: AbortSignal) => ({
    assets: [{ ...asset, kit: { id: asset.id, instances: [] } }],
    parts: {},
    assemblies: { [asset.id]: { id: asset.id, instances: [] } },
  }));
  const view = render(
    <StrictMode>
      <StudioApp
        data={{ assets: [asset], parts: {}, assemblies: {} }}
        loadAsset={loadAsset}
      />
    </StrictMode>,
  );
  await screen.findByLabelText(/三维视口/);
  expect(loadAsset).not.toHaveBeenCalled();
  expect(instances.at(-1)!.runtime.prepare).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "选择 lazy-chair" }));
  await waitFor(() =>
    expect(instances.at(-1)!.runtime.commit).toHaveBeenCalledTimes(1),
  );
  expect(loadAsset).toHaveBeenCalledTimes(1);
  expect(loadAsset.mock.calls[0][0]).toBe("lazy-chair");
  view.unmount();
});
