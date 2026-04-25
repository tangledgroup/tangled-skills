# Performance Tuning & Optimization

## Worker Process Tuning

### `worker_processes`

```nginx
# Best practice: auto-detect CPU cores
worker_processes auto;

# Or explicitly set to number of physical cores (not hyper-threaded)
worker_processes 4;
```

**Guidelines:**
- Set to `auto` for most deployments
- For high-throughput proxying, consider matching physical cores (not logical/HT cores)
- Each worker handles connections independently — more workers = more parallelism

### `worker_connections`

```nginx
events {
    worker_connections 4096;
}
```

**Maximum theoretical connections per worker:** `worker_connections × worker_processes`

For a single server handling ~8192 connections with 2 workers: `4096 × 2 = 8192`

**Considerations:**
- Includes ALL connections (clients + proxied backends)
- Must not exceed OS limit on open files (`worker_rlimit_nofile`)
- Typical values: 1024–65536 depending on available memory

### `worker_rlimit_nofile`

```nginx
worker_rlimit_nofile 65535;
```

Ensure this is set high enough to accommodate all connections plus log files. Check current limit:
```bash
ulimit -n
```

Set in `/etc/security/limits.conf`:
```
* soft nofile 65535
* hard nofile 65535
```

### `worker_cpu_affinity`

```nginx
# Bind each worker to specific CPU core
worker_processes    4;
worker_cpu_affinity 0001 0010 0100 1000;

# Hyper-threading friendly: spread across physical cores
worker_processes    8;
worker_cpu_affinity 01010101 10101010 01010101 10101010 01010101 10101010 01010101 10101010;

# Auto-bind (Linux, FreeBSD)
worker_processes auto;
worker_cpu_affinity auto;
```

### `worker_priority`

```nginx
# Higher priority (lower nice value) for production
worker_priority -5;
```

Range typically -20 to 20. Negative values increase priority.

## Connection Processing Optimization

### `use epoll` (Linux)

```nginx
events {
    use epoll;
}
```

Nginx auto-detects the best method, but explicit setting can be useful for documentation or when cross-compiling.

### `multi_accept`

```nginx
events {
    multi_accept on;
}
```

Workers accept all pending connections at once instead of one at a time. Recommended for high-traffic servers.

### `accept_mutex` and `accept_mutex_delay`

```nginx
events {
    accept_mutex on;
    accept_mutex_delay 500ms;
}
```

On Linux 4.5+ with `EPOLLEXCLUSIVE`, this is unnecessary. With `reuseport`, also unnecessary.

### `stall_threshold`

```nginx
events {
    stall_threshold 1000ms;
}
```

Time threshold for event loop iteration before a stall is reported. Useful for monitoring and debugging performance issues. *Commercial subscription feature.*

## File I/O Optimization

### `sendfile`

```nginx
http {
    sendfile on;
    tcp_nopush on;
}
```

Uses `sendfile()` syscall instead of read/write for static file serving. Much more efficient — kernel handles the data transfer directly from page cache to socket.

### `tcp_nopush`

Must be used with `sendfile on`. Combines response header and beginning of file into one packet (Linux: `TCP_CORK`, FreeBSD: `TCP_NOPUSH`).

### `tcp_nodelay`

Enables `TCP_NODELAY` option, disabling Nagle's algorithm. Critical for interactive applications and keep-alive connections.

**Default:** `on` — usually no change needed.

### `sendfile_max_chunk`

```nginx
sendfile_max_chunk 4m;
```

Limits data transferred per `sendfile()` call. Prevents a single fast connection from monopolizing a worker process. Set to `0` for unlimited (not recommended for high-traffic).

**Default:** `2m`

### `read_ahead`

```nginx
read_ahead 128k;
```

Pre-reads data into kernel page cache. On Linux, uses `posix_fadvise(POSIX_FADV_SEQUENTIAL)` — size parameter is ignored.

**Default:** `0` (disabled)

