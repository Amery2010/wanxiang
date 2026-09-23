import * as Guards from "./three-guards.js";
/* Wanxiang3D 1.7 — portable file boundary and resource ownership.
 * This module deliberately does not reference preview transforms or DOM state.
 * Exported GLBs are validated snapshots of recipes, not screenshots of a scene.
 */
import * as T from "./three.js";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
interface View {
  buffer?: number;
  byteOffset?: number;
  byteLength: number;
  byteStride?: number;
}
interface Accessor {
  count: number;
  type: string;
  componentType: number;
  bufferView?: number;
  byteOffset?: number;
  min?: number[];
  max?: number[];
}
interface Node {
  children?: number[];
  mesh?: number;
  matrix?: number[];
  translation?: number[];
  rotation?: number[];
  scale?: number[];
}
export interface GLBDocument {
  asset?: { version?: string };
  buffers?: { uri?: string; byteLength: number }[];
  images?: { uri?: string; bufferView: number; mimeType: string }[];
  extensionsRequired?: string[];
  bufferViews?: View[];
  accessors?: Accessor[];
  nodes?: Node[];
  meshes?: {
    primitives?: {
      mode?: number;
      attributes?: { POSITION?: number };
      indices?: number;
    }[];
  }[];
  skins?: { joints: number[] }[];
  materials?: unknown[];
}
export interface Inspection {
  doc: GLBDocument;
  triangles: number;
  vertices: number;
  bytes: number;
}
export interface PreparedGLB {
  inspection: Inspection;
  load(): Promise<GLTF>;
}
interface CachedAsset {
  glb?: string;
  dynamic?: boolean;
  _usedAt?: number;
  _builtSignature?: unknown;
}

