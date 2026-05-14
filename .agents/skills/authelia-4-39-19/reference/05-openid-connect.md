# OpenID Connect 1.0

## Contents
- Overview
- Provider Configuration
  - HMAC Secret and JWKS
  - PKCE and Security Settings
  - Authorization Policies
  - Lifespans
  - Claims Policies
  - Scopes
  - CORS
- Client Configuration
- OAuth 2.0 Bearer Token Usage
- OpenID Connect Claims
- Frequently Asked Questions

## Overview

Authelia supports the OpenID Connect 1.0 Provider role as an open beta feature. Authelia is OpenID Certified™, conforming to the OpenID Connect™ protocol. It does not support the Relying Party role — Authelia cannot use other identity providers for login.

As a Provider, Authelia issues ID tokens, access tokens, and refresh tokens to registered client applications. Applications implementing the OIDC Relying Party role (e.g., Grafana, Nextcloud, Gitea, Bitwarden) can authenticate users through Authelia.

**Key distinction**: Proxy Authorization access control rules do not apply to OpenID Connect. OIDC has its own separate `authorization_policies` configuration within the OIDC provider settings.

## Provider Configuration

### HMAC Secret and JWKS

```yaml
identity_providers:
  oidc:
    hmac_secret: '{{ .AUTHELIA_OIDC_HMAC_SECRET }}'
    jwks:
      - key_id: 'default'
        algorithm: 'RS256'
        use: 'sig'
        key: |
          -----BEGIN PRIVATE KEY-----
          ...
          -----END PRIVATE KEY-----
        certificate_chain: |
          -----BEGIN CERTIFICATE-----
          ...
          -----END CERTIFICATE-----
```

- `hmac_secret` — signs JWTs. Hashed to SHA256. Use 64+ character random string via secret file.
- `jwks` — list of JSON Web Keys. At least one RSA private key with RS256 algorithm required. Supports additional key types: RS384, RS512, ES256, ES384, ES512, PS256, PS384, PS512, EdDSA.
- First key of each algorithm type is the default for clients without explicit `key_id`.

### PKCE and Security Settings

```yaml
    enable_client_debug_messages: false
    minimum_parameter_entropy: 8
    enforce_pkce: 'public_clients_only'
    enable_pkce_plain_challenge: false
    enable_jwt_access_token_stateless_introspection: false
    discovery_signed_response_alg: 'none'
    require_pushed_authorization_requests: false
```

- `enforce_pkce` — `all_clients`, `public_clients_only`, or `none`. PKCE protects public clients (SPAs, mobile apps) from authorization code interception. Use `public_clients_only` as default.
- `minimum_parameter_entropy` — minimum Shannon entropy for client secrets.
- `enable_jwt_access_token_stateless_introspection` — enables JWT-based introspection endpoint without database lookup.

### Authorization Policies

OIDC-specific authorization policies separate from proxy access control:

```yaml
    authorization_policies:
      default:
        default_policy: 'two_factor'
        rules:
          - policy: 'deny'
            subject: 'group:services'
            networks:
              - '192.168.1.0/24'
```

- Policies follow the same structure as proxy access control (deny, bypass, one_factor, two_factor).
- Applied during OIDC authorization flows to determine required authentication level.
- `default_policy` applies when no rules match.

### Lifespans

```yaml
    lifespans:
      access_token: '1h'
      authorize_code: '1m'
      id_token: '1h'
      refresh_token: '90m'
      device_code: '5m'
```

- `access_token` — lifetime of access tokens (default 1h).
- `authorize_code` — authorization code validity window (default 1m).
- `id_token` — ID token lifetime (default 1h).
- `refresh_token` — refresh token lifetime (default 90m). Can be extended via rotation.
- `device_code` — device authorization code lifetime for Device Flow (default 5m).

### Claims Policies

Control which claims appear in tokens per policy name:

```yaml
    claims_policies:
      default:
        id_token: []
        access_token: []
        id_token_audience_mode: 'specification'
        custom_claims:
          groups:
            name: 'groups'
            attribute: 'groups'
```

- `id_token` / `access_token` — lists of claims to include/exclude. Empty means use defaults (standard OIDC claims).
- `id_token_audience_mode` — `specification` (client_id only) or `extend` (add additional audiences).
- `custom_claims` — map LDAP/user attributes to token claims. Reference user attribute names from the authentication backend configuration.

