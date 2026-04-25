# Model Evaluation & Selection

## Cross-Validation

### K-Fold Split

```python
from sklearn.model_selection import KFold, cross_val_score

kf = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(clf, X, y, cv=kf, scoring='accuracy')
print(f"Mean score: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
```

### Stratified K-Fold

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
# Preserves class distribution in each fold
```

### Repeated Stratified K-Fold

```python
from sklearn.model_selection import RepeatedStratifiedKFold

rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
# Repeats the k-fold process multiple times for more stable estimates
```

### Train-Test Split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

- `stratify`: ensures same class distribution in split
- `shuffle`: shuffle before splitting (default True)

### Time Series Split

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
```

- Maintains temporal order (no future data in training)
- Each test set is a contiguous block after the training set

### Group K-Fold

```python
from sklearn.model_selection import GroupKFold

gkf = GroupKFold(n_splits=5)
# Ensures same group never appears in both train and test
for train_idx, test_idx in gkf.split(X, y, groups=patient_ids):
    ...
```

- `groups`: array of sample group labels (e.g., patient IDs, sessions)
- Prevents data leakage from related samples

### Leave-One-Out / Leave-P-Out

```python
from sklearn.model_selection import LeaveOneOut, LeavePOut

loo = LeaveOneOut()  # n_splits = n_samples
lpo = LeavePOut(p=5)  # leave out 5 samples at a time
```

- Maximum cross-validation; computationally expensive
- LOO: each sample gets exactly one test set

## Model Selection

### Grid Search

```python
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

param_grid = {
    'C': [0.1, 1, 10, 100],
    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
    'kernel': ['rbf', 'linear']
}

grid = GridSearchCV(
    SVC(), param_grid, cv=5, scoring='accuracy',
    n_jobs=-1, verbose=1
)
grid.fit(X_train, y_train)

print(f"Best params: {grid.best_params_}")
print(f"Best CV score: {grid.best_score_:.4f}")
```

- Exhaustive search over all parameter combinations
- `n_jobs=-1`: use all CPU cores
- Returns fitted estimator with best parameters

### Randomized Search

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_distributions = {
    'C': randint(1, 100),
    'gamma': uniform(0.001, 0.1),
    'kernel': ['rbf', 'linear']
}

random_search = RandomizedSearchCV(
    SVC(), param_distributions, n_iter=20, cv=5,
    scoring='accuracy', random_state=42, n_jobs=-1
)
random_search.fit(X_train, y_train)
```

- `n_iter`: number of parameter settings sampled
- More efficient than grid search for large parameter spaces
- scipy.stats distributions for continuous parameters

### Bayes Optimization (v1.8+)

```python
# Requires scikit-optimize or similar package
from skopt import BayesSearchCV

bayes = BayesSearchCV(
    SVC(),
    search_spaces={'C': (1e-3, 1e3, 'log-uniform'),
                   'gamma': (1e-4, 1e2, 'log-uniform')},
    n_iter=50, cv=5
)
```

- Uses Bayesian optimization to select promising parameters
- More sample-efficient than random search
- Requires external package

### Nested Cross-Validation

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.model_selection import GridSearchCV

inner_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Each outer fold:
#   - Inner CV performs hyperparameter tuning
#   - Outer fold evaluates on held-out data
scores = cross_val_score(
    SVC(), X, y, cv=outer_cv,
    # For nested CV with GridSearchCV:
    estimator=GridSearchCV(SVC(), param_grid, cv=inner_cv)
)
print(f"Nested CV score: {scores.mean():.4f}")
```

- Unbiased estimate of generalization performance
- Inner loop for hyperparameter tuning, outer loop for evaluation
- Avoids optimistic bias from single CV

## Learning Curves & Validation Curves

### Learning Curve

```python
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt

train_sizes, train_scores, val_scores = learning_curve(
    clf, X, y, cv=5, scoring='accuracy',
    train_sizes=[0.1, 0.25, 0.5, 0.75, 1.0],
    n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)
plt.plot(train_sizes, train_mean, 'o-', label='Training')
plt.plot(train_sizes, val_mean, 'o-', label='Validation')
plt.legend()
```

- `train_sizes`: fractions or absolute numbers
- High training + low validation → overfitting
- Low training + low validation → underfitting
- Gap closing with more data → need more data

### Validation Curve

```python
from sklearn.model_selection import validation_curve

param_range = [0.001, 0.01, 0.1, 1, 10, 100]
train_scores, val_scores = validation_curve(
    clf, X, y, param_name='C', param_range=param_range,
    cv=5, scoring='accuracy', n_jobs=-1
)
```

- Evaluates model performance as a function of one hyperparameter
- Helps identify overfitting (large gap) and optimal parameter values

## Model Persistence

### Saving/Loading Models

```python
from sklearn import set_config
import joblib

# Save
joblib.dump(clf, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')

# Load
clf = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
```

- `joblib` preferred over `pickle` for numpy arrays
- Works with pipelines, transformers, and estimators
- Model files include all fitted parameters

### Exporting Config

```python
# Get estimator parameters
print(clf.get_params())
clf.set_params(C=10)  # update parameter

# Set global config
set_config(transform_output='pandas')  # return pandas DataFrames
```

## Scoring Metrics

See [Classification Metrics](#classification-metrics) and [Regression Metrics](#regression-metrics) sections below for detailed metric reference.

### Custom Scoring

```python
from sklearn.metrics import make_scorer, f1_score, accuracy_score

# Custom scorer
custom_scorer = make_scorer(f1_score, average='macro')

# In GridSearchCV
grid = GridSearchCV(clf, param_grid, cv=5, scoring=custom_scorer)

# Or as string name
grid = GridSearchCV(clf, param_grid, cv=5, scoring='f1_macro')
```

### Scoring Function from Scratch

```python
from sklearn.metrics import _scorer

class MyScorer:
    def __init__(self, weight=None):
        self.weight = weight
    
    def __call__(self, model, X, y):
        y_pred = model.predict(X)
        # custom logic
        return np.mean(y_pred == y)

# Register as scorer
scorer = make_scorer(MyScorer(), greater_is_better=True)
```

## Permutation Test

```python
from sklearn.model_selection import permutation_test_score

score, perm_scores, pvalue = permutation_test_score(
    clf, X, y, n_permutations=1000, scoring='accuracy', random_state=42
)
print(f"Score: {score:.4f}, P-value: {pvalue:.4f}")
```

- Tests if model performance is significantly better than chance
- `n_permutations`: number of permutations for null distribution
- `pvalue < 0.05` indicates statistically significant performance

## Cross-Validation Considered Harmful

When to be cautious:
- **Time series data**: use TimeSeriesSplit instead
- **Grouped data**: use GroupKFold to prevent leakage
- **Imbalanced data**: use StratifiedKFold
- **Small datasets**: high variance in CV estimates; consider LOO
- **Pipeline with transformers**: ensure fit_transform is called on train only
- **Multiple testing**: many hyperparameter combinations inflate false positive rate
