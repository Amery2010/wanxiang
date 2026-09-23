import { Button } from "../../ui/button";
import { useEffect, useRef, useState } from "react";
import {
  Ban,
  CheckCircle2,
  Clock3,
  LoaderCircle,
  ListChecks,
  RefreshCw,
  X,
} from "lucide-react";
import type { TasksPanelProps } from "./types";
import { formatCount, isRecord, readString, taskRecords } from "./utils";
import { createPortal } from "react-dom";

export function TasksPanel({
  tasks,
  open,
  onClose,
  onRetryFailed,
  progress,
}: TasksPanelProps) {
  const [snapshot, setSnapshot] = useState<unknown>(() => readSnapshot(tasks));
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!open) return;
    const refresh = () => setSnapshot(readSnapshot(tasks));
    refresh();
    const timer = window.setInterval(refresh, 300);
    return () => window.clearInterval(timer);
  }, [onClose, open, tasks]);

  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    return () => previous?.focus();
  }, [open]);
  if (!open) return null;
  const records = taskRecords(snapshot);
  const active = readArray(snapshot, "active");
  const queued = readArray(snapshot, "queued");
  const history = readArray(snapshot, "history");
  const latest = new Map(history.map((record) => [record.asset, record]));
  const failed = [...latest.values()].filter(
    (record) => record.phase === "failed",
  );
  const retryableCount =
    isRecord(snapshot) && typeof snapshot.retryableCount === "number"
      ? snapshot.retryableCount
      : failed.length;
  return createPortal(
    <section
      role="dialog"
      aria-modal="false"
      aria-labelledby="library-tasks-title"
      className="tasks-drawer library-dialog-content"
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          event.stopPropagation();
          onClose();
        }
      }}
    >
      <header className="library-dialog-header">
        <div>
          <span className="library-overline">后台队列</span>
          <h2 id="library-tasks-title">构建任务</h2>
          <p>
            {formatCount(active.length)} 进行中 · {formatCount(queued.length)}{" "}
            等待
          </p>
        </div>
        <Button
          ref={closeRef}
          type="button"
          className="library-icon-button"
          aria-label="关闭任务面板"
          onClick={onClose}
        >
          <X size={17} />
        </Button>
      </header>
      <div className="library-task-toolbar">
        <label className="text-xs">
          并发
          <select
            aria-label="构建并发数"
            disabled={!tasks?.setConcurrency}
            value={isRecord(snapshot) ? Number(snapshot.limit) || 1 : 1}
            onChange={(event) => {
              tasks?.setConcurrency?.(Number(event.target.value));
              setSnapshot(readSnapshot(tasks));
            }}
          >
            {[1, 2, 3].map((count) => (
              <option key={count} value={count}>
                {count}
              </option>
            ))}
          </select>
        </label>

        <Button
          type="button"
          className="library-button library-button--outline"
          onClick={() => tasks?.cancelAll()}
          disabled={!tasks || active.length + queued.length === 0}
        >
          <Ban size={14} />
          停止全部
        </Button>
        <Button
          type="button"
          variant="outline"
          disabled={
            !onRetryFailed ||
            !retryableCount ||
            active.length + queued.length > 0
          }
          onClick={onRetryFailed}
        >
          <RefreshCw size={14} />
          重试失败
        </Button>
      </div>
      {progress && (
        <div className="batch-progress" role="status">
          <progress max={progress.total} value={progress.completed} />
          <span>
            {progress.running
              ? "批量导出"
              : progress.cancelled
                ? "已取消"
                : "批次完成"}{" "}
            {progress.completed} / {progress.total} · 跳过 {progress.skipped} ·
            失败 {progress.failed}
          </span>
        </div>
      )}
      <div className="library-task-list">
        {!tasks && (
          <p className="library-dialog-empty">当前运行时尚未连接任务队列。</p>
        )}
        {records.length === 0 && tasks && (
          <p className="library-dialog-empty">
            <ListChecks size={20} />
            尚无任务。选择资源后，后台会按需生成真实网格。
          </p>
        )}
        {records
          .slice()
          .reverse()
          .map((record, index) => (
            <TaskRow
              key={`${readString(record.id, "task")}-${index}`}
              record={record}
              active={active.includes(record)}
              queued={queued.includes(record)}
              onCancel={
                tasks && typeof record.id === "number"
                  ? () => tasks.cancel(record.id as number)
                  : undefined
              }
            />
          ))}
      </div>
      {history.length > 0 && (
        <footer className="library-dialog-footer">
          <span>
            <CheckCircle2 size={14} />
            最近保留 {Math.min(history.length, 5)} 项记录
          </span>
          <span className="library-muted-label">本地按需构建</span>
        </footer>
      )}
    </section>,
    document.body,
  );
}

function TaskRow({
  record,
  active,
  queued,
  onCancel,
}: {
  record: Record<string, unknown>;
  active: boolean;
  queued: boolean;
  onCancel?(): void;
}) {
  const state = active
    ? "生成中"
    : queued
      ? "等待中"
      : { complete: "已完成", failed: "失败", cancelled: "已取消" }[
          readString(record.phase)
        ] || readString(record.phase, "已完成");
  return (
    <div className="library-task-row">
      <span
        className={`library-task-icon ${active ? "is-active" : queued ? "is-queued" : "is-done"}`}
      >
        {active ? (
          <LoaderCircle size={15} className="library-spin" />
        ) : queued ? (
          <Clock3 size={15} />
        ) : (
          <CheckCircle2 size={15} />
        )}
      </span>
      <div>
        <strong>
          {readString(record.asset, readString(record.name, "未命名任务"))}
        </strong>
        <small>
          {record.error
            ? readString(record.error)
            : record.worker === true
              ? "Worker"
              : "本地构建"}
        </small>
      </div>
      <span className="library-task-state">{state}</span>
      {(active || queued) && onCancel && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onCancel}
          aria-label={`取消 ${readString(record.asset, "任务")}`}
        >
          <Ban size={14} />
        </Button>
      )}
    </div>
  );
}

function readSnapshot(tasks?: TasksPanelProps["tasks"]): unknown {
  try {
    return tasks?.snapshot() ?? null;
  } catch {
    return null;
  }
}

function readArray(
  value: unknown,
  key: string,
): Array<Record<string, unknown>> {
  if (!isRecord(value) || !Array.isArray(value[key])) return [];
  return value[key].filter(isRecord);
}
