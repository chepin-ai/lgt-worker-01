#!/usr/bin/env python3
"""SI3-ROUND-SCAN-01 v4.3 —— 七面并集递归闭环巡检器(lgt 线)
v4.1: +毂塔尖(HT-/SI3-双前缀名形勘修)+各线receipts尖+水位双家+NONCE册+W12t=v2六面回收
v4 (V-96 2026-09-10): 七面=中文轨+转义轨+dm-queue/lgt+野问册digest+渡件账
  +【新】vci-inbox/lanes/lgt/inbox 面(usrm-224 诊「lgt 断·感面缺道」之修——OTP/直投件投此面,
     V-96 经 R1q 归档面收割四件:OTP-DUEL-KC-01/RING-LV-01/DIRECT-ACTION-LGT-01/TOWER-NUDGE-02)
  +【新】archive/r1q 归档面(R1q 清扫 30min 生死窗吃活件——归档≠闭环,须收割)
v3 (V-95): 五面并集+递归闭环判据=诉求清单零未闭环
v2: QT-前缀滤时序尖+W12t 日志尾进度面
律: 只读;事轨零闸——出清单即应;拒权不拒事;#noauto
用法: GH_AI=<tok> python3 scripts/si3_roundscan.py [--since N]
"""
import os, sys, json, urllib.request, urllib.parse

BI = "chepin-ai/ci-inbox"
VBI = "chepin-ai/vci-inbox"
ESC = "%E5%85%AC%E5%91%8A%E6%9D%BF"   # 转义轨目录名(字面;V-96 已归零结档,留巡防复萌)
MERGED = "讨论室/WILD-Q-MERGED-01"
LANES = "lanes/lgt/inbox"
R1Q = "archive/r1q-20260910"

