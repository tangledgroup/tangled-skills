# Heapq Library

The `asyncstdlib.heapq` library implements Python's `heapq` for (async) functions and (async) iterables. Added in version 3.10.3.

This module does not re-implement heap maintenance functions (`heappush`, `heappop`, etc.). Since Python's `heapq` relies on `(key, item)` pairs for custom ordering, the same interface works with async key functions:

```python
import heapq

# With async key function
key_val = await key_func(item)
heapq.heappush(heap, (key_val, item))
```

## Iterator Merging

### merge

Merge all pre-sorted (async) iterables into a single sorted iterator. Operates lazily — at any moment only one item per iterable is stored for comparison. Allows merging streams of pre-sorted items such as timestamped records from multiple sources. Supports `key` (sync or async callable, default `None` for identity) and `reverse` parameters. Iterables must be pre-sorted in the same order.

```python
import asyncstdlib as a

# Merge multiple sorted streams
async for val in a.merge(sorted_stream_a, sorted_stream_b, sorted_stream_c):
    print(val)

# With async key function
async def get_timestamp(record):
    return await record.fetch_timestamp()

async for record in a.merge(stream_a, stream_b, key=get_timestamp):
    print(record)

# Descending order
async for val in a.merge(stream_a, stream_b, reverse=True):
    print(val)
```

## Iterator Selecting

### nlargest

Return a sorted list of the `n` largest elements from the (async) iterable(s). Supports async `key` function. Consumes iterable lazily and discards items eagerly — equivalent to `sorted(iterable, key=key, reverse=True)[:n]` but more memory-efficient for large inputs.

```python
import asyncstdlib as a

top5 = await a.nlargest(fetch_scores(), n=5)
top3 = await a.nlargest(fetch_items(), n=3, key=lambda x: x.priority)
```

### nsmallest

Return a sorted list of the `n` smallest elements. Reverse of `nlargest`. Same parameters and behavior.

```python
import asyncstdlib as a

bottom5 = await a.nsmallest(fetch_scores(), n=5)
```
