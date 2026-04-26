# Statistics (scipy.stats)

## Probability Distributions

SciPy provides over 80 continuous and discrete probability distributions. Each distribution is a class with consistent methods.

### Common Methods

All distributions share these methods:

- `pdf(x)` / `logpdf(x)`: Probability density function
- `cdf(x)` / `logcdf(x)`: Cumulative distribution function
- `sf(x)` / `logsf(x)`: Survival function (1 - CDF, more accurate in tails)
- `ppf(q)` / `isf(q)`: Percent point function (inverse CDF)
- `rvs(size=...)`: Random variate generation
- `fit(data)`: Maximum likelihood estimation of parameters
- `entropy()`: Differential/discrete entropy

### Usage Pattern

```python
from scipy import stats
import numpy as np

# Create a frozen distribution with fixed parameters
norm = stats.norm(loc=0, scale=1)
print(norm.pdf(0))     # 0.3989...
print(norm.cdf(1.96))  # 0.975
print(norm.ppf(0.975)) # 1.96

# Generate random samples
samples = norm.rvs(size=1000)

# Fit distribution to data
data = np.random.randn(1000) * 2 + 5
loc, scale = stats.norm.fit(data)
```

### Key Continuous Distributions

`norm`, `expon`, `gamma`, `beta`, `chi2`, `f`, `t`, `lognorm`, `uniform`, `cauchy`, `laplace`, `gumbel_r`, `weibull_min`, `truncnorm`, `vonmises`, `multivariate_normal`, `dirichlet`

### Key Discrete Distributions

`binom`, `poisson`, `geom`, `hypergeom`, `nbinom`, `bernoulli`, `zipf`, `scipy.stats.zipfian`

### New in 1.17

- `matrix_t`: Matrix t distribution with `pdf`, `logpdf`, `rvs` methods
- `Logistic`: Logistic distribution for modeling random variables
- `truncpareto` now accepts negative exponent shape parameter
- `multivariate_t` and `multivariate_normal` gained `marginal` method

## Hypothesis Tests

### One-Sample Tests

```python
from scipy import stats
import numpy as np

data = np.random.randn(100) + 0.5

# T-test against a known mean
t_stat, p_value = stats.ttest_1samp(data, popmean=0)

# Shapiro-Wilk test for normality
stat, p = stats.shapiro(data)

# Kolmogorov-Smirnov test
stat, p = stats.kstest(data, 'norm')
```

### Two-Sample Tests

```python
data1 = np.random.randn(50)
data2 = np.random.randn(50) + 1

# T-test for equal means
t_stat, p_value = stats.ttest_ind(data1, data2)

# Mann-Whitney U test (non-parametric)
u_stat, p_value = stats.mannwhitneyu(data1, data2)

# Kolmogorov-Smirnov two-sample
stat, p = stats.ks_2samp(data1, data2)
```

### Variance Tests

- `levene`: Levene's test for equal variances
- `bartlett`: Bartlett's test (requires normality)
- `fligner`: Fligner-Killeen test (robust to non-normality)

### Correlation

```python
# Pearson correlation
r, p = stats.pearsonr(x, y)

# Spearman rank correlation
rho, p = stats.spearmanr(x, y)
# Or array-API compatible: stats.spearmanrho(x, y) (new in 1.17)

# Kendall tau
tau, p = stats.kendalltau(x, y)
```

### Chi-Square Tests

```python
# Goodness of fit
stat, p = stats.chisquare(f_obs, f_exp=None)

# Independence in contingency table
from scipy.stats import chi2_contingency
stat, p, dof, expected = chi2_contingency(observed_table)
```

## Descriptive Statistics

```python
from scipy import stats
import numpy as np

data = np.random.randn(1000)

# Quantiles
q = stats.quantile(data, [0.25, 0.5, 0.75])
# New in 1.17: weights argument, round_inward/outward/neareast methods

# Trimmed mean
tm = stats.trim_mean(data, proportiontocut=0.1)

# Median absolute deviation
mad = stats.median_abs_deviation(data)

# Skewness and kurtosis
skew = stats.skew(data)
kurt = stats.kurtosis(data)
```

## Kernel Density Estimation (KDE)

```python
from scipy.stats import gaussian_kde

samples = np.random.randn(1000)
kde = gaussian_kde(samples)
x_eval = np.linspace(-3, 3, 100)
pdf_est = kde(x_eval)
```

Multivariate KDE: `gaussian_kde` works with 2D arrays for multivariate data.

## Quasi-Monte Carlo (QMC)

For low-discrepancy sequences in integration and sampling:

```python
from scipy.stats import qmc
import numpy as np

# Sobol sequence
sobol = qmc.Sobol(d=2)
points = sobol.random(n=1000)

# Halton sequence
halton = qmc.Halton(d=3)
points = halton.random(n=1000)

# Latin hypercube sampling
lhc = qmc.LatinHypercube(d=5)
points = lhc.random(n=100)

# Poisson disk sampling (fixed overlapping bug in 1.17.1)
pd = qmc.PoissonDisk(radius=0.1, bounding_radius=0.5)
points = pd.random(n=100)
```

## Trimming and Winsorizing

```python
from scipy.stats import trimboth, winsorize

# Trim 10% from each end
trimmed = trimboth(data, proportionstocut=0.1)

# Winsorize at 5%
winsorized = winsorize(data, limits=0.05)
```

## Performance Notes

Many test statistics were vectorized in 1.17: `ansari`, `cramervonmises`, `fligner`, `friedmanchisquare`, `kruskal`, `ks_1samp`, `levene`, `mood`. This improves performance with multidimensional (batch) input.
