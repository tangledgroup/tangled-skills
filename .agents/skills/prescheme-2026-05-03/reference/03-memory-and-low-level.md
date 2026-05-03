# Memory and Low-Level Features

## Contents
- Manual Memory Management
- Record Types
- Fixed-Size Numeric Types
- C Interoperability and FFI
- No Runtime Closures Implications

## Manual Memory Management

Pre-Scheme has no garbage collector. The programmer manages memory explicitly, similar to C.

**Allocation:** `make-vector`, `make-string`, and record constructors compile to `malloc` (or equivalent platform allocator). The returned pointer must be tracked by the caller.

**Deallocation:** Explicit deallocation calls free heap memory. The compiler provides polymorphic `deallocate` that works on any heap-allocated type. Forgetting to deallocate produces memory leaks identical to C.

**Stack vs heap:** Local variables and procedure arguments use stack allocation (C locals). Only explicitly allocated collections use the heap. This mirrors C's storage model precisely.

**Patterns for safe management:**
- Allocate in one module, deallocate in the same module when possible
- Use tail recursion to avoid accumulating heap allocations across iterations
- Design data structures with clear ownership semantics (one owner responsible for deallocation)
- Compile-time top-level evaluation builds static data that never needs runtime allocation

## Record Types

Record types are the primary data structure mechanism in Pre-Scheme, analogous to C structs.

**Definition:** Records declare named fields with inferred or explicit types. The compiler generates a C struct and accessor functions (constructors, field getters/setters).

**Usage:** Records support product types (all fields present simultaneously). They are the foundation for implementing complex data structures — linked lists, trees, hash tables, etc., must be built from records rather than using Scheme's built-in cons cells.

**Nascent sum types:** The original Pre-Scheme had incomplete support for C-style tagged unions (sum types). The Restoration project plans to complete this feature, enabling full algebraic data types with pattern matching syntax.

## Fixed-Size Numeric Types

The current Pre-Scheme implements two numeric types:
- **Long fixnums:** Signed integers matching the C `long` type
- **Flonums:** Floating-point numbers matching the C `double` type

Arithmetic operations are typed separately for each kind (integer +, float +, etc.), requiring the programmer to choose the correct operation or rely on type inference to select it.

**Planned extension:** The Restoration project will add the full set of sized numeric types found in modern systems languages: 8/16/32/64-bit signed and unsigned integers, plus 32/64-bit floating-point numbers. Polymorphic arithmetic operators will be introduced to avoid combinatorial explosion of operation variants.

## C Interoperability and FFI

Pre-Scheme compiles to C, making interoperability natural rather than requiring a separate FFI layer.

**Direct integration:** Generated C code can call C library functions directly. System calls, POSIX APIs, and platform-specific libraries are accessible without wrappers.

**Type correspondence:** Pre-Scheme types map directly to C types:
- Long fixnum → `long`
- Flonum → `double`
- String → `char*` (null-terminated in current implementation)
- Record → C struct with matching field layout

**String representation:** Current strings are C-style null-terminated byte arrays. The Restoration project plans length-prefixed, null-terminated UTF-8 strings as the default, with bytevector type for raw byte handling (matching R7RS conventions).

## No Runtime Closures Implications

The restriction against runtime closures shapes how Pre-Scheme programs are structured:

**Compile-time vs runtime:** Code at the top-level is evaluated at compile time and has full closure support. Only runtime code is restricted. This means you can build complex higher-order structures during compilation, but they become static in the generated C.

**Workaround patterns:**
- Pass captured values as explicit parameters instead of closing over them
- Use records to bundle data with behavior (similar to C function pointers + context structs)
- Perform computation at compile time when possible, pushing work out of runtime
- Restructure algorithms to avoid needing long-lived closures

**Design philosophy:** This restriction enforces a clear boundary between compile-time and runtime, similar to how C separates build-time configuration from execution. It prevents subtle memory management issues that arise from heap-allocated closures without garbage collection.
