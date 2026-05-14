# Corpora & Data

## NLTK Data System

### Downloading Data

```python
import nltk

# Interactive downloader (GUI)
nltk.download()

# Download specific packages
nltk.download('punkt')           # Sentence tokenizer models
nltk.download('averaged_perceptron_tagger')  # POS tagger
nltk.download('wordnet')         # WordNet lexical database
nltk.download('brown')           # Brown Corpus
nltk.download('movie_reviews')   # Sentiment analysis corpus
nltk.download('vader_lexicon')   # VADER sentiment lexicon

# Download collections
nltk.download('popular')  # Most commonly used data
nltk.download('book')     # Data needed for NLTK book exercises
nltk.download('all')      # Everything
nltk.download('all-corpora')  # All corpora, no models/grammars
```

### Command Line Download

```bash
python -m nltk.downloader popular
python -m nltk.downloader all
python -m nltk.downloader -d /custom/path punkt
```

### Data Locations

NLTK searches for data in these paths (in order):

1. `NLTK_DATA` environment variable
2. `~/.nltk/`
3. `/usr/share/nltk_data/` (Unix)
4. `/usr/local/share/nltk_data/` (Mac)
5. `C:\nltk_data` (Windows)

Directory structure:

```
nltk_data/
├── corpora/
│   ├── brown/
│   ├── gutenberg/
│   └── wordnet/
├── taggers/
│   └── averaged_perceptron_tagger/
├── tokenizers/
│   └── punkt/
├── chunkers/
├── grammars/
├── sentiment/
│   └── vader_lexicon/
├── models/
├── stemmers/
└── misc/
```

### Proxy Configuration

```python
nltk.set_proxy('http://proxy.example.com:3128', ('username', 'password'))
nltk.download('punkt')
```

## Corpus Readers

All NLTK corpora share a common API through the `CorpusReader` base class.

### Plaintext Corpora

```python
from nltk.corpus import gutenberg, webtext, nps_chat

# Gutenberg
print(gutenberg.fileids())
# ['austen-emma.txt', 'melville-moby_dick.txt', ...]
print(gutenberg.words('melville-moby_dick.txt')[:10])
print(gutenberg.sents('melville-moby_dick.txt')[:2])
print(gutenberg.raw('melville-moby_dick.txt')[:200])

# Web text (blogs, chat logs, overheard conversations)
print(webtext.fileids())
# ['firefox.txt', 'grail.txt', 'overheard.txt', ...]
print(webtext.words('grail.txt')[:10])

# NPS Chat Corpus
print(nps_chat.words()[:20])
```

### Tagged Corpora

```python
from nltk.corpus import brown, conll2000, treebank

# Brown Corpus — 1 million words, 15 categories
print(brown.categories())
# ['adventure', 'belles_lettres', 'editorial', ...]
print(brown.words(categories='news')[:10])
print(brown.sents(categories='news')[:2])
print(brown.tagged_words(categories='news')[:5])
print(brown.tagged_sents(categories='news')[:1])

# CoNLL 2000 — chunked corpus
print(conll2000.chunked_sents()[:1])

# Penn Treebank
print(treebank.words()[:10])
print(treebank.tagged_words()[:5])
print(treebank.sents()[:1])
```

### Parsed Corpora

```python
from nltk.corpus import treebank, alpino, sinica_treebank

# Penn Treebank parsed sentences
print(treebank.parsed_sents()[:1])
tree = treebank.parsed_sents('wsj_0001.mrg')[0]
tree.pprint()

# Alpino (Dutch)
print(alpino.fileids()[:5])
print(alpino.parsed_sents()[:1])
```

### Categorized Corpora

Corpora with category metadata for conditional analysis:

```python
from nltk.corpus import movie_reviews, inaugural

# Movie Reviews — labeled 'pos' or 'neg'
print(movie_reviews.categories())  # ['neg', 'pos']
print(movie_reviews.fileids(categories='pos')[:5])

# Inaugural addresses — categorized by year
print(inaugural.fileids())
print(inaugural.categories())
```

### Specialized Corpora

**CMU Pronouncing Dictionary**:

```python
from nltk.corpus import cmudict
pronunciations = cmudict.dict()
print(pronunciations['cat'])  # [['K', 'AE1', 'T']]
```

**Senseval / Semcor** (word sense disambiguation):

```python
from nltk.corpus import semcor
print(semcor.tagged_sents()[:1])
```

**VerbNet** (verb lexicon with semantic classes):

```python
from nltk.corpus import verbnet
print(verbnet.lemmas()[:10])
```

**FrameNet**:

```python
from nltk.corpus import framenet_v17 as framenet
print(framenet.frame_names()[:10])
```

**PropBank** (proposition bank):

```python
from nltk.corpus import propbank
print(propbank.instances()[:5])
```

**SentiWordNet**:

```python
from nltk.corpus import sentiwordnet as swn
synset = wn.synset('work.v.01')
senti_synset = swn.senti_synset('work.v.01')
print(senti_synset.pos_score())   # positive sentiment
print(senti_synset.neg_score())   # negative sentiment
print(senti_synset.obj_score())   # objectivity score
```

**Twitter Corpus**:

```python
from nltk.corpus import twitter_samples
positive = twitter_samples.strings('positive_tweets.json')
negative = twitter_samples.strings('negative_tweets.json')
```

**UDHR** (Universal Declaration of Human Rights, multiple languages):

```python
from nltk.corpus import udhr
print(udhr.fileids()[:10])  # files in different languages
print(udhr.words('English-Latin2')[:20])
```

## Frequency Distributions

### FreqDist

Count and analyze token frequencies:

```python
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize

tokens = word_tokenize("the cat sat on the mat the cat ran")
fdist = FreqDist(tokens)

print(fdist['the'])       # 3
print(fdist.freq('the'))  # 0.375
print(fdist.N())          # 8 (total count)
print(fdist.most_common(5))
# [('the', 3), ('cat', 2), ('sat', 1), ('on', 1), ('mat', 1)]

# Plot (requires matplotlib)
fdist.plot(20, cumulative=True, title="Top 20 Words")
```

### ConditionalFreqDist

Frequency distributions conditioned on a category:

```python
from nltk.probability import ConditionalFreqDist
from nltk.corpus import brown

cfd = ConditionalFreqDist()
for word in brown.words():
    word = word.lower()
    cfd[brown.categories()[brown.fileids().index(brown.fileids()[0])]][word] += 1

# Or more simply using corpus categories:
cfd = ConditionalFreqDist(
    (category, word.lower())
    for category in brown.categories()
    for word in brown.words(categories=category)
)

print(cfd['news']['the'])       # count of 'the' in news
print(cfd['news'].most_common(10))

# Plot
cfd.plot conditions=['news', 'fiction'], samples=['the', 'a', 'is'])
cfd.tabulate(conditions=['news', 'fiction'], samples=['the', 'a', 'is'])
```

## LazyCorpusLoader

Deferred loading — corpora load only when first accessed:

```python
from nltk.corpus import brown  # loaded lazily, not at import
words = brown.words()  # loads here
```
