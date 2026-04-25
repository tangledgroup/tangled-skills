---
name: podman-5-8-1
description: Comprehensive toolkit for Podman 5.8.1 container engine providing daemonless container management with Docker-compatible CLI, rootless containers, pods, images, volumes, networks, Kubernetes integration, and systemd/Quadlet declarative management. Use when building, running, or managing containers without a daemon, implementing rootless container workflows, orchestrating pods, integrating with Kubernetes, automating with systemd services, or migrating from Docker.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - containers
  - podman
  - docker-alternative
  - rootless-containers
  - pods
  - container-engine
  - kubernetes
  - systemd
  - quadlet
category: devops
required_environment_variables: []
compatibility:
  platforms:
    - linux
    - macOS (remote client)
    - windows (remote client, WSL2 native)
  agents:
    - pi
    - opencode
    - claude
    - hermes
---

# Podman 5.8.1


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

Comprehensive toolkit for Podman 5.8.1 container engine providing daemonless container management with Docker-compatible CLI, rootless containers, pods, images, volumes, networks, Kubernetes integration, and systemd/Quadlet declarative management. Use when building, running, or managing containers without a daemon, implementing rootless container workflows, orchestrating pods, integrating with Kubernetes, automating with systemd services, or migrating from Docker.

Podman (Pod Manager) is a fully featured, daemonless container engine that provides Docker-compatible CLI for managing pods, containers, and images. Most commands can run as a regular user without requiring root privileges, making it ideal for rootless container workflows, CI/CD pipelines, and shared environments.

**Key features:**
- Daemonless architecture (no central daemon required)
- Rootless container support by default
- Docker CLI compatibility (`alias docker=podman`)
- Pod support for grouping related containers
- Kubernetes integration (play kube, generate kube)
- Systemd and Quadlet declarative management
- Built-in image building (uses Buildah internally)
- Multi-architecture image support
- Container signing and verification

## When to Use

- Running containers without root privileges
- Migrating from Docker to a daemonless alternative
- Managing groups of containers as pods
- Generating Kubernetes manifests from running containers/pods
- Creating systemd services for containers using Quadlet
- Building container images with Containerfiles
- Working in CI/CD environments where daemons are unavailable
- Implementing rootless container workflows
- Managing container registries and image authentication

## Setup

### Installation

**Fedora/RHEL:**
```bash
sudo dnf install podman
```

**Debian/Ubuntu:**
```bash
sudo apt install podman
```

**Arch Linux:**
```bash
sudo pacman -S podman
```

**macOS/Windows:** Use Podman Desktop or connect to remote Linux host via `--connection` flag.

### Basic Configuration

Podman reads configuration from `/etc/containers/containers.conf` (system-wide) and `~/.config/containers/containers.conf` (user-specific). View current settings:

```bash
podman info
```

### Quick Start

See [Core Concepts](references/01-core-concepts.md) for fundamental workflows.

## Quick Start

### Run a Simple Container

```bash
# Run hello world container
podman run fedora echo "Hello from Podman"

# Run interactive container
podman run -it fedora /bin/bash

# Run with port mapping
podman run -p 8080:80 nginx
```

See [Core Concepts](references/01-core-concepts.md) for detailed container management.

### Manage Images

```bash
# Pull an image
podman pull fedora:latest

# List images
podman images

# Build from Containerfile
podman build -t myapp:latest .

# Push to registry
podman push myapp:latest quay.io/username/myapp
```

Refer to [Image Management](references/02-image-management.md) for comprehensive image workflows.

### Work with Pods

```bash
# Create a pod
podman pod create --name mypod

# Run container in pod
podman run --pod mypod nginx

# List pods
podman ps -a --format table "{{.PodName}}\t{{.Names}}"
```

See [Pod Management](references/03-pod-management.md) for advanced pod operations.

### Kubernetes Integration

```bash
# Generate Kubernetes YAML from running container
podman generate kube mycontainer > pod.yaml

# Play containers from Kubernetes YAML
podman play kube pod.yaml
```

Refer to [Kubernetes Integration](references/04-kubernetes-integration.md) for detailed workflows.

### Systemd and Quadlet

