CLASSIFY: L1
# V-147 Quafu RAC 单格单次发射：仿真全绿，真机在队

## 证据地位

本件只证明单格 RAC 电路已被平台接收入队；尚无真机 counts，不得记作已完成实验。

## 仿真与判读自证

- SIM run `41922417262`：八格 `S_sim=1.0`，每格 1024 shots。
- big-endian 已知答案：`X(q0)→10`、`X(q1)→01` 均通过；目标格模拟 counts 为 `01:513`、`10:511`，奇校验成功率 1.0。
- 本地 QRAND：`χ²=256.5`，`df=255`，`p=0.4618385405538116`，通过 `p≥0.01` 闸。
- 独立 NumPy 态矢量重建得到 `01／10` 各 0.5，和 SDK 模拟一致。

## 唯一真机提交

- FIRE run `41922704802`：`ScQ-P5`，单电路，1024 shots，`Task.send` 一次，零重试，无备用后端。
- task id：`91C842B01A238734`；QASM SHA-256：`24aea2fed6cea4bb6aa1532278b7d33984640de8055acdca29462ace0c0921c6`。
- 首次 RETRIEVE run `41923004075`：`In Queue`，counts 为空。
- 账目：`jobs=1`、`pending=1`、`returned_shots=0`、`S_real_pilot=null`；本源任务与机时均为 0。

## 边界与下一步

不把单格结果外推为八格 `S_real`，不在真机补发 QRAND，不开启 WILDQ-C。仓内一次性花费锚已启用；后续只回收上述 task id，完成或失败均零重发。私域正本以 `REPO` 代号归档。
