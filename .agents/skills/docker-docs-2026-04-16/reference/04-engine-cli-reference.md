# Docker Engine and CLI Reference

## Core Commands

### docker build

Build an image from a Dockerfile:
```bash
docker build -t myapp:latest .
docker build -f Dockerfile.prod -t myapp:prod ./src
docker build --build-arg VERSION=1.0 --target builder -t myapp:build .
docker build --platform linux/amd64,linux/arm64 -t myapp:multi .
```

Options:
- `-t, --tag` — Name and optionally a tag
- `-f, --file` — Dockerfile path
- `--build-arg` — Set build-time variables
- `--target` — Build to specific target stage
- `--platform` — Set platform if server is multi-platform capable
- `--no-cache` — Do not use cache
- `--progress=plain|auto` — Progress output format
- `--quiet, -q` — Suppress build output

### docker run

Create and start a container:
```bash
docker run -d --name web -p 8080:80 nginx
docker run -it --rm alpine sh
docker run -v data:/var/lib/data --network mynet postgres
docker run --gpus all nvidia/cuda:12.0-base
docker run --memory=512m --cpus=1.5 redis
```

Common options:
- `-d` — Detached mode
- `-it` — Interactive + TTY
- `--name` — Container name
- `-p, --publish` — Publish port (`host:container`)
- `-P` — Publish all exposed ports
- `-v, --volume` — Bind mount or named volume
- `--mount` — Mount (more explicit syntax)
- `-e, --env` — Set environment variable
- `--env-file` — Read env from file
- `--network` — Connect to network
- `--restart` — Restart policy
- `--rm` — Remove container on exit
- `--user` — Username or UID
- `--workdir, -w` — Working directory
- `--memory, -m` — Memory limit
- `--cpus` — CPU quota
- `--gpus` — GPU devices
- `--privileged` — Full privileges
- `--read-only` — Read-only root filesystem
- `--health-cmd` / `--health-interval` / `--health-timeout` — Health check
- `--entrypoint` — Override entrypoint
- `--hostname` — Container hostname
- `--dns` — Custom DNS servers
- `--cap-add` / `--cap-drop` — Linux capabilities
- `--security-opt` — Security options

### docker container

Manage containers:
```bash
docker container ls                          # List running
docker container ls -a                       # List all
docker container inspect web                 # Inspect details
docker container logs web                    # View logs
docker container logs -f --tail 100 web      # Follow last 100 lines
docker container exec -it web sh             # Execute command
docker container top web                     # Running processes
docker container stats                       # Resource usage
docker container stop web                    # Graceful stop
docker container kill web                    # Force kill
docker container rm web                      # Remove
docker container prune                       # Remove stopped containers
```

### docker image

Manage images:
```bash
docker image ls                              # List images
docker image pull nginx:latest               # Pull image
docker image build -t myapp .                # Build image
docker image tag myapp:latest registry/myapp:v1
docker image push registry/myapp:v1          # Push to registry
docker image inspect nginx                   # Inspect
docker image history nginx                   # Layer history
docker image rm nginx                        # Remove
docker image prune                           # Remove dangling
docker image save -o backup.tar nginx        # Save to tar
docker image load -i backup.tar              # Load from tar
```

### docker volume

Manage persistent data:
```bash
docker volume ls                             # List volumes
docker volume create mydata                  # Create
docker volume inspect mydata                 # Inspect
docker volume rm mydata                      # Remove
docker volume prune                          # Remove unused
```

### docker network

Manage networks:
```bash
docker network ls                            # List networks
docker network create mynet                  # Create bridge network
docker network create -d overlay myoverlay   # Create overlay network
docker network inspect mynet                 # Inspect
docker network connect mynet container       # Connect container
docker network disconnect mynet container    # Disconnect
docker network rm mynet                      # Remove
docker network prune                         # Remove unused
```

### docker context

Manage connections to Docker engines:
```bash
docker context ls                            # List contexts
docker context create remote --docker "host=ssh://user@host"
docker context use remote                    # Switch context
docker context rm remote                     # Remove
```

### docker system

System information and cleanup:
```bash
docker system info                           # System details
docker system df                             # Disk usage
docker system df -v                          # Detailed disk usage
docker system prune                          # Remove unused data
docker system prune -a                       # Remove all unused
docker system events                         # Real-time events
```

### docker login / logout

Registry authentication:
```bash
docker login                                 # Login to Docker Hub
docker login myregistry.example.com          # Login to custom registry
docker logout                                # Logout
```

## Mount Syntax

The `--mount` flag provides more readable mount specification:

```bash
# Bind mount
docker run --mount type=bind,source=/host/path,target=/container/path nginx

# Named volume
docker run --mount type=volume,source=mydata,target=/data postgres

# tmpfs
docker run --mount type=tmpfs,target=/tmp,tmpfs-size=100M nginx

# Bind mount with options
docker run --mount type=bind,source=. ,target=/app,readonly nginx
```

## Restart Policies

- `no` — Default, don't restart
- `always` — Always restart
- `on-failure[:max-retries]` — Restart on non-zero exit
- `unless-stopped` — Restart unless explicitly stopped

## Resource Constraints

```bash
docker run --memory=512m --memory-swap=1g --cpus=1.5 --cpu-shares=512 nginx
docker run --pids-limit=100 nginx
docker run --ulimit nofile=1024:2048 nginx
```

## Docker Daemon Configuration

Configuration file: `/etc/docker/daemon.json`

```json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-address-pools": [
    {
      "base": "172.80.0.0/16",
      "size": 24
    }
  ],
  "data-root": "/var/lib/docker",
  "insecure-registries": ["registry.internal:5000"],
  "registry-mirrors": ["https://mirror.example.com"],
  "live-restore": true
}
```

## Storage Drivers

- **overlay2** — Default on most Linux distributions (requires kernel 4.0+)
- **btrfs** — B-tree file system
- **zfs** — ZFS file system
- **vfs** — Filesystem-level copying (slowest, for debugging)

## Logging Drivers

- **json-file** — Default, JSON formatted log files
- **journald** — Systemd journal
- **syslog** — Syslog daemon
- **gelf** — Graylog Extended Log Format
- **fluentd** — Fluentd forward protocol
- **awslogs** — Amazon CloudWatch Logs
- **splunk** — Splunk HTTP Event Collector
- **etwlogs** — Windows Event Tracing
- **none** — Disable logging

## Proxy Configuration

Set via systemd drop-in or environment:
```bash
# In /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=http://proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1,.internal"
```
