# Text Classification

This reference covers building custom text classifiers using TextBlob 0.20.0.

## Classifier Types

TextBlob provides three classifier implementations:

1. **NaiveBayesClassifier** - Default, efficient for text classification
2. **DecisionTreeClassifier** - Good for interpretable models
3. **MaxEntClassifier** - Maximum Entropy (requires NumPy)

## Creating a Naive Bayes Classifier

### Basic Setup

```python
from textblob.classifiers import NaiveBayesClassifier

# Training data: list of (text, label) tuples
train_data = [
    ("I love this sandwich.", "pos"),
    ("This is an amazing place!", "pos"),
    ("I feel very good about these beers.", "pos"),
    ("This is my best work.", "pos"),
    ("What an awesome view", "pos"),
    ("I do not like this restaurant", "neg"),
    ("I am tired of this stuff.", "neg"),
    ("I can't deal with this", "neg"),
    ("He is my sworn enemy!", "neg"),
    ("My boss is horrible.", "neg"),
]

# Create classifier
classifier = NaiveBayesClassifier(train_data)
```

### Test Data

```python
test_data = [
    ("The beer was good.", "pos"),
    ("I do not enjoy my job", "neg"),
    ("I ain't feeling dandy today.", "neg"),
    ("I feel amazing!", "pos"),
    ("Gary is a friend of mine.", "pos"),
    ("I can't believe I'm doing this.", "neg"),
]
```

## Classifying Text

### Single Classification

```python
from textblob.classifiers import NaiveBayesClassifier

classifier = NaiveBayesClassifier(train_data)

# Classify a string
label = classifier.classify("This is an amazing library!")
print(label)  # 'pos'
```

### Probability Distribution

Get confidence scores for each class:

```python
# Get probability distribution
prob_dist = classifier.prob_classify("This one's a doozy.")

# Most likely class
most_likely = prob_dist.max()
print(most_likely)  # 'pos'

# Probability of specific classes
pos_prob = prob_dist.prob("pos")
neg_prob = prob_dist.prob("neg")

print(f"Positive: {pos_prob:.2f}")  # 0.63
print(f"Negative: {neg_prob:.2f}")  # 0.37

# All probabilities
for label in prob_dist.labels():
    print(f"{label}: {prob_dist.prob(label):.2f}")
```

### Classification Thresholds

Implement custom decision thresholds:

```python
def classify_with_threshold(text, classifier, threshold=0.6):
    """Only classify if confidence exceeds threshold."""
    prob_dist = classifier.prob_classify(text)
    most_likely = prob_dist.max()
    confidence = prob_dist.prob(most_likely)
    
    if confidence >= threshold:
        return most_likely, confidence
    else:
        return "unknown", confidence

label, confidence = classify_with_threshold("It's okay.", classifier)
print(f"Label: {label}, Confidence: {confidence:.2f}")
```

## Classifying TextBlobs

### Attaching Classifier to TextBlob

```python
from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier

classifier = NaiveBayesClassifier(train_data)

# Pass classifier to TextBlob constructor
blob = TextBlob("The beer is good. But the hangover is horrible.", 
                classifier=classifier)

# Classify entire blob
print(blob.classify())  # 'pos'

# Classify each sentence
for sentence in blob.sentences:
    print(f"{sentence}: {sentence.classify()}")

# Output:
# The beer is good.: pos
# But the hangover is horrible.: neg
```

### Sentence-Level Analysis

```python
def analyze_sentiment_by_sentence(text, classifier):
    """Analyze sentiment for each sentence."""
    blob = TextBlob(text, classifier=classifier)
    
    results = []
    for sentence in blob.sentences:
        label = sentence.classify()
        prob_dist = sentence.prob_classify()
        confidence = prob_dist.prob(label)
        
        results.append({
            'text': str(sentence),
            'label': label,
            'confidence': confidence
        })
    
    return results

review = "Great product! Terrible customer service. But the quality is excellent."
analysis = analyze_sentiment_by_sentence(review, classifier)

for result in analysis:
    print(f"{result['label']}: {result['confidence']:.2f} - {result['text']}")
```

## Evaluating Classifiers

### Accuracy

```python
accuracy = classifier.accuracy(test_data)
print(f"Accuracy: {accuracy:.2%}")  # 83.33%
```

### Cross-Validation

Manual cross-validation implementation:

```python
from sklearn.model_selection import KFold
import numpy as np

def cross_validate(data, n_folds=5):
    """Simple k-fold cross-validation."""
    from textblob.classifiers import NaiveBayesClassifier
    
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    accuracies = []
    
    for train_idx, test_idx in kf.split(data):
        train = [data[i] for i in train_idx]
        test = [data[i] for i in test_idx]
        
        clf = NaiveBayesClassifier(train)
        acc = clf.accuracy(test)
        accuracies.append(acc)
    
    return np.mean(accuracies), np.std(accuracies)

# Combine train and test data
all_data = train_data + test_data
mean_acc, std_acc = cross_validate(all_data)

print(f"Cross-validation accuracy: {mean_acc:.2%} (+/- {std_acc:.2%})")
```