### `open_file_cache`

```nginx
open_file_cache          max=10000 inactive=20s;
open_file_cache_valid    30s;
open_file_cache_min_uses 3;
open_file_cache_errors   on;
```

Caches:
- Open file descriptors, sizes, modification times
- Directory existence info
- File lookup errors (when `open_file_cache_errors on`)

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `max` | Max cached entries (LRU eviction) |
| `inactive` | Time before removing unused entries (default: 60s) |
| `valid` | Validation interval for cached entries |
| `min_uses` | Min accesses during inactive period to stay cached |

**Best practice:** Set `max` based on number of unique files served. Higher values reduce disk I/O but use more memory.

### `output_buffers`

```nginx
output_buffers 4 32k;
```

Number and size of buffers for reading response from disk. Important for large file serving.

**Default:** `2 32k` (prior to 1.9.5: `1 32k`)

## Proxy Performance Tuning

### Keepalive Connections to Upstream

```nginx
upstream backend {
    server backend1.example.com;
    keepalive 64;
}

server {
    location / {
        proxy_pass http://backend;
        # For versions before 1.29.7:
        # proxy_http_version 1.1;
        # proxy_set_header Connection "";
    }
}
```

**Parameters:**
| Directive | Description | Default (since 1.29.7) |
|-----------|-------------|----------------------|
| `keepalive connections` | Max idle keepalive connections per worker | 32 |
| `keepalive_requests` | Max requests per keepalive connection | 1000 |
| `keepalive_timeout` | Idle timeout for upstream keepalive | 60s |
| `keepalive_time` | Max lifetime of keepalive connection | 1h |

**Important:** For HTTP/1.1 persistent connections to upstream, set:
```nginx
proxy_http_version 1.1;
proxy_set_header Connection "";
```

### Proxy Buffer Tuning

```nginx
proxy_buffer_size 8k;
proxy_buffers 8 16k;
proxy_busy_buffers_size 32k;
proxy_temp_file_write_size 64k;
proxy_max_temp_file_size 1024m;
```

| Directive | Description |
|-----------|-------------|
| `proxy_buffer_size` | Buffer for first (initial) part of response headers |
| `proxy_buffers` | Number and size of buffers per request |
| `proxy_busy_buffers_size` | Max data that can be sent to client while reading from upstream |
| `proxy_temp_file_write_size` | Max data written to temp file at once |
| `proxy_max_temp_file_size` | Max total size of proxy temp files |

### Proxy Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=static_cache:50m max_size=10g inactive=7d use_temp_path=off;

server {
    location ~* \.(css|js|jpg|png|gif|ico|svg|woff2)$ {
        proxy_cache static_cache;
        proxy_cache_valid 200 302 7d;
        proxy_cache_valid 404 1m;
        proxy_cache_key $scheme$request_method$host$request_uri;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        proxy_cache_lock on;
        expires 7d;
        add_header X-Cache-Status $upstream_cache_status;
        proxy_pass http://backend;
    }
}
```

**Cache parameters:**
| Directive | Description |
|-----------|-------------|
| `proxy_cache_path` | Define cache storage path, zones, and limits |
| `proxy_cache` | Enable cache for location |
| `proxy_cache_key` | Key used to identify cached objects |
| `proxy_cache_valid` | Cache validity by response code |
| `proxy_cache_use_stale` | Serve stale content during errors/timeouts |
| `proxy_cache_lock` | Only one request populates cache at a time |
| `proxy_cache_bypass` | Skip cache when condition is true |
| `proxy_no_cache` | Never cache when condition is true |

### Proxy Timeout Tuning

```nginx
proxy_connect_timeout 10s;
proxy_send_timeout 30s;
proxy_read_timeout 60s;
proxy_next_upstream error timeout http_502 http_503;
proxy_next_upstream_tries 3;
proxy_next_upstream_timeout 30s;
```

Tune based on expected backend response times. Shorter timeouts fail faster, allowing `proxy_next_upstream` to try another server quickly.

## Compression Optimization

### Gzip Tuning

```nginx
gzip on;
gzip_comp_level 4;          # Balance between CPU and bandwidth (1-9)
gzip_min_length 1024;       # Only compress responses >= 1KB
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
gzip_vary on;
gzip_proxied any;
```

**Compression level guide:**
| Level | CPU Usage | Compression Ratio | Best For |
|-------|-----------|-------------------|----------|
| 1 | Lowest | ~60% of max | Very high traffic, cheap CPU |
| 4-6 | Medium | ~85-90% of max | **Recommended default** |
| 9 | Highest | Maximum | Low traffic, bandwidth-constrained |

### Gunzip Module

```nginx
gunzip on;
```

Decompresses responses with `Content-Encoding: gzip` for clients that don't support gzip encoding.

## Rate Limiting & DDoS Protection

### Request Rate Limiting

```nginx
# Define zones
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=2r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/m;

