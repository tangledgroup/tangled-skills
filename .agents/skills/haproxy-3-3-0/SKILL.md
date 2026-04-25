---
name: haproxy-3-3-0
description: Complete HAProxy 3.3.0 toolkit for load balancing, reverse proxying, SSL/TLS termination, and traffic management. Use when configuring HTTP/TCP load balancers, implementing high availability, managing SSL certificates, setting up health checks, configuring ACLs and content switching, or deploying HAProxy as a production-grade reverse proxy and load balancer.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.3.0"
tags:
  - load balancing
  - reverse proxy
  - SSL termination
  - high availability
  - HTTP proxy
  - TCP proxy
  - health checks
  - ACLs
category: infrastructure
external_references:
  - https://github.com/haproxy/haproxy/tree/v3.3.0/doc
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/configuration.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/intro.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/lua.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/management.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/peers.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/proxy-protocol.txt
---

# HAProxy 3.3.0

## Overview

HAProxy (HTTP Proxy) is a high-performance TCP/HTTP reverse proxy and load balancer written in C. It is widely used in production environments to distribute traffic across multiple servers, providing high availability, SSL/TLS termination, and advanced traffic management. HAProxy operates at both Layer 4 (TCP) and Layer 7 (HTTP), making it suitable for a wide range of use cases from simple reverse proxying to complex content switching and API gateway patterns.

HAProxy supports HTTP/1.x, HTTP/2, and HTTP/3 (QUIC) protocols, with features including SSL/TLS termination, compression, caching, rate limiting, and extensive monitoring capabilities. It uses an event-driven architecture that allows it to handle tens of thousands of concurrent connections with minimal resource consumption.

## When to Use

Use this skill when:
- Configuring HTTP or TCP load balancers for web applications
- Implementing SSL/TLS termination at the proxy layer
- Setting up high availability with health checks and failover
- Performing content switching based on ACLs, headers, or URI patterns
- Configuring rate limiting, connection limits, or traffic shaping
- Deploying HAProxy in production as a reverse proxy or API gateway
- Managing SSL certificates with ACME/Let's Encrypt integration
- Setting up statistics dashboards and monitoring via Unix socket CLI
- Configuring stickiness/sessions via cookies, headers, or hashing algorithms
- Implementing HTTP request/response rewriting and redirections

## Core Concepts

### Architecture

HAProxy configuration is organized into named sections:

| Section | Purpose |
|---------|---------|
| `global` | Process-wide settings (daemon mode, ulimit, SSL paths, CPU affinity) |
| `defaults` | Default values inherited by subsequent sections |
| `frontend` | Client-facing side (defines listen address, ACLs, HTTP rules) |
| `backend` | Server-facing side (defines servers, load balancing algorithm) |
| `listen` | Combined frontend + backend (layer 4 or HTTP) |
| `resolvers` | DNS resolver configuration for server name resolution |
| `peers` | Peer session configuration for stick-table replication |
| `userlist` | User credential stores for HTTP authentication |
| `caches` | Cache section declarations |
| `fcgi-app` | FastCGI application definitions |

### Proxy Modes

HAProxy operates in three modes:

- **TCP mode** (`mode tcp`) — Layer 4 proxy, forwards raw TCP connections without inspecting content. Used for database proxies, SSH, SMTP, etc.
- **HTTP mode** (`mode http`) — Layer 7 proxy, fully parses and can modify HTTP requests/responses. Enables ACLs, header manipulation, redirections.
- **health mode** (`mode health`) — Returns OK on any request; used for simple health check listeners.

### Load Balancing Algorithms

Key algorithms available in backends:

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| `roundrobin` | Dynamic round-robin with weights, supports slow-start | General purpose HTTP/TCP |
| `static-rr` | Static round-robin, no dynamic weight changes | Large farms (>4095 servers) |
| `leastconn` | Server with fewest connections receives request | Long sessions (LDAP, SQL) |
| `first` | Fills servers up to maxconn before using next | Resource optimization |
| `source` | Hashes source IP for stickiness | TCP mode without cookies |
| `uri` / `url_param` | Hashes URI or URL parameter | Cache-friendly backends |
| `hdr(<name>)` | Hashes header value | Header-based routing |
| `random` | Consistent hashing with random key | Frequently changing farms |

### ACLs and Conditions

ACLs (Access Control Lists) enable conditional rule evaluation:

```haproxy
# Define ACLs
acl is_api path_beg /api
acl is_static path_end .css .js .png .jpg
acl healthy server_is_up srv1

# Use ACLs in rules
http-request deny if !is_api !is_static
use_backend api_servers if is_api
default_backend static_servers
```

ACL matching methods include: `-m found`, `-m sub`, `-m reg`, `-m_beg`, `-m end`, `-i` (case-insensitive), `-f` (file-based lookup).

### Health Checks

HAProxy supports multiple health check types:

- **Layer 4** (`option httpchk` with TCP connect) — Verifies server is reachable
- **Layer 7** (`option httpchk` with HTTP request) — Sends HTTP request and checks response code
- **Agent checks** (`agent-check`) — Independent auxiliary health checks via custom protocol
- **Slowstart** — Gradually increases server weight after it becomes healthy

