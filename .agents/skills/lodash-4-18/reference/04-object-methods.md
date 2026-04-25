# Object Methods (46 methods)

Utilities for working with object properties, including assignment, cloning, iteration, and manipulation.

## Assignment

### `_.assign(object, [sources])`

Assigns own enumerable string-keyed properties from sources to object. **Mutates object.** Later sources overwrite earlier ones.

**Since:** 0.10.0

```javascript
_.assign({ 'a': 1 }, { 'b': 2 }, { 'a': 3 });
// => { 'a': 3, 'b': 2 }

// Only copies own properties (not prototype)
function Foo() { this.a = 1; }
Foo.prototype.b = 2;
_.assign({}, new Foo()); // => { 'a': 1 }
```

### `_.assignIn(object, [sources])` / `_.extend`

Like `_.assign` but copies own AND inherited properties. **Mutates object.**

**Since:** 4.0.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;
_.assignIn({}, new Foo()); // => { 'a': 1, 'b': 2 }
```

### `_.assignInWith(object, sources, [customizer])` / `_.extendWith`

Like `_.assignIn` but accepts customizer function for value transformation.

**Since:** 4.0.0

```javascript
function customizer(objValue, srcValue) {
  return _.isUndefined(objValue) ? srcValue : objValue;
}
_.assignInWith({}, { 'a': 1 }, { 'a': 2 }, customizer);
// => { 'a': 1 } (keeps first value)
```

### `_.assignWith(object, sources, [customizer])`

Like `_.assign` but accepts customizer function.

**Since:** 4.0.0

```javascript
function customizer(objValue, srcValue) {
  return _.isArray(srcValue) ? _.concat(objValue || [], srcValue) : srcValue;
}
var defaults = _.partialRight(_.assignWith, customizer);
defaults({ 'a': [1] }, { 'b': [2] }, { 'a': [3] });
// => { 'a': [1, 3], 'b': [2] }
```

### `_.defaults(object, [sources])`

Assigns properties from sources only where object property is undefined. **Mutates object.**

**Since:** 0.1.0

```javascript
_.defaults({ 'a': 1 }, { 'b': 2 }, { 'a': 3 });
// => { 'a': 1, 'b': 2 } (a=1 preserved)
```

### `_.defaultsDeep(object, [sources])`

Like `_.defaults` but recursively assigns default properties. **Mutates object.**

**Since:** 3.10.0

```javascript
_.defaultsDeep({ 'a': { 'b': 2 } }, { 'a': { 'b': 1, 'c': 3 } });
// => { 'a': { 'b': 2, 'c': 3 } } (b=2 preserved)
```

## Cloning

### `_.clone(value)`

Creates a shallow copy of value. Handles primitives, arrays, and plain objects.

**Since:** 0.1.0

```javascript
var object = { 'a': [1, 2], 'b': { 'c': 3 } };
var copy = _.clone(object);

copy.a[0] = 5;       // Modifies both (shallow)
copy.b.c = 4;        // Modifies both (shallow)
```

### `_.cloneDeep(value)`

Creates a deep copy of value. Recursively clones arrays and objects.

**Since:** 0.1.0

```javascript
var object = { 'a': [1, 2], 'b': { 'c': 3 } };
var copy = _.cloneDeep(object);

copy.a[0] = 5;       // Doesn't modify original
copy.b.c = 4;        // Doesn't modify original
```

### `_.cloneDeepWith(value, [customizer])`

Like `_.cloneDeep` but accepts customizer for specific types.

**Since:** 4.0.0

```javascript
function customizer(value) {
  if (_.isElement(value)) {
    return value.cloneNode(true);
  }
}
var element = document.body;
var clone = _.cloneDeepWith(element, customizer);
```

### `_.cloneWith(value, [customizer])`

Like `_.clone` but accepts customizer for specific types.

**Since:** 4.0.0

```javascript
function customizer(value) {
  if (_.isElement(value)) {
    return value.cloneNode(false);
  }
}
var element = document.body;
var clone = _.cloneWith(element, customizer);
```

## Creation

### `_.create(prototype, [properties])`

Creates object with specified prototype and optional properties.

**Since:** 2.3.0

```javascript
function Shape() { this.x = 0; this.y = 0; }
function Circle() { Shape.call(this); }
Circle.prototype = _.create(Shape.prototype, { 'constructor': Circle });

