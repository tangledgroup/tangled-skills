---
name: nginx-1-30-0
description: Complete toolkit for Nginx 1.30.0 high-performance HTTP server, reverse proxy, and load balancer covering configuration syntax, core modules, HTTP/stream/TCP/UDP proxying, SSL/TLS, caching, compression, rate limiting, WebSocket support, virtual servers, location matching, access control, FastCGI/uWSGI/gRPC proxying, dynamic modules, signal-based process control, logging, and embedded variables. Use when configuring Nginx as web server or reverse proxy, setting up load balancing, implementing HTTPS with TLS, tuning performance, creating virtual hosts, routing to backend application servers, or troubleshooting Nginx configurations.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.30.0"
tags:
  - HTTP server
  - reverse proxy
  - load balancer
  - SSL/TLS
  - caching
  - compression
  - WebSocket
  - FastCGI
  - stream proxy
category: web-servers
external_references:
  - https://nginx.org/en/docs/
  - https://github.com/nginx/nginx/tree/stable-1.30
---

# Nginx 1.30.0

## Overview

Nginx (pronounced "engine-x") is a high-performance HTTP server, reverse proxy, and load balancer known for its event-driven architecture, low memory footprint, and ability to handle thousands of simultaneous connections. It consists of a master process that manages worker processes, which do the actual request processing using OS-dependent mechanisms like epoll (Linux), kqueue (FreeBSD/macOS), /dev/poll (Solaris), or eventport (Solaris 10+).

Nginx operates in three primary modes:
- **HTTP server**: Serving static/dynamic content, SSL termination, compression
- **Reverse proxy**: Forwarding requests to backend application servers with load balancing
- **Stream proxy**: Generic TCP/UDP proxying for non-HTTP protocols (mail, databases, game servers)

## When to Use

Use this skill when:
- Configuring Nginx as a web server or reverse proxy
- Setting up HTTPS/TLS termination with SSL certificates
- Implementing load balancing across backend servers
- Creating virtual hosts with name-based or IP-based routing
- Configuring caching, compression (gzip), or rate limiting
- Proxying to FastCGI, uWSGI, SCGI, gRPC, or memcached backends
- Setting up WebSocket proxying or streaming protocols
- Tuning Nginx for high-concurrency environments
- Troubleshooting Nginx configuration or performance issues

## Core Concepts

### Architecture

Nginx uses a master-worker architecture:
- **Master process**: Reads configuration, manages worker processes, handles signals
- **Worker processes**: Handle actual request processing using event-driven models
- **Connection methods**: `epoll` (Linux 2.6+), `kqueue` (FreeBSD/macOS), `/dev/poll` (Solaris), `select`/`poll` (fallback)

### Configuration Structure

Directives are divided into **simple directives** (name + parameters + semicolon) and **block directives** (nested contexts with braces).

```
main context          # Top-level directives
  events { ... }      # Connection processing settings
  http { ... }        # HTTP server configuration
    server { ... }    # Virtual server block
      location / { ... }  # Request routing rules
```

Key contexts (nested order): `main` → `events` | `http` | `mail` | `stream` → `server` → `location`

### Server Name Matching

Nginx selects virtual servers in this priority:
1. Exact name match
2. Longest wildcard starting with `*` (e.g., `*.example.com`)
3. Longest wildcard ending with `*` (e.g., `mail.*`)
4. First matching regular expression (`~^regex$`)

### Location Matching

Nginx location matching order:
1. Exact match (`= /uri`) — terminates search immediately
2. Prefix locations (`/uri/`) — longest prefix wins
3. Preferential prefix (`^~ /uri/`) — stops regex checking
4. Regular expressions (`~` case-sensitive, `~*` case-insensitive) — first match wins
5. Falls back to longest prefix location from step 2

```nginx
location = / { /* A: exact */ }
location / {     /* B: prefix */ }
location /documents/ { /* C: longer prefix */ }
location ^~ /images/ { /* D: preferential prefix */ }
location ~* \.(gif|jpg|png)$ { /* E: regex */ }
```

