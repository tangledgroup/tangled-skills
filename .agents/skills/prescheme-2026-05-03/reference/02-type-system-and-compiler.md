# Type System and Compiler

## Contents
- Hindley/Milner Type Reconstruction
- Parametric Polymorphism
- CPS Intermediate Representation
- Transformational Compilation Pipeline
- Efficient Tail Recursion Implementation

## Hindley/Milner Type Reconstruction

Pre-Scheme uses a modified Hindley/Milner algorithm to reconstruct types from usage patterns. The compiler infers types without manual annotations, then uses those types to choose specific machine representations for every variable.

**Inference process:** The compiler traverses the program, generating type constraints from each expression (e.g., `+` requires both arguments to be numeric). These constraints are solved via unification to produce a principal type for each binding.

**Modified HM for Scheme:** Standard HM handles algebraic data types and pattern matching natively. Pre-Scheme adapts it for Scheme's dynamic-style syntax where types aren't declared — the compiler must infer from usage alone. The modification models Scheme's dynamic typing as accurately as possible while still producing static machine code.

**Machine representation selection:** Once types are inferred, the compiler selects the optimal C type for each variable: `long` for fixnums, `double` for flonums, `char*` for strings, or a struct pointer for records. This eliminates the need for tagged unions or runtime type checks.

## Parametric Polymorphism

Pre-Scheme supports parametric polymorphism — procedures that work uniformly across multiple types. When a polymorphic procedure is used at multiple call sites with different types, the compiler generates specialized copies (monomorphization).

**Polymorphic primitives:** Some primitive operations like `deallocate` are inherently polymorphic — they work on any heap-allocated type. The compiler handles these by generating type-specific code paths during monomorphization.

**Type copying:** When a polymorphic procedure is called with different argument types, the compiler produces separate C functions for each instantiation. This preserves performance without runtime dispatch overhead.

## CPS Intermediate Representation

The Pre-Scheme compiler uses Continuation-Passing Style (CPS) as its sole internal representation. All program transformations operate on the same CPS-based lambda calculus IR.

**CPS transformation:** The first compilation pass converts direct-style Scheme code into CPS, where every function takes an extra continuation argument representing "what to do next." This makes control flow explicit and uniform.

**Single IR advantage:** Having one IR for all optimization passes means:
- Each transformation is simpler (operates on a uniform representation)
- Correctness is easier to prove (transformations are composable)
- New optimizations can be added without designing new data structures

This approach follows Richard Kelsey's dissertation "Compilation By Program Transformation" (1989), which describes compilation as a sequence of transformations on a lambda-calculus-based IR.

## Transformational Compilation Pipeline

Compilation proceeds through a series of correctness-preserving transformations on the CPS IR:

1. **Source parsing:** Scheme S-expressions → abstract syntax tree
2. **Macro expansion:** Hygienic macro system expands all macros
3. **CPS conversion:** Direct-style code → continuation-passing style
4. **Type inference:** Hindley/Milner reconstruction assigns types to all bindings
5. **Optimization passes:** Multiple transformations on the CPS IR:
   - Eta-reduction: eliminate unnecessary continuations
   - Inlining: substitute small procedures at call sites
   - Specialization: generate type-specific copies of polymorphic code
   - Common-subexpression elimination: share repeated computations
   - Dead-code elimination: remove unreachable branches
6. **Code generation:** CPS IR → C source code

Each transformation preserves program semantics while improving performance or reducing code size. The pipeline is designed so that later passes can exploit opportunities created by earlier ones.

## Efficient Tail Recursion Implementation

Local tail-recursive procedures are guaranteed to run in constant space. The compiler recognizes tail-recursive `let` and `letrec` patterns and converts them to C loops or trampolines.

**How it works:** When the compiler detects that a recursive call is in tail position within a `let`/`letrec` binding, it transforms the recursion into an iterative loop in the generated C code. The continuation structure in CPS makes this detection straightforward — a tail-recursive call simply reuses the current continuation.

**Limitation:** Only local recursion is optimized. Cross-module tail calls and mutually recursive tail calls across separate compilation units are not guaranteed constant space, unlike Scheme's universal tail-call elimination.
