# Caddyfile Directives Reference

Complete reference for all built-in Caddyfile directives in Caddy 2.11.2.

## Directive Order

In the HTTP app, handler directives are executed in a specific order unless inside `route` blocks:

1. `tracing`
2. `basicauth`
3. `forward_auth`
4. `request_body`
5. `copy_response`
6. `encode`
7. `templates`
8. `static_file_redirect`
9. `file_server`
10. `static_response` (respond)
11. `error`
12. `rewrite`
13. `route`
14. `handle` / `handle_path`
15. `reverse_proxy`
16. `metrics`
17. `abort`
18. `skip_log`

Inside `route` blocks, directives execute in the order they appear.

---

## respond

Return a fixed response to the client.

```caddyfile
respond [<matcher>] <body|status> [status <code>] [header <Field>: <value>]
```

**Examples:**

```caddyfile
# Simple text response
respond "Hello, World!"

# With status code
respond 404 "Not Found"

# With headers
respond /api {
    body "OK"
    header Content-Type application/json
    header X-Custom-Value "test"
}

# Template evaluation supported
respond "{{.Host}} - {{.Path}}"
```

---

## redir

Redirect requests to another location.

```caddyfile
redir [<matcher>] <destination> [status_code]
```

**Examples:**

```caddyfile
# Permanent redirect
redir https://example.com{uri} 301

# Redirect with status code
redir /old /new 302

# Redirect to external URL
redir /external https://other-site.com 301

# Using placeholders in destination
redir {http.request.uri} https://example.com{path} 301
```

---

## file_server

Serve static files from a directory.

```caddyfile
file_server [<matcher>] [root <dir>] [browse] [precompressed <encoding...>] [hide <glob...>] [index <name...>] [ascend] [page_feedback] [header <Field>: <value>] [basicauth [...]]
```

**Examples:**

```caddyfile
# Basic file server
file_server

# With root directory
file_server /static {
    root /var/www/static
}

# With directory browsing
file_server {
    browse
}

# Precompressed variants (Gzip, Brotli, Zstandard)
file_server {
    precompressed gzip br zstd
}

# Hide files/directories matching glob patterns
file_server {
    hide *.txt .git/*
}

# With custom index files
file_server {
    index home.html index.html
}

# Complete example
file_server /docs {
    root /var/www/docs
    browse
    precompressed gzip br
    header Cache-Control "max-age=31536000, immutable"
}
```

---

## reverse_proxy

Proxy requests to upstream servers.

```caddyfile
reverse_proxy [<matcher>] [<addresses...>] [<handler_module>] {
    # Transport settings
    transport <protocol> {
        tls [tls_client_auth]
        read_buffer <size>
        write_buffer <size>
        max_response_header_size <size>
        dial_timeout <duration>
        dial_fallback_delay <duration>
        fallback_delay <duration>
        initial_stream_window_size <size>
        initial_connection_window_size <size>
        max_concurrent_streams <count>
        max_streams <count>
        proxy_protocol <version|header>
        tls_handshake_timeout <duration>
        tls_alpn [<protocols...>]
        force_https [true|false]
        ows [true|false]
        strict_sni_host [true|false]
        
        # HTTP/2 settings
        read_concurrency [true|false]
        read_flow_initial_window_size_bytes <size>
        read_max_frame_size <size>
        read_rst_stream_buffer_size <size>
        read_slow_connection_threshold <duration>
        read_slow_timeout <duration>
        
        # HTTP/3 settings
        alternate_protocols [true|false]
    }
    
    # Load balancing
    lb_policy <policy> [round_robin|random|first|nearest|latency|ip_hash|uri_hash|header_<name>|cookie_<name>]
    lb_retries <count>
    lb_try_interval <duration>
    lb_try_duration <duration>
    lb_response_matcher [<matcher>]
    
    # Health checks
    health_uri <uri>
    health_interval <duration>
    health_timeout <duration>
    health_status <status_code>
    health_body <regexp>
    health_headers <Field>: <value> [...]
    
    # Health check follow redirects
    health_follow_redirects [true|false]
    health_check_header <name> <value> [...]
    health_check_interval <duration>
    health_check_uri <uri>
    
    # Passive health check (fails filter)
    fails_filter <regexp>
    
    # Circuit breaker
    circuit_breaker expression <expr>
    
    # Flapping settings
    flapping_retries <count>
    flapping_interval <duration>
    flapping_window <duration>
    
    # Request rewriting
    rewrite [<matcher>] <field> <value>
    strip_path [true|false]
    strip_prefix <prefix...>
    strip_suffix <suffix...>
    
    # Header manipulation
    header_up [<matcher>] <Field>: <value> [...]
    header_down [<matcher>] <Field>: <value> [...]
    
    # Buffering
    buffer_requests [true|false]
    buffer_responses [true|false]
    max_buffer_size <size>
    
    # Compression
    compression gzip|zstd|br [true|false]
    
    # Batch size
    batch_size <count>
    
    # Proxy protocol
    proxy_protocol <version>|*|header
    
    # Trusted proxies
    trusted_proxies <ip|cidr|static|private_ranges|range <start>-<end> [...]>
    
    # Flush interval
    flush_interval <duration>|-1
    
    # Server name header
    upstream_header_format format <format...>
    
    # Metrics namespace
    metrics [<path>]
}
```

