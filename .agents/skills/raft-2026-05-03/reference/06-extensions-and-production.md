# Raft Extensions and Production Use

## Contents
- Pre-Vote Extension
- Leadership Transfer Extension
- Production Systems Using Raft
- Comparison With Other Algorithms
- Formal Verification

## Pre-Vote Extension

When a member rejoins the cluster after being partitioned, it may have an outdated term number. Upon timing out, it would increment its term and start an election, which could disrupt the current leader even though the rejoining server's log is stale.

### How Pre-Vote works

Before starting a real election, a candidate sends **pre-vote requests** that:
- Do not increment the candidate's term
- Do not reset the candidate's `votedFor`
- Are answered only if the voter would actually grant a vote (i.e., its log is at least as up-to-date)

If the pre-vote fails to get majority support, the candidate doesn't start a real election. This prevents unnecessary disruptions when a recently-rejoined server with stale information times out.

### Why it matters

Pre-vote improves cluster availability by avoiding unnecessary elections. It is usually present in production implementations.

## Leadership Transfer Extension

A leader that is shutting down orderly can explicitly transfer leadership to another member, which is faster than waiting for an election timeout.

### How it works

1. Leader selects a target follower (preferably one with the most up-to-date log)
2. Leader replicates any outstanding entries to the target
3. Leader steps down voluntarily
4. Target's election timeout expires and it becomes leader

A leader can also step down when another member would be a better leader (e.g., on faster hardware or in a lower-latency network segment).

## Production Systems Using Raft

Raft is widely deployed in production systems:

| System | Use Case |
|--------|----------|
| **etcd** | Highly-available key-value store for Kubernetes, service discovery |
| **CockroachDB** | Replication layer for distributed SQL database |
| **TiKV / TiDB** | Storage engine with Raft-based replication |
| **Kafka (KRaft)** | Metadata management, replacing ZooKeeper |
| **ScyllaDB** | Metadata (schema and topology changes) |
| **RabbitMQ** | Quorum queues (durable, replicated FIFO queues) |
| **Neo4j** | Clustering consistency and safety |
| **MongoDB** | Replica set replication (variant of Raft) |
| **NATS JetStream** | Cluster management and data replication |
| **Redpanda** | Data replication for Kafka-compatible streaming |
| **ClickHouse Keeper** | ZooKeeper-like coordination service |
| **IBM MQ** | Highly-available replicated log |
| **Splunk** | Search Head Cluster coordination |
| **Hazelcast** | CP Subsystem (strongly consistent distributed data structures) |
| **YugabyteDB** | DocDB replication layer |
| **Camunda / Zeebe** | Data replication for workflow engine |

## Comparison With Other Algorithms

### Raft vs Paxos

| Aspect | Raft | Paxos |
|--------|------|-------|
| Leadership | Strong leader — essential to protocol | Leader election orthogonal to basic consensus |
| Decomposition | Leader election + log replication + safety | Single-decree + multi-Paxos composition |
| Message types | 4 (2 RPC requests + 2 responses) | More complex, varies by variant |
| Log direction | One-way: leader → followers | Bidirectional in some variants |
| Understandability | User study: significantly easier than Paxos | Notoriously difficult to understand |
| Practical foundation | Designed for implementation | Gaps between theory and practice |

### Raft vs Viewstamped Replication (VR)

- Both are leader-based with similar advantages over Paxos
- Raft has less mechanism: minimizes functionality in non-leaders
- VR log entries flow bidirectionally; Raft is one-way (leader → followers)
- VR stops all normal processing during configuration changes; Raft continues serving requests
- Raft adds less mechanism for membership changes than VR or SMART

### Raft vs EPaxos

- EPaxos achieves higher performance under some conditions with a leaderless approach
- EPaxos exploits commutativity: any server can commit if concurrent commands commute
- Raft's strong leadership precludes these optimizations but keeps the algorithm simpler

## Formal Verification

Raft has been formally specified and verified:

- **TLA+ specification**: ~400 lines, makes Figure 2 completely precise. Available at https://github.com/ongardie/raft.tla
- **Mechanically proven**: Log Completeness Property using TLA proof system
- **Informal proof**: State Machine Safety property (~3500 words), complete and relatively precise
- **Dissertation**: Diego Ongaro's Ph.D. dissertation "Consensus: Bridging Theory and Practice" expands on the paper in much more detail, including a simpler cluster membership change algorithm

### Implementation

The reference Raft implementation (LogCabin) contains ~2000 lines of C++ code, excluding tests, comments, and blank lines. Source: https://github.com/logcabin/logcabin
