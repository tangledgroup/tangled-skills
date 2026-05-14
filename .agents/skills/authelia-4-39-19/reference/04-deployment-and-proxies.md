# Deployment and Proxies

## Contents
- Docker Deployment
  - Container Environment Variables
  - Permission Context
  - Docker Compose Examples
- Kubernetes Deployment
- Bare-Metal Deployment
- Proxy Integration
  - Required Headers
  - Response Statuses
  - NGINX
  - Traefik
  - Caddy
  - Envoy
  - HAProxy
- Forwarded Headers Security

## Docker Deployment

### Container Environment Variables

These are container-specific and do not affect the Authelia daemon:

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 0 | Drop privileges to this UID if running as root. |
| `PGID` | 0 | Drop privileges to this GID if running as root. |
| `UMASK` | N/A | Set umask for the container process. |

### Permission Context

Three methods to control filesystem permissions:

1. **Recommended**: Run container as non-root user via Docker's `user` directive. Process never has privileged access; manually set filesystem permissions.
2. **PUID/PGID**: Container entrypoint drops privileges after setting ownership. Entrypoint runs as root briefly.
3. **User namespace remapping**: Beyond Authelia's documentation scope.

### Docker Compose Examples

**Standalone with secrets volume:**

```yaml
---
services:
  authelia:
    container_name: authelia
    image: docker.io/authelia/authelia:4.39.19
    restart: unless-stopped
    networks:
      net:
        aliases: []
    environment:
      AUTHELIA_IDENTITY_VALIDATION_RESET_PASSWORD_JWT_SECRET_FILE: '/secrets/JWT_SECRET'
      AUTHELIA_SESSION_SECRET_FILE: '/secrets/SESSION_SECRET'
      AUTHELIA_STORAGE_POSTGRES_PASSWORD_FILE: '/secrets/STORAGE_PASSWORD'
      AUTHELIA_STORAGE_ENCRYPTION_KEY_FILE: '/secrets/STORAGE_ENCRYPTION_KEY'
    volumes:
      - '${PWD}/data/authelia/config:/config'
      - '${PWD}/data/authelia/secrets:/secrets'
networks:
  net:
    external: true
    name: 'net'
...
```

**With host proxy access:** Add `ports: ['127.0.0.1:9091:9091']` to allow the host's reverse proxy to reach Authelia.

**Bundles**: Authelia provides pre-configured Docker Compose bundles:
- **lite**: Authelia + Traefik + SQLite + file-based users. Clone repo, edit `users_database.yml`, `configuration.yml`, and `compose.yml`.
- **local**: Full local demo with self-signed certificates. Run `./setup.sh` to configure `/etc/hosts`.

**Debugging**: Run interactively:
```bash
docker exec -it authelia sh
authelia
```

Or use a debug compose overlay with `AUTHELIA_LOG_LEVEL: 'trace'` and `command: 'sleep 3300'`.

## Kubernetes Deployment

Authelia provides an official Helm chart for Kubernetes deployment.

**Key considerations:**
- Use Redis (not memory) for session storage in HA scenarios.
- All replicas share the same Redis session store and database.
- Secrets should be managed via Kubernetes Secrets, not embedded in values.
- The chart supports Traefik Ingress, NGINX Ingress, Envoy Gateway, and Istio integrations.

**Chart configuration highlights:**
- `session.redis` — enable for HA deployments
- `storage.postgres` — recommended over SQLite for K8s
- `notifier.smtp` — configure external SMTP
- `accessControl` — define rules via chart values
- OIDC provider settings configurable through chart values

**Ingress patterns**: The chart supports Traefik IngressRoute, NGINX Ingress, and Envoy Gateway configurations. Each pattern routes protected subdomains through Authelia's authz endpoint for authorization before reaching backends.

## Bare-Metal Deployment

Download the binary from GitHub releases or build from source.

```bash
authelia --config /etc/authelia/configuration.yml
```

- Binary is a single static Go executable — no runtime dependencies beyond the OS.
- Run as a systemd service with `User=authelia` and `Group=authelia`.
- Bind to `127.0.0.1:9091` when the proxy runs on the same host.
- Ensure the config directory is owned by the authelia user.

