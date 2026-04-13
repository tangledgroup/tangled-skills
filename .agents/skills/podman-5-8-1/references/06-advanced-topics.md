# Podman Advanced Topics

This reference covers advanced Podman features including rootless containers, security profiles (seccomp, AppArmor, SELinux), performance tuning, and comprehensive troubleshooting.

## Rootless Containers

### Overview

Rootless containers run without root privileges, providing enhanced security:
- No need for sudo or root access
- User namespaces isolate container processes
- Container processes map to unprivileged host user
- Ideal for shared environments and CI/CD

### Setup Rootless Podman

```bash
# Install required packages
sudo dnf install podman rootlesskit slirp4netns  # Fedora/RHEL
sudo apt install podman rootlesskit slirp4netns   # Debian/Ubuntu

# Ensure user has subuid/subgid entries
cat /etc/subgid | grep $USER
cat /etc/subuid | grep $USER

# Add user to required groups
sudo usermod -aG storage,lxc $USER

# Restart user session or reboot
newgrp storage
```

### Run Rootless Containers

```bash
# Basic rootless container (default behavior)
podman run fedora /bin/bash

# Explicit user namespace mode
podman run --userns=auto fedora /bin/bash

# Keep root inside container but non-root outside
podman run --userns=auto -u 0 fedora whoami  # Shows "root" inside, safe outside
```

### Rootless Port Mapping

```bash
# Use rootless port forwarding (requires slirp4netns)
podman run -p 8080:80 --userns=auto nginx

# Check port mapping
podman ps --format "{{.Ports}}"

# Note: Rootless ports bind to 127.0.0.1 by default for security
```

### Rootless Networking

```bash
# Default rootless network (slirp4netns)
podman network ls

# Create custom rootless network
podman network create --driver bridge mynetwork

# Use with container
podman run --network mynetwork --userns=auto fedora ip addr
```

### Rootless Volumes

```bash
# Named volumes work in rootless mode
podman volume create mydata
podman run -v mydata:/data --userns=auto fedora ls /data

# Bind mounts to user-writable paths
podman run -v ${HOME}/data:/data --userns=auto fedora ls /data

# Cannot mount system directories (requires root)
```

### Rootless Limitations

- Cannot bind ports below 1024 without workarounds
- Limited access to host devices
- Some security options unavailable (AppArmor, SELinux contexts)
- Network performance slightly reduced with slirp4netns
- Cannot run privileged containers

## Security Profiles

### Seccomp Profiles

#### Overview

Seccomp (Secure Computing Mode) filters system calls:
- Default profile blocks dangerous syscalls
- Custom profiles for specific application needs
- Balance security and functionality

#### Use Default Profile

```bash
# Default seccomp profile (automatic)
podman run fedora uname -a

# Check seccomp status
podman inspect mycontainer --format '{{.HostConfig.SeccompProfile}}'
```

#### Custom Seccomp Profile

```bash
# Create custom profile
cat > /etc/containers/seccomp.json << 'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "defaultErrnoRet": 1,
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_AARCH64"
  ],
  "syscalls": [
    {
      "names": [
        "read",
        "write",
        "open",
        "close",
        "exit",
        "exit_group"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

# Run with custom profile
podman run --security-opt seccomp=/etc/containers/seccomp.json fedora /bin/bash
```

#### Disable Seccomp (Not Recommended)

```bash
# Disable seccomp filtering
podman run --security-opt seccomp=unconfined fedora /bin/bash

# Or use privileged mode (also disables seccomp)
podman run --privileged fedora /bin/bash
```

### AppArmor Profiles

#### Overview

AppArmor provides mandatory access control:
- Profile-based security policy
- Restricts program capabilities
- Docker-compatible profile names

#### Use Default Profile

```bash
# Default AppArmor profile
podman run fedora /bin/bash

# Check AppArmor status
podman inspect mycontainer --format '{{.AppArmorProfile}}'
```

#### Custom AppArmor Profile

