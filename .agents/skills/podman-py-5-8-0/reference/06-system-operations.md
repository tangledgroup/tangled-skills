# System Operations Reference

Complete guide to system information, diagnostics, cleanup operations, and event monitoring.

## System Information

### Get System Info

```python
from podman import PodmanClient

client = PodmanClient()

# Get comprehensive system information
info = client.info()

# Storage information
print(f"Storage Driver: {info['storage']['Driver']}")
print(f"Root Dir: {info['storage']['GraphDirectory']}")
print(f"Run Dir: {info['storage']['RunRootDirectory']}")

# Runtime information
print(f"Runtime: {info['host']['ociRuntime']['RuntimeName']}")
print(f"Runtime Path: {info['host']['ociRuntime']['RuntimePath']}")

# Host information
print(f"OS: {info['host']['os']}")
print(f"Architecture: {info['host']['arch']}")
print(f"CPU Cores: {info['host']['ncpu']}")
print(f"Memory: {info['host']['mem'] } bytes")

# Security features
print(f"SELinux Enabled: {info['host']['security']['SECCOMPEnabled']}")
print(f"AppArmor Enabled: {info['host']['security']['AppArmorEnabled']}")

# Version information
print(f"Podman Version: {info['version']['Version']}")
print(f"API Version: {info['version']['ApiVersion']}")
```

### Get Version Details

```python
# Get version information
version = client.version()

print(f"Podman Version: {version['Version']}")
print(f"API Version: {version['ApiVersion']}")
print(f"Git Commit: {version.get('GitCommit', 'N/A')}")

# Get component versions
for component in version.get('Components', []):
    name = component['Name']
    ver = component['Version']
    details = component.get('Details', {})
    
    print(f"\n{name}: {ver}")
    if 'APIVersion' in details:
        print(f"  API Version: {details['APIVersion']}")
```

### Check System Health

```python
def check_system_health():
    """Check Podman system health."""
    client = PodmanClient()
    
    # Ping service
    if not client.ping():
        return {"status": "unhealthy", "error": "Service not responding"}
    
    # Get info
    info = client.info()
    
    health = {
        "status": "healthy",
        "version": info['version']['Version'],
        "storage": info['storage']['Driver'],
        "runtime": info['host']['ociRuntime']['RuntimeName']
    }
    
    # Check for warnings
    warnings = []
    
    if not info['host']['security']['SECCOMPEnabled']:
        warnings.append("SECCOMP is disabled")
    
    if info['host']['swapSpace'] == 0:
        warnings.append("No swap space configured")
    
    if warnings:
        health["status"] = "warning"
        health["warnings"] = warnings
    
    return health

# Usage
health = check_system_health()
print(f"System Status: {health['status']}")
if 'warnings' in health:
    for warning in health['warnings']:
        print(f"  Warning: {warning}")
```

## Disk Usage and Statistics

### Get Disk Usage

```python
from podman import PodmanClient

client = PodmanClient()

# Get disk usage summary
disk_usage = client.df()

print("=== Disk Usage Summary ===")
print(f"Images: {disk_usage['ImagesSpaceUsed']} bytes ({disk_usage['ImagesSpaceUsed']/1024/1024:.2f} MB)")
print(f"Containers: {disk_usage['ContainersSpaceUsed']} bytes ({disk_usage['ContainersSpaceUsed']/1024/1024:.2f} MB)")
print(f"Local Volumes: {disk_usage['LocalVolumesSpaceUsed']} bytes ({disk_usage['LocalVolumesSpaceUsed']/1024/1024:.2f} MB)")
print(f"Build Cache: {disk_usage['BuilderCacheSizeUsed']} bytes ({disk_usage['BuilderCacheSizeUsed']/1024/1024:.2f} MB)")

# Calculate total
total = (
    disk_usage['ImagesSpaceUsed'] +
    disk_usage['ContainersSpaceUsed'] +
    disk_usage['LocalVolumesSpaceUsed'] +
    disk_usage['BuilderCacheSizeUsed']
)
print(f"\nTotal: {total/1024/1024:.2f} MB")
```

### Detailed Disk Usage

