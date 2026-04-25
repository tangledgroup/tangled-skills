# Podman Pod Management

This reference covers pod creation, container orchestration within pods, pod networking, and advanced pod operations.

## Pod Fundamentals

### What Are Pods?

Pods are groups of containers that share:
- Network namespace (IP address and ports)
- IPC namespace (System V IPC, POSIX message queues)
- User namespace (optional)
- PID namespace (optional)
- UTS namespace (optional)

**Benefits:**
- Containers in a pod can communicate via localhost
- Shared networking simplifies service discovery
- Co-scheduling of related containers
- Kubernetes-compatible abstraction

### Create a Pod

```bash
# Basic pod creation
podman pod create --name mypod

# With custom network
podman pod create --name mypod --network mynetwork

# With hostname
podman pod create --name mypod --hostname myhost

# With DNS servers
podman pod create --name mypod --dns=8.8.8.8

# With restart policy
podman pod create --name mypod --restart=on-failure:5

# Infer container name from pod
podman pod create --name mypod --infra-conmon-pidfile=/var/run/myinfra.pid
```

### Pod Infrastructure Container

Each pod has an infrastructure container that holds shared namespaces:

```bash
# Create pod with custom infra image
podman pod create --name mypod --infra-image kubeinfra:latest

# View infrastructure container
podman pod inspect mypod | grep -A5 InfraContainerId

# The infra container name is <podname>-infra
podman ps --filter pod=myPod
```

## Running Containers in Pods

### Add Container to Pod

```bash
# Run container in existing pod
podman run --pod mypod nginx

# Run with specific name in pod
podman run --pod mypod --name web nginx

# Multiple containers in same pod
podman run --pod mypod --name db postgres
podman run --pod mypod --name cache redis
```

### Pod vs Container Options

```bash
# Network options at pod level (shared)
podman pod create --name mypod \
  --network bridge \
  --publish 8080:80 \
  --dns=8.8.8.8

# All containers inherit these settings
podman run --pod mypod nginx
podman run --pod mypod redis
```

### Pod Startup Order

```bash
# Create pod with dependencies
podman pod create --name app-pod

# Start database first
podman run -d --pod app-pod --name db \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# Start web app (can connect to db via localhost)
podman run -d --pod app-pod --name web \
  -e DB_HOST=localhost \
  myapp:latest
```

## Pod Listing and Inspection

### List Pods

```bash
# Running pods only
podman pod ps

# All pods (including stopped)
podman pod ps -a

# Detailed output
podman pod ps --format table "{{.ID}}\t{{.Name}}\t{{.Status}}\t{{.Containers}}"

# Filter by name
podman pod ps --filter name=myapp

# Show pod with container count
podman pod ps --format "{{.Name}}: {{.NumContainers}} containers"
```

### Inspect Pods

```bash
# Full inspection JSON
podman pod inspect mypod

# Specific fields
podman pod inspect --format '{{.Name}}' mypod
podman pod inspect --format '{{.Status}}' mypod
podman pod inspect --format '{{json .Containers}}' mypod

# View network information
podman pod inspect --format '{{json .Networks}}' mypod

# List containers in pod
podman pod inspect --format '{{range .Containers}}{{.Name}} \n{{end}}' mypod
```

### Pod Statistics

```bash
# Real-time stats for pod
podman pod stats mypod

# One-time stats snapshot
podman pod stats --no-stream mypod

# Stats for all pods
podman pod stats --all

# Specific metrics
podman pod stats --format table "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## Pod Lifecycle Management

### Start and Stop Pods

```bash
# Start pod (starts all containers)
podman pod start mypod

# Stop pod (stops all containers gracefully)
podman pod stop mypod

# Stop with timeout
podman pod stop -t 30 mypod

# Restart pod
podman pod restart mypod

# Kill pod (immediate SIGKILL to all containers)
podman pod kill mypod
```

### Pause and Unpause

```bash
# Pause all containers in pod
podman pod pause mypod

# Resume containers
podman pod unpause mypod

# Check paused status
podman pod ps --filter status=paused
```

### Remove Pods

```bash
# Remove stopped pod (containers must be removed first)
podman pod rm mypod

# Force remove running pod and containers
podman pod rm -f mypod

# Remove all stopped pods
podman pod prune

