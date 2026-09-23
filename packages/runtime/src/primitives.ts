import type { Form, LoftForm, Ring } from "./geometry-types.js";
import * as T from "./three.js";
/* Small, bounded construction operators. These are L0 tools, not catalogue items. */
const fail = (m: string): never => {
  throw Error("PRIMITIVE_INVALID: " + m);
};
const vector = (a: unknown, n: number): a is number[] =>
  Array.isArray(a) && a.length === n && a.every(Number.isFinite);

/** Rotation-minimising frames. A fixed global projection flips at X-aligned
 * tangents; transport eliminates the half-turn in cables, tails and tubes. */
function loftFrames(f: LoftForm) {
  const rs = f.rings,
    n = rs.length,
    V = (a: number[]) => new T.Vector3(a[0], a[1], a[2]);
  const closed =
    n > 3 &&
    V(rs[0].c).distanceTo(V(rs[n - 1].c)) < 1e-8 &&
    Math.hypot(...rs[0].r.map((x, k) => x - rs[n - 1].r[k])) < 1e-8;
  const count = closed ? n - 1 : n,
    frames: { t: T.Vector3; u: T.Vector3; v: T.Vector3 }[] = [];
  for (let j = 0; j < n; j++) {
    const i = j % count,
      prev = closed ? (i - 1 + count) % count : Math.max(0, j - 1),
      next = closed ? (i + 1) % count : Math.min(n - 1, j + 1);
    const t = f.frame_axis ? V(f.frame_axis) : V(rs[next].c).sub(V(rs[prev].c));
    if (!Number.isFinite(t.lengthSq()) || t.lengthSq() < 1e-12)
      fail("Degenerate loft tangent");
    t.normalize();
    let u;
    if (j && !f.frame_axis) {
      const last = frames[j - 1];
      u = last.u
        .clone()
        .applyQuaternion(new T.Quaternion().setFromUnitVectors(last.t, t));
    } else {
      u = V(f.axis === "x" ? [0, 0, 1] : [1, 0, 0]);
      if (Math.abs(u.dot(t)) > 0.98)
        u = V(Math.abs(t.y) < 0.9 ? [0, 1, 0] : [0, 0, 1]);
    }
    u.addScaledVector(t, -u.dot(t)).normalize();
    frames.push({ t, u, v: new T.Vector3().crossVectors(t, u) });
  }
  if (closed && !f.frame_axis) {
    const first = frames[0],
      last = frames[n - 1],
      angle = Math.atan2(
        first.t.dot(new T.Vector3().crossVectors(last.u, first.u)),
        last.u.dot(first.u),
      );
    for (let j = 1; j < n; j++) {
      frames[j].u.applyAxisAngle(frames[j].t, (angle * j) / (n - 1));
      frames[j].v.crossVectors(frames[j].t, frames[j].u);
    }
    frames[n - 1] = {
      t: first.t.clone(),
      u: first.u.clone(),
      v: first.v.clone(),
    };
  }
  return { frames, closed };
}

