# Checkpoint and Restore with crun

Complete guide to container checkpointing and restoration using CRIU (Checkpoint/Restore In Userspace).

## Overview

crun integrates with CRIU to checkpoint running containers and restore them later, enabling:
- Container migration between hosts
- Live container updates
- Save/restore container state
- Reduced downtime during maintenance

## Basic Checkpointing

### Simple Checkpoint

Stop and checkpoint a container:

```bash
crun checkpoint container-id
```

This:
1. Stops the container
2. Creates checkpoint images
3. Saves container state

### Checkpoint with Options

```bash
# Specify image path (where checkpoint files are saved)
crun checkpoint --image-path /var/lib/crun/checkpoints/container-id container-id

# Specify work path for temporary files and logs
crun checkpoint --work-path /tmp/criu-work container-id

# Leave container running after checkpoint
crun checkpoint --leave-running container-id

# Allow open TCP connections
crun checkpoint --tcp-established container-id

# Allow external UNIX sockets
crun checkpoint --ext-unix-sk container-id

# Allow shell jobs
crun checkpoint --shell-job container-id
```

## Advanced Checkpointing

### Pre-Dump (Live Migration)

Pre-dumps reduce downtime by checkpointing memory multiple times before final stop:

```bash
# Step 1: Pre-dump (container keeps running)
crun checkpoint \
  --pre-dump \
  --image-path /checkpoints/pre-dump-1 \
  --work-path /tmp/criu-work \
  container-id

# Step 2: Another pre-dump (optional, reduces final downtime)
crun checkpoint \
  --pre-dump \
  --image-path /checkpoints/pre-dump-2 \
  --parent-path ../pre-dump-1 \
  --work-path /tmp/criu-work \
  container-id

# Step 3: Final checkpoint (stops container)
crun checkpoint \
  --image-path /checkpoints/final \
  --parent-path ../pre-dump-2 \
  --work-path /tmp/criu-work \
  container-id
```

**Important:** `--parent-path` must be a **relative path** from the actual checkpoint directory. Absolute paths will fail.

### Checkpoint Features

**TCP Established Connections:**
```bash
# Allow checkpointing containers with open TCP connections
crun checkpoint --tcp-established container-id
```

**External UNIX Sockets:**
```bash
# Include external UNIX socket state
crun checkpoint --ext-unix-sk container-id
```

**Shell Jobs:**
```bash
# Preserve shell job control state
crun checkpoint --shell-job container-id
```

## Restoring Containers

### Basic Restore

Restore from checkpoint:

```bash
crun restore container-id
```

This recreates the container from the last checkpoint.

### Restore with Options

```bash
# Specify bundle directory
crun restore --bundle /path/to/bundle container-id

# Specify image path
crun restore --image-path /var/lib/crun/checkpoints/container-id container-id

# Specify work path
crun restore --work-path /tmp/criu-work container-id

# Detach after restore
crun restore --detach container-id

# Save restored container PID
crun restore --pid-file /tmp/restored.pid container-id

# Allow TCP established connections
crun restore --tcp-established container-id

# Allow external UNIX sockets
crun restore --ext-unix container-id

# Allow shell jobs
crun restore --shell-job container-id
```

### Restore with LSM Profiles

Apply security profiles during restore:

```bash
# Apply AppArmor profile
crun restore \
  --lsm-profile apparmor:my-profile \
  container-id

# Apply SELinux context
crun restore \
  --lsm-profile selinux:system_u:object_r:container_t:s0 \
  container-id
```

### Restore with Mount Context

Override LSM mount context during restore (useful for Pod restoration):

```bash
crun restore \
  --lsm-mount-context "system_u:object_r:container_t:s0" \
  container-id
```

This replaces existing mount context information with the specified value.

## CRIU Manage Cgroups Mode

Control how CRIU manages cgroups during checkpoint/restore:

```bash
# Soft mode (default): CRIU tries to manage cgroups, falls back if fails
crun checkpoint --manage-cgroups-mode soft container-id

# Ignore mode: CRIU doesn't manage cgroups
crun checkpoint --manage-cgroups-mode ignore container-id

# Full mode: CRIU fully manages cgroups
crun checkpoint --manage-cgroups-mode full container-id

# Strict mode: CRIU manages cgroups, fails if cannot
crun checkpoint --manage-cgroups-mode strict container-id
```

Same options apply to restore:

```bash
crun restore --manage-cgroups-mode soft container-id
```

## CRIU Configuration

### Annotation-Based Config

Specify CRIU configuration file via annotation:

