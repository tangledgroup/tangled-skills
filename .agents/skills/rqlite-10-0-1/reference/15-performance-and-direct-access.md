# Performance & Direct Access

## Performance Factors

rqlite performance (database updates per time period) is primarily determined by two factors:

### Disk Performance

Disk I/O is the single biggest determinant of rqlite performance on a low-latency network. Every change goes through the Raft subsystem, which calls `fsync()` after every write to its log before applying changes to SQLite.

### Network Latency

In a cluster, network latency becomes the bottleneck once it gets high enough. Raft must contact every other node **twice** (in parallel) before a change is committed to the Raft log.

### Snapshotting

Raft log entries grow over time. Periodic _Snapshots_ capture the SQLite database state and allow older entries to be discarded. **Writes are blocked during snapshot creation.** Frequent snapshots reduce start-up time but increase CPU/I/O load. Infrequent snapshots use fewer resources but result in larger logs and slower follower catch-up.

Tune via `-raft-snap`, `-raft-snap-wal-size`, and `-raft-snap-int`.

## Improving Performance

### VACUUM

Defragment the database to improve query performance:

```bash
curl -XPOST 'localhost:4001/db/execute' -H 'Content-Type: application/json' -d '["VACUUM"]'
```

Schedule automatic VACUUMs:

```bash
rqlited -auto-vacuum-int=24h ~/node
```

> VACUUM may temporarily double disk usage. Ensure sufficient free space. Writes are **blocked** during VACUUM.

### PRAGMA optimize

Instruct SQLite to analyze tables and gather statistics:

```bash
curl -XPOST 'localhost:4001/db/execute' -H 'Content-Type: application/json' -d '["PRAGMA optimize"]'
```

rqlite automatically runs `PRAGMA optimize` once daily. Change the interval or disable:

```bash
rqlited -auto-optimize-int=6h ~/node   # Every six hours
rqlited -auto-optimize-int=0h ~/node   # Disabled
```

### Batching

The more SQLite statements in a single write request, the greater the throughput — often by 2 orders of magnitude. Use [bulk API](reference/02-http-api-and-developer-guide.md#bulk-writes), [transactions](reference/02-http-api-and-developer-guide.md#transactions), or both.

### Queued Writes

[Queued Writes](reference/02-http-api-and-developer-guide.md#queued-writes) can provide orders of magnitude improvement in write performance without changing client code, at the cost of a small risk of data loss.

### Better Hardware

Higher-performance disks and lower-latency networks improve performance generally (vertical scaling).

### Memory-Backed Filesystem

Running rqlite on a memory-backed filesystem can result in ~100x improvement:

```bash
mount -t tmpfs -o size=512m tmpfs /mnt/ramdisk
rqlited -node-id=1 /mnt/ramdisk/data
```

> **Risk:** If the entire cluster loses power, all data is lost. Only suitable if you always rebuild from an external data source or backup.

## Memory Usage

Go's garbage collector usually manages memory effectively. However, large repeated requests may cause significant memory spikes. To address this:

- Reduce [`GOGC`](https://tip.golang.org/doc/gc-guide#GOGC) (default 100). Setting to 50 doubles GC frequency but increases CPU load.
- Adjust `GOMEMLIMIT` as needed.

See the [Go GC Guide](https://tip.golang.org/doc/gc-guide) for details.

## Direct SQLite Access

rqlite manages the SQLite database under the hood. Most applications should interact exclusively through the [HTTP API](reference/02-http-api-and-developer-guide.md).

### Can I Modify the SQLite Database Directly?

**No.** Never modify the SQLite database directly. All modifications must occur through the rqlite HTTP API. Altering the SQLite file, changing its journaling mode, or checkpointing the WAL will cause undefined behavior and likely data loss.

### Can I Read the SQLite Database Directly?

Yes, but follow these guidelines strictly:

- **Read-only access:** Use OS-level mechanisms to enforce read-only permissions on the directory containing SQLite files (the main database, `-wal`, and `-shm` files)
- **Open in read-only mode:** Via the [SQLite C API](https://www.sqlite.org/c3ref/open.html) or by setting `mode=ro` in a [filename URI](https://www.sqlite.org/uri.html)
- **Do not open in EXCLUSIVE locking mode:** This may block rqlite's access to the database

> Even a read-only SQLite client may checkpoint the WAL when closing its connection, which breaks rqlite. Direct reads are a known use case but have not been extensively tested.

### Impact of Long-Running Reads

rqlite periodically snapshots the SQLite database, requiring exclusive access. A long-running read transaction holding a database lock could interfere with snapshotting. If snapshotting is persistently blocked, it may lead to excessive disk usage or degraded query performance. Monitor logs to detect this issue.

> Snapshotting typically completes within milliseconds, making conflicts with long-running reads unlikely in practice.
