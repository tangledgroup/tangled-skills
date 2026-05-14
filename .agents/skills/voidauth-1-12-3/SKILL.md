---
name: voidauth-1-12-3
description: Open-source SSO authentication and user management provider for self-hosted applications. Provides OIDC Provider, ProxyAuth forward authentication, user/group management, passkeys, and email-based invitations. Use when deploying or configuring VoidAuth as an identity provider, setting up OIDC integrations with self-hosted apps, securing domains via ProxyAuth behind Caddy/NGINX/Traefik reverse proxies, managing users and security groups, or troubleshooting authentication flows.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - voidauth
  - sso
  - oidc
  - authentication
  - selfhosted
  - proxy-auth
  - identity-provider
category: tooling
external_references:
  - https://voidauth.app/#/
  - https://github.com/voidauth/voidauth/tree/v1.12.3
---

# VoidAuth 1.12.3

## Overview

VoidAuth is an open-source Single Sign-On (SSO) authentication and user management provider designed for self-hosted application ecosystems. It operates as an OpenID Connect (OIDC) Provider and a ProxyAuth forward-authentication gateway, sitting between a reverse proxy and protected applications. Built on Node.js with TypeScript, it runs as a Docker container with Postgres or SQLite backend support.

Key capabilities include OIDC provider functionality for apps that support standard OAuth2/OIDC flows, ProxyAuth for securing any domain or path regardless of app support, user and group management via web UI, passkey and MFA authentication, email-based invitations and self-registration, and full branding customization.

## When to Use

- Deploying a centralized identity provider for a self-hosted application stack
- Configuring OIDC integrations between VoidAuth and client applications (Immich, Jellyfin, Portainer, Vaultwarden, etc.)
- Setting up ProxyAuth to secure domains/paths behind Caddy, NGINX, or Traefik reverse proxies
- Managing users, security groups, and access control across multiple self-hosted services
- Configuring environment variables, Docker Compose setups, or database migrations for VoidAuth
- Troubleshooting authentication issues (session cookies, redirect URIs, X-Forwarded-* headers)

## Core Concepts

**OIDC Provider**: VoidAuth acts as an OpenID Connect identity provider. Client applications register as OIDC Apps with a Client ID, Client Secret, and Redirect URLs. VoidAuth exposes standard OIDC endpoints (authorization, token, userinfo, jwks, logout) discoverable via the well-known endpoint. Auth methods include `client_secret_basic`, `client_secret_post`, and `none` (PKCE).

**ProxyAuth**: For applications without native OIDC support, ProxyAuth intercepts requests at the reverse proxy level. The reverse proxy forwards auth checks to VoidAuth (`/api/authz/forward-auth` for Caddy/Traefik, `/api/authz/auth-request` for NGINX). On successful authentication, VoidAuth sets trusted headers (`Remote-User`, `Remote-Email`, `Remote-Name`, `Remote-Groups`) that the reverse proxy passes to the backend app.

**Security Groups**: Groups control access to both OIDC Apps and ProxyAuth Domains. The special `auth_admins` group grants full administrative access. Groups can enforce MFA requirements and auto-assign on new invitations. If no group is assigned to a ProxyAuth Domain, any signed-in user has access.

**User Management**: Users are created exclusively through invitations (admin-created) or self-registration (if `SIGNUP=true`). Invited users choose their own password upon acceptance. Self-registration can require admin approval via `SIGNUP_REQUIRES_APPROVAL`.

## Quick Start

Deploy VoidAuth with Docker Compose using a Postgres database:

```yaml
services:
  voidauth:
    image: voidauth/voidauth:latest
    restart: unless-stopped
    volumes:
      - ./voidauth/config:/app/config
    environment:
      APP_URL: "https://auth.example.com"    # required — full external URL
      STORAGE_KEY: ""                         # required — 32+ char random key
      DB_PASSWORD: ""                         # required — match POSTGRES_PASSWORD below
      DB_HOST: voidauth-db                    # required
    depends_on:
      voidauth-db:
        condition: service_healthy

  voidauth-db:
    image: postgres:18
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ""                   # required — match DB_PASSWORD above
    volumes:
      - ./voidauth/db:/var/lib/postgresql/18/docker
    healthcheck:
      test: "pg_isready -U postgres -h localhost"
```

After `docker compose up -d`, retrieve the initial admin password reset link from logs:

```bash
docker compose logs voidauth
```

Visit the link to set a password for the default `auth_admin` user, then create your own user account and add it to the `auth_admins` group.

> VoidAuth does not terminate HTTPS itself — place it behind a reverse proxy with TLS (Caddy, NGINX, Traefik).

## Advanced Topics

**Getting Started**: Full setup guide, environment variables, Docker Compose variants, branding → [Getting Started](reference/01-getting-started.md)

**OIDC Setup**: OIDC App creation, declared apps via env vars/docker labels, endpoint discovery → [OIDC Setup](reference/02-oidc-setup.md)

**ProxyAuth**: Domain authorization, reverse proxy configurations (Caddy, NGINX, Traefik), trusted header SSO → [ProxyAuth](reference/03-proxyauth.md)

**User Management**: Invitations, self-registration, security groups, password resets → [User Management](reference/04-user-management.md)

**OIDC App Guides**: Community-maintained integration guides for 25+ self-hosted applications → [OIDC App Guides](reference/05-oidc-app-guides.md)

**Advanced Topics**: CLI commands, database migration, email templates, troubleshooting → [Advanced Topics](reference/06-advanced-topics.md)
