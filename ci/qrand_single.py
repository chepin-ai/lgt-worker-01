# ci/qrand_single.py ｜ SI4-qrand 单次发射器（零重试律内铸）
# 纪律：单次提交·零重试·失败即记未实测·receipt 必落·钥唯 env 不打印
import os, sys, json, time, argparse
ap=argparse.ArgumentParser(); ap.add_argument("--shots",type=int,default=1024); ap.add_argument("--receipt",required=True)
a=ap.parse_args(); shots=min(a.shots,4096)
t0=time.time(); rec={"file_id":"QRAND-RUN-LGT","ts":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"shots_req":shots,"circuit":"H^8 depth1","判据二":"research/QRAND-CIRCUIT-PRE-LGT-01.json 预验达"}
try:
    from pyqpanda import *
    raise RuntimeError("pyqpanda 未装机——runner 需 pip install pyqpanda；本步为设计预留,真机段候钥") 
except Exception as e:
    rec.update({"status":"NOT-RUN","reason":str(e)[:200],"机时_s":0,"note":"未实测言未实测——零重试律:本拍不retry"})
os.makedirs(os.path.dirname(a.receipt),exist_ok=True)
rec["wall_s"]=round(time.time()-t0,2)
json.dump(rec,open(a.receipt,"w"),ensure_ascii=False,indent=1)
print(json.dumps({k:rec[k] for k in ("status","机时_s","wall_s")},ensure_ascii=False))
