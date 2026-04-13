# Collection Methods (24 methods)

Generic iteration utilities that work on both arrays and objects. Unlike array-specific methods, these handle any iterable collection.

## Aggregation

### `_.countBy(collection, [iteratee=_.identity])`

Creates an object composed of keys generated from running each element through iteratee. Values represent the count of times each key was returned.

**Since:** 0.5.0

```javascript
_.countBy([6.1, 4.2, 6.3], Math.floor);
// => { '4': 1, '6': 2 }

// Property shorthand
_.countBy(['one', 'two', 'three'], 'length');
// => { '3': 2, '5': 1 }
```

### `_.groupBy(collection, [iteratee=_.identity])`

Creates an object composed of keys generated from running each element through iteratee. Values are arrays of elements that returned the same key.

**Since:** 0.1.0

```javascript
_.groupBy([6.1, 4.2, 6.3], Math.floor);
// => { '4': [4.2], '6': [6.1, 6.3] }

// Property shorthand
_.groupBy(['one', 'two', 'three'], 'length');
// => { '3': ['one', 'two'], '5': ['three'] }
```

### `_.keyBy(collection, [iteratee=_.identity])`

Creates an object composed of keys generated from running each element through iteratee. Later elements overwrite earlier ones with the same key.

**Since:** 4.0.0 (was `_.indexBy` in v3)

```javascript
var array = [
  { 'dir': 'left', 'code': 97 },
  { 'dir': 'right', 'code': 100 }
];

_.keyBy(array, function(obj) {
  return String.fromCharCode(obj.code);
});
// => { 'a': { 'dir': 'left', 'code': 97 }, 'd': { 'dir': 'right', 'code': 100 } }

// Property shorthand
_.keyBy(array, 'dir');
// => { 'left': { 'dir': 'left', 'code': 97 }, 'right': { 'dir': 'right', 'code': 100 } }
```

### `_.partition(collection, [predicate=_.identity])`

Creates arrays grouping elements by predicate result. Returns `[truthy, falsy]`.

**Since:** 4.0.0

```javascript
_.partition([1, 2, 3], n => n % 2);
// => [[1, 3], [2]]
```

## Checking

### `_.every(collection, [predicate=_.identity])`

Checks if **all** elements pass predicate test. Returns `true` for empty collections (vacuous truth).

**Since:** 0.1.0

```javascript
_.every([true, 1, null, 'yes'], Boolean);
// => false

var users = [
  { 'user': 'barney', 'age': 36, 'active': false },
  { 'user': 'fred', 'age': 40, 'active': false }
];

// Matches shorthand
_.every(users, { 'user': 'barney', 'active': false });
// => false

// Property shorthand
_.every(users, ['active', false]);
// => true
```

### `_.some(collection, [predicate=_.identity])`

Checks if **any** element passes predicate test. Returns `false` for empty collections.

**Since:** 0.1.0 (was `_.any`)

```javascript
_.some([false, 0, null, 'yes'], Boolean);
// => true

var users = [
  { 'user': 'barney', 'age': 36, 'active': false },
  { 'user': 'fred', 'age': 40, 'active': false }
];

_.some(users, { 'user': 'fred', 'active': false });
// => true
```

### `_.includes(collection, value, [fromIndex=0])`

Checks if collection contains value using SameValueZero. Works on arrays and objects.

**Since:** 4.0.0

```javascript
_.includes([1, 2, 3], 1);     // => true
_.includes([1, 2, 3], 1, 2);  // => false (search from index 2)

_.includes({ 'a': 1, 'b': 2 }, 1);  // => true
```

## Finding

### `_.find(collection, [predicate=_.identity], [fromIndex=0])`

Gets the first element that passes predicate test. Returns `undefined` if not found.

**Since:** 0.1.0

```javascript
var users = [
  { 'user': 'barney', 'age': 36, 'active': true },
  { 'user': 'fred', 'age': 40, 'active': false },
  { 'user': 'pebbles', 'age': 1, 'active': true }
];

// Function predicate
_.find(users, o => o.age < 40);
// => { 'user': 'barney', 'age': 36, 'active': true }

// Matches shorthand
_.find(users, { 'age': 1, 'active': true });
// => { 'user': 'pebbles', 'age': 1, 'active': true }

// Property shorthand
_.find(users, 'active');
// => { 'user': 'barney', 'age': 36, 'active': true }
```

