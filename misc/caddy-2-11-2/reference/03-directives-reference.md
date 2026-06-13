# Directives Reference

Directives are functional keywords within site blocks. They execute in a specific default order unless wrapped in `route` blocks or reordered with the `order` global option.

## Directive Order

The default execution order (top to bottom):

```
tracing
map
vars
fs
root
log_append
log_skip
log_name
header
request_body
redir
method
rewrite
uri
try_files
basic_auth
forward_auth
request_header
encode
push
intercept
templates
invoke
handle
handle_path
route
abort
error
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```

Within `route` blocks, directives execute in the order they appear (no sorting).

## Core Directives

### `respond`

Write a hard-coded response:

```caddy
example.com {
    respond "Hello, world!" 200
    respond /hello "Hello!" 200
}
```

With headers and content type:

```caddy
respond /api/status `{ "status": "ok" }` 200 {
    header Content-Type application/json
}
```

### `file_server`

Serve static files from disk:

```caddy
example.com {
    root * /var/www
    file_server
}
```

With browsing and precompressed files:

```caddy
file_server {
    browse
    precompressed gzip zstd
}
```

### `reverse_proxy`

Powerful reverse proxy with load balancing, health checks, and websockets:

```caddy
example.com {
    reverse_proxy localhost:9001 localhost:9002 {
        lb_policy round_robin
        health_uri /health
        health_interval 10s
        header_up -Origin
        header_down -Server
        flush_interval -1
    }
}
```

Load balancing policies: `round_robin`, `random`, `first`, `least_connection`, `least_time`, `ip_hash`.

Proxy to multiple upstreams with port range shorthand:

```caddy
reverse_proxy localhost:9001-9010
```

Handle response from proxy:

```caddy
reverse_proxy localhost:8080 {
    handle_response {
        @success {
            expression {hp.Response.Status} >= 200 && {hp.Response.Status} < 300
        }
        copy_response @success
    }
}
```

### `redir`

Issue HTTP redirects:

```caddy
# Simple redirect
redir https://newsite.com{uri}

# With status code
redir /old /new 301

# Matcher-based
redir @mobile https://m.example.com{uri} 302
```

### `root`

Set the site root for file operations:

```caddy
root * /var/www
root /api/* /var/www/api
```

### `encode`

Response encoding (compression):

```caddy
encode gzip zstd
```

With content type filtering:

```caddy
encode gzip zstd {
    prefer br gzip zstd
}
```

### `header`

Set or remove response headers:

```caddy
# Set header
header Security-Header "value"

# Add to existing (append)
header +X-Custom "value"

# Remove header
header -Server

# Conditional
header /api/* Cache-Control "no-store"
```

### `request_header`

Manipulate request headers:

```caddy
request_header set X-Real-IP {remote_host}
request_header set X-Forwarded-Proto {scheme}
request_header strip Authorization
```

### `rewrite`

Internal URI rewrite:

```caddy
rewrite /old-path /new-path
rewrite @legacy /api/v2{uri}
```

### `try_files`

Rewrite based on file existence (useful for SPAs):

```caddy
try_files {path} {path}/ /index.html
```

### `tls`

Customize TLS settings per site:

```caddy
# Use specific cert and key
tls /path/to/cert.pem /path/to/key.pem

# Internal (local CA) certificate
tls internal

# With custom issuer
tls {
    protocol min version 1.3
    ciphers TLS_AES_128_GCM_SHA256
}
```

### `bind`

Bind to specific interfaces:

```caddy
bind 10.0.0.1
bind ::1 127.0.0.1
```

## Routing Directives

### `handle`

Mutually exclusive group — first matching handle block wins:

```caddy
example.com {
    handle /api/* {
        reverse_proxy localhost:8080
    }
    handle /static/* {
        root * /var/www
        file_server
    }
    handle {
        respond "Not found" 404
    }
}
```

### `handle_path`

