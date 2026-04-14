# NLTK Corpus Access - Complete Guide

## Overview

NLTK provides access to 50+ corpora for NLP research and development, including annotated text, parsed sentences, and specialized datasets.

## Built-in Corpora

### Text Corpora

#### Brown Corpus

First major corpus in NLTK, categorized English text:

```python
from nltk.corpus import brown

# Get all words
words = brown.words()[:100]  # First 100 words
print(words)

# Get words from specific category
news_words = brown.words(categories='news')[:50]
print(news_words)

# Get categorized sentences
sentences = brown.sents()[:5]
for sent in sentences:
    print(sent)

# Get raw text
raw_text = brown.raw()[:500]
print(raw_text)

# List available categories
categories = brown.categories()
print(f"Categories: {categories[:10]}...")
```

#### Gutenberg Corpus

Literature from Project Gutenberg:

```python
from nltk.corpus import gutenberg

# List available files
files = gutenberg.files()
print(f"Available: {files[:10]}...")

# Get text from specific file
emma_text = gutenberg.raw('austen-emma.txt')[:500]
print(emma_text)

# Get words and sentences
words = gutenberg.words('austen-emma.txt')[:100]
sentences = gutenberg.sents('austen-emma.txt')[:5]

# Analyze vocabulary
from nltk.probability import FreqDist
fdist = FreqDist(gutenberg.words('austen-emma.txt'))
print(f"Total tokens: {len(gutenberg.words('austen-emma.txt'))}")
print(f"Unique types: {fdist.N()}")
```

#### Reuters Corpus

News articles for text classification:

```python
from nltk.corpus import reuters

# List categories
categories = reuters.categories()
print(f"Categories: {len(categories)} total")

# Get documents in category
doc_ids = reuters.fileids('earn')  # Earnings category
print(f"Earnings documents: {len(doc_ids)}")

# Get text from specific document
text = reuters.raw(reuters.fileids('earn')[0])[:500]
print(text)

# Get categories for a document
doc_id = reuters.fileids()[0]
cats = reuters.categories(doc_id)
print(f"Document {doc_id} categories: {cats}")
```

### Annotated Corpora

#### Penn Treebank

POS-tagged and parsed sentences:

```python
from nltk.corpus import treebank

# Get tagged sentences
tagged_sents = treebank.tagged_sents()[:5]
for sent in tagged_sents:
    print(sent)

# Get parsed sentences
parsed_sents = treebank.parsed_sents()[:3]
for tree in parsed_sents:
    print(tree.prettify())

# List file IDs
fileids = treebank.fileids()[:10]
print(fileids)
```

#### CMU Pronouncing Dictionary

Word pronunciations in ARPABET format:

```python
from nltk.corpus import cmudict

# Load dictionary
d = cmudict.dict()

# Get pronunciations
word = 'better'
pronunciations = d[word]
print(f"Pronunciations of '{word}': {pronunciations}")

# Find rhyming words
def find_rhymes(word, min_rhyme_length=2):
    target = d[word][0][-min_rhyme_length:]  # Last 2 phonemes
    rhymes = []
    for w, pronuns in d.items():
        for pronun in pronuns:
            if pronun[-min_rhyme_length:] == target and w != word:
                rhymes.append(w)
                break
    return rhymes

rhymes = find_rhymes('better')[:20]
print(f"Rhymes with 'better': {rhymes}")
```

### Linguistic Corpora

#### WordNet

Lexical database (covered in detail in wordnet-integration.md):

```python
import nltk.corpus.wordnet as wn

# Basic usage
synsets = wn.synsets('dog')
print(f"Synsets for 'dog': {len(synsets)}")

# Get definition
first_synset = synsets[0]
print(f"Definition: {first_synset.definition()}")
```

#### VerbNet

Verb classifications and argument structures:

```python
from nltk.corpus import verbnet

# List available classes
classes = verbnet.classes()
print(f"Verb classes: {len(classes)}")

# Get class information
cls = verbnet.class('motion')
print(f"Motion verbs: {[v.name() for v in cls.verbs][:10]}")
```

### Specialized Corpora

#### Movie Reviews (Sentiment Analysis)

