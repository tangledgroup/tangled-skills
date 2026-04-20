# Data Preprocessing & Feature Engineering

## Scaling

### StandardScaler (Zero Mean, Unit Variance)

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Attributes after fit:
print(scaler.mean_)   # mean of each feature
print(scaler.scale_)  # standard deviation of each feature
```

- Most common scaling; assumes Gaussian distribution
- `with_mean=False` or `with_std=False` to disable centering/scaling
- Works with sparse data (only scales, doesn't center)

### MinMaxScaler (Scale to [0, 1] range)

```python
from sklearn.preprocessing import MinMaxScaler

minmax = MinMaxScaler(feature_range=(0, 1))
X_scaled = minmax.fit_transform(X_train)
```

- `feature_range`: tuple (default (0, 1))
- Scales to: (X - X.min()) / (X.max() - X.min()) * (max - min) + min
- Sensitive to outliers

### MaxAbsScaler (Scale to [-1, 1])

```python
from sklearn.preprocessing import MaxAbsScaler

maxabs = MaxAbsScaler()
X_scaled = maxabs.fit_transform(X_train)
```

- Divides by maximum absolute value
- Preserves sparsity; good for sparse data
- Scales to range based on max absolute value

### RobustScaler (Robust to Outliers)

```python
from sklearn.preprocessing import RobustScaler

robust = RobustScaler(with_centering=True, with_scaling=True)
X_scaled = robust.fit_transform(X_train)
```

- Uses median and IQR instead of mean/std
- `quantile_range`: tuple for custom quantiles (default (25.0, 75.0))
- Best when data contains outliers

### Normalizer (Scale samples to unit norm)

```python
from sklearn.preprocessing import Normalizer

normalizer = Normalizer(norm='l2')
X_normalized = normalizer.fit_transform(X_train)
```

- Scales each **sample** (row), not each feature
- `norm`: 'l1', 'l2', 'max'
- Used for text classification or cosine similarity

### QuantileTransformer

```python
from sklearn.preprocessing import QuantileTransformer

qt = QuantileTransformer(output_distribution='uniform', random_state=42)
X_transformed = qt.fit_transform(X_train)
```

- Maps features to uniform or normal distribution
- `output_distribution`: 'uniform' (default), 'normal'
- Robust to outliers; makes data Gaussian-like

### PowerTransformer

```python
from sklearn.preprocessing import PowerTransformer

pt = PowerTransformer(method='yeo-johnson', standardize=True)
X_transformed = pt.fit_transform(X_train)
```

- `method`: 'yeo-johnson' (handles negative values), 'box-cox' (positive only)
- Makes data more Gaussian-like using power transformations

## Imputation

### SimpleImputer

```python
from sklearn.impute import SimpleImputer

# Mean imputation for numeric
mean_imp = SimpleImputer(strategy='mean')
X_imputed = mean_imp.fit_transform(X_train)

# Most frequent for categorical
mode_imp = SimpleImputer(strategy='most_frequent')

# Constant value
const_imp = SimpleImputer(strategy='constant', fill_value=-999)
```

- `strategy`: 'mean', 'median', 'most_frequent', 'constant'
- `fill_value`: used with strategy='constant'
- Supports `missing_values` parameter (default NaN)

### KNN Imputer

```python
from sklearn.impute import KNNImputer

knn_imp = KNNImputer(n_neighbors=5, weights='uniform')
X_imputed = knn_imp.fit_transform(X_train)
```

- Uses k nearest neighbors to impute missing values
- `n_neighbors`: number of neighbors (default 5)
- `weights`: 'uniform' or 'distance'
- More accurate than mean/mode but slower

### Iterative Imputer

```python
from sklearn.impute import IterativeImputer

iter_imp = IterativeImputer(max_iter=10, random_state=42)
X_imputed = iter_imp.fit_transform(X_train)
```

- Models each feature with missing values as regression on other features
- `max_iter`: maximum iterations (default 10)
- Can be slow for large datasets

## Encoding Categorical Features

### OneHotEncoder

```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = encoder.fit_transform(X_train)

# Get feature names
feature_names = encoder.get_feature_names_out(['color', 'size'])
print(feature_names)
# ['color_blue' 'color_green' 'color_red' 'size_L' 'size_M']
```

- `sparse_output`: False for dense array (default True in older versions)
- `handle_unknown`: 'ignore' or 'error'
- `categories`: specify known categories manually
- Creates binary columns per category

### OrdinalEncoder

```python
from sklearn.preprocessing import OrdinalEncoder

