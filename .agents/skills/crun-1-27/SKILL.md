---
name: crun-1-27
description: Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high performance. Use when deploying containers via podman, building container orchestration tools, checkpointing/restoring containers with CRIU, running WebAssembly workloads, or needing faster container startup than runc provides.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - oci-runtime
  - containers
  - podman
  - checkpointing
  - criu
  - wasi
  - webassembly
  - cgroups
category: devops
external_references:
  - https://github.com/containers/crun
  - https://github.com/containers/crun/blob/main/Documentation/crun.md
---
## Overview
Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high performance. Use when deploying containers via podman, building container orchestration tools, checkpointing/restoring containers with CRIU, running WebAssembly workloads, or needing faster container startup than runc provides.

A fast and lightweight OCI (Open Container Initiative) container runtime fully written in C. crun provides lower memory footprint and faster execution compared to runc, making it ideal for resource-constrained environments and high-performance container workloads.

## When to Use
- Running containers with podman as the default OCI runtime
- Needing faster container startup times (approximately 50% faster than runc)
- Deploying in memory-constrained environments (works with as little as 512KB memory limit)
- Checkpointing and restoring running containers using CRIU
- Running WebAssembly workloads natively with WASI support
- Building container orchestration tools that need a runtime library
- Working with cgroup v1 or v2 systems

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Usage Examples
### Installation

**Fedora:**
```bash
sudo dnf install crun
```

**Ubuntu/Debian:**
```bash
sudo apt-get install crun
```

**Alpine:**
```bash
apk add crun
```

### Basic Usage

Run a container directly:
```bash
# Create bundle directory with config.json and rootfs
crun run my-container
```

Use with podman (recommended):
```bash
podman --runtime /usr/bin/crun run -it fedora /bin/bash
```

List running containers:
```bash
crun list
```

## Core Commands
### Container Lifecycle Management

**Create and start a container:**
```bash
# Create only (detached)
crun create --bundle /path/to/bundle container-id

# Start previously created container
crun start container-id

# Create and start in one step
crun run --bundle /path/to/bundle container-id
```

**Execute commands in running containers:**
```bash
# Run command in container
crun exec container-id /bin/bash

# With specific user and working directory
crun exec -u 1000:1000 --cwd /home/user container-id ls -la

# Allocate TTY
crun exec -t container-id top
```

**Monitor containers:**
```bash
# List all containers
crun list

# Quiet mode (IDs only)
crun list -q

# Show processes in container
crun ps container-id

# JSON output format
crun ps --format json container-id

# Check container state
crun state container-id
```

**Control containers:**
```bash
# Pause container (freeze all processes)
crun pause container-id

# Resume container
crun resume container-id

# Send signal to container process
crun kill container-id

# Send SIGTERM (default)
crun kill container-id SIGTERM

# Kill all processes in container
crun kill --all container-id
```

**Cleanup:**
```bash
# Remove container definition
crun delete container-id

# Force delete running container
crun delete --force container-id

# Delete multiple containers by regex
crun delete --regex "myapp-.*"
```

### Resource Updates

Update resource limits on running containers:
```bash
# Update memory limit
crun update --memory 512m container-id

# Update CPU shares
crun update --cpu-share 512 container-id

# Update from resources file
crun update --resources /path/to/resources.json container-id

# Set PID limit
crun update --pids-limit 100 container-id

# Set CPU quota and period
crun update --cpu-quota 80000 --cpu-period 100000 container-id
```

See [Resource Management](reference/02-resource-management.md) for detailed resource options.

## Advanced Topics
## Advanced Topics

- [Oci Bundle Setup](reference/01-oci-bundle-setup.md)
- [Resource Management](reference/02-resource-management.md)
- [Checkpoint Restore](reference/03-checkpoint-restore.md)
- [Advanced Features](reference/04-advanced-features.md)
- [Troubleshooting](reference/05-troubleshooting.md)

## Troubleshooting
**Container won't start:**
```bash
# Enable debug logging
crun --debug run container-id

# Log to file
crun --log file:/var/log/crun.log run container-id

# Log to journald
crun --log journald:mycontainer run container-id
```

**Cgroup issues:**
```bash
# Use systemd cgroup manager
crun --systemd-cgroup run container-id

# Specify cgroup manager explicitly
crun --cgroup-manager systemd run container-id

# Disable cgroups (not recommended for production)
crun --cgroup-manager disabled run container-id
```

**State directory issues:**
```bash
# Override state directory
crun --root /custom/crun-state run container-id

# Check default state location
# Root: /run/crun
# Unprivileged: $XDG_RUNTIME_DIR/crun
```

For more troubleshooting, see [reference/05-troubleshooting.md](reference/05-troubleshooting.md).

## Performance Comparison
crun outperforms runc in both speed and memory usage:

| Metric | crun | runc | Improvement |
|--------|------|------|-------------|
| 100 container startups | 1.69s | 3.34s | -49.4% |
| Minimum memory limit | 512KB | 4MB+ | 87.5% less |

## Key Features
- **Low memory footprint**: Written in C, no runtime dependencies
- **Fast startup**: No re-exec pattern like runc
- **CRIU integration**: Native checkpoint/restore support
- **WebAssembly support**: Run WASI modules natively
- **Cgroup v2 native**: Full support with automatic v1 conversion
- **Library mode**: Use libcrun in your applications
- **Rootless containers**: Automatic user namespace creation

## Compatibility
- **OCI Runtime Spec**: Fully compliant
- **Podman**: Default runtime on many distributions
- **Buildah**: Compatible image building
- **Skopeo**: Image transport support
- **cgroup v1/v2**: Automatic conversion between versions

**Note:** cgroup v1 support is deprecated and will be removed in future releases.

