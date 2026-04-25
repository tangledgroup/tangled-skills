# Podman Core Concepts

This reference covers fundamental Podman operations including container lifecycle management, common workflows, networking basics, and volume management.

## Container Lifecycle

### Create a Container

```bash
# Create without starting
podman create --name mycontainer fedora /bin/bash

# Create with resource limits
podman create --name webapp \
  -p 8080:80 \
  -m 512M \
  --cpus=1.0 \
  nginx:latest
```

### Start a Container

```bash
# Start created container
podman start mycontainer

# Start and attach
podman start -a mycontainer

# Auto-remove on exit
podman run --rm fedora echo "temporary"
```

### Stop and Remove

```bash
# Stop gracefully (sends SIGTERM, waits 10s, then SIGKILL)
podman stop mycontainer

# Force immediate stop
podman kill mycontainer

# Remove stopped container
podman rm mycontainer

# Remove all stopped containers
podman container prune

# Force remove running container
podman rm -f mycontainer
```

### Restart

```bash
# Restart container
podman restart mycontainer

# Restart with timeout
podman restart --time=30 mycontainer
```

### Inspect and Debug

```bash
# Full JSON inspection
podman inspect mycontainer

# Extract specific fields
podman inspect --format '{{.State.Status}}' mycontainer
podman inspect --format '{{.NetworkSettings.IPAddress}}' mycontainer

# View container processes
podman top mycontainer

# Check resource usage
podman stats --no-stream mycontainer
```

## Common Operations

### Run Interactive Containers

```bash
# Interactive with pseudo-TTY
podman run -it fedora /bin/bash

# Keep STDIN open even without TTY
podman run -i fedora cat

# Both interactive and TTY
podman run -it --rm ubuntu:22.04 bash
```

### Execute Commands in Running Containers

```bash
# Execute command
podman exec mycontainer ls -la

# Interactive shell
podman exec -it mycontainer /bin/bash

# Run as different user
podman exec -u root mycommand whoami
```

### View Logs

```bash
# Follow logs (like docker logs -f)
podman logs -f mycontainer

# Show last 100 lines
podman logs --tail=100 mycontainer

# Show logs with timestamps
podman logs -t mycontainer

# Show logs since specific time
podman logs --since=20m mycontainer
podman logs --since=2024-01-15T10:30:00Z mycontainer

# Follow and show last 50 lines
podman logs -f --tail=50 mycontainer
```

### Copy Files

```bash
# Copy from host to container
podman cp file.txt mycontainer:/tmp/file.txt

# Copy from container to host
podman cp mycontainer:/etc/hosts ./hosts.backup

# Copy directory
podman cp ./config/ mycontainer:/app/config/
```

### Manage Container Resources

```bash
# Set memory limit
podman run -m 512M fedora free -m

# Set CPU limit
podman run --cpus=1.5 fedora stress --cpu 2

# Set both CPU and memory
podman run --cpus=1.0 -m 1G nginx

# Update resource limits on running container
podman update --memory=1G mycontainer
```

## Listing and Filtering

### List Containers

```bash
# Running containers only
podman ps

# All containers (including stopped)
podman ps -a

# Detailed output
podman ps --format table "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"

# Filter by status
podman ps --filter status=running
podman ps --filter status=exited

# Filter by name
podman ps --filter name=myapp

# Filter by image
podman ps --filter ancestor=fedora
```

### List Images

```bash
# All images
podman images

# Dangling images (untagged)
podman images -f "dangling=true"

# Specific repository
podman images fedora

# Output as JSON
podman images --format json
```

## Networking Basics

### Network Types

Podman supports multiple network drivers:

- **bridge** (default): Creates bridge network with NAT
- **macvlan**: Direct MAC address on physical interface
- **ipvlan**: Lighter weight than macvlan
- **host**: Container shares host network namespace
- **none**: No networking

### Default Networks

