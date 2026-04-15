# scipy.fft - Fast Fourier Transform

The `scipy.fft` module provides fast Fourier transform functions with a consistent API across different backends. It's the recommended FFT interface in SciPy 1.17.1, offering better performance and consistency than the legacy `scipy.fftpack`.

## Basic FFT Operations

### 1D Fourier Transform

```python
from scipy import fft
import numpy as np

# Create sample signal
fs = 1000  # Sampling frequency (Hz)
T = 1/fs   # Sampling period
t = np.arange(0, 1, T)  # 1 second of data
signal = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)

# Forward FFT
fft_result = fft.fft(signal)

# Inverse FFT (reconstruct signal)
signal_reconstructed = fft.ifft(fft_result)

# Verify reconstruction
assert np.allclose(signal, signal_reconstructed.real)
```

### Frequency Components

```python
from scipy import fft
import numpy as np

fs = 1000  # Sampling frequency
N = len(signal)  # Number of samples

# Compute FFT
fft_result = fft.fft(signal)

# Frequency bins (Hz)
freqs = fft.fftfreq(N, d=T)  # T = 1/fs

# Single-sided spectrum (only positive frequencies)
N_half = N // 2
freqs_positive = freqs[:N_half]
fft_magnitude = np.abs(fft_result[:N_half]) * 2 / N  # Scale for single-sided

# Find dominant frequencies
peaks, _ = signal.find_peaks(fft_magnitude, height=0.1)
dominant_freqs = freqs_positive[peaks]
```

### Real-Valued FFT (More Efficient)

```python
from scipy import fft
import numpy as np

# For real-valued signals, use rfft/irfft (saves ~50% computation)
signal_real = np.sin(2 * np.pi * 50 * t)

# Forward FFT for real input
fft_real = fft.rfft(signal_real)

# Inverse FFT to recover real signal
signal_recovered = fft.irfft(fft_real, n=len(signal_real))

# Frequency bins for rfft
freqs_rfft = fft.rfftfreq(N, d=T)
```

## Multidimensional FFT

### 2D Fourier Transform (Images)

```python
from scipy import fft
import numpy as np

# Create 2D signal (image)
x = np.linspace(-1, 1, 256)
y = np.linspace(-1, 1, 256)
X, Y = np.meshgrid(x, y)
image = np.sin(2 * np.pi * 5 * X) * np.sin(2 * np.pi * 3 * Y)

# 2D FFT
fft_2d = fft.fft2(image)

# Inverse 2D FFT
image_reconstructed = fft.ifft2(fft_2d)

# Shift zero frequency to center (for visualization)
fft_shifted = fft.fftshift(fft_2d)

# Magnitude spectrum
magnitude = np.abs(fft_2d)
magnitude_db = 20 * np.log10(magnitude + 1e-10)  # Log scale for display
```

### 3D and Higher-Dimensional FFT

```python
from scipy import fft

# 3D volume data
volume = np.random.rand(64, 64, 64).astype(np.float64)

# 3D FFT
fft_3d = fft.fft3(volume)

# Inverse 3D FFT
volume_reconstructed = fft.ifft3(fft_3d)

# Partial FFT (along specific axes)
fft_axis0 = fft.fft(volume, axis=0)  # FFT only along first axis
fft_axes12 = fft.fft2(volume, axes=(1, 2))  # 2D FFT on axes 1 and 2
```

## FFT Frequency Analysis

### Power Spectral Density

```python
from scipy import fft
import numpy as np

fs = 1000  # Sampling frequency
signal = np.sin(2 * np.pi * 50 * t) + 0.3 * np.random.randn(len(t))

# Compute PSD using FFT
fft_result = fft.rfft(signal)
psd = np.abs(fft_result)**2 / (fs * len(signal))

# Double-sided PSD (except DC and Nyquist)
psd[1:-1] *= 2

# Frequency axis
freqs = fft.rfftfreq(len(signal), d=1/fs)

# Alternative: Use Welch's method from scipy.signal
from scipy import signal
f, Pxx = signal.welch(signal, fs, nperseg=256)
```

