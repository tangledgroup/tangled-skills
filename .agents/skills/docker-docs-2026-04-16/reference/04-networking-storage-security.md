# Docker Networking, Storage, and Security

## Networking

### Network Drivers

| Driver | Scope | Use Case |
|--------|-------|----------|
| `bridge` | Single host | Default for standalone containers. User-defined bridges provide DNS resolution. |
| `overlay` | Multi-host | Swarm/Kubernetes clusters. Containers on different hosts can communicate. |
| `host` | Single host | Container shares host network stack. No isolation. Best performance. |
| `macvlan` | Single host | Each container gets a unique MAC address on the physical network. |
| `ipvlan` | Single host | Layer 2/3 network virtualization. |
| `none` | Single host | No networking. Only loopback interfaces. |

### Bridge Network (Default)

When Docker starts, it creates a default bridge network called `bridge`.

**Default bridge limitations:**
- Containers can only communicate by IP address
- No automatic DNS resolution between containers
- Must use `--link` (legacy) for name-based communication

**User-defined bridges (recommended):**
- Automatic DNS resolution between containers by name
- Better isolation — only connected containers can communicate
- Can attach/detach containers on the fly
- Configurable subnets and gateways

```console
# Create a user-defined bridge network
docker network create --driver bridge my-network

# Run containers on the same network
docker run -d --name web --network my-network nginx
docker run -d --name db --network my-network postgres

# Containers can now resolve each other by name
# web container can reach db at hostname "db"
```

### Overlay Network (Swarm)

Required for multi-host communication in Swarm mode.

```console
# Create an overlay network
docker network create --driver overlay --attachable my-overlay-net

# Connect standalone containers to overlay
docker network connect my-overlay-net standalone-container
```

**Overlay features:**
- Automatic service discovery within the swarm
- Encrypted traffic (swarm internal)
- Supports ingress and routing mesh

### Port Publishing

```console
# Publish to all interfaces
docker run -p 8080:80 nginx

# Publish to specific IP (localhost only)
docker run -p 127.0.0.1:8080:80 nginx

# Publish multiple ports
docker run -p 80:80 -p 443:443 nginx

# Publish with protocol specification
docker run -p 8080:80/tcp -p 53:53/udp nginx

# Random host port assignment
docker run -P nginx    # All exposed ports get random host ports
```

**Port mapping formats:**
| Format | Description |
|--------|-------------|
| `"hostPort:containerPort"` | Map specific host port |
| `"hostIP:hostPort:containerPort"` | Bind to specific IP |
| `"hostPort:containerPort/protocol"` | Specify TCP or UDP |

### Network Inspection

```console
# List networks
docker network ls

# Inspect a network
docker network inspect my-network

# Filter by driver
docker network ls --filter driver=bridge

# Disconnect/connect containers
docker network disconnect my-network web
docker network connect my-network web
```

---

## Storage and Volumes

### Storage Drivers

| Driver | Description | Best For |
|--------|-------------|----------|
| `overlay2` | Copy-on-write, stacked layers | Linux (default) |
| `fuse-overlayfs` | FUSE-based overlay | Rootless mode on older kernels |
| `vfs` | Very simple, no kernel dependencies | Environments without native overlay support |
| `btrfs` | BTRFS-based storage | BTRFS filesystems |
| `zfs` | ZFS-based storage | ZFS filesystems |

**Check current driver:**
```console
docker info | grep Storage
# Output: Storage Driver: overlay2
```

### Volumes vs. Bind Mounts vs. Tmpfs

| Type | Host Location | Managed By | Performance | Use Case |
|------|--------------|------------|-------------|----------|
| **Volume** | `/var/lib/docker/volumes/` (Linux) | Docker | Best | Persistent data, databases |
| **Bind mount** | Any host path | User | Good | Source code, config files |
| **Tmpfs** | Host memory | Ephemeral | Fastest | Secrets, cache, temp files |

### Volume Management

```console
# List volumes
docker volume ls

# Create a named volume
docker volume create my-volume

# Inspect a volume
docker volume inspect my-volume

# Remove a volume
docker volume rm my-volume

# Remove all unused volumes
docker volume prune
```

### Using Volumes in Containers

**Via `-v` / `--volume` flag:**

```console
# Named volume
docker run -v my-volume:/app/data nginx

# Bind mount (host path)
docker run -v ./src:/app/src nginx

# Read-only bind mount
docker run -v ./config:/etc/app:ro nginx

# Anonymous volume (no name, Docker manages it)
docker run -v /app/data nginx
```

**Via `--mount` flag (more explicit):**

```console
# Named volume
docker run --mount type=volume,source=my-volume,target=/app/data nginx

# Bind mount
docker run --mount type=bind,source=./src,target=/app/src nginx

# Read-only bind mount
docker run --mount type=bind,source=./config,target=/etc/app,readonly nginx

# Tmpfs (no persistence)
docker run --mount type=tmpfs,target=/tmp,tmpfs-size=100m nginx
```

**`--mount` vs `-v` comparison:**

