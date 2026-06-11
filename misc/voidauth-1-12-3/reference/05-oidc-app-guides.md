# OIDC App Guides

## Contents
- Setup Notes
- Actual Budget
- Arcane
- AutoCaliWeb
- Beszel
- ByteStash
- Cloudflare ZeroTrust
- Dawarich
- Dockhand
- Grist
- Immich
- Jellyfin
- Jellyseerr
- Komodo
- Manyfold
- Mastodon
- Memos
- Open WebUI
- Pangolin
- Paperless-ngx
- Portainer
- Proxmox PVE
- Seafile
- Unraid
- Vaultwarden
- WikiJS

## Setup Notes

Client IDs must be unique between OIDC Apps. Client Secrets must be long and randomly generated — use the generate button on the OIDC App page. Endpoint URLs should always be copied from the VoidAuth OIDC Info dropdown, not constructed manually. Placeholders: `your-client-id`, `your-client-secret`, `Copy from VoidAuth OIDC Info`.

## Actual Budget

```bash
ACTUAL_OPENID_DISCOVERY_URL="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
ACTUAL_OPENID_CLIENT_ID="your-client-id"
ACTUAL_OPENID_CLIENT_SECRET="your-client-secret"
ACTUAL_OPENID_SERVER_HOSTNAME="https://actual.example.com"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://actual.example.com/openid/callback`

## Arcane

```bash
OIDC_ENABLED="true"
OIDC_CLIENT_ID="your-client-id"
OIDC_CLIENT_SECRET="your-client-secret"
OIDC_ISSUER_URL="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
OIDC_SCOPES="openid email profile groups"
OIDC_ADMIN_CLAIM="groups"
OIDC_ADMIN_VALUE="your-admin-role"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://arcane.example.com/auth/oidc/callback`

## AutoCaliWeb

In Settings > Configuration > Edit Basic Configuration > Feature Configuration, set Login Type to `Use OAuth`, select Generic.

```
generic OAuth Client Id: your-client-id
generic OAuth Client Secret: your-client-secret
generic OAuth scope: openid profile email
generic OAuth Metadata URL: Copy from VoidAuth OIDC Info (Well-Known Endpoint)
generic OAuth Username mapper: preferred_username
generic OAuth Email mapper: email
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://autocaliweb.example.com/login/generic/authorized`

## Beszel

Follow the Beszel OAuth Guide, select `OpenID Connect (oidc)`.

```
Client ID: your-client-id
Client Secret: your-client-secret
Auth URL: Copy from VoidAuth OIDC Info (Authorization Endpoint)
Token URL: Copy from VoidAuth OIDC Info (Token Endpoint)
User info URL: Copy from VoidAuth OIDC Info (UserInfo Endpoint)
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://beszel.example.com/api/oauth2-redirect`

## ByteStash

```bash
OIDC_ENABLED="true"
OIDC_DISPLAY_NAME="VoidAuth"
OIDC_ISSUER_URL="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
OIDC_CLIENT_ID="your-client-id"
OIDC_CLIENT_SECRET="your-client-secret"
OIDC_SCOPES="openid profile email groups"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://bytestash.example.com/api/auth/callback`

## Cloudflare ZeroTrust

In Cloudflare ZeroTrust Dashboard > Settings > Authentication > Login methods, add OpenID Connect.

```
App ID: your-client-id
Client secret: your-client-secret
Auth URL: Copy from VoidAuth OIDC Info (Authorization Endpoint)
Token URL: Copy from VoidAuth OIDC Info (Token Endpoint)
Certificate URL: Copy from VoidAuth OIDC Info (JWKs Endpoint)
PKCE: ON
OIDC Claims: mail, preferred_username
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://your-team-name.cloudflareaccess.com/cdn-cgi/access/callback`

## Dawarich

```bash
OIDC_CLIENT_ID="your-client-id"
OIDC_CLIENT_SECRET="your-client-secret"
OIDC_ISSUER="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
OIDC_REDIRECT_URI="https://dawarich.example.com/users/auth/openid_connect/callback"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://dawarich.example.com/users/auth/openid_connect/callback`

## Dockhand

