import { createAssetLoader, type LoadAsset } from "./asset-loader";
import { importGLBAsset } from "./import-glb";
import { zipStore, closedManifest, type ArchiveFile } from "../runtime/archive";
import type { StudioStore } from "./store";
import { core, sceneAPI, type Asset, type Spec, type Runtime } from "./types";
export function download(
  value: BlobPart,
  name: string,
  type = "application/json",
) {
  const url = URL.createObjectURL(new Blob([value], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
}
export { closedManifest } from "../runtime/archive";
export function createSession(
  store: StudioStore,
  runtime: Runtime,
  loadAsset?: LoadAsset,
) {
  let generation = 0,
    abort: AbortController | null = null,
    batchAbort: AbortController | null = null,
    retryAbort: AbortController | null = null;
  let pendingDelete: {
    assetId: string;
    spec: Spec;
    ids: string[];
    count: number;
  } | null = null;
  const failedBuilds = new Map<string, { asset: Asset; spec?: Spec }>();
  const catalog = {
    ...store.getState().data.parts,
    ...store.getState().data.assemblies,
  };
  const loader = loadAsset
    ? createAssetLoader(store, loadAsset, (patch) => {
        runtime.mergeDefinitions?.(patch);
        const data = store.getState().data;
        const loaded = new Map(patch.assets.map((asset) => [asset.id, asset]));
        const next = {
          ...data,
          assets: data.assets.map((asset) => {
            const full = loaded.get(asset.id);
            return full
              ? { ...asset, ...full, hero: asset.hero || full.hero }
              : asset;
          }),
          parts: { ...data.parts, ...patch.parts },
          assemblies: { ...data.assemblies, ...patch.assemblies },
          motions: { ...data.motions, ...patch.motions },
          interfaces: patch.interfaces ?? data.interfaces,
        };
        Object.assign(catalog, patch.parts, patch.assemblies);
        store.setState({ data: next });
      })
    : null;
  async function ready(asset: Asset, spec?: Spec, signal?: AbortSignal) {
    return loader ? loader.asset(asset, spec, signal) : asset;
  }
  const fail = (error: unknown) => {
    store.setState({
      error: error instanceof Error ? error.message : String(error),
    });
  };
  const draft = (asset: Asset, spec: Spec, checkpoint = false) => {
    if (asset.level !== 4) return;
    const key = "wanxiang.scene.v35." + asset.id,
      record = {
        schema: "wx.scene-draft/1.0",
        saved: new Date().toISOString(),
        source: spec,
      };
    const ok = core().save(key, record);
    if (!ok) store.getState().notify("浏览器无法保存草稿，请下载场景 JSON。");
    if (checkpoint) {
      const versions = [
        record,
        ...core().storage<(typeof record)[]>(key + ".versions", []),
      ].slice(0, 5);
      while (JSON.stringify(versions).length > 1500000 && versions.length > 1)
        versions.pop();
      core().save(key + ".versions", versions);
    }
    return ok;
  };
  async function transact(
    asset: Asset,
    spec: Spec | undefined,
    mode: "select" | "edit" | "undo" | "redo" = "edit",
    command?: Record<string, unknown>,
  ) {
    const ticket = ++generation;
    abort?.abort();
    const controller = new AbortController();
    abort = controller;
    store.setState({ busy: true, error: "" });
    try {
      if (loader) {
        asset = await ready(asset, spec, controller.signal);
        spec ||= asset.kit;
        if (command) await loader.references(command, controller.signal);
        if (controller.signal.aborted || ticket !== generation) return false;
      }
      if (command && spec) spec = sceneAPI().apply(spec, command, catalog);
      const normalized =
        asset.level === 4 && spec ? sceneAPI().normalize(spec, catalog) : spec;
      const prepared = await runtime.prepare(
        asset,
        normalized,
        controller.signal,
      );
      if (ticket !== generation) {
        runtime.discard(prepared);
        return false;
      }
      const before = store.getState();
      try {
        runtime.commit(prepared);
      } catch (error) {
        runtime.discard(prepared);
        throw error;
      }
      const next = prepared.asset;
      failedBuilds.delete(asset.id);
      let history = before.history,
        future = before.future;
      if (mode === "select") {
        const saved = before.documents[asset.id];
        history = saved?.history || [];
        future = saved?.future || [];
      } else if (mode === "undo") {
        history = history.slice(0, -1);
        future = before.spec ? [...future, before.spec] : future;
      } else if (mode === "redo") {
        future = future.slice(0, -1);
        history = before.spec ? [...history, before.spec] : history;
      } else {
        history = before.spec ? [...history, before.spec].slice(-50) : history;
        future = [];
      }
      const saved = before.documents[asset.id];
      const state = {
        current: next,
        spec: normalized ?? next.kit ?? null,
        history,
        future,
        selection:
          mode === "select"
            ? saved?.selection || []
            : before.selection.filter((id) =>
                normalized?.instances?.some((i: { id: string }) => i.id === id),
              ),
        dirty: mode === "select" ? saved?.dirty || false : true,
      };
      store.setState({
        ...state,
        documents: {
          ...before.documents,
          ...(before.current
            ? {
                [before.current.id]: {
                  current: before.current,
                  spec: before.spec,
                  history: before.history,
                  future: before.future,
                  selection: before.selection,
                  dirty: before.dirty,
                },
              }
            : {}),
          [asset.id]: state,
        },
        busy: false,
      });
      if (mode === "select")
        before.setPrefs({
          recent: [
            asset.id,
            ...before.prefs.recent.filter((id) => id !== asset.id),
          ].slice(0, 60),
        });
      else if (normalized) draft(asset, normalized);
      return true;
    } catch (error) {
      if (
        ticket === generation &&
        !(error instanceof Error && error.name === "AbortError")
      ) {
        failedBuilds.set(asset.id, {
          asset,
          spec: spec && structuredClone(spec),
        });
        fail(error);
      }
      return false;
    } finally {
      if (ticket === generation) store.setState({ busy: false });
    }
  }
  const api = {
    runtime,
    store,
    catalog,
    async ensureAsset(id: string, signal?: AbortSignal) {
      const asset = store
        .getState()
        .data.assets.find((asset) => asset.id === id);
      if (asset) return ready(asset, undefined, signal);
      await loader?.ensure(id, signal);
      return undefined;
    },
    select: (asset: Asset) => {
      const saved = store.getState().documents[asset.id];
      return transact(
        saved?.current || asset,
        saved?.spec || asset.kit,
        "select",
      );
    },
    cancel() {
      generation++;
      abort?.abort();
      retryAbort?.abort();
      store.setState({ busy: false });
    },
    requestDelete(ids = store.getState().selection) {
      const s = store.getState();
      if (s.busy || !s.spec || !s.current || !ids.length) return false;
      const count = sceneAPI().descendants(s.spec, ids).size;
      if (count > 12) {
        pendingDelete = {
          assetId: s.current.id,
          spec: s.spec,
          ids: [...ids],
          count,
        };
        store.setState({ dialog: "delete-scene" });
      } else void api.command({ type: "remove-many", ids });
      return true;
    },
    getPendingDelete() {
      return pendingDelete
        ? { count: pendingDelete.count, ids: [...pendingDelete.ids] }
        : null;
    },
    cancelDelete() {
      pendingDelete = null;
    },
    async confirmDelete(): Promise<boolean> {
      const s = store.getState(),
        request = pendingDelete;
      if (!request || s.busy) return false;
      if (request.assetId !== s.current?.id || request.spec !== s.spec) {
        pendingDelete = null;
        store.setState({ dialog: null });
        s.notify("场景已发生变化，请重新选择要删除的对象。");
        return false;
      }
      const ok = await api.command({ type: "remove-many", ids: request.ids });
      if (ok) pendingDelete = null;
      return ok;
    },
    requestGroup() {
      const s = store.getState();
      if (!s.busy && s.selection.length)
        store.setState({ dialog: "name-group" });
    },
    async retryFailed() {
      if (retryAbort || !failedBuilds.size) return;
      const controller = new AbortController();
      retryAbort = controller;
      try {
        for (const [id, input] of [...failedBuilds]) {
          if (controller.signal.aborted) break;
          try {
            const asset = loader
              ? await ready(input.asset, input.spec, controller.signal)
              : input.asset;
            const prepared = await runtime.prepare(
              asset,
              input.spec || asset.kit,
              controller.signal,
            );
            runtime.discard(prepared);
            if (!controller.signal.aborted && failedBuilds.get(id) === input)
              failedBuilds.delete(id);
          } catch (error) {
            if (controller.signal.aborted) break;
            fail(error);
          }
        }
        store
          .getState()
          .notify(
            controller.signal.aborted
              ? "重试已停止"
              : "重试结束，成功的资源已可重新打开。",
          );
      } finally {
        retryAbort = null;
      }
    },
    retryableCount: () => failedBuilds.size,
    async apply(spec: Spec) {
      const s = store.getState();
      if (!s.data.parts) {
        fail(Error("此页面仅支持查看与导出，未包含可重建的组件库。"));
        return false;
      }
      return s.current ? transact(s.current, spec) : false;
    },
    async command(command: Record<string, unknown>) {
      const s = store.getState();
      if (s.busy || !s.spec) return false;
      try {
        const before = new Set((s.spec.instances || []).map((i) => i.id)),
          ok = s.current
            ? await transact(s.current, s.spec, "edit", command)
            : false;
        if (
          ok &&
          ["add", "duplicate", "duplicate-many", "paste", "batch"].includes(
            String(command.type),
          )
        ) {
          const added = (store.getState().spec?.instances || [])
            .filter((i) => !before.has(i.id))
            .map((i) => i.id);
          if (added.length) api.selectObjects(added);
        }
        return ok;
      } catch (error) {
        fail(error);
        return false;
      }
    },
    async undo() {
      const s = store.getState();
      return !s.busy && s.current && s.history.length
        ? transact(s.current, s.history.at(-1), "undo")
        : false;
    },
    async redo() {
      const s = store.getState();
      return !s.busy && s.current && s.future.length
        ? transact(s.current, s.future.at(-1), "redo")
        : false;
    },
    selectObjects(ids: string[], toggle = false) {
      store.setState((s) => ({
        selection: toggle
          ? [
              ...new Set([
                ...s.selection.filter((id) => !ids.includes(id)),
                ...ids.filter((id) => !s.selection.includes(id)),
              ]),
            ]
          : ids,
      }));
    },
    checkpoint() {
      const s = store.getState();
      if (!s.current || !s.spec) return false;
      return draft(s.current, s.spec, true) === true;
    },
    save() {
      const s = store.getState();
      if (!s.spec || !s.current) return;
      download(
        JSON.stringify(s.spec, null, 2),
        s.current.id + (s.current.level === 4 ? ".scene.json" : ".json"),
      );
      draft(s.current, s.spec, true);
      store.setState({
        dirty: false,
        documents: {
          ...s.documents,
          [s.current.id]: {
            current: s.current,
            spec: s.spec,
            selection: s.selection,
            history: s.history,
            future: s.future,
            dirty: false,
          },
        },
      });
      s.notify("已发起场景源 JSON 下载，请确认浏览器保存完成。");
    },
    async exportGLB() {
      try {
        const data = await runtime.exportGLB();
        download(
          data,
          (store.getState().current?.id || "asset") + ".glb",
          "model/gltf-binary",
        );
      } catch (error) {
        fail(error);
      }
    },
    async exportBatch(onlyChanged = false) {
      const state = store.getState(),
        ids = [...state.batch];
      if (!ids.length || batchAbort) return;
      if (ids.length > 256) {
        state.notify("每批最多 256 项，请按主题或层级拆分。");
        return;
      }
      const controller = new AbortController();
      batchAbort = controller;
      store.setState({
        batchProgress: {
          total: ids.length,
          completed: 0,
          failed: 0,
          skipped: 0,
          running: true,
          cancelled: false,
        },
      });
      const maxChunk = 32 * 1048576,
        maxItems = 8;
      type Row = {
        id?: string;
        status: string;
        error?: string;
        key?: string;
        sha256?: string;
        archive?: string;
      };
      const records: Row[] = [];
      const updateProgress = (running = true) =>
        store.setState({
          batchProgress: {
            total: ids.length,
            completed: records.length,
            failed: records.filter((row) => row.status === "failed").length,
            skipped: records.filter((row) => row.status === "unchanged").length,
            running,
            cancelled: controller.signal.aborted,
          },
        });
      let files: ArchiveFile[] = [],
        size = 0,
        chunk = 0,
        chunkItems: Row[] = [];
      const flush = async () => {
        if (!files.length) return;
        files.push(["WX_MANIFEST.json", closedManifest(files)]);
        const name =
          "Wanxiang3D_Selection_" + String(++chunk).padStart(3, "0") + ".zip";
        download(zipStore(files), name, "application/zip");
        for (const row of chunkItems) {
          row.archive = name;
          if (row.key) await runtime.cache?.markExported(row.key);
        }
        files = [];
        size = 0;
        chunkItems = [];
      };
      try {
        for (const id of ids) {
          if (controller.signal.aborted) break;
          const original =
            state.documents[id]?.current ||
            state.data.assets.find((a) => a.id === id);
          if (!original) {
            records.push({
              id,
              status: "failed",
              error: "资产已不在当前目录中",
            });
            updateProgress();
            continue;
          }
          let source = state.documents[id]?.spec || original.kit;
          let asset: Asset = {
            ...original,
            kit: source ? structuredClone(source) : undefined,
          };
          try {
            asset = await ready(asset, source, controller.signal);
            source ||= asset.kit;
            const key =
              asset.dynamic && source ? runtime.cache?.key(source) : undefined;
            if (onlyChanged && key && (await runtime.cache?.wasExported(key))) {
              records.push({ id, status: "unchanged", key });
              store.setState({
                batchProgress: {
                  total: ids.length,
                  completed: records.length,
                  failed: records.filter((r) => r.status === "failed").length,
                  skipped: records.filter((r) => r.status === "unchanged")
                    .length,
                  running: true,
                  cancelled: false,
                },
              });
              continue;
            }
            const prepared = await runtime.prepare(
              asset,
              source,
              controller.signal,
            );
            try {
              if (controller.signal.aborted) break;
              if (!prepared.asset.glb) throw Error("构建没有产生 GLB");
              const built = prepared.asset,
                binary = Uint8Array.from(atob(built.glb!), (c) =>
                  c.charCodeAt(0),
                );
              if (binary.byteLength > maxChunk)
                throw Error("单模型超过 32 MiB，请单独导出或降低细节");
              if (
                size + binary.byteLength > maxChunk ||
                chunkItems.length >= maxItems
              )
                await flush();
              const added: ArchiveFile[] = [
                [id + "/asset.glb", binary],
                [
                  id + "/spec.json",
                  JSON.stringify(source || asset.spec, null, 2),
                ],
                [id + "/bom.json", JSON.stringify(built.bom || [], null, 2)],
                [
                  id + "/runtime-recipes.json",
                  JSON.stringify(
                    asset.dynamic
                      ? runtime.runtimeSidecar(built)
                      : { imported: true },
                    null,
                    2,
                  ),
                ],
              ];
              files.push(...added);
              size += added.reduce(
                (sum, [, value]) =>
                  sum +
                  (typeof value === "string"
                    ? new TextEncoder().encode(value).length
                    : value.length),
                0,
              );
              const row = { id, status: "exported", sha256: built.sha256, key };
              failedBuilds.delete(id);
              records.push(row);
              chunkItems.push(row);
            } finally {
              runtime.discard(prepared);
            }
          } catch (error) {
            if (controller.signal.aborted) break;
            records.push({ id, status: "failed", error: String(error) });
            failedBuilds.set(id, {
              asset,
              spec: source && structuredClone(source),
            });
          }
          updateProgress();
          state.notify("批量导出 " + records.length + " / " + ids.length);
        }
      } finally {
        try {
          await flush();
          const report = {
            schema: "wx.batch/1.0",
            requested: ids.length,
            records,
            chunk_limit_bytes: maxChunk,
            cancelled: controller.signal.aborted,
            download_receipt_scope:
              "browser download initiated; disk completion is controlled by browser",
          };
          download(
            JSON.stringify(report, null, 2),
            "Wanxiang3D_batch_report.json",
          );
          const globals = globalThis as unknown as {
            WX_QA?: Record<string, unknown>;
          };
          if (globals.WX_QA) globals.WX_QA.batchReport = report;
        } finally {
          batchAbort = null;
          updateProgress(false);
          state.notify("批次结束，请核对下载报告和浏览器保存结果。");
        }
      }
    },
    cancelBatch() {
      batchAbort?.abort();
    },
    async exportSubset(query: Record<string, unknown>) {
      const s = store.getState();
      if (!s.spec || !s.current) return false;
      let input: { asset: Asset; spec: Spec } | null = null;
      try {
        const spec = sceneAPI().subset(s.spec, query, catalog);
        input = { asset: { ...s.current, id: spec.id }, spec };
        const prepared = await runtime.prepare(input.asset, spec);
        failedBuilds.delete(input.asset.id);
        try {
          if (!prepared.asset.glb) throw Error("构建没有产生 GLB");
          if (prepared.asset.glb) {
            const bytes = Uint8Array.from(atob(prepared.asset.glb), (c) =>
              c.charCodeAt(0),
            );
            download(bytes, spec.id + ".glb", "model/gltf-binary");
          }
          download(JSON.stringify(spec, null, 2), spec.id + ".scene.json");
          return true;
        } finally {
          runtime.discard(prepared);
        }
      } catch (error) {
        if (input) failedBuilds.set(input.asset.id, input);
        fail(error);
        return false;
      }
    },
    async importGLB(file: File) {
      try {
        if (file.size > 64000000) throw Error("导入上限 64 MB");
        const asset = importGLBAsset(await file.arrayBuffer(), file.name);
        if (await api.select(asset)) {
          store.setState((s) => ({
            data: { ...s.data, assets: [asset, ...s.data.assets] },
          }));
          store.getState().setFilters({
            workspace: "library",
            collection: "custom",
            level: "all",
            query: "",
            domain: "all",
          });
          store.getState().notify("真实 GLB 已导入；来源、拓扑与美术仍需审查");
          return true;
        }
        return false;
      } catch (error) {
        fail(error);
        return false;
      }
    },
    async newScene(name = "未命名场景", templateId = "empty") {
      const data = store.getState().data;
      let template =
        data.assets.find((a) => a.id === templateId) ||
        data.assets.find((a) => a.id.startsWith("l4-interior-")) ||
        data.assets.find((a) => a.level === 4);
      if (template && loader) {
        const ticket = ++generation;
        abort?.abort();
        const controller = new AbortController();
        abort = controller;
        store.setState({ busy: true, error: "" });
        try {
          template = await ready(template, undefined, controller.signal);
          if (ticket !== generation || controller.signal.aborted) return false;
        } catch (error) {
          if (ticket === generation && !controller.signal.aborted) fail(error);
          return false;
        } finally {
          if (ticket === generation) store.setState({ busy: false });
        }
      }
      const groundPart =
        templateId === "empty" && !template?.kit
          ? ["exp.arch.floor", "w.arch.floor", "p5.habitat.floor"].find(
              (id) => data.parts?.[id],
            )
          : undefined;
      if (!template?.kit && !groundPart) {
        store.setState({
          error:
            templateId === "empty"
              ? "当前目录缺少基础地台部件，无法创建场景。"
              : "当前目录没有可用的场景模板。",
        });
        return false;
      }
      const id = "local-scene-" + Date.now().toString(36),
        spec: Spec = template?.kit
          ? structuredClone(template.kit)
          : {
              schema: "wx.assembly/1.0",
              id,
              name,
              instances: [{ id: "ground", part: groundPart }],
            };
      spec.id = id;
      spec.name = name;
      if (templateId === "empty") {
        const ground =
          spec.instances?.find((i: { id: string }) =>
            /^(ground|floor|site|base|terrain|platform)/i.test(i.id),
          ) || spec.instances?.[0];
        if (!ground) return false;
        const instance: import("../runtime/types").RuntimeInstance = {
          ...ground,
          id: "ground",
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          enabled: true,
        };
        delete instance.parent;
        delete instance.attach;
        delete instance.repeat;
        spec.instances = [instance];
        delete spec.exports;
        delete spec.rigid_controls;
        delete spec.joints;
        spec.metadata = {
          level: 4,
          scene: {
            title: name,
            units: "m",
            layers: {
              ground: { label: "地台", visible: true, locked: true },
              objects: { label: "场景对象", visible: true },
            },
            regions: { site: { label: "全场地" } },
            objects: {
              ground: {
                label: "基础地台",
                layer: "ground",
                region: "site",
                locked: false,
                hidden: false,
              },
            },
          },
        };
      } else {
        spec.metadata = {
          ...spec.metadata,
          scene: {
            ...(typeof spec.metadata?.scene === "object"
              ? spec.metadata.scene
              : {}),
            title: name,
          },
        };
      }
      const asset = {
        ...(template ?? {}),
        id,
        name,
        level: 4,
        local: true,
        kit: spec,
        dynamic: true,
        glb: undefined,
      };
      if (await api.select(asset)) {
        store.setState((s) => ({
          data: { ...s.data, assets: [asset, ...s.data.assets] },
          dirty: true,
        }));
        store.getState().setFilters({ workspace: "scene" });
        draft(asset, spec);
        return true;
      }
      return false;
    },
    dispose() {
      api.cancel();
      api.cancelBatch();
      loader?.dispose();
    },
  };
  return api;
}
export type Session = ReturnType<typeof createSession>;
