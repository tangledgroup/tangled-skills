# OIDC Setup

## Contents
- Creating OIDC Apps via Web UI
- OIDC Provider Endpoints
- Declared OIDC Apps (Environment Variables)
- Declared OIDC Apps (Docker Labels)
- Configurable Fields

## Creating OIDC Apps via Web UI

Create new OIDC Apps from the admin OIDC page. Each app needs:

- **Client ID**: Unique identifier for the client application
- **Client Secret**: Long, randomly generated secret (use the generate button on the OIDC App page)
- **Redirect URLs**: Callback URL(s) where VoidAuth redirects after authentication. Supports wildcards — use with caution and follow the client app's documentation.
- **PostLogout URL**: URL to redirect to after logout

Optional settings on the OIDC App page:
- **Display Name** / **Logo URL**: Shown during consent screen
- **Groups**: Restrict access to specific security groups
- **Skip Consent**: Skip the consent prompt for this app
- **MFA Required**: Force MFA for this specific app

When a configuration property is omitted from an OIDC App Guide, the default value works. Follow the client application's OIDC setup guide parameters exactly — mismatches cause integration failures.

## OIDC Provider Endpoints

At the top of the OIDC Apps page, a dropdown panel shows VoidAuth's OIDC endpoint URLs that client applications need during their setup. These include:

- **Issuer Endpoint**: Base URL for OIDC discovery
- **Well-Known Endpoint**: OpenID Connect discovery document
- **Authorization Endpoint**: OAuth2 authorization request
- **Token Endpoint**: Token exchange
- **UserInfo Endpoint**: User profile information
- **JWKs Endpoint**: JSON Web Key Set for token verification
- **Logout Endpoint**: RP-initiated logout

Always copy endpoint URLs from this dropdown rather than constructing them manually.

## Declared OIDC Apps (Environment Variables)

OIDC Apps can be declared via environment variables instead of the web UI. Declared apps are stored in memory and take priority over web-configured apps with the same client ID.

**Naming**: Client IDs must not contain `_` when using environment variables.

```bash
OIDC_<client-id>_CLIENT_SECRET="1234"
OIDC_<client-id>_CLIENT_REDIRECT_URLS="https://example.com, https://test.example.com"
OIDC_<client-id>_CLIENT_AUTH_METHOD="client_secret_post"
```

## Declared OIDC Apps (Docker Labels)

OIDC Apps can be declared via docker labels. Client IDs must not contain `.` when using docker labels. The client ID is inferred from the container name.

```yaml
labels:
  voidauth.enable: "true"
  voidauth.oidc.<client-id>.client_secret: "1234"
  voidauth.oidc.<client-id>.client_redirect_urls: "https://example.com, https://test.example.com"
```

VoidAuth watches docker containers on the same host and updates its configuration as containers start, stop, and restart. This requires mounting `/var/run/docker.sock` read-only.

## Configurable Fields

All configurable fields for OIDC Apps (web UI, env vars, or docker labels):

| Variable | Default | Possible Values |
|----------|---------|-----------------|
| `CLIENT_DISPLAY_NAME` | | Display name shown to users |
| `CLIENT_HOMEPAGE_URL` | | Application homepage URL |
| `CLIENT_LOGO_URL` | | Logo URL shown during consent |
| `CLIENT_SECRET` | | Randomly generated secret |
| `CLIENT_AUTH_METHOD` | `client_secret_basic` | `client_secret_basic`, `client_secret_post`, `none` |
| `CLIENT_GROUPS` | | Comma-separated security group names |
| `CLIENT_REDIRECT_URLS` | | Comma-separated redirect URLs |
| `CLIENT_RESPONSE_TYPES` | `code` | `code`, `id_token`, `token`, `none` |
| `CLIENT_GRANT_TYPES` | `authorization_code, refresh_token` | `authorization_code`, `implicit`, `refresh_token` |
| `CLIENT_POST_LOGOUT_URLS` | | Comma-separated post-logout redirect URLs |
| `CLIENT_SKIP_CONSENT` | `false` | `true`, `false` |
