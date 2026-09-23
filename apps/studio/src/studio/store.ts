import { createStore } from "zustand/vanilla";
import {
  core,
  type Asset,
  type Data,
  type Filters,
  type Preferences,
  type Spec,
} from "./types";
export const preferenceKey = "wanxiang.studio.preferences.v35";
export interface DocumentSession {
  current: Asset;
  spec: Spec | null;
  history: Spec[];
  future: Spec[];
  selection: string[];
  dirty: boolean;
}
export interface StudioState {
  focusMode: boolean;
  materialId: string | null;
  runtimeStatus: Record<string, unknown>;
  documents: Record<string, DocumentSession>;
  data: Data;
  prefs: Preferences;
  filters: Filters;
  current: Asset | null;
  spec: Spec | null;
  selection: string[];
  history: Spec[];
  future: Spec[];
  busy: boolean;
  error: string;
  notice: string;
  dirty: boolean;
  tab: string;
  tool: string;
  dialog: string | null;
  batch: string[];
  batchProgress: {
    total: number;
    completed: number;
    failed: number;
    skipped: number;
    running: boolean;
    cancelled: boolean;
  } | null;
  mobilePanel: string | null;
  setFilters(patch: Partial<Filters>): void;
  setPrefs(patch: Partial<Preferences>): void;
  notify(message: string): void;
}
export function createStudioStore(data: Data) {
  const prefs = core().cleanPrefs(core().storage(preferenceKey, {}));
  return createStore<StudioState>()((set, get) => ({
    focusMode: false,
    materialId: null,
    runtimeStatus: {},
    documents: {},
    data,
    prefs,
    filters: {
      workspace: "library",
      level: data.parts ? "3" : "all",
      domain: "all",
      theme: "all",
      collection: "all",
      gameKit: "all",
      query: "",
      sort: prefs.sort,
      page: 1,
      pageSize: 48,
      motion: "all",
      lod: "all",
      collision: "all",
      budget: "all",
      interface: "all",
      tag: "",
      compatibleIds: null,
    },
    current: null,
    spec: null,
    selection: [],
    history: [],
    future: [],
    busy: false,
    error: "",
    notice: "",
    dirty: false,
    tab: "parameters",
    tool: "translate",
    dialog: null,
    batch: [],
    batchProgress: null,
    mobilePanel: null,
    setFilters(patch) {
      const legacyCollection = patch.collection === "game410";
      set((s) => ({
        filters: {
          ...s.filters,
          ...(legacyCollection
            ? {
                level: "all",
                domain: "all",
                theme: "all",
                query: "",
                motion: "all",
                lod: "all",
                gameKit: "all",
                collision: "all",
                budget: "all",
                interface: "all",
                tag: "",
                compatibleIds: null,
              }
            : {}),
          ...patch,
          // Older callers may still request the retired release collection.
          ...(legacyCollection ? { collection: "all", gameKit: "all" } : {}),
          page: patch.page ?? 1,
        },
      }));
    },
    setPrefs(patch) {
      const prefs = core().cleanPrefs({ ...get().prefs, ...patch });
      core().save(preferenceKey, prefs);
      set({ prefs });
    },
    notify(message) {
      set({ notice: message });
    },
  }));
}
export type StudioStore = ReturnType<typeof createStudioStore>;
