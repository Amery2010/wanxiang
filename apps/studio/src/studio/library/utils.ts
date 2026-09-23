import type { createContracts } from "@wanxiang/runtime/modules/contracts";
import type { RuntimeData } from "../../runtime/types";
import {
  core,
  type Core,
  type Filters,
  type Preferences,
  type Spec,
} from "../types";
import type { LibraryAsset, MaterialRecord } from "./types";

const FALLBACK_LEVELS: Record<string, { label: string; long: string }> = {
  "1": { label: "基础部件", long: "L1 语义基础部件" },
  "2": { label: "功能装配", long: "L2 功能子装配" },
  "3": { label: "完整资产", long: "L3 完整生产资产" },
  "4": { label: "可编辑场景", long: "L4 可编辑场景" },
};

const DOMAIN_ICONS: Record<string, string> = {
  architecture: "building",
  interior: "sofa",
  nature: "leaf",
  terrain: "mountain",
  props: "package",
  vehicle: "truck",
  industry: "settings",
  character: "user",
  creature: "paw-print",
  robot: "bot",
  gameplay: "gamepad-2",
  scene: "layers-3",
};

export function getStudioCore(): Core | null {
  try {
    return core();
  } catch {
    return null;
  }
}

export function levelMap(): Record<string, { label: string; long: string }> {
  return getStudioCore()?.levels ?? FALLBACK_LEVELS;
}

export function coreThemes(): Record<string, string> {
  return getStudioCore()?.themes ?? {};
}

export function domainId(asset: LibraryAsset): string {
  const activeCore = getStudioCore();
  if (activeCore) return activeCore.domain(asset);
  return asset.level === 4 ? "scene" : "props";
}

export function domainIcon(id: string): string {
  return DOMAIN_ICONS[id] ?? "layers-3";
}

export function assetName(asset: LibraryAsset): string {
  return asset.name?.trim() || asset.id;
}

export function assetTriangles(asset: LibraryAsset): number | null {
  const triangles = asset.report?.triangles;
  return typeof triangles === "number" && Number.isFinite(triangles)
    ? triangles
    : null;
}

export function assetNodes(asset: LibraryAsset): number | null {
  const nodes = asset.report?.nodes;
  return typeof nodes === "number" && Number.isFinite(nodes) ? nodes : null;
}

export function assetMaterials(asset: LibraryAsset): number | null {
  const materials = asset.report?.materials;
  return typeof materials === "number" && Number.isFinite(materials)
    ? materials
    : null;
}

export function assetBytes(asset: LibraryAsset): number | null {
  return typeof asset.bytes === "number" && Number.isFinite(asset.bytes)
    ? asset.bytes
    : null;
}

export function formatCount(count: number): string {
  return new Intl.NumberFormat("zh-CN").format(count);
}

export function formatTriangles(count: number | null): string {
  if (count === null) return "按需生成";
  if (count >= 1000)
    return `${(count / 1000).toFixed(count >= 10000 ? 0 : 1)}k 三角面`;
  return `${count} 三角面`;
}

export function assetHero(asset: LibraryAsset): string | null {
  return typeof asset.hero === "string" && asset.hero.length > 0
    ? asset.hero
    : null;
}

export function isSceneAsset(asset: LibraryAsset): boolean {
  return asset.level === 4;
}

export function filterAssets(
  assets: LibraryAsset[],
  filters: Filters,
  prefs: Preferences,
): LibraryAsset[] {
  const activeCore = getStudioCore();
  const filtered = applyAdvancedFilters(
    activeCore
      ? (activeCore.filter([...assets], filters, prefs) as LibraryAsset[])
      : fallbackFilter(assets, filters, prefs),
    filters,
  );
  if (!activeCore) return filtered;
  if (
    filters.sort === "recommended" &&
    filters.domain === "all" &&
    filters.theme === "all" &&
    filters.collection === "all" &&
    !filters.query &&
    filters.level !== "4" &&
    !hasAdvancedFilters(filters)
  ) {
    return interleaveDomains(filtered, activeCore);
  }
  return filtered;
}