encoder = OrdinalEncoder(categories=[['small', 'medium', 'large']])
X_encoded = encoder.fit_transform(X_train)
```

- Assigns integer codes to categories
- Use when order matters (ordinal data)
- `categories`: list of known categories per feature

### TargetEncoder (for high cardinality)

```python
from sklearn.preprocessing import TargetEncoder

te = TargetEncoder(categories='auto', target_type='binary')
X_encoded = te.fit_transform(X_train, y_train)
```

- Replaces category with mean of target variable
- Good for high-cardinality categorical features
- `target_type`: 'binary' (classification) or 'continuous' (regression)
- Use cross-validation to avoid overfitting

## Binning / Discretization

### KBinsDiscretizer

```python
from sklearn.preprocessing import KBinsDiscretizer

kb = KBinsDiscretizer(n_bins=5, strategy='uniform', encode='onehot')
X_binned = kb.fit_transform(X_train)
```

- `n_bins`: number of bins per feature (default 5)
- `strategy`: 'uniform' (equal-width), 'quantile' (equal-frequency), 'kmeans'
- `encode`: 'onehot', 'ordinal', 'onehot-dense'

### Binarizer

```python
from sklearn.preprocessing import Binarizer

binarizer = Binarizer(threshold=0.0)
X_binarized = binarizer.fit_transform(X_train)
```

- Converts to binary (0/1) based on threshold
- Values >= threshold become 1, else 0

## Polynomial Features

```python
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)
X_poly = poly.fit_transform(X_train)
# Creates: x1, x2, x1², x1*x2, x2² for 2 features
```

- `degree`: polynomial degree (default 2)
- `interaction_only`: True to only create interaction terms (x1*x2, not x1²)
- `include_bias`: add column of ones (default True, deprecated in 1.8)

## Feature Selection

### SelectKBest

```python
from sklearn.feature_selection import SelectKBest, f_classif

selector = SelectKBest(score_func=f_classif, k=10)
X_selected = selector.fit_transform(X_train, y_train)
# Get selected mask
print(selector.get_support())
# Get feature scores
print(selector.scores_)
```

- `score_func`: scoring function ('f_classif', 'mutual_info_classif', etc.)
- `k`: number of top features to select (or 'all', or float for percentile)

### RFE (Recursive Feature Elimination)

```python
from sklearn.feature_selection import RFE
from sklearn.svm import SVC

rfe = RFE(estimator=SVC(kernel='linear'), n_features_to_select=5, step=1)
X_selected = rfe.fit_transform(X_train, y_train)
print(rfe.support_)       # mask of selected features
print(rfe.ranking_)       # ranking of each feature
```

- Recursively removes weakest features
- `n_features_to_select`: number to keep
- `step`: fraction or number of features to remove per iteration

### Sequential Feature Selection

```python
from sklearn.feature_selection import SequentialFeatureSelector

sfs = SequentialFeatureSelector(LogisticRegression(), n_features_to_select=5, direction='forward')
X_selected = sfs.fit_transform(X_train, y_train)
```

- `direction`: 'forward' (add features) or 'backward' (remove features)
- More thorough than SelectKBest but slower

### VarianceThreshold

```python
from sklearn.feature_selection import VarianceThreshold

vt = VarianceThreshold(threshold=0.1)
X_selected = vt.fit_transform(X_train)
```

- Removes features with low variance
- `threshold`: minimum variance (default 0)
- Binary features with p > 1 - threshold or p < threshold are removed

## Array API Support (v1.8 New)

scikit-learn 1.8 adds experimental support for Array API compliant inputs:

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, roc_curve
from sklearn.model_selection import cross_val_predict

# Many estimators now support array API inputs
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # works with array API arrays

conf_mat = confusion_matrix(y_true, y_pred)  # array API compatible
roc = roc_curve(y_true, y_scores)              # array API compatible
cv_preds = cross_val_predict(estimator, X, y)  # array API compatible
```

Supported in v1.8: StandardScaler, RidgeCV/RidgeClassifier with 'svd', pairwise_kernels, pairwise_distances, confusion_matrix, roc_curve, precision_recall_curve, BrierScoreLoss, log_loss, d2_brier_score, CalibratedClassifierCV (with method='temperature'), PolynomialFeatures, cross_val_predict
