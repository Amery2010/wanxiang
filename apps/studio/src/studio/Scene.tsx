import { Button } from "../ui/button";
import { Input } from "../ui/input";
import {
  Fragment,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { useStore } from "zustand";
import {
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Plus,
  Trash2,
  Copy,
  Undo2,
  Redo2,
  Save,
  MousePointer2,
  Move,
  RotateCw,
  Scaling,
  Group,
  Download,
  Settings,
  Maximize,
  ChevronDown,
  Star,
} from "lucide-react";
import type { Session } from "./session";
import { core, sceneAPI, type SceneDocument } from "./types";
export function SceneTree({ session }: { session: Session }) {
  const s = useStore(session.store),
    [query, setQuery] = useState("");
  const anchor = useRef<string | null>(null);
  const treeRef = useRef<HTMLDivElement>(null);
  const rowRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const summaryRefs = useRef<Record<string, HTMLElement | null>>({});
  const layerRefs = useRef<Record<string, HTMLDetailsElement | null>>({});
  const [openLayers, setOpenLayers] = useState<Record<string, boolean>>({});
  const [activeTreeId, setActiveTreeId] = useState<string>();
  const doc = s.spec as SceneDocument | null;
  const layerIds = doc?.metadata.scene
    ? Object.keys(doc.metadata.scene.layers)
    : [];
  useEffect(() => {
    const currentDoc = s.spec as SceneDocument | null;
    const currentLayerIds = currentDoc?.metadata.scene
      ? Object.keys(currentDoc.metadata.scene.layers)
      : [];
    setOpenLayers((old) =>
      Object.fromEntries(currentLayerIds.map((id) => [id, old[id] ?? true])),
    );
  }, [s.spec]);
  if (!doc?.metadata.scene) return null;
  const meta = doc.metadata.scene;
  const normalizedQuery = query.trim().toLowerCase();
  const visibleRowsByLayer = Object.fromEntries(
    layerIds.map((id) => [
      id,
      doc.instances.filter(
        (i) =>
          meta.objects[i.id].layer === id &&
          [i.id, meta.objects[i.id].label, i.part, i.assembly]
            .join(" ")
            .toLowerCase()
            .includes(normalizedQuery),
      ),
    ]),
  );
  const visibleRows = layerIds.flatMap((id) => visibleRowsByLayer[id]);
  const selectRow = (
    id: string,
    event: {
      shiftKey: boolean;
      altKey: boolean;
      metaKey: boolean;
      ctrlKey: boolean;
    },
  ) => {
    const order = visibleRows.map((item) => item.id);
    const start = anchor.current ? order.indexOf(anchor.current) : -1;
    const end = order.indexOf(id);
    if (event.shiftKey && event.altKey && start >= 0 && end >= 0) {
      session.selectObjects(
        order.slice(Math.min(start, end), Math.max(start, end) + 1),
      );
    } else {
      session.selectObjects(
        [id],
        event.shiftKey || event.metaKey || event.ctrlKey,
      );
      anchor.current = id;
    }
  };
  const tabRowId = visibleRows.some((item) => item.id === activeTreeId)
    ? activeTreeId
    : visibleRows[0]?.id;
  const focusRow = (id: string | undefined) => {
    if (!id) return;
    setActiveTreeId(id);
    rowRefs.current[id]?.focus();
  };
  const focusAdjacentRow = (id: string, direction: 1 | -1) => {
    const index = visibleRows.findIndex((item) => item.id === id);
    if (index < 0) return;
    focusRow(visibleRows[index + direction]?.id);
  };
  const handleTreeRowKeyDown = (
    event: KeyboardEvent<HTMLDivElement>,
    id: string,
    layerId: string,
  ) => {
    if (event.target !== event.currentTarget) return;
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      selectRow(id, event);
      return;
    }
    if (event.key === "ArrowDown") {
      event.preventDefault();
      focusAdjacentRow(id, 1);
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      focusAdjacentRow(id, -1);
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      focusRow(visibleRows[0]?.id);
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      focusRow(visibleRows.at(-1)?.id);
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      summaryRefs.current[layerId]?.focus();
      return;
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      const details = layerRefs.current[layerId];
      if (details && !details.open) {
        details.open = true;
        setOpenLayers((old) => ({ ...old, [layerId]: true }));
      }
    }
  };
  const handleLayerKeyDown = (
    event: KeyboardEvent<HTMLElement>,
    layerId: string,
  ) => {
    if (event.target !== event.currentTarget) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      const rows = visibleRowsByLayer[layerId];
      const layerIndex = layerIds.indexOf(layerId);
      const nextLayer = layerIds
        .slice(layerIndex + 1)
        .find((id) => visibleRowsByLayer[id].length);
      focusRow(
        rows[0]?.id || (nextLayer && visibleRowsByLayer[nextLayer][0]?.id),
      );
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      const layerIndex = layerIds.indexOf(layerId);
      const previousLayer = layerIds
        .slice(0, layerIndex)
        .reverse()
        .find((id) => visibleRowsByLayer[id].length);
      focusRow(previousLayer && visibleRowsByLayer[previousLayer].at(-1)?.id);
      return;
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      const details = layerRefs.current[layerId];
      if (details && !details.open) {
        details.open = true;
        setOpenLayers((old) => ({ ...old, [layerId]: true }));
      }
      focusRow(visibleRowsByLayer[layerId][0]?.id);
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      const details = layerRefs.current[layerId];
      if (details?.open) {
        details.open = false;
        setOpenLayers((old) => ({ ...old, [layerId]: false }));
      }
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      const firstLayer = layerIds[0];
      if (firstLayer) summaryRefs.current[firstLayer]?.focus();
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      const lastLayer = layerIds.at(-1);
      if (lastLayer) summaryRefs.current[lastLayer]?.focus();
    }
  };
  return (
    <section id="sceneTreePanel">
      <h3>
        场景对象 <small>{doc.instances.length}</small>
      </h3>
      <Input
        id="treeSearch"
        aria-label="搜索场景对象"
        placeholder="搜索对象或引用…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="tree-actions">
        {" "}
        <Button
          id="treeAdd"
          variant="ghost"
          aria-label="插入资产"
          onClick={() => session.store.setState({ dialog: "scene-picker" })}
        >
          <Plus />
        </Button>
        <Button
          id="treeAddLayer"
          aria-label="新建图层"
          variant="outline"
          onClick={() =>
            void session.command({
              type: "add-layer",
              layer: "layer_" + Date.now().toString(36),
              label: "新图层",
            })
          }
        >
          <Plus />
        </Button>
        <Button
          variant="ghost"
          aria-label="场景源文件"
          onClick={() => session.store.setState({ dialog: "scene-source" })}
        >
          <Save />
        </Button>
        <Button
          variant="ghost"
          aria-label="管理图层与选择组"
          onClick={() => session.store.setState({ dialog: "scene-manage" })}
        >
          <Group />
        </Button>
        <small>按图层组织</small>
      </div>
      <div
        ref={treeRef}
        role="tree"
        aria-label="场景对象树"
        aria-multiselectable="true"
      >
        {layerIds.map((id, layerIndex) => {
          const layer = meta.layers[id];
          const rows = visibleRowsByLayer[id];
          const isOpen = openLayers[id] ?? true;
          const groupId = `scene-tree-group-${layerIndex}`;
          return (
            <details
              key={id}
              ref={(element) => {
                layerRefs.current[id] = element;
              }}
              open={isOpen}
              onToggle={(event) => {
                const nextOpen = event.currentTarget.open;
                setOpenLayers((old) => ({ ...old, [id]: nextOpen }));
              }}
              data-layer-drop={id}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                try {
                  void session.command({
                    type: "move-layer",
                    ids: JSON.parse(
                      e.dataTransfer.getData("application/x-wx-objects"),
                    ),
                    layer: id,
                  });
                } catch {
                  /* External drags have no scene IDs. */
                }
              }}
            >
              <summary
                id={`${groupId}-label`}
                ref={(element) => {
                  summaryRefs.current[id] = element;
                }}
                aria-controls={groupId}
                aria-expanded={isOpen}
                onKeyDown={(event) => handleLayerKeyDown(event, id)}
              >
                <span>{layer.label}</span>
                <small>{rows.length}</small>
                <Button
                  aria-label={
                    (layer.visible ? "隐藏" : "显示") + "图层 " + layer.label
                  }
                  onClick={(e) => {
                    e.preventDefault();
                    void session.command({
                      type: "layer-visibility",
                      layer: id,
                      visible: !layer.visible,
                    });
                  }}
                >
                  {layer.visible ? <Eye /> : <EyeOff />}
                </Button>
                <Button
                  aria-label={
                    (layer.locked ? "解锁" : "锁定") + "图层 " + layer.label
                  }
                  onClick={(e) => {
                    e.preventDefault();
                    void session.command({
                      type: "layer-lock",
                      layer: id,
                      locked: !layer.locked,
                    });
                  }}
                >
                  {layer.locked ? <Lock /> : <Unlock />}
                </Button>
              </summary>
              <div
                id={groupId}
                role="group"
                aria-labelledby={`${groupId}-label`}
              >
                {rows.map((item, rowIndex) => {
                  const o = meta.objects[item.id];
                  const group = o.group && meta.groups[o.group];
                  const firstInGroup =
                    o.group &&
                    !rows
                      .slice(0, rowIndex)
                      .some((row) => meta.objects[row.id].group === o.group);
                  const inheritedLock =
                    !o.locked && sceneAPI().locked(doc, item.id);
                  return (
                    <Fragment key={item.id}>
                      {group && firstInGroup && (
                        <Button
                          className="tree-group-head"
                          variant="ghost"
                          onClick={() =>
                            session.selectObjects(
                              doc.instances
                                .filter(
                                  (row) =>
                                    meta.objects[row.id].group === o.group,
                                )
                                .map((row) => row.id),
                            )
                          }
                        >
                          <Group />
                          {group.label}
                          <small>选择组</small>
                        </Button>
                      )}
                      <div
                        className={[
                          "tree-row",
                          s.selection.includes(item.id) && "selected",
                          item.enabled === false && "is-hidden",
                          sceneAPI().locked(doc, item.id) && "is-locked",
                        ]
                          .filter(Boolean)
                          .join(" ")}
                        data-object={item.id}
                        data-tree-item="true"
                        role="treeitem"
                        aria-label={o.label}
                        aria-level={2}
                        aria-posinset={rowIndex + 1}
                        aria-setsize={rows.length}
                        aria-selected={s.selection.includes(item.id)}
                        tabIndex={tabRowId === item.id ? 0 : -1}
                        ref={(element) => {
                          rowRefs.current[item.id] = element;
                        }}
                        onFocus={() => setActiveTreeId(item.id)}
                        draggable={!sceneAPI().locked(doc, item.id)}
                        onDragStart={(e) =>
                          e.dataTransfer.setData(
                            "application/x-wx-objects",
                            JSON.stringify(
                              s.selection.includes(item.id)
                                ? s.selection
                                : [item.id],
                            ),
                          )
                        }
                        onClick={(e) => selectRow(item.id, e)}
                        onContextMenu={(e) => {
                          e.preventDefault();
                          if (!s.selection.includes(item.id))
                            session.selectObjects([item.id]);
                          session.store.setState({ dialog: "scene-context" });
                        }}
                        onDoubleClick={() => session.runtime.focusSelection()}
                        onKeyDown={(event) =>
                          handleTreeRowKeyDown(event, item.id, id)
                        }
                      >
                        <span>
                          {o.group && <Group />}
                          {o.label}
                        </span>
                        <Button
                          disabled={sceneAPI().locked(doc, item.id)}
                          aria-label={
                            (o.hidden ? "显示" : "隐藏") + " " + o.label
                          }
                          onClick={(e) => {
                            e.stopPropagation();
                            void session.command({
                              type: "visibility",
                              id: item.id,
                              visible: o.hidden,
                            });
                          }}
                        >
                          {o.hidden ? <EyeOff /> : <Eye />}
                        </Button>
                        <Button
                          disabled={inheritedLock}
                          aria-label={
                            inheritedLock
                              ? "继承锁定 " + o.label
                              : (o.locked ? "解锁" : "锁定") + " " + o.label
                          }
                          onClick={(e) => {
                            e.stopPropagation();
                            void session.command({
                              type: "lock",
                              id: item.id,
                              locked: !o.locked,
                            });
                          }}
                        >
                          {sceneAPI().locked(doc, item.id) ? (
                            <Lock />
                          ) : (
                            <Unlock />
                          )}
                        </Button>
                      </div>
                    </Fragment>
                  );
                })}
                {!rows.length && !normalizedQuery && (
                  <p className="empty-state" role="status">
                    此图层暂无对象
                  </p>
                )}
              </div>
            </details>
          );
        })}
        {normalizedQuery && !visibleRows.length && (
          <p className="empty-state" role="status">
            没有匹配的场景对象
          </p>
        )}
        {!layerIds.length && (
          <p className="empty-state" role="status">
            场景暂无图层
          </p>
        )}
      </div>
      <Button
        onClick={() => session.store.setState({ dialog: "scene-source" })}
      >
        <Save />
        保存 / 载入场景源
      </Button>
    </section>
  );
}
export function SceneTools({ session }: { session: Session }) {
  const s = useStore(session.store);
  const doc = s.spec as SceneDocument | null;
  return (
    <>
      <div id="sceneTopbar">
        <div className="scene-title-group">
          <small>SCENE WORKSPACE {s.dirty ? " · 未保存" : ""}</small>
          <Input
            aria-label="重命名场景"
            key={String(doc?.metadata?.scene?.title || s.current?.id)}
            defaultValue={String(
              doc?.metadata?.scene?.title ||
                s.spec?.name ||
                s.current?.name ||
                "场景",
            )}
            onKeyDown={(event) => {
              if (event.key === "Enter") event.currentTarget.blur();
            }}
            onBlur={(event) => {
              const title = event.target.value.trim();
              if (title && title !== doc?.metadata?.scene?.title)
                void session.command({ type: "rename-scene", title });
            }}
          />
          <small>{s.spec?.instances?.length || 0} 个对象 · 可编辑源配方</small>
        </div>
        <Button
          variant="outline"
          onClick={() => session.store.setState({ dialog: "scene-source" })}
        >
          源文件
        </Button>
        <Button
          onClick={() => session.store.setState({ dialog: "scene-picker" })}
        >
          <Plus />
          插入资产
        </Button>
        <Button
          variant="outline"
          onClick={() => session.store.setState({ dialog: "scene-export" })}
        >
          <Download />
          分区导出
        </Button>
      </div>
      <div id="sceneToolbar">
        {(
          [
            ["select", MousePointer2, "选择"],
            ["translate", Move, "移动"],
            ["rotate", RotateCw, "旋转"],
            ["scale", Scaling, "缩放"],
          ] as const
        ).map(([tool, Icon, label]) => (
          <Button
            key={tool}
            variant={s.tool === tool ? "secondary" : "outline"}
            aria-label={label}
            aria-pressed={s.tool === tool}
            onClick={() => session.store.setState({ tool })}
          >
            <Icon />
            {label}
          </Button>
        ))}
        <label>
          <Input
            type="checkbox"
            checked={s.prefs.snap}
            onChange={(e) => s.setPrefs({ snap: e.target.checked })}
          />
          吸附
        </label>
        <select
          aria-label="移动吸附步长"
          value={s.prefs.snapMove}
          onChange={(event) =>
            s.setPrefs({ snapMove: Number(event.target.value) })
          }
        >
          {[...new Set([0.1, 0.25, 0.5, 1, s.prefs.snapMove])]
            .sort((a, b) => a - b)
            .map((value) => (
              <option key={value} value={value}>
                {value} m
              </option>
            ))}
        </select>
        <Button
          variant="outline"
          aria-label="编辑设置"
          onClick={() => session.store.setState({ dialog: "scene-settings" })}
        >
          <Settings />
        </Button>
        <span className="toolbar-spacer" />
        <Button
          id="sceneUndo"
          variant="outline"
          disabled={s.busy || !s.history.length}
          onClick={() => void session.undo()}
          aria-label="撤销"
        >
          <Undo2 />
        </Button>
        <Button
          variant="outline"
          disabled={s.busy || !s.future.length}
          onClick={() => void session.redo()}
          aria-label="重做"
        >
          <Redo2 />
        </Button>
        <Button
          variant="outline"
          aria-label="适配全场"
          onClick={() => session.runtime.fit()}
        >
          <Maximize />
        </Button>
        <Button
          variant="outline"
          aria-label="专注模式"
          aria-pressed={s.focusMode}
          onClick={() => session.store.setState({ focusMode: !s.focusMode })}
        >
          <Maximize />
        </Button>
        <details className="scene-more-actions">
          <summary aria-label="更多场景操作">更多</summary>
          <div>
            <Button
              variant="outline"
              onClick={() => session.store.setState({ dialog: "scene-manage" })}
            >
              管理
            </Button>
            <Button
              variant="outline"
              disabled={s.selection.length < 2}
              onClick={() => session.store.setState({ dialog: "scene-align" })}
            >
              对齐
            </Button>
            <Button
              variant="outline"
              disabled={!s.selection.length}
              onClick={() => session.store.setState({ dialog: "scene-array" })}
            >
              阵列
            </Button>
            <Button
              variant="outline"
              disabled={!s.selection.length}
              onClick={() =>
                void session.command({
                  type: "duplicate-many",
                  ids: s.selection,
                })
              }
            >
              <Copy />
              复制
            </Button>
            <Button
              variant="outline"
              disabled={!s.selection.length}
              onClick={() => session.requestDelete()}
            >
              <Trash2 />
              删除
            </Button>
          </div>
        </details>
      </div>
    </>
  );
}
export function Shelf({ session }: { session: Session }) {
  const s = useStore(session.store),
    [query, setQuery] = useState(""),
    [level, setLevel] = useState("3"),
    [domain, setDomain] = useState("all"),
    [favorites, setFavorites] = useState(false),
    [collapsed, setCollapsed] = useState(false);
  const rows = core()
    .filter(
      s.data.assets.filter(
        (asset) => (asset.dynamic || asset.kit) && (asset.level || 0) < 4,
      ),
      { query, level, domain, collection: favorites ? "favorites" : "all" },
      s.prefs,
    )
    .slice(0, 40);
  return (
    <section id="assetShelf" data-collapsed={collapsed}>
      <div className="shelf-bar">
        <strong>资产架</strong>
        <Button
          id="shelfBrowse"
          variant="outline"
          onClick={() => session.store.setState({ dialog: "scene-picker" })}
        >
          浏览全部
        </Button>
        <Input
          id="shelfSearch"
          aria-label="搜索资产架"
          placeholder="搜索并拖入场景…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          id="shelfLevel"
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          aria-label="资产架层级"
        >
          {["1", "2", "3"].map((l) => (
            <option key={l} value={l}>
              L{l}
            </option>
          ))}
        </select>
        <select
          aria-label="资产架用途"
          value={domain}
          onChange={(event) => setDomain(event.target.value)}
        >
          <option value="all">所有用途</option>
          {core()
            .domains.filter((entry) => entry.id !== "scene")
            .map((entry) => (
              <option key={entry.id} value={entry.id}>
                {entry.label}
              </option>
            ))}
        </select>
        <Button
          variant="outline"
          aria-label="仅收藏资产"
          aria-pressed={favorites}
          onClick={() => setFavorites(!favorites)}
        >
          <Star />
        </Button>
        <Button
          variant="ghost"
          aria-label={collapsed ? "展开资产架" : "折叠资产架"}
          aria-expanded={!collapsed}
          onClick={() => setCollapsed(!collapsed)}
        >
          <ChevronDown />
        </Button>
      </div>
      {!collapsed && (
        <div className="shelf-items">
          {rows.map((a) => (
            <Button
              className="shelf-card"
              variant="outline"
              key={a.id}
              data-shelf-ref={a.id}
              draggable
              onDragStart={(e) =>
                e.dataTransfer.setData("application/x-wx-asset", a.id)
              }
              aria-label={"插入 " + a.name}
              onClick={() => {
                const doc = s.spec as SceneDocument;
                const layer = doc.metadata.scene.objects[s.selection[0]]?.layer;
                void session.command({
                  type: "add",
                  ref: a.id,
                  position: session.runtime.groundCenter(),
                  ...(layer && !doc.metadata.scene.layers[layer].locked
                    ? { layer }
                    : {}),
                });
              }}
            >
              <img src={String(a.hero || "")} alt="" width={64} height={64} />
              <span>{a.name}</span>
              <Plus />
            </Button>
          ))}
          {!rows.length && (
            <p className="empty-state" role="status">
              没有匹配的资产，试试其他关键词或层级。
            </p>
          )}
        </div>
      )}
    </section>
  );
}
export function SceneProperties({ session }: { session: Session }) {
  const s = useStore(session.store),
    doc = s.spec as SceneDocument,
    meta = doc.metadata.scene,
    items = doc.instances.filter((i) => s.selection.includes(i.id)),
    item = items[0],
    o = item && meta.objects[item.id],
    locked = items.some((i) => sceneAPI().locked(doc, i.id)),
    [uniform, setUniform] = useState(true);
  if (!item)
    return (
      <>
        <div className="scene-empty-selection">
          <MousePointer2 />
          <h3>选择一个对象开始编辑</h3>
          <p>在视口点击模型，或从左侧对象树选择。按住 Shift 可以多选。</p>
        </div>
        <h3>场景概况</h3>
        <dl className="keyvals">
          <dt>顶层对象</dt>
          <dd>{doc.instances.length}</dd>
          <dt>可见对象</dt>
          <dd>{doc.instances.filter((row) => row.enabled !== false).length}</dd>
          <dt>图层 / 分区</dt>
          <dd>
            {Object.keys(meta.layers).length} /{" "}
            {Object.keys(meta.regions).length}
          </dd>
          <dt>选择组</dt>
          <dd>{Object.keys(meta.groups).length}</dd>
        </dl>
        <div className="property-actions">
          <Button
            onClick={() => session.store.setState({ dialog: "scene-picker" })}
          >
            <Plus />
            插入资产
          </Button>
          <Button variant="outline" onClick={() => session.runtime.fit()}>
            适配全场
          </Button>
        </div>
        <label>
          场景默认风格
          <select
            aria-label="场景默认风格"
            value={String(doc.style || "lowpoly")}
            disabled={s.busy}
            onChange={(event) =>
              void session.apply({ ...doc, style: event.target.value })
            }
          >
            <option value="lowpoly">Lowpoly</option>
            <option value="toon">卡通</option>
            <option value="voxel">像素</option>
          </select>
        </label>
        <p>对象可以单独覆盖此风格。</p>
        <label>
          场景名称
          <Input
            key={meta.title}
            defaultValue={meta.title}
            onBlur={(e) => {
              if (e.target.value !== meta.title)
                void session.command({
                  type: "rename-scene",
                  title: e.target.value,
                });
            }}
          />
        </label>
        <Button
          onClick={() => session.store.setState({ dialog: "scene-source" })}
        >
          保存与恢复
        </Button>
      </>
    );
  return (
    <>
      <h3>{items.length > 1 ? items.length + " 个对象" : o.label}</h3>
      {locked && <p role="note">所选对象或所属图层 / 组已锁定。</p>}
      <label>
        显示名称
        <Input
          id="objectLabel"
          key={item.id + o.label}
          defaultValue={o.label}
          disabled={locked || items.length > 1}
          onBlur={(e) => {
            if (e.target.value !== o.label)
              void session.command({
                type: "rename",
                id: item.id,
                label: e.target.value,
              });
          }}
        />
      </label>
      {(["position", "rotation", "scale"] as const).map((kind) => (
        <fieldset key={kind} disabled={locked || items.some((i) => !!i.attach)}>
          <legend>
            {
              { position: "位置 · m", rotation: "旋转 · °", scale: "比例" }[
                kind
              ]
            }
          </legend>
          <div className="scene-vector">
            {item[kind].map((v, axis) => (
              <label key={axis}>
                {"XYZ"[axis]}
                <Input
                  type="number"
                  step={kind === "rotation" ? 1 : 0.1}
                  aria-label={kind + " " + "XYZ"[axis]}
                  key={item.id + ":" + v}
                  defaultValue={v}
                  onBlur={(e) => {
                    const n = e.target.valueAsNumber;
                    if (!Number.isFinite(n) || n === v) return;
                    const values = Object.fromEntries(
                      items.map((i) => {
                        const vector = [...i[kind]];
                        for (let j = 0; j < 3; j++) {
                          if (kind === "scale" && (uniform || j === axis))
                            vector[j] *= n / v;
                          else if (j === axis) vector[j] += n - v;
                        }
                        return [i.id, { [kind]: vector }];
                      }),
                    );
                    void session.command({
                      type: "transform-many",
                      ids: s.selection,
                      values,
                    });
                  }}
                />
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      <label>
        <Input
          type="checkbox"
          checked={uniform}
          onChange={(e) => setUniform(e.target.checked)}
        />
        等比缩放
      </label>
      <label>
        图层
        <select
          value={o.layer}
          disabled={locked}
          onChange={(e) =>
            void session.command({
              type: "move-layer",
              ids: s.selection,
              layer: e.target.value,
            })
          }
        >
          {Object.entries(meta.layers).map(([id, l]) => (
            <option key={id} value={id}>
              {l.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        分区
        <select
          value={o.region}
          disabled={locked}
          onChange={(e) =>
            void session.command({
              type: "move-region",
              ids: s.selection,
              region: e.target.value,
            })
          }
        >
          {Object.entries(meta.regions).map(([id, l]) => (
            <option key={id} value={id}>
              {l.label}
            </option>
          ))}
        </select>
      </label>
      <div className="property-actions">
        <Button
          disabled={locked || items.some((row) => !!row.attach)}
          onClick={() =>
            void session.command({
              type: "transform-many",
              ids: s.selection,
              values: Object.fromEntries(
                s.selection.map((id) => [
                  id,
                  { rotation: [0, 0, 0], scale: [1, 1, 1] },
                ]),
              ),
            })
          }
        >
          重置姿态
        </Button>
        <Button onClick={() => session.runtime.focusSelection()}>
          聚焦所选
        </Button>
        <Button disabled={locked} onClick={() => session.requestDelete()}>
          删除对象
        </Button>
        <Button
          id="objectGround"
          disabled={locked || items.some((i) => !!i.attach)}
          onClick={() => void session.runtime.ground()}
        >
          贴地
        </Button>
        <Button disabled={locked} onClick={() => session.requestGroup()}>
          创建选择组
        </Button>
        <Button
          disabled={locked}
          onClick={() =>
            void session.command({ type: "ungroup", ids: s.selection })
          }
        >
          移出组
        </Button>
        <Button onClick={() => void session.exportSubset({ ids: s.selection })}>
          导出所选
        </Button>
        <Button
          disabled={locked}
          onClick={() =>
            void session.command({
              type: "visibility",
              ids: s.selection,
              visible: items.every((row) => row.enabled === false),
            })
          }
        >
          {items.every((row) => row.enabled === false) ? "显示" : "隐藏"}
        </Button>
        <Button
          onClick={() =>
            void session.command({
              type: "lock",
              ids: s.selection,
              locked: !items.every((row) => meta.objects[row.id].locked),
            })
          }
        >
          {items.every((row) => meta.objects[row.id].locked) ? "解锁" : "锁定"}
        </Button>
      </div>
      <h4>源资产</h4>
      <Button
        id="objectReplace"
        disabled={locked || items.length !== 1}
        onClick={() => session.store.setState({ dialog: "scene-replace" })}
      >
        替换资产
      </Button>
      <code>{item.part || item.assembly}</code>
      {items.length === 1 && (
        <ObjectParameters session={session} item={item} locked={locked} />
      )}
      <label>
        对象风格
        <select
          disabled={locked}
          value={item.style || ""}
          onChange={(e) =>
            void session.command({
              type: "params",
              id: item.id,
              style: e.target.value,
            })
          }
        >
          <option value="">继承场景</option>
          <option value="lowpoly">Lowpoly</option>
          <option value="toon">卡通</option>
          <option value="voxel">像素</option>
        </select>
      </label>
    </>
  );
}

function ObjectParameters({
  session,
  item,
  locked,
}: {
  session: Session;
  item: import("./types").SceneObject;
  locked: boolean;
}) {
  const ref = item.part || item.assembly,
    definition = ref ? session.catalog[ref] : undefined,
    properties =
      (definition?.parameter_schema || definition?.metadata?.parameter_schema)
        ?.properties || {};
  return (
    <>
      {Object.entries(properties).map(([key, p]) => {
        const value = item.params?.[key] ?? p.default,
          apply = (v: unknown) =>
            void session.command({
              type: "params",
              id: item.id,
              params: { [key]: v },
            });
        return (
          <label key={key}>
            {p.title || key}
            {p.enum ? (
              <select
                disabled={locked}
                value={String(value)}
                onChange={(e) =>
                  apply(
                    p.type === "number" || p.type === "integer"
                      ? Number(e.target.value)
                      : e.target.value,
                  )
                }
              >
                {p.enum.map((v) => (
                  <option key={String(v)} value={String(v)}>
                    {String(v)}
                  </option>
                ))}
              </select>
            ) : p.type === "boolean" ? (
              <Input
                type="checkbox"
                disabled={locked}
                checked={Boolean(value)}
                onChange={(e) => apply(e.target.checked)}
              />
            ) : (
              <Input
                type="number"
                disabled={locked}
                min={p.minimum}
                max={p.maximum}
                step={p.step || 0.01}
                key={String(value)}
                defaultValue={Number(value)}
                onBlur={(e) => {
                  if (
                    Number.isFinite(e.target.valueAsNumber) &&
                    e.target.valueAsNumber !== value
                  )
                    apply(e.target.valueAsNumber);
                }}
              />
            )}
          </label>
        );
      })}
    </>
  );
}
