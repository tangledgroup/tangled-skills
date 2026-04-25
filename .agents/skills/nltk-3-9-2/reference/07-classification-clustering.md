# NLTK Classification and Clustering - Complete Guide

## Overview

NLTK provides various classification and clustering algorithms for text categorization, sentiment analysis, and document clustering tasks.

## Text Classification

### Naive Bayes Classifier

Most commonly used classifier in NLTK:

```python
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.probability import FreqDist

# Prepare data
def extract_features(words):
    """Extract word presence features."""
    return {f"contains({w})": True for w in words}

# Get documents and labels
documents = [(movie_reviews.words(fileid), category) 
             for category in movie_reviews.categories()
             for fileid in movie_reviews.fileids(category)]

# Find most common words (features)
all_words = FreqDist(w.lower() for w in movie_reviews.words())
common_words = [w for w, f in all_words.most_common(2000)]

def extract_features_limited(words):
    """Extract features using limited vocabulary."""
    words = [w.lower() for w in words]
    return {f"contains({w})": w in words for w in common_words}

# Create feature sets
featuresets = [(extract_features_limited(d), c) for d, c in documents]

# Split into train/test
train_size = int(0.8 * len(featuresets))
train_set = featuresets[:train_size]
test_set = featuresets[train_size:]

# Train classifier
classifier = NaiveBayesClassifier.train(train_set)

# Evaluate
accuracy = classifier.accuracy(test_set)
print(f"Accuracy: {accuracy:.2%}")

# Show most informative features
classifier.show_most_informative_features(20)
```

### Maximum Entropy Classifier

More sophisticated but slower:

```python
from nltk.classify import MaxentClassifier
from nltk.corpus import movie_reviews

# Use same feature extraction as Naive Bayes
# (from previous example)

# Train with fewer features for speed
def extract_features_simple(words):
    words = [w.lower() for w in words]
    return {f"contains({w})": w in words for w in common_words[:500]}

featuresets = [(extract_features_simple(d), c) for d, c in documents]

# Split data
train_size = int(0.8 * len(featuresets))
train_set = featuresets[:train_size]
test_set = featuresets[train_size:]

# Train classifier (can be slow)
classifier = MaxentClassifier.train(train_set, max_iter=10)

# Evaluate
accuracy = classifier.accuracy(test_set)
print(f"Accuracy: {accuracy:.2%}")
```

### Decision Tree Classifier

Interpretable classification rules:

```python
from nltk.classify import decisiontree

# Use same featuresets from previous examples

# Train decision tree
classifier = decisiontree.DiscriminantClassifier.train(train_set)

# Evaluate
accuracy = classifier.accuracy(test_set)
print(f"Accuracy: {accuracy:.2%}")

# Show decision tree (if supported)
print(classifier)
```

### One-Class Classifier

Anomaly detection with single class:

```python
from nltk.classify import OneClassClassifier
from nltk.corpus import movie_reviews

# Get only positive reviews (one class)
positive_docs = [(movie_reviews.words(f), 'pos') 
                 for f in movie_reviews.fileids('pos')]

# Extract features
def extract_features(words):
    return {w.lower(): True for w in words[:50]}  # First 50 words

featuresets = [(extract_features(d), c) for d, c in positive_docs]

# Train one-class classifier
classifier = OneClassClassifier.train(featuresets)

# Test on new document
test_words = movie_reviews.words(movie_reviews.fileids('neg')[0])
test_features = extract_features(test_words)

label = classifier.classify(test_features)
print(f"Classification: {label}")  # 'pos' or 'unknown'
```

## Feature Extraction

### Word Features

```python
from nltk.probability import FreqDist
from nltk.corpus import movie_reviews

# Document frequency (number of docs containing word)
doc_freq = FreqDist()
for fileid in movie_reviews.fileids():
    words = set(w.lower() for w in movie_reviews.words(fileid))
    for word in words:
        doc_freq[word] += 1

# Most discriminative words (high document frequency)
print("Words appearing in most documents:")
for word, freq in doc_freq.most_common(20):
    if len(word) > 2:  # Filter short words
        print(f"  {word}: {freq} documents")
```

