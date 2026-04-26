# Environment and Variables

Podman Compose uses a multi-layer approach for environment variable resolution, supporting `.env` files, shell environment, and inline compose file variables.

## Dotenv Files

By default, podman-compose loads `.env` from the project directory. Override with `--env-file`:

```bash
podman-compose --env-file .env.production up
```

The `.env` file uses simple `KEY=VALUE` format:

```bash
# Database configuration
DB_HOST=postgres
DB_PORT=5432
DB_PASSWORD="s3cret"

# Quoted values preserve special characters
API_KEY='sk-abc123'
JSON_CONFIG='{"key": "value"}'
```

Rules:
- Lines starting with `#` are comments
- Blank lines are ignored
- Values can be single-quoted, double-quoted, or unquoted
- Single-quoted values are literal (no interpolation)
- Double-quoted values support interpolation and escape sequences
- `KEY=` (empty value) sets the variable to empty string
- `KEY` (no equals) leaves it unset

## Variable Interpolation

Variables in compose files use `${VAR}` or `$VAR` syntax:

```yaml
services:
  web:
    image: nginx:${NGINX_VERSION:-alpine}
    environment:
      DB_HOST: ${DB_HOST}
      API_URL: "https://${API_DOMAIN}/api"
```

Syntax options:
- `${VAR}` — Required variable (error if not set)
- `${VAR:-default}` — Use default if unset or empty
- `${VAR-default}` — Use default only if unset
- `${VAR:?error message}` — Error with custom message if unset

The `COMPOSE_PROJECT_NAME` variable is automatically set to the project name and available for interpolation.

## Variable Precedence

Variables are resolved in this order (highest priority first):

1. Inline values in compose file
2. Environment variables from `environment:` section
3. Variables from `env_file:` files (last file wins for duplicates)
4. Shell environment variables
5. `.env` file variables
6. Default values specified with `${VAR:-default}`

## Multiple Compose Files

Override base configuration with additional compose files:

```bash
podman-compose -f compose.yaml -f compose.override.yaml up
```

Merge behavior:
- Mappings (dicts): later file overrides earlier keys
- Lists: items are appended
- Scalars: later file wins
- Relative paths: resolved from first file's directory

Example base file (`compose.yaml`):

```yaml
services:
  web:
    image: myapp:latest
    ports:
      - "8080:80"
    environment:
      LOG_LEVEL: info
```

Override file (`compose.override.yaml`):

```yaml
services:
  web:
    environment:
      LOG_LEVEL: debug
      DEBUG: "true"
```

Result: `LOG_LEVEL` becomes `debug`, `DEBUG` is added, ports and image unchanged.

## Environment in Build Context

Build args are separate from runtime environment:

```yaml
services:
  web:
    build:
      context: .
      args:
        NODE_ENV: ${NODE_ENV:-production}
        BUILD_DATE: "${COMPOSE_PROJECT_NAME}-build"
    environment:
      NODE_ENV: production  # Runtime env, independent of build args
```

Build-time variables don't persist in the running container unless explicitly set in `environment`.

## Secrets and Environment

Secrets from environment variables:

```yaml
secrets:
  api-key:
    environment: "API_KEY"  # Reads from shell/env-file variable
```

The secret value is taken from the process environment at compose execution time, not from within the container.

## Podman-Specific Variable Handling

Podman Compose passes variables through `podman` commands using `--env` flags. Special characters in values are properly escaped for shell execution. When using rootless mode, user namespace remapping may affect how UID/GID variables resolve.
