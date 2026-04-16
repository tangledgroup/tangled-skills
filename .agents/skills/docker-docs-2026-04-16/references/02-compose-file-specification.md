# Docker Compose File Specification

## Overview

The Compose Specification defines the format for configuration files used by Docker Compose. It supersedes legacy versions 2.x and 3.x. Implemented in Compose v2 (v1.27.0+).

**Source:** https://docs.docker.com/compose/compose-file/
**Specification repo:** https://github.com/compose-spec/compose-spec

## Top-Level Elements

A Compose file must declare a `services` top-level element. Other elements are optional.

```yaml
name: myproject          # Optional: project name
version: "3.8"           # Deprecated in favor of spec version
services:                # Required: define containers
networks:                # Optional: define networks
volumes:                 # Optional: define named volumes
configs:                 # Optional: application config files
secrets:                 # Optional: sensitive data
```

## Services Top-Level Element

The `services` element maps service names to service definitions.

```yaml
services:
  <service-name>:
    <attribute>: <value>
```

### Service Attributes Reference

#### Image vs Build

| Attribute | Description |
|-----------|-------------|
| `image` | Docker image name (with optional tag). Mutually exclusive with `build`. |
| `build` | Build configuration. Can be a string (path) or an object with detailed options. |

```yaml
# Simple: use pre-built image
services:
  web:
    image: nginx:alpine

# Build from Dockerfile
services:
  api:
    build: .

# Detailed build config
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile.prod
      target: production
      args:
        NODE_ENV: production
      cache_from:
        - type: local,src=/tmp/.buildcache
```

#### Container Configuration

| Attribute | Description |
|-----------|-------------|
| `container_name` | Custom container name (must be unique) |
| `hostname` | Container hostname |
| `domainname` | Container domain name |
| `stdin_open` | Keep stdin open (`true`/`false`) |
| `tty` | Allocate a pseudo-TTY (`true`/`false`) |
| `entrypoint` | Override the container's entrypoint |
| `command` | Override the default command |
| `env_file` | Path(s) to environment variable files |
| `environment` | Environment variables (list or map) |
| `labels` | Metadata labels |
| `depends_on` | Service dependencies |
| `restart` | Restart policy (`no`, `always`, `on-failure`, `unless-stopped`) |
| `deploy` | Deployment configuration (Swarm mode) |

```yaml
services:
  web:
    container_name: my-web
    hostname: webserver
    entrypoint: /docker-entrypoint.sh
    command: ["--port", "8080"]
    
    env_file: .env
    environment:
      - DEBUG=true
      - DATABASE_URL=postgresql://db
    
    restart: unless-stopped
    
    depends_on:
      db:
        condition: service_healthy
```

#### Ports

| Attribute | Description |
|-----------|-------------|
| `ports` | Host-to-container port mappings |

**Short syntax:** `"host:container"` or `"host:container/protocol"`

```yaml
ports:
  - "80:80"           # All interfaces
  - "127.0.0.1:8080:80"  # Localhost only
  - "8080:80/tcp"     # TCP protocol specified
  - "8080:80/udp"     # UDP protocol
```

**Long syntax:**

```yaml
ports:
  - target: 80
    published: 8080
    protocol: tcp
    mode: host         # or 'ingress' for Swarm routing
    ip: 127.0.0.1
```

#### Volumes

| Attribute | Description |
|-----------|-------------|
| `volumes` | Mount points (bind mounts, named volumes, or anonymous volumes) |

**Short syntax:** `"<source>:<target>[:<options>]"`

```yaml
volumes:
  - ./src:/app/src              # Bind mount (host path)
  - /var/lib/mysql              # Anonymous volume
  - mydata:/var/lib/data        # Named volume
  - ./config:/etc/app:ro        # Read-only bind mount
```

**Long syntax:**

```yaml
volumes:
  - type: bind
    source: ./src
    target: /app/src
    read_only: true
    bind:
      propagate: rprivate

  - type: volume
    source: mydata
    target: /var/lib/data
    volume:
      nocopy: true

  - type: tmpfs
    target: /tmp
    tmpfs:
      size: 100000000  # 100MB in bytes
```

#### Networks

| Attribute | Description |
|-----------|-------------|
| `networks` | Networks to connect the service to |

```yaml
services:
  web:
    networks:
      - frontend
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true     # No external access
```

#### Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
  start_interval: 5s    # For Swarm mode
```

**test formats:**
- `CMD` — Run command, exit code 0 = healthy
- `CMD-SHELL` — Run command in shell
- `NONE` — Disable healthcheck (from base image)

#### Resource Limits (deploy section)

```yaml
services:
  web:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "0.5"
          memory: 50M
        reservations:
          cpus: "0.25"
          memory: 20M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      placement:
        constraints:
          - node.role == manager
```

#### Other Service Attributes

| Attribute | Description |
|-----------|-------------|
| `logging` | Logging configuration for the service |
| `pull_policy` | Image pull policy (`always`, `never`, `if-not-present`, `missing`) |
| `profiles` | Profiles this service belongs to (conditional startup) |
| `extends` | Extend configuration from another file or section |
| `build` | Build configuration (see above) |
| `image` | Image name (see above) |
| `init` | Run init process inside container (`true`/`false`) |

```yaml
services:
  web:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    
    pull_policy: always
    
    profiles: ["dev"]
    
    init: true
```

## Networks Top-Level Element

```yaml
networks:
  <network-name>:
    driver: bridge|overlay|host|macvlan|ipvlan|none
    driver_opts:
      opt1: value1
    ipam:
      config:
        - subnet: 172.28.0.0/16
          ip_range: 172.28.5.0/24
          gateway: 172.28.5.254
    external: true|false
    name: <network-name>
