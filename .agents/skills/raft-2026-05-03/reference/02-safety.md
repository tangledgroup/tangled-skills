# Raft Safety Properties

## Contents
- Safety Properties Overview
- Election Restriction
- Committing Entries From Previous Terms
- Safety Argument (Leader Completeness Proof)
- Follower and Candidate Crash Handling

## Safety Properties Overview

Raft guarantees these five safety properties at all times:

| Property | Description |
|----------|-------------|
| **Election Safety** | At most one leader can be elected in a given term. |
| **Leader Append-Only** | A leader never overwrites or deletes entries in its log; it only appends new entries. |
| **Log Matching** | If two logs contain an entry with the same index and term, then the logs are identical in all entries up through that index. |
| **Leader Completeness** | If a log entry is committed in a given term, that entry will be present in the logs of the leaders for all higher-numbered terms. |
| **State Machine Safety** | If a server has applied a log entry at a given index to its state machine, no other server will ever apply a different command for the same index. |

The first four are guaranteed by the core protocol mechanics. State Machine Safety requires an additional restriction on the election process.

## Election Restriction

A candidate cannot win an election unless its log contains all committed entries from previous terms. This prevents a new leader from overwriting previously committed entries.

### How it works

The RequestVote RPC includes the candidate's `lastLogIndex` and `lastLogTerm`. The voter denies its vote if its own log is more up-to-date than the candidate's.

### "Up-to-date" comparison

Raft determines which of two logs is more up-to-date by comparing the last entries:
1. If last entries have different terms, the log with the **later term** is more up-to-date
2. If last entries have the same term, the **longer** log is more up-to-date

Since a candidate must contact a majority to win, and every committed entry is present on at least one server in that majority, the up-to-date check ensures the winner contains all committed entries.

## Committing Entries From Previous Terms

A leader **cannot** determine that an entry from a previous term is committed simply by counting replicas. Only entries from the leader's **current term** are committed by counting replicas. Once a current-term entry is committed, all prior entries become committed indirectly via the Log Matching Property.

### Why the current-term-first rule?

Consider this scenario:
1. S1 (leader for term T) partially replicates entry at index 2 to a majority
2. S1 crashes; S5 is elected leader for term U > T with votes from a different majority
3. S5 accepts a **different** entry at index 2
4. S5 crashes; S1 restarts, is re-elected, and continues replication
5. Now the entry from term T exists on a majority, but it could still be overwritten

If S1 had replicated an entry from its current term T on a majority before crashing, S5 could never win an election (the voter that accepted S1's entry would deny S5's vote since S1's log is more up-to-date). Therefore, committing only current-term entries by counting replicas is safe.

### Leader behavior for commitment

The leader sets `commitIndex = N` when:
- N > commitIndex
- A majority of `matchIndex[i] >= N`
- `log[N].term == currentTerm`

This automatically commits all preceding entries (including those from previous terms) because of the Log Matching Property.

## Safety Argument (Leader Completeness Proof)

The Leader Completeness Property is proven by contradiction:

1. Assume leader T commits an entry from term T, but some future leader U does not store it
2. Consider the smallest term U > T whose leader doesn't contain the entry
3. The committed entry was absent from leader U's log at election time (leaders never delete entries)
4. Leader T replicated on a majority; leader U received votes from a majority → at least one server ("the voter") both accepted the entry and voted for leader U
5. The voter accepted the entry before voting for leader U (otherwise it would have rejected AppendEntries from leader T)
6. The voter still stored the entry when voting (leaders never remove entries, followers only remove on conflict with a leader that contained the entry)
7. Leader U's log was at least as up-to-date as the voter's (vote granted). Two cases:
   - **Same last log term**: leader U's log is at least as long → it contains the entry. Contradiction.
   - **Leader U has later last log term**: the earlier leader that created that entry contained the committed entry (by assumption). By Log Matching Property, leader U also contains it. Contradiction.
8. Therefore, all future leaders contain all entries committed in term T

### State Machine Safety follows

At the time a server applies an entry, its log is identical to the leader's up through that entry and the entry is committed. Leader Completeness guarantees all future leaders store that same entry, so servers applying the index in later terms apply the same value. Combined with in-order application, all servers apply exactly the same entries in the same order.

## Follower and Candidate Crash Handling

Follower and candidate crashes are simpler than leader crashes:

- Future RequestVote and AppendEntries RPCs to the crashed server fail
- Raft handles this by retrying indefinitely
- If the server restarts, the RPC completes successfully
- If the server crashed after completing an RPC but before responding, it receives the same RPC again — this causes no harm because **Raft RPCs are idempotent** (e.g., a follower receiving AppendEntries with already-present entries simply ignores them)
