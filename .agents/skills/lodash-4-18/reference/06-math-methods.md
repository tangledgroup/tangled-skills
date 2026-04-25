# Math Methods (16 methods)

Mathematical operations including arithmetic, rounding, and aggregation.

## Arithmetic

### `_.add(augend, addend)`

Adds two numbers.

```javascript
_.add(6, 4); // => 10
```

### `_.divide(dividend, divisor)`

Divides two numbers.

```javascript
_.divide(6, 3); // => 2
```

### `_.multiply(multiplier, multiplicand)`

Multiplies two numbers.

```javascript
_.multiply(6, 4); // => 24
```

### `_.subtract(minuend, subtrahend)`

Subtracts two numbers.

```javascript
_.subtract(6, 4); // => 2
```

## Rounding

### `_.ceil(number, [precision=0])`

Ceils number to precision (rounds up).

```javascript
_.ceil(4.008);           // => 5
_.ceil(6.004, 2);        // => 6.01
_.ceil(6040, -2);        // => 6100
```

### `_.floor(number, [precision=0])`

Floors number to precision (rounds down).

```javascript
_.floor(4.006);           // => 4
_.floor(0.046, 2);        // => 0.04
_.floor(4060, -2);        // => 4000
```

### `_.round(number, [precision=0])`

Rounds number to precision.

```javascript
_.round(4.006);           // => 4
_.round(4.006, 2);        // => 4.01
_.round(4060, -2);        // => 4100
```

## Extremes

### `_.max(array)`

Gets maximum value in array.

```javascript
var array = [2, 1, 7];
_.max(array); // => 7
```

### `_.maxBy(array, [iteratee=_.identity])`

Gets maximum value using iteratee for comparison.

```javascript
var objects = [{ 'n': 1 }, { 'n': 2 }];
_.maxBy(objects, o => o.n); // => { 'n': 2 }
```

### `_.min(array)`

Gets minimum value in array.

```javascript
var array = [2, 1, 7];
_.min(array); // => 1
```

### `_.minBy(array, [iteratee=_.identity])`

Gets minimum value using iteratee for comparison.

```javascript
var objects = [{ 'n': 1 }, { 'n': 2 }];
_.minBy(objects, o => o.n); // => { 'n': 1 }
```

## Averages

### `_.mean(array)`

Calculates arithmetic mean of array.

```javascript
_.mean([4, 2, 8, 6]); // => 5
```

### `_.meanBy(array, [iteratee=_.identity])`

Calculates mean using iteratee for value extraction.

```javascript
var objects = [{ 'n': 4 }, { 'n': 2 }, { 'n': 8 }, { 'n': 6 }];
_.meanBy(objects, o => o.n); // => 5
```

## Summation

### `_.sum(array)`

Calculates sum of array values.

```javascript
_.sum([4, 6, 8, 10]); // => 28
```

### `_.sumBy(array, [iteratee=_.identity])`

Calculates sum using iteratee for value extraction.

```javascript
var objects = [{ 'n': 4 }, { 'n': 6 }];
_.sumBy(objects, o => o.n); // => 10
```

## Common Patterns

### Safe Arithmetic

```javascript
// Add with default values
const total = _.add(amount || 0, tax || 0);

// Divide with zero check
const average = count ? _.divide(sum, count) : 0;
```

### Aggregation

```javascript
// Sum of property values
const totalAge = _.sumBy(users, 'age');

// Average calculation
const avgScore = _.meanBy(scores, s => s.value);

// Find max by computed value
const oldestUser = _.maxBy(users, u => u.age);
```

### Precision Control

```javascript
// Round to 2 decimal places
const price = _.round(amount, 2);

// Round to nearest hundred
const rounded = _.round(value, -2);
```
