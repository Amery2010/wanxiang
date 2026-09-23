import type {
  RuntimeAsset,
  RuntimeSpec,
  RuntimeData,
  RuntimeInstance,
  StudioRuntime,
} from "../runtime/types";
export type Asset = RuntimeAsset;
export type Spec = RuntimeSpec;
export type Data = RuntimeData;
export interface Preferences {
  favorites: string[];
  recent: string[];
  view: string;
  theme: string;
  sort: string;
  leftWidth: number;
  rightWidth: number;
  snap: boolean;
  snapMove: number;
  snapRotate: number;
  snapScale: number;
}
export interface Filters {
  workspace: "library" | "scene";
  level: string;
  domain: string;
  theme: string;
  collection: string;
  gameKit: string;
  query: string;
  sort: string;
  page: number;
  pageSize: number;
  motion: string;
  lod: string;
  collision: string;
  budget: string;
  interface: string;
  tag: string;
  compatibleIds: string[] | null;
}
export interface SceneObject extends RuntimeInstance {
  id: string;
  part?: string;
  assembly?: string;
  position: number[];
  rotation: number[];
  scale: number[];
  enabled?: boolean;
  parent?: string;
  params?: Record<string, unknown>;
  style?: string;
}
export interface SceneMeta {
  label: string;
  layer: string;
  region: string;
  group?: string;
  hidden: boolean;
  locked: boolean;
}
export interface SceneDocument extends Spec {
  id: string;
  name?: string;
  instances: SceneObject[];
  metadata: {
    scene: {
      title: string;
      objects: Record<string, SceneMeta>;
      layers: Record<
        string,
        { label: string; visible: boolean; locked?: boolean }
      >;
      regions: Record<string, { label: string }>;
      groups: Record<
        string,
        { label: string; hidden: boolean; locked: boolean }
      >;
    };
  };
}
export interface Core {
  domains: { id: string; label: string }[];
  themes: Record<string, string>;
  levels: Record<string, { label: string; long: string }>;
  defaultPrefs: Preferences;
  cleanPrefs(value: unknown): Preferences;
  storage<T>(key: string, fallback: T): T;
  save(key: string, value: unknown): boolean;
  filter(
    assets: Asset[],
    filters: Partial<Filters>,
    prefs: Preferences,
  ): Asset[];
  domain(asset: Asset): string;
  counts(assets: Asset[]): {
    total: number;
    levels: Record<string, number>;
    domains: Record<string, number>;
  };
}
export interface SceneAPI {
  normalize(source: Spec, catalog?: Record<string, Spec>): SceneDocument;
  apply(
    source: Spec,
    command: Record<string, unknown>,
    catalog: Record<string, Spec>,
  ): SceneDocument;
  subset(
    source: Spec,
    query: Record<string, unknown>,
    catalog: Record<string, Spec>,
  ): SceneDocument;
  locked(source: Spec, id: string): boolean;
  descendants(source: Spec, ids: string[]): Set<string>;
}
export const core = () =>
  (globalThis as unknown as { WXStudioCore: Core }).WXStudioCore;
export const sceneAPI = () =>
  (globalThis as unknown as { WXSceneDocument: SceneAPI }).WXSceneDocument;
export type Runtime = StudioRuntime;
