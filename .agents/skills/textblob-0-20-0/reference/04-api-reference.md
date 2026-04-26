# API Reference

## TextBlob

Main class for text processing. Inherits from BaseBlob.

```python
from textblob import TextBlob
blob = TextBlob("text here", tokenizer=None, pos_tagger=None, np_extractor=None, analyzer=None, parser=None, classifier=None)
```

### Properties

- `raw` / `string` — The original text string
- `stripped` — Lowercased text with whitespace stripped
- `words` — WordList of word tokens (excludes punctuation). As of 0.20.0, respects custom tokenizer
- `tokens` — WordList of all tokens (includes punctuation)
- `sentences` — List of Sentence objects
- `raw_sentences` — List of raw sentence strings
- `noun_phrases` — WordList of extracted noun phrases (lowercased)
- `pos_tags` / `tags` — List of `(Word, tag)` tuples with Penn Treebank POS tags
- `sentiment` — Namedtuple `Sentiment(polarity, subjectivity)` from the analyzer
- `sentiment_assessments` — Namedtuple with polarity, subjectivity, and per-token assessments
- `polarity` — Float in [-1.0, 1.0] (convenience property using PatternAnalyzer)
- `subjectivity` — Float in [0.0, 1.0] (convenience property using PatternAnalyzer)
- `word_counts` — Dictionary of word frequencies (case-insensitive)
- `np_counts` — Dictionary of noun phrase frequencies
- `serialized` — List of dict representations for each sentence
- `json` — JSON string representation of serialized data

### Methods

- `ngrams(n=3)` — Returns list of WordLists, each containing n successive words
- `correct()` — Attempt spelling correction, returns new TextBlob
- `tokenize(tokenizer=None)` — Tokenize using specified or default tokenizer
- `parse(parser=None)` — Parse text using specified or default parser
- `classify()` — Classify using the blob's classifier (must be set)
- `to_json(*args, **kwargs)` — JSON representation (same args as json.dumps)

### String-like Operations

- `blob[start:end]` — Slicing returns new TextBlob
- `blob.upper()`, `blob.lower()`, etc. — Standard string methods return TextBlob
- `blob1 + blob2` — Concatenation returns TextBlob
- `blob == "string"` — Comparison with strings works
- `hash(blob)` — Hashable

## Sentence

A sentence within a TextBlob. Inherits all BaseBlob properties and methods.

```python
# Created automatically by TextBlob.sentences
for s in blob.sentences:
    print(s)           # The sentence text
    print(s.start)     # Character index where sentence starts
    print(s.end)       # Character index where sentence ends
    print(s.sentiment) # Sentiment of this sentence
    print(s.classify())# Classification if classifier is set
```

### Additional Properties

- `start` / `start_index` — Character index within parent TextBlob
- `end` / `end_index` — Character index where sentence ends
- `dict` — Dictionary representation with raw text, indices, noun phrases, polarity, subjectivity

## Word

A string subclass with NLP methods.

```python
from textblob import Word
w = Word("octopi", pos_tag=None)
```

### Methods

- `singularize()` — Return singular form as Word
- `pluralize()` — Return plural form as Word
- `lemmatize(pos=None)` — Return lemma using WordNet morphy. Pass `'n'`, `'v'`, `'a'`, `'r'` for POS
- `stem(stemmer=PorterStemmer)` — Stem using NLTK stemmer (Porter, Lancaster, or Snowball)
- `spellcheck()` — Return list of `(word, confidence)` tuples
- `correct()` — Return corrected Word (highest confidence spelling)

### Properties

- `string` — The word string
- `pos_tag` — POS tag if set
- `synsets` — List of Synset objects for this word
- `definitions` — List of definition strings (one per synset)

### WordNet Methods

- `get_synsets(pos=None)` — Return Synset list, optionally filtered by POS (`nltk.corpus.wordnet.NOUN`, `VERB`, `ADJ`, `ADV`)
- `define(pos=None)` — Return definition list, optionally filtered by POS

### Stemmers (class attributes)

