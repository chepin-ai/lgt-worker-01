CLASSIFY: L1
# V-148 Quafu RAC：真机仍在队，终态判读器预注册并通过已知答案自证

## 队列快照

RETRIEVE run `41931682046` 回收 task `91C842B01A238734`，状态仍为 `In Queue`。本拍新增量子任务 `0`、send `0`；累计 `jobs=1`、`pending=1`、`returned_shots=0`、`S_real_pilot=null`。

## 结果返回前锁定的判读口径

- 主指标：`S=(n01+n10)/N`，与该格 `S_sim=1.0` 描述性对拍，附 Wilson 95％区间。
- 错误结构：偶校验错误率、四 outcome 总变差距离，以及 `01／10` 条件平衡 `χ²(df=1)`。
- 空 counts、Failed、Canceled 不评分；shots 不符照实标记；重复 Completed 回收以 canonical counts 哈希检测变化。

## 自证结果

五组已知答案全过：模拟目标格、均匀四 outcome、全偶校验、全单 outcome、混合错误。另验空 counts 不评分、非法 bitstring 拒绝。独立 SciPy 对拍最大绝对误差 `3.618915179919496e-25`。

分析器 commit `d58db88ff01bfc4ab14d92de591d6854176a5ef7`；生产集成 commit `213e1fb824d5e3e3614c64259184741b481a0623`。分析器尚未用于真实 counts，不构成实验完成证据。

下一步只回收同一 task id；终态后按上述预注册口径判读，零重发，不把单格外推为八格或真机 QRAND。
