---
name: ot-2026-05-03
description: Operational Transformation (OT) theory and practice for consistency maintenance in real-time collaborative editing systems. Covers transformation functions (inclusion/exclusion), consistency models (CC, CCI, CSM, CA), system architectures (server-based vs distributed OT), control algorithms, timestamp schemes, and OT vs CRDT comparison. Use when building real-time collaborative editors, resolving concurrent edit conflicts, designing collaboration backends, integrating multi-user editing into existing applications, or choosing between OT and CRDT for a collaborative system.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026-05-03"
tags:
  - operational-transformation
  - ot
  - collaborative-editing
  - concurrency-control
  - real-time-collaboration
category: protocol
external_references:
  - https://en.wikipedia.org/wiki/Operational_transformation
  - https://dev.to/sudoboink/the-basics-of-operational-transformation-288j
  - https://goyalkavya.medium.com/crdts-vs-ots-99a7cfce2418
  - https://arxiv.org/pdf/1905.01517
---

# Operational Transformation (OT)

## Overview

Operational Transformation (OT) is a concurrency control technique that maintains consistency across replicated copies of shared documents in collaborative editing systems. Instead of locking or serializing edits, OT transforms concurrent operations against each other so each achieves its intended effect regardless of execution order.

OT was pioneered by Ellis and Gibbs in 1989 with the GROVE system. Since 2009 it has powered Google Docs, Google Wave (later Apache Wave), ShareJS, CKEditor collaboration, Etherpad, Dropbox Paper, Box Notes, and numerous other real-time collaborative products.

### The Core Idea

Given a document "abc" replicated at two sites with concurrent operations:

1. `O1 = Insert[0, "x"]` — insert "x" at position 0 (site 1)
2. `O2 = Delete[2, "c"]` — delete "c" at position 2 (site 2)

At site 1, `O1` executes first: document becomes "xabc". To apply `O2`, it must be transformed against `O1`: the insert shifted positions by 1, so `O2' = Delete[3, "c"]`. Executing `O2'` on "xabc" correctly deletes "c", yielding "xab".

Without transformation, executing `O2 = Delete[2, "c"]` directly would delete "b" instead — a correctness violation.

### System Architecture

OT systems use replicated document storage: each client holds its own copy, operates locally (lock-free, non-blocking), and propagates changes to other clients. When a client receives remote operations, it transforms them against locally-executed operations before applying them. This ensures high responsiveness even over high-latency networks.

Two architecture classes exist:

- **Server-based OT** — a central server performs part of the transformation and broadcasts operations (Google Docs, Google Wave, ShareJS, CKEditor).
- **Distributed OT** — all sites run the same OT algorithm; no central transformation server is required (adOPTed, GOT, GOTO, COT, TIBOT). A message server may still be used for session management and broadcast.

## When to Use

- Building real-time collaborative text or rich-text editors (Google Docs-style)
- Resolving concurrent edit conflicts in distributed document systems
- Integrating collaboration into existing single-user editors via the Transparent Adaptation approach
- Designing collaboration backends that require intention preservation (not just convergence)
- Choosing between OT and CRDT for a collaborative editing system
- Implementing group undo in collaborative environments
- Supporting application-sharing with consistent state across replicas

## Core Concepts

**Operation**: A user edit expressed as a function on document state. Primitive operations include `Insert(position, content)`, `Delete(position, length)`, and `Update(position, attributes)`. Each operation carries its generation context (the document state at creation time).

**Inclusion Transformation (IT)**: Transforms operation `Oa` against concurrent operation `Ob` so the effect of `Ob` is included. Example: adjusting an insert position upward when another insert precedes it.

**Exclusion Transformation (ET)**: Transforms `Oa` against `Ob` so the effect of `Ob` is excluded. Used in systems supporting undo, where inverse operations must be transformed.

**Convergence**: All document replicas become identical at quiescence (all generated operations executed everywhere). Achievable by serialization alone, but serialization doesn't preserve intention.

**Causality Preservation**: Causally dependent operations execute in cause-effect order everywhere, determined by Lamport's happened-before relation. Concurrent operations may execute in different orders at different sites.

**Intention Preservation**: The effect of executing an operation on any document state matches the user's original intention (the effect achieved when the operation was generated). This cannot be achieved by serialization alone — it requires transformation.

## Plain-Text Transformation Table

The following table shows how to transform operation `Op1` against concurrent operation `Op2` for character-wise insert and delete on a linear address space. Position tie-breaking uses site identifiers (`sid1`, `sid2`).

| Op1 | Op2 | Transform Rule (result is transformed Op1) |
|-----|-----|-------------------------------------------|
| `Insert[p1, c1]` | `Insert[p2, c2]` | If `p1 < p2` or (`p1 = p2` and `sid1 < sid2`): `Insert[p1, c1]`. Else: `Insert[p1+1, c1]` |
| `Insert[p1, c1]` | `Delete[p2, n]` | If `p1 <= p2`: `Insert[p1, c1]`. If `p1 > p2 + n`: `Insert[p1-n, c1]`. If `p2 < p1 <= p2+n`: `Insert[p2+n, c1]` |
| `Delete[p1, n]` | `Insert[p2, c2]` | If `p2 <= p1`: `Delete[p1+1, n]`. Else: `Delete[p1, n]` |
| `Delete[p1, n]` | `Delete[p2, m]` | If `p1 >= p2 + m`: `Delete[p1-m, n]`. If `p1 + n <= p2`: `Delete[p1, n]`. If overlapping: adjust position and length to the non-overlapping remainder (or produce no-op if fully overlapped) |

## Advanced Topics

**Transformation Functions**: Inclusion/exclusion transform definitions, complete primitive operation tables, string-wise operations, code examples → [Transformation Functions](reference/01-transformation-functions.md)

**Consistency Models**: CC, CCI, CSM, CA models; transformation properties CP1/TP1, CP2/TP2; inverse properties IP1-IP3 for undo → [Consistency Models](reference/02-consistency-models.md)

**System Architectures**: Server-based vs distributed OT, control algorithms, communication topologies, timestamp schemes, industry products → [System Architectures](reference/03-system-architectures.md)

**OT vs CRDT**: Comparison with Conflict-free Replicated Data Types, when to choose which, industry adoption patterns, p2p myths → [OT vs CRDT](reference/04-ot-vs-crdt.md)