```python
def get_detailed_disk_usage():
    """Get detailed disk usage by resource type."""
    client = PodmanClient()
    
    # Image sizes
    print("\n=== Image Sizes ===")
    images = client.images.list(all=True)
    for image in sorted(images, key=lambda x: x.size, reverse=True)[:10]:
        tags = ', '.join(image.tags) if image.tags else '<none>'
        print(f"{tags}: {image.size/1024/1024:.2f} MB")
    
    # Container sizes
    print("\n=== Container Sizes ===")
    containers = client.containers.list(all=True)
    for container in containers:
        container.reload()
        size = container.attrs.get('SizeRw', 0) + container.attrs.get('SizeRootFs', 0)
        print(f"{container.name}: {size/1024/1024:.2f} MB")
    
    # Volume sizes
    print("\n=== Volume Locations ===")
    volumes = client.volumes.list()
    for volume in volumes:
        print(f"{volume.name}: {volume.mountpoint}")
```

## Prune Operations

### Prune Images

```python
from podman import PodmanClient

client = PodmanClient()

# Remove dangling images (untagged, not used)
result = client.images.prune()
print(f"Images pruned:")
print(f"  Deleted: {result.get('ImagesDeleted', [])}")
print(f"  Space reclaimed: {result.get('SpaceReclaimed', 0)/1024/1024:.2f} MB")

# Remove all unused images (not just dangling)
result = client.images.prune(all=True)
print(f"\nAll unused images pruned:")
print(f"  Space reclaimed: {result.get('SpaceReclaimed', 0)/1024/1024:.2f} MB")

# Prune with filters
result = client.images.prune(
    filters={
        "until": "2024-01-01T00:00:00Z",  # Images older than date
        "label": {"keep": "false"}        # Exclude images with keep=true label
    }
)

# Prune build cache
result = client.images.prune_builds()
print(f"\nBuild cache pruned:")
print(f"  Caches deleted: {result.get('CachesDeleted', [])}")
```

### Prune Containers

```python
# Remove all stopped containers
result = client.containers.prune()

print(f"Containers pruned:")
for container in result.get('ContainersDeleted', []):
    print(f"  - {container}")
print(f"Space reclaimed: {result.get('SpaceReclaimed', 0)/1024/1024:.2f} MB")
```

### Prune Networks

```python
# Remove unused networks
result = client.networks.prune()

print(f"Networks pruned:")
for network in result.get('NetworksDeleted', []):
    print(f"  - {network}")
```

### Prune Volumes

```python
# Remove unused volumes
result = client.volumes.prune()

print(f"Volumes pruned:")
for volume in result.get('VolumesDeleted', []):
    print(f"  - {volume}")
print(f"Space reclaimed: {result.get('SpaceReclaimed', 0)/1024/1024:.2f} MB")

# Prune with filters
result = client.volumes.prune(
    filters={
        "label": {"temporary": "true"}  # Only volumes marked as temporary
    }
)
```

### Prune Pods

```python
# Remove stopped pods
result = client.pods.prune()

print(f"Pods pruned:")
for pod in result.get('PodsDeleted', []):
    print(f"  - {pod}")
```

### Full System Cleanup

```python
def full_cleanup(dry_run=False):
    """Perform complete system cleanup."""
    client = PodmanClient()
    
    print("=== Podman System Cleanup ===\n")
    
    # Get current disk usage
    before = client.df()
    before_total = (
        before['ImagesSpaceUsed'] +
        before['ContainersSpaceUsed'] +
        before['LocalVolumesSpaceUsed'] +
        before['BuilderCacheSizeUsed']
    )
    print(f"Before: {before_total/1024/1024:.2f} MB")
    
    if dry_run:
        print("\nDry run - no changes made")
        return
    
    # Prune all resource types
    print("\nPruning images...")
    img_result = client.images.prune(all=True)
    print(f"  Reclaimed: {img_result.get('SpaceReclaimed', 0)/1024/1024:.2f} MB")
    
    print("Pruning containers...")
    ctr_result = client.containers.prune()
    print(f"  Reclaimed: {ctr_result.get('SpaceReclaimed', 0)/1024/1024:.2f} MB")
    
    print("Pruning networks...")
    net_result = client.networks.prune()
    print(f"  Deleted: {len(net_result.get('NetworksDeleted', []))} networks")
    
    print("Pruning volumes...")
    vol_result = client.volumes.prune()
    print(f"  Reclaimed: {vol_result.get('SpaceReclaimed', 0)/1024/1024:.2f} MB")
    
    print("Pruning pods...")
    pod_result = client.pods.prune()
    print(f"  Deleted: {len(pod_result.get('PodsDeleted', []))} pods")
    
    # Get final disk usage
    after = client.df()
    after_total = (
        after['ImagesSpaceUsed'] +
        after['ContainersSpaceUsed'] +
        after['LocalVolumesSpaceUsed'] +
        after['BuilderCacheSizeUsed']
    )
    print(f"\nAfter: {after_total/1024/1024:.2f} MB")
    print(f"Total reclaimed: {(before_total - after_total)/1024/1024:.2f} MB")

# Usage
full_cleanup(dry_run=False)
```

