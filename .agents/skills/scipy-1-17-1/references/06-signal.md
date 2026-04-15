# scipy.signal - Signal Processing and Filters

The `scipy.signal` module provides tools for filtering, spectral analysis, convolution, and signal processing operations.

## Filtering

### Butterworth Filters

```python
from scipy import signal
import numpy as np

# Design a lowpass Butterworth filter
# Cutoff frequency: 0.2 * Nyquist (normalized)
b, a = signal.butter(N=5, Wn=0.2, btype='low')

# Apply filter to signal
t = np.linspace(0, 1, 1000)
signal_data = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 50 * t)

# Filter using lfilter (causal, one-pass)
filtered = signal.lfilter(b, a, signal_data)

# Filter with zero-phase filtering (forward and backward)
filtered_zp = signal.filtfilt(b, a, signal_data)

# Alternative: SOS format (more numerically stable)
sos = signal.butter(5, 0.2, btype='low', output='sos')
filtered_sos = signal.sosfilt(sos, signal_data)
```

### Filter Types and Design

```python
from scipy import signal

# Different filter types
b_butter, a_butter = signal.butter(5, 0.2, btype='low')    # Butterworth (maximally flat)
b_cheby1, a_cheby1 = signal.cheby1(5, 1, 0.2, btype='low') # Chebyshev Type I (ripple in passband)
b_cheby2, a_cheby2 = signal.cheby2(5, 20, 0.2, btype='low') # Chebyshev Type II (ripple in stopband)
b_ellip, a_ellip = signal.ellip(5, 1, 20, 0.2, btype='low') # Elliptic (ripple in both bands)

# Filter types: 'low' (default), 'high', 'bandpass', 'bandstop'
b_bandpass, a_bandpass = signal.butter(5, [0.1, 0.3], btype='bandpass')
```

### FIR Filters

```python
from scipy import signal

# Design FIR filter using window method
numtaps = 51  # Must be odd for linear phase
cutoff = 0.2  # Normalized frequency (0 to 1)

# Hamming window
fir_coeffs = signal.firwin(numtaps, cutoff, window='hamming')

# Other windows: 'boxcar', 'triang', 'blackman', 'hann'
fir_hann = signal.firwin(numtaps, cutoff, window='hann')

# Bandpass FIR filter
fir_bp = signal.firwin(51, [0.1, 0.3], pass_zero=False)

# Apply FIR filter (faster than IIR for long filters)
filtered = signal.lfilter(fir_coeffs, [1], signal_data)
```

### Filter Analysis

```python
from scipy import signal
import numpy as np

b, a = signal.butter(5, 0.2, btype='low')

# Frequency response
w, h = signal.freqz(b, a, worN=8000)
freq = w * fs / (2 * np.pi)  # Convert to Hz if sampling rate known

# Group delay
w, gd = signal.group_delay((b, a), w=1000)

# Pole-zero plot data
z, p, k = signal.tf2zpk(b, a)  # zeros, poles, gain

# Filter order and coefficients
print(f"Filter order: {len(a) - 1}")
print(f"Zeros: {z}")
print(f"Poles: {p}")
```

## Spectral Analysis

### Power Spectral Density (PSD)

```python
from scipy import signal
import numpy as np

# Generate sample signal
fs = 1000  # Sampling frequency (Hz)
t = np.linspace(0, 1, fs, endpoint=False)
signal_data = 0.5 * np.sin(2 * np.pi * 50 * t) + 0.3 * np.sin(2 * np.pi * 120 * t)

# Welch's method (recommended)
f, Pxx = signal.welch(signal_data, fs, nperseg=256)

# Periodogram (simpler but noisier)
f, Pxx_period = signal.periodogram(signal_data, fs, window='hann')

# Multitaper method (better spectral leakage control)
f, Pxx_mt = signal.multitaper(signal_data, fs, nw=4)
```

### Spectrogram (Time-Frequency Analysis)

```python
from scipy import signal
import numpy as np

fs = 1000
t = np.linspace(0, 2, 2*fs, endpoint=False)

# Chirp signal (frequency changes over time)
signal_data = signal.chirp(t, f0=20, t1=2, f1=200)

# Compute spectrogram
f, t_spec, Sxx = signal.spectrogram(signal_data, fs, nperseg=256, noverlap=128)

# Alternative: Short-time Fourier transform
f, t_spec, Zxx = signal.stft(signal_data, fs, nperseg=256)
```

