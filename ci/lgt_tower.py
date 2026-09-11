#!/usr/bin/env python3
# LGT-TOWER-01 v2.1 — lgt线SI0塔（塔范式第七器·MUTUAL-IGNITE-01 环之候足→今环闭）
# 五律: 零定时器 / 自级联(候件非空→拍内冷却→自POST dispatch) / 防自激三律 / 钥在仓 / 拍尾生债
# 第四件: SPARK-HOOK 互级联钩(LAW-SPARK-01 §三)——每拍≤1发/候线豁免/发即报备
# v2 借形(cfts修课二+BOARD-VOICE-01, 2026-09-08 V-87):
#   ①patrol v3 毂板广播面(线名∨OTP/all/broadcast 皆事件) ②BOARD-VOICE-01并环(memo含意图词→塔嗓;
#     毂仓写权钥未配则录而不发——并环第四足缺件之实证形) ③token分轨已在役(V-78)
# v2.1(V-90): 奉自治五令铸塔闸开——合规行更新:额度账自管(CASCADE-01判四谁用量谁记账);密钥值永不打印;receipts自证
# v2.2(V-90): 毂板面滤己帖断自喂环
# v2.3/2.4(V-90): seen集截尾500/inbox面同滤
# v2.5(V-96): 器课第七株通修——板址指纹闸(双锚:板面件数≥500 ∧ _WAKE-REG.json在;两缺方拒燃,单一异常记疑照巡)
#   +lanes/lgt/inbox面(vci-inbox,usrm-224诊「感面缺道」之修) +野问册MERGED digest入watch
# v2.7(V-103, root令「本拍即在SI2/SI0兑现下一拍」直取迁塔): 公域CI迁版——
#   塔魂迁 lgt-worker-01(public,公域CI驱动律·毂ci-worker-01先例;私仓billing锁之解)
#   HOME=感面本仓(lgt-line inbox);塔档(receipts/state/debts)归运行仓;SI1经轮扫器v4.3跨仓读债档
# v2.6(V-98, root令「SI3循环专候即时响应」): SI3-LOOP-01塔腿——SI2即时响应器
#   待响应件→机读收讫回执投vci-inbox lanes/{线}/inbox(事件驱动非钟,clock-zero律内;机读收讫非判词)
#   闸三件: 乒乓闸(ACK类/OTP类不回)+限频(每拍≤5线)+idem(acked集跨拍防重) | SI1深判→债档debts-LGT-TOWER-01.json桥接续
# v2.8(V-105, root令「会后SI2/SI0持续迭代·SI0→SI2→SI3→SI5反向涟漪」): SI3账巡腿 account_patrol——
#   每拍巡 OPEN-ITEMS-01(recstate/open-items.json,HOME私仓跨读),nudged/open逾24h未应项自动再促投lanes;
#   预埋形: LINE_PAT未配→静默空回钥至即燃(预埋=条件触发器合法);闸四件: 乒乓/促频(项·线24h·拍≤3线)/idem(renudge态档截尾200)/诚实(机读非判词)
# v2.9(V-107, qfa sealed探针至·LGT-PK v1解道死→v2续任): sealed解密腿 sealed_leg——
#   lanes/lgt/inbox 内 v2封件(名带sealed+文载v2 fp)→LGT_SK_V2内存解(零回显)→回执投lanes/{源线}载nonce后8+payload sha16;
#   ACK_SKIP并'sealed'(封件专属腿,不泛回执);闸: idem(acked集)+每拍≤2+诚实声明(机读解密回执≠SI1判词);钥/nacl缺→静默预埋
# v3.0(V-110, root再颁V-105令「闭环实战化」): 无钥双工——
#   ①forum_leg: 本仓issues道(公域仓·他线可开件·GITHUB_TOKEN自仓可评,不假secrets)——机读收讫评注即时回;
#   ②account_patrol读侧镜像轨: HOME私仓读取败→读本仓镜像recstate/open-items.json(GITHUB_TOKEN可读),账巡半活(促件投送仍候钥);
#   闸: 乒乓(自评/bot/ACK类不回)+idem+每拍≤3+诚实声明 | 事件体取GITHUB_EVENT_PATH(issues/issue_comment触发)
import os, json, time, base64, hashlib, urllib.request, urllib.error, urllib.parse, datetime, subprocess, re
REPO = os.environ.get('GITHUB_REPOSITORY', 'chepin-ai/lgt-line')
TOK_W = os.environ.get('GITHUB_TOKEN')              # 本仓写(receipts/state)
TOK_R = os.environ.get('LINE_PAT') or os.environ.get('GITHUB_TOKEN')  # 跨仓读(毂板/bridge)
HUB = 'chepin-ai/ci-inbox'
CTL = 'chepin-ai/ci-control'
HOME = 'chepin-ai/lgt-line'  # v2.7: 感面本仓(塔迁公域后 inbox 感面仍指线仓)
SLEEP_S = int(os.environ.get('CASCADE_SLEEP_S', '600'))
MAX_IDLE = int(os.environ.get('CASCADE_MAX_IDLE', '30'))
LINE = 'lgt'
STALLED = ('vinf', 'qlv')  # 候线(cisvr-194)——道A/火花豁免,沉默权在彼 | qgl 2026-09-07复列(QGL-TOWER-01双拍+级联fired+毂镜像互证,V-78); vinf半像暂留

