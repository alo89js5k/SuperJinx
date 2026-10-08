FROM gozargah/marzban:latest

RUN apt-get update \
 && apt-get install -y --no-install-recommends nginx curl ca-certificates \
 && curl -fsSL -o /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
 && chmod +x /usr/local/bin/cloudflared && cloudflared --version \
 && rm -rf /var/lib/apt/lists/* /etc/nginx/sites-enabled/default

COPY ws.inc /etc/nginx/ws.inc
COPY nginx.conf /etc/nginx/conf.d/marzban.conf
COPY xray_config.json locked_inbound.json lock.py enforce_hosts.py /opt/
COPY start.sh /start.sh

# fix Windows line endings, just in case
RUN sed -i 's/\r$//' /start.sh /opt/*.py /etc/nginx/ws.inc /etc/nginx/conf.d/marzban.conf \
 && chmod +x /start.sh

ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["/start.sh"]
CMD []
