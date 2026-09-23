# L1 接入检视示例

11 个 JSON 将各领域新增部件排布在检视网格上，便于复用 `part` 引用、局部坐标和导出流程。
这些文件没有登记到正式装配目录，不计入 L2、L3、L4 或新增资产数量；不是完成的生产场景。
`metadata.l1_examples` 可由部件 ID 定位对应实例。例子仅演示引用与定位，不证明自动卡扣、物理关节、可动骨架或游戏行为已经实现。

```sh
python wx kit build --spec examples/l1/robot.json --out exports/l1-robot-layout --no-review --no-cache
```

规模较大的道具排布可只保留需要的实例。用于游戏前重新设计布局、比例、碰撞、LOD 与遮挡。
