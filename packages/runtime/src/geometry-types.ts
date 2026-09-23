import type * as T from "./three.js";

export type SkinWeights = string | Record<string, number> | undefined;
export interface RigBone {
  name: string;
  position: number[];
  parent?: string;
  [key: string]: unknown;
}
export interface Ring {
  c: number[];
  r: number[];
  twist?: number;
  color?: string;
  bone?: SkinWeights;
  weights?: SkinWeights;
  seam_points?: number[][];
}
interface FormBase {
  enabled?: boolean;
  color?: string;
  bone?: SkinWeights;
  matrix?: number[];
  rotation?: number[];
  scale?: number[];
  position?: number[];
  roundness?: number;
  roundable?: boolean;
  smooth_angle?: number;
  hard?: boolean;
  preserve_ends?: boolean;
  sides?: number;
  variation?: number;
  seed?: number;
  voxel_box?: boolean;
  material?: string;
  source_part?: string;
  source_path?: string;
  style_overrides?: Record<string, Partial<FormBase> & Record<string, unknown>>;
  color_regions?: { center: number[]; radii: number[]; color: string }[];
}
export interface LoftForm extends FormBase {
  kind: "loft";
  rings: Ring[];
  axis?: string;
  frame_axis?: number[];
  outline?: number[][];
  twist?: number;
  phase_degrees?: number;
  twist_degrees?: number;
  join_start?: string;
  join_end?: string;
  join_tolerance?: number;
  cap?: boolean;
  cap_start?: boolean;
  cap_end?: boolean;
}
export type Form =
  | LoftForm
  | (FormBase & { kind: "bevelbox"; size: number[]; bevel?: number })
  | (FormBase & {
      kind: "lathe";
      profile: number[][];
      closed_profile?: boolean;
      cap?: boolean;
      reverse?: boolean;
    })
  | (FormBase & {
      kind: "extrude";
      outline: number[][];
      holes?: number[][][];
      depth: number;
    })
  | (FormBase & {
      kind: "poly";
      points: number[][];
      faces: (number[] | { v: number[]; color?: string })[];
      colors?: string[];
    })
  | (FormBase & {
      kind: "ico";
      detail?: number;
      distort?: number;
      floor?: number;
      size?: number[];
    });
export interface Shape {
  forms?: Form[];
  rig?: RigBone[];
  normalise?: boolean;
}
export interface GeometryParameters {
  size?: number[];
  uv_scale?: number;
  palette?: Record<string, string>;
  roundness?: number;
  voxel_resolution?: number;
  seed?: number;
  paint_strength?: number;
  texture_scale?: number;
  [key: string]: unknown;
}
export interface FormRange {
  start: number;
  count: number;
  material?: string | null;
  smoothAngle?: number;
  analytic?: boolean;
  kind?: string;
  voxelBox?: boolean;
  source_part?: string | null;
  source_path?: string | null;
}
export interface SeamReport {
  id: string;
  vertices: number;
  max_input_gap: number;
  max_output_gap: number;
  shared_weights: boolean;
  removed_caps: number;
  points: number[][];
}
export type Face = [number[], string | undefined];
export type RuntimeGeometry = T.BufferGeometry;
