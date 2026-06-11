# Configuration Syntax and Core Module

## Directive Structure

Nginx configuration uses directives — either simple or block:

**Simple directive:** name + parameters, ends with semicolon.

```nginx
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /run/nginx.pid;
```

**Block directive:** same structure but ends with braces containing nested directives. Blocks that can contain other directives are called contexts: `events`, `http`, `server`, `location`.

```nginx
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        location / {
            root /var/www/html;
        }
    }
}
```

Directives outside any context are in the `main` context. Comments use `#`.

## Measurement Units

**Sizes:** suffixes `k`/`K` (kilobytes), `m`/`M` (megabytes). Offsets also support `g`/`G` (gigabytes). Examples: `1024`, `8k`, `1m`.

**Time intervals:** `ms` (milliseconds), `s` (seconds, default), `m` (minutes), `h` (hours), `d` (days), `w` (weeks), `M` (months = 30 days), `y` (years = 365 days). Multiple units can be combined: `1h 30m` equals `90m` or `5400s`. Always specify a suffix for clarity.

## Core Module Directives

### worker_processes

Sets the number of worker processes. Value `auto` matches available CPU cores. This is the recommended default.

```nginx
worker_processes auto;
```

### worker_connections

Maximum simultaneous connections per worker process, set in the `events` block.

```nginx
events {
    worker_connections 1024;
}
```

### error_log

Specifies error log file and level (debug, info, notice, warn, error, crit, alert, emerg). Default level is `error`.

```nginx
error_log /var/log/nginx/error.log warn;
```

### pid

Path to the PID file for the master process. Default: `/usr/local/nginx/logs/nginx.pid` or `/var/run/nginx.pid`.

```nginx
pid /run/nginx.pid;
```

### include

Includes external configuration files, supporting wildcards.

```nginx
include /etc/nginx/conf.d/*.conf;
include /etc/nginx/sites-enabled/*;
```

## Events Block

The `events` block configures connection processing methods:

```nginx
events {
    worker_connections 1024;
    use epoll;  # Linux — most efficient method
}
```

Available methods:
- `epoll` — Linux 2.6+, most efficient
- `kqueue` — FreeBSD, macOS
- `eventport` — Solaris 10+
- `/dev/poll` — Solaris 7+
- `select` / `poll` — fallback, portable but less efficient

The method is auto-detected by default. Explicitly setting it is only needed for optimization or debugging.

## HTTP Block

The `http` block is the primary context for all HTTP server configuration. It contains `server` blocks, global settings, and module configurations:

```nginx
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    server {
        # ...
    }
}
```

## Server Block

Defines a virtual server. Distinguished by `listen` directives (port/address) and `server_name`:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name example.com www.example.com;
    root /var/www/example;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### listen

Specifies address and port. Parameters include `default_server`, `ssl`, `http2`, `quic`. Since version 0.8.21, use `default_server` (not `default`).

```nginx
listen 80;
listen 443 ssl http2;
listen 443 ssl quic;
listen [::]:80 ipv6only=on;
```

### server_name

Matches the `Host` header. Supports exact names, wildcard prefixes/suffixes (`*.example.com`, `www.example.*`), and regex (`~^www\d+\.example\.com$`).

```nginx
server_name example.com www.example.com;
```

## Location Block

Routes requests within a server block based on URI matching:

```nginx
server {
    location / {
        root /var/www/html;
    }

    location /images/ {
        root /var/www;
    }

    location ~* \.(jpg|png|gif)$ {
        expires 30d;
    }
}
```

Modifier types:
- `/prefix` — prefix match, longest wins
- `= /exact` — exact match, highest priority
- `~ /regex` — case-sensitive regex
- `~* /regex` — case-insensitive regex
- `@named` — internal named location

Selection order: exact match → longest prefix → first regex match → longest prefix fallback.

## Key HTTP Core Directives

### root vs alias

`root` appends the full URI to the path. `alias` replaces the matched location prefix.

```nginx
# root: /images/photo.png → /data/images/photo.png
location /images/ {
    root /data;
}

# alias: /images/photo.png → /data/photos/photo.png
location /images/ {
    alias /data/photos/;
}
```

### try_files

Tests files in order and uses the first that exists. Falls back to a URI or status code:

```nginx
location / {
    try_files $uri $uri/index.html $uri.html =404;
}

# Named location fallback
location / {
    try_files $uri $uri/ @backend;
}

location @backend {
    proxy_pass http://app_server;
}
```

### index

Specifies default index files:

```nginx
location / {
    root /var/www/html;
    index index.html index.htm;
}
```

### error_page

Custom error pages:

```nginx
error_page 404 /404.html;
error_page 500 502 503 504 /50x.html;
error_page 404 =200 /empty.gif;       # override status code
error_page 403 =301 http://example.com/forbidden.html;  # redirect
```

### include

Modularize configuration:

```nginx
http {
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```
