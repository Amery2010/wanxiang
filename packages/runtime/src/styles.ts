import * as T from "./three.js";
/* Portable style contract for Wanxiang3D 2.1. Three supported looks: lowpoly, toon, voxel. */

const profiles = Object.freeze({
  lowpoly: Object.freeze({
    id: "lowpoly",
    label: "Lowpoly · 清晰切面",
    subdivide: 0,
    roundness: 0,
    flat: true,
    roughness: 0.94,
    metalness: 0,
    color: "original",
    lighting: "continuous",
  }),
  toon: Object.freeze({
    id: "toon",
    label: "卡通 · 柔和色阶",
    subdivide: 1,
    roundness: 0.54,
    flat: false,
    roughness: 0.88,
    metalness: 0,
    color: "vivid",
    lighting: "three-bands",
  }),
  voxel: Object.freeze({
    id: "voxel",
    label: "像素 · 方块世界",
    subdivide: 0,
    roundness: 0,
    flat: true,
    roughness: 1,
    metalness: 0,
    color: "voxel",
    lighting: "continuous",
    texture: "pixel",
  }),
});
const aliases = Object.freeze({ rounded: "toon", pixel: "voxel" });
function resolve(id: string = "lowpoly") {
  id = aliases[id as keyof typeof aliases] || id;
  if (!Object.hasOwn(profiles, id))
    throw Error("STYLE_INVALID: " + id + " (lowpoly / toon / voxel)");
  return profiles[id as keyof typeof profiles];
}
function color(hex: T.ColorRepresentation, style: string) {
  const c = new T.Color(hex),
    p = resolve(style);
  if (p.color === "original") return c;
  const h = { h: 0, s: 0, l: 0 };
  c.getHSL(h, T.SRGBColorSpace);
  if (p.color === "vivid")
    c.setHSL(
      h.h,
      Math.min(0.83, h.s * 1.06),
      Math.min(0.92, h.l * 1.035),
      T.SRGBColorSpace,
    );
  else
    c.setHSL(
      h.h,
      Math.min(0.85, h.s * 1.12),
      Math.min(0.91, h.l * 1.05),
      T.SRGBColorSpace,
    );
  return c;
}
function shader(material: T.MeshStandardMaterial, style: string) {
  const p = resolve(style);
  material.userData.wxStyle = p.id;
  if (!material.userData.wxBaseMaterial)
    material.userData.wxBaseMaterial = {
      roughness: material.roughness,
      metalness: material.metalness,
    };
  const base = material.userData.wxBaseMaterial;
  material.roughness = p.id === "voxel" ? 1 : base.roughness;
  material.metalness = p.id === "voxel" ? 0 : base.metalness;
  delete material.userData.wxToon;
  material.onBeforeCompile = () => {};
  material.customProgramCacheKey = () => "wx-portable-2.1";
  if (p.lighting === "three-bands") {
    // Quantize illumination BEFORE pigment/albedo. Quantizing the final RGB
    // would give a dark red and pale cream surface different shadow edges.
    // Preserve physically-based metallic highlights and glTF PBR fallback.
    material.userData.wxToon = {
      version: "2.1",
      domain: "NdotL-before-albedo",
      thresholds: [0.25, 0.65],
      bands: [0.13, 0.5, 0.97],
      specular: "continuous-PBR",
      exportFallback:
        "core glTF metallic-roughness; runtime shader not embedded",
    };
    material.onBeforeCompile = (sh) => {
      const source = T.ShaderChunk.lights_physical_pars_fragment;
      const begin = source.indexOf("void RE_Direct_Physical(");
      const end = source.indexOf("void RE_IndirectDiffuse_Physical(", begin);
      const direct = source.slice(begin, end < 0 ? undefined : end);
      const needle = "reflectedLight.directDiffuse += irradiance *";
      if (begin < 0 || !direct.includes(needle))
        throw Error(
          "TOON_SHADER_CONTRACT: unsupported Three.js lighting chunk",
        );
      const patched = direct.replace(
        needle,
        `float wxBand = dotNL < 0.25 ? 0.13 : (dotNL < 0.65 ? 0.50 : 0.97);
          vec3 wxDiffuseIrradiance = wxBand * directLight.color;
          reflectedLight.directDiffuse += wxDiffuseIrradiance *`,
      );
      const chunk =
        source.slice(0, begin) + patched + (end < 0 ? "" : source.slice(end));
      sh.fragmentShader = sh.fragmentShader.replace(
        "#include <lights_physical_pars_fragment>",
        chunk,
      );
    };
    material.customProgramCacheKey = () => "wx-toon-2.1";
  }
  if (p.id === "voxel" && material.map) {
    material.map.magFilter = T.NearestFilter;
    material.map.minFilter = T.NearestFilter;
    material.map.generateMipmaps = false;
    material.map.needsUpdate = true;
  }
  material.needsUpdate = true;
  return material;
}
const styles = { profiles, aliases, resolve, color, shader, version: "2.1.0" };

export default styles;
