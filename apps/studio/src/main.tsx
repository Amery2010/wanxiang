import { Component, StrictMode, type ErrorInfo, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import "@wanxiang/runtime/studio";
import { StudioApp } from "./studio/StudioApp";
import type { Data } from "./studio/types";
import baseCss from "./styles.css?inline";
import studioCss from "./studio/studio.css?inline";
import libraryCss from "./studio/library/library.css?inline";

class StartupBoundary extends Component<
  { children: ReactNode },
  { error: string }
> {
  state = { error: "" };
  static getDerivedStateFromError(error: unknown) {
    return { error: error instanceof Error ? error.message : String(error) };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Studio interface error", error, info.componentStack);
  }
  render() {
    if (this.state.error) {
      return (
        <main role="alert" style={{ padding: 32 }}>
          <h1>工作台未能启动</h1>
          <p>请重新打开完整离线文件，或检查开发终端中的数据加载错误。</p>
          <pre style={{ whiteSpace: "pre-wrap" }}>{this.state.error}</pre>
        </main>
      );
    }
    return this.props.children;
  }
}

const host = document.getElementById("root");
if (!host) throw new Error("Missing studio root");
const style = document.createElement("style");
style.id = "wanxiang-react-styles";
style.textContent = `${baseCss}\n${libraryCss}\n${studioCss}`;
document.head.append(style);
const startup = window as unknown as {
  WX_DATA: Data;
  WX_LOAD_ASSET?: import("./studio/asset-loader").LoadAsset;
  WX_LOAD_DATA?: () => Promise<Data>;
};
const data = startup.WX_DATA;
if (!data || !Array.isArray(data.assets))
  throw new Error("Missing embedded asset catalogue");
const root = createRoot(host);
root.render(
  <StrictMode>
    <StartupBoundary>
      <StudioApp
        data={data}
        loadData={startup.WX_LOAD_DATA}
        loadAsset={startup.WX_LOAD_ASSET}
      />
    </StartupBoundary>
  </StrictMode>,
);
import.meta.hot?.dispose(() => {
  root.unmount();
  style.remove();
});
