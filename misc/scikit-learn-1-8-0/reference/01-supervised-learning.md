# Supervised Learning

## Linear Models

Linear models assume a linear relationship between features and target. Scikit-learn provides a comprehensive suite covering regression, classification, and regularization.

### Ordinary Least Squares

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X, y)
predictions = model.predict(X_new)
```

Key attributes after fitting: `coef_` (weights), `intercept_` (bias), `score()` returns R².

### Ridge Regression (L2 Regularization)

Prevents overfitting by penalizing large coefficients:

```python
from sklearn.linear_model import Ridge, RidgeCV
model = Ridge(alpha=1.0).fit(X, y)
# Automatic alpha selection via cross-validation
model_cv = RidgeCV(alphas=[0.1, 1.0, 10.0]).fit(X, y)
print(f"Best alpha: {model_cv.alpha_}")
```

### Lasso (L1 Regularization)

Produces sparse solutions by driving some coefficients to exactly zero:

```python
from sklearn.linear_model import Lasso, LassoCV
model = Lasso(alpha=0.1).fit(X, y)
# Cross-validation variant
model_cv = LassoCV(alphas=[0.01, 0.1, 1.0]).fit(X, y)
```

In version 1.8, Lasso and ElasticNet families gained significant speed improvements through gap safe screening rules — up to 10x faster for regularization paths.

### Elastic-Net (L1 + L2)

Combines L1 sparsity with L2 stability:

```python
from sklearn.linear_model import ElasticNet
model = ElasticNet(alpha=0.1, l1_ratio=0.5).fit(X, y)
```

### Logistic Regression

For binary and multiclass classification:

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(C=1.0, max_iter=1000).fit(X, y)
probas = model.predict_proba(X_new)
```

**Version 1.8 API change:** The `penalty` parameter is deprecated. Use `l1_ratio` instead:
- `l1_ratio=0` for L2 (was `penalty="l2"`)
- `l1_ratio=1` for L1 (was `penalty="l1"`)
- `0 < l1_ratio < 1` for elasticnet
- `C=np.inf` for no penalty (was `penalty=None`)

### Stochastic Gradient Descent

For large-scale learning with online capabilities:

```python
from sklearn.linear_model import SGDClassifier, SGDRegressor
clf = SGDClassifier(loss="log_loss", random_state=0).fit(X, y)
reg = SGDRegressor(loss="squared_error", random_state=0).fit(X, y)
```

**Version 1.8 note:** `PassiveAggressiveClassifier` and `PassiveAggressiveRegressor` are deprecated. Use `SGDClassifier` / `SGDRegressor` with `learning_rate="pa1"` or `"pa2"`.

### Generalized Linear Models

```python
from sklearn.linear_model import HuberRegressor, QuantileRegressor
# Robust to outliers
huber = HuberRegressor().fit(X, y)
# Quantile regression
qr = QuantileRegressor(quantile=0.5).fit(X, y)
```

### Bayesian Regression

```python
from sklearn.linear_model import BayesianRidge,ARDRegression
model = BayesianRidge().fit(X, y)
```

## Support Vector Machines

SVMs find the optimal hyperplane separating classes:

```python
from sklearn.svm import SVC, SVR
clf = SVC(kernel="rbf", C=1.0).fit(X, y)
reg = SVR(kernel="rbf", C=1.0).fit(X, y)
```

Common kernels: `"linear"`, `"poly"`, `"rbf"` (default), `"sigmoid"`.

For large datasets, use `LinearSVC` or `SGDClassifier(loss="hinge")` instead.

## Nearest Neighbors

```python
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
clf = KNeighborsClassifier(n_neighbors=5).fit(X, y)
reg = KNeighborsRegressor(n_neighbors=5).fit(X, y)
# Unsupervised: find nearest neighbors
from sklearn.neighbors import NearestNeighbors
nn = NearestNeighbors(n_neighbors=3).fit(X)
distances, indices = nn.kneighbors(X_new)
```

