import type {
  LoftForm,
  Shape,
  SkinWeights,
  SeamReport,
} from "./geometry-types.js";
import * as T from "./three.js";
import Primitives from "./primitives.js";
import Semantic from "./semantic.js";
/* Semantic seam compiler. Only explicitly paired organic interfaces are joined.
 * World-space ring registration (cyclic/reversed), common positions + weights,
 * selective end-cap removal, and angle-limited normal transport. No global blur.
 * Source definitions remain independently buildable; isolated ports stay capped.
 */

const V = (a: number[]) => new T.Vector3(a[0], a[1], a[2]),
  fail = (m: string): never => {
    throw Error("SEAM_INVALID: " + m);
  };
function matrix(f: LoftForm) {
  return f.matrix ? new T.Matrix4().fromArray(f.matrix) : Semantic.transform(f);
}
function ringPoints(f: LoftForm, j: number) {
  const rs = f.rings,
    r = rs[j],
    n = f.sides || 8;
  const { u, v } = Primitives.loftFrames(f).frames[j],
    m = matrix(f);
  return Array.from({ length: n }, (_, k) => {
    const xy = Primitives.loftSection(f, r, j, k);
    return V(r.c)
      .addScaledVector(u, xy[0] * r.r[0])
      .addScaledVector(v, xy[1] * r.r[1])
      .applyMatrix4(m);
  });
}
function weights(a: SkinWeights, b: SkinWeights) {
  const out: Record<string, number> = {};
  for (const w of [a, b])
    for (const [k, v] of Object.entries(
      typeof w === "string" ? { [w]: 1 } : w || {},
    ))
      out[k] = (out[k] || 0) + v * 0.5;
  const values = Object.entries(out)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 4),
    s = values.reduce((n, x) => n + x[1], 0);
  return s ? Object.fromEntries(values.map(([k, v]) => [k, v / s])) : undefined;
}
function compile(input: Shape) {
  const o: Shape = JSON.parse(JSON.stringify(input)),
    groups = new Map<
      string,
      { f: LoftForm; j: number; side: "start" | "end"; points: T.Vector3[] }[]
    >(),
    report: SeamReport[] = [];
  for (const f of o.forms || []) {
    if (f.kind !== "loft") continue;
    for (const side of ["start", "end"] as const) {
      const id = f[`join_${side}`];
      if (!id) continue;
      const j = side === "start" ? 0 : f.rings.length - 1;
      const g = groups.get(id) || [];
      g.push({ f, j, side, points: ringPoints(f, j) });
      groups.set(id, g);
    }
  }
  for (const [id, entries] of groups) {
    if (entries.length === 1) continue; // Standalone component: retain its sealed end.
    if (entries.length !== 2) fail(id + ": a seam requires exactly two ports");
    const [a, b] = entries,
      n = a.points.length;
    if (n !== b.points.length) fail(id + ": unequal section tessellation");
    let best: { cost: number; indexes: number[] } | null = null;
    for (const direction of [1, -1])
      for (let offset = 0; offset < n; offset++) {
        const indexes = Array.from(
            { length: n },
            (_, k) => (offset + direction * k + n * 2) % n,
          ),
          cost = indexes.reduce(
            (s, j, k) => s + a.points[k].distanceToSquared(b.points[j]),
            0,
          );
        if (!best || cost < best.cost) best = { cost, indexes };
      }
    const maxGap = Math.max(
        ...best!.indexes.map((j, k) => a.points[k].distanceTo(b.points[j])),
      ),
      limit = Math.min(
        a.f.join_tolerance || 0.055,
        b.f.join_tolerance || 0.055,
      );
    if (maxGap > limit)
      fail(
        id + ": authored ports are too far apart (" + maxGap.toFixed(4) + "m)",
      );
    const ra = a.f.rings[a.j],
      rb = b.f.rings[b.j],
      w = weights(
        ra.weights || ra.bone || a.f.bone,
        rb.weights || rb.bone || b.f.bone,
      ),
      ia = matrix(a.f).invert(),
      ib = matrix(b.f).invert();
    ra.seam_points = new Array(n);
    rb.seam_points = new Array(n);
    const points = [];
    for (let k = 0; k < n; k++) {
      const j = best!.indexes[k],
        p = a.points[k].clone().add(b.points[j]).multiplyScalar(0.5);
      points.push(p.toArray());
      ra.seam_points[k] = p.clone().applyMatrix4(ia).toArray();
      rb.seam_points[j] = p.clone().applyMatrix4(ib).toArray();
    }
    if (w) {
      ra.weights = w;
      rb.weights = w;
    }
    a.f.preserve_ends = true;
    b.f.preserve_ends = true;
    a.f[`cap_${a.side}`] = false;
    b.f[`cap_${b.side}`] = false;
    report.push({
      id,
      vertices: n,
      max_input_gap: maxGap,
      max_output_gap: 0,
      shared_weights: !!w,
      removed_caps: 2,
      points,
    });
  }
  return { shape: o, report };
}
function normals(geo: T.BufferGeometry, seams: SeamReport[], angle = 32) {
  if (!seams.length) return;
  const p = geo.attributes.position,
    n = geo.attributes.normal,
    keys = new Set(seams.flatMap((s) => s.points.map(key))),
    at = new Map<string, number[]>();
  function key(p: number[]) {
    return p.map((x) => Math.round(x * 1e6)).join(",");
  }
  for (let i = 0; i < p.count; i++) {
    const k = key([p.getX(i), p.getY(i), p.getZ(i)]);
    if (keys.has(k)) {
      if (!at.has(k)) at.set(k, []);
      at.get(k)!.push(i);
    }
  }
  const cos = Math.cos((angle * Math.PI) / 180),
    original = n.array.slice();
  for (const ids of at.values())
    for (const i of ids) {
      const ref = new T.Vector3().fromArray(original, i * 3),
        sum = new T.Vector3();
      for (const j of ids) {
        const v = new T.Vector3().fromArray(original, j * 3);
        if (ref.dot(v) >= cos) sum.add(v);
      }
      sum.normalize();
      n.setXYZ(i, sum.x, sum.y, sum.z);
    }
  n.needsUpdate = true;
}
const seams = { compile, normals, version: "2.1.0" };

export default seams;