### Peak Detection in Spectrum

```python
from scipy import signal

# Find peaks in PSD
f, Pxx = signal.welch(signal_data, fs, nperseg=256)

# Detect peaks (minimum height and distance)
peaks, properties = signal.find_peaks(Pxx, height=0.1, distance=10)

peak_freqs = f[peaks]
peak_powers = Pxx[peaks]
```

## Convolution and Correlation

### Convolution Operations

```python
from scipy import signal
import numpy as np

x = np.array([1, 2, 3])
h = np.array([0, 1, 0.5])

# Full convolution (output length = len(x) + len(h) - 1)
y_full = signal.convolve(x, h, mode='full')

# Same mode (output same size as larger input)
y_same = signal.convolve(x, h, mode='same')

# Valid mode (only fully overlapping regions)
y_valid = signal.convolve(x, h, mode='valid')

# 2D convolution (for images)
x2d = np.random.rand(10, 10)
h2d = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
y2d = signal.convolve2d(x2d, h2d, mode='same')

# Fast convolution using FFT (faster for long signals)
y_fast = signal.fftconvolve(x, h)
```

### Correlation Operations

```python
from scipy import signal

x = np.array([1, 2, 3, 4, 5])
y = np.array([5, 4, 3, 2, 1])

# Cross-correlation
corr = signal.correlate(x, y, mode='same')

# Auto-correlation
autocorr = signal.correlate(x, x, mode='full')

# Normalize correlation to [-1, 1]
corr_norm = signal.correlate(x, y, mode='same', method='fft')
corr_norm = corr_norm / np.max(np.abs(corr_norm))
```

### Matched Filtering

```python
from scipy import signal

# Template signal to detect
template = np.array([0, 1, 2, 3, 2, 1, 0])

# Signal containing template (with noise)
signal_data = np.concatenate([np.random.randn(10), template, np.random.randn(10)])

# Matched filter (cross-correlation with template)
matched = signal.correlate(signal_data, template, mode='same')

# Find detection peak
peak_idx = np.argmax(np.abs(matched))
```

## Wavelets

### Continuous Wavelet Transform (CWT)

```python
from scipy import signal
import numpy as np

# Generate signal with transient
t = np.linspace(0, 1, 1000)
signal_data = np.sin(2 * np.pi * 10 * t) + 0.5 * np.exp(-50 * (t - 0.5)**2)

# CWT with Morlet wavelet
scales = np.arange(1, 128)
cwt_coefficients, frequencies = signal.cwt(signal_data, 'morl', scales)

# CWT with different wavelets: 'mexh' (Mexican Hat), 'gaus1'-'gaus6', 'dmey'
```

### Discrete Wavelet Transform (DWT)

```python
from scipy import signal
import pywt  # PyWavelets package (separate installation)

# Note: DWT requires PyWavelets, not built into scipy.signal
# This is mentioned for completeness

# Alternative: Use scipy's built-in wavelet functions
signal_data = np.random.randn(1024)

# Maximal overlap discrete wavelet transform (MODWT)
# Available in newer SciPy versions
```

## Signal Generation

### Common Waveforms

```python
from scipy import signal
import numpy as np

t = np.linspace(0, 1, 1000)

# Sine wave
sine = signal.tone(1000, t, 50)  # 50 Hz tone at 1000 Hz sample rate

# Chirp (frequency sweep)
chirp = signal.chirp(t, f0=20, t1=1, f1=200)

# Pulse train
pulse_train = signal.square(2 * np.pi * 5 * t)  # 5 Hz square wave

# Sawtooth wave
sawtooth = signal.sawtooth(2 * np.pi * 5 * t)

# Triangle wave
triangle = signal.sawtooth(2 * np.pi * 5 * t, width=0.5)
```

### Impulse and Step Responses

