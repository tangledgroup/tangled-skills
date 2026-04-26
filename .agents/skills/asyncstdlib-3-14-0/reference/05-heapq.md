# Heapq Library

The `asyncstdlib.heapq` module implements Python's `heapq` for async callables and iterables. Added in version 3.10.3.

This module does **not** re-implement functions to maintain a heap data structure (like `heappush`, `heappop`). Since Python's `heapq` relies on `(key, item)` pairs rather than an internal `key` function, the same interface works for async key functions:

```python
# With async key function, use (key, item) pairs
await heapq.heappush(heap, (await key_func(item), item))
```

## Iterator Merging

### merge

```python
async for :T in merge(*iterables: (async) iter T, key: (T) -> (await) Any = None, reverse: bool = False)
```

Merge all pre-sorted async iterables into a single sorted iterator. Operates lazily — at any moment only one item from each iterable is stored for comparison. This allows merging streams of pre-sorted items, such as timestamped records from multiple sources.

Equivalent to `sorted(chain(*iterables), key=key, reverse=reverse)` but memory-efficient. The `key` may be an async callable (defaults to identity). Default sort order is ascending; use `reverse=True` for descending. All iterables must be pre-sorted in the same order.

```python
# Merge multiple sorted streams
async for record in a.merge(stream_a, stream_b, stream_c, key=lambda r: r.timestamp):
    process(record)
```

## Iterator Selecting

### nlargest

```python
await nlargest(*iterables: (async) iter T, n: int, key: (T) -> (await) Any = None) -> [T, ...]
```

Return a sorted list of the `n` largest elements. Equivalent to `sorted(iterable, key=key, reverse=True)[:n]` but consumes lazily and discards eagerly. The `key` may be an async callable.

### nsmallest

```python
await nsmallest(*iterables: (async) iter T, n: int, key: (T) -> (await) Any = None) -> [T, ...]
```

Return a sorted list of the `n` smallest elements. Equivalent to `sorted(iterable, key=key)[:n]` but consumes lazily and discards eagerly. The `key` may be an async callable.