In Settings > Authentication > SSO, add provider. See Dockhand OIDC Configuration Guide for details.

```
Issuer URL: Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)
Client ID: your-client-id
Client Secret: your-client-secret
Scopes: openid profile email groups
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://dockhand.example.com/api/auth/oidc/callback`

## Grist

```bash
GRIST_OIDC_IDP_ISSUER="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
GRIST_OIDC_IDP_CLIENT_ID="your-client-id"
GRIST_OIDC_IDP_CLIENT_SECRET="your-client-secret"
GRIST_OIDC_SP_IGNORE_EMAIL_VERIFIED="true"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://grist.example.com/oauth2/callback`, PostLogout: `https://grist.example.com/signed-out`

## Immich

In Administration > Settings > OAuth Settings. See Immich OAuth Documentation for details.

```
Issuer URL: Copy from VoidAuth OIDC Info (Well-Known Endpoint)
Client ID: your-client-id
Client Secret: your-client-secret
Scope: openid profile email
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirects: `https://immich.example.com/auth/login`, `https://immich.example.com/user-settings`, `app.immich:///oauth-callback`

## Jellyfin

Install the Jellyfin SSO Plugin from catalog (repository: `https://raw.githubusercontent.com/9p4/jellyfin-plugin-sso/manifest-release/manifest.json`). In Dashboard > Plugins > SSO-Auth:

```
OID Endpoint: Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)
OpenID Client ID: your-client-id
OID Secret: your-client-secret
Request Additional Scopes: groups
Set default username claim: preferred_username
Scheme Override: https
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://jellyfin.example.com/sso/OID/redirect/VoidAuth`

## Jellyseerr

> OIDC support is experimental, available in preview image only: `fallenbagel/jellyseerr:preview-OIDC`.

In Settings > OpenID Connect section:

```
Issuer URL: Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)
Client ID: your-client-id
Client Secret: your-client-secret
Scopes: openid profile email groups
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://jellyseerr.example.com/login?provider=voidauth&callback=true`

## Komodo

```bash
KOMODO_OIDC_ENABLED=true
KOMODO_OIDC_PROVIDER="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
KOMODO_OIDC_CLIENT_ID="your-client-id"
KOMODO_OIDC_CLIENT_SECRET="your-client-secret"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://komodo.example.com/auth/oidc/callback`

> Temporarily set `KOMODO_DISABLE_USER_REGISTRATION=false` for initial OIDC login, then revert to `true`.

## Manyfold

```bash
MULTIUSER="true"
OIDC_CLIENT_ID="your-client-id"
OIDC_CLIENT_SECRET="your-client-secret"
OIDC_ISSUER="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://manyfold.example.com/users/auth/openid_connect/callback`

## Mastodon

```bash
OIDC_ENABLED="true"
OIDC_DISCOVERY="true"
OIDC_ISSUER="Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)"
OIDC_CLIENT_ID="your-client-id"
OIDC_CLIENT_SECRET="your-client-secret"
OIDC_SCOPE="openid,profile,email"
OIDC_UID_FIELD="preferred_username"
OIDC_REDIRECT_URI="https://mastodon.example.com/auth/auth/openid_connect/callback"
OIDC_SECURITY_ASSUME_EMAIL_IS_VERIFIED="true"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://mastodon.example.com/auth/auth/openid_connect/callback`

## Memos

In Settings > SSO > Create > Custom template:

```
Authorization endpoint: Copy from VoidAuth OIDC Info (Authorization Endpoint)
Token endpoint: Copy from VoidAuth OIDC Info (Token Endpoint)
User endpoint: Copy from VoidAuth OIDC Info (UserInfo Endpoint)
Scopes: openid profile email offline_access
Identifier: preferred_username
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://memos.example.com/auth/callback`

> Scopes are separated by spaces, not commas.

## Open WebUI

