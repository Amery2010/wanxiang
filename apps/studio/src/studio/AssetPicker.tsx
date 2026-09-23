import { useState } from "react";
import { useStore } from "zustand";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../ui/dialog";
import { core, type SceneDocument } from "./types";
import type { Session } from "./session";
export function AssetPicker({ session }: { session: Session }) {
  const s = useStore(session.store),
    [query, setQuery] = useState(""),
    [level, setLevel] = useState("all"),
    [domain, setDomain] = useState("all"),
    [page, setPage] = useState(1),
    [selected, setSelected] = useState<string[]>([]),
    replace = s.dialog === "scene-replace",
    open = replace || s.dialog === "scene-picker";
  if (!open) return null;
  const assets = core().filter(
      s.data.assets.filter((a) => (a.level || 0) < 4 && (a.dynamic || a.kit)),
      { query, level, domain },
      s.prefs,
    ),
    pages = Math.max(1, Math.ceil(assets.length / 30)),
    current = Math.min(page, pages);
  return (
    <Dialog
      open={open}
      onOpenChange={(value) => {
        if (!value) {
          session.store.setState({ dialog: null });
          setSelected([]);
        }
      }}
    >
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>
            {replace ? "替换所选资产" : "插入资产到场景"}
          </DialogTitle>
          <DialogDescription>
            保留真实资产引用；单次最多插入 24 项。
          </DialogDescription>
        </DialogHeader>
        <div className="picker-toolbar">
          <Input
            id="pickerSearch"
            aria-label="搜索可插入资产"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(1);
            }}
          />
          <select
            id="pickerLevel"
            value={level}
            aria-label="插入资产层级"
            onChange={(e) => {
              setLevel(e.target.value);
              setPage(1);
            }}
          >
            <option value="all">所有层级</option>
            {["1", "2", "3"].map((l) => (
              <option value={l} key={l}>
                L{l}
              </option>
            ))}
          </select>
          <select
            id="pickerDomain"
            aria-label="插入资产领域"
            value={domain}
            onChange={(e) => {
              setDomain(e.target.value);
              setPage(1);
            }}
          >
            <option value="all">所有用途</option>
            {core()
              .domains.filter((d) => d.id !== "scene")
              .map((d) => (
                <option value={d.id} key={d.id}>
                  {d.label}
                </option>
              ))}
          </select>
        </div>
        <div id="pickerGrid" className="picker-grid">
          {assets.length ? (
            assets.slice((current - 1) * 30, current * 30).map((a) => (
              <Button
                className="picker-card"
                key={a.id}
                data-ref={a.id}
                aria-pressed={selected.includes(a.id)}
                onClick={() =>
                  setSelected((old) =>
                    replace
                      ? [a.id]
                      : old.includes(a.id)
                        ? old.filter((id) => id !== a.id)
                        : old.length < 24
                          ? [...old, a.id]
                          : old,
                  )
                }
              >
                <img src={a.hero || ""} width={96} height={96} alt="" />
                <span>{a.name}</span>
              </Button>
            ))
          ) : (
            <div className="empty-state" role="status" aria-live="polite">
              <strong>没有匹配的可插入资产</strong>
              <span>请尝试清空搜索词或调整层级、用途筛选。</span>
            </div>
          )}
        </div>
        <div className="property-actions">
          <Button
            id="pickerPrev"
            disabled={current <= 1}
            onClick={() => setPage(current - 1)}
          >
            上一页
          </Button>
          <span>
            {current} / {pages} · {assets.length} 项
          </span>
          <Button
            id="pickerNext"
            disabled={current >= pages}
            onClick={() => setPage(current + 1)}
          >
            下一页
          </Button>
          <Button
            id="pickerInsert"
            disabled={
              !selected.length ||
              s.busy ||
              (replace && s.selection.length !== 1)
            }
            onClick={() => {
              session.store.setState({ dialog: null });
              if (replace && s.selection.length === 1)
                void session.command({
                  type: "replace",
                  id: s.selection[0],
                  ref: selected[0],
                });
              else {
                const center = session.runtime.groundCenter();
                const doc = s.spec as SceneDocument;
                const layer = doc.metadata.scene.objects[s.selection[0]]?.layer;
                void session.command({
                  type: "batch",
                  commands: selected.map((ref, i) => ({
                    type: "add",
                    ref,
                    position: [
                      center[0] + (i % 4) * 2,
                      center[1],
                      center[2] + Math.floor(i / 4) * 2,
                    ],
                    ...(layer && !doc.metadata.scene.layers[layer].locked
                      ? { layer }
                      : {}),
                  })),
                });
              }
              setSelected([]);
            }}
          >
            {replace ? "替换所选" : "插入所选"} ({selected.length})
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
