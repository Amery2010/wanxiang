/* Small deterministic linkage solver. A telescoping rod is translated, never stretched. */
import * as T from "./three.js";
import type { RuntimeSpec } from "./types.js";
function fail(m: string): never {
  throw Error("LINKAGE_INVALID: " + m);
}
export function apply(
  root: T.Object3D,
  spec: RuntimeSpec,
  state: Record<string, number> = {},
) {
  const metadata = spec.metadata || {},
    controls = metadata.state_controls || [],
    struts = metadata.struts || [];
  if (!state || typeof state !== "object" || Array.isArray(state))
    fail("State must be an object");
  for (const k of Object.keys(state))
    if (!controls.some((c) => c.id === k)) fail("Unknown state control: " + k);
  if (controls.length > 24 || struts.length > 24) fail("Constraint budget");
  const by = new Map<string, T.Object3D>();
  root.traverse((o) => {
    by.set(o.userData.wxSourceName || o.name, o);
    if (!by.has(o.name)) by.set(o.name, o);
  });
  const node = (name: string | undefined) => {
    const o = by.get(name || "");
    if (!o) fail("Node missing: " + name);
    return o;
  };
  const previous: [
    T.Object3D,
    T.Vector3,
    T.Quaternion,
    T.Vector3,
    number[] | undefined,
  ][] = [];
  root.traverse((o) =>
    previous.push([
      o,
      o.position.clone(),
      o.quaternion.clone(),
      o.scale.clone(),
      o.userData.wxRestMatrix?.slice(),
    ]),
  );
  try {
    if (!state || typeof state !== "object" || Array.isArray(state))
      fail("State must be an object");
    const changes = new Map<T.Object3D, T.Matrix4>();
    for (const control of controls) {
      const value = state[control.id] ?? control.default ?? 0;
      if (!Number.isFinite(value) || value < control.min || value > control.max)
        fail("State outside range: " + control.id);
      if (
        !Array.isArray(control.axis) ||
        control.axis.length !== 3 ||
        control.axis.some((v) => !Number.isFinite(v))
      )
        fail("Invalid control axis");
      const axis = new T.Vector3(...control.axis);
      if (axis.lengthSq() < 1e-12) fail("Degenerate control axis");
      axis.normalize();
      if (!["rotation", "translation"].includes(control.mode || "rotation"))
        fail("Unknown control mode");
      for (const name of control.nodes || [control.node]) {
        const o = node(name);
        o.updateMatrix();
        if (!o.userData.wxRestMatrix)
          o.userData.wxRestMatrix = o.matrix.toArray();
        if (!changes.has(o))
          changes.set(o, new T.Matrix4().fromArray(o.userData.wxRestMatrix));
        const delta =
          control.mode === "translation"
            ? new T.Matrix4().makeTranslation(
                axis.x * value,
                axis.y * value,
                axis.z * value,
              )
            : new T.Matrix4().makeRotationAxis(axis, (value * Math.PI) / 180);
        changes.get(o)!.multiply(delta);
      }
    }
    for (const [o, m] of changes) {
      m.decompose(o.position, o.quaternion, o.scale);
      o.updateMatrix();
    }
    root.updateMatrixWorld(true);
    const report = [];
    for (const c of struts) {
      const o = node(c.node),
        a = node(c.from.node),
        b = node(c.to.node),
        rod = node(c.node + "." + c.rod);
      const parent = o.parent!;
      parent.updateWorldMatrix(true, false);
      const inv = parent.matrixWorld.clone().invert();
      const from = new T.Vector3(...c.from.point)
          .applyMatrix4(a.matrixWorld)
          .applyMatrix4(inv),
        to = new T.Vector3(...c.to.point)
          .applyMatrix4(b.matrixWorld)
          .applyMatrix4(inv),
        direction = to.clone().sub(from),
        length = direction.length();
      if (
        !Number.isFinite(length) ||
        length < 1e-5 ||
        length < c.min_length - 1e-6 ||
        length > c.max_length + 1e-6
      )
        fail(c.node + " exceeds cylinder travel: " + length.toFixed(4));
      o.position.copy(from);
      o.quaternion.setFromUnitVectors(
        new T.Vector3(0, 1, 0),
        direction.normalize(),
      );
      o.scale.set(1, 1, 1);
      o.updateMatrix();
      rod.position.set(0, length - c.rod_length, 0);
      rod.updateMatrix();
      root.updateMatrixWorld(true);
      const tip = new T.Vector3(0, c.rod_length, 0).applyMatrix4(
          rod.matrixWorld,
        ),
        target = new T.Vector3(...c.to.point).applyMatrix4(b.matrixWorld);
      report.push({ node: c.node, length, error: tip.distanceTo(target) });
    }
    root.userData.wxLinkage = { state: { ...state }, constraints: report };
    return report;
  } catch (e) {
    for (const [o, p, q, s, rest] of previous) {
      o.position.copy(p);
      o.quaternion.copy(q);
      o.scale.copy(s);
      if (rest) o.userData.wxRestMatrix = rest;
      else delete o.userData.wxRestMatrix;
      o.updateMatrix();
    }
    root.updateMatrixWorld(true);
    throw e;
  }
}
export default { apply, version: "2.0.0" };
