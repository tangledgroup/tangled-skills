---
name: podman-py-5-8-0
description: Python client library for Podman container engine providing programmatic access to containers, images, pods, networks, and volumes via RESTful API. Use when building Python applications that require container orchestration, automation scripts, CI/CD integration, or container management without Docker dependency.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - podman
  - containers
  - python
  - docker-alternative
  - containerization
  - orchestration
  - automation
category: devops
required_environment_variables:
  - name: CONTAINER_HOST
    prompt: "Podman service URL (e.g., unix:///run/user/1000/podman/podman.sock)"
    help: "Set to connect to Podman socket. Default: uses rootless socket path"
    required_for: "remote connections or non-default socket paths"
---

# PodmanPy 5.8.0 - Python Client for Podman

PodmanPy is a Python library that provides bindings to the Podman RESTful API, enabling programmatic management of containers, images, pods, networks, and volumes. It offers a Docker-compatible interface while leveraging Podman's daemonless architecture and security features.

**Key capabilities:**
- Container lifecycle management (create, start, stop, remove)
- Image operations (pull, push, build, tag, load)
- Pod orchestration (Podman-specific multi-container units)
- Network and volume management
- System information and resource monitoring
- Registry authentication and image search

## When to Use

- Automate container deployment and management workflows in Python
- Build CI/CD pipelines that interact with Podman
- Create container orchestration tools without Docker dependency
- Manage rootless containers programmatically
- Script container operations for DevOps automation
- Integrate Podman with monitoring or logging systems
- Migrate Docker SDK scripts to Podman-compatible code

## Setup

### Installation

```bash
pip install podman
```

**Optional dependencies:**
```bash
# For progress bars during image pull/push
pip install podman[progress_bar]

# For documentation generation
pip install podman[docs]

# For testing
pip install podman[test]
```

### Prerequisites

- **Podman installed**: Version 4.0 or higher recommended
- **Python**: 3.9, 3.10, 3.11, 3.12, or 3.13
- **Running Podman service**: Start with `podman system service --timeout=0`

### Starting the Podman Service

For rootless containers (default):

```bash
# Start service in background (Unix socket)
podman system service --timeout=0 unix:///run/user/$(id -u)/podman/podman.sock &

# Or start with TCP (for remote access)
podman system service --timeout=0 tcp:0.0.0.0:8888 &
```

For root containers:

```bash
sudo podman system service --timeout=0 unix:///run/podman/podman.sock &
```

See [Connection Configuration](references/01-connection-config.md) for detailed connection options and authentication.

## Quick Start

### Basic Container Operations

```python
from podman import PodmanClient

# Connect to Podman service (default: rootless socket)
client = PodmanClient()

# Verify connection
if client.ping():
    print("Connected to Podman!")

# List all containers
containers = client.containers.list(all=True)
for container in containers:
    container.reload()  # Refresh status
    print(f"{container.name}: {container.status}")

# Pull an image
image = client.images.pull("quay.io/podman/stable", tag="latest")

# Create and start a container
container = client.containers.run(
    image,
    command=["/bin/sh", "-c", "echo Hello World"],
    detach=True,
    name="hello-podman"
)

# Get container logs
logs = container.logs(stream=False, stdout=True).decode()
print(logs)

# Stop and remove container
container.stop()
container.remove()

# Close connection
client.close()
```

See [Container Operations](references/02-container-operations.md) for comprehensive container management.

### Working with Images

```python
from podman import PodmanClient

client = PodmanClient()

# Search for images
results = client.images.search("podman", limit=5)
for result in results:
    print(f"{result['repo_tag']}: {result['description']}")

# Pull image with progress
image = client.images.pull("docker.io/library/alpine", tag="3.18")
print(f"Pulled: {image.id} ({image.tags})")

# Build image from Dockerfile
image, logs = client.images.build(
    path="./my-app",
    dockerfile="Dockerfile",
    tag="my-app:latest"
)

# Push to registry
client.images.push("my-app", tag="latest", auth_config={
    "username": "myuser",
    "password": "mypassword"
})

# List local images
for img in client.images.list():
    print(f"{img.repository}:{img.tag} - {img.short_id}")
```

See [Image Management](references/03-image-management.md) for advanced image operations.

### Pod Orchestration (Podman-Specific)

```python
from podman import PodmanClient

client = PodmanClient()

# Create a pod
pod = client.pods.create(name="my-pod")

# Add containers to the pod
db_container = client.containers.run(
    "postgres:15",
    name="database",
    pod="my-pod",
    environment={"POSTGRES_PASSWORD": "secret"},
    detach=True
)

web_container = client.containers.run(
    "nginx:latest",
    name="webserver",
    pod="my-pod",
    ports={"80/tcp": 8080},
    detach=True
)

# List pods
for p in client.pods.list():
    print(f"Pod {p.name}: {p.status}")

# Get pod statistics
stats = client.pods.stats(name="my-pod")
print(stats)

# Remove pod (and containers)
pod.remove(force=True)
```

See [Pod Management](references/04-pod-management.md) for complete pod orchestration guide.

### Context Manager Pattern (Recommended)

