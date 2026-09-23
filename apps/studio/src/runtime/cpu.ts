export interface CPUShadow {
  depth: Float32Array;
  positions: Float32Array;
  resolution: number;
  span: number;
  center: number[];
  right: number[];
  up: number[];
  direction: number[];
  floor: number;
}
export interface CPUData {
  vertices: Float32Array;
  normals: Float32Array;
  uv: Float32Array;
  colors: Float32Array;
  faces: Uint32Array;
  matids: Uint16Array;
  materials: CPUMaterial[];
  center: number[];
  span: number;
  shadow?: CPUShadow | null;
}
export interface CPUMaterial {
  style: string;
  texture: Uint8ClampedArray;
  size: number;
  color: number[];
  emissive: number[];
  cutoff: number;
  repeatS: boolean;
  repeatT: boolean;
}
export interface CPUOptions {
  width: number;
  height: number;
  az: number;
  el: number;
  zoom: number;
  wire: boolean;
  center?: number[];
  span?: number;
  lighting: string;
}
/* Presentation-only shadow maps for the actual decoded GLB. No texture / network input.
 * This module is also serialized into the CPU raster worker; no THREE dependency.
 */
export function prepareCPUShadows(d: CPUData) {
  if (!d.vertices.length || !d.faces.length) {
    d.shadow = null;
    return d;
  }
  const resolution = d.faces.length > 300000 ? 256 : 512,
    shadow = new Float32Array(resolution * resolution).fill(-1e20),
    a = (-38 * Math.PI) / 180,
    e = (57 * Math.PI) / 180;
  const right = [Math.cos(a), 0, -Math.sin(a)],
    direction = [
      Math.sin(a) * Math.cos(e),
      Math.sin(e),
      Math.cos(a) * Math.cos(e),
    ],
    up = [-Math.sin(a) * Math.sin(e), Math.cos(e), -Math.cos(a) * Math.sin(e)],
    span = d.span * 1.1,
    center = d.center,
    p = new Float32Array(d.vertices.length);
  let floor = Infinity;
  for (let i = 0; i < p.length; i += 3) {
    const x = d.vertices[i] - center[0],
      y = d.vertices[i + 1] - center[1],
      z = d.vertices[i + 2] - center[2];
    p[i] =
      ((x * right[0] + y * right[1] + z * right[2]) / span) * resolution +
      resolution / 2;
    p[i + 1] =
      (-(x * up[0] + y * up[1] + z * up[2]) / span) * resolution +
      resolution / 2;
    p[i + 2] = x * direction[0] + y * direction[1] + z * direction[2];
    floor = Math.min(floor, d.vertices[i + 1]);
  }
  for (let k = 0; k < d.faces.length; k += 3) {
    const ia = d.faces[k] * 3,
      ib = d.faces[k + 1] * 3,
      ic = d.faces[k + 2] * 3,
      x0 = p[ia],
      y0 = p[ia + 1],
      x1 = p[ib],
      y1 = p[ib + 1],
      x2 = p[ic],
      y2 = p[ic + 1],
      area = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2);
    if (Math.abs(area) < 1e-8) continue;
    const minx = Math.max(0, Math.floor(Math.min(x0, x1, x2))),
      maxx = Math.min(resolution - 1, Math.ceil(Math.max(x0, x1, x2))),
      miny = Math.max(0, Math.floor(Math.min(y0, y1, y2))),
      maxy = Math.min(resolution - 1, Math.ceil(Math.max(y0, y1, y2)));
    for (let y = miny; y <= maxy; y++)
      for (let x = minx; x <= maxx; x++) {
        const aa =
            ((y1 - y2) * (x + 0.5 - x2) + (x2 - x1) * (y + 0.5 - y2)) / area,
          bb = ((y2 - y0) * (x + 0.5 - x2) + (x0 - x2) * (y + 0.5 - y2)) / area,
          cc = 1 - aa - bb;
        if (aa < 0 || bb < 0 || cc < 0) continue;
        const z = aa * p[ia + 2] + bb * p[ib + 2] + cc * p[ic + 2],
          i = y * resolution + x;
        if (z > shadow[i]) shadow[i] = z;
      }
  }
  d.shadow = {
    depth: shadow,
    positions: p,
    resolution,
    span,
    center,
    right,
    up,
    direction,
    floor: floor - d.span * 0.0015,
  };
  return d;
}
export function cpuShadowVisibility(
  s: CPUShadow | null | undefined,
  x: number,
  y: number,
  z: number,
  bias: number,
) {
  if (!s || x < 1 || y < 1 || x >= s.resolution - 2 || y >= s.resolution - 2)
    return 1;
  let lit = 0;
  for (let j = -1; j <= 1; j++)
    for (let i = -1; i <= 1; i++)
      lit +=
        s.depth[(Math.floor(y) + j) * s.resolution + Math.floor(x) + i] >
        z + bias
          ? 0
          : 1;
  return lit / 9;
}

