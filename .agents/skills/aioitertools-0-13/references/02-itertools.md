# itertools Reference

Async-compatible versions of Python's `itertools` module functions. All functions support both standard iterables and async iterables, and can accept sync or async functions where applicable.

See [Python itertools documentation](https://docs.python.org/3/library/itertools.html) for conceptual reference.

## Accumulation Functions

### `accumulate(itr: AnyIterable[T], func: Accumulator[T] = operator.add) -> AsyncIterator[T]`

Yield the running accumulation of an iterable with a binary function. Accepts both standard functions and coroutines for accumulation.

```python
from aioitertools import accumulate
import operator

# Running sum (default)
data = [1, 2, 3, 4]
async for total in accumulate(data):
    ...  # 1, 3, 6, 10

# Custom function (multiplication)
async def mul(a, b):
    return a * b

async for product in accumulate(data, func=mul):
    ...  # 1, 2, 6, 24

# Async accumulator function
async for total in accumulate(data, func=async_add_func):
    ...
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `func` (optional): Binary function for accumulation (default: addition)

**Returns:** `AsyncIterator[T]`

---

## Batching Functions

### `batched(iterable: AnyIterable[T], n: int, *, strict: bool = False) -> AsyncIterator[tuple[T, ...]]`

Yield batches of values from the given iterable. The final batch may be shorter unless `strict=True`.

```python
from aioitertools import batched

# Basic batching
async for batch in batched(range(15), 5):
    ...  # (0-4), (5-9), (10-14)

# With strict mode (raises if final batch incomplete)
try:
    async for batch in batched(range(13), 5, strict=True):
        ...  # Raises ValueError on incomplete batch
except ValueError as e:
    print(f"Incomplete batch: {e}")
```

**Parameters:**
- `iterable`: Iterable or AsyncIterable of type T
- `n`: Batch size (must be >= 1)
- `strict` (optional): Raise ValueError if final batch is incomplete

**Returns:** `AsyncIterator[tuple[T, ...]]`

**Raises:** `ValueError` if n < 1 or if strict=True and final batch incomplete

---

## Chaining Functions

### `chain(*itrs: AnyIterable[T]) -> AsyncIterator[T]`

Yield values from one or more iterables in series. Consumes the first iterable lazily, then the second, and so on.

```python
from aioitertools import chain

# Chain multiple iterables
async for value in chain([1, 2, 3], [7, 8, 9]):
    ...  # 1, 2, 3, 7, 8, 9

# Mix sync and async iterables
async for value in chain(sync_list, async_gen(), another_sync):
    ...

# Chain from iterable of iterables
async for value in chain.from_iterable([list1, list2, list3]):
    ...
```

**Returns:** `AsyncIterator[T]`

---

### `chain.from_iterable(itrs: AnyIterableIterable[T]) -> AsyncIterator[T]`

Like `chain`, but takes an iterable of iterables instead of multiple arguments.

```python
from aioitertools import chain

lists = [[1, 2], [3, 4], [5, 6]]
async for value in chain.from_iterable(lists):
    ...  # 1, 2, 3, 4, 5, 6
```

**Parameters:**
- `itrs`: Iterable of Iterables

**Returns:** `AsyncIterator[T]`

---

## Combinatorial Functions

### `combinations(itr: AnyIterable[T], r: int) -> AsyncIterator[tuple[T, ...]]`

Yield r-length subsequences from the given iterable. Consumes entire iterable before yielding values.

```python
from aioitertools import combinations

# All 3-element combinations
async for combo in combinations(range(4), 3):
    ...  # (0,1,2), (0,1,3), (0,2,3), (1,2,3)

# String combinations
async for combo in combinations("ABC", 2):
    ...  # ("A","B"), ("A","C"), ("B","C")
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `r`: Length of each combination

**Returns:** `AsyncIterator[tuple[T, ...]]`

**Note:** Consumes entire iterable before yielding.

---

### `combinations_with_replacement(itr: AnyIterable[T], r: int) -> AsyncIterator[tuple[T, ...]]`

Yield r-length subsequences with replacement allowed. Consumes entire iterable first.

```python
from aioitertools import combinations_with_replacement

# Combinations with replacement
async for combo in combinations_with_replacement("ABC", 2):
    ...  # ("A","A"), ("A","B"), ("A","C"), ("B","B"), ("B","C"), ("C","C")
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `r`: Length of each combination

**Returns:** `AsyncIterator[tuple[T, ...]]`

---

### `permutations(itr: AnyIterable[T], r: int = None) -> AsyncIterator[tuple[T, ...]]`

Yield all r-length permutations of elements. If r not specified, defaults to length of iterable. Consumes entire iterable first.

```python
from aioitertools import permutations

# All permutations (r=len)
async for perm in permutations("AB"):
    ...  # ("A","B"), ("B","A")

# Specific length
async for perm in permutations(range(3), 2):
    ...  # (0,1), (0,2), (1,0), (1,2), (2,0), (2,1)
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `r` (optional): Length of each permutation

**Returns:** `AsyncIterator[tuple[T, ...]]`

---

### `product(*itrs: AnyIterable[Any], repeat: int = 1) -> AsyncIterator[tuple[Any, ...]]`

Yield elements from the Cartesian product of input iterables. Equivalent to nested for-loops. Consumes all iterables first.

```python
from aioitertools import product

# Product of two iterables
async for pair in product("AB", "XY"):
    ...  # ("A","X"), ("A","Y"), ("B","X"), ("B","Y")

# With repeat parameter
async for triple in product(range(3), repeat=2):
    ...  # (0,0), (0,1), (0,2), (1,0), ..., (2,2)
```

**Parameters:**
- `*itrs`: One or more Iterables or AsyncIterables
- `repeat` (optional): Number of repeats for single iterable

**Returns:** `AsyncIterator[tuple[Any, ...]]`

---

## Filtering Functions

### `compress(data: AnyIterable[T], selectors: AnyIterable[Any]) -> AsyncIterator[T]`

Yield elements from data only when the corresponding selector evaluates to True. Stops when either iterable exhausted.

```python
from aioitertools import compress

# Select specific elements
async for value in compress(range(5), [1, 0, 0, 1, 1]):
    ...  # 0, 3, 4

# With async selectors
async for value in compress(data, async_selector_generator()):
    ...
```

**Parameters:**
- `data`: Iterable or AsyncIterable of type T
- `selectors`: Iterable or AsyncIterable of truthy/falsy values

**Returns:** `AsyncIterator[T]`

---

### `dropwhile(predicate: Predicate[T], iterable: AnyIterable[T]) -> AsyncIterator[T]`

Drop items while predicate is True, then yield all remaining items. Predicate can be sync or async.

```python
from aioitertools import dropwhile

# Drop while condition holds
def pred(x):
    return x < 4

async for item in dropwhile(pred, range(6)):
    ...  # 4, 5

# Async predicate
async def is_small(x):
    return await check_size(x) < threshold

async for item in dropwhile(is_small, items):
    ...
```

**Parameters:**
- `predicate`: Callable (sync or async) returning bool
- `iterable`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[T]`

---

### `filterfalse(predicate: Predicate[T], iterable: AnyIterable[T]) -> AsyncIterator[T]`

Yield items where predicate returns False. Opposite of builtins.filter(). Predicate can be sync or async.

```python
from aioitertools import filterfalse

# Yield items that don't match predicate
async for odd in filterfalse(lambda x: x % 2 == 0, range(10)):
    ...  # 1, 3, 5, 7, 9

# Async predicate
async for invalid in filterfalse(is_valid, items):
    ...
```

**Parameters:**
- `predicate`: Callable (sync or async) returning bool
- `iterable`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[T]`

---

## Grouping Functions

### `groupby(itr: AnyIterable[T], key: KeyFunction[T] = None) -> AsyncIterator[tuple[Any, AsyncIterator[T]]]`

Group consecutive items by key function. Returns (key, group_iterator) pairs. Key can be sync or async.

```python
from aioitertools import groupby

# Group by function
data = "AAABBBAACC"
async for key, group in groupby(data):
    group_str = ''.join([item async for item in group])
    ...  # ("A", "AAA"), ("B", "BBB"), ("C", "CC")

# Async key function
async def get_category(item):
    return await fetch_category(item)

async for category, items in groupby(data, key=get_category):
    async for item in items:
        ...  # Process grouped items
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `key` (optional): Key function (sync or async)

**Returns:** `AsyncIterator[tuple[Any, AsyncIterator[T]]]`

**Note:** Groups only consecutive items with same key. Sort data first if needed.

---

## Infinite Iterators

### `count(start: int = 0, step: int = 1) -> AsyncIterator[int]`

Yield an infinite series starting at given value and increasing by step.

```python
from aioitertools import count

# Count from 0
counter = count()
async for i in count():
    ...  # 0, 1, 2, 3, ...

# Custom start and step
async for i in count(10, -1):
    ...  # 10, 9, 8, 7, ...

# Use with islice to limit
async for i in islice(count(1), 5):
    ...  # 1, 2, 3, 4, 5
```

**Parameters:**
- `start` (optional): Starting value (default: 0)
- `step` (optional): Increment (default: 1)

**Returns:** `AsyncIterator[int]`

---

### `cycle(itr: AnyIterable[T]) -> AsyncIterator[T]`

Yield a repeating series from the given iterable. Lazily consumes iterable and caches values for repetition.

```python
from aioitertools import cycle

# Cycle through list
counter = 0
async for value in cycle([1, 2]):
    ...  # 1, 2, 1, 2, 1, 2, ...
    counter += 1
    if counter >= 6:
        break

# Use with islice to limit
async for value in islice(cycle("AB"), 5):
    ...  # A, B, A, B, A
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[T]`

---

### `repeat(object: T, times: int = None) -> AsyncIterator[T]`

Yield object indefinitely or specified number of times.

```python
from aioitertools import repeat

# Infinite repeat
async for value in repeat("default"):
    ...  # "default", "default", ...
    break  # Need explicit break

# Limited repeat
async for value in repeat("x", 5):
    ...  # "x" repeated 5 times
```

**Parameters:**
- `object`: Value to repeat
- `times` (optional): Number of repetitions (None = infinite)

**Returns:** `AsyncIterator[T]`

---

## Slicing Functions

### `islice(itr: AnyIterable[T], stop: int) -> AsyncIterator[T]`
### `islice(itr: AnyIterable[T], start: int, stop: int, step: int = 1) -> AsyncIterator[T]`

Yield items from iterable according to slice notation. Supports start, stop, and step parameters.

```python
from aioitertools import islice

# First N items
async for item in islice(async_iterator, 5):
    ...  # Items 0-4

# Range with start, stop
async for item in islice(async_iterator, 2, 10):
    ...  # Items 2-9

# With step
async for item in islice(async_iterator, 0, 10, 2):
    ...  # Items 0, 2, 4, 6, 8
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `start` (optional): Start index
- `stop`: Stop index (exclusive)
- `step` (optional): Step size (default: 1)

**Returns:** `AsyncIterator[T]`

---

## Taking Functions

### `takewhile(predicate: Predicate[T], iterable: AnyIterable[T]) -> AsyncIterator[T]`

Yield items while predicate is True. Stops when predicate first returns False. Predicate can be sync or async.

```python
from aioitertools import takewhile

# Take while condition holds
async for item in takewhile(lambda x: x < 5, range(10)):
    ...  # 0, 1, 2, 3, 4

# Async predicate
async def is_valid(x):
    return await check(x)

async for item in takewhile(is_valid, items):
    ...
```

**Parameters:**
- `predicate`: Callable (sync or async) returning bool
- `iterable`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[T]`

---

## Teeing Functions

### `tee(itr: AnyIterable[T], n: int = 2) -> tuple[AsyncIterator[T], ...]`

Split one iterator into multiple independent async iterators. Returns tuple of n async iterators.

```python
from aioitertools import tee

# Split into two independent iterators
iter1, iter2 = tee(async_iterator)

async for item in iter1:
    ...  # Process first copy

async for item in iter2:
    ...  # Process second copy (independent)

# Split into multiple iterators
iter1, iter2, iter3 = tee(large_iterator, 3)
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `n` (optional): Number of copies (default: 2)

**Returns:** `tuple[AsyncIterator[T], ...]`

**Note:** Each iterator must be consumed independently. Buffering occurs internally.

---

## Zipping Functions

### `zip_longest(*itrs: AnyIterable[Any], fillvalue: Any = None) -> AsyncIterator[tuple[Any, ...]]`

Aggregate items from multiple iterables into tuples. Continues until longest iterable exhausted, filling missing values with fillvalue.

```python
from aioitertools import zip_longest

# Zip with different lengths
async for pair in zip_longest([1, 2, 3], ["a", "b"]):
    ...  # (1,"a"), (2,"b"), (3,None)

# Custom fill value
async for pair in zip_longest([1, 2, 3], ["a", "b"], fillvalue="N/A"):
    ...  # (1,"a"), (2,"b"), (3,"N/A")
```

**Parameters:**
- `*itrs`: One or more Iterables or AsyncIterables
- `fillvalue` (optional): Value for missing items (default: None)

**Returns:** `AsyncIterator[tuple[Any, ...]]`

---

## Mapping Functions

### `starmap(fn: Callable[..., R], itr: AnyIterableIterable[Any]) -> AsyncIterator[R]`

Apply function to arguments from iterable of argument tuples. Like map but unpacks arguments. Function can be sync or async.

```python
from aioitertools import starmap

# Apply function with multiple arguments
args = [(1, 2), (3, 4), (5, 6)]
async for result in starmap(lambda x, y: x + y, args):
    ...  # 3, 7, 11

# Async function
async def add(x, y):
    return await compute_sum(x, y)

async for result in starmap(add, arg_pairs):
    ...
```

**Parameters:**
- `fn`: Callable (sync or async) accepting multiple arguments
- `itr`: Iterable of argument tuples

**Returns:** `AsyncIterator[R]`
