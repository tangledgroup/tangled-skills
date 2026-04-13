# Networks and Volumes Reference

Complete guide to network creation, configuration, volume management, and bind mounts.

## Network Management

### Network Types

Podman supports several network drivers:
- **bridge**: Default bridge network (similar to Docker)
- **macvlan**: Direct MAC address assignment to containers
- **ipvlan**: Lighter-weight alternative to macvlan
- **none**: No networking
- **host**: Use host's network namespace

### Create Network

```python
from podman import PodmanClient

client = PodmanClient()

# Create default bridge network
network = client.networks.create("my-network")

# Create network with custom configuration
network = client.networks.create(
    "custom-network",
    driver="bridge",
    ipam={
        "driver": "default",
        "config": [
            {
                "subnet": "172.20.0.0/16",
                "gateway": "172.20.0.1"
            }
        ]
    }
)

# Create network with labels
network = client.networks.create(
    "labeled-network",
    labels={
        "com.example.environment": "development",
        "com.example.team": "backend"
    }
)

# Create macvlan network
network = client.networks.create(
    "macvlan-network",
    driver="macvlan",
    options={
        "parent": "eth0"  # Host interface
    },
    ipam={
        "config": [
            {
                "subnet": "192.168.1.0/24",
                "gateway": "192.168.1.1"
            }
        ]
    }
)

# Create ipvlan network
network = client.networks.create(
    "ipvlan-network",
    driver="ipvlan",
    options={
        "parent": "eth0",
        "mode": "l2"  # or "l3"
    }
)
```

### List Networks

```python
# List all networks
networks = client.networks.list()

for network in networks:
    print(f"{network.name}: {network.driver}")

# List specific network by filter
networks = client.networks.list(filters={"driver": "bridge"})

# Get network by name
network = client.networks.get("my-network")

# Check if network exists
if client.networks.exists("my-network"):
    print("Network exists")
```

### Network Properties

```python
network = client.networks.get("my-network")

# Basic properties
print(f"Name: {network.name}")
print(f"ID: {network.id}")
print(f"Driver: {network.driver}")
print(f"Scope: {network.scope}")  # "local" or "global"
print(f"Labels: {network.labels}")

# Full attributes
attrs = network.attrs
print(f"IPAM: {attrs['IPAM']}")
print(f"Containers: {attrs['Containers']}")
print(f"Options: {attrs.get('Options', {})}")
```

### Connect/Disconnect Containers

```python
network = client.networks.get("my-network")
container = client.containers.get("my-container")

# Connect container to network
network.connect(container)

# Connect with custom IP
network.connect(
    container,
    endpoint_config={
        "IPv4Address": "172.20.0.100",
        "Aliases": ["my-alias"]
    }
)

# Disconnect container from network
network.disconnect(container)

# Disconnect with force
network.disconnect(container, force=True)
```

### Network Inspect

```python
network = client.networks.get("my-network")

# Get connected containers
attrs = network.attrs
containers = attrs.get('Containers', {})

for container_id, info in containers.items():
    print(f"Container: {info['Name']}")
    print(f"  IP: {info.get('IPv4Gateway', 'N/A')}")
    print(f"  MAC: {info.get('MacAddress', 'N/A')}")
```

### Remove Network

```python
network = client.networks.get("my-network")

# Remove network (must be unused)
network.remove()

# Force remove (even if in use)
network.remove(force=True)

# Remove by name
client.networks.remove("my-network")
```

### Prune Networks

```python
# Remove unused networks
result = client.networks.prune()

print(f"Deleted networks: {result.get('NetworksDeleted', [])}")
print(f"Space reclaimed: {result.get('SpaceReclaimed', 0)} bytes")

# Prune with filters
result = client.networks.prune(
    filters={
        "until": "2024-01-01T00:00:00Z",
        "label": {"remove": "true"}
    }
)
```

## Volume Management

### Create Volume

