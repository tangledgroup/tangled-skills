# Preprocessing and Feature Engineering

## Scaling

### StandardScaler

Centers data to zero mean and unit variance:

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_back = scaler.inverse_transform(X_scaled)
```

Version 1.8: Now supports Array API compliant inputs.

### MinMaxScaler

Scales to a fixed range (default [0, 1]):

```python
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)
```

### MaxAbsScaler

Scales to [-1, 1] based on max absolute value. Ideal for sparse data:

```python
from sklearn.preprocessing import MaxAbsScaler
scaler = MaxAbsScaler()
X_scaled = scaler.fit_transform(X)
```

Version 1.8: New `clip` parameter to clip out-of-range values in held-out data.

### RobustScaler

Uses median and IQR — robust to outliers:

```python
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)
```

### Normalizer

Normalizes samples to unit norm (L1, L2, max):

```python
from sklearn.preprocessing import Normalizer
normalizer = Normalizer(norm="l2")
X_normalized = normalizer.fit_transform(X)
```

## Encoding Categorical Variables

### OneHotEncoder

Converts categorical features to binary vectors:

```python
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
X_encoded = encoder.fit_transform([["male"], ["female"], ["other"]])
```

Version 1.8: Fixed bug where `handle_unknown='warn'` incorrectly behaved like `'ignore'` instead of `'infrequent_if_exist'`.

### OrdinalEncoder

Encodes categorical features as integers:

```python
from sklearn.preprocessing import OrdinalEncoder
encoder = OrdinalEncoder()
X_encoded = encoder.fit_transform([["low"], ["medium"], ["high"]])
```

### LabelEncoder

Encodes target labels as integers (use only for y, not X):

```python
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_int = le.fit_transform(["cat", "dog", "cat"])
labels = le.classes_  # ['cat', 'dog']
```

### LabelBinarizer

Binary encoding of labels:

```python
from sklearn.preprocessing import LabelBinarizer
lb = LabelBinarizer()
y_binary = lb.fit_transform(["cat", "dog", "cat"])
```

Version 1.8: Now supports numeric Array API compatible inputs with `sparse_output=False`.

## Imputation of Missing Values

### SimpleImputer

Replace missing values with mean, median, or constant:

```python
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy="median")
X_imputed = imputer.fit_transform(X_with_nans)
```

Strategies: `"mean"`, `"median"`, `"most_frequent"`, `"constant"`.

### KNNImputer

Impute using k-nearest neighbors:

```python
from sklearn.impute import KNNImputer
imputer = KNNImputer(n_neighbors=5)
X_imputed = imputer.fit_transform(X_with_nans)
```

### IterativeImputer

Models each feature as a function of other features (MICE algorithm):

```python
from sklearn.impute import IterativeImputer
imputer = IterativeImputer(random_state=0)
X_imputed = imputer.fit_transform(X_with_nans)
```

## Nonlinear Transformations

### PowerTransformer

Transforms features toward normality:

```python
from sklearn.preprocessing import PowerTransformer
pt = PowerTransformer(method="yeo-johnson", standardize=True)
X_transformed = pt.fit_transform(X)
```

Methods: `"yeo-johnson"` (handles negative values), `"box-cox"` (positive only).

Version 1.8: Now returns a warning when NaN values are encountered in `inverse_transform`.

### QuantileTransformer

Transforms features using quantile information:

```python
from sklearn.preprocessing import QuantileTransformer
qt = QuantileTransformer(output_distribution="normal", n_quantiles=1000)
X_transformed = qt.fit_transform(X)
```

Output distributions: `"uniform"`, `"normal"`.

### Binarizer

Threshold features to binary values:

```python
from sklearn.preprocessing import Binarizer
binarizer = Binarizer(threshold=0.0)
X_binary = binarizer.transform(X)
```

## Polynomial and Spline Features

### PolynomialFeatures

Generate polynomial and interaction features:

```python
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
```

Version 1.8: Now supports Array API compatible inputs.

### SplineTransformer

Transforms features into spline bases:

```python
from sklearn.preprocessing import SplineTransformer
spline = SplineTransformer(n_knots=5, degree=3)
X_spline = spline.fit_transform(X)
```

Version 1.8: New `handle_missing` parameter to handle missing values.

## Feature Selection

### VarianceThreshold

Remove features with low variance:

```python
from sklearn.feature_selection import VarianceThreshold
selector = VarianceThreshold(threshold=0.1)
X_selected = selector.fit_transform(X)
```

### SelectKBest / SelectPercentile

Select top k features or a percentile based on statistical tests:

```python
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(score_func=f_classif, k=10)
X_selected = selector.fit_transform(X, y)
# For regression: f_regression, mutual_info_regression
# For classification: chi2, mutual_info_classif
```

### RFE (Recursive Feature Elimination)

Recursively removes least important features:

```python
from sklearn.feature_selection import RFE
selector = RFE(estimator=LogisticRegression(), n_features_to_select=5)
X_selected = selector.fit_transform(X, y)
support_mask = selector.support_
ranking = selector.ranking_
```

### SelectFromModel

Select features based on model weights/importances:

```python
from sklearn.feature_selection import SelectFromModel
selector = SelectFromModel(
    estimator=RandomForestClassifier(), threshold="median"
)
X_selected = selector.fit_transform(X, y)
```

Version 1.8: `SelectFromModel` no longer forces `max_features` to be less than or equal to the number of input features.

### Mutual Information

```python
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
scores = mutual_info_classif(X, y)
```

## Text Feature Extraction

### CountVectorizer / TfidfVectorizer

Convert text documents to feature vectors:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
X_tfidf = vectorizer.fit_transform(documents)
```

## Image Feature Extraction

```python
from sklearn.feature_extraction.image import extract_patches_2d, reconstruct_from_patches_2d
patches = extract_patches_2d(image, patch_size=(6, 6))
reconstructed = reconstruct_from_patches_2d(patches, image.shape)
```

## ColumnTransformer

Apply different transformations to different columns:

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_columns),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ("imp", SimpleImputer(strategy="median"), columns_with_missing),
    ]
)
X_processed = preprocessor.fit_transform(X)
```

Version 1.8: `ColumnTransformer` now correctly fits on data provided as a polars.DataFrame when any transformer has sparse output.
