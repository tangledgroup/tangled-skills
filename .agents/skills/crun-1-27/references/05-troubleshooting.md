# Troubleshooting crun

Comprehensive guide to diagnosing and resolving common issues with crun.

## Debugging Basics

### Enable Verbose Logging

```bash
# Debug mode with verbose output
crun --debug run container-id

# Create command with debug
crun --debug create container-id
crun --debug start container-id
```

### Log to File

```bash
# Log errors and warnings to file
crun --log file:/var/log/crun.log run container-id

# Custom log path
crun --log file:/tmp/mycontainer.log run container-id
```

### Log to Systemd Journald

```bash
crun --log journald:mycontainer run container-id

# View logs
journalctl -t mycontainer
journalctl -u mycontainer
```

### Log to Syslog

```bash
crun --log syslog:myapp run container-id
```

### Control Log Level

```bash
# Debug level (most verbose)
crun --log-level debug run container-id

# Warning level
crun --log-level warning run container-id

# Error level (default, least verbose)
crun --log-level error run container-id
```

### Log Format

```bash
# JSON format for parsing
crun --log-format json run container-id

# Text format (default)
crun --log-format text run container-id
```

## Common Issues and Solutions

### Container Won't Start

**Symptom:** `crun run` fails immediately

**Diagnosis:**

```bash
# Enable debug logging
crun --debug run container-id 2>&1 | tee /tmp/crun-error.log

# Check config.json validity
cat config.json | python3 -m json.tool

# Verify rootfs exists and is accessible
ls -la rootfs/

# Check if process executable exists
ls -la rootfs/bin/bash  # or whatever process.args[0] specifies
```

**Common causes:**

1. **Missing executable in rootfs**
   ```bash
   # Solution: Ensure the binary exists in rootfs
   cp /bin/bash my-container/rootfs/bin/
   ```

2. **Invalid config.json**
   ```bash
   # Solution: Regenerate config
   crun spec --bundle my-container
   
   # Or fix JSON syntax errors
   ```

3. **Permission denied on rootfs**
   ```bash
   # Solution: Fix permissions
   chmod 755 my-container/rootfs
   chown -R root:root my-container/rootfs
   ```

4. **Missing libraries in rootfs**
   ```bash
   # Check required libraries
   ldd /bin/bash
   
   # Solution: Copy required libraries to rootfs
   ```

### Cgroup Errors

**Symptom:** `cgroup kill: no cgroup controller` or similar

**Diagnosis:**

```bash
# Check cgroup version
stat -fc %T /sys/fs/cgroup/

# List available cgroup controllers
ls /sys/fs/cgroup/

# Check if systemd is running
systemctl is-system-running
```

**Solutions:**

1. **Use systemd cgroup manager**
   ```bash
   crun --systemd-cgroup run container-id
   
   # Or explicitly
   crun --cgroup-manager systemd run container-id
   ```

2. **Use cgroupfs directly**
   ```bash
   crun --cgroup-manager cgroupfs run container-id
   ```

3. **Disable cgroups (not recommended for production)**
   ```bash
   crun --cgroup-manager disabled run container-id
   ```

4. **cgroup v1 on v2 system**
   ```json
   {
     "annotations": {
       "run.oci.systemd.force_cgroup_v1": "/sys/fs/cgroup/systemd"
     }
   }
   ```

### Memory Limit Issues

**Symptom:** Container killed immediately or won't start with memory limits

**Diagnosis:**

```bash
# Check available memory
free -h

# Check cgroup memory limits
cat /sys/fs/cgroup/memory.max  # v2
cat /sys/fs/cgroup/*/memory.limit_in_bytes  # v1

# View OOM kills
dmesg | grep -i "killed process"
```

**Solutions:**

1. **Increase memory limit**
   ```bash
   # In config.json
   {
     "linux": {
       "resources": {
         "memory": {
           "limit": 536870912
         }
       }
     }
   }
   ```

2. **Use memory reservation instead of hard limit**
   ```json
   {
     "linux": {
       "resources": {
         "memory": {
           "limit": 536870912,
           "reservation": 268435456
         }
       }
     }
   }
   ```

