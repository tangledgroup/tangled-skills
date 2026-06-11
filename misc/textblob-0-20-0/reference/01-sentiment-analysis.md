# Sentiment Analysis

TextBlob provides two sentiment analysis implementations via the `textblob.sentiments` module.

## PatternAnalyzer (Default)

Based on the pattern library's implementation. Uses a lexicon-based approach with an XML sentiment corpus. Returns results as a namedtuple:

```
Sentiment(polarity, subjectivity)
```

- **polarity**: Float in range [-1.0, 1.0]. Negative = negative sentiment, positive = positive sentiment.
- **subjectivity**: Float in range [0.0, 1.0]. 0.0 = very objective (factual), 1.0 = very subjective (opinion).

```python
from textblob import TextBlob

blob = TextBlob("I love this library")
blob.sentiment
# Sentiment(polarity=0.35, subjectivity=0.6)
```

### Sentiment Assessments

Use `keep_assessments=True` to get per-token polarity scores:

```python
blob = TextBlob("The food was good but the service was bad.")
result = blob.analyzer.analyze(blob.raw, keep_assessments=True)
# Sentiment(polarity=0.0, subjectivity=0.5, assessments=[...])
```

Or use the `sentiment_assessments` property:

```python
blob.sentiment_assessments
# Sentiment(polarity=..., subjectivity=..., assessments=[(...)])
```

Each assessment is a tuple of `(token, polarity, subjectivity)` for words found in the pattern sentiment lexicon.

### PatternAnalyzer Limitations

- Lexicon-based: only scores words present in its built-in corpus
- Does not handle context well (e.g., "not good" may score each word independently)
- Best for quick approximations, not production-grade sentiment

## NaiveBayesAnalyzer

A machine learning approach trained on the NLTK movie_reviews corpus. Returns results as a namedtuple:

```
Sentiment(classification, p_pos, p_neg)
```

- **classification**: String label — `'pos'` or `'neg'`
- **p_pos**: Probability of positive classification (float 0.0–1.0)
- **p_neg**: Probability of negative classification (float 0.0–1.0)

```python
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

blob = TextBlob("I love this library", analyzer=NaiveBayesAnalyzer())
blob.sentiment
# Sentiment(classification='pos', p_pos=0.799, p_neg=0.201)
```

### Training

The NaiveBayesAnalyzer trains lazily on first use. It loads the NLTK movie_reviews corpus (positive and negative reviews) and trains an NLTK NaiveBayesClassifier. Requires the `movie_reviews` corpus:

```python
import nltk
nltk.download('movie_reviews')
```

### Custom Feature Extractor

Pass a custom feature extractor function to the constructor:

```python
def my_extractor(words):
    return {word: True for word in words if len(word) > 3}

analyzer = NaiveBayesAnalyzer(feature_extractor=my_extractor)
blob = TextBlob("text here", analyzer=analyzer)
```

## Choosing an Analyzer

- **PatternAnalyzer**: Fast, no training needed, continuous scores. Good for general-purpose sentiment approximation.
- **NaiveBayesAnalyzer**: Trained on movie reviews, discrete classification with probabilities. Better for domain-specific tasks where you can retrain with custom data.

## Analyzer Kind Constants

The `textblob.base` module defines:

- `CONTINUOUS` — Analyzers that return continuous scores (PatternAnalyzer)
- `DISCRETE` — Analyzers that return discrete classifications (NaiveBayesAnalyzer)

Access via `analyzer.kind`.
