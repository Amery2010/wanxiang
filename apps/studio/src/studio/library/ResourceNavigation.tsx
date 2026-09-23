import { useMemo } from "react";
import { useStore } from "zustand";
import { Button } from "../../ui/button";
import type { LucideIcon } from "lucide-react";
import {
  Box,
  Bot,
  Building2,
  Clock3,
  Cog,
  Folder,
  Gamepad2,
  Grid2X2,
  Layers,
  Leaf,
  ListChecks,
  Mountain,
  Package,
  Palette,
  PawPrint,
  Plus,
  Settings2,
  Shapes,
  Sofa,
  Sparkles,
  Star,
  Truck,
  UserRound,
} from "lucide-react";
import type { Asset } from "../types";
import type { NavigationProps } from "./types";
import { dataAssets, dataMaterials } from "./types";
import {
  countAssets,
  domainIcon,
  formatCount,
  getStudioCore,
  levelMap,
} from "./utils";

const iconMap: Record<string, LucideIcon> = {
  building: Building2,
  sofa: Sofa,
  leaf: Leaf,
  mountain: Mountain,
  package: Package,
  truck: Truck,
  settings: Cog,
  user: UserRound,
  "paw-print": PawPrint,
  bot: Bot,
  "gamepad-2": Gamepad2,
  "layers-3": Layers,
};

export function ResourceNavigation({
  store,
  onNewScene,
  onShowTasks,
  onShowCache,
}: NavigationProps) {
  const data = useStore(store, (state) => state.data);
  const filters = useStore(store, (state) => state.filters);
  const prefs = useStore(store, (state) => state.prefs);
  const assets = useMemo(() => dataAssets(data), [data]);
  const materials = useMemo(() => dataMaterials(data), [data]);
  const counts = useMemo(() => {
    const base = assets.filter(
      (asset) =>
        filters.level === "all" ||
        !filters.level ||
        asset.level === Number(filters.level),
    );
    return countAssets(base);
  }, [assets, filters.level]);
  const levelCounts = useMemo(() => countAssets(assets), [assets]);
  const domains = getStudioCore()?.domains ?? [];
  const levels = levelMap();

  const choose = (patch: Partial<typeof filters>) => {
    store.getState().setFilters({ ...patch, page: 1 });
  };

  return (
    <aside className="library-navigation" aria-label="资源导航">
      <div className="library-navigation__header">
        <div>
          <span className="library-overline">资源导航</span>
          <strong>Wanxiang Studio</strong>
        </div>
        <span className="library-local-badge">LOCAL</span>
      </div>

      <div className="library-navigation__scroll">
        <section
          className="library-navigation__section"
          aria-labelledby="workspace-nav-heading"
        >
          <h2 id="workspace-nav-heading">我的工作空间</h2>
          <NavItem
            active={
              filters.collection === "all" && filters.workspace === "library"
            }
            icon={Grid2X2}
            label="全部资源"
            count={assets.length}
            onClick={() =>
              choose({
                workspace: "library",
                collection: "all",
                gameKit: "all",
                domain: "all",
                theme: "all",
                level: "3",
              })
            }
          />
          <NavItem
            collection="favorites"
            active={filters.collection === "favorites"}
            icon={Star}
            label="我的收藏"
            count={prefs.favorites.length}
            onClick={() =>
              choose({
                workspace: "library",
                collection: "favorites",
                gameKit: "all",
                level: "all",
                domain: "all",
                theme: "all",
              })
            }
          />
          <NavItem
            collection="recent"
            active={filters.collection === "recent"}
            icon={Clock3}
            label="最近使用"
            count={prefs.recent.length}
            onClick={() =>
              choose({
                workspace: "library",
                collection: "recent",
                gameKit: "all",
                level: "all",
                domain: "all",
                theme: "all",
              })
            }
          />
          <NavItem
            collection="materials"
            active={filters.collection === "materials"}
            icon={Palette}
            label="材质库"
            count={materials.length}
            onClick={() =>
              choose({
                workspace: "library",
                collection: "materials",
                level: "all",
                domain: "all",
                theme: "all",
                query: "",
              })
            }
          />
        </section>

        <section
          className="library-navigation__section"
          aria-labelledby="taxonomy-heading"
        >
          <h2 id="taxonomy-heading">
            {filters.level === "4" ? "场景主题" : "按用途分类"}
          </h2>
          <NavItem
            active={filters.domain === "all" && filters.theme === "all"}
            icon={filters.level === "4" ? Layers : Shapes}
            label={filters.level === "4" ? "全部场景" : "所有领域"}
            count={counts.total}
            onClick={() => choose({ domain: "all", theme: "all" })}
          />
          {filters.level === "4"
            ? Object.entries(getStudioCore()?.themes ?? {}).map(
                ([id, label]) => (
                  <NavItem
                    key={id}
                    active={filters.theme === id}
                    icon={Folder}
                    label={label}
                    count={
                      assets.filter((asset) => sceneTheme(asset) === id).length
                    }
                    onClick={() => choose({ theme: id, domain: "all" })}
                  />
                ),
              )
            : domains.map((domain) => {
                const count = counts.domains[domain.id] ?? 0;
                if (!count) return null;
                return (
                  <NavItem
                    key={domain.id}
                    active={filters.domain === domain.id}
                    icon={iconMap[domainIcon(domain.id)] ?? Box}
                    label={domain.label}
                    count={count}
                    onClick={() => choose({ domain: domain.id, theme: "all" })}
                  />
                );
              })}
        </section>

        <section
          className="library-navigation__section library-navigation__levels"
          aria-labelledby="levels-heading"
        >
          <h2 id="levels-heading">资产层级</h2>
          <div className="library-level-stack">
            <LevelButton
              active={filters.level === "all"}
              label="全部"
              count={levelCounts.total}
              onClick={() =>
                choose({ level: "all", domain: "all", theme: "all" })
              }
            />
            {Object.entries(levels).map(([id, level]) => (
              <LevelButton
                key={id}
                active={filters.level === id}
                label={`L${id} ${level.label}`}
                count={levelCounts.levels[id] ?? 0}
                onClick={() =>
                  choose({ level: id, domain: "all", theme: "all" })
                }
              />
            ))}
          </div>
        </section>
      </div>

      <div className="library-navigation__footer">
        <div className="library-navigation__tip">
          <Sparkles size={15} aria-hidden="true" />
          <div>
            <strong>配置就是创作源</strong>
            <p>
              模型按需生成，保留部件来源。
              <br />
              不需要联网，也不预存 GLB。
            </p>
          </div>
        </div>
        <div className="library-navigation__actions">
          <Button
            type="button"
            className="library-button library-button--primary library-button--wide"
            onClick={onNewScene}
            disabled={!onNewScene}
          >
            <Plus size={15} aria-hidden="true" />
            新建场景
          </Button>
          <div className="library-navigation__quick-actions">
            <Button
              type="button"
              className="library-button library-button--quiet"
              onClick={onShowTasks}
              disabled={!onShowTasks}
            >
              <ListChecks size={15} aria-hidden="true" />
              任务
            </Button>
            <Button
              type="button"
              className="library-button library-button--quiet"
              onClick={onShowCache}
              disabled={!onShowCache}
            >
              <Settings2 size={15} aria-hidden="true" />
              缓存
            </Button>
            <Button
              type="button"
              className="library-button library-button--quiet"
              onClick={() =>
                choose({
                  workspace: "library",
                  collection: "all",
                  level: "all",
                  domain: "all",
                  theme: "all",
                  query: "",
                  gameKit: "all",
                  motion: "all",
                  lod: "all",
                  collision: "all",
                  budget: "all",
                  interface: "all",
                  tag: "",
                  compatibleIds: null,
                })
              }
            >
              <Palette size={15} aria-hidden="true" />
              重置
            </Button>
          </div>
        </div>
      </div>
    </aside>
  );
}

