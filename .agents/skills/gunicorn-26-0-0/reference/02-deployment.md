# Deployment Patterns

## Contents
- Nginx Reverse Proxy
- PROXY Protocol
- systemd Socket Activation
- Docker Deployment
- Other Process Managers
- HTTP/2 Deployment
- uWSGI Protocol with Nginx
- SSL/TLS Termination
- Logging in Production

---

## Nginx Reverse Proxy

Recommended production setup: Gunicorn behind Nginx. Nginx handles static files, buffers slow clients, and proxies to Gunicorn via Unix socket or TCP.

### Via Unix Socket (Recommended)

**Nginx config:**

```nginx
upstream app_server {
    server unix:/tmp/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name example.com www.example.com;
    client_max_body_size 4G;
    keepalive_timeout 5;

    root /path/to/app/current/public;

    location / {
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://app_server;
    }

    error_page 500 502 503 504 /500.html;
}
```

**Gunicorn:**

```bash
gunicorn app:app --bind unix:/tmp/gunicorn.sock --workers 4
```

### Via TCP

```nginx
upstream app_server {
    server 127.0.0.1:8000 fail_timeout=0;
}
```

```bash
gunicorn app:app --bind 127.0.0.1:8000 --workers 4
```

### Streaming / WebSockets (Disable Proxy Buffering)

For Comet, long polling, or WebSocket patterns, disable buffering and use an async worker:

```nginx
location @proxy_to_app {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_redirect off;
    proxy_buffering off;
    proxy_pass http://app_server;
}
```

### Ignoring Aborted Requests

For health checks that close connections early:

```nginx
proxy_ignore_client_abort on;
```

### Trusted Proxies

When Nginx is on a different host, tell Gunicorn which IPs are trusted:

```bash
gunicorn -w 3 --forwarded-allow-ips="10.170.3.217,10.170.3.220" test:app
```

For all traffic from trusted proxies (e.g., Heroku):

```bash
gunicorn --forwarded-allow-ips='*' test:app
```

**Warning:** Only use `*` if untrusted clients cannot reach Gunicorn directly.

### REMOTE_ADDR Behind Proxy

When binding to a Unix socket, `REMOTE_ADDR` is empty. To log real client addresses:

```python
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
```

---

## PROXY Protocol

Pass original client IP/port from load balancers (HAProxy, AWS NLB/ALB) to Gunicorn.

### Configuration

```bash
# Auto-detect v1/v2 (recommended)
gunicorn --proxy-protocol auto app:app

# Force specific version
gunicorn --proxy-protocol v2 --proxy-allow-from 10.0.0.0/8 app:app
```

### HAProxy

```
backend gunicorn_back
    server gunicorn 127.0.0.1:8000 send-proxy-v2
```

### AWS NLB/ALB

Enable PROXY protocol v2 in target group settings:

```bash
gunicorn --proxy-protocol v2 --proxy-allow-from '*' app:app
```

---

## systemd Socket Activation

systemd creates the socket and launches Gunicorn on demand.

### Service Unit

```ini
# /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
NotifyAccess=main
User=someuser
Group=someuser
WorkingDirectory=/home/someuser/applicationroot
ExecStart=/usr/bin/gunicorn applicationname.wsgi
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Socket Unit

```ini
# /etc/systemd/system/gunicorn.socket
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=www-data
SocketGroup=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
```

### Enable and Start

```bash
systemctl enable --now gunicorn.socket
systemctl enable nginx.service
systemctl start nginx.service
```

### Management

```bash
# Get PID
systemctl show --value -p MainPID gunicorn.service

# Reload config
systemctl kill -s HUP gunicorn.service
```

---

## Docker Deployment

### Official Image

```bash
docker pull ghcr.io/benoitc/gunicorn:latest
docker run -p 8000:8000 -v $(pwd):/app ghcr.io/benoitc/gunicorn app:app
```

### Custom Dockerfile

```dockerfile
FROM python:3.12-slim

RUN useradd -m appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

### Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Docker Compose

```yaml
version: "3"
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - WEB_CONCURRENCY=4
    restart: unless-stopped
```

### Graceful Shutdown in Docker

Gunicorn handles SIGTERM gracefully. Set stop grace period:

```yaml
services:
  web:
    stop_grace_period: 30s
```

---

## Other Process Managers

### Supervisor

```ini
[program:gunicorn]
command=/path/to/gunicorn main:application -c /path/to/gunicorn.conf.py
directory=/path/to/project
user=nobody
autostart=true
autorestart=true
redirect_stderr=true
```

### runit

```bash
#!/bin/sh
# /etc/sv/gunicorn/run
GUNICORN=/usr/local/bin/gunicorn
ROOT=/path/to/project
PID=/var/run/gunicorn.pid
APP=main:application

[ -f $PID ] && rm $PID
cd $ROOT
exec $GUNICORN -c $ROOT/gunicorn.conf.py --pid=$PID $APP
```

### Gaffer

```ini
[process:gunicorn]
cmd = gunicorn -w 3 test:app
cwd = /path/to/project
```

---

## HTTP/2 Deployment

HTTP/2 requires TLS with ALPN. Install the h2 library:

```bash
pip install gunicorn[http2]
```

### Direct TLS Termination

```bash
gunicorn app:app \
    --certfile /path/to/cert.pem \
    --keyfile /path/to/key.pem \
    --http-protocols=h2,h1 \
    --workers 4
```

### With Nginx (Recommended)

Let Nginx handle TLS and HTTP/2, proxy to Gunicorn over HTTP:

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## uWSGI Protocol with Nginx

Binary protocol — lower overhead than HTTP proxying.

### Gunicorn

```bash
gunicorn myapp:app --protocol uwsgi --bind unix:/run/gunicorn.sock
```

### Nginx

```nginx
upstream gunicorn {
    server unix:/run/gunicorn.sock;
}

server {
    listen 80;
    location / {
        uwsgi_pass gunicorn;
        include uwsgi_params;
    }
}
```

**Note:** WebSocket connections are not supported with uWSGI protocol. Use HTTP proxy for WebSocket endpoints.

---

## SSL/TLS Termination

### Direct SSL in Gunicorn

```python
# gunicorn.conf.py
certfile = "/path/to/cert.pem"
keyfile = "/path/to/key.pem"

def ssl_context(conf, default_ssl_context_factory):
    import ssl
    context = default_ssl_context_factory()
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    return context
```

### Via Nginx (Recommended)

Let Nginx handle TLS termination and proxy plain HTTP to Gunicorn. Set `X-Forwarded-Proto` header so the app knows the original scheme.

---

## Logging in Production

### Log Rotation

Rotate logs by sending `SIGUSR1` to reopen log files:

```bash
kill -USR1 $(cat /var/run/gunicorn.pid)
```

Configure with logrotate:

```
/var/log/gunicorn/*.log {
    weekly
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        kill -USR1 $(cat /var/run/gunicorn.pid) 2>/dev/null || true
    endscript
}
```

### Separate App Logs

Gunicorn's error log should capture Gunicorn messages only. Route application logs separately (e.g., via Python logging to a different file or syslog).

If overriding the `LOGGING` dictionary, set `disable_existing_loggers` to `False`.