```json
{
  "annotations": {
    "org.criu.config": "/etc/criu/custom-crun.conf"
  }
}
```

### Configuration File Lookup Order

crun searches for CRIU config in this order:
1. Annotation `org.criu.config` value
2. `/etc/criu/crun.conf`
3. `/etc/criu/runc.conf` (for runc compatibility)

**Requires CRIU version 4.2 or newer.**

### Example CRIU Configuration

```conf
# /etc/criu/crun.conf
tcp-established = true
ext-unix = socket
shell-job = true
log-file = /var/log/criu/container.log
log-level = info
manage-cgroups-mode = soft
```

Options in config file override crun's default CRIU options.

## Checkpoint Directory Structure

After checkpointing, the image directory contains:

```
/checkpoints/container-id/
├── img/                  # CRIU image files
│   ├── tasks/           # Task state
│   ├── files/           # File descriptors
│   ├── tty/             # TTY state
│   └── ...
├──Criu.conf            # CRIU configuration used
├──dump.rst             # Statistics
└──log                  # CRIU log file
```

## Migration Workflow

### Full Migration Example

**Source Host:**

```bash
# 1. Pre-dump to minimize downtime
crun checkpoint \
  --pre-dump \
  --image-path /migration/pre1 \
  --tcp-established \
  --ext-unix-sk \
  my-app

# 2. Transfer pre-dump to destination
rsync -avz /migration/pre1 user@destination:/migration/pre1

# 3. Final checkpoint (brief downtime)
crun checkpoint \
  --image-path /migration/final \
  --parent-path ../pre1 \
  --tcp-established \
  --ext-unix-sk \
  my-app

# 4. Transfer final checkpoint
rsync -avz /migration/final user@destination:/migration/final

# 5. Delete source container
crun delete my-app
```

**Destination Host:**

```bash
# 1. Ensure bundle exists (config.json + rootfs)
# Copy from source or recreate

# 2. Restore container
crun restore \
  --bundle /path/to/bundle \
  --image-path /migration/final \
  --tcp-established \
  --ext-unix \
  my-app

# 3. Verify container is running
crun ps my-app
```

## Requirements and Limitations

### System Requirements

- **CRIU installed** on both source and destination
- **Same kernel version** (or very similar) recommended
- **Compatible filesystems** for rootfs
- **Sufficient privileges** (root or CAP_SYS_ADMIN)

### What Can Be Checkpointed

- Container processes and memory
- Open file descriptors
- Network connections (with `--tcp-established`)
- UNIX sockets (with `--ext-unix-sk`)
- Namespace state
- cgroup configuration

### Known Limitations

- Some kernel modules may not be fully supported
- GPU devices and specialized hardware require extra configuration
- NFS mounts have limited support
- Some applications with complex state may not restore correctly
- Requires CRIU 4.2+ for custom config file support

## Troubleshooting

### Check CRIU Logs

```bash
# View CRIU log from checkpoint
cat /checkpoints/container-id/log

# Enable verbose crun logging
crun --debug checkpoint container-id
```

### Common Issues

**"TCP sockets cannot be dumped":**
```bash
# Use --tcp-established flag
crun checkpoint --tcp-established container-id
```

**"Cgroup restore failed":**
```bash
# Try different manage-cgroups-mode
crun restore --manage-cgroups-mode ignore container-id
```

**"File descriptor leaked":**
```bash
# Check application doesn't hold unexpected FDs
# Use --ext-unix-sk for external sockets
crun checkpoint --ext-unix-sk container-id
```

**"Kernel version mismatch":**
- Ensure source and destination have similar kernel versions
- Some features require specific kernel versions

### Verification Commands

```bash
# Check CRIU version
criu --version

# Verify CRIU features
criu feature-check --all

# List checkpointed containers
crun list

# Check container state
crun state container-id
```

## Best Practices

1. **Test checkpoint/restore** in non-production environment first
2. **Use pre-dumps** for production migrations to minimize downtime
3. **Enable TCP established** if container has network connections
4. **Keep CRIU logs** for troubleshooting
5. **Verify application state** after restore
6. **Use relative paths** for `--parent-path` in multi-step checkpoints
7. **Monitor memory usage** during checkpoint (can be high)
8. **Ensure sufficient disk space** for checkpoint images

## Performance Considerations

- **Pre-dumps reduce final downtime** but increase total migration time
- **Memory-intensive applications** take longer to checkpoint
- **Network state adds overhead** but enables live migration
- **Multiple pre-dumps** can further reduce final stop time
- **Checkpoint size** roughly equals container RSS memory usage