const LIMITS = Object.freeze({
  bytes: 64_000_000,
  nodes: 10000,
  triangles: 500000,
  vertices: 2000000,
  depth: 128,
});
function invalid(message: string): never {
  throw Error("GLB_INVALID: " + message);
}
function integer(n: unknown, min: number, max: number, label: string): number {
  if (typeof n !== "number" || !Number.isInteger(n) || n < min || n > max)
    invalid(label);
  return n;
}
export function inspect(buffer: ArrayBuffer): Inspection {
  if (
    !(buffer instanceof ArrayBuffer) ||
    buffer.byteLength < 28 ||
    buffer.byteLength > LIMITS.bytes
  )
    invalid("file size");
  const v = new DataView(buffer);
  if (
    v.getUint32(0, true) !== 0x46546c67 ||
    v.getUint32(4, true) !== 2 ||
    v.getUint32(8, true) !== buffer.byteLength
  )
    invalid("header / declared length");
  let doc: GLBDocument | null = null;
  let binLength = 0,
    binStart = 0,
    chunks = 0;
  for (let p = 12; p < buffer.byteLength;) {
    if (p + 8 > buffer.byteLength) invalid("truncated chunk");
    const length = v.getUint32(p, true),
      type = v.getUint32(p + 4, true);
    if (length % 4 || p + 8 + length > buffer.byteLength)
      invalid("chunk boundary");
    if (!chunks && type !== 0x4e4f534a) invalid("JSON must be first");
    if (type === 0x4e4f534a) {
      if (doc || length > 12_000_000) invalid("JSON budget / duplicate");
      doc = JSON.parse(
        new TextDecoder("utf8", { fatal: true }).decode(
          new Uint8Array(buffer, p + 8, length),
        ),
      ) as GLBDocument;
    } else if (type === 0x004e4942) {
      if (binStart) invalid("duplicate BIN");
      binStart = p + 8;
      binLength = length;
    }
    p += 8 + length;
    chunks++;
  }
  if (!doc || doc.asset?.version !== "2.0") invalid("asset version");
  if (
    (doc.buffers || []).some((b) => b.uri) ||
    (doc.images || []).some((i) => i.uri)
  )
    invalid("external / data URI resources are not accepted; use embedded GLB");
  if ((doc.buffers || []).length > 1) invalid("multiple buffers");
  if (
    doc.buffers?.length &&
    (doc.buffers[0].byteLength > binLength ||
      doc.buffers[0].byteLength < binLength - 3)
  )
    invalid("binary length");
  const supportedRequired = new Set([
    "KHR_materials_unlit",
    "KHR_texture_transform",
  ]);
  if ((doc.extensionsRequired || []).some((e) => !supportedRequired.has(e)))
    invalid("unsupported required extension");
  const views = doc.bufferViews || [],
    accessors = doc.accessors || [],
    nodes = doc.nodes || [];
  if (
    nodes.length > LIMITS.nodes ||
    accessors.length > 40000 ||
    views.length > 50000
  )
    invalid("structure budget");
  for (const b of views) {
    if ((b.buffer ?? 0) !== 0) invalid("buffer index");
    integer(b.byteOffset ?? 0, 0, binLength, "view offset");
    integer(b.byteLength, 0, binLength - (b.byteOffset ?? 0), "view length");
  }
  const components: Record<string, number> = {
    SCALAR: 1,
    VEC2: 2,
    VEC3: 3,
    VEC4: 4,
    MAT2: 4,
    MAT3: 9,
    MAT4: 16,
  };
  const bytes: Record<number, number> = {
    5120: 1,
    5121: 1,
    5122: 2,
    5123: 2,
    5125: 4,
    5126: 4,
  };
  for (const a of accessors) {
    const count = integer(a.count, 1, LIMITS.vertices * 3, "accessor count"),
      size = components[a.type] * bytes[a.componentType];
    if (!size) invalid("accessor type");
    if (a.bufferView !== undefined) {
      const bv =
        views[integer(a.bufferView, 0, views.length - 1, "accessor view")];
      const stride = bv.byteStride ?? size;
      integer(stride, size, 252, "accessor stride");
      const offset = integer(
        a.byteOffset ?? 0,
        0,
        bv.byteLength,
        "accessor offset",
      );
      if (offset + (count - 1) * stride + size > bv.byteLength)
        invalid("accessor exceeds view");
    }
    for (const key of ["min", "max"] as const)
      if (a[key] && (!Array.isArray(a[key]) || !a[key].every(Number.isFinite)))
        invalid("non-finite bounds");
  }
  const meshTriangles: number[] = [],
    meshVertices: number[] = [];
  for (const m of doc.meshes || []) {
    let tris = 0,
      verts = 0;
    for (const p of m.primitives || []) {
      if ((p.mode ?? 4) !== 4) invalid("triangle primitives only");
      const a =
        accessors[
          integer(p.attributes?.POSITION, 0, accessors.length - 1, "POSITION")
        ];
      if (a.type !== "VEC3") invalid("position type");
      verts += a.count;
      const count =
        p.indices === undefined
          ? a.count
          : accessors[integer(p.indices, 0, accessors.length - 1, "indices")]
              .count;
      if (count % 3) invalid("incomplete triangle");
      tris += count / 3;
    }
    meshTriangles.push(tris);
    meshVertices.push(verts);
  }
  // Kahn traversal rejects cycles/multiple parents without recursively exhausting JS.
  const parents = new Int32Array(nodes.length),
    depth = new Int32Array(nodes.length);
  let triangles = 0,
    vertices = 0;
  nodes.forEach((n) => {
    for (const key of ["matrix", "translation", "rotation", "scale"] as const)
      if (n[key] && (!Array.isArray(n[key]) || !n[key].every(Number.isFinite)))
        invalid("non-finite transform");
    for (const c of n.children || []) {
      integer(c, 0, nodes.length - 1, "child index");
      if (++parents[c] > 1) invalid("multiple parents");
    }
    if (n.mesh !== undefined) {
      integer(n.mesh, 0, meshTriangles.length - 1, "mesh index");
      triangles += meshTriangles[n.mesh];
      vertices += meshVertices[n.mesh];
    }
  });
  if (triangles > LIMITS.triangles || vertices > LIMITS.vertices)
    invalid("expanded geometry budget");
  const q: number[] = [];
  parents.forEach((p, i) => {
    if (!p) q.push(i);
  });
  for (let i = 0; i < q.length; i++)
    for (const c of nodes[q[i]].children || []) {
      depth[c] = depth[q[i]] + 1;
      if (depth[c] > LIMITS.depth) invalid("hierarchy depth");
      if (--parents[c] === 0) q.push(c);
    }
  if (q.length !== nodes.length) invalid("node cycle");
  for (const skin of doc.skins || []) {
    if (!skin.joints?.length || skin.joints.length > 256)
      invalid("skin bone budget");
    for (const j of skin.joints)
      integer(j, 0, nodes.length - 1, "bone reference");
  }
  for (const im of doc.images || []) {
    const bv = views[integer(im.bufferView, 0, views.length - 1, "image view")];
    if (!["image/png", "image/jpeg", "image/webp"].includes(im.mimeType))
      invalid("image encoding");
    if (im.mimeType === "image/png" && bv.byteLength >= 24) {
      const p = binStart + (bv.byteOffset || 0),
        w = v.getUint32(p + 16, false),
        h = v.getUint32(p + 20, false);
      if (!w || !h || w > 4096 || h > 4096 || w * h > 16777216)
        invalid("PNG pixel budget");
    }
  }
  return { doc, triangles, vertices, bytes: buffer.byteLength };
}
export function dispose(root?: T.Object3D | null) {
  if (!root) return;
  const geos = new Set<T.BufferGeometry>(),
    mats = new Set<T.Material>(),
    textures = new Set<T.Texture>(),
    skeletons = new Set<T.Skeleton>(),
    images = new Set<{ close(): void }>();
  root.traverse((o) => {
    const mesh = o as T.Mesh;
    if (mesh.geometry) geos.add(mesh.geometry);
    const skeleton = (o as T.SkinnedMesh).skeleton;
    if (skeleton) skeletons.add(skeleton);
    for (const m of mesh.material
      ? Array.isArray(mesh.material)
        ? mesh.material
        : [mesh.material]
      : [])
      mats.add(m);
  });
  mats.forEach((m) =>
    Object.values(m).forEach((v: unknown) => {
      if (Guards.isTexture(v)) textures.add(v);
    }),
  );
  skeletons.forEach((s) => s.dispose());
  geos.forEach((g) => g.dispose());
  textures.forEach((t) => {
    t.dispose();
    const im: unknown = t.image;
    if (
      im &&
      typeof im === "object" &&
      "close" in im &&
      typeof im.close === "function"
    )
      images.add(im as { close(): void });
  });
  images.forEach((im) => im.close());
  mats.forEach((m) => m.dispose());
}
function parse(buffer: ArrayBuffer): Promise<GLTF> {
  const manager = new T.LoadingManager();
  manager.setURLModifier((url) => {
    if (/^(blob:|data:)/.test(url)) return url;
    invalid("external URL blocked");
  });
  return new T.GLTFLoader(manager).parseAsync(buffer, "");
}
export async function load(buffer: ArrayBuffer): Promise<GLTF> {
  return prepare(buffer).load();
}
export function prepare(buffer: ArrayBuffer): PreparedGLB {
  // Own the validated bytes: callers may mutate or transfer their input later.
  if (
    !(buffer instanceof ArrayBuffer) ||
    buffer.byteLength < 28 ||
    buffer.byteLength > LIMITS.bytes
  )
    invalid("file size");
  const snapshot = buffer.slice(0);
  const inspection = inspect(snapshot);
  return { inspection, load: () => parse(snapshot) };
}
export function trimCache(
  assets: CachedAsset[],
  active: CachedAsset | null,
  max = 32 * 1024 * 1024,
) {
  // JS strings may use UTF-16. Account for base64, not only raw GLB length.
  let total = assets.reduce((n, a) => n + (a.glb?.length || 0) * 2, 0);
  for (const a of [...assets].sort(
    (a, b) => (a._usedAt || 0) - (b._usedAt || 0),
  )) {
    if (total <= max) break;
    if (a !== active && a.dynamic && a.glb) {
      total -= a.glb.length * 2;
      delete a.glb;
      delete a._builtSignature;
    }
  }
  return total;
}
export { LIMITS };
export default { inspect, prepare, load, dispose, trimCache, LIMITS };
