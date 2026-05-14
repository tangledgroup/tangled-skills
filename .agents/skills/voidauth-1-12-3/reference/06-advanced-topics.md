# Advanced Topics

## Contents
- CLI Commands
- Database Migration
- Email Templates
- Troubleshooting

## CLI Commands

Run CLI commands via `docker compose run voidauth <command> [options]` from the directory containing the compose file.

### Serve

```bash
voidauth serve
```

Default command — starts the VoidAuth application. Runs automatically when no arguments are supplied.

### Migrate

```bash
voidauth migrate
```

Migrates all data from the current database (`DB_*` variables) to the target database (`MIGRATE_TO_DB_*` variables). See Database Migration section for full procedure.

### Generate Password Reset

```bash
voidauth generate password-reset [username]
```

Generates a password reset link for an existing user. Username can be positional or via flag:

```bash
voidauth generate password-reset example_user
voidauth generate password-reset --username example_user
```

## Database Migration

Migrate VoidAuth to a new database (e.g., SQLite → Postgres, or changing Postgres hosts). The migration is non-destructive to the source database but **is destructive** to the target database.

### Procedure

1. Stop existing VoidAuth instances: `docker compose rm -s voidauth`
2. Ensure the target database exists (Postgres) or can be created (SQLite)
3. Set `MIGRATE_TO_DB_*` environment variables with the target database connection details (same format as `DB_*` variables)
4. Run migration: `docker compose run voidauth migrate`
5. Wait for success message: `Database migration complete...`
6. Update `DB_*` environment variables to match the `MIGRATE_TO_DB_*` values used during migration
7. Remove `MIGRATE_TO_DB_*` variables (not used outside of migration)
8. Start VoidAuth: `docker compose up -d voidauth`

### Migration Environment Variables

| Variable | Description |
|----------|-------------|
| `MIGRATE_TO_DB_ADAPTER` | `postgres` or `sqlite` |
| `MIGRATE_TO_DB_HOST` | Target database host (required for Postgres) |
| `MIGRATE_TO_DB_PASSWORD` | Target database password |
| `MIGRATE_TO_DB_PORT` | Target database port (default: 5432) |
| `MIGRATE_TO_DB_USER` | Target database username (default: postgres) |
| `MIGRATE_TO_DB_NAME` | Target database name (default: postgres) |
| `MIGRATE_TO_DB_SSL` | Enable SSL to target database |
| `MIGRATE_TO_DB_SSL_VERIFICATION` | Verify SSL certificate on target |

## Email Templates

VoidAuth emails use EJS templates located in `/app/config/email_templates/`. On each start, default templates (`*.default.ejs`) are copied into place. Each email type has three files:

- `subject.default.ejs` — Email subject line
- `html.default.ejs` — HTML body
- `text.default.ejs` — Plain text body

Email types: `invitation`, `email_verification`, `reset_password`, `approved`, `admin_notification`, `test_notification`.

### Customizing Templates

1. Rename the template by removing the `.default` suffix (e.g., `html.default.ejs` → `html.ejs`)
2. Edit the renamed file

> Modified templates **must** have the `.default` suffix removed. All `*.default.ejs` files are overwritten with current defaults on every start. The renamed `*.ejs` file takes precedence over its `*.default.ejs` counterpart.

Templates use EJS syntax. Available variables for each template type are shown in the default templates and can be reused in custom versions.

## Troubleshooting

### Initial Admin Reset Link Not Working

**Link Expired**: If more than one day has passed since first start, generate a new reset link:

```bash
docker compose run voidauth generate password-reset auth_admin
```

Alternatively, remove or reset the database and start over.

### Could Not Create Session

The `x-voidauth-session` or `x-voidauth-interaction` cookies could not be set. Verify:
- `APP_URL` is set to the public URL of VoidAuth and matches how users access it
- `SESSION_DOMAIN` is valid — browsers block cookies on top-level domains (`com`, `co.uk`, `lan`) and some public domains (`azurewebsites.net`, `cdn.cloudflare.net`). Check the [Public Suffix List](https://publicsuffix.org/list/).

### Invalid Client

Ensure an OIDC App exists and the `Client ID` in VoidAuth matches exactly what the client application expects.

### Invalid Redirect Uri

The client application must specify the correct Redirect URL matching what is configured in VoidAuth. Check the app's OIDC documentation or the OIDC App Guides for the expected callback path.

### The Page Cannot Be Found (During OIDC Auth)

An OIDC endpoint URL was likely entered incorrectly during the client app's setup. Verify all endpoint URLs were copied from the VoidAuth OIDC Info dropdown on the admin OIDC Apps page.

### Not Redirected After Login (ProxyAuth)

Incorrect `X-Forwarded-*` headers reaching VoidAuth from the reverse proxy. Check that the reverse proxy is forwarding `X-Forwarded-Proto`, `X-Forwarded-Host`, and `X-Forwarded-URI` correctly. See ProxyAuth reference for correct configurations.

### IP Address Incorrect or Missing in Logs

Misconfigured trusted IP settings in the reverse proxy. Check the reverse proxy documentation for trusted proxy/IP forwarding configuration.

### OIDC Endpoints Show Wrong Protocol (http vs https)

An intermediate proxy is not setting `X-Forwarded-Proto` or VoidAuth does not trust the upstream proxy that set it. Some reverse proxies set this automatically; others require manual configuration. In NGINX, ensure `proxy_set_header X-Forwarded-Proto $scheme;` is present in the proxy snippet for VoidAuth.
