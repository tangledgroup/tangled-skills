---
name: authentik-2026-5-0
description: Open-source Identity Provider (IdP) for modern SSO supporting OAuth2/OIDC, SAML, LDAP, RADIUS, SCIM, and Proxy protocols. Use when configuring identity management, setting up authentication flows with stages and policies, deploying outposts for reverse-proxy or LDAP services, provisioning users via blueprints, or integrating applications as OAuth2 clients, SAML service providers, or LDAP consumers.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - authentik
  - identity-provider
  - sso
  - oauth2
  - oidc
  - saml
  - ldap
category: tooling
external_references:
  - https://github.com/goauthentik/authentik/tree/version/2026.5.0-rc2
  - https://next.goauthentik.io/developer-docs/
---

# authentik 2026.5.0

## Overview

authentik is an open-source Identity Provider and SSO platform designed for self-hosting from small labs to large production clusters. It supports OAuth2/OIDC, SAML, LDAP, RADIUS, SCIM, Proxy, RAC, SSF, and WS-Federation protocols. The core is a Django application running under gunicorn, proxied by a lightweight Go reverse proxy. Background tasks execute via Dramatiq with PostgreSQL coordination.

authentik 2026.5.0-rc2 uses Python 3.14, Go 1.26+, Node.js 24+, and Rust for tooling. The web frontend is TypeScript with lit-html and PatternFly CSS. It runs on PostgreSQL 14-18.

## When to Use

- Setting up a self-hosted SSO/IdP to replace Okta, Auth0, Entra ID, or Ping Identity
- Configuring authentication flows with custom stages (identification, password, TOTP, WebAuthn, email)
- Deploying OAuth2/OIDC, SAML, LDAP, Proxy, RADIUS, SCIM, or RAC providers for applications
- Managing identity infrastructure-as-code via YAML blueprints
- Connecting external user directories (LDAP/AD, SAML IdP, OAuth social logins, Kerberos)
- Building development environments for authentik contributions
- Integrating with the authentik REST API (1139 endpoints covering stages, sources, providers, flows, policies)

## Core Concepts

**Flows and Stages**: A flow is an ordered sequence of stages. Each stage is a single verification or logic step (identification, password, email, TOTP, WebAuthn, consent, deny, etc.). Flows have designations: Authentication, Authorization, Enrollment, Invalidation, Recovery, Stage Configuration, Unenrollment.

**Applications and Providers**: An application defines what users authenticate into. A provider is the authentication method (OAuth2/OIDC, SAML, LDAP, Proxy, RADIUS, SCIM, etc.). Applications and providers typically have a 1-to-1 relationship.

**Policies**: Reusable yes/no checks bound to flows, stages, applications, or sources. Types include Expression (Python), Event Matcher, GeoIP, Password, Password Expiry, Password Uniqueness (enterprise), and Reputation. Bound via Any/All evaluation mode.

**Blueprints**: YAML files that template and reconcile authentik configuration. Support custom tags (`!KeyOf`, `!Context`, `!Env`, `!File`, `!Find`, `!If`, `!Format`, `!Condition`, `!Enumerate`, `!AtIndex`). Stored as local files, OCI registry packages, or in-database. Applied atomically — full rollback on any error.

**Outposts**: Separate components providing services like reverse proxying (proxy outpost), LDAP server (ldap outpost), or RADIUS server (radius outpost). Deployable via Docker socket auto-discovery, Kubernetes, or manual deployment.

**Sources**: Connect authentik to external user directories. Protocols include LDAP/AD, SAML, OAuth/OIDC social logins, Kerberos, SCIM, and Plex. Sources sync users/groups into authentik for use with providers.

## Usage Examples

### Docker Compose Installation

```bash
wget https://docs.goauthentik.io/compose.yml
echo "PG_PASS=$(openssl rand -base64 36 | tr -d '\n')" >> .env
echo "AUTHENTIK_SECRET_KEY=$(openssl rand -base64 60 | tr -d '\n')" >> .env
docker compose pull
docker compose up -d
```

Access at `http://<server>:9000`, set password for `akadmin` user.

### Creating an OAuth2/OIDC Provider via Blueprint

```yaml
version: 1
metadata:
  name: my-oauth2-app
entries:
  - identifiers:
      slug: my-oauth2-provider
    model: authentik_providers_oauth2.oauth2provider
    attrs:
      name: My OAuth2 Provider
      authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-explicit-consent]]
      invalidation_flow: !Find [authentik_flows.flow, [slug, default-provider-invalidation-flow]]
      client_type: confidential
      client_id: my-client-id
      client_secret: !Env OAUTH2_CLIENT_SECRET
      redirect_uris:
        - https://myapp.example.com/callback
  - identifiers:
      slug: my-oauth2-app
    model: authentik_core.application
    attrs:
      name: My OAuth2 App
      provider: !KeyOf my-oauth2-provider
```

Mount this YAML to `/blueprints/` in the authentik container or push via OCI registry.

### Configuration via Environment Variables

All settings use double-underscore nesting translated to YAML internally. Load from env vars, files, or defaults:

```bash
AUTHENTIK_POSTGRESQL__HOST=postgres
AUTHENTIK_POSTGRESQL__PASSWORD=env://PG_PASS
AUTHENTIK_LISTEN__HTTP=[::]:9000
AUTHENTIK_SECRET_KEY=env://AUTHENTIK_SECRET_KEY
```

Verify with `docker compose run --rm worker ak dump_config`.

## Advanced Topics

**Installation and Configuration**: Docker Compose, Kubernetes/Helm, AWS, environment variables, HA, air-gapped → [Installation and Configuration](reference/01-installation-configuration.md)

**Providers**: OAuth2/OIDC, SAML, LDAP, Proxy, RADIUS, SCIM, RAC, SSF, WS-Fed, Google Workspace, Entra ID → [Providers](reference/02-providers.md)

**Flows, Stages, and Policies**: Flow designations, all stage types, executors, bindings, policy engine → [Flows, Stages, and Policies](reference/03-flows-stages.md)

**Sources**: LDAP/AD, SAML, OAuth social logins, Kerberos, SCIM, property mappings → [Sources](reference/04-sources.md)

**Blueprints**: YAML structure, custom tags, model references, OCI storage, examples → [Blueprints](reference/05-blueprints.md)

**Development**: Full dev environment, frontend-only, debugging, contributing, testing, releasing → [Development](reference/06-development.md)

**API Reference**: OpenAPI 3.0 schema, 1139 endpoints, key resource groups → [API Reference](reference/07-api.md)
