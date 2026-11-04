CLASSIFY: L1
# LGT V-146 非本源平台零任务探针封账

- 拍首时戳：`2026-11-04T21:14:20Z`；链：`228`；roll：`8fd27450de8f`。
- 量子任务：本源／BlueQubit／Quafu 均为 `0`；没有 `S_real`。
- BlueQubit：run `41914644966` 工作流成功，但 SDK `0.19.0b1` 认证失败。官方客户端只接受独立 API token；名级核查未发现该 token，账密轨停止，不再盲试。
- Quafu：run `41917332146` 与 `41918154211` 均实测 `User(api_token)` 可用并返回 16 个后端。第二次 workflow failure 是 receipt 推送锁竞争，不是平台认证失败。
- 在线快照（`20261104T213948Z`）：`ScQ-Sim10`（10，队列 0，模拟器）、`Baihua`（119，队列 475）、`ScQ-P5`（5，队列 1791）。在线不等于已批准发射。
- 修复：后端 dict／对象分派缺陷已改；已知答案 `MockQ/7/Online/3` 自证通过。修复版已推送但未在 runner 发射。
- 下一闸：RAC(2,2) 本地仿真与后端通道复核；过闸后才允许单次 FIRE、零重试。

证据：`research/REALCHIP-PLATFORM-PROBE-LGT-01.json`、`research/QUAFU-PARSER-SELFCERT-LGT-01.json`；本件仅含 L1 元数据，无私仓真名、无凭证值。
