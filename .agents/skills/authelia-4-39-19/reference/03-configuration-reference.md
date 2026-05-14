# Configuration Reference

## Contents
- Configuration Methods
  - File-Based Configuration
  - Environment Variables
  - Secrets
- Session Configuration
  - Providers (Memory, Redis)
  - Cookie Configuration
- Storage Backends
  - SQLite3
  - PostgreSQL
  - MySQL
- Notifications
  - SMTP
  - File System
- Telemetry and Metrics
- Definitions
  - Networks
  - User Attributes
- Miscellaneous
  - Server
  - Logging
  - NTP

## Configuration Methods

Authelia supports three ways to supply configuration values, used together in practice.

### File-Based Configuration

Primary YAML file (typically `/config/configuration.yml`). Authelia validates the configuration on startup — check for unknown keys, deprecated options, and type mismatches. Validate manually:

```bash
authelia config validate --config configuration.yml
# Docker
docker run authelia/authelia:latest authelia config validate --config /config/configuration.yml
```

### Environment Variables

Override any YAML configuration value using environment variables with the prefix `AUTHELIA_`. The path is derived from the YAML key hierarchy, uppercased and joined with underscores.

```bash
# Overrides session.secret in YAML
AUTHELIA_SESSION_SECRET=my_secret_value

# Overrides storage.postgres.address
AUTHELIA_STORAGE_POSTGRES_ADDRESS=postgres://authelia:password@db:5432/authelia
```

Environment variables take precedence over file values. Use for non-sensitive overrides and container-specific settings.

### Secrets

For sensitive values (passwords, encryption keys), use secret files referenced via environment variables with the `_FILE` suffix:

```bash
AUTHELIA_SESSION_SECRET_FILE=/secrets/SESSION_SECRET
AUTHELIA_STORAGE_ENCRYPTION_KEY_FILE=/secrets/STORAGE_ENCRYPTION_KEY
AUTHELIA_IDENTITY_VALIDATION_RESET_PASSWORD_JWT_SECRET_FILE=/secrets/JWT_SECRET
```

In YAML, reference secrets using the template syntax:

```yaml
session:
  secret: '{{ .AUTHELIA_SESSION_SECRET }}'
```

Authelia reads the file at startup and substitutes the value. This is the recommended approach for all sensitive values in containerized deployments.

## Session Configuration

Session cookies enable SSO across configured domains. Two providers available.

### Providers (Memory, Redis)

**Memory** (default): Stateful, no additional configuration. Not suitable for high-availability or Kubernetes deployments where multiple replicas exist.

**Redis**: Stateless, recommended for production and HA deployments.

```yaml
session:
  secret: '{{ .AUTHELIA_SESSION_SECRET }}'
  name: 'authelia_session'
  same_site: 'lax'
  inactivity: '5m'
  expiration: '1h'
  remember_me: '1M'
  redis:
    host: 'redis'
    port: 6379
    # Optional: password, tls, max_idle_connections, etc.
```

**Redis Sentinel** is also supported for high availability by specifying `sentinel_hosts` and `master_name` instead of `host`.

### Cookie Configuration

The `cookies` list defines per-domain session settings. Domains not listed are denied.

```yaml
session:
  cookies:
    - domain: 'example.com'
      authelia_url: 'https://auth.example.com'
      default_redirection_url: 'https://www.example.com'
      name: 'authelia_session'
      same_site: 'lax'
      inactivity: '5m'
      expiration: '1h'
      remember_me: '1d'
```

| Option | Required | Description |
|--------|----------|-------------|
| `domain` | Yes | Domain the session cookie protects. Must match Authelia's serving domain or its root. Cannot be a Public Suffix List domain (e.g., `duckdns.org`). |
| `authelia_url` | Yes | HTTPS URL of Authelia for this domain. Used for generating redirect URLs during authentication. |
| `default_redirection_url` | No | Where to redirect when visiting Authelia directly. |
| `name` | No | Cookie name (default: `authelia_session`). |
| `same_site` | No | `lax`, `strict`, or `none`. Default `lax`. Use `none` with `secure: true` for cross-site scenarios. |
| `inactivity` | No | Session expires after this duration of no activity (default 5m). |
| `expiration` | No | Absolute session lifetime (default 1h). |
| `remember_me` | No | Extended duration when "Remember Me" is selected (default 1M = 1 month). |

## Storage Backends

Authelia requires a database for storing second-factor registrations, session data (if not using Redis), and regulation state. Choose one backend.

### SQLite3

Recommended for testing and small deployments. Single-file database, no external service required.

```yaml
storage:
  encryption_key: '{{ .AUTHELIA_STORAGE_ENCRYPTION_KEY }}'
  sqlite:
    path: '/config/db.sqlite3'
    wal_auto_vacuum: false
    wal_checkpoint_interval: '60m'
    driver_options: ''
```

