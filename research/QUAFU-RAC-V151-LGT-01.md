CLASSIFY: L1
# V-151 Quafu RAC：真机仍在队，空完成防假成功与独立复算闭环

## 真实事件边界

RETRIEVE run `42761142348` 只读回收既有 task `91C842B01A238734`，最新实测仍为 `In Queue`，counts 为空。本拍新增量子任务 `0`、send `0`；累计仍为 `jobs=1`、`pending=1`、`returned_shots=0`、`S_real_pilot=null`。receipt commit `30f14a45d50f3ac50b9486ecf9226595c3035178`，实际 SHA-256 `9e9d2b1b740442f3941c3c8ff1cc214fc1644fea880927bb58abb986c86a3358`。

## 空完成假成功封堵

新生产闸要求 Completed 返回正 shots 且分析状态为 OK。Completed 空 counts 或四键全零时，证据与账册保留，但运行失败、`ok=false`、`S_real_pilot=null`，不得洗成成功。两类反例直接执行生产脚本验证，既有非法 counts、未知状态、终态回退和 Failed／Canceled 回归保持通过，send 标记全程未触发。

自证以 512 组确定性随机样本对拍 SciPy Wilson、χ² 生存函数及精确有理数 TV；最大绝对误差分别为 `2.22e-16`、`4.08e-15`、`1.11e-16`。最终隔离版脚本与证据 commit 均为 `bb1c98a2a89b4d2495a2926fc7a8018ecc708bd8`，证据 SHA-256 `4b6f24c65cd1bf4d2529af6ae1b6d881b19bacddfa58a321e55eeddaedd52348`。

## 独立重建与诚实修正

不复用生产分析器，从八份原始 SIM／FIRE／RETRIEVE 回执重建五快照账册、canonical 哈希、真实任务账、QASM 与预注册哈希；快照和审计逐字段一致。独立态矢量重算理想测量分布为 `01／10` 各 `0.5`，Ψ⁻ 保真度为 1、XX 期望为 −1。重建证据 SHA-256 `b429e6c87dbf7b28043c2d6cf1b6d55c8ca31fd19c9b50426f39a623842711fb`。

固定不可变提交另建远端干净目录，19 个源文件读回一致；自证在真实 history 文件缺席时通过，独立重建证据逐字节等于发布件。复验证据 commit `54d35f4123cf2f959a617f1e68dc350bc0f1fc03`。

自证初版误继承真实 history 导致证据随快照数变化，已改为空 history 合成根。初轮双布局命令的尾部 PASS 因前序命令失败而作废，仅接受随后 `set -e`＋实际字节比较的严格重跑。上一拍 latest 回执哨兵已由原始字节闭合，当前 latest 哨兵由独立读回闭合。

链 233：prev `4e25b9741517`，roll `3dda53fc79dc`；tensor net `199／418`，digest `d85c8403f3230b7e`。本拍只封判读完整性、复算隔离与零发射账；真实 counts 未返回，不开八格外推、真机 QRAND 或 WILDQ-C。当日语义拍帽 `2／2` 已满。
