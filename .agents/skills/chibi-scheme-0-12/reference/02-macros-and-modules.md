# Macros And Modules

## Contents
- Hygienic Macro System
- Syntactic Closures
- Low-Level Macro Transformers
- Module Hierarchy
- Import/Export System
- Include Forms
- Cond-Expand And Features
- The Auto Module

## Hygienic Macro System

Chibi provides full hygienic macros. Variable capture is prevented at the identifier level — not just by renaming, but by carrying syntactic context through the expansion process.

**Key procedures:**

- `identifier?` — test if a value is a hygienic identifier (not just a symbol)
- `identifier->symbol` — extract the underlying symbol
- `identifier=?` — compare identifiers respecting hygiene (same name AND same binding context)
- `make-syntactic-closure` — create an identifier in a different lexical context
- `strip-syntactic-closures` — remove syntactic closure wrappers, yielding bare symbols

Hygiene means that `(identifier=? 'x 'x)` can return `#f` if the two `x` identifiers come from different macro contexts. This is correct behavior — it prevents accidental variable capture.

## Syntactic Closures

Syntactic closures are the internal representation of hygienic identifiers. They wrap a symbol with lexical context information (a "stamp" identifying where the identifier was created). During macro expansion, the system uses this context to determine whether two identifiers refer to the same binding.

The syntactic-closure interface is the low-level API for building macros that need fine-grained control over hygiene. Most Scheme code uses `syntax-rules` instead.

## Low-Level Macro Transformers

Beyond `syntax-rules`, Chibi provides three low-level macro transformer types:

- **`sc-macro-transformer`** — full syntactic-closure access; the transformer receives and returns syntactic closures, enabling precise hygiene control
- **`rsc-macro-transformer`** — restricted syntactic-closure access; like `sc-macro-transformer` but with limited introspection (cannot create arbitrary identifiers)
- **`er-macro-transformer`** — "er" (environment-restricted) transformer; receives plain symbols, not syntactic closures. Easier to write but no hygiene guarantees — the programmer must avoid capture manually

Choose `syntax-rules` for most macros. Use `sc-macro-transformer` when you need to manipulate identifiers programmatically (e.g., generating unique names). Use `er-macro-transformer` only when performance matters and you can guarantee safety yourself.

## Module Hierarchy

Chibi implements R7RS `define-library` but with a **Scheme48-style layered language** model rather than flat modules. Each module can extend a parent language, inheriting its bindings and adding new ones.

```scheme
(define-library (my-module)
  (import (scheme base))
  (export my-function)
  (begin
    (define (my-function x)
      (+ x 1))))
```

Module names are hierarchical lists: `(foo bar baz)` maps to file `foo/bar/baz.sld`. The search path includes installed directories, `.`, and `./lib` by default. Add directories with `-I`/`-A` command-line flags or `add-module-directory` at runtime.

Within a module definition, `include` loads files relative to the `.sld` file location.

## Import/Export System

**Export list:** `(export <id> ...)` declares which identifiers are visible outside the module.

**Import specifications** support composition:

- `(only <spec> <id> ...)` — import only listed bindings
- `(except <spec> <id> ...)` — import all except listed
- `(rename <spec> (<from> <to>) ...)` — rename during import
- `(prefix <spec> <prefix-id>)` — prefix all imported names
- `(drop-prefix <spec> <prefix-id>)` — non-R7RS, strip a prefix

These are composable: `(only (prefix (scheme base) s:) s:+ s:-)` imports `+` and `-` as `s:+` and `s:-`.

## Include Forms

- **`include`** — load a Scheme file at the module level (like paste-in)
- **`include-ci`** — same with case-folding enabled
- **`include-shared`** — dynamically load a compiled shared library (no suffix in the name; `.so`/`.dylib` added portably). The library must export `sexp_init_library`

## Cond-Expand And Features

`cond-expand` checks feature symbols at compile time:

```scheme
(cond-expand
  (chibi-scheme (display "Running on Chibi"))
  (else (display "Unknown implementation")))
```

Chibi maintains a feature list including the implementation name, version, architecture, OS, and compiled-in capabilities (`bignums`, `flonums`, `ratios`, `complex`, `unicode`, `green-threads`). Features can be checked from C via preprocessor defines in `features.h`.

## The Auto Module

Chibi provides a special `(auto)` module that exports any identifier requested via `only`:

```scheme
(import (only (auto) else))
```

This solves the R7RS macro conflict problem where two macros from different modules both need the same auxiliary keyword (like `else` in `cond`). Each module gets its own fresh binding without needing to know about each other. Non-portable — Chibi-specific extension.
