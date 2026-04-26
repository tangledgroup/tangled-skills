# Signal Processing (scipy.signal)

## Overview

The signal processing toolbox provides filtering functions, filter design tools, B-spline interpolation for equally-spaced data, and spectral analysis utilities.

## Filter Design

### IIR Filters

```python
from scipy import signal
import numpy as np

# Butterworth filter design
b, a = signal.butter(4, 0.2, btype='low')  # 4th order, cutoff 0.2

# Chebyshev Type I
b, a = signal.cheby1(4, 1, 0.2, btype='high')  # 1dB ripple

# Elliptic filter
b, a = signal.ellip(4, 1, 20, 0.2, btype='band')

# Automatic order selection
N, Wn = signal.buttord(0.2, 0.3, 1, 20)  # pass/stop freq, pass/stop ripple
b, a = signal.butter(N, Wn, btype='low')

# General IIR design
b, a = signal.iirdesign(0.2, 0.3, 1, 20)
```

### FIR Filters

```python
# Window method
fir_coeff = signal.firwin(65, 0.5, window='hamming')

# Frequency response method
fir_coeff = signal.firwin2(65, [0, 0.2, 0.4, 1.0], [1, 1, 0, 0])

# Parks-McClellan (equiripple)
fir_coeff = signal.remez(65, [0, 0.2, 0.4, 1.0], [1, 0])
```

## Filtering

### Applying Filters

```python
# Filter a signal using lfilter (direct form II transposed)
filtered = signal.lfilter(b, a, x)

# Zero-phase filtering (forward-backward, doubles filter order)
filtered = signal.filtfilt(b, a, x)

# Frequency-domain filtering (for FIR filters on long signals)
filtered = signal.fftconvolve(h, x, mode='full')
```

### Decimation and Resampling

```python
# Downsample by removing aliases (requires filter design)
downsampled = signal.decimate(x, 4)  # decimate by factor of 4

# Resample using FFT method
resampled = signal.resample(x, 1000)  # resample to 1000 points

# Resample with polyphase filter (better quality)
resampled = signal.resample_poly(x, 3, 4)  # up by 3, down by 4
```

## Spectral Analysis

### Power Spectral Density

```python
# Welch's method (recommended for PSD estimation)
f, Pxx = signal.welch(x, fs=1000, nperseg=256)

# Periodogram
f, Pxx = signal.periodogram(x, fs=1000)

# Cross-spectral density
f, Pxy = signal.csd(x, y, fs=1000)

# Coherence
f, Cxy = signal.coherence(x, y, fs=1000)
```

### Spectrogram and STFT

```python
# Short-time Fourier transform
f, t, Zxx = signal.stft(x, fs=1000, nperseg=256)

# Inverse STFT
x_reconstructed = signal.istft(Zxx, fs=1000, nperseg=256)

# Spectrogram (magnitude squared of STFT)
f, t, Sxx = signal.spectrogram(x, fs=1000)
```

## Window Functions

```python
# Get a window by name
window = signal.get_window('hann', 64)
window = signal.get_window('hamming', 64)
window = signal.get_window(('kaiser', 4.0), 64)  # tuple for parameterized

# New in 1.17: periodic/symmetric suffixes
window = signal.get_window('hann_periodic', 64)
window = signal.get_window('hann_symmetric', 64)
```

## B-Spline Interpolation

For equally-spaced data, B-spline routines provide fast interpolation and derivatives:

```python
# Upsample by spline interpolation
upsampled = signal.upfirdn(1, fir_coeff, x, up=4)

# Smooth via spline fitting
smoothed = signal.medfilt(x, kernel_size=5)  # median filter
```

## Continuous-Time Systems

```python
# Create transfer function from zeros, poles, gain
sys = signal.zpk(zeros, poles, gain)

# Convert between representations
b, a = signal.tf2zpk(num, den)  # TF to ZPK
num, den = signal.zpk2tf(z, p, k)  # ZPK to TF

# State-space representation
A, B, C, D = signal.tf2ss(num, den)

# Step and impulse response
t, y_step = signal.step(sys, T=np.linspace(0, 10, 1000))
t, y_impulse = signal.impulse(sys)
```

## 2-D Filtering

```python
# 2-D Butterworth filter
b, a = signal.butter(4, 0.2)
# Apply with filtfilt for zero-phase
result = signal.filtfilt(b, a, image, axis=0)
```

`hilbert2` gained `axes` keyword in 1.17 for specifying calculation axes.
