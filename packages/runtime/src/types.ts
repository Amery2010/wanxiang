/** Data actually consumed by a Library and transferable to the build worker. */
export type RuntimeLibraryData = Pick<
  RuntimeData,
  | "parts"
  | "assemblies"
  | "motions"
  | "materials"
  | "retired"
  | "interfaces"
  | "aliases"
>;

export interface ParameterSchema extends Record<string, unknown> {
  type?: string;
  title?: string;
  default?: unknown;
  enum?: unknown[];
  minimum?: number;
  maximum?: number;
  step?: number;
  unit?: string;
  properties?: Record<string, ParameterSchema>;
}
export interface Parameters extends Record<string, unknown> {
  size?: number[];
  palette?: Record<string, string>;
  roundness?: number;
  voxel_resolution?: number;
}
export interface CollisionRecipe extends Record<string, unknown> {
  type?: string;
  static_only?: boolean;
  size?: number[];
  center?: number[];
  radius?: number;
  segment_start?: number[];
  segment_end?: number[];
  shapes?: CollisionRecipe[];
}
export interface InteractionRecipe extends Record<string, unknown> {
  fragments?: string[];
  target_node?: string;
  schema?: string;
  authority?: string;
  kind?: string;
  event?: string;
  trigger?: Omit<CollisionRecipe, "type"> & { shape: string };
}
export interface RuntimeCapabilities extends Record<string, unknown> {
  collision?: boolean | CollisionRecipe;
  interaction?: InteractionRecipe;
  lod?: boolean | Record<string, unknown>;
  lod_levels?: unknown[];
  interfaces?: string[];
  tags?: string[];
  budget?: number;
  motion?: string;
  helper_only?: boolean;
}
export interface DefinitionRuntime extends Record<string, unknown> {
  collision?: CollisionRecipe;
  schema?: string;
  units?: string;
  up?: string;
  forward?: string;
  triangle_budget?: number;
  lod?: {
    levels?: {
      level: number;
      parameters: Record<string, unknown>;
      screen_height?: number;
    }[];
  };
  interaction?: InteractionRecipe;
  helper_only?: boolean;
}
export interface SceneMetadata extends Record<string, unknown> {
  title?: string;
  objects?: Record<
    string,
    {
      label?: string;
      layer?: string;
      region?: string;
      group?: string;
      hidden?: boolean;
      locked?: boolean;
    }
  >;
  layers?: Record<
    string,
    { label?: string; visible?: boolean; locked?: boolean }
  >;
  regions?: Record<string, { label?: string }>;
  groups?: Record<
    string,
    { label?: string; hidden?: boolean; locked?: boolean }
  >;
}
export interface RuntimeMetadata extends Record<string, unknown> {
  level?: number;
  scene?: SceneMetadata | boolean;
  parameter_schema?: ParameterSchema;
  parameters?: Parameters;
  roundness?: number;
  voxel_resolution?: number;
  runtime?: DefinitionRuntime;
  runtime_fragment_nodes?: string[];
  struts?: {
    node: string;
    from: { node: string; point: number[] };
    to: { node: string; point: number[] };
    rod: string;
    min_length: number;
    max_length: number;
    rod_length: number;
  }[];
  state_controls?: {
    id: string;
    node?: string;
    title?: string;
    axis?: number[];
    nodes?: string[];
    mode?: string;
    min: number;
    max: number;
    step?: number;
    default?: number;
    unit?: string;
  }[];
}
/** Consumed fields are typed; untouched author extensions stay opaque. */
export interface RuntimeSpec extends Record<string, unknown> {
  internal?: boolean;
  id?: string;
  schema?: string;
  name?: string;
  part?: string;
  assembly?: string;
  style?: string;
  material?: string;
  params?: Parameters;
  metadata?: RuntimeMetadata;
  instances?: RuntimeInstance[];
  parameter_schema?: ParameterSchema;
  runtime?: DefinitionRuntime;
  source?: unknown;
  position?: number[];
  rotation?: number[];
  scale?: number[];
  enabled?: boolean;
  attach?: {
    target: string;
    socket?: string;
    own?: string;
    mode?: string;
    offset?: number[];
    twist?: number;
    allow_interface_mismatch?: boolean;
  };
  joint?: { axis?: number[]; limits?: number[] };
  angle?: number;
  role?: string;
  collision?: CollisionRecipe;
  max_triangles?: number;
  exports?: import("./contract-types.js").Socket[];
  category?: string;
  level?: number;
  repeat?:
    | { type?: "linear"; count?: number; step?: number[] }
    | { type: "grid"; count?: number[]; step?: number[] }
    | {
        type: "radial";
        count?: number;
        radius?: number;
        start?: number;
        orient?: boolean;
      };
}
export interface RuntimeInstance extends RuntimeSpec {
  id: string;
  parent?: string;
  pivot?: number[];
}
export interface BomEntry extends Record<string, unknown> {
  instance: string;
  part: string;
  name?: string;
  style?: string;
  material?: string;
  params?: Parameters;
  collision_override?: CollisionRecipe;
}
export interface BuildReport extends Record<string, unknown> {
  triangles?: number;
  triangles_after?: number;
  nodes?: number;
  materials?: number;
  textures?: number;
  bones?: number;
  skins?: number;
  animations?: number;
  mesh_stats?: Record<string, unknown>[];
}
export interface RuntimeAsset extends Record<string, unknown> {
  id: string;
  name?: string;
  level?: number;
  dynamic?: boolean;
  local?: boolean;
  hero?: string;
  category?: string;
  family?: string;
  tags?: string[];
  theme?: string;
  game_category?: string;
  game_kit?: string;
  game_expansion?: boolean;
  l1?: boolean;
  l2?: boolean;
  l3?: boolean;
  l4?: boolean;
  kit?: RuntimeSpec;
  spec?: RuntimeSpec;
  recipe?: Record<string, unknown>;
  runtime?: RuntimeCapabilities;
  glb?: string;
  report?: BuildReport;
  bom?: BomEntry[];
  provenance?: Record<string, unknown>;
  sha256?: string;
  bytes?: number;
  cacheSource?: string;
  _buildKey?: string;
  _buildMs?: number;
}
export interface MaterialRow extends Record<string, unknown> {
  id: string;
  name?: string;
  preview?: string;
  emissive?: string;
  record: Record<string, unknown> & {
    baseColorFactor?: number[];
    emissiveFactor?: number[];
    roughnessFactor?: number;
    metallicFactor?: number;
    alphaMode?: string;
    alphaCutoff?: number;
    doubleSided?: boolean;
    kind?: string;
    sampler?: {
      wrapS?: string;
      wrapT?: string;
      magFilter?: number;
      minFilter?: number;
    };
    extras?: Record<string, unknown>;
  };
  files?: Record<string, string>;
}
export interface RuntimeData extends Record<string, unknown> {
  version?: string;
  title?: string;
  assets: RuntimeAsset[];
  parts?: Record<string, Part>;
  aliases?: Record<string, string>;
  interfaces?: import("./contract-types.js").RegistryInput;
  retired?: { entries?: { kind: string; id: string }[] };
  assemblies?: Record<string, RuntimeSpec>;
  materials?: MaterialRow[];
  motions?: Record<
    string,
    RuntimeSpec & {
      clips?: {
        name: string;
        duration: number;
        tracks: {
          node: string;
          axis: number[];
          degrees?: number[];
          translations?: number[];
        }[];
      }[];
    }
  >;
  game_expansion?: {
    parts: string[];
    assemblies: string[];
    kits: Record<
      string,
      { name?: string; title?: string; parts: string[]; assembly: string }
    >;
  };
}

