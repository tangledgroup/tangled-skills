# Development

## Contents
- Prerequisites
- Full Development Environment
- Frontend-Only Development
- Running and Debugging
- Code Quality and Testing
- Contributing Guidelines
- Releasing

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.14 |
| uv | Latest stable |
| Rust | Per `rust-toolchain.toml` (nightly for rustfmt) |
| Go | 1.26+ |
| Node.js | 24+ |
| PostgreSQL | 16+ |
| Docker / Docker Compose | Latest CE, Compose v2 |
| Make | 3+ |
| CMake | Latest stable |

**Platform dependencies**:
- **macOS**: `brew install libxmlsec1 libpq pkg-config uv postgresql node@24 golangci-lint krb5 cmake`
- **Debian/Ubuntu**: `apt-get install libgss-dev krb5-config libkrb5-dev libxml2 libxslt1-dev libxmlsec1 xmlsec1 postgresql-server-dev-all postgresql cmake`, then `pip install uv` and install `golangci-lint` separately
- **GCC >= 14 issue**: aws-lc-rs FIPS module build failure. Use older GCC or set `export AWS_LC_FIPS_SYS_CC=clang`.

## Full Development Environment

### Setup

```bash
# Clone and initialize
git clone https://github.com/goauthentik/authentik.git
cd authentik

# Start required services (PostgreSQL, S3/Zenko, Sentry Spotlight)
docker compose -f scripts/compose.yml up -d

# Install dependencies (Python + JS)
make install

# Generate dev config
make gen-dev-config

# Run migrations
make migrate
```

### Running

```bash
# Start authentik (backend + embedded outpost)
make run

# Hot-reloading (requires watchexec)
make run-watch
```

First run: navigate to `http://localhost:9000`, set password for `akadmin`.

### Frontend

```bash
# Build frontend (required even for backend-only work)
make web-build

# Real-time preview
make web-watch
```

Access UI at `http://localhost:9000`.

## Frontend-Only Development

Minimal setup using Docker for backend and Node.js for frontend:

```bash
# Start backend via Docker
docker compose -f scripts/compose.yml up -d server worker postgres

# Install JS dependencies and watch
make web-watch
```

## Running and Debugging

**Recovery key**: If locked out due to misconfigured flows:
```bash
uv run ak create_recovery_key 10 akadmin
```
Paste the token into `http://localhost:9000/recovery/use-token/<token>/`.

**Debug endpoints**:
- Go debug metrics: `AUTHENTIK_LISTEN__DEBUG` (default `0.0.0.0:9900`)
- Python debug server: `AUTHENTIK_LISTEN__DEBUG_PY` (default `0.0.0.0:9901`)
- Prometheus metrics: `AUTHENTIK_LISTEN__METRICS` (default `[::]:9300`)

**Reset development database**: `make dev-reset`

## Code Quality and Testing

```bash
# Lint and fix
make lint-fix
make lint

# Generate API docs
make gen

# Format frontend
make web

# Run tests
make test

# All checks at once
make all
```

**E2E testing**: `docker compose -f tests/e2e/compose.yml up -d`. View Selenium Chrome at `http://localhost:7900/` (password: `secret`) or VNC on port 5900.

## Contributing Guidelines

**PR naming**: `<package>: <verb> <description>` — e.g., `providers/saml2: fix parsing of requests`. Package names follow the Django app structure (admin, api, blueprints, core, crypto, flows, outposts, policies, providers/*, sources/*, stages/*, tasks, tenants).

**Commit messages**: Same format as PR naming. Squash-merge on PR, so individual commit messages within a PR need not adhere.

**Python style**: Linted with black and Ruff. Use native type annotations, meaningful docstrings. Ensure migrations work from last stable version.

**Feature branches only**: Never open PRs from `main`. Create feature branch, push, then PR.

**Documentation**: Use MDX with React components for tabs, action buttons, advanced formatting. Product name is "authentik" (lowercase "a", "k" at end). Company name is "Authentik Security". Sentence case in titles. Bold for UI components, italic for variables.

## Releasing

Releases follow calendar versioning (e.g., 2026.5.0). Release process involves:
1. Update version in lifecycle/package files
2. Generate release notes
3. Tag and push
4. CI builds Docker images and publishes to GHCR/Docker Hub

See the releasing documentation for detailed steps.
