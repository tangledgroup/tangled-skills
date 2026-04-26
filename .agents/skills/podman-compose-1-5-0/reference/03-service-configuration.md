# Service Configuration

Service definitions are the core of compose files. Each service maps to one or more identically configured containers.

## Image and Build

Specify a pre-built image:

```yaml
services:
  web:
    image: nginx:alpine
```

Build from source:

```yaml
services:
  web:
    build:
      context: ./webapp
      dockerfile: Dockerfile
      args:
        NODE_ENV: production
      target: production
      cache_from:
        - nginx:alpine
      labels:
        - "com.example.description=Web frontend"
```

Build attributes:
- `context` — Build context path (relative to compose file)
- `dockerfile` — Dockerfile name or path
- `args` — Build-time variables
- `target` — Multi-stage build target
- `cache_from` — Images to use as cache
- `labels` — Labels on built image
- `extra_hosts` — Host entries during build
- `network` — Network for build (e.g., `host`)
- `shm_size` — Shared memory size for build
- `ssh` — SSH agent socket or keys

## Ports

Expose container ports to the host.

Short syntax (`[HOST_IP:]HOST_PORT:CONTAINER_PORT[/PROTOCOL]`):

```yaml
ports:
  - "8080:80"
  - "127.0.0.1:8443:443"
  - "9090-9091:8080-8081"
  - "6060:6060/udp"
```

Long syntax for additional options:

```yaml
ports:
  - name: web
    target: 80
    published: "8080"
    host_ip: 127.0.0.1
    protocol: tcp
    app_protocol: http
    mode: host
```

Long syntax fields:
- `target` — Container port (required)
- `published` — Host port or range
- `host_ip` — Bind to specific interface
- `protocol` — `tcp` or `udp`
- `app_protocol` — Application protocol hint (`http`, `https`)
- `mode` — `host` (each node) or `ingress` (load balanced)

## Volumes

Mount host paths or named volumes into containers.

Short syntax:

```yaml
volumes:
  - ./data:/app/data
  - db-volume:/var/lib/db
  - /host/path:/container/path:ro
  - /host/path:/container/path:rw,z
```

Long syntax:

```yaml
volumes:
  - type: volume
    source: db-data
    target: /data
    volume:
      nocopy: true
  - type: bind
    source: ./config
    target: /etc/app/config
    read_only: true
    bind:
      create_host_path: false
  - type: tmpfs
    target: /tmp
    tmpfs:
      size: 100000000
```

Mount types: `volume`, `bind`, `tmpfs`, `npipe`

Bind mount options:
- `propagation` — Mount propagation mode
- `create_host_path` — Create host directory if missing (default: true)
- `selinux` — `z` (shared) or `Z` (private)

Volume options:
- `nocopy` — Don't copy image data when creating volume
- `subpath` — Mount a subdirectory of the volume

## Environment

Set environment variables in containers. Map syntax:

```yaml
environment:
  DATABASE_URL: postgresql://db:5432/app
  DEBUG: "false"
  PORT: "8080"
```

Array syntax:

```yaml
environment:
  - DATABASE_URL=postgresql://db:5432/app
  - DEBUG=false
  - PORT=8080
```

Load from file:

```yaml
env_file:
  - .env
  - ./config/production.env
```

With optional files:

```yaml
env_file:
  - path: .env
    required: true
  - path: .env.local
    required: false
    format: raw
```

Variables declared in `environment` override values from `env_file`.

## Networks

Attach services to named networks:

```yaml
services:
  web:
    networks:
      - frontend
      - backend
  db:
    networks:
      backend:
        aliases:
          - database
        ipv4_address: 172.16.238.10
```

Per-network options:
- `aliases` — Alternative hostnames on this network
- `ipv4_address` / `ipv6_address` — Static IP assignment
- `mac_address` — MAC address for this network
- `priority` — Connection order priority
- `gw_priority` — Default gateway priority

Network mode overrides:

```yaml
network_mode: host      # Raw host network access
network_mode: none      # No networking
network_mode: "service:db"  # Share another service's network
```

When `network_mode` is set, the `networks` attribute is not allowed.

## Dependencies

Short syntax (startup order only):

```yaml
services:
  web:
    depends_on:
      - db
      - redis
```

Long syntax with conditions:

```yaml
services:
  web:
    depends_on:
      db:
        condition: service_healthy
        restart: true
      redis:
        condition: service_started
```

Conditions:
- `service_started` — Service is running (default)
- `service_healthy` — Healthcheck passes
- `service_completed_successfully` — Previous service exited successfully

## Healthchecks

Define container health monitoring:

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:80/ || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
  start_interval: 5s
```

Disable inherited healthcheck:

```yaml
healthcheck:
  disable: true
```

Test formats:
- `CMD` — Exec form (no shell)
- `CMD-SHELL` — Run through `/bin/sh`
- String form is equivalent to `CMD-SHELL`
- `NONE` — Disable healthcheck

## Resource Limits

CPU and memory constraints:

```yaml
deploy:
  resources:
    limits:
      cpus: "0.5"
      memory: 512M
    reservations:
      cpus: "0.25"
      memory: 256M
```

Direct service-level limits (also supported):

```yaml
cpus: 0.5
mem_limit: 512m
pids_limit: 100
```

## Restart Policy

Control container restart behavior:

```yaml
restart: "no"           # Never restart (default)
restart: always         # Always restart
restart: on-failure     # Restart on non-zero exit
restart: "on-failure:5" # Max 5 retries
restart: unless-stopped # Restart unless explicitly stopped
```

## Container Identity

```yaml
container_name: my-web-app   # Fixed container name (prevents scaling)
hostname: web01              # Custom hostname
domainname: example.com      # Domain name
user: "1000:1000"            # UID:GID
working_dir: /app            # Working directory
```

## Security

```yaml
privileged: true              # Full host privileges
read_only: true               # Read-only root filesystem
security_opt:
  - apparmor:unconfined
  - label:user:USER
cap_add:
  - NET_ADMIN
cap_drop:
  - ALL
```

## Miscellaneous

```yaml
entrypoint: ["/app/entrypoint.sh"]   # Override entrypoint
command: ["npm", "start"]            # Override command
init: true                           # Run init process (PID 1)
tty: true                            # Allocate TTY
stdin_open: true                     # Keep stdin open
stop_signal: SIGUSR1                 # Custom stop signal
stop_grace_period: 30s               # Seconds before SIGKILL
ulimits:
  nofile:
    soft: 65536
    hard: 65536
tmpfs:
  - /run:mode=755,size=100M
shm_size: 256m                       # /dev/shm size
sysctls:
  net.core.somaxconn: 1024
extra_hosts:
  - "myhost=192.168.1.100"
dns:
  - 8.8.8.8
  - 1.1.1.1
labels:
  com.example.app: "myapp"
```

## Podman-Specific Features

Podman Compose adds these compose-spec extensions:

```yaml
services:
  web:
    image: nginx
    podman_args:
      --cap-add: SYS_ADMIN        # Pass extra args to podman run
    pid: "host"                    # Host PID namespace
    userns_mode: "keep-id:uid=1000"  # User namespace remapping
```

The `--no-pod` flag disables automatic pod creation, running each service as independent containers instead.
