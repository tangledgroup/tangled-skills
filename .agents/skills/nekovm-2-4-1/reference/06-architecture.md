# Architecture

## Contents
- VM Overview
- Value Representation
- Neko vs Lua Comparison
- Closures
- OO Support
- FFI Design
- Performance Characteristics
- Language Interoperability

## VM Overview

NekoVM is a stack-based bytecode virtual machine with 63 opcodes. Bytecode files (`.n`) are loaded and executed by the `neko` binary or embedded via the C API. The VM uses a Boehm conservative garbage collector for automatic memory management.

**Bytecode format:** Opcodes have one optional 32-bit parameter, stored as one or two 32-bit values. The bytecode loader validates all jump offsets and performs optimizations on load (e.g., inlining global addresses).

**JIT:** Optional JIT compilation available on select platforms. Disable with `NEKO_JIT_DISABLE=ON` CMake option.

## Value Representation

Neko uses **value pointers** (not value structs), so passing values involves pointer copying, not struct copying. This is more efficient than Lua's approach of copying 12-byte value structures.

**Integers are the only unboxed type:** A 31-bit signed integer has its last bit set to `1`, while all other values are aligned pointers (last bit `0`). Type checking requires checking oddness first.

**Type-specific structures:**

| Type | Structure |
|------|-----------|
| null | Single shared instance, no data |
| bool | Two shared instances (`true`/`false`), no data |
| int | Raw 31-bit integer (tagged via last bit) |
| float | Pointer to `{ type_tag, double value }` — allocated by GC |
| string | Pointer to `{ type_tag \| length, bytes... }` — mutable, length in tag |
| array | Pointer to `{ type_tag, size, elements[] }` |
| object | Pointer to `{ type_tag, prototype, fields[] }` — sorted flat array |
| function | Pointer to `{ type_tag, nargs, code_ptr, env[] }` |
| abstract | Pointer to `{ type_tag, kind, data_pointer }` |

## Neko vs Lua Comparison

Neko and Lua share similar goals (embeddable scripting VM) but make different architectural choices.

### Value types

Both have null, bool, float/double, string, function, and user data. Key differences:
- Neko has a separate `int` type (31-bit); Lua uses only floats for numbers
- Neko separates `array` (fixed-size integer-indexed) and `object` (hashed-field); Lua has one generic `table`
- Neko's `abstract` combines Lua's `lightuserdata` and `userdata` with runtime type checking via *kind*

### Strings

| | Neko | Lua |
|--|------|-----|
| Mutability | Mutable | Immutable |
| Memory | Can have duplicates | Interdeduped (one copy) |
| Comparison | Linear scan | Pointer comparison |
| Creation | Fast (mutable append) | Slower for incremental building |

Neko's mutable strings make byte-by-byte file reading linear instead of quadratic. Lua's immutable strings enable O(1) equality and precomputed hashes for table indexing.

### Objects vs Tables

Neko objects use compile-time hashed field names stored in a sorted flat array with O(log n) dichotomy lookup. This is faster than Lua tables for known-field access but cannot handle runtime-generated field names.

**Prototype chains:** Neko uses `$objsetproto` for inheritance; Lua uses `__index` metamethods (which can be either a table or a function). Both enable class-like patterns without per-instance method copies:

```neko
// Neko prototype chain
classA = { foo => function() { } };
classB = { foo2 => function() { } };
$objsetproto(classB, classA);  // B extends A
inst = $new(null);
$objsetproto(inst, classA);    // new instance of A
```

## Closures

Neko stores closure environments as small arrays accessed by integer index. When a function captures a variable, the environment array holds the captured values:

```neko
add = function(x) {
    return function(y) { return x + y; };
};
add2 = add(2);
$print(add2(3));  // 5
```

Compiled to opcodes: `AccEnv 0` (capture `x`), `MakeEnv 1` (create closure of size 1).

**Key difference from Lua:** Modifying a captured variable inside a closure does not affect the outer scope in Neko:

```neko
var x = 0;
f = function() { x += 1; };
f();
$print(x);  // 0 in Neko (the env variable was incremented, not the outer x)
// Same code in Lua prints 1
```

## OO Support

Neko provides a `this` register for object context. Calling `o.method(args)` sets `this = o` inside the method; calling `(o.method)(args)` does not (plain function call). This distinguishes method calls from function calls without special syntax.

Methods can be shared via prototypes rather than duplicated per instance, keeping memory usage low. High-level languages targeting Neko (like Haxe) use method-closure conversion only when an object method is extracted and used as a standalone value, minimizing overhead.

## FFI Design

Neko's C FFI uses **direct function arguments** instead of stack manipulation:

```c
// Neko: direct args
value do_add( value a, value b ) {
    val_check(a, float);
    val_check(b, float);
    return alloc_float(val_float(a) + val_float(b));
}

// Lua: stack manipulation
int do_add(lua_State *L) {
    lua_pushnumber(L, luaL_checknumber(L,1) + luaL_checknumber(L,2));
    return 1;
}
```

**Advantages of Neko's approach:**
- No VM stack to manipulate — less chance of corruption
- Argument count is enforced by function type at call time
- Single return value (multiple returns via arrays)
- VM instance in thread-local storage (not passed as argument)
- Macros for common operations (zero overhead vs function calls)

**Restrictions compared to Lua:** No arbitrary stack manipulation, no multiple return values from C functions.

## Performance Characteristics

| Workload | Neko advantage | Lua advantage |
|----------|---------------|---------------|
| Small arrays + integer recursion | Faster (unboxed ints, fast array access) | — |
| Heavy floating-point calculus | — | Faster (unboxed floats, register-based VM) |
| Global variable access | Faster (inlined addresses) | Slower (hash table lookup) |
| String creation/modification | Faster (mutable strings) | Slower (immutable, must concat) |
| Hash table indexing with string keys | — | Faster (precomputed hashes) |

Neko is stack-based (vs Lua's register-based since 5.0). Stack-based VMs have simpler code generation but more push/pop instructions. Register-based VMs reduce instruction count but require more complex register allocation.

## Language Interoperability

Neko is designed as a **common runtime for multiple languages**. The approach is data sharing with language-specific APIs wrapping common Neko data structures:

**The Array Problem:** Different languages have different array semantics (resizable, immutable, OO API). Neko provides a minimal fixed-size array that any language can wrap with its own API. A generic wrapper converts between the Neko array and the language-specific representation.

**The Class Problem:** Neko does not enforce a class system. Language generators choose how to represent classes within Neko objects. The dynamic type system enables static and dynamically typed languages to interact. Preferred practice: use Neko objects for cross-language interaction so field access works uniformly.

**Globals:** Stored by inlined address (not hash table), providing fast access but preventing runtime-generated global names or resizing the global table — trade-offs favoring performance over flexibility.
