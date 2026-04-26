# Collection Methods

Collection methods work on arrays, objects, strings, and other iterable values. They provide iteration, grouping, filtering, reduction, and aggregation patterns.

## Iteration

### `_.forEach(collection, [iteratee=_.identity])` / `_.forEachRight()`

Iterates over elements. Iteratee receives `(value, index|key, collection)`. Returns collection for chaining. `forEachRight` iterates from right to left. `each` and `eachRight` are aliases.

```js
_.forEach([1, 2], function(value) { console.log(value); });
_.forEach({ 'a': 1, 'b': 2 }, function(value, key) { console.log(key); });
```

### `_.forIn(object, [iteratee])` / `_.forInRight()`

Iterates over own and inherited enumerable properties. `forOwn` iterates only own properties.

### `_.map(collection, [iteratee=_.identity])`

Creates a new array of values returned by running each element through iteratee.

```js
_.map([1, 2], function(n) { return n * 3; });
// → [3, 6]

_.map({ 'a': 1, 'b': 2 }, function(n) { return n * 3; });
// → [3, 6]

_.map([[1, 2], [3, 4]], _.flatten);
// → [1, 2, 3, 4]
```

### `_.times(n, [iteratee=_.identity])`

Invokes iteratee n times, returning results. Iteratee receives `(index)`.

```js
_.times(3, function(n) { return _.random(0, 100); });
// → [84, 78, 54]
```

## Filtering and Finding

### `_.filter(collection, [predicate=_.identity])` / `_.reject(collection, [predicate=_.identity])`

Creates an array of elements predicate returns truthy for. `reject` is the inverse — keeps elements where predicate returns falsey.

```js
var users = [
  { 'user': 'barney',  'active': false },
  { 'user': 'fred',    'active': false },
  { 'user': 'pebbles', 'active': true }
];
_.filter(users, function(o) { return !o.active; });
// → objects for ['barney', 'fred']

_.reject(users, function(o) { return !o.active; });
// → objects for ['pebbles']
```

### `_.find(collection, [predicate=_.identity], [fromIndex=0])`

Gets the first element predicate returns truthy for. Returns undefined if not found. Supports iteratee shorthands.

```js
_.find(users, { 'user': 'barney', 'active': false }); // → { 'user': 'barney', 'active': false }
_.find(users, 'active');                               // → { 'user': 'pebbles', 'active': true }
```

### `_.findLast(collection, [predicate=_.identity])`

Like `find` but iterates right to left.

### `_.findKey(object, [predicate=_.identity])` / `_.findLastKey()`

Returns the key of the first/last element predicate returns truthy for. Searches own and inherited properties.

## Grouping

### `_.groupBy(collection, [iteratee=_.identity])`

Groups elements by iteratee result. Returns an object with group keys mapping to arrays.

```js
_.groupBy([6.1, 4.2, 6.3], Math.floor);
// → { '4': [4.2], '6': [6.1, 6.3] }

_.groupBy(['one', 'two', 'three'], 'length');
// → { '3': ['one', 'two'], '5': ['three'] }
```

### `_.countBy(collection, [iteratee=_.identity])`

Counts elements by iteratee result. Returns counts instead of arrays.

```js
_.countBy([6.1, 4.2, 6.3], Math.floor);
// → { '4': 1, '6': 2 }
```

### `_.partition(collection, [predicate=_.identity])`

Creates an array of two arrays: first with elements predicate returns truthy for, second with the rest.

```js
_.partition([1, 2, 3, 4, 5, 6], function(n) { return n % 2 == 0; });
// → [[2, 4, 6], [1, 3, 5]]
```

### `_.keyBy(collection, [iteratee=_.identity])`

Creates an object keyed by iteratee result. If duplicate keys exist, the last value wins.

```js
var array = [
  { 'dir': 'left', 'code': 97 },
  { 'dir': 'right', 'code': 100 }
];
_.keyBy(array, function(o) { return String.fromCharCode(o.code); });
// → { 'a': { 'dir': 'left', 'code': 97 }, 'd': { 'dir': 'right', 'code': 100 } }
```

