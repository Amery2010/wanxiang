import { useState } from "react";
import { Command } from "lucide-react";
import { Button } from "../../ui/button";
import { useStore } from "zustand";
import type { Asset } from "../types";
import type { LibraryProps } from "./types";
import { asLibraryAsset } from "./types";
import { ResourceNavigation } from "./ResourceNavigation";
import { AssetCatalog } from "./AssetCatalog";
import { CachePanel } from "./CachePanel";
import { CommandPalette } from "./CommandPalette";
import { CompareDialog } from "./CompareDialog";
import { TasksPanel } from "./TasksPanel";

export function LibraryShell({
  store,
  loading = false,
  onSelect,
  onNewScene,
  onBatchExport,
  onOpenScene,
  onShowInspector,
  onShowTasks,
  onShowCache,
  bridge,
  className = "",
}: LibraryProps) {
  const dialog = useStore(store, (state) => state.dialog);
  const currentId = useStore(store, (state) => state.current?.id);
  const batchProgress = useStore(store, (state) => state.batchProgress);
  const theme = useStore(store, (state) => state.prefs.theme);
  const [compareAssets, setCompareAssets] = useState<Asset[]>([]);
  const closeDialog = () => store.setState({ dialog: null });
  const openDialog = (name: string) => store.setState({ dialog: name });
  const showTasks = () => {
    onShowTasks?.();
    openDialog("tasks");
  };
  const showCache = () => {
    onShowCache?.();
    openDialog("cache");
  };
  const resolvedOpenScene = onOpenScene ?? bridge?.onOpenScene;

  return (
    <div
      className={`library-shell ${className}`.trim()}
      data-library-theme={theme}
    >
      <ResourceNavigation
        store={store}
        onNewScene={onNewScene}
        onShowTasks={loading ? undefined : showTasks}
        onShowCache={loading ? undefined : showCache}
      />
      <main className="library-shell__main">
        <div className="library-shell__command-row">
          <Button
            variant="ghost"
            className="library-command-trigger"
            onClick={() => openDialog("command")}
          >
            <Command />
            <span>搜索资产或命令</span>
            <kbd>⌘ K</kbd>
          </Button>
        </div>
        <AssetCatalog
          store={store}
          onSelect={onSelect}
          onNewScene={onNewScene}
          onBatchExport={onBatchExport}
          onOpenScene={resolvedOpenScene}
          onOpenMaterial={bridge?.onMaterial}
          onShowInspector={onShowInspector}
          onCompare={(assets) => {
            setCompareAssets(assets);
            openDialog("compare");
          }}
        />
      </main>
      <CommandPalette
        store={store}
        open={dialog === "command"}
        onClose={closeDialog}
        onSelect={onSelect}
        onNewScene={onNewScene}
        onOpenScene={resolvedOpenScene}
      />
      <CompareDialog
        assets={compareAssets}
        open={dialog === "compare"}
        onClose={closeDialog}
        onSelect={(asset) => onSelect(asLibraryAsset(asset))}
      />
      {!loading && (
        <TasksPanel
          tasks={bridge?.tasks}
          onRetryFailed={bridge?.onRetryFailed}
          progress={batchProgress}
          open={dialog === "tasks"}
          onClose={closeDialog}
        />
      )}
      {!loading && (
        <CachePanel
          cache={bridge?.cache}
          assetId={currentId}
          open={dialog === "cache"}
          onClose={closeDialog}
        />
      )}
    </div>
  );
}

export default LibraryShell;
