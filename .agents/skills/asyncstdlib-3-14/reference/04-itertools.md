# Itertools Library

The `asyncstdlib.itertools` module implements Python's `itertools` for async callables and iterables. Only functions that benefit from explicit async implementation are provided. Other itertools functions can be turned async using `iter()`, e.g., `asyncstdlib.iter(itertools.count(5))`.

All utilities in this module explicitly close their iterable arguments when done. This can be unexpected for non-exhausting utilities like `dropwhile()` and may require explicit scoping with `scoped_iter()`.

## Infinite Iterators

### cycle

```python
async for :T in cycle(iterable: (async) iter T)
```

Indefinitely iterate over `iterable`. Lazily exhausts on first pass, recalls from internal buffer on subsequent passes. If empty, terminates immediately. Items are provided as they become available — subsequent passes do not replicate delays. All items are stored internally (may consume significant memory for large iterables).

## Iterator Merging

### chain

```python
async for :T in chain(*iterables: (async) iter T)
```

Flatten values from all iterables consecutively. Lazily exhausts each iterable. Assumes ownership and closes iterables reliably when `chain` is closed. Pass iterables via a tuple to `chain.from_iterable` to avoid closing unprocessed ones.

### chain.from_iterable

```python
async for :T in chain.from_iterable(iterable: (async) iter (async) iter T)
```

Alternate constructor that lazily exhausts the iterable of iterables as well. Suitable for lazy or infinite outer iterables. Closing only closes already-fetched inner iterables.

### zip_longest

```python
async for :(T or S, ...) in zip_longest(*iterables: (async) iter T, fillvalue: S = None)
```

Aggregate elements from each iterable into tuples. Shorter iterables are padded with `fillvalue`. Exhausted when all iterables are exhausted. Mixed sync and async iterables are supported.

## Iterator Filtering

### compress

```python
async for :T in compress(data: (async) iter T, selectors: (async) iter T)
```

Yield items from `data` where paired `selectors` evaluate as true. Equivalent to `(item async for item, select in zip(data, selectors) if select)`.

### dropwhile

```python
async for :T in dropwhile(predicate: (T) -> (await) bool, iterable: (async) iter T)
```

Discard items while `predicate` is true. Once predicate returns false, that item and all subsequent items are yielded without further predicate evaluation.

### filterfalse

```python
async for :T in filterfalse(predicate: None | (T) -> (await) bool, iterable: (async) iter T)
```

Yield items where `predicate(item)` is false. If `predicate` is `None`, yield items that are false.

### takewhile

```python
async for :T in takewhile(predicate: (T) -> (await) bool, iterable: (async) iter T)
```

Yield items while `predicate` is true. Once predicate returns false, iteration stops and the failing item is discarded (not available from either `takewhile` or the original iterable).

### islice

```python
async for :T in islice(iterable: (async) iter T, stop: int)
async for :T in islice(iterable: (async) iter T, start: int, stop: int, step: int = 1)
```

Lazy async version of `iterable[start:stop:step]`. First `start` items are discarded, then every `step` item is yielded until `stop` total items fetched.

## Iterator Transforming

### accumulate

```python
async for :T in accumulate(iterable: (async) iter T, function: (T, T) -> (await) T = add[, initial: T])
```

Running reduction of `iterable`. Unlike `reduce()`, this yields each intermediate value. Defaults to `operator.add` (running sum). If `initial` is provided, it is the first value processed and yielded. Raises `TypeError` if iterable is empty and no `initial` given.

```python
# Running sum
async for total in a.accumulate(async_data()):
    print(total)

# Running product
async for prod in a.accumulate(async_data(), function=operator.mul, initial=1):
    print(prod)
```

Changed in version 3.13.2: `initial=None` means no initial value is assumed.

### starmap

```python
async for :T in starmap(function: (*A) -> (await) T, iterable: (async) iter (A, ...))
```

Apply a function to arguments unpacked from a single iterable of tuples. Like `map()` but with one iterable of multiple arguments instead of multiple iterables of single arguments.

## Iterator Splitting

### tee

```python
for :(async iter T, ...) in tee(iterable: (async) iter T, n: int = 2[, *, lock: async with Any])
```

Split a single iterable into `n` separate async iterators, each providing the same items in order. All child iterators may advance separately but share items — when the most advanced iterator retrieves an item, it is buffered until all others yield it. Works lazily with infinite iterables if all iterators advance.

```python
async def derivative(sensor_data):
    previous, current = a.tee(sensor_data, n=2)
    await a.anext(previous)  # advance one iterator
    return a.map(operator.sub, previous, current)
```

- `tee` of a `tee` shares its buffer with parent, sibling, and child tees (changed 3.13.2)
- If underlying iterable is concurrency-safe, children are too. Otherwise, provide a `lock` (e.g., `asyncio.Lock`) to synchronize `anext` calls (added 3.10.5)
- Unlike `itertools.tee()`, returns a custom type (not a tuple). Supports indexing, iteration, unpacking, and `aclose()` to close all children. Can be used in `async with`.

### pairwise

```python
async for :(T, T) in pairwise(iterable: (async) iter T)
```

Yield successive overlapping pairs `(iter[n], iter[n+1])`. No pair emitted if iterable has 0 or 1 items. If exactly one item, `pairwise` waits for and consumes it before finishing. Added in version 3.10.0.

### batched

```python
async for :T in batched(iterable: (async) iter T, n: int, strict: bool = False)
```

Batch the iterable into tuples of length `n`. Returns each batch as soon as ready. If `strict=True` and last batch is smaller than `n`, raises `ValueError`. Added in version 3.11.0; `strict` parameter added in 3.13.0.

### groupby

```python
async for :(T, async iter T) in groupby(iterable: (async) iter T)
async for :(R, async iter T) in groupby(iterable: (async) iter T, key: (T) -> (await) R)
```

Create an async iterator over consecutive keys and groups. Groups are consecutive with respect to the original iterable — multiple groups may share a key if separated by different keys (e.g., `1,1,1,2,2,1` produces groups `1`, `2`, `1`).

The groupby iterator and each group's iterator share the same underlying iterator. Previous groups become inaccessible when groupby advances. Not safe to concurrently advance both the groupby iterator and any group iterator.

Unlike `itertools.groupby()`, sorting beforehand is generally not useful since it requires all values and keys up-front, losing the advantage of lazy async iteration. Added in version 1.1.0.
