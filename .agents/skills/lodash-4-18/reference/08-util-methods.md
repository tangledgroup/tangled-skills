# Util Methods (34 methods)

General utility functions for function creation, iteration, and common patterns.

## Function Creation

### `_.attempt(func, [args])`

Attempts to invoke func, returning { error, value } object.

```javascript
function fn() { throw new Error('Oops'); }

const result = _.attempt(fn);
console.log(result.error);  // => Error: Oops
console.log(result.value);  // => undefined
```

### `_.cond(pairs)`

Creates a function that evaluates predicates in order, returning first matching result.

```javascript
function greet({ type, name }) {
  return `Hello ${name}!`;
}

function welcome({ type, name }) {
  return `Welcome back, ${name}!`;
}

const greetUser = _.cond([
  [{ 'type': 'returning' }, welcome],
  [{ 'type': 'new' }, greet]
]);

greetUser({ 'type': 'new', 'name': 'Fred' }); // => 'Hello Fred!'
```

### `_.conforms(source)`

Creates function that checks if object conforms to source predicates.

```javascript
var conformTo = _.conforms({
  'a': n => n > 1,
  'b': n => n < 3
});

conformTo({ 'a': 2, 'b': 2 }); // => true
conformTo({ 'a': 1, 'b': 2 }); // => false
```

### `_.constant(value)`

Creates function that always returns value.

```javascript
var object = { 'a': 1 };
const fn = _.constant(object);

fn() === object; // => true (same reference)
```

### `_.defaultTo(value, defaultValue)`

Returns value if not null/undefined, otherwise defaultValue.

```javascript
_.defaultTo(1, 10);      // => 1
_.defaultTo(null, 10);   // => 10
_.defaultTo(undefined, 10); // => 10
```

### `_.identity(value)`

Returns value unchanged (useful as default iteratee).

```javascript
var fn = _.identity;
fn('abc'); // => 'abc'
```

### `_.iteratee([func=_.identity])`

Creates iteratee function (supports shorthands like object, string).

```javascript
var mapAge = _.iteratee(function(o) {
  return o.age;
});

mapAge({ 'user': 'fred', 'age': 40 }); // => 40

// Shorthand support
_.iteratee('age');        // Property accessor
_.iteratee({ 'age': 40 }); // Matches predicate
```

### `_.matches(source)`

Creates function that checks if object matches source properties.

```javascript
var matches = _.matches({ 'a': 1, 'b': 2 });

matches({ 'a': 1, 'b': 2, 'c': 3 }); // => true
matches({ 'a': 1, 'b': 1 });         // => false
```

### `_.matchesProperty(path, srcValue)`

Creates function that checks if property at path equals srcValue.

```javascript
var matches = _.matchesProperty('age', 36);

matches({ 'user': 'barney', 'age': 36 }); // => true
matches({ 'user': 'fred', 'age': 40 });   // => false
```

### `_.method(path, [args])`

Creates function that invokes method at path with args.

```javascript
var array = ['a', 'b', 'c'];
var invoke = _.method('join');

invoke(array, ','); // => 'a,b,c'
```

### `_.methodOf(object, [args])`

Creates function that invokes method on object.

```javascript
var object = {
  'pow': Math.pow,
  'log': Math.log
};

var invoke = _.methodOf(object);
invoke('pow', 2, 3); // => 8 (2^3)
```

### `_.noop()`

No operation function (useful as callback placeholder).

```javascript
const fn = _.noop;
fn('a', 'b', undefined); // => undefined (does nothing)
```

### `_.stubArray()`

Returns empty array.

```javascript
_.stubArray(); // => []
```

### `_.stubFalse()`

Returns false.

```javascript
_.stubFalse(); // => false
```

### `_.stubObject()`

Returns empty object.

```javascript
_.stubObject(); // => {}
```

### `_.stubString()`

Returns empty string.

```javascript
_.stubString(); // => ''
```

### `_.stubTrue()`

Returns true.

```javascript
_.stubTrue(); // => true
```

## Composition

### `_.flow([funcs])`

Creates function that composes funcs from left to right.

```javascript
function greet(name) { return 'hi ' + name; }
function exclaim(statement) { return statement + '!'; }

var greetExclaim = _.flow([greet, exclaim]);
greetExclaim('fred'); // => 'hi fred!'
```

### `_.flowRight([funcs])`

Creates function that composes funcs from right to left.

```javascript
function greet(name) { return 'hi ' + name; }
function exclaim(statement) { return statement + '!'; }

var greetExclaim = _.flowRight([greet, exclaim]);
greetExclaim('fred'); // => 'hi fred!' (same result, different order)
```

