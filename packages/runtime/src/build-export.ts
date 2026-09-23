import * as Guards from "./three-guards.js";
import * as T from "./three.js";
import type { BuildOptions } from "./runtime.js";
import type { RuntimeSpec, BomEntry, BuildReport } from "./types.js";

/** Resources belong to one build, including textures allocated before export. */
export function disposeBuild(root: T.Object3D): void {
  const geometries = new Set<T.BufferGeometry>(),
    materials = new Set<T.Material>(),
    textures = new Set<T.Texture>(),
    skeletons = new Set<T.Skeleton>();
  root.traverse((object) => {
    if (Guards.isMesh(object)) {
      geometries.add(object.geometry);
      for (const material of Array.isArray(object.material)
        ? object.material
        : [object.material])
        materials.add(material);
    }
    if (Guards.isSkinnedMesh(object)) skeletons.add(object.skeleton);
  });
  for (const material of materials)
    for (const value of Object.values(material))
      if (Guards.isTexture(value)) textures.add(value);
  for (const texture of textures) texture.dispose();
  for (const geometry of geometries) geometry.dispose();
  for (const skeleton of skeletons) skeleton.dispose();
  for (const material of materials) material.dispose();
}
export interface ExportableBuild {
  root: T.Object3D;
  bom: BomEntry[];
  report: BuildReport;
  spec?: RuntimeSpec;
}
export interface BuildExportLibrary {
  build(spec: RuntimeSpec, options?: BuildOptions): Promise<ExportableBuild>;
  clips(root: T.Object3D, id?: string): T.AnimationClip[];
}
export interface BuildExportOptions {
  noTextures?: boolean;
  phase?: (phase: "geometry" | "export") => void;
  check?: () => void;
  exporter?: Pick<T.GLTFExporter, "parseAsync">;
  dispose?: (root: T.Object3D) => void;
}
/** Main-thread and dedicated-worker adapters share ownership and export rules. */
export async function buildAndExport(
  library: BuildExportLibrary,
  spec: RuntimeSpec,
  options: BuildExportOptions = {},
) {
  let built: ExportableBuild | undefined;
  try {
    options.check?.();
    options.phase?.("geometry");
    built = await library.build(spec, {
      noTextures: options.noTextures ?? false,
    });
    options.check?.();
    options.phase?.("export");
    const glb = await (options.exporter ?? new T.GLTFExporter()).parseAsync(
      built.root,
      {
        binary: true,
        onlyVisible: false,
        animations: library.clips(built.root, spec.id),
        maxTextureSize: 4096,
      },
    );
    options.check?.();
    if (!(glb instanceof ArrayBuffer))
      throw Error("GLB exporter did not return binary data");
    return {
      glb,
      buffer: glb,
      bom: built.bom,
      report: built.report,
      spec: built.spec,
    };
  } finally {
    if (built) (options.dispose ?? disposeBuild)(built.root);
  }
}
export default { buildAndExport, disposeBuild };
