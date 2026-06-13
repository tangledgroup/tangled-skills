# Access Control and Rate Limiting

## IP-Based Access Control

The `ngx_http_access_module` allows or denies access by IP:

```nginx
location /admin/ {
    deny  192.168.1.1;
    allow 192.168.1.0/24;
    allow 10.1.1.0/16;
    allow 2001:0db8::/32;
    deny  all;
}
```

Rules are processed in order — the first matching rule applies. `all` matches any address including UNIX-domain sockets.

## Basic Authentication

```nginx
location /admin/ {
    auth_basic "Restricted Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

Generate password files with `htpasswd` (from Apache tools) or OpenSSL:

```bash
printf 'user:%s\n' "$(openssl passwd -apr1)" >> /etc/nginx/.htpasswd
```

## JWT Authentication

The `ngx_http_auth_jwt_module` validates JSON Web Tokens:

```nginx
location /api/ {
    auth_jwt "API" token=$cookie_token;
    auth_jwt_key_file /etc/nginx/jwtRS256.key;
}
```

Supports RSA, ECDSA, and HMAC algorithms. Can use remote JWK endpoint with `auth_jwt_key_request`.

## Auth Request Subrequest

Delegate authentication to a subrequest:

```nginx
location /protected/ {
    auth_request /auth;
    proxy_pass http://backend;
}

location = /auth {
    internal;
    proxy_pass http://auth_service$request_uri;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
}
```

The subrequest returns 2xx for access granted, anything else denies.

## satisfy Directive

Control whether all or any access methods must pass:

```nginx
location / {
    satisfy all;   # default — both IP and auth must pass
    allow 10.0.0.0/8;
    auth_basic "closed";
    auth_basic_user_file /etc/nginx/.htpasswd;
}

location / {
    satisfy any;   # either IP match OR valid credentials
    allow 10.0.0.0/8;
    auth_basic "closed";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

## Rate Limiting — limit_req_zone

Define rate limits in the `http` context using shared memory zones:

```nginx
http {
    # 10MB zone, 1 request per second per client IP
    limit_req_zone $binary_remote_addr zone=per_ip:10m rate=1r/s;

    # Per-server rate limit
    limit_req_zone $server_name zone=per_server:10m rate=10r/s;
}
```

The `$binary_remote_addr` variable is more memory-efficient than `$remote_addr` (4 bytes vs 7-40 bytes per IP).

## Rate Limiting — limit_req

Apply limits in `server` or `location` context:

```nginx
server {
    # Allow bursts of 5 requests, delay excess
    limit_req zone=per_ip burst=5;

    # Allow bursts without delay
    limit_req zone=per_ip burst=5 nodelay;
}
```

Without `nodelay`, excess requests are delayed to conform to the rate. With `nodelay`, they are processed immediately (up to burst size). Requests exceeding burst receive 503.

Multiple zones can be applied:

```nginx
location /api/ {
    limit_req zone=per_ip burst=5 nodelay;
    limit_req zone=per_server burst=20;
}
```

## Rate Limiting Status and Logging

```nginx
limit_req_status 429;           # return 429 instead of 503
limit_req_log_level warn;       # log level for rejected requests (default: error)
limit_req_dry_run on;           # evaluate but don't enforce
```

## Connection Limiting — limit_conn_zone / limit_conn

Limit concurrent connections per key:

```nginx
http {
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    limit_conn_zone $server_name zone=server:10m;
}

server {
    limit_conn addr 10;    # max 10 connections per IP
    limit_conn server 100; # max 100 connections per server
}
```

## Geo-based Rate Limiting

Combine `geo` with rate limiting for different limits per region:

```nginx
geo $limit_key {
    default $binary_remote_addr;
    10.0.0.0/8 "";   # internal IPs — no limit
}

limit_req_zone $limit_key zone=api:10m rate=5r/s;
```

## limit_except

Restrict allowed HTTP methods:

```nginx
location /files/ {
    limit_except GET HEAD {
        allow 10.0.0.0/8;
        deny all;
    }
}
```

Only GET and HEAD are open to everyone; other methods require matching the access rules inside the block.
