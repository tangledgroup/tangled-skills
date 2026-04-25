# scipy.interpolate - Interpolation and Smoothing

The `scipy.interpolate` module provides tools for interpolation of 1D and multi-dimensional data, spline fitting, and smoothing.

## 1D Interpolation

### InterpolatingUnivariateSpline (Fitting Splines)

```python
from scipy import interpolate
import numpy as np

# Sample data with noise
x = np.linspace(0, 10, 20)
y = np.sin(x) + 0.1 * np.random.randn(20)

# Fit a smoothing spline
spl = interpolate.InterpolatingUnivariateSpline(x, y)
y_smooth = spl(x)  # Interpolate at original points

# Evaluate at new points
x_new = np.linspace(0, 10, 100)
y_new = spl(x_new)

# Get derivatives
dy_dx = spl.derivative()(x_new)
d2y_dx2 = spl.derivatives(x_new, 2)[:, 1]
```

### UnivariateSpline (Smoothing Splines)

```python
# Smoothing spline with smoothing factor s
# s=0 gives interpolating spline, larger s gives smoother curve
spl_smooth = interpolate.UnivariateSpline(x, y, s=1.5)
y_smooth = spl_smooth(x_new)

# Using k for spline degree (k=1..5, default=3 cubic)
spl_quad = interpolate.UnivariateSpline(x, y, k=2, s=0.5)  # Quadratic spline
```

### interp1d (Simple Interpolation)

```python
from scipy import interpolate
import numpy as np

x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([0, 1, 4, 9, 16, 25])  # y = x²

# Linear interpolation
f_linear = interpolate.interp1d(x, y, kind='linear')
y_interp = f_linear(2.5)  # 12.5

# Cubic spline interpolation
f_cubic = interpolate.interp1d(x, y, kind='cubic')

# Nearest neighbor
f_nearest = interpolate.interp1d(x, y, kind='nearest')

# With extrapolation
f_extrap = interpolate.interp1d(x, y, kind='linear', fill_value='extrapolate')
y_outside = f_extrap(-1, 6)  # Extrapolate beyond data range
```

### CubicSpline (Explicit Cubic Splines)

```python
from scipy import interpolate
import numpy as np

x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 1, 0, 1, 0])

# Natural cubic spline (second derivative = 0 at endpoints)
cs = interpolate.CubicSpline(x, y, bc_type='natural')

# Clamped spline (first derivative specified at endpoints)
cs_clamped = interpolate.CubicSpline(x, y, bc_type=((1, 0.5), (1, -0.5)))

# Periodic spline
cs_periodic = interpolate.CubicSpline(x, y, bc_type='periodic')

# Evaluate and get derivatives
x_new = np.linspace(0, 4, 100)
y_new = cs(x_new)
dy_dx = cs.derivative()(x_new)
```

### Akima1DInterpolator (Robust to Outliers)

```python
from scipy import interpolate

x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 1, 10, 9, 8])  # Outlier at x=2

akima = interpolate.Akima1DInterpolator(x, y)
y_smooth = akima(np.linspace(0, 4, 100))
```

## Piecewise Polynomials

### BPoly (B-spline Representation)

```python
from scipy import interpolate
import numpy as np

# Create piecewise polynomial from coefficients
x = np.array([0, 1, 2, 3])
coeffs = np.array([
    [1, 0, 0, 0],  # Coefficients for interval [0, 1]
    [0, 1, 0, 0],  # Coefficients for interval [1, 2]
    [0, 0, 1, 0]   # Coefficients for interval [2, 3]
])

pp = interpolate.BPoly(coeffs, x)
y = pp(1.5)  # Evaluate at x=1.5
```

### make_interp_spline (B-spline Interpolation)

```python
x = np.linspace(0, 10, 20)
y = np.sin(x)

# Cubic B-spline interpolation
tck = interpolate.make_interp_spline(x, y, k=3)
y_new = tck(np.linspace(0, 10, 100))

# With smoothing (least squares fit)
tck_smooth = interpolate.make_lsq_spline(x, y, t=knots, k=3)
```

## Multidimensional Interpolation

### Regular Grid Data (interpn)

```python
from scipy import interpolate
import numpy as np

# Create a regular grid
x = np.linspace(0, 10, 20)
y = np.linspace(0, 10, 20)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y)

# Interpolate at arbitrary points
xi = np.array([5.5, 6.3, 7.1])
yi = np.array([3.2, 4.8, 5.9])

zi = interpolate.interpn((x, y), Z, (xi, yi), method='linear')
# or method='nearest' or method='slinear' (trilinear in 3D)
```

### RectBivariateSpline (2D Smoothing Splines)

```python
from scipy import interpolate

# Data on a regular grid
x = np.linspace(0, 10, 50)
y = np.linspace(0, 10, 50)
X, Y = np.meshgrid(x, y)
Z = np.exp(-(X**2 + Y**2))

# Fit 2D smoothing spline
spl2d = interpolate.RectBivariateSpline(x, y, Z, kx=3, ky=3)

# Evaluate at new grid
x_new = np.linspace(0, 10, 100)
y_new = np.linspace(0, 10, 100)
Z_new = spl2d(x_new, y_new)  # Returns 2D array

# Derivatives
dZ_dx = spl2d.derivative(m=1, n=0)(x_new, y_new)
```

### RegularGridInterpolator

```python
from scipy import interpolate
import numpy as np

# Define points on a regular grid
points = [np.linspace(0, 10, 5), np.linspace(0, 10, 5)]
values = np.random.rand(5, 5)

# Create interpolator
interp = interpolate.RegularGridInterpolator(points, values, method='linear')

# Evaluate at arbitrary points (must be 2D array of shape (n_points, ndim))
x_new = np.array([[2.5, 3.7], [5.1, 6.8], [8.2, 1.9]])
values_new = interp(x_new)
```