| Feature | `-v` | `--mount` |
|---------|------|-----------|
| Syntax | Short, comma-separated | Verbose, key=value |
| Read-only | `:ro` suffix | `readonly=true` |
| Multiple volumes | Hard to read | Clear and explicit |
| Recommended for | Quick use | Complex configurations |

### Volume Drivers

Docker supports pluggable volume drivers for remote storage.

```console
# List volume drivers
docker plugin ls

# Create a volume with a specific driver
docker volume create --driver flocker my-flocker-vol
```

**Built-in drivers:** `local` (default)
**Third-party drivers:** Flocker, S3FS, Ceph RBD, etc.

---

## Security

### Container Isolation

Docker containers use Linux kernel features for isolation:

| Feature | Purpose |
|---------|---------|
| **Namespaces** | Isolate process tree, network, mounts, UTS, IPC, PID |
| **cgroups** | Limit resource usage (CPU, memory, I/O) |
| **Seccomp** | Filter system calls available to the container |
| **AppArmor / SELinux** | Mandatory access control profiles |
| **Capability dropping** | Remove unnecessary Linux capabilities |

### Running as Non-Root

```dockerfile
# In Dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

```console
# At runtime
docker run --user 1000:1000 nginx
```

### Dropping Capabilities

```console
# Drop all capabilities, add back only what's needed
docker run \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  nginx
```

**Common capabilities:**

| Capability | Purpose |
|------------|---------|
| `NET_BIND_SERVICE` | Bind to ports below 1024 |
| `SYS_PTRACE` | Debug processes |
| `NET_RAW` | Use raw sockets |
| `DAC_OVERRIDE` | Bypass file permission checks |

### Security Scanning with Docker Scout

```console
# Scan an image for vulnerabilities
docker scout cves myapp:latest

# Compare images
docker scout compare --to myapp:latest myapp:v1.0

# Generate SBOM
docker scout sbom myapp:latest > sbom.json

# Quick remediation suggestions
docker scout quickfix myapp:latest
```

### Docker Hardened Images (DHI)

Minimal, secure base images with near-zero CVEs:

```console
# Pull a DHI image
docker pull docker.io/library/python:3.13-dhi
docker pull docker.io/library/node:20-dhi
docker pull docker.io/library/alpine:3.20-dhi
```

### Image Signing (Docker Content Trust)

```console
# Enable content trust
export DOCKER_CONTENT_TRUST=1

# Push a signed image
docker push myapp:latest

# Verify a signed image
docker inspect --format='{{.Signatures}}' myapp:latest
```

### Resource Constraints

```console
# Memory limits
docker run --memory=512m --memory-swap=1g nginx
# --memory: hard limit (container killed if exceeded)
# --memory-swap: swap limit (must be >= memory)

# CPU limits
docker run --cpus=1.5 nginx          # Max 1.5 CPUs
docker run --cpu-shares=512 nginx    # Relative weight (default 1024)
docker run --cpu-period=100000 \     # CFS period (microseconds)
           --cpu-quota=50000 nginx   # CFS quota

# CPUset (specific CPUs)
docker run --cpuset-cpus="0,2" nginx

# I/O limits
docker run --blkio-weight=500 nginx
```

### Health Checks

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

```console
# Check container health status
docker inspect --format='{{.State.Health.Status}}' web

# Manually trigger health check
docker inspect --format='{{.State.Health.LastCheck}}' web
```

**Health states:** `starting` → `healthy` or `unhealthy`

### Security Checklist

| Check | Command/Config |
|-------|---------------|
| Run as non-root | `USER <user>` in Dockerfile |
| Use specific tags | `nginx:1.25-alpine` not `nginx:latest` |
| Scan for CVEs | `docker scout cves <image>` |
| Use DHI images | `docker pull docker.io/library/python:3.13-dhi` |
| Drop capabilities | `--cap-drop=ALL --cap-add=NET_BIND_SERVICE` |
| Set memory limits | `--memory=512m` |
| Read-only root fs | `--read-only` |
| Use secrets | Docker secrets or mount from host |
| Health checks | `HEALTHCHECK` in Dockerfile |
| .dockerignore | Exclude unnecessary files from build context |

---

## Docker Engine Configuration

### daemon.json Locations

| OS | Path |
|----|------|
| Linux (regular) | `/etc/docker/daemon.json` |
| Linux (rootless) | `~/.config/docker/daemon.json` |
| Windows | `C:\ProgramData\docker\config\daemon.json` |

### Common Configuration Options

```json
{
  "registry-mirrors": ["https://mirror.example.com"],
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "iptables": true,
  "ip-forward": true,
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    }
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "default-runtime": "runc",
  "runtimes": {
    "crun": {
      "path": "/usr/bin/crun"
    }
  },
  "features": {
    "buildkit": true
  }
}
```

### Restarting the Daemon

```console
# Linux (systemd)
sudo systemctl restart docker

# Check daemon status
sudo systemctl status docker

# View daemon logs
journalctl -u docker.service -f
```
