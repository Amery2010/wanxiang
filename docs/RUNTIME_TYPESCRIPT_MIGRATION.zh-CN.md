# Runtime TypeScript 迁移验收记录

本轮将 runtime 自有实现、兼容入口与 worker 迁移为严格 TypeScript。几何算法、资产定义与数据协议保持原有行为。Three.js 固定为 `0.186.0`，类型包同版本；第三方源码由包管理器安装，旧 vendor 资源仅在构建时生成并携带许可证。

## 模块与分发契约

- `src` 使用显式 import/export，独立于 Studio 与 Python。共享数据、连接契约、构建结果与 worker 协议均由 runtime 定义；Studio 保留 UI 类型。
- `dist/cjs`、`dist/esm` 提供模块与声明；`dist/compat` 提供 CommonJS 兼容入口、WX 全局 adapter、独立 worker 和离线 Three.js 资源。
- 原有包入口、`sources` 方法、manifest 字段和逻辑资源路径保留。普通模块入口 `@wanxiang/runtime/modules/*` 使用声明的 Three.js 依赖；离线资源包含执行所需代码。
- Python checkout 和作者工具消费 `dist/compat`。wheel/sdist 包含该资源树，安装后不需要 npm/pnpm。源码快照仍可在构建或测试未通过时生成。
- 每个 Library 拥有独立连接 registry；旧 `WXContracts` 默认 registry 的修改不影响既有 Library。Studio 从当前会话数据查询接口，并随延迟加载更新。
- 主线程和 worker 共用构建、GLB 导出与资源释放 implementation；主线程加载贴图，worker 保持无贴图。每任务独立 worker，取消、超时、进度与不可用回退继续保留。

## 二进制准备流程

动态构建及缓存命中保留原始 ArrayBuffer，生成兼容的 `asset.glb` 后不再立即反向解码。`Pipeline.prepare` 保存经检查的私有字节快照，供本次加载复用检查结果。公开 `inspect/load` 仍执行检查，没有跳过验证选项；损坏缓存仍删除并重建。

固定样例为 1,000,072 字节的合成 GLB，Node 24.18.0，预热 5 次，再取 7 组、每组 30 次的中位数。命令：`pnpm --filter @wanxiang/runtime benchmark`。

| CPU 准备工作 | 迁移前流程 | 迁移后流程 |
| --- | ---: | ---: |
| GLB 检查次数 | 4 | 1 |
| Base64 编码次数 | 1 | 1 |
| Base64 反向解码次数 | 1 | 0 |
| 验证字节快照 | 0 | 1 |
| 样例耗时中位数 | 2.44 ms | 0.78 ms |

此数据只衡量检查与编码准备，不包含几何生成、GLTFLoader 解析、浏览器、GPU 或真实资产总耗时。未新增缓存层或输出体积预算门禁。

## 本地验证

最终 `pnpm build`、`pnpm typecheck`、`pnpm lint` 与 `pnpm test:js` 均通过。JS 合计 **219 项通过**（runtime 20、Studio 194、场景命令 5）；最终产物生成后，Python 路径/分发接口与几何定向检查另有 **48 项通过**。npm tarball、wheel、sdist 均已重新生成并通过下述独立安装验证。

构建、类型检查和 lint 覆盖 runtime 与 Studio。测试覆盖代表性几何数组指纹、场景与参数操作、跨 Library 状态隔离、共享导出失败释放、worker 取消和超时、缓存命中与损坏恢复、CPU 回退、延迟定义更新。12 个代表性几何样例与迁移前 JavaScript 输出指纹一致。

在独立临时目录完成：

- 安装 npm tarball，验证 CommonJS、ESM、旧浏览器全局、Node worker，以及严格 TypeScript 的 ESM/CommonJS 消费方；类型探针不使用 `skipLibCheck`。
- 安装 wheel，使用没有 pnpm 的 PATH 验证 CLI、CPU worker、live geometry 和空资源 fixture 的离线 HTML 生成。
- 解压 sdist 后在仓库外重建 wheel，并重复安装运行探针。
- 开发服务通过 HTTP 提供页面和 runtime 资源，修改 runtime 源码触发重建；SIGTERM 后端口关闭且无子进程残留。未打开浏览器执行测试。

持久缓存补测使用 Node 模拟存储 adapter，未验证实际浏览器 IndexedDB 跨重启持久化。离线 HTML 探针使用空资源 fixture，不代表完整资产库、贴图与 GPU 渲染均已验证。Python 全库已有的几何及目录限制见 [LIMITATIONS.md](LIMITATIONS.md)。

定向 Python 回归中的 297 条 LOD 失败已逐条在原始 HEAD JavaScript 内核上重跑：失败用例集合及面数断言数值完全相同。本轮未调整这些资产、几何算法或断言来消除已有失败。

另外，莲花柱及其装配的 4 条法线断言、人体参数的 6 条接缝断言，也已在旧内核上复现。这些限制在迁移前的 `LIMITATIONS.md` 中已有记录。

作者重建用例还受到 `l1.architecture.column.fluted` 的过期测量基线阻塞（`Stale L1 placement bounds`）；旧内核同样失败，相关作者文件与 `authoring/l1-bounds.json` 本轮均未修改。该限制也已在迁移前文档中记录。

Python 当前收集 23,595 条用例。完整命令在完成前 23,530 条后，停留于 depot 场景运动测试：13 个控制量各取三种值，穷举共 1,594,323 组。该项被主动中止，原测试未修改；随后单独执行其余 64 条。合计 **23,286 条通过、308 条基线失败、1 条穷举未完成**，失败用例集合与旧内核对照完全相同，不能宣称全量 Python 测试通过。

depot 补充验证保留原测试的约束误差、网格不变性和非法状态回滚断言，检查默认值、整体极值、单控制量极值及两两极值，共 **226 组去重样例通过**；该结果不能替代完整穷举。详细本地记录为 `generated/python-migration-verification.json` 与 `generated/depot-motion-sample.json`。

本轮未执行 E2E、提交、发布或部署；本地证据不作为浏览器、设备或生产验证证据。

协作分工：六个实施子任务分别负责几何、语义、Library、执行链、Studio 与 Python；独立只读审查检查跨模块兼容性，主代理负责构建适配、集成修正与最终验收。
