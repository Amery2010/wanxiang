import type { GeometryParameters, FormRange } from "./geometry-types.js";
import * as T from "./three.js";
/* Portable appearance geometry. Shared verbatim by Node and the browser.
 * Voxel output is real exposed axis-aligned faces, not a pixelation shader.
 * The common part grid preserves the source bounds and rigs. Closed individual
 * forms are filled separately before union, so overlapping volumes do not XOR.
 */

function validate(p: GeometryParameters) {
  for (const [key, lo, hi] of [
    ["paint_strength", 0, 1],
    ["texture_scale", 0.25, 8],
  ] as const) {
    if (
      p[key] !== undefined &&
      (!Number.isFinite(p[key]) || p[key] < lo || p[key] > hi)
    )
      throw Error("SURFACE_INVALID: " + key);
  }
  if (
    p.voxel_resolution !== undefined &&
    (!Number.isInteger(p.voxel_resolution) ||
      p.voxel_resolution < 6 ||
      p.voxel_resolution > 40)
  )
    throw Error(
      "SURFACE_INVALID: voxel_resolution must be an integer in 6..40",
    );
  if (
    p.seed !== undefined &&
    (!Number.isInteger(p.seed) || p.seed < 0 || p.seed > 4294967295)
  )
    throw Error("SURFACE_INVALID: seed must be uint32");
}
function voxelize(src: T.BufferGeometry, p: GeometryParameters) {
  const pos = src.attributes.position,
    color = src.attributes.color,
    si = src.attributes.skinIndex,
    sw = src.attributes.skinWeight;
  const b = src.boundingBox!.clone(),
    lo = b.min.toArray(),
    size = b.getSize(new T.Vector3()).toArray();
  const resolution = p.voxel_resolution ?? 16,
    step = Math.max(...size) / resolution;
  const dims = size.map((s) => Math.max(1, Math.ceil(s / step - 1e-7)));
  const unit = size.map((s, k) => s / dims[k]);
  const [nx, ny, nz] = dims,
    total = nx * ny * nz;
  if (total > 64000) throw Error("SURFACE_BUDGET: grid");
  const grid = new Int32Array(total);
  grid.fill(-1);
  const index = (x: number, y: number, z: number) => x + nx * (y + ny * z);
  const coord = (v: number, k: number) =>
    Math.max(
      0,
      Math.min(dims[k] - 1, Math.floor((v - lo[k]) / Math.max(1e-12, unit[k]))),
    );
  const vertex = (i: number) => [pos.getX(i), pos.getY(i), pos.getZ(i)];
  const put = (v: number[], i: number) => {
    grid[index(coord(v[0], 0), coord(v[1], 1), coord(v[2], 2))] = i;
  };
  const ranges: FormRange[] = src.userData.formRanges || [
    { start: 0, count: pos.count },
  ];
  for (const range of ranges) {
    const end = range.start + range.count;
    if (range.voxelBox) {
      const mn = [Infinity, Infinity, Infinity],
        mx = [-Infinity, -Infinity, -Infinity];
      for (let i = range.start; i < end; i++) {
        const v = vertex(i);
        for (let k = 0; k < 3; k++) {
          mn[k] = Math.min(mn[k], v[k]);
          mx[k] = Math.max(mx[k], v[k]);
        }
      }
      const a = mn.map((v, k) => coord(v + 1e-8, k)),
        c = mx.map((v, k) => coord(v - 1e-8, k));
      for (let z = a[2]; z <= c[2]; z++)
        for (let y = a[1]; y <= c[1]; y++)
          for (let x = a[0]; x <= c[0]; x++) grid[index(x, y, z)] = range.start;
      continue;
    }
    const columns = new Map<number, number[][]>();
    for (let i = range.start; i < end; i += 3) {
      const a = vertex(i),
        c = vertex(i + 1),
        d = vertex(i + 2);
      const ab = c.map((v, k) => v - a[k]),
        ac = d.map((v, k) => v - a[k]);
      const length = Math.max(
        Math.hypot(...ab),
        Math.hypot(...ac),
        Math.hypot(...c.map((v, k) => v - d[k])),
      );
      const samples = Math.max(
        1,
        Math.min(90, Math.ceil((length / step) * 1.4)),
      );
      // Conservative shell also covers thin leaves, horns and open panels.
      for (let u = 0; u <= samples; u++)
        for (let v = 0; v <= samples - u; v++)
          put(
            a.map((x, k) => x + (ab[k] * u) / samples + (ac[k] * v) / samples),
            i + (u > samples / 2 ? 1 : v > samples / 2 ? 2 : 0),
          );
      const det = ab[0] * ac[2] - ab[2] * ac[0];
      if (Math.abs(det) < 1e-12) continue;
      const xmin = coord(Math.min(a[0], c[0], d[0]), 0),
        xmax = coord(Math.max(a[0], c[0], d[0]), 0);
      const zmin = coord(Math.min(a[2], c[2], d[2]), 2),
        zmax = coord(Math.max(a[2], c[2], d[2]), 2);
      for (let z = zmin; z <= zmax; z++)
        for (let x = xmin; x <= xmax; x++) {
          const dx = lo[0] + (x + 0.5) * unit[0] - a[0],
            dz = lo[2] + (z + 0.5) * unit[2] - a[2];
          const u = (dx * ac[2] - dz * ac[0]) / det,
            v = (ab[0] * dz - ab[2] * dx) / det;
          if (u < -1e-7 || v < -1e-7 || u + v > 1.0000001) continue;
          const k = x + nx * z;
          if (!columns.has(k)) columns.set(k, []);
          columns
            .get(k)!
            .push([
              a[1] + u * ab[1] + v * ac[1],
              i + (u > 0.5 ? 1 : v > 0.5 ? 2 : 0),
            ]);
        }
    }
    for (const [k, hits] of columns) {
      hits.sort((a, b) => a[0] - b[0]);
      const h = hits.filter(
        (a, i) =>
          !i || Math.abs(a[0] - hits[i - 1][0]) > Math.max(1e-8, step * 1e-5),
      );
      for (let j = 0; j + 1 < h.length; j += 2) {
        const y0 = coord(h[j][0] + 1e-8, 1),
          y1 = coord(h[j + 1][0] - 1e-8, 1),
          z = Math.floor(k / nx),
          x = k % nx;
        for (let y = y0; y <= y1; y++)
          grid[index(x, y, z)] = y - y0 < (y1 - y0) / 2 ? h[j][1] : h[j + 1][1];
      }
    }
  }
  const P: number[] = [],
    C: number[] = [],
    N: number[] = [],
    SI: number[] = [],
    SW: number[] = [],
    materialGroups: FormRange[] = [];
  const owners = new Int32Array(pos.count);
  ranges.forEach((r, j) => owners.fill(j, r.start, r.start + r.count));
  let occupied = 0,
    quads = 0;
  // Greedy same-pigment / same-skin faces; one quad per coplanar region, no cubes
  // hidden inside cubes. Pixel detail is texture, not thousands of tiny objects.
  const sampleKey = (i: number) => {
    if (i < 0) return "";
    return [
      ranges[owners[i]]?.material || "",
      Math.round(color.getX(i) * 255),
      Math.round(color.getY(i) * 255),
      Math.round(color.getZ(i) * 255),
      ...(si ? Array.from(si.array.subarray(i * 4, i * 4 + 4)) : []),
      ...(sw
        ? Array.from(sw.array.subarray(i * 4, i * 4 + 4)).map((v) =>
            Math.round(v * 32),
          )
        : []),
    ].join(",");
  };
  const keys = new Map<number, string>();
  const keyOf = (i: number) => {
    if (!keys.has(i)) keys.set(i, sampleKey(i));
    return keys.get(i);
  };
  for (const i of grid) if (i >= 0) occupied++;
  for (let axis = 0; axis < 3; axis++) {
    const u = (axis + 1) % 3,
      v = (axis + 2) % 3,
      w = dims[u],
      h = dims[v];
    for (const sign of [-1, 1])
      for (let layer = 0; layer < dims[axis]; layer++) {
        const mask = new Int32Array(w * h);
        mask.fill(-1);
        for (let j = 0; j < h; j++)
          for (let i = 0; i < w; i++) {
            const q = [0, 0, 0];
            q[axis] = layer;
            q[u] = i;
            q[v] = j;
            const val = grid[index(q[0], q[1], q[2])];
            if (val < 0) continue;
            q[axis] += sign;
            if (
              q[axis] < 0 ||
              q[axis] >= dims[axis] ||
              grid[index(q[0], q[1], q[2])] < 0
            )
              mask[i + w * j] = val;
          }
        for (let j = 0; j < h; j++)
          for (let i = 0; i < w;) {
            const val = mask[i + w * j];
            if (val < 0) {
              i++;
              continue;
            }
            const key = keyOf(val);
            let rw = 1,
              rh = 1;
            while (
              i + rw < w &&
              mask[i + rw + w * j] >= 0 &&
              keyOf(mask[i + rw + w * j]) === key
            )
              rw++;
            height: while (j + rh < h) {
              for (let x = 0; x < rw; x++)
                if (
                  mask[i + x + w * (j + rh)] < 0 ||
                  keyOf(mask[i + x + w * (j + rh)]) !== key
                )
                  break height;
              rh++;
            }
            const corners = [
              [i, j],
              [i + rw, j],
              [i + rw, j + rh],
              [i, j + rh],
            ].map(([x, y]) => {
              const q = lo.slice();
              q[axis] += (layer + (sign > 0 ? 1 : 0)) * unit[axis];
              q[u] += x * unit[u];
              q[v] += y * unit[v];
              return q;
            });
            const normal = [0, 0, 0];
            normal[axis] = sign;
            for (const k of sign > 0
              ? [0, 1, 2, 0, 2, 3]
              : [0, 2, 1, 0, 3, 2]) {
              P.push(...corners[k]);
              N.push(...normal);
              C.push(color.getX(val), color.getY(val), color.getZ(val));
              if (si) {
                SI.push(...si.array.subarray(val * 4, val * 4 + 4));
                SW.push(...sw.array.subarray(val * 4, val * 4 + 4));
              }
            }
            const role = ranges[owners[val]]?.material || null,
              last = materialGroups.at(-1);
            if (last && last.material === role) last.count += 6;
            else
              materialGroups.push({
                start: P.length / 3 - 6,
                count: 6,
                material: role,
              });
            quads++;
            if (quads > 15000)
              throw Error("SURFACE_BUDGET: lower voxel_resolution");
            for (let y = 0; y < rh; y++)
              mask.fill(-1, i + w * (j + y), i + rw + w * (j + y));
            i += rw;
          }
      }
  }
  if (!P.length) throw Error("SURFACE_INVALID: empty voxel output");
  const g = new T.BufferGeometry();
  g.setAttribute("position", new T.Float32BufferAttribute(P, 3));
  g.setAttribute("normal", new T.Float32BufferAttribute(N, 3));
  g.setAttribute("color", new T.Float32BufferAttribute(C, 3));
  g.setAttribute(
    "uv",
    new T.Float32BufferAttribute(new Float32Array((P.length / 3) * 2), 2),
  );
  if (si) {
    g.setAttribute("skinIndex", new T.Uint16BufferAttribute(SI, 4));
    g.setAttribute("skinWeight", new T.Float32BufferAttribute(SW, 4));
  }
  g.userData = {
    rig: src.userData.rig,
    anatomy: {
      ...src.userData.anatomy,
      materialGroups,
      voxel: {
        resolution,
        occupied,
        exposedQuads: quads,
        greedy: true,
        method: "per-form-solid-union",
        grid: dims,
      },
    },
  };
  g.computeBoundingBox();
  src.dispose();
  return g;
}
const surfaces = { validate, voxelize };

export default surfaces;
