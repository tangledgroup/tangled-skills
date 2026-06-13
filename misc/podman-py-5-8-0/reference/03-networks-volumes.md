# Networks and Volumes

## Contents
- Creating Networks
- IPAM Configuration
- Listing Networks
- Getting and Checking Networks
- Connecting / Disconnecting Containers
- Removing Networks
- Pruning Networks
- Network Properties
- Volume Operations
- Using Volumes with Containers

## Network Operations

### Creating Networks

```python
network = client.networks.create(
    "my-network",
    driver="bridge",
    enable_ipv6=True,
    internal=False,
    labels={"com.example.project": "myapp"},
)
```

Parameters:
- `name` (str): Network name
- `driver` (str): Network driver, e.g. `"bridge"`
- `enable_ipv6` (bool): Enable IPv6
- `internal` (bool): Restrict external access
- `labels` (dict[str, str]): Labels
- `options` (dict[str, Any]): Driver options
- `ipam` (IPAMConfig): Custom IP scheme

### IPAM Configuration

```python
from podman.domain.ipam import IPAMConfig, IPAMPool

ipam = IPAMConfig(
    driver="host-local",
    pool_configs=[
        IPAMPool(
            subnet="172.20.0.0/24",
            gateway="172.20.0.1",
            iprange="172.20.0.128/25",
        )
    ],
)

network = client.networks.create("custom-net", ipam=ipam)
```

### Listing Networks

```python
# List all networks
networks = client.networks.list()

# Filter by driver
networks = client.networks.list(filters={"driver": "bridge"})

# Filter by label
networks = client.networks.list(filters={"label": "com.example.app"})

# Filter by type
networks = client.networks.list(filters={"type": "custom"})

# With container details
networks = client.networks.list(greedy=True)
```

Filters:
- `driver` (str): Network driver, only `"bridge"` supported
- `label` (str | list[str]): Label filter, format `"key"` or `"key=value"`
- `type` (str): `"custom"` or `"builtin"`
- `plugin` (list[str]): CNI plugins (Podman only)

### Getting and Checking Networks

```python
network = client.networks.get("my-network")
exists = client.networks.exists("my-network")
```

### Connecting / Disconnecting Containers

```python
# Connect container to network
network.connect(container, aliases=["app"], ipv4_address="172.20.0.10")

# Disconnect
network.disconnect(container, force=True)
```

Connect parameters:
- `container` (str | Container): Container to connect
- `aliases` (list[str]): Network aliases for container
- `driver_opt` (dict[str, Any]): Driver options
- `ipv4_address` / `ipv6_address` (str): Specific IP assignment
- `link_local_ips` (list[str]): Link-local addresses

### Removing Networks

```python
network.remove(force=True)
# or via manager:
client.networks.remove("my-network", force=True)
```

### Pruning Networks

```python
result = client.networks.prune()
# Returns {"NetworksDeleted": [...], "SpaceReclaimed": int}
```

### Network Properties

```python
print(network.id)        # Network ID
print(network.name)      # Network name
print(network.short_id)  # Truncated ID
print(network.containers) # List of connected containers
```

## Volume Operations

### Creating Volumes

```python
volume = client.volumes.create(
    "my-volume",
    driver="local",
    driver_opts={"type": "tmpfs", "device": "tmpfs", "o": "size=10G"},
    labels={"com.example.app": "myapp"},
)
```

Parameters:
- `name` (str | None): Volume name
- `driver` (str): Volume driver
- `driver_opts` (dict[str, str]): Driver options
- `labels` (dict[str, str]): Labels

### Listing Volumes

```python
# List all volumes
volumes = client.volumes.list()

# Filter by driver
volumes = client.volumes.list(filters={"driver": "local"})

# Filter by label
volumes = client.volumes.list(filters={"label": {"key": "value"}})

# Filter by name
volumes = client.volumes.list(filters={"name": "my-volume"})
```

### Getting and Checking Volumes

```python
volume = client.volumes.get("my-volume")
exists = client.volumes.exists("my-volume")
```

### Inspecting Volumes

```python
info = volume.inspect()
# Returns dict with Driver, Mountpoint, Labels, etc.
```

### Removing Volumes

```python
volume.remove(force=True)
# or via manager:
client.volumes.remove("my-volume", force=True)
```

Parameters:
- `force` (bool): Force deletion of in-use volume

### Pruning Volumes

```python
result = client.volumes.prune()
# Returns {"VolumesDeleted": [...], "SpaceReclaimed": int}
```

### Volume Properties

```python
print(volume.id)       # Volume ID
print(volume.name)     # Volume name
print(volume.short_id) # Truncated ID
```

## Using Volumes with Containers

Mount volumes when creating containers:

```python
# Using bind mount via mounts parameter
from podman.domain.containers_create import Mount

container = client.containers.create(
    "alpine:latest",
    command=["sleep", "3600"],
    mounts=[
        Mount(
            type="bind",
            source="/host/data",
            target="/container/data",
            read_only=False,
        ),
        Mount(
            type="volume",
            source="my-named-volume",
            target="/container/volume",
        ),
    ],
)

# Using volumes parameter (Docker-style)
container = client.containers.create(
    "alpine:latest",
    volumes={
        "/host/path": {"bind": "/container/path", "mode": "rw"},
        "named-volume": {"bind": "/container/data", "mode": "ro"},
    },
)
```
