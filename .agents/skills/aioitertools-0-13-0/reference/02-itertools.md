# Itertools

Async-compatible version of the `itertools` standard library. All functions accept mixed iterables (sync or async) and return async generators. Predicate, key, and accumulation functions can be sync callables or coroutines.

## accumulate

```python
async def accumulate(itr: AnyIterable[T], func: Accumulator[T] = operator.add) -> AsyncIterator[T]
```

Yield running accumulation with a binary operator. The function defaults to `operator.add` (running sum). Accepts both sync and async functions.

```python
data = [1, 2, 3, 4]

# Running sum (default)
async for total in accumulate(data):
    ...  # 1, 3, 6, 10

# Running product
async def mul(a, b):
    return a * b

async for total in accumulate(data, func=mul):
    ...  # 1, 2, 6, 24
```

## batched

```python
async def batched(iterable: AnyIterable[T], n: int, *, strict: bool = False) -> AsyncIterator[tuple[T, ...]]
```

Yield batches of `n` values. The final batch may be shorter unless `strict=True`, which raises `ValueError` on incomplete batches.

```python
async for batch in batched(range(15), 5):
    ...  # (0,1,2,3,4), (5,6,7,8,9), (10,11,12,13,14)
```

## chain

```python
chain(*itrs: AnyIterable[T]) -> AsyncIterator[T]
chain.from_iterable(itrs: AnyIterableIterable[T]) -> AsyncIterator[T]
```

Yield values from one or more iterables in series. Consumes each iterable lazily in full before moving to the next.

`chain()` is implemented as a callable class instance — call it directly with multiple iterables, or use `chain.from_iterable()` with an iterable of iterables.

```python
# Multiple arguments
async for v in chain([1, 2, 3], [7, 8, 9]):
    ...  # 1, 2, 3, 7, 8, 9

# From iterable of iterables
async for v in chain.from_iterable([[1, 2], [3, 4]]):
    ...
```

## combinations

```python
async def combinations(itr: AnyIterable[T], r: int) -> AsyncIterator[tuple[T, ...]]
```

Yield `r`-length subsequences. Consumes the entire iterable before yielding. Wraps `itertools.combinations`.

```python
async for value in combinations(range(4), 3):
    ...  # (0,1,2), (0,1,3), (0,2,3), (1,2,3)
```

## combinations_with_replacement

```python
async def combinations_with_replacement(itr: AnyIterable[T], r: int) -> AsyncIterator[tuple[T, ...]]
```

Yield `r`-length subsequences with replacement. Consumes the entire iterable before yielding.

```python
async for value in combinations_with_replacement("ABC", 2):
    ...  # ("A","A"), ("A","B"), ("A","C"), ("B","B"), ...
```

## compress

```python
async def compress(itr: AnyIterable[T], selectors: AnyIterable[Any]) -> AsyncIterator[T]
```

Yield elements only when the corresponding selector is truthy. Stops when either iterable is exhausted.

```python
async for value in compress(range(5), [1, 0, 0, 1, 1]):
    ...  # 0, 3, 4
```

## count

```python
async def count(start: N = 0, step: N = 1) -> AsyncIterator[N]
```

Yield an infinite series starting at `start`, incrementing by `step`. Use with `islice` or a break condition to avoid infinite loops.

```python
async for value in count(10, -1):
    ...  # 10, 9, 8, 7, ...
```

## cycle

```python
async def cycle(itr: AnyIterable[T]) -> AsyncIterator[T]
```

Yield a repeating series from the iterable. Lazily consumes on first pass, then caches values for subsequent cycles.

```python
async for value in cycle([1, 2]):
    ...  # 1, 2, 1, 2, 1, 2, ...
```

## dropwhile

```python
async def dropwhile(predicate: Predicate[T], iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Drop items while the predicate is `True`, then yield all remaining items. Accepts sync or async predicates.

```python
def pred(x):
    return x < 4

async for item in dropwhile(pred, range(6)):
    ...  # 4, 5
