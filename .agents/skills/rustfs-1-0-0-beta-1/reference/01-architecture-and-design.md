# Architecture and Design

## Decentralized Peer-to-Peer Design

RustFS uses a decentralized architecture with no central metadata server. Every node in the cluster participates equally. This eliminates single points of failure and enables horizontal scaling without reconfiguration.

Key design principles:
- **No metadata server**: All metadata is distributed across data drives
- **Equal peers**: Every node has identical capabilities and responsibilities
- **Automatic healing**: Self-healing runs on every node independently
- **Linear scale-out**: Add nodes and drives to grow capacity

## Consistency Model

RustFS provides strong consistency for all operations. Reads always return the latest written value. This is achieved through quorum-based writes: a write succeeds only when acknowledged by a majority of shards in the erasure set.

For an erasure code configuration of 12 data + 4 parity (16 total), the write quorum is 9 (majority of 16). Reads can succeed with fewer shards, and missing shards are reconstructed on-the-fly.

## Erasure Coding

Reed-Solomon erasure coding splits each object into `n` shards across drives in a set. The default configuration is 12+4:

- **12 data shards**: Store actual object content
- **4 parity shards**: Allow reconstruction after drive failures
- **Tolerates up to 4 simultaneous drive failures** per erasure set

This provides better storage efficiency than triple replication (50% overhead vs 200%). Configurable via `--erasure-coding-drive-per-set` or environment variables.

## Set Architecture

The cluster divides drives into sets. Each object belongs to exactly one set, determined by a hash of the bucket and object name. Sets are the unit of data distribution:

- One cluster = multiple sets
- One set = group of drives across nodes
- One object = stored within one set only
- Set count scales with total drive count

For optimal performance, distribute sets evenly across network segments to avoid cross-rack traffic for single-object operations.

## Memory Management (beta.1)

The beta.1 release adds memory reclaim signals and cache controls, allowing the system to respond to memory pressure more gracefully. These controls improve stability under high-concurrency workloads and reduce OOM risk in resource-constrained deployments.