**Transport Protocols:**

```caddyfile
# HTTP transport (default)
transport http {
    tls
    tls_connection_safety_timeout 10s
    tls_handshake_timeout 10s
    tls_max_size 2MB
    tls_min_version tls1.3
    tls_server_name upstream.example.com
}

# FastCGI transport
transport fastcgi {
    split <delimiter>
    index <name...>
    env <NAME>=<value> [...]
    root <path>
    send_on_empty <values...>
    read_timeout <duration>
    write_timeout <duration>
    keepalive <interval>
    maxbytespersec <size>
}

# H2C transport (HTTP/2 cleartext)
transport h2c {
    # Same options as HTTP transport
}

# Websocket transport
transport websocket {
    # Same options as HTTP transport
}
```

**Examples:**

```caddyfile
# Simple reverse proxy
reverse_proxy localhost:8080

# With load balancing
reverse_proxy {
    to backend1:8080 backend2:8080 backend3:8080
    lb_policy round_robin
    health_uri /healthz
    health_interval 10s
    health_timeout 5s
}

# With custom headers
reverse_proxy localhost:3000 {
    header_up Host {upstream_hostport}
    header_up X-Real-IP {remote_host}
    header_up X-Forwarded-For {remote_host}
    header_up X-Forwarded-Proto {scheme}
    header_down -Server
}

# With request rewriting
reverse_proxy /api/* localhost:8080 {
    strip_prefix /api
}

# HTTP/2 cleartext
reverse_proxy h2c://localhost:9090

# FastCGI
reverse_proxy unix//run/php/php-fpm.sock {
    transport fastcgi {
        root /var/www/html
        split .php
        index index.php
    }
}

# With circuit breaker
reverse_proxy localhost:8080 {
    health_uri /health
    fails_filter `5[0-9]{2}`
    circuit_breaker rate(10, 60s)
}

# WebSocket proxy
websocket /ws/* localhost:8080
```

---

## handle / handle_path

Group directives with custom matchers and execution order.

```caddyfile
handle [<matcher>] {
    <directive> [...]
}

handle_path [<matcher>] <path_template> {
    <directive> [...]
}
```

**Examples:**

```caddyfile
# Handle all requests with specific handlers
handle {
    respond "Hello" 200
}

# With matcher
handle /api/* {
    reverse_proxy api:8080
}

# handle_path strips the prefix
handle_path /api/* {
    # {path} will not include /api prefix
    reverse_proxy localhost:3000
}

# Nested handles
handle /static/* {
    file_server
}

handle /api/* {
    reverse_proxy backend:8080
}

handle {
    respond "404" 404
}
```

---

## route

Group directives with explicit ordering.

```caddyfile
route [<matcher>] {
    <directive> [...]
}
```

**Examples:**

```caddyfile
# Route with explicit order (executes top to bottom)
route /api/* {
    # First try to serve cached response
    respond "cached" 200 {
        expression `{http.request.uri.path}` =~ `^/cache/`
    }
    
    # Then proxy to backend
    reverse_proxy localhost:8080
}

# Named route for reuse
route /graphql {
    reverse_proxy graphql:4000
}

# Invoke named route elsewhere
handle /api/graphql {
    invoke /graphql
}
```

---

## tls

Configure TLS certificates and settings.

