# Random Number Generation in NumPy 2.4.4

## Overview

NumPy provides modern random number generation via the `Generator` API (introduced in NumPy 1.17):

- **Modern Generator API**: `default_rng()` with PCG64, Philox, SFC64 bit generators
- **Legacy RandomState**: Still available for backward compatibility
- **SeedSequence**: Advanced seed management and spawning
- **Parallel generation**: Independent streams for multiprocessing

## Modern Generator API (Recommended)

### Creating a Generator

```python
import numpy as np

# Create generator with default PCG64 bit generator
rng = np.random.default_rng()  # Seeded from OS randomness

# Create reproducible generator with seed
rng = np.random.default_rng(42)  # Integer seed
rng = np.random.default_rng(123456789)  # Large integer recommended

# Use SeedSequence for advanced seeding
from numpy.random import SeedSequence
ss = SeedSequence(42)
rng = np.random.default_rng(ss)

# Specify bit generator explicitly
from numpy.random import PCG64, Philox, SFC64
rng = np.random.default_rng(bit_generator=Philox(42))
```

### Basic Distributions

#### Uniform Distribution

```python
rng = np.random.default_rng(42)

# Single random number in [0.0, 1.0)
single = rng.random()  # e.g., 0.773956048...

# Array of random numbers
array_1d = rng.random(5)           # 1D array
array_2d = rng.random((3, 4))      # 3x4 array

# Uniform in custom range [low, high)
uniform_range = rng.uniform(low=0, high=10, size=5)
uniform_range = rng.uniform(-5, 5, (3, 3))  # Range [-5, 5)
```

#### Integer Generation

```python
rng = np.random.default_rng(42)

# Random integers in [low, high)
single_int = rng.integers(low=0, high=10)     # e.g., 7
array_ints = rng.integers(0, 10, size=5)      # 5 integers in [0, 10)

# Inclusive high parameter
inclusive = rng.integers(0, 10, endpoint=True)  # [0, 10] inclusive

# Specific dtype
int32_arr = rng.integers(0, 100, size=5, dtype=np.int32)
```

#### Normal (Gaussian) Distribution

```python
rng = np.random.default_rng(42)

# Standard normal: mean=0, std=1
standard = rng.standard_normal(5)          # e.g., [-0.18, 1.14, ...]
standard_2d = rng.standard_normal((3, 3))

# Custom mean and standard deviation
custom = rng.normal(loc=100, scale=15, size=5)  # IQ-like distribution

# Multivariate normal
mean = [0, 0]
cov = [[1, 0.5], [0.5, 1]]
multivariate = rng.multivariate_normal(mean, cov, size=100)
```

### Common Probability Distributions

#### Continuous Distributions

```python
rng = np.random.default_rng(42)

# Exponential distribution
exponential = rng.exponential(scale=1.0, size=5)  # Mean = scale

# Gamma distribution
gamma = rng.gamma(shape=2.0, scale=1.0, size=5)

# Beta distribution (values in [0, 1])
beta = rng.beta(alpha=2, beta=5, size=5)

# Chi-square distribution
chi_square = rng.chisquare(df=2, size=5)

# F distribution
f_dist = rng.f(dfnum=2, dfden=2, size=5)

# Student's t-distribution
t_dist = rng.standard_t(df=3, size=5)

# Log-normal distribution
lognormal = rng.lognormal(mean=0, sigma=1, size=5)

# Pareto distribution
pareto = rng.pareto(a=1.0, size=5)

# Power function distribution
power = rng.power(a=2.0, size=5)  # [0, 1]

# Rayleigh distribution
rayleigh = rng.rayleigh(scale=1.0, size=5)

# Weibull distribution
weibull = rng.weibull(a=1.0, size=5)

# Gumbel distribution
gumbel = rng.gumbel(loc=0, scale=1, size=5)

# Von Mises distribution (circular data)
vonmises = rng.vonmises(mu=0.0, kappa=1.0, size=5)  # [-π, π]
```

#### Discrete Distributions

```python
rng = np.random.default_rng(42)

# Binomial distribution
binomial = rng.binomial(n=10, p=0.5, size=5)  # 10 trials, 50% success

# Poisson distribution (rare events)
poisson = rng.poisson(lam=3.0, size=5)  # Average 3 events

# Negative binomial
nbinom = rng.negative_binomial(n=5, p=0.5, size=5)

# Geometric distribution
geometric = rng.geometric(p=0.5, size=5)  # Trials until success

# Hypergeometric
hypergeom = rng.hypergeometric(ngood=5, nbad=5, nsample=5, size=5)

# Laplace distribution
laplace = rng.laplace(loc=0, scale=1, size=5)

# Logistic distribution
logistic = rng.logistic(loc=0, scale=1, size=5)

# Multinomial distribution
multinomial = rng.multinomial(n=10, p=[0.2, 0.3, 0.5], size=5)
```

