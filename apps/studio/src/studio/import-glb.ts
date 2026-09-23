import { sha256Bytes, to64 } from "../runtime/archive";
import type { Asset } from "./types";
interface GLBDocument {
  images?: { uri?: string }[];
  buffers?: { uri?: string }[];
  extensionsRequired?: string[];
  skins?: { joints?: number[] }[];
  nodes?: { mesh?: number }[];
  meshes?: {
    primitives: {
      mode?: number;
      indices?: number;
      attributes: { POSITION: number };
    }[];
  }[];
  accessors: { count: number }[];
  materials?: unknown[];
}
export function importGLBAsset(buffer: ArrayBuffer, name: string): Asset {
  if (buffer.byteLength > 64000000) throw Error("导入上限 64 MB");
  if (buffer.byteLength < 20) throw Error("无效 GLB 文件");
  const view = new DataView(buffer);
  if (view.getUint32(0, true) !== 0x46546c67 || view.getUint32(4, true) !== 2)
    throw Error("仅支持 GLB 2.0");
  if (
    view.getUint32(8, true) !== buffer.byteLength ||
    view.getUint32(16, true) !== 0x4e4f534a
  )
    throw Error("无效 GLB 数据块");
  const len = view.getUint32(12, true);
  if (len > buffer.byteLength - 20) throw Error("GLB JSON 数据块越界");
  const doc = JSON.parse(
    new TextDecoder().decode(new Uint8Array(buffer, 20, len)),
  ) as GLBDocument;
  if (
    (doc.images || []).some((i) => i.uri) ||
    (doc.buffers || []).some((i) => i.uri)
  )
    throw Error("不接受外部纹理或缓冲 URI");
  if (doc.extensionsRequired?.length)
    throw Error("导入器尚未配置该文件需要的压缩扩展");
  if ((doc.skins || []).some((s) => (s.joints?.length || 0) > 256))
    throw Error("每套蒙皮最多 256 骨骼");
  if ((doc.nodes?.length || 0) > 10000) throw Error("交互导入上限 1 万节点");
  const meshCounts = (doc.meshes || []).map((m) =>
    m.primitives.reduce((sum, p) => {
      if ((p.mode ?? 4) !== 4) throw Error("仅支持三角形模型");
      const accessor = doc.accessors[p.indices ?? p.attributes.POSITION];
      if (!accessor || !Number.isFinite(accessor.count))
        throw Error("无效网格 accessor");
      return sum + accessor.count / 3;
    }, 0),
  );
  const triangles = (doc.nodes || []).reduce(
    (sum, n) => sum + (n.mesh === undefined ? 0 : meshCounts[n.mesh] || 0),
    0,
  );
  if (triangles > 500000) throw Error("交互导入上限 50 万实例化三角面");
  const id = "import-" + Date.now();
  return {
    id,
    name: name.replace(/\.glb$/i, ""),
    family: "imported",
    category: "custom",
    local: true,
    glb: to64(buffer),
    sha256: sha256Bytes(new Uint8Array(buffer)),
    bytes: buffer.byteLength,
    report: {
      triangles,
      nodes: doc.nodes?.length || 0,
      materials: doc.materials?.length || 0,
      textures: doc.images?.length || 0,
    },
  };
}
