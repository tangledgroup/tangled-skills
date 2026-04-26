# Math Methods

Math methods provide aggregation, rounding, clamping, and random number generation utilities.

## Aggregation

### `_.max(array)` / `_.maxBy(array, [iteratee=_.identity])`

Gets the maximum value. `maxBy` computes using an iteratee.

```js
_.max([4, 2, 8, 6]); // → 8

var users = [
  { 'user': 'barney', 'age': 36 },
  { 'user': 'fred',   'age': 40 }
];
_.maxBy(users, 'age'); // → { 'user': 'fred', 'age': 40 }
```

### `_.min(array)` / `_.minBy(array, [iteratee=_.identity])`

Gets the minimum value.

```js
_.min([4, 2, 8, 6]); // → 2
```

### `_.sum(array)` / `_.sumBy(array, [iteratee=_.identity])`

Gets the sum of values. `sumBy` maps through iteratee first.

```js
_.sum([4, 2, 8, 6]); // → 20

_.sumBy([{ 'n': 4 }, { 'n': 2 }, { 'n': 8 }], 'n');
// → 14
```

### `_.mean(array)` / `_.meanBy(array, [iteratee=_.identity])`

Gets the arithmetic mean (average).

```js
_.mean([4, 2, 8, 6]); // → 5
```

## Rounding

### `_.ceil(number, [precision=0])` / `_.floor(number, [precision=0])` / `_.round(number, [precision=0])`

Rounds up, down, or to nearest. Precision controls decimal places.

```js
_.ceil(4.006);    // → 5
_.ceil(6.004, 2); // → 6.01
_.floor(4.006);   // → 4
_.round(4.006);   // → 4
_.round(4.006, 2); // → 4.01
_.round(4.016, 2); // → 4.02
```

## Arithmetic

### `_.add(augend, addend)` / `_.subtract(minuend, subtrahend)` / `_.multiply(multiplier, multiplicand)` / `_.divide(dividend, divisor)`

Basic arithmetic operations. Useful in functional pipelines where native operators don't work as iteratees.

```js
_.add(6, 4);     // → 10
_.subtract(10, 4); // → 6
_.multiply(6, 4);  // → 24
_.divide(6, 4);    // → 1.5
```

## Clamping

### `_.clamp(number, [lower], upper)`

Clamps number within the inclusive lower and upper bounds.

```js
_.clamp(-10, -5, 5);  // → -5
_.clamp(10, -5, 5);   // → 5
```

## Range

### `_.range([start=0], end, [step=1])` / `_.rangeRight([start=0], end, [step=1])`

Creates an array of numbers. `range` generates left-to-right; `rangeRight` right-to-left.

```js
_.range(4);       // → [0, 1, 2, 3]
_.range(-4);      // → [-3, -2, -1]
_.range(1, 5);    // → [1, 2, 3, 4]
_.range(0, 20, 5); // → [0, 5, 10, 15]
_.range(0, -4, -1); // → [0, -1, -2, -3]
_.rangeRight(4);   // → [3, 2, 1, 0]
```

## Random

### `_.random([lower=0], [upper=1], [floating])`

Gets a random number between lower and upper (inclusive). If floating is true (or only one argument given), returns a floating-point number.

```js
_.random(0, 5);       // → an integer between 0 and 5
_.random(5);          // → a floating-point number between 0 and 5
_.random(5, true);    // → a floating-point number between 0 and 5
_.random(1.2, 5.2);   // → a floating-point number between 1.2 and 5.2
```

## In Range

### `_.inRange(number, [start=0], end)`

Checks if number is between start and end (inclusive of start, exclusive of end).

```js
_.inRange(3, 2, 4);    // → true
_.inRange(4, 2);       // → false
_.inRange(4, 2, 8);    // → true
_.inRange(2, 2);       // → false
_.inRange(1.2, 2);     // → true
_.inRange(5.2, 4);     // → false
_.inRange('-3', '-2', '-6'); // → true
```
