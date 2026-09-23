import type {
  Shape,
  GeometryParameters,
  SkinWeights,
  FormRange,
  Face,
} from "./geometry-types.js";
interface Edge {
  a: number;
  b: number;
  faces: number[];
  new?: number;
}
import * as T from "./three.js";
import Styles from "./styles.js";
import Primitives from "./primitives.js";
import Seams from "./seams.js";
/* Wanxiang 2.1 / audited polygon authoring.
 * Authored planes, ring silhouettes and bounded palettes; never a decimated field.
 * Shared unchanged by the offline browser and Node worker. +Y up, +Z forward.
 */

const V = (p: number[] = [0, 0, 0]) => new T.Vector3(...p),
  clone = <T>(x: T): T => JSON.parse(JSON.stringify(x));
const bad = (m: string): never => {
    throw Error("FACET_INVALID: " + m);
  },
  finite = (p: unknown, n: number): p is number[] =>
    Array.isArray(p) && p.length === n && p.every(Number.isFinite);

function weighted(items: [SkinWeights, number][]) {
  const out: Record<string, number> = {};
  let sum = 0;
  for (const [w, a] of items) {
    if (!w) continue;
    const d = typeof w === "string" ? { [w]: 1 } : w;
    for (const [b, v] of Object.entries(d)) out[b] = (out[b] || 0) + v * a;
    sum += a;
  }
  if (!sum) return undefined;
  const list = Object.entries(out)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 4),
    total = list.reduce((n, e) => n + e[1], 0);
  return Object.fromEntries(list.map(([b, v]) => [b, v / total]));
}
function subdivide(
  points: number[][],
  faces: Face[],
  weights: SkinWeights[],
  amount: number,
  ends = 0,
) {
  // Weld per form only; separate overlapping body/equipment surfaces never get fused.
  const weld = new Map<string, number>(),
    P: number[][] = [],
    W: SkinWeights[] = [],
    remap: number[] = [];
  for (let i = 0; i < points.length; i++) {
    const key =
      points[i].map((v) => Math.round(v * 1e8)).join(",") +
      "|" +
      JSON.stringify(weights[i] || null);
    let j = weld.get(key);
    if (j === undefined) {
      j = P.length;
      weld.set(key, j);
      P.push(points[i]);
      W.push(weights[i]);
    }
    remap.push(j);
  }
  const locks = new Set<number>();
  if (ends)
    for (let i = 0; i < points.length; i++)
      if (i < ends || i >= points.length - ends) locks.add(remap[i]);
  const FS = faces
      .map(([v, c]): Face => [[...new Set(v.map((i) => remap[i]))], c])
      .filter(([v]) => v.length >= 3),
    edges = new Map<string, Edge>(),
    vFaces = P.map((): number[] => []),
    vEdges = P.map((): Edge[] => []),
    C: number[][] = [],
    CW: SkinWeights[] = [];
  const mean = (items: number[][]) =>
      [0, 1, 2].map((k) => items.reduce((s, p) => s + p[k], 0) / items.length),
    mix = (a: number[], b: number[], t: number) =>
      a.map((v, k) => v * (1 - t) + b[k] * t),
    edgeKey = (a: number, b: number) => (a < b ? a + "," + b : b + "," + a);
  FS.forEach(([v, _c], fi) => {
    C.push(mean(v.map((i) => P[i])));
    CW.push(weighted(v.map((i) => [W[i], 1])));
    v.forEach((a, j) => {
      vFaces[a].push(fi);
      const b = v[(j + 1) % v.length],
        key = edgeKey(a, b);
      let e = edges.get(key);
      if (!e) {
        e = { a, b, faces: [] };
        edges.set(key, e);
        vEdges[a].push(e);
        vEdges[b].push(e);
      }
      e.faces.push(fi);
    });
  });
  const NP = P.map((p, i) => {
      const es = vEdges[i];
      if (locks.has(i) || es.length < 3 || es.some((e) => e.faces.length !== 2))
        return p.slice();
      const F = mean(vFaces[i].map((j) => C[j])),
        R = mean(es.map((e) => mean([P[e.a], P[e.b]]))),
        n = es.length;
      return mix(
        p,
        p.map((v, k) => (F[k] + 2 * R[k] + (n - 3) * v) / n),
        amount,
      );
    }),
    NW = W.slice();
  for (const e of edges.values()) {
    const mid = mean([P[e.a], P[e.b]]);
    e.new = NP.length;
    NP.push(
      e.faces.length === 2 && !(locks.has(e.a) && locks.has(e.b))
        ? mix(mid, mean([P[e.a], P[e.b], C[e.faces[0]], C[e.faces[1]]]), amount)
        : mid,
    );
    NW.push(
      weighted([
        [W[e.a], 1],
        [W[e.b], 1],
      ]),
    );
  }
  const base = NP.length;
  NP.push(...C);
  NW.push(...CW);
  const NF: Face[] = [];
  FS.forEach(([v, c], fi) =>
    v.forEach((a, j) =>
      NF.push([
        [
          a,
          edges.get(edgeKey(a, v[(j + 1) % v.length]))!.new!,
          base + fi,
          edges.get(edgeKey(v[(j + v.length - 1) % v.length], a))!.new!,
        ],
        c,
      ]),
    ),
  );
  // Retain attachment envelopes and semantic pivot after rounding, including thin plates.
  for (let k = 0; k < 3; k++) {
    const a = Math.min(...P.map((p) => p[k])),
      b = Math.max(...P.map((p) => p[k])),
      c = Math.min(...NP.map((p) => p[k])),
      d = Math.max(...NP.map((p) => p[k]));
    if (!locks.size && d - c > 1e-8)
      for (const p of NP) p[k] = a + ((p[k] - c) * (b - a)) / (d - c);
  }
  return { points: NP, faces: NF, weights: NW };
}
/** Area x corner-angle normals, isolated per authored form. Colour is NOT
 * topology. A colour boundary must not create an arbitrary shading crack. */