3. **Check swap configuration**
   ```json
   {
     "linux": {
       "resources": {
         "memory": {
           "limit": 536870912,
           "swap": 1073741824
         }
       }
     }
   }
   ```

### Network Issues

**Symptom:** Container can't connect to network

**Diagnosis:**

```bash
# Check network namespace
crun exec container-id ip addr

# Check routing
crun exec container-id ip route

# Test connectivity
crun exec container-id ping -c 3 8.8.8.8
```

**Solutions:**

1. **Ensure network namespace is configured**
   ```json
   {
     "linux": {
       "namespaces": [
         {"type": "network"}
       ]
     }
   }
   ```

2. **Check host networking**
   ```bash
   # Verify bridge exists (if using one)
   ip link show
   
   # Check iptables rules
   iptables -L -n
   ```

3. **Use host network namespace (not recommended)**
   ```json
   {
     "linux": {
       "namespaces": [
         {
           "type": "network",
           "path": "/proc/self/ns/net"
         }
       ]
     }
   }
   ```

### User Namespace Errors

**Symptom:** `Operation not permitted` or user mapping failures

**Diagnosis:**

```bash
# Check subuid/subgid ranges
cat /etc/subuid
cat /etc/subgid

# Check current user namespace
cat /proc/self/nsinfo

# Verify user mappings
cat /proc/self/uid_map
cat /proc/self/gid_map
```

**Solutions:**

1. **Add user to subuid/subgid ranges**
   ```bash
   # Edit /etc/subuid and /etc/subgid
   echo "myuser:100000:65536" >> /etc/subuid
   echo "myuser:100000:65536" >> /etc/subgid
   ```

2. **Run as root (if user namespace not required)**
   ```bash
   sudo crun run container-id
   ```

3. **Generate rootless config**
   ```bash
   crun spec --bundle my-container --rootless
   ```

4. **Check kernel user namespace support**
   ```bash
   # Verify kernel supports user namespaces
   grep USERNS /boot/config-$(uname -r)
   ```

### Checkpoint/Restore Failures

**Symptom:** CRIU checkpoint or restore fails

**Diagnosis:**

```bash
# Check CRIU version
criu --version

# Verify CRIU features
criu feature-check --all

# View CRIU logs
cat /checkpoints/container-id/log

# Enable crun debug
crun --debug checkpoint container-id
```

**Common issues:**

1. **TCP connections not supported**
   ```bash
   # Solution: Use --tcp-established
   crun checkpoint --tcp-established container-id
   ```

2. **Cgroup restore failed**
   ```bash
   # Solution: Try different manage-cgroups-mode
   crun restore --manage-cgroups-mode ignore container-id
   ```

3. **File descriptor leaks**
   ```bash
   # Solution: Use --ext-unix-sk
   crun checkpoint --ext-unix-sk container-id
   ```

4. **Kernel version mismatch**
   - Ensure source and destination have similar kernel versions
   - Some features require specific kernel versions

5. **Missing CRIU configuration**
   ```bash
   # Create /etc/criu/crun.conf
   cat > /etc/criu/crun.conf << 'EOF'
   tcp-established = true
   ext-unix = socket
   shell-job = true
   EOF
   ```

### Mount Errors

**Symptom:** Mount failures or permission denied on mounted paths

**Diagnosis:**

```bash
# Check mount points inside container
crun exec container-id mount | grep /mnt

# Verify source paths exist
ls -la /host/data/path

# Check mount options
crun --debug run container-id 2>&1 | grep -i mount
```

**Solutions:**

1. **Fix bind mount source path**
   ```json
   {
     "mounts": [
       {
         "destination": "/mnt/data",
         "type": "bind",
         "source": "/absolute/path/on/host",
         "options": ["rbind", "rw"]
       }
     ]
   }
   ```

2. **Adjust mount options**
   ```json
   {
     "mounts": [
       {
         "destination": "/mnt/data",
         "type": "bind",
         "source": "/host/data",
         "options": ["rbind", "ro"]  # Try read-only
       }
     ]
   }
   ```

3. **Use tmpcopyup for writable configs**
   ```json
   {
     "mounts": [
       {
         "destination": "/etc/app",
         "type": "tmpfs",
         "source": "tmpfs",
         "options": ["rw", "tmpcopyup"]
       }
     ]
   }
   ```