server {
    location / {
        limit_req zone=general burst=20 nodelay;
    }

    location /api/ {
        limit_req zone=api burst=5 nodelay;
    }

    location /login {
        limit_req zone=login burst=3;
        # Note: no nodelay means requests are queued, not rejected
        limit_req_status 429;
    }
}
```

### Connection Limiting

```nginx
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    limit_conn addr 10;
    limit_conn_status 429;
    limit_req_status 429;

    location / {
        proxy_pass http://backend;
    }
}
```

### Custom Rate Limit Response

```nginx
# In events or main context (not available — use error_page)
error_page 429 /429.html;

location = /429.html {
    internal;
    default_type text/plain;
    return 429 "Rate limit exceeded. Try again later.\n";
}
```

## SSL/TLS Performance

### Session Resumption

```nginx
ssl_session_cache shared:SSL:50m;
ssl_session_timeout 1d;
ssl_session_tickets off;  # Disable for forward secrecy
```

| Setting | Recommendation |
|---------|---------------|
| `ssl_session_cache` | `shared:SSL:50m` (supports ~200K sessions) |
| `ssl_session_timeout` | `1d` or longer |
| `ssl_session_tickets` | `off` for forward secrecy, `on` for performance |

### OCSP Stapling

```nginx
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

Reduces SSL handshake latency by eliminating separate OCSP lookups.

### Protocol Selection

```nginx
# Recommended: only TLS 1.2 and 1.3
ssl_protocols TLSv1.2 TLSv1.3;

# Cipher suites (modern, secure)
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers on;
```

### HTTP/2 Performance

```nginx
listen 443 ssl http2;

http2_max_requests 1000;
http2_max_concurrent_streams 128;
http2_recv_timeout 60s;
```

HTTP/2 multiplexing reduces connection overhead. Tune `max_concurrent_streams` based on application characteristics.

### HTTP/3 (QUIC) Performance

```nginx
listen 443 quic reuseport;
listen 443 ssl http2;

quic_retry on;
add_header Alt-Svc 'h3=":443"; ma=86400';
```

QUIC reduces handshake latency and eliminates head-of-line blocking at TCP layer. Requires UDP port 443 open.

## Thread Pools

For multi-threaded file I/O without blocking workers:

```nginx
thread_pool my_io_pool threads=16 max_queue=65536;

server {
    location /large-files/ {
        aio threads=my_io_pool;
        sendfile on;
    }
}
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `threads` | Number of threads in the pool |
| `max_queue` | Max tasks waiting in queue (overflow returns error) |

Default pool: `default threads=32 max_queue=65536`

## Memory Optimization

### Hash Table Sizing

Nginx uses hash tables for server names, types, and variables. Proper sizing avoids runtime resizing overhead.

```nginx
# Server names hash
server_names_hash_bucket_size 64;
server_names_hash_max_size 1024;

# Types hash
types_hash_bucket_size 64;
types_hash_max_size 1024;

