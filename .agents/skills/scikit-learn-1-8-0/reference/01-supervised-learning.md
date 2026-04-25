# Supervised Learning Algorithms

## Linear Models

### Ordinary Least Squares

```python
from sklearn.linear_model import LinearRegression

reg = LinearRegression()
reg.fit(X_train, y_train)
predictions = reg.predict(X_test)
```

- Coefficients stored in `coef_`, intercept in `intercept_`
- Relies on feature independence; problematic with multicollinearity
- For non-negative coefficients: `LinearRegression(positive=True)`

### Ridge Regression (L2 Regularization)

```python
from sklearn.linear_model import Ridge

ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)
```

- Minimizes: ||Xw - y||² + α||w||²
- Larger α → more shrinkage → more robust to collinearity
- `RidgeClassifier` variant for classification
- Solvers: `'auto'` (default), `'lbfgs'`, `'cholesky'`, `'sparse_cg'`

### Lasso (L1 Regularization)

```python
from sklearn.linear_model import Lasso

lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)
```

- Performs feature selection by driving some coefficients to zero
- Good for high-dimensional data with sparse true solutions
- `LassoCV` / `LassoLarsCV` for automatic alpha selection via cross-validation

### Elastic Net

```python
from sklearn.linear_model import ElasticNet

enet = ElasticNet(alpha=0.1, l1_ratio=0.5)
enet.fit(X_train, y_train)
```

- Combines L1 and L2 penalties: α·ρ||w||₁ + ½α(1-ρ)||w||²₂
- `l1_ratio=0` → Ridge, `l1_ratio=1` → Lasso
- Useful when features are correlated

### Logistic Regression

```python
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=1000)
clf.fit(X_train, y_train)
proba = clf.predict_proba(X_test)
```

- `C`: inverse regularization strength (smaller = stronger regularization)
- `penalty`: 'l1', 'l2', 'elasticnet', 'none'
- `solver`: `'lbfgs'` (default), `'liblinear'`, `'saga'`, `'newton-cg'`, `'sag'`
- For multiclass: `'ovr'` (one-vs-rest) or `'multinomial'`
- Supports class weighting via `class_weight='balanced'`

### Support Vector Machines

#### SVC / NuSVC

```python
from sklearn.svm import SVC

svc = SVC(kernel='rbf', C=1.0, gamma='scale')
svc.fit(X_train, y_train)
```

- **Kernels:** `'linear'`, `'poly'`, `'rbf'` (default), `'sigmoid'`, `'precomputed'`
- `C`: regularization parameter (larger = less overfitting)
- `gamma`: kernel coefficient — `'scale'` (default), `'auto'`, or float
- `NuSVC`: uses ν parameter instead of C
- Memory efficient: uses subset of training points (support vectors)
- For sparse data: use `scipy.sparse.csr_matrix` with `dtype=float64`

#### LinearSVC

```python
from sklearn.svm import LinearSVC

lin_svc = LinearSVC(C=1.0, dual='auto', max_iter=1000)
```

- Faster for large datasets with linear kernel
- Uses squared hinge loss
- Lacks `support_` attribute and probability estimates

#### SVR (Regression)

```python
from sklearn.svm import SVR

svr = SVR(kernel='rbf', C=1.0, epsilon=0.1)
```

- `epsilon`: margin of tolerance — predictions within ε are ignored
- `NuSVR` variant available

### k-Nearest Neighbors

```python
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='minkowski')
knn.fit(X_train, y_train)
```

- `n_neighbors`: number of neighbors (default 5)
- `weights`: `'uniform'` or `'distance'` (closer points weighted more)
- `metric`: 'euclidean', 'manhattan', 'chebyshev', 'minkowski', or custom
- No training phase; stores all data in memory
- Good for multi-output problems with discrete outputs

### Decision Trees

```python
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

tree = DecisionTreeClassifier(max_depth=5, min_samples_split=10, random_state=42)
tree.fit(X_train, y_train)
```

- `max_depth`: max tree depth (None = unlimited)
- `min_samples_split`: min samples to split a node (default 2)
- `min_samples_leaf`: min samples required at leaf node
- `criterion`: 'gini' (default), 'entropy', 'squared_error' (regression), 'absolute_error', 'friedman_mse', 'poisson'
- Extractable: `tree.feature_importances_`, `tree.export_text()`

