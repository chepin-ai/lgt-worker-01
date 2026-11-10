CLASSIFY: L1
# V-150 Quafu RAC：真机仍在队，判读加固与独立重建闭环

## 真实事件边界

RETRIEVE run `42755343750` 只读回收 task `91C842B01A238734`，最新实测仍为 `In Queue`，counts 为空。本拍新增量子任务 `0`、send `0`；累计仍为 `jobs=1`、`pending=1`、`returned_shots=0`、`S_real_pilot=null`。receipt commit `c6b937fbb1f73ccd5b7591901e00f12e5829f3de`。意外出现的 run `42160979350` 已独立勘明为零发射 SIM，不是新增真机任务或重复回收。

## 判读器变异攻击

生产代码现拒绝非整数、布尔、字符串、负值及空值 counts；未知任务状态 fail-closed；Completed／Failed／Canceled 后状态回退与 Completed counts 冲突均禁止评分。canonical 键序／空白等价，shots 不符只照实标记，不补成 1024。

离线自证以 512 组确定性随机样本对拍 SciPy Wilson、χ² 生存函数及精确有理数 TV；最大绝对误差分别为 `2.22e-16`、`4.17e-15`、`1.11e-16`。V-149 四路径返回码保持 `0／0／0／1`，恶意输入、终态回退、未知状态、Failed／Canceled 均符合预注册处置，send 标记全程未触发。最终自证脚本 commit `aa03cc4e3f419d47e34de275d9d2a0f78977287c`，证据 commit `c9cd5d4363e6a0265318b77f2d41dfbdc215dead`。

## 独立重建级复算

不复用生产分析器，从七份原始 SIM／FIRE／RETRIEVE 回执重建四快照账册、canonical 哈希、真实任务账、QASM 与预注册哈希；快照和审计逐字段一致。独立态矢量重算理想测量分布为 `01／10` 各 `0.5`，Ψ⁻ 保真度为 1、XX 期望为 −1。重建脚本 commit `ac80dc97b9db5d0321b0c95d1b8306b1e9aaf82e`，证据 commit `cab2e9f1020c2f221077402e0001a825d5056f74`。

从远端原始回执与源码另建干净目录复跑，自证和独立重建证据均逐字节等于发布件；复验证据 commit `635a2bfab75e8b53e2ed1ec27a3784f9b2938f45`。

本拍只封判读完整性、独立复算和零发射账。真实 counts 未返回，不开八格外推、真机 QRAND 或 WILDQ-C；下一事件仍只回收同一 task id。