## Event Monitoring

### Stream All Events

```python
from podman import PodmanClient

client = PodmanClient()

# Stream all events continuously
for event in client.events():
    print(f"{event['time']}: {event['action']} on {event['actor']['name']}")
    print(f"  Type: {event['type']}")
    print(f"  Attributes: {event['actor'].get('attributes', {})}")
```

### Filter Events

```python
# Filter by container
for event in client.events(filters={"container": "my-container"}):
    print(f"Container event: {event['action']} - {event['actor']['name']}")

# Filter by image
for event in client.events(filters={"image": "alpine"}):
    print(f"Image event: {event['action']}")

# Filter by pod
for event in client.events(filters={"pod": "my-pod"}):
    print(f"Pod event: {event}")

# Filter by event type
for event in client.events(filters={"type": "container"}):
    print(f"Container event: {event['action']}")

# Multiple filters
for event in client.events(
    filters={
        "type": ["container", "image"],
        "event": ["start", "stop", "pull"]
    }
):
    print(event)
```

### Time-Bounded Events

```python
import time

client = PodmanClient()

# Events since timestamp (last 5 minutes)
since_time = int(time.time()) - 300
for event in client.events(since=since_time):
    print(f"Recent event: {event['action']} on {event['actor']['name']}")

# Events until timestamp
until_time = int(time.time())
for event in client.events(until=until_time):
    print(event)

# Events in time range
for event in client.events(
    since=int(time.time()) - 60,  # Last minute
    until=int(time.time())
):
    print(event)
```

### Decode Events

```python
# Get decoded events (dict instead of raw)
for event in client.events(decode=True):
    print(f"Time: {event['time']}")
    print(f"Type: {event['type']}")
    print(f"Action: {event['action']}")
    print(f"Actor: {event['actor']['name']}")
    print(f"ID: {event['actor'].get('id', 'N/A')[:12]}")
    
    attrs = event['actor'].get('attributes', {})
    if attrs:
        print(f"Attributes:")
        for key, value in attrs.items():
            print(f"  {key}: {value}")
    print("---")
```

### Event Monitoring with Timeout

```python
import signal
import time

def monitor_events(duration=60):
    """Monitor events for specified duration."""
    client = PodmanClient()
    
    def handler(signum, frame):
        raise TimeoutError("Duration reached")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(duration)
    
    try:
        print(f"Monitoring events for {duration} seconds...")
        event_count = 0
        
        for event in client.events(decode=True):
            event_count += 1
            timestamp = event['time'].strftime('%H:%M:%S')
            print(f"[{timestamp}] {event['action']:10s} {event['actor']['name'][:20]}")
        
        print(f"\nTotal events: {event_count}")
    
    except TimeoutError:
        print("\nMonitoring stopped (timeout)")
    finally:
        signal.alarm(0)

# Usage
monitor_events(duration=30)
```

### Event Statistics

```python
from collections import Counter
import time

def get_event_statistics(duration=60):
    """Collect event statistics over time."""
    client = PodmanClient()
    
    event_types = Counter()
    event_actions = Counter()
    actor_names = Counter()
    
    start_time = time.time()
    
    for event in client.events(decode=True):
        elapsed = time.time() - start_time
        if elapsed > duration:
            break
        
        event_types[event['type']] += 1
        event_actions[event['action']] += 1
        actor_names[event['actor']['name']] += 1
    
    print(f"=== Event Statistics (last {duration}s) ===")
    print(f"\nBy Type:")
    for event_type, count in event_types.most_common():
        print(f"  {event_type}: {count}")
    
    print(f"\nBy Action:")
    for action, count in event_actions.most_common():
        print(f"  {action}: {count}")
    
    print(f"\nTop Actors:")
    for name, count in actor_names.most_common(5):
        print(f"  {name[:30]}: {count}")

# Usage
get_event_statistics(duration=30)
```

