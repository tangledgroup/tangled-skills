# Classification & Sentiment

## Text Classification

### Naive Bayes Classifier

The workhorse of text classification in NLTK:

```python
from nltk.classify import NaiveBayesClassifier
from nltk.classify.util import accuracy as classify_accuracy

# Feature extraction
def document_features(words):
    word_set = set(words)
    return {word: (word in word_set) for word in all_word_features}

# Training data: list of (features, label) tuples
train_data = [
    (document_features(['great', 'amazing', 'love']), 'positive'),
    (document_features(['terrible', 'awful', 'hate']), 'negative'),
]

classifier = NaiveBayesClassifier.train(train_data)
label = classifier.classify(document_features(['great', 'love']))
prob_dist = classifier.prob_classify(document_features(['great']))
print(prob_dist.max())  # most likely label
```

### Most Informative Features

```python
classifier.show_most_informative_features(n=10)
```

### Positive Naive Bayes

For learning from positive examples only (useful for spam detection, anomaly detection):

```python
from nltk.classify import PositiveNaiveBayesClassifier

classifier = PositiveNaiveBayesClassifier.train(positive_train_data)
```

### Maximum Entropy Classifier

Logistic regression-based classifier with configurable training algorithms:

```python
from nltk.classify import MaxentClassifier

classifier = MaxentClassifier.train(
    train_data,
    algorithm='megam',     # or 'gis', 'iis'
    trace=True,
    max_iter=100,
)

label = classifier.classify(features)
prob_dist = classifier.prob_classify(features)
classifier.show_most_informative_features(n=10)
```

Training algorithms: `'gis'` (Gibbs Iterative Scaling), `'iis'` (Improved IS), `'megam'` (requires MEGAM binary).

### Decision Tree Classifier

```python
from nltk.classify import DecisionTreeClassifier

classifier = DecisionTreeClassifier.train(train_data)
label = classifier.classify(features)
classifier.pretty_format()  # print the tree
```

### Scikit-Learn Wrapper

Use any scikit-learn classifier through NLTK's interface:

```python
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

# Wrap a scikit-learn classifier
sklearn_classifier = SklearnClassifier(MultinomialNB())
sklearn_classifier.train(train_data)
label = sklearn_classifier.classify(features)
```

### Text Categorization (Language Identification)

```python
from nltk.classify.textcat import TextCat

tc = TextCat()
# Profile a language with sample text
tc.profile('English', open('english_samples.txt').read())
tc.profile('Spanish', open('spanish_samples.txt').read())

# Guess the language
language = tc.guess_language('This is an English sentence.')
```

## Feature Extraction Patterns

### Document Classification Features

```python
def document_features(document):
    words = set(word_tokenize(document.lower()))
    return {
        'contains_good': 'good' in words,
        'contains_bad': 'bad' in words,
        'word_count': len(words),
        'has_exclamation': '!' in document,
    }
```

### Name Gender Classification

```python
def gender_features(name):
    return {
        'last_letter': name[-1],
        'last_2_letters': name[-2:],
        'length': len(name),
        'has_vowel': any(c in 'aeiou' for c in name.lower()),
    }
```

### Sentence Polarity Features

```python
def sentence_features(sentence):
    words = set(word_tokenize(sentence.lower()))
    return {
        'last_word': word_tokenize(sentence)[-1],
        'has_negation': any(w in words for w in ['not', 'no', "n't"]),
        'word_count': len(words),
    }
```

## Evaluation Utilities

### Accuracy

```python
from nltk.classify.util import accuracy

accuracy = accuracy(classifier, test_data)
print(f"Accuracy: {accuracy:.4f}")
```

### Confusion Matrix

```python
from nltk.metrics import ConfusionMatrix

cm = ConfusionMatrix(gold_labels, predicted_labels)
cm.pretty_format()
print(cm.precision())
print(cm.recall())
print(cm.f_measure())
```

## Sentiment Analysis

### VADER (Valence Aware Dictionary and sEntiment Reasoner)

Rule-based sentiment analyzer designed for social media text. Handles emojis, slang, capitalization, and punctuation intensifiers.

```python
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

# polarity_scores returns: neg, neu, pos, compound
scores = sia.polarity_scores("This movie was absolutely fantastic!!!")
print(scores)
# {'neg': 0.0, 'neu': 0.242, 'pos': 0.758, 'compound': 0.8129}

# compound: [-1, 1] — overall sentiment
# >= 0.05  → positive
# <= -0.05 → negative
# between  → neutral

# Batch scoring
texts = ["I love this!", "Terrible experience.", "It was okay."]
for text in texts:
    print(text, sia.polarity_scores(text))
```

VADER handles:

- Capitalization amplification ("GREAT" > "great")
- Punctuation intensifiers ("wow!!!" > "wow")
- Degree modifiers ("very good", "slightly bad")
- Negation ("not good")
- Emoji and emoticons
- Slang and social media conventions

### SentiWordNet

Lexicon-based sentiment using WordNet with polarity scores:

```python
from nltk.corpus import sentiwordnet as swn

synset = wn.synset('awesome.a.01')
senti_synset = swn.senti_synset('awesome.a.01')

print(senti_synset.pos_score())   # positive sentiment (0 to 1)
print(senti_synset.neg_score())   # negative sentiment (0 to 1)
print(senti_synset.obj_score())   # objectivity score (0 to 1)
```

### Opinion Lexicon

Simple positive/negative word lists:

```python
from nltk.corpus import opinion_lexicon

print(opinion_lexicon.positive()[:5])
# ['absolutist', 'accessible', 'accommodative', ...]
print(opinion_lexicon.negative()[:5])
# ['abnormalities', 'abolish', 'abominable', ...]
```

### Movie Reviews Corpus

Standard sentiment analysis dataset:

```python
from nltk.corpus import movie_reviews

documents = [
    (list(movie_reviews.words(fileid)), category)
    for category in movie_reviews.categories()
    for fileid in movie_reviews.fileids(category)
]

import random
random.shuffle(documents)

# Feature extraction
all_words = FreqDist(w.lower() for w in movie_reviews.words())
word_features = list(all_words.keys())[:2000]

def document_features(words):
    words_set = set(words)
    return {wf: (wf in words_set) for wf in word_features}

train_features = [document_features(doc) for doc, cat in documents[:1900]]
test_features = [document_features(doc) for doc, cat in documents[1900:]]
train_labels = [cat for doc, cat in documents[:1900]]
test_labels = [cat for doc, cat in documents[1900:]]

classifier = NaiveBayesClassifier.train(train_features)
print(classify_accuracy(classifier, [(f, l) for f, l in zip(test_features, test_labels)]))
```

### Custom Sentiment Analyzer

Build a trainable sentiment classifier with configurable feature extractors:

```python
from nltk.sentiment import SentimentAnalyzer

sa = SentimentAnalyzer()

# Define features
all_words = sa.all_words([list(movie_reviews.words()) for _ in range(100)])
word_features = sa.unigram_word_feats(all_words, min_freq=4)

# Train
train_feats = [sa.apply_features(words) for words, _ in documents[:1900]]
train_labels = [cat for _, cat in documents[:1900]]
classifier = sa.train(NaiveBayesClassifier, train_feats, train_labels)

# Classify
sentiment = sa.classify(classifier, "This movie was wonderful")
```

Add bigram features:

```python
bigram_features = sa.bigram_collocation_feats(all_words, max_freq=100, min_freq=4)
sa.add_feat_extractor(extract_bigram_feats, bigrams=bigram_features)
```