### N-gram Features

```python
from nltk.util import ngrams

def extract_ngram_features(words, n=2):
    """Extract n-gram features."""
    words = [w.lower() for w in words]
    ngrams_list = list(ngrams(words, n))
    return {f"ngram_{' '.join(ng)}": True for ng in ngrams_list}

# Example
words = ["this", "is", "a", "great", "movie"]
features = extract_ngram_features(words, n=2)
print(features)
# {'ngram_this is': True, 'ngram_is a': True, ...}
```

### Regex Features

```python
import re

def extract_regex_features(text):
    """Extract features based on regex patterns."""
    features = {}
    
    # Count exclamation marks (indicates excitement)
    features['exclamation_count'] = text.count('!')
    
    # Check for question marks
    features['has_question'] = '?' in text
    
    # Word length statistics
    words = text.split()
    features['avg_word_length'] = sum(len(w) for w in words) / len(words) if words else 0
    features['long_words_count'] = sum(1 for w in words if len(w) > 8)
    
    # Capitalization
    features['caps_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
    
    return features

# Example
text = "This is an AMAZING movie!!! You must see it!"
features = extract_regex_features(text)
print(features)
```

### Combined Features

```python
def extract_combined_features(words):
    """Combine multiple feature types."""
    features = {}
    
    # Word presence (limited vocabulary)
    common_words = ['great', 'amazing', 'terrible', 'bad', 'wonderful']
    words_lower = [w.lower() for w in words]
    for word in common_words:
        features[f"contains_{word}"] = word in words_lower
    
    # Document statistics
    features['word_count'] = len(words)
    features['unique_ratio'] = len(set(words_lower)) / len(words_lower) if words else 0
    
    # N-grams
    bigrams = list(ngrams(words_lower, 2))
    features['not_good'] = ('not', 'good') in bigrams
    features['very_good'] = ('very', 'good') in bigrams
    
    return features

# Example
words = ["This", "is", "not", "a", "good", "movie"]
features = extract_combined_features(words)
print(features)
```

## Classifier Evaluation

### Confusion Matrix

```python
from nltk.classify.util import apply_confusion_matrix
from nltk.corpus import movie_reviews

# Train classifier (using code from earlier examples)
# ... training code ...

# Generate confusion matrix
def analyze_errors(test_set, classifier):
    """Analyze classification errors."""
    correct = 0
    incorrect = []
    
    for features, label in test_set:
        predicted = classifier.classify(features)
        if predicted == label:
            correct += 1
        else:
            incorrect.append((features, label, predicted))
    
    accuracy = correct / len(test_set)
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Correct: {correct}/{len(test_set)}")
    print(f"Incorrect: {len(incorrect)}")
    
    # Show some errors
    print("\nSample errors:")
    for features, true_label, predicted in incorrect[:5]:
        print(f"  True: {true_label}, Predicted: {predicted}")
    
    return accuracy

# Evaluate
accuracy = analyze_errors(test_set, classifier)
```

### Cross-Validation

```python
from nltk.classify.util import train_on_labels
import random

def cross_validate(featuresets, k=5):
    """K-fold cross-validation."""
    # Shuffle data
    random.shuffle(featuresets)
    
    # Split into k folds
    fold_size = len(featuresets) // k
    folds = [featuresets[i:i+fold_size] for i in range(0, len(featuresets), fold_size)]
    
    accuracies = []
    
    for i in range(k):
        # Use one fold for testing, rest for training
        test_set = folds[i]
        train_set = [f for j, f in enumerate(featuresets) if j // fold_size != i]
        
        # Train and evaluate
        classifier = NaiveBayesClassifier.train(train_set)
        accuracy = classifier.accuracy(test_set)
        accuracies.append(accuracy)
        print(f"Fold {i+1}: {accuracy:.2%}")
    
    avg_accuracy = sum(accuracies) / len(accuracies)
    print(f"\nAverage accuracy: {avg_accuracy:.2%}")
    
    return accuracies

# Run cross-validation
accuracies = cross_validate(featuresets, k=5)
```

