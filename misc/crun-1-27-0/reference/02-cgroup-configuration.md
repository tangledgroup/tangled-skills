# Cgroup Configuration

## Overview

crun supports both cgroupfs and systemd backends for resource control. The backend is selected via `--cgroup-manager` (`cgroupfs`, `systemd`, or `disabled`) or `--systemd-cgroup`.

**cgroup v1 support is deprecated** and will be removed in a future release. On cgroup v2 systems, crun automatically converts cgroup v1 OCI configurations using well-defined formulas.

## Cgroup v2 Controllers

### Memory Controller

| OCI resource (v1) | cgroup v2 file | conversion | notes |
|---|---|---|---|
| `limit` | `memory.max` | direct | — |
| `swap` | `memory.swap.max` | `x - memory_limit` | v1 swap includes memory usage |
| `reservation` | `memory.low` | direct | — |

### PIDs Controller

| OCI resource (v1) | cgroup v2 file | conversion |
|---|---|---|
| `limit` | `pids.max` | direct |

### CPU Controller

| OCI resource (v1) | cgroup v2 file | conversion | notes |
|---|---|---|---|
| `shares` | `cpu.weight` | quadratic formula | maps [2–262144] → [1–10000] |
| `period` | `cpu.max` | direct | written with quota |
| `quota` | `cpu.max` | direct | written with period |

The shares-to-weight conversion uses a quadratic function so that minimum, maximum, and default values align between the two systems.

### blkio Controller

| OCI resource (v1) | cgroup v2 file | conversion | notes |
|---|---|---|---|
| `weight` | `io.bfq.weight` | direct | or fallback to `io.weight` |
| `weight_device` | `io.bfq.weight` | direct | or fallback to `io.weight` |
| `rbps` | `io.max` | direct | read bytes per second |
| `wbps` | `io.max` | direct | write bytes per second |
| `riops` | `io.max` | direct | read IOPS |
| `wiops` | `io.max` | direct | write IOPS |

When `io.bfq.weight` is unavailable, crun falls back to `io.weight` with linear conversion from [10–1000] → [1–10000].

### cpuset Controller

| OCI resource (v1) | cgroup v2 file | conversion |
|---|---|---|
| `cpus` | `cpuset.cpus` | direct |
| `mems` | `cpuset.mems` | direct |

### hugetlb Controller

| OCI resource (v1) | cgroup v2 file | conversion |
|---|---|---|
| `<PAGE_SIZE>.limit_in_bytes` | `hugetlb.<PAGE_SIZE>.max` | direct |

## Cgroup v2 Limitations

cgroup v2 does not yet support control of realtime processes. The CPU controller can only be enabled when all RT processes are in the root cgroup, which will cause crun to fail when running alongside RT processes.

## systemd Integration

When using `--cgroup-manager=systemd`, crun creates a systemd scope for the container and configures resource limits through the D-Bus API. The `run.oci.systemd.subgroup` annotation controls whether a sub-cgroup is created under the scope (default: `container` on cgroup v2, empty string on cgroup v1).

## NUMA Support

crun supports `set_mempolicy` for NUMA-aware memory placement (added in 1.24).