```bash
# Create custom profile in /etc/apparmor.d/
sudo tee /etc/apparmor.d/docker-podman-custom > /dev/null << 'EOF'
#include <tunables/global>

profile docker-podman-custom flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  network inet,
  network raw,

  capability setuid,
  capability setgid,
  capability cap_sys_admin,

  /usr/bin/podman ix,
  /lib/x86_64-linux-gnu/** irx,

  # Allow access to specific paths
  /var/lib/containers/** rw,
  /run/user/*/containers/** rw,
}
EOF

# Load profile
sudo apparmor_parser -r /etc/apparmor.d/docker-podman-custom

# Run with custom profile
podman run --security-opt apparmor=docker-podman-custom fedora /bin/bash
```

#### Disable AppArmor

```bash
# Disable AppArmor profiling
podman run --security-opt apparmor=unconfined fedora /bin/bash
```

### SELinux Contexts

#### Overview

SELinux (Security-Enhanced Linux) provides mandatory access control:
- Default on RHEL, Fedora, CentOS
- Label-based security policy
- Automatic context labeling for containers

#### Run with SELinux

```bash
# Default SELinux labeling (automatic)
podman run fedora /bin/bash

# Check SELinux status
getenforce
podman inspect mycontainer --format '{{.ProcessLabel}}'
```

#### Mount Volumes with SELinux

```bash
# Automatic relabeling (shared content)
podman run -v /host/data:/data:Z fedora ls /data

# Private relabeling (container-only access)
podman run -v /host/data:/data:z fedora ls /data

# Disable SELinux labeling
podman run -v /host/data:/data:nosuid fedora ls /data
```

#### SELinux Troubleshooting

```bash
# Check for denials
sudo ausearch -m avc -ts recent

# Analyze denials
sudo audit2allow -a

# Temporary permissive mode (for debugging only)
sudo setenforce 0
# ... test container ...
sudo setenforce 1
```

## Capabilities

### Overview

Linux capabilities divide root privileges into distinct units:
- Drop unnecessary capabilities for security
- Add specific capabilities when required
- Principle of least privilege

### Default Capabilities

```bash
# View default capabilities
podman info | grep -A20 "default_capabilities"

# Typical defaults: CHOWN, DAC_OVERRIDE, FOWNER, etc.
```

### Drop Capabilities

```bash
# Drop all capabilities (very restrictive)
podman run --cap-drop=ALL fedora /bin/bash

# Drop specific capabilities
podman run --cap-drop=NET_ADMIN --cap-drop=SYS_ADMIN fedora /bin/bash

# Common drops for web apps:
podman run \
  --cap-drop=NET_ADMIN \
  --cap-drop=SYS_ADMIN \
  --cap-drop=SYS_MODULE \
  nginx
```

### Add Capabilities

```bash
# Add specific capability
podman run --cap-add=NET_ADMIN fedora ip addr

# Add multiple capabilities
podman run \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  fedora /bin/bash

# Common additions:
# NET_ADMIN - Network configuration
# SYS_TIME - System time modification
# DAC_OVERRIDE - Bypass file permissions
```

### Capability Reference

| Capability | Use Case | Risk Level |
|------------|----------|------------|
| NET_ADMIN | Network configuration, bridges | High |
| SYS_ADMIN | Mount operations, namespaces | Very High |
| SYS_TIME | Clock modification | Medium |
| SYS_PTRACE | Process debugging | High |
| NET_RAW | Raw socket access | Medium |
| DAC_OVERRIDE | Bypass file permissions | High |
| CHOWN | Change file ownership | Low |
| SETUID | Set user ID | Low |

## Resource Management

### CPU Limits

```bash
# Limit to specific CPU cores
podman run --cpuset-cpus="0-1" fedora /bin/bash

# Limit CPU shares (relative weight)
podman run --cpu-shares=512 fedora /bin/bash  # Half of default

# Limit CPU quota (hard limit)
podman run --cpus=1.5 fedora /bin/bash  # 1.5 CPUs

# Combine cpu period and quota
podman run --cpu-period=100000 --cpu-quota=50000 fedora /bin/bash  # 50% CPU
```

