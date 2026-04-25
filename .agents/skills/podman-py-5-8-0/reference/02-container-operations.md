# Container Operations Reference

Complete guide to container lifecycle management, including creation, execution, monitoring, and resource control.

## Container Creation

### Using containers.run() (Quick Start)

```python
from podman import PodmanClient

client = PodmanClient()

# Simple run with image name
container = client.containers.run("alpine:latest", command=["echo", "Hello"])

# Run in detached mode
container = client.containers.run(
    "nginx:latest",
    detach=True,
    name="web-server"
)

# With port mapping
container = client.containers.run(
    "nginx:latest",
    detach=True,
    ports={"80/tcp": 8080}  # Container port : Host port
)

# Multiple port mappings
container = client.containers.run(
    "my-app",
    detach=True,
    ports={
        "8080/tcp": 8080,
        "8443/tcp": ("127.0.0.1", 8443),  # Bind to specific interface
        "3000/tcp": None  # Random host port
    }
)
```

### Using containers.create() + start() (More Control)

```python
from podman import PodmanClient

client = PodmanClient()

# Create container without starting
container = client.containers.create(
    "alpine:latest",
    name="my-container",
    command=["sleep", "infinity"]
)

# Start the container
container.start()

# Or create and start in one call
container = client.containers.create("alpine:latest")
container.start()
```

## Container Configuration Options

### Environment Variables

```python
container = client.containers.run(
    "my-app",
    environment={
        "DATABASE_URL": "postgres://user:pass@db:5432/app",
        "LOG_LEVEL": "info",
        "API_KEY": "secret123"
    },
    detach=True
)

# Or as list format
container = client.containers.run(
    "my-app",
    environment=["VAR1=value1", "VAR2=value2"],
    detach=True
)
```

### Volume Mounts

```python
from podman.domain.containers import Mount

# Bind mount (host directory to container)
container = client.containers.run(
    "my-app",
    volumes={
        "/host/path": {"bind": "/container/path", "mode": "rw"},
        "/host/readonly": {"bind": "/container/ro", "mode": "ro"}
    },
    detach=True
)

# Named volume
container = client.containers.run(
    "postgres",
    volumes={
        "postgres-data": {"bind": "/var/lib/postgresql/data", "mode": "rw"}
    },
    detach=True
)

# Using Mount objects (more control)
mounts = [
    Mount(
        type="bind",
        source="/host/config",
        target="/app/config",
        read_only=True,
        propagation="rprivate"
    ),
    Mount(
        type="tmpfs",
        target="/tmp",
        read_only=False,
        size=67108864  # 64MB
    )
]

container = client.containers.run(
    "my-app",
    mounts=mounts,
    detach=True
)
```

### Resource Limits

```python
container = client.containers.run(
    "my-app",
    # Memory limits
    mem_limit="512m",  # or 536870912 (bytes)
    mem_reservation="256m",
    memswap_limit="1g",
    
    # CPU limits
    cpu_shares=512,  # Relative weight (default: 1024)
    nano_cpus=500000000,  # 0.5 CPU (in nanoseconds)
    cpuset_cpus="0-1",  # Pin to CPUs 0 and 1
    
    # PIDs limit
    pids_limit=100,
    
    detach=True
)
```

### Networking

```python
# Use default network
container = client.containers.run("my-app", detach=True)

# Connect to specific network
container = client.containers.run(
    "my-app",
    network="my-network",
    detach=True
)

# Disable networking
container = client.containers.run(
    "my-app",
    network_disabled=True,
    detach=True
)

# Use host network
container = client.containers.run(
    "my-app",
    network_mode="host",
    detach=True
)

# Custom networks with aliases
networks = {
    "network1": {"aliases": ["app1", "service1"]},
    "network2": {"aliases": ["app2"]}
}

container = client.containers.run(
    "my-app",
    networks=networks,
    detach=True
)
```

### Restart Policy

```python
# Never restart (default)
container = client.containers.run("my-app", detach=True)

# Restart on failure (max 5 attempts)
container = client.containers.run(
    "my-app",
    restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
    detach=True
)

# Always restart
container = client.containers.run(
    "my-app",
    restart_policy={"Name": "always"},
    detach=True
)

# Restart unless stopped
container = client.containers.run(
    "my-app",
    restart_policy={"Name": "unless-stopped"},
    detach=True
)
```

### Health Checks

```python
container = client.containers.run(
    "my-app",
    healthcheck={
        "test": ["CMD", "curl", "-f", "http://localhost/health"],
        "interval": 30000000000,  # 30 seconds in nanoseconds
        "timeout": 10000000000,   # 10 seconds
        "retries": 3,
        "start_period": 40000000000  # 40 seconds grace period
    },
    detach=True
)
```

### Security Options

