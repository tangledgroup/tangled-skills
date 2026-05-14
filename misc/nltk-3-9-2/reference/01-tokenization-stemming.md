# Tokenization & Stemming

## Word Tokenizers

### TreebankWordTokenizer

The standard English word tokenizer. Handles contractions, punctuation separation, and quotes correctly. Used internally by `nltk.word_tokenize()`.

```python
from nltk.tokenize import word_tokenize, TreebankWordTokenizer

tokenizer = TreebankWordTokenizer()
tokens = tokenizer.tokenize("It's a nice day, isn't it?")
print(tokens)
# ['It', "'s", 'a', 'nice', 'day', ',', 'is', "n't", 'it', '?']
```

Convenience function:

```python
from nltk.tokenize import word_tokenize
tokens = word_tokenize("Hello world!")
# ['Hello', 'world', '!']
```

### TweetTokenizer

Handles Twitter-specific patterns: hashtags, mentions, URLs, emojis (including ZWJ sequences and skin tone modifiers), elongated words, and phone numbers.

```python
from nltk.tokenize import TweetTokenizer

tokenizer = TweetTokenizer(
    reduce_length=True,   # collapse 'sooo' -> 'soo'
    strip_handles=True    # remove '@username'
)
tokens = tokenizer.tokenize("Check out @nltk! It's sooo cool 🔥")
# ['Check', 'out', 'It', "'s", 'soo', 'cool', '🔥']
```

### RegexpTokenizer

Tokenize using regular expressions. Can include matching patterns or split on them with `underscore=True`.

```python
from nltk.tokenize import RegexpTokenizer

# Tokenize on word characters (alphanumeric + underscore)
tokenizer = RegexpTokenizer(r'\w+')
tokens = tokenizer.tokenize("Hello, world! It's 2025.")
# ['Hello', 'world', 'It', 's', '2025']

# Tokenize on alphanumeric sequences
tokenizer = RegexpTokenizer(r'[a-zA-Z0-9]+')
```

### WordPunctTokenizer

Splits words and punctuation into separate tokens. Useful when punctuation carries meaning.

```python
from nltk.tokenize import wordpunct_tokenize
tokens = wordpunct_tokenize("Hello, world!")
# ['Hello', ',', 'world', '!']
```

### Simple Tokenizers

```python
from nltk.tokenize import WhitespaceTokenizer, BlanklineTokenizer, LineTokenizer, SpaceTokenizer, TabTokenizer, CharTokenizer

# Whitespace-based tokenization
tokens = WhitespaceTokenizer().tokenize("Hello world")
# ['Hello', 'world']

# Line-based tokenization
lines = LineTokenizer().tokenize("Line 1\nLine 2\nLine 3")
```

## Sentence Tokenization

### PunktSentenceTokenizer

Unsupervised sentence boundary detector. Trains on text to learn abbreviations, collocations, and sentence starters. Pre-trained models available for multiple languages.

```python
from nltk.tokenize import sent_tokenize, PunktSentenceTokenizer

# Using pre-trained English model
sentences = sent_tokenize("Dr. Smith went to Washington. The weather was nice.")
# ['Dr. Smith went to Washington.', 'The weather was nice.']

# Available language models
nltk.download('punkt')        # English (default)
nltk.download('punkt_tab')    # Updated punkt with tab-separated data
```

### Training a Custom Punkt Model

```python
from nltk.tokenize.punkt import PunktTrainer, PunktParameters, load_punkt_params

trainer = PunktTrainer()
trainer.train(open('training_text.txt').read(), lenient=False)
params = trainer.get_params()

tokenizer = PunktSentenceTokenizer(params)
sentences = tokenizer.tokenize("Your custom text here.")
```

### Language-Specific Models

Download language-specific punkt models:

```python
nltk.download('punkt')  # English, German, Spanish, French, Italian, Portuguese, Dutch, Finnish
```

Available via `PunktLanguageVars` for: English, German, Spanish, French, Italian, Portuguese, Dutch, Finnish.

## Multi-Word Expression Tokenizer

