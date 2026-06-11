# Compose File Reference

## Overview

The Compose Specification defines multi-container Docker applications in YAML. Legacy versions 2.x and 3.x were merged into the unified specification, implemented in Compose v2 (v1.27.0+).

File names: `docker-compose.yml`, `docker-compose.yaml`, `compose.yml`, `compose.yaml`

## Top-Level Elements

### name (optional)

Sets a custom project name instead of auto-derived from directory:
```yaml
name: my-application
```

### services (required for running containers)

Defines the containers that make up the application.

### networks (optional)

Configures named networks for service communication.

### volumes (optional)

Configures named persistent data stores.

### configs (optional)

Read-only configuration files mounted into containers.

### secrets (optional)

Sensitive data mounted as files in `/run/secrets/`.

### profiles (optional)

Named groups of services activated with `--profile`:
```yaml
profiles:
  - debug
  - monitoring
```

### include (optional)

Includes other Compose files:
```yaml
include:
  - ./common.yml
  - path: ./monitoring.yml
    project_directory: ../monitoring
```

## Service Attributes

### image

Specifies the container image:
```yaml
image: redis
image: redis:7.2
image: myregistry.example.com:5000/myapp:v1.0
image: nginx@sha256:abc123...
```

### build

Builds an image from a Dockerfile:
```yaml
build:
  context: .
  dockerfile: Dockerfile
  args:
    BUILD_VERSION: "1.0"
  target: production
  platforms:
    - linux/amd64
    - linux/arm64
```

### command

Overrides the default CMD:
```yaml
command: ["python", "app.py", "--debug"]
command: python app.py --debug
```

### depends_on

Controls startup order and availability:
```yaml
depends_on:
  db:
    condition: service_healthy
    restart: true
  redis:
    condition: service_started
  migration:
    condition: service_completed_successfully
```

Conditions: `service_started`, `service_healthy`, `service_completed_successfully`

### ports

Maps host ports to container ports:

**Short syntax:** `[HOST:]CONTAINER[/PROTOCOL]`
```yaml
ports:
  - "3000"                    # Random host port -> 3000
  - "8000:8000"               # Host 8000 -> Container 8000
  - "9090-9091:8080-8081"     # Port ranges
  - "127.0.0.1:8001:8001"     # Bind to specific IP
  - "6060:6060/udp"           # UDP protocol
```

**Long syntax:**
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

### expose

Internal ports accessible only to linked services (not published to host):
```yaml
expose:
  - "3000"
  - "8000/tcp"
```

### volumes

Mounts storage into the container:

**Bind mount:**
```yaml
volumes:
  - ./config:/app/config:ro
  - ./data:/app/data
```

**Named volume:**
```yaml
volumes:
  - db-data:/var/lib/postgresql/data
```

**Long syntax:**
```yaml
volumes:
  - type: volume
    source: db-data
    target: /var/lib/postgresql/data
    volume:
      nocopy: true
  - type: bind
    source: ./app
    target: /code
  - type: tmpfs
    target: /run
    tmpfs:
      size: 100000000
```

### environment

Sets environment variables:

**Map syntax:**
```yaml
environment:
  RACK_ENV: development
  SHOW: "true"
  PORT: "3000"
```

**Array syntax:**
```yaml
environment:
  - RACK_ENV=development
  - SHOW=true
```

### env_file

Loads environment variables from files:
```yaml
env_file: .env
env_file:
  - ./default.env
  - path: ./override.env
    required: false
  - path: ./raw.env
    format: raw
```

**Env file format rules:**
- `VAR=value` or `VAR:value`
- Lines starting with `#` are comments
- Single quotes (`'`) prevent interpolation
- Double quotes (`"`) support escape sequences (`\n`, `\t`)
- `VAR=` sets empty string, `VAR` alone unsets

### networks

Connects service to defined networks:
```yaml
networks:
  - frontend
  - backend
```

**With options:**
```yaml
networks:
  frontend:
    aliases:
      - webapp
    ipv4_address: 172.16.238.10
  backend:
    priority: 1000
```

### restart

Restart policy on container termination:
```yaml
restart: "no"            # Default, never restart
restart: always          # Always restart until removal
restart: on-failure      # Restart on non-zero exit
restart: on-failure:3    # Max 3 retries
restart: unless-stopped  # Restart unless explicitly stopped
```

### healthcheck

Health monitoring configuration:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost"]
  interval: 1m30s
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

### deploy

Deployment and lifecycle configuration (primarily for Swarm, some attributes used in standalone):
```yaml
deploy:
  replicas: 3
  resources:
    limits:
      cpus: "0.5"
      memory: 512M
    reservations:
      cpus: "0.25"
      memory: 256M
  restart_policy:
    condition: on-failure
    delay: 5s
    max_attempts: 3
    window: 120s
  update_config:
    parallelism: 2
    delay: 10s
    order: start-first
  rollback_config:
    parallelism: 1
    order: stop-first
  placement:
    constraints:
      - node.role == manager
    preferences:
      - spread: node.labels.datacenter
```