```

**Built-in network drivers:**
- `bridge` — Default, single-host
- `overlay` — Multi-host (Swarm/Kubernetes)
- `host` — Use host networking directly
- `none` — No networking
- `macvlan` / `ipvlan` — Advanced networking

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: overlay
    attachable: true     # Standalone containers can join
    ipam:
      config:
        - subnet: 10.0.0.0/24
```

## Volumes Top-Level Element

```yaml
volumes:
  <volume-name>:
    driver: local|<custom-driver>
    driver_opts:
      type: nfs
      o: addr=10.40.0.1,nosuid
      device: ":<dir>"
    external: true|false
    name: <volume-name>
```

**Volume drivers:**
- `local` — Default, stored in Docker's managed path
- Custom drivers via plugins (e.g., `flocker`, `s3fs`)

```yaml
volumes:
  db-data:
    driver: local
  nfs-share:
    driver: flocker
    driver_opts:
      type: "nfs"
      o: "addr=10.40.0.1,nosuid"
      device: ":/exports/nfs"
```

## Configs Top-Level Element

Application configuration files (not secrets).

```yaml
configs:
  <config-name>:
    file: ./path/to/config
    external: true|false
    name: <remote-config-name>
```

Used in services via `configs` attribute:

```yaml
services:
  web:
    configs:
      - source: nginx-config
        target: /etc/nginx/conf.d/default.conf
        mode: 0444       # Octal file permissions
        uid: "1001"
        gid: "1001"

configs:
  nginx-config:
    file: ./nginx/nginx.conf
```

## Secrets Top-Level Element

Sensitive data (passwords, keys, certificates).

```yaml
secrets:
  <secret-name>:
    file: ./path/to/secret-file
    external: true|false
    name: <remote-secret-name>
```

Used in services via `secrets` attribute:

```yaml
services:
  db:
    secrets:
      - db-password
      - source: aws-credentials
        target: /run/secrets/aws-credentials
        uid: "1001"
        gid: "1001"
        mode: 0400

secrets:
  db-password:
    file: ./db/password.txt
  aws-credentials:
    external: true
```

## Variable Interpolation

Compose supports shell-like variable substitution.

**Syntax:** `${VARIABLE}` or `${VARIABLE:-default}` (with default)

```yaml
services:
  web:
    image: ${REGISTRY:-docker.io}/myapp:${TAG:-latest}
    environment:
      - DB_HOST=${DB_HOST:-localhost}
```

**Variable sources (in priority order):**
1. Environment variables in the shell
2. `.env` file in the project directory
3. `--env-file` flag
4. Default values specified with `:-`

## Profiles

Profiles allow conditional startup of services.

```yaml
services:
  web:
    image: nginx
  redis:
    image: redis
    profiles: ["cache"]
  monitoring:
    image: grafana
    profiles: ["monitoring", "cache"]
```

**Startup commands:**
```console
# Start only default services
$ docker compose up -d

# Include specific profile
$ docker compose --profile cache up -d

# Include multiple profiles
$ docker compose --profile monitoring --profile cache up -d

# Start everything (including all profiles)
$ docker compose --all-profiles up -d
```

## Multiple Compose Files

Compose merges files; later files override earlier ones.

```console
$ docker compose -f base.yaml -f production.yaml up -d
```

**Merge behavior:**
- Lists are **replaced**, not merged
- Maps are **merged** (later values override)
- Scalars are **overridden** by later files

**Example — base.yaml:**
```yaml
services:
  web:
    image: nginx
    ports: ["80:80"]
    environment:
      - DEBUG=true
```

**Example — production.yaml:**
```yaml
services:
  web:
    ports: ["443:443"]     # Replaces the ports list
    environment:
      - DEBUG=false         # Overrides the map value
```

## extends (Deprecated)

The `extends` keyword for sharing service definitions across files has been deprecated. Use file merging instead.

**Old approach (deprecated):**
```yaml
services:
  webapp:
    extends:
      file: common.yaml
      service: webapp-base
```

**New approach:** Merge files at the command line with `-f`.

## Build Context Details

### Build Attributes

| Attribute | Description |
|-----------|-------------|
| `context` | Path to build context (default: `.`, directory containing Dockerfile) |
| `dockerfile` | Name of the Dockerfile (default: `Dockerfile`) |
| `dockerfile_inline` | Inline Dockerfile content (overrides `dockerfile`) |
| `target` | Named stage to build in multi-stage Dockerfile |
| `args` | Build-time arguments (map or list) |
| `labels` | Labels for the resulting image |
| `cache_from` | External cache sources |
| `cache_to` | Cache export destinations |
| `extra_hosts` | Additional host entries |
| `ssh` | SSH agent sockets to forward |
| `pull` | Always pull base image (`true`/`false`) |
| `network` | Network mode for RUN instructions during build |
| `add_host` | Add custom host-to-IP mappings |
| `privileged` | Privileged build mode |

```yaml
build:
  context: .
  dockerfile: Dockerfile.prod
  target: production
  args:
    NODE_ENV: production
    VERSION: "1.0"
  cache_from:
    - type: local,src=/tmp/.buildcache
    - myuser/app:buildcache
  labels:
    com.example.description: "Production image"
```

## Complete Example

```yaml
name: todo-app
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      api:
        condition: service_healthy
    networks:
      - frontend
    restart: unless-stopped

  api:
    build:
      context: ./api
      target: production
    environment:
      - DATABASE_URL=postgresql://app:pass@db:5432/todos
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: todos
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    networks:
      - backend

volumes:
  pgdata:
    driver: local

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```