export interface BuildResult {
  buffer: ArrayBuffer;
  bom: BomEntry[];
  report: BuildReport;
}
export interface Part extends RuntimeSpec {
  id: string;
  size?: number[];
  shape?: string;
  anchor?: string;
  connectors?: import("./contract-types.js").Socket[];
  shape_params?: SemanticShape;
}
export interface Assembly extends RuntimeSpec {
  id: string;
  instances: RuntimeInstance[];
}
export type Instance = RuntimeInstance;
export type LibraryData = RuntimeData;
export interface Scene extends Assembly {
  metadata: RuntimeMetadata & { scene: NormalizedSceneMetadata };
  instances: SceneInstance[];
}
export interface SceneInstance extends RuntimeInstance {
  position: number[];
  rotation: number[];
  scale: number[];
}
export interface SceneObjectMetadata {
  label?: string;
  layer: string;
  region: string;
  group?: string;
  hidden?: boolean;
  locked?: boolean;
}
export interface SceneRow {
  label?: string;
  visible?: boolean;
  hidden?: boolean;
  locked?: boolean;
}
export interface NormalizedSceneMetadata extends SceneMetadata {
  objects: Record<string, SceneObjectMetadata>;
  layers: Record<string, SceneRow>;
  regions: Record<string, SceneRow>;
  groups: Record<string, SceneRow>;
  title: string;
}

export interface ComponentTransform {
  position?: number[];
  rotation?: number[];
  scale?: number[];
  frame_scale?: number[];
  mirror?: string;
}
export interface SemanticComponent extends ComponentTransform {
  id?: string;
  part: string;
  params?: Parameters;
  bind?: Record<string, string>;
  bone?: string;
  material?: string;
}
export interface SemanticShape extends importShape {
  components?: SemanticComponent[];
}
import type { Shape as importShape } from "./geometry-types.js";
