# scipy.special - Special Mathematical Functions

The `scipy.special` module provides a comprehensive collection of special mathematical functions commonly used in scientific computing, including Bessel functions, gamma functions, error functions, elliptic integrals, and more.

## Gamma and Beta Functions

### Gamma Function

```python
from scipy import special
import numpy as np

# Gamma function: Γ(n) = (n-1)! for integers
gamma_val = special.gamma(5)  # = 4! = 24

# Log gamma (more numerically stable)
log_gamma = special.gammaln(100)  # ln(Γ(100))

# Beta function: B(x, y) = Γ(x)Γ(y)/Γ(x+y)
beta_val = special.beta(2, 3)

# Log beta
log_beta = special.betaln(2, 3)

# Incomplete gamma functions
gammainc_val = special.gammainc(a, x)  # Regularized incomplete gamma
gammainc_inv = special.gammaincinv(a, p)  # Inverse
```

### Factorial and Combinatorial Functions

```python
from scipy import special

# Factorial
fact_10 = special.factorial(10)

# Log factorial (for large numbers)
log_fact_100 = special.gammaln(101)  # ln(100!)

# Binomial coefficient: C(n, k)
binom = special.comb(10, 3)  # = 120

# Multinomial coefficient
multinom = special.multinomial([2, 3, 5])

# Permutations and combinations with replacement
perm = special.perm(10, 3)  # P(10, 3)
comb_rep = special.comb(10, 3, repetition=True)
```

## Bessel Functions

### Ordinary Bessel Functions

```python
from scipy import special
import numpy as np

x = np.array([0.5, 1.0, 2.0, 5.0])

# Bessel function of the first kind: J_n(x)
j0 = special.j0(x)      # Order 0
j1 = special.j1(x)      # Order 1
jn = special.jn(2, x)   # Order n (integer)
jv = special.jv(2.5, x) # Order ν (non-integer)

# Bessel function of the second kind: Y_n(x) (Weber/Neumann)
y0 = special.y0(x)
y1 = special.y1(x)
yn = special.yn(2, x)
yv = special.yv(2.5, x)

# Hankel functions: H_n^(1)(x) and H_n^(2)(x)
h1 = special.h1(0, x)   # First kind
h2 = special.h2(0, x)   # Second kind
```

### Modified Bessel Functions

```python
from scipy import special
import numpy as np

x = np.array([0.5, 1.0, 2.0, 5.0])

# Modified Bessel function of the first kind: I_ν(x)
i0 = special.i0(x)      # Order 0
i1 = special.i1(x)      # Order 1
iv = special.iv(2.5, x) # Order ν

# Modified Bessel function of the second kind: K_ν(x)
k0 = special.k0(x)
k1 = special.k1(x)
kv = special.kv(2.5, x)

# Scaled versions (for large x to avoid overflow)
iv_scaled = special.iv(2, x, scal=True)  # e^(-x) * I_ν(x)
kv_scaled = special.kv(2, x, scal=True)  # e^(x) * K_ν(x)
```

### Spherical Bessel Functions

```python
from scipy import special
import numpy as np

x = np.array([0.5, 1.0, 2.0, 5.0])

# Spherical Bessel function: j_n(x)
spherical_j = special.spherical_jn(n=2, x=x)

# Spherical Neumann function: y_n(x)
spherical_y = special.spherical_yn(n=2, x=x)

# Modified spherical Bessel functions
spherical_i = special.spherical_in(n=2, x=x)  # i_n(x)
spherical_k = special.spherical_kn(n=2, x=x)  # k_n(x)
```

### Bessel Function Zeros

```python
from scipy import special

# Zeros of Bessel function J_n
j_zeros = special.jn_zeros(n=2, nt=10)  # First 10 zeros of J_2

# Zeros of derivative of J_n
jprime_zeros = special.jnp_zeros(n=2, nt=10)

# Zeros of Y_n
y_zeros = special.yn_zeros(n=2, nt=10)
```

## Error Functions and Integrals

### Error Function

