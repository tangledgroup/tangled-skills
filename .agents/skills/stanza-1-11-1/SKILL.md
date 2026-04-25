---
name: stanza-1-11-1
description: Stanford NLP Python library for linguistic analysis of 80+ human languages. Use when building multilingual NLP pipelines requiring tokenization, POS tagging, lemmatization, dependency parsing, NER, sentiment analysis, constituency parsing, or language identification with pretrained neural models or CoreNLP integration.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.11.1"
tags:
  - nlp
  - natural-language-processing
  - python
  - multilingual
  - pytorch
  - stanford
category: machine-learning
external_references:
  - https://github.com/stanfordnlp/stanza/tree/v1.11.1
  - https://arxiv.org/abs/2003.07082
  - https://arxiv.org/abs/2007.14640
  - https://stanfordnlp.github.io/CoreNLP/
  - https://universaldependencies.org/
  - https://stanfordnlp.github.io/stanza/
  - https://huggingface.co/stanfordnlp/models
---
## Overview
Stanza is the official Python NLP library from the Stanford NLP Group, providing state-of-the-art neural network models for linguistic analysis across **80+ human languages**. Built on PyTorch, it offers a full neural pipeline including tokenization, multi-word token expansion, part-of-speech tagging, lemmatization, dependency parsing, named entity recognition, sentiment analysis, constituency parsing, and language identification.

**Key features:**
- Native Python implementation with minimal setup
- Full neural network pipeline for robust text analytics
- Pretrained models supporting 70+ human languages via Universal Dependencies
- Biomedical and clinical English models for specialized domains
- Official Python interface to Stanford CoreNLP Java package
- GPU-accelerated inference for high-performance processing

## When to Use
Use Stanza when:
- Building multilingual NLP applications requiring consistent analysis across languages
- Needing accurate neural network-based linguistic analysis (tokenization, POS, parsing)
- Working with Universal Dependencies treebanks or BIOES-formatted NER data
- Requiring biomedical/clinical text analysis capabilities
- Wanting to integrate Stanford CoreNLP Java tools into Python workflows
- Building pipelines that need constituency parsing or coreference resolution
- Training custom models on your own annotated data

## Core Concepts
### Neural Pipeline Architecture

Stanza's neural pipeline consists of modular **processors**, each performing a specific NLP task:

| Processor | Task | Dependencies | Output |
|-----------|------|--------------|--------|
| `tokenize` | Sentence segmentation & tokenization | None | Sentences, Tokens |
| `mwt` | Multi-word token expansion | tokenize | Words (expanded MWTs) |
| `pos` | Part-of-speech & morphological tagging | tokenize, mwt | UPOS, XPOS, UFeats |
| `lemma` | Lemmatization | tokenize, mwt, pos | Word lemmas |
| `depparse` | Dependency parsing | tokenize, mwt, pos, lemma | Heads, dependency relations |
| `ner` | Named entity recognition | tokenize, mwt | Entity spans (BIOES) |
| `sentiment` | Sentiment analysis | tokenize, mwt | Sentence sentiment scores |
| `constituency` | Constituency parsing | tokenize, mwt, pos | Parse trees |
| `langid` | Language identification | None | Language code |

### Data Objects

Stanza represents annotated text through hierarchical objects:

- **Document**: Top-level container with raw text, sentences, and entities
- **Sentence**: Segmented sentence with tokens, words, dependencies, sentiment
- **Token**: Surface-form token (may expand to multiple Words via MWT)
- **Word**: Syntactic word with annotations (POS, lemma, head, deprel)
- **Span**: Contiguous text span for entities and other annotations
- **ParseTree**: Nested tree structure for constituency parsing

### Universal Dependencies

Stanza uses the [Universal Dependencies](https://universaldependencies.org/) framework for cross-linguistic consistency:
- **UPOS**: Universal Part-of-Speech tags (17 categories)
- **XPOS**: Treebank-specific POS tags
- **UFeats**: Universal morphological features
- **Deprel**: Universal dependency relations

## Installation / Setup
### Quick Start with pip

```bash
pip install stanza
```

**Requirements:**
- Python 3.9 or later
- PyTorch 1.13.0 or above (auto-installed)

**Core dependencies:**
- emoji, numpy, platformdirs, protobuf>=3.15.0, requests, networkx, torch>=1.13.0, tqdm, udtools>=0.2.4

### Alternative Installation Methods

**Anaconda:**
```bash
conda install -c stanfordnlp stanza
```

**From source (for development):**
```bash
git clone https://github.com/stanfordnlp/stanza.git
cd stanza
pip install -e .
```

### Downloading Models

Models must be downloaded separately for each language:

```python
import stanza

# Download English models (auto-downloads on first use if needed)
stanza.download('en')

# Download multiple languages
stanza.download(['en', 'fr', 'de'])

# Download specific packages
stanza.download('en', package='combined')

# With proxy (for restricted networks)
proxies = {'http': 'http://ip:port', 'https': 'http://ip:port'}
stanza.download('en', proxies=proxies)
```

See [Model Downloading](reference/02-model-downloading.md) for complete model packages and language support.

## Basic Usage Examples
### Simple Pipeline

```python
import stanza

# Download and initialize pipeline
stanza.download('en')
nlp = stanza.Pipeline('en')

# Process text
doc = nlp("Barack Obama was born in Hawaii. He was elected president in 2008.")

# Access annotations
print(doc.sentences[0].print_dependencies())
# Output:
# ('Barack', '4', 'nsubj:pass')
# ('Obama', '1', 'flat')
# ('was', '4', 'aux:pass')
# ('born', '0', 'root')
# ('in', '6', 'case')
# ('Hawaii', '4', 'obl')
# ('.', '4', 'punct')

# Extract named entities
print(doc.entities)  # [Span(text='Barack Obama', type='PERSON'), ...]
```

### Customizing Processors

```python
# Use only specific processors
nlp = stanza.Pipeline('en', processors='tokenize,pos,depparse')

# Exclude NER for faster processing
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma,depparse')

# Use dict to specify packages per processor
nlp = stanza.Pipeline(
    'en',
    processors={'tokenize': 'default', 'pos': 'combined', 'ner': 'ontonotes'}
)
```

### Batching for Performance

```python
# Concatenate documents with blank lines for batching
text = """Document 1 sentence 1. Document 1 sentence 2.

Document 2 sentence 1. Document 2 sentence 2.

Document 3 sentence 1."""

doc = nlp(text)
# Pipeline processes all sentences together for maximum speed
```

See [Pipeline Configuration](reference/01-pipeline-configuration.md) for advanced options and custom processors.

## Advanced Topics
## Advanced Topics

- [Pipeline Configuration](reference/01-pipeline-configuration.md)
- [Model Downloading](reference/02-model-downloading.md)
- [Data Objects](reference/03-data-objects.md)
- [Processor Details](reference/04-processor-details.md)
- [Custom Processors](reference/05-custom-processors.md)
- [Model Training](reference/06-model-training.md)
- [Corenlp Client](reference/07-corenlp-client.md)
- [Biomedical Models](reference/08-biomedical-models.md)

