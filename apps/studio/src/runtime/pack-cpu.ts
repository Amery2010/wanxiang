import type { Object3D, Mesh, MeshStandardMaterial, SkinnedMesh } from "three";
import type { ThreeGlobal } from "./types";
import type { CPUData, CPUMaterial } from "./cpu";
export function effectivelyVisible(object: Object3D): boolean {
  for (let p: Object3D | null = object; p; p = p.parent)
    if (!p.visible) return false;
  return true;
}
export function packCPU(root: Object3D, T: ThreeGlobal): CPUData {
  root.updateMatrixWorld(true);
  const meshes: Mesh[] = [];
  let nv = 0,
    nf = 0;
  root.traverse((object) => {
    const o = object as Mesh;
    if (o.isMesh && o.geometry?.attributes.position && effectivelyVisible(o)) {
      meshes.push(o);
      nv += o.geometry.attributes.position.count;
      nf += o.geometry.index?.count ?? o.geometry.attributes.position.count;
    }
  });
  if (nf > 1500000) throw Error("CPU 交互预览面数超限，使用静态审查图");
  const colors = new Float32Array(nv * 3).fill(1),
    vertices = new Float32Array(nv * 3),
    normals = new Float32Array(nv * 3),
    uv = new Float32Array(nv * 2),
    faces = new Uint32Array(nf),
    matids = new Uint16Array(nf / 3),
    materials: CPUMaterial[] = [],
    matmap = new Map<string, number>();
  let vo = 0,
    fo = 0;
  function material(m: MeshStandardMaterial): number {
    const old = matmap.get(m.uuid);
    if (old !== undefined) return old;
    const size = 128,
      canvas = document.createElement("canvas");
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) throw Error("Canvas 2D 不可用");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, size, size);
    if (m.map?.image) {
      try {
        ctx.drawImage(m.map.image as CanvasImageSource, 0, 0, size, size);
      } catch {
        /* Unsupported decoded image retains the base color. */
      }
    }
    const index = materials.length;
    materials.push({
      style: m.userData.wxStyle || "lowpoly",
      texture: ctx.getImageData(0, 0, size, size).data,
      size,
      color: [m.color?.r ?? 0.7, m.color?.g ?? 0.7, m.color?.b ?? 0.7],
      emissive: [m.emissive?.r || 0, m.emissive?.g || 0, m.emissive?.b || 0],
      cutoff: m.alphaTest || 0.001,
      repeatS: m.map?.wrapS === T.RepeatWrapping,
      repeatT: m.map?.wrapT === T.RepeatWrapping,
    });
    matmap.set(m.uuid, index);
    return index;
  }
  for (const o of meshes) {
    const g = o.geometry,
      p = g.attributes.position,
      nn = g.attributes.normal,
      uu = g.attributes.uv,
      normal = new T.Matrix3().getNormalMatrix(o.matrixWorld),
      skin = o as SkinnedMesh;
    if (skin.isSkinnedMesh) skin.skeleton.update();
    const point = new T.Vector3(),
      norm = new T.Vector3(),
      sk = new T.Matrix4(),
      temp = new T.Matrix4();
    for (let i = 0; i < p.count; i++) {
      point.fromBufferAttribute(p, i);
      norm.set(nn ? nn.getX(i) : 0, nn ? nn.getY(i) : 1, nn ? nn.getZ(i) : 0);
      if (skin.isSkinnedMesh) {
        skin.applyBoneTransform(i, point);
        sk.elements.fill(0);
        for (let k = 0; k < 4; k++) {
          const weight = g.attributes.skinWeight.array[i * 4 + k],
            bone = g.attributes.skinIndex.array[i * 4 + k];
          if (weight) {
            temp.fromArray(skin.skeleton.boneMatrices!, bone * 16);
            for (let j = 0; j < 16; j++)
              sk.elements[j] += temp.elements[j] * weight;
          }
        }
        sk.premultiply(skin.bindMatrixInverse).multiply(skin.bindMatrix);
        norm.transformDirection(sk);
      }
      point.applyMatrix4(o.matrixWorld);
      norm.applyMatrix3(normal);
      const q = (vo + i) * 3;
      vertices.set(point.toArray(), q);
      normals.set(norm.toArray(), q);
      if (g.attributes.color)
        colors.set(
          [
            g.attributes.color.getX(i),
            g.attributes.color.getY(i),
            g.attributes.color.getZ(i),
          ],
          q,
        );
      uv[(vo + i) * 2] = uu?.getX(i) || 0;
      uv[(vo + i) * 2 + 1] = uu?.getY(i) || 0;
    }
    const count = g.index?.count ?? p.count;
    for (let i = 0; i < count; i++)
      faces[fo + i] = vo + (g.index ? g.index.getX(i) : i);
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    matids.fill(
      material(mats[0] as MeshStandardMaterial),
      fo / 3,
      (fo + count) / 3,
    );
    // GLTF generally splits materials, but imported BufferGeometry groups remain valid.
    for (const group of g.groups)
      matids.fill(
        material(
          (mats[group.materialIndex ?? 0] || mats[0]) as MeshStandardMaterial,
        ),
        (fo + group.start) / 3,
        (fo + Math.min(count, group.start + group.count)) / 3,
      );
    vo += p.count;
    fo += count;
  }
  const box = new T.Box3().setFromObject(root),
    center = box.getCenter(new T.Vector3()),
    size = box.getSize(new T.Vector3());
  return {
    vertices,
    normals,
    uv,
    colors,
    faces,
    matids,
    materials,
    center: center.toArray(),
    span: Math.max(0.01, size.length() * 1.08),
  };
}
