# Array Methods (56 methods)

Array-specific utilities for manipulation, transformation, and analysis.

## Splitting and Grouping

### `_.chunk(array, [size=1])`

Creates an array of elements split into groups of length `size`. If `array` can't be split evenly, the final chunk contains remaining elements.

**Since:** 3.0.0

```javascript
_.chunk(['a', 'b', 'c', 'd'], 2);
// => [['a', 'b'], ['c', 'd']]

_.chunk(['a', 'b', 'c', 'd'], 3);
// => [['a', 'b', 'c'], ['d']]
```

### `_.compact(array)`

Creates an array with all falsey values removed. Falsey values include: `false`, `null`, `0`, `-0`, `0n`, `""`, `undefined`, and `NaN`.

**Since:** 0.1.0

```javascript
_.compact([0, 1, false, 2, '', 3]);
// => [1, 2, 3]
```

### `_.split(array, separator, [limit])`

Splits array into strings based on separator pattern.

**Since:** 4.0.0

```javascript
_.split('a-b-c', '-', 2);
// => ['a', 'b-c']
```

## Concatenation

### `_.concat(array, [values])`

Creates a new array concatenating `array` with additional arrays and/or values.

**Since:** 4.0.0

```javascript
var array = [1];
var other = _.concat(array, 2, [3], [[4]]);

console.log(other); // => [1, 2, 3, [4]]
console.log(array); // => [1] (original unchanged)
```

## Difference Operations

### `_.difference(array, [values])`

Creates an array of `array` values not included in the other arrays using SameValueZero equality. Order determined by first array.

**Note:** Unlike `_.pullAll`, returns a new array.

**Since:** 0.1.0

```javascript
_.difference([2, 1], [2, 3]);
// => [1]
```

### `_.differenceBy(array, [values], [iteratee=_.identity])`

Like `_.difference` but accepts an iteratee to generate comparison criteria.

**Since:** 4.0.0

```javascript
_.differenceBy([2.1, 1.2], [2.3, 3.4], Math.floor);
// => [1.2]
```

### `_.differenceWith(array, [values], [comparator])`

Like `_.difference` but accepts a custom comparator function.

**Since:** 4.0.0

```javascript
var objects = [{ x: 1, y: 2 }, { x: 2, y: 1 }];
_.differenceWith(objects, [{ x: 1, y: 2 }], _.isEqual);
// => [{ x: 2, y: 1 }]
```

## Dropping Elements

### `_.drop(array, [n=1])`

Creates a slice of array with the first n elements removed.

**Since:** 0.5.0

```javascript
var array = [1, 2, 3, 4, 5];
_.drop(array);     // => [2, 3, 4, 5]
_.drop(array, 2);  // => [3, 4, 5]
_.drop(array, 5);  // => []
```

### `_.dropRight(array, [n=1])`

Creates a slice of array with the last n elements removed.

**Since:** 3.0.0

```javascript
var array = [1, 2, 3, 4, 5];
_.dropRight(array);     // => [1, 2, 3, 4]
_.dropRight(array, 2);  // => [1, 2, 3]
```

### `_.dropRightWhile(array, [predicate=_.identity])`

Creates a slice of array excluding elements dropped from the right that match predicate.

**Since:** 3.0.0

```javascript
var array = [1, 2, 3, 4];
_.dropRightWhile(array, n => n >= 3);
// => [1, 2]
```

### `_.dropWhile(array, [predicate=_.identity])`

Creates a slice of array excluding elements dropped from the beginning that match predicate.

**Since:** 3.0.0

```javascript
var array = [1, 2, 3, 4];
_.dropWhile(array, n => n < 3);
// => [3, 4]
```

## Filling Arrays

### `_.fill(array, value, [start=0], [end=array.length])`

Fills elements of array with value from start up to end. **Mutates array.**

**Since:** 3.2.0

```javascript
var array = [1, 2, 3];
_.fill(array, 'a');
console.log(array); // => ['a', 'a', 'a']

_.fill(Array(3), 2);
// => [2, 2, 2]

_.fill([4, 6, 8, 10], '*', 1, 3);
// => [4, '*', '*', 10]
```

