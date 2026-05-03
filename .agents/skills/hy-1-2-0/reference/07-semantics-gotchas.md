# Semantics & Gotchas

## Contents
- Implicit names
- Order of evaluation
- Bytecode regeneration
- Traceback positioning

## Implicit Names

Every Hy module implicitly begins with `(import hy)`. This ensures the compiler can access `hy.models.*` and other internal names needed during compilation.

**Consequences:**
- Don't assign to the name `hy` (even locally) — generated code may reference it expecting the module
- You can use `hy.repr`, `hy.mangle`, etc. without explicit import
- The implicit import is unconditional — Hy can't predict which features your code needs

**Temporary variables**: Hy creates temp variables starting with `_hy_` for internal operations (e.g., storing `with` results). Avoid this prefix in your own variable names. These temps follow normal scoping and aren't explicitly cleaned up, so they may delay `__del__` calls. Check `hy2py` output when in doubt.

**Pure Python subset**: If you restrict yourself to a subset of Hy that doesn't use models or compiler internals, you can translate with `hy2py`, remove the `import hy`, and get working pure Python.

## Order of Evaluation

Hy does **not guarantee** the order in which function arguments are evaluated. The evaluation order of child models within any `hy.models.Sequence` is unspecified.

```hy
; (f (g) (h)) might evaluate (h) before (g)!
; This can happen especially when f is a function but h is a macro
; that produces Python-level statements.
```

**Rule**: If you need specific evaluation order, call the earlier form separately:

```hy
(setv result-g (g))
(f result-g (h))
```

Or use `do` to force sequential evaluation within an expression context.

## Bytecode Regeneration

First execution of a `.hy` file produces bytecode (unless `PYTHONDONTWRITEBYTECODE` is set). Subsequent executions load bytecode if source hasn't changed.

**Critical issue with macros**: If a macro's source changes but the file using it hasn't, the old bytecode retains the old macro expansion:

```bash
$ echo '(defmacro m [] 1)' >a.hy
$ echo '(require a) (print (a.m))' >b.hy
$ hy b.hy     ; → 1
$ echo '(defmacro m [] 2)' >a.hy
$ hy b.hy     ; → 1 (NOT 2! bytecode not regenerated)
```

**Fix**: Delete bytecode files (`git clean -dfx` or manually remove `__pycache__/`) or set `PYTHONDONTWRITEBYTECODE=1` during development.

This also affects `eval-and-compile`, reader macros, and any compile-time code generation.

## Traceback Positioning

Python uses line/column numbers from AST nodes for traceback pointers. Hy sets these appropriately, but there are cases where it can't:

- Code built at runtime from explicit model constructors
- Evaluated code without source position information

In these cases, Hy sets positions to `(1, 1)` as fallback. Tracebacks may point to the beginning of a file even though the relevant code isn't there.

**Debugging tip**: Use `HY_SHOW_INTERNAL_ERRORS=1` to see parts of tracebacks pointing into internal Hy code. Use `hy2py` to inspect the generated Python when behavior is unexpected.
