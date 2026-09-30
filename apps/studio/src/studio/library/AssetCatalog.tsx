import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
import { useStore } from "zustand";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import {
  ArrowDownUp,
  Check,
  ChevronLeft,
  ChevronRight,
  ChevronsUpDown,
  Filter,
  Grid2X2,
  Layers,
  List,
  Search,
  SlidersHorizontal,
  Star,
  X,
} from "lucide-react";
import type { Asset, Filters } from "../types";
import type { CatalogProps, LibraryAsset, MaterialRecord } from "./types";
import { dataAssets, dataMaterials } from "./types";
import { MaterialDialog } from "./MaterialDialog";
import {
  assetHero,
  assetName,
  assetTriangles,
  coreThemes,
  domainId,
  filterAssets,
  formatCount,
  formatTriangles,
  getStudioCore,
  hasActiveFilters,
  hasMaterialImage,
  interfaceOptions,
  levelMap,
  materialName,
  materialPreview,
} from "./utils";

export function AssetCatalog({
  store,
  onSelect,
  onNewScene,
  onBatchExport,
  onOpenScene,
  onOpenMaterial,
  onCompare,
}: CatalogProps) {
  const data = useStore(store, (state) => state.data);
  const filters = useStore(store, (state) => state.filters);
  const prefs = useStore(store, (state) => state.prefs);
  const current = useStore(store, (state) => state.current);
  const batch = useStore(store, (state) => state.batch);
  const notice = useStore(store, (state) => state.notice);
  const catalogRef = useRef<HTMLDivElement | null>(null);
  const [material, setMaterial] = useState<MaterialRecord | null>(null);
  const assets = useMemo(() => dataAssets(data), [data]);
  const materials = useMemo(() => dataMaterials(data), [data]);
  const materialMode = filters.collection === "materials";
  const filteredAssets = useMemo(
    () => filterAssets(assets, filters, prefs),
    [assets, filters, prefs],
  );
  const filteredMaterials = useMemo(
    () => filterMaterials(materials, filters.query),
    [materials, filters.query],
  );
  const total = materialMode ? filteredMaterials.length : filteredAssets.length;
  const pages = Math.max(1, Math.ceil(total / Math.max(1, filters.pageSize)));
  const page = Math.min(pages, Math.max(1, filters.page));
  const start = (page - 1) * filters.pageSize;
  const visibleAssets = filteredAssets.slice(start, start + filters.pageSize);
  const visibleMaterials = filteredMaterials.slice(
    start,
    start + filters.pageSize,
  );
  const selectedAssets = assets.filter((asset) => batch.includes(asset.id));
  const compareAssets = useMemo(() => {
    if (selectedAssets.length >= 2) return selectedAssets.slice(0, 4);
    const first = selectedAssets[0] ?? current ?? filteredAssets[0];
    const second = filteredAssets.find((asset) => asset.id !== first?.id);
    return [first, second].filter((asset): asset is LibraryAsset =>
      Boolean(asset),
    );
  }, [current, filteredAssets, selectedAssets]);
  const activeLevel =
    filters.level === "all"
      ? "全部层级"
      : (levelMap()[filters.level]?.long ?? "资产资源库");

  useEffect(() => {
    if (filters.page !== page) store.getState().setFilters({ page });
  }, [filters.page, page, store]);

  const setFilters = (patch: Partial<Filters>) =>
    store.getState().setFilters({ ...patch, page: patch.page ?? 1 });
  const toggleFavorite = (asset: LibraryAsset) => {
    const favorites = prefs.favorites.includes(asset.id)
      ? prefs.favorites.filter((id) => id !== asset.id)
      : [asset.id, ...prefs.favorites];
    store.getState().setPrefs({ favorites });
  };
  const toggleBatch = (asset: LibraryAsset) => {
    const next = batch.includes(asset.id)
      ? batch.filter((id) => id !== asset.id)
      : [...batch, asset.id];
    store.setState({ batch: next });
  };
  const selectAsset = (asset: LibraryAsset) => {
    onSelect(asset);
  };
  const clearAll = () =>
    setFilters({
      workspace: "library",
      level: "all",
      domain: "all",
      theme: "all",
      collection: "all",
      gameKit: "all",
      query: "",
      motion: "all",
      lod: "all",
      collision: "all",
      budget: "all",
      interface: "all",
      tag: "",
      compatibleIds: null,
    });

  const selectAllFiltered = () => {
    const ids = filteredAssets.map((asset) => asset.id);
    const allSelected = ids.length > 0 && ids.every((id) => batch.includes(id));
    if (allSelected) {
      store.setState({ batch: batch.filter((id) => !ids.includes(id)) });
      return;
    }
    if (ids.length > 256) {
      store
        .getState()
        .notify(
          `当前筛选结果有 ${formatCount(ids.length)} 项，超过每批最多 256 项，请缩小筛选范围。`,
        );
      return;
    }
    store.setState({ batch: Array.from(new Set([...batch, ...ids])) });
  };

  const onCatalogKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    if (!event.key.startsWith("Arrow")) return;
    if (
      event.target instanceof Element &&
      event.target.closest(
        "input, select, .library-favorite-button, .library-asset-card__scene-link",
      )
    ) {
      return;
    }
    const card =
      event.target instanceof Element
        ? event.target.closest<HTMLElement>(".library-asset-card")
        : null;
    if (!card || !catalogRef.current) return;
    const cards = Array.from(
      catalogRef.current.querySelectorAll<HTMLElement>(".library-asset-card"),
    );
    const index = cards.indexOf(card);
    if (index < 0) return;
    const width = card.getBoundingClientRect().width;
    const columns =
      event.key === "ArrowUp" || event.key === "ArrowDown"
        ? Math.max(
            1,
            Math.round(catalogRef.current.clientWidth / Math.max(1, width)),
          )
        : 1;
    const nextIndex =
      index +
      (["ArrowLeft", "ArrowUp"].includes(event.key) ? -columns : columns);
    const next = cards[nextIndex];
    if (!next) return;
    event.preventDefault();
    (
      next.querySelector<HTMLElement>(".library-asset-card__preview") ?? next
    ).focus();
  };

  return (
    <section className="library-catalog" aria-label="资产目录">
      <CatalogHeading filters={filters} onNewScene={onNewScene} />

      <div
        className="library-level-tabs"
        role="tablist"
        aria-label="按资产层级筛选"
      >
        <LevelTab
          active={filters.level === "all"}
          label="全部"
          count={assets.length}
          onClick={() =>
            setFilters({ level: "all", domain: "all", theme: "all" })
          }
        />
        {Object.entries(levelMap()).map(([id, level]) => (
          <LevelTab
            key={id}
            active={filters.level === id}
            label={`L${id} ${level.label}`}
            count={assets.filter((asset) => asset.level === Number(id)).length}
            onClick={() =>
              setFilters({ level: id, domain: "all", theme: "all" })
            }
          />
        ))}
      </div>

      <div className="library-catalog-tools">
        <div className="library-search-field">
          <Search size={16} aria-hidden="true" />
          <Input
            type="search"
            id="search"
            aria-label="搜索资产"
            placeholder="搜索名称、用途或 ID…"
            value={filters.query}
            onChange={(event) => setFilters({ query: event.target.value })}
          />
          {filters.query && (
            <Button
              type="button"
              className="library-search-clear"
              aria-label="清除搜索"
              onClick={() => setFilters({ query: "" })}
            >
              <X size={14} />
            </Button>
          )}
          <kbd>/</kbd>
        </div>
        <details className="library-filter-details">
          <summary className="library-button library-button--outline">
            <SlidersHorizontal size={15} />
            筛选
          </summary>
          <div className="library-filter-popover">
            <label>
              运动
              <select
                value={filters.motion}
                onChange={(event) => setFilters({ motion: event.target.value })}
              >
                <option value="all">全部</option>
                <option value="static">静态</option>
                <option value="rigid">刚性机构</option>
                <option value="skinned">骨骼</option>
              </select>
            </label>
            <label>
              碰撞配方
              <select
                aria-label="碰撞配方"
                value={filters.collision}
                onChange={(event) =>
                  setFilters({ collision: event.target.value })
                }
              >
                <option value="all">全部</option>
                <option value="yes">已定义实体</option>
                <option value="no">未定义 / 非实体</option>
              </select>
            </label>
            <label>
              三角面预算
              <select
                aria-label="三角面预算"
                value={filters.budget}
                onChange={(event) => setFilters({ budget: event.target.value })}
              >
                <option value="all">全部预算</option>
                <option value="1000">≤ 1,000</option>
                <option value="3000">≤ 3,000</option>
                <option value="10000">≤ 10,000</option>
                <option value="25000">≤ 25,000</option>
              </select>
            </label>
            <label>
              接口类型
              <select
                aria-label="接口类型"
                value={filters.interface}
                onChange={(event) =>
                  setFilters({ interface: event.target.value })
                }
              >
                <option value="all">全部接口</option>
                {interfaceOptions(data).map((id) => (
                  <option value={id} key={id}>
                    {id}
                  </option>
                ))}
              </select>
            </label>
            <label>
              标签
              <Input
                aria-label="资产标签"
                placeholder="如：桥梁 / 地形 / 森林"
                value={filters.tag}
                onChange={(event) => setFilters({ tag: event.target.value })}
              />
            </label>
            <label>
              LOD
              <select
                value={filters.lod}
                onChange={(event) => setFilters({ lod: event.target.value })}
              >
                <option value="all">全部</option>
                <option value="yes">有参数化 LOD</option>
                <option value="no">无 LOD</option>
              </select>
            </label>
            <Button
              type="button"
              className="library-button library-button--quiet"
              onClick={() =>
                setFilters({
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
              <Filter size={14} />
              重置筛选
            </Button>
          </div>
        </details>
        <label className="library-sort-control" aria-label="资产排序">
          <ArrowDownUp size={14} aria-hidden="true" />
          <select
            value={filters.sort}
            onChange={(event) => {
              const sort = event.target.value;
              setFilters({ sort });
              store.getState().setPrefs({ sort });
            }}
          >
            <option value="recommended">推荐顺序</option>
            <option value="name">名称排序</option>
            <option value="triangles">三角面从少到多</option>
            <option value="level">层级从高到低</option>
            <option value="recent">最近使用优先</option>
          </select>
          <ChevronsUpDown size={13} aria-hidden="true" />
        </label>
        <div className="library-view-toggle" role="group" aria-label="展示方式">
          <Button
            type="button"
            className={prefs.view === "grid" ? "is-active" : ""}
            id="gridView"
            aria-label="网格视图"
            aria-pressed={prefs.view === "grid"}
            onClick={() => store.getState().setPrefs({ view: "grid" })}
          >
            <Grid2X2 size={16} />
          </Button>
          <Button
            type="button"
            className={prefs.view === "list" ? "is-active" : ""}
            id="listView"
            aria-label="列表视图"
            aria-pressed={prefs.view === "list"}
            onClick={() => store.getState().setPrefs({ view: "list" })}
          >
            <List size={16} />
          </Button>
        </div>
      </div>

      <div className="library-filter-summary">
        <div className="library-filter-chips">
          {filters.collection !== "all" && (
            <FilterChip
              label={collectionLabel(filters.collection)}
              onRemove={() => setFilters({ collection: "all", gameKit: "all" })}
            />
          )}
          {filters.domain !== "all" && (
            <FilterChip
              label={
                getStudioCore()?.domains.find(
                  (domain) => domain.id === filters.domain,
                )?.label ?? filters.domain
              }
              onRemove={() => setFilters({ domain: "all" })}
            />
          )}
          {filters.theme !== "all" && (
            <FilterChip
              label={coreThemes()[filters.theme] ?? filters.theme}
              onRemove={() => setFilters({ theme: "all" })}
            />
          )}
          {filters.gameKit !== "all" && (
            <FilterChip
              label={filters.gameKit}
              onRemove={() => setFilters({ gameKit: "all" })}
            />
          )}
          {filters.query && (
            <FilterChip
              label={`“${filters.query}”`}
              onRemove={() => setFilters({ query: "" })}
            />
          )}
          {filters.motion !== "all" && (
            <FilterChip
              label={`运动 · ${motionLabel(filters.motion)}`}
              onRemove={() => setFilters({ motion: "all" })}
            />
          )}
          {filters.collision !== "all" && (
            <FilterChip
              label={`碰撞 · ${filters.collision === "yes" ? "已定义实体" : "未定义 / 非实体"}`}
              onRemove={() => setFilters({ collision: "all" })}
            />
          )}
          {filters.lod !== "all" && (
            <FilterChip
              label={`LOD · ${filters.lod === "yes" ? "有参数化 LOD" : "无 LOD"}`}
              onRemove={() => setFilters({ lod: "all" })}
            />
          )}
          {filters.budget !== "all" && (
            <FilterChip
              label={`预算 · ≤ ${formatCount(Number(filters.budget))}`}
              onRemove={() => setFilters({ budget: "all" })}
            />
          )}
          {filters.interface !== "all" && (
            <FilterChip
              label={`接口 · ${filters.interface}`}
              onRemove={() => setFilters({ interface: "all" })}
            />
          )}
          {filters.tag && (
            <FilterChip
              label={`标签 · ${filters.tag}`}
              onRemove={() => setFilters({ tag: "" })}
            />
          )}
          {filters.compatibleIds !== null && (
            <FilterChip
              label={`兼容部件 · ${formatCount(filters.compatibleIds.length)}`}
              onRemove={() => setFilters({ compatibleIds: null })}
            />
          )}
          {!filters.query &&
            filters.collection === "all" &&
            filters.domain === "all" &&
            filters.theme === "all" && (
              <span className="library-muted-label">{activeLevel}</span>
            )}
        </div>
        <span id="catalogCount" className="library-catalog-count">
          {formatCount(total)} 项{materialMode ? "材质" : "资源"}
        </span>
        <Button
          type="button"
          className="library-text-button"
          aria-label="选择当前筛选结果"
          disabled={materialMode || filteredAssets.length === 0}
          onClick={selectAllFiltered}
        >
          {filteredAssets.length > 0 &&
          filteredAssets.every((asset) => batch.includes(asset.id)) ? (
            <Check size={14} />
          ) : null}
          批量选择
        </Button>
        <Button
          type="button"
          className="library-text-button"
          disabled={compareAssets.length < 2}
          onClick={() => onCompare?.(compareAssets)}
        >
          对比{" "}
          <span className="library-count-pill">
            {selectedAssets.length >= 2
              ? selectedAssets.length
              : compareAssets.length}
          </span>
        </Button>
      </div>

      {notice && (
        <p className="library-catalog-notice" role="status" aria-live="polite">
          {notice}
        </p>
      )}

      <div
        id="catalog"
        ref={catalogRef}
        className={`library-catalog-scroll ${prefs.view === "list" ? "is-list" : "is-grid"}`}
        tabIndex={-1}
        onKeyDown={onCatalogKeyDown}
      >
        {materialMode ? (
          <MaterialGrid
            materials={visibleMaterials}
            onOpen={(nextMaterial) => {
              if (onOpenMaterial) onOpenMaterial(nextMaterial);
              else setMaterial(nextMaterial);
            }}
          />
        ) : (
          <AssetGrid
            assets={visibleAssets}
            currentId={current?.id ?? null}
            favorites={prefs.favorites}
            batch={batch}
            view={prefs.view}
            onSelect={selectAsset}
            onOpenScene={onOpenScene}
            onToggleFavorite={toggleFavorite}
            onToggleBatch={toggleBatch}
          />
        )}
        {!total && (
          <EmptyState
            collection={filters.collection}
            materialMode={materialMode}
            query={filters.query}
            filtered={hasActiveFilters(filters)}
            onReset={clearAll}
          />
        )}
      </div>

      <CatalogPager
        page={page}
        pages={pages}
        start={start}
        total={total}
        pageSize={filters.pageSize}
        onPage={(nextPage) => setFilters({ page: nextPage })}
      />
      {batch.length > 0 && (
        <BatchBar
          count={batch.length}
          onClear={() => store.setState({ batch: [] })}
          onExport={(onlyChanged) => onBatchExport?.(onlyChanged)}
        />
      )}
      <MaterialDialog material={material} onClose={() => setMaterial(null)} />
    </section>
  );
}

function CatalogHeading({
  filters,
  onNewScene,
}: {
  filters: Filters;
  onNewScene?(): void;
}) {
  const subtitle =
    filters.collection === "materials"
      ? "查看材质参数预览；有贴图的材质保留原图。"
      : filters.collection === "favorites"
        ? "从收藏中继续下一次创作。"
        : filters.collection === "recent"
          ? "从基础部件到完整场景，找到下一次创作的起点。"
          : filters.level === "4"
            ? "120 个可编辑起点 · 双击进入工作台 · 保留对象引用与源文件"
            : "从基础部件到完整场景，找到下一次创作的起点。";
  return (
    <header className="library-catalog-heading">
      <div>
        <div className="library-breadcrumb">
          <span>工作空间</span>
          <span>/</span>
          <strong>{collectionLabel(filters.collection)}</strong>
        </div>
        <h1>
          {filters.collection === "materials"
            ? "颜色与质感，构成世界。"
            : filters.collection === "favorites"
              ? "为下一次创作，保留灵感。"
              : filters.collection === "recent"
                ? "接着上一次，继续创造。"
                : filters.level === "4"
                  ? "从一个场景，开始构建。"
                  : "让每个构件，各得其所。"}
        </h1>
        <p>{subtitle}</p>
      </div>
      <Button
        type="button"
        className="library-button library-button--primary"
        onClick={onNewScene}
        disabled={!onNewScene}
      >
        <PlusIcon />
        新建场景
      </Button>
    </header>
  );
}

function AssetGrid({
  assets,
  currentId,
  favorites,
  batch,
  view,
  onSelect,
  onOpenScene,
  onToggleFavorite,
  onToggleBatch,
}: {
  assets: LibraryAsset[];
  currentId: string | null;
  favorites: string[];
  batch: string[];
  view: string;
  onSelect(asset: LibraryAsset): void;
  onOpenScene?(asset: Asset): void;
  onToggleFavorite(asset: LibraryAsset): void;
  onToggleBatch(asset: LibraryAsset): void;
}) {
  return (
    <div className="library-asset-grid">
      {assets.map((asset) => (
        <AssetCard
          key={asset.id}
          asset={asset}
          selected={currentId === asset.id}
          favorite={favorites.includes(asset.id)}
          picked={batch.includes(asset.id)}
          view={view}
          onSelect={onSelect}
          onOpenScene={onOpenScene}
          onToggleFavorite={onToggleFavorite}
          onToggleBatch={onToggleBatch}
        />
      ))}
    </div>
  );
}

function AssetCard({
  asset,
  selected,
  favorite,
  picked,
  view,
  onSelect,
  onOpenScene,
  onToggleFavorite,
  onToggleBatch,
}: {
  asset: LibraryAsset;
  selected: boolean;
  favorite: boolean;
  picked: boolean;
  view: string;
  onSelect(asset: LibraryAsset): void;
  onOpenScene?(asset: Asset): void;
  onToggleFavorite(asset: LibraryAsset): void;
  onToggleBatch(asset: LibraryAsset): void;
}) {
  const hero = assetHero(asset);
  const openScene = () => {
    if (asset.level === 4) onOpenScene?.(asset);
  };
  return (
    <article
      data-id={asset.id}
      className={`asset-card library-asset-card${selected ? " is-selected" : ""}`}
    >
      <button
        type="button"
        className="library-asset-card__preview"
        aria-label={`${selected ? "当前资产，" : ""}预览 ${assetName(asset)}`}
        aria-current={selected ? "true" : undefined}
        onClick={() => onSelect(asset)}
        onDoubleClick={openScene}
      >
        <span className="card-image library-asset-card__media">
          {hero ? (
            <img
              src={hero}
              alt=""
              width={view === "list" ? 72 : 256}
              height={view === "list" ? 72 : 256}
              loading="lazy"
              decoding="async"
            />
          ) : (
            <span className="library-asset-card__placeholder">
              <Layers size={32} />
            </span>
          )}
          {asset.level && (
            <span className="library-level-badge">L{asset.level}</span>
          )}
        </span>
        <span className="library-asset-card__body">
          <strong>{assetName(asset)}</strong>
          <span className="library-asset-card__meta">
            <span>{domainLabel(asset)}</span>
            <span>{formatTriangles(assetTriangles(asset))}</span>
          </span>
          {asset.level === 4 && (
            <span className="library-asset-card__scene-hint">
              双击或使用“打开场景”
            </span>
          )}
        </span>
      </button>
      <div className="library-asset-card__media-actions">
        <label className="library-asset-card__pick">
          <input
            type="checkbox"
            checked={picked}
            aria-label={`加入批量选择：${assetName(asset)}`}
            onChange={() => onToggleBatch(asset)}
          />
          <span aria-hidden="true">
            <Check size={12} />
          </span>
        </label>
        <Button
          type="button"
          className={`library-favorite-button${favorite ? " is-favorite" : ""}`}
          aria-label={`${favorite ? "取消收藏" : "收藏"} ${assetName(asset)}`}
          aria-pressed={favorite}
          onClick={(event) => {
            event.stopPropagation();
            onToggleFavorite(asset);
          }}
        >
          <Star size={16} fill={favorite ? "currentColor" : "none"} />
        </Button>
      </div>
      {asset.level === 4 && onOpenScene && (
        <Button
          type="button"
          className="library-asset-card__scene-link"
          onClick={openScene}
          onDoubleClick={(event) => event.stopPropagation()}
        >
          打开场景 <ChevronRight size={13} aria-hidden="true" />
        </Button>
      )}
    </article>
  );
}

function MaterialGrid({
  materials,
  onOpen,
}: {
  materials: MaterialRecord[];
  onOpen?(material: MaterialRecord): void;
}) {
  return (
    <div className="library-asset-grid">
      {materials.map((material) => (
        <article
          key={material.id}
          className="library-asset-card"
          tabIndex={0}
          role="button"
          aria-label={`查看材质 ${materialName(material)}`}
          onClick={() => onOpen?.(material)}
          onKeyDown={(event) => {
            if (event.key !== "Enter" && event.key !== " ") return;
            event.preventDefault();
            onOpen?.(material);
          }}
        >
          <div className="card-image library-asset-card__media">
            {materialPreview(material) ? (
              <img
                src={materialPreview(material) ?? undefined}
                alt=""
                loading="lazy"
              />
            ) : (
              <div className="library-asset-card__placeholder">
                <PaletteIcon />
              </div>
            )}
          </div>
          <div className="library-asset-card__body">
            <strong>{materialName(material)}</strong>
            <div>
              <span>{material.id}</span>
              <span>
                {hasMaterialImage(material.record)
                  ? "含原图"
                  : "无贴图 · 参数材质"}
              </span>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

function EmptyState({
  collection,
  materialMode,
  query,
  filtered,
  onReset,
}: {
  collection: string;
  materialMode: boolean;
  query: string;
  filtered: boolean;
  onReset(): void;
}) {
  return (
    <div className="library-empty-state">
      <Search size={25} />
      <h2>
        {materialMode
          ? "没有找到匹配材质"
          : collection === "favorites"
            ? "还没有符合条件的收藏"
            : query
              ? "没有找到匹配资源"
              : "这里还没有资产"}
      </h2>
      <p>
        {materialMode
          ? "尝试搜索其他材质名称或 ID。"
          : filtered
            ? "试试其他关键词，或清除筛选条件。"
            : "从目录中选择资产，或创建一个新的场景。"}
      </p>
      {filtered && (
        <Button
          type="button"
          className="library-button library-button--primary"
          onClick={onReset}
        >
          查看全部资源
        </Button>
      )}
    </div>
  );
}

function CatalogPager({
  page,
  pages,
  start,
  total,
  pageSize,
  onPage,
}: {
  page: number;
  pages: number;
  start: number;
  total: number;
  pageSize: number;
  onPage(page: number): void;
}) {
  if (!total)
    return (
      <div className="library-pager">
        <span>0–0 / 0 项</span>
      </div>
    );
  const pageNumbers = Array.from(
    new Set(
      [1, page - 1, page, page + 1, pages].filter(
        (number) => number > 0 && number <= pages,
      ),
    ),
  ).sort((a, b) => a - b);
  return (
    <nav className="library-pager" aria-label="资产分页">
      <span>
        {start + 1}–{Math.min(start + pageSize, total)} / {formatCount(total)}{" "}
        项
      </span>
      <div>
        {
          <Button
            type="button"
            aria-label="上一页"
            disabled={page === 1}
            onClick={() => onPage(page - 1)}
          >
            <ChevronLeft size={15} />
          </Button>
        }
        {pageNumbers.map((number, index) => (
          <span key={number}>
            {index > 0 && number - pageNumbers[index - 1] > 1 && <i>…</i>}
            <Button
              type="button"
              className={number === page ? "is-active" : ""}
              aria-current={number === page ? "page" : undefined}
              onClick={() => onPage(number)}
            >
              {number}
            </Button>
          </span>
        ))}
        <Button
          type="button"
          aria-label="下一页"
          disabled={page === pages}
          onClick={() => onPage(page + 1)}
        >
          <ChevronRight size={15} />
        </Button>
      </div>
    </nav>
  );
}

function BatchBar({
  count,
  onClear,
  onExport,
}: {
  count: number;
  onClear(): void;
  onExport(onlyChanged: boolean): void;
}) {
  const [onlyChanged, setOnlyChanged] = useState(false);
  return (
    <div className="library-batch-bar">
      <span>
        <strong>{count}</strong> 项已选择
      </span>
      <div>
        <label className="library-batch-option">
          <input
            type="checkbox"
            checked={onlyChanged}
            onChange={(event) => setOnlyChanged(event.target.checked)}
          />
          仅导出已变更
        </label>
        <Button
          type="button"
          className="library-button library-button--quiet"
          onClick={onClear}
        >
          清空
        </Button>
        <Button
          type="button"
          className="library-button library-button--primary"
          onClick={() => onExport(onlyChanged)}
        >
          批量处理
        </Button>
      </div>
    </div>
  );
}

function LevelTab({
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
      className={`library-level-tab${active ? " is-active" : ""}`}
      role="tab"
      aria-selected={active}
      onClick={onClick}
    >
      <span>{label}</span>
      <small>{formatCount(count)}</small>
    </Button>
  );
}

function FilterChip({ label, onRemove }: { label: string; onRemove(): void }) {
  return (
    <Button type="button" className="library-filter-chip" onClick={onRemove}>
      {label}
      <X size={12} />
    </Button>
  );
}

function filterMaterials(
  materials: MaterialRecord[],
  query: string,
): MaterialRecord[] {
  const needle = query.trim().toLocaleLowerCase("zh-CN");
  return needle
    ? materials.filter((material) =>
        `${material.id} ${materialName(material)}`
          .toLocaleLowerCase("zh-CN")
          .includes(needle),
      )
    : materials;
}

function domainLabel(asset: LibraryAsset): string {
  const activeCore = getStudioCore();
  return (
    activeCore?.domains.find((domain) => domain.id === domainId(asset))
      ?.label ?? "程序化资产"
  );
}

function collectionLabel(collection: string): string {
  if (collection === "favorites") return "我的收藏";
  if (collection === "recent") return "最近使用";
  if (collection === "materials") return "材质色板";
  return "资产资源库";
}

function motionLabel(value: string): string {
  if (value === "static") return "静态";
  if (value === "rigid") return "刚性机构";
  if (value === "skinned") return "骨骼";
  return value;
}

function PlusIcon() {
  return <span aria-hidden="true">＋</span>;
}
function PaletteIcon() {
  return <span aria-hidden="true">◆</span>;
}
