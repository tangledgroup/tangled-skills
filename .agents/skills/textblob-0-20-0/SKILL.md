---
name: textblob-0-20-0
description: Python library for simplified natural language processing (NLP) tasks including sentiment analysis, part-of-speech tagging, noun phrase extraction, tokenization, classification, word inflection, lemmatization, and spelling correction. Use when building text processing applications requiring quick NLP operations without complex setup, or when integrating with NLTK and pattern libraries.
license: MIT
author: Steven Loria <oss@stevenloria.com>
version: "0.20.0"
tags:
  - nlp
  - text-processing
  - sentiment-analysis
  - pos-tagging
  - classification
  - tokenization
  - lemmatization
category: natural-language-processing
external_references:
  - https://github.com/sloria/TextBlob/tree/0.20.0
  - https://textblob.readthedocs.io/
---

# TextBlob 0.20.0

## Overview

TextBlob is a Python library for processing textual data that provides a simple, Pythonic API for common natural language processing (NLP) tasks. It stands on the shoulders of [NLTK](http://www.nltk.org/) and [pattern](https://github.com/clips/pattern/), playing nicely with both while offering a streamlined interface.

TextBlob treats text as string-like objects that "know how to do NLP," making it intuitive for developers familiar with Python strings.

## When to Use

Use TextBlob when:
- Building applications requiring sentiment analysis, POS tagging, or noun phrase extraction
- Prototyping NLP workflows quickly without complex configuration
- Needing simple tokenization, lemmatization, or word inflection
- Creating custom text classifiers (Naive Bayes, Decision Tree)
- Implementing spelling correction functionality
- Working with WordNet for semantic similarity and definitions
- Building educational NLP applications or demos

**Don't use TextBlob when:**
- You need state-of-the-art deep learning models (use transformers/spaCy instead)
- Processing requires multilingual support beyond English (limited extensions available)
- Production-scale performance is critical (TextBlob prioritizes simplicity over speed)

## Core Concepts

### TextBlob Objects

The core building block is the `TextBlob` class, which wraps text and provides NLP methods:

```python
from textblob import TextBlob

text = TextBlob("Python is a high-level programming language.")
```

### Sentiment Analysis

Returns polarity (-1.0 to 1.0) and subjectivity (0.0 to 1.0):

```python
testimonial = TextBlob("TextBlob is amazingly simple to use!")
sentiment = testimonial.sentiment
# Sentiment(polarity=0.39, subjectivity=0.44)
```

### Part-of-Speech Tagging

Identifies grammatical categories for each word:

```python
blob = TextBlob("Python is a high-level programming language.")
tags = blob.tags
# [('Python', 'NNP'), ('is', 'VBZ'), ('a', 'DT'), ...]
```

### Noun Phrase Extraction

Extracts meaningful noun phrases from text:

```python
blob.noun_phrases
# WordList(['python', 'high-level programming language'])
```

## Installation / Setup

### Install from PyPI

```bash
pip install -U textblob
python -m textblob.download_corpora
```

### Minimal Corpora Download

For basic functionality only (default models):

```bash
python -m textblob.download_corpora lite
```

### Conda Installation

```bash
conda install -c conda-forge textblob
python -m textblob.download_corpora
```

### Development Version

```bash
pip install -U git+https://github.com/sloria/TextBlob.git@dev
```

### Dependencies

- **Required**: NLTK >= 3.9 (installed automatically)
- **Optional**: NumPy (for maximum entropy classifier and NLTKTagger)

### Environment Variables

Set `NLTK_DATA` to change the default corpus download directory:

```bash
export NLTK_DATA=/path/to/nltk/data
python -m textblob.download_corpora
```

## Basic Usage Examples

See reference files for detailed examples:
- [Core NLP Operations](references/01-core-nlp-operations.md)
- [Text Classification](references/02-text-classification.md)
- [Advanced Model Configuration](references/03-advanced-models.md)
- [API Reference Summary](references/04-api-reference.md)

## Advanced Topics

### Custom Models and Components

TextBlob allows overriding default implementations:
- **Sentiment analyzers**: PatternAnalyzer (default), NaiveBayesAnalyzer
- **POS taggers**: PatternTagger (default), NLTKTagger
- **Noun phrase extractors**: FastNPExtractor (default), ConllExtractor
- **Tokenizers**: Custom tokenizers from NLTK or other libraries
- **Parsers**: PatternParser and custom implementations

### Blobber Factory Class

Create TextBlobs with shared models using `Blobber`:

```python
from textblob import Blobber
from textblob.taggers import NLTKTagger

blobber = Blobber(pos_tagger=NLTKTagger())
blob1 = blobber("First text.")
blob2 = blobber("Second text.")
# Both use the same tagger instance
```

### Extensions Framework

Add support for new languages and models:
- `textblob-fr`: French language support
- `textblob-de`: German language support
- `textblob-aptagger`: Averaged Perceptron tagger

## Troubleshooting

### Common Issues

**MissingCorpusError**: Corpora not downloaded
```bash
python -m textblob.download_corpora
```

**Import errors after upgrade**: TextBlob 0.8+ renamed from `text` to `textblob`
```python
# Old (pre-0.8)
from text.blob import TextBlob

# New (0.8+)
from textblob import TextBlob
```

**NLTKTagger requires NumPy**:
```bash
pip install numpy
```

**Spelling correction accuracy**: Based on Peter Norvig's algorithm (~70% accurate), works best for common misspellings

### Performance Considerations

- POS tagging and parsing can be slow on large texts
- Use `Blobber` to share models across multiple TextBlobs
- Consider NLTKTagger over PatternTagger for accuracy (requires NumPy)
- For production use, consider caching results or using specialized libraries

## References

- **Official documentation**: https://textblob.readthedocs.io/
- **GitHub repository**: https://github.com/sloria/TextBlob
- **Changelog**: https://textblob.readthedocs.io/en/latest/changelog.html
- **PyPI package**: https://pypi.org/project/textblob/
- **NLTK documentation**: http://www.nltk.org/
- **Pattern library**: https://github.com/clips/pattern

## Version Information

- **Current version**: 0.20.0 (released 2026-04-01)
- **Python support**: 3.10, 3.11, 3.12, 3.13, 3.14
- **NLTK compatibility**: >= 3.9
- **License**: MIT

### Recent Changes (0.20.0)

- Custom tokenizer support for `.words` property
- Python 3.10-3.14 support
- Removed deprecated translation features (use Google Translate API instead)

## See Also

For detailed examples and API documentation, see the reference files:
- [`references/01-core-nlp-operations.md`](references/01-core-nlp-operations.md) - Complete NLP task examples
- [`references/02-text-classification.md`](references/02-text-classification.md) - Building custom classifiers
- [`references/03-advanced-models.md`](references/03-advanced-models.md) - Model configuration and extensions
- [`references/04-api-reference.md`](references/04-api-reference.md) - Complete API documentation
