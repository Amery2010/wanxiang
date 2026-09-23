/* Wanxiang Studio 3.5 — pure information architecture, search and local preferences.
 * No network, no catalogue mutation, no synthetic assets. Shared with Node tests. */
import type { RuntimeAsset } from "./types.js";
export interface Preferences {
  favorites: string[];
  recent: string[];
  view: string;
  theme: string;
  sort: string;
  leftWidth: number;
  rightWidth: number;
  snap: boolean;
  snapMove: number;
  snapRotate: number;
  snapScale: number;
}
export interface CatalogFilter {
  level?: string | number;
  domain?: string;
  theme?: string;
  collection?: string;
  gameKit?: string;
  query?: string;
  motion?: string;
  lod?: string;
  sort?: string;
}

const domains = [
  ["architecture", "建筑与结构", "building", "architecture arch buildings"],
  ["interior", "室内与家具", "sofa", "interior"],
  ["nature", "自然与植被", "leaf", "nature"],
  ["terrain", "地形与道路", "mountain", "terrain roads"],
  ["props", "道具与陈设", "package", "props camp"],
  ["vehicle", "车辆与交通", "truck", "vehicle vessel"],
  ["industry", "工业与机械", "gear", "mechanism mech machines"],
  ["character", "角色与穿戴", "person", "wear body people gear"],
  ["creature", "动物与生态", "paw", "animal bird aquatic insect fauna"],
  ["robot", "机器人与无人机", "robot", "robot"],
  ["gameplay", "交互与机关", "gamepad", "gameplay"],
  ["scene", "场景与环境", "layers", "scene"],
].map(([id, label, icon, aliases]) => ({
  id,
  label,
  icon,
  aliases: aliases.split(" "),
}));
const byCategory = Object.fromEntries(
  domains.flatMap((d) => d.aliases.map((c) => [c, d.id])),
);
const themes = {
  urban: "城镇与公共空间",
  heritage: "传统建筑",
  interior: "室内生活",
  factory: "工业与工程",
  farm: "农场与乡村",
  harbor: "港口与海岸",
  transit: "交通枢纽",
  wildland: "自然野外",
  science: "研究与前哨",
  scifi: "科幻空间",
  dungeon: "遗迹与机关",
  community: "社区与生活",
};
const sceneThemes: Record<string, string> = {
  city: "urban",
  public: "urban",
  medieval: "heritage",
  castle: "heritage",
  home: "interior",
  industrial: "factory",
  construction: "factory",
  depot: "factory",
  farm: "farm",
  harbor: "harbor",
  rail: "transit",
  airport: "transit",
  transport: "transit",
  forest: "wildland",
  desert: "wildland",
  snow: "wildland",
  swamp: "wildland",
  mountain: "wildland",
  cave: "wildland",
  wildlife: "wildland",
  outpost: "science",
  camp: "wildland",
  space: "scifi",
  cyber: "scifi",
  dungeon: "dungeon",
  adventure: "dungeon",
};
const levels = {
  1: { label: "基础部件", long: "L1 语义基础部件" },
  2: { label: "功能装配", long: "L2 功能子装配" },
  3: { label: "完整资产", long: "L3 完整生产资产" },
  4: { label: "可编辑场景", long: "L4 可编辑场景" },
};
const synonyms = [
  ["树", "tree", "forest", "植物"],
  ["猫", "cat"],
  ["狗", "dog"],
  ["汽车", "车", "vehicle", "car"],
  ["沙发", "sofa", "seat"],
  ["机器人", "robot"],
  ["房屋", "建筑", "building", "cottage", "house"],
  ["桌子", "桌", "table", "desk"],
  ["椅子", "椅", "chair"],
  ["花", "flower"],
  ["门", "door"],
  ["灯", "lamp", "light"],
  ["船", "boat", "ship", "vessel"],
  ["轮", "wheel"],
  ["地形", "terrain"],
  ["窗", "window"],
  ["床", "bed"],
  ["室内", "interior"],
  ["机甲", "robot"],
  ["人物", "角色", "character", "body"],
];
function domain(a: RuntimeAsset) {
  return (
    byCategory[a.game_category || a.category?.replace(/^part_/, "") || ""] ||
    (a.level === 4 ? "scene" : "props")
  );
}
function sceneTheme(a: RuntimeAsset) {
  return a.theme?.startsWith("l4-")
    ? a.theme.slice(3)
    : sceneThemes[a.theme || ""] || "community";
}
function text(a: RuntimeAsset) {
  return [
    a.id,
    a.name,
    a.game_category,
    a.theme,
    domains.find((d) => d.id === domain(a))?.label,
    ...(a.tags || []),
    ...(a.runtime?.tags || []),
  ]
    .join(" ")
    .normalize("NFKC")
    .toLowerCase();
}
function match(a: RuntimeAsset, q: unknown) {
  const words = String(q || "")
    .normalize("NFKC")
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);
  if (!words.length) return true;
  const t = text(a);
  return words.every(
    (w) =>
      t.includes(w) ||
      synonyms.some((g) => g.includes(w) && g.some((v) => t.includes(v))),
  );
}
function filter(
  assets: RuntimeAsset[],
  f: CatalogFilter = {},
  prefs: Partial<Preferences> = {},
) {
  const fav = new Set(prefs.favorites || []),
    recent = prefs.recent || [];
  const a = assets.filter(
    (a) =>
      (!f.level || f.level === "all" || a.level === Number(f.level)) &&
      (!f.domain || f.domain === "all" || domain(a) === f.domain) &&
      (!f.theme || f.theme === "all" || sceneTheme(a) === f.theme) &&
      (!f.collection ||
        f.collection === "all" ||
        (f.collection === "favorites" && fav.has(a.id)) ||
        (f.collection === "recent" && recent.includes(a.id)) ||
        (f.collection === "custom" && a.local === true) ||
        (f.collection === "game410" && a.game_expansion === true)) &&
      (!f.gameKit ||
        f.gameKit === "all" ||
        f.collection !== "game410" ||
        a.game_kit === f.gameKit) &&
      match(a, f.query) &&
      (!f.motion ||
        f.motion === "all" ||
        (f.motion === "moving" &&
          a.runtime?.motion !== "static" &&
          !!a.runtime?.motion) ||
        a.runtime?.motion === f.motion) &&
      (!f.lod ||
        !["yes", "no"].includes(f.lod) ||
        Boolean(a.runtime?.lod) === (f.lod === "yes")),
  );
  const sort = f.sort || "recommended";
  if (sort === "name")
    a.sort((a, b) => a.name!.localeCompare(b.name!, "zh-CN"));
  if (sort === "triangles")
    a.sort(
      (a, b) =>
        (a.report?.triangles || Infinity) - (b.report?.triangles || Infinity),
    );
  if (sort === "level")
    a.sort(
      (a, b) => b.level! - a.level! || a.name!.localeCompare(b.name!, "zh-CN"),
    );
  if (sort === "recent" || f.collection === "recent")
    a.sort(
      (a, b) =>
        (recent.indexOf(a.id) < 0 ? Infinity : recent.indexOf(a.id)) -
        (recent.indexOf(b.id) < 0 ? Infinity : recent.indexOf(b.id)),
    );
  return a;
}
function counts(assets: RuntimeAsset[]) {
  return {
    total: assets.length,
    levels: Object.fromEntries(
      Object.keys(levels).map((l) => [
        l,
        assets.filter((a) => a.level === Number(l)).length,
      ]),
    ),
    domains: Object.fromEntries(
      domains.map((d) => [
        d.id,
        assets.filter((a) => domain(a) === d.id).length,
      ]),
    ),
  };
}
const defaultPrefs: Preferences = {
  favorites: [],
  recent: [],
  view: "grid",
  theme: "light",
  sort: "recommended",
  leftWidth: 224,
  rightWidth: 360,
  snap: true,
  snapMove: 0.25,
  snapRotate: 15,
  snapScale: 0.1,
};
const cleanPrefs = (input: unknown): Preferences => {
  const p: Record<string, unknown> =
    input && typeof input === "object" && !Array.isArray(input)
      ? (input as Record<string, unknown>)
      : {};
  const number = (
    k: "leftWidth" | "rightWidth" | "snapMove" | "snapRotate" | "snapScale",
    min: number,
    max: number,
  ) =>
    typeof p[k] === "number" && Number.isFinite(p[k])
      ? Math.max(min, Math.min(max, p[k]))
      : defaultPrefs[k];
  return {
    ...defaultPrefs,
    theme:
      typeof p.theme === "string" && ["light", "dark"].includes(p.theme)
        ? p.theme
        : "light",
    view:
      typeof p.view === "string" && ["grid", "list"].includes(p.view)
        ? p.view
        : "grid",
    sort:
      typeof p.sort === "string" &&
      ["recommended", "name", "triangles", "level", "recent"].includes(p.sort)
        ? p.sort
        : "recommended",
    favorites: [
      ...new Set(
        Array.isArray(p.favorites)
          ? p.favorites.filter((x) => typeof x === "string")
          : [],
      ),
    ].slice(0, 10000),
    recent: [
      ...new Set(
        Array.isArray(p.recent)
          ? p.recent.filter((x) => typeof x === "string")
          : [],
      ),
    ].slice(0, 60),
    leftWidth: number("leftWidth", 180, 360),
    rightWidth: number("rightWidth", 270, 470),
    snap: typeof p.snap === "boolean" ? p.snap : true,
    snapMove: number("snapMove", 0.001, 100),
    snapRotate: number("snapRotate", 0.1, 180),
    snapScale: number("snapScale", 0.001, 10),
  };
};

