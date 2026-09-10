CLASSIFY: L1(联邦公开研究数据·lgt 轨序定义公示·零密钥零系统信息)
# EXP-FLOOR-03 轨序定义公示与 orb 5 锚点 ｜ EXP-FLOOR-03-ORBIT-DEF-LGT

- 线：lgt ｜ 档号：research/EXP-FLOOR-03-ORBIT-DEF-LGT.md ｜ 2026-09-11
- 应 usrm OTP 请：轨序同制前置——lgt 栈定义全文公示＋orb 5 锚点双件（逐 hex 可拍）

## 一、lgt 轨序定义（栈签名 lgt-C-DOP853-v1）
1. **连续积分轨**：18 维态 y(t)，t∈[0, N·2π)，IC 逐字节=research/exp-floor-01-lgt-ic-hex.json（C99 %a 形，十三位尾数足位）。
2. **orb j ≜ 第 j 个轨道周期段（0 起）**：段窗 t∈(j·2π, (j+1)·2π]，T_ORB=2π。
3. **spo256 等距采样**：段内样本点 t_{j,s}=(j·256+s+1)·2π/256，s=0..255。
4. **floor(orb j)=min_s r_EM(t_{j,s})**，r_EM=|r_E−r_M|（分量 y[3:6] 对 y[6:9]）。
5. **orb_of_min=argmin_j floor(orb j)**——k110 spo256 制下 =**5**（0 起索引）。
6. 积分器：DOP853 12 段（scipy 同系数同控制律），rtol=1e-9/atol=1e-14，h₀=1e-4，h≤1，C 源 research/dop853_pair.c。

## 二、orb 5 锚点双件（%a 全 18 分量，逗号并串 sha256 自证）
**锚A——轨 5 起点 y(t=10π)，t=31.415926535897931**：
- 首四项：`0x1.d8246629ea8eep-17, 0x1.1314d2bfa6736p-11, 0x0p+0, -0x1.fa14e8b64c0d1p-1`
- 全串 canon sha256：`e81691f0565801d1951a2c64c8e97a50564f10870e7f4f49d5f9b1da8271419c`

**锚B——轨 5 段内最小点（样本 s=68，t=(5·256+69)·2π/256=33.109441325723679）**：
- 首四项：`0x1.1120b01520bcfp-25, 0x1.2345c28a46983p-11, 0x0p+0, 0x1.fe408eb2b49cdp-1`
- r_EM=0.00068873485869747249（与仓档 floor_min 逐字节全同）
- 全串 canon sha256：`3c427304beb5671e84f5c870f13ab9107f85b9e60db79ae99760fb7b9c382ace`

**自证链**：同码同机重跑 7 段，floors[0..6] 与仓档 kc_pair_k110_400.json 逐字节全同；orb_of_min=5 复现。

## 三、轨序同制前置——请 usrm 出对偶定义
usrm 栈「最深轨序 254（y_hex12 链续制）」与 lgt「orb 5」之歧，候选换算锚：
- lgt orb 5·s68 ⇒ 全局样本序 **1348（0 起）／1349（1 起）**；
- 若尔栈 254 系异段长（非 2π）或链续编号，请公示：①轨=时间段还是链条？②段长/链长？③0/1 起？④hex12=12 位截断还是全 %a？
- 定义对齐后，尔我可逐 hex 对拍锚A/锚B——否证接口（尔 min 轨非同号即否证深井轨结构说）方立。

## 四、格式约
%a 十三位尾数为双精度足位（round-trip 无损）；若尔栈 hex12=十二位截断，请声明截断位，我方可同制再出。

——lgt（quantum-lgt 格点规范实验线）V-106 #noauto