```caddyfile
tls [<email>|internal|force_automate]|[<cert_file> <key_file>] {
    protocols <min> [<max>]
    ciphers   <cipher_suites...>
    curves    <curves...>
    client_auth {
        mode                   [request|require|verify_if_given|require_and_verify]
        trust_pool             <module_name> [...]
        trusted_leaf_cert      <base64_der>
        trusted_leaf_cert_file <filename>
    }
    alpn                          <values...>
    load                          <paths...>
    ca                            <acme_ca_endpoint>
    ca_root                       <pem_file>
    key_type                      [ed25519|p256|p384|rsa2048|rsa4096]
    dns                           [<provider_name> [...]]
    propagation_delay             <duration>
    propagation_timeout           <duration>
    resolvers                     <dns_servers...>
    dns_ttl                       <duration>
    dns_challenge_override_domain <domain>
    on_demand
    reuse_private_keys
    force_automate
    eab                           <key_id> <mac_key>
    issuer                        <module_name> [...]
    get_certificate               <module_name> [...]
    insecure_secrets_log          <log_file>
    renewal_window_ratio          <ratio>
}
```

**Examples:**

```caddyfile
# Let's Encrypt with email
example.com {
    tls admin@example.com
}

# ZeroSSL
example.com {
    tls {
        issuer acme zerossl
    }
}

# Custom certificates
example.com {
    tls /etc/ssl/certs/example.crt /etc/ssl/private/example.key
}

# Internal CA (local)
internal.example.com {
    tls internal
}

# Full TLS configuration
secure.example.com {
    tls admin@example.com {
        protocols tls1.2 tls1.3
        ciphers TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256
        curves x25519 secp384r1
        
        client_auth {
            mode require_and_verify
            trusted_leaf_cert_file /etc/caddy/client-ca.pem
        }
        
        alpn h3
        key_type ed25519
    }
}

# ACME with custom CA
example.com {
    tls {
        ca https://my-acme-server/dir
        eab key_id mac_key
        dns cloudflare {env.CLOUDFLARE_API_KEY}
    }
}

# On-demand TLS (issue certs for arbitrary hostnames)
example.com {
    tls {
        on_demand
    }
}

# Force automate (skip DNS check)
wildcard.example.com {
    tls admin@example.com force_automate
}
```

---

## log

Configure access logging.

```caddyfile
log {
    output <stdout|file|discard> [<path>] {
        rotate_size     <size>      # Rotate at size
        rotate_gzip     [true|false]
        rotate_keep     <count>     # Number of files to keep
        rotate_keep_age <duration>  # Keep files for duration
        rotate_compress [true|false]
    }
    
    encoding <encoding> [<params...>]
    format <format>|<module_name> [<params...>]
    log_call <string>
    selector <expression>
    suppress [<matcher>]
    common_log [<remote_ip>:<remote_port> <ident> <user> [<timestamp>] "<request>" <status> <size> "<referer>" "<user_agent>"]
    console [<format>]
    file <path> [true|false] [true|false] [true|false]
    filter {
        expression <expr>
        routing <expression> <handler_name> [...]
    }
}
```

**Examples:**

```caddyfile
# Default logging
log

# Custom log output
log {
    output file /var/log/caddy/access.log {
        roll_size 10MiB
        roll_keep 10
        roll_keep_age 30d
    }
}

# JSON format with rotation
log {
    output file /var/log/cidy/app.log
    format json {
        time_format 2006-01-02T15:04:05.000Z07:00
    }
}

# Console output for development
log {
    output stdout
}

# Suppress logging for specific paths
log {
    output file /var/log/cidy/access.log
    suppress /health
}
```

---

## bind

Specify network interfaces and protocols.

```caddyfile
bind [<addresses...>] [{
    protocols [h1|h2|h2c|h3] [...]
}]
```

**Examples:**

```caddyfile
# Bind to specific interface
bind 192.168.1.1 :443 {
    protocols h1 h2 h3
}

# HTTP/3 only
bind :443 {
    protocols h3
}

# Standard HTTPS (h1 + h2 + h3)
bind :443 {
    protocols h1 h2 h3
}
```

---

## basicauth

HTTP Basic Authentication.

```caddyfile
basecret [<matcher>] {
    <username> <hashed_password> [hash_algorithm]
}
```

**Hashing passwords:**

