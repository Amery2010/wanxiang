import { useStore } from "zustand";
import {
  Box,
  Clock3,
  Download,
  Grid2X2,
  HelpCircle,
  Layers,
  ListChecks,
  Moon,
  Palette,
  Save,
  Search,
  Settings2,
  Star,
  Sun,
  Upload,
} from "lucide-react";
import { Button } from "../ui/button";
import type { StudioStore } from "./store";

interface ChromeProps {
  store: StudioStore;
  ready?: boolean;
  onScene(): void;
  onImport?(): void;
  onExport?(): void;
  onSave?(): void;
}

export function WorkbenchHeader({
  store,
  ready = true,
  onScene,
  onImport,
  onExport,
  onSave,
}: ChromeProps) {
  const s = useStore(store);
  const scene = s.filters.workspace === "scene";
  return (
    <header className="app-header">
      <a
        className="brand"
        aria-label="万象工坊 3D 首页"
        href="#"
        onClick={(event) => {
          event.preventDefault();
          s.setFilters({ workspace: "library" });
        }}
      >
        <Box />
        <div>
          <strong>
            万象工坊 <em>3D</em>
          </strong>
          <small>WANXIANG STUDIO</small>
        </div>
      </a>
      <nav className="workspace-nav" aria-label="工作空间">
        <Button
          id="gotoLibrary"
          variant="ghost"
          aria-current={!scene ? "page" : undefined}
          onClick={() => s.setFilters({ workspace: "library" })}
        >
          资产资源库
        </Button>
        <Button
          id="gotoScene"
          variant="ghost"
          aria-current={scene ? "page" : undefined}
          onClick={onScene}
        >
          场景工作台
        </Button>
      </nav>
      <Button
        id="commandsBtn"
        variant="outline"
        aria-label="打开命令面板"
        onClick={() => store.setState({ dialog: "command" })}
      >
        <Search />
        <span>搜索资产或命令</span>
        <kbd>⌘ K</kbd>
      </Button>
      <div className="header-actions">
        <Button
          id="themeBtn"
          variant="ghost"
          aria-label="切换主题"
          onClick={() =>
            s.setPrefs({ theme: s.prefs.theme === "dark" ? "light" : "dark" })
          }
        >
          {s.prefs.theme === "dark" ? <Sun /> : <Moon />}
        </Button>
        <Button
          id="helpBtn"
          variant="ghost"
          aria-label="使用帮助"
          disabled={!ready}
          onClick={() => store.setState({ dialog: "help" })}
        >
          <HelpCircle />
        </Button>
        <Button
          id="importBtn"
          variant="ghost"
          aria-label="导入 GLB"
          disabled={!ready}
          onClick={onImport}
        >
          <Upload />
          <span>导入</span>
        </Button>
        {scene && (
          <Button
            id="saveSceneTop"
            aria-label="保存场景"
            variant="outline"
            disabled={!ready || s.busy}
            onClick={onSave}
          >
            <Save />
            <span>保存场景</span>
          </Button>
        )}
        <Button
          id="exportBtn"
          className="primary"
          aria-label="导出模型"
          disabled={!ready || !s.current || s.busy}
          onClick={onExport}
        >
          <Download />
          <span>导出 GLB</span>
        </Button>
      </div>
    </header>
  );
}

export function WorkbenchRail({ store, ready = true, onScene }: ChromeProps) {
  const s = useStore(store);
  const library = (collection: string) =>
    s.setFilters({
      workspace: "library",
      collection,
      query: "",
      level: "all",
      domain: "all",
      theme: "all",
      gameKit: "all",
      motion: "all",
      lod: "all",
      collision: "all",
      budget: "all",
      interface: "all",
      tag: "",
      compatibleIds: null,
    });
  return (
    <nav className="app-rail" aria-label="主导航">
      <div className="rail-main">
        <Button
          variant="ghost"
          className="rail-button"
          aria-label="资产资源库"
          aria-current={
            s.filters.workspace === "library" && s.filters.collection === "all"
              ? "page"
              : undefined
          }
          onClick={() => library("all")}
        >
          <Grid2X2 />
          <span>资源</span>
        </Button>
        <Button
          variant="ghost"
          className="rail-button"
          aria-label="场景工作台"
          aria-current={s.filters.workspace === "scene" ? "page" : undefined}
          onClick={onScene}
        >
          <Layers />
          <span>场景</span>
        </Button>
        <div className="rail-divider" />
        {(
          [
            ["favorites", "收藏", Star],
            ["recent", "最近", Clock3],
            ["materials", "材质", Palette],
          ] as const
        ).map(([collection, label, Icon]) => (
          <Button
            key={collection}
            variant="ghost"
            className="rail-button"
            aria-label={label}
            aria-current={
              s.filters.workspace === "library" &&
              s.filters.collection === collection
                ? "page"
                : undefined
            }
            onClick={() => library(collection)}
          >
            <Icon />
            <span>{label}</span>
          </Button>
        ))}
      </div>
      <div className="rail-bottom">
        <Button
          id="tasksBtn"
          variant="ghost"
          className="rail-button"
          aria-label="打开构建任务"
          disabled={!ready}
          onClick={() =>
            store.setState({ dialog: s.dialog === "tasks" ? null : "tasks" })
          }
        >
          <ListChecks />
          <span>任务</span>
        </Button>
        <Button
          id="cacheBtn"
          variant="ghost"
          className="rail-button"
          aria-label="打开缓存"
          disabled={!ready}
          onClick={() => store.setState({ dialog: "cache" })}
        >
          <Settings2 />
          <span>设置</span>
        </Button>
        <span className="local-dot" aria-label="本地工作空间" />
      </div>
    </nav>
  );
}