function smoothNormals(g: T.BufferGeometry, ranges: FormRange[]) {
  const p = g.attributes.position,
    n = g.attributes.normal,
    original = n.array.slice();
  for (const r of ranges) {
    if ((r.smoothAngle ?? 0) <= 0 || r.analytic || !r.count) continue;
    const count = r.count,
      parent = Int32Array.from({ length: count }, (_, i) => i),
      weights = new Float64Array(count);
    const weld = new Map<string, number>(),
      ids = new Int32Array(count),
      edges = new Map<string, number[][]>();
    const find = (i: number): number => {
      while (parent[i] !== i) {
        parent[i] = parent[parent[i]];
        i = parent[i];
      }
      return i;
    };
    const join = (a: number, b: number) => {
      a = find(a);
      b = find(b);
      if (a !== b) parent[b] = a;
    };
    for (let i = 0; i < count; i++) {
      const k = r.start + i,
        key = [p.getX(k), p.getY(k), p.getZ(k)]
          .map((v) => Math.round(v * 1e7))
          .join(",");
      if (!weld.has(key)) weld.set(key, weld.size);
      ids[i] = weld.get(key)!;
    }
    for (let i = 0; i < count; i += 3) {
      const vs = [0, 1, 2].map((k) =>
        new T.Vector3().fromBufferAttribute(p, r.start + i + k),
      );
      const area = vs[1]
        .clone()
        .sub(vs[0])
        .cross(vs[2].clone().sub(vs[0]))
        .length();
      for (let k = 0; k < 3; k++) {
        const a = vs[(k + 1) % 3].clone().sub(vs[k]).normalize(),
          b = vs[(k + 2) % 3].clone().sub(vs[k]).normalize();
        weights[i + k] = area * Math.acos(Math.max(-1, Math.min(1, a.dot(b))));
        const x = i + k,
          y = i + ((k + 1) % 3),
          key = ids[x] < ids[y] ? ids[x] + "," + ids[y] : ids[y] + "," + ids[x];
        if (!edges.has(key)) edges.set(key, []);
        edges.get(key)!.push([x, y]);
      }
    }
    const cos = Math.cos(((r.smoothAngle ?? 0) * Math.PI) / 180);
    for (const entries of edges.values()) {
      // Two sheets touching at a vertex do not share a smoothing island. Only
      // edge-connected, manifold neighbours with a permitted dihedral may join.
      if (entries.length !== 2) continue;
      const [a, b] = entries,
        [x, y] = b;
      const na = new T.Vector3().fromArray(original, (r.start + a[0]) * 3),
        nb = new T.Vector3().fromArray(original, (r.start + x) * 3);
      if (na.dot(nb) < cos - 1e-7) continue;
      join(a[0], ids[a[0]] === ids[x] ? x : y);
      join(a[1], ids[a[1]] === ids[y] ? y : x);
    }
    const sums = new Map<number, T.Vector3>();
    for (let i = 0; i < count; i++) {
      const root = find(i);
      if (!sums.has(root)) sums.set(root, new T.Vector3());
      sums
        .get(root)!
        .addScaledVector(
          new T.Vector3().fromArray(original, (r.start + i) * 3),
          weights[i],
        );
    }
    for (const v of sums.values()) v.normalize();
    for (let i = 0; i < count; i++) {
      const v = sums.get(find(i))!;
      if (v.lengthSq() > 0.5) n.setXYZ(r.start + i, v.x, v.y, v.z);
    }
  }
  n.needsUpdate = true;
}
/** Ear-clip only concave polygons; keep the original fan on convex faces.
 * Projection uses Newell's normal, so an inward-authored polygon stays inward
 * and is caught by the audit, rather than being silently 'fixed' at runtime. */
