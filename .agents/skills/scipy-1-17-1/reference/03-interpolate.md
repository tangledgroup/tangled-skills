# Interpolation (scipy.interpolate)

## Choosing an Interpolation Method

The choice depends on data structure and desired smoothness:

**1D data**:
- Linear: `numpy.interp` or `interp1d(kind='linear')`
- Cubic spline: `CubicSpline` (2nd derivative continuous)
- Monotone cubic: `PchipInterpolator` (1st derivative continuous, non-overshooting)
- General spline: `make_interp_spline` (k-th derivative continuous for order k)
- Nearest: `interp1d(kind='nearest')`

**N-D regular grid**:
- `RegularGridInterpolator` — methods: 'nearest', 'linear', 'cubic', 'quintic', 'pchip'

**N-D scattered data**:
- `NearestNDInterpolator` / `griddata(method='nearest')`
- `LinearNDInterpolator` / `griddata(method='linear')`
- `CloughTocher2DInterpolator` (2D only, cubic)
- `RBFInterpolator` — radial basis functions

## 1-D Interpolation

### Cubic Splines

```python
from scipy.interpolate import CubicSpline
import numpy as np

x = np.array([0, 1, 2, 3])
y = np.array([1, 0, 1, -1])
cs = CubicSpline(x, y)
new_x = np.linspace(0, 3, 50)
new_y = cs(new_x)
```

### Monotone Interpolation (PCHIP)

Preserves monotonicity and avoids overshooting:

```python
from scipy.interpolate import PchipInterpolator
pchip = PchipInterpolator(x, y)
```

### B-Splines

`make_interp_spline` creates interpolating B-splines of arbitrary order. `make_smoothing_spline` creates smoothing splines with GCV penalty:

```python
from scipy.interpolate import make_interp_spline, make_smoothing_spline

# Interpolating spline of order 3 (cubic)
spl = make_interp_spline(x, y, k=3)

# Smoothing spline
ss = make_smoothing_spline(x, y)
```

In 1.17, `make_splrep` and `make_splprep` gained a `bc_type` argument ('not-a-knot' or 'periodic') for boundary condition control.

### Piecewise Polynomials

`PPoly` represents piecewise polynomials with efficient evaluation:

```python
from scipy.interpolate import PPoly
pp = PPoly.from_spline(cs)
```

## N-D Interpolation on Regular Grids

`RegularGridInterpolator` for data on structured grids:

```python
from scipy.interpolate import RegularGridInterpolator
import numpy as np

x, y = np.mgrid[0:3:10j, 0:3:10j]
z = np.sin(x**2 + y**2)
interp = RegularGridInterpolator((np.linspace(0, 3, 10),
                                   np.linspace(0, 3, 10)), z, method='cubic')
new_points = np.random.rand(5, 2)
values = interp(new_points)
```

In 1.17, 'cubic' and 'quintic' modes have improved performance, and `.grid`/`.values` are now read-only properties.

## Scattered Data Interpolation

`griddata` for unstructured point data:

```python
from scipy.interpolate import griddata
import numpy as np

points = np.random.rand(100, 2)
values = np.sin(10 * points[:, 0]) * np.cos(10 * points[:, 1])
grid_x, grid_y = np.mgrid[0:1:100j, 0:1:100j]
grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')
```

## Radial Basis Functions

`RBFInterpolator` for smooth interpolation of scattered data:

```python
from scipy.interpolate import RBFInterpolator
rbf = RBFInterpolator(points, values, kernel='WendlandC6')
```

In 1.17, RBFInterpolator gained an array API standard compatible backend with improved GPU support.

## Rational Interpolation

`AAA` algorithm for rational approximation (improved numerical stability in 1.17):

```python
from scipy.interpolate import AAA
r = AAA(x, y)
```

`FloaterHormannInterpolator` for non-polynomial rational interpolation with multidimensional batched input support (new in 1.17).

## Smoothing Splines

For noisy data, smoothing splines balance fit quality and smoothness:

```python
from scipy.interpolate import make_smoothing_spline
ss = make_smoothing_spline(x_noisy, y_noisy)
```

2D smoothing via `bisplrep` (scattered data), `RectBivariateSpline` (gridded data).

## Legacy Interface

`interp1d` is the legacy 1-D interpolation interface. Recommended replacements:
- `interp1d(kind='linear')` → `PchipInterpolator` or `CubicSpline`
- `interp1d(kind='nearest')` → `interp1d` with kind='nearest' (still supported)
