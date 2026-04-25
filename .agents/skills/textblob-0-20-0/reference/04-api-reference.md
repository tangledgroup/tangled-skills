# API Reference Summary

This reference provides a summary of TextBlob 0.20.0's public API. For complete documentation, see the official docs at https://textblob.readthedocs.io/.

## Core Classes

### TextBlob

Main class for text processing.

```python
from textblob import TextBlob

blob = TextBlob(
    text,              # String to process
    pos_tagger=None,   # POSTagger instance (default: PatternTagger)
    np_extractor=None, # BaseNPExtractor instance (default: FastNPExtractor)
    analyzer=None,     # BaseSentimentAnalyzer (default: PatternAnalyzer)
    tokenizer=None,    # Tokenizer instance
    classifier=None,   # BaseClassifier instance
    parser=None        # BaseParser instance (default: PatternParser)
)
```

#### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `words` | WordList | List of words in the text |
| `sentences` | list[Sentence] | List of Sentence objects |
| `tags` | list[(str, str)] | List of (word, POS tag) tuples |
| `noun_phrases` | WordList | Extracted noun phrases |
| `sentiment` | Sentiment | Polarity and subjectivity scores |
| `sentiment_assessments` | list | Detailed sentiment assessments |
| `word_counts` | dict[str, int] | Word frequency dictionary (case-insensitive) |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `tags()` | list[(str, str)] | Part-of-speech tags |
| `noun_phrases()` | WordList | Noun phrase extraction |
| `sentiment` | Sentiment | Sentiment analysis |
| `parse()` | str | Parsed text with chunk/phrase info |
| `ngrams(n=2)` | list[WordList] | N-grams of words |
| `correct()` | TextBlob | Spelling correction |
| `classify()` | str | Classification (requires classifier) |
| `prob_classify()` | ProbDist | Probability distribution (requires classifier) |
| `tokenize(tokenizer)` | WordList | Tokenize with custom tokenizer |
| `upper()` | TextBlob | Uppercase text |
| `lower()` | TextBlob | Lowercase text |
| `find(substring)` | int | Find substring index |

#### String-like Operations

TextBlobs support:
- Slicing: `blob[0:10]`
- Comparison: `blob == "string"`
- Concatenation: `blob1 + blob2`
- Formatting: `f"{blob}"`

### Sentence

Represents a single sentence within a TextBlob.

```python
# Sentences have the same API as TextBlob
sentence = blob.sentences[0]
print(sentence.tags)        # POS tags for sentence
print(sentence.sentiment)   # Sentiment of sentence
print(sentence.words)       # Words in sentence
```

#### Additional Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `start` | int | Start index in parent TextBlob |
| `end` | int | End index in parent TextBlob |

### Word

Represents a single word with NLP methods.

```python
from textblob import Word

w = Word("running")
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `singularize()` | str | Singular form |
| `pluralize()` | str | Plural form |
| `lemmatize(pos=None)` | str | Lemma (base form) |
| `stem()` | str | Stemmed form |
| `spellcheck()` | list[(str, float)] | Spelling suggestions with confidence |

#### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `synsets` | list[Synset] | WordNet synsets |
| `definitions` | list[str] | WordNet definitions |

#### Methods for WordNet

| Method | Returns | Description |
|--------|---------|-------------|
| `get_synsets(pos=None)` | list[Synset] | Synsets filtered by POS |
| `define(pos=None)` | list[str] | Definitions filtered by POS |

### WordList

List of Word objects with batch operations.

```python
words = blob.words  # Returns WordList
```

#### Batch Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `singularize()` | WordList | Singularize all words |
| `pluralize()` | WordList | Pluralize all words |
| `stem()` | WordList | Stem all words |
| `lemmatize(pos=None)` | WordList | Lemmatize all words |
| `count(word, case_sensitive=False)` | int | Count occurrences |

#### List Operations

WordList supports standard list operations:
- Indexing: `words[0]`
- Slicing: `words[0:5]`
- Iteration: `for word in words:`
- Length: `len(words)`

## Blobber Factory

### Blobber

Factory class for creating TextBlobs with shared components.

```python
from textblob import Blobber

blobber = Blobber(
    pos_tagger=None,     # POSTagger instance
    np_extractor=None,   # BaseNPExtractor instance
    analyzer=None,       # BaseSentimentAnalyzer
    tokenizer=None,      # Tokenizer instance
    classifier=None,     # BaseClassifier instance
    parser=None          # BaseParser instance
)

