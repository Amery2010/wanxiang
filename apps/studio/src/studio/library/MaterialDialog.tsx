import { Button } from "../../ui/button";
import { useRef } from "react";
import { Download, FileJson, X } from "lucide-react";
import type { MaterialDialogProps } from "./types";
import { LibraryModal } from "./modal";
import { materialName, materialPreview, readString } from "./utils";

export function MaterialDialog({ material, onClose }: MaterialDialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null);
  if (!material) return null;
  const record =
    material.record && typeof material.record === "object"
      ? material.record
      : material;
  const preview = materialPreview(material);
  const palette = readString((record as { kind?: unknown }).kind) === "palette";
  return (
    <LibraryModal
      title="材质详情"
      onClose={onClose}
      initialFocus={closeRef}
      className="library-compare-dialog library-material-dialog"
    >
      <header className="library-dialog-header">
        <div>
          <span className="library-overline">材质角色</span>
          <h2 id="library-material-title">{materialName(material)}</h2>
          <p>
            {palette
              ? "纯色材质参数（没有伪造贴图）"
              : "原创表面纹理 · 可平铺 · GLB 内嵌"}
          </p>
        </div>
        <Button
          ref={closeRef}
          type="button"
          className="library-icon-button"
          aria-label="关闭材质详情"
          onClick={onClose}
        >
          <X size={17} />
        </Button>
      </header>
      <div className="library-material-content">
        <div className="library-material-preview">
          {preview ? (
            <img src={preview} alt={`${materialName(material)}预览`} />
          ) : (
            <div aria-hidden="true">
              <FileJson size={32} />
            </div>
          )}
          <p>
            {palette
              ? "颜色与参数会在导出时保留。"
              : "预览来源来自当前材质记录，未生成额外替代贴图。"}
          </p>
        </div>
        <div className="library-material-details">
          <dl>
            <dt>粗糙度</dt>
            <dd>{readMetric(record, "roughnessFactor")}</dd>
            <dt>金属度</dt>
            <dd>{readMetric(record, "metallicFactor")}</dd>
            <dt>采样</dt>
            <dd>
              {readString(
                (record as { sampler?: { wrapS?: unknown } }).sampler?.wrapS,
                "COLOR FACTOR",
              )}
            </dd>
            <dt>透明模式</dt>
            <dd>
              {readString(
                (record as { alphaMode?: unknown }).alphaMode,
                "OPAQUE",
              )}
            </dd>
          </dl>
          <p className="library-material-note">
            Lowpoly
            使用原创切面与顶点色；布料、金属、橡胶、玻璃与发光保持不同的材质角色。
          </p>
          <Button
            type="button"
            className="library-button library-button--primary"
            onClick={() => downloadMaterial(material)}
          >
            <Download size={14} />
            下载当前材质 JSON
          </Button>
          <Button
            type="button"
            className="library-button library-button--quiet"
            onClick={() =>
              downloadMaterialRecord(record, `${material.id}-source.json`)
            }
          >
            <FileJson size={14} />
            下载来源记录
          </Button>
        </div>
      </div>
    </LibraryModal>
  );
}

function readMetric(record: object, key: string): string {
  const value = (record as Record<string, unknown>)[key];
  return typeof value === "number" ? value.toFixed(3) : "—";
}

function downloadMaterial(material: object & { id?: string }) {
  downloadMaterialRecord(material, `${material.id ?? "material"}.json`);
}

function downloadMaterialRecord(value: object, name: string) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }),
  );
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
