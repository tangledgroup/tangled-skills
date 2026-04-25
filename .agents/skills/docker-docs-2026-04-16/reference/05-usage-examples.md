# Usage Examples

### Running a Container

```console
# Run a container in detached mode with port mapping
$ docker run --name my-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=mydb -d -p 3306:3306 mysql:latest

# Run interactively
$ docker run -it ubuntu bash

# Run with bind mount and resource limits
$ docker run -d --name web \
  -v ./src:/app/src \
  --memory=512m --cpus=1.0 \
  -p 8080:80 nginx:latest
```

### Writing a Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13
WORKDIR /usr/local/app

# Install dependencies (separate layer for caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src
EXPOSE 8080

# Run as non-root user
RUN useradd app
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Common Dockerfile instructions:**

| Instruction | Description |
|-------------|-------------|
| `FROM <image>` | Base image for the build stage |
| `RUN <command>` | Execute commands in a new layer |
| `COPY <src> <dest>` | Copy files from build context |
| `WORKDIR <path>` | Set working directory |
| `ENV <key>=<value>` | Set environment variables |
| `EXPOSE <port>` | Document which port the container listens on |
| `CMD ["cmd", "arg"]` | Default command when container starts (only last CMD takes effect) |
| `ENTRYPOINT ["cmd"]` | Make container behave like an executable |
| `USER <user>` | Set default user for subsequent instructions |
| `VOLUME ["/path"]` | Create a mount point for volumes |
| `ARG <name>` | Build-time variable (not available at runtime) |
| `LABEL <key>=<value>` | Add metadata to the image |
| `HEALTHCHECK CMD <cmd>` | Define a health check command |
| `ADD <src> <dest>` | Copy files, with optional tar extraction and URL support |
| `SHELL <shell>` | Set default shell for shell-form commands |

### Multi-Stage Builds

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN go build -o /bin/hello ./main.go

FROM scratch
COPY --from=build /bin/hello /bin/hello
CMD ["/bin/hello"]
```

Multi-stage builds let you copy artifacts from earlier stages into a final, minimal image. This keeps production images small and secure by excluding build tools.

### Docker Compose

**Basic `compose.yaml`:**

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api

  api:
    build:
      context: ./api
      target: builder
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:18
    environment:
      POSTGRES_USER: user
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

**Common Docker Compose commands:**

```console
# Start all services in detached mode
$ docker compose up -d

# Build and start
$ docker compose up --build -d

# View logs
$ docker compose logs -f api

# Scale a service
$ docker compose up -d --scale api=3

# Stop and remove all containers and networks
$ docker compose down

# Stop but keep volumes
$ docker compose down --volumes

# Run a one-off command
$ docker compose run --rm api bash

# Check configuration
$ docker compose config

# List running projects
$ docker compose ls
```

**Compose file top-level elements:**

| Element | Description |
|---------|-------------|
| `services` | Define containers (required) |
| `networks` | Define custom networks |
| `volumes` | Define named volumes |
| `configs` | Application configuration files |
| `secrets` | Sensitive data (passwords, keys) |

**Service attributes (most common):**

| Attribute | Description |
|-----------|-------------|
| `image` | Image name (or use `build` to build from Dockerfile) |
| `ports` | Port mappings (`"host:container"` or `"host:container/protocol"`) |
| `volumes` | Bind mounts or volume mounts |
| `environment` | Environment variables |
| `depends_on` | Service dependencies (controls start order) |
| `restart` | Restart policy (`no`, `always`, `on-failure`, `unless-stopped`) |
| `healthcheck` | Container health check definition |
| `deploy` | Deployment configuration (Swarm mode: replicas, resources, update config) |

### Docker Networking

**Network drivers:**

| Driver | Use Case |
|--------|----------|
| `bridge` | Default. Containers on same host communicate. User-defined bridges provide DNS resolution. |
| `host` | Container uses host networking directly. No isolation. |
| `overlay` | Multi-host communication. Required for Swarm mode. |
| `macvlan` | Assign a MAC address to each container, making it appear as a physical device. |
| `ipvlan` | Layer 2 or 3 network virtualization. |
| `none` | No networking. Container has only loopback interfaces. |

**Port publishing:**

```console
# Publish port to all interfaces
$ docker run -p 8080:80 nginx

# Publish to specific IP (localhost only)
$ docker run -p 127.0.0.1:8080:80 nginx

# Publish both TCP and UDP
$ docker run -p 8080:80/tcp -p 8080:80/udp nginx
```

> **Security note:** Publishing ports makes them accessible from the outside world by default. Use `127.0.0.1` binding for local-only access.

### Docker Swarm Mode

**Initializing a swarm:**

```console
# Initialize swarm (manager node)
$ docker swarm init --advertise-addr <MANAGER-IP>