## Gaussian Processes

Probabilistic model for regression and classification with uncertainty estimates:

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel

kernel = ConstantKernel(1.0) * RBF(length_scale=1.0)
gpr = GaussianProcessRegressor(kernel=kernel).fit(X, y)
y_pred, sigma = gpr.predict(X_new, return_std=True)
```

Version 1.8: `GaussianProcessRegressor.predict` is faster when `return_cov=False` and `return_std=False`.

## Decision Trees

```python
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
clf = DecisionTreeClassifier(max_depth=5, random_state=0).fit(X, y)
reg = DecisionTreeRegressor(max_depth=5, random_state=0).fit(X, y)
# Visualize
from sklearn.tree import export_text
print(export_text(clf, feature_names=["a", "b"]))
```

Version 1.8: `DecisionTreeRegressor` with `criterion="absolute_error"` is now O(n log n) instead of O(n²), enabling scaling to millions of data points. Multiple bug fixes for missing value handling and near-constant features.

## Ensemble Methods

### Random Forests

```python
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
clf = RandomForestClassifier(n_estimators=100, random_state=0).fit(X, y)
# Feature importances
importances = clf.feature_importances_
```

### Gradient Boosting

```python
from sklearn.ensemble import GradientBoostingClassifier
clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=0).fit(X, y)
```

### Histogram-based Gradient Boosting (HistGBR/HistGBC)

Faster than classic gradient boosting for large datasets:

```python
from sklearn.ensemble import HistGradientBoostingClassifier
clf = HistGradientBoostingClassifier(random_state=0).fit(X, y)
# Supports missing values natively
# Supports categorical features via categorical_features parameter
```

### Bagging

```python
from sklearn.ensemble import BaggingClassifier
clf = BaggingClassifier(estimator=DecisionTreeClassifier(), n_estimators=100, random_state=0).fit(X, y)
```

Version 1.8: `BaggingClassifier`, `BaggingRegressor`, and `IsolationForest` now properly use `sample_weight` to draw samples. When `max_samples` is a float, it is interpreted as a fraction of `sample_weight.sum()`.

### Voting and Stacking

```python
from sklearn.ensemble import VotingClassifier, StackingClassifier
voting = VotingClassifier(
    estimators=[("lr", LogisticRegression()), ("rf", RandomForestClassifier())],
    voting="soft"
).fit(X, y)
stacking = StackingClassifier(
    estimators=[("lr", LogisticRegression()), ("rf", RandomForestClassifier())],
    final_estimator=LogisticRegression()
).fit(X, y)
```

### Isolation Forest (Anomaly Detection)

```python
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.1, random_state=0).fit(X)
labels = iso.predict(X)  # 1 for inliers, -1 for outliers
scores = iso.score_samples(X)
```

## Multiclass and Multioutput

```python
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
ovr = OneVsRestClassifier(SVC()).fit(X, y_multiclass)
ovo = OneVsOneClassifier(SVC()).fit(X, y_multiclass)
# Multi-output regression
from sklearn.multioutput import MultiOutputRegressor
mor = MultiOutputRegressor(RandomForestRegressor()).fit(X, y_multioutput)
```

## Semi-Supervised Learning

```python
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
# -1 indicates unlabeled samples
y_partial = y.copy()
y_partial[10:] = -1
lp = LabelPropagation(kernel="knn", n_neighbors=7).fit(X, y_partial)
```

Version 1.8: User-written kernel results are now properly normalized in `LabelPropagation`.

## Neural Networks (MLP)

```python
from sklearn.neural_network import MLPClassifier, MLPRegressor
clf = MLPClassifier(hidden_layer_sizes=(100,), max_iter=1000, random_state=0).fit(X, y)
reg = MLPRegressor(hidden_layer_sizes=(100,), max_iter=1000, random_state=0).fit(X, y)
```
