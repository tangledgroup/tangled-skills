---
name: crdt-2026-05-03
description: Conflict-free replicated data types (CRDTs) replicate across distributed nodes without coordination, guaranteeing strong eventual consistency via merge functions. Covers CvRDT/CmRDT theory, counters, registers, sets, sequence CRDTs (RGA/WOOT/Logoot), maps, trees, garbage collection, delta CRDTs, and OT comparison. Use when building collaborative editors, offline-first apps, or distributed systems.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026-05-03"
tags:
  - crdt
  - distributed-systems
  - conflict-resolution
  - collaborative-editing
  - eventual-consistency
  - offline-first
category: distributed-systems
external_references:
  - https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type
  - https://crdt.tech/implementations
  - https://github.com/alangibson/awesome-crdt
  - https://www.iankduncan.com/engineering/2025-11-27-crdt-dictionary/
  - https://hackernoon.com/crdts-vs-operational-transformation-a-practical-guide-to-real-time-collaboration
---

# Conflict-free Replicated Data Types (CRDTs)

## Overview

A CRDT is a data structure replicated across multiple networked replicas that allows concurrent updates without coordination and guarantees all replicas eventually converge to the same state. The convergence guarantee comes from mathematically proven merge functions rather than locks, consensus protocols, or central coordinators.

CRDTs trade metadata overhead for availability: they accumulate information (tombstones, tags, version vectors) so that any two replicas can be merged correctly regardless of network partitions, message reordering, or duplication. This makes them ideal for offline-first applications, peer-to-peer collaboration, and geo-distributed systems where strong consistency is too expensive.

## When to Use

- Building real-time collaborative editors (documents, whiteboards, code)
- Implementing offline-first applications that sync when connectivity returns
- Designing distributed databases with automatic conflict resolution
- Synchronizing state across replicas in peer-to-peer networks
- Replacing server-authoritative architectures where latency or availability matters more than immediate consistency

## Core Concepts

**State-based CRDTs (CvRDT — Convergent)**: Replicas periodically exchange their full state and merge using a join function that is commutative, associative, and idempotent. Simpler to implement; requires gossip-style dissemination. Drawback: entire state transmitted on each sync. Optimized via *delta state* CRDTs that send only changes since last sync.

**Operation-based CRDTs (CmRDT — Commutative)**: Replicas broadcast individual operations rather than full states. Operations must be commutative and associative, and require causal delivery (no drops or duplicates). Lower bandwidth for small updates; stricter requirements on the communication layer.

Both approaches provide *strong eventual consistency*: if two replicas have received the same set of updates (regardless of order), they are guaranteed to hold identical state.

**Semilattice foundation**: The merge function computes the join in a join-semilattice, ensuring convergence. Key properties:
- **Commutative**: `merge(A, B) = merge(B, A)` — handles message reordering
- **Associative**: `merge(A, merge(B, C)) = merge(merge(A, B), C)` — enables batch merging
- **Idempotent**: `merge(A, A) = A` — handles duplicate messages

## Advanced Topics

**Core Theory**: CvRDT vs CmRDT formal definitions, semilattice properties, delta CRDT optimization → [Core Theory](reference/01-core-theory.md)

**Basic Types**: Counters (G-Counter, PN-Counter), registers (LWW-Register, MV-Register), sets (G-Set, 2P-Set, LWW-Element-Set, OR-Set) with code, tradeoffs, and selection guidance → [Basic Types](reference/02-basic-types.md)

**Advanced Types**: Sequence CRDTs (RGA, WOOT, Logoot/LSEQ, YATA), OR-Map for nested structures, Tree CRDTs for hierarchical data → [Advanced Types](reference/03-advanced-types.md)

**Practical Concerns**: Garbage collection strategies (time-based expiry, coordinated GC, version vectors, bounded structures, checkpoint/rebase), performance comparison table, causal delivery requirements → [Practical Concerns](reference/04-practical-concerns.md)

**Libraries and Ecosystem**: Yjs, Automerge, Loro, pycrdt; CRDT-enabled databases (Riak, AntidoteDB, Redis Enterprise, CosmosDB); production applications (Apple Notes, Zed, Figma) → [Libraries and Ecosystem](reference/05-libraries-and-ecosystem.md)

**OT vs CRDT**: Operational transformation mechanics, comparison across architecture/offline-support/complexity/bandwidth dimensions, hybrid approaches → [OT vs CRDT](reference/06-ot-vs-crdt.md)
