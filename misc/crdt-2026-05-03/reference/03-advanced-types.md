# Advanced CRDT Types

## Contents
- Sequence CRDTs: The Challenge
- RGA (Replicated Growable Array)
- WOOT (Without Operational Transformation)
- Logoot and LSEQ (Position-Based)
- YATA (Yjs Algorithm for Text Editing)
- OR-Map (Observed-Remove Map)
- Tree CRDTs

## Sequence CRDTs: The Challenge

Sequences are the hardest CRDT category. Unlike sets where elements have stable identity, sequences must maintain ordering despite concurrent insertions and deletions at arbitrary positions. Positional indices change as other replicas modify the document, making "insert at position 5" ambiguous.

All sequence CRDTs solve this by assigning each element a unique, immutable identifier that determines its position independently of array index. The main approaches:

- **Tree-based** (RGA): Elements form a tree; position derived from parent relationships
- **Constraint-based** (WOOT): Elements store prev/next references with deterministic tiebreaking
- **Position-based** (Logoot/LSEQ): Dense ordering between elements via allocatable identifiers
- **Plainlist** (YATA/Yjs): Optimized flat structure for text editing workloads

All sequence CRDTs accumulate tombstones for deleted elements. A 1000-character document with heavy editing may internally contain 50,000+ tombstones.

## RGA (Replicated Growable Array)

RGA assigns each element a unique ID and stores the sequence as a tree based on insertion order and causality. Each element knows its "parent" — the element after which it was inserted.

```python
# State: dict[uid, (value, parent_uid)]
# uid = (replica_id, sequence_number) — globally unique
def insert(parent_uid, value, my_uid, state):
    state[my_uid] = (value, parent_uid)

def delete(uid, state):
    if uid in state:
        state[uid] = (state[uid][0], state[uid][1], True)  # mark tombstone

def linearize(state):
    # Build tree from parent pointers, do in-order traversal
    # Skip tombstoned elements
    pass

def merge(a, b):
    return {**a, **b}  # union of all elements
```

**Key insight**: Instead of "insert at position 5," you say "insert after element X." Since X has a unique ID, this instruction is unambiguous regardless of concurrent edits elsewhere.

**Tradeoffs**: O(log n) insert/delete, O(n) linearization. Tombstones accumulate — no compaction without coordination. Causal order preserved: if A was inserted before B on the same replica, that relationship holds globally.

**When to use**: Collaborative text editing where arbitrary-position insertions must be supported.

## WOOT (Without Operational Transformation)

WOOT stores characters as objects with unique IDs and bidirectional prev/next references. When multiple characters claim to be between two neighbors, a deterministic UID ordering resolves conflicts.

```python
# State: set of {id: uid, value: char, prev: uid, next: uid, visible: bool}
def insert(value, my_uid, prev_uid, next_uid, state):
    state.add({
        'id': my_uid,
        'value': value,
        'prev': prev_uid,
        'next': next_uid,
        'visible': True,
    })

def delete(uid, state):
    for char in state:
        if char['id'] == uid:
            char['visible'] = False  # tombstone

def linearize(state):
    # Topological sort respecting prev/next constraints
    # Filter invisible chars, break ties by UID order
    pass
```

**Tradeoffs**: O(n²) worst-case linearization. No causal delivery required — constraints handle ordering. More complex than RGA with slower reads. Primarily of historical interest; modern implementations prefer RGA or YATA.

## Logoot and LSEQ (Position-Based)

Logoot assigns each element a position identifier — a sequence of (digit, replicaId) pairs ordered lexicographically. Positions form a **dense order**: between any two positions, you can always allocate a new one.

```python
# Position = [(int, replica_id), ...]
# State: set of {position: Position, value: char, deleted: bool}
def insert(value, before_pos, after_pos, my_id, state):
    new_pos = allocate_position(before_pos, after_pos, my_id)
    state.add({'position': new_pos, 'value': value, 'deleted': False})

def allocate_position(before, after, replica_id):
    # Find a position between before and after
    # Use replica_id as tiebreaker for determinism
    pass
```

**LSEQ** improves on Logoot with adaptive allocation: alternates strategies (boundary+ vs boundary-) based on tree depth to keep positions shorter on average.

**Tradeoffs**: No need to reference other elements by ID. Positions are self-describing. Can insert without knowing full document structure. Position identifiers grow over time — pathologically long with many edits at the same location. O(n log n) read complexity.

**When to use**: When you want simpler semantics than RGA/WOOT and can tolerate position identifier growth.

## YATA (Yjs Algorithm for Text Editing)

YATA (Yet Another Transformation Approach), developed by Kevin Jahns for Yjs, combines ideas from RGA and WOOT while optimizing for the common case of sequential insertions (typing).

Key optimizations:
- **Plainlist instead of tree**: Uses a flat structure rather than tree navigation, reducing pointer chasing
- **Chunked updates**: Batches consecutive inserts from the same author into single update messages
- **State vector**: Tracks what each replica knows, enabling delta-state sync
- **Content blocks**: Groups characters by type (string, format, embed) for efficient storage

Yjs with YATA is notably faster than Automerge for text operations and includes bindings for CodeMirror, Monaco, Quill, and ProseMirror. Used in production by JupyterLab, Nimbus Note, and Serenity Notes.

## OR-Map (Observed-Remove Map)

Maps are common application structures. OR-Map implements a CRDT map where each key maps to an OR-Set of tagged values.

```python
# State: dict[key, dict[tag, value]]
def put(key, value, tag, state):
    state.setdefault(key, {})[tag] = value

def remove_key(key, state):
    if key in state:
        del state[key]

def get(key, state):
    values = state.get(key, {})
    if not values:
        return None
    # Return the "latest" value (implementation-dependent tiebreaker)
    return next(iter(values.values()))

def merge(a, b):
    result = dict(a)
    for key, tags in b.items():
        result.setdefault(key, {}).update(tags)
    return result
```

Alternatively, implement as OR-Set of keys with per-key nested CRDTs (e.g., LWW-Register for each value).

**Tradeoffs**: Full map operations with CRDT semantics. Can nest other CRDTs as values. Complex metadata management and garbage collection challenges.

**When to use**: Collaborative JSON documents, distributed configuration, nested data structures. Automerge implements this pattern for its JSON CRDT.

## Tree CRDTs

Extending CRDTs to trees is challenging because parent-child relationships must be maintained consistently under concurrent structural changes: moving the same node to different parents, or creating cycles (A under B while B under A).

**OR-Tree approach**: Each node stores an OR-Set of potential parents. Conflict resolution strategies:
- Last-write-wins (timestamps pick winning parent)
- First-wins (first observed parent wins)
- Application-level merge (temporarily allow multiple parents)

```python
# State: dict[node_id, {parents: ORSet[parent_id], value: data}]
```

**Tradeoffs**: Handles concurrent structural changes. Must prevent cycles (may require rejecting some operations). Moving subtrees is complicated. High metadata overhead.

**When to use**: File systems, organizational charts, document outlines where hierarchy must be replicated. For many cases, an OR-Map with explicit parent fields is simpler than a full Tree CRDT.