## System Diagnostics

### Check Resource Limits

```python
def check_resource_limits():
    """Check system resource limits and configuration."""
    client = PodmanClient()
    info = client.info()
    
    print("=== Resource Configuration ===")
    
    # CPU
    host_info = info.get('host', {})
    print(f"\nCPU:")
    print(f"  Cores: {host_info.get('ncpu', 'N/A')}")
    print(f"  Cgroups Version: {host_info.get('cgroupVersion', 'N/A')}")
    
    # Memory
    print(f"\nMemory:")
    print(f"  Total: {host_info.get('mem', 0)/1024/1024:.2f} MB")
    print(f"  Swap: {host_info.get('swapSpace', 0)/1024/1024:.2f} MB")
    
    # Storage
    storage = info.get('storage', {})
    print(f"\nStorage:")
    print(f"  Driver: {storage.get('Driver', 'N/A')}")
    print(f"  Graph Root: {storage.get('GraphDirectory', 'N/A')}")
    print(f"  Run Root: {storage.get('RunRootDirectory', 'N/A')}")
    
    # Security
    security = host_info.get('security', {})
    print(f"\nSecurity:")
    print(f"  SELinux: {'Enabled' if security.get('SECCOMPEnabled') else 'Disabled'}")
    print(f"  AppArmor: {'Enabled' if security.get('AppArmorEnabled') else 'Disabled'}")
    print(f"  Namespaces: {security.get('namespaces', [])}")

# Usage
check_resource_limits()
```

### Monitor System Load

```python
import time

def monitor_system_load(interval=5, duration=60):
    """Monitor Podman system load over time."""
    client = PodmanClient()
    
    print(f"=== System Load Monitor ({duration}s) ===")
    print(f"Interval: {interval}s\n")
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Get container stats
        containers = client.containers.list()
        running = len(containers)
        
        # Get disk usage
        disk = client.df()
        images_space = disk['ImagesSpaceUsed'] / 1024 / 1024
        containers_space = disk['ContainersSpaceUsed'] / 1024 / 1024
        
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Running: {running:3d} | Images: {images_space:8.2f} MB | Containers: {containers_space:8.2f} MB")
        
        time.sleep(interval)

# Usage
monitor_system_load(interval=5, duration=30)
```

### System Health Check

```python
def system_health_check():
    """Comprehensive system health check."""
    client = PodmanClient()
    
    health = {
        "status": "healthy",
        "checks": [],
        "warnings": [],
        "errors": []
    }
    
    # Check 1: Service connectivity
    try:
        if client.ping():
            health["checks"].append("Service connectivity: OK")
        else:
            health["errors"].append("Service not responding")
            health["status"] = "unhealthy"
    except Exception as e:
        health["errors"].append(f"Service connection failed: {e}")
        health["status"] = "unhealthy"
        return health
    
    # Check 2: Version info
    try:
        version = client.version()
        health["checks"].append(f"Version: {version['Version']}")
    except Exception as e:
        health["warnings"].append(f"Could not get version: {e}")
    
    # Check 3: Disk usage
    try:
        disk = client.df()
        total_gb = (disk['ImagesSpaceUsed'] + disk['ContainersSpaceUsed']) / 1024 / 1024 / 1024
        
        health["checks"].append(f"Disk usage: {total_gb:.2f} GB")
        
        if total_gb > 50:  # Warning if > 50GB
            health["warnings"].append("High disk usage (> 50GB)")
    except Exception as e:
        health["warnings"].append(f"Could not get disk usage: {e}")
    
    # Check 4: Container count
    try:
        containers = client.containers.list(all=True)
        running = len(client.containers.list())
        stopped = len(containers) - running
        
        health["checks"].append(f"Containers: {running} running, {stopped} stopped")
        
        if stopped > 10:
            health["warnings"].append(f"Many stopped containers ({stopped})")
    except Exception as e:
        health["warnings"].append(f"Could not list containers: {e}")
    
    # Check 5: Image count
    try:
        images = client.images.list(all=True)
        dangling = len(client.images.list(filters={"dangling": True}))
        
        health["checks"].append(f"Images: {len(images)} total, {dangling} dangling")
        
        if dangling > 5:
            health["warnings"].append(f"Many dangling images ({dangling})")
    except Exception as e:
        health["warnings"].append(f"Could not list images: {e}")
    
    # Update status based on warnings/errors
    if health["errors"]:
        health["status"] = "unhealthy"
    elif health["warnings"]:
        health["status"] = "warning"
    
    return health

# Usage and display
def print_health_check():
    health = system_health_check()
    
    print("=== Podman System Health Check ===")
    print(f"\nStatus: {health['status'].upper()}")
    
    if health["checks"]:
        print("\nChecks:")
        for check in health["checks"]:
            print(f"  ✓ {check}")
    
    if health["warnings"]:
        print("\nWarnings:")
        for warning in health["warnings"]:
            print(f"  ⚠ {warning}")
    
    if health["errors"]:
        print("\nErrors:")
        for error in health["errors"]:
            print(f"  ✗ {error}")

# Run health check
print_health_check()
```

