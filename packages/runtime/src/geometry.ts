import type { Part } from "./types.js";
import type {
  GeometryParameters,
  RigBone,
  FormRange,
} from "./geometry-types.js";
import type { Contracts as ContractsInstance } from "./contracts.js";
import * as T from "./three.js";
import Styles from "./styles.js";
import Surfaces from "./surfaces.js";
import Facets from "./facets.js";
import Semantic from "./semantic.js";
import Contracts from "./contracts.js";
/* Wanxiang3D 1.7: only authored low-poly source meshes are shipped.
 * A style derives bounded geometry/colour from that single source. +Y up, +Z forward.
 */
function fail(m: string): never {
  throw Error("GEOMETRY_INVALID: " + m);
}
function part(
  input: Part,
  style = "lowpoly",
  params: GeometryParameters = {},
  registry: Map<string, Part> | Record<string, Part> = {},
  contracts: ContractsInstance | null | false = Contracts,
) {
  const def = Semantic.part(input, params, registry);
  if (contracts) contracts.validateRuntime(def.runtime);
  Surfaces.validate(params);
  const look = Styles.resolve(style);
  if (!def || def.shape !== "faceted")
    fail("Retired model kind. Use a faceted component definition.");
  for (const k of Object.keys(params))
    if (
      ![
        "size",
        "uv_scale",
        "palette",
        "roundness",
        "voxel_resolution",
        "seed",
      ].includes(k) &&
      !Object.prototype.hasOwnProperty.call(
        def.parameter_schema?.properties || {},
        k,
      )
    )
      fail("Unknown part parameter " + k);
  const size = params.size || def.size;
  if (
    !Array.isArray(size) ||
    size.length !== 3 ||
    size.some((v) => !Number.isFinite(v) || v <= 0 || v > 100)
  )
    fail("Invalid dimensions");
  const uvScale = params.uv_scale ?? 1;
  if (!Number.isFinite(uvScale) || uvScale <= 0 || uvScale > 100)
    fail("UV scale outside (0,100]");
  const authoredSize = def.size;
  if (!authoredSize) fail("Invalid dimensions");
  let g = Facets.build(def.shape_params, params, look.id);
  const sc = size.map((x, i) => x / authoredSize[i]);
  if (def.shape_params.normalise) {
    g.computeBoundingBox();
    const b = g.boundingBox!.clone(),
      s = b.getSize(new T.Vector3()),
      c = b.getCenter(new T.Vector3());
    if (s.toArray().some((v) => v < 1e-9))
      fail("Zero-thickness normalized component");
    g.translate(-c.x, -c.y, -c.z).scale(
      size[0] / s.x,
      size[1] / s.y,
      size[2] / s.z,
    );
    if (def.anchor === "base" || !def.anchor) g.translate(0, size[1] / 2, 0);
    else if (def.anchor === "hinge") g.translate(size[0] / 2, size[1] / 2, 0);
    else if (def.anchor === "top") g.translate(0, -size[1] / 2, 0);
    else if (def.anchor !== "center") fail("Invalid anchor");
  } else {
    g.scale(sc[0], sc[1], sc[2]);
    for (const b of (g.userData.rig || []) as RigBone[])
      b.position = b.position.map((v, i) => v * sc[i]);
  }
  g.userData.anatomy.scale = sc;
  g.userData.anatomy.connectors = (def.connectors || [])
    .filter((c) => c.enabled !== false)
    .map((c) =>
      contracts
        ? contracts.scaled(c, sc)
        : { ...c, position: c.position.map((v, i) => v * sc[i]) },
    );
  g.userData.anatomy.parameters = def.resolved_parameters;
  g.userData.anatomy.dependencies = def.dependencies;
  g.computeBoundingBox();
  if (look.id === "voxel") g = Surfaces.voxelize(g, params);
  const b = g.boundingBox!,
    s = b.getSize(new T.Vector3()),
    p = g.attributes.position,
    uv = g.attributes.uv;
  for (let i = 0; i < p.count; i += 3) {
    const a = new T.Vector3().fromBufferAttribute(p, i),
      n = new T.Vector3()
        .fromBufferAttribute(p, i + 1)
        .sub(a)
        .cross(new T.Vector3().fromBufferAttribute(p, i + 2).sub(a)),
      ns = [Math.abs(n.x), Math.abs(n.y), Math.abs(n.z)],
      axis = ns.indexOf(Math.max(...ns)),
      axes = [0, 1, 2].filter((v) => v !== axis);
    for (let j = 0; j < 3; j++) {
      const v = new T.Vector3().fromBufferAttribute(p, i + j);
      const coords = axes.map(
        (k) =>
          ((v.getComponent(k) - b.min.getComponent(k)) /
            Math.max(1e-8, s.getComponent(k))) *
            uvScale +
          (look.id === "voxel" ? ((params.seed ?? 0) % 997) / 997 : 0),
      );
      uv.setXY(i + j, coords[0], coords[1]);
    }
  }
  g.computeBoundingSphere();
  return g;
}
export interface GeometryArrays {
  colors: number[] | null;
  skin_indices: number[] | null;
  skin_weights: number[] | null;
  rig: RigBone[];
  anatomy: Record<string, unknown> | null;
  vertices: number[];
  normals: number[];
  uv: number[];
  faces: number[];
}
function arrays(g: T.BufferGeometry): GeometryArrays {
  return {
    colors: g.attributes.color ? Array.from(g.attributes.color.array) : null,
    skin_indices: g.attributes.skinIndex
      ? Array.from(g.attributes.skinIndex.array)
      : null,
    skin_weights: g.attributes.skinWeight
      ? Array.from(g.attributes.skinWeight.array)
      : null,
    rig: g.userData.rig || [],
    anatomy: g.userData.anatomy || null,
    vertices: Array.from(g.attributes.position.array),
    normals: Array.from(g.attributes.normal.array),
    uv: Array.from(g.attributes.uv.array),
    faces: g.index
      ? Array.from(g.index.array)
      : Array.from({ length: g.attributes.position.count }, (_, i) => i),
  };
}
function split(g: T.BufferGeometry) {
  const ranges: FormRange[] = g.userData.anatomy?.materialGroups || [],
    groups = new Map<string, FormRange[]>();
  for (const r of ranges) {
    const key = r.material || "";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(r);
  }
  if (groups.size <= 1)
    return [{ role: groups.keys().next().value || "", geometry: g }];
  const result = [];
  for (const [role, ranges] of groups) {
    const out = new T.BufferGeometry(),
      indices = [];
    for (const r of ranges)
      for (let i = r.start; i < r.start + r.count; i++) indices.push(i);
    for (const [name, a] of Object.entries(g.attributes)) {
      const data = new (
        a.array.constructor as { new (length: number): T.TypedArray }
      )(indices.length * a.itemSize);
      let j = 0;
      for (const i of indices)
        for (let k = 0; k < a.itemSize; k++)
          data[j++] = a.array[i * a.itemSize + k];
      out.setAttribute(
        name,
        new T.BufferAttribute(data, a.itemSize, a.normalized),
      );
    }
    out.userData = JSON.parse(JSON.stringify(g.userData));
    out.userData.anatomy.materialGroups = [];
    out.computeBoundingBox();
    out.computeBoundingSphere();
    result.push({ role, geometry: out });
  }
  return result;
}
const geometry = { part, arrays, split, version: "2.0.0" };

export default geometry;
