# Function Methods (24 methods)

Utilities for creating and manipulating functions, including binding, currying, throttling, and composition patterns.

## Call Count Restrictions

### `_.after(n, func)`

Creates a function that invokes `func` once called n or more times. Opposite of `_.before`.

**Since:** 0.1.0

```javascript
var saves = ['profile', 'settings'];
var done = _.after(saves.length, function() {
  console.log('done saving!');
});

_.forEach(saves, function(type) {
  asyncSave({ 'type': type, 'complete': done });
});
// => Logs 'done saving!' after two async saves complete
```

### `_.before(n, func)`

Creates a function that invokes `func` while called less than n times. Subsequent calls return last result.

**Since:** 3.0.0

```javascript
var fahrenheit = _.before(3, function() {
  console.log('Called');
  return Math.random();
});

fahrenheit(); // => Logs 'Called'
fahrenheit(); // => Logs 'Called'
fahrenheit(); // => Returns second result without logging
```

## Arity Control

### `_.ary(func, [n=func.length])`

Creates a function that invokes `func` with up to n arguments, ignoring additional ones.

**Since:** 3.0.0

```javascript
_.map(['6', '8', '10'], _.ary(parseInt, 1));
// => [6, 8, 10]
```

### `_.unary(func)`

Creates a function that invokes `func` with at most one argument.

**Since:** 3.0.0

```javascript
var fn = _.unary(function() {
  return _.toArray(arguments);
});

fn(1, 2, 3);
// => [1]
```

## Binding

### `_.bind(func, thisArg, [partials])`

Creates a function that invokes `func` with `this` bound to `thisArg` and partials prepended.

**Note:** Unlike native `Function#bind`, doesn't set "length" property.

**Since:** 0.1.0

```javascript
function greet(greeting, punctuation) {
  return greeting + ' ' + this.user + punctuation;
}

var object = { 'user': 'fred' };
var bound = _.bind(greet, object, 'hi');
bound('!'); // => 'hi fred!'

// With placeholder
var bound = _.bind(greet, object, _, '!');
bound('hi'); // => 'hi fred!'
```

### `_.bindKey(object, key, [partials])`

Creates a function that invokes method at `object[key]`. Method can be redefined after binding.

**Since:** 0.10.0

```javascript
var object = {
  'user': 'fred',
  'greet': function(greeting, punctuation) {
    return greeting + ' ' + this.user + punctuation;
  }
};

var bound = _.bindKey(object, 'greet', 'hi');
bound('!'); // => 'hi fred!'

object.greet = function(greeting, punctuation) {
  return greeting + 'ya ' + this.user + punctuation;
};

bound('!'); // => 'hiya fred!' (uses new method)
```

### `_.bindAll(object, methodNames)`

Binds methods to object, setting each as a bound function.

**Since:** 2.0.0

```javascript
var view = {
  'label': 'docs',
  'getLabel': function() {
    return this.label;
  }
};

Object.assign(view, _.bindAll(view, ['getLabel']));
```

## Currying

### `_.curry(func, [arity=func.length])`

Creates a curried function that accepts arguments in batches.

**Since:** 2.0.0

```javascript
var abc = function(a, b, c) {
  return [a, b, c];
};

var curried = _.curry(abc);

curried(1)(2)(3);    // => [1, 2, 3]
curried(1, 2)(3);    // => [1, 2, 3]
curried(1, 2, 3);    // => [1, 2, 3]

// With placeholders
curried(1)(_, 3)(2); // => [1, 2, 3]
```

### `_.curryRight(func, [arity=func.length])`

Like `_.curry` but arguments applied from right to left.

**Since:** 3.0.0

```javascript
var add = function(a, b, c) {
  return a + b + c;
};

var curried = _.curryRight(add);

curried(3)(2)(1);     // => 6
curried(2, 1)(3);     // => 6
curried(1, 2, 3);     // => 6
curried(_, 2, 1)(3);  // => 6 (with placeholder)
```

## Debouncing and Throttling

### `_.debounce(func, [wait=0], [options={ }])`

Creates a debounced function that delays invoking `func` until after wait milliseconds have elapsed since last call.

**Options:**
- `leading`: Invoke on leading edge
- `trailing`: Invoke on trailing edge
- `maxWait`: Max time to wait between invocations

**Since:** 0.1.0

```javascript
var lazyLoad = _.debounce(function() {
  console.log('loaded');
}, 300);

$(window).on('scroll', lazyLoad);

// With options
var async = _.debounce(fetchData, 1000, { 'leading': true, 'trailing': false });
```

**Use case:** Search input that waits for user to stop typing.

### `_.throttle(func, [wait=0], [options={ }])`

Creates a throttled function that invokes at most once per wait milliseconds.

**Options:** Same as debounce (leading, trailing)

**Since:** 0.1.0

```javascript
var throttled = _.throttle(doStuff, 100);
_.times(5, throttled); // doStuff called once every 100ms

// With options
var throttled = _.throttle(move, 200, { 'trailing': false });
```

**Use case:** Limit scroll event handlers to fixed rate.

### `_.defer(func, [args])`

Defers invoking `func` until next millisecond (via setTimeout).

**Since:** 4.6.1

```javascript
_.defer(function() { console.log('deferred'); });
// => Logs after other synchronous statements
```

### `_.delay(func, wait, [args])`

Invokes `func` after wait milliseconds with given arguments.

**Since:** 0.1.0

```javascript
_.delay(function() { console.log('delayed'); }, 300);
// => Logs after 300ms
```

