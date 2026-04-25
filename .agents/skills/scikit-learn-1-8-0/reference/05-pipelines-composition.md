# Pipelines & Composition

## Pipeline

### Basic Pipeline

```python
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Method 1: explicit steps
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression())
])
pipe.fit(X_train, y_train)
predictions = pipe.predict(X_test)

# Method 2: convenience function (step names auto-generated)
pipe = make_pipeline(StandardScaler(), LogisticRegression())
```

**Benefits:**
- Prevents data leakage by fitting transformers only on training data
- Simplifies code and deployment
- Enables grid search over all pipeline steps
- Single object for saving/loading

### Accessing Pipeline Components

```python
# Get step by name
scaler_step = pipe.named_steps['standardscaler']
clf_step = pipe.named_steps['logisticregression']

# Or via attribute access
pipe.named_steps['standardscaler'].mean_
pipe[-1].coef_  # last step

# Set parameters on specific steps
pipe.set_params(logisticregression__C=10)

# Grid search over pipeline parameters
param_grid = {
    'standardscaler__with_mean': [True, False],
    'logisticregression__C': [0.1, 1, 10]
}
```

## ColumnTransformer

### Selecting Columns for Different Transformations

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

# Define numeric and categorical columns
numeric_cols = ['age', 'income', 'score']
categorical_cols = ['gender', 'city', 'category']

# Preprocess each type differently
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ],
    remainder='drop'  # or 'passthrough', or column indices
)

# Full pipeline
pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression())
])
pipe.fit(X_train, y_train)
```

### Using Function Transformers

```python
from sklearn.compose import ColumnTransformer
import numpy as np

def extract_day(x):
    return np.array([d.day for d in x])

def extract_month(x):
    return np.array([d.month for d in x])

ct = ColumnTransformer([
    ('day', extract_day, ['date']),
    ('month', extract_month, ['date']),
    ('other', 'passthrough', ['id', 'amount'])
], remainder='drop')
```

### Named Columns in Pipeline

```python
from sklearn.pipeline import FeatureUnion
from sklearn.compose import ColumnTransformer

# Use column names that reference pipeline outputs
ct = ColumnTransformer([
    ('num', StandardScaler(), numeric_cols),
    ('cat', OneHotEncoder(), categorical_cols)
], remainder='drop')

# Pass DataFrame to fit/predict; transformer keeps column names
pipe = Pipeline([('preprocess', ct), ('model', LogisticRegression())])
```

## FeatureUnion

### Parallel Feature Transformations

```python
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA

feature_union = FeatureUnion([
    ('scaler', StandardScaler()),
    ('minmax', MinMaxScaler()),
    ('pca', PCA(n_components=5))
])

X_combined = feature_union.fit_transform(X_train)
```

- Applies multiple transformers in parallel
- Concatenates results horizontally
- Less common than ColumnTransformer (which handles mixed column types)

## Custom Transformers

### Using Function as Transformer

```python
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class CustomScaler(BaseEstimator, TransformerMixin):
    def __init__(self, axis=0):
        self.axis = axis
    
    def fit(self, X, y=None):
        self.mean_ = X.mean(axis=self.axis)
        return self
    
    def transform(self, X):
        return (X - self.mean_) / (X.std(axis=self.axis) + 1e-8)

# Use in pipeline
pipe = Pipeline([
    ('custom', CustomScaler()),
    ('clf', LogisticRegression())
])
```

### Using Class with get_params/set_params

```python
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class PolynomialExpansion(BaseEstimator, TransformerMixin):
    def __init__(self, degree=2, columns=None):
        self.degree = degree
        self.columns = columns
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        if self.columns is not None:
            X_selected = X[:, self.columns]
        else:
            X_selected = X
        
        # Generate polynomial features
        from itertools import combinations_with_replacement
        features = [X_selected]
        for d in range(2, self.degree + 1):
            for combo in combinations_with_replacement(range(X_selected.shape[1]), d):
                prod = np.prod(X_selected[:, list(combo)], axis=1).reshape(-1, 1)
                features.append(prod)
        
        return np.hstack(features)