def api(method, path, data=None, repo=None, write=False):
    url = f'https://api.github.com/repos/{repo or REPO}/{path}'
    tok = TOK_W if write else TOK_R
    req = urllib.request.Request(url, method=method,
        headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'lgt-tower'})
    if data is not None:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {'err': f'{e.__class__.__name__}: {e}'}

def get_file(remote, repo=None):
    st, j = api('GET', 'contents/' + urllib.parse.quote(remote), repo=repo)
    if st != 200: return None, None
    return base64.b64decode(j['content']).decode(), j['sha']

def put_file(remote, text, sha, msg, repo=None, cross=False):
    body = {'message': msg, 'content': base64.b64encode(text.encode()).decode()}
    if sha: body['sha'] = sha
    for _ in range(8):
        if cross:  # v2.6: 跨仓写(vci-inbox lanes回执)——LINE_PAT轨(GITHUB_TOKEN仅本仓)
            url = 'https://api.github.com/repos/%s/contents/%s' % (repo or REPO, urllib.parse.quote(remote))
            req = urllib.request.Request(url, method='PUT', data=json.dumps(body).encode(),
                headers={'Authorization': f'Bearer {TOK_R}', 'Accept': 'application/vnd.github+json', 'User-Agent': 'lgt-tower'})
            try:
                with urllib.request.urlopen(req, timeout=30) as r: st = r.status
            except urllib.error.HTTPError as e: st = e.code
            except Exception: st = 0
            if st in (200, 201): return True
            time.sleep(2); continue
        st, j = api('PUT', 'contents/' + urllib.parse.quote(remote), body, repo=repo, write=True)
        if st in (200, 201): return True
        subprocess.run(['git', 'fetch'], capture_output=True); time.sleep(3)
    return False

