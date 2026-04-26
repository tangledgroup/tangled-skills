# Array Methods

Lodash provides 30+ methods for working with arrays, including creation, transformation, searching, and set operations.

## Creation and Transformation

### `_.chunk(array, [size=1])`

Splits array into groups of length size. If array can't be split evenly, the final chunk contains remaining elements.

```js
_.chunk(['a', 'b', 'c', 'd'], 2);
// → [['a', 'b'], ['c', 'd']]

_.chunk(['a', 'b', 'c', 'd', 'e'], 2);
// → [['a', 'b'], ['c', 'd'], ['e']]
```

### `_.compact(array)`

Creates an array with all falsy values removed. Falsy values are: `false`, `null`, `0`, `""`, `NaN`, and `undefined`.

```js
_.compact([0, 1, false, 2, '', 3]);
// → [1, 2, 3]
```

### `_.concat(array, [values])`

Creates a new array concatenating array with additional values. Supports spreading multiple arrays.

```js
var array = [1];
var other = _.concat(array, 2, [3], [[4]]);
// → [1, 2, 3, [4]]
```

### `_.flatten(array)` / `_.flattenDeep(array)` / `_.flattenDepth(array, [depth=1])`

Flatten nested arrays. `flatten` removes one level, `flattenDeep` recursively flattens all levels, `flattenDepth` controls recursion depth.

```js
_.flatten([1, [2, [3, [4]], 5]]);
// → [1, 2, [3, [4]], 5]

_.flattenDeep([1, [2, [3, [4]], 5]]);
// → [1, 2, 3, 4, 5]

_.flattenDepth([1, [2, [3, [4]], 5]], 2);
// → [1, 2, 3, [4], 5]
```

### `_.fromPairs(pairs)`

The inverse of `_.toPairs`; creates an object from key-value pairs.

```js
_.fromPairs([['a', 1], ['b', 2]]);
// → { 'a': 1, 'b': 2 }
```

### `_.slice(array, [start=0], [end=array.length])`

Creates a slice of array from start up to, but not including end. Used instead of `Array#slice` to ensure dense arrays are returned.

## Access

### `_.head(array)` / `_.first(array)`

Gets the first element. `first` is an alias for `head`.

```js
_.head([1, 2, 3]); // → 1
_.head([]);         // → undefined
```

### `_.last(array)`

Gets the last element.

```js
_.last([1, 2, 3]); // → 3
```

### `_.initial(array)` / `_.tail(array)`

`initial` gets all but the last element. `tail` gets all but the first element.

```js
_.initial([1, 2, 3]); // → [1, 2]
_.tail([1, 2, 3]);    // → [2, 3]
```

### `_.nth(array, [n=0])`

Gets the element at index n. Supports negative indices for counting from the end.

```js
var array = ['a', 'b', 'c', 'd'];
_.nth(array, 1);   // → 'b'
_.nth(array, -2);  // → 'c'
```

## Searching

### `_.findIndex(array, [predicate=_.identity], [fromIndex=0])`

Gets the index of the first element predicate returns truthy for. Supports iteratee shorthands.

```js
var users = [
  { 'user': 'barney', 'active': false },
  { 'user': 'fred', 'active': false },
  { 'user': 'pebbles', 'active': true }
];
_.findIndex(users, { 'user': 'fred', 'active': false }); // → 1
_.findIndex(users, ['active', false]);                   // → 0
_.findIndex(users, 'active');                            // → 2
```

### `_.findLastIndex(array, [predicate=_.identity], [fromIndex=array.length-1])`

Like `findIndex` but iterates right to left.

### `_.indexOf(array, value, [fromIndex=0])` / `_.lastIndexOf(array, value, [fromIndex=array.length-1])`

Gets the index of first/last occurrence using SameValueZero equality. Negative fromIndex offsets from end.

```js
_.indexOf([1, 2, 1, 2], 2);    // → 1
_.indexOf([1, 2, 1, 2], 2, 2); // → 3
_.lastIndexOf([1, 2, 1, 2], 2); // → 3
```

### `_.includes(collection, value, [fromIndex=0])`

Checks if value is in array (uses SameValueZero). Supports searching strings and objects too.

```js
_.includes([1, 2, 3], 1);      // → true
_.includes('hello', 'ell');    // → true
_.includes({ 'a': 1 }, 1);     // → true
```

## Sorted Array Operations

Optimized binary search methods for already-sorted arrays:

- `_.sortedIndex(array, value)` — lowest index to insert value to maintain sort order
- `_.sortedIndexBy(array, value, [iteratee])` — with custom iteratee for ranking
- `_.sortedIndexOf(array, value)` — binary search for value in sorted array
- `_.sortedLastIndex(array, value)` — highest insertion index
- `_.sortedLastIndexBy(array, value, [iteratee])` — with iteratee
- `_.sortedLastIndexOf(array, value)` — binary search from right
- `_.sortedUniq(array)` — remove duplicates from sorted array
- `_.sortedUniqBy(array, [iteratee])` — with custom iteratee

```js
_.sortedIndex([30, 50], 40);           // → 1
_.sortedIndexOf([4, 5, 5, 5, 6], 5);   // → 1
_.sortedLastIndexOf([4, 5, 5, 5, 6], 5); // → 3
_.sortedUniq([1, 1, 2]);               // → [1, 2]
```

## Mutation

These methods modify the original array:

### `_.pull(array, [values])` / `_.pullAll(array, values)`

