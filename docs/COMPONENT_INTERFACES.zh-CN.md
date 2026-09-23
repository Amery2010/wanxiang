# 组件接口、碰撞与 LOD

## 连接点不是分类标签

规范来源为 `library/interfaces.json`，生产校验在 `packages/kit/src/wanxiang/contracts.py` / `packages/runtime/src/contracts.js`；声明结构在 `schemas/interface-port.schema.json`。接口字段使用米制坐标，+Y 向上，+Z 为默认正面。`normal` 与 `tangent` 必须是有限、单位且正交的向量。

15 类接口覆盖地形边、河道、车道、步道、轨道、墙体、楼板、门、两种管法兰、车轮、手持装备、背部挂点、玩法触发和特效发射器。ID 的版本后缀与 `version` 字段必须一致。已有未版本化的通用 `surface` 端口保留兼容规则，但不能因此匹配任意新接口。

`span` 是**实际开口/接缝宽度**，不能仅从接口名称推断；`profile` 是沿 `tangent` 排列的边界高度样本。`.1m` 类接口表示网格约定，不强制每个模块只能 1 米宽。譬如 4 米地形边必须用 `span:4`，不能伪称 1 米。尺寸、轮廓、轨距/直径、性别与版本均需相容。

默认误差 0.0001 米，门、装备、触发器等按注册表的专用容差。`gender` 可为 neutral / male / female；两个同为 male 或同为 female 的物理连接拒绝。注册端口默认 `allowed_scale:none`，世界变换中有缩放的模块不能仅凭“名称相同”强行吸附；应使用作者尺寸参数修改几何与端口，再重新校验。

```json
{
  "id":"south",
  "interface":"terrain.edge.1m.v1",
  "version":1,
  "units":"m",
  "position":[0,0,2],
  "normal":[0,0,1],
  "tangent":[1,0,0],
  "span":4,
  "profile":[0,0,0,0,0,0,0,0,0],
  "gender":"neutral",
  "allowed_scale":"none"
}
```

适配搜索先解析默认参数与实际连接点，而不是只查询 tags。结果表示**默认参数候选**，并不表示已摆放成功；装配时还要在世界变换下二次检查。匹配后的装配日志含真实位置误差和法线点积。`exp-site-forest-path` 是五次真实端口装配的坡道/台阶/转角验证配方，地形样本也与实际顶点逐点对应。

## 碰撞意图必须显式声明

`runtime.collision` 可为 none、box、sphere、capsule、compound、convex-hull、authored-mesh、heightfield 或 children。结构定义见 `schemas/runtime-metadata.schema.json`。生产路径会校验坐标约定、代理类型、正尺寸、LOD 列表和静态凹面要求。

浏览器下载 `*.runtime-recipes.json`，保存来源部件、参数、对应 GLB 节点、碰撞和 LOD 配方。它是轻量引擎适配输入，不是已烘焙的物理世界。

CLI 的 `release/colliders.json` 另外包含显式要求的局部坐标网格代理，以及节点世界变换与尺寸参数缩放。处理建议：

- box/capsule/compound 由消费端按作者尺寸与局部变换创建；门洞使用两侧柱和顶部梁，不用一整个实体包围盒堵住通路。
- heightfield/authored-mesh 保留真实地形或凹形轮廓，例如环岛中孔；以静态三角网格使用。当前代理可含地形侧面和底盖，不冒充仅有高度样本的专用物理引擎 HeightField 格式。
- convex-hull 按实际形体生成凸包；固体晶体不会因材质透明而被误删。水面、纯装饰叶片和未声明碰撞的旧资产不会自动变成实体障碍。

已生成网格代理的顶点已应用 Part 尺寸参数，使用时只应用对应节点世界矩阵，不能再次乘 `parameter_size_scale`。该字段用于消费端按作者配方重建基本碰撞原语时参考。

`selection_bounds_are_colliders:false` 是显式区分。没有接入 Rapier / Cannon / Ammo，没有自动角色控制器或 NavMesh。消费端必须处理胶囊非均匀缩放、动态凹体限制和碰撞层。

## LOD 不是给文件改名

22 个目录条目提供两级作者参数 LOD（A–C 的 11 个，加上 D–E 的 11 个）。LOD0 / LOD1 会改变几何细节参数，然后重新构建真实模型；同一资产保留语义原点、来源和装配方式。小型物件默认关闭 LOD，避免为少量面数增加管理成本。

```bash
python wx kit list --lod yes
python wx kit build --assembly exp-birch --lod 1 --out exports/birch-low
python wx kit export-lods --assembly exp-birch --out exports/birch-set
```

`lod-set.json` 记录各级真实三角面数、GLB 路径与 SHA-256。以默认 Lowpoly 桦树为例，本轮实测从 724 降为 424 个三角形。`screen_height` 是消费端切换建议，不意味着编辑器已经安装自动远近切换系统。没有为全库强制生成 LOD，也没有把简化后可能的轮廓变化说成零误差。