```

## filterfalse

```python
async def filterfalse(predicate: Predicate[T], iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Yield items only when the predicate evaluates to `False`. Accepts sync or async predicates.

```python
def pred(x):
    return x < 4

async for item in filterfalse(pred, range(6)):
    ...  # 4, 5
```

## groupby

```python
async def groupby(itr: AnyIterable[T], key: Optional[KeyFunction[T, R]] = None) -> AsyncIterator[tuple[Any, list[T]]]
```

Yield `(key, group_list)` pairs for consecutive groups. Key defaults to identity. Suggest sorting by key before grouping.

```python
data = ["A", "a", "b", "c", "C", "c"]

async for key, group in groupby(data, key=str.lower):
    ...  # ("a", ["A","a"]), ("b", ["b"]), ("c", ["c","C","c"])
```

## islice

```python
async def islice(itr: AnyIterable[T], stop) -> AsyncIterator[T]
async def islice(itr: AnyIterable[T], start, stop[, step]) -> AsyncIterator[T]
```

Yield selected items by index range. Supports `stop` only, or `start, stop, step`.

```python
data = range(10)

async for item in islice(data, 5):
    ...  # 0, 1, 2, 3, 4

async for item in islice(data, 2, 5):
    ...  # 2, 3, 4

async for item in islice(data, 1, 7, 2):
    ...  # 1, 3, 5
```

## permutations

```python
async def permutations(itr: AnyIterable[T], r: Optional[int] = None) -> AsyncIterator[tuple[T, ...]]
```

Yield `r`-length permutations (defaults to full length). Consumes entire iterable first.

```python
async for value in permutations(range(3)):
    ...  # (0,1,2), (0,2,1), (1,0,2), (1,2,0), (2,0,1), (2,1,0)
```

## product

```python
async def product(*itrs: AnyIterable[T], repeat: int = 1) -> AsyncIterator[tuple[T, ...]]
```

Yield cartesian products of all iterables. Consumes all iterables before yielding.

```python
async for value in product("abc", "xy"):
    ...  # ("a","x"), ("a","y"), ("b","x"), ...

async for value in product(range(3), repeat=3):
    ...  # (0,0,0), (0,0,1), (0,0,2), ...
```

## repeat

```python
async def repeat(elem: T, n: int = -1) -> AsyncIterator[T]
```

Yield the given value repeatedly. Forever by default, or up to `n` times.

```python
async for value in repeat(7):
    ...  # 7, 7, 7, ... (infinite)

async for value in repeat("x", 3):
    ...  # x, x, x
```

## starmap

```python
async def starmap(fn: AnyFunction[R], iterable: AnyIterableIterable[Any]) -> AsyncIterator[R]
```

Call `fn` with each sub-iterable unpacked as arguments. Each inner iterable is fully consumed before the call.

```python
import operator

data = [(1, 1), (1, 1, 1), (2, 2)]

async for value in starmap(operator.add, data):
    ...  # 2, 3, 4
```

## takewhile

```python
async def takewhile(predicate: Predicate[T], iterable: AnyIterable[T]) -> AsyncIterator[T]
```

Yield values while the predicate is `True`, then stop. Accepts sync or async predicates.

```python
def pred(x):
    return x < 4

async for value in takewhile(pred, range(8)):
    ...  # 0, 1, 2, 3
```

## tee

```python
def tee(itr: AnyIterable[T], n: int = 2) -> tuple[AsyncIterator[T], ...]
```

Return `n` async iterators that each yield items from the source. The first iterator fetches lazily from the original and queues values for others.

**Caveat**: All iterators depend on the first. If consumed slowly, other consumers block. If consumed quickly, memory grows holding queued values.

```python
it1, it2 = tee(range(5), n=2)

async for value in it1:
    ...  # 0, 1, 2, 3, 4

async for value in it2:
    ...  # 0, 1, 2, 3, 4
```

## zip_longest

```python
async def zip_longest(*itrs: AnyIterable[Any], fillvalue: Any = None) -> AsyncIterator[tuple[Any, ...]]
```

Yield tuples until all iterables are exhausted. Shorter iterables are padded with `fillvalue`.

```python
a = range(3)
b = range(5)

async for x, y in zip_longest(a, b, fillvalue=-1):
    ...  # (0,0), (1,1), (2,2), (-1,3), (-1,4)
```
