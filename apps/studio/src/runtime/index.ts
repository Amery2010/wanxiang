import type * as Three from "three";
import type { GLTF } from "three/addons/loaders/GLTFLoader.js";
import type {
  RuntimeData,
  RuntimeAsset,
  RuntimeSpec,
  RuntimeCallbacks,
  RuntimeGlobals,
  StudioRuntime,
  PreparedAsset,
  ViewportElements,
  ViewState,
  BuildResult,
  EditorBridge,
} from "./types";
import { from64, to64, sha256Bytes, zipStore } from "./archive";
import {
  cpuRaster,
  prepareCPUShadows,
  cpuShadowVisibility,
  type CPUData,
  type CPUOptions,
} from "./cpu";
import { packCPU } from "./pack-cpu";
import { createInteractions } from "./interactions";
export * from "./types";
export { from64, to64, sha256Bytes, zipStore, closedManifest } from "./archive";

export function createStudioRuntime(
  data: RuntimeData,
  callbacks: RuntimeCallbacks = {},
  injected?: RuntimeGlobals,
): StudioRuntime {
  const G = injected || (globalThis as unknown as RuntimeGlobals),
    T = G.THREE,
    pipeline = G.WXPipeline;
  if (!T || !pipeline) throw Error("离线渲染内核尚未加载");
  let disposed = false,
    current: RuntimeAsset | null = null,
    loaded: GLTF | null = null,
    model: Three.Object3D | null = null,
    elements: ViewportElements | null = null;
  let scene: Three.Scene | null = null,
    camera: Three.OrthographicCamera | null = null,
    renderer: Three.WebGLRenderer | null = null,
    gpu: Three.WebGLRenderer | null = null;
  let floor: Three.Mesh | null = null,
    keyLight: Three.DirectionalLight | null = null,
    animationFrame = 0,
    cpuTimer: ReturnType<typeof setTimeout> | null = null;
  let mixer: Three.AnimationMixer | null = null,
    playing = false,
    clipIndex = 0,
    lastTime = 0,
    serial = 0,
    cpuBusy = false,
    cpuPending = false,
    cpuData: CPUData | null = null,
    cpuWorker: Worker | null = null;
  const frameTimes: number[] = [];
  let lastCPUFrame = 0,
    lastMotionStatus = 0;
  let rigidState: Record<string, number> = {};
  let wire = false,
    grid = true,
    lighting = "studio",
    view: ViewState = {
      center: [0, 0, 0],
      span: 10,
      az: 36,
      el: 24,
      zoom: 1.12,
    },
    mountDispose: (() => void) | null = null;
  const nodes = new Map<string, Three.Object3D>(),
    handles = new Map<
      symbol,
      { asset: RuntimeAsset; loaded: GLTF; cpu: CPUData | null }
    >(),
    controllers = new Set<AbortController>();
  const neutral = new Map<
    Three.MeshStandardMaterial,
    {
      color: Three.Color;
      emissive: Three.Color;
      map: Three.Texture | null;
      vertexColors: boolean;
      metalness: number;
      roughness: number;
    }
  >();
  const qa: RuntimeSpec = {
    version: data.version,
    offline: true,
    assetCount: data.assets.length,
    partCount: Object.keys(data.parts || {}).length,
    loaded: false,
    renderer: "detecting",
    runtimeDrawn: false,
  };
  const status = (patch: RuntimeSpec) => {
    Object.assign(qa, patch);
    G.WX_QA = Object.assign(G.WX_QA || {}, patch);
    if (!disposed) callbacks.onStatus?.({ ...qa });
  };
  const error = (e: unknown) => {
    if (!disposed)
      callbacks.onError?.(e instanceof Error ? e.message : String(e));
  };
  const abort = () => new DOMException("Cancelled", "AbortError");
  const check = (signal?: AbortSignal) => {
    if (disposed || signal?.aborted) throw abort();
  };
  let live = data.parts && G.WXRuntime ? new G.WXRuntime.Library(data) : null;
  const cache =
    live && G.WXBuildCache ? new G.WXBuildCache.Cache(data, sha256Bytes) : null;
  const tasks =
    live && G.WXBuildTasks
      ? new G.WXBuildTasks.Tasks(
          data,
          async (spec, signal) => {
            check(signal);
            const library = live;
            if (!library) throw Error("实时构建内核不可用");
            if (!G.WXBuildExport) throw Error("实时导出内核不可用");
            return G.WXBuildExport.buildAndExport(library, spec, {
              check: () => check(signal),
              exporter: new T.GLTFExporter(),
              dispose: pipeline.dispose,
            });
          },
          (snapshot) => status({ tasks: snapshot }),
        )
      : null;
  status({
    ...qa,
    compiledOnDemand: !!live,
    loader: "Three.GLTFLoader r186",
    exporter: "Three.GLTFExporter r186",
  });
  function meshMaterials(
    root: Three.Object3D,
    fn: (m: Three.MeshStandardMaterial) => void,
  ) {
    root.traverse((o) => {
      const mesh = o as Three.Mesh;
      if (mesh.material)
        for (const m of Array.isArray(mesh.material)
          ? mesh.material
          : [mesh.material])
          fn(m as Three.MeshStandardMaterial);
    });
  }
  function restoreMaterials() {
    for (const [m, old] of neutral) {
      m.color?.copy(old.color);
      m.emissive?.copy(old.emissive);
      m.map = old.map;
      m.vertexColors = old.vertexColors;
      m.metalness = old.metalness;
      m.roughness = old.roughness;
      m.needsUpdate = true;
    }
    neutral.clear();
  }
  async function prepare(
    asset: RuntimeAsset,
    spec = asset.kit,
    signal?: AbortSignal,
  ): Promise<PreparedAsset> {
    check(signal);
    const controller = new AbortController();
    controllers.add(controller);
    const relay = () => controller.abort();
    signal?.addEventListener("abort", relay, { once: true });
    if (signal?.aborted) controller.abort();
    let next: GLTF | null = null;
    try {
      check(controller.signal);
      const candidate = { ...asset };
      let prepared: ReturnType<typeof pipeline.prepare> | undefined;
      if (asset.dynamic) {
        if (!cache || !tasks || !spec) throw Error("此页面没有实时构建内核");
        const immutable = structuredClone(spec),
          key = cache.key(immutable),
          started = performance.now();
        let hit = await cache.get(key),
          result: BuildResult | undefined;
        check(controller.signal);
        if (hit) {
          try {
            prepared = pipeline.prepare(hit.buffer);
            result = { buffer: hit.buffer, ...hit.payload };
          } catch {
            await cache.remove(key);
            hit = null;
          }
        }
        if (!result) {
          result = await tasks.submit(immutable, {
            asset: asset.id,
            level: asset.level || 1,
            signal: controller.signal,
          });
          check(controller.signal);
          prepared = pipeline.prepare(result.buffer);
          await cache.put(key, immutable, result.buffer, {
            bom: result.bom,
            report: result.report,
          });
        }
        check(controller.signal);
        const inspected = prepared!.inspection,
          doc = inspected.doc,
          bytes = new Uint8Array(result.buffer);
        Object.assign(candidate, {
          kit: immutable,
          spec: { ...asset.spec, style: immutable.style },
          glb: to64(result.buffer),
          sha256: sha256Bytes(bytes),
          bytes: bytes.length,
          bom: result.bom,
          provenance: Object.fromEntries(
            result.bom.map((row) => [
              row.part,
              data.parts?.[row.part]?.source || {},
            ]),
          ),
          report: {
            ...result.report,
            nodes: doc.nodes?.length || 0,
            materials: doc.materials?.length || 0,
            textures: doc.images?.length || 0,
            evidence: {
              runtime_generation: true,
              exporter: true,
              glb_boundary_validated: true,
            },
          },
          _builtSignature: JSON.stringify(immutable),
          _buildMs: performance.now() - started,
          _buildKey: key,
          cacheSource: hit?.cacheSource || "generated",
          buildState: "ready",
        });
      }
      if (!candidate.glb) throw Error("资产未包含 GLB");
      prepared ??= pipeline.prepare(from64(candidate.glb).buffer);
      next = await prepared.load();
      check(controller.signal);
      next.scene.updateMatrixWorld(true);
      next.scene.traverse((object) => {
        const mesh = object as Three.Mesh;
        if (mesh.isMesh) {
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          meshMaterials(mesh, (m) => {
            const style = m.userData.wxStyle || candidate.kit?.style;
            if (
              style &&
              G.WXStyles &&
              (G.WXStyles.profiles[style] || G.WXStyles.aliases[style])
            )
              G.WXStyles.shader(m, style);
          });
        }
      });
      const cpu = renderer ? null : packCPU(next.scene, T);
      check(controller.signal);
      const token = Symbol(candidate.id);
      handles.set(token, { asset: candidate, loaded: next, cpu });
      next = null;
      return { asset: candidate, token };
    } finally {
      if (next) pipeline.dispose(next.scene);
      signal?.removeEventListener("abort", relay);
      controllers.delete(controller);
    }
  }
  function discard(prepared: PreparedAsset) {
    const value = handles.get(prepared.token);
    if (value) {
      handles.delete(prepared.token);
      pipeline.dispose(value.loaded.scene);
    }
  }
  function commit(prepared: PreparedAsset) {
    check();
    const next = handles.get(prepared.token);
    if (!next) throw Error("Prepared model is no longer available");
    // Packing can fail after a context loss; complete it before changing the old model.
    const nextCPU = renderer ? null : next.cpu || packCPU(next.loaded.scene, T),
      preserve = current?.id === next.asset.id && next.asset.level === 4;
    interactions.cancel();
    handles.delete(prepared.token);
    restoreMaterials();
    playing = false;
    if (mixer && model) {
      mixer.stopAllAction();
      mixer.uncacheRoot(model);
    }
    if (model) {
      scene?.remove(model);
      pipeline.dispose(model);
    }
    current = next.asset;
    rigidState = {};
    frameTimes.length = 0;
    loaded = next.loaded;
    model = loaded.scene;
    cpuData = nextCPU;
    serial++;
    nodes.clear();
    model.userData.wx_provenance = current.provenance || {};
    model.traverse((o) => {
      const association = loaded!.parser.associations.get(o),
        name =
          association && "nodes" in association
            ? loaded!.parser.json.nodes[association.nodes as number]?.name
            : o.name;
      if (name) {
        nodes.set(name, o);
        o.userData.wxSourceName = name;
      }
      o.userData.wxInitialPosition = o.position.clone();
    });
    mixer = loaded.animations.length ? new T.AnimationMixer(model) : null;
    clipIndex = 0;
    if (mixer) mixer.clipAction(loaded.animations[0]).play();
    scene?.add(model);
    cpuPending = false;
    if (cpuWorker && cpuData)
      cpuWorker.postMessage({ type: "init", data: cpuData });
    if (elements) {
      elements.cpuCanvas.hidden = !!renderer;
      if (elements.fallback) {
        elements.fallback.src = current.hero || "";
        elements.fallback.hidden = true;
      }
    }
    status({
      loaded: true,
      actualGLBLoaded: true,
      assetId: current.id,
      sourceNodeCount: nodes.size,
      buildMs: current._buildMs || 0,
      cacheSource: current.cacheSource,
      geometrySignature: current.sha256,
      activeStyle: current.kit?.style,
      liveTriangleCount: current.report?.triangles,
      textureCount: current.report?.textures,
      animationCount: loaded.animations.length,
      motionTime: 0,
      motionPlaying: false,
      motionClip: 0,
      rigidState: {},
      cpuDrawn: false,
      runtimeDrawn: false,
      explodeAmount: 0,
      isolated: null,
      buildError: null,
      loadError: null,
    });
    if (!preserve) fit();
    else resize();
    setWire(wire);
    setLighting(lighting);
    interactions.draw();
  }
  function snapshot() {
    return current ? { ...current } : null;
  }
  function requestCPU() {
    interactions.draw();
    if (renderer || !cpuData || !elements || disposed) return;
    const rect = elements.stage.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return;
    if (cpuBusy) {
      cpuPending = true;
      return;
    }
    const height = Math.min(600, Math.max(320, Math.round(rect.height * 1.6))),
      width = Math.max(1, Math.round((rect.width / rect.height) * height));
    const opt: CPUOptions & { type: string; id: number } = {
      type: "render",
      width,
      height,
      ...view,
      wire,
      lighting,
      id: serial,
    };
    cpuBusy = true;
    if (cpuWorker) cpuWorker.postMessage(opt);
    else {
      const generation = serial,
        packed = cpuData;
      cpuTimer = setTimeout(() => {
        cpuTimer = null;
        try {
          if (disposed || generation !== serial || !elements) return;
          const start = performance.now(),
            pixels = cpuRaster(
              packed.shadow ? packed : prepareCPUShadows(packed),
              opt,
            );
          paintCPU(
            pixels,
            width,
            height,
            generation,
            performance.now() - start,
          );
        } catch (e) {
          error(e);
        } finally {
          cpuBusy = false;
          if (cpuPending) {
            cpuPending = false;
            requestCPU();
          }
        }
      }, 0);
    }
  }
  function paintCPU(
    pixels: Uint8ClampedArray<ArrayBuffer>,
    width: number,
    height: number,
    generation: number,
    ms: number,
  ) {
    if (disposed || generation !== serial || renderer || !elements) return;
    const canvas = elements.cpuCanvas;
    canvas.width = width;
    canvas.height = height;
    canvas
      .getContext("2d")
      ?.putImageData(new ImageData(pixels, width, height), 0, 0);
    canvas.hidden = false;
    if (elements.fallback) elements.fallback.hidden = true;
    frameTimes.push(ms);
    if (frameTimes.length > 90) frameTimes.shift();
    status({
      cpuDrawn: true,
      frameSerial: serial,
      cpuFrameMs: ms,
      cpuSampleCount: frameTimes.length,
      cpuFrameMedian: [...frameTimes].sort((a, b) => a - b)[
        Math.floor(frameTimes.length / 2)
      ],
    });
  }
  function initWorker() {
    try {
      // Function names are supplied explicitly so minification cannot break worker scope.
      const code = `const prepareCPUShadows=${prepareCPUShadows.toString()};const cpuShadowVisibility=${cpuShadowVisibility.toString()};const cpuRaster=${cpuRaster.toString()};let data=null;self.onmessage=e=>{if(e.data.type==='init'){data=prepareCPUShadows(e.data.data);return}if(data){const t=performance.now(),image=cpuRaster(data,e.data,cpuShadowVisibility);self.postMessage({image,width:e.data.width,height:e.data.height,id:e.data.id,ms:performance.now()-t},[image.buffer])}}`;
      const url = URL.createObjectURL(
        new Blob([code], { type: "text/javascript" }),
      );
      try {
        cpuWorker = new Worker(url);
      } finally {
        URL.revokeObjectURL(url);
      }
      cpuWorker.onmessage = (e) => {
        cpuBusy = false;
        paintCPU(
          e.data.image,
          e.data.width,
          e.data.height,
          e.data.id,
          e.data.ms,
        );
        if (cpuPending) {
          cpuPending = false;
          requestCPU();
        }
      };
      cpuWorker.onerror = () => {
        cpuWorker?.terminate();
        cpuWorker = null;
        cpuBusy = false;
        requestCPU();
      };
    } catch {
      cpuWorker = null;
    }
  }
  function refresh() {
    if (!model) return;
    model.updateMatrixWorld(true);
    if (!renderer) {
      restoreMaterials();
      cpuData = packCPU(model, T);
      cpuWorker?.postMessage({ type: "init", data: cpuData });
      requestCPU();
    }
    interactions.draw();
  }
  function setView(value: Partial<ViewState>) {
    view = { ...view, ...value, center: [...(value.center || view.center)] };
    view.span = Math.max(0.01, view.span);
    view.zoom = Math.max(0.03, Math.min(50, view.zoom));
    updateCamera();
    resize();
    requestCPU();
    interactions.draw();
    callbacks.onViewChange?.({ ...view, center: [...view.center] });
  }
  function updateCamera() {
    if (!camera) return;
    const c = new T.Vector3().fromArray(view.center),
      a = (view.az * Math.PI) / 180,
      e = (view.el * Math.PI) / 180;
    camera.zoom = view.zoom;
    camera.position
      .copy(c)
      .addScaledVector(
        new T.Vector3(
          Math.sin(a) * Math.cos(e),
          Math.sin(e),
          Math.cos(a) * Math.cos(e),
        ),
        Math.max(view.span * 3, 10),
      );
    camera.far = Math.max(10000, view.span * 20);
    camera.lookAt(c);
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld();
  }
  function resize() {
    if (elements && camera) {
      const r = elements.stage.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) {
        camera.left = (-view.span * r.width) / r.height / 2;
        camera.right = -camera.left;
        camera.top = view.span / 2;
        camera.bottom = -view.span / 2;
        camera.updateProjectionMatrix();
        renderer?.setSize(r.width, r.height, false);
      }
    }
    requestCPU();
    interactions.draw();
  }
  function fit() {
    if (!model) return;
    const bounds = new T.Box3().setFromObject(model),
      center = bounds.getCenter(new T.Vector3()),
      span = Math.max(0.01, bounds.getSize(new T.Vector3()).length() * 1.08);
    view = {
      center: center.toArray(),
      span,
      az: 36,
      el:
        current?.level === 4
          ? 32
          : current?.category === "part_body" ||
              current?.kit?.category === "body"
            ? 16
            : 24,
      zoom: 1.12,
    };
    if (keyLight) {
      keyLight.position
        .copy(center)
        .addScaledVector(new T.Vector3(-0.335, 0.839, 0.431), span * 2);
      keyLight.target.position.copy(center);
      const sh = keyLight.shadow.camera;
      sh.left = -span * 0.6;
      sh.right = span * 0.6;
      sh.top = span * 0.6;
      sh.bottom = -span * 0.6;
      sh.near = 0.05;
      sh.far = span * 6;
      sh.updateProjectionMatrix();
      floor?.position.set(center.x, bounds.min.y - span * 0.0015, center.z);
      floor?.scale.setScalar(span * 8);
    }
    updateCamera();
    resize();
    callbacks.onViewChange?.({ ...view });
  }
  function setWire(value: boolean) {
    wire = value;
    if (model)
      meshMaterials(model, (m) => {
        m.wireframe = wire;
      });
    requestCPU();
  }
  function setGrid(value: boolean) {
    grid = value;
    interactions.draw();
  }
  const extraLights: Three.PointLight[] = [];
  function setLighting(value: string) {
    if (!["studio", "neutral", "night"].includes(value))
      throw Error("Unknown presentation preset");
    lighting = value;
    restoreMaterials();
    const night = value === "night",
      gray = value === "neutral";
    if (elements) {
      elements.stage.style.background = night
        ? "radial-gradient(ellipse at 45% 25%,#293046,#141d2d)"
        : "radial-gradient(ellipse at 50% 35%,#f2f1e9,#e0e1d7)";
      elements.stage.classList.toggle("night", night);
    }
    if (scene && renderer) {
      for (const l of extraLights) {
        scene.remove(l);
        l.dispose();
      }
      extraLights.length = 0;
      scene.traverse((o) => {
        const light = o as Three.Light;
        if (light.isLight) {
          light.userData.wxBaseIntensity ??= light.intensity;
          light.intensity = light.userData.wxBaseIntensity * (night ? 0.24 : 1);
        }
      });
      renderer.toneMappingExposure = night ? 1 : 1.1;
      scene.environmentIntensity = night ? 0.18 : 1;
      if (night)
        for (const item of presentationLights(
          current?.kit?.metadata?.lighting,
        )) {
          const light = new T.PointLight(
            item.color || "#59BDD2",
            item.intensity || 9,
            item.distance || 9,
            2,
          );
          light.position.fromArray(item.position);
          scene.add(light);
          extraLights.push(light);
        }
      if (gray && model)
        meshMaterials(model, (m) => {
          if (!m.color || !m.emissive) return;
          neutral.set(m, {
            color: m.color.clone(),
            emissive: m.emissive.clone(),
            map: m.map,
            vertexColors: m.vertexColors,
            metalness: m.metalness,
            roughness: m.roughness,
          });
          m.color.setRGB(0.53, 0.53, 0.53);
          m.emissive.setRGB(0, 0, 0);
          m.vertexColors = false;
          m.map = null;
          m.metalness = 0;
          m.roughness = 0.9;
          m.needsUpdate = true;
        });
    } else requestCPU();
    status({
      lightingMode: value,
      lightingCertification: renderer
        ? "GPU preview path (hardware validation separate)"
        : "CPU approximation; not full PBR",
    });
  }
  function mount(host: ViewportElements) {
    check();
    mountDispose?.();
    elements = host;
    let active = true;
    const cleanupListeners: (() => void)[] = [];
    scene = new T.Scene();
    camera = new T.OrthographicCamera(-5, 5, 5, -5, 0.01, 10000);
    try {
      const canvas = document.createElement("canvas");
      canvas.id = "gpuCanvas";
      canvas.style.cssText =
        "position:absolute;inset:0;width:100%;height:100%;";
      gpu = new T.WebGLRenderer({ canvas, alpha: true, antialias: true });
      renderer = gpu;
      gpu.setPixelRatio(Math.min(globalThis.devicePixelRatio || 1, 2));
      gpu.outputColorSpace = T.SRGBColorSpace;
      gpu.toneMapping = T.ACESFilmicToneMapping;
      gpu.shadowMap.enabled = true;
      gpu.shadowMap.type = T.PCFSoftShadowMap;
      host.stage.prepend(canvas);
      const lost = (e: Event) => {
        e.preventDefault();
        renderer = null;
        canvas.hidden = true;
        status({ contextLost: true, runtimeDrawn: false, renderer: "cpu" });
        try {
          refresh();
        } catch (errorValue) {
          error(errorValue);
          if (host.fallback) host.fallback.hidden = false;
        }
      };
      const restored = () => {
        renderer = gpu;
        canvas.hidden = false;
        host.cpuCanvas.hidden = true;
        status({ contextLost: false, renderer: "webgl2" });
        setLighting(lighting);
        resize();
      };
      canvas.addEventListener("webglcontextlost", lost);
      canvas.addEventListener("webglcontextrestored", restored);
      cleanupListeners.push(() => {
        canvas.removeEventListener("webglcontextlost", lost);
        canvas.removeEventListener("webglcontextrestored", restored);
        canvas.remove();
      });
      scene.add(new T.HemisphereLight(0xdde8ee, 0x565743, 1.5));
      keyLight = new T.DirectionalLight(0xffeddb, 2.7);
      keyLight.castShadow = true;
      keyLight.shadow.mapSize.set(2048, 2048);
      keyLight.shadow.normalBias = 0.025;
      scene.add(keyLight, keyLight.target);
      floor = new T.Mesh(
        new T.PlaneGeometry(1, 1),
        new T.ShadowMaterial({ color: 0x2a3e2b, opacity: 0.2 }),
      );
      floor.rotation.x = -Math.PI / 2;
      floor.receiveShadow = true;
      scene.add(floor);
      const rim = new T.DirectionalLight(0xc0dbe3, 0.7);
      rim.position.set(6, 4, -6);
      scene.add(rim);
      const w = 64,
        h = 32,
        pixels = new Uint8Array(w * h * 4);
      for (let y = 0; y < h; y++)
        for (let x = 0; x < w; x++) {
          const at = (y * w + x) * 4,
            sky = 0.25 + 0.5 * (1 - y / h),
            bright = Math.exp(-((x - 12) ** 2 + (y - 8) ** 2) / 32) * 0.2;
          pixels[at] = Math.min(255, (sky + bright) * 255);
          pixels[at + 1] = Math.min(255, (sky + bright + 0.025) * 255);
          pixels[at + 2] = Math.min(255, (sky + bright + 0.04) * 255);
          pixels[at + 3] = 255;
        }
      const env = new T.DataTexture(pixels, w, h, T.RGBAFormat);
      env.mapping = T.EquirectangularReflectionMapping;
      env.needsUpdate = true;
      scene.environment = env;
      status({ renderer: "webgl2" });
    } catch (e) {
      renderer = null;
      gpu?.domElement.remove();
      gpu?.dispose();
      gpu = null;
      status({
        renderer: "cpu",
        webglReason: e instanceof Error ? e.message : String(e),
      });
    }
    initWorker();
    if (model) {
      scene.add(model);
      if (!renderer) refresh();
      else host.cpuCanvas.hidden = true;
    }
    const stopInteractions = interactions.mount(host);
    const observer =
      typeof ResizeObserver === "undefined" ? null : new ResizeObserver(resize);
    observer?.observe(host.stage);
    const tick = (time: number) => {
      if (!active || disposed) return;
      animationFrame = requestAnimationFrame(tick);
      if (document.hidden) {
        lastTime = time;
        return;
      }
      if (playing && mixer) {
        mixer.update(Math.min(0.1, (time - lastTime) / 1000 || 0.016));
        if (!renderer && time - lastCPUFrame >= 100) {
          lastCPUFrame = time;
          refresh();
        }
        if (time - lastMotionStatus >= 100) {
          lastMotionStatus = time;
          status({ motionTime: mixer.time });
        }
      }
      lastTime = time;
      if (renderer && scene && camera) {
        renderer.render(scene, camera);
        if (model && renderer.info.render.calls > 0 && !qa.runtimeDrawn)
          status({ runtimeDrawn: true });
      }
    };
    animationFrame = requestAnimationFrame(tick);
    fit();
    resize();
    setLighting(lighting);
    const detach = () => {
      if (!active) return;
      active = false;
      cancelAnimationFrame(animationFrame);
      observer?.disconnect();
      stopInteractions();
      for (const clean of cleanupListeners) clean();
      cpuWorker?.terminate();
      cpuWorker = null;
      cpuBusy = false;
      cpuPending = false;
      if (cpuTimer !== null) clearTimeout(cpuTimer);
      cpuTimer = null;
      restoreMaterials();
      if (model) scene?.remove(model);
      scene?.environment?.dispose();
      if (scene) {
        scene.traverse((object) => {
          const light = object as Three.Light;
          if (light.isLight) light.dispose();
        });
        pipeline.dispose(scene);
      }
      gpu?.dispose();
      gpu = null;
      renderer = null;
      scene = null;
      camera = null;
      keyLight = null;
      floor = null;
      extraLights.length = 0;
      if (elements === host) elements = null;
      if (mountDispose === detach) mountDispose = null;
    };
    mountDispose = detach;
    return detach;
  }
  function poseTime(time: number) {
    playing = false;
    mixer?.setTime(time);
    refresh();
    status({ motionTime: time, motionPlaying: false });
  }
  function playMotion(value: boolean, clip = clipIndex) {
    if (!mixer || !loaded) return;
    if (clip !== clipIndex) {
      clipIndex = Math.max(0, Math.min(loaded.animations.length - 1, clip));
      mixer.stopAllAction();
      mixer.setTime(0);
      mixer.clipAction(loaded.animations[clipIndex]).reset().play();
      refresh();
    }
    if (value) mixer.clipAction(loaded.animations[clipIndex]).play();
    playing = value;
    lastTime = performance.now();
    status({ motionPlaying: value, motionClip: clipIndex });
  }
  function resetVisibility() {
    model?.traverse((o) => {
      o.visible = true;
    });
    status({ isolated: null });
    refresh();
  }
  function isolateNode(id: string) {
    const root = nodes.get(id);
    if (!root) throw Error("节点未找到");
    resetVisibility();
    const keep = new Set<Three.Object3D>();
    root.traverse((o) => keep.add(o));
    model?.traverse((o) => {
      if ((o as Three.Mesh).isMesh) o.visible = keep.has(o);
    });
    status({ isolated: id });
    refresh();
  }
  function explode(amount: number) {
    if (!model) return;
    model.traverse((o) => {
      if (o.userData.wxInitialPosition)
        o.position.copy(o.userData.wxInitialPosition);
    });
    model.updateMatrixWorld(true);
    const center = new T.Box3().setFromObject(model).getCenter(new T.Vector3()),
      all: Three.Object3D[] = [];
    model.traverse((o) => {
      if (o.userData.wx_role === "part_instance") all.push(o);
    });
    if (!all.length)
      model.traverse((o) => {
        if ((o as Three.Mesh).isMesh) all.push(o);
      });
    const targets = all.map((o) => ({
      o,
      pos: o
        .getWorldPosition(new T.Vector3())
        .sub(center)
        .multiplyScalar(1 + 0.8 * amount)
        .add(center),
    }));
    for (const { o, pos } of targets) {
      o.parent?.updateWorldMatrix(true, false);
      o.position.copy(o.parent ? o.parent.worldToLocal(pos) : pos);
    }
    status({ explodeAmount: amount });
    refresh();
  }
  async function exportGLB(reexport = false) {
    check();
    if (!current?.glb) throw Error("没有可导出的模型");
    const asset = current;
    let buffer = from64(asset.glb!).buffer;
    pipeline.inspect(buffer);
    if (reexport) {
      const original = await pipeline.load(buffer);
      try {
        const result = await new T.GLTFExporter().parseAsync(original.scene, {
          binary: true,
          onlyVisible: false,
          animations: original.animations,
        });
        if (!(result instanceof ArrayBuffer))
          throw Error("Expected binary GLB");
        buffer = result;
        pipeline.inspect(buffer);
      } finally {
        pipeline.dispose(original.scene);
      }
    }
    status({
      exporterPassed: true,
      exportSnapshotHash: asset.sha256,
      exportedStyle: asset.kit?.style || "imported",
    });
    return buffer;
  }
  async function exportPart(id: string) {
    check();
    const entry = (current?.bom as RuntimeSpec[] | undefined)?.find(
      (row) => row.instance === id,
    );
    if (!entry || !live) throw Error("请选择物料清单中的组件根节点");
    const built = await live.build({
      schema: "wx.part-build/1.0",
      id: entry.part,
      part: entry.part,
      style: entry.style || current?.kit?.style || "lowpoly",
      params: entry.params || {},
      material: entry.material,
    });
    try {
      const buffer = await new T.GLTFExporter().parseAsync(built.root, {
        binary: true,
        onlyVisible: false,
      });
      if (!(buffer instanceof ArrayBuffer)) throw Error("Expected binary GLB");
      pipeline.inspect(buffer);
      status({ partExported: id });
      return buffer;
    } finally {
      pipeline.dispose(built.root);
    }
  }
  async function exportRuntime() {
    check();
    if (!current?.glb || !G.WXRuntimePack) throw Error("运行时导出不可用");
    const asset = current,
      original = await pipeline.load(from64(asset.glb!).buffer);
    let packed: ReturnType<
      NonNullable<RuntimeGlobals["WXRuntimePack"]>["pack"]
    > | null = null;
    try {
      packed = G.WXRuntimePack.pack(original, asset.kit || {}, data);
      const buffer = await new T.GLTFExporter().parseAsync(packed.root, {
        binary: true,
        onlyVisible: false,
        animations: original.animations,
      });
      if (!(buffer instanceof ArrayBuffer)) throw Error("Expected binary GLB");
      if (pipeline.inspect(buffer).triangles !== packed.report.triangles_after)
        throw Error("Runtime triangle count mismatch");
      status({
        runtimeExport: {
          ...packed.report,
          source_hash: asset.sha256,
          export_bytes: buffer.byteLength,
        },
      });
      return zipStore([
        ["runtime.glb", new Uint8Array(buffer)],
        ["runtime-map.json", JSON.stringify(packed.report, null, 2)],
        ["source.assembly.json", JSON.stringify(asset.kit, null, 2)],
        [
          "README.txt",
          "Opaque static batches only. Dynamic, skinned and transparent nodes remain. Not physics, LOD or GPU certification.",
        ],
      ]);
    } finally {
      pipeline.dispose(original.scene);
      packed?.cleanup();
    }
  }
  function runtimeSidecar(asset = current!): Record<string, unknown> {
    if (!asset) throw Error("No asset");
    return buildSidecar(asset, data, G);
  }
  const interactions = createInteractions(T, {
    elements: () => elements,
    model: () => model,
    node: (id) => nodes.get(id),
    getView: () => ({ ...view, center: [...view.center] }),
    setView,
    grid: () => grid,
    fit,
    refresh,
    error: (message) => callbacks.onError?.(message),
    stopMotion: () => poseTime(0),
    locked: (doc, id) => G.WXSceneDocument?.locked(doc, id) ?? false,
  });
  function dispose() {
    if (disposed) return;
    disposed = true;
    for (const controller of controllers) controller.abort();
    tasks?.cancelAll();
    mountDispose?.();
    interactions.dispose();
    for (const item of handles.values()) pipeline.dispose(item.loaded.scene);
    handles.clear();
    if (mixer && model) {
      mixer.stopAllAction();
      mixer.uncacheRoot(model);
    }
    if (model) pipeline.dispose(model);
    model = null;
    loaded = null;
    current = null;
    nodes.clear();
    void cache?.openPromise?.then((db) => db?.close());
  }
  return {
    mergeDefinitions(patch) {
      for (const key of ["parts", "assemblies", "motions"] as const)
        Object.assign((data[key] ||= {}), patch[key]);
      for (const key of ["interfaces", "aliases", "retired", "build_context"])
        if (patch[key] !== undefined) data[key] = patch[key];
      // Library snapshots its maps. Replace that lightweight index, retaining
      // viewport, task queue and cache, which all share this data object.
      if (G.WXRuntime) live = new G.WXRuntime.Library(data);
    },
    prepare,
    commit,
    discard,
    mount,
    dispose,
    snapshot,
    getView: () => ({ ...view, center: [...view.center] }),
    setView,
    fit,
    resize,
    setWire,
    setGrid,
    setLighting,
    bindEditor: (editor: EditorBridge | null) =>
      interactions.bindEditor(editor),
    selectionChanged: () => interactions.draw(),
    focusSelection: () => interactions.focusSelection(),
    cancelInteraction: () => interactions.cancel(),
    groundCenter: () => interactions.groundCenter(),
    isolateNode,
    resetVisibility,
    explode,
    poseTime,
    playMotion,
    applyRigidState: (state) => {
      if (!model || !current?.kit || !G.WXMechanics)
        throw Error("刚性状态不可用");
      playing = false;
      mixer?.stopAllAction();
      status({ motionPlaying: false });
      explode(0);
      resetVisibility();
      try {
        const result = G.WXMechanics.apply(model, current.kit, state);
        rigidState = { ...state };
        refresh();
        status({ rigidState: { ...state }, linkage: result });
        return result;
      } catch (errorValue) {
        G.WXMechanics.apply(model, current.kit, rigidState);
        refresh();
        throw errorValue;
      }
    },
    exportPose: async () => {
      check();
      if (!current?.glb || !G.WXMechanics) throw Error("姿态导出不可用");
      const asset = current,
        state = { ...rigidState },
        original = await pipeline.load(from64(asset.glb!).buffer);
      try {
        G.WXMechanics.apply(original.scene, asset.kit || {}, state);
        const buffer = await new T.GLTFExporter().parseAsync(original.scene, {
          binary: true,
          onlyVisible: false,
          animations: [],
        });
        if (!(buffer instanceof ArrayBuffer))
          throw Error("Expected binary GLB");
        pipeline.inspect(buffer);
        status({ stateExported: true });
        return buffer;
      } finally {
        pipeline.dispose(original.scene);
      }
    },
    motionInfo: () =>
      loaded?.animations.map((clip) => ({
        name: clip.name,
        duration: clip.duration,
      })) || [],
    exportGLB,
    exportPart,
    exportRuntime,
    runtimeSidecar,
    ground: () => interactions.ground(),
    align: (axis, mode, anchor) => interactions.align(axis, mode, anchor),
    getModel: () => model,
    cache,
    tasks,
  };
}

