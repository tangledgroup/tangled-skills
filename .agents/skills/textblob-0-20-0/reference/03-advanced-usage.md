# Advanced Usage

TextBlob allows overriding all underlying models — tokenizers, POS taggers, noun phrase extractors, sentiment analyzers, parsers, and classifiers. This is done either per-blob via constructor parameters or globally via the Blobber factory class.

## Overriding Models Per-Blob

Pass model instances to the TextBlob constructor:

```python
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from textblob.taggers import PatternTagger
from textblob.np_extractors import ConllExtractor

blob = TextBlob(
    "Some text to analyze.",
    pos_tagger=PatternTagger(),
    np_extractor=ConllExtractor(),
    analyzer=NaiveBayesAnalyzer()
)
```

## The Blobber Factory

`Blobber` creates TextBlobs that share the same model instances. Useful for batch processing where you want consistent models across multiple blobs:

```python
from textblob import Blobber
from textblob.taggers import NLTKTagger
from textblob.sentiments import NaiveBayesAnalyzer

tb = Blobber(
    pos_tagger=NLTKTagger(),
    analyzer=NaiveBayesAnalyzer()
)

blob1 = tb("First document text.")
blob2 = tb("Second document text.")
blob1.pos_tagger is blob2.pos_tagger  # True
```

## Tokenizers

### WordTokenizer (default)

NLTK's TreeBankTokenizer. Splits contractions, handles commas and quotes, separates end-of-line periods.

```python
from textblob.tokenizers import WordTokenizer

tokenizer = WordTokenizer()
tokenizer.tokenize("Hello, world!")  # ['Hello', ',', 'world', '!']
tokenizer.tokenize("Hello, world!", include_punc=False)  # ['Hello', 'world']
```

### SentenceTokenizer

NLTK's PunktSentenceTokenizer. Builds a model for abbreviations, collocations, and sentence-starting words.

```python
from textblob.tokenizers import SentenceTokenizer

tokenizer = SentenceTokenizer()
tokenizer.tokenize("Dr. Smith went home. He said hello.")
# ['Dr. Smith went home.', 'He said hello.']
```

### Custom Tokenizers (0.20.0+)

As of version 0.20.0, you can use a custom tokenizer for the `.words` property:

```python
from textblob import TextBlob
from textblob.base import BaseTokenizer

class MyTokenizer(BaseTokenizer):
    def tokenize(self, text):
        return text.split()

blob = TextBlob("Custom tokenized text.", tokenizer=MyTokenizer())
blob.words  # Uses MyTokenizer instead of default WordTokenizer
```

When a custom tokenizer is used, token filtering (punctuation removal) is deferred to the tokenizer itself. The default `WordTokenizer` path preserves historical no-punctuation behavior.

### Convenience Functions

```python
from textblob.tokenizers import word_tokenize, sent_tokenize

word_tokenize("Hello world")    # Generator of word tokens
sent_tokenize("One. Two.")      # List of sentences
```

## POS Taggers

### NLTKTagger (default)

Uses NLTK's averaged perceptron tagger trained on the Penn Treebank. Returns Penn Treebank POS tags (NN, VB, JJ, etc.).

```python
from textblob.taggers import NLTKTagger

tagger = NLTKTagger()
tagger.tag("Python is great.")
# [('Python', 'NNP'), ('is', 'VBZ'), ('great', 'JJ'), ('.', '.')]
```

### PatternTagger

Uses the pattern library's tagger. May differ slightly from NLTKTagger in accuracy and tag set.

```python
from textblob.taggers import PatternTagger

tagger = PatternTagger()
tagger.tag("Python is great.")
```

## Noun Phrase Extractors

### FastNPExtractor (default)

Fast rule-based extractor. Uses a simplified version of the noun phrase chunking algorithm.

```python
from textblob.np_extractors import FastNPExtractor

extractor = FastNPExtractor()
extractor.extract("The natural language processing toolkit is great.")
# ['the natural language processing toolkit', 'great']
```

### ConllExtractor

Uses the CoNLL-2000 chunking corpus for more accurate extraction. Slower than FastNPExtractor but potentially more precise.

```python
from textblob.np_extractors import ConllExtractor

extractor = ConllExtractor()
extractor.extract("The quick brown fox.")
```

## Parsers

### PatternParser (default)

Uses the pattern library's parser. Returns IOB-format tagged chunks:

```python
from textblob.parsers import PatternParser

parser = PatternParser()
parser.parse("And now for something completely different.")
# And/CC/O/O now/RB/B-ADVP/O for/IN/B-PP/B-PNP ...
```

Format: `word/POS/chunk-tag/pnp-tag` where chunk-tag uses BIO format (B-begin, I-inside, O-outside).

## Base Classes for Custom Implementations

All models inherit from abstract base classes in `textblob.base`:

- **BaseTagger** — Implement `tag(text)` returning `list[tuple[str, str]]`
- **BaseNPExtractor** — Implement `extract(text)` returning `list[str]`
- **BaseTokenizer** — Implement `tokenize(text)` returning `list[str]`. Also provides `itokenize()` for generator-based tokenization.
- **BaseSentimentAnalyzer** — Implement `analyze(text)`. Call `self.train()` lazily. Set `self._trained = True` after training.
- **BaseParser** — Implement `parse(text)`

Example custom sentiment analyzer:

```python
from textblob.base import BaseSentimentAnalyzer, CONTINUOUS

class MyAnalyzer(BaseSentimentAnalyzer):
    kind = CONTINUOUS

    def train(self):
        # Load your model
        self._trained = True

    def analyze(self, text):
        if not self._trained:
            self.train()
        # Return (polarity, subjectivity) tuple
        return (0.5, 0.3)
```

## Extensions Framework

TextBlob supports adding custom models and new languages through extensions. Extensions are installed as separate PyPI packages (e.g., `textblob-aptagger` for the averaged perceptron tagger).

The refactored architecture in version 0.7.0+ moved all English-specific code to `textblob.en`, making it easier to develop language extensions.