```bash
# List networks
podman network ls

# Inspect default network
podman network inspect podman

# Default networks created by Podman:
# - podman (bridge)
# - slirp4netns (for rootless)
```

### Create Custom Network

```bash
# Create bridge network
podman network create mynetwork

# Create with specific subnet
podman network create --subnet=10.10.0.0/24 mynetwork

# Create macvlan network
podman network create -d macvlan \
  --ipam-opt parent=eth0 \
  mymacvlan
```

### Connect Containers to Networks

```bash
# Run container on specific network
podman run --network mynetwork nginx

# Connect running container to network
podman network connect mynetwork mycontainer

# Disconnect from network
podman network disconnect mynetwork mycontainer

# Add alias in network
podman network connect --alias myapp mynetwork mycontainer
```

### Port Mapping

```bash
# Map single port
podman run -p 8080:80 nginx

# Map specific IP and port
podman run -p 127.0.0.1:8080:80 nginx

# Map range of ports
podman run -p 3000-3005:3000-3005 myapp

# UDP port mapping
podman run -p 53:53/udp dns-server

# Random high port
podman run -p 80 nginx  # Maps to random port, check with podman ps
```

### DNS Configuration

```bash
# Use custom DNS servers
podman run --dns=8.8.8.8 --dns=8.8.4.4 fedora nslookup google.com

# Add custom host entries
podman run --add-host=myhost:192.168.1.100 fedora ping myhost

# Disable /etc/hosts mounting
podman run --no-hosts fedora cat /etc/hosts
```

## Volume Management

### Volume Types

- **Named volumes**: Managed by Podman, persistent
- **Bind mounts**: Host directory mounted into container
- **Anonymous volumes**: Temporary, not named
- **tmpfs mounts**: In-memory filesystem

### Create and Use Named Volumes

```bash
# Create volume
podman volume create mydata

# Inspect volume
podman volume inspect mydata

# List volumes
podman volume ls

# Use volume in container
podman run -v mydata:/app/data nginx

# Remove volume
podman volume rm mydata

# Prune unused volumes
podman volume prune
```

### Bind Mounts

```bash
# Mount host directory
podman run -v /host/path:/container/path nginx

# Read-only bind mount
podman run -v /host/config:/container/config:ro nginx

# Automatic directory creation
podman run -v mydata:/app/data nginx  # Creates if not exists

# Mount with specific options
podman run -v /host/data:/data:rw,noexec,nosuid nginx
```

### Named Volumes vs Bind Mounts

| Feature | Named Volume | Bind Mount |
|---------|-------------|------------|
| Management | Podman manages | User manages |
| Location | `/var/lib/containers/storage/volumes` | Any host path |
| Portability | High | Low (path-dependent) |
| Performance | Good | Excellent (direct access) |
| Use case | Persistent data | Development, config files |

### tmpfs Mounts

```bash
# Create tmpfs mount (in-memory)
podman run --tmpfs=/app/tmp:rw,noexec,nosuid fedora

# Size limit for tmpfs
podman run --tmpfs=/app/tmp:size=100M fedora
```

## Container Environment

### Set Environment Variables

```bash
# Single variable
podman run -e API_KEY=secret123 myapp

# Multiple variables
podman run -e VAR1=value1 -e VAR2=value2 myapp

# From file
podman run --env-file .env myapp

# From current environment
podman run --env HOSTNAME=$HOSTNAME myapp
```

### Working Directory and User

```bash
# Set working directory
podman run -w /app node npm install

# Run as specific user
podman run -u 1000 fedora whoami

# Run as named user (if exists in image)
podman run -u nginx nginx

# Keep root inside but non-root outside (rootless)
podman run --userns=auto -u 0 fedora whoami
```

### Labels and Metadata

```bash
# Add labels
podman run --label version=1.0 \
  --label maintainer="team@example.com" \
  myapp

# View labels
podman inspect --format '{{json .Config.Labels}}' mycontainer

# Filter by label
podman ps --filter label=version=1.0
```