### Informative Features

Identify which features are most predictive:

```python
# Show top 10 informative features
classifier.show_informative_features(10)

# Example output:
# Most Informative Features
#              contains(my) = True              neg : pos    =      1.7 : 1.0
#              contains(an) = False             neg : pos    =      1.6 : 1.0
#               contains(I) = True              neg : pos    =      1.4 : 1.0
#               contains(I) = False             pos : neg    =      1.4 : 1.0
#              contains(my) = False             pos : neg    =      1.3 : 1.0
```

### Confusion Matrix (Manual)

```python
def confusion_matrix(classifier, test_data):
    """Generate a simple confusion matrix."""
    labels = sorted(set(label for _, label in test_data))
    matrix = {label: {l: 0 for l in labels} for label in labels}
    
    for text, true_label in test_data:
        pred_label = classifier.classify(text)
        matrix[true_label][pred_label] += 1
    
    return matrix

cm = confusion_matrix(classifier, test_data)
for true_label, predictions in cm.items():
    print(f"True {true_label}: {predictions}")
```

## Loading Data from Files

### CSV Format

Create a file `train.csv`:
```csv
I love this sandwich.,pos
This is an amazing place!,pos
I do not like this restaurant,neg
```

Load and train:
```python
from textblob.classifiers import NaiveBayesClassifier

with open('train.csv', 'r') as fp:
    classifier = NaiveBayesClassifier(fp, format='csv')
```

### JSON Format

Create a file `train.json`:
```json
[
    {"text": "I love this sandwich.", "label": "pos"},
    {"text": "This is an amazing place!", "label": "pos"},
    {"text": "I do not like this restaurant", "label": "neg"}
]
```

Load and train:
```python
with open('train.json', 'r') as fp:
    classifier = NaiveBayesClassifier(fp, format='json')
```

### TSV Format

Create a file `train.tsv`:
```tsv
I love this sandwich.	pos
This is an amazing place!	pos
I do not like this restaurant	neg
```

Load and train:
```python
with open('train.tsv', 'r') as fp:
    classifier = NaiveBayesClassifier(fp, format='tsv')
```

### Evaluating with File Data

```python
# Evaluate accuracy using file
with open('test.json', 'r') as fp:
    accuracy = classifier.accuracy(fp, format='json')

print(f"Test accuracy: {accuracy:.2%}")
```

## Updating Classifiers

### Adding New Training Data

```python
new_data = [
    ("She is my best friend.", "pos"),
    ("I'm happy to have a new friend.", "pos"),
    ("Stay thirsty, my friend.", "pos"),
    ("He ain't from around here.", "neg"),
]

# Update classifier
classifier.update(new_data)

# Check improved accuracy
new_accuracy = classifier.accuracy(test_data)
print(f"Updated accuracy: {new_accuracy:.2%}")  # May improve to 100%
```

### Incremental Learning Pattern

```python
def incremental_classifier():
    """Create a classifier that can be updated over time."""
    from textblob.classifiers import NaiveBayesClassifier
    
    # Initial training data
    initial_data = [
        ("Great product!", "pos"),
        ("Terrible experience", "neg"),
    ]
    
    clf = NaiveBayesClassifier(initial_data)
    return clf

# Initialize classifier
classifier = incremental_classifier()

# Update with user feedback
def add_feedback(text, label, classifier):
    """Add a single example to the classifier."""
    classifier.update([(text, label)])

# Usage
add_feedback("Absolutely love it!", "pos", classifier)
add_feedback("Not worth the money", "neg", classifier)
```

## Custom Feature Extractors

### Default Feature Extractor

By default, NaiveBayesClassifier uses a feature extractor that creates features like:
- `contains(word): True/False` for each word in the training set

### Creating Custom Extractors

```python
def end_word_extractor(document):
    """Use first and last words as features."""
    tokens = document.split()
    if not tokens:
        return {}
    
    first_word, last_word = tokens[0], tokens[-1]
    feats = {
        f"first({first_word})": True,
        f"last({last_word})": True,
    }
    return feats

# Use custom extractor
classifier = NaiveBayesClassifier(train_data, 
                                   feature_extractor=end_word_extractor)

# Test
blob = TextBlob("I'm excited to try my new classifier.", 
                classifier=classifier)
print(blob.classify())  # 'pos'
```

### Advanced Feature Extractors

```python
def advanced_feature_extractor(document):
    """Extract multiple types of features."""
    from textblob import TextBlob
    
    blob = TextBlob(document.lower())
    features = {}
    
    # Word presence features
    for word in blob.words:
        features[f"contains({word})"] = True
    
    # Length features
    features["num_words"] = len(blob.words)
    features["num_sentences"] = len(blob.sentences)
    features["avg_word_length"] = sum(len(w) for w in blob.words) / max(len(blob.words), 1)
    
    # Punctuation features
    features["has_exclamation"] = "!" in document
    features["has_question"] = "?" in document
    
    # Sentiment features
    features["polarity"] = blob.sentiment.polarity
    features["subjectivity"] = blob.sentiment.subjectivity
    
    return features

# Train with advanced features
classifier = NaiveBayesClassifier(train_data, 
                                   feature_extractor=advanced_feature_extractor)
```