```bash
# Generate systemd unit file
podman generate systemd --new --name mycontainer > mycontainer.service

# Or use Quadlet (simpler declarative format)
cat > /etc/containers/systemd/myapp.container << 'EOF'
[Unit]
Description=My Application Container
[Container]
Image=fedora
Exec=/bin/bash -c "echo hello"
[Install]
WantedBy=default.target
EOF

# Reload systemd and start
sudo systemctl daemon-reload
sudo systemctl start myapp.container
```

See [Systemd Integration](references/05-systemd-quadlet.md) for comprehensive service management.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Container lifecycle, common operations, networking basics, volume management
- [`references/02-image-management.md`](references/02-image-management.md) - Image pull/push/build, registry authentication, multi-arch images, image signing
- [`references/03-pod-management.md`](references/03-pod-management.md) - Pod creation, container orchestration within pods, pod networking
- [`references/04-kubernetes-integration.md`](references/04-kubernetes-integration.md) - Generate/play Kubernetes manifests, compatibility notes
- [`references/05-systemd-quadlet.md`](references/05-systemd-quadlet.md) - Systemd unit generation, Quadlet declarative management, service lifecycle
- [`references/06-advanced-topics.md`](references/06-advanced-topics.md) - Rootless containers, security profiles, seccomp/AppArmor, SELinux, performance tuning

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/podman-5-8-1/`). All paths are relative to this directory.

## Common Patterns

### Docker Migration

Most Docker commands work with Podman:
```bash
# Add alias for compatibility
alias docker=podman

# These work identically
docker run -d -p 80:80 nginx      # → podman run -d -p 80:80 nginx
docker ps                         # → podman ps
docker build -t myapp .           # → podman build -t myapp .
```

### Rootless Container Workflow

```bash
# Run as regular user (no sudo needed)
podman run --userns=auto fedora /bin/bash

# Use rootless port forwarding
podman run -p 8080:80 --userns=auto nginx
```

### Development Workflows

```bash
# Mount local code into container
podman run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  node:18-alpine npm install

# Use existing user ID for file ownership
podman run -it --rm \
  -u $(id -u):$(id -g) \
  -v $(pwd):/workspace \
  python:3.11-slim bash
```

## Troubleshooting

### Container Won't Start

```bash
# Check container logs
podman logs <container-name>

# Inspect container configuration
podman inspect <container-name>

# Check for port conflicts
sudo ss -tlnp | grep :8080
```

### Permission Issues

```bash
# Ensure user is in correct groups
sudo usermod -aG storage,lxc $USER

# For rootless containers, check user namespace configuration
cat /etc/subgid | grep $USER
```

### Network Problems

```bash
# List networks
podman network ls

# Check container IP
podman inspect --format '{{.NetworkSettings.IPAddress}}' <container>

# Restart libpod network
sudo systemctl restart podman-network
```

See [Advanced Topics](references/06-advanced-topics.md) for detailed troubleshooting guides.

## Environment Variables

Podman supports these environment variables for configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `CONTAINER_HOST` | Remote Podman socket URL | `unix:/run/user/$UID/podman/podman.sock` |
| `CONTAINER_TLS_VERIFY` | TLS verification for remote connections | `false` |
| `CONTAINER_CONFIG` | Path to containers.conf | `~/.config/containers/containers.conf` |
| `REGISTRY_AUTH_FILE` | Authentication file path | `$XDG_RUNTIME_DIR/containers/auth.json` |
| `PODMAN_SYSTEMD_UNIT` | Systemd unit directory | `~/.config/systemd/user` |

## Best Practices

1. **Use rootless containers** whenever possible for improved security
2. **Pin image versions** with specific tags or digests, not `:latest`
3. **Use Quadlet for production services** instead of systemd units generated by Podman
4. **Implement health checks** for long-running containers
5. **Clean up unused resources** regularly with `podman system prune`
6. **Use pods for multi-container applications** to share namespaces
7. **Leverage Kubernetes manifests** for portable deployments

## Validation Checklist

- [ ] Podman installed and accessible via `podman --version`
- [ ] User can run containers without sudo (rootless mode)
- [ ] Container registry authentication configured if needed
- [ ] Storage driver working correctly (`podman info | grep storage`)
- [ ] Network interfaces available (`podman network ls`)

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
