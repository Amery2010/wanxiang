import { useStore } from "zustand";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../ui/dialog";
import { zipStore, type ArchiveFile } from "../runtime/archive";
import { download, closedManifest, type Session } from "./session";
import { hasMaterialImage } from "./library/utils";
export function MaterialDialog({ session }: { session: Session }) {
  const s = useStore(session.store),
    material = s.data.materials?.find((m) => m.id === s.materialId),
    open = s.dialog === "material";
  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) session.store.setState({ dialog: null });
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{material?.name || "材质详情"}</DialogTitle>
          <DialogDescription>
            {hasMaterialImage(material?.record)
              ? "原始图片与可复用材质参数"
              : "参数材质示意图 · 无贴图，模型颜色由顶点色提供"}
          </DialogDescription>
        </DialogHeader>
        {material ? (
          <>
            <img
              src={material.preview}
              alt={material.name || material.id}
              width={256}
              height={256}
              className="mx-auto rounded-lg object-contain"
            />
            <pre>{JSON.stringify(material.record, null, 2)}</pre>
            <Button
              id="matDownload"
              onClick={() => {
                try {
                  const files: ArchiveFile[] = [
                      [
                        "material.json",
                        JSON.stringify(material.record, null, 2),
                      ],
                    ],
                    decode = (base64: string) =>
                      Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
                  if (
                    material.record.kind !== "palette" &&
                    material.preview?.startsWith("data:image/png;base64,")
                  )
                    files.push([
                      "basecolor.png",
                      decode(material.preview.split(",")[1]),
                    ]);
                  for (const [name, base64] of Object.entries(
                    material.files || {},
                  )) {
                    if (name.includes("..") || name.startsWith("/"))
                      throw Error("无效材质文件路径");
                    files.push([name, decode(base64)]);
                  }
                  files.push(["WX_MANIFEST.json", closedManifest(files)]);
                  download(
                    zipStore(files),
                    material.id + ".zip",
                    "application/zip",
                  );
                } catch (e) {
                  s.notify(String(e));
                }
              }}
            >
              下载当前材质包 ZIP
            </Button>
          </>
        ) : (
          <p>未找到当前材质。</p>
        )}
      </DialogContent>
    </Dialog>
  );
}
