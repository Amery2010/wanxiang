# Wanxiang3D 万象工坊

Wanxiang3D 是用于语义化资产作者、场景装配和实时 GLB 导出的本地模块化 Lowpoly 工作台。在仓库根目录运行 `pnpm dev` 预览工作台。当前公开目录为 3,730 项：L1 1,600、L2 1,010、L3 1,000、L4 120。`library/game-expansion.json` 另含 120 个 L1 部件和 10 个单独计数的 L2 组合样例。

## Monorepo 结构

| 模块 | 职责 |
| --- | --- |
| `apps/studio` | React/Vite 工作台、界面测试和编译后的 UI bundle |
| `packages/runtime` | 严格 TypeScript 几何、场景操作、浏览器运行时、包依赖管理的 Three.js 和 Node Worker |
| `packages/kit` | Python `wanxiang` 包与 `wx` CLI；从已安装包加载代码，从外部资源根加载资产 |

根目录继续保留 `tools/`、`schemas/`、`authoring/` 和 `library/`，它们是作者源和数据源。runtime 不依赖 Studio 或 Python 包。Studio、Node Worker 和 Python kit 共用有序 runtime 源文件清单，路径和加载顺序只在一个地方维护。

## 环境安装

使用 Node **24.18.0**、pnpm **11.23.0** 和 Python **3.11 以上**（推荐 Python 3.13）。已有多个 Python 解释器时可用 `WX_PYTHON` 指定实际解释器。

```sh
corepack prepare pnpm@11.23.0 --activate
pnpm install
python -m venv .venv
WX_PYTHON=.venv/bin/python
"$WX_PYTHON" -m pip install -e './packages/kit[test,build]'
```

所有 workspace 命令从仓库根目录执行：

```sh
pnpm dev
pnpm build
pnpm typecheck
pnpm lint
pnpm test
pnpm pack:runtime
pnpm pack:python
pnpm pack:source
pnpm verify:authoring
```

`pack:runtime` 准备 npm tarball，`pack:python` 准备 wheel 和 sdist，`pack:source` 在仓库外生成完整源码 ZIP。这些命令只准备分发产物；发布需要另行明确授权。runtime 和 Python 打包前会先构建 runtime。源码 ZIP 不以测试或构建成功为前提，包含 TypeScript 输入和已有的 runtime 编译产物。

在仓库之外的项目中安装生成的分发包：

```sh
npm install /path/to/wanxiang/generated/distributions/wanxiang-runtime-3.10.0.tgz
python -m pip install /path/to/wanxiang/generated/distributions/python/wanxiang3d_agent_kit-3.10.0-py3-none-any.whl
export WX_RESOURCE_ROOT="/path/to/resource root"
export WX_WORKSPACE_ROOT="/path/to/writable workspace"
wx kit list
```

Python wheel 和 sdist 自带独立运行的 JavaScript 编译产物、Three.js 及许可证与预编译资产审查界面，几何 Worker 需要 Node，但不需要 npm 或 pnpm。解压完整源码 ZIP 后，其根目录即可作为兼容的外部资源根。

## 资源和可写状态

轻量 Python 包不包含完整资产库。请将 `WX_RESOURCE_ROOT` 指向含有 `library/` 和作者策略文件（包括 `authoring/thumbnail-policy.json`）的外部资源根。源码 checkout 默认使用当前仓库；独立安装必须为目录查询和构建配置资源根，缺少数据时不会自动下载。

`WX_WORKSPACE_ROOT` 选择隐式工作区、候选操作和状态的可写基础目录。源码 checkout 默认使用仓库；独立安装默认使用 `~/.wanxiang`。支持 `--workspace` 的命令中，该参数优先；`WX_CACHE_DIR` 继续优先指定缓存目录；`--out` 指定显式导出位置。

`pnpm dev` 监听并重新构建 runtime，通过 Vite 提供工作台，并通过 Python 读取本地资产数据。`pnpm build` 先编译 runtime，再更新 Studio 编译产物 `apps/studio/artifacts/app.js`，不生成单文件 HTML。在全新 checkout 中直接调用 Python 几何或作者工具之前，请先运行构建。runtime 产物包括带类型声明的 ESM/CommonJS 模块，以及独立离线资源树 `packages/runtime/dist/compat`。Three.js 版本在 `package.json` 中固定，旧 vendor 路径由该依赖生成。CPU 回退和实时 GLB 导出继续可用。

工作台首屏只加载列表 metadata；选中模型或在场景、导出操作中使用模型时，才加载其配置及引用的部件、装配和动画，首页不再下载全量模型定义。接口与离线查看器的边界见 [Studio 加载说明](apps/studio/README.md)。

## 作者与验证

修改 `tools/` 中的作者模块和 `authoring/overrides/` 中的当前覆盖；不要把生成的 `library/` JSON 当作源文件直接编辑。新的游戏 profile 放在 `tools/game410/`，并在 repair39 原子作者步骤之后应用。模型单位为米，+Y 向上，+Z 向前。碰撞元数据表达消费端意图，不等于物理实现。

当前缩略图策略在 `library/thumbnails/` 为每项公开资产保留一张 256×256 Q80 Lowpoly WebP。几何变化必须从新 GLB 渲染；不要使用历史缩略图命令或转码旧压缩输出。

已知隔离重建问题是 `authoring/l1-bounds.json` 源码指纹过期，首个报告 ID 为 `l1.architecture.column.fluted`。保持已交付定义不变，在重新生成 library 前先核对作者源和测量基线。

架构和分发见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)，Python/CLI 接口见 [docs/API.md](docs/API.md)，作者与新组件流程见 [docs/AUTHORING.md](docs/AUTHORING.md)，工作台使用见 [docs/USAGE.md](docs/USAGE.md)，限制和证据边界见 [docs/LIMITATIONS.md](docs/LIMITATIONS.md)。几何契约见 [docs/MODELING_STANDARDS.zh-CN.md](docs/MODELING_STANDARDS.zh-CN.md)、[docs/COMPONENT_INTERFACES.zh-CN.md](docs/COMPONENT_INTERFACES.zh-CN.md) 和 [docs/SEAM_CONTRACT.md](docs/SEAM_CONTRACT.md)；运行时接入见 [docs/PRODUCTION_RUNTIME.zh-CN.md](docs/PRODUCTION_RUNTIME.zh-CN.md) 与 [docs/RUNTIME_EXPORT.md](docs/RUNTIME_EXPORT.md)。

本地静态检查不代表移动设备、实体 GPU、目标引擎、Cloud、部署或生产认证。浏览器和 E2E 检查独立执行，需明确授权。
