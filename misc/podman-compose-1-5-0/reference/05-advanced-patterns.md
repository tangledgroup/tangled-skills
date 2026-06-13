# Advanced Patterns

## Profiles

Profiles conditionally enable services. Services without a profile are always started; services with profiles start only when the profile is activated.

```yaml
services:
  web:
    image: nginx
    # Always started (no profile)

  admin:
    image: phpmyadmin
    depends_on:
      - db
    profiles:
      - debug

  monitoring:
    image: grafana/grafana
    profiles:
      - monitoring
```

Activate profiles:

```bash
podman-compose --profile debug up        # Starts web + admin
podman-compose --profile monitoring up   # Starts web + monitoring
podman-compose --profile debug --profile monitoring up  # All services
```

Profile names match `[a-zA-Z0-9][a-zA-Z0-9_.-]+`.

## Extends

Share service configuration across files or within the same file:

```yaml
services:
  base:
    image: node:18
    environment:
      NODE_ENV: production
    working_dir: /app

  web:
    extends:
      service: base
    ports:
      - "3000:3000"

  worker:
    extends:
      file: common.yml
      service: base-config
    command: ["node", "worker.js"]
```

Cross-file extends:

```yaml
services:
  web:
    extends:
      file: ../shared/compose.yml
      service: webapp-base
    ports:
      - "8080:80"
```

Merge rules for extends:
- Mappings (environment, labels): main overrides extended keys
- Sequences (ports, volumes, cap_add): items combined, extended first
- Scalars (image, user): main takes precedence

## Multi-Compose Include

Reference other compose files as dependencies:

```yaml
include:
  - ./infrastructure/compose.yaml
  - path: ./monitoring/compose.yaml
    project_name: monitoring-stack
```

Included files are resolved before the main file. Services from included files can be depended upon.

## Systemd Service Generation

Generate systemd unit files for rootless service management:

```bash
# Register the podman-compose systemd template (once, as root)
sudo podman-compose systemd -a create-unit

# Generate per-project unit files
podman-compose systemd --dir ~/.config/systemd/user

# Enable and start
systemctl --user enable compose@myproject.service
systemctl --user start compose@myproject.service
```

The generated unit file runs `podman-compose up` on start and `podman-compose down` on stop, with automatic restart on failure.

## Migration from Docker Compose

Key differences when migrating:

**No daemon**: Podman Compose calls `podman` CLI directly. Commands that rely on Docker socket (`/var/run/docker.sock`) won't work. Use `--no-pod` if you don't want pod grouping.

**Rootless by default**: Containers run as the current user. Volume permissions may need adjustment:

```yaml
services:
  web:
    volumes:
      - ./app:/app:U  # U option for rootless UID mapping
```

**Pod mode**: By default, podman-compose groups services into pods (shared network namespace). Disable with `--no-pod` flag or `PODMAN_COMPOSE_NO_POD=1`.

**DNS resolution**: Requires the `dnsname` plugin (`podman-plugins` package) for container name resolution on CNI networks. Not needed with netavark backend.

**SELinux labels**: Use `:z` (shared) or `:Z` (private) suffix on bind mounts:

```yaml
volumes:
  - ./data:/app/data:z   # Shared SELinux context
  - ./private:/secret:Z  # Private SELinux context
```

**Unsupported features**: Some docker-compose features are not yet implemented in podman-compose:
- `scale` (use `--scale SERVICE=NUM` with `up`)
- Container healthcheck propagation (basic support exists)
- Full deploy specification (limited to resources)
- Configs and secrets from external platforms

## Development Workflow

Build with SSH agent forwarding:

```bash
podman-compose build --ssh default
```

Hot-reload with bind mounts:

```yaml
services:
  web:
    build: .
    volumes:
      - .:/app:delegated
    command: ["npm", "run", "dev"]
```

Console attachment for debugging:

```bash
podman-compose up  # Attached mode (foreground)
podman-compose logs -f web  # Follow specific service logs
```

## Testing

Run integration tests:

```bash
python3 -m unittest discover tests/unit
python3 -m unittest discover tests/integration
```

Test a specific compose file:

```bash
podman-compose -f test-compose.yaml config  # Validate without running
podman-compose -f test-compose.yaml up --abort-on-container-exit
```
