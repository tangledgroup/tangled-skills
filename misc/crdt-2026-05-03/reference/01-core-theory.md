# Core Theory

## Contents
- State-Based CRDTs (CvRDT)
- Operation-Based CRDTs (CmRDT)
- Semilattice Requirements
- Delta State CRDTs
- Strong Eventual Consistency

## State-Based CRDTs (CvRDT)

A state-based CRDT, or **Convergent Replicated Data Type** (CvRDT), is defined by:

- A **state type** `S` representing the local replica's data
- An **initial state** function producing the empty/neutral state
- An **update** function that modifies local state based on user actions
- A **merge** (join) function that combines two states into one

```
CvRDT = (S, init, update, merge)
  S       — state type
  init    : → S
  update  : Action → S → S
  merge   : S × S → S
```

Replicas periodically disseminate their full state via gossip protocols. On receiving a remote state, each replica applies `merge(local, remote)`. Convergence is guaranteed because merge forms a join-semilattice.

**Key insight**: The merge function must be commutative, associative, and idempotent — properties that make the CRDT invariant under message reordering, batching, and duplication.

## Operation-Based CRDTs (CmRDT)

An operation-based CRDT, or **Commutative Replicated Data Type** (CmRDT), is defined by:

- A **state type** `S`
- An **operation type** `Op`
- An **apply** function that executes an operation on local state

```
CmRDT = (S, Op, apply)
  S     — state type
  Op    — operation type
  apply : Op → S → S
```

Replicas broadcast operations directly to other replicas. Operations must be commutative and associative. Unlike CvRDTs, CmRDTs do **not** require idempotency — instead they require that operations are delivered exactly once (no drops, no duplicates) and in causal order.

**Tradeoff**: CmRDTs transmit less data (only the operation, not full state) but place stricter requirements on the communication layer. CvRDTs work over unreliable gossip; CmRDTs need reliable causal delivery.

The two approaches are theoretically equivalent — each can emulate the other — but practical differences matter for bandwidth and implementation complexity.

## Semilattice Requirements

A **join-semilattice** is a partially ordered set where every pair of elements has a least upper bound (join). The merge function computes this join.

For a CRDT's merge to guarantee convergence, the state space with merge must form a join-semilattice:

- **Commutativity**: `merge(a, b) = merge(b, a)` — order of arrival doesn't matter
- **Associativity**: `merge(a, merge(b, c)) = merge(merge(a, b), c)` — batch merging works
- **Idempotence**: `merge(a, a) = a` — duplicate messages are harmless
- **Monotonicity**: Updates only move state "upward" in the partial order

The partial order is defined by: `a ≤ b` iff `merge(a, b) = b`. This means `b` contains all information in `a` plus possibly more.

**Practical consequence**: State can only grow (monotonically increase). To support "removal" semantics, CRDTs use tombstones — markers that something was removed, retained so merges remain correct.

## Delta State CRDTs

Pure state-based CRDTs send the entire state on every sync, which is wasteful when only small changes occurred. **Delta state CRDTs** optimize this by sending only the difference between current state and what was last sent to each replica.

```
delta(target_replica) = state ⊖ last_sent[target_replica]
merge_with_delta(state, delta) = merge(state, delta)
```

For a G-Counter with 1000 replicas, incrementing once generates a delta of `{my_id: +1}` instead of transmitting all 1000 entries.

Delta CRDTs preserve the same convergence guarantees as full-state CRDTs because deltas are themselves valid states in the semilattice — merging them incrementally equals merging the full state.

Most production systems (Riak, Automerge) use delta-state internally. Start with deltas if implementing from scratch.

## Strong Eventual Consistency

CRDTs provide **strong eventual consistency** (SEC), a consistency model stronger than plain eventual consistency:

> If two replicas have received the same set of updates (from any sources), they are guaranteed to hold identical state — regardless of the order those updates arrived.

This differs from plain eventual consistency, which only guarantees convergence if no new updates occur. SEC guarantees convergence even under concurrent updates, because the merge function is deterministic and confluent.

SEC does **not** require:
- Synchronized clocks
- Central coordinators
- Consensus protocols
- Locks or transactions

It requires only that all updates eventually propagate (no permanent partitions) and that the merge function satisfies semilattice properties.