export function cpuRaster(
  d: CPUData,
  opt: CPUOptions,
  shadowVisibility = cpuShadowVisibility,
) {
  const width = opt.width,
    height = opt.height,
    out = new Uint8ClampedArray(width * height * 4),
    depth = new Float32Array(width * height);
  depth.fill(-1e30);
  const a = (opt.az * Math.PI) / 180,
    e = (opt.el * Math.PI) / 180,
    sa = Math.sin(a),
    ca = Math.cos(a),
    se = Math.sin(e),
    ce = Math.cos(e),
    v = d.vertices,
    n = d.normals,
    uv = d.uv,
    f = d.faces,
    screen = new Float32Array(v.length),
    scale = height / ((opt.span || d.span) / opt.zoom),
    c = opt.center || d.center;
  for (let i = 0; i < v.length; i += 3) {
    const x = v[i] - c[0],
      y = v[i + 1] - c[1],
      z = v[i + 2] - c[2];
    screen[i] = (x * ca - z * sa) * scale + width / 2;
    screen[i + 1] = -(-x * sa * se + y * ce - z * ca * se) * scale + height / 2;
    screen[i + 2] = x * sa * ce + y * se + z * ca * ce;
  }
  const l = d.shadow?.direction || [0.477, 0.755, 0.448],
    shadow = d.shadow,
    lp = shadow?.positions || new Float32Array();
  for (let t = 0; t < f.length; t += 3) {
    const ia = f[t],
      ib = f[t + 1],
      ic = f[t + 2],
      a0 = ia * 3,
      b0 = ib * 3,
      c0 = ic * 3,
      x0 = screen[a0],
      y0 = screen[a0 + 1],
      x1 = screen[b0],
      y1 = screen[b0 + 1],
      x2 = screen[c0],
      y2 = screen[c0 + 1];
    const area = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2);
    if (Math.abs(area) < 1e-8) continue;
    const minx = Math.max(0, Math.floor(Math.min(x0, x1, x2))),
      maxx = Math.min(width - 1, Math.ceil(Math.max(x0, x1, x2))),
      miny = Math.max(0, Math.floor(Math.min(y0, y1, y2))),
      maxy = Math.min(height - 1, Math.ceil(Math.max(y0, y1, y2))),
      mat = d.materials[d.matids[t / 3]],
      tex = mat.texture,
      ts = mat.size;
    for (let y = miny; y <= maxy; y++)
      for (let x = minx; x <= maxx; x++) {
        const aa =
            ((y1 - y2) * (x + 0.5 - x2) + (x2 - x1) * (y + 0.5 - y2)) / area,
          bb = ((y2 - y0) * (x + 0.5 - x2) + (x0 - x2) * (y + 0.5 - y2)) / area,
          cc = 1 - aa - bb;
        if (aa < 0 || bb < 0 || cc < 0) continue;
        const z =
            aa * screen[a0 + 2] + bb * screen[b0 + 2] + cc * screen[c0 + 2],
          idx = y * width + x;
        if (z <= depth[idx]) continue;
        const u = aa * uv[ia * 2] + bb * uv[ib * 2] + cc * uv[ic * 2],
          vv = aa * uv[ia * 2 + 1] + bb * uv[ib * 2 + 1] + cc * uv[ic * 2 + 1],
          tx = Math.floor(
            (mat.repeatS ? u - Math.floor(u) : Math.max(0, Math.min(1, u))) *
              (ts - 1),
          ),
          ty = Math.floor(
            (mat.repeatT ? vv - Math.floor(vv) : Math.max(0, Math.min(1, vv))) *
              (ts - 1),
          ),
          ti = (ty * ts + tx) * 4;
        if (tex[ti + 3] / 255 < mat.cutoff) continue;
        let nx = aa * n[a0] + bb * n[b0] + cc * n[c0],
          ny = aa * n[a0 + 1] + bb * n[b0 + 1] + cc * n[c0 + 1],
          nz = aa * n[a0 + 2] + bb * n[b0 + 2] + cc * n[c0 + 2];
        const len = Math.hypot(nx, ny, nz) || 1;
        nx /= len;
        ny /= len;
        nz /= len;
        const direct = Math.max(0, nx * l[0] + ny * l[1] + nz * l[2]);
        const visibility = shadow
          ? shadowVisibility(
              shadow,
              aa * lp[a0] + bb * lp[b0] + cc * lp[c0],
              aa * lp[a0 + 1] + bb * lp[b0 + 1] + cc * lp[c0 + 1],
              aa * lp[a0 + 2] + bb * lp[b0 + 2] + cc * lp[c0 + 2],
              (shadow.span / shadow.resolution) * (1.4 + 2.4 * (1 - direct)),
            )
          : 1;
        const night = opt.lighting === "night",
          gray = opt.lighting === "neutral";
        const shade =
          (night ? 0.11 : 0.35) +
          (night ? 0.085 : 0.12) * (ny * 0.5 + 0.5) +
          (night ? 0.23 : 0.61) *
            (mat.style === "toon"
              ? direct < 0.25
                ? 0.13
                : direct < 0.65
                  ? 0.5
                  : 0.97
              : direct) *
            (0.18 + 0.82 * visibility) +
          0.09 * Math.max(0, -nx * 0.72 + ny * 0.28 - nz * 0.62);
        const o = idx * 4;
        if (opt.wire && Math.min(aa, bb, cc) < 0.038) {
          out[o] = 122;
          out[o + 1] = 223;
          out[o + 2] = 182;
        } else
          for (let k = 0; k < 3; k++) {
            const color = gray
              ? 0.53
              : Math.pow(tex[ti + k] / 255, 2.2) *
                mat.color[k] *
                (d.colors
                  ? aa * d.colors[a0 + k] +
                    bb * d.colors[b0 + k] +
                    cc * d.colors[c0 + k]
                  : 1);
            const linear =
              color * shade * (night ? [0.8, 0.88, 1.1][k] : 1) +
              (gray ? 0 : mat.emissive[k] * (night ? 0.72 : 0.14));
            out[o + k] = Math.min(
              255,
              Math.pow(Math.max(0, linear), 1 / 2.2) * 255,
            );
          }
        out[o + 3] = 255;
        depth[idx] = z;
      }
  }
  // Invisible presentation ground receives real mesh shadows; it is never exported.
  if (shadow && se > 0.08) {
    const s = shadow,
      dir = [sa * ce, se, ca * ce],
      right = [ca, 0, -sa],
      up = [-sa * se, ce, -ca * se];
    for (let y = 0; y < height; y++)
      for (let x = 0; x < width; x++) {
        const at = (y * width + x) * 4;
        if (out[at + 3]) continue;
        const u = (x + 0.5 - width / 2) / scale,
          w = -(y + 0.5 - height / 2) / scale,
          t = (s.floor - c[1] - up[1] * w) / dir[1],
          px = c[0] + right[0] * u + up[0] * w + dir[0] * t - s.center[0],
          py = s.floor - s.center[1],
          pz = c[2] + right[2] * u + up[2] * w + dir[2] * t - s.center[2],
          sx =
            ((px * s.right[0] + py * s.right[1] + pz * s.right[2]) / s.span) *
              s.resolution +
            s.resolution / 2,
          sy =
            (-(px * s.up[0] + py * s.up[1] + pz * s.up[2]) / s.span) *
              s.resolution +
            s.resolution / 2,
          sz = px * s.direction[0] + py * s.direction[1] + pz * s.direction[2],
          vis = shadowVisibility(s, sx, sy, sz, (s.span / s.resolution) * 1.4);
        if (vis < 1) {
          out[at] = 42;
          out[at + 1] = 62;
          out[at + 2] = 43;
          out[at + 3] = Math.round((1 - vis) * 48);
        }
      }
  }
  return out;
}
