---
name: raft-2026-05-03
description: Raft consensus algorithm for managing replicated logs across a cluster of servers. Provides leader election, log replication, safety guarantees, cluster membership changes via joint consensus, and log compaction via snapshotting. Use when building fault-tolerant distributed systems, implementing replicated state machines, designing consensus-based coordination services, configuring Raft-based databases (etcd, CockroachDB, TiKV), or reasoning about distributed consistency and safety properties.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - raft
  - consensus
  - distributed-systems
  - replicated-log
  - leader-election
  - fault-tolerance
category: protocol
external_references:
  - https://raft.github.io/
  - https://raft.github.io/raft.pdf
  - https://en.wikipedia.org/wiki/Raft_(algorithm)
  - https://web.stanford.edu/~ouster/cs190-winter23/lectures/raft/
---

# Raft Consensus Algorithm

## Overview

Raft is a consensus algorithm for managing a replicated log across a cluster of servers. Designed by Diego Ongaro and John Ousterhout at Stanford University, it produces results equivalent to (multi-)Paxos but decomposes the problem into relatively independent subproblems — leader election, log replication, and safety — making it significantly more understandable. Raft is not Byzantine fault tolerant; it assumes all participants are trustworthy and failures are crash-stop.

A Raft cluster typically has 5 servers (tolerating 2 failures). At any time each server is a **leader**, **follower**, or **candidate**. The leader handles all client requests, replicates log entries to followers via `AppendEntries` RPCs, and commits entries once replicated on a majority. If the leader fails, followers detect this via election timeouts and trigger a new election.

## When to Use

- Implementing a consensus-based replicated state machine from scratch
- Building fault-tolerant coordination services (key-value stores, configuration management, leader election)
- Understanding or debugging Raft-based systems (etcd, CockroachDB, TiKV, Kafka KRaft, ScyllaDB)
- Designing cluster membership change protocols with zero-downtime reconfiguration
- Reasoning about distributed safety properties and linearizability
- Choosing between consensus algorithms (Raft vs Paxos vs Viewstamped Replication)

## Core Concepts

**Replicated state machines:** Each server runs an identical state machine fed by a replicated log. The consensus algorithm ensures all logs contain the same commands in the same order, so all state machines reach identical states.

**Terms:** Time is divided into numbered terms (logical clock). Each term begins with an election. A winning candidate serves as leader for the rest of the term. Terms detect stale information — servers reject requests with older term numbers and revert to follower on discovering a higher term.

**Roles:**
- **Leader** — handles all client requests, replicates log entries, commits entries
- **Follower** — passive; responds to RPCs from leaders and candidates only
- **Candidate** — transitional state during elections; votes for self and requests votes

**Log entries:** Each entry has an index (position), a term (when created), and a command for the state machine. Entries retain their original term number across all logs, enabling consistency checks.

**Majority rule:** A cluster of N servers tolerates floor(N/2) failures. Decisions require votes from a majority. For N=5, any 3 servers form a majority.

## Advanced Topics

**Core Protocol**: Server states, persistent/volatile state, RequestVote and AppendEntries RPCs, leader election, log replication → [Core Protocol](reference/01-core-protocol.md)

**Safety Properties**: Election safety, Log Matching, Leader Completeness, State Machine Safety, election restrictions, commitment rules, crash handling → [Safety](reference/02-safety.md)

**Membership Changes**: Joint consensus, configuration change timeline, edge cases (new servers, leader exclusion, removed server disruptions) → [Membership Changes](reference/03-membership-changes.md)

**Log Compaction**: Snapshotting, InstallSnapshot RPC, performance considerations → [Log Compaction](reference/04-log-compaction.md)

**Client Interaction**: Leader discovery, linearizability, idempotency via serial numbers, read-only operations, timing requirements → [Client Interaction](reference/05-client-interaction.md)

**Extensions and Production**: Pre-Vote, leadership transfer, production systems (etcd, CockroachDB, TiKV), Paxos comparison, formal verification → [Extensions and Production](reference/06-extensions-and-production.md)