### `_.nthArg([n=0])`

Creates function that returns nth argument.

```javascript
var getSecond = _.nthArg(1);
getSecond('a', 'b', 'c'); // => 'b'
```

### `_.over([iteratees=[_.identity]])`

Creates function that invokes iteratees and returns results as array.

```javascript
var over = _.over([Math.round, Math.ceil]);
over(4.2); // => [4, 5]
```

### `_.overEvery([predicates=[_.identity]])`

Creates function that returns true if ALL predicates pass.

```javascript
var overEvery = _.overEvery([_.isBoolean, _.isString]);
overEvery(true);   // => false (boolean but not string)
overEvery('true'); // => false (string but not boolean)
```

### `_.overSome([predicates=[_.identity]])`

Creates function that returns true if ANY predicate passes.

```javascript
var overSome = _.overSome([_.isBoolean, _.isString]);
overSome(true);   // => true (is boolean)
overSome('true'); // => true (is string)
```

## Property Access

### `_.property(path)`

Creates function that gets property at path.

```javascript
var getAge = _.property('age');
getAge({ 'user': 'fred', 'age': 40 }); // => 40

// Nested path
var getName = _.property('data.name');
getName({ 'data': { 'name': 'Fred' } }); // => 'Fred'
```

### `_.propertyOf(object)`

Creates function that gets properties from object.

```javascript
var food = { 'apple': 1, 'banana': 2 };
var getApple = _.propertyOf(food);

getApple('apple'); // => 1
getApple('orange'); // => undefined
```

### `_.toPath(value)`

Converts value to property path array.

```javascript
_.toPath('a.b.c');        // => ['a', 'b', 'c']
_.toPath(['a', 'b', 'c']); // => ['a', 'b', 'c']
_.toPath('a[0].b');       // => ['a', '0', 'b']
```

## Mixing

### `_.mixin([object=lodash], source, [options={ }])`

Adds methods from source to object (and prototype if chainable).

**Options:**
- `chain`: Add to lodash.prototype for chaining

```javascript
function view() { console.log('Viewing'); }

_.mixin({ 'view': view });
_([]).view(); // => Logs 'Viewing'
```

### `_.noConflict()`

Releases underscore from global variable (browser only).

```javascript
var lodash = _.noConflict();
// underscore is restored, use lodash instead
```

### `_.runInContext([context=root])`

Creates new lodash instance with given context.

```javascript
var _ = _.runInContext();
_.VERSION; // => '4.18.1'
```

## Iteration

### `_.times(n, [iteratee=_.identity])`

Invokes iteratee n times with index as argument.

```javascript
_.times(3, function(n) { console.log(n); });
// => Logs 0, 1, 2

var squares = _.times(4, n => n * n);
// => [0, 1, 4, 9]
```

## Unique ID

### `_.uniqueId([prefix=''])`

Generates unique ID with optional prefix.

```javascript
_.uniqueId('contact_'); // => 'contact_104'
_.uniqueId();           // => '105'
```

## Common Patterns

### Function Composition Pipeline

```javascript
// Transform data through pipeline
const process = _.flow([
  _.trim,
  _.toLower,
  str => str.split(' '),
  words => words.map(_.capitalize),
  words => words.join(' ')
]);

process('  hello world  '); // => 'Hello World'
```

### Conditional Logic with Cond

```javascript
const handleStatus = _.cond([
  [{ status: 'pending' }, () => sendReminder()],
  [{ status: 'active' }, () => processOrder()],
  [{ status: 'completed' }, () => sendConfirmation()],
  [_.stubTrue, () => handleError()] // Default case
]);

handleStatus({ status: 'active' }); // => processOrder()
```

### Property Accessors

```javascript
// Create reusable accessors
const getName = _.property('name');
const getNested = _.property('data.user.name');

users.map(getName);           // ['Fred', 'Barney']
response.map(getNested);      // Extract nested values
```

### Predicate Combination

```javascript
// Combine multiple predicates
const isValidUser = _.overEvery([
  o => o.email,
  o => o.age >= 18,
  o => !o.banned
]);

// Any condition matches
const isSpecial = _.overSome([
  o => o.vip,
  o => o.premium,
  o => o.legacy
]);
```

### Default Values

```javascript
// Chain default values
const value = _.defaultTo(
  _.defaultTo(userInput, configValue),
  defaultValue
);

// Or use nullish coalescing (ES2021)
const value = userInput ?? configValue ?? defaultValue;
```

### Stub Functions for Testing

```javascript
// Replace side effects with stubs during testing
component.onSubmit = _.stubTrue;
component.onError = _.noop;
component.getData = _.stubArray;
```
