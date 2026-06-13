# Visitors API

## Contents
- Visitor Pattern Overview
- Base Visitor Classes
- Substitution Visitors
- Beta Normalization
- Term Traversal
- Errors

## Visitor Pattern Overview

The library uses the Visitor pattern for all term transformations. Every `Term` has an `accept(visitor)` method that dispatches to the visitor's corresponding `visit_*` method. This enables uniform traversal and transformation without modifying the term classes.

```python
from lambda_calculus.visitors import Visitor

class MyVisitor(Visitor[MyResult, str]):
    def visit_variable(self, variable): ...
    def visit_abstraction(self, abstraction): ...
    def visit_application(self, application): ...
```

The visitor is responsible for visiting child terms — the base `Visitor` does not automatically descend.

## Base Visitor Classes

### Visitor (ABC)

Abstract base with three abstract methods: `visit_variable`, `visit_abstraction`, `visit_application`. Child terms are **not** automatically visited — implement descent explicitly.

```python
visitor.visit(term)  # convenience: calls term.accept(visitor)
```

### BottomUpVisitor

Visits child terms first, then calls `ascend_*` to process the parent. Child traversal is automatic:

```python
from lambda_calculus.visitors import BottomUpVisitor

class MyBottomUp(BottomUpVisitor[int, str]):
    def visit_variable(self, variable):
        return 1

    def ascend_abstraction(self, abstraction, body_count):
        return 1 + body_count

    def ascend_application(self, application, abs_count, arg_count):
        return abs_count + arg_count
```

### DeferrableVisitor

Enables top-down lazy traversal. Instead of `visit_*`, implement `defer_*` methods that return the constructed term plus optional visitor instances for visiting children:

```python
def defer_abstraction(self, abstraction):
    new_body_visitor = ...  # or None to skip body
    return (new_abstraction, new_body_visitor)

def defer_application(self, application):
    abs_visitor = ...  # or None
    arg_visitor = ...  # or None
    return (new_application, abs_visitor, arg_visitor)
```

## Substitution Visitors

Substitution replaces free occurrences of a variable with another term. The library provides three strategies:

### CheckedSubstitution (default)

Checks that no free variable in the replacement value would become bound. Raises `CollisionError` on capture:

```python
from lambda_calculus.visitors.substitution.checked import CheckedSubstitution

sub = CheckedSubstitution.from_substitution("x", replacement)
result = term.accept(sub)
```

This is used by `Term.substitute()` automatically. Track binding context manually with `bind_variable(name)` / `unbind_variable(name)` when needed.

### RenamingSubstitution

Automatically performs alpha conversion to avoid collisions. When a bound variable would capture a free variable from the replacement, it renames the bound variable:

```python
from lambda_calculus.visitors.substitution.renaming import RenamingSubstitution

sub = RenamingSubstitution.from_substitution("x", replacement)
result = term.accept(sub)

# Trace alpha conversions as they happen
for intermediate in sub.trace().visit(term):
    print(intermediate)
```

### UnsafeSubstitution

No collision checking. Fastest but can produce incorrect results if free variables are captured:

```python
from lambda_calculus.visitors.substitution.unsafe import UnsafeSubstitution

sub = UnsafeSubstitution.from_substitution("x", replacement)
result = term.accept(sub)
```

Use only when you have verified that no capture is possible.

## Beta Normalization

`BetaNormalisingVisitor` reduces a term to its beta-normal form, yielding each intermediate step:

```python
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor, Conversion

visitor = BetaNormalisingVisitor()
for conversion, term in visitor.visit(some_term):
    print(f"{conversion}: {term}")
    # conversion is Conversion.BETA or Conversion.ALPHA
```

- `Conversion.BETA` — a beta reduction was performed
- `Conversion.ALPHA` — an alpha conversion was performed to avoid variable capture

If the term is already in normal form, no steps are yielded. Terms without a normal form (e.g., OMEGA) cause infinite recursion.

### Direct Normalization

Skip intermediate steps and compute the result directly:

```python
normal_form = visitor.skip_intermediate(some_term)
```

## Term Traversal

`DepthFirstVisitor` yields all subterms in depth-first order:

```python
from lambda_calculus.visitors.walking import DepthFirstVisitor

for subterm in DepthFirstVisitor().visit(term):
    print(subterm)
```

This is used by `Term.__iter__()` internally, so `for subterm in term:` is equivalent.

## Errors

### CollisionError

Raised when a variable name conflicts with an existing free variable. Inherits from `ValueError` and is generic over the variable type `V`.

```python
from lambda_calculus.errors import CollisionError

try:
    abs.alpha_conversion("x")  # "x" is already free in body
except CollisionError as e:
    print(e.message)           # descriptive message
    print(e.collisions)        # collection of conflicting variables
```

Occurs in:
- `Abstraction.alpha_conversion()` — new name is a free variable in body
- `CheckedSubstitution` — substitution would bind free variables
- `Variable.with_valid_name()` — uses `ValueError` directly, not CollisionError
