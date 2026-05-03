# Classes & Modules

## Contents
- Class definitions
- Import syntax
- Require for macros
- One-shot imports
- Packaging Hy libraries

## Class Definitions

**`defclass`**: Create new classes. Returns `None`.

```hy
(defclass MyClass [SuperClass1 SuperClass2]
  "docstring"
  (setv class_attr 42)
  (defn method1 [self arg1] ...)
  (defn method2 [self arg1 arg2] ...))
```

Optional modifiers before name (same order as `defn`): `[decorators]`, `:tp [type-params]`.

Access attributes with dotted identifiers or the dot macro:

```hy
(setv obj (MyClass))
(print obj.attr)          ; simple variable only
(print (. obj attr))      ; arbitrary form
(print (.obj method arg)) ; method call
(print (obj.method arg))  ; alternative
```

Dotted syntax `obj.attr` and `obj.method` only works when `obj` is a simple variable name. For arbitrary forms, use `(. FORM attr)` or `(.method FORM)`.

**The dot macro**: Chain attribute access, method calls, and subscripts:

```hy
(. a (b 1 2) c [d] [(e 3 4)])
; → a.b(1, 2).c[d][e(3, 4)]
```

Parenthesized args = method call. Bracketed args = subscript.

## Import Syntax

**`import`**: Compiles to Python `import`. Returns `None`. Multiple forms in one call:

```hy
(import sys os.path)                                    ; import modules
(import os.path [exists isdir :as is-dir isfile])       ; from X import Y, Z as W
(import sys :as systest)                                ; import X as Y
(import sys *)                                          ; from X import *
```

**`__all__`**: Controls `import module *`. Use `(export :objects [my-fun MyClass])` to set it conveniently — names are auto-mangled.

## Require for Macros

**`require`**: Like `import` but brings macros into scope at compile-time. Same syntax variants as `import`:

```hy
(require mymodule)             ; all macros
(require mymodule [foo])       ; specific macro
(require mymodule *)           ; exported macros
(require mymodule :as M)       ; aliased
(require mymodule [foo :as bar]) ; renamed
```

Reader macros use `:readers`:

```hy
(require mymodule :readers [spiff])
(require mymodule :readers *)    ; all exported reader macros
```

Note: `(require mymodule :readers [spiff])` does NOT imply `(require mymodule)` — regular macros aren't brought in. List both if needed.

**`_hy_export_macros`**: Controls `require module *`. Set via `(export :macros [my-macro])`. Default: all macros except those whose mangled names start with `_`.

## One-Shot Imports

**`hy.I`**: One-shot import without polluting namespace:

```hy
(print (hy.I.math.sqrt 2))     ; → (import math) (math.sqrt 2)
(print (hy.I.os/path.basename "/a/b"))  ; dots in module name use /
(hy.I "module-name")           ; runtime module name
```

**`hy.R`**: One-shot require and call a macro:

```hy
(hy.R.foo.bar 1)               ; → (require foo) (foo.bar 1)
```

Useful in macro expansions to avoid bringing modules into scope. Dots in module name replaced with `/`.

## Packaging Hy Libraries

Standard Python packaging infrastructure applies. Key differences:

**`__init__.py`** (not `.hy`): Must begin with `import hy` to set up import hooks:

```python
# __init__.py
import hy
from my_module.hy_init import *
hy.eval(hy.read('(require my-module.hy-init :macros * :readers *)'))
```

**PyPI classifier**: Use `Programming Language :: Hy` for libraries providing Hy-specific features (macros, etc.), not for packages just written in Hy.

**Compile at install-time**: See Hy's own `setup.py` for pre-compiling `.hy` to bytecode during installation (useful for read-only install directories).

**Setup file**: Write `setup.py`/`pyproject.toml` in Python (not Hy), since you declare dependence on Hy there.
