/* Versioned metre-space interfaces. Source definitions, not selection bounds,
 * decide mating compatibility. Legacy untyped surface ports remain unchanged. */
import * as T from "./three.js";
import type {
  InterfaceRegistry,
  RegistryInput,
  Socket,
  RuntimeContractMetadata,
  Collision,
} from "./contract-types.js";
const copy = <V>(x: V): V => JSON.parse(JSON.stringify(x));
export function createContracts(initial?: RegistryInput) {
  let registry: InterfaceRegistry = {};
  for (const d of [
    "architecture",
    "interior",
    "nature",
    "terrain",
    "props",
    "vehicle",
    "industry",
    "character",
    "creature",
    "robot",
    "gameplay",
  ])
    for (const u of ["mount", "edge"]) {
      const id = `l2.${d}.${u}.v1`;
      registry[id] = {
        id,
        version: 1,
        tolerance: 0.0001,
        allowed_scale: "none",
      };
    }
  const known = [
    "terrain.edge.1m.v1",
    "terrain.river.2m.v1",
    "road.lane.3m.v1",
    "road.sidewalk.1m.v1",
    "rail.standard.v1",
    "arch.wall.1m.v1",
    "arch.floor.1m.v1",
    "arch.door.v1",
    "pipe.flange.small.v1",
    "pipe.flange.medium.v1",
    "vehicle.wheel.v1",
    "character.hand.grip.v1",
    "character.back.mount.v1",
    "gameplay.trigger.v1",
    "fx.emitter.v1",
  ];
  for (const id of known) registry[id] = { id, version: 1, tolerance: 0.0001 };
  Object.assign(registry["road.lane.3m.v1"], { span: 3 });
  Object.assign(registry["terrain.river.2m.v1"], { span: 2 });
  Object.assign(registry["road.sidewalk.1m.v1"], { span: 1 });
  Object.assign(registry["rail.standard.v1"], { gauge: 1.435 });
  Object.assign(registry["pipe.flange.small.v1"], { diameter: 0.1 });
  Object.assign(registry["pipe.flange.medium.v1"], { diameter: 0.25 });
  function bad(m: string): never {
    throw Error("RECIPE_INVALID: " + m);
  }
  const vec = (p: unknown): p is number[] =>
    Array.isArray(p) && p.length === 3 && p.every(Number.isFinite);
  function validate(s: Socket) {
    const r = registry[s.interface || "surface"];
    if (!r) {
      if (
        /^(terrain|road|rail|arch|pipe|vehicle|character|gameplay|fx|l2)\./.test(
          s.interface || "surface",
        )
      )
        bad("Unknown versioned interface " + s.interface);
      return true;
    }
    if (!vec(s.position) || !vec(s.normal) || !vec(s.tangent))
      bad("Interface vector");
    for (const k of ["normal", "tangent"] as const)
      if (Math.abs(s[k].reduce((n, v) => n + v * v, 0) - 1) > 1e-5)
        bad("Interface axis must be unit");
    if (Math.abs(s.normal.reduce((n, v, i) => n + v * s.tangent[i], 0)) > 1e-5)
      bad("Interface axes must be perpendicular");
    if (
      s.interface?.startsWith("l2.") &&
      (s.span === undefined ||
        !Array.isArray(s.profile) ||
        s.profile.length !== 2)
    )
      bad("L2 interfaces require explicit span and two-value profile");
    if ((s.units || "m") !== "m") bad("Versioned interfaces use metres");
    if (!["none", "uniform"].includes(s.allowed_scale || "none"))
      bad("Unknown scale policy");
    for (const k of ["gauge", "diameter", "tolerance"] as const)
      if (s[k] !== undefined && (!Number.isFinite(s[k]) || s[k] <= 0))
        bad("Invalid interface " + k);
    if (s.version !== undefined && s.version !== r.version)
      bad("Interface version field mismatch");
    if (s.span !== undefined && (!Number.isFinite(s.span) || s.span <= 0))
      bad("Invalid span");
    if (
      s.profile !== undefined &&
      (!Array.isArray(s.profile) ||
        s.profile.length < 2 ||
        !s.profile.every(Number.isFinite))
    )
      bad("Invalid edge profile");
    if (!["neutral", "male", "female"].includes(s.gender || "neutral"))
      bad("Invalid interface gender");
    return true;
  }
  function compatible(a: Socket, b: Socket) {
    const ia = a.interface || "surface",
      ib = b.interface || "surface";
    if (ia !== ib)
      return {
        compatible:
          [ia, ib].includes("surface") && !registry[ia] && !registry[ib],
        reason: "interface/version mismatch",
      };
    const r = registry[ia];
    if (!r) return { compatible: true, reason: "legacy-interface" };
    validate(a);
    validate(b);
    const tol = Math.min(
      r.tolerance || 0.0001,
      a.tolerance ?? Infinity,
      b.tolerance ?? Infinity,
    );
    if (a.gender && a.gender !== "neutral" && a.gender === b.gender)
      return { compatible: false, reason: "gender mismatch" };
    for (const p of [a, b]) {
      const scale = p.world_scale || [1, 1, 1],
        policy = p.allowed_scale || r.allowed_scale || "none";
      if (!vec(scale) || scale.some((v) => v <= 0))
        return { compatible: false, reason: "invalid world scale" };
      if (policy === "none" && scale.some((v) => Math.abs(v - 1) > tol))
        return {
          compatible: false,
          reason:
            "interface forbids transformed scale; resize authored geometry instead",
        };
      if (policy === "uniform" && Math.max(...scale) - Math.min(...scale) > tol)
        return {
          compatible: false,
          reason: "interface allows uniform scale only",
        };
    }
    for (const k of ["span", "gauge", "diameter"] as const) {
      const x = a[k] ?? r[k],
        y = b[k] ?? r[k];
      if (x !== undefined && y !== undefined && Math.abs(x - y) > tol)
        return { compatible: false, reason: k + " mismatch" };
    }
    if (
      a.profile &&
      b.profile &&
      (a.profile.length !== b.profile.length ||
        a.profile.some((x, i) => Math.abs(x - b.profile![i]) > tol))
    )
      return { compatible: false, reason: "edge profile mismatch" };
    return {
      compatible: true,
      reason: "matched version, dimensions and edge profile",
      tolerance_m: tol,
    };
  }
  function scaled(s: Socket, scale: number[]) {
    const out = copy(s),
      t = new T.Vector3(...s.tangent).multiply(new T.Vector3(...scale)),
      n = new T.Vector3(...s.normal).divide(new T.Vector3(...scale));
    out.position = s.position.map((v, i) => v * scale[i]);
    if (s.span !== undefined) out.span = s.span * t.length();
    out.tangent = t.normalize().toArray();
    out.normal = n.normalize().toArray();
    if (s.profile) out.profile = s.profile.map((v) => v * scale[1]);
    return out;
  }
  function world(s: Socket, m: T.Matrix4) {
    const out = {} as Socket;
    for (const [k, v] of Object.entries(s))
      if (k !== "node" && v !== undefined) out[k] = copy(v);
    const linear = new T.Matrix3().setFromMatrix4(m),
      t = new T.Vector3(...s.tangent).applyMatrix3(linear),
      n = new T.Vector3(...s.normal).applyMatrix3(
        new T.Matrix3().getNormalMatrix(m),
      );
    out.position = new T.Vector3(...s.position).applyMatrix4(m).toArray();
    out.normal = n.normalize().toArray();
    out.tangent = t.clone().normalize().toArray();
    for (const k of ["span", "gauge", "diameter"] as const) {
      const value = s[k] ?? registry[s.interface || "surface"]?.[k];
      if (value !== undefined) out[k] = value * t.length();
    }
    const sy = new T.Vector3(0, 1, 0).applyMatrix3(linear).length();
    if (s.profile) out.profile = s.profile.map((v) => v * sy);
    out.world_scale = [0, 1, 2].map((i) =>
      new T.Vector3().setFromMatrixColumn(m, i).length(),
    );
    return out;
  }
  function validateRuntime(md?: RuntimeContractMetadata) {
    if (!md || !Object.keys(md).length) return true;
    if (
      md.schema !== "wx.runtime-metadata/1.0" ||
      md.units !== "m" ||
      md.up !== "+Y" ||
      md.forward !== "+Z"
    )
      bad("Runtime metadata coordinate/schema contract");
    if (
      md.triangle_budget !== undefined &&
      (!Number.isInteger(md.triangle_budget) ||
        md.triangle_budget < 1 ||
        md.triangle_budget > 400000)
    )
      bad("Runtime triangle budget");
    const collider = (c: Collision): void => {
      if (
        !c ||
        ![
          "none",
          "box",
          "sphere",
          "capsule",
          "convex-hull",
          "compound",
          "authored-mesh",
          "heightfield",
          "children",
        ].includes(c.type || "")
      )
        bad("Collision recipe type");
      if (
        ["authored-mesh", "heightfield"].includes(c.type || "") &&
        c.static_only !== true
      )
        bad("Concave collision must be static");
      if (
        c.type === "box" &&
        (!vec(c.size) ||
          c.size!.some((v) => v <= 0) ||
          !vec(c.center || [0, 0, 0]))
      )
        bad("Box collision recipe");
      if (
        ["sphere", "capsule"].includes(c.type || "") &&
        (!Number.isFinite(c.radius) || c.radius! <= 0)
      )
        bad("Collision radius");
      if (c.type === "sphere" && !vec(c.center || [0, 0, 0]))
        bad("Sphere centre");
      if (
        c.type === "capsule" &&
        (!vec(c.segment_start) || !vec(c.segment_end))
      )
        bad("Capsule endpoints");
      if (c.type === "compound") {
        if (
          !Array.isArray(c.shapes) ||
          !c.shapes.length ||
          c.shapes.length > 128
        )
          bad("Compound collision shape budget");
        c.shapes!.forEach(collider);
      }
    };
    collider(md.collision || { type: "none" });
    const hook = md.interaction;
    if (hook !== undefined) {
      if (
        !hook ||
        hook.schema !== "wx.interaction/1.0" ||
        hook.authority !== "consumer-game"
      )
        bad("Interaction schema/authority");
      for (const k of ["kind", "event"] as const)
        if (
          typeof hook[k] !== "string" ||
          !/^[a-z][a-z0-9_.-]{0,79}$/.test(hook[k]!)
        )
          bad("Interaction " + k);
      const t = hook.trigger || { shape: "none" };
      if (!["none", "box", "sphere"].includes(t.shape))
        bad("Interaction trigger");
      if (t.shape !== "none") collider({ ...t, type: t.shape });
      if (
        hook.fragments !== undefined &&
        (!Array.isArray(hook.fragments) ||
          hook.fragments.length > 256 ||
          new Set(hook.fragments).size !== hook.fragments.length ||
          hook.fragments.some(
            (i) => typeof i !== "string" || !/^[A-Za-z0-9_.-]{1,95}$/.test(i),
          ))
      )
        bad("Fragment nodes");
    }
    if (md.helper_only !== undefined && typeof md.helper_only !== "boolean")
      bad("helper_only boolean");
    const seen = new Set();
    for (const l of md.lod?.levels || []) {
      if (
        ![0, 1, 2].includes(l.level) ||
        seen.has(l.level) ||
        !l.parameters ||
        Array.isArray(l.parameters) ||
        typeof l.parameters !== "object"
      )
        bad("LOD parameters/level");
      seen.add(l.level);
      if (
        l.screen_height !== undefined &&
        (!(l.screen_height > 0) || l.screen_height > 1)
      )
        bad("LOD screen height");
    }
    return true;
  }
  function setRegistry(r?: RegistryInput) {
    if (r)
      registry = copy(
        ("interfaces" in r ? r.interfaces : r) as InterfaceRegistry,
      );
  }
  setRegistry(initial);
  return {
    validateRuntime,
    validate,
    compatible,
    scaled,
    world,
    setRegistry,
    registry: () => copy(registry),
  };
}
export type Contracts = ReturnType<typeof createContracts>;
export default { ...createContracts(), createContracts };
