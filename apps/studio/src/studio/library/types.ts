import type { BuildCache, BuildTasks } from "../../runtime/types";
import type { Asset, Data, Spec } from "../types";
import type { StudioState, StudioStore } from "../store";

/** Callbacks at the seam between the library UI and the runtime/editor. */
export interface LibraryBridge {
  tasks?: BuildTasks | null;
  cache?: BuildCache | null;
  /** Open a material detail surface owned by the host. */
  onMaterial?(material: Spec): void;
  /** Open the selected scene in the scene workspace. */
  onOpenScene?(asset: Asset): void;
  /** Retry failed builds from the host task queue. */
  onRetryFailed?(): void;
}

export interface LibraryProps {
  store: StudioStore;
  loading?: boolean;
  onSelect(asset: Asset): void;
  onNewScene?(): void;
  onBatchExport?(onlyChanged: boolean): void;
  onOpenScene?(asset: Asset): void;
  onShowInspector?(): void;
  onShowTasks?(): void;
  onShowCache?(): void;
  bridge?: LibraryBridge;
  className?: string;
}

export interface NavigationProps {
  store: StudioStore;
  onNewScene?(): void;
  onShowTasks?(): void;
  onShowCache?(): void;
}

export interface CatalogProps {
  store: StudioStore;
  onSelect(asset: Asset): void;
  onNewScene?(): void;
  onBatchExport?(onlyChanged: boolean): void;
  onOpenScene?(asset: Asset): void;
  onOpenMaterial?(material: MaterialRecord): void;
  onShowInspector?(): void;
  onCompare?(assets: Asset[]): void;
}

export interface CommandPaletteProps {
  store: StudioStore;
  open: boolean;
  onClose(): void;
  onSelect(asset: Asset): void;
  onNewScene?(): void;
  onOpenScene?(asset: Asset): void;
}

export interface CompareDialogProps {
  assets: Asset[];
  open: boolean;
  onClose(): void;
  onSelect?(asset: Asset): void;
}

export interface TasksPanelProps {
  tasks?: BuildTasks | null;
  open: boolean;
  onClose(): void;
  onRetryFailed?(): void;
  progress?: StudioState["batchProgress"];
}

export interface CachePanelProps {
  cache?: BuildCache | null;
  assetId?: string;
  open: boolean;
  onClose(): void;
}

export interface MaterialDialogProps {
  material: MaterialRecord | null;
  onClose(): void;
}

export interface MaterialRecord extends Spec {
  id: string;
  name?: string;
  preview?: string;
}

export type LibraryAsset = Asset & {
  id: string;
  name?: string;
  hero?: string;
  level?: number;
  game_expansion?: boolean;
  game_kit?: string;
  local?: boolean;
  report?: Record<string, unknown>;
  runtime?: Record<string, unknown>;
};

export function asLibraryAsset(asset: Asset): LibraryAsset {
  return asset as LibraryAsset;
}

export function dataAssets(data: Data): LibraryAsset[] {
  return data.assets.map(asLibraryAsset);
}

export function dataMaterials(data: Data): MaterialRecord[] {
  const source = data.materials;
  if (Array.isArray(source)) {
    return source.filter(isMaterialRecord);
  }
  if (source && typeof source === "object") {
    return Object.entries(source)
      .map(([id, value]) => ({
        ...(value as Spec),
        id: typeof (value as Spec).id === "string" ? (value as Spec).id : id,
      }))
      .filter(isMaterialRecord);
  }
  return [];
}

function isMaterialRecord(value: unknown): value is MaterialRecord {
  return Boolean(
    value &&
    typeof value === "object" &&
    typeof (value as { id?: unknown }).id === "string",
  );
}
