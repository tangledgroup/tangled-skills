# Asynctools Library

The `asyncstdlib.asynctools` module implements the core toolset used by asyncstdlib itself. All documented members are stable regardless of asyncstdlib internals. Added in version 1.1.0.

## Iterator Lifetime

### borrow

```python
borrow(iterator: async iter T) -> async iter T
```

Borrow an async iterator, preventing `aclose()` on the underlying iterator. The original owner guarantees to close the iterator; the borrowed iterator does not allow closing it. Supports `asend()` and `athrow()` if the underlying iterator supports them (works with both `AsyncIterator` and `AsyncGenerator`). Calling `aclose()` on the borrowed iterator closes only the wrapper, not the underlying iterator.

```python
import asyncstdlib as a

async def process(data):
    it = a.filter(predicate, data)
    # Pass to another function without it being closed
    result = await some_function(a.borrow(it))
    # Continue using `it` safely
    remaining = await a.list(it)
```

### scoped_iter

```python
async with scoped_iter(iterable: (async) iter T) as :async iter T
```

Context manager providing an async iterator for an `(async)` iterable. Roughly equivalent to combining `iter()` with `closing`. The resulting iterator is automatically **borrowed** to prevent premature closing when passing it around.

```python
from collections import deque
import asyncstdlib as a

async def head_tail(iterable, leading=5, trailing=5):
    """Provide the first `leading` and last `trailing` items."""
    # Create async iterator valid for the entire block
    async with a.scoped_iter(iterable) as async_iter:
        # Safely pass it on without it being closed
        async for item in a.islice(async_iter, leading):
            yield item
        tail = deque(maxlen=trailing)
        # Use it again in the block
        async for item in async_iter:
            tail.append(item)
    for item in tail:
        yield item
```

Nested scoping of the same iterator is safe — inner scopes automatically forfeit closing in favor of the outermost scope. This allows passing the scoped iterator to other functions that use `scoped_iter()`.

## Async Transforming

### sync

```python
sync(function: (...) -> (await) T) -> (...) -> await T
```

Wrap a callable to ensure its result can be `await`ed. Useful for writing async-neutral functions by wrapping callable arguments, or using synchronous functions where asynchronous ones are expected. Wrapping a regular `def` function makes it behave roughly as if defined with `async def`.

```python
import asyncstdlib as a

def sync_func(x, y):
    return x + y

async def main():
    result = await a.sync(sync_func)(x=1, y=2)
    # Also works with lambdas
    result2 = await a.sync(lambda x: x ** 3)(x=5)
```

Do not apply as the sole decorator on a function — define it as `async def` instead. Added in version 3.9.3.

### any_iter

```python
async for :T in any_iter(iter: (await) (async) iter (await) T)
```

Provide an async iterator for various forms of "asynchronous iterable". Uniformly handles async iterables, awaitable iterables, iterables of awaitables, and similar. Matches all forms of `async def` functions providing iterables.

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

This eagerly resolves each "async layer" before checking the next — incurs performance penalty. Prefer `iter()` with EAFP when only simple iterables need handling. Added in version 3.10.3.

### await_each

```python
async for :T in await_each(awaitables: iter await T)
```

Iterate through awaitables and await each item. Converts an iterable of async into an async iterator of awaited values.

```python
import asyncstdlib as a

async def check1() -> bool: ...
async def check2() -> bool: ...
async def check3() -> bool: ...

okay = await a.all(a.await_each([check1(), check2(), check3()]))
```

Added in version 3.9.1.

### apply

```python
await apply(func: (*T, **T) -> R, *args: await T, **kwargs: await T) -> R
```

Await all arguments and keyword arguments, then apply `func`. Useful for chaining operations on awaitables where you need to pass around the final awaitable.

```python
async def compute_something() -> float: ...
async def compute_something_else() -> float: ...

result = await a.apply(
    lambda x, y: x ** y,
    compute_something(),
    compute_something_else()
)
```

Added in version 3.9.1.