```bash
# Recommended: Argon2id
caddy hash-password --plaintext mypassword --algorithm argon2id

# Legacy: bcrypt
caddy hash-password --plaintext mypassword --algorithm bcrypt

# With custom bcrypt cost
caddy hash-password -p "mypassword" -a bcrypt --bcrypt-cost 14
```

**Examples:**

```caddyfile
admin.example.com {
    basicauth {
        admin $2a$14$...bcrypt_hash...
        operator $argon2id$v=19$m=65536,t=3,p=4$...argon2_hash...
    }
    file_server
}
```

---

## vars

Set variables/placeholders.

```caddyfile
vars [<matcher>] <name> <value> [...]
```

**Examples:**

```caddyfile
example.com {
    vars base_path /app
    vars cache_control "max-age=3600"
    
    respond "{base_path}"
}
```

---

## abort

Abort the request immediately (return 503).

```caddyfile
abort [<matcher>]
```

**Example:**

```caddyfile
# Block specific paths
@blocked path /admin/* /debug/*
abort @blocked
```

---

## error

Generate an error response.

```caddyfile
error [<matcher>] <status_code> <body|expression>
```

**Example:**

```caddyfile
error 404 "Custom Not Found"
error {http.request.uri.path} /errors/404.html
```

---

## skip_log / log_skip

Skip logging for matched requests.

```caddyfile
skip_log [<matcher>]
log_skip [<matcher>]
```

**Example:**

```caddyfile
# Don't log health check requests
skip_log /health /ready /metrics
```

---

## templates

Render Go templates and markdown files with frontmatter.

```caddyfile
templates [<matcher>] {
    delimiter <open> <close>     # Template delimiters (default {{ }})
    ext       [.ext...]          # File extensions to process
    status    <code>             # Override response status code
}
```

**Example:**

```caddyfile
blog.example.com {
    root * /var/www/blog
    templates
    file_server
}

# Custom delimiters
templates {
    delimiter {% %}
    ext .html .md
}
```

---

## forward_auth

Forward authentication to an external service.

```caddyfile
forward_auth [<matcher>] <address> [{
    uri         <uri>
    method      [GET|POST]
    header      <Field>: <value> [...]
    copy_headers <header...>
    trust_header <header>
    trusted_uri <uri> [...]
}]
```

---

## request_body

Read request body into a variable.

```caddyfile
request_body [<matcher>] <variable_name>
```

**Example:**

```caddyfile
request_body @post body
# {body} now contains the request body
```

---

## import

Import another Caddyfile or snippet.

```caddyfile
import <path|glob_pattern>|snippet <name>
```

**Examples:**

```caddyfile
# Import a file
import /etc/caddy/conf.d/*.conf

# Import with glob pattern
import sites/*.caddyfile

# Import a snippet
(snippet) {
    header X-Frame-Options DENY
}

example.com {
    import snippet
}
```

---

## matchers Reference

### Built-in Matchers

| Matcher | Syntax | Description |
|---------|--------|-------------|
| `method` | `method GET POST` | HTTP method |
| `path` | `path /foo* /bar` | Path matching (supports glob) |
| `header` | `header Content-Type image/*` | Request header matching |
| `host` | `host example.com *.example.com` | Hostname matching |
| `remote` | `remote 10.0.0.0/8 192.168.1.1` | Client IP matching (supports CIDR) |
| `query` | `query key=val key other*` | URL query parameter matching |
| `path_regexp` | `path_regexp name ^/foo/(.*)$` | Path regex matcher |
| `header_regexp` | `header_regexp Name ^value.*` | Header regex matcher |

### Named Matchers

```caddyfile
@get method GET
@static path /static* /assets/*
@api method {GET POST} path /api/*
@secure tls {}  # Requires TLS
```

---

## Response Matchers

| Matcher | Syntax | Description |
|---------|--------|-------------|
| `status` | `status 200 2xx 4xx` | HTTP response status |
| `header` | `header Content-Type text/*` | Response header matching |
| `body` | `body "pattern"` | Response body regex matching |

---

## Shorthand Abbreviations

Caddyfile supports shorthand for common patterns:

```caddyfile
# Instead of:
handle /api/* {
    respond "OK" 200
}

# You can use:
/api/* "OK" 200

# File server shorthand:
/static /var/www/static
```