```python
from podman import PodmanClient

client = PodmanClient()

# Create default volume
volume = client.volumes.create("my-volume")

# Create volume with custom driver
volume = client.volumes.create(
    "custom-volume",
    driver="local"  # or other available drivers
)

# Create volume with labels
volume = client.volumes.create(
    "labeled-volume",
    labels={
        "com.example.app": "myapp",
        "com.example.environment": "production"
    }
)

# Create volume with custom options
volume = client.volumes.create(
    "options-volume",
    driver="local",
    options={
        "device": "/dev/sdb",
        "type": "ext4",
        "o": "nodev,noexec"
    }
)
```

### List Volumes

```python
# List all volumes
volumes = client.volumes.list()

for volume in volumes:
    print(f"{volume.name}: {volume.driver}")

# Get volume by name
volume = client.volumes.get("my-volume")

# Check if volume exists
if client.volumes.exists("my-volume"):
    print("Volume exists")

# List with filters (Podman-specific)
volumes = client.volumes.list(
    filters={"dangling": True}  # Unused volumes
)
```

### Volume Properties

```python
volume = client.volumes.get("my-volume")

# Basic properties
print(f"Name: {volume.name}")
print(f"Driver: {volume.driver}")
print(f"Mountpoint: {volume.mountpoint}")
print(f"Labels: {volume.labels}")
print(f"Scope: {volume.scope}")  # "local" or "global"

# Full attributes
attrs = volume.attrs
print(f"Create Options: {attrs.get('Mountpoint', 'N/A')}")
print(f"Status: {attrs.get('Status', {})}")
```

### Use Volume in Container

```python
# Create volume first
volume = client.volumes.create("app-data")

# Use named volume in container
container = client.containers.run(
    "nginx",
    volumes={
        "app-data": {"bind": "/usr/share/nginx/html", "mode": "rw"}
    },
    detach=True
)

# Multiple volumes
container = client.containers.run(
    "my-app",
    volumes={
        "data-volume": {"bind": "/app/data", "mode": "rw"},
        "config-volume": {"bind": "/app/config", "mode": "ro"}
    },
    detach=True
)
```

### Remove Volume

```python
volume = client.volumes.get("my-volume")

# Remove volume (must be unused)
volume.remove()

# Force remove (even if in use)
volume.remove(force=True)

# Remove by name
client.volumes.remove("my-volume")
```

### Prune Volumes

```python
# Remove unused volumes
result = client.volumes.prune()

print(f"Deleted volumes: {result.get('VolumesDeleted', [])}")
print(f"Space reclaimed: {result.get('SpaceReclaimed', 0)} bytes")

# Prune with filters
result = client.volumes.prune(
    filters={
        "label": {"remove": "true"}
    }
)
```

## Bind Mounts

### Directory Bind Mounts

```python
# Simple bind mount
container = client.containers.run(
    "alpine",
    command=["ls", "-la", "/host"],
    volumes={
        "/host/path": {"bind": "/container/path", "mode": "rw"}
    }
)

# Read-only bind mount
container = client.containers.run(
    "alpine",
    volumes={
        "/host/config": {"bind": "/app/config", "mode": "ro"}
    }
)

# Multiple bind mounts
container = client.containers.run(
    "my-app",
    volumes={
        "/host/data": {"bind": "/app/data", "mode": "rw"},
        "/host/logs": {"bind": "/app/logs", "mode": "rw"},
        "/host/config": {"bind": "/app/config", "mode": "ro"}
    },
    detach=True
)
```

### Advanced Mount Options

```python
from podman.domain.containers import Mount

# Using Mount objects for more control
mounts = [
    Mount(
        type="bind",
        source="/host/data",
        target="/app/data",
        read_only=False,
        propagation="rprivate",  # or "rslave", "rshared"
        bind_options={
            "nonempty": True,  # Allow binding to non-empty directory
            "create_dir": True  # Create target if doesn't exist
        }
    ),
    Mount(
        type="bind",
        source="/host/config",
        target="/app/config",
        read_only=True,
        propagation="rprivate"
    )
]

container = client.containers.run(
    "my-app",
    mounts=mounts,
    detach=True
)
```

