import { useEffect, useLayoutEffect, useState } from "react";
import { useStore } from "zustand";
import { Button } from "../ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "../ui/sheet";
import { Menu, RotateCw } from "lucide-react";
import type { StudioStore } from "./store";
import type { Asset } from "./types";
import { LibraryShell } from "./library/LibraryShell";
import { WorkbenchHeader, WorkbenchRail } from "./WorkbenchChrome";
import { ResourceNavigation } from "./library/ResourceNavigation";

export function CatalogStartup({
  store,
  scrollPosition,
  focusSearch,
  error,
  onRetry,
  onSelect,
  onOpenScene,
}: {
  store: StudioStore;
  scrollPosition: { current: number };
  focusSearch: { current: boolean };
  error: string;
  onRetry(): void;
  onSelect(asset: Asset): void;
  onOpenScene(asset: Asset): void;
}) {
  const state = useStore(store);
  const [navOpen, setNavOpen] = useState(false);
  const preview =
    state.current ||
    state.data.assets.find((asset) => asset.level === 3) ||
    state.data.assets[0];
  useEffect(() => {
    document.body.dataset.theme = state.prefs.theme;
  }, [state.prefs.theme]);
  useLayoutEffect(
    () => () => {
      scrollPosition.current =
        document.getElementById("catalog")?.scrollTop || 0;
      focusSearch.current = document.activeElement?.id === "search";
    },
    [focusSearch, scrollPosition],
  );
  const newScene = () => store.setState({ dialog: "new-scene" });
  return (
    <div
      className="studio-app is-library startup-catalog"
      style={
        {
          "--left-width": state.prefs.leftWidth + "px",
          "--right-width": state.prefs.rightWidth + "px",
        } as React.CSSProperties
      }
    >
      <WorkbenchHeader
        store={store}
        ready={false}
        onScene={() => {
          const asset = state.data.assets.find((asset) => asset.level === 4);
          if (asset) onOpenScene(asset);
          else newScene();
        }}
      />
      <div className="workbench-layout">
        <WorkbenchRail
          store={store}
          ready={false}
          onScene={() => {
            const asset = state.data.assets.find((asset) => asset.level === 4);
            if (asset) onOpenScene(asset);
            else newScene();
          }}
        />
        <div className="library-shell-slot">
          <LibraryShell
            store={store}
            loading
            onSelect={onSelect}
            onOpenScene={onOpenScene}
            onNewScene={newScene}
            onBatchExport={() =>
              store.getState().notify("实时预览加载后可批量导出。")
            }
          />
        </div>
        <div className="viewport-slot">
          <div className="inspector-heading">属性检查器</div>
          <section className="stage-wrap" aria-label="模型预览准备中">
            <div className="stage-toolbar">
              <span>
                {error ? "无法启动实时预览" : "图像预览 · 实时模型准备中"}
              </span>
              {error && (
                <Button type="button" variant="outline" onClick={onRetry}>
                  <RotateCw /> 重试
                </Button>
              )}
            </div>
            <div className="startup-catalog__preview">
              {preview?.hero && (
                <img
                  src={preview.hero}
                  alt={`${preview.name || preview.id} 缩略图`}
                />
              )}
            </div>
            <div id="stageFooter">
              {error || "目录可先搜索和筛选，模型会在准备完成后显示。"}
            </div>
          </section>
        </div>
        <aside className="inspector-panel startup-catalog__inspector">
          <div className="inspector-top">
            <small>当前资产</small>
            <h3>{preview?.name || "选择资产"}</h3>
            <code>{preview?.id || ""}</code>
            <p>
              {state.dialog === "new-scene"
                ? "加载完成后将打开新建场景。"
                : "可先浏览资源；属性与编辑工具正在准备。"}
            </p>
          </div>
        </aside>
      </div>
      <footer className="statusbar">
        <Button
          id="mobileNav"
          variant="outline"
          onClick={() => setNavOpen(true)}
        >
          <Menu /> 导航
        </Button>
        <span>本地工作空间</span>
        <span id="statusDocument">{preview?.name || "选择资产"}</span>
        <span id="statusHint">{state.notice || "资源目录已可使用"}</span>
      </footer>
      <Sheet open={navOpen} onOpenChange={setNavOpen}>
        <SheetContent
          side="left"
          className="mobile-studio-sheet startup-catalog__sheet"
        >
          <SheetHeader>
            <SheetTitle>工作空间导航</SheetTitle>
            <SheetDescription>选择资源类别或创建场景。</SheetDescription>
          </SheetHeader>
          <ResourceNavigation store={store} onNewScene={newScene} />
        </SheetContent>
      </Sheet>
    </div>
  );
}