var circle = new Circle();
circle instanceof Circle; // => true
circle instanceof Shape;  // => true
```

## Property Access

### `_.at(object, [paths])`

Creates array of values at given paths.

**Since:** 1.0.0

```javascript
var object = { 'a': [{ 'b': { 'c': 3 } }], 'd': 4 };
_.at(object, ['a[0].b.c', 'd']);
// => [3, 4]
```

### `_.get(object, path, [defaultValue])`

Gets value at path of object. Returns defaultValue if not found.

**Since:** 3.2.0

```javascript
var object = { 'a': [{ 'b': { 'c': 3 } }] };

_.get(object, 'a[0].b.c');     // => 3
_.get(object, ['a', '0', 'b', 'c']); // => 3
_.get(object, 'a.b.c', 'default');   // => 'default'
```

**Path formats:**
- String: `'a.b.c'`, `'a[0].b'`
- Array: `['a', 'b', 'c']`

### `_.has(object, path)`

Checks if path is a direct property of object (not inherited).

**Since:** 2.4.1

```javascript
var object = { 'a': 1 };
Object.setPrototypeOf(object, { 'b': 2 });

_.has(object, 'a'); // => true
_.has(object, 'b'); // => false (inherited)
```

### `_.hasIn(object, path)`

Checks if path exists on object OR its prototype chain.

**Since:** 4.0.0

```javascript
var object = { 'a': 1 };
Object.setPrototypeOf(object, { 'b': 2 });

_.hasIn(object, 'a'); // => true
_.hasIn(object, 'b'); // => true (inherited)
```

### `_.invoke(object, path, [args])`

Invokes method at path with given arguments.

**Since:** 4.0.0

```javascript
var object = { 'a': [{ 'b': { 'c': [1, 2, 3] } }] };
_.invoke(object, 'a[0].b.c.join', '-');
// => '1-2-3'
```

### `_.result(object, path, [defaultValue])`

Gets value at path. If function, invokes it with (object, key) as arguments.

**Since:** 3.7.0

```javascript
var object = { 'a': [{ 'b': { 'c': _.constant(3) } }] };

_.result(object, 'a[0].b.c');     // => 3
_.result(object, 'x', 'default'); // => 'default'
```

### `_.set(object, path, value)`

Sets value at path of object. Creates intermediate objects as needed.

**Since:** 4.0.0

```javascript
var object = {};
_.set(object, 'a.b.c', 3);
console.log(object); // => { 'a': { 'b': { 'c': 3 } } }
```

### `_.setWith(object, path, value, [customizer])`

Like `_.set` but accepts customizer for creating intermediate objects.

**Since:** 4.0.0

```javascript
var object = {};
_.setWith(object, 'a.b.c', 3, Object.create);
console.log(object); // => { 'a': { 'b': { 'c': 3 } } } (with custom prototype)
```

### `_.unset(object, path)`

Removes property at path. Returns true if removed. **Mutates object.**

**Since:** 4.0.0

```javascript
var object = { 'a': [{ 'b': { 'c': 7 } }] };
_.unset(object, 'a[0].b.c');
console.log(object); // => { 'a': [{ 'b': {} }] }
```

### `_.update(object, path, updater)`

Gets value at path, updates it with function, sets result.

**Since:** 4.6.0

```javascript
var object = { 'a': [{ 'b': { 'c': 3 } }] };
_.update(object, 'a[0].b.c', n => n * 2);
console.log(object); // => { 'a': [{ 'b': { 'c': 6 } }] }
```

### `_.updateWith(object, path, updater, [customizer])`

Like `_.update` but accepts customizer for creating intermediate objects.

**Since:** 4.6.0

```javascript
var object = {};
_.updateWith(
  object,
  ['a', 'b', 'c'],
  n => n + 1,
  _.constant({})
);
console.log(object); // => { 'a': { 'b': { 'c': 1 } } }
```

## Iteration

### `_.forIn(object, [iteratee=_.identity])`

Iterates over own and inherited string-keyed properties.

**Since:** 0.1.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;

_.forIn(new Foo(), function(value, key) {
  console.log(key); // Logs 'a' then 'b'
});
```