# Remove specific pod with cleanup
podman pod stop mypod && podman pod rm mypod
```

## Pod Networking

### Shared Network Namespace

```bash
# All containers in pod share same IP
podman pod create --name network-pod
podman run --pod network-pod --name c1 fedora ip addr
podman run --pod network-pod --name c2 fedora ip addr

# Both show same IP address

# Containers can communicate via localhost
podman exec c1 ping -c 3 localhost
podman exec c2 nc -l 8080 &
podman exec c1 curl http://localhost:8080
```

### Port Publishing at Pod Level

```bash
# Publish ports on pod (available to all containers)
podman pod create --name web-pod \
  --publish 8080:80 \
  --publish 8443:443

# Any container in pod can bind to these ports
podman run --pod web-pod nginx
```

### Pod Network Isolation

```bash
# Create isolated network for pods
podman network create app-network

# Create pod on isolated network
podman pod create --name app-pod --network app-network

# Containers automatically join same network
podman run --pod app-pod nginx
```

### Inter-Pod Communication

```bash
# Pods on same network can communicate
podman network create shared-network

podman pod create --name pod1 --network shared-network
podman run -d --pod pod1 --name web nginx

podman pod create --name pod2 --network shared-network
podman run -d --pod pod2 --name client fedora sleep infinity

# Get pod1 IP
POD1_IP=$(podman pod inspect pod1 --format '{{.NetworkSettings.IPAddress}}')

# Access from pod2
podman exec client curl http://$POD1_IP
```

## Pod Logs and Exec

### View Pod Logs

```bash
# Logs from all containers in pod
podman pod logs mypod

# Follow logs
podman pod logs -f mypod

# Specific container in pod
podman pod logs --container web mypod

# Last 100 lines
podman pod logs --tail=100 mypod

# With timestamps
podman pod logs -t mypod
```

### Execute in Pod Containers

```bash
# Exec in specific container within pod
podman exec <container-name> <command>

# List containers to exec into
podman pod inspect mypod --format '{{range .Containers}}{{.Name}} \n{{end}}'

# Or use podman ps with pod filter
podman ps --filter pod=mypod
```

## Pod Restart Policies

### Configure Restart Behavior

```bash
# No restart (default)
podman pod create --name mypod --restart=no

# Restart on failure
podman pod create --name mypod --restart=on-failure

# Restart on failure with max retries
podman pod create --name mypod --restart=on-failure:5

# Always restart
podman pod create --name mypod --restart=always

# Restart unless stopped manually
podman pod create --name mypod --restart=unless-stopped
```

### Container-Level Restart Policies

```bash
# Container can override pod policy
podman run --pod mypod --restart=always nginx

# Useful for different restart needs per container
```

## Advanced Pod Features

### Resource Limits at Pod Level

```bash
# Create pod with resource constraints
podman pod create --name limited-pod \
  --memory=1g \
  --cpus=2.0 \
  --pids-limit=100

# All containers inherit limits (unless overridden)
podman run --pod limited-pod nginx
```

### Pod Labels and Metadata

```bash
# Add labels to pod
podman pod create --name mypod \
  --label app=myapp \
  --label version=1.0 \
  --label team=platform

# View labels
podman pod inspect mypod --format '{{json .Labels}}'

# Filter pods by label
podman pod ps --filter label=app=myapp
```

### Pod Health Checks

```bash
# Health checks configured per container, not pod
podman run --pod mypod \
  --name web \
  --health-cmd="curl -f http://localhost/health || exit 1" \
  --health-interval=30s \
  nginx

# Check health status of all containers in pod
podman ps --filter pod=mypod --format "{{.Names}}\t{{.State}}"
```

### Pod Checkpointing

```bash
# Checkpoint entire pod state
podman pod checkpoint mypod

# Export pod checkpoint
podman pod checkpoint --export=/tmp/pod-checkpoint.tar mypod

# Restore pod from checkpoint
podman pod checkpoint --import=/tmp/pod-checkpoint.tar restored-pod
```

## Pod Volumes

### Shared Volumes in Pods

```bash
# Create volume for pod
podman volume create shared-data

# Mount same volume to multiple containers
podman run -d --pod mypod --name writer \
  -v shared-data:/data \
  fedora tail -f /dev/null