```python
# Drop capabilities
container = client.containers.run(
    "my-app",
    cap_drop=["NET_RAW", "SYS_ADMIN"],
    detach=True
)

# Add capabilities
container = client.containers.run(
    "my-app",
    cap_add=["NET_BIND_SERVICE"],
    detach=True
)

# Run as specific user
container = client.containers.run(
    "my-app",
    user="1000:1000",  # UID:GID
    detach=True
)

# Read-only root filesystem
container = client.containers.run(
    "my-app",
    read_only=True,
    tmpfs={"/tmp": "", "/var/tmp": ""},
    detach=True
)

# Security options (SELinux, AppArmor)
container = client.containers.run(
    "my-app",
    security_opt=["label:disable", "apparmor:unconfined"],
    detach=True
)
```

## Container Lifecycle Operations

### Start, Stop, Restart

```python
container = client.containers.get("my-container")

# Start container
container.start()

# Stop container (default 10s timeout)
container.stop()

# Stop with custom timeout
container.stop(timeout=30)  # 30 seconds

# Restart container
container.restart()

# Restart with timeout
container.restart(timeout=5)

# Kill container (immediate)
container.kill()

# Kill with specific signal
container.kill(signal="SIGTERM")
```

### Pause/Unpause

```python
container = client.containers.get("my-container")

# Suspend all processes
container.pause()

# Resume processes
container.unpause()
```

### Remove Container

```python
container = client.containers.get("my-container")

# Stop and remove
container.stop()
container.remove()

# Force remove (including running containers)
container.remove(force=True)

# Remove with volumes
container.remove(force=True, v=True)
```

## Container Inspection

### Get Container Details

```python
container = client.containers.get("my-container")

# Reload latest state
container.reload()

# Basic attributes
print(f"Name: {container.name}")
print(f"ID: {container.id}")
print(f"Status: {container.status}")
print(f"Created: {container.created}")

# Full attributes (dict)
attrs = container.attrs
print(f"Image: {attrs['Config']['Image']}")
print(f"Command: {attrs['Config']['Cmd']}")
print(f"State: {attrs['State']}")

# Specific properties
print(f"Ports: {container.ports}")
print(f"Labels: {container.labels}")
print(f"NetworkSettings: {container.network_settings}")
```

### List Containers

```python
# All containers (running and stopped)
containers = client.containers.list(all=True)

# Only running containers
containers = client.containers.list()

# With filters
containers = client.containers.list(
    filters={
        "status": ["running"],
        "ancestor": "alpine:latest",
        "label": {"com.example.service": "api"}
    }
)

# Limit results
containers = client.containers.list(limit=10, all=True)

# Since/before specific container
containers = client.containers.list(
    since="container-name",
    all=True
)
```

## Container Logs

### Get Logs

```python
container = client.containers.get("my-container")

# Get all logs as bytes
logs = container.logs(stream=False)
print(logs.decode())

# Get stdout only
logs = container.logs(stream=False, stdout=True)

# Get stderr only
logs = container.logs(stream=False, stderr=True)

# Follow logs (streaming)
for line in container.logs(stream=True, follow=True):
    print(line.decode(), end="")

# Since timestamp
import time
logs = container.logs(since=int(time.time()) - 3600)  # Last hour

# Tail specific lines
logs = container.logs(tail=100)  # Last 100 lines

# Timestamps in output
logs = container.logs(timestamps=True)
```

### Stream Logs with Timeout

```python
import signal

def stream_logs(container, duration=60):
    """Stream logs for specified duration."""
    def handler(signum, frame):
        raise TimeoutError("Duration reached")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(duration)
    
    try:
        for line in container.logs(stream=True, follow=True):
            print(line.decode(), end="")
    except TimeoutError:
        print("\nStopped streaming")
    finally:
        signal.alarm(0)

stream_logs(container, duration=30)
```

## Exec Commands in Container

### Run Command

```python
container = client.containers.get("my-container")

# Simple command
result = container.exec_run(["ls", "-la", "/app"])
print(result.output.decode())

# With working directory
result = container.exec_run(
    ["ls", "-la"],
    workdir="/app"
)

# As specific user
result = container.exec_run(
    ["id"],
    user="www-data"
)

# With environment variables
result = container.exec_run(
    ["printenv"],
    environment={"MY_VAR": "value"}
)

# Interactive (TTY)
result = container.exec_run(
    ["bash"],
    tty=True,
    detach=True
)

# Get exit code
print(f"Exit code: {result.exit_code}")
```

### Detached Exec

```python
# Start detached process
exec_instance = container.exec_run(
    ["long-running-command"],
    detach=True
)

# Inspect exec instance
print(f"Exec ID: {exec_instance.id}")
print(f"Exit Code: {exec_instance.exit_code}")

# Inspect via API
exec_inspect = client.api.inspect_exec(exec_instance.id)
```

