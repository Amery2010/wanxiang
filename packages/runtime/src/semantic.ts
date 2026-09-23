/* Declarative authoring expressions and semantic composition. No eval, functions,
 * prototype access or remote sources. Shared verbatim by Node and the browser. */
import * as T from "./three.js";
import type {
  ParameterSchema,
  Parameters,
  Part,
  RuntimeSpec,
  ComponentTransform,
  SemanticShape,
} from "./types.js";
import type { Form, SkinWeights } from "./geometry-types.js";
const RESERVED = new Set([
  "size",
  "uv_scale",
  "palette",
  "roundness",
  "voxel_resolution",
  "seed",
]);
const own = (o: object, k: PropertyKey) =>
  Object.prototype.hasOwnProperty.call(o, k);
function fail(m: string): never {
  throw Error("SEMANTIC_INVALID: " + m);
}
const copy = <V>(o: V): V => JSON.parse(JSON.stringify(o));
export function parameters(
  schema: ParameterSchema = {},
  supplied: Parameters = {},
) {
  if (!supplied || typeof supplied !== "object" || Array.isArray(supplied))
    fail("Parameters must be an object");
  const props = schema.properties || {},
    values: Parameters = {};
  if (Object.keys(props).length > 32) fail("Parameter budget");
  for (const k of Object.keys(supplied))
    if (!RESERVED.has(k) && !own(props, k)) fail("Unknown parameter " + k);
  for (const [k, p] of Object.entries(props)) {
    if (["__proto__", "constructor", "prototype"].includes(k))
      fail("Reserved parameter");
    const v = own(supplied, k) ? supplied[k] : p.default;
    if (p.enum) {
      if (!p.enum.includes(v)) fail(k + " is outside the declared choices");
    } else if (p.type === "boolean") {
      if (typeof v !== "boolean") fail(k + " must be boolean");
    } else if (
      typeof v !== "number" ||
      !Number.isFinite(v) ||
      (p.type === "integer" && !Number.isInteger(v)) ||
      (p.minimum !== undefined && v < p.minimum) ||
      (p.maximum !== undefined && v > p.maximum)
    )
      fail(k + " is outside " + p.minimum + ".." + p.maximum);
    values[k] = v;
  }
  return values;
}
export function evaluate(
  value: unknown,
  values: Parameters,
  depth = 0,
  budget = { n: 0 },
): unknown {
  if (depth > 48 || ++budget.n > 100000) fail("Expression budget");
  if (Array.isArray(value))
    return value.map((v) => evaluate(v, values, depth + 1, budget));
  if (!value || typeof value !== "object") return value;
  const node = value as Record<string, unknown>;
  if (own(node, "$param")) {
    if (!own(values, String(node.$param)))
      fail("Unknown parameter reference " + String(node.$param));
    return values[String(node.$param)];
  }
  if (own(node, "$switch")) {
    const k = String(values[String(node.$switch)]),
      cases = (node.cases || {}) as Record<string, unknown>;
    return evaluate(
      own(cases, k) ? cases[k] : node.default,
      values,
      depth + 1,
      budget,
    );
  }
  if (own(value, "$op")) {
    const args = evaluate(node.args, values, depth + 1, budget);
    if (
      !Array.isArray(args) ||
      !args.length ||
      args.length > 8 ||
      args.some((x) => typeof x !== "number" || !Number.isFinite(x))
    )
      fail("Numeric expression arguments");
    const a = args as number[];
    let v: number;
    switch (node.$op) {
      case "add":
        v = a.reduce((x, y) => x + y, 0);
        break;
      case "mul":
        v = a.reduce((x, y) => x * y, 1);
        break;
      case "sub":
        if (a.length !== 2) fail("sub arity");
        v = a[0] - a[1];
        break;
      case "div":
        if (a.length !== 2 || Math.abs(a[1]) < 1e-10) fail("Division by zero");
        v = a[0] / a[1];
        break;
      case "min":
        v = Math.min(...a);
        break;
      case "max":
        v = Math.max(...a);
        break;
      case "sin":
        v = Math.sin((a[0] * Math.PI) / 180);
        break;
      case "cos":
        v = Math.cos((a[0] * Math.PI) / 180);
        break;
      case "sqrt":
        v = Math.sqrt(a[0]);
        break;
      case "neg":
        v = -a[0];
        break;
      case "abs":
        v = Math.abs(a[0]);
        break;
      default:
        fail("Unknown operation " + node.$op);
    }
    if (!Number.isFinite(v) || Math.abs(v) > 1e6) fail("Non-finite expression");
    return v;
  }
  const result: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(value)) {
    if (["__proto__", "constructor", "prototype"].includes(k))
      fail("Unsafe object key");
    result[k] = evaluate(v, values, depth + 1, budget);
  }
  return result;
}
export function transform(c: ComponentTransform = {}) {
  const p = c.position || [0, 0, 0],
    r = c.rotation || [0, 0, 0],
    s = c.scale || [1, 1, 1];
  if (
    [p, r, s].some(
      (x) =>
        !Array.isArray(x) ||
        x.length !== 3 ||
        x.some((v) => !Number.isFinite(v)),
    ) ||
    s.some((x) => x <= 0 || x > 100)
  )
    fail("Component transform");
  const m = new T.Matrix4().compose(
    new T.Vector3(...p),
    new T.Quaternion().setFromEuler(
      new T.Euler(
        (r[0] * Math.PI) / 180,
        (r[1] * Math.PI) / 180,
        (r[2] * Math.PI) / 180,
        "ZYX",
      ),
    ),
    new T.Vector3(...s),
  );
  if (c.frame_scale) {
    const f = c.frame_scale;
    if (
      !Array.isArray(f) ||
      f.length !== 3 ||
      f.some((x) => !Number.isFinite(x) || x <= 0 || x > 100)
    )
      fail("Frame scale");
    for (let j = 0; j < 3; j++)
      for (let i = 0; i < 3; i++) m.elements[j * 4 + i] *= f[i];
  }
  if (c.mirror === "x") m.multiply(new T.Matrix4().makeScale(-1, 1, 1));
  else if (c.mirror) fail("Unsupported mirror axis");
  return m;
}
export interface Dependency {
  id: string;
  part: string;
  params: Parameters;
  dependencies: Dependency[];
}
export type ResolvedPart = Part & {
  shape_params: SemanticShape & { forms: Form[] };
  dependencies: Dependency[];
  resolved_parameters: Parameters;
};
export function part(
  def: Part,
  supplied: Parameters = {},
  registry: Map<string, Part> | Record<string, Part> = {},
  chain: string[] = [],
): ResolvedPart {
  if (!def || chain.length > 8 || chain.includes(def.id))
    fail("Missing or cyclic component definition");
  const values = parameters(def.parameter_schema, supplied),
    d = evaluate(def, values) as ResolvedPart,
    o = d.shape_params;
  if (!o) fail("Missing shape parameters");
  const forms: Form[] = (o.forms || []).map((f) => ({
      ...f,
      source_part: def.id,
    })),
    deps: Dependency[] = [];
  if ((o.components || []).length > 96) fail("Composition budget");
  for (const c of o.components || []) {
    const child =
      registry instanceof Map ? registry.get(c.part) : registry[c.part];
    if (!child) fail("Unknown component " + c.part);
    const resolved = part(child, c.params || {}, registry, [...chain, def.id]);
    const m = transform(c),
      boneMap = c.bind || {};
    deps.push({
      id: c.id || c.part,
      part: c.part,
      params: c.params || {},
      dependencies: resolved.dependencies,
    });
    for (const source of resolved.shape_params.forms) {
      const f = copy(source),
        fm = source.matrix
          ? new T.Matrix4().fromArray(source.matrix)
          : transform(source);
      f.matrix = m.clone().multiply(fm).toArray();
      delete f.position;
      delete f.rotation;
      delete f.scale;
      const bind = (w: SkinWeights): SkinWeights =>
        typeof w === "string"
          ? boneMap[w] || w
          : w
            ? Object.fromEntries(
                Object.entries(w).map(([k, v]) => [boneMap[k] || k, v]),
              )
            : w;
      for (const key of ["join_start", "join_end"] as const)
        if (f.kind === "loft" && f[key]) f[key] = boneMap[f[key]] || f[key];
      if (f.bone) f.bone = bind(f.bone);
      for (const r of f.kind === "loft" ? f.rings : []) {
        if (r.bone) r.bone = bind(r.bone);
        if (r.weights) r.weights = bind(r.weights);
      }
      if (c.bone) {
        f.bone = c.bone;
        for (const r of f.kind === "loft" ? f.rings : []) {
          delete r.weights;
          r.bone = c.bone;
        }
      }
      const localPalette = c.params?.palette || {};
      const recolor = (v: string) =>
        localPalette[v] || localPalette[String(v).toLowerCase()] || v;
      if (f.color) f.color = recolor(f.color);
      for (const r of f.kind === "loft" ? f.rings : [])
        if (r.color) r.color = recolor(r.color);
      for (const r of f.color_regions || []) r.color = recolor(r.color);
      if (f.kind === "poly" && f.colors) f.colors = f.colors.map(recolor);
      f.material = c.material || source.material || resolved.material;
      f.source_path =
        (c.id || c.part) + (f.source_path ? "." + f.source_path : "");
      forms.push(f);
    }
  }
  delete o.components;
  o.forms = forms;
  d.resolved_parameters = values;
  d.dependencies = deps;
  if (forms.length > 640) fail("Expanded form budget");
  return d;
}
export function assembly<S extends RuntimeSpec>(spec: S): S {
  const schema = spec.metadata?.parameter_schema;
  if (!schema) return copy(spec);
  const values = parameters(schema, spec.metadata?.parameters || {}),
    result = evaluate(spec, values) as S;
  result.metadata!.resolved_parameters = values;
  return result;
}
export default {
  parameters,
  evaluate,
  part,
  assembly,
  transform,
  version: "2.0.0",
};