### Memory Limits

```bash
# Set memory limit
podman run -m 512M fedora free -m

# Set memory reservation (soft limit)
podman run --memory-reservation=256M fedora /bin/bash

# Set swap limit
podman run -m 512M --swap-memory=1G fedora /bin/bash

# No swap
podman run -m 512M --memory-swap=512M fedora /bin/bash

# Memory swappiness (0-100)
podman run -m 512M --memory-swappiness=0 fedora /bin/bash
```

### PID Limits

```bash
# Limit number of processes
podman run --pids-limit=50 fedora /bin/bash

# Unlimited PIDs
podman run --pids-limit=-1 fedora /bin/bash
```

### Block I/O Limits

```bash
# Set block I/O weight (10-1000)
podman run --blkio-weight=300 fedora /bin/bash

# Device-specific weights
podman run --blkio-weight-device=/dev/sda:500 fedora /bin/bash
```

### Monitor Resources

```bash
# Real-time stats
podman stats

# One-time snapshot
podman stats --no-stream

# Specific container
podman stats --no-stream mycontainer

# Custom format
podman stats --no-stream --format "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## Performance Tuning

### Storage Driver Optimization

```bash
# Check current driver
podman info --format '{{.Storage.Driver}}'

# Recommended: overlay with native lowerdir
cat > /etc/containers/storage/storage.conf << 'EOF'
[storage]
driver = "overlay"
[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
EOF

# For best performance, use native overlay (requires privileged or root)
# fuse-overlayfs for rootless with slight performance overhead
```

### Image Layer Caching

```bash
# Build with layer caching
podman build --layers -t myapp .

# Clean build cache
podman system prune -a

# Increase build cache size
# In containers.conf: runs.lockfile = "/run/libpod/libpod.lock"
```

### Network Performance

```bash
# Use CNI networking for better performance (root only)
podman network create --driver bridge --opt mtu=1500 fastnet

# For rootless, use slirp4netns with tuned settings
cat > ~/.config/containers/containers.conf << 'EOF'
[engine]
network_backend = "cni"
EOF

# Increase file descriptors for high-connection workloads
podman run --sysctl=net.core.somaxconn=1024 nginx
```

### Logging Optimization

```bash
# Set log size limits in containers.conf
cat > ~/.config/containers/containers.conf << 'EOF'
[engine]
log_size_max = "8m"
log_driver = "journald"  # Or "k8s-file", "json-file"
EOF

# Per-container log options
podman run --log-opt max-size=4m --log-opt max-file=2 nginx
```

## Container Registries

### Configure Registries

Edit `~/.config/containers/registries.conf`:

```ini
# Unqualified search registries (in order)
unqualified-search-registries = ["docker.io", "quay.io", "registry.example.com"]

# Registry mirrors
[[registry]]
prefix = "docker.io"
location = "mirror.gcr.io"

[[registry]]
prefix = "registry.example.com"
location = "internal-registry.company.com:5000"
verify = false  # For self-signed certificates

# Insecure registries
[[registry]]
prefix = "insecure-registry.local"
insecure = true
```

### Registry Authentication

```bash
# Login with credentials
podman login registry.example.com

# With specific auth file
podman --authfile=/path/to/auth.json login registry.example.com

# Using Docker-compatible auth
# Podman reads ~/.docker/config.json if no containers auth exists

# Logout
podman logout registry.example.com
podman logout -a  # All registries
```

### Private Registry Setup

```bash
# Create local registry
podman run -d \
  --name registry \
  -p 5000:5000 \
  -v reg-data:/var/lib/registry \
  registry:2

# Tag and push to local registry
podman tag fedora:39 localhost:5000/fedora:39
podman push localhost:5000/fedora:39

# Pull from local registry
podman pull localhost:5000/fedora:39
```

## Troubleshooting

### Debug Mode

```bash
# Run podman with debug logging
podman --log-level=debug run fedora /bin/bash

# Set log level in environment
export CONTAINER_LOG_LEVEL=debug
podman run fedora /bin/bash

# Enable system-wide debug logging
cat > /etc/containers/containers.conf << 'EOF'
[engine]
log_level = "debug"
EOF
```

### Common Issues

#### Container Exits Immediately

```bash
# Check exit code
podman ps -a --format "{{.Names}}\t{{.Status}}"

# View logs
podman logs mycontainer

# Inspect last command
podman inspect --format '{{.Config.Cmd}} {{.Config.Entrypoint}}' mycontainer

# Run with shell to debug
podman run -it --rm fedora /bin/bash
```

#### Permission Denied

```bash
# Check user namespace configuration
cat /etc/subuid | grep $USER
cat /etc/subgid | grep $USER

# For rootless, ensure storage directory permissions
ls -la ~/.local/share/containers/storage/

# Fix storage permissions
podman system reset
```

#### Network Not Working

```bash
# Check network interfaces
podman network ls

# Inspect container networking
podman inspect mycontainer --format '{{json .NetworkSettings}}'

# Restart network stack (root only)
sudo systemctl restart podman-network

# For rootless, check slirp4netns
which slirp4netns
ls -la ~/.local/share/containers/storage/volumes/
```

#### Port Already in Use

```bash
# Check what's using the port
sudo ss -tlnp | grep :8080
lsof -i :8080

# Use different port
podman run -p 8081:80 nginx

# Or bind to specific IP
podman run -p 127.0.0.1:8080:80 nginx
```

#### Image Pull Failures

```bash
# Check registry connectivity
curl -I https://registry.example.com/v2/

# Verify authentication
podman login registry.example.com

# Try explicit transport
podman pull docker://registry.example.com/image:tag

# Check for proxy issues
echo $http_proxy $https_proxy

# Use registry mirror
# Configure in registries.conf
```

### Storage Troubleshooting

```bash
# Check storage usage
podman system df

# Inspect storage driver
podman info --format '{{.Storage.Driver}}'
podman info --format '{{.Storage.GraphRoot}}'

# Clean up unused resources
podman system prune -a

# Reset storage (WARNING: removes all data)
podman system reset
```

### Logs and Diagnostics

```bash
# View container logs
podman logs mycontainer
podman logs -f --tail=100 mycontainer

# System events
podman events

# Inspect detailed configuration
podman inspect mycontainer > inspection.json

# Export container for analysis
podman export mycontainer > container.tar
```

## Best Practices Summary

### Security

1. **Always use rootless mode** when possible
2. **Drop unnecessary capabilities**: `--cap-drop=ALL --cap-add=<needed>`
3. **Use read-only filesystems**: `--read-only --tmpfs /tmp`
4. **Implement seccomp profiles** for production workloads
5. **Scan images for vulnerabilities** before deployment
6. **Use specific image tags**, not `:latest`

### Performance

1. **Use multi-stage builds** to minimize image size
2. **Enable layer caching** in Containerfiles
3. **Set appropriate resource limits** to prevent runaway containers
4. **Use overlay storage driver** for best performance
5. **Tune logging** to prevent disk exhaustion

### Reliability

1. **Implement health checks** for all long-running containers
2. **Use restart policies** based on workload criticality
3. **Configure log rotation** to prevent disk fill
4. **Monitor resource usage** with `podman stats`
5. **Backup named volumes** regularly

### Operations

1. **Use Quadlet for production** deployments
2. **Version control container configurations**
3. **Document custom seccomp/AppArmor profiles**
4. **Implement centralized logging** for production
5. **Test rootless workflows** before deployment

## See Also

- [Core Concepts](01-core-concepts.md) - Container lifecycle management
- [Image Management](02-image-management.md) - Image operations and registry configuration
- [Pod Management](03-pod-management.md) - Multi-container orchestration
- [Systemd Integration](05-systemd-quadlet.md) - Declarative service management
