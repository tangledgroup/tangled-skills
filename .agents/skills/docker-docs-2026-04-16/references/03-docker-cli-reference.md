# Docker CLI Reference

## Overview

This reference covers the most commonly used Docker CLI commands. The `docker` CLI is the primary interface for interacting with the Docker daemon.

**Source:** https://docs.docker.com/engine/reference/commandline/cli/

## General Syntax

```console
docker [OPTIONS] COMMAND [ARG...] [flags]
```

### Global Flags

| Flag | Description |
|------|-------------|
| `-H`, `--host` | Daemon socket(s) to connect to |
| `-D`, `--debug` | Enable debug mode |
| `-l`, `--log-level` | Log level (`debug`, `info`, `warn`, `error`, `fatal`) |
| `--tls` | Use TLS; implied by `--tlsverify` |
| `--tlscacert` | Trust certs signed only by CA |
| `--context` | Name of the context to use |

### Common Subcommands

| Command | Description |
|---------|-------------|
| `images` | List images |
| `ps` / `container ls` | List containers |
| `pull` | Pull an image from a registry |
| `push` | Push an image to a registry |
| `run` | Run a container |
| `build` / `buildx build` | Build an image |
| `compose` | Define and run multi-container apps |
| `system df` | Disk usage |
| `info` | Display system-wide information |
| `version` | Show version information |

---

## Container Commands

### docker run

Create and start a new container.

```console
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

**Most commonly used flags:**

| Flag | Description |
|------|-------------|
| `-d`, `--detach` | Run in detached mode (background) |
| `-it`, `--interactive --tty` | Keep stdin open and allocate a TTY |
| `-p`, `--publish` | Publish container port(s) to host |
| `-P`, `--publish-all` | Publish all exposed ports to random host ports |
| `-v`, `--volume` | Bind mount a volume |
| `--mount` | Mount a file/system (more verbose than -v) |
| `--name` | Assign a name to the container |
| `--rm` | Automatically remove the container when it exits |
| `--restart` | Restart policy (`no`, `always`, `on-failure`, `unless-stopped`) |
| `-e`, `--env` | Set environment variables |
| `--env-file` | Read in a file of environment variables |
| `--network` | Connect container to a network |
| `--link` | Link to another container (legacy, use networks) |
| `--memory` / `-m` | Memory limit (e.g., `512m`, `1g`) |
| `--cpus` | Number of CPUs |
| `--cpu-shares` | CPU shares (relative weight) |
| `--user` / `-u` | Username or UID |
| `--workdir` / `-w` | Working directory inside container |
| `--entrypoint` | Override the default entrypoint |
| `--health-cmd` | Health check command |
| `--cap-add` | Add Linux capability |
| `--cap-drop` | Drop Linux capability |
| `--read-only` | Mount root filesystem as read-only |
| `--shm-size` | Size of `/dev/shm` |

```console
# Run interactively
docker run -it ubuntu bash

# Run in detached mode with port mapping and volume
docker run -d --name web \
  -p 8080:80 \
  -v ./html:/usr/share/nginx/html \
  nginx:alpine

# Run with resource limits
docker run -d --name app \
  --memory=512m --cpus=1.0 \
  --restart=unless-stopped \
  myapp:latest

