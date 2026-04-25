# scipy.stats - Statistical Distributions and Functions

The `scipy.stats` module provides a large collection of continuous and discrete probability distributions, statistical functions, and hypothesis tests.

## Continuous Distributions

### Normal Distribution

```python
from scipy import stats
import numpy as np

# Standard normal distribution (mean=0, std=1)
norm = stats.norm

# PDF at x
pdf_value = norm.pdf(0)  # Maximum of standard normal

# CDF at x (cumulative probability P(X <= x))
cdf_value = norm.cdf(1.96)  # ~0.975

# PPF (percent point function, inverse CDF)
ppf_value = norm.ppf(0.975)  # ~1.96

# Generate random samples
samples = norm.rvs(size=1000)

# Custom normal distribution
norm_custom = stats.norm(loc=5, scale=2)  # mean=5, std=2
pdf_custom = norm_custom.pdf(7)
```

### Other Common Distributions

```python
from scipy import stats

# t-distribution (Student's t)
t_dist = stats.t(df=10)  # 10 degrees of freedom

# Chi-square distribution
chi2_dist = stats.chi2(df=5)  # 5 degrees of freedom

# F-distribution
f_dist = stats.f(dfnum=5, dfden=10)  # numerator and denominator df

# Exponential distribution
exp_dist = stats.expon(scale=1/lambda_)  # scale = 1/λ

# Gamma distribution
gamma_dist = stats.gamma(a=2, scale=1)  # shape a, scale θ

# Beta distribution
beta_dist = stats.beta(alpha=2, beta=5)

# Uniform distribution
uniform_dist = stats.uniform(loc=0, scale=1)  # [0, 1]
```

### Working with Distributions

```python
from scipy import stats
import numpy as np

# Fit distribution to data
data = np.random.normal(5, 2, 1000)
params = stats.norm.fit(data)  # Returns (loc, scale)
mean_fit, std_fit = params

# Get distribution statistics
dist = stats.norm(loc=0, scale=1)
mean = dist.mean()      # Expected value
variance = dist.var()   # Variance
std = dist.std()        # Standard deviation
skewness = dist.skew()  # Skewness
kurtosis = dist.kurtosis()  # Kurtosis

# Interval containing specified probability
interval = stats.norm.interval(0.95, loc=0, scale=1)  # 95% interval

# Survival function (1 - CDF)
sf_value = stats.norm.sf(1.96)  # P(X > 1.96)

# Log PDF (more numerically stable)
logpdf = stats.norm.logpdf(0)
```

## Discrete Distributions

### Common Discrete Distributions

```python
from scipy import stats

# Binomial distribution
binom_dist = stats.binom(n=10, p=0.5)  # n trials, success probability p
pmf_value = binom_dist.pmf(5)  # P(X = 5)

# Poisson distribution
poisson_dist = stats.poisson(mu=3)  # mean rate λ
pmf_poisson = poisson_dist.pmf(2)  # P(X = 2)

# Geometric distribution
geom_dist = stats.geom(p=0.3)  # success probability p

# Hypergeometric distribution
hyper_dist = stats.hypergeom(M=50, n=10, nsample=5)  # Population M, successes n, sample size

# Negative binomial
nbinom_dist = stats.nbinom(n=5, p=0.3)  # n successes, probability p
```

## Statistical Tests

### Goodness of Fit Tests

#### Chi-Square Test

```python
from scipy import stats

# Test observed frequencies against expected
observed = [10, 20, 30, 40]
expected = [25, 25, 25, 25]

chi2_stat, p_value = stats.chisquare(observed, f_exp=expected)

if p_value < 0.05:
    print("Reject null hypothesis (distribution differs from expected)")
```

#### Kolmogorov-Smirnov Test

```python
import numpy as np

# Test if sample comes from specified distribution
data = np.random.normal(0, 1, 100)

# One-sample KS test (vs normal distribution)
ks_stat, p_value = stats.kstest(data, 'norm')

# KS test vs custom distribution
ks_stat, p_value = stats.kstest(data, 'norm', args=(5, 2))  # N(5, 2)

# Two-sample KS test (compare two samples)
data2 = np.random.normal(0.5, 1, 100)
ks_stat, p_value = stats.ks_2samp(data, data2)
```

