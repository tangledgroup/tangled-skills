# Language Semantics

## Contents
- Scheme Features Retained
- Restrictions vs Full Scheme
- Comparison with C
- Compile-Time Top-Level Evaluation

## Scheme Features Retained

Pre-Scheme code is valid Scheme code. With a small compatibility library, Pre-Scheme programs can run directly in a Scheme interpreter for interactive development and debugging.

**Syntax:** Full S-expression syntax with prefix notation. All standard special forms (`lambda`, `let`, `letrec`, `if`, `cond`, `case`, `begin`) are available.

**Macros:** Scheme's hygienic macro system is fully supported. Macros manipulate source code as data structures, enabling new control-flow operators, DSLs, and boilerplate elimination. The Restoration project targets `syntax-case` macros for R7RS portability.

**Tail recursion:** Local tail-recursive procedures (via `let` or `letrec`) are guaranteed to run in constant space. This enables safe iterative processes using recursion instead of mutation-based loops. Note: only local recursion is optimized — not universal tail-call elimination.

**First-class procedures:** Procedures are first-class values and can be passed as arguments, returned from functions, and stored in data structures. However, lambda expressions that capture free variables requiring heap-allocated closures are rejected at compile time (see Restrictions).

## Restrictions vs Full Scheme

Pre-Scheme deliberately omits features that require a garbage collector or runtime type system:

**No garbage collector:** Memory is managed manually. `make-vector` and `make-string` compile to `malloc`; the programmer must explicitly deallocate. This is the most significant departure from idiomatic Scheme.

**No runtime closures:** Lambda expressions capturing locally-bound variables in ways requiring dynamic closure allocation produce compilation errors. Compile-time top-level code has no this restriction — it's evaluated during compilation when all bindings are known statically.

**Limited tail recursion:** Only local recursion (`let`/`letrec`) is optimized to constant space. Scheme's universal tail-call guarantee (any tail position, including mutually recursive calls across module boundaries) is not provided.

**Strict static typing:** Type information is fully resolved at compile time. No runtime type predicates (`number?`, `string?`, `list?`) exist. Any runtime type system must be implemented in application code, as in C.

**Limited first-class data types:** Only C-native types are supported: fixed-size integers (long fixnums), floating-point numbers (flonums), character arrays, and record types. No lists, no first-class continuations, no heterogenous collections. Complex data structures require explicit record-based implementations.

## Comparison with C

Compared to C, Pre-Scheme offers:

- **Scheme semantics:** Code is Scheme code — familiar syntax, prefix notation, uniform expression model (everything returns a value)
- **Macros:** Hygienic macro system for compile-time code generation and language extension
- **Compile-time evaluation:** Top-level expressions evaluated at compile time, building static data structures incrementally
- **Type inference:** Hindley/Milner type reconstruction eliminates manual type annotations while choosing optimal machine representations
- **Polymorphism:** Parametric polymorphism with automatic monomorphization — one procedure definition works across types
- **Efficient tail recursion:** Constant-space iteration via recursion, without relying on compiler-specific optimizations

Compared to Scheme, Pre-Scheme lacks:

- Garbage collection (manual memory management instead)
- Runtime closures and full lexical scoping for long-lived lambdas
- Universal tail-call optimization
- Lists, continuations, and the full numeric tower
- Runtime type predicates and dynamic typing

## Compile-Time Top-Level Evaluation

The top-level of every Pre-Scheme file is evaluated at compile time. This means:

- Complex data structures can be built incrementally and treated as static constants
- Procedures defined at top-level are compiled into the generated C code
- The compiler uses this to perform partial evaluation and constant folding
- Code evaluated at compile time has full access to closures and dynamic features (these restrictions apply only to runtime code)

This dual-phase model — compile-time Scheme with full features, runtime Pre-Scheme with restrictions — is central to how Pre-Scheme programs are structured.