### `_.forInRight(object, [iteratee=_.identity])`

Like `_.forIn` but iterates in reverse order.

**Since:** 3.0.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;

_.forInRight(new Foo(), function(value, key) {
  console.log(key); // Logs 'b' then 'a'
});
```

### `_.forOwn(object, [iteratee=_.identity])`

Iterates over own string-keyed properties only.

**Since:** 0.1.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;

_.forOwn(new Foo(), function(value, key) {
  console.log(key); // Logs 'a' only
});
```

### `_.forOwnRight(object, [iteratee=_.identity])`

Like `_.forOwn` but iterates in reverse order.

**Since:** 0.1.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;

_.forOwnRight(new Foo(), function(value, key) {
  console.log(key); // Logs 'a' only (reverse order)
});
```

## Keys and Values

### `_.keys(object)`

Creates array of own enumerable string-keyed property keys.

**Since:** 0.1.0

```javascript
var object = { 'a': 1, 'b': 2 };
_.keys(object); // => ['a', 'b'] (order not guaranteed)
```

### `_.keysIn(object)`

Creates array of own and inherited enumerable string-keyed property keys.

**Since:** 0.1.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;
_.keysIn(new Foo()); // => ['a', 'b'] (order not guaranteed)
```

### `_.values(object)`

Creates array of own enumerable string-keyed property values.

**Since:** 0.1.0

```javascript
var object = { 'a': 1, 'b': 2 };
_.values(object); // => [1, 2] (order not guaranteed)
```

### `_.valuesIn(object)`

Creates array of own and inherited enumerable string-keyed property values.

**Since:** 3.0.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;
_.valuesIn(new Foo()); // => [1, 2] (order not guaranteed)
```

### `_.toPairs(object)` / `_.entries`

Creates array of [key, value] pairs for own enumerable properties.

**Since:** 3.0.0

```javascript
var object = { 'a': 1, 'b': 2 };
_.toPairs(object); // => [['a', 1], ['b', 2]]
```

### `_.toPairsIn(object)` / `_.entriesIn`

Creates array of [key, value] pairs for own and inherited properties.

**Since:** 3.0.0

```javascript
function Foo() { this.a = 1; }
Foo.prototype.b = 2;
_.toPairsIn(new Foo()); // => [['a', 1], ['b', 2]]
```

## Finding Keys

### `_.findKey(object, [predicate=_.identity])`

Gets key of first element that passes predicate test.

**Since:** 1.1.0

```javascript
var users = {
  'barney': { 'age': 36, 'active': true },
  'fred': { 'age': 40, 'active': false }
};

_.findKey(users, o => o.age < 40); // => 'barney'
```

### `_.findLastKey(object, [predicate=_.identity])`

Gets key of last element that passes predicate test.

**Since:** 1.1.0

```javascript
var users = {
  'barney': { 'age': 36, 'active': true },
  'fred': { 'age': 40, 'active': false }
};

_.findLastKey(users, o => o.age < 40); // => 'barney' (last match)
```

## Functions

### `_.functions(object)`

Creates array of own enumerable function property names.

**Since:** 0.1.0

```javascript
function Foo() { this.a = _.noop; this.b = 1; }
Foo.prototype.c = _.noop;
_.functions(new Foo()); // => ['a'] (own functions only)
```

### `_.functionsIn(object)`

Creates array of own and inherited function property names.

**Since:** 4.0.0

```javascript
function Foo() { this.a = _.noop; }
Foo.prototype.b = _.noop;
_.functionsIn(new Foo()); // => ['a', 'b']
```

## Inversion

### `_.invert(object)`

Creates object with keys and values swapped.

**Since:** 0.7.0

```javascript
_.invert({ 'a': 1, 'b': 2 });
// => { '1': 'a', '2': 'b' } (all values become strings)
```

### `_.invertBy(object, [iteratee=_.identity])`

Like `_.invert` but accepts iteratee for value transformation.

**Since:** 4.0.0

```javascript
var object = { 'a': 1, 'b': 2, 'c': 1 };
_.invertBy(object, String);
// => { '1': ['a', 'c'], '2': ['b'] } (grouped by value)
```

## Mapping

### `_.mapKeys(object, [iteratee=_.identity])`

Creates object with keys transformed by iteratee.

**Since:** 4.0.0

```javascript
var object = { 'a': 1, 'b': 2 };
_.mapKeys(object, function(value, key) {
  return key + value;
});
// => { 'a1': 1, 'b2': 2 }
```

### `_.mapValues(object, [iteratee=_.identity])`

Creates object with values transformed by iteratee.

**Since:** 4.0.0

```javascript
var object = { 'a': 1, 'b': 2 };
_.mapValues(object, n => n * 3);
// => { 'a': 3, 'b': 6 }
```

## Merging

### `_.merge(object, [sources])`

Recursively assigns properties from sources to object. **Mutates object.**

**Since:** 2.4.0

```javascript
var object = { 'a': [{ 'b': 2 }, { 'd': 4 }] };
var source = { 'a': [{ 'c': 3 }, { 'e': 5 }] };

