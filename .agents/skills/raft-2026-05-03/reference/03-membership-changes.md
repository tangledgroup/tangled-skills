# Raft Cluster Membership Changes

## Contents
- Joint Consensus Approach
- Configuration Change Timeline
- Edge Cases
- Non-Voting Members

## Joint Consensus Approach

Directly switching from one configuration to another is unsafe: different servers switch at different times, potentially creating two independent majorities that can each elect a leader for the same term. Raft uses a **two-phase approach** with a transitional **joint consensus** configuration.

### Joint consensus rules

Given `C_old` (old configuration) and `C_new` (new configuration), the joint consensus `C_old,new`:

- Log entries are replicated to all servers in both `C_old` and `C_new`
- Any server from either configuration may serve as leader
- Agreement (for elections and entry commitment) requires **separate majorities** from both `C_old` and `C_new`

This means no point in time exists where both configurations can make unilateral decisions, guaranteeing safety.

## Configuration Change Timeline

Configuration changes are stored as special log entries and communicated through the replicated log:

1. **Leader receives request** to change configuration from `C_old` to `C_new`
2. **Create joint consensus entry**: leader stores `C_old,new` as a log entry and replicates it
3. **Servers adopt new config on receipt**: each server uses the latest configuration in its log (regardless of commit status)
4. **Commit joint consensus**: replicated using `C_old,new` rules (majority of both `C_old` and `C_new`)
   - If leader crashes before commit, new leader may be chosen under either `C_old` or `C_old,new`
   - Once committed, neither `C_old` nor `C_new` can make decisions without the other's approval
5. **Create final config entry**: leader creates log entry describing `C_new` and replicates it
6. **Commit final config**: replicated under rules of `C_new` (majority of `C_new` only)
7. **Old servers shut down**: servers not in `C_new` are irrelevant and can be removed

If the leader crashes during this process, a new leader may be chosen under whichever configuration the winning candidate has received. The joint consensus ensures safety throughout.

## Edge Cases

### New servers with no log entries

New servers added to the cluster initially store no log entries. If immediately included in majorities, it could take too long for them to catch up, blocking commitment of new entries.

**Solution**: Before the configuration change, new servers join as **non-voting members**. The leader replicates log entries to them, but they are not considered for majorities. Once caught up, the reconfiguration proceeds normally.

### Leader not in C_new

The cluster leader may not be part of the new configuration (e.g., it's being removed).

**Solution**: The leader steps down (returns to follower state) once it has committed the `C_new` log entry. Until then, it manages a cluster that doesn't include itself — it replicates entries but doesn't count itself in majorities. The transition occurs when `C_new` is committed because that's the first point where `C_new` can operate independently (a leader can always be chosen from `C_new`).

### Removed server disruptions

Servers not in `C_new` won't receive heartbeats, so they time out and start new elections. Their RequestVote RPCs with new term numbers cause the current leader to revert to follower, triggering repeated election cycles.

**Solution**: Servers disregard RequestVote RPCs when they believe a current leader exists. Specifically, if a server receives a RequestVote RPC within the **minimum election timeout** of hearing from a current leader, it does not update its term or grant its vote. This doesn't affect normal elections (each server waits at least the minimum timeout before starting one), but prevents removed servers from disrupting the cluster.

## Non-Voting Members

Non-voting members are servers that receive log replication but don't participate in majorities for elections or commitment. They exist in a phase before joining the voting cluster:

1. Server is added as non-voting member
2. Leader replicates entries to it (via AppendEntries)
3. Once caught up with the rest of the cluster, configuration change proceeds to include it as a voting member

This avoids availability gaps during server onboarding.
