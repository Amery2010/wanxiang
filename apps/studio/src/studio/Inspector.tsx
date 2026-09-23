import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Button } from "../ui/button";
import { useState } from "react";
import { useStore } from "zustand";
import { Star } from "lucide-react";
import { download, type Session } from "./session";
import {
  AdvancedParameters,
  SourcePartTree,
  StructureControls,
} from "./AdvancedInspector";
import { ReviewParameters } from "./ReviewParameters";
import { SceneProperties } from "./Scene";
import type { Spec } from "./types";
import {
  SemanticParameterFields,
  type InspectorParameters,
} from "./inspector-utils";
function JsonEditor({ session }: { session: Session }) {
  const s = useStore(session.store),
    [text, setText] = useState(JSON.stringify(s.spec, null, 2));
  return (
    <>
      <textarea
        id="kitEditor"
        aria-label="组合配方 JSON"
        value={text}
        onChange={(e) => setText(e.target.value)}
        spellCheck={false}
      />
      <Button
        id="kitApplyBtn"
        disabled={s.busy}
        onClick={() => {
          try {
            const spec: unknown = JSON.parse(text);
            if (!spec || typeof spec !== "object" || Array.isArray(spec))
              throw Error("配置必须为对象");
            void session.apply(spec as Spec);
          } catch (e) {
            s.notify(String(e));
          }
        }}
      >
        应用配置并实时预览
      </Button>
    </>
  );
}

function EvidenceStatus({
  session,
  report,
}: {
  session: Session;
  report: Record<string, unknown>;
}) {
  const s = useStore(session.store),
    evidence =
      report.evidence && typeof report.evidence === "object"
        ? (report.evidence as Record<string, unknown>)
        : {},
    fields: [string, unknown][] = [
      ["GLB 结构与重读", evidence.glb_boundary_validated],
      ["独立 trimesh 导入", evidence.independent_reader],
      ["CPU 多视图", evidence.cpu_preview],
      ["当前 WebGL 实际绘制", s.runtimeStatus.runtimeDrawn],
      ["Khronos 完整验证器", evidence.khronos_validator],
      ["美术人工批准", evidence.artistic_approval],
      ["目标项目运行时批准", evidence.target_project_approval],
    ];
  return (
    <section className="quality-evidence" aria-label="导出检查证据">
      {fields.map(([label, value]) => (
        <div className="quality-line" key={label}>
          <span>{label}</span>
          <strong className={value === true ? "yes" : "no"}>
            {value === true ? "已执行" : "未认证"}
          </strong>
        </div>
      ))}
      <dl>
        <dt>三角面</dt>
        <dd>{String(report.triangles ?? "—")}</dd>
        <dt>节点</dt>
        <dd>{String(report.nodes ?? "—")}</dd>
        <dt>材质</dt>
        <dd>{String(report.materials ?? "—")}</dd>
      </dl>
      <p className="small muted">
        结构检查和当前渲染状态用于审查证据；它们不代表美术或目标项目最终批准。
      </p>
      <details>
        <summary>查看原始检查报告</summary>
        <pre>{JSON.stringify(report, null, 2)}</pre>
      </details>
    </section>
  );
}

