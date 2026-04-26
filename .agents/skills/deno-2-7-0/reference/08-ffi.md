# Foreign Function Interface (FFI)

## Overview

Deno's FFI allows JavaScript and TypeScript code to call functions in native dynamic libraries written in C, C++, or Rust. This enables integrating native performance and capabilities directly into Deno applications.

> **Security warning:** Native libraries loaded via FFI have the same access level as the Deno process itself — they can access the filesystem, network, environment variables, and execute system commands. Always trust the libraries you load.

## Basic Usage

The `Deno.dlopen()` API loads a dynamic library and creates JavaScript bindings:

```typescript
const dylib = Deno.dlopen("libexample.so", {
  add: { parameters: ["i32", "i32"], result: "i32" },
});

console.log(dylib.symbols.add(5, 3)); // 8

dylib.close();
```

Run with: `deno run --allow-ffi=./libexample.so script.ts`

## Supported Types

| FFI Type | JavaScript | C Type | Rust Type |
|----------|-----------|--------|-----------|
| `i8` | number | char / signed char | i8 |
| `u8` | number | unsigned char | u8 |
| `i16` | number | short int | i16 |
| `u16` | number | unsigned short int | u16 |
| `i32` | number | int / signed int | i32 |
| `u32` | number | unsigned int | u32 |
| `i64` | bigint | long long int | i64 |
| `u64` | bigint | unsigned long long int | u64 |
| `usize` | bigint | size_t | usize |
| `isize` | bigint | ssize_t | isize |
| `f32` | number | float | f32 |
| `f64` | number | double | f64 |
| `void` | undefined | void | () |
| `pointer` | {} \| null | void * | *mut c_void |
| `buffer` | TypedArray \| null | uint8_t * | *mut u8 |
| `function` | {} \| null | function pointer | extern "C" fn() |

Notes:
- `void` can only be used as a result type
- `pointer` is an opaque object or `null` for null pointers (since Deno 1.31)
- `buffer` accepts TypedArrays as parameters but returns a pointer object as result

## Working with Structs

Define C structures using the struct type:

```typescript
const pointStruct = {
  fields: { x: "f64", y: "f64" },
} as const;

const signatures = {
  distance: {
    parameters: [{ struct: pointStruct }, { struct: pointStruct }],
    result: "f64",
  },
} as const;

const dylib = Deno.dlopen("libexample.so", signatures);

// Structs are represented as TypedArrays with automatic padding
const pointData = new Float64Array([1.0, 2.0, 4.0, 6.0]);
const dist = dylib.symbols.distance(
  pointData.buffer.slice(0, 16),
  pointData.buffer.slice(16),
);
```

Packed structs can be defined by using `u8` fields to avoid padding.

## Working with Callbacks

Pass JavaScript functions as callbacks to native code:

```typescript
const signatures = {
  setCallback: { parameters: ["function"], result: "void" },
  runCallback: { parameters: [], result: "void" },
} as const;

const dylib = Deno.dlopen("libexample.so", signatures);

// Create a callback
const callback = new Deno.UnsafeCallback(
  { parameters: ["i32"], result: "void" } as const,
  (value: number) => {
    console.log("Callback received:", value);
  },
);

// Pass the callback pointer to native code
dylib.symbols.setCallback(callback.pointer);

// Native code will call our JavaScript function
dylib.symbols.runCallback();

// Always clean up
callback.close();
dylib.close();
```

## Best Practices

- Always call `dylib.close()` when done to release native resources
- Always call `callback.close()` for UnsafeCallback instances
- Use specific paths in `--allow-ffi` rather than allowing all FFI access
- Validate input data before passing to native functions
- Handle potential crashes from native code gracefully
- Consider using WebAssembly as a safer alternative when possible

## Alternatives to FFI

- **WebAssembly** — Compile C/Rust to Wasm for a sandboxed execution environment
- **Node-API (N-API)** — Use N-API addons through `--allow-ffi` permission
- **Subprocesses** — Spawn native executables via `Deno.run()` or `new Deno.Command()`