## Reduction

### `_.reduce(collection, [iteratee=_.identity], [accumulator])`

Reduces collection to a single value. Iteratee receives `(accumulator, value, index|key, collection)`. If accumulator not provided, first element is used.

```js
_.reduce([1, 2], function(sum, n) { return sum + n; }, 0);
// → 3

_.reduce({ 'a': 1, 'b': 2, 'c': 1 }, function(result, value, key) {
  (result[value] || (result[value] = [])).push(key);
  return result;
}, {});
// → { '1': ['a', 'c'], '2': ['b'] }
```

### `_.reduceRight(collection, [iteratee=_.identity], [accumulator])`

Like `reduce` but iterates right to left.

## Aggregation

### `_.max(array)` / `_.maxBy(array, [iteratee=_.identity])`

Gets the maximum value. `maxBy` uses iteratee for comparison.

```js
_.max([4, 2, 8, 6]); // → 8
_.maxBy([{ 'n': 1 }, { 'n': 2 }], 'n'); // → { 'n': 2 }
```

### `_.min(array)` / `_.minBy(array, [iteratee=_.identity])`

Gets the minimum value.

### `_.sum(array)` / `_.sumBy(array, [iteratee=_.identity])`

Gets the sum of values. `sumBy` maps through iteratee first.

```js
_.sum([4, 2, 8, 6]); // → 20
_.sumBy([{ 'n': 4 }, { 'n': 2 }, { 'n': 8 }], 'n'); // → 14
```

### `_.mean(array)` / `_.meanBy(array, [iteratee=_.identity])`

Gets the mean (average) of values.

```js
_.mean([4, 2, 8, 6]); // → 5
```

## Testing

### `_.every(collection, [predicate=_.identity])`

Checks if predicate returns truthy for all elements. Returns true for empty collections.

```js
_.every([true, 1, null, 'yes'], Boolean); // → false
```

### `_.some(collection, [predicate=_.identity])`

Checks if predicate returns truthy for any element.

```js
_.some([null, 0, 'yes', false], Boolean); // → true
```

## Sampling and Shuffling

### `_.sample(collection)` / `_.sampleSize(collection, [n=1])`

Gets a random element or n random elements.

```js
_.sample([1, 2, 3, 4]);       // → 2
_.sampleSize([1, 2, 3, 4], 2); // → [3, 1]
```

### `_.shuffle(collection)`

Creates a random permutation of the collection.

## Size

### `_.size(collection)`

Gets the number of elements. For objects, counts own enumerable string-keyed properties. For strings, returns string length.

```js
_.size([1, 2, 3]);         // → 3
_.size({ 'a': 1, 'b': 2 }); // → 2
_.size('pebbles');          // → 7
```

## Flat Mapping

### `_.flatMap(collection, [iteratee=_.identity])`

Maps then flattens one level. Equivalent to `_.flatten(_.map(collection, iteratee))`.

```js
var over = function(n) {
  return function(array) {
    return _.filter(array, function(x) { return x >= n; });
  };
};
_.flatMap([1, 2], function(x) { return [[x], [x + 1]]; });
// → [[1], [2], [2], [3]]
```

### `_.flatMapDeep()` / `_.flatMapDepth(collection, [iteratee], [depth=1])`

Maps then flattens recursively or to specified depth.

## Invoke and Map

### `_.invokeMap(collection, path, [args])`

Invokes the method at path on each element, returning results.

```js
var objects = [{ 'a': 1 }, { 'a': 2 }];
_.invokeMap(objects, 'toString');
// → ['[object Object]', '[object Object]']
```

### `_.mapKeys(object, [iteratee=_.identity])` / `_.mapValues(object, [iteratee=_.identity])`

Creates a new object with keys or values transformed by iteratee.

```js
_.mapKeys({ 'a': 1, 'b': 2 }, function(value, key) {
  return key + value;
});
// → { 'a1': 1, 'b2': 2 }

_.mapValues({ 'a': 1, 'b': 2 }, function(n) { return n * 3; });
// → { 'a': 3, 'b': 6 }
```