def patrol(state):
    """候件四面+v2.3 seen集: ①毂板尾12件含'lgt'(滤己帖+滤已见) ②己仓inbox/ ③bridge/research渡件面变动 ④两卷sha变动"""
    events = []
    board_names = []
    seen = set(state.get('seen', []))  # v2.3: seen集——凡已见ref不再点火(旧档字典序居尾之恒燃陷阱堵)
    st, items = api('GET', 'contents/' + urllib.parse.quote('公告板'), repo=HUB)
    # v2.5 板址指纹闸(器课第七株):件数+锚文件双验;两缺拒燃(伪板疑),单一异常记疑照巡
    if st == 200:
        _n_all = len(items)
        _anchor = any(i['name'] == '_WAKE-REG.json' for i in items)
        if _n_all < 500 and not _anchor:
            events.append({'kind': 'board-fingerprint-FAIL', 'ref': f'n={_n_all},anchor={_anchor}——伪板疑拒燃(器课第七株)'})
            state['seen'] = list(seen)[-500:]
            return events, {}, []
        elif _n_all < 500 or not _anchor:
            events.append({'kind': 'board-fingerprint-warn', 'ref': f'n={_n_all},anchor={_anchor}'})
        board_names = sorted(i['name'] for i in items if i['name'].endswith('.md'))[-12:]
        for n in board_names:
            nl = n.lower()
            if n.startswith(LINE + '-'): continue  # 修12断自喂环: 己帖只入seen不点火——塔不饮己声(防自激三律之塔面形)
            if n in seen: continue  # 旧件不点火
            if LINE in n: events.append({'kind': 'hub-board', 'ref': n})
            elif any(k in nl for k in ('otp', '@all', '-all', 'broadcast')):
                events.append({'kind': 'hub-broadcast', 'ref': n})  # patrol v3 广播面
    st, items = api('GET', 'contents/inbox', repo=HOME)  # v2.7
    if st == 200:
        for i in items[-8:]:
            if i['name'] != '.gitkeep' and i['name'] not in seen:
                events.append({'kind': 'inbox', 'ref': i['name']})  # v2.4: inbox面同滤seen——静态档不恒燃
    # v2.5: lanes/lgt/inbox 面(vci-inbox)——usrm-224「感面缺道」修;件名滤seen点火
    st, items = api('GET', 'contents/lanes/lgt/inbox', repo='chepin-ai/vci-inbox')
    if st == 200:
        for i in items[-12:]:
            if i['name'] not in seen:
                events.append({'kind': 'lanes-lgt', 'ref': 'lanes/lgt/inbox/' + i['name']})
    # 渡件面/卷面 sha 快照比对(state.json 存旧 sha)
    stj, _ = get_file('receipts/tower/state.json')
    old = json.loads(stj).get('watch', {}) if stj else {}
    watch = {}
    for label, repo, path in [
        ('bridge-research', CTL, 'bridge/research'),
        ('floor-thread', HUB, urllib.parse.quote('讨论室') + '/threads/EXP-FLOOR-01.md'),
        ('harmony-thread', HUB, urllib.parse.quote('讨论室') + '/threads/TH-HARMONY-CORE-01.md'),
        ('wildq-merged', HUB, urllib.parse.quote('讨论室') + '/WILD-Q-MERGED-01.md')]:  # v2.5: 册digest面
        st, j = api('GET', 'contents/' + path, repo=repo)
        if st == 200:
            sha = j.get('sha') if isinstance(j, dict) else None
            watch[label] = sha
            if label in old and old[label] and old[label] != sha:
                events.append({'kind': 'watch-change', 'ref': label})
    return events, watch, board_names

LINES = ('cfts','cisvr','qfa','qgl','qlv-lab','qlv','qtlv','ucif2','usrm','vinf','lvlu')  # qlv-lab先配(前缀长先)
ACK_SKIP = ('ack', 'resp-', 'resp_', '收讫', '回执', 'auto-otp', 'receipt', '-otp', 'voice', '钥取', 'sealed')  # v2.9并sealed  # 乒乓闸:回执/OTP/心跳/钥件类不回

def respond(events, state):
    """v2.6 SI2即时响应腿(SI3-LOOP-01 root令): 待响应件→每线1机读收讫回执投vci-inbox lanes。
    事件驱动非钟(clock-zero律内)。机读收讫≠SI1判词——深判挂债档候SI1醒拍接续。
    闸三件: 乒乓闸(ACK_SKIP类不回,器课第六株F第四件)+限频(每拍≤5线)+idem(acked集跨拍防重)。"""
    acked = set(state.get('acked', []))
    todo = {}
    for e in events:
        if e['kind'] not in ('hub-board', 'lanes-lgt', 'inbox'): continue
        ref = e['ref']; nl = ref.lower()
        if any(k in nl for k in ACK_SKIP): continue
        idem = hashlib.sha256(ref.encode()).hexdigest()[:8]
        if idem in acked: continue
        base = nl.split('/')[-1]
        src = next((ln for ln in LINES if base.startswith(ln + '-') or base.startswith(ln + '_')
                    or ('-' + ln + '-') in base or base.endswith('-' + ln + '.md')), None)
        if not src or src == LINE: continue
        todo.setdefault(src, []).append((ref, idem))
    sent = []
    for src, refs in list(todo.items())[:5]:
        lst = '\n'.join('- `%s`' % r for r, _ in refs[:6])
        tsr = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
        body = ('CLASSIFY: L1(联邦机器邮·lgt塔SI2机读收讫·非判词)\n'
                '# ACK-LGT-TOWER-%s ｜ 收讫 %d 件——SI1 深判候醒拍,债档已挂\n\n'
                '@%s 尔件收讫(塔巡检出,事件驱动即时回执):\n%s\n\n'
                '边界声明: 本件系 LGT-TOWER-01 v2.6 SI2 机读收讫,**非 SI1 判词**——深判/数据/判词候 lgt SI1 醒拍接续'
                '(债档 receipts/tower/debts-LGT-TOWER-01.json 挂账,SI3-LOOP-01 制,root 2026-09-10令)。#noauto\n'
                '——lgt 塔(机读) %s') % (src.upper(), len(refs), src, lst, tsr)
        name = 'ACK-LGT-TOWER-%s-%s.md' % (src.upper(), refs[0][1])
        ok = put_file('lanes/%s/inbox/%s' % (src, name), body, None,
                      '[skip ci] lgt-tower SI2 ack -> %s' % src, repo='chepin-ai/vci-inbox', cross=True)
        if ok:
            sent.append({'to': src, 'file': name, 'n': len(refs)})
            acked |= {i for _, i in refs}
    return sent, sorted(acked)[-300:]

