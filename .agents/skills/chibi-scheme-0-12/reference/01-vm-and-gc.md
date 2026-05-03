# VM And GC

## Contents
- Tagged Pointer Layout
- Heap Object Model
- Precise Garbage Collection
- Opcode Virtual Machine
- Boehm GC Alternative

## Tagged Pointer Layout

Chibi uses a tagged-pointer scheme where the low bits of every `sexp` value encode its type. This allows small values to be stored directly in the pointer without heap allocation.

**Bit patterns (low 8 bits):**

- `...1` — fixnum (integer shifted left by 1, low bit set)
- `...00` — heap pointer (type tag in object header)
- `...010` — string cursor (optional, can be disjoint or shared with fixnum)
- `...0110` — immediate symbol (optional, for small interned symbols)
- `...00001110` — immediate flonum (optional, floats stored inline)
- `...00011110` — character
- `...00101110` — reader label (optional, for shared structure read/write)
- `...00111110` — unique immediates: NULL, TRUE, FALSE

The constants `SEXP_FIXNUM_BITS`, `SEXP_POINTER_BITS`, etc. in `sexp.h` define the bit widths. On 64-bit systems this gives 63 bits for fixnums (values up to 2^62).

**Immediate values available as C macros:** `SEXP_FALSE`, `SEXP_TRUE`, `SEXP_NULL`, `SEXP_EOF`, `SEXP_VOID`, `SEXP_ZERO` through `SEXP_TEN`, `SEXP_NEG_ONE`.

## Heap Object Model

Heap-allocated objects carry a type tag in their header. The tag determines the object's layout:

- **Pairs**: car/cdr pointers (the fundamental cons cell)
- **Strings**: length + UTF-8 byte array
- **Vectors**: length + element array
- **Bytevectors**: length + raw byte array
- **Bignums**: sign + digit array
- **Ratios**: numerator + denominator bignums
- **Complex numbers**: real + imaginary parts
- **Procedures/bytecode**: compiled code + closure environment
- **Ports**: file descriptor or buffer + direction
- **C pointers**: type tag + void* + optional parent reference for GC linking

Object allocation is done through the context's heap. The heap grows in segments and tracks free space via a free list.

## Precise Garbage Collection

Chibi's default GC is **precise** (knows exactly which words are pointers) and **non-moving** (objects never change address). Non-moving is essential for C interop — C code can hold raw pointers into the Scheme heap without any write barriers or root scanning.

**From C code, use the preserve/release pattern:**

```c
sexp foo(sexp ctx, sexp bar) {
  sexp_gc_var2(tmp, res);       // declare variables at function start
  sexp_gc_preserve2(ctx, tmp, res); // register with GC before any allocation
  tmp = sexp_cons(ctx, bar, SEXP_NULL);
  res = sexp_eval_string(ctx, "(+ 1 2)", -1, NULL);
  sexp_gc_release2(ctx);        // unregister before returning
  return res;
}
```

The `sexp_gc_varN` macro declares N variables. `sexp_gc_preserveN` registers them with the current context's GC roots. `sexp_gc_releaseN` removes them. The preserve/release must be paired — missing a release leaks root entries, missing a preserve risks collecting live objects.

Macros exist for N=1 through 6. For more variables, use `sexp_gc_varn`, `sexp_gc_preserven`, `sexp_gc_releasen`.

**Manual object preservation:** `sexp_preserve_object(ctx, obj)` increments an absolute reference count, keeping the object alive regardless of heap reachability. Pair with `sexp_release_object(ctx, obj)`.

## Opcode Virtual Machine

Chibi compiles Scheme source to bytecode executed by a register-based VM. The compilation pipeline:

1. **Reader** parses S-expressions
2. **Macro expansion** applies syntactic transformations
3. **Compiler** translates to intermediate AST
4. **Simplifier** (optional, `SEXP_USE_SIMPLIFY`) performs constant folding, dead code elimination, and other optimizations
5. **Code generator** emits opcodes

The opcode set is small — enough to express let-bindings, closures, application, arithmetic, comparison, vector/string operations, and control flow. The VM uses a stack for argument passing and return values.

Use `(chibi disasm)` to inspect compiled bytecode:

```scheme
(import (chibi disasm))
(disassemble (lambda (x) (+ x 1)))
```

## Boehm GC Alternative

Compile with `SEXP_USE_BOEHM=1` (or `make SEXP_USE_BOEHM=1`) to use the Boehm conservative GC instead of Chibi's precise collector. With Boehm:

- `sexp_gc_varN` becomes a plain declaration
- `sexp_gc_preserveN` and `sexp_gc_releaseN` become noops
- The GC scans all memory for potential pointers (slower, but handles C-side references automatically)
- Trade-off: convenience over precision — Boehm may keep unreachable objects alive if stack/heap happen to contain pointer-like values
