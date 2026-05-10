---
name: asyncstdlib-3-14-0
description: Python async standard library providing async versions of builtins, itertools, functools, contextlib, and heapq for asyncio, trio, and custom event loops. Use when building async Python applications that need iterator operations (zip, map, chain, groupby), async caching (lru_cache), async context managers, or safe iterator lifecycle management.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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

# asyncstdlib 3.14.0

## Overview

`asyncstdlib` re-implements functions and classes from the Python standard library to make them compatible with async callables, iterables, and context managers. It is fully agnostic to async event loops — it works seamlessly with `asyncio`, `trio`, and any custom async event loop.

The library mirrors the structure of the standard library, with submodules named after their stdlib counterparts:

- **`asyncstdlib.builtins`** — Async versions of built-in functions: `zip()`, `map()`, `sum()`, `list()`, `sorted()`, etc.
- **`asyncstdlib.functools`** — Async versions of `reduce()`, `lru_cache()`, and `cached_property()`.
- **`asyncstdlib.contextlib`** — Async versions of `contextmanager()`, `closing()`, `ExitStack`, and related tools.
- **`asyncstdlib.itertools`** — Async versions of `chain()`, `cycle()`, `accumulate()`, `groupby()`, `tee()`, etc.
- **`asyncstdlib.heapq`** — Async versions of `merge()`, `nlargest()`, and `nsmallest()`.
- **`asyncstdlib.asynctools`** — Core utilities: `scoped_iter()`, `borrow()`, `sync()`, `any_iter()`, `await_each()`, `apply()`.

All functions are also available directly from the top-level `asyncstdlib` namespace. For example, `asyncstdlib.enumerate` is a shortcut for `asyncstdlib.builtins.enumerate`.

## When to Use

- Processing async iterables with familiar stdlib patterns (`zip`, `map`, `filter`, `chain`, `groupby`)
- Reducing async iterables (`sum`, `all`, `any`, `max`, `min`, `reduce`)
- Collecting async iterables into standard types (`list`, `dict`, `set`, `tuple`)
- Caching async function results with `lru_cache` or `cached_property`
- Building async context managers with `contextmanager` or managing multiple contexts with `ExitStack`
- Merging pre-sorted async streams with `heapq.merge`
- Safely managing async iterator lifecycle with `scoped_iter` and `borrow`
- Writing async-neutral code that accepts both sync and async arguments

## Core Concepts

### Async Neutral Arguments

Many asyncstdlib functions are **async neutral** — they accept *both* regular (sync) and async arguments. Type annotations use parentheses to denote this: `(async) iter T` means the parameter can be either a sync or async iterable. Whether a callable is sync or async is determined by inspecting its return type at runtime.

However, all asyncstdlib functions consistently produce awaitables, async iterators, and async context managers as output. Only *arguments* may be async neutral.

### Async Iterator Cleanup

Cleanup of async iterables requires an active event loop (via `aclose()`). All asyncstdlib utilities that work on async iterators assume **sole ownership** of passed-in iterators and eagerly `aclose()` them when done. This provides a resource-safe default for the most common case of exhausting iterators.

Use `borrow()` to prevent automatic cleanup when passing an iterator to another function. Use `scoped_iter()` as a context manager to guarantee cleanup in custom code while providing a borrowed iterator for safe passing around.

### Event Loop Agnosticism

asyncstdlib does not depend on any specific event loop. It works with `asyncio`, `trio`, or any custom async framework that supports the standard async iteration and context manager protocols.

## Usage Examples

Basic async iteration with builtins:

```python
import asyncstdlib as a

async def main():
    # Async zip of sync and async iterables
    names = ["alice", "bob", "carol"]
    async def get_scores():
        for s in [95, 87, 92]:
            yield s

    async for name, score in a.zip(names, get_scores()):
        print(f"{name}: {score}")

    # Reduce an async iterable
    total = await a.sum(a.iter(range(100)))
    print(total)  # 4950
```

Async context manager with contextmanager:

```python
from asyncstdlib import contextmanager

@contextmanager
async def managed_resource():
    resource = await acquire_resource()
    try:
        yield resource
    finally:
        await release_resource(resource)
```

## Advanced Topics

**Builtins Library**: Async versions of `zip`, `map`, `filter`, `sum`, `all`, `any`, `list`, `dict`, `sorted` and more → [Builtins Library](reference/01-builtins.md)

**Functools Library**: Async `reduce`, `lru_cache`, `cached_property`, and `cache` for async callables → [Functools Library](reference/02-functools.md)

**Contextlib Library**: Async `contextmanager`, `closing`, `ExitStack`, `nullcontext`, and `ContextDecorator` → [Contextlib Library](reference/03-contextlib.md)

**Itertools Library**: Async `chain`, `cycle`, `accumulate`, `groupby`, `tee`, `islice`, `starmap`, `compress`, `dropwhile`, `takewhile`, and more → [Itertools Library](reference/04-itertools.md)

**Heapq Library**: Async `merge`, `nlargest`, `nsmallest` for async iterables with async key functions → [Heapq Library](reference/05-heapq.md)

**Asynctools Library**: Core utilities `scoped_iter`, `borrow`, `sync`, `any_iter`, `await_each`, `apply` → [Asynctools Library](reference/06-asynctools.md)

**Iterator Scoping Guide**: Understanding cleanup semantics, ownership, and safe iterator lifetime management → [Iterator Scoping Guide](reference/07-iter-scope.md)
