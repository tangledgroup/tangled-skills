# Podman Systemd and Quadlet Integration

This reference covers systemd unit file generation for containers and the modern Quadlet declarative management system for production container orchestration.

## Overview

Podman provides two approaches for systemd integration:

1. **Generated Unit Files**: Create systemd units from running containers using `podman generate systemd`
2. **Quadlet Files**: Declarative configuration files that Podman converts to systemd units (recommended for production)

**Quadlet advantages:**
- Simpler syntax than systemd units
- Easier to version control and manage
- Better suited for automation
- Officially recommended for production use

## Systemd Unit Generation

### Generate Unit File from Container

```bash
# Generate unit file for single container
podman generate systemd --name=mycontainer > mycontainer.service

# Generate with new service (container starts on boot)
podman generate systemd --new --name=mycontainer > mycontainer.service

# Generate with restart policy
podman generate systemd --restart=always --name=mycontainer > mycontainer.service

# Generate for all containers
podman generate systemd --new --all > podman-containers.service
```

### Generate Unit File from Pod

```bash
# Generate unit for entire pod
podman generate systemd --new --name=mypod > mypod.service

# All containers in pod start together
```

### Install and Use Generated Units

```bash
# Copy to systemd directory (rootful)
sudo mv mycontainer.service /etc/systemd/system/

# Or for user-level services (rootless)
mv mycontainer.service ~/.config/systemd/user/

# Reload systemd
sudo systemctl daemon-reload  # or: systemctl --user daemon-reload

# Start service
sudo systemctl start mycontainer  # or: systemctl --user start mycontainer

# Enable on boot
sudo systemctl enable mycontainer  # or: systemctl --user enable mycontainer

# Check status
systemctl status mycontainer
```

### Unit File Options

```bash
# Generate with specific options
podman generate systemd \
  --new \
  --restart=on-failure:5 \
  --name=myapp \
  --files  # Include container files in unit

# Conditional generation (only if container exists)
podman generate systemd --conditional --name=myapp > myapp.service
```

### Unit File Format

Generated unit files look like:

```ini
[Unit]
Description=Podman mycontainer Container
Documentation=man:podman-run(1)
After=network.target
Wants=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=2
Environment=CONTAINER_UID=1000
Environment=CONTAINER_GID=1000
ExecStartPre=/usr/bin/podman%{suffix} start mycontainer
ExecStart=/usr/bin/sleep infinity
ExecStop=/usr/bin/podman%{suffix} stop -t 5 mycontainer
ExecStopPost=/usr/bin/podman%{suffix} rm -f mycontainer
LimitNOFILE=65536:65536

[Install]
WantedBy=default.target
```

## Quadlet Overview

### What is Quadlet?

Quadlet is a Podman feature that provides simple declarative configuration files for containers, pods, volumes, and networks. These files are automatically converted to systemd units by `podman-quadlet`.

**File locations:**
- System-wide: `/etc/containers/systemd/`
- User-level: `~/.config/containers/systemd/`

**File extensions:**
- `.container` - Single container
- `.kube` - Kubernetes manifest
- `.volume` - Volume definition
- `.network` - Network definition
- `.pod` - Pod definition

### Quadlet vs Generated Units

| Feature | Generated Units | Quadlet |
|---------|----------------|---------|
| Source | Running container | Configuration file |
| Syntax | systemd unit format | Simple key-value |
| Version control | Difficult | Easy |
| Automation | Manual generation | Declarative |
| Recommendation | Development/testing | Production |

## Quadlet Container Files

### Basic Container

```ini
# /etc/containers/systemd/myapp.container
[Unit]
Description=My Application Container

[Container]
Image=fedora:39
Exec=/bin/bash -c "echo hello && sleep infinity"

[Install]
WantedBy=default.target
```

### Named Container with Options

