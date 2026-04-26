# Functools Library

The `asyncstdlib.functools` module implements Python's `functools` for async callables. Both `lru_cache()` and `cached_property()` work only with async callables (they are not async neutral). They also work with regular callables that return an awaitable, such as an `async def` function wrapped by `partial()`.

## Iterator Reducing

### reduce

```python
await reduce(function: (T, T) -> (await) T, iterable: (async) iter T, initial: T) -> T
```

Reduce an async iterable by cumulative application of an `(async)` function. Applies `function` from the beginning of `iterable`, as if executing `await function(current, await anext(iterable))` until exhausted. The optional `initial` is prepended to all items. If `initial` and `iterable` together contain exactly one item, it is returned without calling `function`. Raises `TypeError` if iterable is empty and no `initial` is given.

```python
async def multiply(a, b):
    return a * b

product = await a.reduce(multiply, async_data(), initial=1)
```

## Async Caches

The regular `functools.lru_cache()` and `functools.cached_property()` are not appropriate for async callables because their direct return value is an awaitable, causing the cache to store temporary helpers instead of actual values.

### Attribute Caches: cached_property

```python
@cached_property(getter: (Self) -> await T, /) -> await T
@cached_property(context_type: Type[AsyncContextManager], /)((Self) -> await T) -> await T
```

Transform an async method into a cached attribute. The value is computed once on first `await` and cached on the instance. Clear with `del`. Added in version 1.1.0.

```python
import asyncstdlib as a

class Resource:
    def __init__(self, url):
        self.url = url

    @a.cached_property
    async def data(self):
        return await http.get(self.url)

resource = Resource("http://example.com")
print(await resource.data)  # fetches
print(await resource.data)  # instant (cached)
del resource.data           # clear cache
print(await resource.data)  # fetches again
```

If the attribute is accessed by multiple concurrent tasks before a cached value is produced, the getter may run more than once. To enforce single execution, provide a lock type:

```python
from asyncio import Lock, gather

class Resource:
    @a.cached_property(Lock)
    async def data(self):
        return await http.get(self.url)
```

Instances must have a `__dict__` that is a mutable mapping. Added in version 3.12.5: the `context_type` decorator parameter.

### Callable Caches: lru_cache / cache

#### cache

```python
@cache((...) -> await R) -> LRUAsyncCallable
```

Simple unbounded memoization for async functions. Equivalent to `lru_cache()` with `maxsize=None`. Added in version 3.9.0.

#### lru_cache

```python
@lru_cache((...) -> await R) -> LRUAsyncCallable
@lru_cache(maxsize: int = 128, typed: bool = False)((...) -> await R) -> LRUAsyncCallable
```

Least Recently Used cache for async functions. Stores call arguments and their awaited return value. Arguments must be hashable. Exceptions are not cached — making it suitable for queries that may fail.

- `maxsize` as a positive integer: up to that many patterns stored, oldest evicted on overflow
- `maxsize` as zero or negative: cache disabled, every call forwarded
- `maxsize=None`: unlimited size, patterns never auto-evicted
- `typed=True`: values compared by value and type (`3` vs `3.0` are distinct)

Unlike `functools.lru_cache()`, this is not thread-safe. Supports overlapping await calls if the wrapped function does as well.

```python
import asyncstdlib as a

@a.lru_cache(maxsize=256)
async def fetch_user(user_id: int):
    return await db.query("SELECT * FROM users WHERE id = ?", user_id)

# Cache metadata
info = fetch_user.cache_info()
print(info.hits, info.misses, info.currsize, info.maxsize)
fetch_user.cache_clear()
fetch_user.cache_discard(some_user_id)
params = fetch_user.cache_parameters()
```

#### LRUAsyncCallable Protocol

Cached async callables expose:

- `__wrapped__` — The original callable
- `cache_clear()` — Evict all entries
- `cache_discard(...)` — Evict a specific argument pattern (added 3.10.4)
- `cache_info()` — NamedTuple with `hits`, `misses`, `maxsize`, `currsize`
- `cache_parameters()` — Dict with `"maxsize"` and `"typed"` keys (added 3.9.0)
