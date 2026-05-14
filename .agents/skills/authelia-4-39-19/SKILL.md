---
name: authelia-4-39-19
description: Open-source authentication and authorization server providing multi-factor authentication (MFA), single sign-on (SSO), and OpenID Connect 1.0 Provider. Supports LDAP, file-based identity providers, TOTP, WebAuthn, Duo Push, passkeys, fine-grained access control rules, session management via Redis, and proxy integration with NGINX, Traefik, Caddy, Envoy, HAProxy. Use when deploying or configuring Authelia for authentication gateways, SSO portals, MFA enforcement, or OpenID Connect identity provider setups.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - authelia
  - authentication
  - mfa
  - sso
  - openid-connect
  - access-control
  - reverse-proxy
category: security
external_references:
  - https://www.authelia.com/
  - https://github.com/authelia/authelia/tree/v4.39.19
---

# Authelia 4.39.19

## Overview

Authelia is an open-source authentication and authorization server that provides multi-factor authentication (MFA) and single sign-on (SSO) for applications behind a reverse proxy. Written in Go with a React frontend, it operates as a companion to reverse proxies — intercepting authentication requests via the proxy while never touching application payloads directly.

Authelia serves two primary integration modes:

- **Proxy Authorization (Forwarded Authentication)**: The proxy forwards each request to Authelia's `/api/verify` or `/api/authz/*` endpoints. Authelia checks session cookies and returns 200 (allow), 401/302 (redirect to login portal), or 403 (deny) based on access control policies.
- **OpenID Connect 1.0 Provider**: Authelia acts as an OpenID Certified™ identity provider, enabling applications that implement the OIDC Relying Party role to authenticate users through Authelia.

Key characteristics: compressed container under 20 MB, memory usage typically under 30 MB, HTTPS-only operation (HTTP not supported), session cookies for SSO across subdomains.

## When to Use

- Deploying Authelia as an authentication gateway behind a reverse proxy
- Configuring multi-factor authentication (TOTP, WebAuthn, Duo Push, passkeys) for web applications
- Setting up single sign-on (SSO) across multiple domains via session cookies or OpenID Connect
- Writing access control rules to enforce per-domain, per-path, or per-user authentication levels
- Integrating Authelia with Docker, Kubernetes, or bare-metal deployments
- Configuring proxy integrations for NGINX, Traefik, Caddy, Envoy, HAProxy, or Skipper
- Setting up OpenID Connect 1.0 as an identity provider for third-party applications

## Core Concepts

### Architecture

Authelia sits between the reverse proxy and application backends. The proxy sends authentication requests to Authelia; Authelia never sees application payloads. Requests are identified by forwarded headers (`X-Forwarded-Proto`, `X-Forwarded-Host`, `X-Forwarded-For`, `X-Forwarded-URI`).

### Authentication Flow (Proxy Authorization)

1. Unauthenticated request hits the proxy → proxy forwards to Authelia's authz endpoint
2. Authelia checks for a valid session cookie → none found, returns 302 redirect to login portal
3. User authenticates at the Authelia portal (1FA + optional 2FA) → session cookie issued
4. Subsequent requests include the session cookie → proxy forwards it to Authelia → Authelia returns 200 → request passes through

### Authorization Model

Authelia evaluates rules sequentially against each request. A rule matches when all its criteria match: `domain`/`domain_regex`, `resources` (path regex), `subject` (user/group), `networks` (CIDR or named groups), and `methods` (HTTP verbs). The matched rule's `policy` determines the required authentication level:

- **deny** — access denied regardless of authentication state
- **bypass** — no authentication required
- **one_factor** — 1FA sufficient
- **two_factor** — both 1FA and 2FA required

Rules are evaluated in order; first match wins. An unauthenticated user cannot match rules with `subject` criteria.

### Session Cookies

Session cookies enable SSO across configured domains. Each cookie entry specifies a `domain`, `authelia_url`, session duration (`inactivity`, `expiration`, `remember_me`), and `same_site` behavior. For high-availability deployments (Kubernetes), use Redis as the session provider instead of the default in-memory store.

### First Factor / Second Factor

- **First Factor** (something you know): Username + password via LDAP or YAML file backend
- **Second Factor** (something you have): TOTP, WebAuthn (security keys/passkeys), or Duo Push notifications
- **Password Policy**: Enforce minimum strength requirements with configurable criteria
- **Identity Validation**: Email-based verification for users registering 2FA devices; self-service password reset

## Usage Examples

### Minimal Docker Compose Deployment

```yaml
---
services:
  authelia:
    container_name: authelia
    image: docker.io/authelia/authelia:4.39.19
    restart: unless-stopped
    ports:
      - '127.0.0.1:9091:9091'
    volumes:
      - ./config:/config
    environment:
      - AUTHELIA_SESSION_SECRET=<64-char-random-string>
      - AUTHELIA_STORAGE_ENCRYPTION_KEY=<64-char-random-string>
    healthcheck:
      disable: true
...
```

### Basic Configuration (configuration.yml)

```yaml
authentication_backend:
  file:
    path: /config/users_database.yml

session:
  secret: '<64-char-random-string>'
  cookies:
    - domain: example.com
      authelia_url: 'https://auth.example.com'

storage:
  encryption_key: '<64-char-random-string>'
  sqlite:
    path: /config/db.sqlite3

notifier:
  filesystem:
    path: /config/notification.txt

access_control:
  default_policy: deny
  rules:
    - domain: '*.example.com'
      policy: one_factor
    - domain: 'secure.example.com'
      policy: two_factor
```

### NGINX Proxy Integration

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

### Traefik Middleware Integration

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

## Advanced Topics

**Authentication Methods**: First factor (LDAP, File), second factor (TOTP, WebAuthn, Duo Push), password policy, identity validation → [Authentication](reference/01-authentication.md)

**Authorization and Access Control**: Rule-based access control policies, regulation (brute-force protection), trusted header SSO → [Authorization & Access Control](reference/02-authorization-and-access-control.md)

**Configuration Reference**: Configuration methods (files, environment, secrets), session providers, storage backends, notifications, telemetry, definitions → [Configuration Reference](reference/03-configuration-reference.md)

**Deployment and Proxies**: Docker, Kubernetes, bare-metal deployment, proxy integration for NGINX, Traefik, Caddy, Envoy, HAProxy → [Deployment & Proxies](reference/04-deployment-and-proxies.md)

**OpenID Connect 1.0**: Provider configuration, client registration, OAuth 2.0 bearer token usage, claims policies → [OpenID Connect](reference/05-openid-connect.md)
