# Getting Started

## Contents
- Docker Compose Setup (Postgres)
- Docker Compose Setup (SQLite)
- Initial Admin Setup
- Required Environment Variables
- Optional Environment Variables
- Config Directory and Branding
- Multi-Domain Protection (Experimental)

## Docker Compose Setup (Postgres)

VoidAuth runs exclusively via Docker. The recommended setup uses Postgres 18:

```yaml
services:
  voidauth:
    image: voidauth/voidauth:latest
    restart: unless-stopped
    volumes:
      - ./voidauth/config:/app/config
    environment:
      APP_URL: "https://auth.example.com"
      STORAGE_KEY: ""                          # 32+ random characters
      DB_PASSWORD: ""                           # match POSTGRES_PASSWORD below
      DB_HOST: voidauth-db
    depends_on:
      voidauth-db:
        condition: service_healthy

  voidauth-db:
    image: postgres:18
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ""                     # match DB_PASSWORD above
    volumes:
      - ./voidauth/db:/var/lib/postgresql/18/docker
    healthcheck:
      test: "pg_isready -U postgres -h localhost"
```

Mount `/var/run/docker.sock` read-only if using Declared OIDC Apps via docker labels.

VoidAuth does not terminate HTTPS — place it behind a reverse proxy with TLS.

## Docker Compose Setup (SQLite)

For simpler deployments, use SQLite with a mounted volume:

```yaml
services:
  voidauth:
    image: voidauth/voidauth:latest
    restart: unless-stopped
    volumes:
      - ./voidauth/config:/app/config
      - ./voidauth/db:/app/db
    environment:
      APP_URL: "https://auth.example.com"
      STORAGE_KEY: ""
      DB_ADAPTER: sqlite
```

## Initial Admin Setup

On first start, VoidAuth prints a password reset link for the initial `auth_admin` user in logs:

```bash
docker compose logs voidauth
```

Open the link, set a password, then sign in as `auth_admin`. After login, either change the default username or create an invitation for yourself and add your new user to the `auth_admins` group. Any user in `auth_admins` is a full administrator.

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `APP_URL` | Full external URL of VoidAuth (e.g., `https://auth.example.com` or `https://example.com/auth`). Must match how users access the service. |
| `STORAGE_KEY` | Storage encryption key for secrets (client secrets, keys). Minimum 32 characters, randomly generated. |
| `DB_HOST` | Postgres host address (required unless using SQLite). |
| `DB_PASSWORD` | Postgres password (required unless using SQLite; must match `POSTGRES_PASSWORD` in the DB service). |

## Optional Environment Variables

### App Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_DOMAIN` | Base domain of `APP_URL` | Cookie domain. Must be equal to or higher level than `APP_URL`. |
| `DEFAULT_REDIRECT` | `APP_URL` | Landing URL after invitation acceptance, logout, or logo click. |
| `SIGNUP` | `false` | Allow self-registration without invitation. |
| `SIGNUP_REQUIRES_APPROVAL` | `true` | Require admin approval for self-registered users. With `SIGNUP=true` and this `false`, enables open registration. |
| `EMAIL_VERIFICATION` | `true` if SMTP_HOST set | Users must verify email before use. |
| `MFA_REQUIRED` | `false` | Force all users to use a second factor (authenticator token or passkey). |
| `API_RATELIMIT` | `60` | Mutating requests per minute per IP. |
| `ENABLE_DEBUG` | `false` | Debug logging (prints user activity — do not use in production). |

### App Customization

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_TITLE` | `VoidAuth` | Display title on web interface. |
| `APP_PORT` | `3000` | Listen port (also accepts unix socket path). |
| `APP_COLOR` | `#906bc7` | Theme color in RGB hex format. |
| `APP_FONT` | `monospace` | Font family (use safe fonts; fallback format supported). |
| `CONTACT_EMAIL` | | Email shown on 'Contact' links across end-user pages. |

### Database Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_ADAPTER` | `postgres` | `postgres` or `sqlite`. |
| `DB_PORT` | `5432` | Postgres port. |
| `DB_USER` | `postgres` | Postgres username. |
| `DB_NAME` | `postgres` | Database name. |
| `DB_SSL` | `false` | Enable SSL to database. |
| `DB_SSL_VERIFICATION` | `true` | Verify SSL certificate when DB_SSL enabled. |

### SMTP Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | | SMTP server host. |
| `SMTP_FROM` | | Sender email address (name populated from `APP_TITLE`). |
| `SMTP_PORT` | `587` | SMTP port. |
| `SMTP_SECURE` | `false` | TLS/SSL enabled on SMTP connection. |
| `SMTP_USER` | | SMTP username. |
| `SMTP_PASS` | | SMTP password. |
| `SMTP_IGNORE_CERT` | `false` | Ignore invalid/self-signed SMTP certificates. |

### Misc

| Variable | Default | Description |
|----------|---------|-------------|
| `PASSWORD_STRENGTH` | `3` | Minimum password strength (0-4, 3+ recommended). |
| `ADMIN_EMAILS` | `hourly` | Minimum interval between admin notification emails. Set to `false` to disable. Accepts human-readable durations (`4 hours`, `daily`, `weekly`) or seconds. |
| `DEFAULT_USER_EXPIRES_IN` | | Default expiration duration for new user invitations (e.g., `1 week`, `2 days`). |

### Database Migration Settings

Mirror of `DB_*` variables describing the target database during migration:

`MIGRATE_TO_DB_ADAPTER`, `MIGRATE_TO_DB_HOST`, `MIGRATE_TO_DB_PASSWORD`, `MIGRATE_TO_DB_PORT`, `MIGRATE_TO_DB_USER`, `MIGRATE_TO_DB_NAME`, `MIGRATE_TO_DB_SSL`, `MIGRATE_TO_DB_SSL_VERIFICATION`.

### Storage Key Rotation

| Variable | Description |
|----------|-------------|
| `STORAGE_KEY_SECONDARY` | Secondary encryption key for rotating the primary `STORAGE_KEY`. Set both during rotation. |

## Config Directory and Branding

Mount `/app/config` to customize branding and email templates:

- **Logo**: Place `logo.svg`/`logo.png` in `/app/config/branding/`
- **Favicon**: Place `favicon.svg`/`favicon.png` in `/app/config/branding/`
- **Apple Touch Icon**: Place `apple-touch-icon.png` in `/app/config/branding/`
- **Email Templates**: Customize ejs templates in `/app/config/email_templates/` (see Advanced Topics reference)

These options, combined with `APP_TITLE`, `APP_COLOR`, and `APP_FONT`, allow complete removal of VoidAuth branding from the user-facing interface.

## Multi-Domain Protection (Experimental)

Run multiple VoidAuth instances sharing the same database to protect multiple domains. Each instance uses the same `STORAGE_KEY` and `DB_*` variables but different `APP_URL` values covering different domains. All instances share users, OIDC Apps, and ProxyAuth Domains from the common database.

Example: `https://auth.example.com` for example.com services and `https://id.your-domain.net` for your-domain.net services, both backed by one database.
