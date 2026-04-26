---
name: asyncstdlib-3-14
description: Python async standard library providing async versions of builtins, itertools, functools, contextlib, heapq, and core async tools for iterator operations with asyncio, trio, and any custom event loop. Use when building async Python applications that need iterator operations (zip, map, enumerate, chain, tee, groupby), async caching (lru_cache, cached_property), async context managers (contextmanager, ExitStack), or safe async iterator lifecycle management (scoped_iter, borrow).
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.14.0"
tags:
  - python
  - async
  - itertools
  - builtins
  - functools
  - contextlib
  - heapq
  - iterator
category: library
external_references:
  - https://github.com/maxfischer2781/asyncstdlib
  - https://asyncstdlib.readthedocs.io/
---

# asyncstdlib 3.14

## Overview

`asyncstdlib` re-implements functions and classes from the Python standard library to make them compatible with `async` callables, iterables, and context managers. It is fully agnostic to async event loops — it works seamlessly with `asyncio`, `trio`, and any custom async event loop.

The library provides:

- Async versions of advantageous builtins (`zip`, `map`, `enumerate`, `sum`, `all`, `any`, `min`, `max`, `list`, `dict`, `set`, `tuple`, `sorted`)
- Async itertools (`chain`, `cycle`, `accumulate`, `tee`, `groupby`, `islice`, `batched`, `pairwise`, `compress`, `takewhile`, `dropwhile`, `filterfalse`, `starmap`, `zip_longest`)
- Async functools (`reduce`, `lru_cache`, `cache`, `cached_property`)
- Async contextlib (`contextmanager`, `closing`, `nullcontext`, `ExitStack`, `ContextDecorator`)
- Async heapq (`merge`, `nlargest`, `nsmallest`)
- Core async tools (`scoped_iter`, `borrow`, `sync`, `any_iter`, `await_each`, `apply`)

All functions are available both from their submodule (e.g., `asyncstdlib.builtins.zip`) and directly from the top-level namespace (e.g., `asyncstdlib.zip`).

## When to Use

- Converting sync iterator patterns (`for x in zip(a, b)`) to async (`async for x in azip(a, b)`)
- Processing async iterables with familiar itertools-style operations
- Caching async function results with `lru_cache` or `cached_property`
- Creating async context managers from async generator functions
- Managing async iterator lifecycle safely with `scoped_iter` and `borrow`
- Merging pre-sorted async streams with `heapq.merge`
- Building async-neutral utilities that accept both sync and async arguments

## Core Concepts

### Async Neutral Arguments

Many asyncstdlib functions are **async neutral** — they accept both regular (sync) and async arguments. For example, `asyncstdlib.zip()` can handle a mix of sync lists and async iterators. Type annotations use parentheses to denote this: `(async) iter T` means the argument may be either a regular or async iterable.

Whether a callable is sync or async is determined by inspecting its return type at runtime. The result must consistently be either regular or async — mixing both in the same call is not supported.

### Async Iterator Cleanup

All asyncstdlib utilities that work on async iterators eagerly `aclose()` them when done. This provides resource-safe defaults for the most common operation of exhausting iterators. To prevent automatic cleanup, use `borrow()`. To guarantee cleanup in custom code, use `scoped_iter()`.

### Namespace Flattening

For convenience, all functions and classes are exposed both from their submodule and directly at the top-level `asyncstdlib` namespace:

```python
import asyncstdlib as a

# These are equivalent:
a.builtins.zip(async_iter_a, async_iter_b)
a.zip(async_iter_a, async_iter_b)
```

## Usage Examples

### Basic async iteration with builtins

```python
import asyncstdlib as a
import asyncio

async def fetch_items():
    for i in range(5):
        await asyncio.sleep(0.1)
        yield i * 10

async def main():
    # Async enumerate
    async for idx, val in a.enumerate(fetch_items(), start=1):
        print(f"{idx}: {val}")

    # Async zip of mixed sync/async iterables
    async for name, val in a.zip(["a", "b", "c"], fetch_items()):
        print(f"{name} => {val}")

    # Async list/dict/set construction
    items = await a.list(fetch_items())
    total = await a.sum(fetch_items(), start=100)
    result = await a.all(fetch_items())

asyncio.run(main())
```

### Async itertools patterns

```python
import asyncstdlib as a
import asyncio

async def number_stream(n):
    for i in range(n):
        await asyncio.sleep(0.01)
        yield i

async def main():
    # Chain multiple async iterables
    async for val in a.chain(number_stream(3), number_stream(3)):
        print(val)

    # Batch items
    async for batch in a.batched(number_stream(7), n=3):
        print(batch)  # (0,1,2), (3,4,5), (6,)

    # Tee — split one iterator into two
    async with a.tee(number_stream(5), n=2) as t:
        first, second = t
        async for v in first:
            print(f"first: {v}")
        async for v in second:
            print(f"second: {v}")

asyncio.run(main())
```

### Async caching

```python
import asyncstdlib as a
import asyncio

@a.lru_cache(maxsize=64)
async def fetch_data(url):
    await asyncio.sleep(1)  # simulate network
    return f"data from {url}"

async def main():
    result1 = await fetch_data("http://example.com")  # takes ~1s
    result2 = await fetch_data("http://example.com")  # instant (cached)
    print(fetch_data.cache_info())

asyncio.run(main())
```

## Advanced Topics

**Builtins Library**: Async versions of `zip`, `map`, `enumerate`, `sum`, `all`, `any`, `min`, `max`, `list`, `dict`, `set`, `tuple`, `sorted`, `filter`, `iter`, `anext` → See [Builtins Library](reference/01-builtins.md)

**Itertools Library**: Async versions of `chain`, `cycle`, `accumulate`, `tee`, `groupby`, `islice`, `batched`, `pairwise`, `compress`, `takewhile`, `dropwhile`, `filterfalse`, `starmap`, `zip_longest` → See [Itertools Library](reference/02-itertools.md)

**Functools Library**: Async `reduce`, `lru_cache`, `cache`, `cached_property` with LRU cache management → See [Functools Library](reference/03-functools.md)

**Contextlib Library**: Async `contextmanager`, `closing`, `nullcontext`, `ExitStack`, `ContextDecorator`, `AbstractContextManager` → See [Contextlib Library](reference/04-contextlib.md)

**Heapq Library**: Async `merge`, `nlargest`, `nsmallest` for sorted async streams → See [Heapq Library](reference/05-heapq.md)

**Asynctools Library**: Core tools `scoped_iter`, `borrow`, `sync`, `any_iter`, `await_each`, `apply` → See [Asynctools Library](reference/06-asynctools.md)

**Iterator Scoping**: Managing async iterator lifecycle, cleanup semantics, and borrowing patterns → See [Iterator Scoping](reference/07-iterator-scoping.md)