### Precision, Recall, F-Measure

```python
from sklearn.metrics import classification_report

def detailed_evaluation(test_set, classifier):
    """Detailed classification metrics."""
    true_labels = []
    predicted_labels = []
    
    for features, label in test_set:
        predicted = classifier.classify(features)
        true_labels.append(label)
        predicted_labels.append(predicted)
    
    # Generate report
    report = classification_report(true_labels, predicted_labels)
    print(report)
    
    return report

# Evaluate
report = detailed_evaluation(test_set, classifier)
```

## Clustering

### K-Means Clustering

```python
from nltk.cluster import KMeansClusterer
from nltk.corpus import movie_reviews
import numpy as np

# Prepare feature vectors
def extract_numeric_features(words):
    """Extract numeric features for clustering."""
    words_lower = [w.lower() for w in words]
    
    # Feature: word frequencies (normalized)
    features = []
    target_words = ['great', 'good', 'bad', 'terrible', 'amazing']
    total = len(words_lower) if words else 1
    
    for target in target_words:
        count = words_lower.count(target)
        features.append(count / total)
    
    return features

# Get documents
documents = [movie_reviews.words(f) for f in movie_reviews.fileids()[:100]]

# Extract features
feature_vectors = [extract_numeric_features(doc) for doc in documents]

# Create clusterer (k=2 for positive/negative)
clusterer = KMeansClusterer(k=2, repeat=5, verbose=False)

# Assign clusters
assignments = clusterer.cluster_map(feature_vectors)

# Show results
print("Document assignments:")
for i, (doc, assignment) in enumerate(zip(documents[:10], assignments[:10])):
    true_label = movie_reviews.categories(movie_reviews.fileids()[:100][i])[0]
    print(f"Doc {i}: Cluster {assignment}, True label: {true_label}")
```

### Gaussian Clustering

```python
from nltk.cluster import GaussianClusterer

# Use same feature_vectors from K-Means example

# Create Gaussian clusterer
clusterer = GaussianClusterer(k=2)

# Assign clusters
assignments = clusterer.cluster(feature_vectors, assign_all=True)

print("Gaussian clustering results:")
for i, assignment in enumerate(assignments[:10]):
    print(f"Doc {i}: Cluster {assignment}")
```

### Linear Statistical Clustering

```python
from nltk.cluster import LinearSegmentClusterer

# For segmenting text into topics
from nltk.corpus import brown

text = brown.raw()[:5000]
words = text.split()

# Create clusterer (num_clusters=3)
clusterer = LinearSegmentClusterer(num_clusters=3)

# Assign clusters to words
assignments = clusterer.cluster(words, assign_all=True)

# Show segment boundaries
print("Text segments:")
current_cluster = None
for i, (word, cluster) in enumerate(zip(words, assignments)):
    if cluster != current_cluster:
        if current_cluster is not None:
            print(f"  Segment {current_cluster + 1} ended at position {i-1}")
        print(f"  Segment {cluster + 1} started at position {i}")
        current_cluster = cluster
```

## Sentiment Analysis Example

Complete sentiment analysis pipeline:

