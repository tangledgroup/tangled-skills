# Basic CRDT Types

## Contents
- G-Counter (Grow-Only Counter)
- PN-Counter (Positive-Negative Counter)
- LWW-Register (Last-Write-Wins Register)
- MV-Register (Multi-Value Register)
- G-Set (Grow-Only Set)
- 2P-Set (Two-Phase Set)
- LWW-Element-Set
- OR-Set (Observed-Remove Set)

## G-Counter (Grow-Only Counter)

A counter that only increases. Each replica tracks its own increment count in a per-replica map.

```python
# State: dict[replica_id, int]
def init(): return {}

def increment(my_id, state):
    state[my_id] = state.get(my_id, 0) + 1

def value(state):
    return sum(state.values())

def merge(a, b):
    return {k: max(a.get(k, 0), b.get(k, 0)) for k in a | b}
```

**Properties**: Space O(replicas), not O(increments). A billion increments costs the same space as one. Merge is element-wise max — commutative, associative, idempotent.

**When to use**: Page view counters, event occurrence tracking, any metric that only grows.

## PN-Counter (Positive-Negative Counter)

Two G-Counters combined: one for increments (P), one for decrements (N). Value = ΣP − ΣN.

```python
# State: {p: dict[replica_id, int], n: dict[replica_id, int]}
def increment(my_id, state):
    state['p'][my_id] = state['p'].get(my_id, 0) + 1

def decrement(my_id, state):
    state['n'][my_id] = state['n'].get(my_id, 0) + 1

def value(state):
    return sum(state['p'].values()) - sum(state['n'].values())

def merge(a, b):
    return {
        'p': {k: max(a['p'].get(k, 0), b['p'].get(k, 0)) for k in a['p'] | b['p']},
        'n': {k: max(a['n'].get(k, 0), b['n'].get(k, 0)) for k in a['n'] | b['n']},
    }
```

**Tradeoff**: Double the space of G-Counter. Value can decrease externally while internal state grows monotonically. Can go negative if decrements exceed increments — application must validate.

**When to use**: Upvote/downvote counters, inventory tracking, any bidirectional counter.

## LWW-Register (Last-Write-Wins Register)

Stores a single value with a timestamp. Concurrent writes resolve by keeping the latest timestamp.

```python
# State: (value, timestamp)
def write(value, ts, state):
    return (value, ts)

def merge(a, b):
    return a if a[1] >= b[1] else b  # tiebreaker: prefer a
```

**Properties**: Minimal space O(1). Loses concurrent updates — only one survives. Requires clock synchronization or logical clocks with replica ID tiebreakers.

**When to use**: User profile fields, configuration settings, cached computed values where lost updates are acceptable.

## MV-Register (Multi-Value Register)

Preserves all concurrent writes instead of discarding them. Returns a set of values when read.

```python
# State: set of (value, version_vector) pairs
def write(value, vv, state):
    # Remove any entries causally dominated by this write
    return {(value, vv)} | {
        (v, vvv) for v, vvv in state
        if not dominated_by(vvv, vv) and not dominated_by(vv, vvv)
    }

def read(state):
    return {v for v, _ in state}  # may return multiple values
```

**Properties**: No data loss on concurrent updates. Application must handle conflict resolution when multiple values returned. Slightly larger space overhead proportional to number of concurrent writes.

**When to use**: Collaborative text fields, conflict-aware configuration, any scenario where losing an update is unacceptable.

## G-Set (Grow-Only Set)

A set that only allows additions. Once added, an element cannot be removed.

```python
# State: set of elements
def add(element, state):
    return state | {element}

def contains(element, state):
    return element in state

def merge(a, b):
    return a | b  # union
```

**Properties**: Merge is set union — trivially commutative, associative, idempotent. No removal support.

**When to use**: Event logs, observed fact collections, tags that accumulate.

## 2P-Set (Two-Phase Set)

Two G-Sets: one for additions (A), one for removals/R (tombstones). Element is present if in A and not in R. Once removed, cannot be re-added.

