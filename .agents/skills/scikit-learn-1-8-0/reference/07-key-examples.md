# Key Examples & Workflows

## Complete Classification Workflow

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_curve, auc, accuracy_score)

# 1. Load/generate data
X, y = make_classification(n_samples=1000, n_features=20, n_classes=2,
                           random_state=42)

# 2. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 3. Build pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(random_state=42))
])

# 4. Hyperparameter tuning
param_grid = {
    'clf__n_estimators': [50, 100, 200],
    'clf__max_depth': [None, 10, 20],
    'clf__min_samples_split': [2, 5, 10]
}

grid = GridSearchCV(pipe, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid.fit(X_train, y_train)

print(f"Best params: {grid.best_params_}")
print(f"Best CV score: {grid.best_score_:.4f}")

# 5. Evaluate
y_pred = grid.predict(X_test)
y_proba = grid.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

# 6. Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"Confusion Matrix:\n{cm}")

# 7. ROC curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)
print(f"ROC AUC: {roc_auc:.4f}")
```

## Complete Regression Workflow

```python
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# 1. Generate data
X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)

# 2. Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('reg', GradientBoostingRegressor(random_state=42))
])

# 4. Cross-validation
cv_scores = cross_val_score(pipe, X, y, cv=5, scoring='r2')
print(f"CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# 5. Fit and evaluate
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

print(f"R²: {r2_score(y_test, y_pred):.4f}")
print(f"MSE: {mean_squared_error(y_test, y_pred):.4f}")
print(f"MAE: {mean_absolute_error(y_test, y_pred):.4f}")
```

## Multi-Class Classification

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report

# Load multi-class data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', SVC(kernel='rbf', probability=True, random_state=42))
])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

print(classification_report(y_test, y_pred, target_names=load_iris().target_names))
```

## Handling Imbalanced Data

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score

# Generate imbalanced data
X, y = make_classification(n_samples=1000, weights=[0.95, 0.05], random_state=42)

# Method 1: class_weight
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(class_weight='balanced', random_state=42))
])

# Method 2: SMOTE (requires imbalanced-learn)
# from imblearn.pipeline import Pipeline as ImbPipeline
# from imblearn.over_sampling import SMOTE
# pipe = ImbPipeline([
#     ('smote', SMOTE(random_state=42)),
#     ('clf', RandomForestClassifier(random_state=42))
# ])

pipe.fit(*train_test_split(X, y, test_size=0.2, random_state=42))
y_pred = pipe.predict(pipe[:-1][-1].named_steps['scaler'].transform(
    train_test_split(X, y, test_size=0.2, random_state=42)[0]))
```

## Working with Mixed Data Types

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

# Sample mixed data
df = pd.DataFrame({
    'age': [25, 30, None, 45, 35],
    'income': [50000, 60000, 70000, None, 80000],
    'gender': ['M', 'F', 'F', 'M', 'M'],
    'city': ['NYC', 'LA', 'NYC', 'LA', 'Chicago'],
    'target': [0, 1, 0, 1, 0]
})

numeric_cols = ['age', 'income']
categorical_cols = ['gender', 'city']

# Preprocessor
numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_cols),
        ('cat', categorical_transformer, categorical_cols)
    ]
)

# Full pipeline
pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('clf', RandomForestClassifier(random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(
    df.drop('target', axis=1), df['target'], test_size=0.2, random_state=42
)
pipe.fit(X_train, y_train)
print(f"Score: {pipe.score(X_test, y_test):.4f}")
```

## Model Comparison

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import pandas as pd

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = {
    'LogisticRegression': Pipeline([('scaler', StandardScaler()),
                                     ('clf', LogisticRegression())]),
    'RandomForest': RandomForestClassifier(random_state=42),
    'GradientBoosting': GradientBoostingClassifier(random_state=42),
    'SVM': Pipeline([('scaler', StandardScaler()),
                      ('clf', SVC())])
}

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    results[name] = score
    print(f"{name:25s}: {score:.4f}")

# Summary as DataFrame
pd.DataFrame(results, index=['Test Accuracy']).T.sort_values(0, ascending=False)
```

## Time Series Forecasting

```python
from sklearn.linear_model import LinearRegression
import numpy as np

# Simple time series with features
np.random.seed(42)
n = 100
X = np.arange(n).reshape(-1, 1)
y = 2 * np.sin(2 * np.pi * n / 20) + np.random.randn(n) * 0.1

# Create lag features
def create_lag_features(y, lags=5):
    X_lagged = []
    for lag in range(1, lags + 1):
        X_lagged.append(y[:-lag])
    return np.column_stack(X_lagged), y[lags:]

X_lagged, y_reduced = create_lag_features(y, lags=5)
X_train, X_test = X_lagged[:80], X_lagged[80:]
y_train, y_test = y_reduced[:80], y_reduced[80:]

model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
print(f"MAE: {np.mean(np.abs(predictions - y_test)):.4f}")
```

## Feature Importance Analysis

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import matplotlib.pyplot as plt

X, y = make_classification(n_samples=1000, n_features=20, n_informative=5,
                           random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# Feature importances
importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]

print("Feature ranking:")
for i in indices[:10]:
    print(f"  {i}: {importances[i]:.4f}")

# Plot
plt.figure(figsize=(10, 6))
plt.bar(range(10), importances[indices[:10]])
plt.xticks(range(10), [f"F{i}" for i in indices[:10]])
plt.title("Top 10 Feature Importances")
plt.show()
```

## Partial Dependence Plots

```python
from sklearn.inspection import PartialDependenceDisplay
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=500, n_features=10, random_state=42)
clf = GradientBoostingClassifier(n_estimators=50, random_state=42)
clf.fit(X, y)

# Single feature PDP
PartialDependenceDisplay.from_estimator(clf, X, features=[0])

# Two-way interaction
PartialDependenceDisplay.from_estimator(clf, X, features=[(0, 1)])
```

## Saving and Loading Pipelines

```python
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Save
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(random_state=42))
])
pipe.fit(X_train, y_train)
joblib.dump(pipe, 'ml_pipeline.pkl')

# Load and use
loaded_pipe = joblib.load('ml_pipeline.pkl')
predictions = loaded_pipe.predict(X_new)
```

## Array API Support (v1.8)

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, roc_curve
from sklearn.model_selection import cross_val_predict

# Many estimators now support Array API compliant inputs
X = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.float64)
y = np.array([0, 1, 0])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

conf_mat = confusion_matrix(y, y_pred)
roc_curve_vals = roc_curve(y, y_scores)
cv_preds = cross_val_predict(estimator, X, y)
```

v1.8 Array API support: StandardScaler, RidgeCV/RidgeClassifier with 'svd' solver, pairwise_kernels, pairwise_distances, confusion_matrix, roc_curve, precision_recall_curve, BrierScoreLoss, log_loss, d2_brier_score, CalibratedClassifierCV (method='temperature'), PolynomialFeatures, cross_val_predict
