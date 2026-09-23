import type * as Three from "three";
import type { GLTF, GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import type { GLTFExporter } from "three/addons/exporters/GLTFExporter.js";

import type {
  RuntimeSpec,
  RuntimeAsset,
  RuntimeData,
  BomEntry,
  BuildReport,
  BuildResult,
} from "@wanxiang/runtime/types";
export type {
  ParameterSchema,
  Parameters,
  CollisionRecipe,
  InteractionRecipe,
  RuntimeCapabilities,
  DefinitionRuntime,
  SceneMetadata,
  RuntimeMetadata,
  RuntimeSpec,
  RuntimeInstance,
  BomEntry,
  BuildReport,
  RuntimeAsset,
  MaterialRow,
  RuntimeData,
  BuildResult,
} from "@wanxiang/runtime/types";

export interface ViewState {
  center: number[];
  span: number;
  az: number;
  el: number;
  zoom: number;
}
export interface ViewportElements {
  stage: HTMLElement;
  cpuCanvas: HTMLCanvasElement;
  worldGrid?: SVGSVGElement;
  editorOverlay?: SVGSVGElement;
  fallback?: HTMLImageElement;
}
export interface RuntimeCallbacks {
  onStatus?(status: Record<string, unknown>): void;
  onError?(message: string): void;
  onViewChange?(view: ViewState): void;
}
export interface EditorBridge {
  /** Return current state; no React render or stale closure is needed per pointer frame. */
  getState(): {
    doc: RuntimeSpec;
    ids: string[];
    tool: "select" | "translate" | "rotate" | "scale";
    snap: boolean;
    snapMove: number;
    snapRotate: number;
    snapScale: number;
    busy?: boolean;
  };
  select(ids: string[], options?: { toggle?: boolean }): void;
  command(command: RuntimeSpec, options?: { label: string }): Promise<unknown>;
  insert?(assetId: string, position: number[]): void;
  context?(x: number, y: number): void;
}
export interface BuildCache {
  key(spec: RuntimeSpec): string;
  get(key: string): Promise<{
    buffer: ArrayBuffer;
    payload: Omit<BuildResult, "buffer">;
    cacheSource: string;
  } | null>;
  put(
    key: string,
    spec: RuntimeSpec,
    buffer: ArrayBuffer,
    payload: Omit<BuildResult, "buffer">,
  ): Promise<unknown>;
  remove(key: string): Promise<unknown>;
  stats(): Promise<RuntimeSpec>;
  clean(options?: RuntimeSpec): Promise<number>;
  markExported(key: string): Promise<unknown>;
  wasExported(key: string): Promise<boolean>;
  openPromise?: Promise<IDBDatabase | null>;
}
export interface BuildTasks {
  setConcurrency?(count: number): void;
  submit(
    spec: RuntimeSpec,
    options: { asset: string; level?: number; signal?: AbortSignal },
  ): Promise<BuildResult>;
  cancel(id: number): void;
  cancelAll(): void;
  snapshot(): RuntimeSpec;
}
export type ThreeGlobal = typeof Three & {
  GLTFLoader: typeof GLTFLoader;
  GLTFExporter: typeof GLTFExporter;
};
export interface RuntimeGlobals {
  THREE: ThreeGlobal;
  WXPipeline: {
    prepare(buffer: ArrayBuffer): {
      inspection: {
        doc: { nodes?: unknown[]; materials?: unknown[]; images?: unknown[] };
        triangles?: number;
      };
      load(): Promise<GLTF>;
    };
    inspect(buffer: ArrayBuffer): {
      doc: { nodes?: unknown[]; materials?: unknown[]; images?: unknown[] };
      triangles?: number;
    };
    load(buffer: ArrayBuffer): Promise<GLTF>;
    dispose(root: Three.Object3D): void;
  };
  WXBuildExport?: typeof import("@wanxiang/runtime/modules/build-export").default;
  WXRuntime?: {
    Library: new (data: RuntimeData) => {
      build(spec: RuntimeSpec): Promise<{
        root: Three.Object3D;
        bom: BomEntry[];
        report: BuildReport;
      }>;
      clips(root: Three.Object3D, id?: string): Three.AnimationClip[];
    };
  };
  WXBuildCache?: {
    Cache: new (
      data: RuntimeData,
      hash: (input: Uint8Array) => string,
    ) => BuildCache;
  };
  WXBuildTasks?: {
    Tasks: new (
      data: RuntimeData,
      build: (spec: RuntimeSpec, signal?: AbortSignal) => Promise<BuildResult>,
      onStatus: (status: RuntimeSpec) => void,
    ) => BuildTasks;
  };
  WXStyles?: {
    profiles: Record<string, unknown>;
    aliases: Record<string, unknown>;
    shader(material: Three.Material, style: string): void;
  };
  WXMechanics?: {
    apply(
      root: Three.Object3D,
      spec: RuntimeSpec,
      state: Record<string, number>,
    ): unknown;
  };
  WXRuntimePack?: {
    pack(
      loaded: GLTF,
      spec: RuntimeSpec,
      data: RuntimeData,
    ): { root: Three.Object3D; report: BuildReport; cleanup(): void };
  };
  WXSemantic?: {
    assembly(spec: RuntimeSpec): RuntimeSpec;
    part(
      spec: RuntimeSpec,
      params: RuntimeSpec,
      parts: Record<string, RuntimeSpec>,
    ): RuntimeSpec;
  };
  WXSceneDocument?: { locked(doc: RuntimeSpec, id: string): boolean };
  WX_QA?: RuntimeSpec;
}

/** Opaque handle. Model and binary ownership remain private to the runtime. */
export interface PreparedAsset {
  readonly asset: RuntimeAsset;
  readonly token: symbol;
}
export interface StudioRuntime {
  mergeDefinitions?(patch: RuntimeData): void;
  prepare(
    asset: RuntimeAsset,
    spec?: RuntimeSpec,
    signal?: AbortSignal,
  ): Promise<PreparedAsset>;
  commit(prepared: PreparedAsset): void;
  discard(prepared: PreparedAsset): void;
  mount(elements: ViewportElements): () => void;
  dispose(): void;
  snapshot(): RuntimeAsset | null;
  getView(): ViewState;
  setView(view: Partial<ViewState>): void;
  fit(): void;
  resize(): void;
  setWire(value: boolean): void;
  setGrid(value: boolean): void;
  setLighting(value: string): void;
  bindEditor(editor: EditorBridge | null): void;
  selectionChanged(): void;
  focusSelection(): void;
  cancelInteraction(): boolean;
  groundCenter(): number[];
  isolateNode(id: string): void;
  resetVisibility(): void;
  explode(amount: number): void;
  poseTime(time: number): void;
  playMotion(playing: boolean, clip?: number): void;
  applyRigidState(state: Record<string, number>): unknown;
  exportGLB(reexport?: boolean): Promise<ArrayBuffer>;
  exportPart(id: string): Promise<ArrayBuffer>;
  exportRuntime(): Promise<Blob>;
  exportPose(): Promise<ArrayBuffer>;
  motionInfo(): { name: string; duration: number }[];
  runtimeSidecar(asset?: RuntimeAsset): Record<string, unknown>;
  ground(): Promise<unknown> | void;
  align(axis: string, mode: string, anchor?: string): Promise<unknown> | void;
  getModel(): Three.Object3D | null;
  cache: BuildCache | null;
  tasks: BuildTasks | null;
}
