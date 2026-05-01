# Data Protection and Replication

## Erasure Coding Details

RustFS uses Reed-Solomon erasure coding for data protection. Each object is split into shards distributed across drives within an erasure set.

Default configuration: 12 data + 4 parity = 16 total shards. This tolerates up to 4 simultaneous drive failures per set while using only 33% overhead (vs 200% for triple replication).

Configurable via `--erasure-coding-drive-per-set` flag. Common configurations:
- **8 drives**: 4 data + 4 parity (tolerates 4 failures)
- **16 drives**: 10 data + 6 parity (tolerates 6 failures)
- **32 drives**: 24 data + 8 parity (tolerates 8 failures)

## Self-Healing

RustFS performs automatic data repair through three mechanisms:

1. **Read-time verification**: On every read, checksums verify shard integrity. Corrupted shards trigger immediate background repair.
2. **Background scanning**: Periodic full-cluster scans detect bit rot and silent corruption.
3. **Manual triggers**: Admin-initiated healing via console or `mc admin heal`.

Healing reconstructs missing or corrupted shards from available parity data without requiring all drives to be healthy simultaneously.

## Storage Resilience (beta.1)

The beta.1 release includes a storage fix that prevents local drives from being marked as faulty on transient timeouts. This reduces false-positive drive failures during network blips or temporary I/O stalls, improving overall cluster stability.

## Cross-Region Replication

Replicate buckets across geographically distributed clusters for disaster recovery:

```bash
mc replicate add myrustfs/bucket --region us-east-1 \
  myrustfs-dr/bucket --region eu-west-1
```

The beta.1 release includes replication fixes:
- Single-bucket replication rules now correctly fan out to all targets
- Target state is preserved across bucket operations, preventing loss of replication configuration
- These fixes ensure reliable multi-region replication without manual intervention

## Lifecycle Management

Automate object transitions and deletions with lifecycle rules:

```json
{
  "Rules": [
    {
      "ID": "archive-old-data",
      "Status": "Enabled",
      "Filter": {"Prefix": "logs/"},
      "Transition": {
        "Days": 30,
        "StorageClass": "GLACIER"
      }
    },
    {
      "ID": "delete-expired",
      "Status": "Enabled",
      "Filter": {"Prefix": "temp/"},
      "Expiration": {"Days": 7}
    }
  ]
}
```

The beta.1 release fixes a lifecycle issue where eager date-expiry deletion could trigger on config update, preventing premature object removal during rule changes.

## ILM Hardening (beta.1)

The beta.1 release hardens Information Lifecycle Management against signer failures and guards against remote tier delete storms, improving reliability when integrating with external archival tiers.
