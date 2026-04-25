# Compose File Guide

Complete guide to the Compose Specification file format used by podman-compose.

## File Basics

### Default Filenames

Podman Compose looks for these files (in order of preference):
1. `compose.yaml` (recommended)
2. `compose.yml`
3. `docker-compose.yaml`
4. `docker-compose.yml` (legacy compatibility)

Specify custom file with `-f` option:
```bash
podman-compose -f staging-compose.yaml up
```

### Multiple Compose Files

Merge multiple compose files for environment-specific configurations:

```bash
# Base config + environment override
podman-compose -f compose.yaml -f compose.override.yaml up

# Development setup
podman-compose -f compose.yaml -f compose.dev.yaml up
```

Files are merged in order, with later files overriding earlier values.

### File Structure

```yaml
version: "3.8"  # Optional (obsolete but supported)
name: myproject  # Optional project name

services:  # Required
  service_name:
    # Service configuration...

networks:  # Optional
  network_name:
    # Network configuration...

volumes:  # Optional
  volume_name:
    # Volume configuration...

configs:  # Optional
  config_name:
    # Config configuration...

secrets:  # Optional
  secret_name:
    # Secret configuration...
```

## Services

The `services` section is required and defines containerized application components.

### Basic Service Definition

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
```

### Image vs Build

**Use pre-built image:**
```yaml
services:
  redis:
    image: redis:7-alpine
```

**Build from Dockerfile:**
```yaml
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
      args:
        NODE_ENV: production
```

**Build with options:**
```yaml
services:
  web:
    build:
      context: .
      target: production  # Multi-stage build target
      cache_from:
        - myapp:cache
      network: host
      pull_pull: true
```

### Port Mapping

**Simple port mapping:**
```yaml
ports:
  - "8080:80"           # Host:Container
  - "3000"              # Publish to random host port
```

**Advanced port configuration:**
```yaml
ports:
  - target: 80          # Container port
    published: 8080     # Host port
    protocol: tcp       # tcp or udp
    mode: host          # host or ingress (default)
```

**Multiple protocols:**
```yaml
ports:
  - "8080:80/tcp"
  - "5353:53/udp"
```

### Environment Variables

**List format (from .env file or explicit values):**
```yaml
environment:
  - NODE_ENV
  - DEBUG=true
  - PORT=3000
```

**Dictionary format:**
```yaml
environment:
  NODE_ENV: production
  DEBUG: "false"
  PORT: "3000"
```

**From .env file:**
```bash
# .env
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

### Volume Mounts

**Bind mount (host path):**
```yaml
volumes:
  - ./app:/usr/src/app
  - /host/path:/container/path
  - ./html:/usr/share/nginx/html:ro  # Read-only
```

**Named volume:**
```yaml
services:
  db:
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

**Anonymous volume:**
```yaml
volumes:
  - /data  # Podman creates anonymous volume
```

**Advanced mount configuration:**
```yaml
services:
  web:
    volumes:
      - type: bind
        source: ./html
        target: /usr/share/nginx/html
        read_only: true
        bind:
          propagation: shared
      
      - type: volume
        source: db-data
        target: /var/lib/postgresql/data
        volume:
          nocopy: true
```

**SELinux labels (RHEL/Fedora/CentOS):**
```yaml
volumes:
  - ./data:/app/data:Z   # Private unshared content
  - ./shared:/app/shared:z  # Shared content
```

### Network Configuration

**Connect to default network:**
```yaml
services:
  web:
    # Automatically connected to default network
  api:
    # Can reach web at http://web:80
```

**Connect to custom networks:**
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
    internal: true
```

**Network aliases:**
```yaml
services:
  api:
    networks:
      frontend:
        aliases:
          - api-alias
      backend:
        aliases:
          - backend-api

networks:
  frontend:
  backend:
```

**Advanced network options:**
```yaml
networks:
  custom:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
    labels:
      com.example.description: "Custom network"
    internal: false
    attachable: false
```

### Dependencies

**Simple dependency:**
```yaml
services:
  web:
    depends_on:
      - api
      - db
  
  api:
    depends_on:
      - db
```

