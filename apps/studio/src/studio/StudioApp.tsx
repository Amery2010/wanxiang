import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "../ui/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "../ui/tooltip";
import { Button } from "../ui/button";
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { useStore } from "zustand";
import {
  Box,
  Menu,
  PanelRight,
  Grid2X2,
  RotateCw,
  Focus,
  Maximize,
  X,
  Copy,
  Group,
  Trash2,
} from "lucide-react";
import { createStudioRuntime } from "../runtime";
import { createStudioStore } from "./store";
import { createSession, type Session } from "./session";
import { Inspector } from "./Inspector";
import { SceneTree, SceneTools, Shelf } from "./Scene";
import { MaterialDialog } from "./MaterialDialog";
import { WorkbenchDialogs } from "./WorkbenchDialogs";
import { AssetPicker } from "./AssetPicker";
import { SceneDialogs } from "./SceneDialogs";
import { LibraryShell } from "./library/LibraryShell";
import { WorkbenchHeader, WorkbenchRail } from "./WorkbenchChrome";
import { CatalogStartup } from "./CatalogStartup";
import { core, sceneAPI, type Data, type SceneDocument } from "./types";
function ResizeHandle({
  session,
  side,
}: {
  session: Session;
  side: "left" | "right";
}) {
  const key = side === "left" ? "leftWidth" : "rightWidth";
  const width = useStore(session.store, (state) => state.prefs[key]);
  const active = useRef<{ x: number; width: number } | null>(null);
  const min = side === "left" ? 180 : 270;
  const max = side === "left" ? 360 : 470;
  const cssKey = side === "left" ? "--left-width" : "--right-width";
  const clamp = (value: number) => Math.min(max, Math.max(min, value));
  const pointerWidth = (x: number) =>
    clamp(
      active.current!.width +
        (x - active.current!.x) * (side === "left" ? 1 : -1),
    );
  return (
    <div
      id={side + "Resize"}
      className={"panel-resizer " + side}
      role="separator"
      tabIndex={0}
      aria-label={side === "left" ? "调整导航面板宽度" : "调整属性面板宽度"}
      aria-orientation="vertical"
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={width}
      onKeyDown={(e) => {
        if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
          e.preventDefault();
          session.store.getState().setPrefs({
            [key]: clamp(
              width +
                (e.key === "ArrowRight" ? 10 : -10) *
                  (side === "left" ? 1 : -1),
            ),
          });
        }
      }}
      onPointerDown={(e) => {
        active.current = {
          x: e.clientX,
          width: session.store.getState().prefs[key],
        };
        e.currentTarget.setPointerCapture(e.pointerId);
      }}
      onPointerMove={(e) => {
        if (active.current)
          e.currentTarget
            .closest<HTMLElement>(".studio-app")
            ?.style.setProperty(cssKey, pointerWidth(e.clientX) + "px");
      }}
      onPointerUp={(e) => {
        if (!active.current) return;
        const nextWidth = pointerWidth(e.clientX);
        active.current = null;
        e.currentTarget.releasePointerCapture(e.pointerId);
        if (nextWidth !== width)
          session.store.getState().setPrefs({ [key]: nextWidth });
      }}
      onPointerCancel={(e) => {
        active.current = null;
        e.currentTarget
          .closest<HTMLElement>(".studio-app")
          ?.style.setProperty(cssKey, width + "px");
      }}
    />
  );
}
function Viewport({ session }: { session: Session }) {
  const s = useStore(session.store),
    stage = useRef<HTMLDivElement>(null),
    cpu = useRef<HTMLCanvasElement>(null),
    grid = useRef<SVGSVGElement>(null),
    overlay = useRef<SVGSVGElement>(null),
    fallback = useRef<HTMLImageElement>(null),
    [wire, setWire] = useState(false),
    [showGrid, setShowGrid] = useState(true);
  useEffect(() => {
    if (!stage.current || !cpu.current) return;
    return session.runtime.mount({
      stage: stage.current,
      cpuCanvas: cpu.current,
      worldGrid: grid.current ?? undefined,
      editorOverlay: overlay.current ?? undefined,
      fallback: fallback.current ?? undefined,
    });
  }, [session]);
  return (
    <section id="stageWrap" className="stage-wrap">
      <div className="stage-toolbar">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              id="previewExpand"
              variant="outline"
              aria-label="放大或还原预览"
              onClick={() =>
                session.store.setState({ focusMode: !s.focusMode })
              }
            >
              <Maximize />
            </Button>
          </TooltipTrigger>
          <TooltipContent>放大 / 还原预览</TooltipContent>
        </Tooltip>
        <span id="rendererBadge">
          {s.busy
            ? "正在生成…"
            : String(s.runtimeStatus.renderer || "实时预览")}
        </span>
        <select
          id="lightingPreset"
          aria-label="预览灯光"
          onChange={(e) => session.runtime.setLighting(e.target.value)}
        >
          <option value="studio">柔和日光</option>
          <option value="neutral">中性灰模</option>
          <option value="night">夜景</option>
        </select>
        <Button
          id="cancelPreview"
          variant="outline"
          disabled={!s.busy}
          onClick={() => session.cancel()}
          aria-label="取消预览生成"
        >
          <X />
        </Button>
      </div>
      <div
        id="stage"
        ref={stage}
        tabIndex={0}
        aria-label="三维视口。拖动旋转，右键平移，滚轮缩放。"
        aria-busy={s.busy}
      >
        <img id="fallback" ref={fallback} alt="当前模型实际网格预览" hidden />
        <canvas id="cpuCanvas" ref={cpu} />
        <svg id="worldGrid" ref={grid} aria-hidden="true" />
        <svg id="editorOverlay" ref={overlay} aria-hidden="true" />
        <div id="viewCube" className="view-cube">
          {(
            [
              ["前", 0, 0],
              ["右", 90, 0],
              ["顶", 0, 89],
              ["等距", 36, 32],
            ] as const
          ).map(([label, az, el]) => (
            <Button
              key={label}
              variant="outline"
              aria-label={label + "视图"}
              onClick={() => session.runtime.setView({ az, el })}
            >
              {label}
            </Button>
          ))}
        </div>
        {s.filters.workspace === "scene" && s.selection.length > 0 && (
          <div className="selected-toolbar" aria-label="所选对象操作">
            <span>{s.selection.length} 个对象</span>
            <Button
              variant="ghost"
              aria-label="聚焦所选"
              onClick={() => session.runtime.focusSelection()}
            >
              <Focus />
            </Button>
            <Button
              variant="ghost"
              aria-label="复制所选"
              disabled={s.busy}
              onClick={() =>
                void session.command({
                  type: "duplicate-many",
                  ids: s.selection,
                })
              }
            >
              <Copy />
            </Button>
            <Button
              variant="ghost"
              aria-label="编组所选"
              disabled={s.busy}
              onClick={() => session.requestGroup()}
            >
              <Group />
            </Button>
            <Button
              variant="ghost"
              aria-label="删除所选"
              disabled={s.busy}
              onClick={() => session.requestDelete()}
            >
              <Trash2 />
            </Button>
          </div>
        )}
        <div className="stage-tip">拖动旋转 · 右键平移 · 滚轮缩放</div>
        <div className="viewport-controls">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                id="wireBtn"
                variant="outline"
                aria-label="切换线框"
                aria-pressed={wire}
                onClick={() => {
                  setWire(!wire);
                  session.runtime.setWire(!wire);
                }}
              >
                <Box />
              </Button>
            </TooltipTrigger>
            <TooltipContent>切换线框</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                id="gridBtn"
                variant="outline"
                aria-label="切换辅助网格"
                aria-pressed={showGrid}
                onClick={() => {
                  setShowGrid(!showGrid);
                  session.runtime.setGrid(!showGrid);
                }}
              >
                <Grid2X2 />
              </Button>
            </TooltipTrigger>
            <TooltipContent>切换辅助网格</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                id="orbitBtn"
                variant="outline"
                aria-label="旋转视角"
                onClick={() => {
                  const v = session.runtime.getView();
                  session.runtime.setView({ ...v, az: v.az + 45 });
                }}
              >
                <RotateCw />
              </Button>
            </TooltipTrigger>
            <TooltipContent>旋转视角</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                id="resetBtn"
                variant="outline"
                aria-label="适配全部对象"
                onClick={() => session.runtime.fit()}
              >
                <Focus />
              </Button>
            </TooltipTrigger>
            <TooltipContent>适配全部对象</TooltipContent>
          </Tooltip>
        </div>
      </div>
      <div id="stageFooter">
        <span>
          {s.current?.report?.triangles?.toLocaleString() ?? "—"} TRIANGLES
        </span>
        <span>{String(s.current?.report?.nodes ?? "—")} NODES</span>
        <span>
          {s.current?.glb
            ? ((s.current.glb.length * 0.75) / 1024).toFixed(0) + " KB"
            : "按需生成"}
        </span>
        <span className="stage-format">
          {s.current?.glb ? "ACTUAL GLB" : "PREVIEW"}
        </span>
      </div>
    </section>
  );
}
function Workbench({ session }: { session: Session }) {
  const [mobile, setMobile] = useState(() => window.innerWidth <= 800);
  const [compactNav, setCompactNav] = useState(() => window.innerWidth <= 920);
  useEffect(() => {
    const resize = () => {
      setMobile(window.innerWidth <= 800);
      setCompactNav(window.innerWidth <= 920);
    };
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);
  const taskBridge = useMemo(() => {
    const tasks = session.runtime.tasks;
    if (!tasks) return null;
    return {
      setConcurrency: tasks.setConcurrency?.bind(tasks),
      submit: tasks.submit.bind(tasks),
      snapshot: () => ({
        ...tasks.snapshot(),
        retryableCount: session.retryableCount(),
      }),
      cancel: tasks.cancel.bind(tasks),
      cancelAll: () => {
        session.cancel();
        session.cancelBatch();
        tasks.cancelAll();
      },
    };
  }, [session]);
  const [inspectorCollapsed, setInspectorCollapsed] = useState(false);
  const lastMobilePanel = useRef("nav");
  const s = useStore(session.store),
    scene = s.filters.workspace === "scene" && s.current?.level === 4;
  const openScene = async () => {
    const state = session.store.getState();
    if (state.current?.level === 4) {
      state.setFilters({ workspace: "scene" });
      return;
    }
    const asset =
      Object.values(state.documents)
        .reverse()
        .find((doc) => doc.current.level === 4)?.current ||
      state.data.assets.find((asset) => asset.level === 4);
    if (asset && (await session.select(asset)))
      session.store.getState().setFilters({ workspace: "scene" });
    else if (!asset) session.store.setState({ dialog: "new-scene" });
  };
  const navAvailable = scene ? mobile : compactNav;
  useEffect(() => {
    if (
      (s.mobilePanel === "nav" && !navAvailable) ||
      (s.mobilePanel === "inspector" && !mobile)
    )
      session.store.setState({ mobilePanel: null });
  }, [mobile, navAvailable, s.mobilePanel, session]);
  if (s.mobilePanel) lastMobilePanel.current = s.mobilePanel;
  useEffect(() => {
    const globals = globalThis as unknown as {
      WX_QA?: Record<string, unknown>;
    };
    if (globals.WX_QA) {
      globals.WX_QA.building = s.busy;
      globals.WX_QA.buildError = s.error || null;
    }
  }, [s.busy, s.error]);
  useEffect(() => session.runtime.selectionChanged(), [session, s.selection]);
  useEffect(() => {
    document.body.dataset.theme = s.prefs.theme;
  }, [s.prefs.theme]);
  useEffect(() => {
    session.runtime.bindEditor(
      scene
        ? {
            getState: () => {
              const current = session.store.getState();
              return {
                doc: current.spec || {},
                ids: current.selection,
                tool: current.tool as
                  "select" | "translate" | "rotate" | "scale",
                ...current.prefs,
                busy: current.busy,
              };
            },
            select: (ids, opt) => session.selectObjects(ids, opt?.toggle),
            command: (command) => session.command(command),
            insert: (ref, position) => {
              void session.command({ type: "add", ref, position });
            },
            context: () => session.store.setState({ dialog: "scene-context" }),
          }
        : null,
    );
    return () => session.runtime.bindEditor(null);
  }, [scene, session]);
  useEffect(() => {
    let clipboard: Record<string, unknown> | null = null;
    function keyboard(e: KeyboardEvent) {
      if (
        e.defaultPrevented ||
        (e.target instanceof Element &&
          e.target.closest('input,textarea,select,[contenteditable="true"]')) ||
        session.store.getState().mobilePanel ||
        session.store.getState().dialog
      )
        return;
      const state = session.store.getState(),
        ctrl = e.ctrlKey || e.metaKey,
        k = e.key.toLowerCase();
      if (ctrl && k === "k") {
        e.preventDefault();
        session.store.setState({ dialog: "command" });
        return;
      }
      if (k === "/" && !ctrl) {
        e.preventDefault();
        if (state.filters.workspace === "scene")
          session.store.setState({ dialog: "command" });
        else document.getElementById("search")?.focus();
        return;
      }
      if (e.key === "Escape" && state.focusMode) {
        session.store.setState({ focusMode: false });
        return;
      }
      if (state.filters.workspace !== "scene") return;
      const ids = state.selection,
        doc = state.spec as SceneDocument | null;
      if (ctrl) {
        if (["z", "y", "s", "d", "a", "c", "v", "g"].includes(k))
          e.preventDefault();
        if (k === "z") void (e.shiftKey ? session.redo() : session.undo());
        if (k === "y") void session.redo();
        if (k === "s") session.save();
        if (k === "d") void session.command({ type: "duplicate-many", ids });
        if (k === "g") session.requestGroup();
        if (k === "a" && doc)
          session.selectObjects(
            doc.instances.filter((i) => i.enabled !== false).map((i) => i.id),
          );
        if (k === "c" && doc) {
          const selected = sceneAPI().descendants(doc, ids);
          clipboard = {
            instances: doc.instances.filter((i) => selected.has(i.id)),
            objects: Object.fromEntries(
              [...selected].map((id) => [id, doc.metadata.scene.objects[id]]),
            ),
          };
        }
        if (k === "v" && clipboard)
          void session.command({ type: "paste", ...clipboard });
        return;
      }
      if (["q", "w", "e", "r"].includes(k)) {
        e.preventDefault();
        session.store.setState({
          tool: (
            { q: "select", w: "translate", e: "rotate", r: "scale" } as Record<
              string,
              string
            >
          )[k],
        });
      }
      if (e.key === "Delete" || e.key === "Backspace") {
        e.preventDefault();
        session.requestDelete(ids);
      }
      if (k === "f" || e.key === "Home") {
        e.preventDefault();
        if (k === "f") session.runtime.focusSelection();
        else session.runtime.fit();
      }
      if (k === "h")
        void session.command({ type: "visibility", ids, visible: false });
      if (e.key === "Escape") {
        if (!session.runtime.cancelInteraction()) session.selectObjects([]);
      }
    }
    const unload = (e: BeforeUnloadEvent) => {
      if (
        session.store.getState().dirty ||
        Object.values(session.store.getState().documents).some((d) => d.dirty)
      ) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("keydown", keyboard);
    window.addEventListener("beforeunload", unload);
    return () => {
      window.removeEventListener("keydown", keyboard);
      window.removeEventListener("beforeunload", unload);
    };
  }, [session]);
  useEffect(() => {
    const globals = globalThis as unknown as Record<string, unknown>;
    const facade = {
      get: () => session.store.getState().spec,
      apply: session.command,
      import: session.apply,
      select: (id: string | string[]) =>
        session.selectObjects(Array.isArray(id) ? id : [id]),
      undo: session.undo,
      redo: session.redo,
      selection: () => session.store.getState().selection,
      tool: (tool: string) => session.store.setState({ tool }),
      insert: (ref: string, position?: number[]) =>
        session.command({ type: "add", ref, position }),
      save: session.save,
      busy: () => session.store.getState().busy,
    };
    globals.WX_SCENE_QA = facade;
    const editorFacade = {
      isBusy: facade.busy,
      getSelection: facade.selection,
      current: () => ({
        doc: session.store.getState().spec,
        st: { ids: session.store.getState().selection },
        command: session.command,
        select: facade.select,
      }),
      select: facade.select,
      save: session.save,
      assetPicker: () => session.store.setState({ dialog: "scene-picker" }),
      source: () => session.store.setState({ dialog: "scene-source" }),
      insert: facade.insert,
    };
    globals.WXSceneEditor = editorFacade;
    const buildFacade = {
      cache: session.runtime.cache,
      tasks: session.runtime.tasks,
      visible: () =>
        core()
          .filter(
            session.store.getState().data.assets,
            session.store.getState().filters,
            session.store.getState().prefs,
          )
          .map((a) => a.id),
      filter: (key: string, value: string) =>
        session.store.getState().setFilters({ [key]: value }),
      cancelPreview: session.cancel,
      batch: session.exportBatch,
      selectIDs: (ids: string[]) => session.store.setState({ batch: ids }),
      runtimeSidecar: session.runtime.runtimeSidecar,
    };
    globals.WX_BUILD_QA = buildFacade;
    const liveFacade = {
      select: (id: string) => {
        const asset = session.store
          .getState()
          .data.assets.find((a) => a.id === id);
        return asset ? session.select(asset) : Promise.resolve(false);
      },
      compile: async (
        asset: import("./types").Asset,
        spec: import("./types").Spec,
      ) => {
        const prepared = await session.runtime.prepare(asset, spec);
        try {
          return prepared.asset;
        } finally {
          session.runtime.discard(prepared);
        }
      },
      commit: session.apply,
      getSpec: () => structuredClone(session.store.getState().spec),
      getModel: session.runtime.getModel,
      poseTime: session.runtime.poseTime,
      stats: () => session.store.getState().current?.report,
      snapshot: () => session.runtime.snapshot(),
    };
    globals.WX_LIVE_QA = liveFacade;
    const kitFacade = {
      selectPart: (id: string) => session.selectObjects([id]),
      isolateNode: session.runtime.isolateNode,
      resetVisibility: session.runtime.resetVisibility,
      explode: session.runtime.explode,
      exportPart: session.runtime.exportPart,
    };
    globals.WX_KIT_QA = kitFacade;
    const presentationFacade = {
      set: session.runtime.setLighting,
      exportRuntime: session.runtime.exportRuntime,
      stats: () => session.store.getState().runtimeStatus,
    };
    globals.WX_PRESENTATION_QA = presentationFacade;
    globals.WXStudioShell = {
      get state() {
        return session.store.getState().filters;
      },
      get prefs() {
        return session.store.getState().prefs;
      },
      setPrefs: session.store.getState().setPrefs,
      closeModal: () => session.store.setState({ dialog: null }),
    };
    return () => {
      if (globals.WX_SCENE_QA === facade) delete globals.WX_SCENE_QA;
      if (globals.WX_LIVE_QA === liveFacade) delete globals.WX_LIVE_QA;
      if (globals.WX_KIT_QA === kitFacade) delete globals.WX_KIT_QA;
      if (globals.WX_PRESENTATION_QA === presentationFacade)
        delete globals.WX_PRESENTATION_QA;
      delete globals.WXStudioShell;
      if (globals.WXSceneEditor === editorFacade) delete globals.WXSceneEditor;
      if (globals.WX_BUILD_QA === buildFacade) delete globals.WX_BUILD_QA;
    };
  }, [session]);
  return (
    <div
      className={
        "studio-app " +
        (scene ? "is-scene" : "is-library") +
        (s.focusMode ? " focus-mode" : "") +
        (inspectorCollapsed && !mobile ? " inspector-collapsed" : "")
      }
      style={
        {
          "--left-width": s.prefs.leftWidth + "px",
          "--right-width": s.prefs.rightWidth + "px",
        } as React.CSSProperties
      }
    >
      <WorkbenchHeader
        store={session.store}
        onScene={openScene}
        onImport={() => document.getElementById("importFile")?.click()}
        onSave={() => session.save()}
        onExport={() => void session.exportGLB()}
      />
      <input
        id="importFile"
        type="file"
        accept=".glb,model/gltf-binary"
        hidden
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void session.importGLB(file);
          event.target.value = "";
        }}
      />
      <div className={"workbench-layout mobile-" + (s.mobilePanel || "none")}>
        <WorkbenchRail store={session.store} onScene={openScene} />
        <div className="library-shell-slot">
          <LibraryShell
            store={session.store}
            onSelect={(asset: import("./types").Asset) =>
              void session.select(asset)
            }
            onNewScene={() => session.store.setState({ dialog: "new-scene" })}
            onBatchExport={(onlyChanged) => {
              session.store.setState({ dialog: "tasks" });
              void session.exportBatch(onlyChanged);
            }}
            onOpenScene={async (asset) => {
              if (await session.select(asset))
                s.setFilters({ workspace: "scene" });
            }}
            onShowInspector={() =>
              session.store.setState({ mobilePanel: "inspector" })
            }
            bridge={{
              tasks: taskBridge,
              onRetryFailed: () => void session.retryFailed(),
              cache: session.runtime.cache,
              onMaterial: (material) =>
                session.store.setState({
                  dialog: "material",
                  materialId: String(material.id),
                }),
            }}
          />
        </div>
        {scene && !mobile && (
          <aside className="scene-navigation">
            <SceneTree session={session} />
            <ResizeHandle session={session} side="left" />
          </aside>
        )}
        <main className="scene-center" id="sceneWorkspace" hidden={!scene}>
          <SceneTools session={session} />
        </main>
        <div className="viewport-slot">
          {!scene && (
            <div className="inspector-heading">
              <span>属性检查器</span>
              <Button
                variant="ghost"
                aria-label="收起属性面板"
                onClick={() => setInspectorCollapsed(true)}
              >
                <PanelRight />
              </Button>
            </div>
          )}
          <Viewport session={session} />
        </div>
        {scene && (
          <div className="shelf-slot">
            <Shelf session={session} />
          </div>
        )}
        {!mobile && (
          <aside id="inspectorPanel" className="inspector-panel">
            <ResizeHandle session={session} side="right" />
            {scene && (
              <div className="inspector-heading">
                <span>属性检查器</span>
                <Button
                  variant="ghost"
                  aria-label="收起属性面板"
                  onClick={() => setInspectorCollapsed(true)}
                >
                  <PanelRight />
                </Button>
              </div>
            )}
            <Inspector session={session} />
          </aside>
        )}
      </div>
      <Sheet
        open={
          (navAvailable && s.mobilePanel === "nav") ||
          (mobile && s.mobilePanel === "inspector")
        }
        onOpenChange={(open) => {
          if (!open) session.store.setState({ mobilePanel: null });
        }}
      >
        <SheetContent
          side={s.mobilePanel === "inspector" ? "right" : "left"}
          className="mobile-studio-sheet overflow-y-auto"
          onCloseAutoFocus={(event) => {
            event.preventDefault();
            document
              .getElementById(
                lastMobilePanel.current === "inspector"
                  ? "revealInspector"
                  : "mobileNav",
              )
              ?.focus();
          }}
        >
          <SheetHeader>
            <SheetTitle>
              {s.mobilePanel === "inspector" ? "属性检查器" : "工作空间导航"}
            </SheetTitle>
            <SheetDescription>选择内容后可关闭面板返回视口。</SheetDescription>
          </SheetHeader>
          {s.mobilePanel === "inspector" ? (
            <Inspector session={session} />
          ) : scene ? (
            <>
              <div className="mobile-nav-quick-actions">
                <Button
                  onClick={() =>
                    session.store.setState({
                      mobilePanel: null,
                      dialog: "tasks",
                    })
                  }
                >
                  构建任务
                </Button>
                <Button
                  onClick={() =>
                    session.store.setState({
                      mobilePanel: null,
                      dialog: "cache",
                    })
                  }
                >
                  缓存
                </Button>
              </div>
              <SceneTree session={session} />
            </>
          ) : (
            <nav aria-label="移动端资产导航" className="mobile-nav-options">
              <Button
                onClick={() => {
                  s.setFilters({
                    collection: "all",
                    level: "all",
                    domain: "all",
                    theme: "all",
                    query: "",
                    motion: "all",
                    lod: "all",
                    gameKit: "all",
                  });
                  session.store.setState({ mobilePanel: null });
                }}
              >
                全部资产
              </Button>
              {[
                ["favorites", "我的收藏"],
                ["recent", "最近使用"],
                ["custom", "我的资产"],
                ["materials", "材质库"],
              ].map(([collection, label]) => (
                <Button
                  key={collection}
                  onClick={() => {
                    s.setFilters({ collection, level: "all" });
                    session.store.setState({ mobilePanel: null });
                  }}
                >
                  {label}
                </Button>
              ))}
              <h4>资产用途</h4>
              {core().domains.map((domain) => (
                <Button
                  key={domain.id}
                  onClick={() => {
                    s.setFilters({ domain: domain.id });
                    session.store.setState({ mobilePanel: null });
                  }}
                >
                  {domain.label}
                </Button>
              ))}
              <h4>工作台</h4>
              <Button
                onClick={() =>
                  session.store.setState({ mobilePanel: null, dialog: "tasks" })
                }
              >
                构建任务
              </Button>
              <Button
                onClick={() =>
                  session.store.setState({ mobilePanel: null, dialog: "cache" })
                }
              >
                缓存
              </Button>
            </nav>
          )}
        </SheetContent>
      </Sheet>
      <footer className="statusbar">
        <Button
          id="mobileNav"
          variant="outline"
          onClick={() =>
            session.store.setState({
              mobilePanel: s.mobilePanel === "nav" ? null : "nav",
            })
          }
        >
          <Menu />
          导航
        </Button>
        <span>本地工作空间</span>
        <span id="statusDocument">{s.current?.name || "选择资产"}</span>
        <span id="statusHint">
          {s.busy ? "正在生成实际网格…" : "离线可用 · 按需生成 GLB"}
        </span>
        <Button
          id="revealInspector"
          variant="outline"
          onClick={() =>
            mobile
              ? session.store.setState({
                  mobilePanel:
                    s.mobilePanel === "inspector" ? null : "inspector",
                })
              : setInspectorCollapsed((value) => !value)
          }
        >
          <PanelRight />
          属性
        </Button>
      </footer>
      {s.error && (
        <div className="error-banner" role="alert">
          {s.error}
          <Button
            aria-label="关闭错误"
            onClick={() => session.store.setState({ error: "" })}
          >
            <X />
          </Button>
        </div>
      )}
      {s.notice && (
        <div
          id="toast"
          role="status"
          onClick={() => session.store.setState({ notice: "" })}
        >
          {s.notice}
        </div>
      )}
      <SceneDialogs session={session} />
      <AssetPicker session={session} />
      <WorkbenchDialogs session={session} />
      <MaterialDialog session={session} />
    </div>
  );
}
export function StudioApp({
  data,
  loadData,
  loadAsset,
}: {
  data: Data;
  loadData?: () => Promise<Data>;
  loadAsset?: import("./asset-loader").LoadAsset;
}) {
  const [store] = useState(() => {
      const next = createStudioStore(data);
      if (loadData)
        next.setState({
          current:
            data.assets.find((asset) => asset.level === 3) ||
            data.assets[0] ||
            null,
        });
      return next;
    }),
    [session, setSession] = useState<Session | null>(null),
    [loadingError, setLoadingError] = useState(""),
    [attempt, setAttempt] = useState(0),
    requested = useRef<{ id: string; scene: boolean } | null>(null),
    scrollPosition = useRef(0),
    focusSearch = useRef(false);
  useLayoutEffect(() => {
    if (session) {
      const catalog = document.getElementById("catalog");
      if (catalog) catalog.scrollTop = scrollPosition.current;
      if (focusSearch.current && !requested.current?.scene)
        document.getElementById("search")?.focus();
    }
  }, [session]);
  useEffect(() => {
    let cancelled = false;
    let frame = 0;
    let active: Session | null = null;
    let runtime: ReturnType<typeof createStudioRuntime> | null = null;
    setLoadingError("");
    const start = async () => {
      try {
        const full = loadAsset ? data : loadData ? await loadData() : data;
        if (cancelled) return;
        store.setState({ data: full, current: null });
        runtime = createStudioRuntime(full, {
          onStatus: (status) =>
            store.setState((state) => ({
              runtimeStatus: { ...state.runtimeStatus, ...status },
            })),
          onError: (message) => store.setState({ error: message }),
        });
        active = createSession(store, runtime, loadAsset);
        setSession(active);
        const intent = requested.current;
        const initial =
          full.assets.find((asset) => asset.id === intent?.id) ||
          full.assets.find((asset) => asset.level === 3) ||
          full.assets[0];
        if (initial && (!loadAsset || intent))
          void active.select(initial).then((ok) => {
            if (ok && intent?.scene)
              store.getState().setFilters({ workspace: "scene" });
          });
      } catch (error) {
        if (!cancelled) {
          active?.dispose();
          runtime?.dispose();
          active = null;
          runtime = null;
          setLoadingError(
            error instanceof Error ? error.message : String(error),
          );
        }
      }
    };
    if (loadData)
      frame = requestAnimationFrame(() => {
        frame = requestAnimationFrame(() => void start());
      });
    else void start();
    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
      active?.dispose();
      runtime?.dispose();
    };
  }, [attempt, data, loadData, loadAsset, store]);
  return (
    <TooltipProvider delayDuration={300}>
      {session ? (
        <Workbench session={session} />
      ) : loadData ? (
        <CatalogStartup
          store={store}
          scrollPosition={scrollPosition}
          focusSearch={focusSearch}
          error={loadingError}
          onRetry={() => setAttempt((value) => value + 1)}
          onSelect={(asset) => {
            requested.current = { id: asset.id, scene: false };
            store.setState({ current: asset });
          }}
          onOpenScene={(asset) => {
            requested.current = { id: asset.id, scene: true };
            store.setState({ current: asset });
          }}
        />
      ) : (
        <div role={loadingError ? "alert" : "status"}>
          {loadingError || "正在准备万象工坊…"}
        </div>
      )}
    </TooltipProvider>
  );
}