```python
# State: {a: set, r: set}
def add(element, state):
    state['a'].add(element)

def remove(element, state):
    if element in state['a'] and element not in state['r']:
        state['r'].add(element)

def contains(element, state):
    return element in state['a'] and element not in state['r']

def merge(a, b):
    return {
        'a': a['a'] | b['a'],
        'r': a['r'] | b['r'],
    }
```

**Properties**: Remove-wins semantics. Both sets grow monotonically — removed elements never truly disappear (tombstones accumulate). No garbage collection without coordination.

**When to use**: Task completion tracking, revoked permissions, one-lifecycle items (add → remove, never re-add).

## LWW-Element-Set

Each element has a timestamp for its latest add and remove operation. Element is present if the latest operation was an add. Supports re-add after removal.

```python
# State: {adds: dict[element, timestamp], removes: dict[element, timestamp]}
def add(element, ts, state):
    current = state['adds'].get(element, 0)
    state['adds'][element] = max(current, ts)

def remove(element, ts, state):
    current = state['removes'].get(element, 0)
    state['removes'][element] = max(current, ts)

def contains(element, state):
    add_ts = state['adds'].get(element, 0)
    rem_ts = state['removes'].get(element, 0)
    return add_ts > rem_ts  # bias: add wins on tie

def merge(a, b):
    return {
        'adds': {k: max(a['adds'].get(k, 0), b['adds'].get(k, 0)) for k in a['adds'] | b['adds']},
        'removes': {k: max(a['removes'].get(k, 0), b['removes'].get(k, 0)) for k in a['removes'] | b['removes']},
    }
```

**Properties**: Supports add/remove/re-add. Loses information on concurrent add+remove (one is discarded). Requires clock synchronization — clock skew causes one replica to always win. Use hybrid logical clocks or (timestamp, replica_id) pairs as tiebreakers.

**When to use**: User preferences, feature flags, cached collections where LWW semantics are acceptable.

## OR-Set (Observed-Remove Set)

The most sophisticated set CRDT. Each addition generates a unique tag. Removal removes only the tags observed at removal time. Concurrent adds create new tags that survive removal. Add-wins semantics.

```python
# State: dict[element, set[tag]]
# Tag = (replica_id, sequence_number) — globally unique
def add(element, tag, state):
    state.setdefault(element, set()).add(tag)

def remove(element, state):
    # Remove all tags currently observed for this element
    if element in state:
        del state[element]  # observed tags are implicitly tombstoned

def contains(element, state):
    return element in state and len(state[element]) > 0

def merge(a, b):
    result = dict(a)
    for elem, tags in b.items():
        result.setdefault(elem, set()).update(tags)
    # Remove any tags that were tombstoned (observed by a remove)
    # In practice: track removed tags per element
```

More precisely, maintain both add-tags and remove-tags per element:

```python
# State: dict[element, {add_tags: set, remove_tags: set}]
def add(element, tag, state):
    entry = state.setdefault(element, {'add_tags': set(), 'remove_tags': set()})
    entry['add_tags'].add(tag)

def remove(element, state):
    if element in state:
        # Move all observed add-tags to remove-tags (tombstones)
        state[element]['remove_tags'].update(state[element]['add_tags'])
        state[element]['add_tags'].clear()

def contains(element, state):
    if element not in state:
        return False
    return len(state[element]['add_tags'] - state[element]['remove_tags']) > 0

def merge(a, b):
    result = {}
    for elem in set(a) | set(b):
        ea = a.get(elem, {'add_tags': set(), 'remove_tags': set()})
        eb = b.get(elem, {'add_tags': set(), 'remove_tags': set()})
        result[elem] = {
            'add_tags': ea['add_tags'] | eb['add_tags'],
            'remove_tags': (ea['remove_tags'] | eb['remove_tags']) |
                           ((ea['add_tags'] | eb['add_tags']) & (ea['remove_tags'] | eb['remove_tags'])),
        }
```

**Properties**: Add-wins semantics — concurrent add and remove means element stays. No timestamp requirements. Properly handles all concurrent operation patterns. Larger space overhead (tags per element). Requires garbage collection strategy for removed tags.

**When to use**: Collaborative editing, shopping carts, any scenario where concurrent adds must be preserved and re-add after removal is needed. This is the default choice when you need a full-featured set CRDT.
