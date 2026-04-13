# Resource Management in crun

Comprehensive guide to container resource limits, cgroup controllers, and cgroup v1/v2 conversion.

## Cgroup Managers

crun supports multiple cgroup management backends:

```bash
# Use systemd for cgroup management (recommended on systemd systems)
crun --systemd-cgroup run container-id

# Explicitly specify cgroup manager
crun --cgroup-manager systemd run container-id

# Use cgroupfs directly
crun --cgroup-manager cgroupfs run container-id

# Disable cgroups entirely (not recommended for production)
crun --cgroup-manager disabled run container-id
```

## Runtime Resource Updates

Update resource limits on running containers without restart:

```bash
# Memory limit
crun update --memory 512m container-id

# Memory reservation (soft limit)
crun update --memory-reservation 256m container-id

# Total memory + swap
crun update --memory-swap 1g container-id

# CPU shares (relative weight)
crun update --cpu-share 512 container-id

# CPU CFS period and quota
crun update --cpu-period 100000 --cpu-quota 80000 container-id

# CPU realtime period and runtime
crun update --cpu-rt-period 1000000 --cpu-rt-runtime 950000 container-id

# CPU set (which CPUs container can use)
crun update --cpuset-cpus "0-3" container-id

# Memory nodes
crun update --cpuset-mems "0" container-id

# PID limit
crun update --pids-limit 100 container-id

# Block I/O weight
crun update --blkio-weight 500 container-id

# Update from resources JSON file
crun update --resources /path/to/resources.json container-id
```

## Resources JSON File Format

```json
{
  "devices": [],
  "memory": {
    "limit": 536870912,
    "reservation": 268435456,
    "swap": 1073741824,
    "kernel": null,
    "kernelTcp": null
  },
  "cpu": {
    "shares": 512,
    "quota": 80000,
    "period": 100000,
    "rtRuntime": 950000,
    "rtPeriod": 1000000,
    "cpus": "0-3",
    "mems": "0"
  },
  "pids": {
    "limit": 100
  },
  "blkio": {
    "weight": 500
  }
}
```

## Cgroup v2 Support

crun natively supports cgroup v2 with automatic conversion from cgroup v1 configuration.

### Memory Controller Conversion

| OCI Field | cgroup v2 File | Conversion | Notes |
|-----------|---------------|------------|-------|
| `memory.limit` | `memory.max` | Direct | Same value |
| `memory.swap` | `memory.swap.max` | `swap - memory_limit` | cgroup v1 swap includes memory |
| `memory.reservation` | `memory.low` | Direct | Soft limit |

**Example:**
```json
{
  "linux": {
    "resources": {
      "memory": {
        "limit": 536870912,
        "swap": 1073741824,
        "reservation": 268435456
      }
    }
  }
}
```

Becomes in cgroup v2:
```
echo 536870912 > memory.max
echo 536870912 > memory.swap.max  # 1073741824 - 536870912
echo 268435456 > memory.low
```

### PIDs Controller Conversion

| OCI Field | cgroup v2 File | Conversion |
|-----------|---------------|------------|
| `pids.limit` | `pids.max` | Direct |

### CPU Controller Conversion

| OCI Field | cgroup v2 File | Conversion | Notes |
|-----------|---------------|------------|-------|
| `cpu.shares` | `cpu.weight` | Complex formula | Converts [2-262144] to [1-10000] |
| `cpu.period` | `cpu.max` | Direct | Written with quota |
| `cpu.quota` | `cpu.max` | Direct | Written as `quota period` |

**CPU shares conversion formula:**
```
cpu.weight = 10^((log2(shares)^2 + 125 * log2(shares)) / 612.0 - 7.0 / 34.0)
```

**Example:**
```json
{
  "linux": {
    "resources": {
      "cpu": {
        "shares": 1024,
        "period": 100000,
        "quota": 80000
      }
    }
  }
}
```

Becomes in cgroup v2:
```
echo "80000 100000" > cpu.max
echo 75 > cpu.weight  # Calculated from shares=1024
```

### Block I/O Controller Conversion

| OCI Field | cgroup v2 File | Conversion | Notes |
|-----------|---------------|------------|-------|
| `blkio.weight` | `io.bfq.weight` | Direct | Primary |
| `blkio.weight` | `io.weight` | Linear fallback | If bfq not available |
| `blkio.weight_device` | `io.bfq.weight` | Direct | Per-device |
| `blkio.rbps` | `io.max` | Direct | Read bytes/sec |
| `blkio.wbps` | `io.max` | Direct | Write bytes/sec |
| `blkio.riops` | `io.max` | Direct | Read IOPS |
| `blkio.wiops` | `io.max` | Direct | Write IOPS |

**Weight conversion (fallback):**
```
io.weight = 1 + (blkio.weight - 10) * 9999 / 990
```

Converts linearly from [10-1000] to [1-10000].

