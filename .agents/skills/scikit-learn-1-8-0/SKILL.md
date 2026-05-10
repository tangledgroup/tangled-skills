---
name: scikit-learn-1-8-0
description: Complete scikit-learn 1.8 toolkit for machine learning covering supervised and unsupervised algorithms, pipelines, preprocessing, model selection, metrics, and datasets. Use when building ML models in Python, performing classification/regression/clustering, feature engineering, hyperparameter tuning, or evaluating model performance with scikit-learn 1.8+.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - machine-learning
  - classification
  - regression
  - clustering
  - pipelines
  - model-selection
category: data-science
external_references:
  - https://scikit-learn.org/stable/index.html
  - https://github.com/scikit-learn/scikit-learn
  - https://scikit-learn.org/stable/auto_examples/release_highlights/plot_release_highlights_1_8_0.html
  - https://scikit-learn.org/stable/modules/classes.html
  - https://scikit-learn.org/stable/whats_new/v1.8.html
---

# scikit-learn 1.8.0

## Overview

Scikit-learn is the most widely used open-source machine learning library for Python. It provides simple and efficient tools for predictive data analysis, accessible to everybody and reusable in various contexts. Built on NumPy, SciPy, and matplotlib, it is released under the BSD license.

Version 1.8.0 (December 2025) brings free-threaded CPython 3.14 support, major manifold learning improvements with ClassicalMDS and enhanced MDS/TSNE, temperature scaling for probability calibration, significant efficiency gains in linear models via gap safe screening rules, expanded Array API support across 20+ estimators and functions, and numerous bug fixes across the entire codebase.

## When to Use

- Building supervised ML models (classification, regression) with algorithms like SVMs, random forests, gradient boosting, or logistic regression
- Unsupervised learning tasks: clustering (KMeans, DBSCAN, HDBSCAN), dimensionality reduction (PCA, MDS, t-SNE), or density estimation
- Feature engineering and preprocessing: scaling, encoding, imputation, polynomial features, spline transformation
- Model selection via cross-validation, grid search, or random search
- Evaluating models with comprehensive metrics: accuracy, precision/recall, ROC curves, confusion matrices, clustering scores
- Building reproducible ML pipelines that chain preprocessing and modeling steps
- Working with built-in datasets (iris, digits, wine) or generated data

## Core Concepts

### Estimators

Every machine learning algorithm in scikit-learn is an *estimator*. All estimators share a common API:

- `fit(X, y)` — train the model on data. For unsupervised learning, call `fit(X)` without `y`.
- `predict(X)` — predict target values for new data (supervised estimators only).
- `predict_proba(X)` — predict class probabilities (classifiers that support it).
- `score(X, y)` — return evaluation score (accuracy for classifiers, R² for regressors).

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
clf = RandomForestClassifier(random_state=0)
clf.fit(X, y)
predictions = clf.predict(X)
accuracy = clf.score(X, y)  # 1.0 for training data
```

### Transformers

Transformers preprocess data and follow the same API plus a `transform` method:

- `fit(X)` — learn parameters from data (e.g., mean/std for StandardScaler).
- `transform(X)` — apply transformation using learned parameters.
- `fit_transform(X)` — fit then transform in one step (often more efficient).

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### Pipelines

Pipelines chain transformers and a final estimator into a single object, preventing data leakage:

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe = make_pipeline(StandardScaler(), LogisticRegression())
pipe.fit(X_train, y_train)
predictions = pipe.predict(X_test)
```

### Model Selection

Cross-validation and hyperparameter tuning are central to scikit-learn:

- `cross_val_score` — quick evaluation across multiple splits.
- `GridSearchCV` — exhaustive search over a parameter grid.
- `RandomizedSearchCV` — random sampling from parameter distributions.
- Splitting strategies: `train_test_split`, `KFold`, `StratifiedKFold`, `GroupKFold`.

### Datasets

Built-in datasets for quick prototyping:

- Toy: `load_iris`, `load_digits`, `load_wine`, `load_breast_cancer`
- Generated: `make_classification`, `make_regression`, `make_blobs`
- Real-world: `fetch_openml`, `fetch_20newsgroups`, `fetch_california_housing`

## Installation / Setup

Install via pip (recommended with virtual environment):

```bash
python -m venv sklearn-env
source sklearn-env/bin/activate
pip install -U scikit-learn
```

Or via conda:

```bash
conda create -n sklearn-env -c conda-forge scikit-learn
conda activate sklearn-env
```

Verify installation:

```python
import sklearn
sklearn.show_versions()
```

**Requirements:** Python 3.10+, NumPy >= 1.24.0, SciPy >= 1.8.0, joblib >= 1.3.0, threadpoolctl >= 3.1.0. Version 1.8 adds free-threaded CPython 3.14 support with pre-built wheels for all supported platforms.

## Usage Examples

### Classification Pipeline

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

pipe = make_pipeline(StandardScaler(), SVC(probability=True))
pipe.fit(X_train, y_train)
print(classification_report(y_test, pipe.predict(X_test)))
```

### Hyperparameter Tuning with GridSearchCV

```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 5],
}
grid = GridSearchCV(RandomForestClassifier(random_state=0), param_grid, cv=5)
grid.fit(X_train, y_train)
print(f"Best params: {grid.best_params_}")
print(f"Best score: {grid.best_score_:.4f}")
```

### Clustering with KMeans

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=300, centers=4, random_state=0)
kmeans = KMeans(n_clusters=4, random_state=0)
labels = kmeans.fit_predict(X)
```

### Dimensionality Reduction with PCA

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
```

## Advanced Topics

**Supervised Learning**: Linear models, SVMs, nearest neighbors, Gaussian processes, decision trees, ensemble methods (random forests, gradient boosting, bagging, stacking) → [Supervised Learning](reference/01-supervised-learning.md)

**Unsupervised Learning**: Clustering algorithms, Gaussian mixture models, manifold learning (MDS, t-SNE), decomposition (PCA, ICA, NMF), covariance estimation, outlier detection → [Unsupervised Learning](reference/02-unsupervised-learning.md)

**Preprocessing and Feature Engineering**: Scaling, encoding, imputation, polynomial/spline features, feature selection, missing value handling → [Preprocessing and Features](reference/03-preprocessing-features.md)

**Model Selection and Evaluation**: Cross-validation strategies, hyperparameter tuning, metrics (classification, regression, clustering), scoring functions → [Model Selection and Metrics](reference/04-model-selection-metrics.md)

**Pipelines and Compositors**: Pipeline API, ColumnTransformer, FeatureUnion, FrozenEstimator, metadata routing → [Pipelines and Compositors](reference/05-pipelines-compositors.md)

**Version 1.8 Highlights**: Free-threaded CPython 3.14 support, ClassicalMDS, temperature scaling, gap safe screening in linear models, Array API expansion, API changes and deprecations → [Version 1.8 New Features](reference/06-version-1-8-highlights.md)
