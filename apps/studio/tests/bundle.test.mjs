import { createRequire } from "node:module";
import { readFile } from "node:fs/promises";
import { expect, it } from "vitest";
import { JSDOM, VirtualConsole } from "jsdom";
const require = createRequire(import.meta.url);
function triangle() {
  const doc = {
    asset: { version: "2.0" },
    scene: 0,
    scenes: [{ nodes: [0] }],
    nodes: [{ name: "triangle", mesh: 0 }],
    meshes: [{ primitives: [{ attributes: { POSITION: 0 } }] }],
    buffers: [{ byteLength: 36 }],
    bufferViews: [{ buffer: 0, byteOffset: 0, byteLength: 36 }],
    accessors: [
      {
        bufferView: 0,
        componentType: 5126,
        count: 3,
        type: "VEC3",
        min: [0, 0, 0],
        max: [1, 1, 0],
      },
    ],
  };
  const json = Buffer.from(JSON.stringify(doc)),
    length = Math.ceil(json.length / 4) * 4;
  const glb = Buffer.alloc(12 + 8 + length + 8 + 36, 32);
  glb.writeUInt32LE(0x46546c67, 0);
  glb.writeUInt32LE(2, 4);
  glb.writeUInt32LE(glb.length, 8);
  glb.writeUInt32LE(length, 12);
  glb.writeUInt32LE(0x4e4f534a, 16);
  json.copy(glb, 20);
  glb.writeUInt32LE(36, 20 + length);
  glb.writeUInt32LE(0x004e4942, 24 + length);
  [0, 0, 0, 1, 0, 0, 0, 1, 0].forEach((v, i) =>
    glb.writeFloatLE(v, 28 + length + i * 4),
  );
  return glb.toString("base64");
}
it("boots the compiled IIFE in static-review mode and loads a real embedded GLB", async () => {
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on("jsdomError", (error) => errors.push(error.message));
  const dom = new JSDOM(
    '<html><head></head><body><div id="root"></div></body></html>',
    {
      url: "http://localhost/",
      runScripts: "outside-only",
      pretendToBeVisual: true,
      virtualConsole,
    },
  );
  try {
    dom.window.ResizeObserver = class {
      observe() {}
      disconnect() {}
    };
    dom.window.matchMedia = () => ({
      matches: false,
      addEventListener() {},
      removeEventListener() {},
    });
    dom.window.HTMLCanvasElement.prototype.getContext = (type) =>
      type === "2d"
        ? {
            fillRect() {},
            drawImage() {},
            getImageData: () => ({ data: new Uint8ClampedArray(4) }),
            putImageData() {},
          }
        : null;
    dom.window.ImageData = class {
      constructor(data, width, height) {
        Object.assign(this, { data, width, height });
      }
    };
    dom.window.TextDecoder = TextDecoder;
    dom.window.TextEncoder = TextEncoder;
    dom.window.WX_DATA = {
      assets: [{ id: "triangle", name: "三角网格", glb: triangle() }],
    };
    dom.window.eval(
      await readFile(
        require.resolve("@wanxiang/runtime/vendor/three-0.186.0-with-addons.global.js"),
        "utf8",
      ),
    );
    dom.window.eval(
      await readFile(new URL("../artifacts/app.js", import.meta.url), "utf8"),
    );
    await expect
      .poll(() => dom.window.WX_LIVE_QA?.snapshot()?.id, { timeout: 4000 })
      .toBe("triangle")
      .catch((error) => {
        throw new Error(
          dom.window.document.body.textContent + "\n" + errors.join("\n"),
          { cause: error },
        );
      });
    expect(dom.window.document.body.textContent).toContain("万象工坊");
    expect(dom.window.document.body.textContent).not.toContain(
      "工作台未能启动",
    );
    expect(
      dom.window.document.getElementById("wanxiang-react-styles").textContent,
    ).toContain("--primary");
    expect(dom.window.WXRuntime).toBeUndefined();
    expect(dom.window.WX_LIVE_QA.snapshot().glb).toBe(triangle());
    expect(errors).toEqual([]);
  } finally {
    dom.window.close();
  }
});