### develop

Development synchronization configuration:
```yaml
develop:
  watch:
    - path: ./src
      action: sync
      target: /app/src
    - path: ./src
      action: rebuild
    - path: Dockerfile
      action: rebuild
```

### Other Service Attributes

- `cap_add` / `cap_drop` — Linux capabilities
- `cgroup_parent` — Parent cgroup
- `container_name` — Custom container name
- `cpu_count` / `cpu_percent` / `cpu_shares` / `cpus` / `cpuset` — CPU constraints
- `device_cgroup_rules` — Device cgroup rules
- `devices` — Device mappings (`/dev/ttyUSB0:/dev/ttyUSB0`)
- `dns` / `dns_opt` / `dns_search` — DNS configuration
- `domainname` — Custom domain name
- `entrypoint` — Override ENTRYPOINT
- `extends` — Inherit from another service
- `external_links` — Link to external services
- `extra_hosts` — Hostname-to-IP mappings
- `gpus` — GPU allocation (`all` or device requests)
- `group_add` — Additional user groups
- `healthcheck` — Health monitoring
- `hostname` — Custom hostname
- `init` — Enable init process (PID 1 signal forwarding)
- `ipc` — IPC namespace mode
- `isolation` — Container isolation technology
- `labels` / `label_file` — Metadata labels
- `logging` — Logging driver configuration
- `mac_address` — MAC address
- `mem_limit` / `mem_reservation` / `mem_swappiness` / `memswap_limit` — Memory constraints
- `network_mode` — Network mode (`bridge`, `host`, `none`, `service:name`)
- `oom_kill_disable` / `oom_score_adj` — OOM controls
- `pid` / `pids_limit` — PID namespace and limits
- `platform` — Target platform (`linux/amd64`, `windows/amd64`)
- `privileged` — Full host privileges
- `pull_policy` — Image pull behavior (`always`, `never`, `missing`, `build`, `daily`, `weekly`, `every_<duration>`)
- `read_only` — Read-only root filesystem
- `runtime` — Container runtime (e.g., `runc`)
- `scale` — Number of container replicas
- `secrets` — Secret access
- `security_opt` — Security options (`no-new-privileges`, `apparmor`, `seccomp`)
- `shm_size` — /dev/shm size
- `stdin_open` / `tty` — Interactive mode
- `stop_grace_period` — Time before SIGKILL
- `stop_signal` — Override stop signal
- `sysctls` — Kernel parameters
- `tmpfs` — tmpfs mounts
- `ulimits` — Resource limits
- `user` — Run as user
- `working_dir` — Working directory

## Networks Top-Level Element

```yaml
networks:
  frontend:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.host_binding_ipv4: "127.0.0.1"
  backend:
    driver: overlay
    attachable: true
  external-net:
    external: true
    name: existing-network
  custom:
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.5.254
    internal: true
```

Attributes: `attachable`, `driver`, `driver_opts`, `enable_ipv4`, `enable_ipv6`, `external`, `ipam`, `internal`, `labels`, `name`

## Volumes Top-Level Element

```yaml
volumes:
  db-data:
  custom-volume:
    driver: local
    driver_opts:
      type: "nfs"
      o: "addr=10.40.0.199,nolock,soft,rw"
      device: ":/docker/example"
  external-vol:
    external: true
    name: actual-volume-name
```

Attributes: `driver`, `driver_opts`, `external`, `labels`, `name`

## Secrets Top-Level Element

```yaml
secrets:
  server-certificate:
    file: ./certs/server.cert
  db-password:
    environment: DB_PASSWORD
  api-key:
    external: true
```

## Configs Top-Level Element

```yaml
configs:
  my-config:
    file: ./my-config.txt
  redis-config:
    external: true
```

## Interpolation

Compose interpolates variables from environment and `.env` files:
```yaml
environment:
  PORT: ${PORT:-3000}          # Default value
  REQUIRED: ${REQUIRED_VAR}     # Error if not set
  OPTIONAL: ${MISSING_VAR:-}    # Empty string if not set
```

Use single quotes to prevent interpolation: `'${NOT_INTERPOLATED}'`

## Merge Rules

When using `extends` or multiple files:
- **Mappings**: Main definition keys override extended keys
- **Sequences**: Items are combined (extended first, then main)
- **Scalars**: Main takes precedence over extended

## Extensions

Custom keys prefixed with `x-` are ignored by Compose:
```yaml
x-my-extension:
  custom-value: data
```