# Create TextBlob with shared components
blob = blobber("Some text to process.")
```

## Classifiers

### NaiveBayesClassifier

Naive Bayes text classifier.

```python
from textblob.classifiers import NaiveBayesClassifier

classifier = NaiveBayesClassifier(
    train_set,              # Training data or file object
    feature_extractor=None  # Custom feature extractor function
)
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `classify(doc)` | str | Classify document |
| `prob_classify(doc)` | ProbDist | Probability distribution |
| `accuracy(test_set)` | float | Accuracy on test data |
| `update(new_data)` | bool | Add new training data |
| `show_informative_features(n)` | None | Display top features |
| `labels()` | list | Available class labels |

### DecisionTreeClassifier

Decision tree classifier.

```python
from textblob.classifiers import DecisionTreeClassifier

classifier = DecisionTreeClassifier(
    train_set,              # Training data
    feature_extractor=None  # Custom feature extractor
)
```

#### Methods

Same as NaiveBayesClassifier plus:
| Method | Returns | Description |
|--------|---------|-------------|
| `pprint()` | None | Print tree structure |

### MaxEntClassifier

Maximum Entropy classifier (requires NumPy).

```python
from textblob.classifiers import MaxEntClassifier

classifier = MaxEntClassifier(
    train_set,              # Training data
    feature_extractor=None  # Custom feature extractor
)
```

#### Methods

Same as NaiveBayesClassifier.

### ProbDist

Probability distribution over class labels.

```python
prob_dist = classifier.prob_classify("Some text")
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `max()` | str | Most likely label |
| `prob(label)` | float | Probability of label |
| `labels()` | list | All available labels |

## Taggers

### PatternTagger

Default POS tagger based on pattern library.

```python
from textblob.taggers import PatternTagger

tagger = PatternTagger()
tags = tagger.tag(["Python", "is", "great"])
# [('Python', 'NNP'), ('is', 'VBZ'), ('great', 'JJ')]
```

### NLTKTagger

NLTK-based POS tagger (requires NumPy).

```python
from textblob.taggers import NLTKTagger

tagger = NLTKTagger()
tags = tagger.tag(["Python", "is", "great"])
# [(Word('Python'), 'NNP'), (Word('is'), 'VBZ'), ...]
```

## Noun Phrase Extractors

### FastNPExtractor

Default fast noun phrase extractor.

```python
from textblob.np_extractors import FastNPExtractor

extractor = FastNPExtractor()
phrases = extractor.extract_noun_phrases(tagged_words)
```

### ConllExtractor

CoNLL-based noun phrase extractor.

```python
from textblob.np_extractors import ConllExtractor

extractor = ConllExtractor()
phrases = extractor.extract_noun_phrases(tagged_words)
```

## Sentiment Analyzers

### PatternAnalyzer

Default sentiment analyzer based on pattern library.

```python
from textblob.sentiments import PatternAnalyzer

analyzer = PatternAnalyzer()
sentiment = analyzer("This is great!")
# Sentiment(polarity=0.5, subjectivity=0.6)
```

### NaiveBayesAnalyzer

ML-based sentiment analyzer.

```python
from textblob.sentiments import NaiveBayesAnalyzer

analyzer = NaiveBayesAnalyzer()
sentiment = analyzer("This is great!")
# Sentiment(classification='pos', p_pos=0.8, p_neg=0.2)
```

## Tokenizers

### WordTokenizer

Default word tokenizer.

```python
from textblob.tokenizers import WordTokenizer

tokenizer = WordTokenizer()
words = tokenizer.tokenize("Hello world.")
# ['Hello', 'world.']
```

### SentenceTokenizer

NLTK-based sentence tokenizer.

```python
from textblob.tokenizers import SentenceTokenizer

tokenizer = SentenceTokenizer()
sentences = tokenizer.tokenize("First sentence. Second sentence.")
# ['First sentence.', 'Second sentence.']
```

### Convenience Functions

```python
from textblob.tokenizers import word_tokenize, sent_tokenize

words = word_tokenize("Hello world.")
# ['Hello', 'world.']

sentences = sent_tokenize("First. Second.")
# ['First.', 'Second.']
```

## Parsers

### PatternParser

Default parser based on pattern library.

```python
from textblob.parsers import PatternParser

parser = PatternParser()
parsed = parser.parse("The cat runs.")
# The/DT/B-NP/O cat/NN/I-NP/O runs/VBZ/B-VP/O ././O/O
```

## WordNet

### Synset

WordNet synset (sense of a word).

```python
from textblob.wordnet import Synset