```ini
# /etc/containers/systemd/webapp.container
[Unit]
Description=Web Application Container
After=network.target
Requires=database.container

[Container]
Name=webapp
Image=nginx:1.21
PublishPort=8080:80
Environment=NODE_ENV=production
Environment=API_URL=http://localhost:3000
AddHost=host.docker.internal:10.88.0.1

[Install]
WantedBy=default.target
```

### Container with Volumes

```ini
# /etc/containers/systemd/database.container
[Unit]
Description=PostgreSQL Database

[Container]
Name=postgres-db
Image=postgres:15
Environment=POSTGRES_PASSWORD=secret
Environment=POSTGRES_DB=myapp
Volume=pgdata:/var/lib/postgresql/data
Volume=/etc/localtime:/etc/localtime:ro

[Install]
WantedBy=default.target
```

### Container with Resources

```ini
# /etc/containers/systemd/limited.container
[Unit]
Description=Resource-Limited Container

[Container]
Image=fedora:39
Exec=/usr/bin/stress --cpu 2
MemoryLimit=512M
CPUQuota=50000  # 50% of one CPU
PidsLimit=100

[Install]
WantedBy=default.target
```

### Container with Health Check

```ini
# /etc/containers/systemd/healthy.container
[Unit]
Description=Container with Health Check

[Container]
Image=nginx:1.21
Name=webapp
PublishPort=80:80
HealthCmd=curl -f http://localhost/health || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
HealthStartPeriod=40s

[Install]
WantedBy=default.target
```

### Rootless Container

```ini
# ~/.config/containers/systemd/myapp.container
[Unit]
Description=My Rootless Application

[Container]
Image=fedora:39
Userns=auto
Exec=/bin/bash -c "whoami && sleep infinity"

[Install]
WantedBy=default.target
```

## Quadlet Volume Files

### Create Named Volume

```ini
# /etc/containers/systemd/pgdata.volume
[Unit]
Description=PostgreSQL Data Volume

[Volume]
Driver=local
Label=app=postgres
Label=env=production
```

### Volume with Options

```ini
# /etc/containers/systemd/cache.volume
[Unit]
Description=Application Cache Volume

[Volume]
Driver=local
DriverOpt=o=context="system_u:object_r:container_var_t:s0"
Label=app=myapp
Label=type=cache
```

## Quadlet Network Files

### Bridge Network

```ini
# /etc/containers/systemd/app-network.network
[Unit]
Description=Application Network

[Network]
Driver=bridge
 subnet=10.10.0.0/24
Gateway=10.10.0.1
```

### Network with DNS

```ini
# /etc/containers/systemd/custom-network.network
[Unit]
Description=Custom Network with DNS

[Network]
Driver=bridge
DNS=8.8.8.8
DNS=8.8.4.4
DNSSearch=example.com
```

## Quadlet Pod Files

### Basic Pod

```ini
# /etc/containers/systemd/myapp.pod
[Unit]
Description=My Application Pod

[Pod]
AddHost=host.containers.internal:10.88.0.1
PublishPort=8080:80

[Install]
WantedBy=default.target
```

### Pod with Multiple Containers

First create the pod file, then container files reference it:

```ini
# /etc/containers/systems/webapp.pod
[Unit]
Description=Web Application Pod

[Pod]
PublishPort=80:80
PublishPort=443:443
```

```ini
# /etc/containers/systemd/webapp-web.container
[Unit]
Description=Web Server
Requires=webapp.pod

[Container]
Pod=webapp
Image=nginx:1.21
Name=web
```

```ini
# /etc/containers/systemd/webapp-api.container
[Unit]
Description=API Server
Requires=webapp.pod

[Container]
Pod=webapp
Image=myapp/api:latest
Name=api
Environment=PORT=3000
```

## Quadlet Kubernetes Files

### Play K8s Manifest

```ini
# /etc/containers/systemd/myapp.kube
[Unit]
Description=My Application from Kubernetes Manifest

[Kube]
Path=/etc/kubernetes/manifests/myapp.yaml

[Install]
WantedBy=default.target
```

