# Model Selection and Metrics

## Data Splitting

### Train-Test Split

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0, stratify=y
)
```

Use `stratify=y` for classification to preserve class distribution.

### Time Series Split

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
```

## Cross-Validation Strategies

### K-Fold

```python
from sklearn.model_selection import KFold, cross_val_score
kf = KFold(n_splits=5, shuffle=True, random_state=0)
scores = cross_val_score(estimator, X, y, cv=kf)
print(f"Mean score: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
```

### Stratified K-Fold

Preserves class distribution in each fold:

```python
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5)
scores = cross_val_score(estimator, X, y, cv=skf)
```

### Group K-Fold

Ensures samples from the same group are in the same fold:

```python
from sklearn.model_selection import GroupKFold
gkf = GroupKFold(n_splits=5)
scores = cross_val_score(estimator, X, y, groups=groups, cv=gkf)
```

### Stratified Group K-Fold

Combines stratification with group awareness:

```python
from sklearn.model_selection import StratifiedGroupKFold
sgkf = StratifiedGroupKFold(n_splits=5)
scores = cross_val_score(estimator, X, y, groups=groups, cv=sgkf)
```

Version 1.8: Fixed shuffle behavior — stratification among folds is now preserved when `shuffle=True`.

### Leave-One-Out / Leave-P-Out

```python
from sklearn.model_selection import LeaveOneOut, LeavePOut
loo = LeaveOneOut()
lpo = LeavePOut(p=2)
```

### Cross-Validation Predictions

```python
from sklearn.model_selection import cross_val_predict
y_pred = cross_val_predict(estimator, X, y, cv=5)
```

Version 1.8: Now supports Array API compatible inputs.

## Hyperparameter Tuning

### GridSearchCV

Exhaustive search over a parameter grid:

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "C": [0.1, 1, 10, 100],
    "kernel": ["linear", "rbf"],
    "gamma": ["scale", "auto"],
}
grid = GridSearchCV(SVC(), param_grid, cv=5, scoring="accuracy", n_jobs=-1)
grid.fit(X, y)
print(f"Best params: {grid.best_params_}")
print(f"Best CV score: {grid.best_score_:.4f}")
# Access best estimator
best_model = grid.best_estimator_
# Results as DataFrame
results = grid.cv_results_
```

### RandomizedSearchCV

Random sampling from parameter distributions (more efficient for large spaces):

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, loguniform

param_distributions = {
    "C": loguniform(1e-2, 1e3),
    "gamma": loguniform(1e-4, 1e1),
}
random_search = RandomizedSearchCV(
    SVC(), param_distributions, n_iter=50, cv=5, random_state=0
)
random_search.fit(X, y)
```

### HalvingRandomSearchCV / HalvingGridSearchCV

Successive halving — allocates more resources to promising candidates:

```python
from sklearn.model_selection import HalvingRandomSearchCV
halving = HalvingRandomSearchCV(
    SVC(), param_distributions, cv=5, random_state=0
)
halving.fit(X, y)
```

## Classification Metrics

### Accuracy and Confusion Matrix

```python
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
accuracy = accuracy_score(y_true, y_pred)
cm = confusion_matrix(y_true, y_pred)
ConfusionMatrixDisplay(confusion_matrix=cm).plot()
```

Version 1.8: New `confusion_matrix_at_thresholds` function returns TN, FP, FN, TP per threshold.

### Precision, Recall, F1

```python
from sklearn.metrics import precision_score, recall_score, f1_score
precision = precision_score(y_true, y_pred, average="weighted")
recall = recall_score(y_true, y_pred, average="weighted")
f1 = f1_score(y_true, y_pred, average="weighted")
```

Average options: `"binary"`, `"micro"`, `"macro"`, `"weighted"`, `None`.

### Classification Report

```python
from sklearn.metrics import classification_report
print(classification_report(y_true, y_pred, target_names=["class_0", "class_1"]))
```

### ROC Curve and AUC

```python
from sklearn.metrics import roc_curve, auc, RocCurveDisplay
fpr, tpr, thresholds = roc_curve(y_true, y_scores)
roc_auc = auc(fpr, tpr)
display = RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc).plot()
```

Version 1.8: `RocCurveDisplay.from_cv_results` now infers `pos_label` from estimator when `pos_label=None`.

### Precision-Recall Curve

```python
from sklearn.metrics import precision_recall_curve, PrecisionRecallDisplay
precision_vals, recall_vals, thresholds = precision_recall_curve(y_true, y_scores)
display = PrecisionRecallDisplay(precision=precision_vals, recall=recall_vals).plot()
```