```python
from scipy import signal

b, a = signal.butter(5, 0.2, btype='low')

# Impulse response
t, impulse_resp = signal.impulse((b, a), T=np.linspace(0, 1, 1000))

# Step response
t, step_resp = signal.step((b, a), T=np.linspace(0, 1, 1000))

# For state-space systems
A = [[-1, 1], [0, -2]]
B = [[0], [1]]
C = [[1, 0]]
D = [[0]]
system = signal.StateSpace(A, B, C, D)
t, impulse_ss = signal.impulse(system)
```

## Resampling and Interpolation

### Signal Resampling

```python
from scipy import signal
import numpy as np

# Original signal at 1000 Hz
fs_old = 1000
t = np.linspace(0, 1, fs_old)
signal_data = np.sin(2 * np.pi * 50 * t)

# Resample to 200 Hz (factor of 5 downsample)
signal_resampled = signal.resample(signal_data, 200)

# Resample with specific rate
from scipy import signal
signal_newrate = signal.resample_poly(signal_data, 1, 5)  # Downsample by 5

# Upsample by factor of 2
signal_upsampled = signal.resample_poly(signal_data, 2, 1)
```

### Decimation and Interpolation

```python
from scipy import signal

# Decimate (lowpass filter + downsample)
decimated = signal.decimate(signal_data, 5, ftype='iir')

# Interpolate (upsample + lowpass filter)
interpolated = signal.interpn((t,), signal_data, (t_fine,), method='linear')
```

## Feature Detection

### Peak Finding

```python
from scipy import signal
import numpy as np

signal_data = np.array([1, 3, 2, 4, 5, 3, 6, 7, 5, 8])

# Find peaks with various constraints
peaks, properties = signal.find_peaks(signal_data, 
                                      height=4,        # Minimum peak height
                                      distance=2,       # Minimum distance between peaks
                                      prominence=1.5,   # Minimum prominence
                                      width=1)          # Minimum width

# Access peak properties
peak_heights = properties['peak_heights']
peak_prominences = properties['prominences']

# Find valleys (invert signal and find peaks)
valleys, _ = signal.find_peaks(-signal_data)
```

### Zero Crossing Detection

```python
from scipy import signal
import numpy as np

signal_data = np.sin(np.linspace(0, 4 * np.pi, 1000))

# Find zero crossings (sign changes)
zero_crossings = np.where(np.diff(np.signbit(signal_data)))[0]

# Alternative using argrelextrema
peaks, _ = signal.argrelextrema(signal_data, np.greater)
valleys, _ = signal.argrelextrema(signal_data, np.less)
```

### Canny Edge Detection (2D Signals/Images)

```python
from scipy import signal
import numpy as np

# 2D signal or image
image = np.random.rand(100, 100)

# Sobel filter for edge detection
sobel_h = signal.sobelh(image)  # Horizontal edges
sobel_v = signal.sobelv(image)  # Vertical edges

# Gradient magnitude
gradient_mag = np.sqrt(sobel_h**2 + sobel_v**2)
```

## Troubleshooting

### Filter Edge Effects

```python
# Use filtfilt for zero-phase filtering (avoids phase distortion)
filtered = signal.filtfilt(b, a, signal_data, padlen=3*max(len(b), len(a)))

# Or use sosfiltfilt for SOS format (more stable)
sos = signal.butter(5, 0.2, output='sos')
filtered = signal.sosfiltfilt(sos, signal_data)
```

### Aliasing in Resampling

```python
# Always apply anti-aliasing filter before downsampling
signal_decimated = signal.decimate(signal_data, factor, ftype='iir', zero_phase=True)

# Or use resample_poly which includes filtering
signal_resampled = signal.resample_poly(signal_data, 1, factor)
```

### Numerical Stability in High-Order Filters

```python
# Use SOS (second-order sections) for high-order filters
sos = signal.butter(10, 0.2, output='sos')  # Better than b, a for order > 4
filtered = signal.sosfilt(sos, signal_data)

# Cascade multiple low-order filters
sos1 = signal.butter(5, 0.2, output='sos')
sos2 = signal.butter(5, 0.1, output='sos')
filtered = signal.sosfilt_zp(*signal.sos2zpk(sos1))
```

## See Also

- [`scipy.fft`](references/08-fft.md) - Fast Fourier Transform
- [`scipy.ndimage`](references/07-ndimage.md) - N-dimensional image filtering
- [`librosa`](https://librosa.org/) - Audio and music processing
