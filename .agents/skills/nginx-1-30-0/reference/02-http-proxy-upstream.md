# HTTP Proxy and Upstream

## proxy_pass

Forwards requests to a backend server or upstream group:

```nginx
location / {
    proxy_pass http://backend;
}
```

The `proxy_pass` parameter can be:
- A direct address: `http://127.0.0.1:8080`
- An upstream group name: `http://myapp1`
- A Unix socket: `http://unix:/tmp/backend.socket`
- Include URI: `proxy_pass http://backend/other/;`

## Proxy Headers

By default, nginx sends minimal headers to the backend. Set important headers explicitly:

```nginx
location / {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Use `proxy_hide_header` to remove upstream response headers and `proxy_pass_header` to include headers that are hidden by default.

## Proxy Timeouts

```nginx
proxy_connect_timeout 60s;   # timeout establishing connection to backend
proxy_send_timeout 60s;      # timeout between successive writes to backend
proxy_read_timeout 60s;      # timeout between successive reads from backend
```

## Proxy Buffering

By default, nginx buffers the entire upstream response before sending to client:

```nginx
proxy_buffering on;           # default: on
proxy_buffer_size 4k;         # first part of response (headers)
proxy_buffers 8 4k;           # number and size of buffers for rest
proxy_busy_buffers_size 8k;   # max data sent to client while still buffering
```

Disable buffering for streaming responses:

```nginx
proxy_buffering off;
```

## Proxy Caching

Define a cache zone with `proxy_cache_path` in the `http` context, then enable it per location:

```nginx
http {
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m use_temp_path=off;

    server {
        location / {
            proxy_pass http://backend;
            proxy_cache my_cache;
            proxy_cache_valid 200 302 10m;
            proxy_cache_valid 404 1m;
            proxy_cache_key $scheme$proxy_host$request_uri;
            add_header X-Cache-Status $upstream_cache_status;
        }
    }
}
```

Key directives:
- `proxy_cache` — enable caching with named zone
- `proxy_cache_valid` — TTL per status code
- `proxy_cache_key` — cache key expression
- `proxy_cache_bypass` — skip cache when variable is set
- `proxy_no_cache` — skip storing in cache
- `proxy_cache_use_stale` — serve stale content on errors
- `proxy_cache_lock` — prevent cache stampede

## proxy_redirect

Adjusts `Location` and `Refresh` headers from upstream responses:

```nginx
proxy_redirect default;  # adjusts based on proxy_pass
proxy_redirect http://localhost:8000/two/ /one/;
proxy_redirect off;      # pass headers unchanged
```

## proxy_next_upstream

Retries request on next upstream server on specified conditions:

```nginx
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
proxy_next_upstream_timeout 10s;
proxy_next_upstream_tries 3;
```

## Upstream Module

Defines server groups for load balancing:

```nginx
upstream backend {
    server backend1.example.com weight=5;
    server backend2.example.com:8080;
    server unix:/tmp/backend3;
    server backup1.example.com backup;
}
```

### Load Balancing Methods

**Round-robin (default):** Distributes requests evenly across servers.

```nginx
upstream backend {
    server srv1.example.com;
    server srv2.example.com;
    server srv3.example.com;
}
```

**Least connections:** Routes to server with fewest active connections.

```nginx
upstream backend {
    least_conn;
    server srv1.example.com;
    server srv2.example.com;
}
```

**IP hash:** Client IP determines server selection (session persistence).

```nginx
upstream backend {
    ip_hash;
    server srv1.example.com;
    server srv2.example.com;
}
```

**Weighted:** Influence distribution with `weight` parameter.

```nginx
upstream backend {
    server srv1.example.com weight=3;
    server srv2.example.com;
    server srv3.example.com;
}
```

### Server Parameters

- `weight=N` — request weight (default: 1)
- `max_fails=N` — consecutive failures before marking unavailable (default: 1, set to 0 to disable)
- `fail_timeout=T` — duration server is marked unavailable after failures (default: 10s)
- `backup` — only receives traffic when primary servers are down
- `down` — permanently marked as unavailable
- `resolve` — dynamically resolve hostname changes
- `slow_start=T` — gradually increase weight after recovery

### Health Checks

Passive (in-band) health checks are built-in. When a server fails, nginx marks it unavailable for `fail_timeout` then probes with live requests.

### Keepalive Connections

Reuse connections to upstream servers:

```nginx
upstream backend {
    server backend1.example.com;
    server backend2.example.com;
    keepalive 32;
}
```

With keepalive, set HTTP/1.1 for upstream:

```nginx
proxy_http_version 1.1;
proxy_set_header Connection "";
```

### Shared Memory Zone

For dynamic server groups shared across workers:

```nginx
upstream dynamic {
    zone upstream_dynamic 64k;
    server backend1.example.com weight=5;
    server backend2.example.com resolve;
}
```

## FastCGI Proxying

Route requests to PHP-FPM or other FastCGI servers:

```nginx
location ~ \.php$ {
    fastcgi_pass unix:/run/php/php-fpm.sock;
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
}
```

## gRPC Proxying

Forward gRPC requests:

```nginx
location /grpc.service.Service/ {
    grpc_pass grpc://backend:9000;
}
```

Supports `grpc://` (plaintext) and `grpcs://` (TLS) protocols.

## WebSocket Proxying

```nginx
location /ws/ {
    proxy_pass http://websocket_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400s;
}
```

## HTTP Version

Control the HTTP version used for upstream connections:

```nginx
proxy_http_version 1.1;  # needed for WebSocket, keepalive
```
