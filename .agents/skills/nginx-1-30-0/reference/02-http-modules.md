# HTTP Module Reference

## ngx_http_core_module — Core HTTP Functionality

### `listen [ address : port ] [ parameters ]`
Configures addresses and ports for the virtual server. Parameters (any order, once per address:port):

| Parameter | Description |
|-----------|-------------|
| `default_server` | Makes this the default server for this address:port |
| `ssl` | Enable SSL mode |
| `http2` / `quic` | Enable HTTP/2 or QUIC/HTTP/3 |
| `proxy_protocol` | Accept PROXY protocol headers (v2 supported since 1.13.11) |
| `reuseport` | Create separate listening socket per worker (SO_REUSEPORT, Linux 3.9+) |
| `backlog = number` | listen() backlog queue length |
| `rcvbuf = size` / `sndbuf = size` | Socket buffer sizes |
| `so_keepalive = on \| off \| [keepidle]:[keepintvl]:[keepcnt]` | TCP keepalive settings |
| `ipv6only = on \| off` | IPv6-only socket (default: on) |
| `fastopen = number` | TCP Fast Open, limits SYN queue length |

Port ranges: `listen 12345-12399;`  
UNIX sockets: `listen unix:/var/run/nginx.sock;`  
IPv6: `listen [::]:80;`

### `server { ... }`
Defines a virtual server block. Contains one or more `location` blocks.

### `server_name [ name ... ]`
Virtual server hostnames. Supports wildcards and regex:

```nginx
server_name example.com *.example.com www.example.*;
server_name .example.com;  # wildcard at start
server_name ~^www\d+\.example\.com$;  # regex with ~ prefix
server_name ~^(www\.)?(?<domain>.+)$;  # named capture
```

Matching priority: exact → longest `*` prefix → longest `*` suffix → first regex match.  
Use `_` as catch-all for unmatched requests.

### `location [ = \| ~ \| ~* \| ^~ ] uri { ... }`
Request routing rules. Matching order:
1. `= /uri` — exact match (terminates search)
2. `/prefix/` — longest prefix match
3. `^~ /prefix/` — preferential prefix (no regex check)
4. `~ ^regex$` — case-sensitive regex (first match wins)
5. `~* ^regex$` — case-insensitive regex

```nginx
location = / { /* exact */ }
location / { /* longest prefix for anything starting with / */ }
location ^~ /images/ { /* preferential: no regex check */ }
location ~* \.(gif|jpg|png)$ { /* case-insensitive regex */ }
```

### `root [ path ]`
Sets the document root directory. Path is constructed by adding URI to root value.

```nginx
location /i/ {
    root /data;  # /i/top.gif → /data/i/top.gif
}
```

### `alias [ path ]`
Replaces the matching part of the URI with the alias path (unlike `root` which appends).

### `try_files [ file ... uri ]`
Checks files in order, uses first found. Last parameter is fallback URI or error code.

```nginx
location / {
    try_files $uri $uri/ $uri.html =404;
}

# SPA routing
location / {
    try_files $uri $uri/ /index.html;
}
```

### `index [ file ... ]`
Files to use as index when requesting a directory.

**Default:** `index.html`

### `error_page [ code ... ] [ = response_code ] uri`
Specifies URIs for error responses.

```nginx
error_page 404 /404.html;
error_page 500 502 503 504 /50x.html;
error_page 404 = @fallback;  # internal redirect
location @fallback {
    proxy_pass http://backend;
}
```

### `resolver [ address ... ] [ valid=time ] [ ipv4=on\|off ] [ ipv6=on\|off ]`
DNS resolver for dynamic upstream name resolution.

```nginx
resolver 127.0.0.1 [::1]:5353 valid=30s;
```

### `open_file_cache [ max=N [ inactive=time ]]`
Caches open file descriptors, directory info, and lookup errors.

```nginx
open_file_cache          max=1000 inactive=20s;
open_file_cache_valid    30s;
open_file_cache_min_uses 2;
open_file_cache_errors   on;
```

### Embedded Variables (core)