**Example:**
```json
{
  "linux": {
    "resources": {
      "blkio": {
        "weight": 750,
        "throttleReadBpsDevice": [
          {"major": 8, "minor": 0, "rate": 10485760}
        ],
        "throttleWriteIOPSDevice": [
          {"major": 8, "minor": 0, "rate": 1000}
        ]
      }
    }
  }
}
```

### CPUSET Controller Conversion

| OCI Field | cgroup v2 File | Conversion |
|-----------|---------------|------------|
| `cpuset.cpus` | `cpuset.cpus` | Direct |
| `cpuset.mems` | `cpuset.mems` | Direct |

### HugeTLB Controller Conversion

| OCI Field | cgroup v2 File | Conversion |
|-----------|---------------|------------|
| `hugetlb.<SIZE>.limit_in_bytes` | `hugetlb.<SIZE>.max` | Direct |

**Example:**
```json
{
  "linux": {
    "resources": {
      "hugepageLimits": [
        {
          "pageSize": "2MB",
          "limit": 33554432
        }
      ]
    }
  }
}
```

Becomes: `echo 33554432 > hugetlb.2MB.max`

## Cgroup v1 (Deprecated)

**Warning:** cgroup v1 support is deprecated and will be removed in future releases.

### Known Limitations on cgroup v2

- Real-time process control not yet supported
- CPU controller requires all RT processes in root cgroup
- Will fail when running alongside real-time processes

## Systemd Cgroup Integration

When using `--cgroup-manager systemd`:

### Subgroup Naming

Override systemd sub-cgroup name:

```json
{
  "annotations": {
    "run.oci.systemd.subgroup": "custom-subgroup"
  }
}
```

Results in path: `/sys/fs/cgroup/$PATH/custom-subgroup`

Empty string disables sub-cgroup creation.

Defaults:
- cgroup v2: `container`
- cgroup v1: `` (empty)

### Cgroup Delegation

Create delegated sub-cgroup for container payload management (cgroup v2 only):

```json
{
  "annotations": {
    "run.oci.systemd.subgroup": "app",
    "run.oci.delegate-cgroup": "delegated"
  }
}
```

Creates hierarchy:
```
/sys/fs/cgroup/$PATH/app/delegated
```

- Runtime applies limits to `$PATH/app`
- Container payload manages `$PATH/app/delegated`
- Limits on parent still apply to delegated cgroup
- **Only supported on cgroup v2** (unsafe on v1)

### Force cgroup v1 Mount

Run cgroup v1 containers on cgroup v2 system:

```json
{
  "annotations": {
    "run.oci.systemd.force_cgroup_v1": "/sys/fs/cgroup/systemd"
  }
}
```

**Prerequisites:**
1. cgroup v1 mount must already exist on host
2. For rootless: user needs permissions to mountpoint

**Setup example (as root):**
```bash
mkdir /sys/fs/cgroup/systemd
mount cgroup -t cgroup /sys/fs/cgroup/systemd -o none,name=systemd,xattr
chown -R the_user.the_user /sys/fs/cgroup/systemd
```

## Device Cgroups

Restrict device access:

```json
{
  "linux": {
    "resources": {
      "devices": [
        {
          "allow": true,
          "type": "c",
          "major": -1,
          "minor": -1,
          "access": "rwm"
        },
        {
          "allow": false,
          "type": "b",
          "major": -1,
          "minor": -1,
          "access": "rwm"
        }
      ]
    }
  }
}
```

**Access modes:**
- `r`: read
- `w`: write
- `m`: mknod

## Per-Cgroup Weight Updates

Update block I/O weight for specific cgroup:

```bash
crun update --blkio-weight 300 container-id
```

## Monitoring Resource Usage

Check current resource limits and usage:

```bash
# View cgroup files directly
cat /sys/fs/cgroup/container/memory.max
cat /sys/fs/cgroup/container/cpu.max

# Use systemd for systemd-managed cgroups
systemctl show my-container.scope -p MemoryMax
systemctl show my-container.scope -p CPUQuota
```

## Best Practices

1. **Always set PID limits** to prevent fork bombs:
   ```json
   {"pids": {"limit": 100}}
   ```

2. **Use memory reservations** before hard limits for better performance:
   ```json
   {"memory": {"reservation": 268435456, "limit": 536870912}}
   ```

3. **Prefer systemd cgroup manager** on systemd-based systems for better integration

4. **Test cgroup v2 compatibility** before production deployment

5. **Monitor resource usage** and adjust limits accordingly

6. **Use CPU quotas** instead of shares for precise CPU control in multi-tenant environments

## Troubleshooting

**"cgroup kill: no cgroup controller" error:**
- Verify cgroup manager matches system configuration
- Check if systemd is running (for `--cgroup-manager systemd`)

**Resource limits not applied:**
- Check crun logs with `--debug` flag
- Verify kernel supports required controllers
- Ensure sufficient privileges (root or proper capabilities)

**cgroup v2 conversion issues:**
- Review conversion tables for expected behavior
- Some cgroup v1 features may not have v2 equivalents yet
- Consider using cgroup v2-native configuration
