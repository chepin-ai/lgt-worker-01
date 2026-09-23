# ci/realchip_lgt_01.py ｜ lgt 真机单次发射器（本源机时纪律逐字守）
# 纪律：仿真预验为闸(不过闸不发射)/单次批量提交/零重试/钥唯 env 永不打印/receipt 必落
# 实验：QRAND H⊗8 ×1 + RAC n=2,d=2 八电路（4编码×2基）——一批 9 电路 1024 shots
import os, sys, json, time, math, hashlib, datetime

SHOTS = 1024
TOL_S_SIM = 0.90          # 仿真闸：RAC S_sim 阈（1024 shots 有限样本噪声 ~5.5e-3/估）
CHI2_P_MIN = 0.01         # 仿真闸：QRNG χ² p 阈

def now():
    return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

def tsname():
    return datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')

# ---------- 电路构建 ----------
def build_circuits(q, c):
    """返回 [(name, QProg, meta)] — 9 电路"""
    from pyqpanda import QProg, H, CNOT, X, Z, Measure
    progs = []
    # QRAND: H⊗8
    p = QProg()
    for i in range(8):
        p << H(q[i])
    for i in range(8):
        p << Measure(q[i], c[i])
    progs.append(("QRAND_H8", p, {"kind": "qrng"}))
    # RAC n=2,d=2: Bell + Alice 编码(X:x1, Z:x2) + Bob 基(Z 直读 / X 加 H)
    for x1 in (0, 1):
        for x2 in (0, 1):
            for basis in ("Z", "X"):
                p = QProg()
                p << H(q[0]) << CNOT(q[0], q[1])
                if x1: p << X(q[0])
                if x2: p << Z(q[0])
                if basis == "X":
                    p << H(q[0]) << H(q[1])
                p << Measure(q[0], c[0]) << Measure(q[1], c[1])
                progs.append((f"RAC_x1{x1}x2{x2}_{basis}", p,
                              {"kind": "rac", "x1": x1, "x2": x2, "basis": basis}))
    return progs

# ---------- 判读 ----------
def rac_S(results, metas):
    """results: list of dict {bitstring(int或str): prob/count}; 返回 S(8 格均值)"""
    succ = []
    for res, m in zip(results, metas):
        if m["kind"] != "rac":
            continue
        tot, hit = 0.0, 0.0
        for k, v in res.items():
            bits = int(k) if not isinstance(k, str) else int(k, 2) if set(k) <= set("01") else int(k)
            b0 = (bits >> 0) & 1   # q0
            b1 = (bits >> 1) & 1   # q1
            want = m["x1"] if m["basis"] == "Z" else m["x2"]
            tot += v
            if (b0 ^ b1) == want:
                hit += v
        succ.append(hit / tot if tot else 0.0)
    return sum(succ) / len(succ), succ

def qrng_check(res):
    """QRNG 均匀性: 256 格 χ² (df=255) 返回 (chi2, p近似) — p 用 Wilson–Hilferty 近似"""
    tot = sum(res.values())
    exp = tot / 256.0
    chi2 = sum((res.get(str(i), res.get(i, 0)) - exp) ** 2 / exp for i in range(256))
    z = ((chi2 / 255.0) ** (1/3) - (1 - 2/(9*255))) / math.sqrt(2/(9*255))
    p = 0.5 * math.erfc(z / math.sqrt(2))
    return chi2, p

def norm_counts(res):
    """pyqpanda 各版本返回 dict 或 list[(k,v)] — 统一成 {str(十进制): count}
    键形实测: 二进制串('00','11')→int(k,2); 已十进制者直通"""
    items = res.items() if isinstance(res, dict) else res
    out = {}
    for k, v in items:
        if isinstance(k, str) and k and set(k) <= set("01"):
            kk = str(int(k, 2))
        else:
            kk = str(int(k))
        out[kk] = out.get(kk, 0) + v
    return out

# ---------- 仿真预验（零机时） ----------
def sim_gate(progs):
    from pyqpanda import CPUQVM
    m = CPUQVM()
    m.init_qvm()
    q = m.qAlloc_many(8); c = m.cAlloc_many(8)
    sim = []
    for name, _, meta in progs:
        _, p2, _ = [(n, pr, mt) for n, pr, mt in build_circuits(q, c) if n == name][0]
        r = m.run_with_configuration(p2, c, SHOTS)
        sim.append(norm_counts(r))
    metas = [mt for _, _, mt in progs]
    S_sim, per = rac_S(sim, metas)
    chi2, p = qrng_check(sim[0])
    m.finalize()
    return S_sim, per, chi2, p, sim