```bash
OAUTH_CLIENT_ID="your-client-id"
OAUTH_CLIENT_SECRET="your-client-secret"
OPENID_PROVIDER_URL="Copy from VoidAuth OIDC Info (Well-Known Endpoint)"
OAUTH_SCOPES="openid profile groups email"
ENABLE_OAUTH_ROLE_MANAGEMENT="true"
OAUTH_ROLES_CLAIM="groups"
OAUTH_ALLOWED_ROLES="users,admins"
OAUTH_ADMIN_ROLES="admins"
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://openwebui.example.com/oauth/oidc/callback`

## Pangolin

Follow the Pangolin OAuth/OIDC Guide.

```
Client ID: your-client-id
Client Secret: your-client-secret
Auth URL: Copy from VoidAuth OIDC Info (Authorization Endpoint)
Token URL: Copy from VoidAuth OIDC Info (Token Endpoint)
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://pangolin.example.com/auth/idp/1/oidc/callback`

> Callback path may vary if multiple OIDC providers are configured.

## Paperless-ngx

```bash
PAPERLESS_APPS="allauth.socialaccount.providers.openid_connect"
PAPERLESS_SOCIALACCOUNT_PROVIDERS='{"openid_connect": {"OAUTH_PKCE_ENABLED": true, "APPS": [{"provider_id": "voidauth", "name": "VoidAuth", "client_id": "your-client-id", "secret": "your-client-secret", "settings": {"fetch_userinfo": true, "server_url": "https://voidauth.example.com/oidc", "token_auth_method": "client_secret_basic"}}]}}'
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://paperless.example.com/accounts/oidc/voidauth/login/callback/`

## Portainer

In Settings > Authenticate, select OAuth > Custom provider:

```
Authorization URL: Copy from VoidAuth OIDC Info (Authorization Endpoint)
Access token URL: Copy from VoidAuth OIDC Info (Token Endpoint)
Resource URL: Copy from VoidAuth OIDC Info (UserInfo Endpoint)
User identifier: preferred_username
Scopes: openid profile groups email
Auth Style: In Params
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://portainer.example.com`

## Proxmox PVE

In Datacenter > Permissions > Realms > Add > OpenID Connect Server:

```
Issuer URL: Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)
Client ID: your-client-id
Client Key: your-client-secret
Scopes: email profile
Username Claim: preferred_username
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://pve.example.com`

## Seafile

In `seahub_settings.py`:

```python
ENABLE_OAUTH = True
OAUTH_CLIENT_ID = "your-client-id"
OAUTH_CLIENT_SECRET = "your-client-secret"
OAUTH_AUTHORIZATION_URL = "https://voidauth.example.com/oidc/auth"
OAUTH_TOKEN_URL = "https://voidauth.example.com/oidc/token"
OAUTH_USER_INFO_URL = "https://voidauth.example.com/oidc/me"
OAUTH_SCOPE = ["openid", "profile", "email"]
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Basic`, Redirect: `https://seafile.example.com/oauth/callback/`

## Unraid

In Settings > Management Access > Unraid API Settings, add OIDC provider:

```
Provider ID: voidauth
Client ID: your-client-id
Client Secret: your-client-secret
Issuer URL: Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)
OAuth Scopes: openid profile email
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://unraid.example.com/graphql/api/auth/oidc/callback`

## Vaultwarden

In Admin Panel > OpenID Connect SSO settings:

```
Client ID: your-client-id
Client Key: your-client-secret
Authority Server: Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)
Authorization request scopes: email profile
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://vaultwarden.example.com/identity/connect/oidc-signin`

## WikiJS

In Configuration Panel > Authentication, create Generic OpenID Connect / OAuth 2 strategy:

```
Authorization Endpoint URL: Copy from VoidAuth OIDC Info (Authorization Endpoint)
Token Endpoint URL: Copy from VoidAuth OIDC Info (Token Endpoint)
User Info Endpoint URL: Copy from VoidAuth OIDC Info (UserInfo Endpoint)
Issuer: Copy from VoidAuth OIDC Info (OIDC Issuer Endpoint)
Email Claim: email
Display Name Claim: name
Groups Claim: groups
Logout URL: Copy from VoidAuth OIDC Info (Logout Endpoint)
```

**VoidAuth OIDC App**: Auth Method: `Client Secret Post`, Redirect: `https://wikijs.example.com/login/{token-from-wikijs-strategy}/callback`
