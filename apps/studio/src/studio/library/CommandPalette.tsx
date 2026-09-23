import { Button } from "../../ui/button";
import { useEffect, useMemo, useRef, useState } from "react";
import { useStore } from "zustand";
import {
  Command,
  FilePlus2,
  Grid2X2,
  Layers,
  Moon,
  Search,
  Star,
  type LucideIcon,
} from "lucide-react";
import type { CommandPaletteProps, LibraryAsset } from "./types";
import { dataAssets } from "./types";
import { assetHero, assetName, filterAssets, formatTriangles } from "./utils";
import { LibraryModal } from "./modal";

interface PaletteAction {
  id: string;
  label: string;
  hint: string;
  icon: LucideIcon;
  run(): void;
}

interface PaletteEntry extends PaletteAction {
  asset?: LibraryAsset;
}

export function CommandPalette({
  store,
  open,
  onClose,
  onSelect,
  onNewScene,
  onOpenScene,
}: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const data = useStore(store, (state) => state.data);
  const prefs = useStore(store, (state) => state.prefs);
  const filters = useStore(store, (state) => state.filters);
  const assets = useMemo(() => dataAssets(data), [data]);
  const results = useMemo(() => {
    const normalized = query.trim();
    if (!normalized) return [];
    return filterAssets(
      assets,
      {
        ...filters,
        query: normalized,
        level: "all",
        collection: "all",
        domain: "all",
        theme: "all",
        gameKit: "all",
        page: 1,
      },
      prefs,
    ).slice(0, 30);
  }, [assets, filters, prefs, query]);
  const actions = useMemo<PaletteAction[]>(() => {
    const run = (id: string, callback: () => void) => ({
      id,
      label: "",
      hint: "",
      icon: Command,
      run: callback,
    });
    return [
      {
        ...run("new-scene", onNewScene ?? (() => undefined)),
        label: "新建场景",
        hint: "工作空间操作",
        icon: FilePlus2,
      },
      {
        ...run("open-scene", () => {
          const scene = assets.find((asset) => asset.level === 4);
          if (scene) {
            store.getState().setFilters({
              workspace: "scene",
              level: "4",
              collection: "all",
              query: "",
              page: 1,
            });
            onOpenScene?.(scene);
          }
        }),
        label: "打开场景工作台",
        hint: "工作空间操作",
        icon: Layers,
      },
      {
        ...run("all-assets", () =>
          store.getState().setFilters({
            workspace: "library",
            collection: "all",
            level: "all",
            domain: "all",
            theme: "all",
            gameKit: "all",
            query: "",
            motion: "all",
            lod: "all",
            collision: "all",
            budget: "all",
            interface: "all",
            tag: "",
            compatibleIds: null,
            page: 1,
          }),
        ),
        label: "查看全部资源",
        hint: "工作空间操作",
        icon: Grid2X2,
      },
      {
        ...run("favorites", () =>
          store.getState().setFilters({
            workspace: "library",
            collection: "favorites",
            level: "all",
            query: "",
            page: 1,
          }),
        ),
        label: "我的收藏",
        hint: "工作空间操作",
        icon: Star,
      },
      {
        ...run("theme", () =>
          store
            .getState()
            .setPrefs({ theme: prefs.theme === "light" ? "dark" : "light" }),
        ),
        label: "切换深浅主题",
        hint: "工作空间操作",
        icon: Moon,
      },
    ];
  }, [assets, onNewScene, onOpenScene, prefs.theme, store]);
  const entries = useMemo<PaletteEntry[]>(
    () => [
      ...actions.filter((action) => !query || action.label.includes(query)),
      ...results.map((asset) => ({
        id: asset.id,
        label: assetName(asset),
        hint: `L${asset.level ?? "—"} · ${formatTriangles(asset.report?.triangles as number | null)}`,
        icon: Search,
        asset,
        run: () => {
          if (asset.level === 4) onOpenScene?.(asset);
          else onSelect(asset);
        },
      })),
    ],
    [actions, onOpenScene, onSelect, query, results],
  );

  useEffect(() => {
    if (open) {
      setQuery("");
      setActiveIndex(0);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex((index) =>
          Math.max(
            0,
            Math.min(
              entries.length - 1,
              index + (event.key === "ArrowDown" ? 1 : -1),
            ),
          ),
        );
        return;
      }
      if (
        event.key === "Enter" &&
        document.activeElement === inputRef.current
      ) {
        event.preventDefault();
        entries[activeIndex]?.run();
        onClose();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [activeIndex, entries, onClose, open]);

  if (!open) return null;
  return (
    <LibraryModal
      title="搜索资产与命令"
      onClose={onClose}
      initialFocus={inputRef}
      className="library-command-palette"
    >
      <div className="library-command-palette__title">
        <Command size={17} />
        <h2 id="library-command-title">搜索资产与命令</h2>
        <kbd>ESC</kbd>
      </div>
      <div className="library-command-palette__input">
        <Search size={17} aria-hidden="true" />
        <input
          ref={inputRef}
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setActiveIndex(0);
          }}
          placeholder="搜索名称、用途，或输入命令…"
          aria-label="搜索命令与资产"
          autoComplete="off"
        />
      </div>
      <div
        className="library-command-results"
        role="listbox"
        aria-label="命令与资产结果"
      >
        {!entries.length && (
          <p className="library-command-empty">
            输入名称、用途或 ID 开始搜索。
          </p>
        )}
        {entries.map((entry, index) => (
          <Button
            type="button"
            role="option"
            aria-selected={index === activeIndex}
            className={index === activeIndex ? "is-active" : ""}
            key={entry.id}
            onMouseEnter={() => setActiveIndex(index)}
            onClick={() => {
              entry.run();
              onClose();
            }}
          >
            <entry.icon size={17} aria-hidden="true" />
            {entry.asset && <AssetThumb asset={entry.asset} />}
            <span>
              <strong>{entry.label}</strong>
              <small>{entry.hint}</small>
            </span>
            <span className="library-command-arrow">↵</span>
          </Button>
        ))}
      </div>
      <footer className="library-command-palette__footer">
        <span>
          <kbd>↑</kbd>
          <kbd>↓</kbd> 选择
        </span>
        <span>
          <kbd>Enter</kbd> 执行
        </span>
        <span>
          <kbd>Esc</kbd> 关闭
        </span>
      </footer>
    </LibraryModal>
  );
}

function AssetThumb({ asset }: { asset: LibraryAsset }) {
  const hero = assetHero(asset);
  return hero ? (
    <img
      className="library-command-thumb"
      src={hero}
      alt=""
      width={34}
      height={34}
    />
  ) : (
    <span
      className="library-command-thumb library-command-thumb--empty"
      aria-hidden="true"
    />
  );
}
