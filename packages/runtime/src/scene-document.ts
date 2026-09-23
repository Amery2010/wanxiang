/* Wanxiang 3.5 editable scene source. Immutable, validated, renderer-independent.
 * Groups organize selection only; they do not introduce hidden transform parents.
 * Command batches are atomic: a failed member never changes the input document. */
import Semantic from "./semantic.js";
import type {
  RuntimeSpec,
  Scene,
  SceneInstance,
  SceneObjectMetadata,
  Parameters,
} from "./types.js";
type Catalog = Record<string, RuntimeSpec>;
interface CommandFields {
  type: string;
  id?: string;
  ids?: string[];
  commands?: SceneCommand[];
  position?: number[];
  rotation?: number[];
  scale?: number[];
  delta?: number[];
  values?: Record<string, Partial<SceneInstance>>;
  label?: string;
  title?: string;
  visible?: boolean;
  locked?: boolean;
  layer?: string;
  region?: string;
  group?: string;
  target?: string;
  style?: string;
  params?: Parameters;
  ref?: string;
  rename?: boolean;
  withChildren?: boolean;
  offset?: number[];
  newId?: string;
  objectId?: string;
  instances?: SceneInstance[];
  objects?: Record<string, SceneObjectMetadata>;
  before?: string;
}
/** Commands require only the identifiers consumed by their operation. */
export type SceneCommand = CommandFields &
  (
    | { type: "add" | "replace"; ref: string }
    | {
        type:
          | "move-layer"
          | "layer-visibility"
          | "layer-lock"
          | "add-layer"
          | "rename-layer";
        layer: string;
      }
    | { type: "remove-layer"; layer: string; target: string }
    | { type: "move-region" | "add-region"; region: string }
    | {
        type: "group-visibility" | "group-lock" | "rename-group";
        group: string;
      }
    | {
        type:
          | "transform"
          | "transform-many"
          | "rename"
          | "rename-scene"
          | "visibility"
          | "lock"
          | "params"
          | "duplicate"
          | "duplicate-many"
          | "remove"
          | "remove-many"
          | "paste"
          | "group"
          | "ungroup"
          | "reorder"
          | "batch";
      }
  );
export interface SceneQuery {
  ids?: string[];
  layer?: string;
  region?: string;
}

const clone = <V>(x: V): V => JSON.parse(JSON.stringify(x));
function bad(m: string): never {
  throw Error("SCENE_INVALID: " + m);
}
const safe = (s: unknown): s is string =>
  typeof s === "string" &&
  /^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$/.test(s) &&
  !s.includes("..");
const object = (v: unknown): v is Record<string, unknown> =>
  v !== null && typeof v === "object" && !Array.isArray(v);