## Diagnostic Scripts

### Container Performance Analysis

```python
def analyze_container_performance():
    """Analyze container resource usage."""
    client = PodmanClient()
    
    containers = client.containers.list()
    
    print("=== Container Performance Analysis ===\n")
    
    for container in containers:
        # Get stats
        stats = container.stats(stream=False)
        
        # CPU usage
        cpu_percent = stats.get('cpuPercent', 0)
        
        # Memory usage
        mem_usage = stats.get('memory_stats', {}).get('usage', 0)
        mem_limit = stats.get('memory_stats', {}).get('max_usage', 0)
        mem_percent = (mem_usage / mem_limit * 100) if mem_limit > 0 else 0
        
        # Network usage
        networks = stats.get('networks', {})
        total_rx = sum(n.get('rx_bytes', 0) for n in networks.values())
        total_tx = sum(n.get('tx_bytes', 0) for n in networks.values())
        
        print(f"Container: {container.name}")
        print(f"  CPU: {cpu_percent:.2f}%")
        print(f"  Memory: {mem_usage/1024/1024:.2f} MB ({mem_percent:.1f}%)")
        print(f"  Network: RX={total_rx/1024/1024:.2f} MB, TX={total_tx/1024/1024:.2f} MB")
        print()

# Usage
analyze_container_performance()
```

### Storage Cleanup Recommendations

```python
def storage_cleanup_recommendations():
    """Provide recommendations for storage cleanup."""
    client = PodmanClient()
    
    print("=== Storage Cleanup Recommendations ===\n")
    
    # Dangling images
    dangling_images = client.images.list(filters={"dangling": True})
    if dangling_images:
        total_size = sum(img.size for img in dangling_images)
        print(f"✓ Remove {len(dangling_images)} dangling images ({total_size/1024/1024:.2f} MB)")
        print("  Command: client.images.prune()")
    
    # Stopped containers
    stopped_containers = [c for c in client.containers.list(all=True) if c.status == 'exited']
    if stopped_containers:
        print(f"\n✓ Remove {len(stopped_containers)} stopped containers")
        print("  Command: client.containers.prune()")
    
    # Unused networks
    all_networks = client.networks.list()
    # Filter out default networks and those in use
    unused_networks = [n for n in all_networks if n.name not in ['bridge', 'host', 'none']]
    if unused_networks:
        print(f"\n✓ Remove {len(unused_networks)} unused networks")
        print("  Command: client.networks.prune()")
    
    # Unused volumes
    # This requires checking which volumes are actually in use
    print("\n⚠ Check for unused volumes manually")
    print("  Command: podman volume ls")
    
    # Old images (keep only latest tags)
    print("\n⚠ Consider removing old image tags")
    print("  Review with: podman images --format '{{.Repository}} {{.Tag}} {{.CreatedAt}}'")

# Usage
storage_cleanup_recommendations()
```