```python
from nltk.corpus import movie_reviews

# List categories (positive/negative)
categories = movie_reviews.categories()
print(categories)  # ['neg', 'pos']

# Get documents by category
positive_docs = movie_reviews.fileids('pos')
negative_docs = movie_reviews.fileids('neg')

# Get text and labels
doc_id = positive_docs[0]
text = movie_reviews.raw(doc_id)[:200]
label = movie_reviews.categories(doc_id)[0]

print(f"Label: {label}")
print(f"Text: {text}...")

# Prepare for classification
documents = [(movie_reviews.words(fileid), category) 
             for category in movie_reviews.categories()
             for fileid in movie_reviews.fileids(category)]
```

#### Twitter Corpus

Social media text:

```python
from nltk.corpus import twitter

# Get tweets (sample)
tweets = twitter.strings()[:5]
for tweet in tweets:
    print(tweet[:140])  # Truncate to 140 chars

# Note: Full dataset requires separate download
```

## Working with Corpora

### Frequency Analysis

```python
from nltk.corpus import brown
from nltk.probability import FreqDist
from nltk import word_tokenize

# Word frequency
words = brown.words()
fdist = FreqDist(words)

print("Most common words:")
for word, freq in fdist.most_common(20):
    print(f"  {word:15} {freq:5}")

# Plot distribution (requires matplotlib)
# fdist.plot(50, cumulative=True)

# Vocabulary growth
def vocabulary_growth(corpus_words, step=1000):
    """Plot vocabulary growth curve."""
    vocab_sizes = []
    for i in range(step, len(corpus_words), step):
        vocab_sizes.append(len(set(corpus_words[:i])))
    return vocab_sizes

growth = vocabulary_growth(words)
print(f"Vocabulary at checkpoints: {growth[:10]}...")
```

### Collocation Detection

```python
from nltk.corpus import brown
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import AssociationMeasures
from nltk import word_tokenize

# Get text
text = ' '.join(brown.words())

# Tokenize
tokens = word_tokenize(text.lower())

# Find bigram collocations
finder = BigramCollocationFinder.from_words(tokens)

# Filter common words
stopwords = set(['the', 'a', 'an', 'of', 'and', 'to', 'in'])
finder.apply_word_filter(lambda w: w not in stopwords and len(w) > 1)

# Get top collocations by different measures
print("Top bigrams (PMI):")
for bigram, score in finder.nbest(AssociationMeasures.pmi, 10):
    print(f"  {bigram}: {score:.2f}")

print("\nTop bigrams (likelihood ratio):")
for bigram, score in finder.nbest(AssociationMeasures.likeratio, 10):
    print(f"  {bigram}: {score:.2f}")
```

### Text Comparison

```python
from nltk.corpus import brown
from nltk.util import ngrams

# Compare n-gram distributions between categories
news_text = ' '.join(brown.words(categories='news'))
science_text = ' '.join(brown.words(categories='lore'))

# Bigram comparison
news_bigrams = set(ngrams(news_text.split(), 2))
science_bigrams = set(ngrams(science_text.split(), 2))

common = news_bigrams & science_bigrams
unique_news = news_bigrams - science_bigrams
unique_science = science_bigrams - news_bigrams

print(f"Common bigrams: {len(common)}")
print(f"Unique to news: {len(unique_news)}")
print(f"Unique to science: {len(unique_science)}")
```

## Custom Corpora

### Creating a Simple Corpus Reader

```python
from nltk.corpus.reader import PlaintextCorpusReader
import os

# Create corpus reader for directory of text files
corpus_root = '/path/to/my/corpus'
fileids = [f for f in os.listdir(corpus_root) if f.endswith('.txt')]

reader = PlaintextCorpusReader(corpus_root, fileids)

# Use like built-in corpora
words = reader.words()[:100]
sents = reader.sents()[:5]
raw = reader.raw()[:500]
```

### Tagged Corpus Reader

```python
from nltk.corpus.reader import TaggedCorpusReader

# Read tab-separated tagged data
corpus_root = '/path/to/tagged/corpus'
fileids = r'.*\.(tagged|txt)'  # Regex pattern

reader = TaggedCorpusReader(corpus_root, fileids, tagformat='tabs')

# Get tagged sentences
tagged_sents = reader.tagged_sents()[:5]
for sent in tagged_sents:
    print(sent)
```

### Parsed Corpus Reader

