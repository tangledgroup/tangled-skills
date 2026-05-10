---
name: aioitertools-0-13-0
description: Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python applications that need to process iterables with familiar itertools-style functions, work with both standard and async iterables interchangeably, or consume async data streams with functional patterns.
version: "0.1.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - asyncio
  - python
  - itertools
  - async-iterators
  - generators
  - async-streams
category: development
external_references:
  - https://github.com/omnilib/aioitertools
  - https://aioitertools.readthedocs.io/
---

# aioitertools 0.13.0

## Overview

aioitertools provides async-compatible versions of Python's `itertools`, `builtins`, and select `more_itertools` functions. It shadows the standard library API so you can use familiar function names with both regular iterables and async iterables — no `if/else` branching needed. Standard iterables are automatically wrapped in async generators, and all functions work with `await` and `async for`.

Requires Python 3.9+. Licensed under MIT by Amethyst Reese (Omnilib project).

## When to Use

- Processing async data streams with itertools-style operations (chain, islice, groupby, etc.)
- Mixing standard iterables and async iterables in the same pipeline without type checking
- Applying async coroutines as predicates or mapping functions over iterables
- Consuming multiple async generators concurrently (`as_completed`, `as_generated`)
- Building async ETL pipelines, data processors, or streaming applications

## Core Concepts

### Mixed Iterable Support

Every function accepts `AnyIterable[T]` — either a standard `Iterable[T]` or an `AsyncIterable[T]`. The library handles the conversion transparently via `aioitertools.iter()`, which wraps sync iterables in async generators.

```python
from aioitertools import chain

# Works with regular lists
async for v in chain([1, 2], [3, 4]):
    ...

# Works with async generators
async for v in chain(async_gen1(), async_gen2()):
    ...

# Mix and match freely
async for v in chain([1, 2], async_gen3()):
    ...
```

### Functions Accept Coroutines

Predicate and mapping functions can be regular callables or coroutines. The internal `maybe_await` helper checks if the result is awaitable and awaits it automatically.

```python
from aioitertools import takewhile

async def async_pred(x):
    return await some_check(x)

async for v in takewhile(async_pred, data_stream()):
    ...
```

### Module Shadowing

Import from `aioitertools` directly to shadow the builtins:

```python
from aioitertools import iter, next, map, zip
```

Or import specific itertools functions:

```python
from aioitertools import chain, islice, groupby
```

## Installation / Setup

Requires Python 3.9 or newer. Install from PyPI:

```bash
pip install aioitertools
```

No additional configuration needed. Import and use directly.

## Usage Examples

### Basic async iteration over a sync iterable

```python
from aioitertools import iter, next

async for value in iter(range(10)):
    print(value)

first = await next(iter([10, 20, 30]))
# first == 10
```

### Chaining multiple async generators

```python
from aioitertools import chain

async def gen1():
    yield 1
    yield 2

async def gen2():
    yield 3
    yield 4

async for v in chain(gen1(), gen2()):
    print(v)  # 1, 2, 3, 4
```

### Mapping an async function over data

```python
from aioitertools import map

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async for data in map(fetch, URL_LIST):
    process(data)
```

### Grouping with an async key function

```python
from aioitertools import groupby

async def category_key(item):
    return await db.lookup_category(item.id)

async for key, group in groupby(items(), key=category_key):
    print(f"Category {key}: {len(group)} items")
```

## Advanced Topics

**Builtins Reference**: Async versions of `all`, `any`, `enumerate`, `iter`, `list`, `map`, `max`, `min`, `next`, `set`, `sum`, `tuple`, `zip` → [Builtins](reference/01-builtins.md)

**Itertools Reference**: Full itertools module emulation — `accumulate`, `batched`, `chain`, `combinations`, `compress`, `count`, `cycle`, `dropwhile`, `filterfalse`, `groupby`, `islice`, `permutations`, `product`, `repeat`, `starmap`, `takewhile`, `tee`, `zip_longest` → [Itertools](reference/02-itertools.md)

**More Iterables & Asyncio**: Extended utilities — `take`, `chunked`, `before_and_after`, `as_completed`, `as_generated`, `gather`, `gather_iter` → [More Iterables & Asyncio](reference/03-more-itertools-and-asyncio.md)
