# Function Methods

Function methods provide higher-order function utilities: currying, partial application, debouncing, throttling, memoization, and composition.

## Currying

### `_.curry(func, [arity=func.length])` / `_.curryRight(func)`

Creates a function that accepts arguments curried from left-to-right (or right-to-left for `curryRight`). Returns a new function until all arguments are provided.

```js
var abc = function(a, b, c) {
  return [a, b, c];
};
var curried = _.curry(abc);

curried(1)(2)(3);       // → [1, 2, 3]
curried(1, 2)(3);        // → [1, 2, 3]
curried(1, 2, 3);        // → [1, 2, 3]
```

### `_.curryN(func, n)` (lodash/fp)

Curries a function to a specific arity. Useful when the target function has variable arity.

## Partial Application

### `_.partial(func, [partials])` / `_.partialRight(func, [partials])`

Creates a function that invokes func with partials prepended (or appended for `partialRight`). Uses `__` placeholder for unfilled positions.

```js
var greet = function(greeting, name) {
  return greeting + ' ' + name;
};
var sayHello = _.partial(greet, 'hello');
sayHello('fred'); // → 'hello fred'

// Using placeholder
var greetFred = _.partial(greet, _, 'fred');
greetFred('hi'); // → 'hi fred'
```

### `_.rearg(func, indexes)`

Creates a function that invokes func with arguments arranged according to indexes.

```js
var rearged = _.rearg(function(a, b, c) {
  return [a, b, c];
}, [2, 0, 1]);
rearged('a', 'b', 'c'); // → ['c', 'a', 'b']
```

### `_.flip(func)`

Creates a function that invokes func with arguments reversed.

```js
var flipped = _.flip(function(a, b) {
  return [a, b];
});
flipped('a', 'b'); // → ['b', 'a']
```

## Rate Limiting

### `_.debounce(func, [wait=0], [options={}])`

Creates a function that delays invoking func until after wait milliseconds have elapsed since the last time it was invoked. Useful for search inputs and resize handlers.

Options:
- `leading` — invoke on the leading edge (default: false)
- `maxWait` — maximum time func is allowed to be delayed
- `trailing` — invoke on the trailing edge (default: true)

```js
var lazyLayout = _.debounce(function() {
  console.log('layout');
}, 300);

// Invoking lazyLayout will delay the call
lazyLayout();
// Cancel the trailing edge invocation
lazyLayout.cancel();
// Execute pending invocation immediately
lazyLayout.flush();
```

### `_.throttle(func, [wait=0], [options={}])`

Creates a function that invokes func no more than once per every wait milliseconds. Unlike debounce, throttle fires at regular intervals during sustained calls.

Options:
- `leading` — invoke on leading edge (default: true)
- `trailing` — invoke on trailing edge (default: true)

```js
$.element.on('scroll', _.throttle(updatePosition, 100));
```

## Memoization

### `_.memoize(func, [resolver])`

Creates a function that memoizes the result of func. Subsequent calls with the same first argument return the cached result. The resolver determines the cache key (default: first argument).

```js
var fibonacci = _.memoize(function(n) {
  return n < 2 ? n : fibonacci(n - 1) + fibonacci(n - 2);
});
fibonacci(100); // Fast — uses cached results
```

Clear the cache with `fibonacci.cache.clear()`. The cache is a `Map`-backed object with `cache.get(key)`, `cache.set(key, value)`, and `cache.delete(key)`.

## Control Flow

### `_.before(n, func)` / `_.after(n, func)`

Creates a function that invokes func once after being called n times (`after`) or before being called n times (`before`).

```js
var render = _.after(counties.length, function() {
  view.render();
});
counties.forEach(function(county) {
  county.async({ 'success': render });
});

var greet = _.before(3, function(name) {
  console.log('Hello, ' + name);
});
greet('fred'); // → 'Hello, fred'
greet('pebbles'); // → 'Hello, pebbles'
greet('barney'); // (no longer invokes)
```

