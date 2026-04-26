# Fourier Transforms (scipy.fft)

## Overview

`scipy.fft` provides fast and flexible FFT implementations. It is the preferred module over the legacy `scipy.fftpack`. Supports 1-D, N-D transforms with various windowing and normalization options.

```python
from scipy.fft import fft, ifft, fft2, fftshift, fftfreq
import numpy as np
```

## 1-D Discrete Fourier Transforms

```python
# Forward FFT
y = fft(x)

# Inverse FFT
x_recovered = ifft(y)

# With normalization
y = fft(x, norm='ortho')  # orthonormal normalization

# Specifying output size
y = fft(x, n=1024)  # zero-pad or truncate to 1024 points
```

### Frequency Analysis Example

```python
from scipy.fft import fft, fftfreq
import numpy as np

N = 600
T = 1.0 / 800.0
x = np.linspace(0, N*T, N, endpoint=False)
signal = 3*np.sin(50*2*np.pi*x) + 2*np.sin(120*2*np.pi*x)

y = fft(signal)
freqs = fftfreq(N, T)

# Plot positive frequencies only
positive_mask = freqs > 0
plt.plot(freqs[positive_mask], np.abs(y[positive_mask]))
```

## N-D Fourier Transforms

```python
# 2-D FFT
y2d = fft2(image)
x2d = ifft2(y2d)

# N-D FFT (arbitrary dimensions)
y_nd = fftn(data)
x_nd = ifftn(y_nd)

# FFT along specific axis
y = fft(x, axis=0)
```

### Shift Operations

```python
# Shift zero-frequency component to center
shifted = fftshift(fft2(image))

# Inverse shift
unshifted = ifftshift(shifted)
```

## Discrete Cosine Transforms (DCT)

Four types of DCT:

```python
from scipy.fft import dct, idct

# Type II DCT (most common, default)
y = dct(x, type=2)
x_recovered = idct(y, type=2)

# Type I, III, IV
y1 = dct(x, type=1)
y3 = dct(x, type=3)
y4 = dct(x, type=4)

# Orthogonal normalization
y = dct(x, type=2, norm='ortho')
```

## Discrete Sine Transforms (DST)

```python
from scipy.fft import dst, idst

# Type II DST
y = dst(x, type=2)
x_recovered = idst(y, type=2)
```

## Fast Hankel Transform

For functions with radial symmetry:

```python
from scipy.fft import hankel2d, ihankel2d
import numpy as np

# Create radially symmetric data
r = np.linspace(0, 10, 100)
data = np.exp(-r**2 / 2)

# Hankel transform (order 0 by default)
transformed = hankel2d(data, r, order=0)
```

## Performance Tips

- `scipy.fft` uses the FFTPACK library and supports both CPU and GPU backends
- For real-valued input, use `rfft` / `irfft` for ~2x speedup
- Choose power-of-2 sizes when possible for maximum performance
- The `workers` parameter enables multi-threaded computation
