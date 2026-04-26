# Asynctools Library

The `asyncstdlib.asynctools` library implements the core toolset used by asyncstdlib itself. All documented members are stable regardless of asyncstdlib internals. Added in version 1.1.0.

## Iterator Lifetime

### borrow

Borrow an async iterator, preventing `aclose()` on it. The original owner assures cleanup; the borrowed iterator does not allow closing the underlying iterator. Supports `asend()` and `athrow()` if the underlying iterator supports them (works with both `AsyncIterator` and `AsyncGenerator`). The `aclose()` method on the borrowed iterator only closes the wrapper, not the underlying iterator.

```python
import asyncstdlib as a

async def process(iterable):
    borrowed = a.borrow(async_iter)
    # Use borrowed — it won't close the original
    async for item in borrowed:
        yield item
    # Original owner still responsible for cleanup
```

### scoped_iter

Context manager providing an async iterator for an (async) iterable, guaranteed to `aclose()` at block end. The resulting iterator is automatically borrowed to prevent premature closing when passed around. Nested scoping of the same iterator is safe — inner scopes forfeit closing in favor of the outermost scope.

```python
from collections import deque
import asyncstdlib as a

async def head_tail(iterable, leading=5, trailing=5):
    """Provide the first `leading` and last `trailing` items."""
    async with a.scoped_iter(iterable) as async_iter:
        # Safely pass iterator without it being closed
        async for item in a.islice(async_iter, leading):
            yield item
        tail = deque(maxlen=trailing)
        async for item in async_iter:
            tail.append(item)
    for item in tail:
        yield item
```

## Async Transforming

### sync

Wrap a callable to ensure its result can be `await`ed. Useful for writing async-neutral functions or using sync functions where async ones are expected. Wrapping a `def` or `lambda` makes it behave as if defined with `async def`. Should never be the sole decorator on a function — use `async def` instead. Added in version 3.9.3.

```python
import asyncstdlib as a

def sync_func(x, y):
    return x + y

async def async_func(x):
    return x * 2

async def main():
    result = await a.sync(sync_func)(1, 2)     # wraps sync to async
    result = await a.sync(async_func)(8)       # passes through
    result = await a.sync(lambda x: x ** 3)(5) # wraps lambda
```

### any_iter

Provide an async iterator for various forms of "asynchronous iterable". Uniformly handles `AsyncIterator[T]`, `Awaitable[Iterator[T]]`, `Iterable[Awaitable[T]]`, and similar. Matches all forms of `async def` functions providing iterables. Must eagerly resolve each async layer — incurs performance penalty. Prefer `iter()` for simple cases with EAFP. Added in version 3.10.3.

```python
import random
import asyncstdlib as a

# AsyncIterator[T]
async def async_iter(n):
    for i in range(n):
        yield i

# Awaitable[Iterator[T]]
async def await_iter(n):
    return [*range(n)]

some_iter = random.choice([async_iter, await_iter, range])
async for item in a.any_iter(some_iter(4)):
    print(item)
```

### await_each

Convert an *iterable of awaitables* into an *async iterator* of awaited values. Allows applying `AsyncIterable[T]` functions to `Iterable[Awaitable[T]]`. Added in version 3.9.1.

```python
import asyncstdlib as a

async def check1() -> bool: ...
async def check2() -> bool: ...
async def check3() -> bool: ...

# Check all coroutines
okay = await a.all(a.await_each([check1(), check2(), check3()]))
```

### apply

Await all arguments and keyword arguments, then apply `func` on the resolved values. Useful for chaining operations on awaitables. Added in version 3.9.1.

```python
import asyncstdlib as a

async def compute_x() -> float: ...
async def compute_y() -> float: ...

result = await a.apply(
    lambda x, y: x ** y,
    compute_x(),
    compute_y()
)
```
