# Seq Methods (Chaining - 12 methods)

Lodash chaining API for fluent method composition. Chaining enables method calls to be chained together, with results finalized via `.value()`.

## Chain Creation

### `_(value)` / `_.chain(value)`

Creates lodash wrapper around value, enabling method chaining.

```javascript
// Implicit chaining (auto-wraps)
_(users)
  .filter('active')
  .map('name')
  .value(); // => ['Fred', 'Barney']

// Explicit chaining
_.chain(users)
  .filter(user => user.active)
  .map(user => user.name)
  .value(); // => ['Fred', 'Barney']
```

**Difference:** `_(value)` creates wrapper immediately, `_.chain(value)` is explicit but equivalent.

## Chaining Methods

### `_.prototype.at([paths])`

Gets values at paths (chaining version of `_.at`).

```javascript
var object = { 'a': [{ 'b': { 'c': 3 } }], 'd': 4 };

_(object)
  .at(['a[0].b.c', 'd'])
  .value(); // => [3, 4]
```

### `_.prototype.chain()`

Re-wraps value for additional chaining after unwrapping.

```javascript
var wrapped = _([1, 2, 3])
  .map(n => n * 2)
  .value(); // => [2, 4, 6] (unwrapped)

// Re-wrap for more chaining
_(wrapped)
  .chain()
  .filter(n => n > 3)
  .value(); // => [4, 6]
```

### `_.prototype.commit()`

Creates new wrapper around current value (useful after mutations).

```javascript
var array = [1, 2, 3];
var wrapped = _(array);

wrapped
  .push(4)
  .commit() // Creates new wrapper with updated value
  .value(); // => [1, 2, 3, 4]
```

### `_.prototype.next()`

Returns next value in iterator sequence (for Symbol.iterator).

```javascript
var wrapped = _([1, 2, 3]);
wrapped.next(); // => { done: false, value: 1 }
wrapped.next(); // => { done: false, value: 2 }
```

### `_.prototype.plant(value)`

Replaces wrapped value and returns wrapper for chaining.

```javascript
_(users)
  .filter('active')
  .plant([newUser])
  .map('name')
  .value(); // => Includes newUser's name
```

### `_.prototype.reverse()`

Reverses array (chaining version of `_.reverse`).

```javascript
_([1, 2, 3])
  .reverse()
  .value(); // => [3, 2, 1]
```

### `_.prototype.value()` / `_.prototype.toJSON()` / `_.prototype.valueOf()`

Extracts value from wrapper, ending the chain.

```javascript
_(users)
  .filter('active')
  .map('name')
  .value(); // => ['Fred', 'Barney'] (Array)

// All these are equivalent
_(value).value();
_(value).toJSON();
_(value).valueOf();
```

## Intermediate Operations

### `_.tap(value, interceptor)`

Invokes interceptor with value and returns value (for debugging/intermediate ops).

```javascript
_(users)
  .filter('active')
  .tap(console.log) // Logs intermediate result
  .map('name')
  .value();
```

**Use case:** Debugging chain steps or performing side effects.

### `_.thru(value, interceptor)`

Invokes interceptor with value and returns result (for transformations).

```javascript
function add(n) { return n + 1; }

_(1)
  .thru(add)
  .thru(add)
  .value(); // => 3

// More complex transformation
_(data)
  .filter('active')
  .thru(items => items.slice(0, 10)) // Limit to 10
  .map('name')
  .value();
```

**Difference from tap:** `tap` returns original value, `thru` returns interceptor's result.

## Iterator Protocol

### `_.prototype[Symbol.iterator]()`

Makes lodash wrapper iterable (ES2015).

```javascript
var wrapped = _([1, 2, 3]);

for (var item of wrapped) {
  console.log(item); // Logs 1, 2, 3
}

// Spread operator
..._([1, 2, 3]); // => [1, 2, 3]
```

## Chaining Examples

### Basic Filtering and Mapping

```javascript
// Get names of active users over 18
const activeAdultNames = _(users)
  .filter(user => user.active && user.age >= 18)
  .map('name')
  .value();
```

### Complex Transformation Pipeline

```javascript
const result = _(orders)
  .filter(order => order.status === 'completed')
  .map(order => ({
    id: order.id,
    total: order.items.reduce((sum, item) => sum + item.price, 0)
  }))
  .sortBy('total')
  .reverse()
  .take(10)
  .value();
```

### Debugging with tap

```javascript
const result = _(data)
  .filter(validates)
  .tap(filtered => console.log('After filter:', filtered.length))
  .map(transform)
  .tap(transformed => console.log('After transform:', transformed.length))
  .groupBy('category')
  .value();
```

### Conditional Operations with thru

```javascript
const process = (data, limit) => _(data)
  .filter('active')
  .thru(items => limit ? items.slice(0, limit) : items)
  .map('name')
  .value();

process(users, 10); // Limited to 10
process(users);     // No limit
```

### Aggregation with Chaining

```javascript
const stats = _(users)
  .filter('active')
  .groupBy(age => age >= 18 ? 'adult' : 'minor')
  .mapValues(group => ({
    count: group.length,
    avgAge: _.meanBy(group, 'age')
  }))
  .value();

// => { adult: { count: 50, avgAge: 32 }, minor: { count: 10, avgAge: 15 } }
```

## Implicit vs Explicit Chaining

### Implicit Chaining (Recommended)

```javascript
// Simple, readable
_(data)
  .filter('active')
  .map('name')
  .value();
```

### Explicit Chaining

```javascript
// More verbose but explicit
_.chain(data)
  .filter(user => user.active)
  .map(user => user.name)
  .value();
```

**When to use explicit:** When you want to be clear about chaining or need to chain after non-chainable operations.

## Chaining vs Non-Chaining

### Non-Chaining (Recommended for simple cases)

```javascript
// Direct, efficient
const names = _.map(_.filter(users, 'active'), 'name');
```

### Chaining (Better for complex pipelines)

```javascript
// More readable for multiple operations
const names = _(users)
  .filter('active')
  .sortBy('name')
  .map('name')
  .value();
```

**Performance:** Non-chaining is slightly faster (no wrapper overhead), but chaining improves readability for complex transformations.

## Common Patterns

### Lazy Evaluation

Chaining doesn't execute until `.value()` is called:

```javascript
const wrapped = _(largeDataset)
  .filter('active')
  .map('name');

// Nothing executed yet
wrapped.value(); // Now executes filter and map
```

### Reusable Chains

```javascript
const getActiveUserNames = _(users)
  .filter('active')
  .map('name');

getActiveUserNames.value(); // Execute when needed
```

### Combining with Non-Lodash Methods

```javascript
_(data)
  .filter(lodashFilter)
  .thru(customTransformation)
  .map(lodashMap)
  .value();
```