```python
from scipy import special
import numpy as np

x = np.array([-2, -1, 0, 1, 2])

# Error function: erf(x)
erf_val = special.erf(x)

# Complementary error function: erfc(x) = 1 - erf(x)
erfc_val = special.erfc(x)  # More accurate for large x

# Inverse error function
erfinv_val = special.erfinv(0.5)

# Inverse complementary error function
erfcinv_val = special.erfcinv(0.1)

# Imaginary error function: erfi(x) = -i*erf(ix)
erfi_val = special.erfi(x)
```

### Exponential Integrals

```python
from scipy import special
import numpy as np

x = np.array([0.5, 1.0, 2.0, 5.0])

# Exponential integral: E_1(x)
exp1 = special.exp1(x)

# Generalized exponential integral: E_n(x)
expn = special.expn(n=2, x=x)

# Exponential integral Ei(x)
ei = special.ei(x)

# Sine and cosine integrals
si = special.si(x)      # Sine integral
ci = special.ci(x)      # Cosine integral
```

## Elliptic Integrals

### Complete Elliptic Integrals

```python
from scipy import special
import numpy as np

m = np.array([0.0, 0.25, 0.5, 0.75])  # Parameter m = k²

# Complete elliptic integral of the first kind: K(m)
ellipk = special.ellipk(m)

# Complete elliptic integral of the second kind: E(m)
ellipe = special.ellipe(m)

# Using modulus k instead of parameter m
k = np.sqrt(m)
ellipk_k = special.ellipk(k**2)  # Same result
```

### Incomplete Elliptic Integrals

```python
from scipy import special
import numpy as np

phi = np.radians(45)  # Amplitude in radians
m = 0.5               # Parameter

# Incomplete elliptic integral of the first kind: F(φ|m)
ellipkinc_f = special.ellipkinc(phi, m)

# Incomplete elliptic integral of the second kind: E(φ|m)
ellipe_inc = special.ellipeinc(phi, m)

# Incomplete elliptic integral of the third kind: Π(n; φ|m)
n = 0.3
elliprj_pi = special.elliprc(x=1-m, y=(1-n)*np.cos(phi)**2, z=np.cos(phi)**2)
```

### Carlson Symmetric Forms

```python
from scipy import special
import numpy as np

# Carlson's symmetric form: R_F(x, y, z)
rf = special.elliprf(x=1.0, y=2.0, z=3.0)

# R_J(x, y, z, p)
rj = special.elliprj(x=1.0, y=2.0, z=3.0, p=0.5)

# R_D(x, y, z) = R_J(x, y, z, z)
rd = special.elliprd(x=1.0, y=2.0, z=3.0)

# These are numerically stable alternatives to Legendre forms
```

## Orthogonal Polynomials

### Hermite Polynomials

```python
from scipy import special
import numpy as np

x = np.linspace(-3, 3, 100)

# Hermite polynomial H_n(x) (physicists')
hermite_0 = special.hermitenorm(0, x)  # Probabilist's Hermite
hermite_phys = special.hermval(x, [1])  # Using hermite functions

# Evaluate Hermite polynomial with coefficients
coeffs = [1, 2, 3]  # Represents H_0 + 2*H_1 + 3*H_2
hermite_eval = special.hermval(x, coeffs)
```

### Legendre Polynomials

```python
from scipy import special
import numpy as np

x = np.linspace(-1, 1, 100)

# Legendre polynomial P_n(x)
legendre_0 = special.l_roots(5)[0]  # Roots of P_5

# Evaluate Legendre polynomial
pn = special.lgamma(n + 1)  # Related to Legendre

# Associated Legendre functions
Pnm = special.lpmv(m=1, n=2, x=x[0])  # P_n^m(x)
```

### Chebyshev Polynomials

```python
from scipy import special
import numpy as np

x = np.linspace(-1, 1, 100)

# Chebyshev polynomials of the first kind: T_n(x)
chebyt = special.chebyt(n=5, x=x)

# Chebyshev polynomials of the second kind: U_n(x)
chebyu = special.chebyu(n=5, x=x)

# Chebyshev points (roots of T_n)
n = 10
cheby_points = np.cos(np.pi * (np.arange(1, n+1) - 0.5) / n)
```

### Jacobi Polynomials