_.merge(object, source);
console.log(object); // => { 'a': [{ 'b': 2, 'c': 3 }, { 'd': 4, 'e': 5 }] }
```

### `_.mergeWith(object, sources, customizer)`

Like `_.merge` but accepts customizer for value merging.

**Since:** 4.0.0

```javascript
function customizer(objValue, srcValue) {
  if (_.isArray(objValue)) {
    return objValue.concat(srcValue);
  }
}

var object = { 'a': [1] };
var source = { 'a': [2] };
_.mergeWith(object, source, customizer);
// => { 'a': [1, 2] } (concatenated)
```

## Picking and Omitting

### `_.pick(object, [paths])`

Creates object with only specified properties.

**Since:** 0.1.0

```javascript
var object = { 'a': 1, 'b': 2, 'c': 3 };
_.pick(object, ['a', 'c']); // => { 'a': 1, 'c': 3 }
```

### `_.pickBy(object, [predicate=_.identity])`

Creates object with properties that pass predicate test.

**Since:** 4.0.0

```javascript
var object = { 'a': 1, 'b': 2, 'c': 3 };
_.pickBy(object, n => n % 2); // => { 'a': 1, 'c': 3 } (odd values)
```

### `_.omit(object, [paths])`

Creates object without specified properties. Opposite of `_.pick`.

**Since:** 0.1.0

```javascript
var object = { 'a': 1, 'b': 2, 'c': 3 };
_.omit(object, ['a', 'c']); // => { 'b': 2 }
```

### `_.omitBy(object, [predicate=_.identity])`

Creates object with properties that **fail** predicate test. Opposite of `_.pickBy`.

**Since:** 4.0.0

```javascript
var object = { 'a': 1, 'b': 2, 'c': 3 };
_.omitBy(object, n => n % 2); // => { 'b': 2 } (even values)
```

## Transformation

### `_.transform(object, [iteratee=_.identity], [accumulator])`

Creates accumulator by iterating over object properties.

**Since:** 0.1.0

```javascript
// Default accumulator is array or object
_.transform({ 'a': 1, 'b': 2 }, function(result, value, key) {
  result[key] = value * 3;
}); // => { 'a': 3, 'b': 6 }

// Custom accumulator
_.transform([1, 2], function(result, n) {
  result.push(n * 3);
}, []); // => [3, 6]
```

## Common Patterns

### Deep Merging Configs

```javascript
const defaults = {
  database: { host: 'localhost', port: 5432 },
  logging: true
};

const userConfig = {
  database: { host: 'production.db' }
};

const config = _.merge({}, defaults, userConfig);
// => { database: { host: 'production.db', port: 5432 }, logging: true }
```

### Safe Nested Access

```javascript
const theme = _.get(user, 'profile.settings.theme', 'dark');
const name = _.get(user, 'name', 'Guest');
```

### Conditional Property Updates

```javascript
_.update(user, 'stats.playCount', n => n + 1);
_.updateWith(data, ['a', 'b', 'c'], x => x * 2, Object.create);
```

### Object Filtering

```javascript
// Remove null/undefined values
const clean = _.omitBy(data, _.isNil);

// Keep only specific keys
const { id, name } = _.pick(user, ['id', 'name']);

// Filter by value condition
const activeUsers = _.pickBy(users, 'isActive');
```