### Random Forests

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
```

- Ensemble of decorrelated decision trees
- `n_estimators`: number of trees (default 100)
- `max_features`: max features for split ('sqrt'/'log2' recommended)
- `oob_score=True`: use out-of-bag samples for evaluation
- Handles high-dimensional data well; provides feature importances

### Gradient Boosting

#### GradientBoostingClassifier/Regressor

```python
from sklearn.ensemble import GradientBoostingClassifier

gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gb.fit(X_train, y_train)
```

- Builds trees sequentially, each correcting previous errors
- `n_estimators`: number of boosting stages
- `learning_rate`: shrinkage factor (lower = more robust but slower)
- `max_depth`: tree depth (default 3)
- Best for small-to-medium datasets (< tens of thousands samples)

#### HistGradientBoostingClassifier/Regressor

```python
from sklearn.ensemble import HistGradientBoostingClassifier

hgb = HistGradientBoostingClassifier(max_iter=100, max_depth=6, learning_rate=0.1)
hgb.fit(X_train, y_train)
```

- **Orders of magnitude faster** for large datasets (> tens of thousands samples)
- Inspired by LightGBM/XGBoost
- Native support for **missing values** and **categorical features**
- `max_iter`: replaces `n_estimators`
- `max_bins`: number of bins for data binning (default 255)
- `l2_regularization`: L2 regularization parameter

**Losses for regression:** `'squared_error'` (default), `'absolute_error'`, `'gamma'`, `'poisson'`, `'quantile'`

### Neural Networks

```python
from sklearn.neural_network import MLPClassifier

mlp = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
mlp.fit(X_train, y_train)
```

- `hidden_layer_sizes`: tuple of layer sizes (default (100,))
- `activation`: 'identity', 'logistic' (sigmoid), 'tanh', 'relu' (default)
- `solver`: 'lbfgs', 'sgd', 'adam'
- `alpha`: L2 regularization parameter
- `batch_size`: mini-batch size
- Scales well to large datasets with `'sgd'` or `'adam'`

### Naive Bayes

```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB, ComplementNB

# Gaussian (continuous features)
gnb = GaussianNB()
gnb.fit(X_train, y_train)

# Multinomial (count/discrete features, e.g., text)
mnb = MultinomialNB(alpha=1.0)
mnb.fit(X_train_counts, y_train)

# Complement (imbalanced multi-class text classification)
cnb = ComplementNB()
```

- `GaussianNB`: assumes normal distribution
- `MultinomialNB`: for count data; alpha for smoothing
- `BernoulliNB`: for binary/boolean features
- `ComplementNB`: robust to imbalanced classes
- `CategoricalNB`: for categorical features

### Ensemble Methods (Advanced)

#### Bagging

```python
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier

bag = BaggingClassifier(DecisionTreeClassifier(), n_estimators=50, random_state=42)
bag.fit(X_train, y_train)
```

- Base estimator trained on bootstrap samples
- Reduces variance of high-variance estimators

#### AdaBoost

```python
from sklearn.ensemble import AdaBoostClassifier

ada = AdaBoostClassifier(n_estimators=100, learning_rate=1.0, algorithm='SAMME')
ada.fit(X_train, y_train)
```

- `algorithm`: 'SAMME' (categorical) or 'SAMME.R' (real)
- Increases weight of misclassified samples

## Choosing the Right Estimator

| Problem Type | Small Data (<10K) | Large Data (>10K) |
|-------------|-------------------|-------------------|
| Classification | LogisticRegression, SVC, RandomForest | HistGradientBoostingClassifier, SGDClassifier |
| Regression | Ridge, Lasso, SVR | HistGradientBoostingRegressor, LinearRegression |
| High-dimensional | LinearSVC, LogisticRegression | SGDClassifier, LinearSVC |
| Non-linear | RandomForest, GradientBoosting | HistGradientBoostingClassifier |
| Probabilistic output | CalibratedClassifierCV wrapper | Same + scaling |
