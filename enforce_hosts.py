# Super JinX host guard
# 1) Locked inbound: remark/address/TLS are forced and reverted within 20s if anyone edits them
# 2) Other inbounds: fixed ONCE (only while still on Marzban defaults) so the sub link works out of the box
import json, os, time, urllib.request, urllib.parse

API = "http://127.0.0.1:8000"
LOCKED_TAG = json.load(open("/opt/locked_inbound.json"))["tag"]
LOCKED_REMARK = "جینکس | 𝙎𝙪𝙥𝙚𝙧 𝗝𝗶𝗻𝗫"
DOMAIN = os.environ.get("PANEL_DOMAIN") or os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
CF_HOST = os.environ.get("CF_TUNNEL_HOSTNAME", "") if os.environ.get("CF_TUNNEL_TOKEN") else ""
CF_IP = os.environ.get("CF_CLEAN_IP", "")
EXTRA_REMARKS = {"VLESS WS": "𝗝𝗶𝗻𝗫 | VLESS", "VMESS WS": "𝗝𝗶𝗻𝗫 | VMess", "TROJAN WS": "𝗝𝗶𝗻𝗫 | Trojan"}

def base(remark):
    return {"remark": remark, "address": DOMAIN, "port": 443, "sni": DOMAIN, "host": DOMAIN,
            "security": "tls", "alpn": "http/1.1", "fingerprint": "chrome",
            "allowinsecure": False, "is_disabled": False}

def req(method, path, data=None, token=None, form=False):
    h = {}
    if token:
        h["Authorization"] = "Bearer " + token
    if data is not None:
        if form:
            data = urllib.parse.urlencode(data).encode()
            h["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(data).encode()
            h["Content-Type"] = "application/json"
    r = urllib.request.Request(API + path, data=data, headers=h, method=method)
    return json.loads(urllib.request.urlopen(r, timeout=10).read() or b"null")

def tunnel(remark):
    h = base(remark)
    h.update({"address": CF_IP or CF_HOST, "sni": CF_HOST, "host": CF_HOST})
    return h

def locked_wanted():
    if CF_HOST:
        return [tunnel(LOCKED_REMARK), base(LOCKED_REMARK + " ⚡ Direct")]
    return [base(LOCKED_REMARK)]

def is_default(h):
    return (not h) or "{SERVER_IP}" in str(h.get("address", ""))

if not DOMAIN:
    print("[guard] WARNING: no domain yet. Generate a Railway domain (port 8080) and redeploy.", flush=True)

while True:
    try:
        tok = req("POST", "/api/admin/token",
                  {"username": os.environ["SUDO_USERNAME"], "password": os.environ["SUDO_PASSWORD"]},
                  form=True)["access_token"]
        hosts = req("GET", "/api/hosts", token=tok)
        changed = False
        if DOMAIN:
            # locked inbound
            wants = locked_wanted()
            cur = hosts.get(LOCKED_TAG) or []
            ok = len(cur) == len(wants) and all(
                all(c.get(k) == v for k, v in w.items()) for c, w in zip(cur, wants))
            if not ok:
                tmpl = cur[0] if cur else {}
                new = []
                for w in wants:
                    h = dict(tmpl); h.update(w); h.setdefault("path", None); new.append(h)
                hosts[LOCKED_TAG] = new; changed = True
                print("[guard] locked inbound host restored", flush=True)
            # other inbounds: one-time auto setup
            for tag, lst in hosts.items():
                if tag == LOCKED_TAG:
                    continue
                if lst and all(is_default(h) for h in lst):
                    new = dict(lst[0]); new.update(base(EXTRA_REMARKS.get(tag, "𝗝𝗶𝗻𝗫 | " + tag)))
                    new.setdefault("path", None)
                    hosts[tag] = [new]; changed = True
                    print(f"[guard] auto-configured host for {tag}", flush=True)
        if changed:
            req("PUT", "/api/hosts", hosts, token=tok)
    except Exception as e:
        print("[guard] waiting for panel:", e, flush=True)
    time.sleep(20)