### State Directory Issues

**Symptom:** Can't find container state or permission denied

**Diagnosis:**

```bash
# Check default state directory
# Root: /run/crun
# Unprivileged: $XDG_RUNTIME_DIR/crun

# List containers
crun list

# Check state directory permissions
ls -la /run/crun/
ls -la $XDG_RUNTIME_DIR/crun/
```

**Solutions:**

1. **Override state directory**
   ```bash
   crun --root /custom/crun-state run container-id
   ```

2. **Fix XDG_RUNTIME_DIR for rootless**
   ```bash
   export XDG_RUNTIME_DIR=/run/user/$(id -u)
   mkdir -p $XDG_RUNTIME_DIR/crun
   ```

3. **Ensure state directory exists and is writable**
   ```bash
   mkdir -p /custom/crun-state
   chmod 700 /custom/crun-state
   ```

### PID File Issues

**Symptom:** Can't get container process PID

**Diagnosis:**

```bash
# Check if PID file was created
cat /tmp/container.pid

# List running processes in container
crun ps container-id
```

**Solutions:**

1. **Specify PID file explicitly**
   ```bash
   crun run --pid-file /tmp/container.pid container-id
   ```

2. **Use ps command instead**
   ```bash
   crun ps --format json container-id | jq '.[0].pid'
   ```

## Performance Issues

### Slow Container Startup

**Diagnosis:**

```bash
# Time container startup
time crun run container-id

# Profile with strace
strace -tt -T -o /tmp/crun-strace.log crun run container-id
```

**Optimizations:**

1. **Use crun instead of runc** (already doing this!)
2. **Reduce rootfs size** - only include necessary files
3. **Use overlay filesystem** for faster layer merging
4. **Check disk I/O performance**

### High Memory Usage

**Diagnosis:**

```bash
# Check container memory usage
cat /sys/fs/cgroup/container/memory.current  # v2

# Compare with limit
cat /sys/fs/cgroup/container/memory.max
```

**Solutions:**

1. **Set appropriate memory limits**
2. **Use memory reservation for soft limits**
3. **Enable swap if needed**
4. **Profile application memory usage**

## Verification Commands

### Check crun Installation

```bash
# Version
crun --version

# Help
crun --help

# Usage summary
crun --usage
```

### Check Container Status

```bash
# List all containers
crun list

# Quiet mode (IDs only)
crun list -q

# Container state
crun state container-id

# Processes in container
crun ps container-id

# JSON output
crun ps --format json container-id
```

### Check System Compatibility

```bash
# Cgroup version
stat -fc %T /sys/fs/cgroup/

# Kernel version
uname -r

# CRIU version (for checkpoint/restore)
criu --version

# CRIU feature check
criu feature-check --all
```

## Getting Help

### Log Collection

For reporting issues, collect:

```bash
# crun version
crun --version > /tmp/crun-info.txt

# System info
uname -a >> /tmp/crun-info.txt
cat /etc/os-release >> /tmp/crun-info.txt

# Cgroup info
echo "=== Cgroup version ===" >> /tmp/crun-info.txt
stat -fc %T /sys/fs/cgroup/ >> /tmp/crun-info.txt

# Debug log
crun --debug --log file:/tmp/crun-debug.log run container-id 2>&1

# Config file
cp config.json /tmp/config.json
```

### Reporting Issues

When reporting bugs to the crun project:

1. Include crun version and system information
2. Provide minimal reproducing example (config.json)
3. Attach debug logs
4. Describe expected vs actual behavior
5. Note any workarounds discovered

### Resources

- **GitHub repository:** https://github.com/containers/crun
- **Issues:** https://github.com/containers/crun/issues
- **Documentation:** crun.1.md in repository
- **OCI Runtime Spec:** https://github.com/opencontainers/runtime-spec

## Best Practices

1. **Always use debug mode** when troubleshooting new issues
2. **Check logs systematically** - start with crun logs, then system logs
3. **Test minimal configurations** before adding complexity
4. **Verify prerequisites** - rootfs, config.json, permissions
5. **Use version control** for config files to track changes
6. **Document custom configurations** for team knowledge
7. **Keep crun updated** for bug fixes and improvements
8. **Test checkpoint/restore** in non-production first