### Sampling and Permutations

#### Choice and Sampling

```python
rng = np.random.default_rng(42)

# Random choice from array (with replacement by default)
choices = rng.choice([1, 3, 5, 7, 9], size=10)

# Without replacement
no_replace = rng.choice([1, 3, 5, 7, 9], size=3, replace=False)

# With weights/probabilities
weights = [0.1, 0.2, 0.3, 0.2, 0.2]
weighted = rng.choice([1, 2, 3, 4, 5], size=10, p=weights)

# Large population (efficient for large n)
large_choice = rng.choice(1000000, size=100)  # From range [0, 1000000)
```

#### Shuffling and Permutations

```python
rng = np.random.default_rng(42)

# Shuffle array in-place (returns None)
arr = np.array([1, 2, 3, 4, 5])
rng.shuffle(arr)  # arr is modified

# Return shuffled copy
permuted = rng.permutation(10)        # Permuted range [0, 10)
permuted_arr = rng.permutation(arr)   # Permuted copy of arr

# Shuffle specific axis of multi-dimensional array
matrix = np.arange(12).reshape(3, 4)
rng.shuffle(matrix, axis=0)  # Shuffle rows in-place
```

### Bit Generators

NumPy supports multiple bit generators with different properties:

```python
from numpy.random import default_rng, PCG64, Philox, SFC64, MT19937

# PCG64 (default) - Good balance of speed and quality
rng = default_rng(bit_generator=PCG64(42))

# Philox - Better for parallel generation, slightly slower
rng = default_rng(bit_generator=Philox(42))

# SFC64 - Smallest state, good for embedded systems
rng = default_rng(bit_generator=SFC64(42))

# MT19937 - Legacy Mersenne Twister (for compatibility)
rng = default_rng(bit_generator=MT19937(42))
```

## Seed Management

### SeedSequence

```python
from numpy.random import SeedSequence, default_rng

# Create seed sequence from integer
ss = SeedSequence(42)

# Spawn independent sub-generators
sub_ss_1 = ss.spawn(1)[0]
sub_ss_2 = ss.spawn(1)[1]

rng1 = default_rng(sub_ss_1)
rng2 = default_rng(sub_ss_2)
# rng1 and rng2 produce independent sequences

# Entropy from OS (for non-reproducible seeding)
ss_random = SeedSequence()  # Uses OS entropy

# From multiple integers
ss_multi = SeedSequence([1, 2, 3, 4])

# From bytes
ss_bytes = SeedSequence(bytes(16))
```

### Parallel Generation Patterns

```python
from numpy.random import default_rng, SeedSequence

# Pattern 1: Spawn independent streams
parent_ss = SeedSequence(42)
streams = parent_ss.spawn(num_streams=10)
rnga = [default_rng(ss) for ss in streams]

# Each rng produces independent sequence
results = [rng.random(5) for rng in rnga]

# Pattern 2: Jump ahead (for PCG64, Philox)
rng = default_rng(42)
rng.jump()  # Advance state significantly
# Now rng produces sequence far from original

# Pattern 3: Use different generators with same seed
rng1 = default_rng(42)
rng2 = default_rng(42)
# These produce IDENTICAL sequences (for reproducibility testing)
```

## Legacy API (Not Recommended)

The legacy `RandomState` and module-level functions are still available but deprecated:

```python
import numpy as np

# Legacy module-level functions (use Generator instead)
np.random.seed(42)  # Set global seed
rand_val = np.random.rand()          # Uniform [0, 1)
rand_array = np.random.rand(3, 3)    # 3x3 uniform array
randn_val = np.random.randn()        # Standard normal
int_val = np.random.randint(0, 10)   # Integer in [0, 10)

# Legacy RandomState class
rs = np.random.RandomState(42)
val = rs.random()
array = rs.normal(0, 1, (3, 3))

# Migration guide:
# np.random.rand(*shape) → rng.random(shape)
# np.random.randn(*shape) → rng.standard_normal(shape)
# np.random.randint(low, high, size) → rng.integers(low, high, size)
# np.random.random(*shape) → rng.random(shape)
```

