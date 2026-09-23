import { Button } from "../../ui/button";
import { useRef, type ReactNode } from "react";
import { Check, ChevronRight, Star, X } from "lucide-react";
import type { Asset } from "../types";
import type { CompareDialogProps } from "./types";
import { asLibraryAsset } from "./types";
import {
  assetHero,
  assetBytes,
  assetMaterials,
  assetName,
  assetNodes,
  assetTriangles,
  compareMetric,
  domainId,
  formatTriangles,
  getStudioCore,
} from "./utils";
import { LibraryModal } from "./modal";

export function CompareDialog({
  assets,
  open,
  onClose,
  onSelect,
}: CompareDialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null);
  if (!open) return null;
  const compareAssets = assets.slice(0, 4).map(asLibraryAsset);
  return (
    <LibraryModal
      title="比较选择的资源"
      onClose={onClose}
      initialFocus={closeRef}
      className="library-compare-dialog"
    >
      <header className="library-dialog-header">
        <div>
          <span className="library-overline">资产审查</span>
          <h2 id="library-compare-title">比较选择的资源</h2>
          <p>并排查看来源、层级与几何预算，再决定下一步。</p>
        </div>
        <Button
          ref={closeRef}
          type="button"
          className="library-icon-button"
          aria-label="关闭对比"
          onClick={onClose}
        >
          <X size={17} />
        </Button>
      </header>
      <div className="library-compare-table" role="table" aria-label="资源对比">
        <div
          className="library-compare-row library-compare-row--header"
          role="row"
        >
          <span role="columnheader">指标</span>
          {compareAssets.map((asset) => (
            <strong key={asset.id} role="columnheader">
              {assetName(asset)}
            </strong>
          ))}
        </div>
        <CompareRow label="预览">
          {compareAssets.map((asset) => (
            <div key={asset.id} className="library-compare-preview">
              <AssetPreview asset={asset} />
              <Button
                type="button"
                className="library-text-button"
                onClick={() => {
                  onSelect?.(asset);
                  onClose();
                }}
              >
                查看 <ChevronRight size={13} />
              </Button>
            </div>
          ))}
        </CompareRow>
        <CompareRow label="层级">
          {compareAssets.map((asset) => (
            <span key={asset.id}>{compareMetric(asset, "level")}</span>
          ))}
        </CompareRow>
        <CompareRow label="领域">
          {compareAssets.map((asset) => (
            <span key={asset.id}>
              {getStudioCore()?.domains.find(
                (domain) => domain.id === domainId(asset),
              )?.label ?? domainId(asset)}
            </span>
          ))}
        </CompareRow>
        <CompareRow label="三角面">
          {compareAssets.map((asset) => (
            <span key={asset.id}>{formatTriangles(assetTriangles(asset))}</span>
          ))}
        </CompareRow>
        <CompareRow label="语义节点">
          {compareAssets.map((asset) => (
            <span key={asset.id}>{formatValue(assetNodes(asset))}</span>
          ))}
        </CompareRow>
        <CompareRow label="材质映射">
          {compareAssets.map((asset) => (
            <span key={asset.id}>{formatValue(assetMaterials(asset))}</span>
          ))}
        </CompareRow>
        <CompareRow label="文件">
          {compareAssets.map((asset) => (
            <span key={asset.id}>{formatBytes(assetBytes(asset))}</span>
          ))}
        </CompareRow>
        <CompareRow label="源参数">
          {compareAssets.map((asset) => (
            <code key={asset.id}>{formatParameters(asset)}</code>
          ))}
        </CompareRow>
        <CompareRow label="动态">
          {compareAssets.map((asset) => (
            <span key={asset.id}>
              {asset.runtime?.motion && asset.runtime.motion !== "static"
                ? "可动结构"
                : "静态"}
            </span>
          ))}
        </CompareRow>
        <CompareRow label="来源">
          {compareAssets.map((asset) => (
            <span key={asset.id}>
              {asset.local
                ? "本地场景"
                : asset.game_expansion
                  ? "游戏扩展"
                  : "程序化目录"}
            </span>
          ))}
        </CompareRow>
      </div>
      <footer className="library-dialog-footer">
        <span>
          <Check size={14} /> 已选择 {compareAssets.length} 项
        </span>
        <Button
          type="button"
          className="library-button library-button--quiet"
          onClick={onClose}
        >
          完成
        </Button>
      </footer>
    </LibraryModal>
  );
}

function CompareRow({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="library-compare-row" role="row">
      <span role="rowheader">{label}</span>
      {children}
    </div>
  );
}

function AssetPreview({ asset }: { asset: Asset }) {
  const hero = assetHero(asLibraryAsset(asset));
  return hero ? (
    <img src={hero} alt="" width={96} height={96} loading="lazy" />
  ) : (
    <div className="library-compare-preview__empty">
      <Star size={20} />
    </div>
  );
}

function formatValue(value: number | null): string {
  return value === null ? "—" : value.toLocaleString("zh-CN");
}

function formatBytes(value: number | null): string {
  if (value === null) return "—";
  if (value >= 1024 * 1024) return `${(value / (1024 * 1024)).toFixed(2)} MB`;
  if (value >= 1024) return `${Math.round(value / 1024)} KB`;
  return `${value} B`;
}

function formatParameters(asset: Asset): string {
  const source = asset.kit ?? asset.spec;
  const params = source && typeof source === "object" ? source.params : null;
  return params && typeof params === "object" ? JSON.stringify(params) : "—";
}