function triangulate(ids: number[], verts: T.Vector3[]) {
  ids = ids.filter(
    (id, k) => !k || verts[id].distanceToSquared(verts[ids[k - 1]]) > 1e-22,
  );
  if (
    ids.length > 2 &&
    verts[ids[0]].distanceToSquared(verts[ids.at(-1)!]) < 1e-22
  )
    ids.pop();
  if (ids.length < 3) return [];
  if (ids.length === 3) return [ids];
  const normal = new T.Vector3();
  for (let j = 0; j < ids.length; j++) {
    const a = verts[ids[j]],
      b = verts[ids[(j + 1) % ids.length]];
    normal.x += (a.y - b.y) * (a.z + b.z);
    normal.y += (a.z - b.z) * (a.x + b.x);
    normal.z += (a.x - b.x) * (a.y + b.y);
  }
  if (normal.lengthSq() < 1e-24) return [];
  const dim = [Math.abs(normal.x), Math.abs(normal.y), Math.abs(normal.z)],
    axis = dim.indexOf(Math.max(...dim)),
    uv = [0, 1, 2].filter((k) => k !== axis);
  const points = ids.map(
    (id) =>
      new T.Vector2(
        verts[id].getComponent(uv[0]),
        verts[id].getComponent(uv[1]),
      ),
  );
  let plus = false,
    minus = false;
  for (let j = 0; j < points.length; j++) {
    const a = points[j],
      b = points[(j + 1) % points.length],
      c = points[(j + 2) % points.length],
      cross = (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x);
    if (cross > 1e-14) plus = true;
    if (cross < -1e-14) minus = true;
  }
  if (!(plus && minus))
    return Array.from({ length: ids.length - 2 }, (_, j) => [
      ids[0],
      ids[j + 1],
      ids[j + 2],
    ]);
  return T.ShapeUtils.triangulateShape(points, []).map((t) => {
    const tri = t.map((i) => ids[i]);
    const a = verts[tri[0]],
      n = verts[tri[1]].clone().sub(a).cross(verts[tri[2]].clone().sub(a));
    return n.dot(normal) < 0 ? [tri[0], tri[2], tri[1]] : tri;
  });
}

