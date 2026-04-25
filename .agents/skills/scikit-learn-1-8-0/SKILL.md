---
name: scikit-learn-1-8-0
description: Complete toolkit for scikit-learn 1.8.0 machine learning library covering supervised/unsupervised algorithms, pipelines, preprocessing, model selection, metrics, and datasets. Use when building ML models in Python, performing classification/regression/clustering, feature engineering, hyperparameter tuning, or evaluating model performance with scikit-learn 1.8+.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.8.0"
tags:
  - machine learning
  - classification
  - regression
  - clustering
  - preprocessing
  - model selection
  - metrics
category: ai-ml
external_references:
  - https://scikit-learn.org/stable/index.html
  - https://github.com/scikit-learn/scikit-learn
  - https://scikit-learn.org/stable/
  - https://scikit-learn.org/stable/auto_examples/release_highlights/plot_release_highlights_1_8_0.html
  - https://scikit-learn.org/stable/modules/classes.html
  - https://scikit-learn.org/stable/whats_new/v1.8.html
---

# scikit-learn 1.8.0

## Overview

Scikit-learn is an open-source machine learning library for Python that provides simple and efficient tools for data mining and data analysis. It supports supervised and unsupervised learning, along with various tools for model fitting, data preprocessing, model selection, model evaluation, and utilities. Built on NumPy, SciPy, and matplotlib, it features a range of classification, regression, clustering, and dimensionality reduction algorithms.

## When to Use

Use this skill when building Python machine learning applications requiring:
- Supervised learning (classification, regression) with linear models, SVMs, trees, ensembles, neural networks, naive Bayes
- Unsupervised learning (clustering, dimensionality reduction) with k-means, hierarchical clustering, DBSCAN, PCA
- Data preprocessing: scaling, encoding, imputation, feature extraction, polynomial features
- Model evaluation: cross-validation, metrics for classification/regression/clustering
- Hyperparameter tuning: GridSearchCV, RandomizedSearchCV, Bayesian optimization
- Pipelines: chaining transformers and estimators to prevent data leakage
- Text analytics: TF-IDF, CountVectorizer, hashing vectorizer
- Model persistence: saving/loading fitted models with joblib

## Core Concepts

### Estimator API

All machine learning objects in scikit-learn share a unified interface:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=1000, n_features=4, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize estimator
clf = RandomForestClassifier(n_estimators=100, random_state=42)

# Fit (train) the model
clf.fit(X_train, y_train)

# Predict on new data
predictions = clf.predict(X_test)

# Evaluate
accuracy = clf.score(X_test, y_test)
```

**Key methods:**
- `fit(X, y)` — Train the model. For unsupervised, only `X` is needed.
- `predict(X)` — Predict labels for new data (classification/regression).
- `predict_proba(X)` — Predict probability estimates (if supported).
- `transform(X)` — Transform data (for transformers).
- `score(X, y)` — Return mean score on given data (accuracy for classification, R² for regression).

**Data format:**
- `X`: samples matrix of shape `(n_samples, n_features)`, rows are samples, columns are features
- `y`: target values — real numbers for regression, integers for classification
- Both expected as NumPy arrays or array-like (pandas DataFrames, scipy sparse matrices)

### Transformers

Transformers follow the same API with `fit()` and `transform()` methods:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)  # fit on train, transform
X_test_scaled = scaler.transform(X_test)  # only transform test data
```

### Pipelines

Pipelines chain multiple steps (transformers + final estimator) into a single object:

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression

# Numeric features pipeline
numeric_transformer = StandardScaler()

# Categorical features pipeline
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

# Combine preprocessors
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_columns),
        ('cat', categorical_transformer, categorical_columns)
    ])

# Full pipeline
pipe = make_pipeline(preprocessor, LogisticRegression())
pipe.fit(X_train, y_train)
```

**Benefits:** Prevents data leakage, simplifies deployment, enables grid search over all steps.

### Model Selection

```python
from sklearn.model_selection import GridSearchCV, cross_val_score, learning_curve
from sklearn.svm import SVC