### SSL/TLS Termination

HAProxy can terminate SSL/TLS at the proxy layer:

```haproxy
global
    ssl-default-bind-options ssl-min-ver TLSv1.2
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256

frontend https-in
    bind *:443 ssl crt /etc/ssl/certs/haproxy.pem alpn h2,http/1.1
    http-request set-header X-Forwarded-Proto https
    default_backend web_servers
```

### Stickiness (Session Persistence)

Methods to ensure a client reaches the same backend server:

- **Cookie-based**: `cookie SERVERID insert indirect nocache` on servers
- **Source IP hashing**: `balance source` algorithm
- **URL parameter**: `balance url_param <name>`
- **Header hashing**: `balance hdr(<name>)`
- **Stick-tables**: Advanced persistence using shared state tables

### Logging

HAProxy provides detailed logging with multiple formats:

- **TCP log** (`option tcplog`): Connection-level details, timers, bytes transferred
- **HTTP log** (`option httplog`): Full HTTP request/response details, status codes, captures
- **CLF format**: Apache-compatible Common Log Format
- **Custom format**: User-defined log format with `%[]` specifiers

Logs can be sent to up to two syslog servers per instance with configurable severity levels.

### Statistics and Monitoring

HAProxy provides multiple monitoring interfaces:

1. **Statistics page** — HTTP-based dashboard at a configured URI
2. **Unix socket CLI** — Interactive commands via `stats socket` for runtime management
3. **Master CLI** — Multi-process supervision in master-worker mode
4. **Stats-file** — Periodic stats output to file for external monitoring

### Master-Worker Mode

HAProxy supports master-worker (`-W`) mode where:
- A master process monitors worker processes
- Workers handle actual traffic
- Graceful reloads via `SIGUSR2` or CLI `reload` command
- No service interruption during configuration updates

## Installation / Setup

### Building from Source

```bash
# From the v3.3.0 tag
git clone https://github.com/haproxy/hhaproxy.git -b v3.3.0
cd haproxy
make -j$(nproc) \
    TARGET=linux-glibc \
    USE_OPENSSL=1 \
    USE_ZLIB=1 \
    USE_LUA=1 \
    USE_PROMEX=1

sudo make install
```

### Common Build Options

| Option | Purpose |
|--------|---------|
| `USE_OPENSSL=1` | SSL/TLS support |
| `USE_ZLIB=1` | HTTP compression |
| `USE_LUA=1` | Lua scripting support |
| `USE_PROMEX=1` | Prometheus metrics export |
| `USE_PCRE2=1` | PCRE2 regex engine |
| `USE_NS=1` | Network namespaces |
| `USE_TFO=1` | TCP Fast Open |
| `USE_LINUX_SPLICE=1` | Kernel splicing for zero-copy |

### Starting HAProxy

```bash
# Basic start with config file
haproxy -f /etc/haproxy/haproxy.cfg

# Daemon mode
haproxy -D -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid

# Master-worker mode (recommended for systemd)
haproxy -Ws -f /etc/haproxy/haproxy.cfg

# Validate configuration without starting
haproxy -c -f /etc/haproxy/haproxy.cfg
```

## Usage Examples

### Basic HTTP Reverse Proxy

```haproxy
global
    log /dev/log local0
    maxconn 50000
    daemon

defaults
    log     global
    mode    http
    option  httplog
    timeout connect 5s
    timeout client  30s
    timeout server  30s
    retries 3

frontend web
    bind *:80
    default_backend app_servers

backend app_servers
    balance roundrobin
    server srv1 192.168.1.10:8080 check
    server srv2 192.168.1.11:8080 check
    server srv3 192.168.1.12:8080 check
```

### SSL/TLS Termination with HTTP/2

```haproxy
global
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    ssl-default-bind-ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384

frontend https
    bind *:443 ssl crt /etc/ssl/haproxy.pem alpn h2,http/1.1
    http-request set-header X-Forwarded-Proto https
    
    # ACL-based routing
    acl is_api path_beg /api
    use_backend api_servers if is_api
    default_backend web_app

backend web_app
    balance roundrobin
    cookie SERVERID insert indirect nocache
    server srv1 10.0.0.1:80 check cookie srv1
    server srv2 10.0.0.2:80 check cookie srv2

backend api_servers
    balance leastconn
    http-request set-header X-Forwarded-Host %[hdr(host)]
    server api1 10.0.1.1:3000 check
    server api2 10.0.1.2:3000 check
```

### TCP Load Balancer with Health Checks

```haproxy
frontend tcp_lb
    bind *:3306
    mode tcp
    option tcplog
    default_backend mysql_servers

backend mysql_servers
    balance roundrobin
    option tcp-check
    tcp-check send MYSQL_AUTH\r\n
    tcp-check expect string MARIADB_NP
    server db1 10.0.0.1:3306 check inter 5s rise 2 fall 3
    server db2 10.0.0.2:3306 check inter 5s rise 2 fall 3 backup
```

### Rate Limiting with Stick-Tables