Removes all given values using SameValueZero. `pullAll` accepts an array of values to remove.

```js
var array = ['a', 'b', 'c', 'a', 'b', 'c'];
_.pull(array, 'a', 'c');
console.log(array); // → ['b', 'b']
```

### `_.pullAllBy(array, values, [iteratee=_.identity])` / `_.pullAllWith(array, values, [comparator])`

Like `pullAll` but with custom comparison via iteratee or comparator.

### `_.pullAt(array, [indexes])`

Removes elements at specified indexes, returns removed elements.

```js
var array = ['a', 'b', 'c', 'd'];
var pulled = _.pullAt(array, [1, 3]);
console.log(array);  // → ['a', 'c']
console.log(pulled); // → ['b', 'd']
```

### `_.remove(array, [predicate=_.identity])`

Removes elements predicate returns truthy for, returns removed elements. Predicate receives `(value, index, array)`.

```js
var array = [1, 2, 3, 4];
var evens = _.remove(array, function(n) { return n % 2 == 0; });
console.log(array);  // → [1, 3]
console.log(evens);  // → [2, 4]
```

### `_.reverse(array)`

Reverses array in place. Based on `Array#reverse`.

## Non-Mutating Alternatives

- `_.without(array, [values])` — like `pull` but returns new array
- `_.difference(array, [values])` — like `pullAll` but returns new array
- `_.differenceBy(array, [values], [iteratee])` — with custom iteratee
- `_.differenceWith(array, [values], [comparator])` — with custom comparator

## Set Operations

### `_.union([arrays])` / `_.unionBy()` / `_.unionWith()`

Creates an array of unique values from all arrays.

```js
_.union([2, 1], [2, 3]); // → [2, 1, 3]
```

### `_.intersection([arrays])` / `_.intersectionBy()` / `_.intersectionWith()`

Creates an array of values included in all given arrays. Order determined by first array.

```js
_.intersection([2, 1], [2, 3]); // → [2]
```

### `_.xor([arrays])` / `_.xorBy()` / `_.xorWith()`

Creates an array of values that appear in exactly one of the arrays (symmetric difference).

```js
_.xor([2, 1], [2, 3]); // → [1, 3]
```

## Taking and Dropping

### `_.take(array, [n=1])` / `_.takeRight(array, [n=1])`

Creates a slice with n elements from the beginning/end.

```js
_.take([1, 2, 3], 2);     // → [1, 2]
_.takeRight([1, 2, 3], 2); // → [2, 3]
```

### `_.takeWhile(array, [predicate])` / `_.takeRightWhile(array, [predicate])`

Takes elements while predicate returns truthy, from beginning/end.

```js
_.takeWhile([1, 2, 3, 4], n => n < 3); // → [1, 2]
```

### `_.drop(array, [n=1])` / `_.dropRight()` / `_.dropWhile()` / `_.dropRightWhile()`

Drops n elements or elements while predicate is truthy.

## Ordering and Sorting

### `_.sortBy(collection, [iteratees=[_.identity]])`

Sorts by iteratee(s) in ascending order. Multiple iteratees apply left to right.

```js
var users = [
  { 'user': 'fred',   'age': 48 },
  { 'user': 'barney', 'age': 36 },
  { 'user': 'fred',   'age': 40 },
  { 'user': 'barney', 'age': 34 }
];
_.sortBy(users, ['user', function(o) { return -o.age; }]);
// → objects for [['barney', 36], ['barney', 34], ['fred', 48], ['fred', 40]]
```

### `_.orderBy(collection, [iteratees=[_.identity]], [orders])`

Sorts by iteratees with explicit ascending/descending order.

```js
_.orderBy(users, ['user', 'age'], ['asc', 'desc']);
// → objects for [['barney', 36], ['barney', 34], ['fred', 48], ['fred', 40]]
```

## Zipping and Unzipping

### `_.zip([arrays])` / `_.zipObject([props], [values])` / `_.zipObjectDeep()`

Groups elements from multiple arrays by index.

```js
_.zip(['a', 'b'], [1, 2], ['true', 'false']);
// → [['a', 1, 'true'], ['b', 2, 'false']]

_.zipObject(['a', 'b'], [1, 2]);
// → { 'a': 1, 'b': 2 }

_.zipObjectDeep(['a.b.c', 'x.y.z'], [1, 2]);
// → { 'a': { 'b': { 'c': 1 } }, 'x': { 'y': { 'z': 2 } } }
```

### `_.unzip(array)` / `_.unzipWith(array, [iteratee])`

The inverse of zip — transposes a matrix of arrays.

```js
var pairs = [['a', 1], ['b', 2]];
_.unzip(pairs); // → [['a', 'b'], [1, 2]]
```

### `_.zipWith([arrays], [iteratee])`

Zips with a custom iteratee applied to each grouped element.

```js
_.zipWith(['a', 'b'], [1, 2], ['true', 'false'], function(a, b, c) {
  return { 'a': a, 'b': b, 'c': c };
});
// → [{ 'a': 'a', 'b': 1, 'c': 'true' }, { 'a': 'b', 'b': 2, 'c': 'false' }]
```

## Other Array Methods

- `_.join(array, [separator=','])` — joins array elements into a string
- `_.shuffle(array)` — creates a random permutation
- `_.sample(array)` / `_.sampleSize(collection, [n=1])` — random sampling
- `_.toArray(value)` — converts any value to array
