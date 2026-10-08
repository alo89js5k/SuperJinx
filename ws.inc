proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $conn_up;
proxy_set_header Host $host;
proxy_read_timeout 1d;
proxy_send_timeout 1d;
proxy_buffering off;
