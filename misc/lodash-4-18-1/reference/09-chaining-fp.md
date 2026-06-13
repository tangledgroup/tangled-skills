# Chaining and FP

Lodash provides two complementary paradigms for composing operations: method chaining with lazy evaluation, and the functional programming (FP) build.

## Method Chaining

### Explicit Chaining

Wrap a value with `_(value)` or `_.chain(value)` to begin a chain. Call methods on the chain object, then call `.value()` to get the final result.

```js
var users = [
  { 'user': 'barney',  'age': 36 },
  { 'user': 'fred',    'age': 40 },
  { 'user': 'pebbles', 'age': 1 }
];

var youngest = _(users)
  .sortBy('age')
  .map(function(o) {
    return o.user + ' is ' + o.age;
  })
  .head()
  .value();
// → 'pebbles is 1'
```

### Implicit Chaining

Call methods directly on `_` with the value as first argument. Lodash automatically chains when the result is used in further chained calls.

```js
_.map(users, 'user');     // → ['barney', 'fred', 'pebbles']
_(users).map('user').value(); // → ['barney', 'fred', 'pebbles']
```

### Chain Methods

- `_(value)` — creates a lodash wrapper
- `_.chain(value)` — explicitly begins chaining
- `.at([paths])` — gets values at paths (chained)
- `.chain()` — explicitly chains within a chain
- `.commit()` — computes and returns the wrapped value
- `.next()` / `[Symbol.iterator]()` — iterate over wrapped array
- `.plant(value)` — creates a new chain with given value
- `.reverse()` — reverses the wrapped array
- `.value()` — extracts the unwrapped value

```js
var stooges = [
  { 'name': 'curly', 'age': 30 },
  { 'name': 'moe', 'age': 40 },
  { 'name': 'larry', 'age': 50 }
];

_(stooges)
  .sortBy('age')
  .map(function(stooge) {
    return stooge.name + ' is ' + stooge.age;
  })
  .commit();
// → ['curly is 30', 'moe is 40', 'larry is 50']
```

## Lazy Evaluation

Lodash chains compile method sequences into a single optimized function when possible. This avoids creating intermediate arrays and dramatically improves performance on large collections.

**Lazy-evaluable methods**: `chunk`, `compact`, `drop`, `dropRight`, `dropRightWhile`, `dropWhile`, `filter`, `first`, `flatMap`, `flatten`, `flattenDeep`, `flattenDepth`, `map`, `nth`, `reverse`, `sample`, `take`, `takeRight`, `takeRightWhile`, `takeWhile`, `uniq`, `uniqBy`, `uniqWith`.

```js
// Without chaining — creates 3 intermediate arrays
var result = _.map(
  _.filter(largeArray, function(n) { return n % 2 == 0; }),
  function(n) { return n * n; }
);

// With chaining — single pass through data
var result = _(largeArray)
  .filter(function(n) { return n % 2 == 0; })
  .map(function(n) { return n * n; })
  .value();
```

Lazy evaluation is automatically enabled in explicit chains. It also works with implicit chains when methods are called on the same chain object.

## lodash/fp

The `lodash/fp` module exports an instance of lodash with all methods wrapped to produce **immutable**, **auto-curried**, **iteratee-first data-last** methods.

### Loading

```js
// Node.js
var fp = require('lodash/fp');

// Browser (loads lodash.fp.min.js)
<script src="lodash.fp.js"></script>
```

### Key Differences

**Iteratee-first, data-last**: Methods take the iteratee/predicate first and the collection last, enabling easy partial application.

```js
// lodash — data-first
_.map([1, 2, 3], function(n) { return n * 2; });

// lodash/fp — iteratee-first
fp.map(function(n) { return n * 2; }, [1, 2, 3]);
// Or with currying:
fp.map(n => n * 2)([1, 2, 3]); // → [2, 4, 6]
```

**Auto-curried**: Methods return new functions until all arguments are provided.

```js
var add = fp.add;
var inc = add(1);
inc(5); // → 6

var double = fp.map(fp.multiply(2));
double([1, 2, 3]); // → [2, 4, 6]
```

**Immutable**: Methods never modify original data. `pull` becomes `remove`, `reverse` returns a new array.

### Capped Iteratee Arguments

FP methods cap iteratee arguments to avoid variadic gotchas:

```js
// lodash — iteratee gets (value, index, collection)
_.map(['6', '8', '10'], parseInt);
// → [6, NaN, 2]  (parseInt receives radix from index!)

// lodash/fp — iteratee capped to one argument (value)
fp.map(parseInt)(['6', '8', '10']);
// → [6, 8, 10]
```

Methods capping to one argument: `dropRightWhile`, `dropWhile`, `every`, `filter`, `find`, `findIndex`, `findKey`, `findLast`, `findLastIndex`, `findLastKey`, `flatMap`, `flatMapDeep`, `flatMapDepth`, `forEach`, `forEachRight`, `forIn`, `forInRight`, `forOwn`, `forOwnRight`, `map`, `mapKeys`, `mapValues`, `partition`, `reject`, `remove`, `some`, `takeRightWhile`, `takeWhile`, `times`.

Methods capping to two arguments: `reduce`, `reduceRight`, `transform`.

### Placeholders

Use `_` as a placeholder to fill in arguments out of order:

```js
// Equivalent to _.gt(5, 2) — i.e., 5 > 2
_.gt(_, 2)(5); // → true

var cloneDeepMerge = fp.mergeWith(fp.placeholder, fp.cloneDeep);
cloneDeepMerge({ 'a': 1 }, { 'b': 2 });
// → { 'a': 1, 'b': 2 }
```

### FP Aliases (59 total)

lodash/fp provides aliases familiar from other FP libraries:

- `_.F` → `_.stubFalse`
- `_.T` → `_.stubTrue`
- `_.all` → `_.every`
- `_.any` → `_.some`
- `_.compose` → `_.flowRight`
- `_.pipe` → `_.flow`
- `_.equals` → `_.isEqual`
- `__.contains` → `_.includes`
- `_.path` → `_.get`
- `_.pluck` → `_.map`
- `_.prop` → `_.get`
- `_.whereEq` → `_.isMatch`

### Functional Composition

Instead of chaining, FP style uses composition:

```js
var fp = require('lodash/fp');

var process = fp.flow(
  fp.filter(fp.propEq('active', true)),
  fp.map('name'),
  fp.sortBy('length')
);

process(users); // → ['barney', 'fred', 'pebbles']
```

### No Chaining in FP

The `lodash/fp` module does not convert chain sequences. Use functional composition (`flow`, `flowRight`, `pipe`, `compose`) as the alternative to method chaining.

## Migration Tips

When migrating from lodash to lodash/fp:

1. Replace `_.method(data, iteratee)` with `fp.method(iteratee)(data)`
2. Use placeholders `_` for out-of-order arguments
3. Replace chains with `flow`/`flowRight` compositions
4. Remember that FP methods are immutable — `pull` mutates, `remove` (FP alias) does not
5. Fixed arity means optional parameters need explicit values or new method variants (e.g., `padChars` instead of `pad`)