## Health Checks

### Configure Health Checks

```bash
# Run with health check command
podman run --name webapp \
  --health-cmd="curl -f http://localhost/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  nginx

# View health status
podman ps --format "{{.Names}}\t{{.State}}"

# Manually run health check
podman healthcheck run mycontainer
```

## Container Checkpointing

### Save and Restore State

```bash
# Create checkpoint of running container
podman checkpoint mycontainer

# Export checkpoint to archive
podman checkpoint --export=/tmp/checkpoint.tar mycontainer

# Import checkpoint
podman checkpoint --import=/tmp/checkpoint.tar restored-container

# Run with checkpoint/restore support
podman run --rm --name crab nginx
podman checkpoint --extract /tmp/crab.tar crab
```

**Note:** Checkpointing requires CRIO-CR runtime and kernel support.

## Common Patterns

### Development Environment

```bash
# Full development setup
podman run -it --rm \
  --name dev-environment \
  -v $(pwd):/workspace:rw \
  -w /workspace \
  -e NODE_ENV=development \
  node:18-alpine \
  npm run dev
```

### Database with Persistent Data

```bash
# PostgreSQL with named volume
podman run -d \
  --name postgres-db \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=myapp \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15

# Create volume first if needed
podman volume create pgdata
```

### Multi-Container Application

```bash
# Create network for app
podman network create app-network

# Start database
podman run -d \
  --name db \
  --network app-network \
  -e MYSQL_ROOT_PASSWORD=secret \
  mysql:8

# Start web app connected to same network
podman run -d \
  --name webapp \
  --network app-network \
  -p 8080:80 \
  --link db:mysql \
  myapp:latest
```

## Cleanup and Maintenance

### System Prune

```bash
# Remove all stopped containers
podman container prune

# Remove unused images
podman image prune

# Remove unused volumes
podman volume prune

# Remove unused networks
podman network prune

# Remove all unused resources
podman system prune

# Aggressive cleanup (includes dangling images)
podman system prune -a

# Dry run to see what would be removed
podman system prune --dry-run
```

### Reset Podman

```bash
# WARNING: Removes all containers, images, volumes
podman system reset

# Reset without confirmation
podman system reset -f
```

## Performance Tips

1. **Use `--rm` for temporary containers** to auto-clean up
2. **Layer caching in builds** - order Containerfile instructions to maximize cache
3. **Use slim/base images** for smaller footprint
4. **Enable compression** for image storage: `storage.driver = "overlay"`
5. **Use rootless mode** for better security and no privilege escalation
6. **Limit log size** in containers.conf: `log_size_max = "8m"`

## Troubleshooting

### Container Exits Immediately

```bash
# Check exit code
podman ps -a --format "{{.Names}}\t{{.Status}}"

# View logs
podman logs mycontainer

# Inspect last command
podman inspect --format '{{.Config.Cmd}}' mycontainer
```

### Port Already in Use

```bash
# Check what's using the port
sudo ss -tlnp | grep :8080

# Use different port or kill existing process
podman run -p 8081:80 nginx
```

### Permission Denied on Volumes

```bash
# Run with matching user ID
podman run -u $(id -u):$(id -g) -v $(pwd):/app myapp

# Or use --userns=auto for rootless
podman run --userns=auto -v $(pwd):/app myapp
```

### Network Not Working

```bash
# Check network interfaces
podman network ls

# Restart network
podman network rm podman
podman network create podman

# For rootless, check slirp4netns
which slirp4netns
```

## See Also

- [Image Management](02-image-management.md) - Pull, push, build, and manage images
- [Pod Management](03-pod-management.md) - Group containers in pods
- [Systemd Integration](05-systemd-quadlet.md) - Declarative container management
- [Advanced Topics](06-advanced-topics.md) - Security, performance tuning, troubleshooting
