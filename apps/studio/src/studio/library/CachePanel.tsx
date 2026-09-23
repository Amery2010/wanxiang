import { Button } from "../../ui/button";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  Database,
  HardDrive,
  LoaderCircle,
  RefreshCw,
  Trash2,
  X,
} from "lucide-react";
import type { CachePanelProps } from "./types";
import { formatCount, readNumber, readString } from "./utils";
import { LibraryModal } from "./modal";

export function CachePanel({ cache, assetId, open, onClose }: CachePanelProps) {
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [confirmClear, setConfirmClear] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);
  const refresh = useCallback(async () => {
    if (!cache) return;
    setError("");
    try {
      setStats(await cache.stats());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  }, [cache]);
  useEffect(() => {
    if (!open) return;
    setConfirmClear(false);
    setNotice("");
    void refresh();
    return undefined;
  }, [onClose, open, refresh]);

  if (!open) return null;
  const clean = async (options: Record<string, unknown>) => {
    if (!cache || busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await cache.clean(options);
      await refresh();
      setNotice(
        options.asset
          ? "当前资产缓存已清除。"
          : options.stale
            ? "失效缓存已清除。"
            : "全部构建缓存已清除。",
      );
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };
  return (
    <LibraryModal
      title="构建缓存"
      onClose={onClose}
      initialFocus={closeRef}
      className="library-side-dialog"
    >
      <header className="library-dialog-header">
        <div>
          <span className="library-overline">本地存储</span>
          <h2 id="library-cache-title">构建缓存</h2>
          <p>定义仍是唯一来源，删除缓存不会删除配方。</p>
        </div>
        <Button
          ref={closeRef}
          type="button"
          className="library-icon-button"
          aria-label="关闭缓存面板"
          onClick={onClose}
        >
          <X size={17} />
        </Button>
      </header>
      {!cache && (
        <div className="library-dialog-empty">
          <Database size={22} />
          当前运行时尚未连接缓存。
        </div>
      )}
      {cache && (
        <>
          <div className="library-cache-summary">
            <div>
              <span>
                <Database size={15} />
                内存缓存
              </span>
              <strong>
                {formatCount(readNumber(stats?.memory_entries))} 项
              </strong>
              <small>{formatBytes(stats?.memory_bytes)}</small>
            </div>
            <div>
              <span>
                <HardDrive size={15} />
                持久缓存
              </span>
              <strong>{formatCount(readNumber(stats?.disk_entries))} 项</strong>
              <small>{formatBytes(stats?.disk_bytes)}</small>
            </div>
          </div>
          <div className="library-cache-meta">
            <span>存储模式</span>
            <strong>{readString(stats?.mode, "读取中…")}</strong>
            <span>上限</span>
            <strong>
              {formatBytes(stats?.memory_budget)} /{" "}
              {formatBytes(stats?.disk_budget)}
            </strong>
          </div>
          <div className="library-cache-actions">
            <Button
              type="button"
              className="library-button library-button--outline"
              disabled={busy}
              onClick={() => void refresh()}
            >
              <RefreshCw size={14} />
              刷新
            </Button>
            <Button
              type="button"
              className="library-button library-button--quiet"
              disabled={busy}
              onClick={() => void clean({ stale: true })}
            >
              <Trash2 size={14} />
              清除失效缓存
            </Button>
            {assetId && (
              <Button
                type="button"
                className="library-button library-button--quiet"
                disabled={busy}
                onClick={() => void clean({ asset: assetId })}
              >
                <Trash2 size={14} />
                清除当前资产
              </Button>
            )}
            <Button
              type="button"
              className="library-button library-button--danger"
              disabled={busy || confirmClear}
              onClick={() => setConfirmClear(true)}
            >
              <Trash2 size={14} />
              清除全部缓存
            </Button>
          </div>
          {confirmClear && (
            <div
              className="library-cache-confirm"
              role="alertdialog"
              aria-label="确认清除全部缓存"
              aria-describedby="library-cache-confirm-copy"
            >
              <p id="library-cache-confirm-copy">
                确定要清除全部构建缓存吗？这不会删除资产定义或场景源文件。
              </p>
              <div className="library-cache-confirm-actions">
                <Button
                  type="button"
                  className="library-button library-button--outline"
                  disabled={busy}
                  onClick={() => setConfirmClear(false)}
                >
                  取消
                </Button>
                <Button
                  type="button"
                  className="library-button library-button--danger"
                  disabled={busy}
                  onClick={() => {
                    setConfirmClear(false);
                    void clean({});
                  }}
                >
                  {busy && <LoaderCircle size={14} className="library-spin" />}
                  确认清除
                </Button>
              </div>
            </div>
          )}
          <p className="library-cache-note">
            file://、隐私模式或存储配额限制可能禁用持久缓存；此时继续使用内存。浏览器重载即可丢弃内存模型。
          </p>
        </>
      )}
      {notice && (
        <p className="library-dialog-success" role="status" aria-live="polite">
          {notice}
        </p>
      )}
      {error && (
        <p className="library-dialog-error" role="alert">
          {error}
        </p>
      )}
    </LibraryModal>
  );
}

function formatBytes(value: unknown): string {
  const bytes = readNumber(value);
  if (!bytes) return "0 B";
  if (bytes < 1024) return `${Math.round(bytes)} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