#### Anderson-Darling Test

```python
# More powerful than KS for some alternatives
result = stats.anderson(data, dist='norm')

print(result.statistic)    # Test statistic
print(result.critical_values)  # Critical values at different levels
print(result.pvalue)       # P-value (if available)
```

### Tests for Normality

```python
from scipy import stats
import numpy as np

data = np.random.normal(0, 1, 100)

# Shapiro-Wilk test (best for n < 50)
stat_sw, p_sw = stats.shapiro(data)

# D'Agostino-Pearson test (uses skewness and kurtosis)
stat_ap, p_ap = stats.normaltest(data)

# Jarque-Bera test (based on skewness and kurtosis)
stat_jb, p_jb = stats.jarque_bera(data)
```

### Comparison Tests

#### t-Tests

```python
from scipy import stats
import numpy as np

# One-sample t-test
data = np.random.normal(5, 1, 30)
t_stat, p_value = stats.ttest_1samp(data, popmean=5.0)

# Paired samples t-test
before = np.array([20, 22, 19, 21, 23])
after = np.array([22, 25, 21, 24, 26])
t_stat, p_value = stats.ttest_rel(before, after)

# Independent samples t-test
group1 = np.random.normal(10, 2, 30)
group2 = np.random.normal(12, 2, 30)
t_stat, p_value = stats.ttest_ind(group1, group2)

# Welch's t-test (unequal variances)
t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
```

#### ANOVA (Analysis of Variance)

```python
from scipy import stats

# One-way ANOVA
group1 = np.random.normal(10, 2, 30)
group2 = np.random.normal(12, 2, 30)
group3 = np.random.normal(11, 2, 30)

f_stat, p_value = stats.f_oneway(group1, group2, group3)

if p_value < 0.05:
    print("At least one group mean is different")
```

#### Non-Parametric Tests

```python
from scipy import stats

# Mann-Whitney U test (non-parametric alternative to t-test)
group1 = np.array([23, 25, 28, 30, 32])
group2 = np.array([18, 20, 22, 24, 26])
u_stat, p_value = stats.mannwhitneyu(group1, group2)

# Wilcoxon signed-rank test (paired non-parametric)
before = np.array([20, 22, 19, 21, 23])
after = np.array([22, 25, 21, 24, 26])
w_stat, p_value = stats.wilcoxon(before, after)

# Kruskal-Wallis test (non-parametric ANOVA)
group1 = np.random.normal(10, 2, 30)
group2 = np.random.normal(12, 2, 30)
group3 = np.random.normal(11, 2, 30)
h_stat, p_value = stats.kruskal(group1, group2, group3)

# Spearman rank correlation
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 6, 8, 10])
rho, p_value = stats.spearmanr(x, y)

# Kendall's tau
tau, p_value = stats.kendalltau(x, y)
```

### Correlation and Covariance

```python
from scipy import stats
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])

# Pearson correlation coefficient
corr_pearson, p_value = stats.pearsonr(x, y)

# Spearman rank correlation
corr_spearman, p_value = stats.spearmanr(x, y)

# Kendall's tau
tau, p_value = stats.kendalltau(x, y)

# Point-biserial correlation (continuous vs binary)
x_binary = np.array([0, 1, 0, 1, 0])
y_continuous = np.array([2, 4, 3, 5, 2])
corr_pb, p_value = stats.pointbiserialr(x_binary, y_continuous)

# Covariance matrix
data = np.random.rand(100, 3)
cov_matrix = np.cov(data.T)
```

## Descriptive Statistics

### Basic Statistics

```python
from scipy import stats
import numpy as np

data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Mean, variance, standard deviation
mean_val = stats.mean(data)
variance = stats.variance(data)
std_dev = stats.std(data)

# Median and quantiles
median_val = stats.median(data)
q25, q75 = stats.scoreatpercentile(data, [25, 75])

# Mode (most frequent value)
mode_result = stats.mode(data, keepdims=False)
mode_val = mode_result.mode[0]

# Trimmed mean (remove outliers)
trim_mean = stats.trim_mean(data, 0.1)  # Remove 10% from each end

# Winsorized mean (replace outliers with boundary values)
win_mean = stats.winsorize(data, limits=0.1)
```