```python
from nltk.corpus.reader import DependencyCorpusReader

# Read dependency-parsed data
corpus_root = '/path/to/parsed/corpus'
fileids = r'.*\.parsed'

reader = DependencyCorpusReader(corpus_root, fileids)

# Get parsed sentences
parsed_sents = reader.parsed_sents()[:3]
for tree in parsed_sents:
    print(tree.prettify())
```

## Corpus Utilities

### Downloading Corpora

```python
import nltk

# Download specific corpus
nltk.download('brown')
nltk.download('gutenberg')
nltk.download('treebank')

# Download all corpora (2GB+)
nltk.download('all')

# Interactive downloader
nltk.download()
```

### Checking Available Corpora

```python
import nltk.data

# List all available corpora
corpora = nltk.data.find('*/*')
print(f"Total resources: {len(corpora)}")

# Find specific corpus
try:
    brown_path = nltk.data.find('corpora/brown')
    print(f"Brown corpus at: {brown_path}")
except LookupError:
    print("Brown corpus not found - run nltk.download('brown')")
```

### Custom Data Path

```python
import nltk

# Add custom data directory
nltk.data.path.append('/custom/path/to/nltk_data')

# Now NLTK will look there for corpora
from nltk.corpus import brown  # Will find custom version if present
```

## Common Patterns

### Building a Text Classification Dataset

```python
from nltk.corpus import movie_reviews
from nltk.probability import FreqDist
from nltk import word_tokenize

# Prepare features
def extract_features(words):
    """Extract word presence features."""
    return {f"contains({w})": w in words for w in all_words}

# Get documents
documents = [(movie_reviews.words(fileid), category) 
             for category in movie_reviews.categories()
             for fileid in movie_files(category)]

# Find most informative features
all_words = FreqDist(w.lower() for w in movie_reviews.words())
common_words = [w for w, f in all_words.most_common(2000)]

# Create feature sets
featuresets = [(extract_features(d), c) for d, c in documents]
```

### Comparative Corpus Analysis

```python
from nltk.corpus import brown
from nltk.probability import ConditionalFreqDist

# Compare word usage across categories
cfd = ConditionalFreqDist()

for category in brown.categories():
    for word in brown.words(categories=category):
        cfd[category][word.lower()] += 1

# Find characteristic words for each category
categories = ['news', 'lore', 'religion', 'fiction']
for cat in categories:
    print(f"\n{cat.upper()} - most common content words:")
    # Filter out stop words
    stop_words = set(['the', 'a', 'an', 'and', 'of', 'to', 'in'])
    content_words = [(w, f) for w, f in cfd[cat].most_common(20) 
                     if w not in stop_words and len(w) > 2]
    for word, freq in content_words:
        print(f"  {word:15} {freq:5}")
```

## Troubleshooting

### Corpus Not Found

**Problem**: `LookupError: Corpus <name> not found`

**Solution**: Download the corpus:

```python
import nltk
nltk.download('brown')  # Replace with needed corpus
```

### Memory Issues with Large Corpora

**Problem**: Loading entire corpus consumes too much memory

**Solution**: Use iterators and process in chunks:

```python
from nltk.corpus import gutenberg

# Bad: loads everything into memory
all_words = gutenberg.words()

# Good: iterate lazily
for i, word in enumerate(gutenberg.words()):
    process(word)
    if i % 10000 == 0:
        print(f"Processed {i} words")
```

### Slow Corpus Access

**Problem**: Repeated corpus access is slow

**Solution**: Cache data when appropriate:

```python
from functools import lru_cache
from nltk.corpus import brown

@lru_cache(maxsize=100)
def get_category_words(category):
    """Cached category word access."""
    return tuple(brown.words(categories=category))

# Usage
news_words = get_category_words('news')  # Cached for future calls
```

## Performance Tips

1. **Download once**: All corpora download to shared location
2. **Use categories**: Filter data at corpus level, not after loading
3. **Lazy evaluation**: Use generators when possible
4. **Cache results**: Store frequently accessed data

## References

- **Corpus Documentation**: https://www.nltk.org/howto/corpus.html
- **Available Corpora**: https://www.nltk.org/data.html#packages-available
- **Custom Corpus Readers**: https://www.nltk.org/api/nltk.corpus.reader.html