```python
from scipy import special
import numpy as np

x = np.linspace(-1, 1, 100)
alpha, beta = 0.5, 0.5  # Parameters

# Jacobi polynomial P_n^(α,β)(x)
jacobi = special.jacobi(n=5, alpha=alpha, beta=beta)
jacobi_eval = jacobi(x)
```

## Statistical Functions

### Logarithmic Derivatives of Gamma Function

```python
from scipy import special
import numpy as np

x = np.array([1.0, 2.5, 5.0, 10.0])

# Digamma function: ψ(x) = d/dx ln(Γ(x))
digamma_val = special.digamma(x)

# Trigamma function: ψ₁(x) = d²/dx² ln(Γ(x))
trigamma_val = special.polygamma(n=1, z=x)

# Polygamma function: ψ^(n)(x)
polygamma_3 = special.polygamma(n=3, z=x)  # Third derivative
```

### Zeta and Related Functions

```python
from scipy import special
import numpy as np

# Riemann zeta function: ζ(s)
zeta_val = special.zeta(s=2)  # = π²/6 ≈ 1.645

# Zeta for multiple values
s_values = np.array([2, 3, 4])
zeta_array = special.zeta(s_values)

# Hurwitz zeta function: ζ(s, q)
hurwitz_zeta = special.zeta(s=2, q=0.5)

# Bernoulli numbers
bernoulli = special.bernoulli(n=10)

# Generalized Riemann zeta (Dirichlet L-series)
```

### Information Theoretic Functions

```python
from scipy import special
import numpy as np

x = np.array([0.1, 0.5, 0.9])

# Entropy-related functions
entropy = -np.sum(x * np.log(x))  # Shannon entropy

# Relative entropy (KL divergence) components
kl_component = x * np.log(x / 0.5)
```

## Hypergeometric Functions

### Gaussian Hypergeometric Function

```python
from scipy import special
import numpy as np

z = np.array([0.1, 0.5, 0.9])

# Hypergeometric function: ₂F₁(a, b; c; z)
hyp2f1 = special.hyp2f1(a=1.0, b=2.0, c=3.0, z=z)

# Confluent hypergeometric function: ₁F₁(a; c; z)
hyp1f1 = special.hyp1f1(a=1.0, c=2.0, z=z)

# Tricomi confluent hypergeometric function: U(a, b, z)
tricomie = special.hyperu(a=1.0, b=2.0, z=z)
```

### Generalized Hypergeometric Functions

```python
from scipy import special
import numpy as np

z = 0.5

# Generalized hypergeometric: pFq(ap; bq; z)
ap = [1.0, 2.0]  # Numerator parameters
bq = [3.0, 4.0]  # Denominator parameters
hyp_general = special.hyp2f2(ap=[1.0, 2.0], bq=[3.0, 4.0], z=z)

# More general: pFq with arbitrary p and q
from scipy.special import hyp2f1, hyp1f1, hyperu
```

## Troubleshooting

### Numerical Overflow

```python
from scipy import special
import numpy as np

# For large arguments, use log versions
x_large = 1000

# Instead of gamma (may overflow)
log_gamma_val = special.gammaln(x_large)
gamma_val = np.exp(log_gamma_val)

# For Bessel functions with large x
x_bessel = 100
i_scaled = special.iv(n=0, x=x_bessel, scal=True)  # Scaled to avoid overflow
```

### Precision Issues

```python
# Use higher precision for critical calculations
import mpmath

mpmath.mp.dps = 50  # Set decimal precision
result_high_prec = mpmath.besselj(0, 100)

# Or use scipy's arbitrary precision where available
```

### Domain Errors

```python
from scipy import special
import numpy as np

# Handle domain errors gracefully
x_invalid = np.array([-1, 0, 1, 2])

try:
    result = special.loggamma(x_invalid)
except ValueError as e:
    print(f"Domain error: {e}")

# Use where to mask invalid inputs
valid_mask = x_invalid > 0
result = np.zeros_like(x_invalid, dtype=float)
result[valid_mask] = special.loggamma(x_invalid[valid_mask])
```

## See Also

- [`scipy.integrate`](references/02-integrate.md) - Integration of special functions
- [`sympy`](https://docs.sympy.org/) - Symbolic computation with special functions
- [NIST Digital Library of Mathematical Functions](https://dlmf.nist.gov/) - Comprehensive reference
