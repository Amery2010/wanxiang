import { createRequire } from "node:module";
import { beforeAll, afterEach, describe, it, expect, vi } from "vitest";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import { createStudioRuntime } from "../../src/runtime";
import { createInteractions } from "../../src/runtime/interactions";
import type {
  EditorBridge,
  ThreeGlobal,
  ViewState,
} from "../../src/runtime/types";
const require = createRequire(import.meta.url);
let T: ThreeGlobal;
beforeAll(() => {
  const context: { THREE?: ThreeGlobal } = {};
  runInNewContext(
    readFileSync(
      require.resolve("@wanxiang/runtime/vendor/three-0.186.0-with-addons.global.js"),
      "utf8",
    ),
    context,
  );
  T = context.THREE!;
});
afterEach(() => {
  document.body.innerHTML = "";
  vi.restoreAllMocks();
});
function setup() {
  const stage = document.createElement("div"),
    cpuCanvas = document.createElement("canvas"),
    worldGrid = document.createElementNS("http://www.w3.org/2000/svg", "svg"),
    editorOverlay = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "svg",
    );
  stage.tabIndex = 0;
  stage.append(cpuCanvas, worldGrid, editorOverlay);
  document.body.append(stage);
  vi.spyOn(stage, "getBoundingClientRect").mockReturnValue({
    left: 0,
    top: 0,
    right: 800,
    bottom: 600,
    width: 800,
    height: 600,
    x: 0,
    y: 0,
    toJSON: () => ({}),
  });
  const model = new T.Group(),
    node = new T.Mesh(new T.BoxGeometry(1, 1, 1), new T.MeshStandardMaterial());
  node.name = "box";
  model.add(node);
  let view: ViewState = { center: [0, 0, 0], span: 4, az: 36, el: 24, zoom: 1 };
  const setView = vi.fn((patch: Partial<ViewState>) => {
      view = { ...view, ...patch };
    }),
    command = vi.fn(async (_command: Record<string, unknown>) => true),
    select = vi.fn();
  const editor: EditorBridge = {
    getState: () => ({
      doc: { instances: [{ id: "box" }] },
      ids: ["box"],
      tool: "translate",
      snap: true,
      snapMove: 0.25,
      snapRotate: 15,
      snapScale: 0.1,
    }),
    select,
    command,
  };
  const interactions = createInteractions(T, {
    elements: () => ({ stage, cpuCanvas, worldGrid, editorOverlay }),
    model: () => model,
    node: () => node,
    getView: () => view,
    setView,
    grid: () => true,
    fit: vi.fn(),
    refresh: vi.fn(),
    error: vi.fn(),
    stopMotion: vi.fn(),
    locked: () => false,
  });
  interactions.bindEditor(editor);
  return { stage, node, model, setView, command, select, interactions };
}
describe("imperative viewport lifecycle and transforms", () => {
  it("removes all wheel handlers between mounts", () => {
    const f = setup(),
      off = f.interactions.mount({
        stage: f.stage,
        cpuCanvas: f.stage.querySelector("canvas")!,
      });
    f.stage.dispatchEvent(
      new WheelEvent("wheel", { deltaY: 100, cancelable: true }),
    );
    expect(f.setView).toHaveBeenCalledTimes(1);
    off();
    f.stage.dispatchEvent(
      new WheelEvent("wheel", { deltaY: 100, cancelable: true }),
    );
    expect(f.setView).toHaveBeenCalledTimes(1);
    f.interactions.mount({
      stage: f.stage,
      cpuCanvas: f.stage.querySelector("canvas")!,
    });
    f.stage.dispatchEvent(
      new WheelEvent("wheel", { deltaY: 100, cancelable: true }),
    );
    expect(f.setView).toHaveBeenCalledTimes(2);
    f.interactions.dispose();
  });
  it("ground transforms use world-space geometry and convert to local coordinates", async () => {
    const f = setup();
    f.model.position.y = 10;
    f.node.position.y = 2;
    await f.interactions.ground();
    expect(f.command).toHaveBeenCalledTimes(1);
    const command = f.command.mock.calls[0]![0] as unknown as {
      values: { box: { position: number[] } };
    };
    expect(command.values.box.position[1]).toBe(-9.5);
    f.interactions.dispose();
  });
  it("focus selection adjusts the view span and center without replacing the model", () => {
    const f = setup();
    f.node.position.x = 5;
    f.interactions.focusSelection();
    expect(f.setView).toHaveBeenCalledWith(
      expect.objectContaining({ center: [5, 0, 0] }),
    );
    f.interactions.dispose();
  });
});

describe("runtime mount lifecycle", () => {
  it("survives StrictMode style detach/remount without duplicate events or RAF", () => {
    const stage = document.createElement("div"),
      cpuCanvas = document.createElement("canvas");
    stage.append(cpuCanvas);
    document.body.append(stage);
    vi.spyOn(stage, "getBoundingClientRect").mockReturnValue({
      left: 0,
      top: 0,
      right: 800,
      bottom: 600,
      width: 800,
      height: 600,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    });
    const raf = vi
        .spyOn(globalThis, "requestAnimationFrame")
        .mockReturnValue(42),
      cancel = vi
        .spyOn(globalThis, "cancelAnimationFrame")
        .mockImplementation(() => {});
    const onViewChange = vi.fn();
    const noGPU = class {
      constructor() {
        throw Error("GPU unavailable");
      }
    } as unknown as ThreeGlobal["WebGLRenderer"];
    const runtime = createStudioRuntime(
      { assets: [] },
      { onViewChange },
      {
        THREE: { ...T, WebGLRenderer: noGPU },
        WXPipeline: {
          prepare: () => ({
            inspection: { doc: {} },
            load: async () => {
              throw Error("unused");
            },
          }),
          inspect: () => ({ doc: {} }),
          load: async () => {
            throw Error("unused");
          },
          dispose: vi.fn(),
        },
      },
    );
    const first = runtime.mount({ stage, cpuCanvas });
    first();
    const second = runtime.mount({ stage, cpuCanvas });
    onViewChange.mockClear();
    stage.dispatchEvent(
      new WheelEvent("wheel", { deltaY: 10, cancelable: true }),
    );
    expect(onViewChange).toHaveBeenCalledTimes(1);
    first();
    stage.dispatchEvent(
      new WheelEvent("wheel", { deltaY: 10, cancelable: true }),
    );
    expect(onViewChange).toHaveBeenCalledTimes(2);
    second();
    stage.dispatchEvent(
      new WheelEvent("wheel", { deltaY: 10, cancelable: true }),
    );
    expect(onViewChange).toHaveBeenCalledTimes(2);
    expect(raf).toHaveBeenCalled();
    expect(cancel).toHaveBeenCalled();
    runtime.dispose();
  });
});
