# More Iterables & Asyncio

Extended utilities from `aioitertools.more_itertools` and friendlier asyncio wrappers from `aioitertools.asyncio`.

## more_itertools

### take

```python
async def take(n: int, iterable: AnyIterable[T]) -> list[T]
```

Return the first `n` items as a list. Returns fewer if the iterable is shorter. `n` must be >= 0.

```python
first_two = await take(2, [1, 2, 3, 4, 5])
# [1, 2]
```

### chunked

```python
async def chunked(iterable: AnyIterable[T], n: int) -> AsyncIterable[list[T]]
```

Break iterable into chunks of length `n`. The last chunk may be shorter.

```python
async for chunk in chunked([1, 2, 3, 4, 5], n=2):
    ...  # [1, 2], [3, 4], [5]
```

### before_and_after

```python
async def before_and_after(predicate: Predicate[T], iterable: AnyIterable[T]) -> tuple[AsyncIterable[T], AsyncIterable[T]]
```

Split an iterator at the first item where the predicate becomes `False`. Returns two async iterables — items before and from the transition point onward.

**Note**: The first iterator must be fully consumed before the second produces valid results.

```python
it = iter('ABCdEfGhI')
all_upper, remainder = await before_and_after(str.isupper, it)

result1 = ''.join([char async for char in all_upper])
# 'ABC'

result2 = ''.join([char async for char in remainder])
# 'dEfGhI'
```

## asyncio

These are friendlier versions of standard `asyncio` functions, imported as `aioitertools.asyncio`.

### as_completed

```python
async def as_completed(aws: Iterable[Awaitable[T]], *, timeout: Optional[float] = None) -> AsyncIterator[T]
```

Run awaitables concurrently and yield results as they complete. Unlike `asyncio.as_completed`, this yields actual values (not Futures), so no per-item `await` is needed.

Cancels all remaining awaitables if a timeout is reached.

```python
futures = [fetch(url) for url in urls]

async for value in as_completed(futures):
    process(value)  # use immediately, no extra await

# With timeout
async for value in as_completed(futures, timeout=10.0):
    ...
```

### as_generated

```python
async def as_generated(iterables: Iterable[AsyncIterable[T]], *, return_exceptions: bool = False) -> AsyncIterable[T]
```

Yield results from multiple async iterables in the order they are produced. Creates a task per iterable and a shared queue for results.

If `return_exceptions=False` (default), any exception is raised immediately and pending tasks are cancelled. If `True`, exceptions are yielded as values.

```python
async def gen(x):
    for i in range(x):
        yield i

gen1 = gen(10)
gen2 = gen(12)

async for value in as_generated([gen1, gen2]):
    ...  # intermixed values from both generators
```

### gather

```python
async def gather(*args: Awaitable[T], return_exceptions: bool = False, limit: int = -1) -> list[Any]
```

Like `asyncio.gather` but with a concurrency `limit`. All results are buffered. Handles input duplicates — if the same awaitable appears multiple times, its result is placed at all corresponding positions.

If cancelled, all internally created pending tasks are also cancelled.

```python
futures = [some_coro(i) for i in range(10)]

# Run all concurrently (default)
results = await gather(*futures)

# Limit concurrency to 2 at a time
results = await gather(*futures, limit=2)
```

### gather_iter

```python
async def gather_iter(itr: AnyIterable[MaybeAwaitable[T]], return_exceptions: bool = False, limit: int = -1) -> list[T]
```

Wrapper around `gather` that accepts an iterable instead of `*args`. Values don't need to be awaitable — `maybe_await` handles both.

```python
mixed = [1, coro1(), 2, coro2()]
results = await gather_iter(mixed)
# [1, <result1>, 2, <result2>]
```