```python
from podman import PodmanClient

# Automatic resource cleanup with context manager
with PodmanClient(base_url="unix:///run/user/1000/podman/podman.sock") as client:
    # All operations here
    image = client.images.pull("alpine:latest")
    container = client.containers.run(image, detach=True)
    
    # Do work...
    
    # Cleanup happens automatically
    pass  # Client closes here
```

## Reference Files

- [`references/01-connection-config.md`](references/01-connection-config.md) - Connection URIs, authentication, TLS, SSH, and environment configuration
- [`references/02-container-operations.md`](references/02-container-operations.md) - Complete container lifecycle: create, run, start, stop, exec, logs, and resource management
- [`references/03-image-management.md`](references/03-image-management.md) - Image operations: pull, push, build, load, save, tag, and registry authentication
- [`references/04-pod-management.md`](references/04-pod-management.md) - Pod orchestration for multi-container applications (Podman-specific feature)
- [`references/05-networks-volumes.md`](references/05-networks-volumes.md) - Network creation, bridge configuration, volume management, and bind mounts
- [`references/06-system-operations.md`](references/06-system-operations.md) - System info, diagnostics, prune operations, and event monitoring
- [`references/07-error-handling.md`](references/07-error-handling.md) - Exception types, error codes, retry patterns, and troubleshooting

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/podman-py-5-8-0/`). All paths are relative to this directory.

## Common Patterns

### Health Check Before Operations

```python
from podman import PodmanClient
from podman.errors import APIError

def get_client():
    """Get connected Podman client with health check."""
    client = PodmanClient()
    try:
        if not client.ping():
            raise ConnectionError("Podman service not responding")
        return client
    except APIError as e:
        client.close()
        raise RuntimeError(f"Podman connection failed: {e}")

with get_client() as client:
    # Safe to perform operations
    info = client.info()
    print(f"Podman version: {info['version']['Version']}")
```

### Batch Container Management

```python
from podman import PodmanClient

def deploy_service(image_name, replicas=3):
    """Deploy multiple container instances."""
    with PodmanClient() as client:
        containers = []
        for i in range(replicas):
            container = client.containers.run(
                image_name,
                name=f"service-{i}",
                detach=True,
                restart_policy={"Name": "on-failure"}
            )
            containers.append(container)
        
        return containers

def cleanup_containers(name_prefix):
    """Stop and remove containers by name prefix."""
    with PodmanClient() as client:
        for container in client.containers.list(all=True):
            if container.name.startswith(name_prefix):
                try:
                    container.stop(timeout=10)
                    container.remove()
                    print(f"Removed {container.name}")
                except APIError as e:
                    print(f"Failed to remove {container.name}: {e}")
```

### Image Build with Caching

```python
from podman import PodmanClient

def build_with_cache(image_name, context_path, dockerfile="Dockerfile"):
    """Build image with cache optimization."""
    with PodmanClient() as client:
        # Check for existing image
        try:
            existing = client.images.get(image_name)
            print(f"Using cached image: {existing.id}")
            return existing
        except Exception:
            pass
        
        # Build new image
        print(f"Building {image_name}...")
        image, logs = client.images.build(
            path=context_path,
            dockerfile=dockerfile,
            tag=image_name,
            pull=True,  # Pull base images
            rm=True     # Remove intermediate containers
        )
        
        print(f"Built {image.id}")
        return image
```

### Resource Monitoring

```python
from podman import PodmanClient
import time

def monitor_containers(container_names, duration=60, interval=5):
    """Monitor container resource usage over time."""
    with PodmanClient() as client:
        containers = [
            client.containers.get(name) for name in container_names
        ]
        
        start_time = time.time()
        while time.time() - start_time < duration:
            stats = client.containers.stats(stream=False, containers=container_names)
            
            for stat in stats:
                cpu_percent = stat['stats']['cpu_stats']['cpu_usage']['total_cpu_usage'] / 1000000
                memory_usage = stat['stats']['memory_stats']['usage'] / 1024 / 1024  # MB
                
                print(f"{stat['name']}: CPU={cpu_percent:.2f}ms, Memory={memory_usage:.2f}MB")
            
            time.sleep(interval)
```

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `ConnectionRefusedError` | Start Podman service: `podman system service --timeout=0` |
| `PermissionDenied` for socket | Check socket permissions or use rootless path |
| Image pull fails | Verify registry credentials and network connectivity |
| Container won't start | Check logs with `container.logs()` and inspect with `container.attrs` |
| `APIError: container not found` | Call `container.reload()` to refresh state |

### Debug Mode

```python
import logging
from podman import PodmanClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("podman")
logger.setLevel(logging.DEBUG)

client = PodmanClient()
# All API calls will now log detailed information
```

### Get System Diagnostics

```python
from podman import PodmanClient

with PodmanClient() as client:
    # System information
    info = client.info()
    print(f"Storage driver: {info['storage']['Driver']}")
    print(f"Runtime: {info['host']['ociRuntime']['RuntimeName']}")
    
    # Disk usage
    disk_usage = client.df()
    print(f"Images: {disk_usage['ImagesSpaceUsed']} bytes")
    print(f"Containers: {disk_usage['ContainersSpaceUsed']} bytes")
    
    # Version details
    version = client.version()
    print(f"Podman version: {version['Version']}")
    print(f"API version: {version['ApiVersion']}")
```

For detailed error handling and troubleshooting, see [Error Handling](references/07-error-handling.md).
