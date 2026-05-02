# Transactions & Events

## Contents
- Transaction Models
- Origins
- Event Observation
- Async Event Iteration
- StickyIndex

## Transaction Models

Every mutation to shared types happens inside a document transaction. Only one transaction exists per document at a time. All changes within a single transaction appear atomic — they are indistinguishable from simultaneous edits.

### `doc.transaction()` — Non-blocking (preferred)

```python
with doc.transaction() as txn:
    doc["text"].insert(0, "new text")
    doc["tags"].append("updated")
```

- Creates a new transaction if none exists, or reuses the current one
- **Never blocks** — use this most of the time
- Nested calls merge into the outer transaction (all changes go to the same txn)
- Accepts an optional `origin` parameter for undo tracking

### `doc.new_transaction()` — Blocking / exclusive

```python
# Synchronous (requires allow_multithreading=True on Doc)
with doc.new_transaction(timeout=5.0):
    # Exclusive access — blocks until transaction acquired
    doc["text"].insert(0, "new")

# Asynchronous (yields to event loop)
async with doc.new_transaction():
    doc["text"].insert(0, "new")
```

- Always creates a **new** transaction (does not reuse)
- Blocks if another transaction is active
- Sync mode: uses OS-level locking — requires `Doc(allow_multithreading=True)` and operations in different threads
- Async mode: yields to event loop — works in single-threaded async code
- Optional `timeout` (seconds) raises `TimeoutError` on expiry

### When to choose which

| Scenario | Use |
|----------|-----|
| Most mutations | `doc.transaction()` |
| Need exclusive access from another thread | `doc.new_transaction()` (sync) + `allow_multithreading=True` |
| Async code needing exclusive access | `doc.new_transaction()` (async) |
| Grouping multiple changes atomically | `doc.transaction()` with multiple ops inside |

## Origins

Transactions carry an optional `origin` — any Python object used to tag changes for undo filtering:

```python
with doc.transaction(origin="user-edit"):
    doc["text"].insert(0, "A")

with doc.transaction(origin="auto-format"):
    doc["text"].format(0, 1, {"bold": True})
```

The `UndoManager` can include or exclude specific origins:

```python
undo_mgr = UndoManager(doc=doc)
undo_mgr.exclude_origin("auto-format")  # auto-format changes won't be undone
```

## Event Observation

Register callbacks on shared types or the document to react to changes.

### Shared type events

Each shared type supports `observe()` (top-level only) and `observe_deep()` (includes nested changes):

```python
from pycrdt import Text, Doc

doc = Doc()
doc["text"] = text = Text("Hello")

# Top-level changes only
sub = text.observe(lambda event: print(f"Text changed: {event.delta}"))

# Deep changes (including nested shared types in Array/Map)
sub_deep = arr.observe_deep(lambda events: print(f"Deep changes: {len(events)}"))

# Unsubscribe
text.unobserve(sub)
```

Event objects carry:
- `target` — the changed shared type
- `delta` — list of change descriptions (insert/remove/retain with attributes)
- `path` — list of indices/keys locating the change within the hierarchy

### Document-level events

Observe all changes to a document (used primarily for syncing):

```python
sub = doc.observe(lambda event: print(f"Update: {len(event.update)} bytes"))
doc.unobserve(sub)
```

The `TransactionEvent` carries an `update` property — the binary-encoded change that can be sent to remote replicas.

### Async callbacks

When using async transactions, register async callbacks for back-pressure:

```python
async def on_change(event):
    await send_to_remote(event.update)

doc.observe(on_change)  # async callback
# Must use async transaction:
async with doc.new_transaction():
    doc["text"].insert(0, "x")
    # Transaction won't exit until on_change completes
```

Registering an async callback while using sync transactions raises `RuntimeError`.

## Async Event Iteration

Instead of callbacks, iterate over events asynchronously. This provides natural back-pressure via buffered streams:

```python
async def main():
    async with doc.events() as events:
        async for event in events:
            update = event.update
            await send_to_remote(update)

# Subdoc events
async with doc.events(subdocs=True) as subdoc_events:
    async for event_batch in subdoc_events:
        for event in event_batch:
            handle_subdoc_event(event)
```

Parameters:
- `subdocs=False` — yields `TransactionEvent` (default)
- `subdocs=True` — yields batches of `SubdocsEvent`
- `max_buffer_size` — max events to buffer (default: infinity). Use finite value with `async_transactions=True` for back-pressure.
- `async_transactions=True` — enables back-pressure on transactions when buffer is full

## StickyIndex

A cursor position that remains stable across edits. Unlike raw integer indices, a `StickyIndex` tracks content by identity rather than position:

```python
from pycrdt import Assoc

doc["text"] = text = Text("Hello World")

# Create sticky index at position 5 (between "Hello" and " World")
sticky = text.sticky_index(5, assoc=Assoc.AFTER)

# After edits, the sticky index follows the content
doc["text"].insert(0, "Say ")  # "Say Hello World"
# sticky still points to between "Hello" and " World"

# Get current integer position
with doc.transaction() as txn:
    pos = sticky.get_index(txn._txn)

# Serialize for persistence
encoded = sticky.encode()
decoded = StickyIndex.decode(encoded)
```

Use cases: saving cursor positions, selection ranges, or any bookmark that should survive concurrent edits.
