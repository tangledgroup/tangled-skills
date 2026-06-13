# OT vs CRDT

## Contents
- Operational Transformation (OT)
- How OT Works
- OT's Complexity
- Comparison: OT vs CRDT
- When to Choose Each
- Hybrid Approaches

## Operational Transformation (OT)

OT was invented at Xerox PARC in 1989 and powers Google Docs, Google Wave, and many collaborative editors. The core idea: transform operations based on what has happened concurrently.

When you receive a remote operation, you don't apply it directly — you **transform** it against operations that have already been applied locally, adjusting positions and semantics so the result is correct.

## How OT Works

Document starts as `"Hello"` (positions 0–4). Concurrently:
- Alice: `Insert(" World", 5)`
- Bob: `Delete(0, 1)` (delete "H")

When Bob receives Alice's insert, he transforms it against his delete. Since Bob deleted a character before position 5, Alice's insert position shifts left:

```
Transform(Insert(" World", 5), Delete(0, 1)) = Insert(" World", 4)
```

When Alice receives Bob's delete, no transformation needed — position 0 comes before her insert at position 5.

Both replicas end up with `"ello World"`.

A minimal transform function handles four cases (insert vs insert, insert vs delete, delete vs insert, delete vs delete), each requiring careful position arithmetic:

```typescript
function transform(op, against): Operation {
  if (op.type === 'insert' && against.type === 'delete') {
    if (against.position < op.position) {
      return { ...op, position: Math.max(against.position, op.position - against.length) };
    }
  }
  // ... 3 more cases, each with edge conditions
}
```

## OT's Complexity

The simple implementation above is incomplete. Real OT systems face:

- **Transformation puzzles**: The order of transformations matters. Getting it wrong leads to divergence. Proving correctness requires formal transformation properties (TT, TP1, TP2).
- **Server authority**: Most OT systems require a central server to determine canonical operation ordering. Peer-to-peer OT is possible but significantly more complex.
- **Operational complexity**: Each operation type needs transformation rules against every other type — O(n²) combinations. Adding rich text (format, undo, selection) multiplies complexity.
- **History management**: Must retain enough history to transform incoming operations, but can compact aggressively once all replicas have caught up.

Google's OT implementation for Docs reportedly has edge cases that took years to resolve.

## Comparison: OT vs CRDT

| Dimension | OT | CRDT |
|-----------|-----|------|
| **Architecture** | Requires central server (typically) | Peer-to-peer, no coordinator |
| **Offline support** | Limited — needs server to reconcile | Full — works offline, syncs later |
| **Correctness model** | Transform operations to resolve conflicts | Mathematical convergence guarantee |
| **Implementation complexity** | High (O(n²) transform rules, edge cases) | Medium (per-type logic, but composable) |
| **Bandwidth** | Lower — sends small operations | Higher — metadata overhead (tombstones, tags) |
| **Storage growth** | Bounded — history can be compacted | Unbounded without garbage collection |
| **Rich text support** | Complex — many operation types to transform | Better — format as separate CRDT layer |
| **Undo/redo** | Native (inverse operations) | Requires additional metadata (intent tracking) |
| **Reasoning about correctness** | Ad-hoc, case-by-case proofs | Formal semilattice properties |

## When to Choose Each

**Choose OT when**:
- You have a central server architecture already
- Bandwidth is constrained (mobile, low-connectivity)
- You need fine-grained control over conflict resolution
- Working with established systems (Google Docs compatibility)
- Undo/redo is a primary requirement

**Choose CRDTs when**:
- Peer-to-peer or mesh networking
- Offline-first is critical
- You want mathematical correctness guarantees
- Syncing across many replicas without central coordination
- Building new projects (use Yjs or Automerge — don't implement from scratch)

## Hybrid Approaches

Many production systems combine both:

- **Figma**: CRDT-inspired data model with server authority for tiebreaking and specific features
- **Apple Notes**: CRDTs for sync between devices, server coordinates
- **Linear**: CRDTs for local-first sync with server-side ordering
- **Microsoft Fluid Framework**: CRDT-inspired distributed data structures with server coordination layer

The hybrid approach takes OT's bandwidth efficiency and CRDT's correctness guarantees, trading some decentralization for practical performance.