### LinearNDInterpolator (Irregular Grid)

```python
from scipy import interpolate
import numpy as np

# Irregularly spaced points
points = np.random.rand(50, 2)  # 50 points in 2D
values = np.sin(points[:, 0] * 10) * np.cos(points[:, 1] * 10)

# Create interpolator
interp = interpolate.LinearNDInterpolator(points, values)

# Evaluate at new points
points_new = np.random.rand(10, 2)
values_new = interp(points_new)
```

### NearestNDInterpolator

```python
from scipy import interpolate

# Same setup as LinearNDInterpolator
interp_nearest = interpolate.NearestNDInterpolator(points, values)
values_new = interp_nearest(points_new)
```

## Radial Basis Functions (RBF)

```python
from scipy import interpolate
import numpy as np

# Scattered data in 2D
np.random.seed(42)
points = np.random.rand(100, 2) * 10
values = np.sin(points[:, 0]) * np.cos(points[:, 1])

# Create RBF interpolator with different functions
rbf_linear = interpolate.Rbf(points, values, function='linear')
rbf_gaussian = interpolate.Rbf(points, values, function='gaussian')
rbf_multiquadric = interpolate.Rbf(points, values, function='multiquadric')

# Evaluate on a regular grid
x_grid = np.linspace(0, 10, 50)
y_grid = np.linspace( 0, 10, 50)
X, Y = np.meshgrid(x_grid, y_grid)
Z = rbf_gaussian(X, Y)
```

## Smoothing Splines for Noisy Data

### LSQUnivariateSpline (Least Squares Spline)

```python
from scipy import interpolate
import numpy as np

# Noisy data
x = np.linspace(0, 10, 50)
y = np.sin(x) + 0.3 * np.random.randn(50)

# Fit smoothing spline with specified knots
knots = np.linspace(0, 10, 10)  # Internal knots
spl = interpolate.LSQUnivariateSpline(x, y, knots)
y_smooth = spl(np.linspace(0, 10, 100))
```

### smoothing_spline (Automatic Smoothing)

```python
from scipy import interpolate

# Smoothing spline with smoothing factor s
# Larger s = smoother curve but less fit to data
x = np.linspace(0, 10, 50)
y = np.sin(x) + 0.3 * np.random.randn(50)

spl = interpolate.smoothing_spline(x, y, s=2.0)
y_smooth = spl(np.linspace(0, 10, 100))
```

## Cubic Splines in Multiple Dimensions

### Bispliner (Bivariate Smoothing Spline)

```python
from scipy import interpolate
import numpy as np

x = np.linspace(0, 10, 30)
y = np.linspace(0, 10, 30)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y) + 0.1 * np.random.randn(30, 30)

# Fit bivariate smoothing spline
spl = interpolate.Bispliner(x, y, Z, s=1.0)
Z_smooth = spl(x, y)
```

## Common Parameters

### interp1d Options

```python
f = interpolate.interp1d(x, y, 
                         kind='cubic',        # 'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                         fill_value=0.0,      # Value for extrapolation (or 'extrapolate')
                         bounds_error=False   # Don't raise error on extrapolation
                        )
```

### CubicSpline Boundary Conditions

```python
# bc_type options:
cs = interpolate.CubicSpline(x, y, bc_type='natural')  # y'' = 0 at endpoints
cs = interpolate.CubicSpline(x, y, bc_type='clamped')  # y' = 0 at endpoints
cs = interpolate.CubicSpline(x, y, bc_type='periodic') # Periodic boundary
cs = interpolate.CubicSpline(x, y, bc_type=((1, 0), (1, 0)))  # Custom: (order, value)
```

### RBF Function Types

```python
# Available functions for Rbf:
rbf = interpolate.Rbf(points, values, function='linear')     # Linear
rbf = interpolate.Rbf(points, values, function='thin_plate') # Thin plate spline
rbf = interpolate.Rbf(points, values, function='gaussian')   # Gaussian
rbf = interpolate.Rbf(points, values, function='cubic')      # Cubic
rbf = interpolate.Rbf(points, values, function='quintic')    # Quintic
```

## Troubleshooting

### Extrapolation Issues

```python
# Method 1: Use fill_value='extrapolate'
f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')

# Method 2: Extend the spline manually
cs = interpolate.CubicSpline(x, y, extrapolate=True)

# Method 3: Clip to valid range
f = interpolate.interp1d(x, y, bounds_error=False, fill_value=(y[0], y[-1]))
```

### Oscillations in High-Degree Splines

```python
# Use lower degree spline
spl = interpolate.UnivariateSpline(x, y, k=2)  # Quadratic instead of cubic

# Or use more smoothing
spl = interpolate.UnivariateSpline(x, y, s=5.0)

# Or use Akima interpolator (less oscillatory)
akima = interpolate.Akima1DInterpolator(x, y)
```

### Memory Issues with Large Grids

```python
# Use RegularGridInterpolator instead of meshgrid-based approaches
interp = interpolate.RegularGridInterpolator(points, values, method='linear')

# Process in chunks if necessary
for chunk in chunks(new_points):
    results.append(interp(chunk))
```

## See Also

- [`scipy.integrate`](references/02-integrate.md) - Integration using interpolants
- [`scipy.signal`](references/06-signal.md) - Signal smoothing with filters
- [`sklearn.neighbors`](https://scikit-learn.org/stable/modules/neighbors.html) - Nearest neighbor methods