param_grid = {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear']}
grid = GridSearchCV(SVC(), param_grid, cv=5, scoring='accuracy')
grid.fit(X_train, y_train)

print(f"Best params: {grid.best_params_}")
print(f"Best score: {grid.best_score_:.4f}")
```

## Installation / Setup

```bash
# Via pip (recommended)
pip install scikit-learn

# Via conda
conda install -c conda-forge scikit-learn

# Verify installation
python -c "import sklearn; print(sklearn.__version__)"  # Should print 1.8.0
```

**Requirements:** Python >= 3.10, NumPy >= 1.25, SciPy >= 1.11.

## Quick Reference by Task

### Classification
- **Linear models:** `LogisticRegression`, `SGDClassifier`, `LinearSVC`
- **Tree-based:** `DecisionTreeClassifier`, `RandomForestClassifier`, `GradientBoostingClassifier`, `HistGradientBoostingClassifier`
- **Nearest neighbors:** `KNeighborsClassifier`, `RadiusNeighborsClassifier`
- **Naive Bayes:** `BernoulliNB`, `MultinomialNB`, `GaussianNB`, `ComplementNB`
- **SVM:** `SVC`, `NuSVC`, `LinearSVC`
- **Neural networks:** `MLPClassifier`
- **Ensembles (voting/stacking):** `VotingClassifier`, `StackingClassifier`

### Regression
- **Linear models:** `LinearRegression`, `Ridge`, `Lasso`, `ElasticNet`, `SGDRegressor`
- **Tree-based:** `DecisionTreeRegressor`, `RandomForestRegressor`, `GradientBoostingRegressor`, `HistGradientBoostingRegressor`
- **Nearest neighbors:** `KNeighborsRegressor`, `RadiusNeighborsRegressor`
- **SVM:** `SVR`, `NuSVR`, `LinearSVR`
- **Neural networks:** `MLPRegressor`
- **Ensembles (voting/stacking):** `VotingRegressor`, `StackingRegressor`

### Clustering
- **Centroid-based:** `KMeans`, `MiniBatchKMeans`
- **Hierarchical:** `AgglomerativeClustering`, `FeatureAgglomeration`
- **Density-based:** `DBSCAN`, `OPTICS`
- **Other:** `SpectralClustering`, `AffinityPropagation`, `MeanShift`
- **Mixture models:** `GaussianMixture`, `BiclusterKMeans`

### Dimensionality Reduction
- **Linear:** `PCA`, `IncrementalPCA`, `RandomizedPCA`, `TruncatedSVD`, `KernelPCA`
- **Manifold learning:** `TSNE`, `Isomap`, `LocallyLinearEmbedding`, `MDS`
- **Feature selection:** `SelectKBest`, `RFE`, `SequentialFeatureSelector`
- **Decomposition:** `NMF`, `FactorAnalysis`, `DictionaryLearning`, `SparsePCA`

### Preprocessing
- **Scaling:** `StandardScaler`, `MinMaxScaler`, `MaxAbsScaler`, `RobustScaler`, `Normalizer`
- **Imputation:** `SimpleImputer`, `KNNImputer`, `IterativeImputer`
- **Encoding:** `OneHotEncoder`, `OrdinalEncoder`, `TargetEncoder`
- **Binning:** `KBinsDiscretizer`
- **Polynomial features:** `PolynomialFeatures`
- **Text:** `CountVectorizer`, `TfidfVectorizer`, `HashingVectorizer`

## Advanced Topics

For detailed coverage of specific topics, see the reference files:

- **[1. Supervised Learning Algorithms](references/01-supervised-learning.md)** — Linear models, SVMs, trees, ensembles, neural networks, naive Bayes
- **[2. Unsupervised Learning & Dimensionality Reduction](references/02-unsupervised-learning.md)** — Clustering algorithms, PCA, manifold learning, decomposition
- **[3. Data Preprocessing & Feature Engineering](references/03-preprocessing.md)** — Scaling, encoding, imputation, text features, column transformers
- **[4. Model Evaluation & Selection](references/04-model-evaluation-selection.md)** — Cross-validation, metrics, hyperparameter tuning, learning curves
- **[5. Pipelines & Composition](references/05-pipelines-composition.md)** — Pipeline, ColumnTransformer, feature union, custom transformers
- **[6. Text Analytics & Feature Extraction](references/06-text-analytics.md)** — Vectorization, TF-IDF, n-grams, document-term matrices
- **[7. Key Examples & Workflows](references/07-key-examples.md)** — Complete end-to-end workflows, common patterns