### Multiple Manifests

```ini
# /etc/containers/systemd/app-stack.kube
[Unit]
Description=Application Stack

[Kube]
Path=/etc/kubernetes/manifests/deployment.yaml
Path=/etc/kubernetes/manifests/service.yaml
Path=/etc/kubernetes/manifests/configmap.yaml
```

## Managing Quadlet Units

### Discover Quadlet Files

```bash
# List all Quadlet files
ls /etc/containers/systemd/*.container
ls ~/.config/containers/systemd/*.container

# Show converted systemd units
systemctl list-units | grep quadlet
```

### Generate Systemd Units from Quadlet

```bash
# Generate all Quadlet units
sudo podman generate systemd --new --all

# Or use quadlet directly
sudo podman quadlet

# Regenerate specific unit
podman quadlet regenerate myapp.container
```

### Reload and Apply Changes

```bash
# After modifying Quadlet files
sudo systemctl daemon-reload

# Start service
sudo systemctl start myapp.container

# Check status
systemctl status myapp.container

# View logs
journalctl -u myapp.container -f
```

### Enable on Boot

```bash
# System-wide (requires root)
sudo systemctl enable myapp.container

# User-level (rootless)
systemctl --user enable myapp.container

# Enable with network dependency
sudo systemctl enable myapp.container.network
```

## Advanced Quadlet Features

### Environment Files

```ini
# /etc/containers/systemd/myapp.container
[Unit]
Description=My Application

[Container]
Image=myapp:latest
EnvFile=/etc/myapp/environment
EnvFile=/etc/myapp/secrets.env  # Multiple files supported

[Install]
WantedBy=default.target
```

Create environment file:
```bash
cat > /etc/myapp/environment << 'EOF'
NODE_ENV=production
LOG_LEVEL=info
DATABASE_URL=postgres://user:pass@localhost/db
EOF
```

### Capabilities and Security

```ini
# /etc/containers/systemd/privileged.container
[Unit]
Description=Privileged Container (use with caution)

[Container]
Image=fedora:39
Privileged=true
CapAdd=SYS_ADMIN
CapDrop=ALL

[Install]
WantedBy=default.target
```

### Restart Policies

```ini
# /etc/containers/systemd/reliable.container
[Unit]
Description=Reliable Container

[Container]
Image=myapp:latest
RestartPolicy=always

[Install]
WantedBy=default.target
```

Restart policy options:
- `no` - Never restart (default)
- `on-failure` - Restart on non-zero exit
- `on-failure:N` - Restart on failure, max N times
- `always` - Always restart
- `unless-stopped` - Restart unless manually stopped

### Timezone and Locale

```ini
# /etc/containers/systemd/localized.container
[Unit]
Description=Localized Container

[Container]
Image=myapp:latest
TZ=America/New_York
Volume=/etc/localtime:/etc/localtime:ro
Volume=/etc/timezone:/etc/timezone:ro

[Install]
WantedBy=default.target
```

## Common Patterns

### Web Application Stack

```ini
# /etc/containers/systemd/webapp-volume.volume
[Volume]
Label=app=webapp
```

```ini
# /etc/containers/systemd/database.container
[Unit]
Description=PostgreSQL Database
Wants=webapp-volume.volume

[Container]
Name=webapp-db
Image=postgres:15
Environment=POSTGRES_PASSWORD_FILE=/run/secrets/db-password
Environment=POSTGRES_DB=webapp
Volume=webapp-volume:/var/lib/postgresql/data
Secret=db-password:/run/secrets/db-password

[Install]
WantedBy=default.target
```

```ini
# /etc/containers/systemd/webapp.container
[Unit]
Description=Web Application
Requires=database.container
After=database.container

[Container]
Name=webapp-web
Image=myapp:latest
PublishPort=8080:80
Environment=DATABASE_URL=postgres://user:pass@localhost:5432/webapp
AddHost=database:127.0.0.1

[Install]
WantedBy=default.target
```

