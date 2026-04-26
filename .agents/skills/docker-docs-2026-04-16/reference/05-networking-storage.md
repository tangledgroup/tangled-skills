# Networking and Storage

## Network Drivers

### Bridge (default)

The default network driver. Containers on the same bridge network can communicate by IP or hostname.

```bash
docker network create -d bridge my-bridge
docker network create -d bridge \
  --subnet 172.28.0.0/16 \
  --gateway 172.28.0.1 \
  my-network
```

Options:
- `com.docker.network.bridge.name` — Bridge interface name
- `com.docker.network.bridge.enable_icc` — Inter-container communication
- `com.docker.network.bridge.enable_ip_masquerade` — IP masquerading
- `com.docker.network.bridge.host_binding_ipv4` — Default binding IP
- `com.docker.network.driver.mtu` — MTU size

### Host

Container shares the host's network namespace directly. No port mapping needed, but less isolation.

```bash
docker run --network host nginx
```

Not available on Docker Desktop for Mac/Windows.

### None

No networking. Useful for completely isolated containers.

```bash
docker run --network none nginx
```

### Overlay

Distributed network connecting multiple Docker daemons. Required for Swarm services.

```bash
docker network create -d overlay my-overlay
```

Requires a key-value store (Consul, etcd, ZooKeeper) in standalone mode, or Swarm mode.

### Macvlan

Assigns a MAC address to each container, making it appear as a physical device on the network.

```bash
docker network create -d macvlan \
  --subnet 192.168.0.0/24 \
  --gateway 192.168.0.1 \
  -o parent=eth0 \
  macnet
```

### IPvlan

Similar to macvlan but operates at the IP layer. Two modes:
- `bridge` — Container shares parent MAC
- `802.1q (route/layer2)` — Each container gets its own MAC

## Port Publishing

```bash
# Publish specific port
docker run -p 8080:80 nginx

# Bind to specific interface
docker run -p 127.0.0.1:8080:80 nginx

# UDP protocol
docker run -p 8080:80/udp nginx

# Port range
docker run -p 9090-9091:8080-8081 nginx
```

**Security note:** Without specifying a host IP, Docker binds to `0.0.0.0` (all interfaces), potentially exposing the container to the internet.

## Container DNS

By default, containers use the host's DNS resolver. Custom configuration:

```bash
docker run --dns 8.8.8.8 --dns-search example.com nginx
```

In Compose files:
```yaml
services:
  web:
    dns:
      - 8.8.8.8
      - 1.1.1.1
    dns_search: example.com
```

## Volumes

Named volumes managed by Docker, stored in `/var/lib/docker/volumes/`.

```bash
# Create
docker volume create mydata

# Use
docker run -v mydata:/data nginx

# Inspect
docker volume inspect mydata

# Remove
docker volume rm mydata
```

In Compose:
```yaml
volumes:
  db-data:

services:
  db:
    image: postgres
    volumes:
      - db-data:/var/lib/postgresql/data
```

## Bind Mounts

Mount a specific host path into the container. Path must exist on the host (or Docker creates it as a directory).

```bash
# Basic bind mount
docker run -v /host/path:/container/path nginx

# Read-only
docker run -v /host/path:/container/path:ro nginx

# Using --mount syntax
docker run --mount type=bind,source=/host/path,target=/container/path,readonly nginx
```

In Compose:
```yaml
services:
  web:
    volumes:
      - ./app:/code:ro
      - ./logs:/var/log/app
```

## tmpfs Mounts

Ephemeral in-memory filesystem. Not persisted after container removal.

```bash
docker run --tmpfs /run:rw,noexec,nosuid,size=65536k nginx
docker run --mount type=tmpfs,target=/tmp,tmpfs-size=100M nginx
```

In Compose:
```yaml
services:
  web:
    tmpfs:
      - /run
      - /tmp
```

## Volume vs Bind Mount vs tmpfs

- **Volume** — Managed by Docker, persists across container lifecycle, best for data persistence
- **Bind mount** — Host filesystem path, useful for development and config files
- **tmpfs** — In-memory, ephemeral, good for sensitive temporary data

## Storage Best Practices

- Use `.dockerignore` to exclude unnecessary files from build context
- Combine RUN instructions to reduce layers
- Use multi-stage builds to minimize final image size
- Prefer named volumes over bind mounts for production data
- Use `:ro` (read-only) for configuration mounts
- Clean up unused resources with `docker system prune`
