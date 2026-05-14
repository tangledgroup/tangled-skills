# Matrices

## Contents
- Creating Matrices
- Basic Operations
- Matrix Constructors
- Advanced Methods
- Eigenvalues and Diagonalization
- Zero Testing Issues

## Creating Matrices

Use `Matrix` with a list of row vectors. A flat list creates a column vector.

```python
from sympy import Matrix

# 3x2 matrix
M = Matrix([[1, -1], [3, 4], [0, 2]])

# Column vector
v = Matrix([1, 2, 3])

# Row vector (list of one row)
r = Matrix([[1, 2, 3]])
```

**Important**: `Matrix` is mutable (the only exception to SymPy's immutability). Use `ImmutableMatrix` when you need an immutable version (e.g., as dictionary keys or inside expressions).

## Basic Operations

Standard operators work: `+`, `-`, `*` (matrix multiplication), `**` (power), `**-1` (inverse).

```python
from sympy import Matrix, shape

M = Matrix([[1, 2, 3], [3, 2, 1]])
N = Matrix([0, 1, 1])

M * N               # matrix-vector product
M + M               # element-wise addition
3 * M               # scalar multiplication
M**2                # matrix power
M**-1               # inverse (raises NonInvertibleMatrixError if singular)
M.T                 # transpose
shape(M)            # (2, 3)
```

### Accessing Rows and Columns

```python
M.row(0)            # first row
M.col(-1)           # last column
```

### Deleting and Inserting

```python
# In-place operations (return None)
M.col_del(0)
M.row_del(1)

# Non-in-place (return new Matrix)
M = M.row_insert(1, Matrix([[0, 4]]))
M = M.col_insert(0, Matrix([1, -2]))
```

## Matrix Constructors

```python
from sympy import eye, zeros, ones, diag

eye(3)              # 3x3 identity
zeros(2, 3)         # 2x3 zero matrix
ones(3, 2)          # 3x2 matrix of ones
diag(1, 2, 3)       # diagonal matrix
diag(-1, ones(2, 2), Matrix([5, 7, 5]))  # block diagonal
```

## Advanced Methods

### Determinant

```python
M = Matrix([[1, 0, 1], [2, -1, 3], [4, 3, 2]])
M.det()             # -1
```

### RREF (Reduced Row Echelon Form)

Returns `(rref_matrix, pivot_columns)`:

```python
M = Matrix([[1, 0, 1, 3], [2, 3, 4, 7], [-1, -3, -3, -4]])
M.rref()
# (Matrix([[1,0,1,3],[0,1,2/3,1/3],[0,0,0,0]]), (0, 1))
```

### Nullspace and Columnspace

```python
M = Matrix([[1, 2, 3, 0, 0], [4, 10, 0, 0, 1]])
M.nullspace()       # list of column vectors spanning nullspace

M2 = Matrix([[1, 1, 2], [2, 1, 3], [3, 1, 4]])
M2.columnspace()    # list of column vectors spanning columnspace
```

## Eigenvalues and Diagonalization

### `eigenvals()` — Eigenvalue Multiplicities

Returns `{eigenvalue: algebraic_multiplicity}`:

```python
M = Matrix([[3, -2, 4, -2], [5, 3, -3, -2], [5, -2, 2, -2], [5, -2, -3, 3]])
M.eigenvals()       # {-2: 1, 3: 1, 5: 2}
```

### `eigenvects()` — Eigenvalues with Eigenvectors

Returns list of `(eigenvalue, algebraic_mult, [eigenvectors])`:

```python
M.eigenvects()
# [(-2, 1, [vec1]), (3, 1, [vec2]), (5, 2, [vec3, vec4])]
```

Use `eigenvals()` if you only need eigenvalues — computing eigenvectors is more expensive.

### `diagonalize()` — Full Diagonalization

Returns `(P, D)` where `M = P*D*P⁻¹`:

```python
P, D = M.diagonalize()
P * D * P**-1 == M  # True
```

Matrix is diagonalizable iff algebraic and geometric multiplicities match for all eigenvalues.

### `charpoly()` — Characteristic Polynomial

More efficient than `eigenvals()` when you only need the polynomial:

```python
lamda = symbols('lamda')  # 'lamda' prints as λ (lambda is a Python keyword)
p = M.charpoly(lamda)
from sympy import factor
factor(p.as_expr())       # (λ - 5)² ⋅ (λ - 3) ⋅ (λ + 2)
```

## Zero Testing Issues

Matrix operations can fail or give wrong results due to undecidable zero tests. SymPy's default `_iszero` may return `None` for complex expressions, which is treated as "not zero."

**Symptoms**: `nullspace()` returns empty list when it should not, `rref()` gives unexpected pivots, `inverse()` fails on invertible matrices.

**Fix**: Provide a custom zero-testing function via `iszerofunc`:

```python
# For hyperbolic/exponential expressions
def my_iszero(x):
    return x.rewrite(exp).simplify().is_zero

M.nullspace(iszerofunc=my_iszero)
```

This is a fundamental limitation — the constant problem makes zero testing undecidable in general. All CAS face this issue.
