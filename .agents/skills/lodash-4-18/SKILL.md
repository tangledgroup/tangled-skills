---
name: lodash-4-18
description: Complete toolkit for Lodash 4.18 utility library providing 300+ helper functions for arrays, collections, objects, strings, numbers, dates, and functions. Use when building JavaScript applications requiring robust data manipulation, functional programming patterns, type checking, or cross-platform compatibility without native ES6+ features.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - javascript
  - utility-library
  - arrays
  - objects
  - strings
  - functional-programming
  - data-manipulation
category: development
required_environment_variables: []
---

# Lodash 4.18 Toolkit

Complete toolkit for [Lodash](https://lodash.com/) v4.18, a modern JavaScript utility library providing over 300 modular helper functions for arrays, collections, objects, strings, numbers, dates, and functions. Lodash emphasizes composability, performance, and cross-platform compatibility.

## When to Use

- Working with arrays that need chunking, slicing, filtering, or transformation
- Manipulating objects with deep cloning, merging, or property access
- Processing strings with case conversion, padding, truncation, or templating
- Implementing functional programming patterns (currying, partial application, composition)
- Type checking and validation across JavaScript environments
- Debouncing/throttling event handlers in UI applications
- Performing mathematical operations on arrays of numbers
- Building API utilities with consistent argument handling
- Needing cross-browser compatibility without polyfills

## Installation

```bash
# npm
npm install lodash

# yarn
yarn add lodash

# CDN (browser)
<script src="https://cdn.jsdelivr.net/npm/lodash@4.18.1/lodash.min.js"></script>
```

**Import patterns:**
```javascript
// Full bundle (not recommended for production)
import _ from 'lodash';

// Individual imports (tree-shaking friendly)
import chunk from 'lodash/chunk';
import debounce from 'lodash/debounce';
import map from 'lodash/map';

// Named exports
import { chunk, debounce, map } from 'lodash';

// Browser global
const _ = require('lodash');
```

## Quick Start

### Array Operations

Split arrays into chunks, remove duplicates, or find elements:

```javascript
import { chunk, uniq, find } from 'lodash';

// Chunk array into groups
chunk([1, 2, 3, 4, 5], 2); // [[1, 2], [3, 4], [5]]

// Remove duplicates
uniq([1, 2, 1, 3]); // [1, 2, 3]

// Find first matching element
find(users, { age: 30 }); // { name: 'Fred', age: 30 }
```

See [Array Methods](references/01-array-methods.md) for 56 array utilities.

### Collection Iteration

Map, filter, reduce, and group collections:

```javascript
import { map, filter, groupBy, sortBy } from 'lodash';

// Transform elements
map([1, 2, 3], n => n * 2); // [2, 4, 6]

// Filter by predicate
filter(users, u => u.age > 25); // [{ name: 'Fred', age: 30 }]

// Group by property
groupBy(users, 'age'); // { '25': [...], '30': [...] }

// Sort by multiple fields
sortBy(users, ['user', 'age']);
```

See [Collection Methods](references/02-collection-methods.md) for 24 iteration utilities.

### Object Manipulation

Deep clone, merge, or access nested properties:

```javascript
import { cloneDeep, get, set, omit } from 'lodash';

// Deep clone objects
cloneDeep({ a: [1, 2], b: { c: 3 } });

// Safe property access
get(user, 'profile.settings.theme', 'dark'); // 'dark'

// Set nested properties
set(object, 'a.b.c', 1);

// Exclude keys
omit(user, ['password', 'token']); // { name: 'Fred', age: 30 }
```

See [Object Methods](references/04-object-methods.md) for 46 object utilities.

### String Utilities

Transform and manipulate strings with consistent behavior:

```javascript
import { camelCase, truncate, template } from 'lodash';

// Convert to camelCase
camelCase('Foo Bar'); // 'fooBar'

// Truncate long strings
truncate('Hello there!', { length: 8 }); // 'Hel...'

// Template string interpolation
const tpl = template('Hello <%= name %>!');
tpl({ name: 'Fred' }); // 'Hello Fred!'
```

See [String Methods](references/07-string-methods.md) for 29 string utilities.

### Function Utilities

Implement advanced function patterns:

```javascript
import { debounce, throttle, curry, flow } from 'lodash';

// Debounce rapid calls
const handleScroll = debounce(() => console.log('scrolled'), 150);

// Throttle to fixed rate
const tick = throttle(() => console.log(tick.count++), 200);

// Curried function
const add = curry((a, b) => a + b);
add(1)(2); // 3

// Function composition
const greet = flow([capitalize, str => `Hello ${str}`]);
greet('fred'); // 'Hello Fred'
```

See [Function Methods](references/03-function-methods.md) for 24 function utilities.

## Reference Files

- [`references/01-array-methods.md`](references/01-array-methods.md) - 56 array manipulation methods (chunk, compact, difference, flatten, intersection, union, uniq, zip, etc.)
- [`references/02-collection-methods.md`](references/02-collection-methods.md) - 24 collection iteration methods (countBy, filter, find, forEach, groupBy, map, reduce, sortBy, etc.)
- [`references/03-function-methods.md`](references/03-function-methods.md) - 24 function utilities (after, ary, bind, curry, debounce, memoize, partial, throttle, wrap, etc.)
- [`references/04-object-methods.md`](references/04-object-methods.md) - 46 object manipulation methods (assign, cloneDeep, get, has, merge, omit, pick, set, transform, etc.)
- [`references/05-lang-methods.md`](references/05-lang-methods.md) - 49 type checking and conversion methods (isArray, isPlainObject, isEqual, toNumber, toString, etc.)
- [`references/06-math-methods.md`](references/06-math-methods.md) - 16 mathematical operations (add, ceil, floor, max, min, round, sum, etc.)
- [`references/07-string-methods.md`](references/07-string-methods.md) - 29 string utilities (camelCase, escape, pad, replace, split, template, truncate, words, etc.)
- [`references/08-util-methods.md`](references/08-util-methods.md) - 34 utility methods (attempt, cond, constant, flow, identity, matches, property, times, uniqueId, etc.)
- [`references/09-seq-methods.md`](references/09-seq-methods.md) - 12 chaining methods (_(), chain, tap, thru, prototype.value, etc.)
- [`references/10-other-methods.md`](references/10-other-methods.md) - Date and Number category methods (now, clamp, inRange, random)

**Note:** `{baseDir}` refers to the skill's base directory (e.g., `.agents/skills/lodash-4-18/`). All paths are relative to this directory.

## Common Patterns

### Iteration vs Array Methods

Lodash provides both array-specific and generic collection methods:

```javascript
// Array-only (faster for arrays)
_.indexOf([1, 2, 3], 2); // 1
_.findIndex(users, { age: 30 }); // 2

// Works on arrays AND objects
_.includes([1, 2, 3], 2); // true
_.includes({ user: 'fred' }, 'fred'); // true

_.map([1, 2, 3], n => n * 2); // [2, 4, 6]
_.map({ a: 1, b: 2 }, n => n * 2); // [2, 4]
```

### Predicate Shortcuts

Most methods accept shorthand predicates:

```javascript
// Function predicate
filter(users, user => user.age > 25);

// Object shorthand (matches properties)
filter(users, { age: 30 });

// Property name string
filter(users, 'active');

// Array of property names
sortBy(users, ['user', 'age']);
```

### Chaining API

Lodash supports fluent method chaining:

```javascript
// Implicit chaining (auto-wraps)
_(users)
  .filter('active')
  .map('name')
  .value(); // ['Fred', 'Barney']

// Explicit chaining
_.chain(users)
  .filter(user => user.active)
  .map(user => user.name)
  .value();

// Tap for debugging
_(users)
  .filter('active')
  .tap(console.log) // Logs intermediate result
  .map('name')
  .value();
```

### Method Variations

Many methods come in related variants:

```javascript
// Direction variants
_.find(users, { age: 30 });    // First match
_.findLast(users, { age: 30 }); // Last match

_.drop([1, 2, 3], 1);          // [2, 3]
_.dropRight([1, 2, 3], 1);     // [1, 2]

// Depth variants
_.flatten([1, [2, 3]]);        // [1, 2, 3]
_.flattenDeep([1, [2, [3]]]);  // [1, 2, 3]
_.flattenDepth([1, [2, [3]]], 2); // [1, 2, [3]]

// With customizer
_.difference([2, 1], [2, 3]);           // [1]
_.differenceBy([2.1, 1.2], [2.3, 1.5], Math.floor); // [1.2]
_.differenceWith([2.1, 1.2], [2.3, 1.5], (a, b) => Math.abs(a - b) < 0.5); // [1.2]
```

## Performance Notes

- Use array-specific methods (`_.indexOf`) over generic ones (`_.includes`) for arrays when possible
- Chaining creates intermediate wrappers; use `.value()` to finalize
- Individual imports enable tree-shaking in bundlers
- Lodash is optimized for both small and large data sets
- Immutable methods return new arrays/objects; mutating methods modify in-place

## Troubleshooting

**Issue:** Bundle size too large
- **Solution:** Import individual modules: `import debounce from 'lodash/debounce'`

**Issue:** Method doesn't work on object
- **Solution:** Use collection methods (`_.map`, `_.filter`) instead of array-specific ones

**Issue:** Deep clone not working as expected
- **Solution:** `_.cloneDeep` handles circular references but not functions or DOM elements

**Issue:** Chaining returns wrapper instead of value
- **Solution:** Call `.value()` at the end of chain to extract result

**Issue:** Predicate shorthand not matching
- **Solution:** Use explicit function predicate for complex conditions

See [Individual reference files](#reference-files) for method-specific documentation and examples.
