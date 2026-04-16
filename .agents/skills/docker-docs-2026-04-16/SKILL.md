---
name: docker-docs-2026-04-16
description: Comprehensive reference for Docker platform including Docker Engine, Docker Desktop, Docker Compose, Docker Build/BuildKit, Docker Swarm, Dockerfile syntax, networking, volumes, security, and Docker Hub. Use when building containerized applications, writing Dockerfiles, configuring multi-container stacks with Compose, setting up container orchestration, managing images and registries, or troubleshooting Docker environments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026.4.16"
tags:
  - containers
  - docker-engine
  - docker-desktop
  - docker-compose
  - dockerfile
  - buildkit
  - swarm
  - kubernetes
  - container-orchestration
  - container-security
category: devops
external_references:
  - https://docs.docker.com/
---

# Docker Documentation Reference (2026-04-16)

## Overview

This skill provides comprehensive reference material from the official [Docker documentation](https://docs.docker.com/) repository. It covers the entire Docker platform including Docker Engine, Docker Desktop, Docker Compose, Docker Build/BuildKit, Docker Swarm, container networking, storage, security, and Docker Hub.

The Docker documentation is organized into four main sections:
- **Get Started** — Installation guides, core concepts (containers, images, registries), and a hands-on workshop
- **Guides** — In-depth tutorials for common workflows (databases, orchestration, CI/CD, security, AI/ML)
- **Reference** — CLI commands, Dockerfile syntax, Compose file specification, glossary
- **Manuals** — Product-specific documentation (Docker Desktop, Docker Build, Swarm, Engine internals)

## When to Use

Use this skill when:
- Writing or debugging `Dockerfile` instructions
- Configuring multi-container applications with `docker compose`
- Setting up container orchestration (Swarm or Kubernetes)
- Understanding Docker networking drivers (bridge, overlay, host, macvlan, ipvlan, none)
- Managing volumes and storage drivers
- Configuring the Docker daemon (`daemon.json`)
- Working with Docker Build/BuildKit for multi-stage builds and multi-platform images
- Publishing/pulling images to/from registries (Docker Hub or custom)
- Setting up resource constraints (memory limits, CPU limits, cgroups)
- Understanding container security best practices
- Troubleshooting Docker Engine issues

## Core Concepts

### Containers vs. Images vs. Volumes

| Concept | Description |
|---------|-------------|
| **Container** | An isolated process running on the host, with its own filesystem, network, and PID namespace. Created from an image. |
| **Image** | A read-only template with instructions for creating a container. Composed of stacked layers (each layer = one Dockerfile instruction). Immutable once created. |
| **Volume** | Persistent storage managed by Docker, stored outside the container's writable layer. Survives container removal. |
| **Bind Mount** | Maps a host filesystem path into a container. Tightly coupled to the host OS. |

### Container Lifecycle

```
docker pull <image>          # Download image from registry
docker run <image>           # Create and start a new container
docker ps                    # List running containers
docker stop <container>      # Stop a running container
docker start <container>     # Start a stopped container
docker rm <container>        # Remove a stopped container
docker rmi <image>           # Remove an image
```

### Docker Architecture

Docker uses a client-server architecture:
- **Docker Client** (`docker` CLI) — Sends commands to the daemon
- **Docker Daemon** (`dockerd`) — Receives and executes commands, manages objects (images, containers, networks, volumes)
- **REST API** — Interface between the CLI and daemon
- **Registry** — Stores Docker images (Docker Hub is the default)

### Build Architecture (Buildx + BuildKit)

- **Buildx** — The CLI client for running builds. `docker build` is a wrapper around `docker buildx build`.
- **BuildKit** — The server/backend that executes build workloads. Resolves Dockerfile instructions and executes build steps.
- **Builders** — BuildKit daemon instances. Docker Engine creates a default builder automatically.

## Installation / Setup

### Get Docker

Choose the appropriate installation path:

| Platform | Product | Link |
|----------|---------|------|
| Mac | Docker Desktop for Mac | `/desktop/setup/install/mac-install/` |
| Windows | Docker Desktop for Windows | `/desktop/setup/install/windows-install/` |
| Linux | Docker Desktop for Linux | `/desktop/setup/install/linux/` |
| Linux (Engine only) | Docker Engine | `/engine/install/` |

### Docker Desktop vs. Docker Engine

- **Docker Desktop** — A full application including Docker Engine, Docker CLI, Docker Compose, Docker Buildx, Kubernetes, Docker Scout, and a GUI dashboard. Recommended for development.
- **Docker Engine** — The core container runtime + CLI. Installed manually on servers/production. No GUI.

## Usage Examples

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

## Advanced Topics

### Compose File Interpolation

Compose files support variable interpolation using shell-like syntax:

```yaml
services:
  web:
    image: ${REGISTRY:-docker.io}/myapp:${TAG:-latest}
```

Variables can be provided via:
- Environment file (`.env` by default)
- Shell environment variables
- Command-line `--env-file` flag

### Compose Profiles

Services can be assigned to profiles for conditional startup:

```yaml
services:
  redis:
    image: redis:alpine
    profiles: ["cache"]
  web:
    build: .
  monitoring:
    image: grafana/grafana
    profiles: ["monitoring", "cache"]
```

Start with specific profiles: `docker compose --profile cache up -d`

### Compose File Extensions / Merging

Multiple Compose files are merged, with later files overriding earlier ones:

```console
$ docker compose -f base.yaml -f override.yaml up -d
```

Use the `extends` keyword to share service definitions across files.

### BuildKit Features

- **Secrets** — Pass secrets to builds without exposing them in image layers:
  ```dockerfile
  RUN --mount=type=secret,id=mysecret cat /run/secrets/mysecret
  ```

- **SSH forwarding** — Forward SSH agent during build:
  ```console
  $ docker buildx build --ssh default .
  ```

- **Cache mounts** — Mount cache volumes for package managers:
  ```dockerfile
  RUN --mount=type=cache,target=/root/.npm npm install
  ```

- **Entitlements** — Special permissions (`network.host`, `security.insecure`, `device`):
  ```console
  $ docker buildx build --allow network.host .
  ```

### Dockerfile Best Practices

1. Use multi-stage builds to minimize final image size
2. Order instructions from least to most frequently changing (leverage build cache)
3. Combine `RUN` commands with `&&` to reduce layers
4. Use `.dockerignore` to exclude unnecessary files from build context
5. Pin base image versions (avoid `:latest`)
6. Use `COPY` instead of `ADD` unless you need tar extraction or URL fetching
7. Set `WORKDIR` instead of using `cd` in `RUN` commands
8. Use `ARG` for build-time variables, `ENV` for runtime variables
9. Clean up temporary files in the same `RUN` layer (e.g., `apt-get clean`)
10. Define a `HEALTHCHECK` for production containers

### Docker Swarm Concepts

| Concept | Description |
|---------|-------------|
| **Node** | A Docker Engine instance that is part of a swarm cluster |
| **Service** | A high-level abstraction that runs tasks on swarm nodes |
| **Task** | A container running as part of a service |
| **Replicated Service** | Runs a specified number of task copies across nodes |
| **Global Service** | Runs one task per node |
| **Rolling Update** | Gradually replaces old tasks with new ones |

### Docker Compose vs. Swarm

- **Compose** is for defining and running single-host multi-container applications
- **Swarm** is for orchestrating containers across multiple hosts
- Swarm uses a subset of the Compose file format (with `deploy` section additions)
- Use `docker stack deploy` to deploy Compose files to Swarm

## References

### Official Documentation
- Main documentation: https://docs.docker.com/
- GitHub repository: https://github.com/docker/docs
- Docker Engine API reference: https://docs.docker.com/engine/api/
- Dockerfile specification: https://docs.docker.com/engine/reference/builder/
- Compose Specification: https://github.com/compose-spec/compose-spec

### CLI References
- `docker buildx build`: https://docs.docker.com/build/concepts/dockerfile/ + BuildKit docs
- `docker compose`: https://docs.docker.com/compose/
- Dockerfile instructions: https://docs.docker.com/engine/reference/builder/
- Compose file reference: https://docs.docker.com/compose/compose-file/

### Related Projects
- Buildx: https://github.com/docker/buildx
- Compose: https://github.com/docker/compose
- Moby (Docker Engine): https://github.com/moby/moby
- Dockerfile spec: https://github.com/moby/buildkit/tree/master/frontend/dockerfile
- Awesome Compose examples: https://github.com/docker/awesome-compose

### Key Content Sections in This Repository

**Get Started:**
- `/get-started/get-docker/` — Installation for all platforms
- `/get-started/docker-concepts/the-basics/` — What is a container, image, registry, Compose
- `/get-started/docker-concepts/building-images/` — Writing Dockerfiles, multi-stage builds, image layers
- `/get-started/workshop/` — 45-minute hands-on workshop

**Guides:**
- `/guides/databases/` — Running containerized databases (MySQL, PostgreSQL, etc.)
- `/guides/orchestration/` — Kubernetes and Swarm deployment overview
- `/guides/kube-deploy/` — Deploy to Kubernetes tutorial
- `/guides/swarm-deploy/` — Deploy to Swarm tutorial

**Reference:**
- `/reference/dockerfile.md` — Full Dockerfile instruction reference
- `/reference/compose-file/` — Compose file specification (services, networks, volumes, etc.)
- `/reference/glossary.md` — Docker terminology glossary

**Manuals:**
- `/manuals/build/` — Docker Build, BuildKit, buildx, multi-stage builds, caching, exporters
- `/manuals/compose/` — Docker Compose features, how-tos, reference
- `/manuals/engine/` — Docker Engine internals: containers, daemon, networking, swarm
- `/manuals/desktop/` — Docker Desktop installation and configuration
- `/manuals/docker-hub/` — Docker Hub usage, repositories, organizations
- `/manuals/build-cloud/` — Docker Build Cloud remote builds