interface NavItemProps {
  collection?: string;
  active: boolean;
  icon: LucideIcon;
  label: string;
  count?: number;
  onClick(): void;
}

function NavItem({
  active,
  icon: Icon,
  label,
  count,
  onClick,
  collection,
}: NavItemProps) {
  return (
    <Button
      type="button"
      data-collection={collection}
      className={`library-nav-item${active ? " is-active" : ""}`}
      aria-current={active ? "page" : undefined}
      onClick={onClick}
    >
      <Icon size={16} strokeWidth={1.8} aria-hidden="true" />
      <span>{label}</span>
      {typeof count === "number" && <small>{formatCount(count)}</small>}
    </Button>
  );
}

function LevelButton({
  active,
  label,
  count,
  onClick,
}: {
  active: boolean;
  label: string;
  count: number;
  onClick(): void;
}) {
  return (
    <Button
      type="button"
      className={`library-level-button${active ? " is-active" : ""}`}
      aria-pressed={active}
      onClick={onClick}
    >
      <span>{label}</span>
      <small>{formatCount(count)}</small>
    </Button>
  );
}

function sceneTheme(asset: Asset): string {
  const theme = typeof asset.theme === "string" ? asset.theme : "";
  if (theme.startsWith("l4-")) return theme.slice(3);
  const activeCore = getStudioCore();
  const sceneThemes = (activeCore as CoreWithSceneTheme | null)?.sceneThemes;
  if (sceneThemes && typeof sceneThemes[theme] === "string")
    return sceneThemes[theme];
  return theme || "community";
}

interface CoreWithSceneTheme {
  sceneThemes?: Record<string, string>;
}