- `Word.PorterStemmer` — NLTK Porter stemmer
- `Word.LancasterStemmer` — NLTK Lancaster stemmer
- `Word.SnowballStemmer` — NLTK Snowball stemmer (English)

## WordList

A list subclass containing Word objects.

```python
wl = TextBlob("cat dog octopus").words  # WordList(['cat', 'dog', 'octopus'])
```

### Methods

- `upper()` — Return new WordList with uppercased words
- `lower()` — Return new WordList with lowercased words
- `singularize()` — Return new WordList with singular forms
- `pluralize()` — Return new WordList with plural forms
- `lemmatize()` — Return new WordList with lemmas
- `stem(*args, **kwargs)` — Return new WordList with stems
- `count(strg, case_sensitive=False)` — Count occurrences (default case-insensitive)
- `append(obj)` — Append Word or string
- `extend(iterable)` — Extend with Words
- `split(sep=None, maxsplit=maxsize)` — Split by separator, returns WordList

## Blobber

Factory for TextBlobs sharing the same models.

```python
from textblob import Blobber
tb = Blobber(tokenizer=..., pos_tagger=..., np_extractor=..., analyzer=..., parser=..., classifier=...)
blob = tb("text")  # Returns TextBlob with shared models
```

Default models: `WordTokenizer`, `NLTKTagger`, `FastNPExtractor`, `PatternAnalyzer`, `PatternParser`.

## Module Reference

### textblob.sentiments

- `PatternAnalyzer` — Lexicon-based sentiment analyzer (default)
- `NaiveBayesAnalyzer(feature_extractor=...)` — ML-based sentiment analyzer trained on movie reviews

### textblob.taggers

- `NLTKTagger` — Penn Treebank averaged perceptron tagger (default)
- `PatternTagger` — Pattern library tagger

### textblob.np_extractors

- `FastNPExtractor` — Fast rule-based noun phrase extractor (default)
- `ConllExtractor` — CoNLL-2000 based noun phrase extractor

### textblob.parsers

- `PatternParser` — Pattern library parser (default)

### textblob.classifiers

- `NaiveBayesClassifier(train_set, feature_extractor=basic_extractor, format=None)`
- `DecisionTreeClassifier(train_set, feature_extractor=basic_extractor, format=None)`
- `MaxEntClassifier(train_set, feature_extractor=basic_extractor, format=None)`
- `PositiveNaiveBayesClassifier(positive_set, unlabeled_set, feature_extractor=contains_extractor, positive_prob_prior=0.5)`
- `basic_extractor(document, train_set)` — Default feature extractor
- `contains_extractor(document)` — Feature extractor for positive-only classification

### textblob.tokenizers

- `WordTokenizer` — NLTK TreeBank word tokenizer
- `SentenceTokenizer` — NLTK Punkt sentence tokenizer
- `word_tokenize(text, include_punc=True)` — Convenience function
- `sent_tokenize(text)` — Convenience function

### textblob.wordnet

- `Synset(name)` — Create Synset directly (e.g., `Synset('octopus.n.01')`)
- `Lemma(synset, name)` — Create Lemma directly
- `VERB`, `NOUN`, `ADJ`, `ADV` — POS constants for filtering

### textblob.base

Abstract base classes for custom implementations:

- `BaseTagger` — Implement `tag(text)`
- `BaseNPExtractor` — Implement `extract(text)`
- `BaseTokenizer` — Implement `tokenize(text)`, provides `itokenize()`
- `BaseSentimentAnalyzer` — Implement `analyze(text)`, call `train()` lazily
- `BaseParser` — Implement `parse(text)`
- `CONTINUOUS` — Kind constant for continuous-score analyzers
- `DISCRETE` — Kind constant for discrete-classification analyzers

### textblob.formats

File format classes for classifier data:

- `CSVFormat`, `JSONFormat`, `TSVFormat` — Built-in formats
- `get_registry()` — Get dict of registered formats
- `register(name, format_class)` — Register custom format
- `detect(stream)` — Auto-detect format from stream