### `_.findLast(collection, [predicate=_.identity], [fromIndex=collection.length-1])`

Like `_.find` but iterates from right to left.

**Since:** 2.0.0

```javascript
_.findLast([1, 2, 3, 4], n => n % 2 == 1);
// => 3
```

## Filtering

### `_.filter(collection, [predicate=_.identity])`

Creates an array of elements that pass predicate test. Returns new array (doesn't mutate).

**Since:** 0.1.0

```javascript
var users = [
  { 'user': 'barney', 'age': 36, 'active': true },
  { 'user': 'fred', 'age': 40, 'active': false }
];

_.filter(users, o => !o.active);
// => [{ 'user': 'fred', 'age': 40, 'active': false }]

// Matches shorthand
_.filter(users, { 'age': 36, 'active': true });
// => [{ 'user': 'barney', 'age': 36, 'active': true }]

// Property shorthand
_.filter(users, 'active');
// => [{ 'user': 'barney', 'age': 36, 'active': true }]
```

### `_.reject(collection, [predicate=_.identity])`

Creates an array of elements that **fail** predicate test. Inverse of `_.filter`.

**Since:** 0.1.0

```javascript
var users = [
  { 'user': 'barney', 'age': 36, 'active': false },
  { 'user': 'fred', 'age': 40, 'active': true }
];

_.reject(users, o => !o.active);
// => [{ 'user': 'fred', 'age': 40, 'active': true }]
```

## Flattening Maps

### `_.flatMap(collection, [iteratee=_.identity])`

Maps each element through iteratee and flattens result one level deep.

**Since:** 4.0.0

```javascript
function duplicate(n) {
  return [n, n];
}

_.flatMap([1, 2], duplicate);
// => [1, 1, 2, 2]
```

### `_.flatMapDeep(collection, [iteratee=_.identity])`

Maps each element through iteratee and recursively flattens result.

**Since:** 4.7.0

```javascript
function duplicate(n) {
  return [[n, n]];
}

_.flatMapDeep([1, 2], duplicate);
// => [1, 1, 2, 2]
```

### `_.flatMapDepth(collection, [iteratee=_.identity], [depth=1])`

Maps each element through iteratee and flattens result up to specified depth.

**Since:** 4.7.0

```javascript
function duplicate(n) {
  return [[n, n]];
}

_.flatMapDepth([1, 2], duplicate, 2);
// => [1, 1, 2, 2]
```

## Iteration

### `_.forEach(collection, [iteratee=_.identity])` / `_.each`

Iterates over collection elements invoking iteratee. Returns collection for chaining.

**Since:** 0.1.0

```javascript
_.forEach(['a', 'b', 'c'], function(letter) {
  console.log(letter);
});
// => logs 'a', 'b', 'c' (order not guaranteed for objects)

// Object iteration
_.forEach({ 'a': 1, 'b': 2 }, function(value, key) {
  console.log(key, value);
});
```

### `_.forEachRight(collection, [iteratee=_.identity])` / `_.eachRight`

Like `_.forEach` but iterates from right to left.

**Since:** 3.0.0

```javascript
var sum = 0;
_.forEachRight([1, 2], n => sum += n);
console.log(sum); // => 3
```

## Mapping

### `_.map(collection, [iteratee=_.identity])`

Creates an array of values by running each element through iteratee.

**Since:** 0.1.0

```javascript
function square(n) {
  return n * n;
}

_.map([4, 8], square);
// => [16, 64]

// Property shorthand
var users = [
  { 'user': 'barney', 'age': 36 },
  { 'user': 'fred', 'age': 40 }
];

_.map(users, 'user');
// => ['barney', 'fred']
```

### `_.invokeMap(collection, path, [args])`

Creates an array of values by invoking method at path on each element.

**Since:** 4.0.0 (was `_.invoke`)

```javascript
var objects = [
  { 'a': [1], 'b': [2], 'c': [3] }
];

_.invokeMap(objects, 'push', 4);
// => [1, 1, 1] (returns array lengths)

// Without args
_.invokeMap([[5], [6]], 'join');
// => ['5', '6']
```

## Ordering

### `_.orderBy(collection, [iteratees=[_.identity]], [orders])`

Creates an array of elements sorted by iteratees with specified orders ('asc' or 'desc').

**Since:** 4.0.0

```javascript
var users = [
  { 'user': 'fred', 'age': 48 },
  { 'user': 'barney', 'age': 34 }
];

_.orderBy(users, ['user', 'age'], ['asc', 'desc']);
// => [{ 'user': 'barney', 'age': 34 }, { 'user': 'fred', 'age': 48 }]
```

### `_.sortBy(collection, [iteratees=[_.identity]])`

Creates an array of elements sorted by iteratees (ascending order).

**Since:** 2.4.0

```javascript
var users = [
  { 'user': 'fred', 'age': 48 },
  { 'user': 'barney', 'age': 34 }
];

_.sortBy(users, o => o.user);
// => [{ 'user': 'barney', 'age': 34 }, { 'user': 'fred', 'age': 48 }]

// Multiple sort keys
_.sortBy(users, ['user', 'age']);
```

## Reduction

### `_.reduce(collection, [iteratee=_.identity], [accumulator])`

Processes elements from left to right, accumulating a single value.

**Since:** 0.1.0 (was `_.inject`, `_.foldl`)

```javascript
var sum = _.reduce([1, 2, 3], function(total, n) {
  return total + n;
}, 0);
console.log(sum); // => 6

// Without initial value (first element used as accumulator)
_.reduce([[1], [2], [3]], function(result, array) {
  return result.concat(array);
});
// => [1, 2, 3]
```

### `_.reduceRight(collection, [iteratee=_.identity], [accumulator])`

Like `_.reduce` but processes from right to left.

**Since:** 0.1.0 (was `_.foldr`)

```javascript
var sum = _.reduceRight([1, 2, 3], function(total, n) {
  return total + n;
}, 0);
console.log(sum); // => 6
```

## Sampling

### `_.sample(collection)`

Gets a random element from collection.

**Since:** 0.7.0

```javascript
_.sample([1, 2, 3, 4]);
// => 2 (random)
```

### `_.sampleSize(collection, [n=1])`

Gets n random elements from collection as an array.

**Since:** 4.0.0

```javascript
_.sampleSize([1, 2, 3], 2);
// => [3, 1] (random order)

_.sampleSize([1, 2, 3], 4);
// => [2, 1, 3] (returns all if n > length)
```

### `_.shuffle(collection)`

Creates an array of shuffled values using Fisher-Yates algorithm.

**Since:** 0.1.0

```javascript
_.shuffle([1, 2, 3, 4]);
// => [2, 4, 1, 3] (random order)
```

## Size

### `_.size(collection)`

Gets the number of elements in collection.

**Since:** 0.1.0

```javascript
_.size([1, 2, 3]);      // => 3
_.size({ 'a': 1, 'b': 2 }); // => 2
```

## Predicate Shorthand Support

Most collection methods support shorthand predicates:

```javascript
// Function predicate (always works)
_.filter(users, user => user.age > 25);

// Object shorthand (matches properties with _.matches)
_.filter(users, { age: 30, active: true });

// Property name string (truthy check with _.property)
_.filter(users, 'active');

// [path, value] array (with _.matchesProperty)
_.filter(users, ['age', 30]);
```

## Array vs Collection Methods

Use **array methods** when:
- Working exclusively with arrays
- Need array-specific operations (chunk, zip, uniq)
- Performance is critical (array methods are faster)

Use **collection methods** when:
- Working with both arrays and objects
- Need generic iteration (map, filter, find)
- Writing reusable code that handles multiple types

```javascript
// Array-specific
_.indexOf([1, 2, 3], 2);     // 1
_.chunk([1, 2, 3, 4], 2);    // [[1, 2], [3, 4]]

// Works on both arrays and objects
_.map([1, 2, 3], n => n * 2);        // [2, 4, 6]
_.map({ a: 1, b: 2 }, n => n * 2);   // [2, 4]

_.includes([1, 2, 3], 2);      // true
_.includes({ a: 1, b: 2 }, 2); // true
```