### Scopes

Define custom scopes with associated claims:

```yaml
    scopes:
      profile:
        claims:
          - name
          - family_name
          - given_name
          - email
      custom_scope:
        claims:
          - groups
```

### CORS

```yaml
    cors:
      endpoints:
        - 'authorization'
        - 'token'
        - 'revocation'
        - 'introspection'
      allowed_origins:
        - 'https://example.com'
      allowed_origins_from_client_redirect_uris: false
```

- `endpoints` — which OIDC endpoints allow CORS preflight.
- `allowed_origins` — explicit list of allowed origins.
- `allowed_origins_from_client_redirect_uris` — auto-derive allowed origins from registered client redirect URIs.

## Client Configuration

Register each client application with Authelia:

```yaml
    clients:
      - client_id: 'grafana'
        client_name: 'Grafana'
        policy: 'default'
        token_endpoint_auth_method: 'client_secret_basic'
        grant_types:
          - 'refresh_token'
          - 'authorization_code'
        redirect_uris:
          - 'https://grafana.example.com/login/gauthelia'
        response_modes:
          - 'form_post'
        response_types:
          - 'code'
        scopes:
          - 'openid'
          - 'profile'
          - 'email'
        subject_identifier:
          algorithm: 'pairwise'
          salt: 'random_salt_string'
```

| Option | Description |
|--------|-------------|
| `client_id` | Unique identifier for the client. Sent by the application during OIDC flows. |
| `client_secret` | Secret for confidential clients. Use secret files. |
| `token_endpoint_auth_method` | `client_secret_basic`, `client_secret_post`, or `none` (public clients). |
| `grant_types` | Allowed grants: `authorization_code`, `refresh_token`, `client_credentials`, `urn:ietf:params:oauth:grant-type:device_code`. |
| `redirect_uris` | Allowed callback URLs. Must be exact match (no wildcards). |
| `response_types` | `code` (authorization code flow), `id_token token` (implicit, not recommended). |
| `scopes` | Scopes the client is allowed to request. |
| `subject_identifier.algorithm` | `pairwise` (opaque, per-client) or `preconfigured` (consistent across clients). |

**Public vs Confidential Clients**: Public clients (SPAs, mobile apps) use `token_endpoint_auth_method: 'none'` and require PKCE. Confidential clients (server-side apps) use `client_secret_basic` or `client_secret_post`.

## OAuth 2.0 Bearer Token Usage

Applications can use Authelia-issued access tokens to authenticate API requests:

- Include the token in the `Authorization: Bearer <token>` header.
- Authelia validates the token signature and expiration.
- For stateless introspection, enable `enable_jwt_access_token_stateless_introspection` — allows validating tokens without database queries.
- The `/introspection` endpoint accepts active access tokens and returns their claims for validation by resource servers.

## OpenID Connect Claims

Standard claims available in ID tokens:

| Claim | Source | Description |
|-------|--------|-------------|
| `sub` | Internal | Unique subject identifier (pairwise or preconfigured) |
| `email` | LDAP/File | User's email address |
| `email_verified` | Internal | Always true for Authelia-authenticated users |
| `name` | LDAP/File | Display name |
| `given_name` | LDAP | First name |
| `family_name` | LDAP | Last name |
| `groups` | LDAP/File | Group memberships (requires scope) |
| `preferred_username` | LDAP/File | Username |

Custom claims are mapped via `claims_policies` and `scopes` configuration. LDAP attributes are pulled from the authentication backend's `attributes` mapping.

## Frequently Asked Questions

**Why doesn't access control configuration work with OpenID Connect 1.0?**
Proxy access control rules apply only to Proxy Authorization flows. OIDC uses separate `authorization_policies` within the OIDC provider configuration. Configure OIDC policies under `identity_providers.oidc.authorization_policies`.

**What authentication flows are supported?**
Authorization Code Flow (recommended), Implicit Flow (not recommended), Device Authorization Grant, and Client Credentials Grant for service-to-service authentication.

**How do I handle multiple client applications?**
Register each application as a separate client under `identity_providers.oidc.clients`. Each gets its own `client_id`, `client_secret`, `redirect_uris`, and scope permissions.
