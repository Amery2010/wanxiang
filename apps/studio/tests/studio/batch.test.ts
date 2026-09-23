import { afterEach, beforeAll, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { createSession, closedManifest } from "../../src/studio/session";
import { createStudioStore } from "../../src/studio/store";
import type { Runtime, Asset } from "../../src/studio/types";
const require = createRequire(import.meta.url);
beforeAll(() => {
  require("@wanxiang/runtime/studio-core");
  require("@wanxiang/runtime/scene-document");
});
afterEach(() => vi.unstubAllGlobals());
it("uses the existing closed roster manifest schema", () => {
  const result = JSON.parse(closedManifest([["source.json", "{}"]]));
  expect(result).toMatchObject({
    schema: "wx.package/1.0",
    closed_roster: true,
    files: { "source.json": { bytes: 2 } },
  });
  expect(result.files["source.json"].sha256).toHaveLength(64);
});
it("splits at eight assets and marks exports after download initiation", async () => {
  const blobs: Blob[] = [],
    downloads: string[] = [],
    events: string[] = [];
  vi.stubGlobal("URL", {
    createObjectURL: (blob: Blob) => {
      blobs.push(blob);
      return "blob:test";
    },
    revokeObjectURL: () => {},
  });
  vi.stubGlobal("document", {
    createElement: () => ({
      href: "",
      download: "",
      click() {
        downloads.push(this.download);
        events.push("download");
      },
    }),
  });
  vi.stubGlobal("setTimeout", () => 0);
  const assets: Asset[] = Array.from({ length: 9 }, (_, i) => ({
      id: "asset" + i,
      dynamic: true,
      kit: { id: "asset" + i },
      glb: btoa("mesh"),
    })),
    store = createStudioStore({ assets, parts: {} });
  store.setState({ batch: assets.map((a) => a.id) });
  const runtime = {
    prepare: vi.fn(async (asset: Asset) => ({ asset, token: Symbol() })),
    discard: vi.fn(),
    runtimeSidecar: () => ({ schema: "wx.collider-recipes/1.0" }),
    cache: {
      key: (s: { id: string }) => s.id,
      markExported: vi.fn(async () => {
        events.push("mark");
      }),
    },
  } as unknown as Runtime;
  await createSession(store, runtime).exportBatch();
  expect(downloads).toEqual([
    "Wanxiang3D_Selection_001.zip",
    "Wanxiang3D_Selection_002.zip",
    "Wanxiang3D_batch_report.json",
  ]);
  expect(events[0]).toBe("download");
  const zip = await blobs[0].text();
  expect(zip).toContain("asset0/asset.glb");
  expect(zip).toContain("asset0/spec.json");
  expect(zip).toContain("asset0/bom.json");
  expect(zip).toContain("asset0/runtime-recipes.json");
  expect(zip).toContain("WX_MANIFEST.json");
  const report = JSON.parse(await blobs[2].text());
  expect(report.records[8].archive).toBe("Wanxiang3D_Selection_002.zip");
  expect(runtime.discard).toHaveBeenCalledTimes(9);
});

it("counts missing assets and unchanged exports in the completed batch", async () => {
  const blobs: Blob[] = [];
  vi.stubGlobal("URL", {
    createObjectURL: (blob: Blob) => {
      blobs.push(blob);
      return "blob:test";
    },
    revokeObjectURL: () => {},
  });
  vi.stubGlobal("document", {
    createElement: () => ({ click() {}, href: "", download: "" }),
  });
  vi.stubGlobal("setTimeout", () => 0);
  const asset: Asset = {
    id: "unchanged",
    dynamic: true,
    kit: { id: "unchanged" },
  };
  const store = createStudioStore({ assets: [asset], parts: {} });
  store.setState({ batch: [asset.id, "missing"] });
  const runtime = {
    prepare: vi.fn(),
    cache: { key: () => "cached", wasExported: async () => true },
  } as unknown as Runtime;
  await createSession(store, runtime).exportBatch(true);
  expect(runtime.prepare).not.toHaveBeenCalled();
  expect(store.getState().batchProgress).toEqual({
    total: 2,
    completed: 2,
    failed: 1,
    skipped: 1,
    running: false,
    cancelled: false,
  });
  const report = JSON.parse(await blobs[0].text());
  expect(
    report.records.map((record: { status: string }) => record.status),
  ).toEqual(["unchanged", "failed"]);
});