## Finding Indices

### `_.findIndex(array, [predicate=_.identity], [fromIndex=0])`

Gets the index of the first element that passes predicate test. Returns -1 if not found.

**Since:** 0.1.0

```javascript
var users = [
  { 'user': 'barney', 'active': false },
  { 'user': 'fred', 'active': true }
];

_.findIndex(users, o => o.user === 'fred');
// => 1
```

### `_.findLastIndex(array, [predicate=_.identity], [fromIndex=array.length-1])`

Gets the index of the last element that passes predicate test. Returns -1 if not found.

**Since:** 0.1.0

```javascript
var users = [
  { 'user': 'barney', 'active': true },
  { 'user': 'fred', 'active': false }
];

_.findLastIndex(users, o => o.user === 'barney');
// => 0
```

## Flattening

### `_.flatten(array)`

Creates a flattened array of a nested array (one level deep).

**Since:** 0.1.0

```javascript
_.flatten([1, [2, 3], [4, 5]]);
// => [1, 2, 3, 4, 5]
```

### `_.flattenDeep(array)`

Recursively flattens array to any depth.

**Since:** 2.4.1

```javascript
_.flattenDeep([1, [2, 3, [4, [5, [6]]]]]);
// => [1, 2, 3, 4, 5, 6]
```

### `_.flattenDepth(array, [depth=1])`

Flattens array up to specified depth.

**Since:** 4.4.0

```javascript
var array = [1, [2, 3, [4, [5, [6]]]]];
_.flattenDepth(array, 1);  // => [1, 2, 3, [4, [5, [6]]]]
_.flattenDepth(array, 2);  // => [1, 2, 3, 4, [5, [6]]]
_.flattenDepth(array, 3);  // => [1, 2, 3, 4, 5, [6]]
```

## Head and Tail

### `_.head(array)` / `_.first(array)`

Gets the first element of array. Returns undefined if array is empty.

**Since:** 0.1.0

```javascript
_.head([1, 2, 3]);  // => 1
_.head([]);         // => undefined
```

### `_.tail(array)`

Gets all elements except the first.

**Since:** 4.0.0

```javascript
_.tail([1, 2, 3]);
// => [2, 3]
```

### `_.initial(array)`

Gets all elements except the last.

**Since:** 0.1.0

```javascript
_.initial([1, 2, 3]);
// => [1, 2]
```

### `_.last(array)`

Gets the last element of array. Returns undefined if empty.

**Since:** 0.1.0

```javascript
_.last([1, 2, 3]);  // => 3
_.last([]);         // => undefined
```

## Index Operations

### `_.indexOf(array, value, [fromIndex=0])`

Gets the index at which value is first found using SameValueZero. Returns -1 if not found.

**Since:** 0.1.0

```javascript
var array = ['a', 'b', 'c', 'a', 'b'];
_.indexOf(array, 'a');     // => 0
_.indexOf(array, 'b');     // => 1
_.indexOf(array, 'c');     // => 2
_.indexOf(array, 'd');     // => -1
_.indexOf(array, 'b', 2);  // => 4 (search from index 2)
```

### `_.lastIndexOf(array, value, [fromIndex=array.length-1])`

Gets the index at which value is last found. Searches backwards.

**Since:** 0.1.0

```javascript
var array = ['a', 'b', 'c', 'b', 'c'];
_.lastIndexOf(array, 'b');   // => 3
_.lastIndexOf(array, 'c');   // => 4
_.lastIndexOf(array, 'd');   // => -1
_.lastIndexOf(array, 'b', 2); // => 1 (search up to index 2)
```

### `_.nth(array, [n=0])`

Gets the element at index n (supports negative indices).

**Since:** 4.7.0

```javascript
var array = ['a', 'b', 'c', 'd'];
_.nth(array, 1);   // => 'b'
_.nth(array, -1);  // => 'd'
```

## Intersection Operations

### `_.intersection([arrays])`

Creates an array of unique values present in all arrays using SameValueZero.