export function countAssets(assets: LibraryAsset[]) {
  const activeCore = getStudioCore();
  if (activeCore) return activeCore.counts(assets);
  const levels = Object.fromEntries(
    Object.keys(FALLBACK_LEVELS).map((level) => [
      level,
      assets.filter((asset) => asset.level === Number(level)).length,
    ]),
  );
  const domains = Object.fromEntries(
    [...new Set(assets.map(domainId))].map((domain) => [
      domain,
      assets.filter((asset) => domainId(asset) === domain).length,
    ]),
  );
  return { total: assets.length, levels, domains };
}

export function materialName(material: MaterialRecord): string {
  return material.name?.trim() || material.id;
}

export function materialPreview(material: MaterialRecord): string | null {
  return typeof material.preview === "string" && material.preview.length > 0
    ? material.preview
    : null;
}

export function readString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

export function readNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

export function readBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

export function taskRecords(value: unknown): Array<Record<string, unknown>> {
  if (!value || typeof value !== "object") return [];
  const record = value as Record<string, unknown>;
  const groups = ["active", "queued", "history"];
  return groups.flatMap((group) => {
    const entries = record[group];
    return Array.isArray(entries) ? entries.filter(isRecord) : [];
  });
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function fallbackFilter(
  assets: LibraryAsset[],
  filters: Filters,
  prefs: Preferences,
): LibraryAsset[] {
  const query = filters.query.trim().toLocaleLowerCase("zh-CN");
  const favorites = new Set(prefs.favorites);
  const recent = new Set(prefs.recent);
  const filtered = assets.filter((asset) => {
    const text = [
      asset.id,
      asset.name,
      asset.category,
      asset.game_category,
      asset.theme,
      ...(Array.isArray(asset.tags) ? asset.tags : []),
      ...(Array.isArray(asset.runtime?.tags) ? asset.runtime.tags : []),
    ]
      .filter((part): part is string => typeof part === "string")
      .join(" ")
      .toLocaleLowerCase("zh-CN");
    return (
      (!filters.level ||
        filters.level === "all" ||
        asset.level === Number(filters.level)) &&
      (!filters.collection ||
        filters.collection === "all" ||
        (filters.collection === "favorites" && favorites.has(asset.id)) ||
        (filters.collection === "recent" && recent.has(asset.id)) ||
        (filters.collection === "custom" && asset.local === true) ||
        (filters.collection === "game410" && asset.game_expansion === true)) &&
      (!filters.gameKit ||
        filters.gameKit === "all" ||
        (filters.collection === "game410" &&
          asset.game_kit === filters.gameKit)) &&
      (!filters.domain ||
        filters.domain === "all" ||
        domainId(asset) === filters.domain) &&
      (!filters.theme ||
        filters.theme === "all" ||
        asset.theme === filters.theme) &&
      (!filters.query || text.includes(query))
    );
  });
  return sortAssets(filtered, filters, prefs);
}

function applyAdvancedFilters(
  assets: LibraryAsset[],
  filters: Filters,
): LibraryAsset[] {
  const maxBudget = filters.budget === "all" ? null : Number(filters.budget);
  return assets.filter((asset) => {
    const runtime = asset.runtime;
    if (filters.motion !== "all") {
      const motion = typeof runtime?.motion === "string" ? runtime.motion : "";
      const isMoving = Boolean(motion && motion !== "static");
      if (filters.motion === "moving" ? !isMoving : motion !== filters.motion) {
        return false;
      }
    }
    if (filters.lod !== "all") {
      const hasLod =
        capabilityDefined(runtime?.lod) ||
        (Array.isArray(runtime?.lod_levels) && runtime.lod_levels.length > 0);
      if (hasLod !== (filters.lod === "yes")) return false;
    }
    if (
      filters.collision !== "all" &&
      capabilityDefined(runtime?.collision) !== (filters.collision === "yes")
    ) {
      return false;
    }
    if (maxBudget !== null) {
      const budget =
        typeof runtime?.budget === "number" && Number.isFinite(runtime.budget)
          ? runtime.budget
          : assetTriangles(asset);
      if (budget === null || budget > maxBudget) return false;
    }
    if (filters.interface !== "all") {
      const interfaces = Array.isArray(runtime?.interfaces)
        ? runtime.interfaces
        : [];
      if (!interfaces.includes(filters.interface)) return false;
    }
    if (filters.tag) {
      const needle = filters.tag.trim().toLocaleLowerCase("zh-CN");
      const tags = [
        ...(Array.isArray(asset.tags) ? asset.tags : []),
        ...(Array.isArray(runtime?.tags) ? runtime.tags : []),
      ].map((tag) => String(tag).toLocaleLowerCase("zh-CN"));
      if (!needle || !tags.some((tag) => tag.includes(needle))) return false;
    }
    if (
      filters.compatibleIds !== null &&
      !filters.compatibleIds.includes(asset.id)
    ) {
      return false;
    }
    return true;
  });
}

function hasAdvancedFilters(filters: Filters): boolean {
  return Boolean(
    filters.motion !== "all" ||
    filters.lod !== "all" ||
    filters.collision !== "all" ||
    filters.budget !== "all" ||
    filters.interface !== "all" ||
    filters.tag ||
    filters.compatibleIds !== null,
  );
}

function capabilityDefined(value: unknown): boolean {
  return Boolean(
    value === true ||
    (value && typeof value === "object" && Object.keys(value).length > 0),
  );
}

function sortAssets(
  assets: LibraryAsset[],
  filters: Filters,
  prefs: Preferences,
): LibraryAsset[] {
  const recent = prefs.recent;
  return [...assets].sort((a, b) => {
    if (filters.sort === "name") {
      return assetName(a).localeCompare(assetName(b), "zh-CN");
    }
    if (filters.sort === "triangles") {
      return (
        (assetTriangles(a) ?? Number.POSITIVE_INFINITY) -
        (assetTriangles(b) ?? Number.POSITIVE_INFINITY)
      );
    }
    if (filters.sort === "level") {
      return (
        (b.level ?? 0) - (a.level ?? 0) ||
        assetName(a).localeCompare(assetName(b), "zh-CN")
      );
    }
    if (filters.sort === "recent" || filters.collection === "recent") {
      return (
        (recent.indexOf(a.id) < 0
          ? Number.POSITIVE_INFINITY
          : recent.indexOf(a.id)) -
        (recent.indexOf(b.id) < 0
          ? Number.POSITIVE_INFINITY
          : recent.indexOf(b.id))
      );
    }
    return 0;
  });
}

function interleaveDomains(
  assets: LibraryAsset[],
  activeCore: Core,
): LibraryAsset[] {
  const groups = activeCore.domains.map((domain) =>
    assets.filter((asset) => activeCore.domain(asset) === domain.id),
  );
  const mixed: LibraryAsset[] = [];
  for (let index = 0; groups.some((group) => group[index]); index += 1) {
    for (const group of groups) {
      const asset = group[index];
      if (asset) mixed.push(asset);
    }
  }
  return mixed;
}

export function compareMetric(
  asset: LibraryAsset,
  key: "level" | "triangles" | "domain",
): string {
  if (key === "level") return asset.level ? `L${asset.level}` : "—";
  if (key === "triangles") return formatTriangles(assetTriangles(asset));
  return domainId(asset);
}

export function recordPreview(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

export function specLabel(spec: Spec): string {
  return readString(spec.name, readString(spec.id, "未命名"));
}

export function sessionContracts(data: RuntimeData) {
  const contracts = (
    globalThis as typeof globalThis & {
      WXContracts?: { createContracts: typeof createContracts };
    }
  ).WXContracts;
  return contracts?.createContracts(data.interfaces);
}

export function interfaceOptions(data: RuntimeData): string[] {
  const contracts = sessionContracts(data);
  return contracts ? Object.keys(contracts.registry()).sort() : [];
}

export function hasActiveFilters(filters: Filters): boolean {
  return Boolean(
    filters.query ||
    filters.level !== "all" ||
    filters.domain !== "all" ||
    filters.theme !== "all" ||
    filters.collection !== "all" ||
    filters.gameKit !== "all" ||
    filters.motion !== "all" ||
    filters.lod !== "all" ||
    filters.collision !== "all" ||
    filters.budget !== "all" ||
    filters.interface !== "all" ||
    filters.tag ||
    filters.compatibleIds !== null,
  );
}
