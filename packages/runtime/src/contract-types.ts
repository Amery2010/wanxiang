import type { Object3D } from "./three.js";
export interface InterfaceDefinition {
  id?: string;
  version: number;
  tolerance?: number;
  allowed_scale?: string;
  span?: number;
  gauge?: number;
  diameter?: number;
  [key: string]: unknown;
}
export type InterfaceRegistry = Record<string, InterfaceDefinition>;
export type RegistryInput =
  InterfaceRegistry | { interfaces: InterfaceRegistry };
export interface Socket {
  id?: string;
  interface?: string;
  position: number[];
  normal: number[];
  tangent: number[];
  axis?: number[];
  node?: Object3D | string;
  socket?: string;
  frame_node?: string;
  version?: number;
  span?: number;
  gauge?: number;
  diameter?: number;
  tolerance?: number;
  profile?: number[];
  units?: string;
  allowed_scale?: string;
  gender?: string;
  world_scale?: number[];
  [key: string]: unknown;
}
export interface Collision {
  type?: string;
  static_only?: boolean;
  size?: number[];
  center?: number[];
  radius?: number;
  segment_start?: number[];
  segment_end?: number[];
  shapes?: Collision[];
}
export interface RuntimeContractMetadata {
  schema?: string;
  units?: string;
  up?: string;
  forward?: string;
  triangle_budget?: number;
  collision?: Collision;
  helper_only?: boolean;
  interaction?: {
    schema?: string;
    authority?: string;
    kind?: string;
    event?: string;
    trigger?: Omit<Collision, "type"> & { shape: string };
    fragments?: string[];
  };
  lod?: {
    levels?: {
      level: number;
      parameters: Record<string, unknown>;
      screen_height?: number;
    }[];
  };
}
