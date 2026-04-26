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
  - https://docs.nginx.com/nginx/admin-guide/
  - https://nginx.org/en/docs/beginners_guide.html
  - https://nginx.org/en/docs/control.html
  - https://github.com/nginx/nginx/tree/stable-1.30
---

# Nginx 1.30.0

## Overview

Nginx is a high-performance HTTP server, reverse proxy, and load balancer. It uses an event-driven, asynchronous architecture with one master process and multiple worker processes. The master process reads configuration and manages workers; worker processes handle actual request processing using OS-dependent mechanisms (epoll on Linux, kqueue on BSD).

Nginx 1.30.0 supports HTTP/1.1, HTTP/2, HTTP/3 (QUIC), WebSocket proxying, TCP/UDP stream proxying, FastCGI/uWSGI/SCGI/gRPC upstreams, built-in caching, gzip compression, rate limiting, SSL/TLS termination, and virtual hosting with name-based and IP-based routing.

## When to Use

- Configuring Nginx as a web server or reverse proxy
- Setting up load balancing across multiple backend servers
- Implementing HTTPS with TLS/SSL termination
- Tuning performance for high-throughput deployments
- Creating virtual hosts (name-based or IP-based)
- Routing requests to backend application servers (HTTP, FastCGI, gRPC)
- Configuring rate limiting, access control, or caching
- Troubleshooting Nginx configurations
- Setting up QUIC/HTTP/3 support
- Proxying TCP/UDP traffic with the stream module

## Core Concepts

**Process model:** One master process + multiple worker processes. Workers are event-driven and non-blocking. Number of workers set via `worker_processes` (or `auto` to match CPU cores).

**Configuration structure:** Directives are either simple (end with `;`) or block (enclosed in `{}`). Key contexts: `main` → `events`, `http` → `server` → `location`. Comments use `#`.

**Request processing:** Nginx first selects a `server` block by matching the request's IP/port and `Host` header, then tests the URI against `location` directives. Prefix locations are checked longest-first; regex locations (prefixed with `~`) take priority over prefix matches.

**Upstream groups:** The `upstream` block defines server pools referenced by `proxy_pass`, `fastcgi_pass`, etc. Supports round-robin (default), `least_conn`, `ip_hash`, and weighted distribution.

## Installation / Setup

Install from packages (Linux, FreeBSD) or build from source:

```bash
# Build from source
./configure --with-http_ssl_module --with-http_v2_module --with-stream
make
sudo make install
```

Default configuration file locations: `/usr/local/nginx/conf/nginx.conf`, `/etc/nginx/nginx.conf`, or `/usr/local/etc/nginx/nginx.conf`.

## Usage Examples

### Basic reverse proxy

```nginx
http {
    upstream backend {
        server 127.0.0.1:8080;
        server 127.0.0.1:8081;
    }

    server {
        listen 80;
        server_name example.com;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### HTTPS with SSL termination

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate     /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/cert.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://backend;
    }
}
```

### Static file serving with caching headers

```nginx
server {
    listen 80;
    server_name static.example.com;

    location / {
        root /var/www/html;
        index index.html;
    }

    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        root /var/www/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## Advanced Topics

**Configuration Syntax and Core Module**: Directives, contexts, measurement units, worker tuning → [Configuration Syntax](reference/01-config-syntax.md)

**HTTP Proxy and Upstream**: proxy_pass, caching, buffering, timeouts, upstream load balancing methods → [HTTP Proxy and Upstream](reference/02-http-proxy-upstream.md)

**SSL/TLS and HTTP/3**: Certificate configuration, protocols, ciphers, OCSP stapling, QUIC/HTTP/3 setup → [SSL/TLS and HTTP/3](reference/03-ssl-tls.md)

**Access Control and Rate Limiting**: IP-based allow/deny, basic auth, JWT auth, limit_req, limit_conn → [Access Control and Rate Limiting](reference/04-access-control.md)

**Rewrite, Map, and Logging**: URI rewriting, return codes, map variables, log_format, access_log → [Rewrite, Map, and Logging](reference/05-rewrite-map-logging.md)

**Stream Module (TCP/UDP)**: TCP/UDP proxying, stream upstreams, DNS proxying → [Stream Module](reference/06-stream-module.md)

**Process Control and Signals**: Starting, stopping, reloading, log rotation, in-place upgrades → [Process Control](reference/07-process-control.md)