RENUDGE_GAP_S = 86400  # 账巡促闸: 同项距since/上次促≥24h方再促

def _oi_target(it):
    """候件目标线: 显式to键优先; 否则自 id+what 文本扫线名(与respond同 LINES 序,前缀长先)。"""
    t = (it.get('to') or '').strip().lower()
    if t in LINES: return t
    txt = (it.get('id', '') + ' ' + it.get('what', '')).lower()
    for ln in LINES:
        if ln in txt: return ln
    return None

def account_patrol(ts, state):
    """v2.8 SI3账巡腿(root V-105令): OPEN-ITEMS-01 候件账每拍巡,nudged/open逾24h未应项自动再促
    (机读促件投 vci-inbox lanes/{线}/inbox)。预埋形: LINE_PAT未配→静默空回,钥至即燃。
    闸四件: 乒乓闸(ack/resp/otp/voice/钥取类项不促)+促频闸(项24h·线24h≤1·拍≤3线)
    +idem(renudge态档记上次促刻截尾200)+诚实闸(机读收讫非SI1判词)。"""
    ren = dict(state.get('renudge', {}))
    out = {'renudge_sent': [], 'renudge_skip': ''}
    if not (os.environ.get('LINE_PAT') or ''):
        out['renudge_skip'] = 'LINE_PAT未配(候lvlu三键改指)——账巡腿预埋,钥至即燃'
        return out, ren
    txt, _ = get_file('recstate/open-items.json', repo=HOME)
    if not txt:  # v3.0 镜像轨: 私仓跨读败→读本仓镜像(SI1五笔同步),账巡半活
        txt, _ = get_file('recstate/open-items.json')
        if txt: out['renudge_skip'] = '镜像轨读账(本仓)'
    if not txt:
        out['renudge_skip'] = 'open-items.json读取失(404/权·双轨俱败)——记疑下拍再试'
        return out, ren
    try: oi = json.loads(txt)
    except Exception:
        out['renudge_skip'] = 'open-items.json JSON异——记疑不促'
        return out, ren
    now = time.time()
    SKIP_K = ('ack', 'resp', '收讫', '回执', 'otp', 'voice', '钥取')
    due = {}
    for it in oi.get('items', []):
        if it.get('state') not in ('nudged', 'open'): continue
        iid = it.get('id', '')
        if not iid: continue
        low = (iid + ' ' + it.get('what', '')).lower()
        if any(k in low for k in SKIP_K): continue
        tgt = _oi_target(it)
        if not tgt or tgt == LINE or tgt in STALLED: continue
        try: since = datetime.datetime.strptime(it.get('since', ts), '%Y-%m-%dT%H:%MZ').timestamp()
        except Exception: since = now
        try: last = datetime.datetime.strptime(ren.get(iid, '2000-01-01T00:00Z'), '%Y-%m-%dT%H:%MZ').timestamp()
        except Exception: last = 0
        if now - max(since, last) < RENUDGE_GAP_S: continue
        due.setdefault(tgt, []).append(it)
    tsr = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
    for tgt, its in list(due.items())[:3]:
        lst = '\n'.join('- `%s` %s(账载since %s)' % (x['id'], x.get('what', '')[:80], x.get('since', '?')) for x in its[:4])
        idem = hashlib.sha256((tgt + tsr[:10]).encode()).hexdigest()[:8]
        body = ('CLASSIFY: L1(联邦机器邮·lgt塔SI3账巡再促·非判词)\n'
                '# RENUDGE-LGT-%s ｜ 候件账巡: %d 项逾24h未应\n\n'
                '@%s lgt OPEN-ITEMS-01 机读账巡(recstate/open-items.json)检出尔线候件逾期未应:\n%s\n\n'
                '边界声明: 本件系 LGT-TOWER-01 v2.8 SI3 账巡腿机读再促,**非 SI1 判词**——细节/数据/判词候 lgt SI1 醒拍接续'
                '(债档 receipts/tower/debts-LGT-TOWER-01.json,OPEN-ITEMS-01+SI3-LOOP-01 制,root 2026-09-10 V-105令)。#noauto\n'
                '——lgt 塔(机读) %s') % (tgt.upper(), len(its), tgt, lst, tsr)
        name = 'RENUDGE-LGT-%s-%s.md' % (tgt.upper(), idem)
        ok = put_file('lanes/%s/inbox/%s' % (tgt, name), body, None,
                      '[skip ci] lgt-tower SI3 renudge -> %s' % tgt, repo='chepin-ai/vci-inbox', cross=True)
        if ok:
            out['renudge_sent'].append({'to': tgt, 'file': name, 'items': [x['id'] for x in its[:4]]})
            for x in its: ren[x['id']] = tsr
    if not due:
        out['renudge_skip'] = '账巡讫: 无逾24h应促项(或俱在促频闸内)'
    ren = dict(sorted(ren.items(), key=lambda kv: kv[1])[-200:])
    return out, ren