Version 1.8: `y_pred` parameter deprecated in favor of `y_score` in `PrecisionRecallDisplay.from_predictions`.

### DET Curve

```python
from sklearn.metrics import det_curve, DetCurveDisplay
fpr, tpr, thresholds = det_curve(y_true, y_scores)
```

Version 1.8: Now supports Array API compliant inputs.

### Brier Score and D² Metrics

```python
from sklearn.metrics import brier_score_loss, d2_brier_score, d2_log_loss_score
brier = brier_score_loss(y_true, y_prob)
d2_brier = d2_brier_score(y_true, y_prob)
d2_log = d2_log_loss_score(y_true, y_prob)
```

Version 1.8: New `d2_brier_score` metric added. All three now support Array API inputs.

### Log Loss

```python
from sklearn.metrics import log_loss
loss = log_loss(y_true, y_prob)
```

### Hamming Loss and Jaccard Score

```python
from sklearn.metrics import hamming_loss, jaccard_score
hl = hamming_loss(y_true, y_pred)  # for multi-label
js = jaccard_score(y_true, y_pred, average="samples")
```

### Cohen's Kappa

```python
from sklearn.metrics import cohen_kappa_score
kappa = cohen_kappa_score(y_true, y_pred)
```

Version 1.8: Now supports Array API inputs.

### Matthews Correlation Coefficient

```python
from sklearn.metrics import matthews_corrcoef
mcc = matthews_corrcoef(y_true, y_pred)
```

### Balanced Accuracy

```python
from sklearn.metrics import balanced_accuracy_score
bal_acc = balanced_accuracy_score(y_true, y_pred)
```

Version 1.8: Now supports Array API inputs.

## Regression Metrics

### R² Score

```python
from sklearn.metrics import r2_score
r2 = r2_score(y_true, y_pred)
```

### Mean Absolute Error

```python
from sklearn.metrics import mean_absolute_error
mae = mean_absolute_error(y_true, y_pred)
```

### Mean Squared Error

```python
from sklearn.metrics import mean_squared_error, mean_squared_log_error
mse = mean_squared_error(y_true, y_pred)
rmse = mean_squared_error(y_true, y_pred, squared=False)
msle = mean_squared_log_error(y_true, y_pred)
```

### Median Absolute Error

```python
from sklearn.metrics import median_absolute_error
medae = median_absolute_error(y_true, y_pred)
```

Version 1.8: Now uses `_averaged_weighted_percentile` for correct weighted median calculation, and supports Array API inputs.

### Explained Variance Score

```python
from sklearn.metrics import explained_variance_score
evs = explained_variance_score(y_true, y_pred)
```

### Max Error

```python
from sklearn.metrics import max_error
me = max_error(y_true, y_pred)
```

## Clustering Metrics

### Silhouette Score

```python
from sklearn.metrics import silhouette_score, silhouette_samples
score = silhouette_score(X, labels)
```

### Calinski-Harabasz Index

```python
from sklearn.metrics import calinski_harabasz_score
score = calinski_harabasz_score(X, labels)
```

Version 1.8: Now supports Array API inputs.

### Davies-Bouldin Index

```python
from sklearn.metrics import davies_bouldin_score
score = davies_bouldin_score(X, labels)
```

Version 1.8: Now supports Array API inputs.

### Adjusted Rand Score and Normalized Mutual Information

For comparing cluster assignments to ground truth:

```python
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
ari = adjusted_rand_score(true_labels, predicted_labels)
nmi = normalized_mutual_info_score(true_labels, predicted_labels)
```

## Scoring Parameters

Use string shortcuts for `scoring` in cross-validation and GridSearchCV:

- Classification: `"accuracy"`, `"precision"`, `"recall"`, `"f1"`, `"roc_auc"`, `"average_precision"`
- Regression: `"r2"`, `"neg_mean_squared_error"`, `"neg_mean_absolute_error"`
- Custom scorer:

```python
from sklearn.metrics import make_scorer, fbeta_score
custom_scorer = make_scorer(fbeta_score, beta=2)
grid = GridSearchCV(estimator, param_grid, scoring=custom_scorer)
```

## Validation Curves

```python
from sklearn.model_selection import validation_curve
param_range = np.logspace(-4, 4, 5)
train_scores, val_scores = validation_curve(
    SVC(), X, y, param_name="C", param_range=param_range, cv=5
)
```