Preserves multi-word expressions as single tokens:

```python
from nltk.tokenize import MWETokenizer

mwe_tok = MWETokenizer()
mwe_tok.add_mwe(('New', 'York'))
mwe_tok.add_mwe(('Natural', 'Language', 'Processing'))

tokens = mwe_tok.tokenize(['New', 'York', 'is', 'great', 'for', 'Natural', 'Language', 'Processing'])
# [('New', 'York'), 'is', 'great', 'for', ('Natural', 'Language', 'Processing')]
```

## Detokenization

Reconstruct text from token lists:

```python
from nltk.tokenize import TreebankWordDetokenizer

detokenizer = TreebankWordDetokenizer()
text = detokenizer.detokenize(['It', "'s", 'a', 'nice', 'day', '.'])
# "It's a nice day."
```

## Stemmers

Stemming removes morphological affixes to produce word stems. Faster than lemmatization but may produce non-dictionary forms.

### PorterStemmer

The classic Porter algorithm for English:

```python
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()
print(stemmer.stem('running'))   # 'run'
print(stemmer.stem('happier'))   # 'happi'
print(stemmer.stem('countries')) # 'countri'
```

### SnowballStemmer (Porter2)

Improved Porter algorithm with support for 17+ languages:

```python
from nltk.stem import SnowballStemmer

# English
stemmer = SnowballStemmer('english')
print(stemmer.stem('running'))   # 'run'

# Other languages
french_stemmer = SnowballStemmer('french')
german_stemmer = SnowballStemmer('german')
spanish_stemmer = SnowballStemmer('spanish')

# Available languages
print(SnowballStemmer.languages)
# ['danish', 'dutch', 'english', 'finnish', 'french', 'german', 'hungarian',
#  'italian', 'norwegian', 'portuguese', 'romanian', 'russian', 'spanish', 'swedish']
```

### LancasterStemmer

Aggressive English stemmer producing shorter stems:

```python
from nltk.stem import LancasterStemmer

stemmer = LancasterStemmer()
print(stemmer.stem('running'))   # 'run'
print(stemmer.stem('connections')) # 'connect'
```

### RegexpStemmer

Stem using regular expression substitution:

```python
from nltk.stem import RegexpStemmer

stemmer = RegexpStemmer('ing$|ed$|es$|s$', min_stem_length=3)
print(stemmer.stem('running'))   # 'run'
print(stemmer.stem('cats'))      # 'cat'
```

### Language-Specific Stemmers

**Arabic**: ARLSTem, ARLSTem2, ISRIStemmer

```python
from nltk.stem import ARLSTem, ISRIStemmer
```

**German**: Cistem

```python
from nltk.stem import Cistem
stemmer = Cistem()
```

**Portuguese (Brazilian)**: RSLPStemmer

```python
from nltk.stem import RSLPStemmer
stemmer = RSLPStemmer()
```

## Lemmatization

Lemmatization uses WordNet to map words to their dictionary form (lemma), producing valid words. Requires POS tag hints for accuracy.

```python
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize

lemmatizer = WordNetLemmatizer()

# Basic lemmatization (defaults to noun)
print(lemmatizer.lemmatize('running'))    # 'run'
print(lemmatizer.lemmatize('better'))     # 'bet' (wrong without POS hint)
print(lemmatizer.lemmatize('better', 'a')) # 'good' (adjective)

# Mapping POS tags to WordNet POS codes
from nltk.corpus import wordnet as wn

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('N'):
        return wn.NOUN
    elif treebank_tag.startswith('R'):
        return wn.ADV
    else:
        return wn.NOUN

tokens = word_tokenize("The runners were running quickly")
tagged = pos_tag(tokens)
lemmas = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in tagged]
# ['the', 'runner', 'were', 'run', 'quickly']
```

### morphy()

Find all possible lemmas for a word:

```python
print(lemmatizer.morphy('running'))     # 'run'
print(lemmatizer.morphy('ran'))         # None (irregular, needs context)
print(lemmatizer.morphy('cats', wn.NOUN)) # 'cat'
```
