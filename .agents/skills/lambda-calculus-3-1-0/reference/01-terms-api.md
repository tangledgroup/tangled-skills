# Terms API

## Contents
- Term Base Class
- Variable
- Abstraction
- Application

## Term Base Class

`lambda_calculus.terms.Term[V]` is the abstract base class for all lambda terms. It is generic over `V`, the type of variable names (typically `str`).

### Common Methods

```python
term.free_variables()       # Set[V] — variables not bound by any abstraction
term.bound_variables()      # Set[V] — variables bound by abstractions
term.is_beta_normal_form()  # bool — True if no beta reductions possible
term.is_combinator()        # bool — True if no free variables
term.accept(visitor)        # T — dispatch to visitor's corresponding method
```

### Convenience Methods

```python
# Bind variables (creates nested Abstraction)
Variable("y").abstract("x")           # λx.y
Variable("z").abstract("x", "y")      # λx.λy.z

# Apply to arguments (creates left-associated Application)
func.apply_to(arg1)                   # (func arg1)
func.apply_to(arg1, arg2, arg3)       # ((func arg1) arg2) arg3)

# Safe substitution with collision checking
term.substitute("x", replacement)     # raises CollisionError on capture
```

### Iteration

Terms implement `__iter__`, yielding all subterms depth-first:

```python
for subterm in term:
    print(subterm)
```

This uses `DepthFirstVisitor` internally.

### String Representation

Each term's `__str__` produces parenthesized notation:
- `Variable("x")` → `"x"`
- `Abstraction("x", body)` → `"(λx.{body})"`
- `Application(f, a)` → `"{f} {a}"`

## Variable

```python
from lambda_calculus import Variable

v = Variable("x")
```

### Constructor Validation

`Variable.with_valid_name(name)` checks that the string representation is non-empty and contains no characters from `().λ` or whitespace. Use this when constructing variables from user input.

### Properties

- `free_variables()` always returns `{self.name}`
- `bound_variables()` always returns empty set
- `is_beta_normal_form()` always returns `True`

## Abstraction

```python
from lambda_calculus import Abstraction, Variable

# Single binding
abs = Abstraction("x", Variable("x"))  # (λx.x)

# Multiple bindings (curried, from first to last)
abs = Abstraction.curried(("x", "y"), Variable("x"))  # (λx.(λy.x))
```

### Alpha Conversion

Rename the bound variable. Raises `CollisionError` if the new name is a free variable in the body:

```python
new_abs = abs.alpha_conversion("z")  # (λz.z)
```

If the new name equals the current bound variable, returns self unchanged.

### Eta Reduction

Remove a useless abstraction where `λx.M x` reduces to `M` (when `x` is not free in `M`):

```python
# λx.(f x) → f  (if x not free in f)
reduced = abs.eta_reduction()
```

Raises `ValueError` if the abstraction does not match the eta pattern.

### Replace

Create a copy with replaced attributes:

```python
new_abs = abs.replace(bound="z")
new_abs = abs.replace(body=new_body)
```

## Application

```python
from lambda_calculus import Application, Abstraction, Variable

app = Application(func, arg)  # (func arg)

# Multiple arguments (left-associated)
app = Application.with_arguments(func, (arg1, arg2, arg3))
# Equivalent to: ((func arg1) arg2) arg3)
```

### Beta Reduction

Perform a single beta reduction on the top-level application:

```python
redex = Application(Variable("x").abstract("x"), Variable("a"))
reduced = redex.beta_reduction()  # Variable("a")
```

Raises `ValueError` if the abstraction side is not an `Abstraction` (checked via `is_redex()`).

### Replace

Create a copy with replaced attributes:

```python
new_app = app.replace(abstraction=new_func)
new_app = app.replace(argument=new_arg)
```
