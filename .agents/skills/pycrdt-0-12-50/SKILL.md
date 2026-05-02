---
name: pycrdt-0-12-50
description: Python bindings for Yrs, the Rust port of the Yjs CRDT framework. Provides shared data types (Text, Array, Map, XML) that automatically merge concurrent edits across replicas with strong eventual consistency. Use when building collaborative editors, real-time co-authoring applications, offline-first document sync, presence/awareness systems, or any distributed system requiring conflict-free replicated state without a central authority.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.12.50"
tags:
  - pycrdt
  - crdt
  - yjs
  - yrs
  - collaborative-editing
  - real-time-sync
  - python
category: library
external_references:
  - https://y-crdt.github.io/pycrdt/
  - https://github.com/y-crdt/pycrdt/tree/0.12.50
  - https://github.com/y-crdt/y-crdt/tree/main/yrs
  - https://github.com/yjs/yjs/blob/main/README.md#yjs-crdt-algorithm
---

# pycrdt 0.12.50

## Overview

pycrdt provides Python bindings for [Yrs](https://github.com/y-crdt/y-crdt/tree/main/yrs), the Rust port of the Yjs CRDT framework. It exposes shared data types — `Text`, `Array`, `Map`, and XML types — that live inside a `Doc` and automatically converge across replicas when their changes are exchanged as binary updates. The library implements the YATA conflict-resolution algorithm using composable blocks identified by Lamport timestamps (client ID + sequence number).

All operations on shared types happen inside a document transaction. Changes generate binary-encoded updates that can be serialized, sent over any transport, and applied to remote documents. The CRDT algorithm guarantees strong eventual consistency: concurrent edits from different replicas always converge to the same state regardless of message ordering.

## When to Use

- Building collaborative text editors or co-authoring tools
- Synchronizing shared state (lists, maps, structured data) across multiple clients
- Implementing offline-first applications where replicas edit independently then merge
- Adding presence/awareness (cursor positions, user state) to real-time apps
- Any distributed system needing conflict-free replicated data without a central server

## Installation / Setup

```bash
# PyPI
pip install pycrdt

# conda-forge (recommended for managed environments)
micromamba create -n my_env pycrdt
micromamba activate my_env

# Development install (requires Rust compiler + pip)
git clone https://github.com/y-crdt/pycrdt.git
cd pycrdt
pip install maturin
pip install -e .
# Rebuild Rust extension after Rust code changes:
maturin develop
```

## Quickstart

Shared types are created as Python objects, then integrated into a `Doc` to become collaborative:

```python
from pycrdt import Doc, Text, Array, Map

doc = Doc()
doc["title"] = Text("Hello")
doc["tags"] = Array(["crdt", "collaborative"])
doc["meta"] = Map({"author": "Alice", "version": 1})

# Read back
print(str(doc["title"]))       # "Hello"
print(len(doc["tags"]))        # 2
print(doc["meta"]["author"])   # "Alice"
```

**Synchronizing two documents:**

```python
# Document A makes changes
doc_a = Doc()
doc_a["text"] = Text("Hello")

# Document B requests what it's missing (state vector)
state_b = doc_b.get_state()

# Document A sends differential update
update = doc_a.get_update(state_b)

# Document B applies the update
doc_b.apply_update(update)
print(str(doc_b["text"]))  # "Hello" — converged
```

## Core Shared Types

### Doc

The container for all shared types. Every operation on shared types requires a transaction bound to a `Doc`. Root types are accessed with dict-like syntax:

```python
doc = Doc()
doc["key"] = Text("value")       # set root type
text = doc["key"]                 # get root type
for name in doc.keys():           # iterate root names
    print(name, type(doc[name]))
for name, value in doc.items():   # iterate root pairs
    pass
```

Constructor options: `client_id` (fixed identity), `skip_gc` (disable garbage collection of deleted content), `allow_multithreading` (permit cross-thread access, required for blocking transactions).

### Text

A shared string supporting insert, delete, formatting attributes, and embeds. Pythonic API mirrors `str`:

```python
doc["text"] = text = Text("Hello")
text += ", World!"                # append
del text[5]                       # remove char at index
print(text[0:5])                  # slice: "Hello"
text[7:12] = "Brian"              # replace range
```

See [Advanced Types](reference/03-advanced-types.md) for formatting (`insert` with `attrs`, `format()`) and `diff()`.

### Array

A shared list supporting index-based operations:

```python
doc["items"] = arr = Array([1, 2, 3])
arr.append(4)
arr.insert(1, "x")
del arr[0]
arr[2] = "replaced"
arr += [5, 6]                     # extend
for item in arr:                  # iterate
    print(item)
print(arr.to_py())                # convert to plain Python list
```

### Map

A shared dict supporting key-value operations:

```python
doc["config"] = m = Map({"theme": "dark"})
m["lang"] = "en"
del m["theme"]
print(m.get("missing", "default"))  # optional access
for k, v in m.items():              # iterate
    print(k, v)
```

Shared types (`Text`, `Array`, `Map`) can nest inside each other and inside `Doc` roots. Use `.to_py()` to recursively convert to plain Python objects.

## Advanced Topics

**Transactions & Events**: Transaction models (non-blocking vs blocking), origins, async context managers, observe/observe_deep callbacks, async event iteration, StickyIndex cursors → [Transactions & Events](reference/01-transactions-and-events.md)

**Synchronization**: Update encoding, state vectors, Y-Sync protocol, Provider/Channel abstraction, Awareness for presence/state sharing → [Synchronization](reference/02-synchronization.md)

**Advanced Types**: XML types (XmlFragment, XmlElement, XmlText), TypedDoc/TypedMap/TypedArray for static typing, Snapshots, UndoManager, Text formatting and diff → [Advanced Types](reference/03-advanced-types.md)