Request `/` → A, `/index.html` → B, `/documents/doc.html` → C, `/images/1.gif` → D, `/documents/1.jpg` → E

### Embedded Variables

Nginx provides built-in variables for dynamic configuration:

| Variable | Description |
|----------|-------------|
| `$remote_addr` | Client IP address |
| `$remote_port` | Client port |
| `$request_method` | HTTP method (GET, POST, etc.) |
| `$request_uri` | Full original request URI with arguments |
| `$uri` | Normalized current URI |
| `$document_root` | Root directory for the current request |
| `$host` | Host name from request line or Host header |
| `$http_*` | Any request header field (e.g., `$http_user_agent`) |
| `$status` | Response status code |
| `$request_time` | Request processing time in seconds |
| `$upstream_addr` | Address of proxied upstream server |
| `$upstream_response_time` | Time spent receiving response from upstream |

See `references/01-configuration-syntax.md` for full directive reference.
See `references/02-http-modules.md` for HTTP module details.
See `references/03-stream-proxy.md` for stream/TCP/UDP proxying.
See `references/04-performance-tuning.md` for optimization techniques.

## Installation / Setup

### Installing from Packages (Linux)

```bash
# Add nginx.org repository and install
sudo apt update && sudo apt install nginx    # Debian/Ubuntu
sudo yum install nginx                       # RHEL/CentOS 7
sudo dnf install nginx                       # RHEL/CentOS 8+
```

### Building from Source

```bash
# Download and build with common modules
./configure \
    --prefix=/usr/local/nginx \
    --conf-path=/usr/local/nginx/conf/nginx.conf \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_gzip_static_module \
    --with-stream \
    --with-stream_ssl_module \
    --with-pcre

make && sudo make install
```

### Directory Layout (default)

```
/usr/local/nginx/
├── conf/nginx.conf       # Main configuration file
├── conf/mime.types       # MIME type mappings
├── sbin/nginx            # Executable
├── logs/access.log       # Access log
├── logs/error.log        # Error log
└── html/                 # Default static content
```

## Usage Examples

### Basic Static File Server

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /images/ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Reverse Proxy with Load Balancing

```nginx
upstream backend_servers {
    least_conn;
    server backend1.example.com weight=5;
    server backend2.example.com:8080 max_fails=3 fail_timeout=30s;
    server backend3.example.com backup;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

### HTTPS Server with HSTS

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-Content-Type-Options nosniff always;

    location / {
        root /var/www/html;
        try_files $uri $uri/ =404;
    }
}
```

### WebSocket Proxy

```nginx
upstream websocket_backend {
    server ws1.example.com:8080;
    server ws2.example.com:8080;
}

server {
    location /ws/ {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

### Gzip Compression

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_min_length 1000;
gzip_types
    text/plain
    text/css
    application/json
    application/javascript
    text/xml
    application/xml
    application/xml+rss
    image/svg+xml;
```

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://backend_servers;
    }
}
```

### FastCGI (PHP-FPM)

```nginx
location ~ \.php$ {
    include fastcgi_params;
    fastcgi_pass 127.0.0.1:9000;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    fastcgi_param QUERY_STRING $query_string;
    fastcgi_cache_bypass $http_cache_control;
}
```

### TCP/UDP Stream Proxy (Mail, DNS, etc.)

```nginx
stream {
    upstream mail_servers {
        hash $remote_addr consistent;
        server mail1.example.com:25;
        server mail2.example.com:25 backup;
    }

    server {
        listen 25;
        proxy_pass mail_servers;
        proxy_timeout 3s;
        proxy_connect_timeout 3s;
    }

    # DNS UDP proxy
    server {
        listen 53 udp reuseport;
        proxy_pass dns_upstream;
        proxy_timeout 20s;
    }
}
```

### HTTP/3 (QUIC) Support

```nginx
server {
    listen 443 quic reuseport;
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    # QUIC-specific settings
    quic_retry on;
    add_header Alt-Svc 'h3=":443"; ma=86400';

    location / {
        root /var/www/html;
    }
}
```

## Control & Process Management

### Signal-Based Control

```bash
# Start nginx
nginx