**Dependency with conditions:**
```yaml
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
  
  api:
    depends_on:
      db:
        condition: service_healthy
  
  web:
    depends_on:
      api:
        condition: service_started
```

**Conditions:**
- `service_started`: Dependency has started (default)
- `service_healthy`: Dependency has passed health check
- `service_completed_successfully`: Dependency completed with exit code 0

### Resource Limits

**CPU and memory limits:**
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "1.5"           # 1.5 CPU cores
          memory: 512M          # 512MB memory
        reservations:
          cpus: "0.5"           # Reserve 0.5 CPU
          memory: 256M          # Reserve 256MB memory
```

**Podman-specific limits:**
```yaml
services:
  web:
    mem_limit: 512m
    cpu_quota: 50000           # 50% CPU time
    pids_limit: 100            # Max 100 processes
```

### Health Checks

**Basic health check:**
```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Shell command health check:**
```yaml
services:
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

**Disable health check:**
```yaml
services:
  web:
    healthcheck:
      disable: true
```

### Restart Policies

```yaml
services:
  web:
    restart: always           # Always restart unless stopped
  
  api:
    restart: on-failure       # Restart on non-zero exit
  
  db:
    restart: "no"             # Never auto-restart
  
  worker:
    restart: unless-stopped   # Restart unless explicitly stopped
```

**Restart with delay:**
```yaml
services:
  api:
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3
      window: 60s
```

### User and Working Directory

```yaml
services:
  web:
    user: "1000"              # Run as UID 1000
    working_dir: /app         # Set working directory
```

**Named user (if exists in image):**
```yaml
user: "nginx"
```

### Command and Entrypoint

**Override command:**
```yaml
services:
  api:
    image: myapi
    command: ["python", "app.py", "--debug"]
```

**Override entrypoint:**
```yaml
services:
  web:
    image: nginx
    entrypoint: ["/bin/sh", "-c"]
    command: "echo 'Starting nginx' && exec nginx -g 'daemon off;'"
```

**Disable default command:**
```yaml
command: []
```

### Labels

```yaml
services:
  web:
    labels:
      - "com.example.version=1.0"
      - "com.example.team=platform"
    
  api:
    labels:
      com.example.monitoring: "true"
      com.example.environment: "production"
```

### Logging Configuration

```yaml
services:
  web:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
  
  api:
    logging:
      driver: journald
      options:
        tag: "api-service"
```

**Supported drivers:**
- `json-file` (default): JSON log files
- `journald`: Systemd journal
- `none`: Disable logging

### Temporary Files and Tmpfs

```yaml
services:
  web:
    tmpfs:
      - /tmp
      - /var/run/docker.sock:size=100M,mode=1777
```

## Profiles

Group services into profiles for selective deployment:

```yaml
services:
  web:
    image: nginx
  
  api:
    image: myapi
  
  worker:
    profile: background       # Only starts with --profile background
    image: myworker
  
  debug-tools:
    profile: debug            # Only starts with --profile debug
    image: debug-image
```

**Usage:**
```bash
# Start only default (non-profile) services
podman-compose up -d

# Start services with debug profile
podman-compose --profile debug up -d

# Multiple profiles
podman-compose --profile debug --profile background up -d
```

## Networks

Define custom networks for service communication.

### Network Types

**Bridge network (default):**
```yaml
networks:
  app-network:
    driver: bridge
```

**Host network:**
```yaml
services:
  web:
    network_mode: host
```

**Container network (share with another container):**
```yaml
services:
  web:
    network_mode: service:api
  
  api:
    # web shares network namespace with api
```

**None (no networking):**
```yaml
services:
  isolated:
    network_mode: none
```

### Network Configuration Options

```yaml
networks:
  frontend:
    driver: bridge
    attachable: true          # Allow manual container attachment
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
      driver_opts:
        com.docker.network.bridge.name: "br-front"
    labels:
      com.example.label.key: label-value
    internal: false           # Allow external access
    enable_ipv6: false
    
  backend:
    driver: bridge
    internal: true            # Isolated network, no external access
```

## Volumes

Persistent data storage for containers.

### Named Volumes

```yaml
volumes:
  db-data:
    driver: local
    driver_opts:
      type: none
      device: /path/on/host
      o: bind
    labels:
      com.example.description: "Database volume"
  
  cache-data:
    # Uses default driver and options