```

### Inherited from sklearn Transformer

```python
from sklearn.preprocessing import FunctionTransformer

# Wrap any function as a transformer
def add_column(x):
    return np.column_stack([x, np.ones(len(x))])

transformer = FunctionTransformer(add_column, validate=True)
```

## Voting Classifier / Regressor

### Hard Voting (Majority Rule)

```python
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

voting_clf = VotingClassifier(
    estimators=[
        ('lr', LogisticRegression()),
        ('dt', DecisionTreeClassifier()),
        ('svm', SVC())
    ],
    voting='hard'  # majority vote
)
voting_clf.fit(X_train, y_train)
```

### Soft Voting (Weighted Average of Probabilities)

```python
voting_clf = VotingClassifier(
    estimators=[
        ('lr', LogisticRegression()),
        ('svm', SVC(probability=True))  # needs probability=True
    ],
    voting='soft',  # average probabilities
    weights=[2, 1]   # optional: weight each classifier
)
```

### Voting Regressor

```python
from sklearn.ensemble import VotingRegressor

voting_reg = VotingRegressor([
    ('rf', RandomForestRegressor()),
    ('gb', GradientBoostingRegressor()),
    ('lr', LinearRegression())
])
```

## Stacking Classifier / Regressor

### Stacking with Meta-Estimator

```python
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

stacking_clf = StackingClassifier(
    estimators=[
        ('dt', DecisionTreeClassifier(max_depth=4)),
        ('svm', SVC(kernel='linear', probability=False))
    ],
    final_estimator=LogisticRegression(),
    cv=5,  # cross-validation for generating meta-features
    stack_method='predict_proba'  # or 'decision_function'
)
stacking_clf.fit(X_train, y_train)
```

- `stack_method`: method to use for stacking ('predict_proba', 'decision_function', 'predict')
- `final_estimator`: meta-learner that combines base predictions
- `cv`: number of folds for generating out-of-fold predictions
- `n_jobs`: parallelization

## Calibrated Classifier

### Probability Calibration

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import SVC

# Wrap any classifier with calibration
calibrated = CalibratedClassifierCV(
    SVC(probability=False),  # base classifier
    method='sigmoid',        # 'sigmoid' (Platt) or 'isotonic'
    cv=5
)
calibrated.fit(X_train, y_train)

# Now predict_proba gives well-calibrated probabilities
proba = calibrated.predict_proba(X_test)
```

- `method`: 'sigmoid' (Platt scaling, works with less data), 'isotonic' (more flexible)
- Uses cross-validation internally to avoid overfitting

## Ensemble Parallelization

### Joblib Backend for Ensembles

```python
from sklearn.ensemble import RandomForestClassifier

# Use multiple cores
rf = RandomForestClassifier(n_estimators=100, n_jobs=-1)  # all available cores
rf.fit(X_train, y_train)

# Or specify number of jobs
rf = RandomForestClassifier(n_estimators=100, n_jobs=4)
```

- `n_jobs`: -1 for all CPUs, 1 for single-threaded
- Applies to tree-based ensembles and some other estimators
- Speedup is typically near-linear for large forests

## Model Evaluation with Pipelines

```python
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Cross-validation automatically handles pipeline fitting
scores = cross_val_score(make_pipeline(StandardScaler(), SVC()), X, y, cv=5)

# Grid search over pipeline parameters
param_grid = {
    'standardscaler__with_mean': [True, False],
    'svc__C': [0.1, 1, 10],
    'svc__gamma': ['scale', 'auto']
}

grid = GridSearchCV(
    make_pipeline(StandardScaler(), SVC()),
    param_grid, cv=5, scoring='accuracy', n_jobs=-1
)
grid.fit(X_train, y_train)
```

**Important:** Always use pipelines to prevent data leakage when combining preprocessing with model training.