# Variables hash
variables_hash_bucket_size 128;
variables_hash_max_size 2048;
```

**Tuning guide:**
- Increase `bucket_size` if you have many long server names or variable names
- Increase `max_size` if warnings appear in error log about "server_names_hash" or "variables_hash"
- Check for hash table warnings in `error_log` during configuration test: `nginx -t`

### Request Body Buffering

```nginx
client_body_buffer_size 16k;
client_max_body_size 10m;
client_header_buffer_size 1k;
large_client_header_buffers 4 8k;
```

| Directive | Description | Default |
|-----------|-------------|---------|
| `client_body_buffer_size` | Buffer for request body | 16k (8k on 32-bit) |
| `client_max_body_size` | Max request body size | 1m |
| `client_header_buffer_size` | Buffer for client request header | 1k |
| `large_client_header_buffers` | Max number/size for large headers | 4 8k |

Exceeding these limits returns `413 Request Entity Too Large` or `414 URI Too Long`.

## Logging Optimization

### Buffered Log Writing

```nginx
access_log /var/log/nginx/access.log combined buffer=32k gzip flush=5m;
```

Buffered and optionally compressed log writes reduce disk I/O significantly.

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `buffer=size` | Buffer size for log writes (default: 64k) |
| `gzip[=level]` | Compress buffered logs (1-9, default: 1) |
| `flush=time` | Flush buffer after this duration |

### Log File Descriptor Caching

```nginx
open_log_file_cache max=1000 inactive=20s valid=1m min_uses=2;
```

Caches file descriptors for logs with variable names (e.g., per-vhost logs).

## Monitoring & Diagnostics

### Status Endpoint

```nginx
location /nginx_status {
    stub_status;
    allow 127.0.0.1;
    allow monitoring_server;
    deny all;
}
```

Output:
```
Active connections: 156
server accepts handled requests
 12345 12345 45678
Reading: 2 Writing: 5 Waiting: 149
```

### Connection Metrics to Monitor

| Metric | How to Check | Healthy Range |
|--------|-------------|---------------|
| Active connections | `stub_status` → Active connections | Below `worker_processes × worker_connections × 0.7` |
| Waiting connections | `stub_status` → Waiting | Should be high relative to Reading/Writing (keep-alive) |
| Dropped connections | Check `/proc/net/sockstat` or system logs | Near zero |
| Worker CPU usage | `top -p $(pgrep nginx)` | Spread evenly across workers |
| Open files | `lsof -p <nginx_pid>` | Below `worker_rlimit_nofile` |

### Debug Logging

Build with `--with-debug` and enable:
```nginx
error_log /var/log/nginx/debug.log debug;

events {
    debug_connection 192.168.1.0/24;  # Only debug specific IPs
}
```

Debug logs are extremely verbose — only use for troubleshooting, never in production.

## Configuration Checklist for High Traffic

```nginx
# Worker tuning
worker_processes auto;
worker_rlimit_nofile 65535;
worker_shutdown_timeout 10s;

events {
    use epoll;
    worker_connections 4096;
    multi_accept on;
}

http {
    # I/O optimization
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;

    # Keepalive
    keepalive_timeout 65;
    keepalive_requests 100;

    # Buffer sizes
    client_body_buffer_size 16k;
    client_header_buffer_size 4k;
    large_client_header_buffers 4 16k;

    # Caching
    open_file_cache max=10000 inactive=20s;
    open_file_cache_valid 60s;
    open_file_cache_min_uses 5;
    open_file_cache_errors on;

    # Compression
    gzip on;
    gzip_comp_level 4;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml image/svg+xml;
    gzip_vary on;

    # Proxy optimization
    proxy_buffer_size 8k;
    proxy_buffers 8 16k;
    proxy_busy_buffers_size 32k;

    # Logging (buffered)
    access_log /var/log/nginx/access.log combined buffer=32k flush=5m;
}
```
