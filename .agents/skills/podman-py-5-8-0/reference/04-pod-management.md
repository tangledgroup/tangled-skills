# Pod Management Reference

Complete guide to Pod orchestration, a Podman-specific feature for managing groups of containers as a single unit.

## Pod Basics

Pods are a Podman-specific concept that allows multiple containers to share resources and be managed as a single unit. Unlike Kubernetes pods, Podman pods are simpler and designed for local development and edge computing scenarios.

### What Pods Provide

- Shared network namespace (containers can communicate via localhost)
- Shared IPC namespace (shared memory segments)
- Shared PID namespace (containers can see each other's processes)
- Coordinated lifecycle management (start/stop all containers together)
- Unified resource statistics and monitoring

## Pod Creation

### Create Basic Pod

```python
from podman import PodmanClient

client = PodmanClient()

# Create empty pod
pod = client.pods.create(name="my-pod")

print(f"Created pod: {pod.name} (ID: {pod.id})")

# Create pod with hostname
pod = client.pods.create(
    name="app-pod",
    hostname="app-hostname"
)

# Create pod with labels
pod = client.pods.create(
    name="my-pod",
    labels={
        "app": "my-application",
        "version": "1.0.0",
        "environment": "development"
    }
)
```

### Create Pod with Network Configuration

```python
# Pod with custom network
pod = client.pods.create(
    name="networked-pod",
    networks=["my-network"]
)

# Pod with IP address assignment
pod = client.pods.create(
    name="static-ip-pod",
    portmappings=[{
        "HostPort": 8080,
        "ContainerPort": 80,
        "Protocol": "tcp"
    }]
)

# Pod with multiple port mappings
pod = client.pods.create(
    name="multi-port-pod",
    portmappings=[
        {"HostPort": 8080, "ContainerPort": 80, "Protocol": "tcp"},
        {"HostPort": 8443, "ContainerPort": 443, "Protocol": "tcp"},
        {"HostPort": 5353, "ContainerPort": 53, "Protocol": "udp"}
    ]
)
```

### Create Pod with Resource Limits

```python
# Pod with CPU and memory limits
pod = client.pods.create(
    name="limited-pod",
    cpu_period=100000,
    cpu_quota=50000,  # 50% of one CPU
    cpu_shares=512,
    memory_limit=536870912,  # 512MB
    memory_reservation=268435456  # 256MB soft limit
)
```

### Create Pod with Infra Container

```python
# Pod with custom infra container image
pod = client.pods.create(
    name="custom-infra-pod",
    infra=True,  # Create infra container (default: True)
    infra_image="k8s.gcr.io/pause:3.9"
)

# Pod without infra container
pod = client.pods.create(
    name="no-infra-pod",
    infra=False
)
```

## Adding Containers to Pods

### Create Container in Pod

```python
from podman import PodmanClient

client = PodmanClient()

# First create the pod
pod = client.pods.create(name="my-app-pod")

# Add database container to pod
db_container = client.containers.run(
    "postgres:15",
    name="database",
    pod="my-app-pod",  # Specify pod name or ID
    environment={
        "POSTGRES_DB": "appdb",
        "POSTGRES_USER": "appuser",
        "POSTGRES_PASSWORD": "secret"
    },
    detach=True
)

# Add web application container to pod
web_container = client.containers.run(
    "my-app:latest",
    name="webapp",
    pod="my-app-pod",
    environment={
        "DATABASE_URL": "postgres://appuser:secret@database:5432/appdb"
    },
    ports={"8080/tcp": 8080},
    detach=True
)

# Add cache container to pod
cache_container = client.containers.run(
    "redis:7",
    name="cache",
    pod="my-app-pod",
    detach=True
)
```

### Container Communication in Pod

```python
# All containers in a pod share network namespace
# They can communicate via localhost or container names

db_container = client.containers.run(
    "postgres:15",
    name="database",
    pod="my-pod",
    detach=True
)

# Web container can reach database via hostname "database"
web_container = client.containers.run(
    "my-app",
    name="webapp",
    pod="my-pod",
    environment={
        "DB_HOST": "database"  # Can use container name as hostname
    },
    detach=True
)

# Or via localhost
web_container = client.containers.run(
    "my-app",
    name="webapp2",
    pod="my-pod",
    environment={
        "DB_HOST": "localhost"  # Also works within pod
    },
    detach=True
)
```

## Pod Listing and Inspection

### List Pods

```python
from podman import PodmanClient

client = PodmanClient()

# List all pods
pods = client.pods.list()

for pod in pods:
    print(f"Pod {pod.name}: {pod.status}")

# List only running pods (default)
running_pods = client.pods.list()

# List with filters
pods = client.pods.list(
    filters={
        "status": ["running"],
        "name": "my-app"
    }
)

# Filter by container status
pods = client.pods.list(
    filters={
        "ctr-status": ["running"]
    }
)

# Filter by number of containers
pods = client.pods.list(
    filters={
        "ctr-number": [3]  # Pods with exactly 3 containers
    }
)

# Filter by label
pods = client.pods.list(
    filters={
        "label": {"app": "myapp"}
    }
)

# Filter by network
pods = client.pods.list(
    filters={
        "network": ["network-id-123"]
    }
)
```

### Get Pod

```python
# Get pod by name
pod = client.pods.get("my-pod")

# Get pod by ID
pod = client.pods.get("abc123def456...")

# Check if pod exists
if client.pods.exists("my-pod"):
    print("Pod exists")
```

### Pod Properties

```python
pod = client.pods.get("my-pod")

# Basic properties
print(f"Name: {pod.name}")
print(f"ID: {pod.id}")
print(f"Status: {pod.status}")
print(f"Created: {pod.created}")
print(f"CNI Type: {pod.cni_type}")

# Full attributes
attrs = pod.attrs
print(f"Hostname: {attrs.get('hostname', 'N/A')}")
print(f"Labels: {attrs.get('labels', {})}")
print(f"Port Mappings: {attrs.get('portmappings', [])}")

# Pod infrastructure
print(f"Infra Container ID: {pod.infra_container_id}")
print(f"Infra Container IP: {pod.infra_container_ip}")
print(f"Infra Container MAC: {pod.infra_container_mac_address}")
```

### Get Pod Containers

```python
pod = client.pods.get("my-pod")

# Get containers in pod (via list filter)
containers = client.containers.list(
    filters={
        "pod": pod.id
    }
)

for container in containers:
    print(f"Container: {container.name} - Status: {container.status}")
```

## Pod Lifecycle Operations

### Start Pod

```python
pod = client.pods.get("my-pod")

# Start all containers in pod
pod.start()

# Start with specific timeout
pod.start(timeout=30)
```

### Stop Pod

```python
pod = client.pods.get("my-pod")

# Stop all containers in pod (default 10s timeout per container)
pod.stop()

# Stop with custom timeout
pod.stop(timeout=30)  # 30 seconds per container

# Stop and remove
pod.stop()
pod.remove()
```

### Restart Pod

```python
pod = client.pods.get("my-pod")

# Restart all containers in pod
pod.restart()

# Restart with timeout
pod.restart(timeout=5)
```

### Pause/Unpause Pod

```python
pod = client.pods.get("my-pod")

# Pause all containers in pod
pod.pause()

# Unpause all containers
pod.unpause()
```

### Remove Pod

```python
pod = client.pods.get("my-pod")

# Remove stopped pod (containers must be stopped first)
pod.stop()
pod.remove()

# Force remove (stops and removes containers first)
pod.remove(force=True)

# Remove with timeout
pod.remove(force=True, timeout=30)
```

## Pod Statistics and Monitoring

### Get Pod Stats

```python
from podman import PodmanClient

client = PodmanClient()

# One-time stats for single pod
stats = client.pods.stats(name="my-pod")

for stat in stats:
    print(f"Pod: {stat['podName']}")
    print(f"  CPU: {stat.get('cpuPercent', 'N/A')}")
    print(f"  Memory: {stat.get('memoryUsage', 'N/A')} / {stat.get('memoryLimit', 'N/A')}")

# Stats for all running pods
all_stats = client.pods.stats(all=True, stream=False)

# Stream stats continuously
for stat_update in client.pods.stats(stream=True):
    for stat in stat_update:
        print(f"Pod {stat['podName']}: CPU={stat.get('cpuPercent')}")

# Stats for specific pods
stats = client.pods.stats(
    name=["pod1", "pod2"],
    stream=False
)
```

### Decode Stats Output

```python
# Get decoded stats
for stat in client.pods.stats(stream=True, decode=True):
    for pod_stat in stat:
        print(f"Pod: {pod_stat['podName']}")
        
        # CPU usage
        if 'cpuPercent' in pod_stat:
            print(f"  CPU: {pod_stat['cpuPercent']}%")
        
        # Memory usage
        if 'memoryUsage' in pod_stat:
            usage = pod_stat['memoryUsage']
            limit = pod_stat.get('memoryLimit', 0)
            percent = (usage / limit * 100) if limit > 0 else 0
            print(f"  Memory: {usage/1024/1024:.2f}MB ({percent:.1f}%)")
        
        # Network stats
        if 'networks' in pod_stat:
            for iface, net_stats in pod_stat['networks'].items():
                rx = net_stats.get('rxBytes', 0)
                tx = net_stats.get('txBytes', 0)
                print(f"  Network {iface}: RX={rx} TX={tx}")
```

## Pod Events

### Monitor Pod Events

```python
from podman import PodmanClient

client = PodmanClient()

# Stream all events
for event in client.events():
    print(f"Event: {event['type']} - {event['actor']['attributes']}")

# Filter by pod
for event in client.events(filters={"pod": "my-pod"}):
    print(f"Pod event: {event}")

# Filter by event type
for event in client.events(filters={"type": "pod"}):
    print(f"Pod event: {event['action']} - {event['actor']['name']}")

# Events since timestamp
import time
for event in client.events(since=int(time.time()) - 300):  # Last 5 minutes
    print(event)

# Events until timestamp
for event in client.events(until=int(time.time())):
    print(event)

# Decode events
for event in client.events(decode=True):
    print(f"{event['time']}: {event['action']} on {event['actor']['name']}")
```

## Pod Top (Process List)

### List Processes in Pod

```python
pod = client.pods.get("my-pod")

# Get process list from all containers in pod
ps_output = pod.top()

print("Processes in pod:")
print(f"Titles: {ps_output['titles']}")
for process in ps_output['processes']:
    print(process)
```

## Pod Logs

### Get Combined Logs

```python
pod = client.pods.get("my-pod")

# Get logs from all containers in pod
logs = pod.logs(stream=False)
print(logs.decode())

# Stream logs
for line in pod.logs(stream=True, follow=True):
    print(line.decode(), end="")

# With timestamps
for line in pod.logs(stream=True, timestamps=True):
    print(line.decode(), end="")

# Tail specific lines
logs = pod.logs(tail=100)

# Since timestamp
import time
logs = pod.logs(since=int(time.time()) - 3600)  # Last hour
```

## Advanced Pod Operations

### Create Pod from Kubernetes YAML

```python
from podman import PodmanClient

client = PodmanClient()

# Podman can import pods from Kubernetes YAML
# First, save your Kubernetes pod spec to a file

# Then play kube (requires podman CLI)
import subprocess

result = subprocess.run(
    ["podman", "play", "kube", "kubernetes-pod.yaml"],
    capture_output=True,
    text=True
)

print(result.stdout)

# The pod will be created and can be managed via PodmanPy
pod = client.pods.get("k8s-imported-pod")
```

### Pod Network Configuration

```python
# Create network first
network = client.networks.create("my-pod-network")

# Create pod with network
pod = client.pods.create(
    name="networked-pod",
    networks=["my-pod-network"]
)

# Add containers to pod (they inherit pod's network)
container = client.containers.run(
    "alpine",
    command=["sleep", "infinity"],
    pod="networked-pod",
    detach=True
)

# All containers in pod share the same network namespace
# They can communicate via localhost
```

### Pod with Shared Volumes

```python
# Create volume for sharing
volume = client.volumes.create("shared-data")

# Create pod
pod = client.pods.create(name="shared-pod")

# Add multiple containers using same volume
container1 = client.containers.run(
    "alpine",
    command=["sh", "-c", "echo data1 > /data/file.txt && sleep infinity"],
    name="writer",
    pod="shared-pod",
    volumes={"shared-data": {"bind": "/data", "mode": "rw"}},
    detach=True
)

container2 = client.containers.run(
    "alpine",
    command=["sh", "-c", "cat /data/file.txt && sleep infinity"],
    name="reader",
    pod="shared-pod",
    volumes={"shared-data": {"bind": "/data", "mode": "ro"}},
    detach=True
)
```

## Pod Error Handling

```python
from podman.errors import APIError, NotFound

try:
    pod = client.pods.get("nonexistent-pod")
except NotFound as e:
    print(f"Pod not found: {e}")

try:
    pod.remove()  # Remove running pod without force
except APIError as e:
    if e.response.status_code == 409:
        print("Cannot remove running pod. Stop first or use force=True")
    else:
        print(f"Remove failed: {e.explanation}")

try:
    pod = client.pods.create(name="my-pod")
    # If creation fails, pod might be partially created
except APIError as e:
    print(f"Pod creation failed: {e}")
    # Cleanup if partial creation occurred
    if client.pods.exists("my-pod"):
        client.pods.get("my-pod").remove(force=True)
```

## Pod Examples

### Web Application Stack

```python
from podman import PodmanClient

def deploy_webstack():
    """Deploy a complete web application stack in a pod."""
    client = PodmanClient()
    
    # Create pod
    pod = client.pods.create(
        name="webapp-stack",
        labels={
            "app": "webapp",
            "environment": "development"
        }
    )
    
    # Database container
    db = client.containers.run(
        "postgres:15",
        name="database",
        pod="webapp-stack",
        environment={
            "POSTGRES_DB": "webapp",
            "POSTGRES_USER": "webapp",
            "POSTGRES_PASSWORD": "changeme"
        },
        volumes={"postgres-data": {"bind": "/var/lib/postgresql/data"}},
        detach=True
    )
    
    # Cache container
    cache = client.containers.run(
        "redis:7-alpine",
        name="cache",
        pod="webapp-stack",
        detach=True
    )
    
    # Web application container
    web = client.containers.run(
        "my-webapp:latest",
        name="webapp",
        pod="webapp-stack",
        environment={
            "DATABASE_URL": "postgres://webapp:changeme@database:5432/webapp",
            "REDIS_URL": "redis://cache:6379"
        },
        ports={"8080/tcp": 8080},
        restart_policy={"Name": "on-failure"},
        detach=True
    )
    
    print(f"Deployed webapp stack in pod {pod.name}")
    print(f"Access webapp at http://localhost:8080")
    
    return pod

def undeploy_webstack():
    """Remove the web application stack."""
    client = PodmanClient()
    
    pod = client.pods.get("webapp-stack")
    pod.remove(force=True)
    
    print("Removed webapp stack")
```

### Microservices in Pod

```python
def deploy_microservices():
    """Deploy multiple microservices sharing network namespace."""
    client = PodmanClient()
    
    # Create shared pod
    pod = client.pods.create(name="microservices-pod")
    
    services = [
        {"name": "auth-service", "image": "auth-svc:latest", "port": 8001},
        {"name": "user-service", "image": "user-svc:latest", "port": 8002},
        {"name": "order-service", "image": "order-svc:latest", "port": 8003},
    ]
    
    containers = []
    for svc in services:
        container = client.containers.run(
            svc["image"],
            name=svc["name"],
            pod="microservices-pod",
            ports={f"{svc['port']}/tcp": svc['port']},
            environment={
                "SERVICE_NAME": svc["name"],
                "AUTH_URL": "http://localhost:8001",
                "USER_URL": "http://localhost:8002",
                "ORDER_URL": "http://localhost:8003"
            },
            detach=True
        )
        containers.append(container)
    
    print(f"Deployed {len(containers)} microservices in pod {pod.name}")
    return pod, containers
```

## Best Practices

1. **Use pods for related services**: Group containers that need to communicate frequently via localhost
2. **Leverage shared network namespace**: Containers in a pod can use container names as hostnames
3. **Monitor pod stats together**: Use `pod.stats()` to get combined resource usage
4. **Manage lifecycle as unit**: Start/stop/remove the entire pod instead of individual containers
5. **Use labels for organization**: Tag pods with application, environment, and team labels