synset = Synset("octopus.n.02")
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `path_similarity(other)` | float | Path similarity score |
| `wup_similarity(other)` | float | Wu-Palmer similarity |
| `lch_similarity(other)` | float | Leacock-Chordidor similarity |

### WordNet Constants

```python
from textblob.wordnet import NOUN, VERB, ADJ, ADV

# Use with Word methods
Word("running").lemmatize(pos=VERB)  # 'run'
Word("octopus").get_synsets(pos=NOUN)
```

## File Formats

### Format Classes

For loading training data:

```python
from textblob.formats import Csv, Json, Tsv

# CSV format
with open('data.csv', 'r') as fp:
    csv_format = Csv(fp)
    data = list(csv_format)

# JSON format
with open('data.json', 'r') as fp:
    json_format = Json(fp)
    data = list(json_format)

# TSV format
with open('data.tsv', 'r') as fp:
    tsv_format = Tsv(fp)
    data = list(tsv_format)
```

### Custom Format Registration

```python
from textblob.formats import register, get_registry

# Register custom format
register('myformat', MyFormatClass)

# Get all registered formats
registry = get_registry()
```

## Exceptions

### TextBlobError

Base exception for TextBlob errors.

### MissingCorpusError

Raised when required NLTK corpora are not downloaded.

```python
from textblob.exceptions import MissingCorpusError

try:
    blob = TextBlob("Some text.")
    _ = blob.tags
except MissingCorpusError:
    print("Run: python -m textblob.download_corpora")
```

### DeprecationError

Raised when using deprecated features.

### TranslatorError

Base exception for translation errors (translation removed in 0.18+).

### NotTranslated

Raised when translation fails or text is unchanged.

### FormatError

Raised when data format is invalid.

## Module Structure

```
textblob/
├── blob/
│   ├── TextBlob
│   ├── Sentence
│   ├── Word
│   ├── WordList
│   └── Blobber
├── classifiers/
│   ├── NaiveBayesClassifier
│   ├── DecisionTreeClassifier
│   └── MaxEntClassifier
├── taggers/
│   ├── PatternTagger
│   └── NLTKTagger
├── np_extractors/
│   ├── FastNPExtractor
│   └── ConllExtractor
├── sentiments/
│   ├── PatternAnalyzer
│   └── NaiveBayesAnalyzer
├── tokenizers/
│   ├── WordTokenizer
│   ├── SentenceTokenizer
│   ├── word_tokenize()
│   └── sent_tokenize()
├── parsers/
│   └── PatternParser
├── wordnet/
│   ├── Synset
│   ├── NOUN
│   ├── VERB
│   ├── ADJ
│   └── ADV
├── formats/
│   ├── Csv
│   ├── Json
│   ├── Tsv
│   ├── register()
│   └── get_registry()
└── exceptions/
    ├── TextBlobError
    ├── MissingCorpusError
    ├── DeprecationError
    ├── TranslatorError
    ├── NotTranslated
    └── FormatError
```

## Type Hints

### Sentiment NamedTuples

PatternAnalyzer returns:
```python
Sentiment(
    polarity: float,      # -1.0 to 1.0
    subjectivity: float   # 0.0 to 1.0
)
```

NaiveBayesAnalyzer returns:
```python
Sentiment(
    classification: str,  # 'pos' or 'neg'
    p_pos: float,         # Probability positive
    p_neg: float          # Probability negative
)
```

### Common Return Types

| Operation | Return Type |
|-----------|-------------|
| `blob.tags` | `list[tuple[str, str]]` |
| `blob.words` | `WordList` |
| `blob.sentences` | `list[Sentence]` |
| `blob.noun_phrases` | `WordList` |
| `blob.sentiment` | `Sentiment` |
| `classifier.classify()` | `str` |
| `classifier.prob_classify()` | `ProbDist`` |
| `word.spellcheck()` | `list[tuple[str, float]]` |

## Version Compatibility

### Python Versions

- Requires: Python >= 3.10
- Tested: 3.10, 3.11, 3.12, 3.13, 3.14

### NLTK Compatibility

- Requires: NLTK >= 3.9

### Optional Dependencies

| Feature | Dependency |
|---------|------------|
| NLTKTagger | NumPy |
| MaxEntClassifier | NumPy |

## Deprecated Features

The following features were removed in version 0.18+:

- `TextBlob.translate()` - Use Google Translate API
- `TextBlob.detect_language()` - Use language detection libraries
- `textblob.translate` module
- `textblob.compat` module
