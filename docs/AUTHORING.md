# 作者与生产链

本指南覆盖现有资产作者、当前覆盖、新组件接入、生成库保护和离线交付。作者源在根目录，运行时代码在 `packages/runtime/`，Python 接口在 `packages/kit/`；不要把生成文件或历史报告当作作者源。

## 唯一数据源

`tools/author_foundation.py` 依次收集 foundation、worlds 和 frontiers 作者模块，再应用 `authoring/overrides/`；`tools/game410/` 在 repair39 步骤后追加当前游戏扩展。`authoring/styles.json` 声明当前允许的派生方式，`authoring/retired-v1.json` 保存停用元数据，`authoring/game410-baseline.json` 保存 v3.9 定义基线。

`tools/rebuild_library.py` 会先验证 ID、依赖闭包、循环和材质，再在临时目录生成完整 `library/` 与伴随 manifest。未改变且仍符合策略的预览可以保留，过期 ID 图片会被删除。不能使用废弃覆盖、旧别名或旧目录重新引入停用资产，也不能只编辑生成的 `library/*.json`。

直接编辑生成 JSON 或图片会触发保护。`--discard-generated` 明确表示放弃未进入作者层的修改；不要把它隐藏在自动保存逻辑中。作者验证和提交过程使用独占锁，失败时恢复原 library 与伴随清单。强制中断后，先确认没有其他写入进程，再检查暂存目录和锁。

## 新组件接入

使用模板创建一个完整定义和 pytest 起点：

```bash
python tools/new_component.py --id custom.module --name '自定义模块' --out workspaces/custom-module
```

模板不会安装依赖或生成 GLB。审查 ID、单位、轴向、原点、几何、材质、碰撞意图和接口后，把定义放入 `authoring/overrides/parts/`，把有意义的测试放入 `tests/`。模板是结构起点，不是美术质量认证。

项目批量作者代码按领域放在 `tools/expansion/`、`tools/l1_expansion/`、`tools/l2_expansion/`、`tools/l34_expansion/` 和 `tools/game410/`。新游戏 profile 只放在 `tools/game410/`，并在 repair39 之后进入原子作者流程。修改作者源而不是生成后的目录文件。

一个条目必须有稳定的语义 ID、名称、分类、层级、主题、标签、参数 schema、材质角色、原点和轴向说明，同时明确碰撞与 LOD 是提供还是不提供。区分可视边界和实际碰撞形体；颜色、风格和轻微尺寸变化不能注册为新资产。

部件至少在一个实际组合或场景中使用。装配依赖必须无环，接口按真实宽度、边界样本和方向定义，不能从对象名称猜测。几何表达式使用受限语义求值器，不嵌入任意 JavaScript 或 Python 代码。

## 语义、接口与几何

部件声明 `parameter_schema.properties`；装配声明 `metadata.parameter_schema`，值放在 `metadata.parameters`。`$param` 引用变量，`$op` 只允许内核登记的算术。组件 TRS、`frame_scale`、骨骼 `bind`、材质和局部 palette 在展开时保留并传播。

L1 是语义形体，L2 是复合部件或功能子装配，L3 是可用完整配方，L4 是场景；L0 几何算子不进入资产计数。复用源组件而不是复制大量换色目录项；需要服务变体时在 metadata 中标明 `variant_of` 和 `variant_not_new_geometry_family`。职业角色可共享骨架，不声称每个职业拥有完全不同的人体拓扑。

局部连接点使用 `position`、`normal`、`tangent` 和有版本的 interface。舱体、气闸和其他结构开口保留真实孔洞，并用射线和实际几何验证。`packages/runtime/src/seams.js` 只对显式配对的放样端环做循环或反向配准，统一位置和权重并移除内部盖面；它不是任意布尔融合。细则见 [SEAM_CONTRACT.md](SEAM_CONTRACT.md)。

有限运动使用 `metadata.state_controls` 声明节点、轴、范围、单位和 `mode`（rotation 或 translation）。多个控制作用于一个节点时，从绑定矩阵按声明顺序组合；`struts` 约束两端点，杆件平移而不按行程拉伸。骨骼、静态装配和刚性预览不能混为物理仿真。场景灯光最多声明六个夜景点灯，预览状态不能写入 GLB 快照。

## 生成、预览与检查

使用根命令编排工作区，作者命令仍由项目 Python 环境执行：

```bash
pnpm verify:authoring
python tools/rebuild_library.py --overwrite
python tools/game410_thumbnails.py --ids custom.module
python tools/verify_game410_previews.py
pnpm dev
```

缩略图管线只保留 `library/thumbnails/` 中每个公开资产的一张 256×256 Q80 Lowpoly WebP，使用当前源和策略指纹幂等更新。几何变化必须从新生成的 GLB 渲染。不要重跑历史 320px/Q91 路径、移除的迁移选项，或转码旧压缩输出。Toon 是实时 3D 渲染样式，不是另一个缩略图层。

模板 pytest 只是起点。测试应覆盖正式风格、默认值、数值边界、枚举值、至少一个真实装配、结构开口、碰撞意图和 LOD 差异；相互依赖的参数另加案例，不以全参数笛卡尔积代替设计测试。

静态和拓扑检查通过不等于艺术认可。至少复查正面、侧面、上方和典型游戏视角，检查轮廓、比例、树冠和枝干关系、道路通行、门洞、悬浮和穿插。图片应来自实际 GLB，并注明 CPU/GPU 和着色限制。

```bash
python -m pytest tests/test_game410.py tests/test_geometry.py -q
python tools/check_game410.py
python tools/rebuild_acceptance.py
```

重建前先检查 [当前源码约束](LIMITATIONS.md#当前源码约束)，在核对作者源码和测量基线前保持已交付定义字节不变。

## 交付

按以下顺序工作：修改作者 → 重建 library → 更新缩略图和实际导出/读回 → 视觉复查 → 构建 Studio → 冻结定义 → 回归与回滚检查 → 源码 ZIP 打包 → 在新目录解压并重建。

`build_worlds.py` 按需生成示例。临时 GLB、大 PNG、验收下载和构建缓存不进入核心源码；小尺寸目录缩略图可以保留。使用以下命令保存完整源码快照：

```bash
pnpm pack:source
```

源码保存不以所有测试通过为前提。浏览器、冷解压、设备和 E2E 证据需单独执行，不能把历史报告写成当前验证结果。