## Common Patterns

### Reproducible Experiments

```python
import numpy as np

def experiment(seed=42):
    """Reproducible experiment with fixed seed"""
    rng = np.random.default_rng(seed)
    
    # Generate data
    X = rng.normal(0, 1, (100, 10))
    y = rng.integers(0, 2, 100)
    
    # Process and return results
    return process_data(X, y)

# Run with same seed for reproducibility
result1 = experiment(seed=42)
result2 = experiment(seed=42)  # Identical to result1
```

### Monte Carlo Simulation

```python
import numpy as np

def monte_carlo_pi(n_samples=100000, seed=42):
    """Estimate π using Monte Carlo"""
    rng = np.random.default_rng(seed)
    
    # Generate random points in unit square
    x = rng.random(n_samples)
    y = rng.random(n_samples)
    
    # Count points inside unit circle
    inside = np.sum(x**2 + y**2 < 1)
    
    # Estimate π
    pi_estimate = 4 * inside / n_samples
    return pi_estimate

result = monte_carlo_pi(1000000, seed=42)
print(f"π ≈ {result}")
```

### Bootstrap Resampling

```python
import numpy as np

def bootstrap_confidence_interval(data, n_bootstraps=1000, confidence=0.95, seed=42):
    """Compute bootstrap confidence interval"""
    rng = np.random.default_rng(seed)
    
    n_samples = len(data)
    bootstrap_means = []
    
    for _ in range(n_bootstraps):
        # Resample with replacement
        sample = rng.choice(data, size=n_samples, replace=True)
        bootstrap_means.append(np.mean(sample))
    
    # Compute confidence interval
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, alpha/2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha/2) * 100)
    
    return lower, upper

data = np.random.normal(100, 15, 100)
ci = bootstrap_confidence_interval(data)
print(f"95% CI: {ci}")
```

### A/B Testing Simulation

```python
import numpy as np

def simulate_ab_test(n_users=10000, conversion_rate_a=0.1, 
                     lift_b=0.1, seed=42):
    """Simulate A/B test with two variants"""
    rng = np.random.default_rng(seed)
    
    n_per_variant = n_users // 2
    
    # Group A conversions
    conversions_a = rng.binomial(1, conversion_rate_a, n_per_variant)
    rate_a = np.mean(conversions_a)
    
    # Group B conversions (with lift)
    conversion_rate_b = conversion_rate_a * (1 + lift_b)
    conversions_b = rng.binomial(1, conversion_rate_b, n_per_variant)
    rate_b = np.mean(conversions_b)
    
    return {
        'rate_a': rate_a,
        'rate_b': rate_b,
        'lift': (rate_b - rate_a) / rate_a,
        'n_a': n_per_variant,
        'n_b': n_per_variant
    }

result = simulate_ab_test(seed=42)
print(f"Conversion A: {result['rate_a']:.3f}")
print(f"Conversion B: {result['rate_b']:.3f}")
print(f"Lift: {result['lift']:.1%}")
```

## Performance Tips

1. **Create Generator once per process** - Reuse the same `rng` instance
2. **Use vectorized generation** - Generate arrays at once, not in loops
3. **Choose appropriate bit generator** - PCG64 for most cases, Philox for parallel
4. **Avoid legacy API** - Generator is faster and more flexible
5. **Use integers for large ranges** - `rng.integers()` is efficient

## Troubleshooting

**"Results not reproducible"**: Ensure you're using the same seed and bit generator.
```python
# WRONG: Different generators with same seed produce different results
rng1 = np.random.default_rng(42)  # PCG64
rng2 = np.random.RandomState(42)  # MT19937

# RIGHT: Use same type of generator
rng1 = np.random.default_rng(42)
rng2 = np.random.default_rng(42)
```

**"Random numbers look suspicious"**: Check you're not re-seeding in a loop.
```python
# WRONG: Re-seeding every iteration
for i in range(10):
    rng = np.random.default_rng(42)  # Always same seed!
    print(rng.random())

# RIGHT: Create generator once
rng = np.random.default_rng(42)
for i in range(10):
    print(rng.random())
```

**"Parallel streams not independent"**: Use SeedSequence.spawn().
```python
# WRONG: Same seed for all workers
rnga = [np.random.default_rng(42) for _ in range(10)]  # All identical!

# RIGHT: Spawn independent streams
ss = np.random.SeedSequence(42)
sub_ss = ss.spawn(10)
rnga = [np.random.default_rng(ss_i) for ss_i in sub_ss]
```
