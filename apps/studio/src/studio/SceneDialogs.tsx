import { useMemo, useState, type ReactNode } from "react";
import { useStore } from "zustand";
import {
  Clock,
  Download,
  FolderOpen,
  Layers,
  Plus,
  Upload,
} from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { core, sceneAPI, type SceneDocument, type Spec } from "./types";
import type { Session } from "./session";

type Props = { session: Session };
type DialogProps = Props & { doc: SceneDocument; close(): void };
interface Draft {
  schema: "wx.scene-draft/1.0";
  saved: string;
  source: Spec;
}
const titles: Record<string, string> = {
  "new-scene": "新建场景",
  "name-group": "创建选择组",
  "delete-scene": "删除场景对象",
  "scene-source": "场景源文件与恢复",
  "scene-export": "导出场景子集",
  "scene-manage": "图层、分区与选择组",
  "scene-array": "创建对象阵列",
  "scene-align": "对齐与分布",
};

function NewSceneDialog({ session, close }: Props & { close(): void }) {
  const state = useStore(session.store);
  const [name, setName] = useState("未命名场景");
  const [template, setTemplate] = useState("empty");
  const [error, setError] = useState("");
  const templates = state.data.assets.filter(
    (asset) =>
      asset.level === 4 && (asset.dynamic || asset.kit) && !asset.local,
  );
  return (
    <form
      className="grid gap-5"
      onSubmit={(event) => {
        event.preventDefault();
        if (!name.trim()) {
          setError("请填写场景名称");
          return;
        }
        setError("");
        void session.newScene(name.trim(), template).then((ok) => {
          if (ok) close();
          else
            setError(
              session.store.getState().error || "无法创建场景，请稍后重试。",
            );
        });
      }}
    >
      <Field label="场景名称">
        <Input
          id="newSceneName"
          value={name}
          maxLength={80}
          autoFocus
          onChange={(event) => setName(event.target.value)}
        />
      </Field>
      <Choice
        id="newSceneTemplate"
        label="起始模板"
        value={template}
        onChange={setTemplate}
        options={[
          { value: "empty", label: "基础地台" },
          ...templates.map((asset) => ({
            value: asset.id,
            label: asset.name || asset.id,
          })),
        ]}
      />
      <p className="text-sm text-muted-foreground">
        创建可编辑的本地副本。场景以米为单位，基础地台放在锁定图层中。
      </p>
      <ErrorMessage error={error} />
      <Button id="newSceneCreate" type="submit" disabled={state.busy}>
        <Plus />
        {state.busy ? "正在创建…" : "创建场景"}
      </Button>
    </form>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="grid gap-2 text-sm">
      <span>{label}</span>
      {children}
    </label>
  );
}

