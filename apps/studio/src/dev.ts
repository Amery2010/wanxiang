import type { Data } from "./studio/types";

async function start() {
  const [response] = await Promise.all([
    fetch("/__wanxiang/catalog.json"),
    new Promise<void>((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "/__wanxiang/runtime.js";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("无法加载本地几何运行时"));
      document.head.append(script);
    }),
  ]);
  if (!response.ok) throw new Error(await response.text());
  const catalog = (await response.json()) as Data;
  Object.assign(window, { WX_DATA: catalog });
  Object.assign(window, {
    WX_LOAD_ASSET: async (id: string, signal?: AbortSignal) => {
      const result = await fetch(
        `/__wanxiang/assets/${encodeURIComponent(id)}.json`,
        { signal },
      );
      if (!result.ok) throw new Error(await result.text());
      return (await result.json()) as Data;
    },
  });
  await import("./main");
}

void start().catch((error: unknown) => {
  const root = document.getElementById("root");
  if (!root) return;
  const message = document.createElement("pre");
  message.setAttribute("role", "alert");
  message.textContent = `工作台未能启动。请检查 README 中的 Python 依赖。\n${error instanceof Error ? error.message : String(error)}`;
  root.replaceChildren(message);
});
