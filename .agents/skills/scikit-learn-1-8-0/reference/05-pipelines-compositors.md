# Pipelines and Compositors

## Pipeline

Chain transformers and an estimator into a single object:

```python
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC

# Explicit constructor
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("pca", PCA(n_components=0.95)),
    ("svm", SVC()),
])

# Shorthand with make_pipeline (auto-generates step names)
pipe = make_pipeline(StandardScaler(), PCA(n_components=0.95), SVC())

pipe.fit(X_train, y_train)
predictions = pipe.predict(X_test)
```

Key benefits:
- Prevents data leakage — preprocessing is fit only on training folds during cross-validation
- Single `fit`/`predict` call for the entire workflow
- Access individual steps: `pipe.named_steps["scaler"]` or `pipe["svm"]`
- Grid search over pipeline parameters: `param_grid = {"svm__C": [0.1, 1, 10], "pca__n_components": [0.9, 0.95]}`

### Caching Transformers

Cache fitted transformers to avoid recomputation:

```python
from joblib import Memory
memory = Memory(location="/tmp/sklearn_cache", verbose=0)
pipe = Pipeline([...], memory=memory)
```

## ColumnTransformer

Apply different transformations to different columns:

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

preprocessor = ColumnTransformer(
    transformers=[
        ("num_scaler", StandardScaler(), ["age", "income"]),
        ("cat_encoder", OneHotEncoder(handle_unknown="ignore"), ["city", "category"]),
        ("imputer", SimpleImputer(strategy="median"), ["missing_col"]),
    ],
    remainder="passthrough",  # or "drop"
)

# Combine with estimator in a Pipeline
pipe = make_pipeline(preprocessor, RandomForestClassifier())
pipe.fit(X, y)
```

- `remainder="passthrough"` keeps unlisted columns as-is
- `remainder="drop"` removes unlisted columns
- Use column indices (integers) or names (strings)

## FeatureUnion

Combine multiple transformers into one:

```python
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

union = FeatureUnion([
    ("poly", PolynomialFeatures(degree=2)),
    ("scaled", StandardScaler()),
])
X_combined = union.fit_transform(X)
```

## FrozenEstimator

Freeze an estimator's parameters to prevent them from being modified:

```python
from sklearn.utils.metaestimators import FrozenEstimator
from sklearn.linear_model import LogisticRegression

frozen = FrozenEstimator(LogisticRegression(C=1.0))
# Cannot modify C after freezing
```

Useful for preventing accidental parameter changes in pipelines or when sharing models.

## Metadata Routing

Enable passing additional arguments (like `sample_weight`) through pipelines:

```python
import sklearn
sklearn.set_config(enable_metadata_routing=True)

pipe = make_pipeline(StandardScaler(), LogisticRegression())
pipe.set_fit_request(sample_weight=True)

# Now sample_weight flows through the pipeline
pipe.fit(X, y, sample_weight=weights)
```

Version 1.8: Fixed issue where passing `sample_weight` to a Pipeline inside `GridSearchCV` raised an error with metadata routing enabled.

## Model Persistence

Save and load fitted models:

```python
import joblib

# Save
joblib.dump(pipe, "model.joblib")

# Load
loaded_pipe = joblib.load("model.joblib")
predictions = loaded_pipe.predict(X_new)
```

Alternatively with `pickle` (not recommended for untrusted data):

```python
import pickle
with open("model.pkl", "wb") as f:
    pickle.dump(pipe, f)
```

## HTML Representation

In Jupyter notebooks, estimators display an interactive HTML representation showing:
- Pipeline structure with expandable steps
- Parameter values (user-set in orange, defaults in black)
- Links to online documentation
- Tooltips with parameter descriptions

Version 1.8: HTML representation now shows parameter descriptions as tooltips and includes links to online documentation for each parameter. Fixed handling of pandas missing values in display.