**Since:** 0.1.0

```javascript
_.intersection([2, 1], [2, 3]);
// => [2]
```

### `_.intersectionBy([arrays], [iteratee=_.identity])`

Like `_.intersection` but accepts an iteratee for comparison.

**Since:** 4.0.0

```javascript
_.intersectionBy([2.1, 1.2], [2.3, 3.4], Math.floor);
// => [2.1]
```

### `_.intersectionWith([arrays], [comparator])`

Like `_.intersection` but accepts a custom comparator.

**Since:** 4.0.0

```javascript
var objects = [{ x: 1, y: 2 }, { x: 2, y: 1 }];
var others = [{ x: 1, y: 2 }];
_.intersectionWith(objects, others, _.isEqual);
// => [{ x: 1, y: 2 }]
```

## Joining

### `_.join(array, [separator=','])`

Joins array elements into a string.

**Since:** 0.1.0

```javascript
_.join(['a', 'b', 'c'], '~');
// => 'a~b~c'
```

## Pulling (Mutating)

### `_.pull(array, [values])`

Removes all given values from array by value. **Mutates array.**

**Since:** 0.1.0

```javascript
var array = ['a', 'b', 'c', 'a', 'b', 'c'];
_.pull(array, 'a', 'c');
console.log(array); // => ['b', 'b']
```

### `_.pullAll(array, values)`

Removes all occurrences of values from array. **Mutates array.**

**Since:** 4.0.0

```javascript
var array = ['a', 'b', 'c', 'a', 'b', 'c'];
_.pullAll(array, ['a', 'c']);
console.log(array); // => ['b', 'b']
```

### `_.pullAllBy(array, values, [iteratee=_.identity])`

Like `_.pullAll` but accepts an iteratee. **Mutates array.**

**Since:** 4.0.0

```javascript
var array = [{ x: 1 }, { x: 2 }, { x: 3 }];
_.pullAllBy(array, [{ x: 1 }, { x: 3 }], 'x');
console.log(array); // => [{ x: 2 }]
```

### `_.pullAllWith(array, values, [comparator])`

Like `_.pullAll` but accepts a comparator. **Mutates array.**

**Since:** 4.0.0

```javascript
var array = [{ x: 1, y: 2 }, { x: 3, y: 4 }];
_.pullAllWith(array, [{ x: 1, y: 2 }], _.isEqual);
console.log(array); // => [{ x: 3, y: 4 }]
```

### `_.pullAt(array, [indexes])`

Removes elements from array at given indexes. **Mutates array.** Returns removed values.

**Since:** 3.0.0

```javascript
var array = ['a', 'b', 'c', 'd'];
var pulled = _.pullAt(array, [1, 3]);
console.log(array);  // => ['a', 'c']
console.log(pulled); // => ['b', 'd']
```

### `_.remove(array, [predicate=_.identity])`

Removes elements from array that match predicate. **Mutates array.** Returns removed values.

**Since:** 0.1.0

```javascript
var array = [1, 2, 3, 4];
var evens = _.remove(array, n => n % 2 == 0);
console.log(array);  // => [1, 3]
console.log(evens);  // => [2, 4]
```

## Reversing

### `_.reverse(array)`

Reverses array. **Mutates array.**

**Since:** 0.1.0

```javascript
var array = [1, 2, 3];
_.reverse(array);
console.log(array); // => [3, 2, 1]
```

## Slicing

### `_.slice(array, [start=0], [end=array.length])`

Creates a slice of array from start to end.

**Since:** 0.1.0

```javascript
var array = ['a', 'b', 'c', 'd', 'e'];
_.slice(array, 2, 4);
// => ['c', 'd']
```

## Sorted Array Operations

### `_.sortedIndex(array, value)`

Gets the index at which value should be inserted to maintain sorted order (binary search).

**Since:** 0.1.0

```javascript
var array = [4, 5, 6];
_.sortedIndex(array, 4); // => 0
_.sortedIndex(array, 6); // => 2 (last occurrence)
```

### `_.sortedIndexBy(array, value, [iteratee=_.identity])`

