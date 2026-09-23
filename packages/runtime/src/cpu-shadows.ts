export interface CPUShadowMap {
  depth: Float32Array;
  positions: Float32Array;
  resolution: number;
  span: number;
  center: ArrayLike<number>;
  right: number[];
  up: number[];
  direction: number[];
  floor: number;
}
export interface CPUShadowData {
  vertices: ArrayLike<number>;
  faces: ArrayLike<number>;
  span: number;
  center: ArrayLike<number>;
  shadow?: CPUShadowMap | null;
}
/* Presentation-only shadow maps for the actual decoded GLB. No texture / network input.
 * This module is also serialized into the CPU raster worker; no THREE dependency.
 */
export function prepareCPUShadows<D extends CPUShadowData>(d: D): D {
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
  s: CPUShadowMap | null | undefined,
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

export default { prepareCPUShadows, cpuShadowVisibility };