function FoundationInfo({ asset }: { asset: import("./types").Asset }) {
  const level = asset.level || 0;
  const metadata =
    asset.metadata && typeof asset.metadata === "object"
      ? (asset.metadata as Record<string, unknown>)
      : {};
  const authored =
    typeof metadata.foundation_note === "string"
      ? metadata.foundation_note
    : level === 1
        ? "语义基础部件：保留作者参数与定位基准。"
        : level === 2
          ? "功能子装配：保留功能实例与安装接口。"
          : level === 3
            ? "完整资产：可追踪作者部件来源与导出结构。"
            : level === 4
              ? "可编辑场景：保留场景源配方与对象引用。"
              : "";
  if (!authored) return null;
  const source =
    typeof metadata.source === "string"
      ? metadata.source
      : typeof asset.provenance === "object" && asset.provenance
        ? "作者来源已记录"
        : "";
  return (
    <details className="foundation-note">
      <summary>{level <= 2 ? "基础能力说明" : "资产来源与能力"}</summary>
      <p>{authored}</p>
      {source && <p className="small muted">{source}</p>}
    </details>
  );
}
export function Inspector({ session }: { session: Session }) {
  const s = useStore(session.store),
    a = s.current,
    k = s.spec;
  if (!a) return <div className="empty-state">选择资产开始预览</div>;
  const part = k?.schema === "wx.part-build/1.0",
    schema = part
      ? s.data.parts?.[String(k?.part)]?.parameter_schema
      : k?.metadata?.parameter_schema;
  const sceneMode = s.filters.workspace === "scene" && a.level === 4,
    properties = (schema?.properties || {}) as InspectorParameters,
    values = (part ? k?.params : k?.metadata?.parameters) || {},
    r = a.report || {};
  const applyParam = (key: string, value: unknown) => {
    if (!k) return;
    void session.apply(
      part
        ? { ...k, params: { ...k.params, [key]: value } }
        : {
            ...k,
            metadata: {
              ...k.metadata,
              parameters: { ...values, [key]: value },
            },
          },
    );
  };
  return (
    <>
      <div className={`inspector-top${sceneMode ? " scene-inspector-top" : ""}`}>
        <small id="assetTypeLabel">
          {sceneMode ? "SCENE / 场景属性" : `L${a.level} / 属性检查器`}
        </small>
        <div className="asset-title-row">
          <h3 id="assetName">
            {sceneMode
              ? String(
                  (typeof k?.metadata?.scene === "object" &&
                    k.metadata.scene.title) ||
                    k?.name ||
                    a.name,
                )
              : a.name}
          </h3>
          {!sceneMode && (
            <Button
              id="favoriteCurrent"
              aria-label="收藏当前资产"
              aria-pressed={s.prefs.favorites.includes(a.id)}
              onClick={() =>
                s.setPrefs({
                  favorites: s.prefs.favorites.includes(a.id)
                    ? s.prefs.favorites.filter((id) => id !== a.id)
                    : [...s.prefs.favorites, a.id],
                })
              }
            >
              <Star
                fill={
                  s.prefs.favorites.includes(a.id) ? "currentColor" : "none"
                }
              />
            </Button>
          )}
        </div>
        <code id="assetId">{a.id}</code>
        {a.level === 4 && !sceneMode && (
          <Button
            id="editCurrentScene"
            onClick={() => s.setFilters({ workspace: "scene" })}
          >
            在工作台编辑场景
          </Button>
        )}
      </div>
      <Tabs
        value={s.tab}
        onValueChange={(tab) => session.store.setState({ tab })}
      >
        <TabsList id="inspectorTabs" aria-label="资产属性">
          {[
            ["parameters", "参数"],
            ["structure", "结构"],
            ["materials", "材质"],
            ["quality", "检查"],
            ["source", "源码"],
          ].map(([id, label]) => (
            <TabsTrigger
              key={id}
              id={`inspector-tab-${id}`}
              value={id}
              data-tab={id}
              aria-controls={`inspector-panel-${id}`}
            >
              {label}
            </TabsTrigger>
          ))}
        </TabsList>
        {(
          ["parameters", "structure", "materials", "quality", "source"] as const
        )
          .filter((id) => id !== s.tab)
          .map((id) => (
            <TabsContent
              key={id}
              value={id}
              id={`inspector-panel-${id}`}
              aria-labelledby={`inspector-tab-${id}`}
              forceMount
              hidden
            />
          ))}
        <TabsContent
          value={s.tab}
          id={`inspector-panel-${s.tab}`}
          aria-labelledby={`inspector-tab-${s.tab}`}
          className="inspector-tabpanel"
        >
          <div id="inspector" className="inspector-body">
            {s.filters.workspace === "scene" &&
            a.level === 4 &&
            s.tab === "parameters" ? (
              <SceneProperties session={session} />
            ) : s.tab === "parameters" ? (
              <>
                <FoundationInfo asset={a} />
                {(!k || !s.data.parts) && (
                  <ReviewParameters key={a.id} session={session} />
                )}
                {k && s.data.parts && (
                  <>
                    <h4>模型风格</h4>
                    <div className="styles">
                      {[
                        ["lowpoly", "Lowpoly"],
                        ["toon", "卡通"],
                      ].map(([id, label]) => (
                        <Button
                          key={id}
                          data-kit-style={id}
                          aria-pressed={k.style === id}
                          variant={k.style === id ? "secondary" : "outline"}
                          disabled={s.busy}
                          onClick={() =>
                            void session.apply({ ...k, style: id })
                          }
                        >
                          {label}
                        </Button>
                      ))}
                    </div>
                    <h4>结构参数</h4>
                    <SemanticParameterFields
                      properties={properties}
                      values={values}
                      disabled={s.busy}
                      onCommit={applyParam}
                    />
                    <AdvancedParameters key={a.id} session={session} />
                    <details>
                      <summary>装配 JSON / 组件与连接点</summary>
                      <JsonEditor key={JSON.stringify(k)} session={session} />
                    </details>
                    <div className="property-actions">
                      <Button
                        id="undoKitBtn"
                        disabled={!s.history.length || s.busy}
                        onClick={() => void session.undo()}
                      >
                        撤销
                      </Button>
                      <Button
                        id="redoKitBtn"
                        disabled={!s.future.length || s.busy}
                        onClick={() => void session.redo()}
                      >
                        重做
                      </Button>
                    </div>
                    <Button id="kitSpecBtn" onClick={() => session.save()}>
                      下载可复现配置 JSON
                    </Button>
                    <Button
                      id="kitCmdBtn"
                      onClick={() =>
                        s.notify(
                          `./wx kit build --spec ${a.id}${a.level === 4 ? ".scene.json" : ".json"} --out workspaces/my-kit`,
                        )
                      }
                    >
                      CLI 构建命令
                    </Button>
                  </>
                )}
                <dl>
                  <dt>实际三角面</dt>
                  <dd>{String(r.triangles ?? "—")}</dd>
                  <dt>骨骼 / 蒙皮</dt>
                  <dd>
                    {String(r.bones || 0)} / {String(r.skins || 0)}
                  </dd>
                </dl>
              </>
            ) : s.tab === "structure" ? (
              <>
                <h4>BOM / 可独立导出的零件</h4>
                <StructureControls key={a.id} session={session} />
                <SourcePartTree key={`source-${a.id}`} session={session} />
                <Button
                  id="bomBtn"
                  onClick={() =>
                    download(
                      JSON.stringify(a.bom || [], null, 2),
                      a.id + ".bom.json",
                    )
                  }
                >
                  下载物料清单 BOM
                </Button>
                {((a.bom || []) as Record<string, unknown>[]).map(
                  (row, index) => (
                    <div
                      className="source-row"
                      key={String(row.instance || index)}
                    >
                      <strong>{String(row.name || row.part)}</strong>
                      <code>{String(row.instance)}</code>
                      <Button
                        data-kit-node={String(row.instance)}
                        onClick={() => {
                          void session.runtime
                            .exportPart(String(row.instance))
                            .then((buffer) =>
                              download(
                                buffer,
                                String(row.instance) + ".glb",
                                "model/gltf-binary",
                              ),
                            )
                            .catch((e) => s.notify(String(e)));
                        }}
                      >
                        导出零件 GLB
                      </Button>
                    </div>
                  ),
                )}
                <details>
                  <summary>组件引用树</summary>
                  <pre>{JSON.stringify(k?.instances || [], null, 2)}</pre>
                </details>
              </>
            ) : s.tab === "materials" ? (
              <>
                <h4>模型实际使用的材质</h4>
                {[
                  ...new Set(
                    (r.mesh_stats || []).map((row: Record<string, unknown>) =>
                      String(row.material),
                    ),
                  ),
                ].map((name) => (
                  <Button
                    key={String(name)}
                    onClick={() =>
                      session.store.setState({
                        dialog: "material",
                        materialId: String(name),
                      })
                    }
                  >
                    {String(name)}
                  </Button>
                ))}
                <p>导出使用标准 GLB 材质；卡通分阶光照由工坊实时渲染。</p>
              </>
            ) : s.tab === "quality" ? (
              <>
                <h4>实际导出检查</h4>
                <EvidenceStatus session={session} report={r} />
                <Button
                  id="reportBtn"
                  onClick={() =>
                    download(JSON.stringify(r, null, 2), a.id + ".report.json")
                  }
                >
                  下载检查报告
                </Button>
                <Button
                  id="runtimePackBtn"
                  onClick={() =>
                    void session.runtime
                      .exportRuntime()
                      .then((blob) =>
                        download(
                          blob,
                          a.id + ".runtime.zip",
                          "application/zip",
                        ),
                      )
                      .catch((e) => s.notify(String(e)))
                  }
                >
                  游戏运行时 ZIP · 静态合批
                </Button>
                <Button
                  id="reexportBtn"
                  onClick={() =>
                    void session.runtime
                      .exportGLB(true)
                      .then((buffer) =>
                        download(
                          buffer,
                          a.id + ".reexport.glb",
                          "model/gltf-binary",
                        ),
                      )
                      .catch((e) => s.notify(String(e)))
                  }
                >
                  GLTFExporter 重导出
                </Button>
              </>
            ) : (
              <>
                <h4>版本化装配源文件</h4>
                <pre>{JSON.stringify(k || a.recipe || a.spec, null, 2)}</pre>
                <Button
                  id="kitOriginalBtn"
                  onClick={() =>
                    download(
                      JSON.stringify(
                        s.data.assets.find((x) => x.id === a.id)?.kit ||
                          k ||
                          a.recipe ||
                          a.spec,
                        null,
                        2,
                      ),
                      a.id + ".original.json",
                    )
                  }
                >
                  下载原始配方
                </Button>
              </>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </>
  );
}
