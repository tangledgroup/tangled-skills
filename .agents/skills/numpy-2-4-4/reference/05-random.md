# Random Number Generation

## Generator API (Recommended)

NumPy 2.x uses the `Generator` class as the recommended random number interface. Create a generator with `default_rng()`:

```python
import numpy as np

# Default: seeded from OS entropy
rng = np.random.default_rng()

# Reproducible: seed with integer
rng = np.random.default_rng(seed=42)

# Large unique seed for statistical independence
import secrets
seed = secrets.randbits(128)
rng = np.random.default_rng(seed)
```

### Generating Random Numbers

```python
# Uniform [0, 1)
rng.random()                    # single float
rng.random((3, 4))              # array of floats

# Integers in [low, high)
rng.integers(0, 10)             # single integer
rng.integers(0, 10, size=(3, 4)) # array of integers

# Standard normal distribution
rng.standard_normal()
rng.standard_normal((100,))

# General normal
rng.normal(loc=0, scale=1, size=1000)

# Other distributions
rng.uniform(low=-1, high=1, size=100)
rng.exponential(scale=2.0, size=50)
rng.poisson(lam=5, size=100)
rng.binomial(n=10, p=0.3, size=100)
rng.chisquare(df=3, size=50)
rng.gamma(shape=2, scale=1, size=50)
```

### Sampling and Permutation

```python
# Choice from array
rng.choice([10, 20, 30, 40], size=2, replace=False)

# Weighted choice
rng.choice(['a', 'b', 'c'], p=[0.1, 0.3, 0.6], size=10)

# Shuffle in place
arr = np.array([1, 2, 3, 4, 5])
rng.shuffle(arr)

# Permutation (returns new array)
perm = rng.permutation(10)       # shuffled [0..9]
perm = rng.permutation([10, 20, 30])  # shuffled copy

# Without replacement
rng.choice(100, size=10, replace=False)
```

## Bit Generators

Each `Generator` owns a `BitGenerator` that implements the core RNG algorithm. The bit generator manages state and produces random bits; the Generator transforms them into distributions.

### Available Bit Generators

| BitGenerator | Algorithm | Period | Notes |
|-------------|-----------|--------|-------|
| `PCG64` | Permuted Congruential Generator | 2^128 - 2^64 | Default, best statistical properties |
| `MT19937` | Mersenne Twister | 2^19937 - 1 | Legacy default (RandomState) |
| `Philox` | Counter-based | 2^128 | Good for parallel generation |
| `SFC64` | Simulated Feedback Counter | 2^64 | Lightweight alternative |
| `PCG64DXSM` | PCG64 with DXSM | 2^128 - 2^64 | Upgraded PCG64 for massive parallelism |
| `JumpableBitGenerator` | Protocol | — | Interface for jumping ahead in state |

### Using Alternative Bit Generators

```python
from numpy.random import MT19937, PCG64, Philox

rng = np.random.default_rng(PCG64(seed=42))
rng = np.random.default_rng(Philox(seed=42))
```

## Seeding and Reproducibility

### Seed Best Practices

- Use large, unique integers for seeds (128+ bits recommended)
- For reproducibility, document the seed value
- For independent experiments, use different seeds
- Never reuse a seed across production runs unless intentional

```python
import secrets
seed = secrets.randbits(128)
rng = np.random.default_rng(seed)
```

### SeedSequence for Advanced Control

`SeedSequence` converts user input into bit generator states and supports spawning child sequences:

```python
from numpy.random import SeedSequence

# Create a parent seed sequence
parent = SeedSequence(42)

# Spawn child sequences for parallel workers
children = parent.spawn(4)
for child in children:
    rng = np.random.default_rng(child)
    # Each generator produces independent streams
```

## Parallel Generation Strategies

### 1. SeedSequence Spawning (Recommended)

```python
from numpy.random import SeedSequence

parent = SeedSequence(12345)
child_seeds = parent.spawn(num_workers)
# Each worker gets: np.random.default_rng(child_seeds[i])
```

### 2. Independent Streams

Some bit generators support jumping to independent streams:

```python
rng = np.random.default_rng()
stream1 = rng.jumping()   # jump far ahead in state
stream2 = rng.jumping()   # another independent stream
```

### 3. State Jumping

```python
# Advance state by a large amount
rng.jumpahead(worker_id)
```

## Legacy RandomState (Deprecated but Available)

The old API still works but is not recommended for new code:

```python
# Old way (still supported)
np.random.seed(42)
np.random.randn(10)
np.random.randint(0, 10, size=5)
np.random.shuffle(arr)

# New way (recommended)
rng = np.random.default_rng(42)
rng.standard_normal(10)
rng.integers(0, 10, size=5)
rng.shuffle(arr)
```

### Migration Guide: Legacy → Generator

| Legacy (numpy.random.*) | Generator method |
|------------------------|-----------------|
| `np.random.rand(*shape)` | `rng.random(shape)` |
| `np.random.randn(*shape)` | `rng.standard_normal(shape)` |
| `np.random.randint(low, high, size)` | `rng.integers(low, high, size)` |
| `np.random.random(size)` | `rng.random(size)` |
| `np.random.normal(loc, scale, size)` | `rng.normal(loc, scale, size)` |
| `np.random.choice(a, size, replace, p)` | `rng.choice(a, size, replace, p)` |
| `np.random.shuffle(x)` | `rng.shuffle(x)` |
| `np.random.permutation(x)` | `rng.permutation(x)` |

Note: `np.random.randint` (legacy) uses `[low, high)` semantics. `rng.integers` supports both `[low, high)` with default `endpoint=False` and `[low, high]` with `endpoint=True`.

## Thread Safety

Generator instances are **not** thread-safe for concurrent access from multiple threads. Create separate Generator instances per thread:

```python
import threading
from numpy.random import SeedSequence

parent = SeedSequence(42)

def worker(worker_id):
    child = parent.spawn(1)[0]
    rng = np.random.default_rng(child)
    data = rng.standard_normal(1000)
    return data
```

NumPy 2.4 improves free-threaded Python support for random generation, but separate instances remain the recommended pattern.
