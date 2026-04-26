# Builtins Library

The `asyncstdlib.builtins` library implements Python's built-in functions for (async) functions and (async) iterables. All functions are also available directly from the `asyncstdlib` namespace.

## Iterator Reducing

### anext

Retrieve the next item from an async iterator. Raises `StopAsyncIteration` if exhausted and no default is set. This function is not async neutral — the iterator must be an asynchronous iterator (supporting `__anext__`).

```python
import asyncstdlib as a

async for val in a.iter(range(5)):
    first = await a.anext(val)       # get first item
    second = await a.anext(val, -1)  # get next with default
```

### all / any

Return `True` if all elements are truthy (`all`), or `False` if none are truthy (`any`). Both accept (async) iterables.

```python
import asyncstdlib as a

result = await a.all(a.iter([True, True, False]))  # False
result = await a.any(a.iter([False, False, True]))  # True
```

### max / min

Return the largest or smallest item from an (async) iterable. Support `key` (sync or async callable) and `default` arguments. The two-or-more-arguments variant is not supported — use the builtin `max()`/`min()` instead. Raises `ValueError` if iterable is empty and no default provided.

```python
import asyncstdlib as a

largest = await a.max(a.iter(fetch_data()), key=len)
smallest = await a.min(a.iter(fetch_data()), default=0)
```

### sum

Sum of `start` (default 0) and all elements in the (async) iterable.

```python
total = await a.sum(a.iter(fetch_numbers()), start=100)
```

## Iterator Transforming

### iter

Create an async iterator from any iterable. Accepts both sync and async iterables, always returning an async iterator. Supports sentinel form for (async) callables.

```python
import asyncstdlib as a

# From a sync iterable
async_iter = a.iter([1, 2, 3])

# From an async iterable
async_iter = a.iter(async_generator())

# Sentinel form — call until value equals sentinel
async_iter = a.iter(async_callable, None)
```

### filter

An async iterator of elements filtered by an (async) callable. Equivalent to `(element async for element in iterable if await func(element))`. Both function and iterable may be sync or async.

```python
async def is_positive(x):
    return x > 0

async for val in a.filter(is_positive, a.iter(fetch_numbers())):
    print(val)
```

### zip

Create an async iterator aggregating elements from each (async) iterable. Stops when the shortest iterable is exhausted. Supports `strict=True` to raise `ValueError` if iterables are not equal length. Multiple iterables may be mixed sync and async.

```python
import asyncstdlib as a

# Basic zip
async for name, val in a.zip(["a", "b"], fetch_items()):
    print(f"{name} => {val}")

# Strict mode — all iterables must be same length
async for a_val, b_val in a.zip(stream_a, stream_b, strict=True):
    ...
```

### map

An async iterator mapping an (async) function to items from (async) iterables. For `n` iterables, the function must take `n` positional arguments. Supports `strict=True`. Function may be sync or async; iterables may be mixed sync and async.

```python
import asyncstdlib as a

async def double(x):
    return x * 2

async for val in a.map(double, a.iter(fetch_numbers())):
    print(val)
```

### enumerate

An async iterator of `(index, element)` pairs from an (async) iterable. Count begins at `start` (default 0). Iterable may be sync or async.

```python
import asyncstdlib as a

async for idx, val in a.enumerate(fetch_items(), start=1):
    print(f"{idx}: {val}")
```

## Standard Types

### list / dict / set / tuple

Create standard collection types from (async) iterables. All return awaitable results.

```python
import asyncstdlib as a

items = await a.list(fetch_items())        # [1, 2, 3]
mapping = await a.dict(fetch_pairs())      # {"a": 1, "b": 2}
unique = await a.set(fetch_items())        # {1, 2, 3}
frozen = await a.tuple(fetch_items())      # (1, 2, 3)
```

### sorted

Sort items from an (async) iterable into a new list. Supports `key` (sync or async callable) and `reverse`. The actual sorting is synchronous — very large iterables may block the event loop. Guaranteed worst-case O(n log n). Added in version 3.9.0.

```python
import asyncstdlib as a

async def get_priority(item):
    return await fetch_priority(item)

items = await a.sorted(fetch_items(), key=get_priority, reverse=True)
```
