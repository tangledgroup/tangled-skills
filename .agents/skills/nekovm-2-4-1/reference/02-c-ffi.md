# C FFI

## Contents
- Primitive Definition
- Value Manipulation API
- Type Checking
- Buffers
- Objects API
- Function Callbacks
- Abstracts and Kinds
- Memory Management
- 32-Bit Integers
- Misc API

## Primitive Definition

Primitives are C functions exposed to Neko code. Include `neko.h` and link with `libneko.so` (Unix) or `neko.lib` (Windows). Compile into a shared library named `<name>.ndll`.

```c
#include <neko.h>

value my_prim( value arg1, value arg2 ) {
    return alloc_int(val_int(arg1) + val_int(arg2));
}

DEFINE_PRIM(my_prim, 2);  // 2 fixed arguments
```

For variable or >5 arguments, use `DEFINE_PRIM_MULT`:

```c
value my_var_prim( value *args, int nargs ) {
    // args[0..nargs-1] are the arguments
    return val_null;
}
DEFINE_PRIM_MULT(my_var_prim);
```

Call from Neko: `$loader.loadprim("library@function_name", nargs)`. Use `-1` as nargs for `DEFINE_PRIM_MULT` primitives.

## Value Manipulation API

All values use the `value` type. The API is defined entirely in `neko.h`; most functions are macros (zero overhead).

### Constants

- `val_null` — Neko null value
- `val_true` / `val_false` — Singleton boolean instances

### Type checks

- `val_is_null(v)` / `val_is_int(v)` / `val_is_float(v)` / `val_is_string(v)` / `val_is_bool(v)` / `val_is_array(v)` / `val_is_object(v)` / `val_is_function(v)` / `val_is_abstract(v)` — return 1 or 0
- `val_is_kind(v, k)` — abstract is of kind `k`
- `val_is_number(v)` — int or float

### Access (ensure type first)

- `val_int(v)` / `val_bool(v)` / `val_float(v)` / `val_string(v)` / `val_strlen(v)` / `val_number(v)`
- `val_array_ptr(v)` / `val_array_size(v)`
- `val_fun_nargs(v)` — argument count
- `val_data(v)` / `val_kind(v)` — abstract data and kind

### Allocation

- `alloc_int(i)` — macro, fast
- `alloc_float(f)`
- `alloc_bool(b)` — 0 = false, nonzero = true
- `alloc_array(size)`
- `alloc_string(str)` — makes a copy
- `alloc_empty_string(n)` — uninitialized string of n bytes
- `copy_string(str, size)` — copy first `size` bytes

## Type Checking

Use `val_check*` macros at the start of primitives. They call `neko_error()` (returns C `NULL`) on failure, which the VM catches and raises as an exception.

```c
value my_prim( value s, value n ) {
    val_check(s, string);
    val_check(n, int);
    // ...
}
```

Available checks:
- `val_check(v, type)` — general type check (int, float, string, bool, array, object, function, number)
- `val_check_kind(v, kind)` — abstract of specific kind
- `val_check_function(v, nargs)` — function accepting exactly `nargs` arguments

## Buffers

Buffers are NOT values — cannot be returned outside a primitive. They are GC-tracked (no manual free needed). Useful for constructing strings from mixed C strings and Neko values.

- `alloc_buffer(str)` — create buffer (empty if `str` is `NULL`)
- `val_buffer(b, v)` — append string representation of value `v`
- `buffer_append(b, str)` — append C string
- `buffer_append_sub(b, str, n)` — append first `n` bytes of C string
- `buffer_to_string(b)` — finalize to Neko string value

```c
value concat( value v1, value v2 ) {
    buffer b = alloc_buffer("Values = ");
    val_buffer(b, v1);
    buffer_append_sub(b, ",xxx", 1);  // append ','
    val_buffer(b, v2);
    return buffer_to_string(b);
}
```

## Objects API

- `alloc_object(o)` — empty object if `o` is `NULL`/`val_null`, otherwise copy
- `val_id("field_name")` — get hashed field identifier
- `val_field(o, f)` — read field (returns `val_null` if missing)
- `alloc_field(o, f, v)` — set/replace field
- `val_iter_fields(o, callback, userdata)` — iterate all fields: `void callback(value v, field f, void *p)`
- `val_field_name(f)` — reverse hash to string name (or `val_null`)

**Creating objects with methods:**

