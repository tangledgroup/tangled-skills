# Other Methods (Date, Number - 4 methods)

Additional utility methods that don't fit into main categories.

## Date Methods

### `_.now()`

Gets the number of milliseconds since the Unix Epoch (January 1, 1970 00:00:00 UTC).

**Since:** 2.0.0

```javascript
// Get current timestamp
const timestamp = _.now();
// => 1699876543210 (example)

// Calculate elapsed time
const start = _.now();
doWork();
const duration = _.now() - start;
console.log(`Elapsed: ${duration}ms`);

// Alternative to Date.now()
_.now() === Date.now(); // => true (same value)
```

**Use cases:**
- Performance measurement and benchmarking
- Timestamp generation for logging or caching
- Calculating time differences

## Number Methods

### `_.clamp(number, [lower], upper)`

Clamps number within the inclusive lower and upper bounds.

**Since:** 2.4.0

```javascript
_.clamp(-10, -5, 5);    // => -5 (below lower bound)
_.clamp(0, -5, 5);      // => 0 (within bounds)
_.clamp(10, -5, 5);     // => 5 (above upper bound)

// Without lower bound
_.clamp(10, undefined, 5); // => 5
_.clamp(-10, undefined, 5); // => -10 (no lower limit)

// Common use: volume/slider values
const volume = _.clamp(userInput, 0, 100);
```

**Use cases:**
- Volume/slide controls (0-100%)
- Score normalization
- Bounding calculated values

### `_.inRange(number, [start=0], end)`

Checks if number is within the inclusive range [start, end].

**Since:** 4.0.0

```javascript
_.inRange(3, 2, 4);    // => true (3 is between 2 and 4)
_.inRange(4, 8);       // => true (4 is between 0 and 8)
_.inRange(4, 2);       // => false (4 is not between 0 and 2)

// Works with negative numbers
_.inRange(-1, -5, 0);  // => true
_.inRange(-6, -5, 0);  // => false

// Handles reversed ranges
_.inRange(3, 5, 1);    // => true (automatically swaps to [1, 5])
```

**Use cases:**
- Validation of numeric inputs
- Checking if values fall within acceptable ranges
- Age/group eligibility checks

### `_.random([lower=0], [upper=1], [floating])`

Generates a random number between lower and upper (inclusive).

**Since:** 0.7.0

```javascript
// Default: random float between 0 and 1
_.random();           // => 0.423... (float)

// Integer range
_.random(5);          // => 3 (integer 0-5)
_.random(1, 5);       // => 3 (integer 1-5)

// Floating point range
_.random(1.2, 5.2);   // => 3.7... (float 1.2-5.2)
_.random(1.2, 5.2, true); // => 3.7... (explicit float)

// Integer only
_.random(0, 5, false); // => 3 (integer 0-5)

// Negative ranges
_.random(-10, -1);    // => -5 (integer -10 to -1)
```

**Parameters:**
- `lower`: Minimum value (default 0)
- `upper`: Maximum value (default 1, or lower if only one arg)
- `floating`: Return float instead of integer

**Use cases:**
- Generating random IDs or tokens
- Simulating data
- Random sampling
- Game mechanics

## Common Patterns

### Timing and Performance

```javascript
// Measure function execution time
function measure(fn, ...args) {
  const start = _.now();
  const result = fn(...args);
  const duration = _.now() - start;
  return { result, duration };
}

const { result, duration } = measure(expensiveOperation);
console.log(`Took ${duration}ms`);
```

### Input Validation

```javascript
// Validate age range
function isValidAge(age) {
  return _.isInteger(age) && _.inRange(age, 0, 120);
}

// Clamp volume to valid range
function setVolume(value) {
  const clamped = _.clamp(value, 0, 100);
  player.volume = clamped / 100;
}
```

### Random Generation

```javascript
// Generate random ID
function generateId(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let id = '';
  for (let i = 0; i < length; i++) {
    id += chars[_.random(0, chars.length - 1)];
  }
  return id;
}

// Random sample from array
function randomItem(array) {
  const index = _.random(0, array.length - 1);
  return array[index];
}

// Shuffle with random
function shuffle(array) {
  return [...array].sort(() => _.random(-1, 1));
}
```

### Range Checks

```javascript
// Check if value is in multiple ranges
function isInAnyRange(value, ...ranges) {
  return ranges.some(([start, end]) => _.inRange(value, start, end));
}

isInAnyRange(5, [0, 10], [20, 30]); // => true

// Business hours check
function isBusinessHours(hour) {
  return _.inRange(hour, 9, 17); // 9 AM to 5 PM
}
```

### Normalization

```javascript
// Normalize value to 0-1 range
function normalize(value, min, max) {
  const clamped = _.clamp(value, min, max);
  return (clamped - min) / (max - min);
}

normalize(50, 0, 100); // => 0.5

// Denormalize from 0-1 range
function denormalize(normalized, min, max) {
  return normalized * (max - min) + min;
}

denormalize(0.5, 0, 100); // => 50
```

## Comparison with Native Methods

### `_.now()` vs `Date.now()`

```javascript
// Equivalent functionality
_.now() === Date.now(); // => true

// Lodash version is consistent across environments
// and can be easily mocked in tests
```

### `_.random()` vs `Math.random()`

```javascript
// Math.random() always returns 0-1 float
Math.random(); // => 0.423...

// _.random() is more flexible
_.random(1, 10);        // Integer 1-10
_.random(1.5, 2.5);     // Float 1.5-2.5
_.random(5);            // Integer 0-5

// Lodash version handles integers automatically
```

### `_.clamp()` vs Manual Clamping

```javascript
// Manual approach
const clamped = Math.min(Math.max(value, min), max);

// Lodash approach (more readable)
const clamped = _.clamp(value, min, max);

// Lodash also handles undefined bounds
_.clamp(value, undefined, 100); // Only upper bound
```

## Edge Cases

### Random with Same Bounds

```javascript
_.random(5, 5);   // => 5 (always returns 5)
_.random(5);      // => 0-5 (lower defaults to 0)
```

### Clamp with Undefined Bounds

```javascript
_.clamp(10);           // => 10 (no bounds)
_.clamp(10, 5);        // => 10 (only lower bound, no effect)
_.clamp(10, undefined, 5); // => 5 (only upper bound)
```

### InRange with Reversed Bounds

```javascript
_.inRange(3, 5, 1);   // => true (automatically handles reversed)
// Equivalent to _.inRange(3, 1, 5)
```