### SELinux Labels

```python
# Relabel shared content (multiple containers can access)
container = client.containers.run(
    "my-app",
    volumes={
        "/host/data": {
            "bind": "/app/data",
            "mode": "rw",
            "relabel": "Z"  # Shared label
        }
    }
)

# Relabel private content (single container only)
container = client.containers.run(
    "my-app",
    volumes={
        "/host/private": {
            "bind": "/app/private",
            "mode": "rw",
            "relabel": "z"  # Private label
        }
    }
)
```

## Temporary Filesystems (tmpfs)

### Mount tmpfs

```python
# Simple tmpfs mount
container = client.containers.run(
    "alpine",
    tmpfs={"/tmp": ""},
    command=["mount", "|", "grep", "tmpfs"]
)

# tmpfs with size limit
container = client.containers.run(
    "my-app",
    tmpfs={
        "/tmp": "size=512m,mode=1777",
        "/var/tmp": "size=256m,mode=1777"
    },
    detach=True
)

# Using Mount objects
from podman.domain.containers import Mount

mounts = [
    Mount(
        type="tmpfs",
        target="/tmp",
        read_only=False,
        tmpfs_options={
            "size": 67108864,  # 64MB in bytes
            "mode": 0o1777
        }
    )
]

container = client.containers.run(
    "my-app",
    mounts=mounts,
    detach=True
)
```

## Network Examples

### Isolated Application Network

```python
def create_isolated_network():
    """Create isolated network for application."""
    client = PodmanClient()
    
    # Create private network
    network = client.networks.create(
        "app-private-network",
        ipam={
            "driver": "default",
            "config": [
                {
                    "subnet": "172.25.0.0/16",
                    "gateway": "172.25.0.1"
                }
            ]
        },
        labels={
            "app": "myapplication",
            "isolated": "true"
        }
    )
    
    print(f"Created network: {network.name}")
    return network

def deploy_to_network(network_name):
    """Deploy containers to isolated network."""
    client = PodmanClient()
    
    # Database container
    db = client.containers.run(
        "postgres:15",
        name="app-database",
        network=network_name,
        environment={
            "POSTGRES_DB": "app",
            "POSTGRES_USER": "app",
            "POSTGRES_PASSWORD": "secret"
        },
        detach=True
    )
    
    # Web container
    web = client.containers.run(
        "my-app",
        name="app-web",
        network=network_name,
        environment={
            "DB_HOST": "app-database"  # Can use container name as hostname
        },
        ports={"8080/tcp": 8080},
        detach=True
    )
    
    print(f"Deployed containers to {network_name}")
```

### Multi-Network Container

```python
def create_multi_network_container():
    """Create container connected to multiple networks."""
    client = PodmanClient()
    
    # Create two networks
    net1 = client.networks.create("frontend-network")
    net2 = client.networks.create("backend-network")
    
    # API gateway connected to both networks
    gateway = client.containers.run(
        "nginx",
        name="api-gateway",
        networks={
            "frontend-network": {"aliases": ["gateway"]},
            "backend-network": {"aliases": ["proxy"]}
        },
        detach=True
    )
    
    # Backend service (only on backend network)
    backend = client.containers.run(
        "my-api",
        name="backend-service",
        network="backend-network",
        environment={"GATEWAY": "http://proxy:80"},
        detach=True
    )
    
    print("Created multi-network topology")
```

## Volume Examples

### Persistent Data Volume