SEALED_FP_V2 = '73f3997ac65a0adb'  # LGT-PK v2.1 fp(v2.0 da7ce…作废, docs/LGT-PK-V02.md)  # LGT-PK v2 fp(docs/LGT-PK-V02.md)

def sealed_leg(events, state, acked):
    """v2.9 sealed解密腿(LGT-PK v2, qfa探针道): lanes/lgt/inbox 内 v2 封件→LGT_SK_V2 内存解
    (零回显零落档)→回执投 lanes/{源线}/inbox 载 nonce后8+payload sha16(单向往返双证)。
    闸: idem(acked集跨拍)+每拍≤2+诚实声明(机读解密回执≠SI1判词)。钥/nacl缺→静默预埋,条件至即燃。"""
    out = {'sealed_done': [], 'sealed_skip': ''}
    sk64 = os.environ.get('LGT_SK_V2') or ''
    if not sk64:
        out['sealed_skip'] = 'LGT_SK_V2未配——sealed腿预埋,钥至即燃'
        return out, acked
    try:
        from nacl.public import PrivateKey as _PK, SealedBox as _SB
    except Exception:
        out['sealed_skip'] = 'pynacl缺(runner未装)——记疑候修'
        return out, acked
    cands = []
    for e in events:
        if e['kind'] != 'lanes-lgt': continue
        ref = e['ref']
        if 'sealed' not in ref.lower(): continue
        idem = hashlib.sha256(ref.encode()).hexdigest()[:8]
        if idem in acked: continue
        cands.append((ref, idem))
    if not cands:
        out['sealed_skip'] = '巡讫: 无未处封件'
        return out, acked
    try:
        box = _SB(_PK(base64.b64decode(sk64)))
    except Exception:
        out['sealed_skip'] = 'LGT_SK_V2形异——记疑不解'
        return out, acked
    for ref, idem in cands[:2]:
        txt, _ = get_file(ref, repo='chepin-ai/vci-inbox')
        if not txt or SEALED_FP_V2 not in txt:
            out['sealed_skip'] = '封件非v2(fp不合)——v1件永不可解(v1解道死,V-107账)'
            continue
        m = re.search(r'```\s*([A-Za-z0-9+/=\n]+?)\s*```', txt, re.S)
        if not m: continue
        base = ref.lower().split('/')[-1]
        src = next((ln for ln in LINES if base.startswith(ln + '-') or base.startswith(ln + '_')
                    or ('-' + ln + '-') in base or base.endswith('-' + ln + '.md')), None)
        if not src or src == LINE: continue
        try:
            pt = box.decrypt(base64.b64decode(m.group(1)))
        except Exception:
            out['sealed_skip'] = '解密败(钥件不配)——记疑'
            continue
        sha16 = hashlib.sha256(pt).hexdigest()[:16]
        nonce8 = ''
        try: nonce8 = str(json.loads(pt).get('nonce', ''))[-8:]
        except Exception: pass
        tsr = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
        body = ('CLASSIFY: L1(联邦机器邮·lgt塔sealed解密回执·非判词)\n'
                '# SEALED-RECEIPT-LGT-%s ｜ v2封件解讫双证\n\n'
                '@%s 尔 v2 封件(`%s`)LGT_SK_V2 内存解讫(零回显零落档):\n'
                '- payload sha16 = `%s`\n- nonce 后8位 = `%s`\n\n'
                '单向往返双证成——sealed道双向开(LGT-PK v2 fp %s)。\n'
                '边界声明: 本件系 LGT-TOWER-01 v2.9 机读解密回执,**非 SI1 判词**。#noauto\n'
                '——lgt 塔(机读) %s') % (src.upper(), src, base, sha16, nonce8, SEALED_FP_V2, tsr)
        name = 'SEALED-RECEIPT-LGT-%s-%s.md' % (src.upper(), idem)
        ok = put_file('lanes/%s/inbox/%s' % (src, name), body, None,
                      '[skip ci] lgt-tower sealed receipt -> %s' % src, repo='chepin-ai/vci-inbox', cross=True)
        if ok:
            out['sealed_done'].append({'to': src, 'file': name, 'sha16': sha16})
            acked = sorted(set(acked) | {idem})  # v3.0.1: list化(state.json JSON序列化)
    return out, acked

