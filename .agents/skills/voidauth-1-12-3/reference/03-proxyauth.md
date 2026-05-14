# ProxyAuth

## Contents
- ProxyAuth Domains and Matching
- User Identification Flow
- Authorization and Security Groups
- Trusted Header SSO
- Reverse Proxy Configurations (Caddy, NGINX, Traefik)

## ProxyAuth Domains and Matching

ProxyAuth Domains are configured on the VoidAuth Admin ProxyAuth Domains page. Each entry defines a domain/path pattern and which security groups may access it.

Matching is evaluated from **most specific to least specific**. A user's access is checked against the first matching domain. Trailing `/` and separators like `.` are strictly checked — access to `*.example.com` does not grant access to `example.com`; they must be added separately.

A wildcard ProxyAuth Domain `*/*` covers any domain not matched by other entries.

> If no group is assigned to a ProxyAuth Domain, **any signed-in user** has access.

## User Identification Flow

When a request hits a protected domain, the reverse proxy checks with VoidAuth. VoidAuth identifies the user using three methods, tried in order:

1. **Session cookie** in `x-voidauth-session` header — standard browser flow
2. **Proxy-Authorization** header (Basic Auth) — returns 407 if invalid
3. **Authorization** header (Basic Auth) — returns 401 if invalid

## Authorization and Security Groups

On successful identification, VoidAuth checks the user's security groups against the ProxyAuth Domain's allowed groups. Response codes:

- `200` — User identified and authorized
- `401` / `407` / `302` — User not identified (includes `Location` header pointing to VoidAuth login)
- `403` — User identified but denied access

## Trusted Header SSO

On allowed requests, VoidAuth sets these response headers for the reverse proxy to forward to the backend app:

| Header | Value |
|--------|-------|
| `Remote-User` | Username |
| `Remote-Email` | Email address |
| `Remote-Name` | Display name |
| `Remote-Groups` | Comma-separated groups (e.g., `users,admins,owners`) |

This enables Trusted Header SSO on self-hosted applications that support it.

## Reverse Proxy Configurations

VoidAuth exposes two proxy auth endpoints:

| Endpoint | Compatible Proxies |
|----------|-------------------|
| `/api/authz/forward-auth` | Caddy, Traefik |
| `/api/authz/auth-request` | NGINX |

### Caddy

```caddy
# Serve VoidAuth
auth.example.com {
  reverse_proxy voidauth:3000
}

# Serve protected app
app.example.com {
  forward_auth voidauth:3000 {
    uri /api/authz/forward-auth
    copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
  }

  reverse_proxy app:8080
}
```

### NGINX

Requires config snippets mounted at `/config/nginx/snippets/`.

**proxy.conf**:
```nginx
proxy_set_header Host $host;
proxy_set_header X-Original-URL $scheme://$http_host$request_uri;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $http_host;
proxy_set_header X-Forwarded-URI $request_uri;
proxy_set_header X-Forwarded-For $remote_addr;
```

**auth-location.conf**:
```nginx
location /api/authz/auth-request {
  internal;
  include /config/nginx/snippets/proxy.conf;
  proxy_set_header Content-Length "";
  proxy_set_header Connection "";
  proxy_pass_request_body off;
  proxy_pass http://voidauth:3000/api/authz/auth-request;
}
```

**proxy-auth.conf**:
```nginx
auth_request /api/authz/auth-request;
auth_request_set $user $upstream_http_remote_user;
auth_request_set $groups $upstream_http_remote_groups;
auth_request_set $name $upstream_http_remote_name;
auth_request_set $email $upstream_http_remote_email;
proxy_set_header Remote-User $user;
proxy_set_header Remote-Groups $groups;
proxy_set_header Remote-Name $name;
proxy_set_header Remote-Email $email;
auth_request_set $redirection_url $upstream_http_location;
error_page 401 =302 $redirection_url;
error_page 407 =302 $redirection_url;
```

**Full server block**:
```nginx
server {
    listen 443 ssl http2;
    server_name app.example.com;

    include /config/nginx/snippets/auth-location.conf;

    location / {
      include /config/nginx/snippets/proxy.conf;
      include /config/nginx/snippets/proxy-auth.conf;
      proxy_pass http://app:8080;
    }
}
```

### NGINX Proxy Manager

Use the same NGINX snippets. In the Advanced tab for a protected app proxy host:

```nginx
include /config/nginx/snippets/auth-location.conf;

location / {
  include /config/nginx/snippets/proxy.conf;
  include /config/nginx/snippets/proxy-auth.conf;
  proxy_pass $forward_scheme://$server:$port;
}
```

### Traefik

Configure VoidAuth as a ForwardAuth middleware via docker labels:

```yaml
services:
  voidauth:
    image: voidauth/voidauth:latest
    labels:
      traefik.enable: "true"
      traefik.http.routers.voidauth.rule: "Host(`auth.example.com`)"
      traefik.http.middlewares.voidauth.forwardAuth.address: "http://voidauth:3000/api/authz/forward-auth"
      traefik.http.middlewares.voidauth.forwardAuth.trustForwardHeader: "true"
      traefik.http.middlewares.voidauth.forwardAuth.authResponseHeaders: "Remote-User,Remote-Name,Remote-Email,Remote-Groups"

  whoami:
    image: traefik/whoami
    labels:
      traefik.enable: "true"
      traefik.http.routers.whoami.rule: "Host(`whoami.example.com`)"
      traefik.http.routers.whoami.middlewares: "voidauth@docker"
```

Apply the `voidauth@docker` middleware to any protected service's router.