Like `_.sortedIndex` but accepts an iteratee.

**Since:** 4.0.0

```javascript
var objects = [{ 'x': 4 }, { 'x': 5 }, { 'x': 6 }];
_.sortedIndexBy(objects, { 'x': 4 }, o => o.x);
// => 0
```

### `_.sortedIndexOf(array, value)`

Gets the index of the first occurrence of value in a sorted array (binary search).

**Since:** 4.0.0

```javascript
_.sortedIndexOf([4, 5, 5, 5, 6], 5);
// => 1
```

### `_.sortedLastIndex(array, value)`

Gets the index at which value should be inserted to maintain order (after duplicates).

**Since:** 0.1.0

```javascript
var array = [4, 5, 5, 5, 6];
_.sortedLastIndex(array, 5); // => 4
```

### `_.sortedLastIndexBy(array, value, [iteratee=_.identity])`

Like `_.sortedLastIndex` but accepts an iteratee.

**Since:** 4.0.0

```javascript
var objects = [{ 'x': 4 }, { 'x': 5 }, { 'x': 6 }];
_.sortedLastIndexBy(objects, { 'x': 5 }, o => o.x);
// => 2
```

### `_.sortedLastIndexOf(array, value)`

Gets the index of the last occurrence of value in a sorted array (binary search).

**Since:** 4.0.0

```javascript
var array = [1, 2, 5, 5, 5, 6];
_.sortedLastIndexOf(array, 5); // => 4
```

### `_.sortedUniq(array)`

Removes duplicates from a sorted array.

**Since:** 4.0.0

```javascript
_.sortedUniq([1, 1, 2, 2]);
// => [1, 2]
```

### `_.sortedUniqBy(array, [iteratee=_.identity])`

Like `_.sortedUniq` but accepts an iteratee.

**Since:** 4.0.0

```javascript
_.sortedUniqBy([1.1, 1.2, 2.3, 2.4], Math.floor);
// => [1.1, 2.3]
```

## Taking Elements

### `_.take(array, [n=1])`

Creates a slice of the first n elements.

**Since:** 0.1.0

```javascript
_.take([1, 2, 3]);      // => [1]
_.take([1, 2, 3], 2);   // => [1, 2]
_.take([1, 2, 3], 5);   // => [1, 2, 3]
_.take([1, 2, 3], -1);  // => []
```

### `_.takeRight(array, [n=1])`

Creates a slice of the last n elements.

**Since:** 0.1.0

```javascript
_.takeRight([1, 2, 3]);      // => [3]
_.takeRight([1, 2, 3], 2);   // => [2, 3]
_.takeRight([1, 2, 3], 5);   // => [1, 2, 3]
```

### `_.takeRightWhile(array, [predicate=_.identity])`

Creates a slice of elements taken from the right that match predicate.

**Since:** 3.0.0

```javascript
var array = [1, 2, 3];
_.takeRightWhile(array, n => n > 1);
// => [2, 3]
```

### `_.takeWhile(array, [predicate=_.identity])`

Creates a slice of elements taken from the beginning that match predicate.

**Since:** 3.0.0

```javascript
var array = [1, 2, 3];
_.takeWhile(array, n => n < 3);
// => [1, 2]
```

## Union Operations

### `_.union([arrays])`

Creates an array of unique values from all arrays.

**Since:** 0.1.0

```javascript
_.union([2], [1, 2]);
// => [2, 1]
```

### `_.unionBy([arrays], [iteratee=_.identity])`

Like `_.union` but accepts an iteratee.

**Since:** 4.0.0

```javascript
_.unionBy([2.1], [1.2, 2.3], Math.floor);
// => [2.1, 1.2]
```

### `_.unionWith([arrays], [comparator])`

Like `_.union` but accepts a comparator.

**Since:** 4.0.0

```javascript
var objects = [{ x: 1, y: 2 }];
var others = [{ x: 1, y: 1 }, { x: 1, y: 2 }];
_.unionWith(objects, others, _.isEqual);
// => [{ x: 1, y: 2 }]
```