```c
value make_point( value x, value y ) {
    val_check(x, number);
    val_check(y, number);
    value o = alloc_object(NULL);
    alloc_field(o, val_id("x"), x);
    alloc_field(o, val_id("y"), y);
    // Add %%__string%% method
    value f = alloc_function(point_to_string, 0, "point_to_string");
    alloc_field(o, val_id("%%__string%%"), f);
    return o;
}

value point_to_string() {
    value o = val_this();  // current object context
    val_check(o, object);
    buffer b = alloc_buffer("Point: ");
    val_buffer(b, val_field(o, val_id("x")));
    buffer_append(b, ",");
    val_buffer(b, val_field(o, val_id("y")));
    return buffer_to_string(b);
}
```

## Function Callbacks

Call Neko functions from C. The general form:

```c
value ret = val_callEx(vthis, f, args, nargs, &exc);
```

- `vthis` — the `this` value inside the call
- `f` — the function to call
- `args` — C array of `value` arguments (left-to-right)
- `nargs` — argument count
- `exc` — pointer to capture exceptions (`NULL` = let exceptions propagate)

Convenience variants:
- `val_call0(f)` / `val_call1(f, a)` / `val_call2(f, a1, a2)` / `val_call3(f, a1, a2, a3)`
- `val_callN(f, args, nargs)`
- `val_ocall0(o, field)` / `val_ocall1(o, field, a)` / `val_ocall2(o, field, a1, a2)` — call method on object (field is hash, not value)

**Storing a Neko function for later callback:**

```c
value *function_storage = NULL;

value set_handler( value f ) {
    val_check_function(f, 1);
    if( function_storage == NULL )
        function_storage = alloc_root(1);
    *function_storage = f;
    return val_null;
}

// Later, call the stored callback:
value ret = val_call1(*function_storage, alloc_string("Hello"));
```

Use `alloc_root(n)` for static variables that hold Neko values — GC scans roots automatically. Free with `free_root`.

## Abstracts and Kinds

Abstracts wrap C pointers in a GC-safe Neko value tagged with a *kind* (type identifier). The VM cannot access the kind or data — only your primitives can, ensuring memory safety.

```c
DEFINE_KIND(k_myfile);  // Define a kind (convention: k_ prefix)

// Create abstract wrapping a C pointer
value create_file( const char *path ) {
    FILE *fp = fopen(path, "r");
    if( !fp ) return val_null;
    value v = alloc_abstract(k_myfile, fp);
    // Optional: auto-free on GC
    val_gc(v, (void (*)(value))fclose);
    return v;
}

// Use abstract in a primitive
value read_file( value f ) {
    val_check_kind(f, k_myfile);
    FILE *fp = val_data(f);
    // ... use fp ...
    return val_null;
}

// Manual close — invalidate the abstract
value close_file( value f ) {
    val_check_kind(f, k_myfile);
    fclose(val_data(f));
    val_kind(f) = NULL;  // Mark as unusable
    return val_null;
}
```

- `val_is_abstract(v)` / `val_is_kind(v, k)` — type checks
- `val_data(v)` — get C pointer
- `val_kind(v)` — get kind (also assignable to set to `NULL`)
- `val_gc(v, finalizer)` — bind/unbind GC finalizer (`NULL` removes)

## Memory Management

Neko provides GC-managed allocation for C code:

- `alloc(n)` — allocate n bytes, scanned by GC. Can store other `value`s and `alloc`'ed pointers. Freed automatically when unreachable.
- `alloc_private(n)` — allocate n bytes, NOT scanned by GC. For raw data (strings, buffers). Do not store Neko values in it.
- `alloc_root(n)` — allocate a root pointer holding up to n `value`s. Always scanned by GC. Must be freed with `free_root`. Use sparingly; prefer abstract values for static storage.

Static C variables are not reachable by the GC — use roots or abstracts if they hold Neko values.

## 32-Bit Integers

Neko integers are signed 31-bit. For full 32-bit, use the int32 abstract type:

- `val_is_int32(v)` — true for both regular int and int32
- `val_int32(v)` — extract as full 32-bit integer
- `val_is_kind(v, k_int32)` — exactly an int32 (not a regular int)
- `alloc_int32(i)` — create int32 (slower than `alloc_int` macro, allocates memory)
- `alloc_best_int(i)` — uses `alloc_int` if fits in 31 bits, otherwise `alloc_int32`
- `val_check(v, int32)` — accepts both regular int and int32

## Misc API

- `val_compare(a, b)` — compare per Neko spec: returns 0 (equal), -1 (a < b), 1 (a > b), or `invalid_comparison`
- `val_print(v)` — print value to VM output
- `val_hash(v)` — hash any value to positive integer
- `val_throw(v)` / `val_rethrow(v)` — throw exception from C
- `failure(msg)` — throw failure exception with C string message (includes filename + line)
- `bfailure(buf)` — same but with a buffer
- `neko_error()` — return C `NULL` to raise an exception (use the macro, not bare `return NULL`)