### Spectrogram (Time-Frequency Analysis)

```python
from scipy import fft
import numpy as np

# Chirp signal (frequency changes over time)
t = np.linspace(0, 2, 2000)
signal = fft.chirp(t, f0=20, t1=2, f1=200)

# Short-time Fourier transform
nperseg = 256
noverlap = 128

# Manual STFT computation
step = nperseg - noverlap
num_windows = (len(signal) - nperseg) // step + 1

spectrogram = np.zeros((nperseg // 2 + 1, num_windows))
times = np.arange(num_windows) * step / fs

for i in range(num_windows):
    start = i * step
    end = start + nperseg
    window = signal[start:end] * np.hanning(nperseg)
    spectrogram[:, i] = np.abs(fft.rfft(window))

# Or use scipy.signal.stft for convenience
from scipy import signal
f, t_spec, Zxx = signal.stft(signal, fs, nperseg=nperseg, noverlap=noverlap)
```

## FFT Convolution and Correlation

### Fast Convolution

```python
from scipy import fft
import numpy as np

# Two signals to convolve
signal1 = np.random.randn(1000)
signal2 = np.random.randn(100)

# FFT-based convolution (faster for long signals)
convolved = fft.fftconvolve(signal1, signal2, mode='full')

# Modes: 'full', 'same', 'valid'
convolved_same = fft.fftconvolve(signal1, signal2, mode='same')

# 2D convolution (for images)
image = np.random.rand(256, 256)
kernel = np.random.rand(11, 11)
convolved_2d = fft.fftconvolve(image, kernel, mode='same')
```

### Fast Correlation

```python
from scipy import fft

# Cross-correlation using FFT
signal1 = np.random.randn(1000)
signal2 = np.random.randn(1000)

# Cross-correlation
corr = fft.correlate(signal1, signal2, mode='same')

# Auto-correlation
autocorr = fft.correlate(signal1, signal1, mode='full')

# Normalize to [-1, 1]
autocorr_norm = autocorr / autocorr[len(autocorr) // 2]
```

## FFT Optimization and Performance

### Choosing FFT Backend

```python
from scipy import fft

# Check available backends
print(fft.get_available_backends())

# Set default backend
fft.set_backend('pocketfft')  # Default, pure Python/NumPy
# fft.set_backend('fftpack')  # Legacy SciPy FFTPACK
# fft.set_backend('pocketfft-threading')  # Multi-threaded

# Use specific backend for single operation
result = fft.fft(signal, backend='pocketfft')
```

### Performance Tips

```python
from scipy import fft
import numpy as np

# 1. Use rfft/irfft for real-valued data (50% faster)
if np.isrealobj(signal):
    result = fft.rfft(signal)
else:
    result = fft.fft(signal)

# 2. Pre-compute FFT for repeated convolutions
kernel_fft = fft.rfft(kernel, n=len(signal) + len(kernel) - 1)
for signal_chunk in signal_chunks:
    signal_fft = fft.rfft(signal_chunk, n=kernel_fft.shape[0])
    convolved = fft.irfft(signal_fft * kernel_fft)

# 3. Use appropriate array dtype (float64 for best precision)
signal = signal.astype(np.float64)

# 4. For very large arrays, consider chunking
def chunked_fft(signal, chunk_size=2**18):
    results = []
    for i in range(0, len(signal), chunk_size):
        chunk = signal[i:i+chunk_size]
        results.append(fft.fft(chunk))
    return np.concatenate(results)
```

### FFT Size Optimization

```python
from scipy import fft
import numpy as np

# FFT is fastest for sizes with small prime factors
# Powers of 2 are optimal
N_optimal = 2**int(np.ceil(np.log2(len(signal))))

# Zero-pad to optimal size
signal_padded = np.pad(signal, (0, N_optimal - len(signal)))
fft_result = fft.fft(signal_padded)

# Check if size is "good" for FFT
from scipy.fftpack import next_fast_len
N_fast = next_fast_len(len(signal))
```

