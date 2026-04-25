---
name: asyncstdlib-3-14
description: Python async standard library providing async versions of builtins, itertools, functools, contextlib, and asynctools for use with asyncio, trio, and any async event loop. Use when building async applications requiring iterator operations, caching, context management, or safe async iteration patterns.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - async
  - asyncio
  - itertools
  - functools
  - contextlib
  - python
  - iterators
category: development
required_environment_variables: []

external_references:
  - https://github.com/aio-libs/asyncstdlib
  - https://asyncstdlib.readthedocs.io/
---
## Overview
Python async standard library providing async versions of builtins, itertools, functools, contextlib, and asynctools for use with asyncio, trio, and any async event loop. Use when building async applications requiring iterator operations, caching, context management, or safe async iteration patterns.

## When to Use
- Building async applications requiring iterator operations (filtering, mapping, zipping)
- Needing async-safe caching decorators (`@lru_cache`, `@cached_property`) for coroutine functions
- Working with async context managers and needing `ExitStack`, `contextmanager`, or `closing`
- Requiring safe async iteration patterns with proper cleanup (`scoped_iter`, `borrow`)
- Converting sync standard library patterns to async equivalents
- Needing async versions of `itertools` functions like `accumulate`, `chain`, `groupby`, `tee`

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

Python async standard library providing async versions of builtins, itertools, functools, contextlib, and asynctools for use with asyncio, trio, and any async event loop. Use when building async applications requiring iterator operations, caching, context management, or safe async iteration patterns.

The `asyncstdlib` library re-implements functions and classes of the Python standard library to make them compatible with `async` callables, iterables, and context managers. It is fully agnostic to `async` event loops and seamlessly works with `asyncio`, third-party libraries such as `trio`, as well as any custom `async` event loop.

**Key features:**
- Full set of async versions of standard library helpers: `zip`, `map`, `enumerate`, `functools.reduce`, `itertools.tee`, `itertools.groupby`, and many others
- Safe handling of async iterators to ensure prompt cleanup
- Small but powerful toolset to seamlessly integrate existing sync code into async programs
- No dependencies - pure Python implementation

## Installation / Setup
Install via pip:

```bash
pip install asyncstdlib==3.14.0
```

Or via conda:

```bash
conda install -c conda-forge asyncstdlib
```

**Python version:** Requires Python 3.8+ (supports up to 3.14)

## Usage Examples
```python
import asyncstdlib as a
import asyncio

async def main():
    # Async enumerate
    async for idx, item in a.enumerate(["a", "b", "c"]):
        print(idx, item)  # 0 a, 1 b, 2 c
    
    # Async zip (stops at shortest iterable)
    async for pair in a.zip([1, 2, 3], ["a", "b"]):
        print(pair)  # (1, 'a'), (2, 'b')
    
    # Async map with async function
    async def square(x):
        return x * x
    
    async for result in a.map(square, [1, 2, 3, 4]):
        print(result)  # 1, 4, 9, 16

asyncio.run(main())
```

## Common Operations
### Async Builtins

See [Builtins Reference](reference/01-builtins.md) for complete documentation.

**Async iteration helpers:**

```python
import asyncstdlib as a

# Convert any iterable to async iterator
async for item in a.iter([1, 2, 3]):
    print(item)

# Async filter with async predicate
async def is_even(x):
    return x % 2 == 0

async for even in a.filter(is_even, [1, 2, 3, 4, 5, 6]):
    print(even)  # 2, 4, 6

# Async zip with strict mode (enforces equal length)
try:
    async for pair in a.zip([1, 2], [3, 4, 5], strict=True):
        print(pair)
except ValueError as e:
    print(f"Iterables not equal length: {e}")

# Async reduce
async def add(x, y):
    return x + y

result = await a.reduce(add, [1, 2, 3, 4])  # 10
result = await a.reduce(add, [1, 2, 3, 4], initial=100)  # 110
```

### Async Caching

See [Functools Reference](reference/02-functools.md) for complete documentation.

**Async cached_property:**

```python
import asyncstdlib as a
from asyncio import Lock

class Resource:
    def __init__(self, url):
        self.url = url
    
    @a.cached_property
    async def data(self):
        # Expensive operation, cached after first access
        return await fetch_data(self.url)

# With lock to prevent duplicate computation in concurrent access
class SafeResource:
    def __init__(self, url):
        self.url = url
    
    @a.cached_property(Lock)  # Lock ensures single computation
    async def data(self):
        return await fetch_data(self.url)
```

**Clear cached value:**

```python
resource = Resource("http://example.com")
await resource.data  # Computes and caches
del resource.data    # Clears cache
await resource.data  # Recomputes
```

### Async Context Managers

See [Contextlib Reference](reference/03-contextlib.md) for complete documentation.

**Async contextmanager decorator:**

```python
from asyncstdlib.contextlib import contextmanager

@contextmanager
async def transaction(db):
    await db.begin()
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise

async with transaction(database) as db:
    await db.execute("INSERT ...")
```

**Safe iterator cleanup:**

