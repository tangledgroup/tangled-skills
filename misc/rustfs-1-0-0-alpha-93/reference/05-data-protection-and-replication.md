# Data Protection and Replication

## Erasure Coding in Detail

RustFS uses Reed-Solomon erasure coding as its primary data protection mechanism.

### Encoding Strategy

Objects are split into dynamic shard sizes (64 KB–4 MB). Each shard includes a Blake3 hash checksum for integrity verification. Parallel encoding leverages Rayon with AVX2 SIMD-accelerated finite field operations over GF(2^8).

### Recovery Process

1. Client sends data read request
2. Coordinator queries shard status across nodes
3. If sufficient shards available (≥ k): decode and return data
4. If insufficient: trigger repair process, collect surviving shards, reconstruct missing shards, write back to nodes

Default RS(12,4) configuration:
- 12 data shards + 4 parity shards = 16 total
- Tolerates up to 4 simultaneous disk failures
- Storage utilization: ~75% (vs 33% for triple replication)
- Recovery time inversely proportional to network bandwidth

## Self-Healing

RustFS provides three levels of self-healing triggered at different times:

### Read-Time Self-Healing

Every `GET` or `HEAD` request triggers shard integrity verification:
1. Check all data shards of the requested object
2. If all intact: return data directly
3. If corruption detected: reconstruct from redundant shards, repair, then return complete object
4. Transparent to client — no request disruption

### Background Scanning

Built-in object scanner traverses 1/1024 of storage pool objects per cycle using hash-based sampling:
- **Light scrub**: Compares metadata and shard sizes, marks corruption
- **Deep scrub** (optional): Reads shard data bit-by-bit, verifies checksums, detects bit rot
- Deep verification disabled by default to reduce resource overhead

### Manual Self-Healing

Administrators can trigger full self-healing via CLI:

```bash
# Start full heal
rc admin heal start --all

# Check status
rc admin heal status

# Heal specific bucket
rc admin heal start --bucket photos

# Stop healing
rc admin heal stop
```

Use during low-peak periods — consumes significant resources.

## Cross-Region Replication

RustFS supports active-active replication at the bucket level with near-synchronous operation:

### Features

- **Encrypted/unencrypted objects**: Replicates data and metadata
- **Object versions**: Preserves version history
- **Object tags**: Replicates tags
- **S3 Object Lock**: Maintains retention information
- **Identical bucket naming**: Enables transparent failover
- **Notifications**: Pushes replication failure events to operations teams

### Infrastructure Requirements

- Same hardware at both endpoints recommended
- Bandwidth critical — changes queue if bandwidth insufficient
- Latency target: RTT ≤ 20ms for Ethernet links
- Packet loss rate: ≤ 0.01%
- Currently recommended for two data centers only

### Failover Behavior

If replication target fails, source caches changes and synchronizes after recovery. Full sync delay depends on duration of outage, number of changes, bandwidth, and latency.

### Versioning Requirements

- In active-active mode, immutability requires versioning
- Versioning cannot be disabled on source
- If versioning suspended on target, replication fails
- Object locking must be enabled on both source and target

## Lifecycle Management

Automate data management based on age and access patterns:

### Object Expiration

Define retention periods as specific dates or number of days. Rules apply per bucket with optional object/tag filters. Applies to versioned buckets — can target non-current versions specifically to minimize costs.

Complies with WORM locking — objects under lock remain until lock expires or is explicitly released. Compatible with AWS Lifecycle Management JSON format for rule import.

### Policy-Based Tiering

Objects transition between storage classes based on time and access frequency:
- **Cross-media tiering**: NVMe/SSD for hot data, HDD for warm/cold
- **Hybrid cloud tiering**: Private cloud for performance, public cloud cold storage for cost optimization
- Applications address objects through RustFS while policies transparently move data between tiers

## Audit Logging

Every cluster operation generates an audit log containing:
- Unique operation ID
- Client information
- Object and bucket details
- Metadata

Logs written to configured HTTP/HTTPS webhook endpoints. Configurable via Console UI or `mc` CLI.

Lambda notifications push bucket/object events to:
- RabbitMQ
- Kafka
- Elasticsearch

Real-time HTTP/S tracing available through Console and `mc admin trace`.

## Bitrot Protection

Inline bitrot detection ensures no corrupted data is ever read. When corruption is detected during reads or background scans, automatic repair reconstructs data from surviving shards. This provides continuous data integrity verification without manual intervention.