## Container Attach

### Attach to Running Container

```python
container = client.containers.get("my-container")

# Attach to stdout/stderr
for line in container.attach(stdout=True, stderr=True, stream=True):
    print(line.decode(), end="")

# Attach with stdin (interactive)
params = {
    "stdout": True,
    "stderr": True,
    "stdin": True,
    "stream": True
}

for line in container.attach(params=params):
    print(line.decode(), end="")
```

## Container Top (Process List)

```python
container = client.containers.get("my-container")

# List processes in container
ps_output = container.top()

print("Processes:")
print(ps_output["titles"])
for process in ps_output["processes"]:
    print(process)
```

## Container Stats

### Resource Usage Statistics

```python
container = client.containers.get("my-container")

# One-time stats
stats = container.stats(stream=False)

print(f"CPU Percent: {stats['read']}")
print(f"Memory Usage: {stats['memory_stats']['usage']} bytes")
print(f"Network RX: {stats['networks']['eth0']['rx_bytes']} bytes")
print(f"Network TX: {stats['networks']['eth0']['tx_bytes']} bytes")

# Stream stats continuously
for stat in container.stats(stream=True):
    cpu_percent = (stat['cpu_stats']['cpu_usage']['total_cpu_usage'] /
                   stat['cpu_stats']['system_cpu_usage']) * 100
    
    memory_used = stat['memory_stats']['usage']
    memory_limit = stat['memory_stats']['max_usage']
    
    print(f"CPU: {cpu_percent:.2f}%, Memory: {memory_used/MEMORY_LIMIT*100:.2f}%")

# Stats for multiple containers
all_stats = client.containers.stats(
    stream=False,
    containers=["container1", "container2"]
)
```

## Container Export/Import

### Export Container

```python
container = client.containers.get("my-container")

# Export to tarball
with open("container.tar", "wb") as f:
    for chunk in container.export():
        f.write(chunk)

# Export to stream
for chunk in container.export():
    process_chunk(chunk)
```

### Import Container

```python
from podman import PodmanClient

client = PodmanClient()

# Import from tarball
with open("container.tar", "rb") as f:
    image = client.images.load(f.read())

print(f"Imported image: {image.id}")
```

## Container Changes

### Inspect File System Changes

```python
container = client.containers.get("my-container")

# Get list of changed files
changes = container.changes()

for change in changes:
    kind = "Added" if change["Kind"] == 0 else \
           "Modified" if change["Kind"] == 1 else "Deleted"
    print(f"{change['Path']}: {kind}")
```

## Wait for Container

### Block Until Container Exits

```python
container = client.containers.run(
    "alpine",
    ["sleep", "30"],
    detach=True
)

# Wait for container to exit (blocks)
exit_status = container.wait()
print(f"Container exited with status: {exit_status['StatusCode']}")

# Wait with timeout
import signal

def wait_with_timeout(container, timeout=60):
    """Wait for container with timeout."""
    def handler(signum, frame):
        raise TimeoutError("Wait timeout reached")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    
    try:
        return container.wait()
    except TimeoutError:
        print("Timeout waiting for container")
        container.kill()
        return container.wait()
    finally:
        signal.alarm(0)

exit_status = wait_with_timeout(container, timeout=30)
```

## Copy Files to/from Container

### Copy to Container

```python
import io
import tarfile

container = client.containers.get("my-container")

# Create file to copy
content = b"Hello from host!"
tar_buffer = io.BytesIO()

with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
    tarinfo = tarfile.TarInfo(name="hello.txt")
    tarinfo.size = len(content)
    tar.addfile(tarinfo, io.BytesIO(content))

tar_buffer.seek(0)

# Put archive in container
container.put_archive("/app", tar_buffer.read())
```

### Copy from Container

```python
container = client.containers.get("my-container")

# Get archive from container
archive, stat = container.get_archive("/app/file.txt")

# Extract content
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
    for member in tar.getmembers():
        f = tar.extractfile(member)
        if f:
            content = f.read()
            print(content.decode())
```

## Container Errors and Handling

```python
from podman.errors import APIError, ContainerError, ImageNotFound

try:
    container = client.containers.run("nonexistent-image")
except ImageNotFound as e:
    print(f"Image not found: {e}")

try:
    container = client.containers.get("nonexistent-container")
except APIError as e:
    if e.response.status_code == 404:
        print("Container not found")
    else:
        print(f"API Error: {e.explanation}")

try:
    result = container.exec_run(["false"])  # Command that exits with error
    if result.exit_code != 0:
        print(f"Command failed with exit code: {result.exit_code}")
except ContainerError as e:
    print(f"Container execution error: {e}")
```
