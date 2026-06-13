# Version 1.8 New Features

## Free-Threaded CPython 3.14 Support

Scikit-learn now supports free-threaded (nogil) CPython with pre-built wheels for all supported platforms on Python 3.14. Free-threaded CPython removes the Global Interpreter Lock (GIL), enabling efficient multi-threaded use cases.

```bash
# Install free-threaded Python 3.14, then:
pip install scikit-learn
python3.14 -X isolated ...
```

## Temperature Scaling in CalibratedClassifierCV

New calibration method for better probability estimates, especially in multi-class settings:

```python
from sklearn.calibration import CalibratedClassifierCV
# Temperature scaling (new in 1.8)
ts = CalibratedClassifierCV(clf, method="temperature", ensemble=False).fit(X, y)
# Sigmoid calibration (existing)
sig = CalibratedClassifierCV(clf, method="sigmoid", ensemble=False).fit(X, y)
```

Temperature scaling often produces better calibrated probabilities than sigmoid calibration in multi-class problems.

## ClassicalMDS

New manifold learning algorithm performing classical MDS via eigendecomposition of the double-centered distance matrix:

```python
from sklearn.manifold import ClassicalMDS
X_embedded = ClassicalMDS(n_components=2).fit_transform(distance_matrix)
```

## Enhanced MDS and TSNE

- `MDS` now supports arbitrary distance metrics via `metric` and `metric_params` parameters
- `MDS` supports initialization via classical MDS via the `init` parameter
- The old `dissimilarity` parameter was deprecated
- The old `metric` parameter was renamed to `metric_mds`
- `TSNE` now supports PCA initialization with sparse input matrices

```python
from sklearn.manifold import MDS
X_embedded = MDS(
    n_components=2, metric="precomputed", init="classical_mds"
).fit_transform(X)
```

## Gap Safe Screening in Linear Models

Major efficiency improvement for L1-penalized estimators. The coordinate descent solver now uses gap safe screening rules to set feature coefficients to zero early and skip them in subsequent iterations. Speedup is particularly pronounced (up to 10x) for regularization paths:

- `ElasticNet`, `Lasso`, `MultiTaskElasticNet`, `MultiTaskLasso` and their CV variants
- `GraphicalLasso`, `GraphicalLassoCV`, `graphical_lasso` with `mode="cd"`
- `DictionaryLearning`, `SparseCoder`, `MiniBatchSparsePCA`, `SparsePCA` with coordinate descent

```python
from sklearn.linear_model import ElasticNetCV
# Up to 10x faster than 1.7 for regularization paths
model = ElasticNetCV().fit(X, y)
```

## Expanded Array API Support

20+ estimators and functions now support Array API compliant inputs, enabling compatibility with PyTorch tensors, JAX arrays, CuPy, and other Array API implementations:

- `StandardScaler`, `PolynomialFeatures`, `LabelBinarizer`
- `RidgeCV`, `RidgeClassifier`, `RidgeClassifierCV` (with `solver="svd"`)
- `CalibratedClassifierCV` (with `method="temperature"`)
- `GaussianMixture` (with random init), `GaussianNB`
- `confusion_matrix`, `roc_curve`, `precision_recall_curve`, `det_curve`
- `brier_score_loss`, `log_loss`, `d2_brier_score`, `d2_log_loss_score`
- `balanced_accuracy_score`, `cohen_kappa_score`, `calinski_harabasz_score`
- `davies_bouldin_score`, `median_absolute_error`
- `pairwise_kernels`, `pairwise_distances`, `manhattan_distances`, `laplacian_kernel`
- `cross_val_predict`

```python
import sklearn
sklearn.set_config(array_api_compat="pytorch")  # or "jax", "cupy", etc.
# Estimators now accept torch tensors, jax arrays, etc.
```

## QuadraticDiscriminantAnalysis Enhancements

QDA now has `solver`, `covariance_estimator`, and `shrinkage` parameters, making it more similar to `LinearDiscriminantAnalysis`:

```python
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
qda = QuadraticDiscriminantAnalysis(
    solver="empirical", shrinkage="auto"
).fit(X, y)
```

## API Changes and Deprecations

### Deprecated (removed in 1.10)

- `LogisticRegression.penalty` — use `l1_ratio` instead
- `LogisticRegressionCV.penalty` — use `l1_ratios` instead
- `PassiveAggressiveClassifier` / `PassiveAggressiveRegressor` — use `SGDClassifier`/`SGDRegressor` with `learning_rate="pa1"` or `"pa2"`
- Negative values for `power_t` in SGD estimators
- `LogisticRegression.n_jobs` — has no effect since 1.8
- `utils.extmath.stable_cumsum` — use `np.cumulative_sum` directly
- `metrics.cluster.entropy`
- `estimator_name` parameter in `PrecisionRecallDisplay` — use `name` instead
- `y_pred` in `DetCurveDisplay.from_predictions` and `PrecisionRecallDisplay.from_predictions` — use `y_score`

### Changed Defaults

- `LogisticRegression.l1_ratio` default changed from `None` to `0.0`
- `SGDClassifier` / `SGDOneClassSVM` default `eta0` changed from `0` to `0.01`
- `HDBSCAN.copy` will change from `False` to `True` in 1.10
- `LogisticRegressionCV.use_legacy_attributes` controls fitted attribute shapes (default `True`, changes to `False` in 1.10)

### Logistic Regression Penalty Migration

```python
# Old (deprecated in 1.8, removed in 1.10)
lr = LogisticRegression(penalty="l2")

# New
lr = LogisticRegression(l1_ratio=0)       # L2 penalty
lr = LogisticRegression(l1_ratio=1)       # L1 penalty
lr = LogisticRegression(l1_ratio=0.5)     # Elasticnet
lr = LogisticRegression(C=np.inf)         # No penalty
```

## Other Notable Changes

- `DecisionTreeRegressor(criterion="absolute_error")`: O(n log n) complexity, scales to millions of data points
- `GaussianProcessRegressor.predict` faster when `return_cov=False` and `return_std=False`
- `SparseCoder` now follows the transformer API with `fit` method
- `BaggingClassifier/Regressor/IsolationForest` properly use `sample_weight` for sampling
- `GraphicalLasso` uses cyclic (not random) coordinate descent for reproducibility
- `MinCovDet` corrected for consistency at normal distribution
- `SelectFromModel` no longer forces `max_features <= n_input_features`
- `SplineTransformer` handles missing values via `handle_missing` parameter
- `MaxAbsScaler` can clip out-of-range values via `clip` parameter
- `PowerTransformer` warns on NaN in `inverse_transform`
- `OneHotEncoder` fixed `handle_unknown='warn'` behavior
- `LabelPropagation` properly normalizes user-written kernel results
- Multiple decision tree fixes for missing value handling and near-constant features
- Improved error messages for sparse inputs in classification metrics
- Classification metrics now consistently raise `ValueError` on empty input arrays