function build(
  o: Shape = {},
  params: GeometryParameters = {},
  style = "lowpoly",
) {
  const look = Styles.resolve(style);
  // Resolve style-specific shapes BEFORE pairing interfaces. A tessellation
  // override may not silently detach its neighbour after seam registration.
  const allowed = new Set([
    "roundable",
    "smooth_angle",
    "roundness",
    "sides",
    "rings",
    "outline",
    "bevel",
  ]);
  if (!Array.isArray(o.forms)) bad("Expected authored forms");
  // Semantic detail gates are evaluated before seam pairing, tessellation and
  // normal generation. False means absent geometry, not an invisible draw call.
  // Reject strings/numeric flags instead of silently accepting truthy mistakes.
  const active = o.forms!.filter((f) => {
    if (f.enabled !== undefined && typeof f.enabled !== "boolean")
      bad("Form enabled must resolve to boolean");
    return f.enabled !== false;
  });
  const styled = {
    ...o,
    forms: active.map((f) => {
      const v = f.style_overrides?.[look.id] || {};
      if (
        !v ||
        typeof v !== "object" ||
        Array.isArray(v) ||
        Object.keys(v).some((k) => !allowed.has(k))
      )
        bad("Unsupported style override");
      return { ...f, ...v };
    }),
  };
  const stitched = Seams.compile(styled);
  o = stitched.shape;
  if (
    params.roundness !== undefined &&
    (!Number.isFinite(params.roundness) ||
      params.roundness < 0 ||
      params.roundness > 1)
  )
    bad("roundness must be 0..1");
  const roundness = params.roundness ?? look.roundness;
  if (!Array.isArray(o.forms) || o.forms.length < 1 || o.forms.length > 640)
    bad("Expected 1..640 authored forms");
  const pal = params.palette || {};
  if (
    typeof pal !== "object" ||
    Array.isArray(pal) ||
    Object.keys(pal).length > 32 ||
    Object.entries(pal).some(
      ([k, v]) => !/^#[0-9a-f]{6}$/i.test(k) || !/^#[0-9a-f]{6}$/i.test(v),
    )
  )
    bad("Invalid palette");
  const ranges: FormRange[] = [],
    P: number[] = [],
    C: number[] = [],
    SI: number[] = [],
    SW: number[] = [],
    AN: number[] = [],
    rig = clone(o.rig || []),
    bm = new Map(rig.map((b, i) => [b.name, i]));
  if (rig.length > 64 || bm.size !== rig.length)
    bad("Rig budget or duplicate bone");
  for (const b of rig) {
    if (
      !finite(b.position, 3) ||
      !/^[A-Za-z][A-Za-z0-9_]*$/.test(b.name) ||
      (b.parent && !bm.has(b.parent))
    )
      bad("Rig frame");
    const seen = new Set([b.name]);
    let p = b.parent;
    while (p) {
      if (seen.has(p)) bad("Cyclic rig");
      seen.add(p);
      p = rig[bm.get(p)!].parent;
    }
  }
  const palette = Object.fromEntries(
    Object.entries(pal).map(([k, v]) => [k.toLowerCase(), v]),
  );
  const paint = (s: string | undefined) => {
    s = palette[(s || "").toLowerCase()] || s || "#ffffff";
    if (!/^#[0-9a-f]{6}$/i.test(s)) bad("Colour must be #RRGGBB");
    return Styles.color(s, look.id);
  };
  const skin = (w: SkinWeights) => {
    if (!rig.length)
      return [
        [0, 0, 0, 0],
        [1, 0, 0, 0],
      ];
    if (typeof w === "string") w = { [w]: 1 };
    w = w || { [rig[0].name]: 1 };
    const list = Object.entries(w);
    if (
      list.some(([k, v]) => !bm.has(k) || !Number.isFinite(v) || v < 0) ||
      list.length > 4 ||
      !list.length
    )
      bad("Skin references");
    const sum = list.reduce((a, x) => a + x[1], 0);
    if (sum <= 0) bad("Zero weights");
    return [
      Array.from({ length: 4 }, (_, i) => bm.get(list[i]?.[0]) || 0),
      Array.from({ length: 4 }, (_, i) => (list[i]?.[1] || 0) / sum),
    ];
  };
  for (const [fi, f] of o.forms!.entries()) {
    if (
      f.roundness !== undefined &&
      (!Number.isFinite(f.roundness) || f.roundness < 0 || f.roundness > 1)
    )
      bad("Form roundness must be 0..1");
    const start = P.length / 3;
    let ps: number[][] = [],
      faces: Face[] = [],
      ws: SkinWeights[] = [],
      analytic: number[][] | null = null;
    const point = (p: number[], w?: SkinWeights) => {
      if (!finite(p, 3) || p.some((x) => Math.abs(x) > 100))
        bad("Point bounds");
      ps.push(p);
      ws.push(w || f.bone);
      return ps.length - 1;
    };
    const face = (v: number[], col = f.color) => faces.push([v, col]);
    const primitive = Primitives.build(f, look);
    if (primitive) {
      primitive.points.forEach((p) => point(p));
      primitive.faces.forEach((ids) => face(ids));
      analytic = primitive.normals || null;
    } else if (f.kind === "loft") {
      const rs = f.rings,
        n = f.sides || 8;
      if (
        !Array.isArray(rs) ||
        rs.length < 2 ||
        rs.length > 64 ||
        !Number.isInteger(n) ||
        n < 3 ||
        n > 16
      )
        bad("Loft budget");
      const transported = Primitives.loftFrames(f);
      for (let j = 0; j < rs.length; j++) {
        const r = rs[j];
        if (
          !finite(r.c, 3) ||
          !finite(r.r, 2) ||
          r.r.some((x) => x < 0 || x > 30)
        )
          bad("Ring dimensions");
        const { u, v } = transported.frames[j];
        for (let k = 0; k < n; k++) {
          const [x, y] = Primitives.loftSection(f, r, j, k);
          const p = V(r.c)
            .addScaledVector(u, x * r.r[0])
            .addScaledVector(v, y * r.r[1]);
          point(
            r.seam_points?.[k] || p.toArray(),
            r.weights || r.bone || f.bone,
          );
        }
      }
      for (let j = 0; j < rs.length - 1; j++)
        for (let k = 0; k < n; k++) {
          const a = j * n + k,
            b = j * n + ((k + 1) % n),
            c = a + n,
            d = b + n;
          face([a, b, d, c], rs[j].color || f.color);
        }
      if (f.cap !== false && !transported.closed) {
        if (f.cap_start !== false)
          face(
            Array.from({ length: n }, (_, i) => n - 1 - i),
            rs[0].color || f.color,
          );
        if (f.cap_end !== false)
          face(
            Array.from({ length: n }, (_, i) => (rs.length - 1) * n + i),
            rs.at(-1)!.color || f.color,
          );
      }
    } else if (f.kind === "poly") {
      if (
        !Array.isArray(f.points) ||
        f.points.length > 4096 ||
        !Array.isArray(f.faces) ||
        f.faces.length > 4096
      )
        bad("Polygon budget");
      f.points.forEach((p) => point(p));
      for (const [i, fc] of f.faces.entries()) {
        const ids = Array.isArray(fc) ? fc : fc.v;
        if (
          ids.length < 3 ||
          ids.some((j) => !Number.isInteger(j) || j < 0 || j >= ps.length)
        )
          bad("Face index");
        face(ids, (Array.isArray(fc) ? f.colors?.[i] : fc.color) || f.color);
      }
    } else if (f.kind === "ico") {
      const detail = f.detail || 0;
      if (![0, 1].includes(detail)) bad("Ico detail");
      const g = new T.IcosahedronGeometry(1, detail),
        p = g.attributes.position;
      for (let i = 0; i < p.count; i++) {
        let x = p.getX(i),
          y = p.getY(i),
          z = p.getZ(i);
        const seed = f.seed || 0,
          d = f.distort || 0;
        const q =
          1 +
          d *
            (0.6 * Math.sin(x * 3.7 + y * 2.2 + seed) +
              0.4 * Math.sin(z * 4.1 - x + seed * 0.43));
        x *= q;
        y *= q;
        z *= q;
        y = Math.max(f.floor ?? -1.5, y);
        const s = f.size || [1, 1, 1];
        point([(x * s[0]) / 2, (y * s[1]) / 2, (z * s[2]) / 2]);
        if (i % 3 === 2) face([i - 2, i - 1, i]);
      }
      g.dispose();
    } else bad("Unknown form " + f.kind);
    // One bounded control-mesh subdivision for rounded styles. Rig weights interpolate
    // with vertices; authored component bounds/pivots remain unchanged.
    if (look.subdivide && !analytic && f.roundable !== false && ps.length > 3) {
      const smooth = subdivide(
        ps,
        faces,
        ws,
        Math.min(
          1,
          roundness *
            (f.roundness === undefined ? 1 : f.roundness / look.roundness),
        ) * (f.hard ? 0.3 : 1),
        f.preserve_ends ? f.sides || 8 : 0,
      );
      ps = smooth.points;
      faces = smooth.faces;
      ws = smooth.weights;
      analytic = null;
    }
    const rot = f.rotation || [0, 0, 0],
      s = f.scale || [1, 1, 1],
      pos = f.position || [0, 0, 0];
    if (
      !finite(rot, 3) ||
      !finite(s, 3) ||
      s.some((v) => v <= 0) ||
      !finite(pos, 3)
    )
      bad("Form transform");
    const m = f.matrix
      ? new T.Matrix4().fromArray(f.matrix)
      : new T.Matrix4().compose(
          V(pos),
          new T.Quaternion().setFromEuler(
            new T.Euler(
              (rot[0] * Math.PI) / 180,
              (rot[1] * Math.PI) / 180,
              (rot[2] * Math.PI) / 180,
              "ZYX",
            ),
          ),
          V(s),
        );
    if (
      f.matrix &&
      (!finite(f.matrix, 16) || Math.abs(m.determinant()) < 1e-10)
    )
      bad("Invalid form matrix");
    const verts = ps.map((p) => V(p).applyMatrix4(m)),
      nm = new T.Matrix3().getNormalMatrix(m);
    const analyticWorld = analytic?.map((n) =>
      V(n).applyMatrix3(nm).normalize(),
    );
    for (const [ids, col] of faces) {
      let colour = col;
      if (f.color_regions) {
        const c = [0, 1, 2].map(
          (k) => ids.reduce((v, i) => v + ps[i][k], 0) / ids.length,
        );
        for (const region of f.color_regions) {
          if (
            !finite(region.center, 3) ||
            !finite(region.radii, 3) ||
            region.radii.some((r) => r <= 0)
          )
            bad("Coat region");
          if (
            c.reduce(
              (v, x, k) => v + ((x - region.center[k]) / region.radii[k]) ** 2,
              0,
            ) <= 1
          )
            colour = region.color;
        }
      }
      const cc = paint(colour),
        variation = look.id === "voxel" ? 0 : (f.variation ?? 0);
      const hash =
        Math.sin(
          fi * 3.11 + ids.reduce((a, x) => a + x, 0) * 7.331 + (f.seed || 0),
        ) * 43758.5453;
      const mult = 1 + variation * (hash - Math.floor(hash) - 0.5);
      cc.multiplyScalar(mult);
      cc.r = Math.min(1, Math.max(0, cc.r));
      cc.g = Math.min(1, Math.max(0, cc.g));
      cc.b = Math.min(1, Math.max(0, cc.b));
      for (const tri of triangulate(ids, verts)) {
        const ix = m.determinant() < 0 ? [tri[0], tri[2], tri[1]] : tri,
          aa = verts[ix[0]],
          b = verts[ix[1]],
          c = verts[ix[2]];
        if (b.clone().sub(aa).cross(c.clone().sub(aa)).lengthSq() < 1e-24)
          continue;
        for (const k of ix) {
          P.push(...verts[k].toArray());
          C.push(cc.r, cc.g, cc.b);
          AN.push(...(analyticWorld?.[k]?.toArray() || [0, 0, 0]));
          const [si, sw] = skin(ws[k]);
          SI.push(...si);
          SW.push(...sw);
        }
      }
    }
    const smoothAngle =
      f.smooth_angle ?? (look.flat ? 0 : f.kind === "poly" || f.hard ? 35 : 70);
    if (!Number.isFinite(smoothAngle) || smoothAngle < 0 || smoothAngle > 89)
      bad("smooth_angle must be 0..89");
    ranges.push({
      start,
      count: P.length / 3 - start,
      smoothAngle,
      analytic: !!analyticWorld,
      kind: f.kind,
      voxelBox: !!f.voxel_box,
      material: f.material || null,
      source_part: f.source_part || null,
      source_path: f.source_path || null,
    });
  }
  if (!P.length || P.length / 9 > 30000) bad("Triangle budget");
  const g = new T.BufferGeometry();
  g.setAttribute("position", new T.Float32BufferAttribute(P, 3));
  g.setAttribute("color", new T.Float32BufferAttribute(C, 3));
  g.setAttribute(
    "uv",
    new T.Float32BufferAttribute(Array((P.length / 3) * 2).fill(0), 2),
  );
  g.computeVertexNormals();
  if (rig.length) {
    g.setAttribute("skinIndex", new T.Uint16BufferAttribute(SI, 4));
    g.setAttribute("skinWeight", new T.Float32BufferAttribute(SW, 4));
  }
  g.userData.rig = rig;
  g.userData.formRanges = ranges;
  g.userData.anatomy = {
    authoring: "explicit-faceted-profiles",
    origin: "semantic",
    style: look.id,
    flatShaded: look.flat,
    autoDecimation: false,
    roundness: look.flat ? 0 : roundness,
    materialGroups: ranges,
  };
  smoothNormals(g, ranges);
  const normal = g.attributes.normal;
  for (let i = 0; i < normal.count; i++)
    if (AN[i * 3] || AN[i * 3 + 1] || AN[i * 3 + 2])
      normal.setXYZ(i, AN[i * 3], AN[i * 3 + 1], AN[i * 3 + 2]);
  const seamNormals = stitched.report.map((r) => ({
    ...r,
    points: look.subdivide
      ? [
          ...r.points,
          ...r.points.map((p, i) =>
            p.map((v, k) => (v + r.points[(i + 1) % r.points.length][k]) * 0.5),
          ),
        ]
      : r.points,
  }));
  Seams.normals(g, seamNormals, look.flat ? 32 : 55);
  g.userData.anatomy.normalPolicy =
    "edge-connected-per-form-area-corner-angle; crease islands; analytic rounded-box panels";
  g.userData.anatomy.seams = stitched.report.map(
    ({ points: _points, ...r }) => r,
  );
  g.computeBoundingBox();
  return g;
}
const facets = { build, triangulate, smoothNormals, version: "2.1.0" };

export default facets;