| Variable | Description |
|----------|-------------|
| `$arg_name` | Request argument `name` |
| `$args` | Query string (same as `$query_string`) |
| `$binary_remote_addr` | Client IP in binary form (4 bytes IPv4, 16 bytes IPv6) |
| `$body_bytes_sent` | Bytes sent excluding headers |
| `$bytes_sent` | Total bytes sent (since 1.3.8) |
| `$connection` | Connection serial number |
| `$connection_requests` | Requests through this connection |
| `$connection_time` | Connection time in seconds with ms resolution |
| `$document_root` | Root/alias for current request |
| `$host` | Host from request line or Host header |
| `$http_name` | Any request header (e.g., `$http_user_agent`) |
| `$https` | `"on"` if SSL, empty otherwise |
| `$is_args` | `"?"` if args present, `""` otherwise |
| `$msec` | Current time in seconds with ms resolution |
| `$nginx_version` | Nginx version string |
| `$pid` | Worker process PID |
| `$proxy_protocol_addr` | Client from PROXY protocol header |
| `$query_string` | Same as `$args` |
| `$remote_addr` | Client IP address |
| `$remote_port` | Client port |
| `$remote_user` | Authenticated user (Basic auth) |
| `$request` | Full original request line |
| `$request_body` | Request body (when in memory buffer) |
| `$request_completion` | `"OK"` if complete, `""` otherwise |
| `$request_filename` | File path for current request |
| `$request_id` | Unique request ID (hex, 1.11.0) |
| `$request_method` | HTTP method |
| `$request_time` | Request processing time (seconds.ms) |
| `$request_uri` | Full original request URI with args |
| `$scheme` | `"http"` or `"https"` |
| `$server_addr` | Server address that accepted the request |
| `$server_name` | Server name that accepted the request |
| `$server_port` | Port of accepting server |
| `$server_protocol` | Request protocol (HTTP/1.0, 1.1, 2.0, 3.0) |
| `$status` | Response status code |
| `$time_iso8601` | Local time in ISO 8601 format |
| `$time_local` | Local time in Common Log Format |
| `$uri` | Normalized current URI |

## ngx_http_proxy_module — HTTP Proxy

### `proxy_pass [ URL ]`
Sets the protocol and address of the proxied server.

```nginx
# With URI replacement
location /name/ {
    proxy_pass http://127.0.0.1/remote/;
}

# Pass original URI unchanged
location /some/path/ {
    proxy_pass http://127.0.0.1;
}

# UNIX domain socket
proxy_pass http://unix:/tmp/backend.socket:/uri/;
```

### `proxy_set_header [ field value ]`
Redefines request headers sent to proxied server. Inherited only if no proxy_set_header at current level.

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

### `proxy_http_version [ 1.0 \| 1.1 \| 2 ]`
HTTP protocol version for proxying. Use `1.1` or `2` with keepalive connections. Default since 1.29.7: `1.1`.

### `proxy_read_timeout [ time ]`
Timeout for reading response from proxied server (between successive reads).

**Default:** `60s`

### `proxy_send_timeout [ time ]`
Timeout for transmitting request to proxied server.

**Default:** `60s`

### `proxy_connect_timeout [ time ]`
Timeout for establishing connection with proxied server.

**Default:** `60s`

### `proxy_next_upstream [ error \| timeout \| denied \| invalid_header \| http_500 \| http_502 \| http_503 \| http_504 \| http_403 \| http_404 \| http_429 \| non_idempotent \| off ]`
Specifies when to pass request to next upstream server.

```nginx
proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
proxy_next_upstream_tries 3;
proxy_next_upstream_timeout 30s;
```

### `proxy_buffer_size [ size ]` and `proxy_buffers [ number size ]`
Buffers for reading response from proxied server.