### Higher Moments

```python
from scipy import stats

# Skewness (asymmetry)
skew = stats.skew(data)  # >0: right-skewed, <0: left-skewed

# Kurtosis (tailedness)
kurt = stats.kurtosis(data)  # Fisher's definition (normal = 0)
kurt_normal = stats.kurtosis(data, fisher=False)  # Pearson's (normal = 3)

# Moment calculations
moment_2 = stats.moment(data, moment=2)  # Second central moment (variance)
```

### Quantile Statistics

```python
from scipy import stats
import numpy as np

data = np.random.normal(0, 1, 1000)

# Percentiles
percentiles = stats.scoreatpercentile(data, [25, 50, 75])

# Interquartile range
q25, q75 = np.percentile(data, [25, 75])
iqr = q75 - q25

# Quantiles with different interpolation methods
quantiles = stats.mstats.quantiles(data, probability=[0.25, 0.5, 0.75])
```

## Contingency Tables

```python
from scipy import stats
import numpy as np

# Create contingency table
observed = np.array([[10, 20, 30], [20, 30, 10]])

# Chi-square test of independence
chi2, p_value, dof, expected = stats.chi2_contingency(observed)

# Fisher's exact test (2x2 tables)
observed_2x2 = np.array([[10, 20], [30, 40]])
odds_ratio, p_value = stats.fisher_exact(observed_2x2)

# Likelihood ratio test
g_stat, p_value = stats.chi2_contingency(observed, lambda_='log-likelihood')
```

## Order Statistics and Quantile Estimation

```python
from scipy import stats
import numpy as np

data = np.random.normal(0, 1, 100)

# Probability plot correlation coefficient
ppcc_norm, p_value = stats.probplot(data, dist='norm', plot=None)

# Q-Q plot data (for manual plotting)
result = stats.probplot(data, dist='norm', plot=None)
x_theoretical = result[0][0]
y_sorted = result[0][1]

# Quantile-quantile comparison between distributions
result = stats.qqplot(data, line='45')
```

## Monte Carlo Integration and Sampling

### Random Number Generation

```python
from scipy import stats
import numpy as np

# Generate from any distribution
normal_samples = stats.norm.rvs(loc=0, scale=1, size=1000)
poisson_samples = stats.poisson.rvs(mu=3, size=1000)

# With random state for reproducibility
samples = stats.norm.rvs(size=1000, random_state=42)
```

### Quantile Estimation

```python
from scipy import stats
import numpy as np

data = np.random.normal(0, 1, 1000)

# Estimate quantiles with confidence intervals
quantile_est = stats.mstats.mquantiles(data, prob=[0.25, 0.5, 0.75], alpha=0.05)
```

## Troubleshooting

### Small Sample Size Issues

```python
# Use non-parametric tests for small samples
if n < 30:
    # Use Mann-Whitney instead of t-test
    stat, p = stats.mannwhitneyu(group1, group2)
else:
    stat, p = stats.ttest_ind(group1, group2)
```

### Ties in Rank-Based Tests

```python
# Specify how to handle ties
rho, p_value = stats.spearmanr(x, y, method='pearson')  # Alternative calculation

# Kendall's tau handles ties automatically
tau, p_value = stats.kendalltau(x, y)
```

### Numerical Stability in Distribution Functions

```python
# Use log PDF for numerical stability
log_prob = stats.norm.logpdf(x)
prob = np.exp(log_prob)

# Use survival function for tail probabilities
tail_prob = stats.norm.sf(10)  # Better than 1 - cdf(10)
```

## See Also

- [`scipy.optimize`](references/01-optimize.md) - Maximum likelihood estimation
- [`numpy.random`](https://numpy.org/doc/stable/reference/random/index.html) - NumPy random number generation
- [`statsmodels`](https://www.statsmodels.org/) - Advanced statistical modeling
