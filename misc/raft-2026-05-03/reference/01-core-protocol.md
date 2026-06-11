# Raft Core Protocol

## Contents
- Server States and Transitions
- Persistent and Volatile State
- RequestVote RPC
- AppendEntries RPC
- Leader Election
- Log Replication

## Server States and Transitions

Each server is always in one of three states:

| State | Behavior |
|-------|----------|
| **Follower** | Passive. Responds to RPCs from leaders and candidates. Converts to candidate if election timeout elapses without hearing from leader. |
| **Candidate** | Transitional. Initiates election by incrementing term, voting for self, sending RequestVote RPCs. Becomes leader on majority votes, reverts to follower on discovering higher-term leader, starts new election on timeout. |
| **Leader** | Handles all client requests. Sends heartbeats (empty AppendEntries) periodically. Replicates log entries via AppendEntries RPCs. Steps down if it discovers a higher term. |

Transitions:
- Follower → Candidate: election timeout elapses
- Candidate → Leader: receives votes from majority
- Candidate → Follower: receives AppendEntries from higher-term leader
- Leader → Follower: discovers higher term in RPC response

## Persistent and Volatile State

### Persistent state (on all servers, updated on stable storage before responding to RPCs)

| Field | Description |
|-------|-------------|
| `currentTerm` | Latest term server has seen. Initialized to 0, increases monotonically. |
| `votedFor` | CandidateId that received vote in current term, or null if none. |
| `log[]` | Log entries; each contains command for state machine and term when entry was received by leader. First index is 1. |

### Volatile state (on all servers)

| Field | Description |
|-------|-------------|
| `commitIndex` | Index of highest log entry known to be committed. Initialized to 0, increases monotonically. |
| `lastApplied` | Index of highest log entry applied to state machine. Initialized to 0, increases monotonically. |

### Volatile state (on leaders only, reinitialized after election)

| Field | Description |
|-------|-------------|
| `nextIndex[]` | For each server, index of next log entry to send. Initialized to leader's last log index + 1. |
| `matchIndex[]` | For each server, index of highest log entry known to be replicated on that server. Initialized to 0, increases monotonically. |

### Universal rules (all servers)

- If `commitIndex > lastApplied`: increment `lastApplied`, apply `log[lastApplied]` to state machine.
- If RPC request or response contains term T > `currentTerm`: set `currentTerm = T`, convert to follower.

## RequestVote RPC

Invoked by candidates to gather votes during elections.

**Arguments:**
- `term` — candidate's current term
- `candidateId` — candidate requesting vote
- `lastLogIndex` — index of candidate's last log entry
- `lastLogTerm` — term of candidate's last log entry

**Results:**
- `term` — currentTerm, for candidate to update itself
- `voteGranted` — true means candidate received vote

**Receiver implementation (follower):**
1. Reply false if `term < currentTerm`
2. If `votedFor` is null or `candidateId`, and candidate's log is at least as up-to-date as receiver's log, grant vote

## AppendEntries RPC

Invoked by leader to replicate log entries; also serves as heartbeat when `entries[]` is empty.

**Arguments:**
- `term` — leader's current term
- `leaderId` — so follower can redirect clients
- `prevLogIndex` — index of log entry immediately preceding new ones
- `prevLogTerm` — term of `prevLogIndex` entry
- `entries[]` — log entries to store (empty for heartbeat; may send more than one for efficiency)
- `leaderCommit` — leader's `commitIndex`

**Results:**
- `term` — currentTerm, for leader to update itself
- `success` — true if follower contained entry matching `prevLogIndex` and `prevLogTerm`

**Receiver implementation (follower):**
1. Reply false if `term < currentTerm`
2. Reply false if log doesn't contain an entry at `prevLogIndex` whose term matches `prevLogTerm`
3. If an existing entry conflicts with a new one (same index, different terms), delete the existing entry and all that follow
4. Append any new entries not already in the log
5. If `leaderCommit > commitIndex`, set `commitIndex = min(leaderCommit, index of last new entry)`

## Leader Election

All servers start as followers. A server remains a follower as long as it receives valid RPCs from a leader or candidate.

### Starting an election

When a follower's election timeout elapses without receiving AppendEntries from the current leader or granting a vote to a candidate:
1. Increment `currentTerm`
2. Transition to candidate state
3. Vote for self
4. Reset election timer
5. Send RequestVote RPCs in parallel to all other servers

### Election outcomes

- **Wins**: receives votes from majority of full cluster → becomes leader, starts sending heartbeats
- **Loses**: receives AppendEntries from another server with term >= currentTerm → reverts to follower
- **Timeout**: neither wins nor loses → start new election (increment term, repeat)

### Split vote prevention

Election timeouts are chosen randomly from a fixed interval (e.g., 150–300ms). This spreads out servers so typically only one times out first, wins the election, and sends heartbeats before others time out. Same mechanism resolves split votes: each candidate restarts its randomized timeout after each failed election.

### Election Safety

At most one leader can be elected in a given term. Each server votes for at most one candidate per term (first-come-first-served). The majority rule ensures at most one candidate can obtain a majority.

## Log Replication

The leader handles all log replication. Followers never initiate log operations.

### Normal operation

1. Client sends command to leader
2. Leader appends command as new entry to its local log
3. Leader issues AppendEntries RPCs in parallel to all followers
4. When entry is replicated on a majority, it is **committed**
5. Leader applies committed entry to its state machine
6. Leader returns result to client
7. Future AppendEntries RPCs (including heartbeats) inform followers of the `commitIndex`
8. Followers apply committed entries to their state machines in log order

### Log consistency after leader crashes

Leader crashes can leave logs inconsistent. A new leader forces followers' logs to match its own:

- Leader maintains `nextIndex` for each follower (initialized to leader's last log index + 1)
- If AppendEntries fails due to inconsistency check, leader decrements `nextIndex` for that follower and retries
- Eventually `nextIndex` reaches a point where leader and follower logs agree
- On success, conflicting entries in the follower's log are removed and replaced with leader's entries

### Log Matching Property

If two entries in different logs have the same index and term:
1. They store the same command (leader creates at most one entry per index per term)
2. The logs are identical in all preceding entries

This is maintained by the AppendEntries consistency check: the leader includes `prevLogIndex` and `prevLogTerm`; if the follower doesn't find a matching entry, it rejects the new entries.

### Leader Append-Only

A leader never overwrites or deletes entries in its own log — it only appends new entries. This simplifies reasoning about log consistency.