```python
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews, stopwords
from nltk.probability import FreqDist
from nltk import word_tokenize

# Feature extraction with stopword removal
def extract_sentiment_features(words):
    """Extract features for sentiment classification."""
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    words = [w.lower() for w in words if w not in stop_words and w.isalpha()]
    
    # Word presence features
    return {f"contains({w})": True for w in words}

# Prepare training data
documents = [(movie_reviews.words(fileid), category) 
             for category in movie_reviews.categories()
             for fileid in movie_reviews.fileids(category)]

# Shuffle and split
import random
random.shuffle(documents)
split_point = int(0.8 * len(documents))
train_data = documents[:split_point]
test_data = documents[split_point:]

# Train classifier
classifier = NaiveBayesClassifier.train(train_data)

# Evaluate
accuracy = classifier.accuracy(test_data)
print(f"Sentiment classification accuracy: {accuracy:.2%}")

# Show most informative words
print("\nMost informative features:")
classifier.show_most_informative_features(30)

# Classify new text
def classify_sentiment(text):
    """Classify sentiment of new text."""
    words = word_tokenize(text)
    features = extract_sentiment_features(words)
    sentiment = classifier.classify(features)
    proba = classifier.prob_classify(features)
    
    return {
        'sentiment': sentiment,
        'positive_prob': proba.prob('pos'),
        'negative_prob': proba.prob('neg')
    }

# Test
test_texts = [
    "This movie was absolutely fantastic! I loved every minute of it.",
    "Terrible film. Waste of time and money.",
    "It was okay, nothing special."
]

for text in test_texts:
    result = classify_sentiment(text)
    print(f"\nText: {text[:50]}...")
    print(f"  Sentiment: {result['sentiment']}")
    print(f"  Positive: {result['positive_prob']:.2%}")
    print(f"  Negative: {result['negative_prob']:.2%}")
```

## Common Patterns

### Training Pipeline with Feature Selection

```python
from nltk.classify import NaiveBayesClassifier
from nltk.feature import BinaryFeatureExtractor, BossineReweight
from nltk.corpus import movie_reviews

# Create feature extractor with selection
def create_feature_extractor(min_df=2, max_features=1000):
    """Create feature extractor with document frequency filtering."""
    # Count document frequencies
    doc_freq = FreqDist()
    for fileid in movie_reviews.fileids():
        words = set(w.lower() for w in movie_reviews.words(fileid))
        for word in words:
            doc_freq[word] += 1
    
    # Select features
    selected_features = [w for w, f in doc_freq.most_common(max_features) if f >= min_df]
    
    def extract_features(words):
        words_lower = set(w.lower() for w in words)
        return {f"contains({w})": w in words_lower for w in selected_features}
    
    return extract_features

# Use extractor
extract_features = create_feature_extractor()
documents = [(movie_reviews.words(f), c) 
             for c in movie_reviews.categories()
             for f in movie_reviews.fileids(c)]

featuresets = [(extract_features(d), c) for d, c in documents]

# Split and train
split_point = int(0.8 * len(featuresets))
train_set = featuresets[:split_point]
test_set = featuresets[split_point:]

classifier = NaiveBayesClassifier.train(train_set)
print(f"Accuracy: {classifier.accuracy(test_set):.2%}")
```

## Troubleshooting

### Imbalanced Classes

**Problem**: One class dominates, classifier biased toward majority

**Solution**: Balance training data or use weights:

```python
from collections import Counter

# Check class distribution
labels = [label for _, label in documents]
print(Counter(labels))

# Option 1: Subsample majority class
from itertools import groupby
balanced_docs = []
for label, group in groupby(sorted(documents, key=lambda x: x[1]), key=lambda x: x[1]):
    group_list = list(group)
    balanced_docs.extend(group_list[:min(500, len(group_list))])

# Option 2: Use class weights (requires custom implementation)
```

### Overfitting

**Problem**: High training accuracy, low test accuracy

**Solution**: Reduce features or use regularization:

```python
# Reduce feature count
def extract_features_limited(words):
    words_lower = [w.lower() for w in words]
    # Use only top 500 most common words instead of 2000
    return {f"contains({w})": w in words_lower for w in common_words[:500]}

# Or use cross-validation to find optimal feature count
```

### Slow Training

**Problem**: Maximum Entropy classifier takes too long

**Solution**: Use Naive Bayes or reduce features:

```python
# Naive Bayes is much faster
classifier = NaiveBayesClassifier.train(train_set)

# Or limit MaxentClassifier iterations
classifier = MaxentClassifier.train(train_set, max_iter=5)
```

## References

- **Classification Documentation**: https://www.nltk.org/howto/classify.html
- **Clustering Documentation**: https://www.nltk.org/api/nltk.cluster.html
- **Feature Extraction**: https://www.nltk.org/api/nltk.feature.html