podman run -d --pod mypod --name reader \
  -v shared-data:/data:ro \
  fedora tail -f /dev/null

# Writer can write, reader can read same data
```

### Anonymous Volumes in Pods

```bash
# Container gets anonymous volume
podman run --pod mypod -v /app/data nginx

# Volume is created but not named
# Data persists across container restarts within pod
```

## Pod Templates and Reuse

### Generate Pod Template

```bash
# Create pod with desired configuration
podman pod create --name template-pod \
  --network app-network \
  --publish 8080:80 \
  --label app=myapp

# Export configuration
podman pod inspect template-pod > template-pod.json

# Use as reference for creating similar pods
```

### Systemd Integration with Pods

```bash
# Generate systemd unit for pod
podman generate systemd --new --name mypod > mypod.service

# Install and start
sudo mv mypod.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start mypod
```

## Common Pod Patterns

### Web Application with Database

```bash
# Create pod for app stack
podman pod create --name webapp-pod \
  --network app-network \
  --publish 8080:80

# Add database container
podman run -d --pod webapp-pod --name db \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=webapp \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15

# Add web application
podman run -d --pod webapp-pod --name web \
  -e DATABASE_URL=postgres://user:pass@localhost:5432/webapp \
  myapp:latest

# Add cache
podman run -d --pod webapp-pod --name cache \
  redis:7

# All containers can communicate via localhost
```

### Microservices Pattern

```bash
# Create network for microservices
podman network create microservices-net

# Service 1: API Gateway
podman pod create --name gateway-pod --network microservices-net
podman run -d --pod gateway-pod --name gateway \
  -p 80:8080 \
  kong:latest

# Service 2: User Service
podman pod create --name user-service-pod --network microservices-net
podman run -d --pod user-service-pod --name user-api \
  myapp/user-service:latest

# Service 3: Order Service
podman pod create --name order-service-pod --network microservices-net
podman run -d --pod order-service-pod --name order-api \
  myapp/order-service:latest
```

### Development Environment

```bash
# Create dev pod with shared volumes
podman pod create --name dev-pod \
  --infra-conmon-pidfile=/var/run/dev-infra.pid

# Mount source code
podman run -d --pod dev-pod --name app \
  -v $(pwd):/app:rw \
  -v node_modules:/app/node_modules \
  -w /app \
  node:18-alpine \
  npm run watch

# Mount database for development
podman run -d --pod dev-pod --name db \
  -e POSTGRES_PASSWORD=dev \
  -v dev-pgdata:/var/lib/postgresql/data \
  postgres:15
```

## Pod Troubleshooting

### Pod Won't Start

```bash
# Check pod status
podman pod inspect mypod --format '{{.Status}}'

# Check individual container status
podman ps --filter pod=mypod --format "{{.Names}}\t{{.Status}}"

# View logs from all containers
podman pod logs mypod

# Check for resource constraints
podman pod stats mypod
```

### Network Issues in Pod

```bash
# Verify all containers have same IP
podman pod inspect mypod --format '{{range .Containers}}{{.Name}}: {{.IPAddress}} \n{{end}}'

# Test connectivity between containers
podman exec <container1> ping -c 3 <container2>

# Check port bindings
podman pod inspect mypod --format '{{json .PortMappings}}'
```

### Resource Contention

```bash
# Monitor resource usage per container in pod
podman pod stats --no-stream mypod

# Adjust limits if needed
podman pod update --memory=2g mypod
```

### Cleanup Stale Pods

```bash
# List all stopped pods
podman pod ps -a --filter status=stopped

# Remove all stopped pods
podman pod prune

# Force remove problematic pod
podman pod kill mypod && podman pod rm -f mypod
```

## Pod Best Practices

1. **Use pods for co-located services** that need tight coupling via localhost
2. **Keep pods focused** - one business function per pod
3. **Use labels** to organize and filter pods
4. **Configure restart policies** based on container criticality
5. **Monitor pod stats** regularly for resource optimization
6. **Use named volumes** for persistent data across pod recreations
7. **Leverage systemd/Quadlet** for production pod management

## See Also

- [Core Concepts](01-core-concepts.md) - Container fundamentals
- [Kubernetes Integration](04-kubernetes-integration.md) - Pod-to-K8s conversion
- [Systemd Integration](05-systemd-quadlet.md) - Declarative pod management