```

### External Volumes

Reference existing volumes:

```yaml
volumes:
  existing-volume:
    external: true
  
  renamed-external:
    external: true
    name: actual-volume-name
```

### Volume Drivers

**Local driver (default):**
```yaml
volumes:
  data:
    driver: local
```

**Custom drivers (if installed):**
```yaml
volumes:
  nfs-data:
    driver: nfs
    driver_opts:
      server: 192.168.1.100
      device: :/exports/data
```

## Configs and Secrets

### Configs (Non-sensitive Configuration)

**From files:**
```yaml
configs:
  app-config:
    file: ./config/app.yaml
  
  nginx-config:
    file: ./nginx.conf
    mode: "0644"              # File permissions
    uid: "1000"               # File owner UID
    gid: "1000"               # File owner GID

services:
  web:
    configs:
      - source: app-config
        target: /etc/app/config.yaml
      - source: nginx-config
        target: /etc/nginx/nginx.conf
        mode: 0444            # Read-only
```

**External configs:**
```yaml
configs:
  external-config:
    external: true
  
  named-external:
    external: true
    name: actual-config-name
```

### Secrets (Sensitive Data)

**From files:**
```yaml
secrets:
  db-password:
    file: ./secrets/db-pass.txt
  
  api-key:
    file: ./secrets/api-key.txt

services:
  api:
    secrets:
      - source: db-password
        target: /run/secrets/db_password
        mode: 0400            # Owner read-only
      
      - source: api-key
        target: /run/secrets/api_key
        uid: "1000"
        gid: "1000"
```

**External secrets:**
```yaml
secrets:
  tls-cert:
    external: true
  
  tls-key:
    external: true
    name: tls-private-key
```

**Secrets from environment (not recommended for production):**
```yaml
secrets:
  api-key:
    external: true
    environment: API_KEY_ENV_VAR
```

## Include

Include other compose files as dependencies:

```yaml
include:
  - path: ./common.yaml       # Relative path
  - path: ./services/*.yaml   # Glob pattern
  - path: ../base/base.yaml   # Parent directory
    envfile: .env.staging
```

**Use case:** Share common service definitions across multiple projects.

## Extensions

Add custom fields without validation errors:

```yaml
services:
  web:
    image: nginx
    x-my-extension:
      custom-field: value
      another-field: data
    
  api:
    image: myapi
    x-trivy:
      ignore-unfixed: true
      severity: HIGH,CRITICAL
```

Fields starting with `x-` are ignored by podman-compose but preserved for custom tools.

## Complete Example

```yaml
name: webapp

services:
  frontend:
    build:
      context: ./frontend
      target: production
    ports:
      - "80:80"
      - "443:443"
    environment:
      - NODE_ENV=production
      - API_URL=http://backend:3000
    volumes:
      - static-files:/var/www/static
    networks:
      - public
      - internal
    depends_on:
      backend:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 512M
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    build:
      context: ./backend
    environment:
      - DATABASE_URL=postgres://db:5432/app
      - REDIS_URL=redis://cache:6379
      - SECRET_KEY_FILE=/run/secrets/secret_key
    networks:
      - internal
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    secrets:
      - secret_key
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - internal
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 2G

  cache:
    image: redis:7-alpine
    networks:
      - internal
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  worker:
    profile: background
    build: ./backend
    command: celery -A app worker -l info
    environment:
      - CELERY_BROKER_URL=redis://cache:6379
    networks:
      - internal
    depends_on:
      - cache

networks:
  public:
    driver: bridge
  internal:
    driver: bridge
    internal: true

volumes:
  db-data:
  redis-data:
  static-files:

configs:
  app-config:
    file: ./config/app.yaml

secrets:
  db_password:
    file: ./secrets/db_password.txt
  secret_key:
    file: ./secrets/secret_key.txt
```

## Validation and Debugging

**Validate compose file:**
```bash
podman-compose config --quiet
```

**View parsed configuration:**
```bash
podman-compose config
```

**List services:**
```bash
podman-compose config --services
```

**Debug mode:**
```bash
podman-compose --verbose up
```
