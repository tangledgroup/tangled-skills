# Lang Methods (49 methods)

Type checking, comparison, and conversion utilities. These methods provide consistent type detection across JavaScript environments.

## Type Checking (is* methods)

### `_.isArray(value)`

Checks if value is classified as an Array. More reliable than `Array.isArray` in some edge cases.

```javascript
_.isArray([1, 2]);     // => true
_.isArray({});         // => false
```

### `_.isArrayBuffer(value)`

Checks if value is classified as an ArrayBuffer.

```javascript
_.isArrayBuffer(new ArrayBuffer(1)); // => true
```

### `_.isArrayLike(value)`

Checks if value is array-like (has numeric length property).

```javascript
_.isArrayLike([1, 2]);      // => true
_.isArrayLike('abc');       // => true
_.isArrayLike({ 'length': 2 }); // => true
```

### `_.isArrayLikeObject(value)`

Checks if value is array-like AND an object (excludes strings).

```javascript
_.isArrayLikeObject([1, 2]);     // => true
_.isArrayLikeObject('abc');      // => false (string)
_.isArrayLikeObject({ 'length': 2 }); // => true
```

### `_.isBoolean(value)`

Checks if value is classified as a Boolean.

```javascript
_.isBoolean(true);   // => true
_.isBoolean(false);  // => true
_.isBoolean('true'); // => false
```

### `_.isBuffer(value)`

Checks if value is a Buffer (Node.js).

```javascript
_.isBuffer(Buffer.alloc(1)); // => true
```

### `_.isDate(value)`

Checks if value is classified as a Date.

```javascript
_.isDate(new Date()); // => true
```

### `_.isElement(value)`

Checks if value is a DOM element.

```javascript
_.isElement(document.body); // => true
```

### `_.isEmpty(value)`

Checks if value is empty (no own enumerable properties for objects, length 0 for arrays/strings).

```javascript
_.isEmpty([]);        // => true
_.isEmpty({});        // => true
_.isEmpty('');        // => true
_.isEmpty([1, 2]);    // => false
_.isEmpty({ a: 1 });  // => false
```

### `_.isEqual(value, other)`

Performs deep equality comparison. Handles circular references.

```javascript
var object = { 'a': 1 };
_.isEqual(object, object);      // => true (same reference)
_.isEqual({ 'a': 1 }, { 'a': 1 }); // => true (deep equal)
_.isEqual([1, 2], [1, 2]);      // => true

// Circular references
var a = []; a[0] = a;
var b = []; b[0] = b;
_.isEqual(a, b); // => true
```

### `_.isEqualWith(value, other, [customizer])`

Like `_.isEqual` but accepts customizer for specific types.

```javascript
function customizer(objValue, otherValue) {
  if (_.isElement(objValue) && _.isElement(otherValue)) {
    return objValue.isEqualNode(otherValue);
  }
}
var el1 = document.createElement('div');
var el2 = document.createElement('div');
_.isEqualWith(el1, el2, customizer); // => true
```

### `_.isError(value)`

Checks if value is an Error object.

```javascript
_.isError(new Error()); // => true
```

### `_.isFinite(value)`

Checks if value is a finite primitive number (unlike native `isFinite`).

```javascript
_.isFinite(3);        // => true
_.isFinite('3');      // => false (string)
_.isFinite(Infinity); // => false
```

### `_.isFunction(value)`

Checks if value is classified as a Function.

```javascript
_.isFunction(_.isFunction); // => true
```

### `_.isInteger(value)`

Checks if value is an integer.

```javascript
_.isInteger(3);    // => true
_.isInteger(3.1);  // => false
_.isInteger('3');  // => false
```

### `_.isLength(value)`

Checks if value is a valid array-like length (non-negative integer).

```javascript
_.isLength(3);     // => true
_.isLength(-1);    // => false
_.isLength(3.2);   // => false
```

### `_.isMap(value)`