function guard(v: unknown, depth = 0) {
  if (depth > 48) bad("结构过深");
  if (typeof v === "number" && !Number.isFinite(v)) bad("非有限数值");
  if (v && typeof v === "object")
    for (const [k, x] of Object.entries(v)) {
      if (["__proto__", "prototype", "constructor"].includes(k))
        bad("不安全的字段");
      guard(x, depth + 1);
    }
}
function vector(v: unknown, kind: string): number[] {
  if (
    !Array.isArray(v) ||
    v.length !== 3 ||
    v.some(
      (n) =>
        typeof n !== "number" ||
        !Number.isFinite(n) ||
        Math.abs(n) > 100000 ||
        (kind === "scale" && (n < 0.0001 || n > 100)),
    )
  )
    bad("无效的 " + kind);
  return [...(v as number[])];
}
function owner(path: string, ids: Iterable<string>) {
  if (path === "root") return "root";
  return (
    [...ids]
      .filter((id) => path === id || path.startsWith(id + "."))
      .sort((a, b) => b.length - a.length)[0] || String(path)
  );
}
function normalize(source: unknown, catalog?: Catalog): Scene {
  guard(source);
  if (!object(source) || JSON.stringify(source).length > 1000000)
    bad("配置必须为对象且不超过 1 MB");
  let d = clone(source) as unknown as Scene;
  if (
    d.schema !== "wx.assembly/1.0" ||
    !safe(d.id) ||
    !Array.isArray(d.instances) ||
    d.instances.length > 2500
  )
    bad("不是有效的场景配方");
  d = Semantic.assembly(d);
  if (d.metadata !== undefined && !object(d.metadata)) bad("无效元数据");
  d.metadata = d.metadata || ({} as Scene["metadata"]);
  if ((d.metadata.scene as unknown) === true)
    d.metadata.scene = {} as Scene["metadata"]["scene"];
  if (d.metadata.scene !== undefined && !object(d.metadata.scene))
    bad("无效场景元数据");
  const s = (d.metadata.scene =
    d.metadata.scene || ({} as Scene["metadata"]["scene"]));
  s.schema = "wx.scene/1.0";
  s.title = String(s.title || d.name || d.id).slice(0, 128);
  s.units = "m";
  for (const k of ["objects", "layers", "regions", "groups"] as const) {
    if (s[k] !== undefined && !object(s[k])) bad("无效的 " + k);
  }
  s.objects = s.objects || {};
  s.layers = s.layers || {};
  s.regions = s.regions || {};
  s.groups = s.groups || {};
  if (!Object.keys(s.layers).length)
    s.layers.default = { label: "默认图层", visible: true };
  if (!Object.keys(s.regions).length) s.regions.site = { label: "全场地" };
  for (const [k, limit] of [
    ["layers", 128],
    ["regions", 128],
    ["groups", 512],
  ] as const) {
    if (Object.keys(s[k]).length > limit) bad(k + " 数量超过限制");
    for (const [id, row] of Object.entries(s[k])) {
      if (!safe(id) || !object(row)) bad("无效的 " + k);
      row.label = String(row.label || id).slice(0, 128);
      if (k === "layers") {
        row.visible = row.visible !== false;
        row.locked = row.locked === true;
      }
      if (k === "groups") {
        row.hidden = row.hidden === true;
        row.locked = row.locked === true;
      }
    }
  }
  const ids = new Set<string>(),
    first = Object.keys(s.layers)[0],
    region = Object.keys(s.regions)[0];
  for (const it of d.instances) {
    if (!object(it) || !safe(it.id) || ids.has(it.id))
      bad("重复或无效的对象 ID");
    ids.add(it.id);
    const ref = it.assembly || it.part;
    if (!safe(ref) || !!it.assembly === !!it.part) bad("对象必须引用一个资产");
    if (catalog && !catalog[ref]) bad("未知资产 " + ref);
    for (const [k, v] of Object.entries({
      position: [0, 0, 0],
      rotation: [0, 0, 0],
      scale: [1, 1, 1],
    }))
      it[k] = vector(it[k] ?? v, k);
    if (it.params !== undefined && !object(it.params)) bad("无效对象参数");
    if (s.objects[it.id] !== undefined && !object(s.objects[it.id]))
      bad("无效对象元数据");
    const o = (s.objects[it.id] = s.objects[it.id] || { layer: first, region });
    o.label = String(o.label || it.id).slice(0, 128);
    o.layer = o.layer || first;
    o.region = o.region || region;
    if (!s.layers[o.layer] || !s.regions[o.region])
      bad("对象引用未知图层或分区");
    if (o.group && !s.groups[o.group]) bad("对象引用未知选择组");
    o.locked = o.locked === true;
    if (o.hidden === undefined) o.hidden = it.enabled === false;
    o.hidden = o.hidden === true;
    it.enabled =
      !o.hidden &&
      s.layers[o.layer].visible &&
      (!o.group || !s.groups[o.group].hidden);
  }
  for (const key of Object.keys(s.objects))
    if (!ids.has(key)) delete s.objects[key];
  const by = new Map(d.instances.map((i) => [i.id, i])),
    edges = new Map(
      d.instances.map((i) => [
        i.id,
        [i.parent, i.attach?.target]
          .filter((x): x is string => !!x)
          .map((x) => owner(String(x), ids))
          .filter((x) => x !== "root"),
      ]),
    );
  const colors = new Map<string, number>();
  function visit(id: string, depth = 0) {
    if (depth > 128) bad("对象依赖过深");
    if (colors.get(id) === 1) bad("对象依赖成环");
    if (colors.get(id) === 2) return;
    colors.set(id, 1);
    for (const dep of edges.get(id)!) {
      if (!by.has(dep)) bad("对象依赖不存在 " + dep);
      visit(dep, depth + 1);
      if (!by.get(dep)!.enabled) by.get(id)!.enabled = false;
    }
    colors.set(id, 2);
  }
  for (const id of ids) visit(id);
  return d;
}
function nextId(d: { instances: { id: string }[] }, base: string) {
  base = (base || "object").replace(/[^A-Za-z0-9_-]/g, "_").slice(0, 70);
  if (!/^[A-Za-z0-9]/.test(base)) base = "object";
  let n = 1,
    id = base;
  const ids = new Set(d.instances.map((i) => i.id));
  while (ids.has(id)) id = base + "_" + n++;
  return id;
}
function locked(d: Scene, id: string) {
  const s = d.metadata.scene,
    o = s.objects[id];
  return !!(
    o?.locked ||
    s.layers[o?.layer || ""]?.locked ||
    s.groups[o?.group || ""]?.locked
  );
}
function references(d: Scene) {
  return d.instances.map((i) => i.id);
}
function descendants(d: Scene, seeds: Iterable<string>) {
  const result = new Set(seeds),
    ids = references(d);
  let changed = true;
  while (changed) {
    changed = false;
    for (const i of d.instances)
      if (
        !result.has(i.id) &&
        [i.parent, i.attach?.target]
          .filter((x): x is string => !!x)
          .some((p) => result.has(owner(p, ids)))
      ) {
        result.add(i.id);
        changed = true;
      }
  }
  return result;
}
function rewrite(
  path: string | undefined,
  map: Record<string, string>,
  ids: string[],
) {
  if (!path) return path;
  const p = owner(path, ids);
  return map[p] ? map[p] + path.slice(p.length) : path;
}
function selection(d: Scene, c: SceneCommand) {
  const ids = [...new Set(c.ids || [c.id!])];
  if (!ids.length || ids.some((id) => !d.metadata.scene.objects[id]))
    bad("请选择存在的场景对象");
  return ids;
}
function editable(d: Scene, ids: string[], { transform = false } = {}) {
  for (const id of ids) {
    if (locked(d, id)) bad("对象或所属图层 / 选择组已锁定：" + id);
    const i = d.instances.find((x) => x.id === id)!;
    if (transform && i!.attach) bad("连接约束对象不可直接变换：" + id);
  }
}
function validateRef(ref: string | undefined, catalog?: Catalog) {
  const def = catalog?.[ref || ""];
  if (!def) bad("新增引用不存在");
  if (def.metadata?.level === 4 || def.metadata?.scene)
    bad("请插入 L1–L3 资产，避免场景递归");
  return def;
}
function apply(
  source: unknown,
  command: SceneCommand,
  catalog?: Catalog,
): Scene {
  let d = normalize(source, catalog);
  guard(command);
  const c = clone(command);
  if (!object(c)) bad("无效指令");
  if (c.type === "add" && c.id) {
    c.newId = c.newId || c.id;
    delete c.id;
  }
  if (c.type === "batch") {
    if (!Array.isArray(c.commands) || c.commands.length > 1000)
      bad("批量指令数量无效");
    for (const cmd of c.commands) {
      if (cmd.type === "batch") bad("不接受嵌套批量指令");
      d = apply(d, cmd, catalog);
    }
    return d;
  }
  const s = d.metadata.scene,
    ids = c.ids || c.id ? selection(d, c) : [],
    it = d.instances.find((i) => i.id === ids[0])!,
    o = it && s.objects[it.id];
  const modifies = [
    "transform",
    "transform-many",
    "rename",
    "remove",
    "remove-many",
    "visibility",
    "move-layer",
    "move-region",
    "params",
    "replace",
    "group",
    "ungroup",
    "reorder",
  ];
  if (
    [
      "transform",
      "transform-many",
      "rename",
      "visibility",
      "lock",
      "move-layer",
      "move-region",
      "params",
      "replace",
      "duplicate",
      "duplicate-many",
      "remove",
      "remove-many",
      "group",
      "ungroup",
      "reorder",
    ].includes(c.type) &&
    !ids.length
  )
    bad("请选择场景对象");
  if (modifies.includes(c.type))
    editable(d, ids, {
      transform: ["transform", "transform-many"].includes(c.type),
    });
  switch (c.type) {
    case "transform":
      for (const k of ["position", "rotation", "scale"] as const)
        if (c[k] !== undefined) it[k] = vector(c[k], k);
      break;
    case "transform-many": {
      const delta = c.delta ? vector(c.delta, "delta") : null;
      for (const id of ids) {
        const x = d.instances.find((i) => i.id === id)!;
        if (delta)
          x.position = vector(
            x.position.map((v, j) => v + delta[j]),
            "position",
          );
        const values = c.values?.[id];
        if (values)
          for (const k of ["position", "rotation", "scale"] as const)
            if (values[k] !== undefined) x[k] = vector(values[k], k);
      }
      break;
    }
    case "rename":
      o.label = String(c.label || it.id).slice(0, 128);
      break;
    case "rename-scene":
      s.title = String(c.title || d.id).slice(0, 128);
      d.name = s.title;
      break;
    case "visibility":
      for (const id of ids) s.objects[id].hidden = !c.visible;
      break;
    case "lock":
      for (const id of ids) s.objects[id].locked = !!c.locked;
      break;
    case "move-layer":
      if (!s.layers[c.layer]) bad("图层不存在");
      if (s.layers[c.layer].locked) bad("目标图层已锁定");
      for (const id of ids) s.objects[id].layer = c.layer;
      break;
    case "move-region":
      if (!s.regions[c.region]) bad("分区不存在");
      for (const id of ids) s.objects[id].region = c.region;
      break;
    case "params":
      if (c.style !== undefined) {
        if (c.style && !["lowpoly", "toon", "voxel"].includes(c.style))
          bad("不支持的对象风格");
        if (c.style) it.style = c.style;
        else delete it.style;
      }
      if (c.params) {
        guard(c.params);
        it.params = { ...it.params, ...c.params };
      }
      break;
    case "replace": {
      const def = validateRef(c.ref, catalog);
      if (it.attach || descendants(d, [it.id]).size > 1)
        bad("此对象包含连接依赖，请先调整连接关系再替换");
      delete it.part;
      delete it.assembly;
      delete it.params;
      delete it.pivot;
      it[def.instances ? "assembly" : "part"] = c.ref;
      if (c.rename !== false) o.label = def.name || c.ref;
      break;
    }
    case "duplicate":
    case "duplicate-many": {
      let targets = ids;
      if (c.withChildren !== false) targets = [...descendants(d, ids)];
      const oldIds = references(d),
        map: Record<string, string> = {},
        items = targets.map((id) => d.instances.find((i) => i.id === id)!);
      for (const x of items) {
        const id = nextId(d, x.id + "_copy");
        map[x.id] = id;
        d.instances.push({ ...clone(x), id });
      }
      const offset = c.offset ? vector(c.offset, "position") : [0.5, 0, 0.5];
      for (const x of items) {
        const copy = d.instances.find((i) => i.id === map[x.id])!;
        if (copy.parent) copy.parent = rewrite(copy.parent, map, oldIds);
        if (copy.attach)
          copy.attach.target = rewrite(copy.attach.target, map, oldIds)!;
        const parent = owner(x.parent || x.attach?.target || "root", oldIds);
        if (!map[parent] && !copy.attach)
          copy.position = vector(
            copy.position.map((v, j) => v + offset[j]),
            "position",
          );
        s.objects[copy.id] = {
          ...clone(s.objects[x.id]),
          label: s.objects[x.id].label + " 副本",
          locked: false,
        };
        delete s.objects[copy.id].group;
      }
      break;
    }
    case "remove":
    case "remove-many": {
      const removed = descendants(d, ids);
      editable(d, [...removed]);
      d.instances = d.instances.filter((x) => !removed.has(x.id));
      for (const id of removed) delete s.objects[id];
      break;
    }
    case "add": {
      const def = validateRef(c.ref, catalog),
        id = nextId(d, c.newId || c.objectId || "object");
      const layer =
        c.layer || Object.keys(s.layers).find((id) => !s.layers[id].locked);
      if (!layer || !s.layers[layer]) bad("没有可用的图层");
      if (s.layers[layer]?.locked) bad("目标图层已锁定");
      const x: SceneInstance = {
        id,
        position: c.position || [0, 0, 0],
        rotation: c.rotation || [0, 0, 0],
        scale: c.scale || [1, 1, 1],
      };
      x[def.instances ? "assembly" : "part"] = c.ref;
      if (
        def.metadata?.parameter_schema?.properties?.detail?.type === "boolean"
      )
        x.params = { detail: false };
      d.instances.push(x);
      s.objects[id] = {
        label: def.name || c.ref,
        layer,
        region: c.region || Object.keys(s.regions)[0],
        locked: false,
        hidden: false,
      };
      break;
    }
    case "paste": {
      if (
        !Array.isArray(c.instances) ||
        !object(c.objects) ||
        c.instances.length > 250
      )
        bad("无效的粘贴数据");
      const oldIds = c.instances.map((x) => x.id),
        map: Record<string, string> = {};
      for (const original of c.instances) {
        validateRef(original.assembly || original.part, catalog);
        const x = clone(original);
        x.id = nextId(d, original.id + "_paste");
        map[original.id] = x.id;
        d.instances.push(x);
      }
      for (const original of c.instances) {
        const x = d.instances.find((i) => i.id === map[original.id])!;
        x.parent = rewrite(x.parent, map, oldIds);
        if (!x.parent) delete x.parent;
        if (x.attach) x.attach.target = rewrite(x.attach.target, map, oldIds)!;
        if (!x.parent && !x.attach)
          x.position = (x.position || [0, 0, 0]).map(
            (v, j) => v + (c.offset || [0.5, 0, 0.5])[j],
          );
        const originalMeta = c.objects[original.id] || {};
        s.objects[x.id] = {
          label: originalMeta.label || original.id,
          layer: s.layers[originalMeta.layer]
            ? originalMeta.layer
            : Object.keys(s.layers)[0],
          region: s.regions[originalMeta.region]
            ? originalMeta.region
            : Object.keys(s.regions)[0],
          locked: false,
          hidden: !!originalMeta.hidden,
        };
      }
      break;
    }
    case "layer-visibility":
      if (!s.layers[c.layer]) bad("图层不存在");
      s.layers[c.layer].visible = !!c.visible;
      break;
    case "layer-lock":
      if (!s.layers[c.layer]) bad("图层不存在");
      s.layers[c.layer].locked = !!c.locked;
      break;
    case "add-layer":
      if (!safe(c.layer) || s.layers[c.layer]) bad("图层 ID 无效或已存在");
      s.layers[c.layer] = {
        label: String(c.label || c.layer).slice(0, 128),
        visible: true,
        locked: false,
      };
      break;
    case "rename-layer":
      if (!s.layers[c.layer]) bad("图层不存在");
      s.layers[c.layer].label = String(c.label || c.layer).slice(0, 128);
      break;
    case "remove-layer":
      if (!s.layers[c.layer] || !s.layers[c.target] || c.layer === c.target)
        bad("选择一个不同的目标图层");
      if (s.layers[c.layer].locked || s.layers[c.target].locked)
        bad("图层已锁定");
      for (const meta of Object.values(s.objects))
        if (meta.layer === c.layer) meta.layer = c.target;
      delete s.layers[c.layer];
      break;
    case "add-region":
      if (!safe(c.region) || s.regions[c.region]) bad("分区 ID 无效或已存在");
      s.regions[c.region] = {
        label: String(c.label || c.region).slice(0, 128),
      };
      break;
    case "group": {
      const id =
        c.group ||
        nextId(
          { instances: Object.keys(s.groups).map((id) => ({ id })) },
          "group",
        );
      if (!safe(id)) bad("无效选择组 ID");
      s.groups[id] = s.groups[id] || {
        label: String(c.label || "选择组").slice(0, 128),
        hidden: false,
        locked: false,
      };
      if (s.groups[id].locked) bad("选择组已锁定");
      for (const id2 of ids) s.objects[id2].group = id;
      break;
    }
    case "ungroup":
      for (const id of ids) delete s.objects[id].group;
      break;
    case "group-visibility":
      if (!s.groups[c.group]) bad("选择组不存在");
      s.groups[c.group].hidden = !c.visible;
      break;
    case "group-lock":
      if (!s.groups[c.group]) bad("选择组不存在");
      s.groups[c.group].locked = !!c.locked;
      break;
    case "rename-group":
      if (!s.groups[c.group]) bad("选择组不存在");
      s.groups[c.group].label = String(c.label || c.group).slice(0, 128);
      break;
    case "reorder": {
      const chosen = d.instances.filter((i) => ids.includes(i.id)),
        rest = d.instances.filter((i) => !ids.includes(i.id));
      const index = c.before
        ? rest.findIndex((i) => i.id === c.before)
        : rest.length;
      if (index < 0) bad("插入位置不存在");
      rest.splice(index, 0, ...chosen);
      d.instances = rest;
      break;
    }
    default:
      bad("未知编辑指令");
  }
  return normalize(d, catalog);
}
function subset(source: unknown, query: SceneQuery, catalog?: Catalog) {
  const d = normalize(source, catalog),
    s = d.metadata.scene;
  const ids = new Set(
    d.instances
      .filter(
        (i) =>
          i.enabled !== false &&
          (query.ids?.includes(i.id) ||
            (query.layer && s.objects[i.id].layer === query.layer) ||
            (query.region && s.objects[i.id].region === query.region)),
      )
      .map((i) => i.id),
  );
  if (!ids.size) bad("没有可导出的可见对象");
  const by = new Map(d.instances.map((i) => [i.id, i])),
    all = references(d);
  for (const id of ids) {
    const i = by.get(id)!;
    for (const dep of [i.parent, i.attach?.target].filter(
      (x): x is string => !!x,
    )) {
      const p = owner(dep, all);
      if (p !== "root") ids.add(p);
    }
  }
  d.instances = d.instances.filter((i) => ids.has(i.id));
  // A selected export owns only its retained objects and their required ancestors.
  // Inherited controls for excluded furniture/vehicles must not target missing nodes.
  if (Array.isArray(d.metadata.state_controls))
    d.metadata.state_controls = d.metadata.state_controls.filter(
      (c) =>
        c.node === "root" ||
        (typeof c.node === "string" && ids.has(owner(c.node, all))),
    );
  d.id = d.id.slice(0, 70) + "-selection";
  d.name = (d.name || d.id) + " · 子集";
  s.export_selection = {
    requested: query,
    included: [...ids],
    ancestors_included: true,
  };
  return normalize(d, catalog);
}
// Old scene clients passed add.id as the desired new ID, not an existing selection.
const compatibilityApply = (
  source: unknown,
  c: SceneCommand,
  catalog?: Catalog,
) => {
  if (c?.type === "add" && c.id) {
    const v = { ...c, newId: c.id };
    delete v.id;
    return apply(source, v, catalog);
  }
  return apply(source, c, catalog);
};
const api = {
  normalize,
  apply: compatibilityApply,
  subset,
  nextId,
  owner,
  descendants,
  locked,
  vector,
  version: "3.5.0",
};
export {
  normalize,
  compatibilityApply as apply,
  subset,
  nextId,
  owner,
  descendants,
  locked,
  vector,
};
export default api;
