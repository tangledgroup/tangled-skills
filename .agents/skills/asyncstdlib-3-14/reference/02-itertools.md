# Itertools Library

The `asyncstdlib.itertools` library implements Python's `itertools` for (async) functions and (async) iterables. Only functions that benefit from explicit async implementation are provided. Other itertools functions can be turned asynchronous using `a.iter()`, e.g., `a.iter(itertools.count(5))`.

All utilities in this module explicitly close their iterable arguments when done. For non-exhausting utilities like `dropwhile`, use `scoped_iter()` to manage lifetime.

## Infinite Iterators

### cycle

An async iterator indefinitely iterating over an (async) iterable. Lazily exhausts the iterable on its first pass, then recalls items from an internal buffer on subsequent passes. If the iterable is empty, terminates immediately. Items are provided immediately as they become available on the first pass. Subsequent passes provide items directly without replicating delays. All items are stored internally — may consume significant memory.

```python
import asyncstdlib as a

async for color in a.cycle(["red", "green", "blue"]):
    print(color)  # red, green, blue, red, green, blue, ...
```

## Iterator Merging

### chain

An async iterator flattening values from all (async) iterables. Consecutively iterates over each iterable lazily. Assumes ownership and closes iterables when the chain is closed. Use `chain.from_iterable` to avoid closing unprocessed iterables.

```python
import asyncstdlib as a

# Chain multiple iterables
async for val in a.chain(stream_a, stream_b, stream_c):
    print(val)

# Lazy chaining from an iterable of iterables
async for val in a.chain.from_iterable(fetch_streams()):
    print(val)
```

### chain.from_iterable

Alternate constructor that lazily exhausts the outer iterable of iterables as well. Suitable for lazy or infinite sources. Closing only closes already-fetched inner iterables.

### zip_longest

Like `zip` but continues until the longest iterable is exhausted. Shorter iterables are padded with `fillvalue` (default `None`). Multiple iterables may be mixed sync and async.

```python
import asyncstdlib as a

async for pair in a.zip_longest([1, 2], ["a", "b", "c"], fillvalue="?"):
    print(pair)  # (1, "a"), (2, "b"), ("?", "c")
```

## Iterator Filtering

### compress

Yield items from `data` where the paired `selectors` value is truthy. Lazily iterates both data and selectors pairwise.

```python
import asyncstdlib as a

async for item in a.compress(data_stream, selector_stream):
    print(item)
```

### dropwhile

Yield items after `predicate(item)` is no longer true. Discards items while predicate is true, then yields all remaining items immediately without further predicate evaluation.

```python
import asyncstdlib as a

async for val in a.dropwhile(lambda x: x < 5, fetch_numbers()):
    print(val)  # starts from first value >= 5
```

### filterfalse

Yield items for which `predicate(item)` is false. If predicate is `None`, yield any items that are false.

```python
import asyncstdlib as a

async for val in a.filterfalse(lambda x: x % 2 == 0, fetch_numbers()):
    print(val)  # odd numbers only
```

### takewhile

Yield items as long as `predicate(item)` is true. Stops at first false — the failing item is discarded and unavailable from either source.

```python
import asyncstdlib as a

async for val in a.takewhile(lambda x: x < 100, fetch_numbers()):
    print(val)  # stops before first value >= 100
```

### islice

An async iterator over items from an (async) iterable in a slice. Accepts `stop`, or `start, stop[, step]` parameters as understood by `slice`. Lazy, asynchronous version of `iterable[start:stop:step]`.

```python
import asyncstdlib as a

# First 5 items
async for val in a.islice(fetch_items(), 5):
    print(val)

# Items 10-20, step 2
async for val in a.islice(fetch_items(), 10, 20, 2):
    print(val)
```

## Iterator Transforming

### accumulate

An async iterator on the running reduction of an (async) iterable. Yields the *running* value as each item is fetched. Default function is `operator.add` (running sum). Supports `initial` value and async reduction functions. Raises `TypeError` if iterable is empty and no initial given.

```python
import asyncstdlib as a
import operator

# Running sum (default)
async for total in a.accumulate(fetch_numbers()):
    print(total)

# Running product
async for prod in a.accumulate(fetch_numbers(), operator.mul, initial=1):
    print(prod)

# Custom async reduction
async def combine(a, b):
    return await merge_results(a, b)

async for result in a.accumulate(fetch_data(), combine):
    print(result)
```

### starmap

An async iterator applying a function to unpacked arguments from an iterable of tuples. Like `map` but with a single iterable of argument tuples instead of multiple iterables.

```python
import asyncstdlib as a

async def add(a, b):
    return a + b

async for result in a.starmap(add, fetch_pairs()):
    print(result)
```

## Iterator Splitting

### tee

Create `n` separate async iterators over an (async) iterable. Each provides the same items in the same order. All child iterators may advance separately but share items — when the most advanced iterator retrieves an item, it is buffered until all others yield it as well. Works lazily with infinite iterables if all iterators advance.

Returns a custom type (not a tuple) that supports indexing, iteration, unpacking, `aclose()`, and `async with` context for closing all children. Supports `lock` parameter for concurrency safety.

```python
import asyncstdlib as a

async def derivative(sensor_data):
    previous, current = a.tee(sensor_data, n=2)
    await a.anext(previous)  # advance one iterator
    return a.map(operator.sub, previous, current)

# Using as context manager
async with a.tee(fetch_items(), n=3) as t:
    first, second, third = t
```

### pairwise

Yield successive overlapping pairs `(a, b)` from an (async) iterable. No pair emitted for 0 or 1 items. Added in version 3.10.0.

```python
import asyncstdlib as a

async for a, b in a.pairwise(fetch_numbers()):
    print(f"{a} -> {b}")
```

### batched

Batch an (async) iterable into tuples of length `n`. Returns each batch as soon as ready. If `strict=True` and the last batch is smaller than `n`, raises `ValueError`. Added in version 3.11.0; `strict` parameter added in 3.13.0.

```python
import asyncstdlib as a

async for batch in a.batched(fetch_items(), n=10):
    process_batch(batch)

# Strict mode — all batches must be exactly size n
async for batch in a.batched(fetch_items(), n=10, strict=True):
    process_batch(batch)
```

### groupby

Create an async iterator over `(key, group_iterator)` pairs from consecutive groups. Groups are consecutive with respect to the original iterable — multiple groups may share the same key if separated by different keys. Supports async `key` function. The groupby iterator and its group iterators share the same underlying iterator — advancing groupby makes previous groups inaccessible. Not safe to concurrently advance both groupby and its groups.

```python
import asyncstdlib as a

async for key, group in a.groupby(sorted_items, key=lambda x: x.category):
    items = await a.list(group)
    print(f"Category {key}: {items}")
```