# Run and auto-remove on exit
docker run --rm ubuntu echo "hello"
```

### docker ps / container ls

List containers.

```console
docker ps [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `-a`, `--all` | Show all containers (including stopped) |
| `-q`, `--quiet` | Only show numeric IDs |
| `--filter` | Filter output (e.g., `status=running`) |
| `-n` | Show N most recent containers |

```console
docker ps                              # Running containers only
docker ps -a                           # All containers
docker ps -q                           # IDs only
docker ps --filter "name=web"          # Filter by name
docker ps --filter "status=exited"     # Stopped containers
```

### docker stop / start / restart

Manage container lifecycle.

```console
docker stop [OPTIONS] CONTAINER [CONTAINER...]   # Stop running containers (default 10s timeout)
docker start [OPTIONS] CONTAINER [CONTAINER...]  # Start stopped containers
docker restart [OPTIONS] CONTAINER [CONTAINER...] # Restart containers
docker kill [OPTIONS] CONTAINER [CONTAINER...]   # Kill a running container immediately
```

### docker rm / rmi

Remove containers and images.

```console
docker rm [OPTIONS] CONTAINER [CONTAINER...]     # Remove stopped containers
docker rmi [OPTIONS] IMAGE [IMAGE...]             # Remove images
docker system prune -a                            # Remove all unused images, containers, networks, volumes
```

| Flag | Description |
|------|-------------|
| `-f`, `--force` | Force removal (even running containers) |
| `-v`, `--volumes` | Remove anonymous volumes associated with the container |

### docker logs

View container output.

```console
docker logs [OPTIONS] CONTAINER
```

| Flag | Description |
|------|-------------|
| `-f`, `--follow` | Follow log output (like `tail -f`) |
| `-n`, `--tail` | Number of lines from the end (`all` for all) |
| `-t`, `--timestamps` | Show timestamps |
| `--details` | Show extra details provided to logs |

```console
docker logs -f web                    # Follow logs in real-time
docker logs --tail 50 web             # Last 50 lines
docker logs -t --tail 100 web         # Timestamps + last 100 lines
```

### docker exec

Execute a command in a running container.

```console
docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
```

| Flag | Description |
|------|-------------|
| `-it` | Interactive TTY |
| `-u` | User to run as |
| `--workdir` | Working directory inside container |

```console
docker exec -it web bash                    # Open shell in running container
docker exec web ls /app                     # Run a command and exit
docker exec -u root web apt-get update      # Run as root user
```

### docker inspect

Return low-level information about containers, images, volumes, etc.

```console
docker inspect [OPTIONS] NAME|ID [NAME|ID...]
```

| Flag | Description |
|------|-------------|
| `--format` | Format output with Go template |
| `-f` | Shorthand for `--format` |

```console
docker inspect web                                    # Full JSON output
docker inspect -f '{{.NetworkSettings.IPAddress}}' web  # Get IP address
docker inspect --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}' web
```

### docker cp

Copy files/folders between a container and the local filesystem.

```console
docker cp [OPTIONS] CONTAINER:SRC_PATH DEST_PATH
docker cp [OPTIONS] SRC_PATH CONTAINER:DEST_PATH
```

```console
docker cp web:/app/logs ./logs/           # Copy from container to host
docker cp ./config.yml web:/etc/app/      # Copy from host to container
```

---

## Image Commands

### docker images / image ls

List local images.

```console
docker images [OPTIONS] [REPOSITORY[:TAG]]
```

| Flag | Description |
|------|-------------|
| `-a`, `--all` | Show all images (including intermediate) |
| `--digests` | Show digests |
| `-q`, `--quiet` | Only show IDs |

### docker pull / push

Pull from or push to a registry.

```console
docker pull [OPTIONS] NAME[:TAG|@DIGEST]
docker push [OPTIONS] NAME[:TAG]
```

```console
docker pull nginx:alpine                          # Pull specific tag
docker pull nginx@sha256:abc123...               # Pull by digest (immutable)
docker push myuser/myapp:latest                   # Push to registry
```

### docker build / buildx build

Build an image from a Dockerfile.

```console
docker build [OPTIONS] PATH | URL | -
docker buildx build [OPTIONS] PATH | URL | -
```

**Common flags:**

| Flag | Description |
|------|-------------|
| `-t`, `--tag` | Name and optionally a tag (`name:tag`) |
| `-f`, `--file` | Path to Dockerfile (default: `PATH/Dockerfile`) |
| `--build-arg` | Set build-time variables |
| `--network` | Network mode for RUN instructions |
| `--progress` | Type of progress output (`auto`, `plain`, `tty`, `quiet`) |
| `--pull` | Always attempt to pull base image |
| `--no-cache` | Do not use cache when building |
| `--target` | Set the target build stage |
| `--platform` | Target platform(s) |
| `--push` | Push the built image to registry |
| `--load` | Load into local Docker daemon (docker buildx only) |
| `--secret` | Expose secrets to the build |

```console
# Basic build
docker build -t myapp:latest .

# Build with arguments
docker build --build-arg VERSION=1.0 --build-arg NODE_ENV=production -t myapp:1.0 .

# Multi-platform build with push
docker buildx build --platform linux/amd64,linux/arm64 \
  -t myuser/myapp:latest --push .

# Load into local daemon (cross-platform)
docker buildx build --platform linux/arm64 --load -t myapp:arm64 .
```

### docker tag / rmi

Tag and remove images.

```console
docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]
docker rmi [OPTIONS] IMAGE [IMAGE...]
```

```console
docker tag myapp:latest myuser/myapp:v1.0
docker rmi nginx:alpine
docker image prune -a   # Remove unused images
```

### docker save / load

Export and import images as tar archives.

```console
docker save -o myimage.tar myimage:tag
docker load -i myimage.tar
```

---

## Volume Commands

### docker volume

Manage named volumes.

```console
docker volume ls                                    # List volumes
docker volume create my-volume                      # Create a volume
docker volume inspect my-volume                     # Inspect a volume
docker volume rm my-volume                          # Remove a volume
docker volume prune                                 # Remove all unused local volumes
```

### docker system df

Show disk usage.

```console
docker system df
```

Output:
```
TYPE                TOTAL               ACTIVE              SIZE                RECLAIMABLE
Images              25                  10                  1.2GB               800MB (66%)
Containers          8                   5                   50MB                30MB (60%)
Local Volumes       15                  10                  500MB               200MB (40%)
Build Cache         -                   -                   200MB               200MB
```

---

## Network Commands

### docker network

Manage networks.

```console
docker network ls                                     # List networks
docker network create --driver bridge my-net          # Create a network
docker network inspect my-net                         # Inspect a network
docker network connect my-net web                     # Connect container to network
docker network disconnect my-net web                  # Disconnect container from network
docker network rm my-net                              # Remove a network
docker network prune                                  # Remove all unused networks
```

**Built-in drivers:** `bridge`, `host`, `overlay`, `macvlan`, `ipvlan`, `none`

---

## Docker Compose Commands

### docker compose

Define and run multi-container Docker applications.

```console
docker compose [OPTIONS] COMMAND [ARGS...]
```

**Global options:**

| Flag | Description |
|------|-------------|
| `-f`, `--file` | Specify an alternate compose file (default: `compose.yaml`) |
| `-p`, `--project-name` | Specify an alternate project name |
| `--profile` | Specify a profile to activate |
| `--env-file` | Specify an alternate env file |

**Main commands:**

| Command | Description |
|---------|-------------|
| `up` | Create and start containers |
| `down` | Stop and remove containers, networks |
| `start` | Start services |
| `stop` | Stop services |
| `restart` | Restart services |
| `ps` | List containers |
| `logs` | View output from containers |
| `build` | Build or rebuild services |
| `pull` | Pull service images |
| `push` | Push service images |
| `config` | Parse, resolve and render compose file |
| `exec` | Execute a command in a running container |
| `run` | Run a one-off command on a service |
| `scale` | Scale services |
| `cp` | Copy files between containers |
| `rm` | Remove stopped containers |
| `volumes` | List volumes |
| `images` | List images used by created containers |
| `version` | Show version info |

```console
# Start all services in detached mode
docker compose up -d

# Build and start
docker compose up --build -d

# Run with specific profiles
docker compose --profile monitoring up -d

# View logs for a specific service
docker compose logs -f api

# Scale a service to 5 instances
docker compose up -d --scale web=5

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Rebuild after Dockerfile changes
docker compose build && docker compose up -d
```

---

## Swarm Commands

### docker swarm

Initialize and manage swarm clusters.

```console
docker swarm init --advertise-addr <IP>   # Initialize as manager
docker swarm join --token <TOKEN> <MANAGER>:2377  # Join as worker/manager
docker swarm leave                        # Leave the swarm
docker swarm unlock                       # Unlock swarm
docker swarm unlock-key                   # View/rotate unlock key
```

### docker service

Manage services in a swarm.

```console
docker service create [OPTIONS] IMAGE [COMMAND] [ARG...]    # Create a new service
docker service ls                                           # List services
docker service inspect --format='{{.Name}}: {{.Endpoint.Spec.Ports}}' <service>  # Inspect
docker service update --image nginx:1.25 <service>          # Update a service
docker service scale <service>=<NUM>                        # Scale a service
docker service rm <service>                                 # Remove a service
```

**Create options:**

| Flag | Description |
|------|-------------|
| `--replicas` | Number of replicas |
| `--publish` | Publish container port to host |
| `--constraint` | Placement constraint |
| `--mount` | Add a bind mount or volume |
| `--env` | Set environment variables |
| `--mode` | Service mode (`replicated`, `global`) |

### docker node

Manage swarm nodes.

```console
docker node ls                          # List nodes
docker node inspect self                # Inspect current node
docker node promote <NODE>              # Promote worker to manager
docker node demote <NODE>               # Demote manager to worker
docker node update --availability drain <NODE>  # Drain a node (stop tasks)
```

### docker stack

Deploy and manage multi-service applications.

```console
docker stack deploy -c compose.yaml myapp   # Deploy a stack
docker stack ls                               # List stacks
docker stack ps myapp                         # List tasks in a stack
docker stack rm myapp                         # Remove a stack
docker stack services myapp                   # List services in a stack
```

---

## Buildx Commands

### docker buildx

Build extended with BuildKit features.

```console
docker buildx [OPTIONS] COMMAND [ARGS...]
```

| Command | Description |
|---------|-------------|
| `build` | Start a build |
| `ls` | List builders |
| `inspect` | Inspect a builder |
| `create` | Create a builder |
| `use` | Set the current builder |
| `rm` | Remove a builder |
| `boot` | Boot the selected builder instance |
| `stop` | Stop the selected builder instance |
| ` bake` | Build using HCL files (like Make for builds) |

```console
# Create a new builder with docker-container driver
docker buildx create --name mybuilder --driver docker-container --use

# List builders
docker buildx ls

# Multi-platform build and push
docker buildx build --platform linux/amd64,linux/arm64 \
  -t myapp:latest --push .

# Build in interactive mode (requires tty driver)
docker buildx create --name tty-builder --driver docker-container --use
```

---

## System Commands

### docker system

Manage Docker system resources.

```console
docker system df              # Disk usage
docker system info            # Display system-wide information
docker system events          # Get real-time events from the server
docker system prune [OPTIONS] # Remove unused data
docker system prune --all     # Remove all unused images, not just dangling ones
```

**Prune flags:**

| Flag | Description |
|------|-------------|
| `-a`, `--all` | Remove all unused images, not just dangling ones |
| `--filter` | Filter (e.g., `until=24h`) |
| `-f`, `--force` | Do not prompt for confirmation |

```console
docker system prune                           # Remove stopped containers, unused networks, dangling images
docker system prune -a                        # Also remove all unused images
docker system prune --volumes                 # Also remove anonymous volumes (CAUTION)
docker system events --filter 'type=container'  # Container events only
```

---

## Docker CLI Quick Reference Cheat Sheet

| Task | Command |
|------|---------|
| Run a container | `docker run -d --name myapp -p 80:80 nginx` |
| See running containers | `docker ps` |
| See all containers | `docker ps -a` |
| View logs | `docker logs -f myapp` |
| Execute in container | `docker exec -it myapp bash` |
| Stop a container | `docker stop myapp` |
| Remove a container | `docker rm myapp` |
| Pull an image | `docker pull nginx:alpine` |
| Build an image | `docker build -t myapp .` |
| Tag and push | `docker tag myapp user/myapp:v1 && docker push user/myapp:v1` |
| Remove unused resources | `docker system prune -a` |
| Multi-container app | `docker compose up -d` |
| Swarm deploy | `docker stack deploy -c compose.yaml myapp` |