```python
import asyncstdlib as a

# Ensure async iterator is properly closed
async with a.closing(a.iter(large_dataset)) as async_iter:
    async for item in async_iter:
        process(item)

# Null context manager (no-op placeholder)
context = a.nullcontext(existing_resource) if has_resource else a.closing(acquire_resource())
async with context as resource:
    use(resource)
```

**ExitStack for dynamic context management:**

```python
from asyncstdlib.contextlib import ExitStack

async with ExitStack() as stack:
    # Enter multiple contexts programmatically
    conn1 = await stack.enter_context(connect_db("db1"))
    conn2 = await stack.enter_context(connect_db("db2"))
    
    # Register cleanup callbacks
    stack.push(async def cleanup(): await flush_buffers())
    
    # All contexts and callbacks executed on exit
```

### Async Itertools

See [Itertools Reference](reference/04-itertools.md) for complete documentation.

**Iterator splitting:**

```python
import asyncstdlib as a

# Tee: split one iterator into multiple
sensor_data = get_sensor_stream()
previous, current = a.tee(sensor_data, n=2)
await a.anext(previous)  # Advance one iterator
derivative = a.map(operator.sub, previous, current)

# Pairwise: overlapping pairs
async for (a_val, b_val) in a.pairwise([1, 2, 3, 4]):
    print(a_val, b_val)  # (1,2), (2,3), (3,4)

# Groupby: group consecutive items with same key
async for key, group_iter in a.groupby(stream, key=lambda x: x.category):
    group_items = await a.list(group_iter)
    process_group(key, group_items)
```

**Iterator merging:**

```python
import asyncstdlib as a

# Chain: concatenate multiple iterables
combined = a.chain(stream1, stream2, stream3)

# Zip longest: like zip but fills missing values
async for pair in a.zip_longest([1, 2], ["a", "b", "c"], fillvalue=None):
    print(pair)  # (1,'a'), (2,'b'), (None,'c')
```

### Safe Iterator Handling

See [Asynctools Reference](reference/05-asynctools.md) for complete documentation.

**Scoped iteration with automatic cleanup:**

```python
import asyncstdlib as a
from collections import deque

async def head_tail(iterable, leading=5, trailing=5):
    """Provide the first and last items from an iterable"""
    async with a.scoped_iter(iterable) as async_iter:
        # Iterator is borrowed - won't be closed prematurely
        for item in a.islice(async_iter, leading):
            yield item
        
        tail = deque(maxlen=trailing)
        for item in async_iter:  # Continue from where we left off
            tail.append(item)
    
    for item in tail:
        yield item
```

**Borrowing iterators:**

```python
import asyncstdlib as a

async def process_stream(stream):
    # Borrow prevents aclose() from closing underlying iterator
    borrowed = a.borrow(stream)
    
    # Pass borrowed to multiple consumers safely
    await consumer1(borrowed)
    await consumer2(borrowed)
    
    # Original owner is responsible for cleanup

async def consumer(iterator):
    async for item in iterator:
        process(item)
```

## Advanced Topics
## Advanced Topics

- [Builtins](reference/01-builtins.md)
- [Functools](reference/02-functools.md)
- [Contextlib](reference/03-contextlib.md)
- [Itertools](reference/04-itertools.md)
- [Asynctools](reference/05-asynctools.md)

## Troubleshooting
**Cached property not working with async functions:**

Ensure you're using `asyncstdlib.cached_property`, not `functools.cached_property`. The standard library version caches the coroutine object, not the result.

```python
# WRONG - caches coroutine, not result
from functools import cached_property

# CORRECT - caches actual awaited result
import asyncstdlib as a

class MyClass:
    @a.cached_property
    async def expensive(self):
        return await compute()
```

**Iterator not being closed:**

Use `scoped_iter` or `closing` to ensure proper cleanup:

```python
# WRONG - iterator may not be closed on early exit
async for item in a.iter(large_dataset):
    if should_stop():
        break  # Iterator not closed!

# CORRECT - always closed
async with a.scoped_iter(large_dataset) as async_iter:
    async for item in async_iter:
        if should_stop():
            break  # Iterator closed on exit
```

**Concurrent access to cached_property:**

Use a lock type parameter to prevent duplicate computation:

```python
from asyncio import Lock

class Resource:
    @a.cached_property(Lock)  # Ensures single computation
    async def data(self):
        return await fetch()
```

**Zip/map with different length iterables:**

Use `strict=False` to allow different lengths (stops at shortest), or handle the mismatch:

```python
# Default strict=True raises ValueError if lengths differ
async for pair in a.zip(iter1, iter2, strict=False):
    process(pair)

# Or use zip_longest with fillvalue
async for pair in a.zip_longest(iter1, iter2, fillvalue=None):
    process(pair)
```

**Version compatibility:**

- Python 3.8+ required
- Version 3.14.0 adds `strict` parameter to `map()` and `batched()`
- Version 3.13.2 changes `accumulate(initial=None)` behavior
- Version 3.12.5 adds lock support to `cached_property`
- Version 3.12.2 makes `contextmanager` return a `ContextDecorator`

