# Embedding And FFI

## Contents
- Context Lifecycle
- Environment Loading
- Evaluation API
- GC Preservation From C
- Adding Primitives
- C Pointer Wrapping
- Type System Overview
- chibi-ffi Stubber

## Context Lifecycle

A context manages the heap, VM state, default environment, and execution stack.

```c
#include <chibi/eval.h>

int main(int argc, char** argv) {
  sexp ctx = sexp_make_eval_context(NULL, NULL, NULL, 0, 0);
  sexp_load_standard_env(ctx, NULL, SEXP_SEVEN);
  sexp_load_standard_ports(ctx, NULL, stdin, stdout, stderr, 1);

  /* ... use ctx ... */

  sexp_destroy_context(ctx);
  return 0;
}
```

- **`sexp_make_context(parent, size, max_size)`** — creates a context without evaluation capability (no environment). Use for constructing Scheme objects from C. If `parent` is non-NULL, shares the parent's heap.
- **`sexp_make_eval_context(parent, stack, env, size, max_size)`** — full evaluation context with stack and environment. Pass NULL for defaults.
- **`sexp_destroy_context(ctx)`** — runs finalizers for all heap objects, frees the heap. Does not affect other contexts.

Child contexts share the parent's heap but have separate stacks. Independent contexts (parent=NULL) have separate heaps and can run in different OS threads simultaneously with no locking needed.

## Environment Loading

After creating a context, load the standard environment:

- **`sexp_load_standard_env(ctx, env, SEXP_SEVEN)`** — loads R7RS initialization, constructs feature list, creates `interaction-environment` parameter
- **`sexp_load_standard_ports(ctx, env, in, out, err, leave_open)`** — binds `current-input-port`, `current-output-port`, `current-error-port`. Set `leave_open=1` if you want to reuse the FILE* after the Scheme port closes

The default environment includes compiled-in C primitives plus 10 core special forms. Without `sexp_load_standard_env`, you get only those — useful for minimal embeddings.

## Evaluation API

- **`sexp_eval(ctx, obj, env)`** — evaluate a parsed S-expression in environment `env` (NULL = default)
- **`sexp_eval_string(ctx, str, len, env)`** — read and evaluate a C string as Scheme code. Negative `len` = use strlen
- **`sexp_load(ctx, file, env)`** — load a Scheme source file or shared library by name, searching the module path
- **`sexp_apply(ctx, proc, args)`** — apply procedure `proc` to argument list `args`

Environment can be NULL to use the context default. Returning an exception from any of these raises it in the VM.

## GC Preservation From C

When your C function performs multiple Scheme operations, declare and preserve temporaries:

```c
sexp my_func(sexp ctx, sexp arg1, sexp arg2) {
  sexp_gc_var3(tmp1, tmp2, result);
  sexp_gc_preserve3(ctx, tmp1, tmp2, result);

  /* validate args before preserve — no allocation yet */
  sexp_assert_type(ctx, sexp_stringp, SEXP_STRING, arg1);

  tmp1 = sexp_c_string(ctx, "hello", -1);
  tmp2 = sexp_eval_string(ctx, "(+ 1 2)", -1, NULL);
  result = sexp_cons(ctx, tmp1, tmp2);

  sexp_gc_release3(ctx);
  return result;
}
```

Key rules:
- `sexp_gc_varN` at function start (it's a declaration)
- `sexp_gc_preserveN` before any allocation that could trigger GC
- Validate arguments before preserve (they don't allocate)
- `sexp_gc_releaseN` on every exit path

With Boehm GC, preserve/release become noops.

## Adding Primitives

Register C functions as Scheme primitives:

```c
/* Fixed-arity primitive */
sexp_proc(sexp ctx, sexp self, sexp n, sexp x, sexp y) {
  return sexp_make_fixnum(sexp_unbox_fixnum(x) + sexp_unbox_fixnum(y));
}

/* Register it */
sexp_define_foreign(ctx, env, "my-add", 2, proc);
```

The C function signature is always: `sexp func(sexp ctx, sexp self, sexp n, sexp arg1, ...)`. The `n` parameter holds the actual argument count (useful for variadic functions). The function is responsible for its own type checking.

**Variants:**
- `sexp_define_foreign_opt(ctx, env, name, num_args, func, default_val)` — last argument optional
- `sexp_define_foreign_param(ctx, env, name, num_args, func, param_name)` — default comes from a parameter binding

**Registering record types:**
- `sexp_register_simple_type(ctx, name, parent, slots)` — create a new record type with named fields
- `make-type-predicate`, `make-constructor`, `make-getter`, `make-setter` — generate accessor opcodes

## C Pointer Wrapping

Wrap raw C pointers as first-class Scheme objects with automatic finalization:

```c
/* Register the type with a finalizer */
sexp my_type = sexp_register_c_type(ctx, "my-thing", free);

/* Wrap a pointer */
sexp obj = sexp_make_cpointer(ctx, sexp_type_tag(my_type), ptr, NULL, 1);
```

The `freep` flag (last arg) controls whether the finalizer runs on GC. The optional `parent` argument links the child to a parent object so the parent isn't collected while child references exist.

Look up types with `sexp_lookup_type(ctx, name, tag_or_id)`.

## Type System Overview

**Predicates** (all end in `p`, implemented as macros, may evaluate args multiple times):

- `sexp_booleanp`, `sexp_fixnump`, `sexp_flonump`, `sexp_bignump`, `sexp_numberp`
- `sexp_charp`, `sexp_stringp`, `sexp_bytesp`, `sexp_symbolp`, `sexp_vectorp`
- `sexp_nullp`, `sexp_pairp`, `sexp_procedurep`, `sexp_portp`
- `sexp_exceptionp`, `sexp_contextp`, `sexp_envp`, `sexp_cpointerp`

**Constructors** (take ctx, may return OOM exception):

- `sexp_cons`, `sexp_list1/2/3`, `sexp_make_string`, `sexp_c_string`, `sexp_intern`
- `sexp_make_bytes`, `sexp_make_vector`, `sexp_make_integer`, `sexp_make_flonum`

**Accessors** (no type checking — check with predicates first):

- `sexp_car/cdr`, `sexp_unbox_fixnum`, `sexp_flonum_value`, `sexp_string_data/size/length`
- `sexp_vector_length/ref/set`, `sexp_bytes_length/data/ref/set`

## chibi-ffi Stubber

The `chibi-ffi` tool generates C wrapper code from a Scheme DSL, eliminating hand-written FFI code.

**Workflow:** Write a `.stub` file with Scheme declarations, run `chibi-ffi -c file.stub`, get a `.so`.

**DSL forms:**

```scheme
(c-system-include "netdb.h")

(define-c-struct addrinfo
  finalizer: freeaddrinfo
  predicate: address-info?
  (int              ai_family    address-info-family)
  ((link sockaddr)  ai_addr      address-info-address))

(define-c int connect (int sockaddr int))

(define-c-const int (address-family/unix "AF_UNIX"))
```

**Type modifiers:** `const`, `free`, `maybe-null`, `pointer`, `reference`, `struct`, `link`, `result`, `(value <expr>)`, `(default <expr>)`, `(array <type> [<length>])`.

**Supported input types:** integers (`int`, `long`, `size_t`, `pid_t`, etc.), floats (`float`, `double`), `string` (null-terminated char*), `input-port`/`output-port`, `fileno` (auto-closed on GC), and custom struct types.

**Output:** `.c` file with C wrappers that compile to a shared library loadable via `(include-shared "file")`.
