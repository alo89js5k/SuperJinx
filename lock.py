import json
p = "/var/lib/marzban/xray_config.json"
locked = json.load(open("/opt/locked_inbound.json"))
cfg = json.load(open(p))
ib = [i for i in cfg.get("inbounds", []) if i.get("tag") != locked["tag"] and i.get("port") != locked["port"]]
cfg["inbounds"] = [locked] + ib
json.dump(cfg, open(p, "w"), indent=2, ensure_ascii=False)
print("[lock] locked inbound enforced")