- `wal_auto_vacuum` — enable automatic WAL vacuuming.
- `wal_checkpoint_interval` — how often to checkpoint WAL to main database.

### PostgreSQL

Recommended for production deployments. Supports high availability and external managed databases.

```yaml
storage:
  encryption_key: '{{ .AUTHELIA_STORAGE_ENCRYPTION_KEY }}'
  postgres:
    username: 'authelia'
    password: '{{ .AUTHELIA_STORAGE_POSTGRES_PASSWORD }}'
    address: 'db'
    port: 5432
    database: 'authelia'
    schema: 'public'
    ssl:
      mode: 'disable'
      # certificate, private_key, server_name for TLS
    driver_options: ''
```

- Migrations are applied automatically on startup.
- `ssl.mode` — `disable`, `require`, `verify-ca`, or `verify-full`.

### MySQL

Alternative production backend.

```yaml
storage:
  encryption_key: '{{ .AUTHELIA_STORAGE_ENCRYPTION_KEY }}'
  mysql:
    username: 'authelia'
    password: '{{ .AUTHELIA_STORAGE_MYSQL_PASSWORD }}'
    address: 'db'
    port: 3306
    database: 'authelia'
    ssl:
      mode: 'disable'
    driver_options: ''
```

## Notifications

Required for 2FA registration emails, identity validation, and password reset. Configure one notifier.

### SMTP

```yaml
notifier:
  smtp:
    username: 'authelia'
    password: '{{ .AUTHELIA_NOTIFIER_SMTP_PASSWORD }}'
    host: 'mail.example.com'
    port: 587
    timeout: '5s'
    sender: 'Authelia <noreply@example.com>'
    subject: '[Authelia] {title}'
    identification_timeout: '15m'
    starttls_policy: ' Opportunistic'
    tls:
      server_name: 'mail.example.com'
      skip_verify: false
      minimum_version: 'TLS1.2'
      maximum_version: 'TLS1.3'
```

- `starttls_policy` — `Opportunistic` (default, upgrade if server supports it), `Always` (require STARTTLS), or `Never` (no encryption, not recommended).
- `subject` — template with `{title}` placeholder replaced by the message context.
- `identification_timeout` — how long SMTP authentication is cached.

### File System

For testing only. Emails are written to a local file instead of sent.

```yaml
notifier:
  filesystem:
    path: '/config/notification.txt'
    template_path: ''
    mode: '0600'
```

## Telemetry and Metrics

Prometheus-compatible metrics endpoint at `/metrics`.

```yaml
telemetry:
  metrics:
    enable: false
    address: '0.0.0.0:9092'
    metrics_path: '/metrics'
    authz_metrics: false
    bucket_divisor: 10
```

- `enable` — expose the metrics endpoint.
- `address` — bind address for the metrics server.
- `authz_metrics` — include per-domain authorization request counts (higher cardinality).
- `bucket_divisor` — controls histogram bucket granularity. Lower = more detailed but higher memory.

## Definitions

### Networks

Named network groups referenced by access control rules:

```yaml
networks:
  - name: 'internal'
    networks:
      - '10.10.0.0/16'
      - '192.168.2.0/24'
  - name: 'external'
    networks:
      - '192.0.2.0/24'
```

Reference in rules: `networks: ['internal']`.

### User Attributes

Map user attributes for display and OIDC claims:

```yaml
default_organization: 'Example Inc.'
```

## Miscellaneous

### Server

```yaml
server:
  address: '0.0.0.0:9091'
  endpoints:
    authz:
      enable: true
      path: '/api/authz'
    verify:
      enable: true
      path: '/api/verify'
```

- `address` — bind address and port. Use `0.0.0.0:9091` for containerized deployments, `127.0.0.1:9091` for bare-metal with local proxy.
- `endpoints.authz.enable` — enable the newer `/api/authz/*` endpoint (recommended over `/api/verify`).
- When using a subpath (e.g., `address: 'authelia'`), the handler listens on both root and configured path.

### Logging

```yaml
log:
  level: 'info'
  format: 'text'
  file:
    path: '/config/authelia.log'
    compress: false
    max_size: '10M'
    max_age: '30d'
    max_backups: 10
```

- `level` — `trace`, `debug`, `info`, `warn`, `error`, `fatal`.
- `format` — `text` or `json`.
- File logging is optional; omit the `file` section for stdout only.

### NTP

Authelia validates system clock drift. TOTP and OIDC tokens are time-sensitive.

```yaml
ntp:
  address: 'time.google.com:123'
  timeout: '10s'
  version: 3
  max_poll_interval: '6h'
  min_poll_interval: '4m'
  disable_start_up: false
  disable_failure: false
```

- `disable_start_up` — skip NTP check on startup (not recommended).
- `disable_failure` — continue running if NTP server unreachable (not recommended for production).
- Clock drift beyond tolerance causes authentication failures. Ensure NTP is configured.
