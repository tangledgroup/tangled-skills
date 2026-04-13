# The Functools Library

The `asyncstdlib.functools` library implements Python's functools module for async functions and iterables.

## Iterator Reducing

### `await reduce(function, iterable, initial=None)`

Reduce an async iterable by cumulative application of an async function.

```python
import asyncstdlib as a

async def add(x, y):
    return x + y

# Basic reduce
result = await a.reduce(add, [1, 2, 3, 4])  # 10 (equivalent to (((1+2)+3)+4))

# With initial value
result = await a.reduce(add, [1, 2, 3, 4], initial=100)  # 110

# Without initial on empty iterable raises TypeError
try:
    await a.reduce(add, [])
except TypeError:
    print("Empty iterable requires initial value")

# With initial on empty iterable returns initial
result = await a.reduce(add, [], initial=0)  # 0
```

**How it works:** Applies `function` cumulatively from the beginning of the iterable, as if executing `await function(current, anext(iterable))` until exhausted.

**Raises:** `TypeError` if iterable is empty and `initial` is not given.

## Async Caches

The regular `functools.lru_cache()` and `functools.cached_property()` are not appropriate for async callables - they cache the coroutine object, not the awaited result. `asyncstdlib` provides async-aware versions.

**Important:** These work only with async callables (not async neutral). They also work with regular callables that return awaitables.

### Attribute Caches

#### `@cached_property(getter)` / `@cached_property(context_type)(getter)`

Transform an async method into a cached attribute.

```python
import asyncstdlib as a

class Resource:
    def __init__(self, url):
        self.url = url
    
    @a.cached_property
    async def data(self):
        print("Fetching data...")
        return await fetch_from_network(self.url)

resource = Resource("http://example.com")
print(await resource.data)  # Fetches and caches
print(await resource.data)  # Returns cached value instantly

# Clear the cache
del resource.data
print(await resource.data)  # Fetches again
```

**With lock for thread safety:**

```python
from asyncio import Lock, gather

class Resource:
    def __init__(self, url):
        self.url = url
    
    @a.cached_property(Lock)  # Prevents duplicate computation
    async def data(self):
        print("Fetching data...")
        await asyncio.sleep(1)  # Simulate network delay
        return await fetch_from_network(self.url)

resource = Resource("http://example.com")

# Without lock: both coroutines might call the getter
# With lock: only one calls the getter, others wait for cached result
results = await gather(resource.data, resource.data, resource.data)
print(len(set(results)))  # All same result, fetched once
```

**Version added:** `context_type` parameter added in version 3.12.5.

**Notes:**
- Instances must have a `__dict__` attribute that is a mutable mapping
- Unlike `property`, does not support `setter()` or `deleter()`
- If accessed by multiple tasks before cached value exists, getter may run multiple times (use lock to prevent)
- Cached value can be cleared using `del instance.attribute`

### Function Caches

#### `@lru_cache(maxsize=128, typed=False)`

LRU cache for async functions.

```python
import asyncstdlib as a

@a.lru_cache(maxsize=128)
async def expensive_computation(x, y):
    print(f"Computing for {x}, {y}")
    await asyncio.sleep(1)  # Simulate expensive operation
    return x * y

# First call - computes
result1 = await expensive_computation(2, 3)  # 6

# Second call with same args - returns cached result instantly
result2 = await expensive_computation(2, 3)  # 6 (cached)

# Different args - computes again
result3 = await expensive_computation(2, 4)  # 8

# Check cache statistics
print(expensive_computation.cache_info())
# CacheInfo(hits=1, misses=2, maxsize=128, currsize=2)

# Clear cache
expensive_computation.cache_clear()
```

**With typed=True:**

```python
@a.lru_cache(typed=True)
async def process(value):
    return value * 2

result1 = await process(1)    # Miss - computes for int
result2 = await process(1.0)  # Miss with typed=True (different type)
# Without typed=True, result2 would be a hit
```

**Cache info and clearing:**

```python
@a.lru_cache()
async def fetch_data(url):
    return await http_get(url)

# Check cache statistics
info = fetch_data.cache_info()
print(f"Hits: {info.hits}, Misses: {info.misses}")

# Clear cache
fetch_data.cache_clear()

# Check if specific key is cached
cached = fetch_data.cache_parameters()  # Returns cache config
```

**Parameters:**
- `maxsize`: Maximum number of items to cache (default 128, use `None` for unlimited)
- `typed`: If True, cache entries with different argument types are stored separately

## Comparison: functools vs asyncstdlib.functools

### cached_property

```python
from functools import cached_property as sync_cached_property
import asyncstdlib as a

class WrongExample:
    # WRONG - caches coroutine object, not result!
    @sync_cached_property
    async def data(self):
        return await fetch()
    
    # Each access creates new coroutine, never actually caches result

class CorrectExample:
    # CORRECT - caches actual awaited result
    @a.cached_property
    async def data(self):
        return await fetch()
    
    # First access computes and caches result
    # Subsequent accesses return cached value
```

### lru_cache

```python
from functools import lru_cache as sync_lru_cache
import asyncstdlib as a

class WrongExample:
    # WRONG - caches coroutine object
    @sync_lru_cache()
    async def compute(self, x):
        return await expensive(x)

class CorrectExample:
    # CORRECT - caches awaited result
    @a.lru_cache()
    async def compute(self, x):
        return await expensive(x)
```

## Usage Patterns

### Caching database queries

```python
import asyncstdlib as a

class DatabaseCache:
    def __init__(self, db):
        self.db = db
    
    @a.cached_property
    async def config(self):
        """Load config once, cache for lifetime"""
        return await self.db.fetch_row("SELECT * FROM config")
    
    @a.lru_cache(maxsize=100)
    async def get_user(self, user_id):
        """Cache recent user lookups"""
        return await self.db.fetch_row("SELECT * FROM users WHERE id = $1", user_id)
    
    def invalidate_user_cache(self):
        """Clear user cache when data changes"""
        self.get_user.cache_clear()
```

### Expensive computations

```python
import asyncstdlib as a

class ImageProcessor:
    @a.lru_cache(maxsize=50)
    async def process_image(self, image_path, filter_type):
        """Cache processed images by path and filter"""
        image = await load_image(image_path)
        return await apply_filter(image, filter_type)
    
    @a.cached_property
    async def color_palette(self):
        """Extract palette once per instance"""
        return await analyze_colors(self.main_image)
```

### API client caching

```python
import asyncstdlib as a

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    @a.cached_property
    async def api_key(self):
        """Fetch API key once"""
        return await self._fetch_credentials()
    
    @a.lru_cache(maxsize=200)
    async def get_resource(self, resource_id):
        """Cache API responses"""
        response = await http_get(f"{self.base_url}/{resource_id}")
        return response.json()
```

## Notes

- Both `lru_cache()` and `cached_property()` work with `async def` functions and regular functions returning awaitables
- They do NOT work with sync functions returning non-awaitable values
- Cache keys are based on argument values (must be hashable)
- For `cached_property`, the instance must have a mutable `__dict__`
- Use lock parameter in `cached_property` to prevent race conditions in concurrent access
