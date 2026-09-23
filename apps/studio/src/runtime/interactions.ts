import type * as Three from "three";
import type {
  ThreeGlobal,
  ViewportElements,
  ViewState,
  EditorBridge,
  RuntimeSpec,
} from "./types";
import { effectivelyVisible } from "./pack-cpu";
interface Bridge {
  elements(): ViewportElements | null;
  model(): Three.Object3D | null;
  node(id: string): Three.Object3D | undefined;
  getView(): ViewState;
  setView(view: Partial<ViewState>): void;
  grid(): boolean;
  fit(): void;
  refresh(): void;
  error(message: string): void;
  stopMotion(): void;
  locked(doc: RuntimeSpec, id: string): boolean;
}
type Axis = "x" | "y" | "z";
type Point = { x: number; y: number };
interface Handle {
  axis: Axis | "xz" | "uniform";
  tool: "translate" | "rotate" | "scale";
  start: Point;
  end: Point;
  pivot: Three.Vector3;
  direction: Three.Vector3;
  worldPerPixel: number;
}
interface Item {
  id: string;
  node: Three.Object3D;
  p: Three.Vector3;
  q: Three.Quaternion;
  scale: Three.Vector3;
  world: Three.Vector3;
  parentInverse: Three.Matrix4 | null;
}
interface Drag {
  kind: "camera" | "marquee" | "gizmo";
  x: number;
  y: number;
  pointer: number;
  view: ViewState;
  pan: boolean;
  toggle: boolean;
  hit: string | null;
  selection: string[];
  moved: boolean;
  handle?: Handle;
  items?: Item[];
  plane?: Three.Plane;
  planeStart?: Three.Vector3 | null;
  rotationStart?: Three.Vector3 | null;
  values?: Record<string, RuntimeSpec>;
}
export function createInteractions(T: ThreeGlobal, b: Bridge) {
  let editor: EditorBridge | null = null,
    frame = 0,
    refreshTimer: ReturnType<typeof setTimeout> | null = null,
    drag: Drag | null = null,
    space = false,
    detach: (() => void) | null = null;
  const pointers = new Map<number, Point>(),
    handles = new Map<string, Handle>();
  let pinch: { distance: number; mid: Point; view: ViewState } | null = null;
  const V = (a: number[] = [0, 0, 0]) => new T.Vector3().fromArray(a),
    rad = T.MathUtils.degToRad,
    deg = T.MathUtils.radToDeg;
  const axes: Record<Axis, Three.Vector3> = {
      x: V([1, 0, 0]),
      y: V([0, 1, 0]),
      z: V([0, 0, 1]),
    },
    colors = {
      x: "#cc646b",
      y: "#58a279",
      z: "#568ecc",
      xz: "#8fb597",
      uniform: "#bd93df",
    };
  const state = () => editor?.getState();
  function camera() {
    const host = b.elements(),
      view = b.getView();
    if (!host) return null;
    const r = host.stage.getBoundingClientRect();
    if (r.height < 1) return null;
    const aspect = r.width / r.height,
      cam = new T.OrthographicCamera(
        (-view.span * aspect) / 2,
        (view.span * aspect) / 2,
        view.span / 2,
        -view.span / 2,
        0.001,
        Math.max(1000000, view.span * 20),
      );
    cam.zoom = view.zoom;
    const az = rad(view.az),
      el = rad(view.el);
    cam.position
      .copy(V(view.center))
      .addScaledVector(
        V([
          Math.sin(az) * Math.cos(el),
          Math.sin(el),
          Math.cos(az) * Math.cos(el),
        ]),
        Math.max(view.span * 3, 10),
      );
    cam.lookAt(V(view.center));
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld();
    return cam;
  }
  function project(p: Three.Vector3, cam = camera()): Point | null {
    const host = b.elements();
    if (!cam || !host) return null;
    const r = host.stage.getBoundingClientRect(),
      q = p.clone().project(cam);
    return { x: ((q.x + 1) * r.width) / 2, y: ((1 - q.y) * r.height) / 2 };
  }
  function rayAt(x: number, y: number) {
    const host = b.elements(),
      cam = camera();
    if (!host || !cam) return null;
    const r = host.stage.getBoundingClientRect(),
      ray = new T.Raycaster();
    ray.setFromCamera(
      new T.Vector2(
        ((x - r.left) / r.width) * 2 - 1,
        1 - ((y - r.top) / r.height) * 2,
      ),
      cam,
    );
    return ray;
  }
  function groundPoint(x: number, y: number, height = 0) {
    return (
      rayAt(x, y)?.ray.intersectPlane(
        new T.Plane(V([0, 1, 0]), -height),
        V(),
      ) || null
    );
  }
  function groundCenter() {
    const r = b.elements()?.stage.getBoundingClientRect();
    return r
      ? groundPoint(r.left + r.width / 2, r.top + r.height / 2)?.toArray() || [
          b.getView().center[0],
          0,
          b.getView().center[2],
        ]
      : [0, 0, 0];
  }
  function pick(x: number, y: number) {
    const model = b.model(),
      s = state();
    if (!model || !s) return null;
    model.updateMatrixWorld(true);
    const targets = new Set(
      (s.doc.instances || [])
        .filter((it: RuntimeSpec) => it.enabled !== false)
        .map((it: RuntimeSpec) => it.id),
    );
    for (const hit of rayAt(x, y)?.intersectObject(model, true) || []) {
      if (!effectivelyVisible(hit.object)) continue;
      for (
        let node: Three.Object3D | null = hit.object;
        node;
        node = node.parent
      ) {
        const name = node.userData.wxSourceName || node.name;
        if (targets.has(name))
          return {
            id: name as string,
            point: hit.point.toArray(),
            distance: hit.distance,
          };
      }
    }
    return null;
  }
  function selected(editable = false, roots = false) {
    const s = state();
    if (!s) return [];
    let list = s.ids
      .map((id) => ({
        id,
        it: (s.doc.instances as RuntimeSpec[]).find((it) => it.id === id),
        node: b.node(id),
      }))
      .filter(
        (item): item is { id: string; it: RuntimeSpec; node: Three.Object3D } =>
          !!item.node && !!item.it && item.it.enabled !== false,
      );
    if (editable)
      list = list.filter(
        (item) => !b.locked(s.doc, item.id) && !item.it.attach,
      );
    if (roots) {
      const set = new Set(list.map((item) => item.node));
      list = list.filter((item) => {
        for (let p = item.node.parent; p; p = p.parent)
          if (set.has(p)) return false;
        return true;
      });
    }
    return list;
  }
  const boxFor = (node: Three.Object3D) => {
    node.updateWorldMatrix(true, true);
    return new T.Box3().setFromObject(node);
  };
  function selectionBox() {
    const box = new T.Box3();
    for (const item of selected()) box.union(boxFor(item.node));
    return box;
  }
  function focusSelection() {
    const box = selectionBox();
    if (box.isEmpty()) {
      b.fit();
      return;
    }
    b.setView({
      center: box.getCenter(V()).toArray(),
      span: Math.max(0.15, box.getSize(V()).length() * 1.7),
      zoom: 1.12,
    });
  }
  function line(a: Point | null, c: Point | null, attrs = "") {
    return a && c && [a.x, a.y, c.x, c.y].every(Number.isFinite)
      ? `<path d="M${a.x.toFixed(2)} ${a.y.toFixed(2)}L${c.x.toFixed(2)} ${c.y.toFixed(2)}" ${attrs}/>`
      : "";
  }
  function drawNow() {
    frame = 0;
    const host = b.elements(),
      cam = camera();
    if (!host || !cam) return;
    const rect = host.stage.getBoundingClientRect(),
      view = b.getView(),
      span = view.span / view.zoom,
      center = V(view.center),
      projectP = (p: Three.Vector3) => project(p, cam);
    handles.clear();
    if (host.worldGrid) {
      host.worldGrid.setAttribute(
        "viewBox",
        `0 0 ${rect.width} ${rect.height}`,
      );
      if (b.grid()) {
        const raw = span / 20,
          pow = Math.pow(10, Math.floor(Math.log10(Math.max(0.001, raw)))),
          ratio = raw / pow,
          step = pow * (ratio > 5 ? 10 : ratio > 2 ? 5 : ratio > 1 ? 2 : 1),
          cx = Math.round(center.x / step) * step,
          cz = Math.round(center.z / step) * step,
          extent = step * 28;
        let lines = "";
        for (let n = -28; n <= 28; n++) {
          const x = cx + n * step,
            z = cz + n * step;
          lines += line(
            projectP(V([x, 0, cz - extent])),
            projectP(V([x, 0, cz + extent])),
            `fill="none" stroke="${Math.abs(x) < step * 0.001 ? "#7299bc" : "var(--grid-line,#cdd6d6)"}" stroke-width=".65" opacity=".5"`,
          );
          lines += line(
            projectP(V([cx - extent, 0, z])),
            projectP(V([cx + extent, 0, z])),
            `fill="none" stroke="${Math.abs(z) < step * 0.001 ? "#c7838b" : "var(--grid-line,#cdd6d6)"}" stroke-width=".65" opacity=".5"`,
          );
        }
        host.worldGrid.innerHTML = lines;
      } else host.worldGrid.innerHTML = "";
    }
    if (!host.editorOverlay) return;
    host.editorOverlay.setAttribute(
      "viewBox",
      `0 0 ${rect.width} ${rect.height}`,
    );
    const s = state();
    if (!s) {
      host.editorOverlay.innerHTML = "";
      return;
    }
    let svg = "";
    const selectedNodes = selected();
    for (const { node } of selectedNodes) {
      const box = boxFor(node);
      if (box.isEmpty()) continue;
      const corners: (Point | null)[] = [];
      for (let z = 0; z < 2; z++)
        for (let y = 0; y < 2; y++)
          for (let x = 0; x < 2; x++)
            corners.push(
              projectP(
                V([
                  x ? box.max.x : box.min.x,
                  y ? box.max.y : box.min.y,
                  z ? box.max.z : box.min.z,
                ]),
              ),
            );
      for (const [a, c] of [
        [0, 1],
        [0, 2],
        [0, 4],
        [1, 3],
        [1, 5],
        [2, 3],
        [2, 6],
        [3, 7],
        [4, 5],
        [4, 6],
        [5, 7],
        [6, 7],
      ])
        svg += line(
          corners[a],
          corners[c],
          'fill="none" stroke="var(--accent,#388b65)" stroke-width="1.15" opacity=".8"',
        );
    }
    const box = selectionBox();
    if (
      !box.isEmpty() &&
      selectedNodes.length === selected(true).length &&
      s.tool !== "select"
    ) {
      const pivot = box.getCenter(V()),
        base = projectP(pivot)!,
        size = (span * Math.min(105, rect.height * 0.19)) / rect.height,
        q = selectedNodes[0].node.getWorldQuaternion(new T.Quaternion());
      for (const axis of ["x", "y", "z"] as Axis[]) {
        const direction = axes[axis].clone();
        if (s.tool !== "translate") direction.applyQuaternion(q);
        const end = projectP(pivot.clone().addScaledVector(direction, size))!,
          len = Math.hypot(end.x - base.x, end.y - base.y),
          name = s.tool + "-" + axis;
        if (s.tool === "rotate") {
          const u = axes[axis === "x" ? "y" : "x"].clone().applyQuaternion(q),
            v = new T.Vector3().crossVectors(direction, u).normalize(),
            points: Point[] = [];
          for (let n = 0; n <= 64; n++) {
            const angle = (n / 64) * Math.PI * 2;
            points.push(
              projectP(
                pivot
                  .clone()
                  .addScaledVector(u, Math.cos(angle) * size * 0.83)
                  .addScaledVector(v, Math.sin(angle) * size * 0.83),
              )!,
            );
          }
          const path = points
            .map(
              (p, n) => (n ? "L" : "M") + p.x.toFixed(2) + " " + p.y.toFixed(2),
            )
            .join("");
          handles.set(name, {
            axis,
            tool: s.tool,
            start: base,
            end: points[9],
            pivot,
            direction,
            worldPerPixel: size / (len || 1),
          });
          svg += `<path d="${path}" fill="none" stroke="${colors[axis]}" stroke-width="2.1"/><path d="${path}" fill="none" stroke="transparent" stroke-width="15" data-gizmo="${name}" style="pointer-events:stroke"/>`;
        } else if (len >= 9) {
          handles.set(name, {
            axis,
            tool: s.tool,
            start: base,
            end,
            pivot,
            direction,
            worldPerPixel: size / len,
          });
          svg +=
            line(
              base,
              end,
              `stroke="${colors[axis]}" stroke-width="2.4" fill="none"`,
            ) +
            line(
              base,
              end,
              `stroke="transparent" stroke-width="18" fill="none" data-gizmo="${name}" style="pointer-events:stroke"`,
            ) +
            `<rect x="${end.x - 5}" y="${end.y - 5}" width="10" height="10" fill="${colors[axis]}" data-gizmo="${name}" style="pointer-events:all"/><text x="${end.x + 8}" y="${end.y + 4}" font-size="11" fill="${colors[axis]}">${axis.toUpperCase()}</text>`;
        }
      }
      if (s.tool === "translate") {
        const p1 = projectP(pivot.clone().add(V([size * 0.28, 0, 0])))!,
          p2 = projectP(pivot.clone().add(V([size * 0.28, 0, size * 0.28])))!,
          p3 = projectP(pivot.clone().add(V([0, 0, size * 0.28])))!;
        handles.set("translate-xz", {
          axis: "xz",
          tool: s.tool,
          start: base,
          end: p2,
          pivot,
          direction: axes.y,
          worldPerPixel: 1,
        });
        svg += `<polygon points="${base.x},${base.y} ${p1.x},${p1.y} ${p2.x},${p2.y} ${p3.x},${p3.y}" fill="#6da879" fill-opacity=".3" stroke="#6da879" data-gizmo="translate-xz" style="pointer-events:all"/>`;
      } else if (s.tool === "scale") {
        handles.set("scale-uniform", {
          axis: "uniform",
          tool: s.tool,
          start: base,
          end: { x: base.x + 55, y: base.y - 55 },
          pivot,
          direction: axes.y,
          worldPerPixel: 1,
        });
        svg += `<rect x="${base.x - 6}" y="${base.y - 6}" width="12" height="12" fill="${colors.uniform}" data-gizmo="scale-uniform" style="pointer-events:all"/>`;
      }
    }
    if (drag?.kind === "marquee") {
      const p = pointers.get(drag.pointer);
      if (p) {
        const x = drag.x - rect.left,
          y = drag.y - rect.top,
          x2 = p.x - rect.left,
          y2 = p.y - rect.top;
        svg += `<rect x="${Math.min(x, x2)}" y="${Math.min(y, y2)}" width="${Math.abs(x2 - x)}" height="${Math.abs(y2 - y)}" fill="#388b6520" stroke="#388b65"/>`;
      }
    }
    host.editorOverlay.innerHTML = svg;
  }
  function draw() {
    if (!frame && b.elements()) frame = requestAnimationFrame(drawNow);
  }
  function refreshSoon() {
    if (refreshTimer !== null) return;
    refreshTimer = setTimeout(() => {
      refreshTimer = null;
      b.refresh();
      draw();
    }, 85);
  }
  function restore(d: Drag | null) {
    if (!d?.items) return;
    for (const item of d.items) {
      item.node.position.copy(item.p);
      item.node.quaternion.copy(item.q);
      item.node.scale.copy(item.scale);
      item.node.updateMatrix();
    }
    if (refreshTimer !== null) clearTimeout(refreshTimer);
    refreshTimer = null;
    b.refresh();
    draw();
  }
  function cancel() {
    const d = drag;
    drag = null;
    pinch = null;
    pointers.clear();
    restore(d);
    draw();
    return !!d;
  }
  function pan(view: ViewState, dx: number, dy: number): ViewState {
    const rect = b.elements()!.stage.getBoundingClientRect(),
      scale = view.span / view.zoom / rect.height,
      az = rad(view.az),
      el = rad(view.el),
      right = V([Math.cos(az), 0, -Math.sin(az)]),
      up = V([
        -Math.sin(az) * Math.sin(el),
        Math.cos(el),
        -Math.cos(az) * Math.sin(el),
      ]);
    return {
      ...view,
      center: V(view.center)
        .addScaledVector(right, -dx * scale)
        .addScaledVector(up, dy * scale)
        .toArray(),
    };
  }
  const ui = (e: Event) =>
    e.target instanceof Element &&
    !!e.target.closest(
      'button,input,textarea,select,[role="dialog"],.stage-toolbar,.viewport-controls,.view-cube',
    );
  function capture(e: PointerEvent) {
    e.preventDefault();
    e.stopPropagation();
    try {
      b.elements()?.stage.setPointerCapture(e.pointerId);
    } catch {
      /* Detached pointer capture. */
    }
  }
  function down(e: PointerEvent) {
    if (ui(e) || !b.model()) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (e.pointerType === "touch" && pointers.size === 2) {
      restore(drag);
      const p = [...pointers.values()];
      pinch = {
        distance: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y),
        mid: { x: (p[0].x + p[1].x) / 2, y: (p[0].y + p[1].y) / 2 },
        view: b.getView(),
      };
      drag = null;
      capture(e);
      return;
    }
    const s = state(),
      name =
        e.target instanceof Element
          ? e.target.closest("[data-gizmo]")?.getAttribute("data-gizmo")
          : null,
      h = name ? handles.get(name) : null,
      hit = s && e.button === 0 && !space ? pick(e.clientX, e.clientY) : null;
    drag = {
      kind: "camera",
      x: e.clientX,
      y: e.clientY,
      pointer: e.pointerId,
      view: b.getView(),
      pan: e.button !== 0 || space,
      toggle: e.shiftKey || e.ctrlKey || e.metaKey,
      hit: hit?.id || null,
      selection: [...(s?.ids || [])],
      moved: false,
    };
    if (h && s && !s.busy) {
      const items = selected(true, true);
      if (!items.length || items.length !== selected(false, true).length) {
        b.error("请先解锁对象 / 图层；连接约束对象不能直接变换");
        drag = null;
        return;
      }
      b.stopMotion();
      b.model()!.updateMatrixWorld(true);
      const plane = new T.Plane().setFromNormalAndCoplanarPoint(
          h.direction,
          h.pivot,
        ),
        start = rayAt(e.clientX, e.clientY)?.ray.intersectPlane(plane, V());
      Object.assign(drag, {
        kind: "gizmo",
        handle: h,
        plane,
        planeStart: groundPoint(e.clientX, e.clientY, h.pivot.y),
        rotationStart: start?.clone().sub(h.pivot).normalize(),
        items: items.map(({ id, node }) => ({
          id,
          node,
          p: node.position.clone(),
          q: node.quaternion.clone(),
          scale: node.scale.clone(),
          world: node.getWorldPosition(V()),
          parentInverse: node.parent?.matrixWorld.clone().invert() || null,
        })),
      });
    } else if (s && e.button === 0 && !space) {
      if (hit) {
        if (!s.ids.includes(hit.id) || drag.toggle)
          editor?.select([hit.id], { toggle: drag.toggle });
      } else if (s.tool === "select") drag.kind = "marquee";
    }
    b.elements()?.stage.focus({ preventScroll: true });
    capture(e);
  }
  function values(d: Drag, x: number, y: number, alt: boolean) {
    const s = state()!,
      h = d.handle!,
      items = d.items!,
      dx = x - d.x,
      dy = y - d.y,
      len = Math.hypot(h.end.x - h.start.x, h.end.y - h.start.y) || 1,
      sx = (h.end.x - h.start.x) / len,
      sy = (h.end.y - h.start.y) / len,
      snap = (value: number, step: number) =>
        s.snap && !alt && step > 0 ? Math.round(value / step) * step : value,
      result: Record<string, RuntimeSpec> = {};
    if (h.tool === "translate") {
      const delta = V();
      if (h.axis === "xz") {
        const p = groundPoint(x, y, h.pivot.y);
        if (p && d.planeStart) delta.copy(p).sub(d.planeStart);
        delta.y = 0;
        delta.x =
          snap(items[0].world.x + delta.x, s.snapMove) - items[0].world.x;
        delta.z =
          snap(items[0].world.z + delta.z, s.snapMove) - items[0].world.z;
      } else {
        const axis = h.axis as Axis,
          amount =
            snap(
              items[0].world[axis] + (dx * sx + dy * sy) * h.worldPerPixel,
              s.snapMove,
            ) - items[0].world[axis];
        delta.copy(axes[axis]).multiplyScalar(amount);
      }
      for (const item of items) {
        const p = item.world.clone().add(delta);
        if (item.parentInverse) p.applyMatrix4(item.parentInverse);
        result[item.id] = {
          position: p.toArray().map((n) => Number(n.toFixed(6))),
        };
      }
    } else if (h.tool === "rotate") {
      const p = rayAt(x, y)?.ray.intersectPlane(d.plane!, V()),
        r = b.elements()!.stage.getBoundingClientRect();
      let delta: number;
      if (p && d.rotationStart && p.distanceTo(h.pivot) > 1e-6) {
        const v = p.sub(h.pivot).normalize(),
          v0 = d.rotationStart;
        delta = Math.atan2(h.direction.dot(v0.clone().cross(v)), v0.dot(v));
      } else
        delta =
          Math.atan2(y - r.top - h.start.y, x - r.left - h.start.x) -
          Math.atan2(d.y - r.top - h.start.y, d.x - r.left - h.start.x);
      delta = rad(snap(deg(delta), s.snapRotate));
      for (const item of items) {
        const q = item.q
            .clone()
            .multiply(
              new T.Quaternion().setFromAxisAngle(axes[h.axis as Axis], delta),
            ),
          e = new T.Euler().setFromQuaternion(q, "ZYX");
        result[item.id] = {
          rotation: [e.x, e.y, e.z].map((n) => Number(deg(n).toFixed(5))),
        };
      }
    } else {
      const factor = Math.max(
        0.01,
        snap(
          1 +
            (h.axis === "uniform" ? (dx - dy) / 110 : (dx * sx + dy * sy) / 95),
          s.snapScale,
        ),
      );
      for (const item of items) {
        const scale = item.scale.toArray();
        for (let i = 0; i < 3; i++)
          if (h.axis === "uniform" || "xyz"[i] === h.axis)
            scale[i] = Math.max(0.0001, Math.min(100, scale[i] * factor));
        result[item.id] = { scale: scale.map((n) => Number(n.toFixed(6))) };
      }
    }
    return result;
  }
  function move(e: PointerEvent) {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch && pointers.size >= 2) {
      const p = [...pointers.values()],
        distance = Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y),
        mid = { x: (p[0].x + p[1].x) / 2, y: (p[0].y + p[1].y) / 2 },
        v = pan(pinch.view, mid.x - pinch.mid.x, mid.y - pinch.mid.y);
      v.zoom = Math.max(
        0.03,
        Math.min(
          50,
          (pinch.view.zoom * distance) / Math.max(1, pinch.distance),
        ),
      );
      b.setView(v);
      capture(e);
      return;
    }
    if (!drag || drag.pointer !== e.pointerId) return;
    const dx = e.clientX - drag.x,
      dy = e.clientY - drag.y;
    if (Math.hypot(dx, dy) > 3) drag.moved = true;
    if (!drag.moved) return;
    if (drag.kind === "gizmo") {
      try {
        drag.values = values(drag, e.clientX, e.clientY, e.altKey);
        for (const item of drag.items!) {
          const v = drag.values[item.id];
          if (v.position) item.node.position.fromArray(v.position);
          if (v.rotation)
            item.node.quaternion.setFromEuler(
              new T.Euler(
                rad(v.rotation[0]),
                rad(v.rotation[1]),
                rad(v.rotation[2]),
                "ZYX",
              ),
            );
          if (v.scale) item.node.scale.fromArray(v.scale);
          item.node.updateMatrix();
        }
        b.model()?.updateMatrixWorld(true);
        refreshSoon();
        draw();
      } catch (error) {
        b.error(String(error));
        cancel();
      }
    } else if (drag.kind === "marquee") draw();
    else
      b.setView(
        drag.pan
          ? pan(drag.view, dx, dy)
          : {
              ...drag.view,
              az: drag.view.az - dx * 0.35,
              el: Math.max(-85, Math.min(89.98, drag.view.el + dy * 0.28)),
            },
      );
    capture(e);
  }
  async function up(e: PointerEvent) {
    const p = pointers.get(e.pointerId);
    pointers.delete(e.pointerId);
    if (pinch) {
      if (pointers.size < 2) {
        pinch = null;
        drag = null;
      }
      return;
    }
    if (!drag || drag.pointer !== e.pointerId) return;
    const d = drag;
    drag = null;
    capture(e);
    try {
      b.elements()?.stage.releasePointerCapture(e.pointerId);
    } catch {
      /* Already released. */
    }
    if (d.kind === "gizmo") {
      restore(d);
      if (d.moved && d.values)
        try {
          await editor?.command(
            {
              type: "transform-many",
              ids: d.items!.map((item) => item.id),
              values: d.values,
            },
            { label: "视口变换" },
          );
        } catch (error) {
          b.error(String(error));
        }
    } else if (d.kind === "marquee" && p && editor) {
      const rect = b.elements()!.stage.getBoundingClientRect();
      if (d.moved) {
        const x1 = Math.min(d.x, p.x) - rect.left,
          x2 = Math.max(d.x, p.x) - rect.left,
          y1 = Math.min(d.y, p.y) - rect.top,
          y2 = Math.max(d.y, p.y) - rect.top,
          ids: string[] = [];
        for (const it of state()!.doc.instances || []) {
          const node = b.node(it.id);
          if (!node || it.enabled === false) continue;
          const at = project(boxFor(node).getCenter(V()));
          if (at && at.x >= x1 && at.x <= x2 && at.y >= y1 && at.y <= y2)
            ids.push(it.id);
        }
        editor.select(d.toggle ? [...new Set([...d.selection, ...ids])] : ids);
      } else if (!d.toggle) editor.select([]);
    } else if (!d.moved && editor) {
      if (e.button === 2 && state()!.ids.length)
        editor.context?.(e.clientX, e.clientY);
      else if (e.button === 0 && !d.pan && !d.toggle)
        editor.select(d.hit ? [d.hit] : []);
    }
    draw();
  }
  function worldDelta(deltas: Record<string, number[]>) {
    const values: Record<string, RuntimeSpec> = {};
    for (const [id, delta] of Object.entries(deltas)) {
      const node = b.node(id);
      if (!node) continue;
      node.updateWorldMatrix(true, false);
      const p = node.getWorldPosition(V()).add(V(delta));
      if (node.parent) node.parent.worldToLocal(p);
      values[id] = { position: p.toArray().map((n) => Number(n.toFixed(6))) };
    }
    return editor?.command(
      { type: "transform-many", ids: Object.keys(values), values },
      { label: "空间对齐" },
    );
  }
  function ground() {
    const list = selected(true, true);
    if (list.length !== selected(false, true).length) {
      b.error("请先解锁所选对象");
      return;
    }
    return worldDelta(
      Object.fromEntries(
        list.map((item) => [item.id, [0, -boxFor(item.node).min.y, 0]]),
      ),
    );
  }
  function align(axis: string, mode: string, anchor = "center") {
    if (!["x", "y", "z"].includes(axis)) return;
    const list = selected(true, true);
    if (list.length < 2) return;
    if (list.length !== selected(false, true).length) {
      b.error("请先解锁所有所选对象");
      return;
    }
    const rows = list.map((item) => {
        const box = boxFor(item.node),
          point =
            anchor === "min"
              ? box.min
              : anchor === "max"
                ? box.max
                : box.getCenter(V());
        return { id: item.id, value: point[axis as Axis] };
      }),
      deltas: Record<string, number[]> = {};
    if (mode === "distribute") rows.sort((a, c) => a.value - c.value);
    const start = rows[0].value,
      step =
        mode === "distribute"
          ? (rows[rows.length - 1].value - start) / (rows.length - 1)
          : 0;
    rows.forEach((item, i) => {
      const d = [0, 0, 0];
      d["xyz".indexOf(axis)] = start + step * i - item.value;
      deltas[item.id] = d;
    });
    return worldDelta(deltas);
  }
  function mount(host: ViewportElements) {
    detach?.();
    const controller = new AbortController(),
      options = { signal: controller.signal },
      stage = host.stage;
    stage.addEventListener("pointerdown", down, options);
    stage.addEventListener("pointermove", move, options);
    stage.addEventListener(
      "pointerup",
      (e) => {
        void up(e);
      },
      options,
    );
    stage.addEventListener("pointercancel", () => cancel(), options);
    stage.addEventListener(
      "lostpointercapture",
      () => {
        if (drag?.kind === "gizmo") cancel();
      },
      options,
    );
    stage.addEventListener("contextmenu", (e) => e.preventDefault(), options);
    stage.addEventListener(
      "wheel",
      (e) => {
        if (ui(e)) return;
        e.preventDefault();
        const view = b.getView();
        b.setView({ zoom: view.zoom * Math.exp(-e.deltaY * 0.0012) });
      },
      { ...options, passive: false },
    );
    stage.addEventListener(
      "dblclick",
      (e) => {
        if (ui(e) || !editor) return;
        const hit = pick(e.clientX, e.clientY);
        if (hit) {
          editor.select([hit.id]);
          focusSelection();
        }
      },
      options,
    );
    stage.addEventListener(
      "dragover",
      (e) => {
        if (
          editor &&
          e.dataTransfer?.types.includes("application/x-wx-asset")
        ) {
          e.preventDefault();
          e.dataTransfer.dropEffect = "copy";
          stage.classList.add("scene-drop-active");
        }
      },
      options,
    );
    stage.addEventListener(
      "dragleave",
      () => stage.classList.remove("scene-drop-active"),
      options,
    );
    stage.addEventListener(
      "drop",
      (e) => {
        stage.classList.remove("scene-drop-active");
        const ref = e.dataTransfer?.getData("application/x-wx-asset"),
          s = state();
        if (!ref || !s) return;
        e.preventDefault();
        const pos =
          groundPoint(e.clientX, e.clientY)?.toArray() || groundCenter();
        if (s.snap && s.snapMove > 0)
          for (const i of [0, 2])
            pos[i] = Math.round(pos[i] / s.snapMove) * s.snapMove;
        editor?.insert?.(ref, pos);
      },
      options,
    );
    stage.addEventListener(
      "keydown",
      (e) => {
        if (
          e.target instanceof Element &&
          e.target.closest("input,textarea,select")
        )
          return;
        if (e.code === "Space") {
          e.preventDefault();
          space = true;
        }
        if (e.key === "Escape" && cancel()) e.preventDefault();
      },
      options,
    );
    document.addEventListener(
      "keyup",
      (e) => {
        if (e.code === "Space") space = false;
      },
      options,
    );
    window.addEventListener(
      "blur",
      () => {
        space = false;
        cancel();
      },
      options,
    );
    const diagnostics = {
      pick,
      project: (point: number[]) => project(V(point)),
      handles: () =>
        Object.fromEntries(
          [...handles].map(([name, h]) => [
            name,
            {
              axis: h.axis,
              start: [h.start.x, h.start.y],
              end: [h.end.x, h.end.y],
              worldPerPixel: h.worldPerPixel,
              pivot: h.pivot.toArray(),
              worldAxis: h.direction.toArray(),
            },
          ]),
        ),
      setView: b.setView,
      view: b.getView,
      selectionBounds: () => {
        const box = selectionBox();
        return { min: box.min.toArray(), max: box.max.toArray() };
      },
      focusSelection,
      ground,
      align,
      cancel,
    };
    const globals = globalThis as typeof globalThis & {
      WX_VIEWPORT_QA?: typeof diagnostics;
    };
    const previous = globals.WX_VIEWPORT_QA;
    globals.WX_VIEWPORT_QA = diagnostics;
    detach = () => {
      if (globals.WX_VIEWPORT_QA === diagnostics) {
        if (previous) globals.WX_VIEWPORT_QA = previous;
        else delete globals.WX_VIEWPORT_QA;
      }
      controller.abort();
      cancel();
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      if (refreshTimer !== null) clearTimeout(refreshTimer);
      refreshTimer = null;
    };
    draw();
    return detach;
  }
  function dispose() {
    detach?.();
    detach = null;
    editor = null;
  }
  return {
    mount,
    dispose,
    bindEditor: (next: EditorBridge | null) => {
      if (editor !== next) cancel();
      editor = next;
      draw();
    },
    draw,
    cancel,
    pick,
    project: (point: number[]) => project(V(point)),
    getHandles: () => Object.fromEntries(handles),
    selectionBox,
    focusSelection,
    ground,
    groundCenter,
    align,
  };
}