### Development Environment

```ini
# ~/.config/containers/systemd/dev-container.container
[Unit]
Description=Development Environment

[Container]
Name=dev-env
Image=node:18-alpine
Userns=auto
Volume=${PWD}:/app:rw
Volume=/app/node_modules
WorkingDir=/app
Exec=npm run watch
Environment=NODE_ENV=development

[Install]
WantedBy=default.target
```

### Background Worker

```ini
# /etc/containers/systemd/worker.container
[Unit]
Description=Background Job Worker

[Container]
Name=worker
Image=myapp/worker:latest
RestartPolicy=on-failure:3
Environment=QUEUE_URL=redis://localhost:6379
MemoryLimit=1G
CPUQuota=100000  # Full CPU

[Install]
WantedBy=default.target
```

## Troubleshooting

### Quadlet Not Loading

```bash
# Check Quadlet file syntax
podman quadlet validate myapp.container

# View generated systemd unit
systemctl cat myapp.container

# Check for errors in generation
journalctl -u podman-quota.service

# Verify file location
ls -la /etc/containers/systemd/*.container
```

### Container Won't Start

```bash
# Check service status
systemctl status myapp.container

# View logs
journalctl -u myapp.container -f

# Inspect container
podman inspect myapp

# Check for port conflicts
sudo ss -tlnp | grep :8080
```

### Permission Issues

```bash
# For rootless containers, ensure user namespaces work
cat /etc/subgid | grep $USER

# Check volume permissions
ls -la /path/to/volume

# Run with explicit user namespace
# Add to Quadlet file: Userns=auto
```

### Network Problems

```bash
# List networks
podman network ls

# Check container IP
podman inspect myapp --format '{{.NetworkSettings.IPAddress}}'

# Test connectivity between containers
podman exec container1 ping container2
```

## Best Practices

1. **Use Quadlet for production** - Generated units are for development/testing
2. **Version control Quadlet files** - Store in Git alongside application code
3. **Separate secrets from config** - Use environment files or systemd secrets
4. **Define dependencies explicitly** - Use `Requires=` and `After=` in [Unit] section
5. **Set resource limits** - Prevent runaway containers with MemoryLimit/CPUQuota
6. **Implement health checks** - Use HealthCmd for reliable restarts
7. **Use named volumes for persistence** - Not bind mounts for production data
8. **Test locally before deployment** - Validate Quadlet files on development machines

## Migration from Docker Compose

### Docker Compose Example

```yaml
version: '3'
services:
  web:
    image: nginx:1.21
    ports:
      - "8080:80"
    volumes:
      - web-data:/usr/share/nginx/html
    environment:
      - NODE_ENV=production

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  web-data:
  pgdata:
```

### Equivalent Quadlet Files

```ini
# /etc/containers/systemd/pgdata.volume
[Volume]
Label=app=webapp
```

```ini
# /etc/containers/systemd/web-data.volume
[Volume]
Label=app=webapp
```

```ini
# /etc/containers/systemd/db.container
[Unit]
Description=PostgreSQL Database

[Container]
Name=webapp-db
Image=postgres:15
Environment=POSTGRES_PASSWORD=secret
Volume=pgdata:/var/lib/postgresql/data

[Install]
WantedBy=default.target
```

```ini
# /etc/containers/systemd/web.container
[Unit]
Description=Web Server
Requires=db.container
After=db.container

[Container]
Name=webapp-web
Image=nginx:1.21
PublishPort=8080:80
Volume=web-data:/usr/share/nginx/html
Environment=NODE_ENV=production

[Install]
WantedBy=default.target
```

## See Also

- [Core Concepts](01-core-concepts.md) - Container lifecycle management
- [Pod Management](03-pod-management.md) - Multi-container orchestration
- [Kubernetes Integration](04-kubernetes-integration.md) - K8s manifest support
- [Advanced Topics](06-advanced-topics.md) - Security and performance tuning