# Stop gracefully (quit)
nginx -s quit

# Fast shutdown
nginx -s stop

# Reload configuration (zero-downtime)
nginx -s reload

# Reopen log files
nginx -s reopen

# Test configuration before applying
nginx -t -c /path/to/nginx.conf
```

### Unix Signals

| Signal | Master Process Effect |
|--------|----------------------|
| `TERM`, `INT` | Fast shutdown |
| `QUIT` | Graceful shutdown (wait for workers) |
| `HUP` | Reload configuration, start new workers |
| `USR1` | Re-open log files (for log rotation) |
| `USR2` | Upgrade executable on the fly |
| `WINCH` | Gracefully shut down worker processes |

### Hot Binary Upgrade

```bash
# 1. Replace binary file in place
cp /usr/local/nginx/sbin/nginx.new /usr/local/nginx/sbin/nginx

# 2. Send USR2 to old master process
kill -USR2 $(cat /var/run/nginx.pid)

# 3. New master starts with new workers
# Both old and new masters run simultaneously

# 4. Gracefully shut down old workers
kill -WINCH $(cat /var/run/nginx.pid.oldbin)

# 5. If upgrade successful, shut down old master
kill -QUIT $(cat /var/run/nginx.pid.oldbin)

# Rollback if needed:
# kill -HUP $(cat /var/run/nginx.pid.oldbin)  # Old starts new workers
# kill -TERM $(cat /var/run/nginx.pid)        # New exits immediately
```

## Key Directives Reference

### Main Context

| Directive | Default | Description |
|-----------|---------|-------------|
| `worker_processes` | `1` | Number of worker processes (use `auto`) |
| `user` | `nobody nobody` | Worker process user/group |
| `error_log` | `logs/error.log error` | Error log path and level |
| `pid` | `logs/nginx.pid` | PID file location |
| `daemon` | `on` | Run as daemon |
| `master_process` | `on` | Start worker processes |
| `timer_resolution` | — | Reduce timer resolution for performance |
| `pcre_jit` | `off` | Enable PCRE JIT compilation |
| `thread_pool` | `default threads=32` | Define thread pools for async I/O |

### Events Context

| Directive | Default | Description |
|-----------|---------|-------------|
| `worker_connections` | `512` | Max connections per worker |
| `use` | auto-detected | Connection method (epoll, kqueue, etc.) |
| `multi_accept` | `off` | Accept all connections at once |
| `accept_mutex` | `off` | Lock for accepting new connections |

### HTTP Context

| Directive | Default | Description |
|-----------|---------|-------------|
| `listen` | `80` | Port/address to listen on |
| `server_name` | `""` | Virtual server hostnames |
| `root` | `html` | Document root directory |
| `index` | `index.html` | Default index files |
| `access_log` | `logs/access.log combined` | Access log path and format |

## References

- Official documentation: https://nginx.org/en/docs/
- GitHub repository: https://github.com/nginx/nginx/tree/stable-1.30
- Admin's Guide: https://docs.nginx.com/nginx/admin-guide/
- Beginner's Guide: https://nginx.org/en/docs/beginners_guide.html
- Control documentation: https://nginx.org/en/docs/control.html

## Reference Files

- [`references/01-configuration-syntax.md`](references/01-configuration-syntax.md) — Full configuration syntax, all main context and events directives, connection processing methods, measurement units
- [`references/02-http-modules.md`](references/02-http-modules.md) — HTTP module reference: core module, proxy, SSL, upstream, gzip, rewrite, FastCGI/uWSGI/gRPC, caching, access control, headers, logging, variables
- [`references/03-stream-proxy.md`](references/03-stream-proxy.md) — Stream/TCP/UDP proxying: stream core module, mail proxy (POP3/IMAP/SMTP), MQTT filter, load balancing in stream context
- [`references/04-performance-tuning.md`](references/04-performance-tuning.md) — Performance optimization: worker tuning, connection handling, caching strategies, compression, sendfile, TCP settings, thread pools, HTTP/2 and HTTP/3 tuning
