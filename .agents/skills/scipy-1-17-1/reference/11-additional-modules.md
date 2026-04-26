# Additional Modules

## Clustering (scipy.cluster)

### Vector Quantization (vq)

```python
from scipy.cluster import vq
import numpy as np

# Normalize data
data, scale = vq.whiten(data)

# K-means clustering
codebook, distortion = vq.kmeans(data, 3)  # 3 clusters
labels, distance = vq.vq(data, codebook)   # assign to nearest centroid
```

### Hierarchical Clustering (hierarchy)

```python
from scipy.cluster import hierarchy
import numpy as np

# Compute linkage matrix
Z = hierarchy.linkage(data, method='ward')

# Cut tree into clusters
clusters = hierarchy.fcluster(Z, t=3, criterion='maxclust')

# Dendrogram
hierarchy.dendrogram(Z)

# Isomorphism test (improved performance in 1.17)
is_same = hierarchy.is_isomorphic(Z1, Z2)
```

Linkage methods: `single`, `complete`, `average`, `weighted`, `centroid`, `median`, `ward`.

## Physical and Mathematical Constants (scipy.constants)

```python
from scipy import constants

# Mathematical constants
print(constants.pi)        # 3.14159...
print(constants.golden)    # 1.61803...

# Physical constants (SI units, CODATA 2022 values)
print(constants.c)         # speed of light: 299792458 m/s
print(constants.h)         # Planck constant
print(constants.G)         # gravitational constant
print(constants.e)         # elementary charge
print(constants.k)         # Boltzmann constant
print(constants.N_A)       # Avogadro constant
print(constants.m_e)       # electron mass

# Constants database
print(constants.value('electron mass'))
print(constants.unit('electron mass'))
print(constants.find('magnetic'))  # search constants
```

## Finite Difference Differentiation (scipy.differentiate)

Numerical differentiation of black-box functions:

```python
from scipy import differentiate
import numpy as np

# Derivative of scalar function
deriv = differentiate.derivative(np.sin, 0.5)

# Jacobian
jac = differentiate.jacobian(my_func, x_point)

# Hessian
hess = differentiate.hessian(my_func, x_point)
```

## File I/O (scipy.io)

### MATLAB Files

```python
import scipy.io as sio

# Load .mat file
data = sio.loadmat('file.mat')

# Save to .mat file
sio.savemat('output.mat', {'variable_name': array})

# List variables in .mat file
info = sio.whosmat('file.mat')
```

### WAV Files

```python
import scipy.io.wavfile as wav

# Read WAV
rate, data = wav.read('audio.wav')

# Write WAV
wav.write('output.wav', rate, data)
```

### ARFF Files (Weka format)

```python
from scipy.io import arff
data, meta = arff.loadarff('file.arff')
```

## Multi-Dimensional Image Processing (scipy.ndimage)

Operations on N-dimensional arrays:

```python
from scipy import ndimage
import numpy as np

# Linear filtering
filtered = ndimage.gaussian_filter(image, sigma=2.0)
filtered = ndimage.uniform_filter(image, size=5)
convolved = ndimage.correlate(image, kernel)

# Non-linear filtering
median_filtered = ndimage.median_filter(image, size=5)
rank_filtered = ndimage.rank_filter(image, rank=10, size=7)

# Morphological operations
eroded = ndimage.binary_erosion(binary_image, structure=np.ones((3,3)))
dilated = ndimage.binary_dilation(binary_image)
opened = ndimage.binary_opening(binary_image)
closed = ndimage.binary_closing(binary_image)

# Object measurement
labeled, num_features = ndimage.label(binary_image)
centers = ndimage.center_of_mass(image, labeled, range(num_features+1))
areas = ndimage.sum(image, labeled, index=np.arange(1, num_features+1))

# Interpolation (geometric transforms)
shifted = ndimage.shift(image, shift=[1, 2])
rotated = ndimage.rotate(image, angle=45)
zoomed = ndimage.zoom(image, zoom=2.0)
```

## Datasets (scipy.datasets)

Built-in sample datasets for testing:

```python
from scipy import datasets

# Ash dataset
ash_data = datasets.ash()
print(ash_data.data)
print(ash_data.descriptions)
```

## Legacy FFTPack (scipy.fftpack)

The legacy `scipy.fftpack` module is still available but `scipy.fft` is preferred:

```python
from scipy import fftpack
y = fftpack.fft(x)
```

## Orthogonal Distance Regression (scipy.odr)

Fits models where both independent and dependent variables have errors:

```python
from scipy import odr
import numpy as np

def linear_beta(beta, x):
    return beta[0] + beta[1] * x

model = odr.Model(linear_beta)
data = odr.Data(x, y)
odr_obj = odr.ODR(data, model, beta0=[1, 1])
result = odr_obj.run()
print(result.beta)  # [intercept, slope]
```

## Parallel Execution

Many SciPy functions support parallel execution:

- `scipy.integrate.quadvec`: Vectorized quadrature with `workers` parameter
- `scipy.optimize.minimize`: Some methods support parallel gradient/Hessian evaluation
- `scipy.fft.fft`: Supports `workers` parameter for multi-threaded computation
- Thread safety: Most SciPy functions are thread-safe when using separate GIL threads. See the thread safety documentation for details.

## Array API Standard Support

Many functions now support the Python Array API standard, enabling dispatch to GPU backends. Coverage tables are available in the development documentation. Set `SCIPY_ARRAY_API` environment variable to control behavior.