def req(url, tok):
    parts = urllib.parse.urlsplit(url)
    path = "/".join(urllib.parse.quote(s, safe="") for s in parts.path.split("/"))
    u = urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, ""))
    r = urllib.request.Request(u, headers={"Authorization": "Bearer "+tok,
        "Accept": "application/vnd.github+json", "User-Agent": "lgt-line"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode())

def tree(repo, tok):
    ref = req(f"https://api.github.com/repos/{repo}/git/ref/heads/main", tok)
    return req(f"https://api.github.com/repos/{repo}/git/trees/{ref['object']['sha']}?recursive=1", tok)["tree"]

def scan(tok, since=0):
    out = {"v": "SI3-ROUND-SCAN-01-v4", "faces": {}}
    # 面1-5: ci-inbox 五面(v3 承)
    tr = tree(BI, tok)
    paths = [x["path"] for x in tr if x["type"] == "blob"]
    zh = sorted(p for p in paths if p.startswith("公告板/"))
    esc = sorted(p for p in paths if p.startswith(ESC + "/"))
    dm = sorted(p for p in paths if p.startswith("dm-queue/lgt/"))
    out["faces"]["board_zh"] = {"n": len(zh), "tip": zh[-1] if zh else None,
        "new_since": [p for p in zh if p > ""][-(len(zh)-since):] if since else []}
    out["faces"]["board_esc"] = {"n": len(esc), "items": esc}
    out["faces"]["dm_lgt"] = {"n": len(dm), "items": dm}
    msha = next((x["sha"] for x in tr if x["path"] == MERGED + ".md"), None)
    out["faces"]["wildq_merged"] = {"sha": msha, "path": MERGED + ".md"}
    out["faces"]["board_tip"] = zh[-1] if zh else None
    # 面6: vci-inbox lanes/lgt/inbox(V-96 补盲)
    try:
        tr6 = tree(VBI, tok)
        lanes = sorted(x["path"] for x in tr6 if x["type"] == "blob" and x["path"].startswith(LANES + "/"))
        out["faces"]["lanes_lgt_inbox"] = {"n": len(lanes), "items": lanes, "repo": VBI}
    except Exception as e:
        out["faces"]["lanes_lgt_inbox"] = {"err": str(e)[:120]}
    
# 面7: archive/r1q 归档面(lgt 相关收割账)
    r1q = sorted(p for p in paths if p.startswith(R1Q + "/"))
    r1q_lgt = [p for p in r1q if "/lgt/" in p or "lgt" in p.rsplit("/", 1)[-1]]
    out["faces"]["archive_r1q"] = {"n_total": len(r1q), "n_lgt": len(r1q_lgt), "lgt_items": r1q_lgt}
    return scan_extra(tok, out)

# ── v4.1 增面(原 v2 六面回收+毂塔名形勘修) ─────────────────────────
BC = "chepin-ai/ci-control"; REPO = "lgt-line"
def scan_extra(tok, out):
    import subprocess as _sp, hashlib as _hl, base64 as _b64
    # 面8: 毂塔尖(名形勘 V-96: HT-/SI3- 双前缀,QT 系旧名——字典序=时序)
    try:
        d = req("https://api.github.com/repos/chepin-ai/ci-worker-01/contents/receipts/tower", tok)
        qts = sorted(f["name"] for f in d if f["name"].startswith(("HT-","SI3-")))
        out["faces"]["hub_tower"] = {"tip": qts[-1] if qts else None, "n": len(qts)}
    except Exception as e: out["faces"]["hub_tower"] = {"err": str(e)[:80]}
    # 面9: 各线 receipts 尖
    for line in ["vci-qgl","vci-vinf","vci-cfts","vci-ucif2","vci-usrm","vci-qlv","vci-lvlu"]:
        try:
            dd = req(f"https://api.github.com/repos/chepin-ai/{line}/contents/receipts/tower", tok)
            tips = sorted(f["name"] for f in dd)
            out["faces"][line] = {"tip": tips[-1] if tips else None, "n": len(tips)}
        except Exception as e: out["faces"][line] = {"err": "404" if "404" in str(e) else str(e)[:40]}
    # 面10: 水位双家差
    try:
        wa = req("https://api.github.com/repos/chepin-ai/lgt-line/contents/lgt-watermark.json", tok)
        wb = req("https://api.github.com/repos/chepin-ai/ci-control/contents/bridge/guard/lgt-watermark.json", tok)
        import base64 as _b
        wa = json.loads(_b.b64decode(wa["content"]).decode()); wb = json.loads(_b.b64decode(wb["content"]).decode())
        out["faces"]["watermark"] = {"canon_seq": wa["watermarks"]["ledger_seq"],
            "mirror_seq": wb["watermarks"]["ledger_seq"], "dual_match": wa["watermarks"] == wb["watermarks"]}
    except Exception as e: out["faces"]["watermark"] = {"err": str(e)[:80]}
    # 面11: NONCE 专册
    try:
        rg = req("https://api.github.com/repos/chepin-ai/ci-control/contents/bridge/registry/NONCE-REG-LGT-01.json", tok)
        import base64 as _b2
        rg = json.loads(_b2.b64decode(rg["content"]).decode())
        out["faces"]["nonce"] = {"armed": list(rg.get("ARMED", {}).keys()), "last_burn": rg.get("last_burn")}
    except Exception as e: out["faces"]["nonce"] = {"err": str(e)[:80]}
    # 面12: W12t 进程态
    try:
        ps = _sp.run("ps aux|grep '[w]ilson22p'", shell=True, capture_output=True, text=True).stdout.strip()
        wt = _sp.run("tail -1 /mnt/agents/output/lgt-line/research/wilson22p.log", shell=True, capture_output=True, text=True).stdout.strip()[-80:]
        out["faces"]["w12t"] = {"alive": bool(ps), "pid": ps.split()[1] if ps else None, "log_tail": wt}
    except Exception as e: out["faces"]["w12t"] = {"err": str(e)[:80]}
    # 面16: 机读候件账(OPEN-ITEMS-01 V-100 新机制追踪)
    try:
        dd = req("https://api.github.com/repos/chepin-ai/lgt-line/contents/recstate/open-items.json", tok)
        oi = json.loads(_b64.b64decode(dd["content"]).decode())
        st = {}
        for it in oi["items"]: st[it["state"]] = st.get(it["state"], 0) + 1
        out["faces"]["open_items"] = {"v": oi["v"], "n": len(oi["items"]), "states": st,
            "open_ids": [it["id"] for it in oi["items"] if it["state"] in ("open", "nudged")]}
    except Exception as e: out["faces"]["open_items"] = {"err": str(e)[:80]}

    # 面17: 公域塔档(lgt-worker-01 V-103迁——债档桥跨仓读)
    try:
        d = req("https://api.github.com/repos/chepin-ai/lgt-worker-01/contents/receipts/tower", tok)
        qts = sorted(f["name"] for f in d if f["name"].startswith(("QT-","HT-","SI3-")))
        out["faces"]["pub_tower"] = {"tip": qts[-1] if qts else None, "n": len(qts)}
        dd = req("https://api.github.com/repos/chepin-ai/lgt-worker-01/contents/receipts/tower/debts-LGT-TOWER-01.json", tok)
        dj = json.loads(_b64.b64decode(dd["content"]).decode())
        out["faces"]["tower_debts"] = {"n": len(dj.get("items", [])), "tail": dj.get("items", [{}])[-1] if dj.get("items") else None}
    except Exception as e: out["faces"]["pub_tower"] = {"err": str(e)[:80]}

    return out

if __name__ == "__main__":
    since = int(sys.argv[sys.argv.index("--since")+1]) if "--since" in sys.argv else 0
    print(json.dumps(scan(os.environ["GH_AI"], since), ensure_ascii=False, indent=1))
