---
name: nltk-3-9-2
description: Complete toolkit for Natural Language Processing with NLTK 3.9.2, covering tokenization, stemming, lemmatization, POS tagging, parsing, WordNet integration, corpus access, text classification, and semantic analysis for Python applications. Use when building Python programs that work with human language data including text preprocessing, linguistic analysis, sentiment scoring, machine translation evaluation, or educational NLP workflows.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - nlp
  - natural-language-processing
  - python
  - text-processing
  - wordnet
  - tokenization
  - parsing
  - sentiment-analysis
  - corpus
category: natural-language-processing
external_references:
  - https://www.nltk.org/
  - https://www.nltk.org/api/
  - https://www.nltk.org/book/
  - https://www.nltk.org/contribute.html
  - https://www.nltk.org/data.html
  - https://www.nltk.org/install.html
  - https://www.nltk.org/news.html
  - https://github.com/nltk/nltk/tree/v3.9.2
---

# NLTK 3.9.2

## Overview

NLTK (Natural Language Toolkit) is a leading platform for building Python programs to work with human language data. It provides easy-to-use interfaces to over 50 corpora and lexical resources such as WordNet, along with a comprehensive suite of text processing libraries for classification, tokenization, stemming, tagging, parsing, semantic reasoning, and more.

NLTK 3.9.2 (October 2025) supports Python 3.9 through 3.13. It resolved the pickled-models security vulnerability (CVE-2024-39705), added Python 3.13 support, updated download checksums to SHA256, and made WordNet interoperable with various taggers and tagged corpora.

The project is in maintenance mode — welcoming bugfixes and minor enhancements. It is freely available under the Apache 2.0 License and has been called "a wonderful tool for teaching, and working in, computational linguistics using Python."

## When to Use

- Tokenizing text into words, sentences, or subword units
- Stemming and lemmatization for morphological normalization
- Part-of-speech tagging with Penn Treebank or Russian tagsets
- Named entity recognition and chunking
- Context-free grammar parsing (chart parsing, Earley parser)
- WordNet-based lexical analysis, synonym lookup, and semantic similarity
- Accessing built-in corpora (Brown, Gutenberg, Treebank, WordNet, SentiWordNet, etc.)
- Text classification with Naive Bayes, Maximum Entropy, decision trees, or scikit-learn wrappers
- Sentiment analysis using VADER, SentiWordNet, or custom classifiers
- Machine translation evaluation (BLEU, METEOR, chrF, GLEU, RIBES)
- Language modeling with n-gram models and smoothing
- Semantic reasoning with Discourse Representation Theory (DRT), first-order logic, and resolution provers
- Educational NLP workflows and introductory computational linguistics

## Core Concepts

**Tokenization**: Breaking text into words, sentences, or other units. NLTK provides multiple tokenizers for different domains — TreebankWordTokenizer for standard English, TweetTokenizer for social media text, PunktSentenceTokenizer for unsupervised sentence boundary detection, and RegexpTokenizer for custom patterns.

**Stemming vs Lemmatization**: Stemming strips affixes to produce word stems (Porter, Snowball, Lancaster). Lemmatization uses WordNet to map words to dictionary forms (lemmas), producing valid words rather than arbitrary stems.

**Part-of-Speech Tagging**: Assigning grammatical categories to tokens. NLTK provides UnigramTagger, BigramTagger, TrigramTagger, PerceptronTagger (default for `pos_tag`), BrillTagger, and HMM-based taggers. English uses the Penn Treebank tagset; Russian uses the Russian National Corpus tagset.

**Parsing**: Building syntactic structure from tagged tokens. NLTK supports context-free grammars with chart parsers (TopDownChartParser, BottomUpChartParser, EarleyChartParser), CCG parsing, dependency parsing, and interfaces to Stanford CoreNLP.

**Corpora**: Pre-packaged text datasets accessible through uniform APIs. Over 50 corpora are available including Brown, Gutenberg, Treebank, WordNet, SentiWordNet, movie reviews, Twitter data, and many others.

