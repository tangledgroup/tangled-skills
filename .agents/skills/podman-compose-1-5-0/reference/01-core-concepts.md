# Core Concepts

## Architecture Overview

Podman Compose is a **thin wrapper** that bridges the Compose specification with Podman's container runtime. Unlike Docker Compose, which communicates with a daemon, Podman Compose directly executes podman commands in a **daemonless, rootless process model**.

### Key Design Principles

1. **Daemonless Operation**: No background daemon process required. Each command directly invokes podman CLI tools.
2. **Rootless by Default**: Runs without root privileges for improved security posture.
3. **Single Python Script**: Entire implementation in one file (`podman_compose.py`), easy to deploy and debug.
4. **Compose Specification Compliance**: Implements the official [Compose Spec](https://compose-spec.io/) for compatibility with docker-compose workflows.

### Process Model Comparison

**Docker Compose:**
```
docker-compose up → Docker Daemon → Container creation
     ↓
  TCP/Unix socket communication
     ↓
  Context tarball sent to daemon
```

**Podman Compose:**
```
podman-compose up → Direct podman CLI execution → Container creation
     ↓
  No daemon, no network overhead
     ↓
  Build context stays local
```

## Podman Integration Modes

### Mode 1: Standalone `podman-compose` Command

The primary usage mode. Install podman-compose as a standalone executable:

```bash
podman-compose up -d
podman-compose ps
podman-compose logs -f web api
```

**Benefits:**
- Works with any podman version (3.1.0+)
- No configuration required
- Clear separation of concerns

### Mode 2: Podman Subcommand (`podman compose`)

Available in Podman 4.0+, allows using compose as a podman subcommand:

```bash
podman compose up -d
podman compose ps
```

**How it works:**
- `podman compose` is a thin wrapper that executes an external compose provider
- Default providers (in order of precedence):
  1. `docker-compose` (if installed)
  2. `podman-compose` (if installed)

**Configuration:**

Edit `containers.conf` or use environment variables:

```bash
# Set custom provider path
export PODMAN_COMPOSE_PROVIDER=/usr/local/bin/podman-compose

# Disable external command warning
export PODMAN_COMPOSE_WARNING_LOGS=false

# Or edit containers.conf:
# compose_providers = ["/usr/local/bin/podman-compose"]
# compose_warning_logs = false
```

## Pods and Container Grouping

Podman Compose leverages Podman's **pod** feature to group related containers:

### What is a Pod?

A pod is a group of containers that share:
- Network namespace (containers can reach each other via localhost)
- IPC namespace (inter-process communication)
- Optional shared volumes
- Coordinated lifecycle management

### Automatic Pod Creation

When running `podman-compose up`, a pod is automatically created:

```bash
# Pod naming convention
<podman-compose-project-name>_pod

# Example: In /myproject directory
podman-compose up -d
# Creates pod: myproject_pod

# Inspect the pod
podman pod ps
podman pod inspect myproject_pod
```

### Benefits of Pod-Based Orchestration

1. **Network Isolation**: Containers in a pod can communicate via localhost
2. **Resource Sharing**: Shared namespaces reduce overhead
3. **Coordinated Lifecycle**: Start/stop all containers together
4. **Name Resolution**: Services reachable by service name within the pod

## Networking Models

### Default: Pod Network (Netavark or CNI)

Containers in the same pod share a network namespace:

```yaml
services:
  web:
    image: nginx
    # Automatically connected to pod network
  
  api:
    image: myapi
    # Can reach web at http://web:8080 (service name resolution)
```

### Custom Networks

Define explicit networks for more complex topologies:

```yaml
services:
  frontend:
    networks:
      - public
      - internal
  
  backend:
    networks:
      - internal

networks:
  public:
    driver: bridge
  internal:
    driver: bridge
    internal: true  # No external access
```

### DNS Resolution

**With Netavark (default in newer Podman):**
- Built-in DNS resolution for service names
- No additional plugins required

**With CNI networks:**
- Requires `podman-dnsname` plugin for service name resolution
- Install: `sudo dnf install podman-dnsname` or `sudo apt install podman-dnsname`

## Volume Management

### Local Volumes

Bind mounts from host filesystem:

```yaml
volumes:
  - ./data:/app/data              # Relative path
  - /host/path:/container/path    # Absolute path
  - ./html:/usr/share/nginx/html:ro  # Read-only mount
```

**SELinux Considerations:**
On SELinux-enabled systems, add `:Z` or `:z` flag:

```yaml
volumes:
  - ./data:/app/data:Z  # Private unshared content
  - ./shared:/app/shared:z  # Shared content (multiple containers)
```

### Named Volumes

Podman-managed volumes for persistent data:

```yaml
services:
  db:
    image: postgres
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
    # Optional: specify driver and options
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/host/data
```

### Volume Drivers

Supported drivers:
- `local` (default): Podman-managed volumes
- Custom drivers via podman volume plugins

## Environment and Configuration

### Environment Variables

**From .env file:**
```bash
# .env file in project directory
DATABASE_URL=postgres://localhost:5432/app
API_KEY=secret123
```

```yaml
services:
  api:
    environment:
      - DATABASE_URL
      - API_KEY
```

**Inline definition:**
```yaml
services:
  web:
    environment:
      NODE_ENV: production
      PORT: "3000"
```

**As dictionary:**
```yaml
services:
  api:
    environment:
      DATABASE_URL: postgres://db:5432/app
      LOG_LEVEL: info
```

### Configs and Secrets

**Configs (non-sensitive configuration):**
```yaml
configs:
  app-config:
    file: ./config/app.yaml

services:
  api:
    configs:
      - source: app-config
        target: /etc/app/config.yaml
```

**Secrets (sensitive data):**
```yaml
secrets:
  db-password:
    file: ./secrets/db-pass.txt

services:
  db:
    secrets:
      - source: db-password
        target: /run/secrets/db_password
```

## Dependency Management

### Service Dependencies

Use `depends_on` to specify startup order:

```yaml
services:
  web:
    depends_on:
      - api
  
  api:
    depends_on:
      - db
```

**Note:** `depends_on` only controls start order, not health checks. For health-based dependencies, use `healthcheck`:

```yaml
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    depends_on:
      db:
        condition: service_healthy
```

### Scaling Services

Scale a service to multiple replicas:

```bash
# Scale via command line
podman-compose up -d --scale web=3 --scale api=2

# Scale in compose file (limited support)
services:
  web:
    deploy:
      replicas: 3
```

## Project Naming and Isolation

### Project Name Resolution

Podman Compose uses a project name to prefix all resources:

1. Explicit `name` in compose file:
```yaml
name: myapp
```

2. Command-line override:
```bash
podman-compose -p custom-name up
```

3. Directory name (default):
```bash
# In /home/user/myproject/
podman-compose up  # Project name: myproject
```

### Resource Naming Convention

All resources are prefixed with `<project>_`:

- Pod: `<project>_pod`
- Container: `<project>_<service>_<replica>`
- Network: `<project>_<network>`
- Volume: `<project>_<volume>`

This enables running multiple isolated deployments of the same compose file.

## Migration from Docker Compose

### Compatibility Level

Podman Compose supports most docker-compose features:
- ✅ Service definitions (image, build, ports, volumes)
- ✅ Networks and inter-service communication
- ✅ Volumes (named and bind mounts)
- ✅ Environment variables and configs
- ✅ Dependencies and startup order
- ✅ Health checks
- ✅ Most compose commands (up, down, ps, logs, etc.)

### Differences to Note

1. **No daemon**: Faster startup, no context transfer overhead
2. **Pod-based grouping**: Containers share network namespace
3. **Rootless by default**: May require volume mount adjustments
4. **Systemd integration**: Generate systemd units for services

### Common Migration Steps

```bash
# 1. Install podman-compose
pip3 install podman-compose

# 2. Use existing docker-compose.yml (works as-is)
podman-compose -f docker-compose.yml up -d

# 3. Adjust volume mounts if needed (SELinux)
# Add :Z flag to bind mounts on SELinux systems

# 4. Optional: Generate systemd service
podman-compose systemd > myapp.service
sudo systemctl enable --now myapp.service
```

See [Troubleshooting Guide](04-troubleshooting.md) for migration issues.