```python
def setup_persistent_storage():
    """Setup persistent storage for application."""
    client = PodmanClient()
    
    # Create volumes
    data_volume = client.volumes.create(
        "app-data",
        labels={"app": "myapplication", "type": "data"}
    )
    
    config_volume = client.volumes.create(
        "app-config",
        labels={"app": "myapplication", "type": "config"}
    )
    
    logs_volume = client.volumes.create(
        "app-logs",
        labels={"app": "myapplication", "type": "logs"}
    )
    
    # Deploy container with volumes
    container = client.containers.run(
        "my-app",
        name="app-instance",
        volumes={
            "app-data": {"bind": "/app/data", "mode": "rw"},
            "app-config": {"bind": "/app/config", "mode": "rw"},
            "app-logs": {"bind": "/var/log/app", "mode": "rw"}
        },
        restart_policy={"Name": "unless-stopped"},
        detach=True
    )
    
    return container

def backup_volume(volume_name):
    """Backup volume to tarball."""
    client = PodmanClient()
    
    # Create temporary container to access volume
    backup_container = client.containers.run(
        "alpine",
        command=["tar", "czf", "/backup.tar.gz", "-C", "/data", "."],
        volumes={
            volume_name: {"bind": "/data", "mode": "ro"}
        },
        detach=True
    )
    
    # Wait for completion
    exit_code = backup_container.wait()["StatusCode"]
    
    if exit_code == 0:
        # Export the tarball
        archive, stat = backup_container.get_archive("/backup.tar.gz")
        
        with open(f"{volume_name}-backup.tar.gz", "wb") as f:
            import io
            import tarfile
            
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                for member in tar.getmembers():
                    f.write(tar.extractfile(member).read())
    
    backup_container.remove()
    print(f"Backed up volume {volume_name}")
```

### Shared Volume Between Containers

```python
def create_shared_storage():
    """Create shared storage accessible by multiple containers."""
    client = PodmanClient()
    
    # Create shared volume
    shared_volume = client.volumes.create("shared-storage")
    
    # Writer container
    writer = client.containers.run(
        "alpine",
        command=["sh", "-c", "echo 'data' > /shared/file.txt && sleep infinity"],
        name="writer",
        volumes={"shared-storage": {"bind": "/shared", "mode": "rw"}},
        detach=True
    )
    
    # Reader container
    reader = client.containers.run(
        "alpine",
        command=["sh", "-c", "cat /shared/file.txt && sleep infinity"],
        name="reader",
        volumes={"shared-storage": {"bind": "/shared", "mode": "ro"}},
        detach=True
    )
    
    return writer, reader
```

## Network Troubleshooting

### Diagnose Network Issues

```python
def diagnose_network(container_name):
    """Diagnose network connectivity issues."""
    client = PodmanClient()
    container = client.containers.get(container_name)
    
    # Get network settings
    container.reload()
    network_settings = container.network_settings
    
    print(f"Container: {container.name}")
    print(f"IP Address: {network_settings.get('IPAddress', 'N/A')}")
    print(f"MAC Address: {network_settings.get('MacAddress', 'N/A')}")
    
    # Check connected networks
    networks = network_settings.get('Networks', {})
    for net_name, net_info in networks.items():
        print(f"\nNetwork: {net_name}")
        print(f"  IP: {net_info.get('IPAddress', 'N/A')}")
        print(f"  Gateway: {net_info.get('Gateway', 'N/A')}")
    
    # Test connectivity
    result = container.exec_run(["ping", "-c", "1", "8.8.8.8"])
    print(f"\nPing 8.8.8.8: {'Success' if result.exit_code == 0 else 'Failed'}")
    
    result = container.exec_run(["nslookup", "google.com"])
    print(f"DNS lookup: {'Success' if result.exit_code == 0 else 'Failed'}")
```

## Volume Troubleshooting

### Check Volume Usage

```python
def check_volume_usage(volume_name):
    """Check which containers are using a volume."""
    client = PodmanClient()
    
    # Get all containers
    containers = client.containers.list(all=True)
    
    using_containers = []
    for container in containers:
        container.reload()
        mounts = container.attrs.get('Mounts', [])
        
        for mount in mounts:
            if mount.get('Name') == volume_name or mount.get('Source') == volume_name:
                using_containers.append({
                    'name': container.name,
                    'status': container.status,
                    'mount_point': mount.get('Destination')
                })
    
    print(f"Volume {volume_name} used by:")
    for ctx in using_containers:
        print(f"  - {ctx['name']} ({ctx['status']}) -> {ctx['mount_point']}")
    
    return using_containers
```
