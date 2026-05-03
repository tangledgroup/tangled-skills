# Practical Concerns

## Contents
- Garbage Collection Strategies
- Performance Comparison
- Causal Delivery and Version Vectors

## Garbage Collection Strategies

CRDTs converge by monotonically accumulating information. Production systems cannot grow unbounded — tombstones, tags, and version vectors must be managed. The fundamental tension: discarding metadata risks incorrect merges with replicas that haven't seen the discarded data.

### The Zombie Resurrection Problem

If replica A garbage-collects tags `{tag_1, tag_2}` for an element it removed, then later merges with replica B (which has been offline and still holds `tag_3`), the element reappears:

```
A after GC: {}
B (offline): {element: {tag_3}}
merge(A, B) = {element: {tag_3}}  # Element resurrected!
```

The removed element comes back because causal information was lost.

### Strategy 1: Time-Based Expiry

Discard metadata older than a threshold (e.g., 90 days). Works when all replicas sync within that window.

```python
def gc_tombstones(cutoff, state):
    return {
        elem: tags for elem, tags in state.items()
        if any(tag_time(t) > cutoff for t in tags)
    }
```

**Pros**: Simple, no coordination. **Cons**: Unsafe if replicas offline longer than grace period. Zombie resurrection risk. Use for mobile apps with bounded offline time.

### Strategy 2: Coordinated Garbage Collection

Use distributed consensus to agree on what's safe to discard. Once all replicas acknowledge an update, its metadata can be removed.

```python
# When all known replicas have acked a tag, it's safe to remove
def safe_to_discard(tag, replica_acks):
    return all(tag in acks for acks in replica_acks.values())
```

**Pros**: Completely safe. **Cons**: Requires coordination (partially defeats CRDT's main benefit). Slow if some replicas rarely come online. Use with bounded, known replica sets.

### Strategy 3: Version Vectors for Causal Tracking

Track causal history explicitly. Metadata can be discarded once causally superseded at all known replicas.

```python
def can_discard_tag(tag_vv, replica_versions):
    return all(tag_vv happened_before rv for rv in replica_versions.values())
```

**Pros**: More precise than time-based, no coordination for happy path. **Cons**: O(replicas) overhead per operation. Complex implementation. Use in systems already using version vectors (Riak, Cassandra-style).

### Strategy 4: Bounded Structures with Fallback

Limit metadata size (e.g., max 1000 tags per element). When exceeded, discard oldest and accept potential anomalies (degrades to LWW semantics within the bound).

**Pros**: Guaranteed bounded space. **Cons**: Correctness sacrificed for space. May lose concurrent operations. Use in embedded systems or strict SLA environments.

### Strategy 5: Checkpoint and Rebase

Periodically snapshot state and discard history before that point. New replicas start from the snapshot. Replicas offline during checkpoint period must do full state sync.

**Pros**: Aggressive pruning, conceptually clean. **Cons**: Pre-checkpoint replicas lose incremental sync. Full state sync is expensive. Use in collaborative editing where most users are mostly online (Google Docs, Figma).

### Recommendation

For most applications, use a hybrid: time-based expiry with conservative grace period (90 days), track oldest unsynced replica timestamp, only discard metadata older than `min(grace_period, oldest_unsynced - safety_margin)`. Provide manual compact operations for administrators.

## Performance Comparison

| Type | Space | Add/Insert | Remove/Delete | Merge | Read/Query |
|------|-------|-----------|---------------|-------|------------|
| G-Counter | O(r) | O(1) | N/A | O(r) | O(r) |
| PN-Counter | O(r) | O(1) | O(1) | O(r) | O(r) |
| G-Set | O(e) | O(1) | N/A | O(e) | O(1) |
| 2P-Set | O(e) | O(1) | O(1) | O(e) | O(1) |
| LWW-Element-Set | O(e) | O(1) | O(1) | O(e) | O(1) |
| OR-Set | O(e×t) | O(1) | O(t) | O(e×t) | O(1) |
| LWW-Register | O(1) | O(1) | N/A | O(1) | O(1) |
| MV-Register | O(c) | O(1) | N/A | O(c) | O(c) |
| OR-Map | O(k×t) | O(1) | O(t) | O(k×t) | O(1) |
| RGA | O(n+d) | O(log n) | O(log n) | O(n+d) | O(n) |
| WOOT | O(n+d) | O(n²) worst | O(log n) | O(n+d) | O(n²) worst |
| Logoot/LSEQ | O(n×p) | O(log n) | O(log n) | O(n) | O(n log n) |

**Legend**: `r` = replicas, `e` = elements, `t` = tags per element, `k` = keys, `n` = visible elements, `d` = tombstones, `c` = concurrent writes, `p` = position identifier length.

**Key observations**:
- Counter CRDTs scale with replica count, not operation count
- Set CRDTs have constant-time operations; OR-Set's space grows with tags
- Sequence CRDTs suffer from tombstone accumulation; RGA typically faster than WOOT in practice
- Position-based sequences trade time complexity for avoiding parent pointers, but positions can grow pathologically
- Merge is often the bottleneck — delta CRDTs dramatically improve performance

## Causal Delivery and Version Vectors

CRDTs themselves don't enforce causal delivery. Operation-based CRDTs (CmRDTs) require it: if operation A happened-before B on one replica, B must not be delivered before A at any other replica. Without causal delivery, CmRDTs may behave incorrectly.

**Version vectors** track logical clocks per replica:

```python
# Version vector: dict[replica_id, counter]
def increment(my_id, vv):
    vv[my_id] = vv.get(my_id, 0) + 1

def happened_before(a, b):
    # a happened-before b if a ≤ b in all components and < in at least one
    return (all(a.get(k, 0) <= b.get(k, 0) for k in set(a) | set(b)) and
            any(a.get(k, 0) < b.get(k, 0) for k in set(a) | set(b)))

def concurrent(a, b):
    return not happened_before(a, b) and not happened_before(b, a)
```

State-based CRDTs (CvRDTs) are more tolerant — they work over unreliable gossip — but causal tracking still helps with garbage collection and optimization. Most production systems use some form of causal tracking regardless of CRDT type.
