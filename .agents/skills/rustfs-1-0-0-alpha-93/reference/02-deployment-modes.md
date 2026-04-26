# Deployment Modes

## Installation Modes Overview

RustFS supports three deployment modes:

1. **SNSD** (Single Node Single Disk) — One server, one disk. Suitable for testing and non-critical workloads.
2. **SNMD** (Single Node Multiple Disk) — One server, multiple disks. Better reliability through erasure coding across local disks.
3. **MNMD** (Multiple Node Multiple Disk) — Multiple servers, multiple disks per server. Enterprise-grade with full fault tolerance.

## Single Node Single Disk (SNSD)

One server with one data disk. All data falls into this single disk. No redundancy — suitable only for development and testing.

Quick start:
```bash
curl -O https://rustfs.com/install_rustfs.sh && bash install_rustfs.sh
```

Default port: `9000` (S3 API), `9001` (Console). Default data path: `/data/rustfs0`.

## Single Node Multiple Disk (SNMD)

One server with multiple disks. Erasure coding distributes data across disks for redundancy. Minimum 4 disks recommended for full erasure coding protection.

## Multiple Node Multiple Disk (MNMD)

Enterprise-grade deployment requiring a minimum of **4 servers**, each with at least 1 disk. Data is distributed across all drives on all nodes.

Default 12+4 configuration splits data into 12 data blocks + 4 parity blocks stored on different disks across different servers. Any single server failure does not affect data security. Up to 4 disk failures are tolerated simultaneously.

### MNMD Hostname Configuration

Sequential hostnames required for cluster nodes:

```bash
# /etc/hosts
192.168.1.1 node1
192.168.1.2 node2
192.168.1.3 node3
192.168.1.4 node4
```

## Prerequisites (All Modes)

### Operating System

Linux kernel 4.x or above recommended. Kernel 5.x/6.x provides better I/O throughput. Ubuntu 22.04 and RHEL 8.x supported.

### Firewall

Disable firewall or allow port 9000:
```bash
firewall-cmd --zone=public --add-port=9000/tcp --permanent
firewall-cmd --reload
```

All RustFS servers in the deployment **must** use the same listening port.

### Memory

- Test environments: minimum 2 GB
- Production environments: minimum 128 GB

### Time Synchronization

Required for multi-node deployments. Use `ntp`, `timedatectl`, or `timesyncd`:
```bash
timedatectl status
```

Status must show "synchronized".

### Disk Planning

**NFS is prohibited** as underlying storage due to phantom writes and lock issues under high I/O.

**JBOD (Just a Bunch of Disks) mode is required**: expose physical disks directly to the OS, let RustFS handle redundancy. Hardware RAID becomes a performance bottleneck.

Recommended storage media: NVMe SSD for highest performance.

### File System

**XFS is strongly recommended** on all storage disks. RustFS development and testing are based on XFS.

Formatting example:
```bash
sudo mkfs.xfs -i size=512 -n ftype=1 -L RUSTFS0 /dev/sdb
```

Mount in `/etc/fstab`:
```bash
LABEL=RUSTFS0 /data/rustfs0 xfs defaults,noatime,nodiratime 0 0
sudo mount -a
```

Key XFS options:
- `-i size=512`: Inode size of 512 bytes, optimal for many small objects
- `-n ftype=1`: Record file types in directory structure for faster readdir/unlink
- `noatime,nodiratime`: Disable access time updates for performance
- XFS `fallocate` API used by RustFS for space reservation before writes

### Capacity and EC Planning

Consider:
- Initial data volume (e.g., 500 TB)
- Data growth rate (daily/weekly/monthly)
- Planning horizon (recommended: 3 years)
- Hardware iteration cycles

EC parity recommendations:

- **Standard production**: EC:4 — tolerates up to 4 disk failures, good balance of reliability and efficiency
- **High availability**: EC:4–8 or higher — extreme data availability at cost of more storage
- **Development/test**: EC:2 — basic redundancy for non-critical workloads

## Hardware Configuration Matrix

| Component | Basic Environment | Production Standard | High-Performance |
|-----------|-------------------|--------------------|------------------|
| Node Count | 4 nodes | 8 nodes | 16+ nodes |
| Storage Media | 4× NVMe SSD | 8× NVMe SSD | 12× NVMe SSD |
| Network | Dual 25GbE | Dual 100GbE | 200GbE |
| CPU | 2× Intel Silver 4310 (16 cores) | 2× AMD EPYC 7313 (32 cores) | 2× Intel Platinum 8461Y (48 cores) |
| Memory | 64 GB DDR4 ECC | 256 GB DDR5 ECC | 512 GB DDR5 ECC |

### Network Bandwidth Reference

- Reserve 0.5 Gbps per TB of effective data
- Inter-node P99 latency ≤ 2ms
- Cross-rack latency ≤ 5ms

| Network Type | Throughput | Suitable Disks | Max Disks |
|-------------|-----------|----------------|-----------|
| 10GbE | 1.25 GB/s | 7.2K HDD | 8 disks |
| 25GbE | 3.125 GB/s | SATA SSD | 6 disks |
| 100GbE | 12.5 GB/s | NVMe Gen4 | 2 disks full-speed |

### Memory Calculator

Dynamic allocation based on data scale and access pattern:

- Read-intensive: `32 + (data_tb × 0.8)` GB
- Write-intensive: `32 + (data_tb × 1.2)` GB
- Mixed: `32 + (data_tb × 1.0)` GB

Memory allocation ratios:
- Metadata cache: 60%
- Read/write buffers: 30%
- System reserve: 10%

## Docker Compose with Observability

The `docker-compose.yml` includes profiles for observability services:

```bash
# Full stack with Grafana, Prometheus, Jaeger, Tempo, Loki
docker compose --profile observability up -d

# Development environment only
docker compose --profile dev up -d
```

Observability components:
- **Tempo**: Distributed tracing storage
- **OpenTelemetry Collector**: Metrics and trace aggregation
- **Jaeger**: Trace visualization (port 16686)
- **Prometheus**: Metrics collection (port 9090)
- **Loki**: Log aggregation

## Docker Container Notes

- Runs as non-root user `rustfs` (UID 10001)
- Host directories must be owned by UID 10001
- Ports: 9000 (S3 API), 9001 (Console)
- Health check endpoints: `/health` and `/rustfs/console/health`

## High Availability Measures

- **Power supply**: Dual power supply architecture, each PDU on different substations
- **UPS**: Minimum 30 minutes runtime
- **Cooling**: Cabinet density ≤ 15kW, inlet/outlet temp difference ≤ 8°C
- **Firmware**: Unified versions across all nodes