**Frequency Distributions**: `FreqDist` and `ConditionalFreqDist` from `nltk.probability` track occurrence counts and support plotting (with Matplotlib).

## Installation / Setup

NLTK requires Python 3.9–3.13. Install via pip:

```bash
pip install --user -U nltk
```

After installing the package, download required data:

```python
import nltk
nltk.download('popular')  # most commonly used datasets and models
```

Or from the command line:

```bash
python -m nltk.downloader popular
```

For all data (including corpora, taggers, parsers):

```python
nltk.download('all')
```

Data is installed to `~/.nltk/` by default. Set `NLTK_DATA` environment variable for custom locations. For central installation: `/usr/local/share/nltk_data` (Mac), `/usr/share/nltk_data` (Unix), or `C:\nltk_data` (Windows).

## Usage Examples

### Basic text processing pipeline

```python
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk import pos_tag

text = "The runners' shoes were amazing. They ran quickly through the park."

# Sentence tokenization
sentences = sent_tokenize(text)
print(sentences)
# ['The runners\' shoes were amazing.', 'They ran quickly through the park.']

# Word tokenization
tokens = word_tokenize(text)
print(tokens)
# ['The', 'runners', "'s", 'shoes', 'were', 'amazing', '.', ...]

# POS tagging
tagged = pos_tag(tokens)
print(tagged[:6])
# [('The', 'DT'), ('runners', 'NNS'), ("'s", 'POS'), ('shoes', 'NNS'), ...]

# Lemmatization
lemmatizer = WordNetLemmatizer()
lemmas = [lemmatizer.lemmatize(word, pos=tag[0].lower()) for word, tag in tagged]
print(lemmas)
```

### Sentiment analysis with VADER

```python
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
scores = sia.polarity_scores("This movie was absolutely fantastic!")
print(scores)
# {'neg': 0.0, 'neu': 0.325, 'pos': 0.675, 'compound': 0.8129}
```

### WordNet lookup

```python
from nltk.corpus import wordnet as wn

synsets = wn.synsets("run")
print(synsets[0].definition())
# "change from one state or mode to another"
print(synsets[0].lemmas()[0].name())
# "run"
```

## Advanced Topics

**Tokenization & Stemming**: Tokenizers (Treebank, Tweet, Punkt, Regex), stemmers (Porter, Snowball, Lancaster, RSLP), lemmatization → [Tokenization & Stemming](reference/01-tokenization-stemming.md)

**POS Tagging & Chunking**: Sequential taggers, PerceptronTagger, BrillTagger, HMM taggers, named entity chunking, regexp chunking → [POS Tagging & Chunking](reference/02-pos-tagging-chunking.md)

**Parsing & Trees**: CFG grammars, chart parsing (top-down, bottom-up, Earley), CCG parsing, dependency graphs, tree operations → [Parsing & Trees](reference/03-parsing-trees.md)

**WordNet & Semantics**: Synset navigation, lexical relations, similarity metrics, semantic logic, DRT, resolution provers → [WordNet & Semantics](reference/04-wordnet-semantics.md)

**Corpora & Data**: Corpus readers (plaintext, tagged, parsed, WordNet, SentiWordNet), data download, available corpora → [Corpora & Data](reference/05-corpora-data.md)

**Classification & Sentiment**: Naive Bayes, Maximum Entropy, decision trees, scikit-learn wrapper, VADER, SentiWordNet, text categorization → [Classification & Sentiment](reference/06-classification-sentiment.md)

**Metrics & Evaluation**: BLEU, METEOR, chrF, GLEU, RIBES, edit distance, confusion matrices, inter-annotator agreement (kappa, alpha) → [Metrics & Evaluation](reference/07-metrics-evaluation.md)

**Translation & Language Models**: IBM Models 1–5, phrase-based translation, n-gram language models with smoothing (Kneser-Ney, Laplace, Witten-Bell) → [Translation & Language Models](reference/08-translation-language-models.md)
