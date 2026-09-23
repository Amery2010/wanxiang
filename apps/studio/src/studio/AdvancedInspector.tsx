import { sessionContracts } from "./library/utils";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { useEffect, useRef, useState } from "react";
import { useStore } from "zustand";
import { download, type Session } from "./session";
import type { Filters, Spec } from "./types";
import {
  componentRootIds,
  reportSocketPorts,
  runtimeCapability,
  runtimeLevels,
  resolvedCandidatePorts,
  sourceAsset,
  sourcePartNodes,
} from "./inspector-utils";

function applySpecParameters(spec: Spec, parameters: Record<string, unknown>) {
  if (spec.schema === "wx.part-build/1.0")
    return { ...spec, params: { ...spec.params, ...parameters } };
  return {
    ...spec,
    metadata: {
      ...spec.metadata,
      parameters: { ...spec.metadata?.parameters, ...parameters },
    },
  };
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object"
    ? (value as Record<string, unknown>)
    : {};
}

function portId(port: Record<string, unknown>, index: number) {
  return String(
    port.id || port.name || port.interface || `socket-${index + 1}`,
  );
}

function portLabel(port: Record<string, unknown>, index: number) {
  const id = portId(port, index);
  const interfaceId = port.interface ? ` · ${String(port.interface)}` : "";
  return `${id}${interfaceId}`;
}

function withAuthoredNormal(port: Record<string, unknown>) {
  const vector = (value: unknown): value is number[] =>
    Array.isArray(value) && value.length === 3 && value.every(Number.isFinite);
  const normal = port.normal || port.axis;
  if (!vector(port.position) || !vector(normal) || !vector(port.tangent))
    return null;
  return {
    ...port,
    position: port.position,
    tangent: port.tangent,
    normal,
  };
}

export function SourcePartTree({ session }: { session: Session }) {
  const s = useStore(session.store),
    asset = s.current,
    spec = s.spec;
  if (!asset || !s.data.parts) return null;
  const roots = componentRootIds(asset, spec),
    nodes = sourcePartNodes(roots, s.data.parts);
  if (!nodes.length) return null;
  return (
    <details className="source-tree">
      <summary>作者层可复用部件 · {nodes.length} 个定义</summary>
      <p className="small muted">
        点击可独立预览、调参和导出。共享来源只统计一次。
      </p>
      {nodes.map((node) => {
        const target = sourceAsset(node.id, s.data.parts!, s.data.assets);
        return (
          <button
            type="button"
            className="source-row"
            data-source-part={node.id}
            key={node.id}
            style={{ marginLeft: `${node.depth * 12}px` }}
            disabled={!target || s.busy}
            onClick={() => target && void session.select(target)}
          >
            <span>L{node.level}</span>
            <strong>{node.name}</strong>
            <code>{node.id}</code>
          </button>
        );
      })}
    </details>
  );
}