Like `handle` but strips the matched path prefix:

```caddy
handle_path /app/* {
    root * /var/www/app
    file_server
}
# Request to /app/foo.js resolves to /foo.js in the root
```

### `route`

Execute directives in literal order (no sorting):

```caddy
route /api/* {
    rewrite /api/v2{uri}
    reverse_proxy localhost:8080
}
```

### `handle_errors`

Handle errors from downstream handlers:

```caddy
handle_errors {
    @5xx {
        expression {http.error.status_code} >= 500
    }
    respond @5xx "Service unavailable" 503
}
```

## Authentication Directives

### `basic_auth`

HTTP Basic Authentication:

```caddy
basic_auth {
    alice $2a$14$...hashed-password...
    bob $2a$14$...hashed-password...
}
```

Hash passwords with `caddy hash-password`. Supports `argon2id` (recommended) and `bcrypt` algorithms.

### `forward_auth`

Delegate authentication to external service:

```caddy
forward_auth https://auth.example.com {
    copy_headers Authorization Set-Cookie
}
```

## Logging Directives

### `log`

Enable access/request logging per site:

```caddy
log {
    output file /var/log/example.com/access.log {
        roll_size 100mb
        roll_keep 10
        roll_gzip
    }
    format json
}
```

Output modules: `stdout`, `stderr`, `file`, `network`. Format modules: `json`, `console`, `filter`, `indent`.

### `log_skip`

Skip logging for matched requests:

```caddy
log_skip {
    path /health
    path /favicon.ico
}
```

### `log_append`

Append custom fields to access logs:

```caddy
log_append my_field "custom_value"
```

## Utility Directives

### `map`

Map input values to outputs:

```caddy
map {header.User-Agent} {upstream} {
    "*Chrome*" localhost:8080
    "*Firefox*" localhost:8081
    "*Safari*"   localhost:8082
    "*"          localhost:8083
}
reverse_proxy {upstream}
```

### `vars`

Set arbitrary variables:

```caddy
vars {my_var} "hello"
respond "Value: {vars.my_var}"
```

### `import`

Include snippets or files:

```caddy
import logging_snippet
import /path/to/config/*.caddyfile
```

### `invoke`

Invoke a named route (experimental):

```caddy
invoke app-proxy
```

### `uri`

Manipulate the URI:

```caddy
uri strip_prefix /api
uri strip_path_suffix .html
uri replace_path /old /new
```

### `method`

Change HTTP method internally:

```caddy
method POST GET
```

### `request_body`

Manipulate request body:

```caddy
request_body {
    max_size 10MB
}
```

### `intercept`

Intercept responses from downstream handlers:

```caddy
intercept {
    header * -Server
    header Content-Security-Policy "default-src 'self'"
}
```

### `tracing`

OpenTelemetry tracing integration:

```caddy
tracing my-service
```

### `metrics`

Prometheus metrics endpoint (per-site):

```caddy
metrics {
    listen :9184
}
```

### `push`

HTTP/2 server push:

```caddy
push /style.css /index.css
push /app.js /index.js
```

### `templates`

Execute Go templates on responses:

```caddy
templates
```

### `php_fastcgi`

Serve PHP via FastCGI:

```caddy
example.com {
    php_fastcgi unix//run/php/php8.3-fpm.sock
    file_server
}
```

### `abort`

Abort the HTTP request:

```caddy
handle @blocked {
    abort
}
```

### `error`

Trigger an error to be handled by `handle_errors`:

```caddy
error @unauthorized 403
```

### `acme_server`

Embedded ACME server (for testing):

```caddy
acme_server
```

## Directive Sorting Rules

- Differently named directives sorted by default order position
- Same-named directives sorted by matcher specificity:
  - Single path matcher first (most specific to least)
  - Other matchers next (in file order)
  - No matcher last
- `vars` directive has reversed matcher ordering
- `route` block contents preserve literal order
