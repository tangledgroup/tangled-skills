# Printing and Output

## Contents
- Pretty Printing Setup
- String Printers
- LaTeX Output
- Code Generation
- Other Output Formats

## Pretty Printing Setup

### `init_printing()` — Auto-Detect Best Printer

```python
from sympy import init_printing
init_printing()  # auto-selects best available printer
```

Behavior depends on environment:
- **IPython QtConsole**: LaTeX rendering if LaTeX installed, otherwise Matplotlib, otherwise Unicode
- **Jupyter Notebook**: MathJax LaTeX rendering
- **Python console with Unicode**: Unicode pretty printer
- **ASCII-only terminal**: ASCII pretty printer

Options:
```python
init_printing(use_unicode=False)   # force ASCII
init_printing(use_latex=False)     # disable LaTeX
```

### `init_session()` — Full Interactive Setup

Imports all SymPy functions, creates common symbols (`x, y, z, t`, `k, m, n`), sets up printing:

```python
from sympy import init_session
init_session()
```

## String Printers

### `str()` / `print()` — Readable Python Syntax

Output is valid Python syntax that can be copy-pasted:

```python
from sympy import Integral, sqrt, symbols
x = symbols('x')
print(Integral(sqrt(1/x), x))
# Integral(sqrt(1/x), x)
```

### `srepr()` — Internal Representation

Shows exact internal structure (useful for debugging):

```python
from sympy import srepr
srepr(Integral(sqrt(1/x), x))
# "Integral(Pow(Pow(Symbol('x'), Integer(-1)), Rational(1, 2)), Tuple(Symbol('x')))"
```

### `pprint()` / `pretty()` — ASCII or Unicode Pretty Print

```python
from sympy import pprint, pretty

# Prints to screen (auto-detects Unicode support)
pprint(Integral(sqrt(1/x), x))

# Returns string
print(pretty(Integral(sqrt(1/x), x), use_unicode=False))
# ASCII art integral
print(pretty(Integral(sqrt(1/x), x), use_unicode=True))
# Unicode art integral
```

## LaTeX Output

```python
from sympy import latex, Integral, cos, symbols
x = symbols('x')
print(latex(Integral(cos(x)**2, (x, 0, pi))))
# \int\limits_{0}^{\pi} \cos^{2}{\left(x \right)}\, dx
```

The `latex()` function supports many formatting options. See its documentation for details on equation numbering, symbol mapping, and output style.

## Code Generation

SymPy can generate code in multiple languages from symbolic expressions:

```python
from sympy import ccode, fcode, python, jscode, sin, symbols
x = symbols('x')
expr = sin(x) * x**2

ccode(expr)      # "sin(x)*x*x"
fcode(expr)      # "sin(x)*x**2"
python(expr)     # "sin(x)*x**2"
jscode(expr)     # "Math.sin(x)*x*x"
```

These printers convert SymPy function names to the target language's equivalents. Use `lambdify()` for numeric evaluation rather than code generation when performance matters.

## Other Output Formats

### MathML

```python
from sympy.printing.mathml import print_mathml, mathml
print_mathml(Integral(sqrt(1/x), x))  # prints to stdout
mathml(Integral(sqrt(1/x), x))        # returns string
```

### Dot (Graphviz)

Print expression tree as a Graphviz dot diagram:

```python
from sympy.printing.dot import dotprint
print(dotprint(x + 2))
# digraph{ ... } — render with Graphviz
```