## Advanced FFT Operations

### Window Functions

```python
from scipy import fft, signal
import numpy as np

# Apply window before FFT to reduce spectral leakage
window = signal.windows.hann(len(signal))  # Hanning window
signal_windowed = signal * window
fft_result = fft.rfft(signal_windowed)

# Other windows: 'hamming', 'blackman', 'triang', 'parzen', 'kaiser'
window_blackman = signal.windows.blackman(len(signal))
```

### Zero-Padding and Interpolation

```python
from scipy import fft

# Zero-padding increases frequency resolution (interpolates spectrum)
signal = np.sin(2 * np.pi * 50 * t)

# Original FFT
fft_original = fft.rfft(signal)
freqs_original = fft.rfftfreq(len(signal), d=T)

# Zero-padded FFT (4x interpolation in frequency domain)
N_padded = len(signal) * 4
fft_padded = fft.rfft(signal, n=N_padded)
freqs_padded = fft.rfftfreq(N_padded, d=T)

# Note: This interpolates the spectrum but doesn't add new information
```

### Phase and Group Delay

```python
from scipy import fft
import numpy as np

# Compute FFT
fft_result = fft.fft(signal)

# Magnitude and phase
magnitude = np.abs(fft_result)
phase = np.angle(fft_result)  # Phase in radians [-π, π]

# Unwrap phase (remove discontinuities)
phase_unwrapped = np.unwrap(phase)

# Group delay (derivative of phase with respect to frequency)
freqs = fft.fftfreq(len(signal), d=T)
group_delay = -np.diff(phase_unwrapped) / np.diff(2 * np.pi * freqs)
```

## Comparison with Legacy fftpack

```python
from scipy import fft, fftpack
import numpy as np

# Modern scipy.fft (recommended)
result_new = fft.fft(signal)

# Legacy scipy.fftpack (still available but not recommended)
result_legacy = fftpack.fft(signal)

# Results should be identical
assert np.allclose(result_new, result_legacy)

# Key differences:
# 1. scipy.fft has consistent axis handling
# 2. scipy.fft supports multiple backends
# 3. scipy.fft is generally faster
# 4. scipy.fft has better error handling
```

## Troubleshooting

### Aliasing Issues

```python
# Ensure sampling rate is at least 2x highest frequency (Nyquist)
fs = 1000  # Sampling frequency
f_max = fs / 2  # Nyquist frequency

# Filter signal before downsampling to avoid aliasing
from scipy import signal
b, a = signal.butter(5, 0.4, btype='low')  # Lowpass at 0.4 * Nyquist
signal_filtered = signal.filtfilt(b, a, signal)

# Then downsample
signal_downsampled = signal_filtered[::2]  # Halve sampling rate
```

### Spectral Leakage

```python
# Apply window function to reduce leakage
from scipy import signal

window = signal.windows.hann(len(signal))
signal_windowed = signal * window
fft_result = fft.rfft(signal_windowed)

# Or use overlapping windows with averaging (Welch's method)
f, Pxx = signal.welch(signal, fs, nperseg=256, noverlap=128)
```

### Gibbs Phenomenon

```python
# Smooth sharp transitions to reduce ringing
from scipy import ndimage

# Apply mild smoothing before FFT
signal_smoothed = ndimage.gaussian_filter1d(signal, sigma=1)
fft_result = fft.fft(signal_smoothed)

# Or use appropriate window function
window = signal.windows.kaiser(len(signal), beta=14)  # Kaiser window
```

## See Also

- [`scipy.signal`](references/06-signal.md) - Signal processing and spectral analysis
- [`numpy.fft`](https://numpy.org/doc/stable/reference/routines.fft.html) - NumPy's FFT implementation
- [`scipy.fftpack`](#legacy) - Legacy FFT interface (use scipy.fft instead)
