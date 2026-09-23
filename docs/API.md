# CLI / Python / 浏览器接口

所有命令支持 `python wx`，结果为 `wx.result/1.0`。完整选项使用 `python wx kit --help`。当前目录、作者源和导出契约以 `library/`、`tools/` 与 `schemas/` 为准。安装后的 `packages/kit` 从 `WX_RESOURCE_ROOT` 读取外部资产；源码 checkout 默认使用当前仓库。

```sh
python wx doctor --deep
python wx kit list --kind assembly --query harbor
python wx kit show l1.gameplay.game_puzzle.tri_key --kind part
python wx kit build --assembly l2-game410-puzzle --out workspaces/puzzle
python wx kit build --part l1.gameplay.game_puzzle.tri_key --out workspaces/tri-key
python wx kit retired --query body.head
python wx kit export-runtime --assembly l2-game410-puzzle --out workspaces/puzzle-runtime
```

工作台使用 `pnpm dev` 启动，通过 `pnpm build` 构建 UI；这些是仓库根目录的 pnpm 命令。

Windows内联JSON引号不同，可先保存参数文件并用 `--params 文件.json`。构建和运行时导出请选新目录。

```python
from wanxiang.kit_assembly import Assembler, get_template, materials_for
from wanxiang.mechanics import apply
from wanxiang.glb import export_glb
from wanxiang.runtime_export import batch_static

spec = get_template('world-service-robot')
asset = Assembler().assemble(spec)
# Use spec['metadata']['state_controls'] for valid names/ranges.
state = {c['id']: c.get('default', 0) for c in spec['metadata']['state_controls']}
apply(asset, spec, state)
export_glb(asset, materials_for(asset), 'robot-state.glb', animations=[])

scene_spec = get_template('world-scene-cyber')
scene = Assembler().assemble(scene_spec)
packed, mapping = batch_static(scene, scene_spec)
assert mapping['triangles_before'] == mapping['triangles_after']
```

Python build_part与Node/浏览器使用相同语义与几何内核。浏览器 `new WXRuntime.Library(bundle).buildSync(spec)` 返回真实root、node map、BOM与材质。`WXMechanics.apply(root,spec,state)`受限更新节点；`WXRuntimePack.pack`用于新加载快照，不直接使用展示态对象。

停用库 API `wanxiang.retirement.lookup(query)` 返回元数据；请求停用模型的构建接口会抛 `ASSET_RETIRED`，无自动旧参数转译。所有骨架、矩阵和连接契约都有边界，不能把它当作通用DCC布尔或物理引擎。
