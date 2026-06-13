# Raft Log Compaction

## Contents
- Snapshotting Approach
- InstallSnapshot RPC
- Snapshot Metadata
- Performance Considerations

## Snapshotting Approach

Raft's log grows during normal operation. Without compaction, it would exhaust storage and slow restarts. **Snapshotting** is the simplest approach: the entire current system state is written to stable storage, then all log entries up to that point are discarded.

### How snapshotting works

Each server takes snapshots independently, covering just the committed entries in its log:

1. State machine writes its current state to the snapshot
2. Raft includes metadata: `lastIncludedIndex` (index of last entry replaced) and `lastIncludedTerm` (term of that entry)
3. Snapshot also includes the latest cluster configuration as of `lastIncludedIndex`
4. Once complete, server may delete all log entries up through `lastIncludedIndex` and any prior snapshot

The `lastIncludedIndex` and `lastIncludedTerm` support the AppendEntries consistency check for the first log entry following the snapshot — that entry needs a previous log index and term to verify against.

### Why followers snapshot independently

Raft departs from its strong leader principle here: followers can take snapshots without the leader's knowledge. This is justified because:
- Consensus has already been reached when snapshotting, so no decisions conflict
- Data still only flows leader → follower; followers just reorganize their data
- Sending snapshots from leader to each follower would waste bandwidth and slow the process
- Each server already has the information needed locally

Alternative approaches (leader creates snapshot, sends to all followers) were rejected for higher complexity and network cost.

## InstallSnapshot RPC

When a follower lags too far behind and the leader has already discarded the entries it needs to send, the leader uses `InstallSnapshot` to transfer a snapshot over the network.

### Arguments

| Field | Description |
|-------|-------------|
| `term` | Leader's current term |
| `leaderId` | So follower can redirect clients |
| `lastIncludedIndex` | Snapshot replaces all entries up through and including this index |
| `lastIncludedTerm` | Term of `lastIncludedIndex` |
| `offset` | Byte offset where chunk is positioned in the snapshot file |
| `data[]` | Raw bytes of the snapshot chunk, starting at `offset` |
| `done` | True if this is the last chunk |

### Results

- `term` — currentTerm, for leader to update itself

### Receiver implementation (follower)

1. Reply immediately if `term < currentTerm`
2. Create new snapshot file if first chunk (`offset` is 0)
3. Write `data` into snapshot file at given `offset`
4. Reply and wait for more data chunks if `done` is false
5. Save snapshot file, discard any existing or partial snapshot with smaller index
6. If existing log entry has same index and term as snapshot's last included entry: retain log entries following it and reply
7. Otherwise: discard the entire log
8. Reset state machine using snapshot contents (and load snapshot's cluster configuration)

Snapshots are split into chunks for transmission, giving the follower a sign of life with each chunk so it can reset its election timer.

## Snapshot Metadata

Each snapshot stores:

- **State machine state**: The complete current state (e.g., variable values, data structures)
- **`lastIncludedIndex`**: Index of the last log entry the snapshot replaces
- **`lastIncludedTerm`**: Term of `lastIncludedIndex`
- **Cluster configuration**: Latest configuration in the log as of `lastIncludedIndex`

These fields position the snapshot in the log and support consistency checks for entries that follow it.

## Performance Considerations

### When to snapshot

- Too often: wastes disk bandwidth and energy
- Too infrequently: risks exhausting storage, increases restart time from log replay
- **Simple strategy**: snapshot when the log reaches a fixed size in bytes
- Set this size significantly larger than expected snapshot size to minimize overhead

### How to snapshot without blocking

Writing a snapshot can take significant time. Raft uses **copy-on-write** techniques so new updates don't impact the snapshot being written:

- State machines built with functional data structures naturally support copy-on-write
- Alternatively, use OS-level copy-on-write (e.g., `fork` on Linux) to create an in-memory snapshot of the entire state machine
- The reference Raft implementation uses the `fork` approach

### Incremental alternatives

Log cleaning and LSM trees operate on fractions of data at once, spreading compaction load more evenly. They require additional mechanism compared to snapshotting but can be implemented by state machines using the same interface as snapshotting.
