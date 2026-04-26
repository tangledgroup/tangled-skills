---
name: lodash-4-18-1
description: Complete toolkit for Lodash 4.18 utility library providing 300+ helper functions for arrays, collections, objects, strings, numbers, dates, and functions. Use when building JavaScript applications requiring robust data manipulation, functional programming patterns, type checking, or cross-platform compatibility without native ES6+ features.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.18.1"
tags:
  - javascript
  - utility-library
  - data-manipulation
  - functional-programming
  - browser-compatibility
category: library
external_references:
  - https://lodash.com/
  - https://github.com/lodash/lodash
---

# Lodash 4.18

## Overview

Lodash is a JavaScript utility library delivering consistency, modularity, performance, and extras. It provides over 300 helper functions organized into 11 categories: Array, Collection, Date, Function, Lang, Math, Number, Object, Seq, String, and Util. Lodash makes JavaScript easier by taking the hassle out of working with arrays, numbers, objects, strings, and more.

The library is released under the MIT license and supports modern environments including Node.js 4+, Bun 1.0+, and the latest Chromium, Firefox, WebKit, and Edge browsers with best-effort support for Chrome 74+, Firefox 66+, IE 11, Edge 18, and Safari 11+.

## When to Use

- Iterating arrays, objects, and strings with consistent cross-browser behavior
- Manipulating and testing values (type checking, deep equality, cloning)
- Creating composite functions (currying, partial application, debouncing, throttling)
- Building functional programming pipelines with `lodash/fp`
- Data transformation tasks: sorting, grouping, partitioning, mapping
- Working with deeply nested objects via path-based access (`_.get`, `_.set`)
- Needing reliable polyfills for older browser environments
- Reducing boilerplate in data processing and ETL workflows

## Core Concepts

### Module Loading

Lodash supports multiple import strategies for tree-shaking and bundle optimization:

```js
// Full build (all methods)
var _ = require('lodash');

// Core build (~4KB gzipped, 63 essential methods)
var _ = require('lodash/core');

// FP build (immutable, auto-curried, iteratee-first data-last)
var fp = require('lodash/fp');

// Category modules
var array = require('lodash/array');
var object = require('lodash/object');

// Individual methods for smallest bundles
var debounce = require('lodash/debounce');
var get = require('lodash/get');
```

In a browser:

```html
<script src="lodash.js"></script>
<!-- or CDN -->
<script src="https://cdn.jsdelivr.net/npm/lodash@4.18.1/lodash.min.js"></script>
```

### Iteratee Shorthands

Most Lodash methods accept an `iteratee` parameter that supports three shorthand forms, reducing boilerplate:

**Property shorthand** — passes a property name to create a function that returns the value of that property:

```js
_.map(users, 'name');
// Equivalent to: _.map(users, function(user) { return user.name; });
```

**Matches shorthand** — passes a source object to create a function that performs a partial deep comparison:

```js
_.filter(users, { 'active': true, 'role': 'admin' });
// Returns users where both active === true AND role === 'admin'
```

**MatchesProperty shorthand** — passes a `[key, srcValue]` pair to create a function that checks if an element's property matches the source value:

```js
_.find(users, ['active', false]);
// Finds first user where user.active === false
```

### Lazy Evaluation

Lodash chains support lazy evaluation — when possible, method calls are compiled into a single optimized function. This avoids creating intermediate arrays and dramatically improves performance on large collections:

```js
// Without chaining — creates multiple intermediate arrays
_.map(_.filter(largeArray, predicate), transform);

// With chaining — single pass, lazy evaluation
_(largeArray).filter(predicate).map(transform).value();
```

Lazy evaluation works with: `chunk`, `compact`, `drop`, `dropRight`, `dropRightWhile`, `dropWhile`, `filter`, `first`, `flatMap`, `flatten`, `flattenDeep`, `flattenDepth`, `map`, `nth`, `reverse`, `sample`, `take`, `takeRight`, `takeRightWhile`, `takeWhile`, `uniq`, `uniqBy`, `uniqWith`.

### Build Options

- **Full build** — all 300+ methods, ~24KB gzipped
- **Core build** — 63 essential methods, ~4KB gzipped, Backbone.js compatible, no lazy evaluation or placeholder support
- **FP build** — immutable auto-curried iteratee-first data-last variants of all methods
- **Strict build** — throws errors when attempting to overwrite read-only properties in `_.assign`, `_.bindAll`, `_.defaults`
- **Custom builds** — via lodash-cli, cherry-pick only needed methods

### Immutability Patterns

Lodash distinguishes between mutating and non-mutating operations:

```js
// Mutating — modifies original array
_.pull(array, 'a', 'c');
_.remove(array, predicate);
_.reverse(array);

// Non-mutating — returns new value, original unchanged
_.without(array, 'a', 'c');  // like pull but doesn't mutate
_.filter(array, predicate);   // like remove inverse, doesn't mutate
_.drop(array, n);             // returns new slice
```

## Usage Examples

### Deep object access with safe defaults

```js
_.get(user, 'profile.address.city', 'Unknown');
// Returns 'Unknown' if user.profile or address is undefined
```

### Function composition

```js
var enhance = _.flow(_.trim, _.capitalize, _.escape);
enhance('  hello world  '); // → '&lt;Hello world&gt;'
```

### Debounced search input

```js
var debouncedSearch = _.debounce(function(query) {
    fetchResults(query);
}, 300, { 'leading': false, 'trailing': true });
```

### Grouping and counting

```js
var byStatus = _.groupBy(users, 'status');
var statusCounts = _.countBy(users, 'status');
// → { 'active': 12, 'inactive': 5, 'pending': 3 }
```

### Deep merge with custom conflict resolution

```js
var result = _.mergeWith(
    defaults,
    overrides,
    function(objValue, srcValue) {
        if (Array.isArray(objValue)) {
            return srcValue; // Replace arrays instead of concatenating
        }
    }
);
```

## Advanced Topics

**Array Methods**: Filtering, sorting, slicing, flattening, set operations → [Array Methods](reference/01-array-methods.md)

**Collection Methods**: Iteration, grouping, partitioning, reduction → [Collection Methods](reference/02-collection-methods.md)

**Function Methods**: Currying, debouncing, throttling, partial application → [Function Methods](reference/03-function-methods.md)

**Object Methods**: Property access, merging, picking, transforming → [Object Methods](reference/04-object-methods.md)

**String Methods**: Formatting, escaping, case conversion, templating → [String Methods](reference/05-string-methods.md)

**Lang Methods**: Type checking, equality comparison, cloning → [Lang Methods](reference/06-lang-methods.md)

**Math Methods**: Aggregation, clamping, random numbers → [Math Methods](reference/07-math-methods.md)

**Util Methods**: Identity functions, iteration helpers, mixins → [Util Methods](reference/08-util-methods.md)

**Chaining and FP**: Lazy evaluation chains, lodash/fp functional style → [Chaining and FP](reference/09-chaining-fp.md)
