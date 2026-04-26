# Interop & Utilities

## FFI (`bun:ffi`)

Call native libraries from JavaScript. Works with C, C++, Rust, Zig, Nim, Kotlin, and any language supporting the C ABI.

> **Warning**: `bun:ffi` is experimental with known bugs. For production, prefer [Node-API modules](#node-api-modules).

### Basic Usage

```ts
import { dlopen, FFIType, suffix } from "bun:ffi";

const { symbols: { sqlite3_libversion } } = dlopen(
  `libsqlite3.${suffix}`,  // platform-specific extension
  {
    sqlite3_libversion: {
      args: [],
      returns: FFIType.cstring,
    },
  },
);

console.log(`SQLite version: ${sqlite3_libversion()}`);
```

### Calling a Custom Library

**Zig source (`add.zig`)**:

```zig
pub export fn add(a: i32, b: i32) i32 {
    return a + b;
}
```

Compile: `zig build-lib add.zig -dynamic -OReleaseFast`

```ts
import { dlopen, FFIType, suffix } from "bun:ffi";
const { i32 } = FFIType;

const lib = dlopen(`libadd.${suffix}`, {
  add: { args: [i32, i32], returns: i32 },
});

console.log(lib.symbols.add(1, 2)); // 3
```

**Rust source (`add.rs`)**:

```rust
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 { a + b }
```

Compile: `rustc --crate-type cdylib add.rs`

### FFI Types

- `i8`, `i16`, `i32`, `i64`, `i64_fast` — signed integers
- `u8`, `u16`, `u32`, `u64`, `u64_fast` — unsigned integers
- `f32`, `f64` — floating point
- `bool`, `char`
- `buffer`, `cstring` — `char*`
- `ptr` (aliases: `pointer`, `void*`) — `void*`
- `function` (aliases: `fn`, `callback`) — function pointers
- `napi_env`, `napi_value` — Node-API interop

Bun generates and JIT-compiles C bindings using embedded TinyCC for fast type conversion.

## Node-API Modules

The most stable way to interact with native code from Bun:

```ts
// Load a .node binary (compiled N-API module)
const native = require("./my-native-addon.node");
native.doSomething();
```

Bun supports loading `.node` files via `require()` or dynamic import.

## C Compiler

Bun embeds TinyCC for compiling C code at runtime:

```ts
import { compile } from "bun:compile";

const wasm = compile(`
  int add(int a, int b) { return a + b; }
`, {
  backend: "wasm",
});

// Use the compiled WASM module
```

## Transpiler API

Access Bun's transpiler programmatically:

```ts
import { transpileSync } from "bun";

const result = transpileSync("code.tsx", `
  import React from 'react';
  export const App = () => <div>Hello</div>;
`);

result.code;    // transpiled JavaScript
result.map;     // source map
```

## Hashing

Built-in cryptographic hashing:

```ts
import { hash } from "bun";

// SHA-256
const sha256 = hash("sha256", "hello world");

// MD5
const md5 = hash("md5", "hello world");

// Multiple algorithms: sha1, sha256, sha384, sha512, md5, xxhash64, murmur32
```

## Glob

Built-in glob pattern matching:

```ts
import { glob } from "bun";

// Sync
const files = glob.sync("src/**/*.ts");

// Async
const asyncFiles = await glob("src/**/*.ts");

// Stream
for await (const file of glob.stream("src/**/*.ts")) {
  console.log(file);
}
```

Supported patterns: `*`, `**`, `{a,b}`, `?`, `[abc]`, `[!abc]`, negation with `!`.

## Semver

Built-in semantic versioning utilities:

```ts
import { semver } from "bun";

semver.satisfies("1.2.3", "^1.0.0");  // true
semver.clean("  ^1.0.0  ");            // "^1.0.0"
semver.major("1.2.3");                 // 1
```

## TOML / YAML / JSON5

Import data files directly:

```ts
import config from "./config.toml";
import settings from "./settings.yaml";
import data from "./data.json5";
```

Or parse programmatically:

```ts
import { TOML } from "bun";
const parsed = TOML.parse(tomlString);

import { YAML } from "bun";
const yamlData = YAML.parse(yamlString);

import { JSON5 } from "bun";
const json5Data = JSON5.parse(json5String);
```

## HTML Rewriter

Stream-based HTML parsing and transformation:

```ts
const response = await fetch("https://example.com");

const rewriter = new HTMLRewriter()
  .on("a", {
    element(element) {
      const href = element.getAttribute("href");
      if (href) {
        element.setAttribute("href", href + "?tracked=1");
      }
    },
  });

await rewriter.transform(response).text();
```

## Color

Terminal color output:

```ts
import { color } from "bun";

console.log(color.red("Error!"));
console.log(color.bold(color.blue("Info")));
```

## Utilities

### `Bun.sleep`

```ts
await Bun.sleep(1000); // sleep 1 second
```

### `Bun.randomUUID`

```ts
const id = Bun.randomUUID(); // generates a v4 UUID
```

### `Bun.gzip` / `Bun.gunzip`

```ts
const compressed = await Bun.gzip(data);
const decompressed = await Bun.gunzip(compressed);
```

### `Bun.deflate` / `Bun.inflate`

```ts
const deflated = await Bun.deflate(data);
const inflated = await Bun.inflate(deflated);
```

### `Bun.escapeHTML`

```ts
const safe = Bun.escapeHTML("<script>alert('xss')</script>");
```

### `Bun.deepEquals`

```ts
Bun.deepEquals({ a: 1 }, { a: 1 }); // true
```

### `Bun.which`

Find executable in PATH:

```ts
const path = Bun.which("node"); // "/usr/bin/node" or null
```

### `import.meta` Utilities

```ts
import.meta.dir;   // directory of current file
import.meta.file;  // full path of current file
import.meta.path;  // same as import.meta.file
```
