# Functools Library

The `asyncstdlib.functools` library implements Python's `functools` for (async) functions and (async) iterables.

## Iterator Reducing

### reduce

Reduce an (async) iterable by cumulative application of an (async) function. Applies `function(current, next_item)` from the beginning until exhausted. The output of `function` should be valid as its first input. Optional `initial` is prepended. If combination of initial and iterable contains exactly one item, it is returned without calling function. Raises `TypeError` if iterable is empty and no initial given.

```python
import asyncstdlib as a
import operator

# Running product of async numbers
result = await a.reduce(operator.mul, fetch_numbers(), initial=1)

# Custom async reduction
async def combine(acc, item):
    return acc + (await transform(item))

result = await a.reduce(combine, fetch_data())
```

## Async Caches

The regular `functools.lru_cache()` and `functools.cached_property()` are not appropriate for async callables — their direct return value is an awaitable, so the cache stores temporary helpers instead of actual values. asyncstdlib's versions work with async callables (not async neutral) and also support regular callables returning awaitables.

### Attribute Caches

#### cached_property

Transform an async method into a cached attribute. After first `await`, the value is stored on the instance. Subsequent `await` accesses return the cached value instantly. Use `del` to clear and force recomputation. Does not support `setter()` or `deleter()`. Added in version 1.1.0; `context_type` parameter added in 3.12.5.

```python
import asyncstdlib as a

class Resource:
    def __init__(self, url):
        self.url = url

    @a.cached_property
    async def data(self):
        return await fetch(self.url)

resource = Resource("http://example.com")
print(await resource.data)  # takes time...
print(await resource.data)  # instant (cached)
del resource.data
print(await resource.data)  # takes time again...
```

For thread safety when multiple tasks access before cache is populated, provide a lock type:

```python
from asyncio import Lock, gather

class Resource:
    def __init__(self, url):
        self.url = url

    @a.cached_property(Lock)
    async def data(self):
        return await fetch(self.url)

resource = Resource("http://example.com")
print(*(await gather(resource.data, resource.data)))  # fetched only once
```

Instances must have a `__dict__` attribute that is a mutable mapping.

### Callable Caches

#### cache

Simple unbounded cache (memoization) for async functions. Equivalent to `lru_cache(maxsize=None)`. Added in version 3.9.0.

```python
import asyncstdlib as a

@a.cache
async def expensive_query(key):
    return await db.lookup(key)
```

#### lru_cache

Least Recently Used cache for async functions. Stores call arguments and their *awaited* return value. Supports overlapping `await` calls (provided the wrapped function does too). Not thread-safe.

Parameters:
- `maxsize` — positive integer stores up to that many patterns; zero/negative disables caching; `None` means unlimited
- `typed` — if `True`, values are compared by value *and* type (`3` and `3.0` are distinct)

```python
import asyncstdlib as a

@a.lru_cache(maxsize=128)
async def fetch(url):
    return await http.get(url)

# Cache management
fetch.cache_clear()      # evict all entries
fetch.cache_discard("http://example.com")  # evict specific pattern
info = fetch.cache_info()  # hits, misses, maxsize, currsize
params = fetch.cache_parameters()  # {"maxsize": ..., "typed": ...}
```

Arguments must be hashable. When arguments are in cache, the underlying function is *not* called — side effects and event loop scheduling are skipped. Exceptions are not cached.

### LRUAsyncCallable Protocol

Cached async callables expose a protocol with:
- `__wrapped__` — the original callable
- `cache_clear()` — evict all entries
- `cache_discard(...)` — evict specific argument pattern
- `cache_info()` — returns NamedTuple with `hits`, `misses`, `maxsize`, `currsize`
- `cache_parameters()` — returns dict with cache configuration (added in 3.9.0)