## Uniqueness

### `_.uniq(array)`

Creates a duplicate-free version of array using SameValueZero.

**Since:** 0.1.0

```javascript
_.uniq([2, 1, 2]);
// => [2, 1]
```

### `_.uniqBy(array, [iteratee=_.identity])`

Like `_.uniq` but accepts an iteratee.

**Since:** 4.0.0

```javascript
_.uniqBy([2.1, 1.2, 2.3], Math.floor);
// => [2.1, 1.2]
```

### `_.uniqWith(array, [comparator=_.isEqual])`

Like `_.uniq` but accepts a comparator.

**Since:** 4.0.0

```javascript
var objects = [{ 'x': 1, 'y': 2 }, { 'x': 2, 'y': 1 }];
_.uniqWith(objects, _.isEqual);
// => [{ 'x': 1, 'y': 2 }] (duplicates removed)
```

## Unzipping

### `_.unzip(array)`

Creates an array grouping elements at each index. Inverse of `_.zip`.

**Since:** 0.1.0

```javascript
_.unzip([['a', 1, true], ['b', 2, false]]);
// => [['a', 'b'], [1, 2], [true, false]]
```

### `_.unzipWith(array, [iteratee=_.identity])`

Like `_.unzip` but accepts an iteratee to transform groups.

**Since:** 4.0.0

```javascript
var array = [['a', 1], ['b', 2]];
_.unzipWith(array, function(group) {
  return _.sum(group);
});
// => [111, 222] (if strings converted to numbers)
```

## Without Values

### `_.without(array, [values])`

Creates an array excluding given values.

**Since:** 0.1.0

```javascript
_.without([2, 1, 2, 3], 1, 2);
// => [3]
```

## XOR Operations

### `_.xor([arrays])`

Creates an array of symmetric difference (values in one array but not all).

**Since:** 0.1.0

```javascript
_.xor([2, 1], [2, 3]);
// => [1, 3]
```

### `_.xorBy([arrays], [iteratee=_.identity])`

Like `_.xor` but accepts an iteratee.

**Since:** 4.0.0

```javascript
_.xorBy([2.1, 1.2], [2.3, 3.4], Math.floor);
// => [1.2, 3.4]
```

### `_.xorWith([arrays], [comparator])`

Like `_.xor` but accepts a comparator.

**Since:** 4.0.0

```javascript
var objects = [{ x: 1, y: 2 }];
var others = [{ x: 1, y: 1 }, { x: 1, y: 2 }];
_.xorWith(objects, others, _.isEqual);
// => [{ x: 1, y: 1 }]
```

## Zipping

### `_.zip([arrays])`

Creates an array grouping elements at each index.

**Since:** 0.1.0

```javascript
_.zip(['a', 'b'], [1, 2], [true, false]);
// => [['a', 1, true], ['b', 2, false]]
```

### `_.zipObject([props=[]], [values=[]])`

Creates an object from keys and values arrays.

**Since:** 0.1.0

```javascript
_.zipObject(['a', 'b'], [1, 2]);
// => { 'a': 1, 'b': 2 }
```

### `_.zipObjectDeep([props=[]], [values=[]])`

Like `_.zipObject` but supports deep paths.

**Since:** 4.0.0

```javascript
_.zipObjectDeep(['a.b[0].c', 'a.b[1].d'], [1, 2]);
// => { 'a': { 'b': [{ 'c': 1 }, { 'd': 2 }] } }
```

### `_.zipWith([arrays], [iteratee=_.identity])`

Like `_.zip` but accepts an iteratee to transform groups.

**Since:** 3.0.0

```javascript
_.zipWith([1, 2], [10, 20], [100, 200], function(a, b, c) {
  return a + b + c;
});
// => [111, 222]
```

## From Pairs

### `_.fromPairs(pairs)`

Creates an object from key-value pairs. Inverse of `_.toPairs`.

**Since:** 3.0.0

```javascript
_.fromPairs([['a', 1], ['b', 2]]);
// => { 'a': 1, 'b': 2 }
```
