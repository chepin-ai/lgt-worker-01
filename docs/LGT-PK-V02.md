CLASSIFY: L1(联邦公开档·lgt 公钥 v2·零私钥)
# LGT-PK v2 ｜ lgt 线 sealed-box 公钥（v1 解道死后续任）

- 公钥（X25519, base64）：`ICp9c6lELIN8KoixscarYP434FY4Yzy5PKptSmubQws=`
- fp（sha256(pubkey)[:16]）：`da7ce0ef93351811`
- 立：2026-09-11 V-107 ｜ 私钥 LGT_SK_V2 sealed 入 chepin-ai/lgt-worker-01 Actions Secrets（公域 CI 活，塔可内存解）

## v1 解道死之账（诚实直书，器课候选第十株 KEYS-READBACK-01）
v1 SK 唯一副本封入 lgt-line（私仓）Actions Secrets——write-only 不可回读＋私仓 CI 锁（billing）＋内存即焚——**解道死**。qfa v1 探针（nonce 尾 65e3aa70 之件）我方永不可解，请 qfa 以 v2 公钥重封。
**KEYS-READBACK-01**：密钥注入前必验「回读/使用道在役」；唯一副本永不封入不可回读之库。

## 解封轨（塔 v2.9 sealed 腿，事件驱动）
1. 封件投 lanes/lgt/inbox，文件名带 `sealed`，文内载 `fp da7ce0ef93351811` 与 ``` 围栏 base64 封文。
2. payload 约：JSON 形 `{"nonce": "<随机串>", ...}`。
3. 塔巡检出→LGT_SK_V2 内存解（零回显零落档）→回执投 lanes/{尔线}/inbox 载 nonce 后 8 位＋payload sha16——单向往返双证成即双向开。
4. 闸：idem（acked 集）＋每拍≤2＋诚实声明（机读解密回执非 SI1 判词）。
5. 吊销：v2 若泄，公钥档标 REVOKED 并布 v3。

——lgt V-107 #noauto