## Proxy Integration

Authelia works with reverse proxies via the Proxy Authorization pattern. The proxy sends each request to Authelia's authz endpoint; Authelia returns a status code and optional headers.

### Required Headers

The proxy must include these headers when forwarding requests to Authelia:

| Header | Purpose | Fallback |
|--------|---------|----------|
| `X-Forwarded-Proto` | Scheme detection (http/https) | TLS socket state |
| `X-Forwarded-Host` | Host detection | `Host` header |
| `X-Forwarded-For` | Client IP for access control and regulation | TCP source IP |
| `X-Forwarded-URI` | Request path for resource matching | Start line request target |
| `X-Forwarded-Method` or `X-Original-Method` | HTTP method for rule matching | — |

Without these headers, Authelia cannot properly evaluate access control rules, identify session domains, or generate correct redirect URLs.

### Response Statuses

| Status | Meaning |
|--------|---------|
| 200 OK | User authenticated and authorized. Includes `Remote-User`, `Remote-Email`, `Remote-Name`, `Remote-Groups` headers for SSO. |
| 302 Found | Redirect to login portal (GET/OPTIONS requests). |
| 303 See Other | Redirect to login portal (non-GET requests). |
| 401 Unauthorized | Redirect to login portal (XMLHttpRequest/AJAX). |
| 403 Forbidden | Access denied by policy. No redirect — user cannot authenticate their way out of a deny rule. |

### NGINX

```nginx
server {
    listen 443 ssl;
    server_name app.example.com;

    location / {
        auth_request /authelia;
        proxy_pass http://backend;
    }

    location = /authelia {
        internal;
        proxy_pass http://127.0.0.1:9091/api/verify;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Uri $request_uri;
        proxy_set_header X-Forwarded-Method $request_method;
    }
}
```

For the newer `/api/authz` endpoint, use `proxy_pass http://127.0.0.1:9091/api/authz/$host$request_uri?`.

### Traefik

**v2 ForwardAuth middleware:**

```yaml
http:
  middlewares:
    authelia:
      forwardAuth:
        address: 'http://127.0.0.1:9091/api/authz'
        trustForwardHeader: true
        authResponseHeaders:
          - Remote-User
          - Remote-Groups
          - Remote-Name
```

**Kubernetes IngressRoute:**

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: authelia-forward-auth
spec:
  forwardAuth:
    address: 'http://authelia.default.svc.cluster.local:9091/api/authz'
    trustForwardHeader: true
    authResponseHeaders:
      - Remote-User
      - Remote-Groups
```

### Caddy

```caddyfile
app.example.com {
    reverse_proxy backend:8080 {
        trusted_proxies private_ranges
    }

    authenticate {
        auth_url http://127.0.0.1:9091/api/authz
        copy_request_header X-Forwarded-Proto, X-Forwarded-Host, X-Forwarded-For, X-Forwarded-Uri
    }
}
```

Or with the `caddy-authelia` plugin for native integration.

### Envoy

```yaml
http_filters:
  - name: envoy.filters.http.ext_authz
    typed_config:
      "@type": types.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
      grpc_service:
        google_grpc:
          target_uri: authelia:9091
          stat_prefix: authelia
      transport_api_version: V3
```

Envoy Gateway and Istio integrations are supported via the Kubernetes chart.

### HAProxy

```haproxy
backend authelia
    server authelia 127.0.0.1:9091

http-request use-service authelia if { path_beg /api/authz }
http-request return status 403 content-type text/plain lf-string "Access denied" if !authelia{ ssc,STR(2) } -m str OK
```

## Forwarded Headers Security

Authelia provides a `/api/verify` and `/api/authz/*` endpoint that trusts forwarded headers. Protect these endpoints so only your reverse proxy can reach them:

- Bind Authelia to `127.0.0.1:9091` (bare-metal) or use internal-only networks (Docker/K8s).
- Never expose Authelia's port directly to the internet.
- Configure the proxy to strip incoming `X-Forwarded-*` headers from clients before forwarding to Authelia, preventing header spoofing.
- Review the Forwarded Headers documentation for implementation-specific hardening guidance.
