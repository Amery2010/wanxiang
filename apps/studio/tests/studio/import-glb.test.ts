import { describe, expect, it } from "vitest";
import { importGLBAsset } from "../../src/studio/import-glb";
function glb(doc: Record<string, unknown>) {
  const json = new TextEncoder().encode(JSON.stringify(doc)),
    length = Math.ceil(json.length / 4) * 4,
    buffer = new ArrayBuffer(20 + length),
    view = new DataView(buffer);
  view.setUint32(0, 0x46546c67, true);
  view.setUint32(4, 2, true);
  view.setUint32(8, buffer.byteLength, true);
  view.setUint32(12, length, true);
  view.setUint32(16, 0x4e4f534a, true);
  new Uint8Array(buffer, 20).fill(32);
  new Uint8Array(buffer, 20, json.length).set(json);
  return buffer;
}
const document = {
  asset: { version: "2.0" },
  accessors: [{ count: 3 }],
  meshes: [{ primitives: [{ attributes: { POSITION: 0 } }] }],
  nodes: [{ mesh: 0 }],
};
describe("external GLB import safety", () => {
  it("retains actual binary bytes and instantiated triangle counts", () => {
    const asset = importGLBAsset(
      glb({ ...document, nodes: [{ mesh: 0 }, { mesh: 0 }] }),
      "model.glb",
    );
    expect(asset.report?.triangles).toBe(2);
    expect(asset.kit).toBeUndefined();
    expect(asset.name).toBe("model");
    expect(asset.glb).toBeTruthy();
  });
  it("rejects external references before runtime loading", () => {
    expect(() =>
      importGLBAsset(
        glb({
          ...document,
          images: [{ uri: "https://example.invalid/private" }],
        }),
        "bad.glb",
      ),
    ).toThrow("外部");
  });
  it("rejects mandatory unsupported extensions", () => {
    expect(() =>
      importGLBAsset(
        glb({
          ...document,
          extensionsRequired: ["KHR_draco_mesh_compression"],
        }),
        "bad.glb",
      ),
    ).toThrow("压缩扩展");
  });
  it("counts every mesh instance against the triangle limit", () => {
    expect(() =>
      importGLBAsset(
        glb({
          ...document,
          accessors: [{ count: 900000 }],
          nodes: [{ mesh: 0 }, { mesh: 0 }],
        }),
        "bad.glb",
      ),
    ).toThrow("50 万");
  });
  it("rejects malformed JSON chunk lengths", () => {
    const buffer = glb(document);
    new DataView(buffer).setUint32(12, buffer.byteLength + 1, true);
    expect(() => importGLBAsset(buffer, "bad.glb")).toThrow("越界");
  });
});
