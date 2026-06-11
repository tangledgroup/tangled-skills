# Core Expressions

## Contents
- Creating Symbols
- Expression Trees and Structure
- Substitution
- Evaluation and Numeric Computation
- Preventing Evaluation
- Key Gotchas

## Creating Symbols

Symbols are the atomic variables in SymPy. They must be explicitly declared — they are not auto-created like in standalone CAS.

```python
from sympy import symbols, Symbol

# Single symbol
x = symbols('x')

# Multiple symbols at once
x, y, z = symbols('x y z')

# With assumptions
x = symbols('x', positive=True)
n = symbols('n', integer=True)
t = symbols('t', real=True)
```

Use `Symbol` for a single symbol, `symbols` (plural) to create multiple from a space-separated string. The name of the Symbol and the Python variable it is assigned to are independent — conventionally they match.

### Common Assumptions

| Assumption | Effect |
|------------|--------|
| `positive=True` | Symbol is strictly positive real |
| `real=True` | Symbol is a real number |
| `integer=True` | Symbol is an integer |
| `nonnegative=True` | Symbol is >= 0 |
| `commutative=False` | Symbol does not commute in multiplication (default: True) |

Assumptions enable simplifications that are only valid under those conditions. Without assumptions, symbols are complex by default, and SymPy will not apply simplifications that fail for some complex values.

## Expression Trees and Structure

Every SymPy expression is a tree. The internal representation may differ from the printed form. Inspect with `srepr()`:

```python
from sympy import srepr, symbols
x, y = symbols('x y')
expr = x**2 + x*y
srepr(expr)
# "Add(Pow(Symbol('x'), Integer(2)), Mul(Symbol('x'), Symbol('y')))"
```

### Key Invariant

Every expression satisfies one of:
- `expr == expr.func(*expr.args)` — reconstructible from head and arguments
- `expr.args == ()` — leaf node (Symbol, Integer, etc.)

### Common Node Types

| Class | Meaning | Example |
|-------|---------|---------|
| `Add` | Addition | `x + y` |
| `Mul` | Multiplication | `x * y` |
| `Pow` | Power/exponentiation | `x**2`, `1/y` (stored as `y**(-1)`) |
| `Symbol` | Variable | `x` |
| `Integer` | Exact integer | `Integer(2)` |
| `Rational` | Exact rational | `Rational(1, 2)` |

There is no `Sub` or `Div` class. Subtraction is `Add(x, Mul(-1, y))`. Division is `Pow(y, -1)`.

### Walking Expression Trees

```python
from sympy import preorder_traversal

for arg in preorder_traversal(expr):
    print(arg)
# x*y + x**2
# x**2
# x
# 2
# x*y
# x
# y
```

Use `expr.func` for the node type and `expr.args` for child nodes.

## Substitution

The `.subs()` method replaces parts of an expression. It returns a new expression (immutability).

```python
from sympy import symbols, cos
x, y = symbols('x y')
expr = cos(x) + 1

# Single substitution
expr.subs(x, 0)        # 2
expr.subs(x, y)        # cos(y) + 1

# Multiple substitutions (pass list of tuples to avoid sequential application)
expr2 = x**3 + 4*x*y - z
expr2.subs([(x, 2), (y, 4), (z, 0)])  # 40
```

Pass a list of `(old, new)` pairs for simultaneous substitution. Passing them one at a time applies sequentially, which can produce different results.

## Evaluation and Numeric Computation

### `.evalf()` — Arbitrary Precision Numeric Evaluation

```python
from sympy import sqrt, pi, cos, symbols
x = symbols('x')

sqrt(8).evalf()                    # 2.82842712474619
pi.evalf(100)                      # 100 digits of pi
cos(2*x).evalf(subs={x: 2.4})     # 0.0874989834394464 (numerically stable)
```

Use `chop=True` to remove negligible roundoff errors:

```python
(cos(1)**2 + sin(1)**2 - 1).evalf(chop=True)  # 0
```

### `lambdify()` — Convert to Fast Numeric Function

For evaluating at many points, convert SymPy expressions to NumPy-compatible functions:

```python
from sympy import lambdify, sin, symbols
import numpy as np

x = symbols('x')
f = lambdify(x, sin(x), 'numpy')
a = np.arange(10)
f(a)  # fast vectorized evaluation
```

Use `'math'` for standard library math, or pass a custom dictionary of function mappings.

### `sympify()` — Convert Strings to Expressions

```python
from sympy import sympify
expr = sympify("x**2 + 3*x - 1/2")
expr.subs(x, 2)  # 19/2
```

**Warning**: `sympify` uses `eval`. Do not use on unsanitized input.

## Preventing Evaluation

SymPy evaluates expressions automatically. Use these techniques to prevent evaluation:

```python
from sympy import Add, sympify, UnevaluatedExpr, symbols
x, y = symbols('x y')

# Method 1: evaluate=False flag
Add(x, x, evaluate=False)           # x + x (not 2*x)
sympify("x + x", evaluate=False)    # x + x

# Method 2: UnevaluatedExpr wrapper
x + UnevaluatedExpr(x)              # x + x (second x is protected)
UnevaluatedExpr(5/7) * UnevaluatedExpr(3/4)  # (5/7)*(3/4)

# Release with .doit()
expr.doit()
```

`evaluate=False` prevents initial evaluation but the expression can still simplify when combined with others. `UnevaluatedExpr` provides stronger protection.

## Key Gotchas

1. **`==` is structural equality, not symbolic equality**. Use `simplify(a - b) == 0` to test if two expressions are mathematically equal, or use `a.equals(b)` for numerical testing at random points.

2. **Python `/` produces floats**. `1/2` is `0.5`, not a rational. Use `Rational(1, 2)` or `S(1)/2` for exact rationals in symbolic expressions: `x + Rational(1, 2)`.

3. **`^` is XOR, not exponentiation**. Use `**` for powers.

4. **Reassigning a Python variable does not affect existing expressions**. If `expr = x + 1` and then `x = 2`, `expr` remains `x + 1`. Use `.subs(x, 2)` to substitute values.

5. **SymPy objects are immutable** (except `Matrix`). All operations return new objects.

6. **Order of terms in Add/Mul is canonical, not input order**. `1 + x` prints as `x + 1`. This is consistent but independent of how you typed it.
