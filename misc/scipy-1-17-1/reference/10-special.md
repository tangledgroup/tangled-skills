# Special Functions (scipy.special)

## Overview

`scipy.special` provides numerous special functions of mathematical physics. Most accept array arguments with NumPy broadcasting rules, and many accept complex numbers.

```python
from scipy import special
import numpy as np
```

## Bessel Functions

Solutions to Bessel's differential equation:

```python
# Bessel function of first kind, real order
y = special.jv(nu, x)

# Modified Bessel function
y = special.iv(nu, x)

# Spherical Bessel functions
y = special.spherical_jn(n, x)

# Zeros of Bessel function
zeros = special.jn_zeros(n, m)  # first m zeros of J_n
```

## Gamma and Related Functions

```python
# Gamma function
y = special.gamma(x)

# Log gamma (more numerically stable)
y = special.gammaln(x)

# Beta function
y = special.beta(a, b)

# Incomplete beta function
y = special.betainc(a, b, x)
```

In 1.17, `betainc`, `betaincc`, `betaincinv`, and `betainccinv` improved for extreme parameter ranges.

## Elliptic Functions

```python
# Complete elliptic integral of first kind
K = special.ellipk(m)

# Complete elliptic integral of second kind
E = special.ellipe(m)

# Incomplete elliptic integrals
F = special.ellipkinc(phi, m)
```

## Error Functions and Fresnel Integrals

```python
# Error function
erf_x = special.erf(x)
erfc_x = special.erfc(x)  # complementary

# Fresnel integrals
S, C = special.fresnel(x)
```

## Combinatorial Functions

```python
# Binomial coefficient
y = special.comb(n, k, exact=True)

# Factorial
y = special.factorial(n)

# Multinomial
y = special.multinomial([n1, n2, n3])
```

## Hypergeometric Functions

```python
# Gaussian hypergeometric function
y = special.hyp2f1(a, b, c, z)

# Confluent hypergeometric functions
y = special.hyp1f1(a, b, z)
y = special.hyperu(a, b, z)
```

## Airy Functions

```python
# Airy function and derivative
Ai, Aip, Bi, Bip = special.airy(x)
```

## Statistical Functions (Low-Level)

These are lower-level functions used by `scipy.stats`:

```python
# Noncentral chi-squared distribution
y = special.chndtr(df, nc, x)

# Student's t distribution
y = special.stdtr(df, delta, x)
```

In 1.17, many statistical functions improved: `btdtria`, `chdtriv`, `chndtr`, `fdtr`, `fdtrc`, `fdtri`, `gdtria`, `pdtrik`, `stdtr`.

## Cython Bindings

For performance-critical code, use Cython bindings for typed scalar versions:

```cython
from scipy.special.cython_special cimport jv
def bessel_example(double x):
    return jv(0, x)
```

## Function Discovery

List available functions:

```python
help(special)
# or
special.__all__
```