function storage<T>(key: string, fallback: T): T {
  try {
    const value = JSON.parse(globalThis.localStorage?.getItem(key) || "null");
    return value ?? fallback;
  } catch {
    return fallback;
  }
}
function save(key: string, value: unknown) {
  try {
    if (!globalThis.localStorage) return false;
    globalThis.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}
const icons: Record<string, string> = {
  group:
    '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><path d="M14 3h7v7M3 14v7h7M10 6h4M6 10v4M14 18h-4M18 14v-4"/>',
  align: '<path d="M3 21h18M7 3v14h4V3ZM15 8v9h4V8Z"/>',
  ground: '<path d="M3 21h18M5 5h14v10H5ZM12 15v5m-3-3 3 3 3-3"/>',
  link: '<path d="m9 15 6-6M8 17l-1 1a4 4 0 0 1-6-6l5-5a4 4 0 0 1 6 0m4 0 1-1a4 4 0 0 1 6 6l-5 5a4 4 0 0 1-6 0" transform="translate(0 0) scale(.95)"/>',
  unlink:
    '<path d="m3 3 18 18M6 10l-3 3a4 4 0 0 0 6 6l3-3M14 5l1-1a4 4 0 1 1 6 6l-2 2M10 3v2M3 10h2M19 14h2M14 19v2"/>',
  refresh:
    '<path d="M20 10a8 8 0 0 0-14-5L3 8m0-5v5h5M4 14a8 8 0 0 0 14 5l3-3m0 5v-5h-5"/>',

  cube: '<path d="m12 3 9 5v8l-9 5-9-5V8Z M3 8l9 5 9-5M12 13v8"/>',
  layers: '<path d="m12 3 10 5-10 5L2 8ZM2 12l10 5 10-5M2 16l10 5 10-5"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  star: '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
  down: '<path d="m5 9 7 7 7-7"/>',
  building: '<path d="m3 10 9-7 9 7M5 9v12h14V9M10 21v-7h4v7"/>',
  sofa: '<path d="M5 12V7a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v5M5 10H3v9h18v-9h-2v5H5ZM5 19v2m14-2v2"/>',
  leaf: '<path d="M20 3C8 2 2 10 6 17c7 6 15-2 14-14ZM4 21l12-13"/>',
  mountain: '<path d="m2 19 7-13 5 8 3-5 5 10ZM7 10l2 2 2-2"/>',
  package:
    '<path d="m12 3 9 5v9l-9 5-9-5V8Z M3 8l9 5 9-5M12 13v9M7.5 5.5l9 5V16"/>',
  truck:
    '<path d="M3 5h11v12H3ZM14 9h4l3 4v4h-7"/><circle cx="7" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
  gear: '<path d="m9 3 6 0 1 3 3 1 2 5-3 3v4l-5 2-3-2-4-1-2-5 2-3V6Z"/><circle cx="12" cy="12" r="3"/>',
  person:
    '<circle cx="12" cy="5" r="3"/><path d="M5 21v-3a7 7 0 0 1 14 0v3M7 12l-3 4m13-4 3 4"/>',
  paw: '<ellipse cx="12" cy="15" rx="6" ry="5"/><ellipse cx="5" cy="8" rx="2" ry="3"/><ellipse cx="10" cy="5" rx="2" ry="3"/><ellipse cx="16" cy="5" rx="2" ry="3"/><ellipse cx="20" cy="10" rx="2" ry="3"/>',
  robot:
    '<rect x="5" y="7" width="14" height="13" rx="3"/><path d="M12 3v4M3 11v5m18-5v5M9 15h6M9 11h.1M15 11h.1"/>',
  gamepad:
    '<path d="M7 6h10c4 0 7 13 3 13-2 0-3-4-5-4H9c-2 0-3 4-5 4C0 19 3 6 7 6Z M6 9v5m-2-2.5h4M16 10h.1M18 13h.1"/>',
  eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  eyeOff: '<path d="m3 3 18 18M8 5c7-3 14 7 14 7l-3 4M5 7l-3 5s5 9 13 6"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4M12 14v3"/>',
  unlock:
    '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V6a4 4 0 0 1 7-2M12 14v3"/>',
  trash: '<path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7"/>',
  copy: '<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M5 16H3V3h13v2"/>',
  undo: '<path d="M4 4v6h6M4 10c6-9 16-5 16 3 0 6-6 8-10 7"/>',
  redo: '<path d="M20 4v6h-6M20 10C14 1 4 5 4 13c0 6 6 8 10 7"/>',
  move: '<path d="M12 2v20M2 12h20M9 5l3-3 3 3M9 19l3 3 3-3M5 9l-3 3 3 3M19 9l3 3-3 3"/>',
  rotate: '<path d="M20 4v6h-6M20 10a9 9 0 1 0 1 6"/>',
  scale: '<path d="M14 3h7v7M21 3l-9 9M9 3H3v18h18v-6"/>',
  cursor: '<path d="M5 3v17l5-5 4 7 3-2-4-7h7Z"/>',
  magnet:
    '<path d="M5 4v10a7 7 0 0 0 14 0V4h-4v10a3 3 0 0 1-6 0V4ZM5 9h4M15 9h4"/>',
  focus:
    '<path d="M8 3H3v5M16 3h5v5M3 16v5h5M21 16v5h-5"/><circle cx="12" cy="12" r="3"/>',
  folder: '<path d="M3 7V4h7l3 3h8v13H3Z"/>',
  save: '<path d="M4 3h13l4 4v14H3V3ZM7 3v6h10V3M7 21v-8h10v8"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 15v6h16v-6"/>',
  upload: '<path d="M12 16V3m-5 5 5-5 5 5M4 15v6h16v-6"/>',
  list: '<path d="M9 5h12M9 12h12M9 19h12M3 5h1m-1 7h1m-1 7h1"/>',
  filter: '<path d="M3 5h18M6 12h12M10 19h4"/>',
  expand: '<path d="M3 9V3h6m6 0h6v6M3 15v6h6m6 0h6v-6"/>',
  panel:
    '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M15 3v18"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 1 1 4 3c-1 0-1 1-1 2M12 17h.1"/>',
  moon: '<path d="M21 13a9 9 0 1 1-10-10 7 7 0 0 0 10 10Z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 1v2m0 18v2M1 12h2m18 0h2M4 4l2 2m12 12 2 2M4 20l2-2M18 6l2-2"/>',
  palette:
    '<path d="M12 3a9 9 0 1 0 0 18c3 0 0-4 3-4h3c5 0 4-14-6-14Z"/><path d="M7 9h.1M11 6h.1M16 8h.1M6 14h.1"/>',
  command:
    '<path d="M8 8H5a3 3 0 1 1 3-3v14a3 3 0 1 1-3-3h14a3 3 0 1 1-3 3V5a3 3 0 1 1 3 3Z"/>',
  more: '<circle cx="4" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="20" cy="12" r="1"/>',
};
const icon = (key: string, cls = "") =>
  `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${icons[key] || icons.cube}</svg>`;
const esc = (x: unknown) =>
  String(x ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ]!,
  );
const api = {
  version: "3.5.0",
  domains,
  themes,
  levels,
  domain,
  sceneTheme,
  match,
  filter,
  counts,
  defaultPrefs,
  cleanPrefs,
  storage,
  save,
  icon,
  esc,
};
export {
  domains,
  themes,
  levels,
  domain,
  sceneTheme,
  match,
  filter,
  counts,
  defaultPrefs,
  cleanPrefs,
  storage,
  save,
  icon,
  esc,
};
export default api;
