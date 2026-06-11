# ES2023 Support and Modules

## Language Feature Coverage

QuickJS 2025-09-13 supports almost the complete ES2023 specification including full Annex B (legacy web compatibility). It passes nearly 100% of the ECMAScript Test Suite when selecting ES2023 features.

### Supported Features

- **Modules** — Full ES6 module support with `import`/`export`, dynamic `import()`, `import.meta.url`, `import.meta.main`, top-level await
- **Async** — Async functions, async generators, `Promise.allSettled`, `Promise.any`, `AggregateError`, `Promise.withResolvers`, `Promise.try`
- **Objects** — Proxies, `Object.fromEntries`, `Object.hasOwn`, `Object.groupBy`, `Map.groupBy`
- **Arrays** — `Array.prototype.at()`, `Array.prototype.findLast()`, `Array.prototype.findLastIndex()`, `Array.prototype.toReversed()`, `Array.prototype.toSpliced()`, `Array.prototype.toSorted()`, `Array.prototype.with()`
- **Strings** — `String.prototype.at()`, `String.prototype.replaceAll()`, `String.prototype.isWellFormed()`, `String.prototype.toWellFormed()`, `String.prototype.matchAll()`
- **TypedArrays** — All TypedArray methods including `.at()`, `.findLast()`, `.findLastIndex()`, `.toReversed()`, `.toSorted()`, `.with()`, plus new `Float16Array`
- **Numbers** — BigInt (always enabled), Number methods
- **Operators** — Nullish coalescing (`??`), optional chaining (`?.`), logical assignment (`&&=`, `||=`, `??=`)
- **Classes** — Public/private fields, methods, accessors, static blocks, `in` operator for private fields
- **RegExp** — Full ES2023 support including Unicode properties, `d` flag (indices), `v` flag (Unicode sets), RegExp modifiers, `RegExp.escape()`
- **Symbols** — Full Symbol support including WeakRef/FinalizationRegistry with symbols as weak refs
- **WeakRef** — `WeakRef`, `FinalizationRegistry`
- **Error** — `Error.isError()`
- **globalThis** — Available globally
- **debugger** — Statement supported
- **Hashbang** — Supported by default

### Unsupported Features

- **Tail calls** — Not implemented (the specification is considered too complicated with limited practical interest)
- **ECMA402 (Internationalization API)** — Not supported

Some ES2024 features are also partially supported.

## Module Resolution

ES6 modules use the following name resolution rules:

- Names starting with `.` or `..` are relative to the current module path
- Names without leading `.` or `..` are system modules (`std`, `os`)
- Names ending with `.so` are native C modules using the QuickJS C API

### JSON Modules

As of 2025-09-13, JSON modules and import attributes are supported:

```javascript
import data from "./config.json" with { type: "json" };
```

## Changelog Highlights

### 2025-09-13 (current)

- JSON modules and import attributes
- `JS_PrintValue()` API for pretty-printing
- Pretty print objects in `print()` and `console.log()`
- RegExp `v` flag, RegExp modifiers, `RegExp.escape`
- `Float16Array`
- `Promise.try`
- Improved JSON parser spec conformance
- `std.parseExtJSON()` accepts JSON5 modules
- `JS_FreePropertyEnum()`, `JS_AtomToCStringLen()` API
- `Error.isError()`

### 2025-04-26

- Removed bignum extensions and `qjscalc`
- New BigInt implementation optimized for small numbers
- `WeakRef`, `FinalizationRegistry`, symbols as weak refs
- Built-in float64 printing/parsing for correctness
- Faster repeated string concatenation
- Unhandled promise rejections are fatal by default
- Column numbers in debug information
- `-s`/`--strip-source` options for qjs/qjsc
- `JS_GetAnyOpaque()`
- More exotic object callbacks in `JSClassExoticMethods`

### 2024-01-13

- Top-level await in modules
- `await` in REPL
- Immutable array methods: `.with()`, `.toReversed()`, `.toSpliced()`, `.toSorted()`
- `String.prototype.isWellFormed` / `.toWellFormed()`
- `Object.groupBy`, `Map.groupBy`
- `Promise.withResolvers`
- Class static blocks
- `in` operator for private fields
- RegExp `d` flag
- `os.sleepAsync()`, `os.getpid()`, `os.now()`
- Cosmopolitan build support

### 2023-12-09

- `Object.hasOwn`, `.at()` on String/Array/TypedArray
- `.findLast()` / `.findLastIndex()` on Array/TypedArray
- BigInt enabled even with `CONFIG_BIGNUM` disabled
- Unicode 15.0.0 update

### Historical Milestones

- **2020-09-06**: Logical assignment operators (`&&=`, `||=`, `??=`)
- **2020-04-12**: Cross-realm support, `AggregateError`, `Promise.any`
- **2019-12-21**: Nullish coalescing, optional chaining (ES2020 features)
- **2019-09-01**: `globalThis`, `import.meta`, `debugger` statement
- **2019-08-10**: Public/private class fields, methods, accessors
- **2019-07-28**: Dynamic import, `Promise.allSettled`, `String.prototype.matchAll`, `Object.fromEntries`
- **2019-07-09**: First public release