function buildSidecar(
  asset: RuntimeAsset,
  data: RuntimeData,
  G: RuntimeGlobals,
): Record<string, unknown> {
  const assemblyInteractions: RuntimeSpec[] = [],
    assemblyColliders: RuntimeSpec[] = [],
    contentNodes = new Map<string, string>(),
    boundaries: { prefix: string; node: string; collision: RuntimeSpec }[] = [];
  function collect(source: RuntimeSpec | undefined, prefix = "", depth = 0) {
    if (!source) return;
    if (depth > 12) throw Error("Interaction dependency depth");
    const spec = G.WXSemantic?.assembly(source) || source,
      rt = spec.metadata?.runtime,
      node = prefix ? prefix.slice(0, -1) : "root";
    if (rt?.collision && rt.collision.type !== "children") {
      assemblyColliders.push({
        node,
        collision: rt.collision,
        child_collision_policy: "replace-children",
      });
      boundaries.push({ prefix, node, collision: rt.collision });
    }
    if (rt?.interaction) {
      const hook = structuredClone(rt.interaction);
      if (Array.isArray(hook.fragments))
        hook.fragments = hook.fragments.map((name: string) => prefix + name);
      if (typeof hook.target_node === "string")
        hook.target_node = prefix + hook.target_node;
      assemblyInteractions.push({ node, interaction: hook });
    }
    for (const instance of spec.instances || []) {
      if (instance.enabled === false) continue;
      const name = prefix + instance.id;
      if (instance.pivot !== undefined)
        contentNodes.set(name, name + ".__content");
      if (instance.assembly) {
        const child = data.assemblies?.[instance.assembly];
        if (child)
          collect(
            {
              ...child,
              metadata: {
                ...child.metadata,
                parameters: {
                  ...child.metadata?.parameters,
                  ...instance.params,
                },
              },
            },
            name + ".",
            depth + 1,
          );
      }
    }
  }
  collect(asset.kit?.instances ? asset.kit : data.assemblies?.[asset.id]);
  return {
    schema: "wx.collider-recipes/1.0",
    asset: asset.id,
    style: asset.kit?.style,
    units: "m",
    up: "+Y",
    coordinate_space: "component-local",
    transform_source: "named GLB content nodes, with parent rigid state",
    selection_bounds_are_colliders: false,
    engine_adapter_required: true,
    warning:
      "Authored recipes require an engine adapter; they are not an implemented physics scene.",
    assembly_interactions: assemblyInteractions,
    assembly_colliders: assemblyColliders,
    lod: asset.runtime?.lod_levels || [],
    instances: (asset.bom || []).map((entry) => {
      const definition = data.parts?.[entry.part],
        resolved =
          definition && G.WXSemantic
            ? G.WXSemantic.part(definition, entry.params || {}, data.parts!)
            : null;
      let collision = structuredClone(
        entry.collision_override ||
          resolved?.runtime?.collision || {
            type: "unspecified",
            reason: "No authored collider",
          },
      );
      const boundary = boundaries.find((item) =>
        entry.instance.startsWith(item.prefix),
      );
      if (boundary)
        collision = {
          type: "none",
          reason: "Assembly collision policy replaces children",
          assembly_node: boundary.node,
          assembly_collision_type: boundary.collision.type,
        };
      return {
        node: entry.instance,
        content_node: contentNodes.get(entry.instance) || entry.instance,
        part: entry.part,
        params: entry.params || {},
        collision,
        lod: resolved?.runtime?.lod || null,
        interaction: resolved?.runtime?.interaction || null,
        helper_only: resolved?.runtime?.helper_only === true,
      };
    }),
  };
}

function presentationLights(value: unknown): {
  color: string;
  intensity: number;
  distance: number;
  position: number[];
}[] {
  if (
    !value ||
    typeof value !== "object" ||
    !("lights" in value) ||
    !Array.isArray(value.lights)
  )
    return [];
  return value.lights.slice(0, 6).flatMap((item: unknown) => {
    if (
      !item ||
      typeof item !== "object" ||
      !("position" in item) ||
      !Array.isArray(item.position) ||
      item.position.length !== 3 ||
      !item.position.every((n) => typeof n === "number" && Number.isFinite(n))
    )
      return [];
    return [
      {
        position: item.position as number[],
        color:
          "color" in item && typeof item.color === "string"
            ? item.color
            : "#59BDD2",
        intensity:
          "intensity" in item && typeof item.intensity === "number"
            ? item.intensity
            : 9,
        distance:
          "distance" in item && typeof item.distance === "number"
            ? item.distance
            : 9,
      },
    ];
  });
}
