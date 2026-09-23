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
import type { Session } from "./session";
export function WorkbenchDialogs({ session }: { session: Session }) {
  const s = useStore(session.store),
    open = ["help", "scene-context", "scene-settings"].includes(s.dialog || ""),
    close = () => session.store.setState({ dialog: null });
  return (
    <Dialog
      open={open}
      onOpenChange={(value) => {
        if (!value) close();
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {s.dialog === "help"
              ? "快捷键与操作指南"
              : s.dialog === "scene-settings"
                ? "编辑设置"
                : "所选对象"}
          </DialogTitle>
          <DialogDescription>
            {s.dialog === "scene-context"
              ? s.selection.length + " 个对象已选中"
              : "本地工作空间 · 源 JSON 可重新载入"}
          </DialogDescription>
        </DialogHeader>
        {s.dialog === "help" ? (
          <>
            <dl>
              <dt>资源库搜索 / 场景命令</dt>
              <dd>/</dd>
              <dt>搜索命令</dt>
              <dd>Ctrl / ⌘ K</dd>
              <dt>移动 / 旋转 / 缩放</dt>
              <dd>W / E / R</dd>
              <dt>聚焦 / 全场景</dt>
              <dd>F / Home</dd>
              <dt>撤销 / 重做</dt>
              <dd>Ctrl Z / Ctrl Shift Z</dd>
              <dt>保存场景</dt>
              <dd>Ctrl S</dd>
              <dt>复制 / 粘贴</dt>
              <dd>Ctrl C / Ctrl V</dd>
              <dt>删除对象</dt>
              <dd>Delete</dd>
            </dl>
            <p>
              拖动空白处旋转，右键平移，滚轮缩放。导出模型下载真实 GLB；JSON
              保留可编辑源。浏览器草稿可能被清理，请保存下载的源文件。
            </p>
            <Button
              onClick={() =>
                session.store.setState({ dialog: "scene-settings" })
              }
            >
              吸附与编辑设置
            </Button>
          </>
        ) : s.dialog === "scene-settings" ? (
          <>
            {(
              [
                ["snapMove", "移动吸附 · m", 0.001, 100],
                ["snapRotate", "旋转吸附 · °", 0.1, 180],
                ["snapScale", "缩放吸附", 0.001, 10],
              ] as const
            ).map(([key, label, min, max]) => (
              <label key={key}>
                {label}
                <Input
                  type="number"
                  min={min}
                  max={max}
                  step={min}
                  defaultValue={s.prefs[key]}
                  onBlur={(e) => {
                    const value = e.target.valueAsNumber;
                    if (Number.isFinite(value) && value >= min && value <= max)
                      s.setPrefs({ [key]: value });
                  }}
                />
              </label>
            ))}
          </>
        ) : (
          <div className="grid gap-2">
            <Button
              onClick={() => {
                close();
                session.runtime.focusSelection();
              }}
            >
              聚焦所选
            </Button>
            <Button
              onClick={() => {
                close();
                void session.command({
                  type: "duplicate-many",
                  ids: s.selection,
                });
              }}
            >
              复制对象
            </Button>
            <Button
              onClick={() => {
                session.requestGroup();
              }}
            >
              创建选择组
            </Button>
            <Button
              onClick={() => session.store.setState({ dialog: "scene-array" })}
            >
              阵列复制
            </Button>
            <Button
              onClick={() => session.store.setState({ dialog: "scene-align" })}
            >
              对齐 / 分布
            </Button>
            <Button
              onClick={() => {
                close();
                void session.exportSubset({ ids: s.selection });
              }}
            >
              导出所选 GLB + JSON
            </Button>
            <Button
              onClick={() => {
                close();
                void session.command({
                  type: "visibility",
                  ids: s.selection,
                  visible: false,
                });
              }}
            >
              隐藏所选
            </Button>
            <Button
              onClick={() => {
                close();
                session.requestDelete();
              }}
            >
              删除对象
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