function build(f: Form, look?: { id: string }) {
  const p: number[][] = [],
    faces: number[][] = [];
  let normals: number[][] | undefined;
  const face = (ids: number[]) => {
    const a = new T.Vector3(...p[ids[0]]),
      b = new T.Vector3(...p[ids[1]]),
      c = new T.Vector3(...p[ids[2]]),
      n = b.sub(a).cross(c.sub(a)),
      mid = new T.Vector3();
    for (const i of ids) mid.add(new T.Vector3(...p[i]));
    if (n.dot(mid) < 0) ids = ids.slice().reverse();
    faces.push(ids);
  };
  if (f.kind === "bevelbox") {
    // Six panels + twelve edge strips + eight corner patches. The old
    // corner-cut octagons overlapped the edge strips (non-manifold topology).
    const size = f.size,
      r = f.bevel ?? 0.02;
    if (
      !vector(size, 3) ||
      size.some((x) => x <= 0 || x > 100) ||
      !Number.isFinite(r) ||
      r <= 0 ||
      r >= Math.min(...size) / 2
    )
      fail("Bevel box dimensions");
    const h = size.map((x) => x / 2),
      core = h.map((x) => x - r),
      rounded = look?.id === "toon",
      segments = rounded ? 2 : 1;
    const point = (pos: number[]) => {
      p.push(pos);
      return p.length - 1;
    };
    // Panel boundaries are shared exactly with the cylinder and octant patches.
    for (let axis = 0; axis < 3; axis++)
      for (const sign of [-1, 1]) {
        const uv = [0, 1, 2].filter((k) => k !== axis);
        face(
          [
            [-1, -1],
            [1, -1],
            [1, 1],
            [-1, 1],
          ].map((q) => {
            const v = [0, 0, 0];
            v[axis] = sign * h[axis];
            q.forEach((v0, k) => (v[uv[k]] = v0 * core[uv[k]]));
            return point(v);
          }),
        );
      }
    for (let axis = 0; axis < 3; axis++) {
      const [a, b] = [0, 1, 2].filter((k) => k !== axis);
      for (const sa of [-1, 1])
        for (const sb of [-1, 1]) {
          const strip = [];
          for (let j = 0; j <= segments; j++) {
            const x = segments - j,
              y = j,
              len = Math.hypot(x, y);
            strip.push(
              [-1, 1].map((sign) => {
                const v = [0, 0, 0];
                v[axis] = sign * core[axis];
                v[a] = sa * (core[a] + (r * x) / len);
                v[b] = sb * (core[b] + (r * y) / len);
                return point(v);
              }),
            );
          }
          for (let j = 0; j < segments; j++)
            face([strip[j][0], strip[j][1], strip[j + 1][1], strip[j + 1][0]]);
        }
    }
    for (const sx of [-1, 1])
      for (const sy of [-1, 1])
        for (const sz of [-1, 1]) {
          const ids = new Map<string, number>(),
            signs = [sx, sy, sz];
          for (let i = 0; i <= segments; i++)
            for (let j = 0; j <= segments - i; j++) {
              const q = [i, j, segments - i - j],
                len = Math.hypot(...q);
              ids.set(
                i + "," + j,
                point(q.map((v, k) => signs[k] * (core[k] + (r * v) / len))),
              );
            }
          const at = (i: number, j: number) => ids.get(i + "," + j)!;
          for (let i = 0; i < segments; i++)
            for (let j = 0; j < segments - i; j++) {
              face([at(i, j), at(i + 1, j), at(i, j + 1)]);
              if (i + j < segments - 1)
                face([at(i + 1, j), at(i + 1, j + 1), at(i, j + 1)]);
            }
        }
    // Analytic normals preserve perfectly planar panel lighting in toon mode.
    if (rounded) {
      normals = p.map((pos) => {
        const n = pos.map(
            (v, k) => v - Math.max(-core[k], Math.min(core[k], v)),
          ),
          len = Math.hypot(...n);
        return n.map((v) => v / len);
      });
    }
  } else if (f.kind === "lathe") {
    const rings = f.profile,
      n = f.sides || 16;
    if (
      !Array.isArray(rings) ||
      rings.length < 2 ||
      rings.length > 64 ||
      !Number.isInteger(n) ||
      n < 5 ||
      n > 32 ||
      rings.some(
        (r) =>
          !vector(r, 2) ||
          r[0] < 0 ||
          Math.abs(r[0]) > 30 ||
          Math.abs(r[1]) > 100,
      )
    )
      fail("Lathe profile/budget");
    for (const [r, y] of rings)
      for (let k = 0; k < n; k++) {
        const a = (k * 2 * Math.PI) / n;
        p.push([r * Math.cos(a), y, r * Math.sin(a)]);
      }
    const count = f.closed_profile ? rings.length : rings.length - 1;
    for (let j = 0; j < count; j++)
      for (let k = 0; k < n; k++) {
        const next = (j + 1) % rings.length;
        faces.push([
          j * n + k,
          next * n + k,
          next * n + ((k + 1) % n),
          j * n + ((k + 1) % n),
        ]);
      }
    if (f.cap && !f.closed_profile) {
      faces.push(Array.from({ length: n }, (_, i) => i));
      faces.push(
        Array.from({ length: n }, (_, i) => (rings.length - 1) * n + n - 1 - i),
      );
    }
    if (f.reverse) for (const fc of faces) fc.reverse();
  } else if (f.kind === "extrude") {
    const outline = f.outline,
      holes = f.holes || [],
      depth = f.depth;
    if (
      !Array.isArray(outline) ||
      outline.length < 3 ||
      outline.length > 128 ||
      !Number.isFinite(depth) ||
      depth <= 0 ||
      depth > 100 ||
      outline.some((x) => !vector(x, 2)) ||
      holes.length > 8 ||
      holes.some(
        (h) =>
          !Array.isArray(h) ||
          h.length < 3 ||
          h.length > 128 ||
          h.some((x) => !vector(x, 2)),
      )
    )
      fail("Extrusion dimensions");
    const rings = [outline, ...holes].map((r, i) => {
      const vs = r.map((x) => new T.Vector2(...x));
      if (T.ShapeUtils.isClockWise(vs) !== (i === 0)) vs.reverse();
      return vs;
    });
    const flat = rings.flat(),
      n = flat.length;
    for (const z of [-depth / 2, depth / 2])
      for (const v of flat) p.push([v.x, v.y, z]);
    const tris = T.ShapeUtils.triangulateShape(rings[0], rings.slice(1));
    for (const t of tris) {
      faces.push(t.slice().reverse());
      faces.push(t.map((x) => x + n));
    }
    let start = 0;
    for (const ring of rings) {
      for (let i = 0; i < ring.length; i++) {
        const a = start + i,
          b = start + ((i + 1) % ring.length);
        faces.push([a, a + n, b + n, b]);
      }
      start += ring.length;
    }
  } else return null;
  return { points: p, faces, normals };
}
/** Explicit degree-based sweep contract. Legacy radian recipes are unchanged. */
function loftSection(f: LoftForm, r: Ring, j: number, k: number) {
  const n = f.sides || 8,
    explicit = f.phase_degrees !== undefined || f.twist_degrees !== undefined;
  let angle = (f.twist || 0) + (r.twist || 0);
  if (explicit) {
    if (f.twist !== undefined || r.twist !== undefined)
      fail("Do not mix legacy radians with degree sweep controls");
    const phase = f.phase_degrees ?? 0,
      total = f.twist_degrees ?? 0;
    if (
      !Number.isFinite(phase) ||
      !Number.isFinite(total) ||
      Math.abs(phase) > 3600 ||
      Math.abs(total) > 3600
    )
      fail("Sweep degrees must be finite and bounded");
    let distance = 0,
      length = 0;
    for (let i = 1; i < f.rings.length; i++) {
      const a = f.rings[i - 1].c,
        b = f.rings[i].c,
        d = Math.hypot(...a.map((v, k) => b[k] - v));
      length += d;
      if (i <= j) distance += d;
    }
    angle =
      ((phase + total * (length > 1e-12 ? distance / length : 0)) * Math.PI) /
      180;
  }
  if (f.outline) {
    if (f.outline.length !== n || !vector(f.outline[k], 2))
      fail("Outline length/coordinates");
    const [x, y] = f.outline[k];
    return explicit
      ? [
          x * Math.cos(angle) - y * Math.sin(angle),
          x * Math.sin(angle) + y * Math.cos(angle),
        ]
      : [x, y];
  }
  const a = (k * 2 * Math.PI) / n + angle;
  return [Math.cos(a), Math.sin(a)];
}
const primitives = { build, loftFrames, loftSection, version: "2.1.0" };

export default primitives;