## Flipping and Reordering

### `_.flip(func)`

Creates a function that invokes `func` with arguments reversed.

**Since:** 4.0.0

```javascript
var flipped = _.flip(function(who, what) {
  return who + ' says ' + what;
});

flipped('Fred', 'Hello'); // => 'Hello says Fred'
```

### `_.rearg(func, indexes)`

Creates a function that invokes `func` with arguments at specified indexes.

**Since:** 4.0.0

```javascript
var rearged = _.rearg(function(a, b, c) {
  return [a, b, c];
}, [2, 0, 1]);

rearged('a', 'b', 'c'); // => ['c', 'a', 'b']
```

## Memoization

### `_.memoize(func, [resolver])`

Creates a memoized function that caches results based on first argument (or resolver result).

**Since:** 0.1.0

```javascript
var factorial = _.memoize(function(n) {
  console.log('computing', n);
  return n < 2 ? 1 : n * factorial(n - 1);
});

factorial(3); // => Computes and logs
factorial(3); // => Returns cached result (no log)
factorial(4); // => Computes and logs

// Clear cache
factorial.cache = {};
```

## Negation

### `_.negate(predicate)`

Creates a function that negates predicate result.

**Since:** 3.0.0

```javascript
var isEven = _.negate(_.isOdd);
isEven(2); // => true
isEven(3); // => false
```

## Once Execution

### `_.once(func)`

Creates a function that invokes `func` only once, returning result on subsequent calls.

**Since:** 0.1.0

```javascript
var initialize = _.once(createApplication);
initialize(); // Creates application
initialize(); // Returns same instance (doesn't recreate)
```

## Partial Application

### `_.partial(func, [partials])`

Creates a function that invokes `func` with partials prepended to arguments.

**Since:** 0.1.0

```javascript
var sayHello = function(greeting, name) {
  return greeting + ' ' + name;
};

var greetFred = _.partial(sayHello, 'hello');
greetFred('Fred'); // => 'hello Fred'

// With placeholder for later argument
var greet = _.partial(sayHello, _, 'Fred');
greet('hi'); // => 'hi Fred'
```

### `_.partialRight(func, [partials])`

Like `_.partial` but partials appended to arguments.

**Since:** 3.0.0

```javascript
var sayHello = function(greeting, name) {
  return greeting + ' ' + name;
};

var greetFred = _.partialRight(sayHello, 'Fred');
greetFred('hello'); // => 'hello Fred'
```

## Rest and Spread

### `_.rest(func, [start=func.length-1])`

Creates a function that invokes `func` with rest of arguments as array.

**Since:** 4.0.0

```javascript
var say = _.rest(function(what, names) {
  return what + ' ' + names.join(', ');
});

say('hello', 'Fred', 'Barney', 'Pebbles'); // => 'hello Fred, Barney, Pebbles'
```

### `_.spread(func, [start=0])`

Creates a function that invokes `func` with array elements as arguments.

**Since:** 4.0.0

```javascript
var add = function(a, b) {
  return 'a: ' + a + ', b: ' + b;
};

var spreadAdd = _.spread(add);
spreadAdd([1, 2]); // => 'a: 1, b: 2'
```

## Wrapping

### `_.wrap(value, [wrapper=identity])`

Creates a function that invokes wrapper with value as first argument.

**Since:** 0.1.0

```javascript
var p = _.wrap(_.escape, function(func, text) {
  return '<p>' + func(text) + '</p>';
});

p('fred, barney, & pebbles'); // => '<p>fred, barney, &amp; pebbles</p>'
```

### `_.overArgs(func, [transforms=[_.identity]])`

Creates a function that invokes func with arguments transformed by corresponding transforms.

**Since:** 4.0.0

```javascript
var mod = _.overArgs(function(x, y) {
  return Math.sin(x) / Math.cos(y);
}, [Math.floor, Math.ceil]);

mod(4.2, 6.1); // => Uses floor(4.2)=4 and ceil(6.1)=7
```

## Placeholder Value

Lodash provides `_.placeholder` (defaults to `_`) for partial application:

```javascript
// All these use placeholder
var bindPlaceholder = _.bind(func, object, _, arg2);
var curryPlaceholder = curried(_, 2)(1);
var partialPlaceholder = _.partial(func, _, arg2);
```

## Performance Considerations

- **Debounce vs Throttle:** Use debounce for "do after user stops", throttle for "limit to X times per second"
- **Memoization:** Be careful with memory - memoized functions grow unbounded without cache management
- **Binding:** Prefer `_.bindKey` when methods might be redefined
- **Currying:** Useful for creating specialized functions from general ones

## Common Patterns

### Event Handler Debouncing

```javascript
const handleScroll = _.debounce(() => {
  updateUI();
}, 150);

window.addEventListener('scroll', handleScroll);
```

### API Call Throttling

```javascript
const fetchUser = _.throttle(() => {
  api.getUser().then(updateDisplay);
}, 1000);

input.addEventListener('input', fetchUser);
```

### Function Composition

```javascript
// Chain transformations
const process = _.flow(
  _.trim,
  _.toLower,
  capitalizeFirstLetter
);

process('  HELLO world  '); // => 'Hello world'
```

### Retry Logic with After

```javascript
const onComplete = _.after(3, () => {
  console.log('All retries complete');
});

function retryFetch() {
  fetch('/api/data')
    .catch(retryFetch)
    .finally(onComplete);
}
```
