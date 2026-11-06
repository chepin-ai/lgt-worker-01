CLASSIFY: L1
# V-149 Quafu RAC：真机仍在队，跨回收不可变对拍已接入生产

## 真实回收快照

RETRIEVE run `42155450189` 只读回收 task `91C842B01A238734`，状态仍为 `In Queue`，counts 为空。本拍新增量子任务 `0`、send `0`；累计 `jobs=1`、`pending=1`、`returned_shots=0`、`S_real_pilot=null`。receipt commit `fcaadf27f67c3980fb59eab008d94f51c5d54b78`。

## 不可变判读联锁

三次真实回收快照已进入持久账册，当前均为在队、无 Completed 记录。每次后续回收先规范化 `00／01／10／11` 并计算 SHA-256，再允许评分：首次 Completed 记录首个哈希；同哈希重复回收判 `IMMUTABLE_OK`；出现不同 Completed 哈希即判 `IMMUTABLE_VIOLATION`，保留全部证据并禁止评分，不得择优。

## 已知答案自证

直接执行生产回收脚本的离线桩测试依次覆盖 `NO_COMPLETED → FIRST_COMPLETED → IMMUTABLE_OK → IMMUTABLE_VIOLATION`，返回码为 `0／0／0／1`；冲突用例无分析结果、`S_real_pilot=null`，send 全程未调用。另验账册篡改、跨任务污染与冲突 run id 均拒绝。

不可变模块 commit `2b90a856e68c492da9ee4356224ae1487e84eb97`；生产集成 commit `030e61d88d57e5263ad8b6e95d0aad78f5ffcfee`；workflow commit `83af25e85a10998a8fff88451796deb242fad1ba`。

下一步仍只回收同一 task id，零重发、零备用后端；没有真实 counts，不开八格外推、真机 QRAND 或 WILDQ-C。
