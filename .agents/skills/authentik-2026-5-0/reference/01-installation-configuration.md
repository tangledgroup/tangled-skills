# Installation and Configuration

## Contents
- Docker Compose Installation
- Kubernetes Installation
- AWS Installation
- Environment Variable Configuration
- PostgreSQL Settings
- Storage Settings
- Worker and Web Tuning
- Upgrade Process
- High Availability
- Air-Gapped Environments

## Docker Compose Installation

Recommended for test setups and small-scale production. Requires 2 CPU cores, 2 GB RAM minimum.

```bash
wget https://docs.goauthentik.io/compose.yml
echo "PG_PASS=$(openssl rand -base64 36 | tr -d '\n')" >> .env
echo "AUTHENTIK_SECRET_KEY=$(openssl rand -base64 60 | tr -d '\n')" >> .env
docker compose pull
docker compose up -d
```

Access at `http://<server>:9000`. Default user is `akadmin`.

**Docker socket**: Mounted by default for automatic outpost deployment. Remove the mount and manually deploy outposts if socket access is a security concern. Use Docker Socket Proxy as an alternative.

**Custom ports**: Set `COMPOSE_PORT_HTTP=80` and `COMPOSE_PORT_HTTPS=443` in `.env`. Internal ports are 9000 (HTTP) and 9443 (HTTPS).

**Do not mount `/etc/timezone` or `/etc/localtime`** — all internal operations use UTC. Mounting timezone files breaks OAuth and SAML.

## Kubernetes Installation

Use the official Helm chart from `authentik/authentik`. Edit `values.yaml` for configuration, then:

```bash
helm repo update
helm upgrade --install authentik authentik/authentik -f values.yaml
```

Persistent data stored in PVCs with default Helm chart. Outposts auto-discover Kubernetes in-cluster config.

## AWS Installation

Deploy via official CloudFormation templates. See documentation for regional and sizing guidance.

## Environment Variable Configuration

All settings use double-underscore nesting (`AUTHENTIK_POSTGRESQL__HOST`) translated to YAML internally. Load values from:
- `env://<name>` — environment variable, optional `?default`
- `file://<name>` — file contents, optional `?default`

Verify config: `docker compose run --rm worker ak dump_config` (Docker) or `kubectl exec -it deployment/authentik-worker -c worker -- ak dump_config` (K8s).

Key settings:
- `AUTHENTIK_SECRET_KEY` — cookie signing key. Changing invalidates sessions. Do not change on pre-2023.6.0 instances.
- `AUTHENTIK_LOG_LEVEL` — `debug`, `info`, `warning`, `error`, `trace`. Trace includes sensitive data (session cookies).
- `AUTHENTIK_LISTEN__HTTP` — comma-separated `address:port`, default `[::]:9000`
- `AUTHENTIK_LISTEN__HTTPS` — default `[::]:9443`
- `AUTHENTIK_WEB__PATH` — URL path prefix, e.g. `/authentik/` (must have leading and trailing slash)
- `AUTHENTIK_COOKIE_DOMAIN` — session cookie domain
- `AUTHENTIK_DISABLE_UPDATE_CHECK` — disable update checker
- `AUTHENTIK_SKIP_MIGRATIONS` — skip migrations on startup (advanced only)

## PostgreSQL Settings

Supports PostgreSQL 14-18. Connection settings support hot-reloading (host, port, user, password). Adding/removing read replicas requires restart.

**Connection**: `AUTHENTIK_POSTGRESQL__HOST`, `__PORT` (5432), `__USER`, `__PASSWORD`, `__NAME`. Password falls back to `POSTGRES_PASSWORD` in default Docker Compose.

**SSL**: `AUTHENTIK_POSTGRESQL__SSLMODE` defaults to `verify-ca`. Options: `disable`, `allow`, `prefer`, `require`, `verify-ca`, `verify-full`. Set `__SSLROOTCERT` for CA verification.

**Connection pooler (PgBouncer/Pgpool)**:
- Transaction pooling: set `AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS=true`, keep `CONN_MAX_AGE=0`
- Session pooling: set `CONN_MAX_AGE` lower than backend timeout, or use `0`
- Enable `AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS=true` to avoid stale connections

**Read replicas**: Configure under `AUTHENTIK_POSTGRESQL__READ_REPLICAS__0__HOST` etc. Primary is not used for queries when replicas are available.

## Storage Settings

Default: file backend at `/data`. S3 also supported.

- `AUTHENTIK_STORAGE__BACKEND` — `file` or `s3`
- `AUTHENTIK_STORAGE__FILE__PATH` — default `/data`
- `AUTHENTIK_STORAGE__S3__BUCKET_NAME`, `__ACCESS_KEY`, `__SECRET_KEY`, `__REGION`, `__ENDPOINT`
- Separate backends for media and reports: `AUTHENTIK_STORAGE__MEDIA__BACKEND`, `AUTHENTIK_STORAGE__REPORTS__BACKEND`

## Worker and Web Tuning

**Worker** (Dramatiq):
- `AUTHENTIK_WORKER__PROCESSES` — default 1, increase if no replica scaling
- `AUTHENTIK_WORKER__THREADS` — default 2, minimum 2 recommended
- `AUTHENTIK_WORKER__TASK_MAX_RETRIES` — default 5
- `AUTHENTIK_WORKER__TASK_DEFAULT_TIME_LIMIT` — default 10 minutes
- `AUTHENTIK_WORKER__SCHEDULER_INTERVAL` — default 60 seconds

**Web** (gunicorn):
- `AUTHENTIK_WEB__WORKERS` — default 2, minimum 2 recommended
- `AUTHENTIK_WEB__THREADS` — default 4
- `AUTHENTIK_WEB__MAX_REQUESTS` — default 1000 (worker restart after N requests)
- `AUTHENTIK_WEB__TIMEOUT_HTTP_READ` — default 30s
- `AUTHENTIK_WEB__TIMEOUT_HTTP_WRITE` — default 60s
- `AUTHENTIK_WEB__TIMEOUT_HTTP_IDLE` — default 120s

## Upgrade Process

Download new `compose.yml`, pull images, restart:

```bash
wget https://docs.goauthentik.io/compose.yml
docker compose pull
docker compose up -d
```

For Kubernetes: `helm upgrade authentik authentik/authentik`. Always check release notes for migration steps.

## High Availability

Multiple server and worker replicas behind a load balancer. PostgreSQL read replicas distribute query load. Session storage is exclusively database-based since 2025.4. Configure `AUTHENTIK_SESSIONS__UNAUTHENTICATED_AGE` (default 1 day).

## Air-Gapped Environments

Pre-pull all images and mount locally. Disable update checker with `AUTHENTIK_DISABLE_UPDATE_CHECK=true`. Ensure outbound connections are not required by pre-loading GeoIP databases and certificates.
