# Design & FAQ

## High-Level Architecture

Each rqlite node consists of:

- **HTTP API layer** — receives client requests on the HTTP port (default 4001)
- **Store layer** — manages SQLite database operations and coordinates with Raft
- **SQLite engine** — embedded SQLite running in WAL mode
- **Raft layer** — consensus protocol implementation that creates and manages the Raft log
- **Network layer** — handles inter-node communication on the Raft port (default 4002)

## Raft Log

The Raft layer always creates a file — the _Raft log_. This log stores committed SQLite commands in execution order. It is the authoritative record of every change to the system. Every node applies the log entries in exactly the same way, guaranteeing identical SQLite databases across all nodes.

## Log Compaction and Truncation

rqlite automatically performs log compaction to bound disk usage. After a configurable number of changes, rqlite snapshots the SQLite database and truncates the Raft log. This is a technical feature of Raft that most users need not be concerned with.

## SQLite WAL Mode

SQLite runs in [WAL mode](https://www.sqlite.org/wal.html) with `SYNCHRONOUS=off` for maximum write performance. Periodically, rqlite switches to `SYNCHRONOUS=full` and fsyncs the entire database to disk. On restart, it begins from the last known fsync'd version or rebuilds from the Raft log if no valid copy exists.

## Autoclustering Design

- **Automatic Bootstrapping:** Each node notifies all others of its existence. The first node contacted by enough others (set by `-bootstrap-expect`) bootstraps the cluster. Only one node can bootstrap; others become Followers.
- **Consul/etcd:** Nodes use the key-value store to atomically set a special key with their network addresses. Only one succeeds and declares itself Leader; others join with it. Uses check-and-set to prevent concurrent updates.
- **DNS:** Nodes resolve a hostname. Once returned addresses meet `-bootstrap-expect`, bootstrapping proceeds as though addresses were passed via `-join`.

## FAQ

### What exactly does rqlite do?

rqlite replicates data written using SQL across multiple nodes for fault tolerance. Raft prevents divergent copies and ensures one authoritative, consistent copy at all times.

### When should I use rqlite?

For easy-to-use, fault-tolerant, highly-available relational databases. Well-suited for edge/IoT deployments, cloud services needing simple HA, and read-intensive globally distributed apps.

### Why rqlite vs other distributed databases?

**Simplicity.** Single binary, seconds to form a cluster, complete control over infrastructure and data. It may be _too_ simple for some needs.

### Is it a drop-in replacement for SQLite?

No. You must write via the HTTP API. But since it exposes SQLite, all of SQLite's power is available. Applications built on top of SQLite may need only small changes to work with rqlite.

### Can I send writes to any node?

Yes. If a Follower receives a write, it transparently forwards to the Leader and returns the response. You do not need to direct writes specifically to the Leader.

### Does rqlite increase SQLite performance?

Only for reads (with `none` consistency level). It does not scale writes — all writes go through the Leader. rqlite is distributed for **high-availability and fault tolerance, not performance**. Write performance is reduced relative to standalone SQLite due to Raft round-trips.

### Where does rqlite fit into the CAP theorem?

Raft is a **Consistency-Partition (CP)** protocol. If partitioned, only the side with a majority of nodes remains available and returns consistent results. The other side stops responding to writes.

### Does rqlite require consensus before accepting a write?

Yes, intrinsically part of Raft. Two round-trips from Leader to quorum (contacted in parallel). Exception: [Queued Writes](reference/02-http-api-and-developer-guide.md#queued-writes) trade durability for performance.

### Can I run a single node?

Yes. Many people do so for networked SQLite access via HTTP. No redundancy or fault tolerance, but fully functional.

### What is the maximum cluster size?

No explicit maximum, but practical limit is about 11 **voting nodes**. Go bigger by adding [read-only nodes](reference/07-read-only-nodes.md).

### Does rqlite support transactions?

It supports [a form of transactions](reference/02-http-api-and-developer-guide.md#transactions) via the `transaction` flag on bulk updates. Explicit `BEGIN`, `COMMIT`, and `ROLLBACK` are unsupported — behavior is undefined if the node fails during an explicit transaction.

### Can I modify or read the SQLite file directly?

- **Modify:** No. See [Direct Access guide](reference/15-performance-and-direct-access.md#can-i-modify-the-sqlite-database-directly).
- **Read:** Yes, with strict guidelines. See [Direct Access guide](reference/15-performance-and-direct-access.md#can-i-read-the-sqlite-database-directly).

### Do concurrent writes block each other?

Yes, same as SQLite. Each HTTP write uses the same SQLite connection on the Leader. Additionally, the Raft log serializes all writes.

### Do concurrent reads block each other?

No. Reads don't block other reads or writes (except with _Strong_ consistency). One exception: a read can indirectly block a write if it blocks snapshotting, but this is rare (snapshotting takes milliseconds).

### How is rqlite different than dqlite?

dqlite is a C library you integrate into your own software. rqlite is a standalone RDBMS with everything needed to read, write, backup, and monitor data. They are completely separate projects; rqlite predates dqlite.

### How is rqlite different than Litestream?

[Litestream](https://github.com/benbjohnson/litestream) periodically backs up SQLite to cloud storage for reliability. If you lose the node, you restore from backup. rqlite adds reliability **and** high-availability via clustering — applications don't notice if a node fails because other nodes automatically take over.

### How is rqlite different than LiteFS?

[LiteFS](https://github.com/superfly/litefs) is another SQLite replication system. rqlite is a highly-available distributed database solution, not a SQLite replication system.

### What dependencies are required?

On Linux, glibc >= 2.34 is required. SQLite is never required on the host (compiled into rqlite). No other external dependencies.
