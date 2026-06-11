# Classifiers

The `textblob.classifiers` module provides text classification with multiple algorithms. All classifiers inherit from `BaseClassifier` and support training from Python lists or data files (CSV, JSON, TSV).

## Training Data Format

Training data is a list of tuples: `(text, label)` where `text` is a string or iterable of tokens, and `label` is a classification string.

```python
train = [
    ('I love this sandwich.', 'pos'),
    ('This is an amazing place!', 'pos'),
    ('I feel very good about these beers.', 'pos'),
    ('I do not like this restaurant', 'neg'),
    ('I am tired of this stuff.', 'neg'),
    ("I can't deal with this", 'neg'),
]
```

## NaiveBayesClassifier

The most commonly used classifier. Based on NLTK's Naive Bayes implementation.

```python
from textblob.classifiers import NaiveBayesClassifier

cl = NaiveBayesClassifier(train)
cl.classify("This is amazing!")  # 'pos'
```

### Probabilistic Classification

Get probability distribution over labels:

```python
prob_dist = cl.prob_classify("I feel happy this morning.")
prob_dist.max()        # 'pos'
prob_dist.prob('pos')  # 0.7
prob_dist.prob('neg')  # 0.3
```

### Most Informative Features

Inspect which features drive classification decisions:

```python
cl.show_informative_features()
# Displays ranked features with their log likelihood ratios
cl.informative_features()  # Returns as list of (feature_name, feature_value) tuples
```

## DecisionTreeClassifier

Based on NLTK's decision tree implementation. Provides interpretable decision rules.

```python
from textblob.classifiers import DecisionTreeClassifier

cl = DecisionTreeClassifier(train)
cl.classify("Great experience!")  # classification result
```

### Tree Inspection

```python
cl.pretty_format()   # Pretty-printed tree structure with indentation
cl.pseudocode()      # Nested if-then pseudocode representation
```

## MaxEntClassifier

Maximum Entropy classifier wrapping NLTK's MaxentClassifier.

```python
from textblob.classifiers import MaxEntClassifier

cl = MaxEntClassifier(train)
cl.prob_classify("I love it")  # Probability distribution
```

## PositiveNaiveBayesClassifier

Binary classification with partially-labeled training sets — only the positive class needs labels. Uses an unlabeled set to estimate feature frequencies for the negative class.

```python
from textblob.classifiers import PositiveNaiveBayesClassifier

sports_sentences = [
    'The team dominated the game',
    'They lost the ball',
    'The game was intense',
]
various_sentences = [
    'The President did not comment',
    'I lost the keys',
    'Sara has two kids',
]

cl = PositiveNaiveBayesClassifier(
    positive_set=sports_sentences,
    unlabeled_set=various_sentences,
    positive_prob_prior=0.5
)

cl.classify("My team lost the game")  # True (sports)
cl.classify("Something completely different.")  # False (not sports)
```

## Using Classifiers with TextBlob

Attach a classifier to a TextBlob for per-sentence classification:

```python
from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier

cl = NaiveBayesClassifier(train)
blob = TextBlob("The beer is good. But the hangover is horrible.", classifier=cl)

for sentence in blob.sentences:
    print(sentence, "->", sentence.classify())
# The beer is good. -> pos
# But the hangover is horrible. -> neg
```

## Feature Extractors

Feature extractors convert text into dictionaries of boolean features. TextBlob provides two built-in extractors:

### basic_extractor (default)

Returns a dict indicating which words from the training set appear in the document:

```python
from textblob.classifiers import basic_extractor
features = basic_extractor(document, train_set)
# {'contains(amazing)': True, 'contains(horrible)': False, ...}
```

### contains_extractor

Returns a dict of all words the document contains (used by PositiveNaiveBayesClassifier):

```python
from textblob.classifiers import contains_extractor
features = contains_extractor(document)
# {'contains(the)': True, 'contains(team)': True, ...}
```

### Custom Feature Extractors

Write your own extractor function:

```python
def my_extractor(document):
    words = set(document.lower().split())
    return {
        'has_exclamation': '!' in document,
        'word_count': len(words),
        f'contains({w})': True for w in words
    }

cl = NaiveBayesClassifier(train, feature_extractor=my_extractor)
```

## Evaluating Classifiers

Compute accuracy on a test set:

```python
test = [
    ('the beer was good.', 'pos'),
    ('I do not enjoy my job', 'neg'),
]
accuracy = cl.accuracy(test)  # float, e.g. 0.85
```

## Updating Classifiers

Add new training data and retrain:

```python
new_data = [
    ('Absolutely fantastic!', 'pos'),
    ('Terrible experience.', 'neg'),
]
cl.update(new_data)  # Retrains with combined old + new data
```

## Loading Data from Files

Classifiers accept file-like objects for CSV, JSON, and TSV data:

```python
with open('training_data.csv', 'r') as fp:
    cl = NaiveBayesClassifier(fp, format='csv')
# format=None auto-detects from file content
```

Custom formats can be registered via `textblob.formats.register()`.