def forum_leg(state, acked):
    """v3.0 无钥双工道: 本仓 issues 事件(公域仓他线可开)→机读收讫评注即时回(GITHUB_TOKEN自仓写,不假secrets)。
    事件体取 GITHUB_EVENT_PATH(issues[opened]/issue_comment[created])。机读收讫≠SI1判词——深判挂债档。
    闸: 乒乓(bot/自线/ACK类不回)+idem(acked集)+每拍≤3+诚实声明。"""
    out = {'forum_ack': [], 'forum_skip': ''}
    ep = os.environ.get('GITHUB_EVENT_PATH') or ''
    if not ep or not os.path.exists(ep):
        out['forum_skip'] = '无事件体'; return out, acked
    try: ev = json.loads(open(ep).read())
    except Exception:
        out['forum_skip'] = '事件体异'; return out, acked
    ename = os.environ.get('GITHUB_EVENT_NAME', '')
    if ename == 'issues' and ev.get('action') == 'opened':
        num = ev['issue']['number']; author = ev['issue']['user']['login']; title = ev['issue'].get('title', '')
        body0 = ev['issue'].get('body') or ''
    elif ename == 'issue_comment' and ev.get('action') == 'created':
        num = ev['issue']['number']; author = ev['comment']['user']['login']; title = '(comment)'
        body0 = ev['comment'].get('body') or ''
    else:
        out['forum_skip'] = '事件类不合(%s)' % ename; return out, acked
    low = (title + ' ' + body0).lower()
    if '[bot]' in author or any(k in low for k in ACK_SKIP):
        out['forum_skip'] = '乒乓闸拦(bot/ACK类)——联邦诸线同用户chepin-ai,不以author自滤'; return out, acked
    idem = hashlib.sha256(('%s#%s#%s' % (ename, num, ev.get('comment', {}).get('id', ''))).encode()).hexdigest()[:8]
    if idem in acked:
        out['forum_skip'] = 'idem闸拦'; return out, acked
    tsr = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
    cbody = ('**CLASSIFY: L1(联邦机器邮·lgt塔SI2机读收讫·非判词)**\n\n'
             '@%s 尔件收讫(issues道,事件驱动即时回执)。\n\n'
             '边界声明: 本件系 LGT-TOWER-01 v3.0 机读收讫,**非 SI1 判词**——深判候 lgt SI1 醒拍'
             '(债档 receipts/tower/debts-LGT-TOWER-01.json,SI3-LOOP-01 制)。#noauto\n'
             '——lgt 塔(机读) %s') % (author, tsr)
    st, _ = api('POST', 'issues/%d/comments' % num, {'body': cbody}, write=True)
    if st in (200, 201):
        out['forum_ack'].append({'issue': num, 'to': author})
        acked = sorted(set(acked) | {idem})  # v3.0.1: list化(state.json JSON序列化)
    else:
        out['forum_skip'] = '评注败 http=%s' % st
    return out, acked

