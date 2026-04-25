# QuickJS ECMAScript Specifications

## ES2023 Support

QuickJS supports nearly complete ES2023 including Annex B (legacy web compatibility) and Unicode features.

### Supported Features

- Full ES2023 specification with modules, async generators, proxies, BigInt
- Some ES2024 features
- Top-level await in modules
- Optional chaining (`?.`)
- Nullish coalescing (`??`)
- Logical assignment operators (`||=`, `&&=`, `??=`)
- Class static blocks
- Public and private class fields/methods/accessors
- `import.meta` and `import.meta.url` / `import.meta.main`
- Dynamic `import()`
- `globalThis`
- `debugger` statement
- `AggregateError` and `Promise.any()`
- `Promise.allSettled()`
- `Promise.withResolvers()`
- `Object.hasOwn()`
- `Object.groupBy()` and `Map.groupBy()`
- `Array.prototype.findLast()` / `findLastIndex()`
- `TypedArray.prototype.at()`, `.with()`, `.toReversed()`, `.toSpliced()`, `.toSorted()`
- `String.prototype.isWellFormed()` / `toWellFormed()`
- `String.prototype.replaceAll()`
- `String.prototype.matchAll()`
- `Object.fromEntries()`
- RegExp `'d'` flag and `'v'` flag
- RegExp modifiers and `RegExp.escape()`
- `Float16Array`
- `Promise.try()`
- `Error.isError()`
- Optional chaining fixes
- Private field `in` operator support

### Unsupported Features

- **Tail calls**: Believed to be too complicated with limited practical interest per TC39 proposal
- **ECMA402 (Intl API)**: Not supported

## Modules

ES6 modules are fully supported.

### Module Resolution

| Pattern | Resolution |
|---------|-----------|
| `./foo` or `../bar` | Relative to current module path |
| `std`, `os` | System modules |
| `foo.so` | Native C module via QuickJS C API |

### Module Detection

Modules are auto-detected when:
- Filename extension is `.mjs`
- First keyword of source is `import`

Override with `-m` (module) or `--script` (script) flags.

## ECMAScript Test Suite (test262)

QuickJS passes nearly 100% of the ECMAScript Test Suite for ES2023 features.

### Running Tests

```bash
# Install test262
git clone https://github.com/tc39/test262.git test262
cd test262
patch -p1 < ../tests/test262.patch
cd ..

# Run tests
make test2

# Update error list
make test2-update

# Run single test
./run-test262 -c test262.conf -f filename.js

# Run from test N
./run-test262 -c test262.conf N
```

### Test Output Files

| File | Description |
|------|-------------|
| `test262_errors.txt` | Current list of errors |
| `test262_report.txt` | Full logs of all tests |

Use `./run-test262 -u` to update the error list when fixing issues.

## Sub-projects (Embedded Libraries)

QuickJS embeds these C libraries that can be used in other projects:

### libregexp
Small, fast regular expression library fully compliant with ES2023 (~15 KiB x86 code).

### libunicode
Small Unicode library supporting case conversion, normalization, script queries, general category queries, and all binary properties (~45 KiB x86 code).

### dtoa
Small library implementing float64 printing and parsing.
