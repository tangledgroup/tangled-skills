# Util Methods

Util methods provide utility functions for iteration, function generation, mixin support, and general-purpose helpers.

## Function Generators

### `_.iteratee([func=_.identity])`

Creates a function that invokes func with the (value, index|key, collection) arguments of the iterated elements. Supports all iteratee shorthands.

```js
var users = [
  { 'user': 'barney', 'age': 36 },
  { 'user': 'fred',   'age': 40 }
];
_.map(users, _.iteratee('user'));
// → ['barney', 'fred']

_.map(users, _.iteratee({ 'user': 'fred', 'age': 40 }));
// → [false, true]

_.filter(users, _.iteratee(function(o) {
  return o.age < 40;
}));
// → objects for ['barney']
```

### `_.matches(source)` / `_.matchesProperty(path, srcValue)`

Creates a function that performs partial deep comparison or property match. Useful for creating reusable predicates.

```js
var users = [
  { 'user': 'barney', 'age': 36, 'active': true },
  { 'user': 'fred',   'age': 40, 'active': false }
];

_.filter(users, _.matches({ 'age': 40, 'active': false }));
// → objects for ['fred']

_.find(users, _.matchesProperty('active', false));
// → { 'user': 'fred', 'age': 40, 'active': false }
```

### `_.property(path)` / `_.propertyOf(object)`

Creates a function that returns the value at path. `propertyOf` flips this — creates a function that takes a path and returns the value from object.

```js
var object = { 'a': { 'b': 2 } };
_.map([['a', 'b']], _.property);
// → [2]

var func = _.propertyOf(object);
func('a.b'); // → 2
```

### `_.method(path, [args])` / `_.methodOf(object, [args])`

Creates a function that invokes the method at path on iteratees. `methodOf` flips this.

```js
var objects = [
  { 'a': { 'b': _.constant(2) } },
  { 'a': { 'b': _.constant(1) } }
];
_.invokeMap(objects, _.method('a.b'));
// → [2, 1]
```

## Composition Helpers

### `_.over([iteratees=[_.identity]])`

Creates a function that invokes iteratees and returns their results as an array.

```js
var minMax = _.over([_.min, _.max]);
minMax([1, 2, 3, 4, 5]);
// → [1, 5]
```

### `_.overEvery([predicates=[_.identity]])` / `_.overSome([predicates=[_.identity]])`

Creates a function that returns true if all (`overEvery`) or any (`overSome`) predicates return truthy.

```js
var validate = _.overEvery(
  _.partial(_.isLength, _),
  _.partial(_.lt, _, 5)
);
validate([1, 2, 3]); // → true
validate([1, 2, 3, 4, 5]); // → false
```

### `_.cond(pairs)`

Creates a function that iterates over pairs and invokes the first function whose predicate returns truthy.

```js
var func = _.cond([
  [_.partial(_.matchesProperty, 'active', true), _.constant('touched')],
  [_.partial(_.matchesProperty, 'active', false), _.constant('untouched')]
]);
func({ 'user': 'barney', 'active': true }); // → 'touched'
```

## Argument Helpers

### `_.nthArg([n=0])`

Creates a function that returns the nth argument it receives.

```js
var func = _.nthArg(1);
func('a', 'b', 'c'); // → 'b'
```

## Stub Functions

Return constant empty values. Useful as defaults and in testing.

```js
_.stubArray();   // → []
_.stubFalse();   // → false
_.stubObject();  // → {}
_.stubString();  // → ''
_.stubTrue();    // → true
```

## Identity and No-op

### `_.identity(value)`

Returns the first argument. Useful as a default iteratee.

```js
var object = { 'a': 1 };
_.map([1, 2, 3], _.identity); // → [1, 2, 3]
_.map(object, _.identity);    // → [1]
```

### `_.noop()`

A no-operation function. Useful as a default callback.

```js
var object = {};
_.forEach(object, _.noop);
```

### `_.constant(value)`

Creates a function that returns value. Useful for creating constant callbacks.

## Mixin

### `_.mixin([object=lodash], source, [options={}])`

Adds functions from source to lodash (or a custom object). Mixed-in functions may be used on chained objects. Options:
- `chain` — enable chaining for mixed-in functions (default: true)

```js
_.mixin({
  'capitalize': function(string) {
    return _.toUpper(_.first(string)) + string.slice(1);
  }
});
_.capitalize('fred'); // → 'Fred'

// Custom object
var object = { 'name': 'fred' };
_.mixin(object, {
  'greet': function() {
    return 'Hello, ' + this.name + '!';
  }
});
object.greet(); // → 'Hello, fred!'
```

## Context and Interception

### `_.runInContext([context=root])`

Creates a new lodash instance with the given context. Useful for sandboxing.

```js
var lodash = _.runInContext({});
lodash.template('hi <%= user %>!')({ 'user': 'fred' });
// → 'hi fred!'
```

### `_.tap(value, interceptor)`

Invokes interceptor with value, then returns value. Useful for debugging or side effects in chains.

```js
_.chain([1, 2, 3])
  .tap(function(array) { console.log(array); })
  .reverse()
  .value();
// → [3, 2, 1] (logs [1, 2, 3] during chain)
```

### `_.thru(value, interceptor)`

Like tap but passes the result of interceptor to the next chained method.

```js
_.thru(1, function(n) { return n + 1; }); // → 2

_.chain([1, 2, 3])
  .thru(function(array) { return array.length; })
  .value(); // → 3
```

## Version and Conflict

### `_.VERSION`

The semantic version number.

```js
_.VERSION; // → '4.18.1'
```

### `_.noConflict()`

Reverts the global `_` variable to its previous value, returning a reference to the lodash function.

```js
var lodash = _.noConflict();
lodash.VERSION; // → '4.18.1'
```