### `proxy_cache_path [ path ] [ levels=levels ] [ keys_zone=name:size ] [ max_size=size ] [ inactive=time ]`
Defines a shared memory zone and path for proxy cache.

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
```

### `proxy_cache [ zone | off ]`
Enables response caching using the specified shared memory zone.

### `proxy_cache_valid [ code ... ] time`
Sets cache validity for specific response codes.

```nginx
proxy_cache_valid 200 302 10m;
proxy_cache_valid 404 1m;
```

## ngx_http_ssl_module — SSL/TLS Configuration

### `ssl_certificate [ file ]`
PEM format certificate file for this server.

```nginx
ssl_certificate /etc/ssl/certs/example.com.crt;
```

### `ssl_certificate_key [ file ]`
PEM format private key file.

```nginx
ssl_certificate_key /etc/ssl/private/example.com.key;
```

### `ssl_protocols [ SSLv2 \| SSLv3 \| TLSv1 \| TLSv1.1 \| TLSv1.2 \| TLSv1.3 ]`
Enabled SSL/TLS protocols. Default since 1.23.4: `TLSv1.2 TLSv1.3`.

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

### `ssl_ciphers [ ciphers ]`
Enabled ciphers in OpenSSL format.

```nginx
ssl_ciphers HIGH:!aNULL:!MD5:!3DES;
```

### `ssl_prefer_server_ciphers [ on \| off ]`
Prefer server's cipher order over client's.

**Default:** `off`

### `ssl_session_cache [ none \| builtin[:size] \| shared:name:size ]`
SSL session caching between requests.

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
```

### `ssl_session_tickets [ on \| off ]`
Enable/disable TLS session tickets.

### `ssl_stapling [ on \| off ]`
Enable OCSP stapling for certificate validation.

### `ssl_stapling_verify [ on \| off ]`
Verify the OCSP response signature.

## ngx_http_upstream_module — Upstream Groups & Load Balancing

### `upstream [ name ] { ... }`
Defines a group of backend servers.

```nginx
upstream backend {
    server backend1.example.com weight=5;
    server backend2.example.com:8080 max_fails=3 fail_timeout=30s;
    server unix:/tmp/backend3;
    server backup1.example.com:8080 backup;
    server down_server.example.com down;
}
```

**Server parameters:**
| Parameter | Description |
|-----------|-------------|
| `weight = number` | Server weight (default: 1) |
| `max_fails = number` | Unsuccessful attempts before marking unavailable |
| `fail_timeout = time` | Duration of failures + period server is considered unavailable |
| `backup` | Only used when primary servers are down |
| `down` | Permanently unavailable (administrative) |
| `max_conns = number` | Max simultaneous active connections (1.11.5) |
| `resolve` | Monitor DNS changes without restart |

### Load Balancing Methods

```nginx
# Weighted round-robin (default)
upstream backend { server a; server b; }

# Least connections
least_conn;

# IP hash (consistent per client IP)
ip_hash;

# Hash on arbitrary key
hash $request_uri consistent;

# Random selection
random two least_conn;

# Least time (commercial subscription)
least_time header | last_byte [inflight];
```

### `keepalive [ connections ]`
Cache keepalive connections to upstream servers. Since 1.29.7, enabled by default with limit of 32.

```nginx
upstream http_backend {
    server 127.0.0.1:8080;
    keepalive 16;
}

server {
    location /http/ {
        proxy_pass http://http_backend;
        # For versions before 1.29.7:
        # proxy_http_version 1.1;
        # proxy_set_header Connection "";
    }
}
```

### `zone [ name ] [ size ]`
Shared memory zone for upstream state (required for dynamic configuration).

```nginx
upstream backend {
    zone my_backend 64k;
    server backend1.example.com;
}
```

## ngx_http_gzip_module — Compression

### `gzip [ on \| off ]`
Enable/disable gzipping of responses.

**Default:** `off`

### `gzip_comp_level [ 1-9 ]`
Compression level (1 = fastest, 9 = best compression).

**Default:** `1`

### `gzip_min_length [ length ]`
Minimum response length to compress (based on Content-Length header).

**Default:** `20`

### `gzip_types [ mime-type ... ]`
MIME types to compress in addition to `text/html` (which is always compressed).