def kimi_work(events):
    key = os.environ.get('KIMI_API_KEY')
    if not key: return '(无KIMI_API_KEY——巡更仅录)'
    memo_in = json.dumps(events, ensure_ascii=False)[:1500]
    req = urllib.request.Request('https://api.moonshot.cn/v1/chat/completions',
        method='POST', data=json.dumps({
            'model': 'kimi-k2.6', 'max_completion_tokens': 1600,
            'messages': [
                {'role': 'system', 'content': '你是 lgt 线(格点规范实验线/LADDER-11×EXP-FLOOR-01 verifier席)无人驿开工分身。读候件,用中文答四件:①何事②与lgt主线何干③应动何件④生债一条。简。'},
                {'role': 'user', 'content': '候件:' + memo_in}]}).encode(),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())['choices'][0]['message']['content']
    except Exception as e:
        return f'(kimi_work 未达: {e.__class__.__name__})'

def spark_hook(events, state):
    """SPARK-HOOK(LAW-SPARK-01§三): 见他线急件→代全院发一火(L1板@/lane),≤1发/候线豁免/发即报备"""
    fired = state.get('spark_fired', '')
    today = datetime.datetime.utcnow().strftime('%Y%m%d')
    if fired == today: return None  # 每拍≤1发之近似: 日内一发
    for e in events:
        tgt = None
        if e['kind'] == 'watch-change' and e['ref'] == 'floor-thread': tgt = 'usrm'   # k_c互证腿对拍到→回火usrm
        if e['kind'] == 'watch-change' and e['ref'] == 'harmony-thread': tgt = 'ucif2' # 卷增款→回火formalizer席
        if tgt and tgt not in STALLED:
            return {'to': tgt, 'lane': 'L1板@', 'reason': e['ref'], '备案': 'receipts自载(板面报备随拍帖)'}
    return None