function Choice({
  id,
  label,
  value,
  onChange,
  options,
}: {
  id: string;
  label: string;
  value: string;
  onChange(value: string): void;
  options: { value: string; label: string; disabled?: boolean }[];
}) {
  return (
    <div className="grid gap-2 text-sm">
      <Label htmlFor={id}>{label}</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id={id} className="w-full">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function ErrorMessage({ error }: { error: string }) {
  return error ? (
    <p
      role="alert"
      className="rounded-md bg-destructive/10 p-3 text-sm text-destructive"
    >
      {error}
    </p>
  ) : null;
}

function asDraft(value: unknown): Draft | null {
  if (!value || typeof value !== "object") return null;
  const record = value as Record<string, unknown>;
  if (
    record.schema !== "wx.scene-draft/1.0" ||
    typeof record.saved !== "string" ||
    !record.source ||
    typeof record.source !== "object"
  )
    return null;
  return record as unknown as Draft;
}

function SourceDialog({ session, close }: DialogProps) {
  const state = useStore(session.store);
  const [, refresh] = useState(0);
  const [error, setError] = useState("");
  const key = `wanxiang.scene.v35.${state.current?.id}`;
  const recovery = (() => {
    const latest = asDraft(core().storage(key, null));
    const raw = core().storage<unknown>(`${key}.versions`, []);
    const versions = Array.isArray(raw)
      ? raw.map(asDraft).filter((item): item is Draft => item !== null)
      : [];
    return { latest, versions };
  })();
  async function restore(source: Spec) {
    setError("");
    try {
      sceneAPI().normalize(source);
      if (await session.apply(source)) close();
      else
        setError(
          session.store.getState().error || "场景未应用，原场景保持不变。",
        );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    }
  }
  return (
    <div className="grid gap-5">
      <p className="text-sm text-muted-foreground">
        源 JSON
        保留对象引用、变换、图层、分区与选择组。浏览器草稿不替代下载备份。
      </p>
      <div className="flex flex-wrap gap-2">
        <Button
          id="sourceDownload"
          onClick={() => session.save()}
          disabled={state.busy}
        >
          <Download />
          下载场景 JSON
        </Button>
        <Button
          id="sourceCheckpoint"
          variant="outline"
          disabled={state.busy}
          onClick={() => {
            session.checkpoint();
            refresh((value) => value + 1);
          }}
        >
          <Clock />
          保存本地检查点
        </Button>
      </div>
      <div className="grid gap-2 rounded-lg border border-dashed p-4">
        <Label htmlFor="sceneImport">
          <Upload className="size-4" />
          载入场景 JSON
        </Label>
        <Input
          id="sceneImport"
          type="file"
          accept=".json,application/json"
          disabled={state.busy}
          onChange={(event) => {
            const file = event.currentTarget.files?.[0];
            event.currentTarget.value = "";
            if (!file) return;
            if (file.size > 1_000_000) {
              setError("场景文件超过 1 MB");
              return;
            }
            void file
              .text()
              .then((text) => restore(JSON.parse(text) as Spec))
              .catch((cause: unknown) =>
                setError(
                  cause instanceof Error ? cause.message : String(cause),
                ),
              );
          }}
        />
      </div>
      <section className="grid gap-3">
        <h3 className="font-medium">本地恢复</h3>
        {recovery.latest ? (
          <>
            <p className="text-sm text-muted-foreground">
              最新草稿：{new Date(recovery.latest.saved).toLocaleString()}
            </p>
            <Button
              id="sourceRecover"
              variant="outline"
              disabled={state.busy}
              onClick={() => void restore(recovery.latest!.source)}
            >
              <FolderOpen />
              恢复最新草稿
            </Button>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">
            当前没有可读取的本地草稿。浏览器禁用存储时请下载源文件。
          </p>
        )}
        {recovery.versions.map((version, index) => (
          <Button
            key={`${version.saved}-${index}`}
            variant="outline"
            data-version={index}
            disabled={state.busy}
            onClick={() => void restore(version.source)}
            className="justify-between"
          >
            <span>{new Date(version.saved).toLocaleString()}</span>
            <span>恢复检查点</span>
          </Button>
        ))}
      </section>
      <p className="text-xs text-muted-foreground">
        载入后生成真实模型。校验或构建失败时保留原场景；成功后可撤销。
      </p>
      <ErrorMessage error={error} />
    </div>
  );
}

function ExportDialog({ session, doc, close }: DialogProps) {
  const state = useStore(session.store);
  const [scope, setScope] = useState(
    state.selection.length ? "selected" : "layer",
  );
  const [layer, setLayer] = useState(
    Object.keys(doc.metadata.scene.layers)[0] || "",
  );
  const [region, setRegion] = useState(
    Object.keys(doc.metadata.scene.regions)[0] || "",
  );
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);
  const scene = doc.metadata.scene;
  const query =
    scope === "selected"
      ? { ids: state.selection }
      : scope === "layer"
        ? { layer }
        : { region };
  return (
    <div className="grid gap-5">
      <p className="text-sm text-muted-foreground">
        导出可见对象的 GLB 与对应 JSON，保留世界位置，并自动包含依赖祖先。
      </p>
      <Choice
        id="exportScope"
        label="导出范围"
        value={scope}
        onChange={setScope}
        options={[
          {
            value: "selected",
            label: `所选对象 (${state.selection.length})`,
            disabled: !state.selection.length,
          },
          { value: "layer", label: "指定图层" },
          { value: "region", label: "指定分区" },
        ]}
      />
      {scope === "layer" && (
        <Choice
          id="exportLayer"
          label="图层"
          value={layer}
          onChange={setLayer}
          options={Object.entries(scene.layers).map(([value, item]) => ({
            value,
            label: item.label,
          }))}
        />
      )}
      {scope === "region" && (
        <Choice
          id="exportRegion"
          label="分区"
          value={region}
          onChange={setRegion}
          options={Object.entries(scene.regions).map(([value, item]) => ({
            value,
            label: item.label,
          }))}
        />
      )}
      <ErrorMessage error={error} />
      <Button
        id="exportCommit"
        disabled={
          state.busy ||
          exporting ||
          (scope === "selected" && !state.selection.length)
        }
        onClick={() => {
          setError("");
          try {
            sceneAPI().subset(doc, query, session.catalog);
          } catch (cause) {
            setError(cause instanceof Error ? cause.message : String(cause));
            return;
          }
          setExporting(true);
          void session
            .exportSubset(query)
            .then((ok) => {
              if (ok) close();
              else
                setError(
                  session.store.getState().error || "导出失败，场景保持不变。",
                );
            })
            .finally(() => setExporting(false));
        }}
      >
        <Download />
        {exporting ? "正在生成导出…" : "导出 GLB + JSON"}
      </Button>
    </div>
  );
}

function ManageDialog({ session, doc }: DialogProps) {
  const busy = useStore(session.store, (state) => state.busy);
  const [layerLabel, setLayerLabel] = useState("新图层");
  const [regionLabel, setRegionLabel] = useState("");
  const [error, setError] = useState("");
  const scene = doc.metadata.scene;
  async function command(value: Record<string, unknown>) {
    setError("");
    if (!(await session.command(value)))
      setError(session.store.getState().error || "修改未应用。");
  }
  return (
    <div className="grid gap-6">
      <section className="grid gap-3">
        <h3 className="flex items-center gap-2 font-medium">
          <Layers className="size-4" />
          图层管理
        </h3>
        {Object.entries(scene.layers).map(([id, layer]) => (
          <div className="flex gap-2" key={id}>
            <Input
              aria-label={`图层名称：${layer.label}`}
              defaultValue={layer.label}
              data-layer-label={id}
              disabled={busy || layer.locked}
              onBlur={(event) => {
                const label = event.currentTarget.value.trim();
                if (label && label !== layer.label)
                  void command({ type: "rename-layer", layer: id, label });
              }}
            />
            <Button
              variant="outline"
              data-layer-remove={id}
              disabled={
                busy || layer.locked || Object.keys(scene.layers).length < 2
              }
              onClick={() => {
                const target = Object.keys(scene.layers).find(
                  (other) => other !== id && !scene.layers[other].locked,
                );
                if (!target) {
                  setError("没有其他可用的解锁图层");
                  return;
                }
                void command({ type: "remove-layer", layer: id, target });
              }}
            >
              删除并转移
            </Button>
          </div>
        ))}
        <div className="flex gap-2">
          <Input
            aria-label="新图层名称"
            value={layerLabel}
            onChange={(event) => setLayerLabel(event.target.value)}
            maxLength={80}
          />
          <Button
            id="managerAddLayer"
            variant="outline"
            disabled={busy || !layerLabel.trim()}
            onClick={() =>
              void command({
                type: "add-layer",
                layer: `layer_${Date.now().toString(36)}`,
                label: layerLabel.trim(),
              })
            }
          >
            <Plus />
            新建图层
          </Button>
        </div>
      </section>
      <section className="grid gap-3">
        <h3 className="font-medium">场景分区</h3>
        <p className="text-sm text-muted-foreground">
          {Object.values(scene.regions)
            .map((region) => region.label)
            .join(" · ")}
        </p>
        <div className="flex gap-2">
          <Input
            id="newRegionLabel"
            aria-label="新分区名称"
            placeholder="新分区名称"
            value={regionLabel}
            onChange={(event) => setRegionLabel(event.target.value)}
            maxLength={80}
          />
          <Button
            id="managerAddRegion"
            variant="outline"
            disabled={busy || !regionLabel.trim()}
            onClick={() =>
              void command({
                type: "add-region",
                region: `region_${Date.now().toString(36)}`,
                label: regionLabel.trim(),
              })
            }
          >
            新增分区
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          在对象属性中分配分区后可单独导出。删除图层会转移对象，不删除模型。
        </p>
      </section>
      <section className="grid gap-3">
        <h3 className="font-medium">选择组</h3>
        {Object.entries(scene.groups).map(([id, group]) => (
          <div key={id} className="flex items-center gap-2">
            <span className="mr-auto">{group.label}</span>
            <Button
              variant="outline"
              disabled={busy}
              data-group-visible={id}
              onClick={() =>
                void command({
                  type: "group-visibility",
                  group: id,
                  visible: group.hidden,
                })
              }
            >
              {group.hidden ? "显示" : "隐藏"}
            </Button>
            <Button
              variant="outline"
              disabled={busy}
              data-group-lock={id}
              onClick={() =>
                void command({
                  type: "group-lock",
                  group: id,
                  locked: !group.locked,
                })
              }
            >
              {group.locked ? "解锁" : "锁定"}
            </Button>
          </div>
        ))}
        {!Object.keys(scene.groups).length && (
          <p className="text-sm text-muted-foreground">
            多选对象后使用“创建选择组”整理场景。
          </p>
        )}
      </section>
      <ErrorMessage error={error} />
    </div>
  );
}

function ArrayDialog({ session, doc, close }: DialogProps) {
  const state = useStore(session.store);
  const [mode, setMode] = useState("linear");
  const [values, setValues] = useState({
    count: "5",
    columns: "5",
    x: "2",
    z: "2",
    angle: "360",
  });
  const [error, setError] = useState("");
  async function create() {
    setError("");
    const count = Number(values.count),
      columns = Number(values.columns),
      x = Number(values.x),
      z = Number(values.z),
      angle = Number(values.angle);
    if (
      !state.selection.length ||
      !Number.isInteger(count) ||
      count < 1 ||
      count > 48 ||
      count * state.selection.length > 96 ||
      !Number.isInteger(columns) ||
      columns < 1 ||
      columns > 48 ||
      ![x, z, angle].every(Number.isFinite) ||
      x < 0.05 ||
      angle < 1 ||
      angle > 360
    ) {
      setError("请检查数量与间距；单次最多新增 96 个对象。");
      return;
    }
    const chosen = doc.instances.filter((item) =>
      state.selection.includes(item.id),
    );
    if (
      chosen.some(
        (item) =>
          item.attach ||
          (item.parent && item.parent !== "root") ||
          sceneAPI().descendants(doc, [item.id]).size > 1,
      )
    ) {
      setError("阵列只接受独立对象；有连接依赖的对象请使用普通复制。");
      return;
    }
    const commands = Array.from({ length: count }, (_, index) => {
      const k = index + 1,
        t = (((angle * Math.PI) / 180) * k) / (count + 1);
      return {
        type: "duplicate-many",
        ids: [...state.selection],
        withChildren: false,
        offset:
          mode === "radial"
            ? [x * Math.sin(t), 0, x * (Math.cos(t) - 1)]
            : [(k % columns) * x, 0, Math.floor(k / columns) * z],
      };
    });
    const before = new Set(doc.instances.map((item) => item.id));
    if (await session.command({ type: "batch", commands })) {
      const updated = sceneAPI().normalize(
        session.store.getState().spec!,
        session.catalog,
      );
      session.selectObjects(
        updated.instances
          .filter((item) => !before.has(item.id))
          .map((item) => item.id),
      );
      close();
    } else
      setError(
        session.store.getState().error || "阵列未创建，原场景保持不变。",
      );
  }
  return (
    <div className="grid gap-5">
      <p className="text-sm text-muted-foreground">
        复制资产引用，最多新增 96 个对象，整个阵列可一步撤销。
      </p>
      <Choice
        id="arrayMode"
        label="阵列类型"
        value={mode}
        onChange={setMode}
        options={[
          { value: "linear", label: "线性 / 网格" },
          { value: "radial", label: "环形（绕 Y 轴）" },
        ]}
      />
      <div className="grid grid-cols-2 gap-4">
        {(
          [
            ["count", "arrayCount", "副本数量（不含原件）", 1, 48, 1],
            ["columns", "arrayColumns", "每行个数", 1, 48, 1],
            ["x", "arrayX", "X 间距 / 环形半径 · m", 0.05, undefined, 0.25],
            ["z", "arrayZ", "Z 行间距 · m", undefined, undefined, 0.25],
            ["angle", "arrayAngle", "环形总角度 · °", 1, 360, 1],
          ] as const
        ).map(([key, id, label, min, max, step]) => (
          <Field key={key} label={label}>
            <Input
              id={id}
              type="number"
              value={values[key]}
              min={min}
              max={max}
              step={step}
              onChange={(event) =>
                setValues({ ...values, [key]: event.target.value })
              }
            />
          </Field>
        ))}
      </div>
      <ErrorMessage error={error} />
      <Button
        id="arrayCreate"
        disabled={state.busy || !state.selection.length}
        onClick={() => void create()}
      >
        <Plus />
        创建阵列
      </Button>
    </div>
  );
}

function AlignDialog({ session, close }: DialogProps) {
  const state = useStore(session.store);
  const [axis, setAxis] = useState("x");
  const [anchor, setAnchor] = useState("center");
  const [error, setError] = useState("");
  async function align(mode: string) {
    try {
      await session.runtime.align(axis, mode, anchor);
      close();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    }
  }
  return (
    <div className="grid gap-5">
      <p className="text-sm text-muted-foreground">
        依据真实网格的世界包围盒，对齐到第一个选中对象。等距分布保留首尾对象的中心。
      </p>
      <Choice
        id="alignAxis"
        label="方向"
        value={axis}
        onChange={setAxis}
        options={["x", "y", "z"].map((value) => ({
          value,
          label: `${value.toUpperCase()} 轴`,
        }))}
      />
      <Choice
        id="alignAnchor"
        label="对齐位置"
        value={anchor}
        onChange={setAnchor}
        options={[
          { value: "center", label: "中心" },
          { value: "min", label: "最小边" },
          { value: "max", label: "最大边" },
        ]}
      />
      <ErrorMessage error={error} />
      <div className="flex justify-end gap-2">
        <Button
          id="alignDistribute"
          variant="outline"
          disabled={state.busy || state.selection.length < 3}
          onClick={() => void align("distribute")}
        >
          等距分布
        </Button>
        <Button
          id="alignCommit"
          disabled={state.busy || state.selection.length < 2}
          onClick={() => void align("align")}
        >
          对齐所选
        </Button>
      </div>
    </div>
  );
}

function NameGroupDialog({ session, close }: DialogProps) {
  const state = useStore(session.store);
  const [label, setLabel] = useState("新选择组");
  const [error, setError] = useState("");
  return (
    <form
      className="grid gap-4"
      onSubmit={(event) => {
        event.preventDefault();
        if (!label.trim() || !state.selection.length) return;
        void session
          .command({ type: "group", ids: state.selection, label: label.trim() })
          .then((ok) => {
            if (ok) close();
            else setError(session.store.getState().error || "创建选择组失败");
          });
      }}
    >
      <p>
        将 {state.selection.length}{" "}
        个对象整理到一个选择组。选择组不改变模型父子关系或变换。
      </p>
      <Field label="选择组名称">
        <Input
          autoFocus
          value={label}
          maxLength={80}
          onChange={(event) => setLabel(event.target.value)}
        />
      </Field>
      <ErrorMessage error={error} />
      <Button
        type="submit"
        disabled={state.busy || !label.trim() || !state.selection.length}
      >
        创建选择组
      </Button>
    </form>
  );
}

function DeleteSceneDialog({ session, close }: DialogProps) {
  const state = useStore(session.store);
  const pending = session.getPendingDelete();
  return (
    <div className="grid gap-4">
      <p>
        将删除 {pending?.count || 0}{" "}
        个对象（包含依赖对象）。此操作完成后可以撤销。
      </p>
      <div className="property-actions">
        <Button variant="outline" onClick={close}>
          取消
        </Button>
        <Button
          variant="destructive"
          disabled={state.busy || !pending}
          onClick={() =>
            void session.confirmDelete().then((ok) => {
              if (ok) close();
            })
          }
        >
          确认删除
        </Button>
      </div>
      <ErrorMessage error={state.error} />
    </div>
  );
}

export function SceneDialogs({ session }: Props) {
  const state = useStore(session.store);
  const kind = state.dialog || "";
  const doc = useMemo(
    () =>
      state.spec && titles[kind] && kind !== "new-scene"
        ? sceneAPI().normalize(state.spec, session.catalog)
        : null,
    [state.spec, kind, session.catalog],
  );
  if (!titles[kind] || (!doc && kind !== "new-scene")) return null;
  const close = () => {
    if (kind === "delete-scene") session.cancelDelete();
    session.store.setState({ dialog: null });
  };
  const props = { session, doc: doc!, close };
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) close();
      }}
    >
      <DialogContent
        className="max-h-[88dvh] overflow-y-auto sm:max-w-xl"
        key={`${kind}-${state.current?.id}`}
      >
        <DialogHeader>
          <DialogTitle>{titles[kind]}</DialogTitle>
          <DialogDescription>
            编辑可追溯的场景源配方，保留原始资产定义。
          </DialogDescription>
        </DialogHeader>
        {kind === "new-scene" && (
          <NewSceneDialog session={session} close={close} />
        )}
        {kind === "scene-source" && <SourceDialog {...props} />}
        {kind === "scene-export" && <ExportDialog {...props} />}
        {kind === "scene-manage" && <ManageDialog {...props} />}
        {kind === "scene-array" && <ArrayDialog {...props} />}
        {kind === "scene-align" && <AlignDialog {...props} />}
        {kind === "name-group" && <NameGroupDialog {...props} />}
        {kind === "delete-scene" && <DeleteSceneDialog {...props} />}
      </DialogContent>
    </Dialog>
  );
}