# Get join commands
$ docker swarm join-token manager   # For managers
$ docker swarm join-token worker    # For workers

# Join as worker
$ docker swarm join --token <TOKEN> <MANAGER-IP>:2377
```

**Deploying with Swarm:**

```console
# Deploy a stack
$ docker stack deploy -c docker-compose.yml myapp

# List services
$ docker service ls

# Scale a service
$ docker service scale myapp_web=5

# View service logs
$ docker service logs myapp_web

# Roll out an update
$ docker service update --image nginx:1.25 myapp_web
```

### Docker Build / BuildKit

**Building images:**

```console
# Basic build
$ docker build -t myapp:latest .

# Multi-platform build
$ docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest --push .

# Build with cache from registry
$ docker buildx build --cache-from type=registry,ref=myapp:cache \
  --cache-to type=registry,ref=myapp:cache,mode=max --push .

# Load into local daemon
$ docker buildx build --load -t myapp:latest .

# Build with secrets (BuildKit feature)
$ docker buildx build --secret id=ssh,key=~/.ssh/id_rsa -t myapp:latest .
```

**Build drivers:**

| Driver | Description |
|--------|-------------|
| `docker` | Default. Uses BuildKit bundled with Docker daemon. |
| `docker-container` | Creates a dedicated BuildKit container. Supports more features. |
| `kubernetes` | Runs BuildKit as pods in Kubernetes. |
| `remote` | Connects to a manually managed BuildKit daemon. |

**Build caching:**

```console
# Use local cache directory
$ docker buildx build --cache-to type=local,dest=/tmp/build-cache .

# Export/import cache between builds
$ docker buildx build --output type=cacheonly .
```

### Docker Engine Resource Constraints

```console
# Memory limits
$ docker run --memory=512m --memory-swap=1g nginx

# CPU limits
$ docker run --cpus=1.5 --cpu-shares=512 nginx

# Shared memory
$ docker run --shm-size=2g nginx

# Ulimits
$ docker run --ulimit nofile=65536:65536 nginx
```

### Docker Hub / Image Distribution

```console
# Pull an image
$ docker pull nginx:latest

# Tag and push to registry
$ docker tag myapp:latest myuser/myapp:latest
$ docker push myuser/myapp:latest

# Login to registry
$ docker login

# Search images on Docker Hub
$ docker search nginx

# Image management
$ docker images                    # List local images
$ docker image inspect <image>    # Inspect image details
$ docker rmi <image>              # Remove an image
```

**Image layers are immutable.** Once created, they cannot be modified. New changes create new layers on top. This enables efficient caching and sharing across images.

### Docker Daemon Configuration

Configuration file: `/etc/docker/daemon.json` (Linux) or `C:\ProgramData\docker\config\daemon.json` (Windows).

```json
{
  "registry-mirrors": ["https://mirror.example.com"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "iptables": true,
  "live-restore": true,
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    }
  ]
}
```

**Key configuration options:**

| Option | Description |
|--------|-------------|
| `registry-mirrors` | Mirror registries for faster pulls |
| `storage-driver` | Storage backend (`overlay2`, `vfs`, etc.) |
| `log-driver` / `log-opts` | Container logging configuration |
| `live-restore` | Keep containers running when daemon restarts |
| `iptables` | Enable/disable Docker's iptables rules |
| `default-address-pools` | Default network address pools for user-defined networks |

### Security Best Practices

1. **Run as non-root** — Use `USER` instruction in Dockerfile, avoid running containers as root
2. **Use specific image tags** — Never use `:latest` in production; pin exact versions
3. **Scan images** — Use Docker Scout or Trivy to detect vulnerabilities
4. **Minimize image size** — Use multi-stage builds, slim/alpine base images, DHI (Docker Hardened Images)
5. **Limit resource usage** — Set memory and CPU constraints
6. **Use read-only filesystems** — `--read-only` flag where possible
7. **Drop capabilities** — Use `--cap-drop=ALL` and selectively add back what's needed
8. **Secrets management** — Use Docker secrets or external vaults, never hardcode in Dockerfile
9. **Network isolation** — Use user-defined bridge networks to isolate containers
10. **Health checks** — Define `HEALTHCHECK` to detect unhealthy containers

### Docker Desktop Key Features

- **GUI Dashboard** — Manage containers, images, volumes, and networks visually
- **Kubernetes integration** — One-click enable Kubernetes on your local machine
- **Docker Scout** — Built-in vulnerability scanning and remediation
- **Compose support** — Full Compose file support with one-click up/down
- **Resource management** — Configure CPU, memory, disk, and swap limits via Settings

### Docker Build Cloud

A remote build service that provides:
- Faster builds on cloud infrastructure
- Shared build cache across team members
- Native multi-platform builds without local cross-compilation tools
- Encrypted in-transit data

To use: connect a builder to your Docker account, then builds run remotely by default.