export function RuntimeInspector({ session }: { session: Session }) {
  const s = useStore(session.store),
    asset = s.current,
    spec = s.spec,
    [socket, setSocket] = useState(""),
    [summary, setSummary] = useState(""),
    search = useRef<AbortController | null>(null);
  useEffect(() => () => search.current?.abort(), [asset?.id]);
  if (!asset || !spec) return null;
  const runtime = runtimeCapability(asset, spec),
    matcher = sessionContracts(s.data),
    ports = matcher
      ? reportSocketPorts(asset).filter((port) => {
          const interfaceId = port.interface;
          if (port.enabled === false || typeof interfaceId !== "string")
            return false;
          try {
            return Boolean(matcher.registry()[interfaceId]);
          } catch {
            return false;
          }
        })
      : [],
    levels = runtimeLevels(asset, spec);
  const collision = runtime.collision,
    interaction = runtime.interaction,
    lod = runtime.lod;
  const collisionType = runtime.collision_type;
  const collisionLabel =
    typeof collisionType === "string"
      ? collisionType
      : collision && typeof collision === "object"
        ? String((collision as Record<string, unknown>).type || "已定义")
        : collision === true
          ? "已定义"
          : "未定义";
  const values =
    spec.schema === "wx.part-build/1.0"
      ? spec.params || {}
      : spec.metadata?.parameters || {};
  const activeLevel = levels.find((level) => {
    const parameters = asRecord(level.parameters);
    return Object.entries(parameters).every(
      ([key, value]) => values[key] === value,
    );
  });
  const selectedPort = ports.find(
    (port, index) => portId(port, index) === socket,
  );
  const setLibraryCompatibility = (ids: string[] | null) => {
    const patch = {
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
      compatibleIds: ids,
    } as unknown as Partial<Filters>;
    s.setFilters(patch);
  };
  const findCompatible = async () => {
    if (!selectedPort) {
      setSummary("请先选择一个连接点。");
      return;
    }
    const semantic = (
      globalThis as unknown as {
        WXSemantic?: Record<string, unknown>;
      }
    ).WXSemantic;
    if (!matcher || !semantic) {
      setLibraryCompatibility([]);
      setSummary("兼容查询不可用：接口契约运行时未加载。");
      return;
    }
    const found: string[] = [],
      sourcePort = withAuthoredNormal(selectedPort),
      sourceInterface = selectedPort.interface;
    if (!sourcePort || typeof sourceInterface !== "string") {
      setLibraryCompatibility([]);
      setSummary("当前连接点没有版本化接口，无法查找兼容部件。");
      return;
    }
    search.current?.abort();
    const controller = new AbortController();
    search.current = controller;
    setSummary("正在加载候选部件配置…");
    for (let candidate of s.data.assets) {
      const advertised = candidate.runtime?.interfaces;
      if (!Array.isArray(advertised) || !advertised.includes(sourceInterface))
        continue;
      try {
        if (!candidate.kit && !candidate.spec)
          candidate =
            (await session.ensureAsset(candidate.id, controller.signal)) ||
            candidate;
      } catch (error) {
        if (controller.signal.aborted) return;
        setSummary(
          `兼容查询未完成：${error instanceof Error ? error.message : String(error)}。请重试。`,
        );
        return;
      }
      if (controller.signal.aborted) return;
      const candidateSpec = candidate.kit || candidate.spec || null;
      const currentMatcher = sessionContracts(session.store.getState().data);
      const candidatePorts = resolvedCandidatePorts(
        candidateSpec,
        session.store.getState().data.parts || {},
      );
      if (
        candidatePorts.some((port) => {
          try {
            const candidatePort = withAuthoredNormal(port);
            return (
              candidatePort &&
              port.enabled !== false &&
              (candidateSpec?.part || Array.isArray(port.position)) &&
              currentMatcher?.compatible(sourcePort, candidatePort).compatible
            );
          } catch {
            return false;
          }
        })
      )
        found.push(candidate.id);
    }
    setLibraryCompatibility(found);
    setSummary(
      `${found.length} 个默认尺寸/轮廓兼容部件；装配时再次检查世界尺寸与方向。`,
    );
  };
  const applyLevel = (value: string) => {
    const level = levels.find((item) => String(item.level) === value);
    if (!level) return;
    const parameters = asRecord(level.parameters);
    void session.apply(applySpecParameters(spec, parameters));
  };
  const runtimeFile = `${asset.id}.collider-recipes.json`;
  return (
    <details className="runtime-inspector">
      <summary>游戏接口 · 碰撞 · LOD</summary>
      <p className="small muted">
        {collisionLabel} · {lod ? "参数化 LOD" : "未启用 LOD"} ·{" "}
        {String(runtime.motion || "静态")}
      </p>
      {!matcher && (
        <p className="small muted" role="status">
          兼容查询不可用：接口契约运行时未加载。
        </p>
      )}
      {ports.length > 0 && (
        <label>
          连接点
          <select
            id="mateSocket"
            aria-label="源连接点"
            value={socket}
            onChange={(event) => setSocket(event.target.value)}
          >
            <option value="">选择连接点</option>
            {ports.map((port, index) => (
              <option key={portId(port, index)} value={portId(port, index)}>
                {portLabel(port, index)}
              </option>
            ))}
          </select>
        </label>
      )}
      <Button
        id="findCompatible"
        onClick={findCompatible}
        disabled={!ports.length}
      >
        查找可拼接部件
      </Button>
      <Button
        id="clearCompatible"
        variant="outline"
        onClick={() => {
          setLibraryCompatibility(null);
          setSummary("已清除拼接筛选");
        }}
      >
        清除拼接筛选
      </Button>
      {summary && (
        <p id="mateSummary" className="small muted">
          {summary}
        </p>
      )}
      {levels.length > 0 && (
        <label>
          生成细节层级
          <select
            id="lodLevel"
            aria-label="LOD 层级"
            value={activeLevel ? String(activeLevel.level) : ""}
            onChange={(event) => applyLevel(event.target.value)}
            disabled={s.busy}
          >
            <option value="">选择 LOD</option>
            {levels.map((level, index) => (
              <option
                key={String(level.level ?? index)}
                value={String(level.level ?? index)}
              >
                LOD {String(level.level ?? index)} ·{" "}
                {String(level.name || level.label || "几何细节")}
              </option>
            ))}
          </select>
        </label>
      )}
      {interaction !== undefined &&
        interaction !== null &&
        interaction !== false && (
          <p className="small muted">
            交互：
            {String(
              asRecord(interaction).kind ||
                asRecord(interaction).event ||
                "已定义",
            )}
          </p>
        )}
      <Button
        id="colliderRecipeBtn"
        onClick={() => {
          try {
            download(
              JSON.stringify(session.runtime.runtimeSidecar(), null, 2),
              runtimeFile,
            );
          } catch (error) {
            s.notify(String(error));
          }
        }}
      >
        导出碰撞、交互与 LOD 配方
      </Button>
      <p className="small muted">
        配方需要游戏运行时适配器；LOD 会通过构建事务重新生成几何。
      </p>
    </details>
  );
}
export function AdvancedParameters({ session }: { session: Session }) {
  const s = useStore(session.store),
    [rigid, setRigid] = useState<Record<string, number>>({}),
    [playing, setPlaying] = useState(false),
    [clip, setClip] = useState(0),
    [query, setQuery] = useState(""),
    [insert, setInsert] = useState(""),
    [sizeDraft, setSizeDraft] = useState<number[] | null>(null);
  const k = s.spec,
    a = s.current;
  const size = k?.params?.size as number[] | undefined;
  const sizeKey = JSON.stringify(size ?? null);
  useEffect(() => {
    setSizeDraft(JSON.parse(sizeKey) as number[] | null);
  }, [sizeKey]);
  if (!k || !a) return null;
  const insertableParts = new Map<string, { name?: string }>(
    s.data.assets
      .filter(
        (asset) =>
          asset.family === "part" ||
          asset.category?.startsWith("part_") ||
          asset.kit?.schema === "wx.part-build/1.0",
      )
      .map((asset) => [asset.id, asset]),
  );
  for (const [id, part] of Object.entries(s.data.parts || {}))
    if (!insertableParts.has(id)) insertableParts.set(id, part);
  const statusRigid =
      s.runtimeStatus.rigidState &&
      typeof s.runtimeStatus.rigidState === "object"
        ? (s.runtimeStatus.rigidState as Record<string, number>)
        : {},
    hasStatusRigid = Object.prototype.hasOwnProperty.call(
      s.runtimeStatus,
      "rigidState",
    ),
    rigidValues = hasStatusRigid ? statusRigid : rigid,
    statusClip =
      typeof s.runtimeStatus.motionClip === "number"
        ? s.runtimeStatus.motionClip
        : clip,
    statusPlaying =
      typeof s.runtimeStatus.motionPlaying === "boolean"
        ? s.runtimeStatus.motionPlaying
        : playing;
  const controls = (k.metadata?.state_controls || []) as {
      id: string;
      title: string;
      min: number;
      max: number;
      step?: number;
      default?: number;
      unit?: string;
    }[],
    sizeValue = sizeDraft || size;
  const applyRigid = (next: Record<string, number>) => {
    try {
      session.runtime.explode(0);
      session.runtime.resetVisibility();
      session.runtime.applyRigidState(next);
      setRigid(next);
      setPlaying(false);
    } catch (e) {
      s.notify(String(e));
    }
  };
  return (
    <>
      {controls.length > 0 && (
        <section>
          <h4>刚性运动状态</h4>
          {controls.map((c) => (
            <label key={c.id}>
              {c.title}
              <output data-state-value={c.id}>
                {rigidValues[c.id] ?? c.default ?? 0} {c.unit || "°"}
              </output>
              <Input
                type="range"
                data-state={c.id}
                min={c.min}
                max={c.max}
                step={c.step || 1}
                value={rigidValues[c.id] ?? c.default ?? 0}
                onChange={(e) =>
                  applyRigid({
                    ...rigidValues,
                    [c.id]: Number(e.target.value),
                  })
                }
              />
            </label>
          ))}
          <Button id="stateReset" onClick={() => applyRigid({})}>
            复位状态
          </Button>
          <Button
            id="stateExport"
            onClick={() =>
              void session.runtime
                .exportPose()
                .then((buffer) =>
                  download(
                    buffer,
                    a.id + ".rigid-state.glb",
                    "model/gltf-binary",
                  ),
                )
                .catch((e) => s.notify(String(e)))
            }
          >
            导出当前姿态
          </Button>
          <p>更新实际节点，不重建网格；姿态导出不包含动画。</p>
        </section>
      )}
      {size && (
        <section>
          <h4>尺寸 · 米</h4>
          <div className="scene-vector">
            {sizeValue?.map((n, axis) => (
              <label key={axis}>
                {"XYZ"[axis]}
                <Input
                  data-size-axis={axis}
                  type="number"
                  min={0.005}
                  max={100}
                  step={0.05}
                  value={n}
                  onChange={(e) => {
                    const value = e.target.valueAsNumber;
                    if (!Number.isFinite(value)) return;
                    const next = [...(sizeValue || [1, 1, 1])];
                    next[axis] = value;
                    setSizeDraft(next);
                  }}
                />
              </label>
            ))}
            <Button
              id="sizeApplyBtn"
              disabled={
                s.busy ||
                !sizeValue ||
                !size ||
                sizeValue.every((value, index) => value === size[index])
              }
              onClick={() =>
                sizeValue &&
                void session.apply({
                  ...k,
                  params: { ...k.params, size: [...sizeValue] },
                })
              }
            >
              应用 XYZ
            </Button>
          </div>
        </section>
      )}
      {["toon", "voxel"].includes(String(k.style)) && (
        <label>
          {k.style === "toon" ? "轮廓柔化程度" : "方块分辨率"}
          <Input
            id={k.style === "toon" ? "roundnessInput" : "voxelInput"}
            key={JSON.stringify(k)}
            type="number"
            min={k.style === "toon" ? 0 : 6}
            max={k.style === "toon" ? 1 : 40}
            step={k.style === "toon" ? 0.01 : 1}
            defaultValue={
              k.style === "toon"
                ? (k.params?.roundness ?? k.metadata?.roundness ?? 0.3)
                : (k.params?.voxel_resolution ??
                  k.metadata?.voxel_resolution ??
                  16)
            }
            onBlur={(e) => {
              if (Number.isFinite(e.target.valueAsNumber))
                void session.apply({
                  ...k,
                  [k.schema === "wx.part-build/1.0" ? "params" : "metadata"]: {
                    ...(k.schema === "wx.part-build/1.0"
                      ? k.params
                      : k.metadata),
                    [k.style === "toon" ? "roundness" : "voxel_resolution"]:
                      e.target.valueAsNumber,
                  },
                });
            }}
          />
        </label>
      )}
      {session.runtime.motionInfo().length > 0 && (
        <section>
          <h4>节点动画</h4>
          <label>
            动画片段
            <select
              id="motionClip"
              value={statusClip}
              onChange={(e) => {
                const nextClip = Number(e.target.value);
                setClip(nextClip);
                session.runtime.playMotion(false, nextClip);
                session.runtime.poseTime(0);
                setPlaying(false);
              }}
            >
              {session.runtime.motionInfo().map((motion, index) => (
                <option key={index} value={index}>
                  {motion.name}
                </option>
              ))}
            </select>
          </label>
          <Button
            id="motionPlayBtn"
            onClick={() => {
              session.runtime.playMotion(!statusPlaying, statusClip);
              setPlaying(!statusPlaying);
            }}
          >
            {statusPlaying ? "暂停动画" : "播放动画"}
          </Button>
          <label>
            动画时间
            <Input
              id="motionScrub"
              type="range"
              min={0}
              max={session.runtime.motionInfo()[statusClip]?.duration || 0}
              step={0.01}
              value={Math.min(
                session.runtime.motionInfo()[statusClip]?.duration || 0,
                Math.max(0, Number(s.runtimeStatus.motionTime || 0)),
              )}
              aria-label="动画时间"
              onChange={(e) => {
                session.runtime.poseTime(e.target.valueAsNumber);
                setPlaying(false);
              }}
            />
            <output data-motion-time>
              {Number(s.runtimeStatus.motionTime || 0).toFixed(2)} /{" "}
              {(
                session.runtime.motionInfo()[statusClip]?.duration || 0
              ).toFixed(2)}{" "}
              s
            </output>
          </label>
        </section>
      )}
      <RuntimeInspector session={session} />
      {s.data.parts && (k.schema === "wx.part-build/1.0" || k.instances) && (
        <details>
          <summary>插入组件到当前装配</summary>
          <Input
            id="insertQuery"
            placeholder="搜索组件名称或 ID"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <select
            id="insertPart"
            aria-label="插入组件"
            value={insert}
            onChange={(e) => setInsert(e.target.value)}
          >
            <option value="">选择组件</option>
            {[...insertableParts.entries()]
              .filter(([id, p]) =>
                [id, p.name]
                  .join(" ")
                  .toLowerCase()
                  .includes(query.toLowerCase()),
              )
              .slice(0, 100)
              .map(([id, p]) => (
                <option key={id} value={id}>
                  {String(p.name || id)}
                </option>
              ))}
          </select>
          <Button
            id="insertPartBtn"
            disabled={!insert || s.busy}
            onClick={() => {
              const instanceId = "insert_" + Date.now().toString(36);
              if (k.schema === "wx.part-build/1.0") {
                void session.apply({
                  schema: "wx.assembly/1.0",
                  id: k.id || a.id,
                  name: k.name || a.name,
                  style: k.style,
                  instances: [
                    {
                      id: "source",
                      part: k.part,
                      params: { ...k.params },
                    },
                    { id: instanceId, part: insert, position: [2, 0, 0] },
                  ],
                });
              } else {
                void session.apply({
                  ...k,
                  instances: [
                    ...(k.instances || []),
                    { id: instanceId, part: insert, position: [2, 0, 0] },
                  ],
                });
              }
            }}
          >
            插入并预览
          </Button>
        </details>
      )}
      <details id="derivedStylePanel">
        <summary>高级派生与风格说明</summary>
        <p className="small muted">
          高级派生会重新生成几何。像素派生使用本地最近邻纹理与方块分辨率，适合需要明确像素风格的资产。
        </p>
        <Button
          data-kit-style="voxel"
          aria-pressed={k.style === "voxel"}
          variant={k.style === "voxel" ? "secondary" : "outline"}
          disabled={s.busy}
          onClick={() => void session.apply({ ...k, style: "voxel" })}
        >
          像素派生
        </Button>
      </details>
    </>
  );
}
export function StructureControls({ session }: { session: Session }) {
  const s = useStore(session.store),
    [selected, setSelected] = useState(""),
    [explode, setExplode] = useState(0);
  const k = s.spec;
  if (!k) return null;
  const instances = (k.instances || []) as Spec[],
    item = instances.find((i) => i.id === selected);
  return (
    <>
      <label>
        真实节点爆炸视图
        <Input
          id="explodeInput"
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={explode}
          onChange={(e) => {
            setExplode(Number(e.target.value));
            session.runtime.explode(Number(e.target.value));
          }}
        />
      </label>
      <Button
        id="restorePartsBtn"
        onClick={() => {
          setExplode(0);
          session.runtime.explode(0);
          session.runtime.resetVisibility();
        }}
      >
        复位全部零件
      </Button>
      <select
        aria-label="选择零件实例"
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
      >
        <option value="">选择零件实例</option>
        {((s.current?.bom || instances) as Spec[]).map((row, index) => (
          <option
            key={String(row.instance || row.id || index)}
            value={String(row.instance || row.id)}
          >
            {String(row.name || row.instance || row.id)}
          </option>
        ))}
      </select>
      <Button
        id="isolatePartBtn"
        disabled={!selected}
        onClick={() => session.runtime.isolateNode(selected)}
      >
        只显示选中
      </Button>
      {item && (
        <section>
          <h4>组件变换</h4>
          {(["position", "rotation", "scale"] as const).map((kind) => (
            <fieldset key={kind} disabled={!!item.attach}>
              <legend>{kind}</legend>
              <div className="scene-vector">
                {(
                  (item[kind] || [
                    kind === "scale" ? 1 : 0,
                    kind === "scale" ? 1 : 0,
                    kind === "scale" ? 1 : 0,
                  ]) as number[]
                ).map((value, axis) => (
                  <label key={axis}>
                    {"XYZ"[axis]}
                    <Input
                      data-trs={kind}
                      type="number"
                      defaultValue={value}
                      key={value}
                      onBlur={(e) => {
                        const n = e.target.valueAsNumber;
                        if (!Number.isFinite(n) || n === value) return;
                        const next = structuredClone(k),
                          i = next.instances?.find(
                            (row: { id: string }) => row.id === selected,
                          );
                        if (!i) return;
                        i[kind] = [...(item[kind] || [0, 0, 0])];
                        i[kind][axis] = n;
                        void session.apply(next);
                      }}
                    />
                  </label>
                ))}
              </div>
            </fieldset>
          ))}
          <label>
            组件材质
            <select
              id="instanceMaterial"
              value={String(item.material || "")}
              onChange={(e) => {
                const next = structuredClone(k),
                  i = next.instances?.find(
                    (row: { id: string }) => row.id === selected,
                  );
                if (!i) return;
                if (e.target.value) i.material = e.target.value;
                else delete i.material;
                void session.apply(next);
              }}
            >
              <option value="">继承材质</option>
              {(s.data.materials || []).map((m) => (
                <option key={String(m.id)} value={String(m.id)}>
                  {String(m.name || m.id)}
                </option>
              ))}
            </select>
          </label>
        </section>
      )}
      <Button
        onClick={() =>
          download(
            JSON.stringify(session.runtime.runtimeSidecar(), null, 2),
            (s.current?.id || "asset") + ".runtime.json",
          )
        }
      >
        下载碰撞与交互配方
      </Button>
    </>
  );
}