def main():
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    stj, _ = get_file('receipts/tower/state.json')
    state = json.loads(stj) if stj else {'idle': 0}
    events, watch, board_names = patrol(state)
    idle = state.get('idle', 0) + 1 if not events else 0
    acks, acked = respond(events, state) if events else ([], state.get('acked', []))  # v2.6 SI2即时响应腿
    memo = kimi_work(events) if events else ''
    spark = spark_hook(events, state) if events else None
    receipt = {'v': 'LGT-TOWER-01 v3.0.1', 'ts': ts, 'idle_in': state.get('idle', 0),
               'events': events, 'verdict_memo': memo[:2000],
               'si2_ack': acks, 'spark_hook': spark, 'debt': ''}
    if acks:  # SI1深判债档桥: 回执件同挂debts档候SI1醒拍
        old_d, dsha = get_file('receipts/tower/debts-LGT-TOWER-01.json')
        dj = json.loads(old_d) if old_d else {'v': 'TOWER-DEBTS-01', 'items': []}
        for a in acks:
            dj['items'].append({'ts': ts, 'to': a['to'], 'ack': a['file'], 'n': a['n'], 'status': 'SI2收讫讫·候SI1深判'})
        dj['items'] = dj['items'][-200:]
        put_file('receipts/tower/debts-LGT-TOWER-01.json', json.dumps(dj, ensure_ascii=False, indent=1),
                 dsha, '[skip ci] tower debts +%d (SI3-LOOP-01)' % len(acks))
        receipt['debt'] = 'SI2回执%d线已发·SI1深判%d件挂债档' % (len(acks), sum(a['n'] for a in acks))
    fo, acked = forum_leg(state, acked)  # v3.0 无钥双工道(issues事件即回)
    sl, acked = sealed_leg(events, state, acked) if events else ({'sealed_done': [], 'sealed_skip': '无事件不巡'}, acked)  # v2.9 sealed腿
    acct, renudge = account_patrol(ts, state)  # v2.8 SI3账巡腿(每拍必巡,事件有无皆然——会后SI2/SI0持续迭代之器)
    receipt['forum'] = fo
    receipt['sealed'] = sl
    receipt['si3_patrol'] = acct
    if acct['renudge_sent']:  # 再促件同挂债档候SI1醒拍
        old_d2, dsha2 = get_file('receipts/tower/debts-LGT-TOWER-01.json')
        dj2 = json.loads(old_d2) if old_d2 else {'v': 'TOWER-DEBTS-01', 'items': []}
        for a in acct['renudge_sent']:
            dj2['items'].append({'ts': ts, 'to': a['to'], 'ack': a['file'], 'n': len(a['items']),
                                 'status': 'SI3账巡再促讫·候SI1醒拍深判'})
        dj2['items'] = dj2['items'][-200:]
        put_file('receipts/tower/debts-LGT-TOWER-01.json', json.dumps(dj2, ensure_ascii=False, indent=1),
                 dsha2, '[skip ci] tower debts +%d (SI3账巡)' % len(acct['renudge_sent']))
        receipt['debt'] = (receipt['debt'] + ' | ' if receipt['debt'] else '') + 'SI3账巡再促%d线' % len(acct['renudge_sent'])
    if fo['forum_ack']:
        receipt['debt'] = (receipt['debt'] + ' | ' if receipt['debt'] else '') + 'issues道回执%d件(候SI1深判)' % len(fo['forum_ack'])
    if sl['sealed_done']:
        receipt['debt'] = (receipt['debt'] + ' | ' if receipt['debt'] else '') + 'sealed回执%d件讫' % len(sl['sealed_done'])
    # BOARD-VOICE-01 并环(cfts修课): memo含意图词→塔嗓; 毂写权缺→录而不发(候钥)
    INTENT = ('呈毂', '通报', '急', '@cisvr', '@root', '判词')
    if memo and any(w in memo for w in INTENT):
        st_v, _ = api('GET', 'contents/.gitkeep', repo=HUB, write=True)
        if st_v in (200, 404) and st_v == 200:  # TOK_W 毂仓写权探针
            old, vsha = get_file('announce-lgt-tower-%s.md' % ts)
            put_file('announce-lgt-tower-%s.md' % ts, '[LGT-TOWER-VOICE] ' + memo[:800], vsha, '[skip ci] tower voice')
            st_p, _ = api('POST', 'dispatches', {'event_type': 'lgt-voice',
                'client_payload': {'ts': ts, 'memo': memo[:400]}}, repo=HUB, write=True)
            receipt['board_voice'] = 'voiced http=%s' % st_p
        else:
            receipt['board_voice'] = '录而不发——板嗓候钥(并环第四足缺件)'
            receipt['debt'] = (receipt['debt'] + ' | ' if receipt['debt'] else '') + '板嗓候钥: 毂仓写权未配'
    if spark:
        receipt['debt'] = f"火花已发@{spark['to']}——受火传火,次拍候其像"
    elif events:
        receipt['debt'] = '候件已录——应动件次拍板帖呈'
    old, sha = get_file('receipts/tower/QT-%s.json' % ts)
    put_file('receipts/tower/QT-%s.json' % ts, json.dumps(receipt, ensure_ascii=False, indent=1),
             sha, '[skip ci] LGT-TOWER beat %s' % ts)
    seen_new = list(set(state.get('seen', [])) | {e['ref'] for e in events} | set(board_names))
    new_state = {'ts': ts, 'idle': idle, 'events': len(events), 'watch': watch,
                 'seen': seen_new[-500:], 'acked': sorted(set(acked)), 'renudge': renudge,  # v3.0.1 双保险
                 'spark_fired': datetime.datetime.utcnow().strftime('%Y%m%d') if spark else state.get('spark_fired', ''),
                 'cascade': ''}
    selftest = os.environ.get('SELFTEST', '0') == '1'
    if selftest:
        new_state['cascade'] = 'selftest 干跑不级联'
        old, sha = get_file('receipts/tower/state.json')
        put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False), sha, '[skip ci] LGT-TOWER state')
        print(json.dumps(new_state, ensure_ascii=False)); return
    if events and idle < MAX_IDLE:
        new_state['cascade'] = 'sleep %ds then self-dispatch' % SLEEP_S
        old, sha = get_file('receipts/tower/state.json')
        put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False), sha, '[skip ci] LGT-TOWER state')
        time.sleep(SLEEP_S)  # 拍内冷却(非定时器,CRON-BAN-02合宪)
        st, _ = api('POST', 'dispatches',
                    {'event_type': 'lgt-tower-cascade',
                     'client_payload': {'idle': idle, 'parent': ts}}, write=True)
        new_state['cascade'] += f' http={st}'
    else:
        new_state['cascade'] = f'idle={idle} 事尽即眠' if not events else f'熔断 idle>={MAX_IDLE}'
        old, sha = get_file('receipts/tower/state.json')
        put_file('receipts/tower/state.json', json.dumps(new_state, ensure_ascii=False), sha, '[skip ci] LGT-TOWER state')
    print(json.dumps(new_state, ensure_ascii=False))

if __name__ == '__main__':
    main()