```haproxy
frontend http_front
    bind *:80
    
    # Define stick-table for tracking request rates
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    
    # Track client IP
    http-request track-sc0 src
    
    # Deny if rate exceeds 100 requests per 10 seconds
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
    
    default_backend web_servers

backend web_servers
    balance roundrobin
    server srv1 10.0.0.1:80 check
```

### Content Switching with Maps

```haproxy
global
    log /dev/log local0

defaults
    mode http
    timeout connect 5s
    timeout client 30s
    timeout server 30s

frontend www
    bind *:80
    
    # Use map file for domain-to-backend routing
    use_backend backend_prod if { hdr(Host) -f prod_domains.lst }
    use_backend backend_staging if { hdr(Host) -f staging_domains.lst }
    
    default_backend default_app

backend backend_prod
    balance roundrobin
    server srv1 10.0.1.1:80 check

backend backend_staging
    balance roundrobin
    server srv2 10.0.2.1:80 check

backend default_app
    balance roundrobin
    server srv3 10.0.3.1:80 check
```

### HAProxy with ACME Certificate Management

```haproxy
global
    acme scheduler day 14:00,2:00
    
defaults
    mode http
    timeout connect 5s
    timeout client 30s
    timeout server 30s

frontend https
    bind *:443 ssl crt /etc/haproxy/certs/ alpn h2,http/1.1
    
    acl letsencrypt path_beg /.well-known/acme-challenge/
    use_backend backend_acme if letsencrypt
    
    default_backend web_app

backend backend_acme
    server acme 127.0.0.1:8081

backend web_app
    balance roundrobin
    server srv1 10.0.0.1:80 check
```

### Runtime Management via Unix Socket

```haproxy
global
    stats socket /var/run/haproxy.sock mode 600 level admin
    stats timeout 2m
```

```bash
# Connect and manage HAProxy at runtime
echo "show info" | socat /var/run/haproxy.sock stdio
echo "show stat" | socat /var/run/haproxy.sock stdio
echo "set maxconn 100000" | socat /var/run/haproxy.sock stdio
echo "disable server app_servers/srv2" | socat /var/run/haproxy.sock stdio
echo "enable server app_servers/srv2" | socat /var/run/haproxy.sock stdio

# Interactive mode
socat /var/run/haproxy.sock readline
prompt
> show errors
> show table
> set rate-limit sessions-per-sec 1000
```

### Master-Worker Mode with Systemd

```haproxy
global
    master-worker
    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
```

```bash
# Reload without downtime (SIGUSR2)
kill -USR2 $(cat /var/run/haproxy-master.pid)

# Or via CLI
echo "reload" | socat /run/haproxy-master.sock stdio
```

## Advanced Topics

### Lua Scripting

HAProxy embeds Lua 5.3 for custom logic:

```haproxy
global
    lua-load /etc/haproxy/lua/myscript.lua

defaults
    http-request deny if { lua.myscript -m bool }
```

See [Lua Integration](references/01-lua-integration.md) for detailed Lua API usage.

### DNS Resolution in HAProxy

HAProxy can resolve server hostnames at runtime with health-aware DNS:

```haproxy
resolvers mydns
    parse-resolv-conf
    timeout resolve 5s
    timeout retry   2s

backend app_servers
    balance roundrobin
    option httpchk
    server srv1 app.example.com:80 check resolvers mydns resolve-prefer ipv4
```

### HTTP Compression

```haproxy
defaults
    compression algo gzip
    compression type text/html text/css text/javascript application/json

# Or per-backend
backend api
    compression algo gzip
    compression type application/json
```

### Error Pages

```haproxy
errorfile 403 /etc/haproxy/errors/403.http
errorfile 408 /etc/haproxy/errors/408.http
errorfile 500 /etc/haproxy/errors/500.http
errorfile 502 /etc/haproxy/errors/502.http
errorfile 503 /etc/haproxy/errors/503.http
errorfile 504 /etc/haproxy/errors/504.http
```

### Connection Slots (Per-Server maxconn)

```haproxy
backend app_servers
    balance roundrobin
    server srv1 10.0.0.1:80 check connslots 100
    server srv2 10.0.0.2:80 check connslots 100
```

### Referenced Configuration Keywords Quick Reference

**Global section keywords**: `daemon`, `maxconn`, `log`, `chroot`, `user`, `group`, `uid`, `gid`, `ssl-default-bind-options`, `ssl-default-bind-ciphers`, `master-worker`, `stats socket`, `tune.ssl.default-dh-param`, `spread-checks`

**Frontend keywords**: `bind`, `default_backend`, `use_backend`, `acl`, `http-request`, `http-response`, `mode`, `maxconn`, `timeout client`, `log`, `option httplog`, `cookie`, `capture`, `stats`, `redirect`

**Backend keywords**: `balance`, `server`, `default-server`, `option httpchk`, `cookie`, `retries`, `timeout server`, `hash-type`, `http-reuse`, `maxconn`, `fullconn`

**Defaults keywords**: Inheritable settings for any section type (precedence: section > named defaults > anonymous defaults)

