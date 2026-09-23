import { beforeAll, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AssetCatalog } from "../../../src/studio/library/AssetCatalog";
import { createStudioStore } from "../../../src/studio/store";
import { filterAssets } from "../../../src/studio/library/utils";
import type { Filters, Preferences } from "../../../src/studio/types";

const require = createRequire(import.meta.url);

beforeAll(() => {
  (
    globalThis as unknown as Record<string, unknown>
  ).WXStudioCore = require("@wanxiang/runtime/studio-core");
});

const preferences: Preferences = {
  favorites: [],
  recent: [],
  view: "grid",
  theme: "light",
  sort: "recommended",
  leftWidth: 224,
  rightWidth: 310,
  snap: true,
  snapMove: 0.25,
  snapRotate: 15,
  snapScale: 0.1,
};

function filters(overrides: Partial<Filters> = {}): Filters {
  return {
    workspace: "library",
    level: "all",
    domain: "all",
    theme: "all",
    collection: "all",
    gameKit: "all",
    query: "",
    sort: "recommended",
    page: 1,
    pageSize: 48,
    motion: "all",
    lod: "all",
    collision: "all",
    budget: "all",
    interface: "all",
    tag: "",
    compatibleIds: null,
    ...overrides,
  };
}

it("applies collision, budget, interface, tag, and compatibility filters together", () => {
  const assets = [
    {
      id: "bridge",
      name: "桥梁",
      level: 3,
      tags: ["桥梁"],
      runtime: {
        collision: { type: "box" },
        budget: 900,
        interfaces: ["road.edge.1m.v1"],
      },
      report: { triangles: 700 },
    },
    {
      id: "tree",
      name: "树",
      level: 3,
      tags: ["森林"],
      runtime: {
        collision: false,
        budget: 700,
        interfaces: ["nature.root.v1"],
      },
      report: { triangles: 500 },
    },
  ];
  const result = filterAssets(
    assets,
    filters({
      collision: "yes",
      budget: "1000",
      interface: "road.edge.1m.v1",
      tag: "桥",
      compatibleIds: ["bridge"],
    }),
    preferences,
  );
  expect(result.map((asset) => asset.id)).toEqual(["bridge"]);
});

function catalogAssets(count: number) {
  return Array.from({ length: count }, (_, index) => ({
    id: `asset-${index}`,
    name: `资产 ${index}`,
    level: 3,
  }));
}

function renderCatalog(
  assets: ReturnType<typeof catalogAssets>,
  onBatchExport = vi.fn(),
) {
  const store = createStudioStore({ assets, parts: {}, materials: [] });
  render(
    <AssetCatalog
      store={store}
      onSelect={vi.fn()}
      onBatchExport={onBatchExport}
    />,
  );
  return { store, onBatchExport };
}

it("selects every filtered page when within the batch limit", async () => {
  const { store } = renderCatalog(catalogAssets(50));
  await userEvent.click(
    screen.getByRole("button", { name: "选择当前筛选结果" }),
  );
  expect(store.getState().batch).toHaveLength(50);
});

it("rejects a filtered result over 256 items without truncating selection", async () => {
  const { store } = renderCatalog(catalogAssets(257));
  await userEvent.click(
    screen.getByRole("button", { name: "选择当前筛选结果" }),
  );
  expect(store.getState().batch).toEqual([]);
  expect(store.getState().notice).toContain("超过每批最多 256 项");
});

it("does not record recent usage before the host confirms a successful load", async () => {
  const { store } = renderCatalog(catalogAssets(1));
  await userEvent.click(screen.getByRole("button", { name: "预览 资产 0" }));
  expect(store.getState().prefs.recent).toEqual([]);
});

it("passes the only-changed batch option to the host", async () => {
  const { onBatchExport } = renderCatalog(catalogAssets(1));
  await userEvent.click(
    screen.getByRole("checkbox", { name: "加入批量选择：资产 0" }),
  );
  await userEvent.click(screen.getByRole("checkbox", { name: "仅导出已变更" }));
  await userEvent.click(screen.getByRole("button", { name: "批量处理" }));
  expect(onBatchExport).toHaveBeenCalledWith(true);
});
