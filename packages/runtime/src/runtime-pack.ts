import * as Guards from "./three-guards.js";
/* Static opaque packing on a fresh decoded snapshot, never the preview tree.
 * Dynamic / skinned / alpha objects stay separate. Semantic nodes remain present;
 * each packed triangle range has a source map. No animation-stripping heuristic.
 */
import * as T from "./three.js";
import type { RuntimeSpec, RuntimeData } from "./types.js";
interface PackGLTF {
  scene: T.Object3D;
  parser: {
    associations: Map<T.Object3D, { nodes?: number }>;
    json: { nodes: { name?: string }[] };
  };
}
export function pack(loaded: PackGLTF, spec: RuntimeSpec, data: RuntimeData) {
  const root = loaded.scene;
  root.updateMatrixWorld(true);
  const by = new Map<string, T.Object3D>(),
    guarded = new Set<T.Object3D>(),
    garbage = new Set<T.BufferGeometry>();
  root.traverse((o) => {
    const a = loaded.parser.associations.get(o),
      name =
        a?.nodes !== undefined
          ? loaded.parser.json.nodes[a.nodes].name
          : o.name;
    if (name) {
      by.set(name, o);
      o.userData.wxSourceName = name;
    }
  });
  const mark = (name: string) => by.get(name)?.traverse((o) => guarded.add(o));
  root.traverse((o) => {
    if (Guards.isBone(o) || Guards.isSkinnedMesh(o))
      o.traverse((n) => guarded.add(n));
  });
  function visit(s: RuntimeSpec, prefix = "", depth = 0) {
    if (depth > 12) throw Error("Runtime dependency depth");
    for (const n of s.metadata?.runtime_fragment_nodes || []) mark(prefix + n);
    for (const c of s.metadata?.state_controls || [])
      for (const n of c.nodes || [c.node]) mark(prefix + n);
    for (const c of s.metadata?.struts || [])
      for (const n of [c.node, c.from.node, c.to.node]) mark(prefix + n);
    for (const clip of data.motions?.[s.id || ""]?.clips || [])
      for (const t of clip.tracks || []) mark(prefix + t.node);
    for (const i of s.instances || []) {
      if (i.assembly)
        visit(data.assemblies![i.assembly], prefix + i.id + ".", depth + 1);
      else if (data.parts?.[i.part || ""]?.runtime?.helper_only)
        mark(prefix + i.id);
    }
  }
  visit(spec);
  const groups = new Map<string, T.Mesh<T.BufferGeometry, T.Material>[]>(),
    kept: string[] = [];
  let before = 0,
    triBefore = 0;
  root.traverse((o) => {
    if (!Guards.isMesh(o)) return;
    before++;
    const g = o.geometry;
    triBefore += (g.index?.count || g.attributes.position.count) / 3;
    if (
      guarded.has(o) ||
      Array.isArray(o.material) ||
      o.material.transparent ||
      Object.values(g.morphAttributes || {}).some(
        (a) => Array.isArray(a) && a.length,
      ) ||
      g.groups.length > 1
    ) {
      kept.push(o.userData.wxSourceName || o.name);
      return;
    }
    const key = o.material.uuid;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(o as T.Mesh<T.BufferGeometry, T.Material>);
  });
  const beforeBounds = new T.Box3().setFromObject(root),
    batches = [];
  const inverseRoot = root.matrixWorld.clone().invert();
  let serial = 0;
  for (const objects of groups.values()) {
    if (objects.length < 2) {
      kept.push(objects[0].userData.wxSourceName || objects[0].name);
      continue;
    }
    const arrays: Record<string, number[]> = {
        position: [],
        normal: [],
        uv: [],
        color: [],
      },
      ranges = [];
    let off = 0;
    const id = "runtime.batch." + serial++;
    for (const o of objects) {
      const g = o.geometry.index
        ? o.geometry.toNonIndexed()
        : o.geometry.clone();
      g.applyMatrix4(inverseRoot.clone().multiply(o.matrixWorld));
      const p = g.attributes.position,
        n = g.attributes.normal,
        uv = g.attributes.uv,
        c = g.attributes.color;
      const name: string = o.userData.wxSourceName || o.name;
      for (let i = 0; i < p.count; i++) {
        arrays.position.push(p.getX(i), p.getY(i), p.getZ(i));
        arrays.normal.push(n?.getX(i) || 0, n?.getY(i) || 0, n?.getZ(i) || 0);
        arrays.uv.push(uv?.getX(i) || 0, uv?.getY(i) || 0);
        arrays.color.push(c?.getX(i) ?? 1, c?.getY(i) ?? 1, c?.getZ(i) ?? 1);
      }
      ranges.push({
        source_node: name,
        batch_node: id,
        vertex_start: off,
        vertex_count: p.count,
        triangle_start: off / 3,
        triangle_count: p.count / 3,
      });
      off += p.count;
      g.dispose();
      garbage.add(o.geometry);
      const original = new T.Group();
      original.name = o.name;
      original.position.copy(o.position);
      original.quaternion.copy(o.quaternion);
      original.scale.copy(o.scale);
      original.userData = { ...o.userData, wxRuntimeBatch: id };
      original.updateMatrix();
      const parent = o.parent!;
      parent.add(original);
      for (const child of [...o.children]) original.add(child);
      parent.remove(o);
    }
    const g = new T.BufferGeometry();
    for (const [name, values] of Object.entries(arrays))
      g.setAttribute(
        name,
        new T.Float32BufferAttribute(values, name === "uv" ? 2 : 3),
      );
    g.computeBoundingBox();
    const m = new T.Mesh(g, objects[0].material);
    m.name = id;
    m.userData = { wx_role: "runtime_static_batch", wxRuntimeSources: ranges };
    root.add(m);
    batches.push({
      node: id,
      material: m.material.name,
      source_meshes: objects.length,
      triangles: off / 3,
      sources: ranges,
    });
  }
  root.updateMatrixWorld(true);
  const afterBounds = new T.Box3().setFromObject(root);
  if (
    beforeBounds.min.distanceTo(afterBounds.min) > 4e-5 ||
    beforeBounds.max.distanceTo(afterBounds.max) > 4e-5
  )
    throw Error("Runtime packing changed bounds");
  let after = 0,
    triAfter = 0;
  root.traverse((o) => {
    if (Guards.isMesh(o)) {
      after++;
      triAfter +=
        (o.geometry.index?.count || o.geometry.attributes.position.count) / 3;
    }
  });
  if (triBefore !== triAfter)
    throw Error("Runtime packing changed triangle count");
  const report = {
    schema: "wx.runtime-map/1.0",
    version: "2.0.0",
    strategy:
      "opaque static-only; semantic nodes and dynamic subtrees retained",
    potential_draws_before: before,
    potential_draws_after: after,
    triangles_before: triBefore,
    triangles_after: triAfter,
    batches,
    unchanged_mesh_nodes: kept,
    source_mutated: false,
    limitations: [
      "Potential draw submissions, not GPU frame-rate certification.",
      "World-space batches can increase memory and reduce culling granularity.",
      "No automatic solid collision or LOD generation.",
    ],
  };
  return {
    root,
    report,
    cleanup: () => {
      for (const g of garbage) g.dispose();
    },
  };
}
export default { pack, version: "2.0.0" };