### `_.once(func)`

Creates a function that is restricted to invoking func once. Subsequent calls return the result of the first invocation.

```js
var initialize = _.once(createApplication);
initialize();
initialize(); // Returns result of first call, doesn't re-execute
```

## Binding

### `_.bind(func, thisArg, [partials])`

Creates a function that invokes func with this bound to thisArg and partials prepended. Supports placeholders.

```js
var greet = function(greeting) {
  return greeting + ': ' + this.name;
};
var Fred = { 'name': 'fred' };
var bound = _.bind(greet, Fred, 'hi');
bound(); // → 'hi: fred'
```

### `_.bindAll(object, methodNames)`

Binds methods of object to the object itself. Useful for event handlers.

```js
var buttonView = {
  'label': 'docs',
  'onClick': function() { console.log('clicked: ' + this.label); }
};
_.bindAll(buttonView, 'onClick');
jQuery('#button').on('click', buttonView.onClick);
```

### `_.bindKey(object, key, [partials])`

Like `bind` but looks up the method at call time (late binding).

## Arity Control

### `_.ary(func, [n=func.length])`

Creates a function that accepts up to n arguments, ignoring extras.

```js
var ary = _.ary(function(a, b, c) {
  return [a, b, c];
}, 2);
ary(1, 2, 3); // → [1, 2, undefined]
```

### `_.unary(func)`

Creates a function that accepts up to one argument. Alias of `_.ary(func, 1)`.

### `_.rest(func, [start=func.length-1])` / `_.spread(func, [start=0])`

`rest` creates a function that invokes func with the rest of its arguments as an array. `spread` does the inverse — spreads an array argument into individual arguments.

```js
var say = _.rest(function(what, names) {
  return what + ' ' + _.initial(names).join(', ') +
    (_.size(names) > 1 ? ', & ' : '') + _.last(names);
});
say('hello', 'fred', 'barney', 'pebbles');
// → 'hello fred, barney, & pebbles'
```

## Negation and Identity

### `_.negate(predicate)`

Creates a function that returns the negation of predicate's result.

```js
_.filter([1, 2, 3], _.negate(_.isOdd)); // → [2]
```

### `_.constant(value)` / `_.identity(value)`

`constant` always returns value. `identity` returns its first argument. Both are useful as iteratees and defaults.

```js
var objects = _.times(2, _.constant({ 'a': 1 }));
_.map(objects, _.property('a')); // → [1, 1]

_.map([1, 2, 3], _.identity); // → [1, 2, 3]
```

## Wrapping

### `_.wrap(value, [wrapper=identity])`

Creates a function that invokes wrapper with value as the first argument.

```js
var hello = _.wrap(_.escape, function(func, string) {
  return 'Hello, ' + func(string) + '!';
});
hello('fred, barney, & pebbles');
// → 'Hello, fred, barney, &amp; pebbles!'
```

## Composition

### `_.flow([funcs])` / `_.flowRight([funcs])`

Creates a function that returns the result of executing funcs left-to-right (`flow`) or right-to-left (`flowRight`). Each function's return value is passed as the argument to the next.

```js
var add = function(a, b) { return a + b; };
var multiply = function(a, b) { return a * b; };

var addThenMultiply = _.flow([add, multiply]);
addThenMultiply(1, 2, 3); // → 9  ((1+2) * 3)

var multiplyThenAdd = _.flowRight([add, multiply]);
multiplyThenAdd(1, 2, 3); // → 5  (1 + (2*3))
```

## Deferred Execution

### `_.defer(func, [args])` / `_.delay(func, wait, [args])`

`defer` defers invoking func until the current call stack has cleared (like `setTimeout(func, 0)`). `delay` invokes after wait milliseconds.

```js
_.defer(function(text) { console.log(text); }, 'deferred');
// → 'deferred' (after current call stack clears)

_.delay(function(text) { console.log(text); }, 1000, 'later');
// → 'later' (after 1 second)
```
