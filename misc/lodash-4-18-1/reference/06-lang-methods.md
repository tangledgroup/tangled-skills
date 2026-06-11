# Lang Methods

Lang methods provide type checking, equality comparison, value conversion, and cloning utilities. They are the backbone of robust JavaScript code that needs to handle diverse input types safely.

## Type Checking

Lodash provides 30+ `is*` methods for type checking. These are more reliable than native checks, especially across iframes and edge cases.

### Basic Types

```js
_.isBoolean(true);     // → true
_.isBoolean('true');   // → false
_.isString('hello');   // → true
_.isNumber(3);         // → true
_.isNumber('3');       // → false
_.isNull(null);        // → true
_.isUndefined(undefined); // → true
_.isNil(null);         // → true  (null or undefined)
_.isNil(undefined);    // → true
```

### Collection Types

```js
_.isArray([1, 2]);           // → true
_.isArray('abc');            // → false
_.isArrayBuffer(new ArrayBuffer(2)); // → true

_.isArrayLike([1, 2]);       // → true  (has length property)
_.isArrayLike('abc');        // → true
_.isArrayLike(document.body.children); // → true
_.isArrayLikeObject([1, 2]); // → true  (array-like AND object)

_.isArguments(function() { return arguments; }()); // → true
```

### Object Types

```js
_.isObject({});          // → true
_.isObject(null);        // → false
_.isObjectLike({});      // → true  (non-null and typeof === 'object')
_.isPlainObject({});     // → true
_.isPlainObject(new Date); // → false
_.isPlainObject(_.create(null)); // → true
```

### Built-in Types

```js
_.isDate(new Date);         // → true
_.isMap(new Map);           // → true
_.isSet(new Set);           // → true
_.isRegExp(/abc/);          // → true
_.isSymbol(Symbol('test')); // → true
_.isTypedArray(new Uint8Array); // → true
```

### Weak Collections

```js
_.isWeakMap(new WeakMap);   // → true
_.isWeakSet(new WeakSet);   // → true
```

### Special Checks

```js
_.isElement(document.body);        // → true
_.isError(new Error);              // → true
_.isFinite(3);                     // → true
_.isFinite(Number.POSITIVE_INFINITY); // → false
_.isInteger(3);                    // → true
_.isInteger(3.2);                  // → false
_.isLength(3);                     // → true  (valid JS array length)
_.isSafeInteger(Number.MAX_SAFE_INTEGER); // → true
_.isFunction(function() {});       // → true
_.isNative(Array.prototype.push);  // → true
_.isNaN(NaN);                      // → true
_.isNaN(undefined);                // → false  (unlike global isNaN)
_.isEmpty(null);                   // → true
_.isEmpty([]);                     // → true
_.isEmpty({});                     // → true
_.isEmpty('');                     // → true
_.isEmpty(new String('abc'));      // → false
```

### `_.conformsTo(object, source)`

Checks if object conforms to the predicates of source. Each value in source should be a predicate function.

```js
_.conformsTo({ 'a': 1, 'b': 2 }, {
  'a': function(n) { return n > 0; },
  'b': function(n) { return n < 3; }
});
// → true
```

## Equality Comparison

### `_.eq(value, other)`

Performs SameValueZero comparison (like `===` but treats NaN as equal to NaN).

```js
_.eq(NaN, NaN); // → true
```

### `_.isEqual(value, other)`

Performs a deep comparison between two values. Supports arrays, objects, typed arrays, dates, maps, sets, regexes, and strings.

```js
var object = { 'a': 1 };
var other = { 'a': 1 };
_.isEqual(object, other); // → true
object === other;          // → false
```

### `_.isEqualWith(value, other, [customizer])`

Like `isEqual` but with a customizer function `(objValue, othValue, key, object, other, stack)` for custom comparison logic. Return undefined to fall back to default.

```js
var array = [[1, 2, 3], [4, 5, 6]];
var other = [[1, 2, 4], [4, 5, 6]];
_.isEqualWith(array, other, function(a, b) {
  if (_.isNumber(a) && _.isNumber(b)) {
    return Math.round(a) == Math.round(b);
  }
});
// → true
```

### `_.isMatch(object, source)` / `_.isMatchWith(object, source, [customizer])`

Performs a partial deep comparison — returns true if source properties match in object. Extra properties in object are ignored.

```js
_.isMatch({ 'a': 1, 'b': 2 }, { 'a': 1 });
// → true

_.isMatch({ 'a': 1, 'b': 2 }, { 'a': 1, 'c': 3 });
// → false
```

## Comparison

### `_.gt(value, other)` / `_.gte(value, other)` / `_.lt(value, other)` / `_.lte(value, other)`

Greater than, greater-or-equal, less than, less-or-equal comparisons. Useful as iteratees.

```js
_.filter([1, 2, 3], _.partial(_.gt, _, 1));
// → [2, 3]
```

## Cloning

### `_.clone(value)` / `_.cloneDeep(value)`

Creates a shallow or deep copy. Shallow clone copies one level; deep clone recursively copies all nested objects and arrays.

```js
var objects = [{ 'a': 1 }, { 'b': 2 }];
var shallow = _.clone(objects);
shallow[0] === objects[0]; // → true (same reference)

var deep = _.cloneDeep(objects);
deep[0] === objects[0];    // → false (new object)
```

### `_.cloneWith(value, [customizer])` / `_.cloneDeepWith(value, [customizer])`

Like clone/cloneDeep but with a customizer `(value, key|index, object, stack)` for custom cloning logic.

```js
function customizer(value) {
  if (_.isElement(value)) {
    return value.cloneNode(false);
  }
}
_.cloneWith($('<div>'), customizer);
```

## Value Conversion

### `_.toFinite(value)` / `_.toInteger(value)` / `_.toLength(value)` / `_.toNumber(value)` / `_.toSafeInteger(value)`

Converts values to specific numeric types.

```js
_.toFinite(1.6);             // → 1.6
_.toInteger('3.2');          // → 3
_.toLength([1, 2, 3]);       // → 3
_.toNumber('4.5');           // → 4.5
_.toSafeInteger('3.2');      // → 3
```

### `_.toString(value)`

Converts value to a string. Returns `''` for null/undefined (unlike native String which throws on some environments).

```js
_.toString(null);    // → ''
_.toString(-0);      // → '-0'
_.toString([1, 2]);  // → '1,2'
```

### `_.toPlainObject(value)`

Converts values to a plain object. Removes non-enumerable properties and prototype chain.

```js
function Foo() { this.a = 1; }
_.toPlainObject(new Foo);
// → { 'a': 1 }
```

### `_.toArray(value)`

Converts any value to an array.

```js
_.toArray({ 'a': 1, 'b': 2 }); // → [1, 2]
_.toArray('abc');               // → ['a', 'b', 'c']
_.toArray(1);                   // → []
_.toArray(null);                // → []
```

### `_.toPath(value)`

Converts value to a property path array.

```js
_.toPath('a.b.c');     // → ['a', 'b', 'c']
_.toPath('a[0].b.c');  // → ['a', '0', 'b', 'c']
_.toPath(['a', 'b']);  // → ['a', 'b']
```
