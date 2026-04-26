---
name: textblob-0-20-0
description: Python library for simplified natural language processing providing part-of-speech tagging, noun phrase extraction, sentiment analysis, classification (Naive Bayes, Decision Tree), tokenization, word inflection, lemmatization, spelling correction, and WordNet integration. Use when building text processing pipelines, performing quick NLP tasks without complex setup, or integrating with NLTK and pattern libraries.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.20.0"
tags:
  - nlp
  - text-processing
  - sentiment-analysis
  - pos-tagging
  - tokenization
  - classification
  - wordnet
category: nlp
external_references:
  - https://github.com/sloria/TextBlob/tree/0.20.0
  - https://textblob.readthedocs.io/
  - https://pypi.org/project/textblob/
  - http://www.nltk.org/
  - https://github.com/clips/pattern
compatibility: Python >=3.10, requires nltk>=3.9
---

# TextBlob 0.20.0

## Overview

TextBlob is a Python library for processing textual data. It provides a simple API for diving into common natural language processing (NLP) tasks such as part-of-speech tagging, noun phrase extraction, sentiment analysis, classification, tokenization, word inflection, lemmatization, spelling correction, and WordNet integration.

TextBlob stands on the giant shoulders of NLTK and pattern, and plays nicely with both. It provides a consistent, Pythonic interface that makes NLP accessible without deep framework knowledge.

Version 0.20.0 supports Python 3.10 through 3.14, requires nltk>=3.9, and introduces custom tokenizer support for the `.words` property. Translation (`TextBlob.translate()` and `TextBlob.detect_language`) was removed in 0.18.0 — use the official Google Translate API instead.

## When to Use

- Performing quick NLP tasks (sentiment analysis, POS tagging, noun phrase extraction) without complex setup
- Building text classification systems with Naive Bayes or Decision Tree classifiers
- Tokenizing text into words and sentences with simple APIs
- Word inflection (pluralization/singularization) and lemmatization
- Spelling correction based on Peter Norvig's algorithm
- WordNet integration for synsets, definitions, and semantic similarity
- Prototyping NLP pipelines before moving to heavier frameworks like spaCy or transformers

## Core Concepts

TextBlob wraps text into objects that behave like Python strings but with NLP superpowers. The main classes form a hierarchy:

- **`TextBlob`** — A general text block for larger bodies of text containing sentences. Supports sentence splitting, sentiment analysis, POS tagging, noun phrase extraction, and more.
- **`Sentence`** — A sentence within a TextBlob. Inherits all BaseBlob properties. Tracks `start` and `end` character indices within the parent blob.
- **`Word`** — A string subclass with methods for inflection (`pluralize()`, `singularize()`), lemmatization, spelling correction, stemming, and WordNet integration (synsets, definitions).
- **`WordList`** — A list subclass containing `Word` objects. Supports batch operations like `.pluralize()`, `.singularize()`, `.lemmatize()`, `.stem()`, `.upper()`, `.lower()`, and `.count()`.
- **`Blobber`** — A factory for TextBlobs that share the same tagger, tokenizer, parser, classifier, and noun phrase extractor.

All text objects support Python string operations: slicing (`blob[0:19]`), comparison (`blob == "text"`), concatenation (`blob1 + blob2`), and common string methods (`.upper()`, `.find()`).

## Installation / Setup

Install via pip and download required NLTK corpora:

```bash
pip install textblob
python -m textblob.download_corpora
```

The `download_corpora` command downloads the Penn Treebank POS tagger, punkt sentence tokenizer, and other required NLTK data. For the NaiveBayes sentiment analyzer, you also need the movie_reviews corpus:

```python
import nltk
nltk.download('movie_reviews')
```

## Usage Examples

### Basic Text Processing

```python
from textblob import TextBlob

blob = TextBlob("Python is a high-level, general-purpose programming language.")
blob.tags          # [('Python', 'NNP'), ('is', 'VBZ'), ('a', 'DT'), ...]
blob.noun_phrases  # WordList(['python'])
```

### Sentiment Analysis

```python
testimonial = TextBlob("TextBlob is amazingly simple to use. What great fun!")
testimonial.sentiment
# Sentiment(polarity=0.39166666666666666, subjectivity=0.4357142857142857)
testimonial.sentiment.polarity    # 0.392 (positive)
testimonial.sentiment.subjectivity # 0.436
```

Polarity ranges from -1.0 (negative) to 1.0 (positive). Subjectivity ranges from 0.0 (objective) to 1.0 (subjective).

### Tokenization

```python
zen = TextBlob("Beautiful is better than ugly. Explicit is better than implicit.")
zen.words     # WordList(['Beautiful', 'is', 'better', 'than', 'ugly', ...])
zen.sentences # [Sentence("Beautiful is better than ugly."), Sentence("Explicit...")]
```

### Word Inflection and Lemmatization

```python
from textblob import Word

w = Word("octopi")
w.singularize()  # 'octopus'
Word("space").pluralize()  # 'spaces'
Word("went").lemmatize(pos='v')  # 'go'
```

### Spelling Correction

```python
b = TextBlob("I havv goood speling!")
print(b.correct())  # I have good spelling!

w = Word('falibility')
w.spellcheck()  # [('fallibility', 1.0)]
```

### N-grams

```python
blob = TextBlob("Now is better than never.")
blob.ngrams(n=3)
# [WordList(['Now', 'is', 'better']), WordList(['is', 'better', 'than']), ...]
```

## Advanced Topics

**Sentiment Analyzers**: Two built-in analyzers — PatternAnalyzer (default, lexicon-based) and NaiveBayesAnalyzer (ML-based, trained on movie reviews) → [Sentiment Analysis](reference/01-sentiment-analysis.md)

**Text Classification**: Naive Bayes, Decision Tree, MaxEnt, and Positive Naive Bayes classifiers with CSV/JSON/TSV data loading → [Classifiers](reference/02-classifiers.md)

**Custom Models**: Override tokenizers, POS taggers, noun phrase extractors, parsers, and sentiment analyzers via the Blobber factory or constructor parameters → [Advanced Usage](reference/03-advanced-usage.md)

**API Reference**: Complete reference for TextBlob, Word, WordList, Sentence, Blobber, and all model classes → [API Reference](reference/04-api-reference.md)