Checks if value is classified as a Map.

```javascript
_.isMap(new Map()); // => true
```

### `_.isMatch(object, source)`

Checks if object matches property values of source (shallow comparison).

```javascript
var object = { 'a': 1, 'b': 2 };
_.matches({ 'a': 1 })(object); // => true
```

### `_.isMatchWith(object, source, [customizer])`

Like `_.isMatch` but accepts customizer for comparison.

```javascript
function customizer(objValue, srcValue) {
  if (_.isNull(srcValue)) {
    return objValue == null; // Treat null and undefined as equal
  }
}
_.isMatchWith({ 'a': undefined }, { 'a': null }, customizer); // => true
```

### `_.isNaN(value)`

Checks if value is NaN (unlike native `isNaN` which coerces).

```javascript
_.isNaN(NaN);     // => true
_.isNaN('abc');   // => false (string)
_.isNaN(undefined); // => false
```

### `_.isNative(value)`

Checks if value is a native function.

```javascript
_.isNative(Array.prototype.push); // => true
```

### `_.isNil(value)`

Checks if value is null or undefined.

```javascript
_.isNil(null);       // => true
_.isNil(undefined);  // => true
_.isNil(NaN);        // => false
```

### `_.isNull(value)`

Checks if value is null.

```javascript
_.isNull(null);       // => true
_.isNull(undefined);  // => false
```

### `_.isNumber(value)`

Checks if value is classified as a Number.

```javascript
_.isNumber(3);     // => true
_.isNumber('3');   // => false
```

### `_.isObject(value)`

Checks if value is an object (includes arrays, functions, null).

```javascript
_.isObject({});      // => true
_.isObject([1, 2]);  // => true
_.isObject(null);    // => false (null is not an object in lodash)
```

### `_.isObjectLike(value)`

Checks if value is object-like (non-null with typeof 'object').

```javascript
_.isObjectLike({});      // => true
_.isObjectLike([1, 2]);  // => true
_.isObjectLike(null);    // => false
```

### `_.isPlainObject(value)`

Checks if value is a plain object (created by {} or new Object()).

```javascript
function Foo() { this.a = 1; }
_.isPlainObject({});          // => true
_.isPlainObject(new Foo());   // => false (instance)
_.isPlainObject([]);          // => false (array)
```

### `_.isRegExp(value)`

Checks if value is classified as a RegExp.

```javascript
_.isRegExp(/abc/); // => true
```

### `_.isSafeInteger(value)`

Checks if value is a safe integer (within -2^53 to 2^53).

```javascript
_.isSafeInteger(3);           // => true
_.isSafeInteger(Number.MAX_SAFE_INTEGER); // => true
_.isSafeInteger(Number.MAX_SAFE_INTEGER + 1); // => false
```

### `isSet(value)`

Checks if value is classified as a Set.

```javascript
_.isSet(new Set()); // => true
```

### `_.isString(value)`

Checks if value is classified as a String.

```javascript
_.isString('abc'); // => true
```

### `_.isSymbol(value)`

Checks if value is classified as a Symbol.

```javascript
_.isSymbol(Symbol.iterator); // => true
```

### `_.isTypedArray(value)`

Checks if value is classified as a TypedArray.

```javascript
_.isTypedArray(new Uint8Array(1)); // => true
```

### `_.isUndefined(value)`

Checks if value is undefined.

```javascript
_.isUndefined(undefined); // => true
_.isUndefined(null);      // => false
```

### `_.isWeakMap(value)`

Checks if value is classified as a WeakMap.

```javascript
_.isWeakMap(new WeakMap()); // => true
```

### `_.isWeakSet(value)`

Checks if value is classified as a WeakSet.

```javascript
_.isWeakSet(new WeakSet()); // => true
```

## Comparison

### `_.eq(value, other)`

 Performs SameValueZero equality comparison (like `===` but treats NaN as equal).