# ---------- 主流程 ----------
def main():
    t0 = time.time()
    rec = {"file_id": "REALCHIP-LGT-01", "ts": now(), "shots": SHOTS,
           "batch": "1×QRAND_H8 + 8×RAC(n=2,d=2)", "chip": "origin_72(本源悟空)",
           "law": "本源机时纪律: 仿真预验为闸/单次批量/零重试/≤120s",
           "status": "PREFLIGHT"}
    # 钥：env 序贯探针(auth 不耗机时), 一经 init 成即锁, 真机提交唯一发
    token = None; keyfp = None; tried = []
    from pyqpanda import QCloud
    for name in ("ORIGINQC_TOKEN", "ORIGINQC_TOKEN_2", "ORIGINQC_TOKEN_3", "ORIGINQC_TOKEN_4"):
        t = os.environ.get(name, "").strip()
        if not t:
            continue
        tried.append(name)
        try:
            qcm = QCloud()
            qcm.set_configure(72, 72)
            qcm.init_qvm(t)
            token = t; keyfp = hashlib.sha256(t.encode()).hexdigest()[:12]
            break
        except Exception as e:
            rec.setdefault("auth_probe", []).append({"env": name, "err": str(e)[:120]})
    rec["key_fp"] = keyfp
    rec["auth_envs_tried"] = tried
    if token is None:
        rec.update({"status": "NOT-RUN", "reason": "auth 探针全败(未耗机时)", "机时_s": 0})
        return rec, t0
    try:
        q = qcm.qAlloc_many(8); c = qcm.cAlloc_many(8)
        progs = build_circuits(q, c)
        # 闸：仿真预验（本地 CPUQVM, 零机时）
        S_sim, per_sim, chi2, p, sim = sim_gate(progs)
        rec["preflight"] = {"S_sim": round(S_sim, 6), "per_sim": [round(x, 4) for x in per_sim],
                            "qrng_chi2": round(chi2, 2), "qrng_p": float(f"{p:.4g}"),
                            "gate": "S_sim>=%.2f 且 p>=%.2f" % (TOL_S_SIM, CHI2_P_MIN)}
        if S_sim < TOL_S_SIM or p < CHI2_P_MIN:
            rec.update({"status": "GATE-FAIL", "reason": "仿真预验未过闸——不发射,零机时", "机时_s": 0})
            qcm.finalize(); return rec, t0
        # 发射：单次批量, 零重试
        tsubmit = time.time()
        result = qcm.batch_real_chip_measure([pr for _, pr, _ in progs], SHOTS,
                                             real_chip_type.origin_72)
        rec["submit_wall_s"] = round(time.time() - tsubmit, 2)
        counts = [norm_counts(r) for r in result]
        metas = [mt for _, _, mt in progs]
        S_real, per_real = rac_S(counts, metas)
        chi2r, pr_ = qrng_check(counts[0])
        rec.update({"status": "DONE", "S_real": round(S_real, 6),
                    "per_real": [round(x, 4) for x in per_real],
                    "qrng_chi2_real": round(chi2r, 2), "qrng_p_real": float(f"{pr_:.4g}"),
                    "counts": [{k: v for k, v in sorted(r.items())} for r in counts],
                    "机时_s": round(time.time() - tsubmit, 2)})
        qcm.finalize()
    except Exception as e:
        rec.update({"status": "FAILED", "reason": str(e)[:300],
                    "机时_s": round(time.time() - t0, 2),
                    "note": "零重试律: 不retry,失败即记未实测回仿真续研"})
    return rec, t0

if __name__ == "__main__":
    rec, t0 = main()
    rec["wall_s"] = round(time.time() - t0, 2)
    os.makedirs("receipts", exist_ok=True)
    path = f"receipts/realchip-lgt-01-{tsname()}.json"
    with open(path, "w") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: rec.get(k) for k in ("status", "S_real", "S_sim", "key_fp", "机时_s", "wall_s")},
                     ensure_ascii=False))
