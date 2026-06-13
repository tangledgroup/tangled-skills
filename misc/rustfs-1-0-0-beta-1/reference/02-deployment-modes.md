# Deployment Modes

## Single Node Single Drive (SNSD)

Simplest deployment for testing and development. One node, one drive.

```bash
rustfs server /data
```

No erasure coding in single-drive mode. Use only for non-production workloads.

## Single Node Multiple Drives (SNMD)

One node with multiple drives for erasure coding and local redundancy.

```bash
rustfs server /data/{drive1..drive8}
```

With 8 drives, defaults to 4+4 erasure coding (tolerates 4 drive failures). Suitable for edge deployments where a single machine handles storage.

## Multiple Node Multiple Drives (MNMD)

Full distributed deployment across multiple nodes. Each node contributes one or more drives.

```bash
# On each node, run:
rustfs server http://node{1..4}/data/{drive1..drive2}
```

This creates a 4-node cluster with erasure coding spanning all nodes. Recommended for production deployments requiring high availability and horizontal scaling.

## Hardware Requirements

### Minimum (Testing)
- CPU: 2 cores
- RAM: 4 GB
- Storage: 1 drive, any size
- Network: 1 Gbps

### Recommended (Production)
- CPU: 8+ cores (Intel Xeon or AMD EPYC)
- RAM: 16+ GB per node
- Storage: NVMe or SATA SSDs, JBOD mode (no hardware RAID)
- Network: 10-25 Gbps dedicated storage network

### Filesystem Requirements
- **Linux**: ext4, xfs recommended
- **macOS**: APFS
- **Windows**: NTFS
- Avoid filesystem-level encryption on data drives

## Windows Compatibility (beta.1)

The beta.1 release adds Windows path compatibility fixes, improving support for deployments on Windows servers and development environments. Path parsing now correctly handles Windows-style paths with backslashes and drive letters.

## macOS Cross-Compilation Note

macOS defaults to `ulimit -n` of 256, which can cause `ProcessFdQuotaExceeded` during cross-compilation. Raise the limit before building:

```bash
ulimit -n 4096
cargo zigbuild --target x86_64-unknown-linux-gnu
```

## Helm Chart Deployment (beta.1)

The beta.1 release fixes a Helm chart issue where `rollingUpdate` was rendered regardless of strategy type. Now it only renders when the strategy type is explicitly `RollingUpdate`, preventing invalid Kubernetes manifests.