```javascript
_.eq(1, 1);        // => true
_.eq(NaN, NaN);    // => true (unlike ===)
_.eq(-0, 0);       // => true (unlike Object.is)
```

### `_.gt(value, other)`

Checks if value is greater than other.

```javascript
_.gt(3, 1); // => true
```

### `_.gte(value, other)`

Checks if value is greater than or equal to other.

```javascript
_.gte(3, 3); // => true
```

### `_.lt(value, other)`

Checks if value is less than other.

```javascript
_.lt(1, 3); // => true
```

### `_.lte(value, other)`

Checks if value is less than or equal to other.

```javascript
_.lte(3, 3); // => true
```

## Conversion

### `_.castArray(value)`

Creates array if value isn't already one.

```javascript
_.castArray(1);      // => [1]
_.castArray([1]);    // => [1] (unchanged)
_.castArray(null);   // => [null]
```

### `_.toArray(value)`

Converts value to array. Handles arrays, strings, maps, sets, and iterables.

```javascript
_.toArray([1, 2]);        // => [1, 2]
_.toArray('abc');         // => ['a', 'b', 'c']
_.toArray({ 'a': 1 });    // => [1] (values)
```

### `_.toFinite(value)`

Converts value to finite number.

```javascript
_.toFinite(3.2);       // => 3.2
_.toFinite('3.2');     // => 3.2
_.toFinite(Infinity);  // => Number.MAX_VALUE
```

### `_.toInteger(value)`

Converts value to integer.

```javascript
_.toInteger(3.2);  // => 3
_.toInteger('3');  // => 3
```

### `_.toLength(value)`

Converts value to length (non-negative integer).

```javascript
_.toLength(3.2);   // => 3
_.toLength(-1);    // => 0
```

### `_.toNumber(value)`

Converts value to number.

```javascript
_.toNumber(3.2);   // => 3.2
_.toNumber('3');   // => 3
_.toNumber(true);  // => 1
```

### `_.toPlainObject(value)`

Converts value to plain object. Clones arrays and objects, converts maps/sets.

```javascript
var map = new Map([['a', 1]]);
_.toPlainObject(map); // => { 'a': 1 }
```

### `_.toSafeInteger(value)`

Converts value to safe integer.

```javascript
_.toSafeInteger(3.2);           // => 3
_.toSafeInteger(Number.MAX_SAFE_INTEGER + 1); // => Number.MAX_SAFE_INTEGER
```

### `_.toString(value)`

Converts value to string. Handles null/undefined safely.

```javascript
_.toString(null);     // => '' (not 'null')
_.toString(undefined); // => ''
_.toString([1, 2]);   // => '1,2'
```

## Conforms To

### `_.conformsTo(object, source)`

Checks if object conforms to source predicates.

```javascript
var object = { 'a': 1, 'b': 2 };
var predicates = { 'a': n => n > 0 };
_.conformsTo(object, predicates); // => true
```

## Common Patterns

### Type Guards

```javascript
// Safe array access
if (_.isArray(data)) {
  data.forEach(process);
}

// Check for plain objects (not instances)
if (_.isPlainObject(config)) {
  mergeDefaults(config);
}

// Handle null/undefined
if (!_.isNil(value)) {
  useValue(value);
}
```

### Deep Comparison

```javascript
// Compare complex objects
if (_.isEqual(prevState, newState)) {
  return; // Skip update if unchanged
}

// Custom comparison for special types
function customizer(a, b) {
  if (a instanceof Date && b instanceof Date) {
    return a.getTime() === b.getTime();
  }
  return undefined; // Fall through to default
}
_.isEqualWith(obj1, obj2, customizer);
```

### Safe Conversions

```javascript
// Always get an array
const items = _.castArray(userInput);

// Convert to number safely
const count = _.toNumber(input) || 0;

// Get string representation (handles null/undefined)
const label = _.toString(value) || 'empty';
```