### N-gram Features

```python
def ngram_feature_extractor(document, n=2):
    """Use n-grams as features."""
    from textblob import TextBlob
    
    blob = TextBlob(document.lower())
    features = {}
    
    # Unigram features
    for word in blob.words:
        features[f"word({word})"] = True
    
    # Bigram features
    for bigram in blob.ngrams(n=2):
        ngram_str = ' '.join(bigram)
        features[f"bigram({ngram_str})"] = True
    
    return features

classifier = NaiveBayesClassifier(train_data, 
                                   feature_extractor=ngram_feature_extractor)
```

## Decision Tree Classifier

### Basic Usage

```python
from textblob.classifiers import DecisionTreeClassifier

# Train decision tree
dt_classifier = DecisionTreeClassifier(train_data)

# Classify
label = dt_classifier.classify("This product is amazing!")
print(label)  # 'pos'

# Evaluate
accuracy = dt_classifier.accuracy(test_data)
print(f"Accuracy: {accuracy:.2%}")
```

### Visualizing Decision Tree

```python
# Print tree structure
dt_classifier.pprint()

# Example output shows decision rules:
# contains(love) = True
#   -> pos
# contains(love) = False
#   contains(horrible) = True
#     -> neg
#   contains(horrible) = False
#     -> pos
```

### Advantages of Decision Trees

- Interpretable decision rules
- No probability smoothing assumptions
- Good for small datasets
- Easy to debug and understand

## Maximum Entropy Classifier

### Requirements

Requires NumPy:
```bash
pip install numpy
```

### Basic Usage

```python
from textblob.classifiers import MaxEntClassifier

# Train maximum entropy classifier
me_classifier = MaxEntClassifier(train_data)

# Classify
label = me_classifier.classify("Excellent service!")
print(label)  # 'pos'

# Get probabilities
prob_dist = me_classifier.prob_classify("It was okay.")
print(prob_dist.max())  # Most likely class
```

### When to Use MaxEnt

- Larger datasets (more training examples)
- When feature correlations matter
- When you need well-calibrated probabilities
- Willing to trade speed for accuracy

## Multi-Class Classification

### Setup with Multiple Classes

```python
from textblob.classifiers import NaiveBayesClassifier

# Training data with multiple categories
multi_class_data = [
    ("Python is great for web development", "web"),
    ("Machine learning with Python is powerful", "ml"),
    ("Data analysis using pandas", "data"),
    ("Building APIs with Flask", "web"),
    ("Neural networks in TensorFlow", "ml"),
    ("SQL queries and databases", "data"),
    ("Django web framework tutorial", "web"),
    ("Deep learning algorithms", "ml"),
    ("Data visualization with matplotlib", "data"),
]

classifier = NaiveBayesClassifier(multi_class_data)

# Classify
test_texts = [
    "Creating a REST API",
    "Training a neural network",
    "Analyzing datasets"
]

for text in test_texts:
    label = classifier.classify(text)
    print(f"{text}: {label}")
```

### Multi-Class Probability Analysis

```python
def multi_class_analysis(text, classifier):
    """Show probabilities for all classes."""
    prob_dist = classifier.prob_classify(text)
    
    print(f"Text: {text}")
    for label in prob_dist.labels():
        prob = prob_dist.prob(label)
        bar = '█' * int(prob * 20)
        print(f"  {label:10s}: {prob:.3f} {bar}")

multi_class_analysis("Building a web application with Python", classifier)
```

## Production Tips

### Saving and Loading Classifiers

```python
import pickle

# Save classifier
with open('classifier.pkl', 'wb') as f:
    pickle.dump(classifier, f)

# Load classifier
with open('classifier.pkl', 'rb') as f:
    classifier = pickle.load(f)
```

### Error Handling

```python
def safe_classify(text, classifier, default='unknown'):
    """Safely classify text with error handling."""
    try:
        if not text or not text.strip():
            return default
        
        return classifier.classify(text)
    except Exception as e:
        print(f"Classification error: {e}")
        return default

# Usage
label = safe_classify("", classifier)  # Returns 'unknown'
```

### Batch Classification

```python
def batch_classify(texts, classifier):
    """Classify multiple texts efficiently."""
    results = []
    for text in texts:
        label = classifier.classify(text)
        prob_dist = classifier.prob_classify(text)
        confidence = prob_dist.prob(label)
        
        results.append({
            'text': text,
            'label': label,
            'confidence': confidence
        })
    
    return results

texts = ["Great product!", "Terrible experience", "It's okay"]
results = batch_classify(texts, classifier)

for result in results:
    print(f"{result['label']} ({result['confidence']:.2f}): {result['text']}")
```
