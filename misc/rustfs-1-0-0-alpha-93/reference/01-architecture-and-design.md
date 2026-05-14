# Architecture and Design

## Decentralized Peer-to-Peer Architecture

RustFS adopts a fully decentralized architecture where all nodes are equal. There are no name nodes, metadata servers, or master nodes. This eliminates single points of failure and greatly simplifies deployment — a single command starts the system.

Key design principles:
- **No metadata bottleneck**: Data and metadata are written atomically together
- **All inline operations**: Erasure coding, bitrot checking, and encryption are performed inline with strict consistency
- **Single process per node**: Runs as one user-space process using lightweight coroutines for high concurrency
- **Deterministic object placement**: Objects placed on erasure sets via deterministic hashing

This design draws inspiration from MinIO's elegant architecture while leveraging Rust's memory safety guarantees.

## Consistency Model

All read and write operations strictly follow the **read-after-write** consistency model in both distributed and single-machine modes. This ensures that once a write completes, subsequent reads always return the latest data.

## Key Architectural Components

**Object**: The fundamental storage unit — files, byte streams, or unstructured data. Maximum 5 TiB via multipart upload.

**Bucket**: Logical container for objects with data isolation between buckets. Functions like a top-level directory.

**Drive**: Physical disk storing data, passed as parameter at startup. All object data resides on drives.

**Set (Erasure Set / Stripe)**: Group of drives distributed across different nodes. Each object lives in one set. The cluster auto-partitions into sets based on scale.

Design considerations for sets:
- One object is stored on exactly one set
- One cluster divides into multiple sets
- Number of drives per set is fixed (auto-calculated by system)
- Drives in a set should be distributed across different nodes

## Erasure Coding Fundamentals

RustFS uses Reed-Solomon erasure coding for data protection:

- Data split into `k` data shards and `m` parity shards (total `n=k+m`)
- Default configuration: RS(12,4) — 12 data shards + 4 parity shards
- Tolerates up to 4 simultaneous disk failures
- Storage utilization: ~75% vs 33% for triple replication
- Recovery via Gaussian elimination or FFT algorithms
- Dynamic adjustment of `(k,m)` parameters at runtime

### Encoding Process

Objects are divided into dynamic shard sizes (64 KB–4 MB). Each shard gets a Blake3 hash checksum. Parallel encoding uses Rayon with AVX2 SIMD acceleration for finite field operations over GF(2^8).

Read quorum: `N/2` drives must respond
Write quorum: `(N/2) + 1` drives must acknowledge

## Performance Characteristics

RustFS delivers exceptional throughput:
- **NVMe SSD**: 325 GiB/s read, 171 GiB/s write
- **HDD**: 11 GiB/s read, 9 GiB/s write
- Binary size under 100 MB
- Efficient CPU and memory usage even under high load
- SIMD-optimized S3 Select queries on CSV, Parquet, JSON

## Cross-Platform Support

Runs on Linux, Unix, Windows, macOS, FreeBSD, Docker, and edge gateways. Supported CPU architectures: x86, ARM, RISC-V.

## Workspace Structure

The RustFS codebase is organized as a Cargo workspace with the following key crates:

- `rustfs` — Core file system implementation
- `ecstore` — Erasure coding storage
- `heal` — Object healing and repair
- `iam` — Identity and Access Management
- `keystone` — OpenStack Keystone integration
- `kms` — Key Management Service
- `crypto` — Cryptography and security
- `scanner` — Data integrity scanning
- `notify` — Event notification system
- `obs` — Observability utilities
- `s3-common` — S3 compatibility layer
- `protocols` — FTPS, SFTP protocol implementations
- `concurrency` — Timeout, locking, backpressure, I/O scheduling
- `io-metrics` / `io-core` — Zero-copy metrics and I/O
