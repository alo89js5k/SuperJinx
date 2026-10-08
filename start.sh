#!/bin/bash
set -e
echo "=== Super JinX | Marzban on Railway ==="
mkdir -p /var/lib/marzban
[ -f /var/lib/marzban/xray_config.json ] || cp /opt/xray_config.json /var/lib/marzban/xray_config.json
python /opt/lock.py

PUBLIC_DOMAIN="${PANEL_DOMAIN:-$RAILWAY_PUBLIC_DOMAIN}"
if [ -z "$XRAY_SUBSCRIPTION_URL_PREFIX" ] && [ -n "$PUBLIC_DOMAIN" ]; then
  export XRAY_SUBSCRIPTION_URL_PREFIX="https://$PUBLIC_DOMAIN"
fi
echo "[start] domain: ${PUBLIC_DOMAIN:-NOT SET} | sub prefix: ${XRAY_SUBSCRIPTION_URL_PREFIX:-NOT SET}"

nginx -t
nginx

# Cloudflare Tunnel (optional): set CF_TUNNEL_TOKEN + CF_TUNNEL_HOSTNAME
if [ -n "$CF_TUNNEL_TOKEN" ]; then
  echo "[tunnel] starting Cloudflare tunnel -> ${CF_TUNNEL_HOSTNAME:-?}"
  ( while true; do
      cloudflared tunnel --no-autoupdate --protocol http2 run --token "$CF_TUNNEL_TOKEN" 2>&1 | sed 's/^/[tunnel] /'
      echo "[tunnel] restarting in 5s"; sleep 5
    done ) &
else
  echo "[tunnel] CF_TUNNEL_TOKEN not set, direct Railway mode"
fi
cd /code
alembic upgrade head
python /code/marzban-cli.py admin import-from-env -y >/dev/null 2>&1 || true
python /opt/enforce_hosts.py &
exec python main.py
