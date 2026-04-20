# Text Analytics & Feature Extraction

## CountVectorizer

```python
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(
    lowercase=True,
    token_pattern=r"(?u)\b\w\w+\b",  # minimum 2-char tokens
    stop_words='english',
    max_features=10000
)
X_counts = vectorizer.fit_transform(corpus)

# Get vocabulary
vocab = vectorizer.vocabulary_
feature_names = vectorizer.get_feature_names_out()

# Transform new documents
X_new = vectorizer.transform(new_documents)
```

- Returns sparse matrix of shape (n_documents, n_features)
- `token_pattern`: regex for token extraction
- `stop_words`: 'english', 'french', etc., or custom list
- `min_df`: ignore terms with document frequency below threshold
- `max_df`: ignore terms above document frequency
- `ngram_range`: tuple (min_n, max_n) for n-grams

## TfidfVectorizer

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(
    stop_words='english',
    max_features=5000,
    ngram_range=(1, 2),
    norm='l2',
    use_idf=True,
    smooth_idf=True
)
X_tfidf = tfidf.fit_transform(corpus)

# Get feature names
print(tfidf.get_feature_names_out()[:10])

# IDF values (term importance)
print(tfidf.idf_)
```

- Combines CountVectorizer with TF-IDF weighting
- `norm`: 'l1', 'l2' (default), 'max', or None
- `sublinear_tf`: apply sublinear tf scaling (1 + log(tf))
- `smooth_idf`: smooth IDF weights by adding 1 to document counts
- Returns sparse matrix

### TF-IDF Formula

```
TF-IDF(t,d) = TF(t,d) × log((1 + N) / (1 + df(t))) + smoothing
```

Where:
- `TF(t,d)` = term frequency in document d
- `N` = total number of documents
- `df(t)` = number of documents containing term t

## HashingVectorizer

```python
from sklearn.feature_extraction.text import HashingVectorizer

hasher = HashingVectorizer(
    n_features=2**20,  # 1 million features
    alternate_sign=True,
    ngram_range=(1, 2)
)
X_hashed = hasher.transform(corpus)
```

- Stateless: no need to call fit()
- Uses hash trick for feature mapping
- Memory efficient; supports streaming/large corpora
- No vocabulary stored; irreversible transformation
- `n_features`: number of output features

## Text Preprocessing Pipeline

### Complete Text Classification Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    documents, labels, test_size=0.2, random_state=42
)

# Build pipeline
text_clf = Pipeline([
    ('tfidf', TfidfVectorizer(
        stop_words='english',
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True
    )),
    ('clf', LinearSVC(class_weight='balanced'))
])

# Hyperparameter tuning
param_grid = {
    'tfidf__max_features': [5000, 10000, 20000],
    'tfidf__ngram_range': [(1, 1), (1, 2)],
    'clf__C': [0.1, 1, 10]
}

grid = GridSearchCV(text_clf, param_grid, cv=5, n_jobs=-1)
grid.fit(X_train, y_train)

print(f"Best: {grid.best_params_}")
print(f"Score: {grid.best_score_:.4f}")

# Evaluate on test set
y_pred = grid.predict(X_test)
print(classification_report(y_test, y_pred))
```

### Custom Tokenizer

```python
import re
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer

def custom_tokenizer(text):
    # Lowercase and extract words
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    
    # Remove short tokens
    tokens = [t for t in tokens if len(t) > 2]
    
    # Optional: stemming or lemmatization
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(t) for t in tokens]
    
    return tokens

vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer, stop_words='english')
```

## N-gram Extraction

### Unigrams + Bigrams

```python
from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")
X = cv.fit_transform(["hello world this is a test", "another test document"])
print(cv.get_feature_names_out())
# ['a' 'another' 'document' 'hello' 'hello world' ...]
```

### Trigrams

```python
cv = CountVectorizer(ngram_range=(3, 3))
X = cv.fit_transform(corpus)
```

## Text Feature Importance

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

tfidf = TfidfVectorizer(max_features=1000)
X_tfidf = tfidf.fit_transform(corpus)

clf = LinearSVC(class_weight='balanced')
clf.fit(X_tfidf, y_train)

# Get top features per class
feature_names = tfidf.get_feature_names_out()
for i, class_name in enumerate(clf.classes_):
    top_indices = clf.coef_[i].argsort()[-10:][::-1]
    print(f"Top for {class_name}:")
    for idx in top_indices:
        print(f"  {feature_names[idx]}: {clf.coef_[i][idx]:.4f}")
```

## Document Similarity

### Cosine Similarity

```python
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer()
X = tfidf.fit_transform(documents)

# Similarity between all pairs
sim_matrix = cosine_similarity(X)

# Similarity of new doc to corpus
new_doc = ["this is a new document"]
new_vec = tfidf.transform(new_doc)
similarities = cosine_similarity(new_vec, X).flatten()
top_indices = similarities.argsort()[::-1][:5]
```

### Document Clustering

```python
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(max_features=5000)
X_tfidf = tfidf.fit_transform(documents)

kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_tfidf)

# Print cluster topics
for i in range(10):
    mask = labels == i
    print(f"\nCluster {i} ({mask.sum()} docs):")
    print(" ".join(documents[mask][:5]))
```

## Key Parameters Summary

| Parameter | CountVectorizer | TfidfVectorizer | HashingVectorizer |
|-----------|----------------|-----------------|-------------------|
| `stop_words` | ✅ | ✅ | ❌ |
| `ngram_range` | ✅ | ✅ | ✅ |
| `max_features` | ✅ | ✅ | ❌ (use n_features) |
| `min_df` | ✅ | ✅ | ❌ |
| `max_df` | ✅ | ✅ | ❌ |
| `token_pattern` | ✅ | ✅ | ❌ |
| `lowercase` | ✅ | ✅ | ✅ |
| `sublinear_tf` | ❌ | ✅ | ❌ |
| `norm` | ❌ | ✅ | ❌ |
| Stateless (no fit) | ❌ | ❌ | ✅ |
| Vocabulary stored | ✅ | ✅ | ❌ |