```nginx
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

Use `*` to match any MIME type.

### `gzip_vary [ on \| off ]`
Add `Vary: Accept-Encoding` header.

**Default:** `off`

### `gzip_proxied [ off \| expired \| no-cache \| no-store \| private \| auth \| any ]`
Compress proxied responses based on request/response headers.

```nginx
gzip_proxied expired no-cache no-store private auth;
```

## ngx_http_rewrite_module — URI Rewriting

### `rewrite [ regex replacement ] [ flag ]`
Changes the request URI using PCRE regular expressions.

**Flags:**
| Flag | Description |
|------|-------------|
| `last` | Stop current rewrite processing, search new location for rewritten URI |
| `break` | Stop current rewrite processing, continue in current location |
| `redirect` | Temporary redirect (302) |
| `permanent` | Permanent redirect (301) |

```nginx
rewrite ^/users/(\d+)/?$ /profile?id=$1 last;
rewrite ^/old-page$ /new-page permanent;
```

### `return [ code [ text ] ]`
Stops processing and returns a response.

```nginx
return 301 https://$host$request_uri;
return 403 "Forbidden";
return 444;  # close connection without response (non-standard)
```

### `if ( condition ) { ... }`
Conditional configuration. Conditions can be:
- Variable name (false if empty or `"0"`)
- Comparison: `= string`, `!= string`
- Regex match: `~ pattern`, `~* pattern`, `!~ pattern`, `!~* pattern`
- File existence: `-f`, `!-f`
- Directory existence: `-d`, `!-d`
- Path exists (file/dir/symlink): `-e`, `!-e`
- Executable: `-x`, `!-x`

```nginx
if ($http_user_agent ~ MSIE) {
    rewrite ^(.*)$ /msie/$1 break;
}
if ($request_method = POST) {
    return 405;
}
if (-f $request_filename) {
    # file exists
}
```

### `break`
Stops processing current set of rewrite directives.

### `set [ $variable value ]`
Sets a variable value (can contain text, variables, and combinations).

```nginx
set $custom_var "hello world";
set $full_url "$scheme://$host$request_uri";
```

## ngx_http_fastcgi_module — FastCGI Proxy

### `fastcgi_pass [ address ]`
Passes request to a FastCGI server.

```nginx
fastcgi_pass 127.0.0.1:9000;
fastcgi_pass unix:/tmp/php-fpm.sock;
```

### `fastcgi_param [ name value ]`
Sets parameters passed to the FastCGI server.

```nginx
fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
fastcgi_param QUERY_STRING $query_string;
fastcgi_param REQUEST_METHOD $request_method;
fastcgi_param CONTENT_TYPE $content_type;
fastcgi_param CONTENT_LENGTH $content_length;
```

### `fastcgi_index [ file ]`
Default FastCGI index file.

### `fastcgi_keep_conn [ on \| off ]`
Keep connection alive with FastCGI server (required for keepalive upstream).

## ngx_http_access_module — Access Control

### `allow [ address \| CIDR \| unix: \| all ]`
Allow access from specified addresses.

```nginx
allow 192.168.1.0/24;
allow 127.0.0.1;
deny all;
```

### `deny [ address \| all ]`
Deny access from specified addresses.

## ngx_http_log_module — Logging

### `access_log [ path [ format [ buffer=size ] [ gzip[=level] ] [ flush=time ] ] ]`
Configure access logging.

```nginx
# Standard combined format
access_log /var/log/nginx/access.log combined;

# Custom format with buffering and compression
log_format compression '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $bytes_sent '
                       '"$http_referer" "$http_user_agent" "$gzip_ratio"';
access_log /spool/logs/nginx-access.log compression buffer=32k;

# Syslog logging
access_log syslog:server=127.0.0.1,facility=local7 combined;

# Conditional logging
map $status $loggable {
    ~^[23]  0;
    default 1;
}
access_log /var/log/nginx/access.log combined if=$loggable;
```

### `log_format [ name [ escape=default\|json\|none ] string ... ]`
Define a custom log format.

```nginx
log_format main '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $body_bytes_sent '
                '"$http_referer" "$http_user_agent"';

log_format json escape=json '{'
    '"time": "$time_iso8601", '
    '"remote_addr": "$remote_addr", '
    '"request": "$request", '
    '"status": $status, '
    '"body_bytes_sent": $body_bytes_sent, '
    '"request_time": $request_time, '
    '"http_referer": "$http_referer", '
    '"http_user_agent": "$http_user_agent"'
'}';

access_log /var/log/nginx/access.log json;
```

### `open_log_file_cache [ max=N [ inactive=time ] [ min_uses=N ] [ valid=time ] ]`
Cache file descriptors for logs with variable names.

```nginx
open_log_file_cache max=1000 inactive=20s valid=1m min_uses=2;
```

## ngx_http_geo_module & ngx_http_map_module — Variable Mapping

### `geo [ $variable address ] { ... }`
Creates variables based on client IP address.

```nginx
geo $remote_addr $is_bot {
    default 0;
    10.0.0.0/8 1;
    192.168.1.100 1;
}
```

### `map [ string variable ] { ... }`
Maps values to other values using exact, prefix, or regex matching.

```nginx
map $http_host $name {
    example.com     alice;
    www.example.com bob;
    ~\.example\.com$ example_user;
}

# Conditional mapping
map $request_method $method_allowed {
    GET     1;
    POST    1;
    default 0;
}
```

## ngx_http_headers_module — Response Headers

### `add_header [ name value [ always ] ]`
Adds a header to the response.

```nginx
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Cache-Control "no-cache" always;
```

The `always` parameter adds the header even for error responses (4xx, 5xx).

## ngx_http_limit_req_module & ngx_http_limit_conn_module — Rate/Connection Limiting

### `limit_req_zone [ variable ] zone=name:size rate=rate`
Defines a shared memory zone for request rate limiting.

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

### `limit_req [ zone ] [ burst=number ] [ nodelay ]`
Applies rate limiting.

```nginx
location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```

### `limit_conn_zone [ variable ] zone=name:size`
Defines a zone for connection limiting.

```nginx
limit_conn_zone $binary_remote_addr zone=addr:10m;
```

### `limit_conn [ zone number ]`
Limits connections per defined key.

```nginx
limit_conn addr 10;
```

## ngx_http_auth_basic_module — Basic Authentication

### `auth_basic [ string \| off ]`
Enables password authentication using HTTP Basic Auth.

```nginx
location /admin/ {
    auth_basic "Restricted Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

Create password file: `openssl passwd -apr1` or use `htpasswd` utility.

## ngx_http_realip_module — Real Client IP

### `set_real_ip_from [ address \| CIDR \| all ]`
Trusted proxy addresses whose headers should be trusted.

```nginx
set_real_ip_from 10.0.0.0/8;
set_real_ip_from unix:;
```

### `real_ip_header [ field ]`
Header containing the real client IP.

```nginx
real_ip_header X-Forwarded-For;
# or
real_ip_header proxy_protocol;
```

### `real_ip_recursive [ on \| off ]`
Recursively search for real IP in X-Forwarded-For chain.

## ngx_http_v2_module — HTTP/2 Support

### `http2 [ on \| off ]`
Enable HTTP/2 protocol for the server (use in `listen` directive).

```nginx
listen 443 ssl http2;
```

HTTP/2 settings:
- `http2_max_requests` — max requests per connection
- `http2_max_concurrent_streams` — max concurrent streams
- `http2_recv_timeout` — timeout for reading HTTP/2 frames

## ngx_http_stub_status_module — Status Page

### Provides basic status information at a location.

```nginx
location /nginx_status {
    stub_status;
    allow 127.0.0.1;
    deny all;
}
```

Output format:
```
Active connections: 1
server accepts handled requests
 1663 1663 5046
Reading: 0 Writing: 1 Waiting: 0
```

## ngx_http_spdy_module — SPDY (Deprecated)

Note: SPDY support was removed in Nginx 1.10.0. Use HTTP/2 instead.
