---
name: stanza-1-11-1
description: Stanford NLP Group's official Python NLP library for 80+ languages providing tokenization, POS tagging, lemmatization, dependency parsing, NER, sentiment analysis, constituency parsing, coreference resolution, and language identification via a neural pipeline built on PyTorch. Also includes a Python wrapper for the Java Stanford CoreNLP server. Use when building multilingual NLP pipelines, performing linguistic analysis across many human languages, training custom models on annotated data, or integrating biomedical/clinical NER and syntactic analysis.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - nlp
  - natural-language-processing
  - multilingual
  - tokenization
  - pos-tagging
  - lemmatization
  - dependency-parsing
  - ner
  - sentiment-analysis
  - constituency-parsing
  - coreference
  - language-identification
  - stanford-nlp
  - pytorch
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

# Stanza 1.11.1

## Overview

Stanza is the Stanford NLP Group's official Python natural language processing library. It provides a full neural network pipeline for robust text analytics across **80 human languages**, using the Universal Dependencies formalism. Built on PyTorch, it supports tokenization, multi-word token expansion, lemmatization, part-of-speech tagging, morphological features, dependency parsing, named entity recognition, sentiment analysis, constituency parsing, coreference resolution, and language identification.

Stanza also includes an officially maintained Python interface to the Java Stanford CoreNLP package, providing access to additional functionality such as constituency parsing (via CoreNLP), coreference resolution, and linguistic pattern matching with Semgrex and Ssurgeon.

Key features:
- Native Python implementation — no Java dependency required for neural pipeline
- Pretrained neural models supporting 80 human languages
- GPU-accelerated processing via PyTorch
- Biomedical and clinical English model packages for domain-specific NER and syntactic analysis
- Trainable on custom annotated data (CoNLL-U format for UD tasks, BIOES for NER)
- Python wrapper for Stanford CoreNLP Java server

## When to Use

- Building multilingual NLP pipelines that need tokenization, POS tagging, lemmatization, or dependency parsing across many languages
- Performing named entity recognition on text in 23+ supported languages
- Analyzing biomedical literature or clinical notes with domain-specific models
- Needing constituency parse trees for English, Chinese, Indonesian, Italian, Japanese, or Vietnamese
- Detecting the language of unknown text and routing to language-specific pipelines
- Resolving coreference chains in documents (English, Hebrew)
- Training custom NLP models on your own annotated data
- Integrating Stanford CoreNLP Java functionality from Python code
- Performing linguistic pattern matching on dependency trees with Semgrex/Ssurgeon

## Installation / Setup

Install via pip:

```bash
pip install stanza
```

Or via conda:

```bash
conda install -c stanfordnlp stanza
```

Requires Python 3.9+. Dependencies include PyTorch (>=1.13.0), numpy, protobuf (>=3.15.0), networkx, tqdm, and others. GPU is optional but recommended for faster processing.

Models are stored in `~/stanza_resources` by default. Override with the `STANZA_RESOURCES_DIR` environment variable or the `model_dir` parameter.

## Core Concepts

- **Pipeline**: The central object that chains together processors. Built with `stanza.Pipeline(lang, processors=...)`. Takes raw text or a Document and returns an annotated Document.
- **Processors**: Individual NLP task units (tokenize, mwt, pos, lemma, depparse, ner, sentiment, constituency, coref). Each has dependencies on earlier processors.
- **Document/Sentence/Token/Word**: The data objects hierarchy. A Document contains Sentences, each Sentence contains Tokens, and each Token wraps one or more Words (for multi-word tokens).
- **Universal Dependencies**: The formalism Stanza follows for POS tags (UPOS), morphological features (UFeats), and dependency relations. Models trained on UD v2.12 treebanks.
- **BIOES tagging**: The format used by the NER processor for token-level entity labels.

## Usage Examples

### Basic Pipeline

```python
import stanza

# Download English models (auto-downloads if missing)
stanza.download('en')

# Build a default pipeline with all processors
nlp = stanza.Pipeline('en')

# Annotate text
doc = nlp("Barack Obama was born in Hawaii. He was elected president in 2008.")

# Print dependency parse of first sentence
doc.sentences[0].print_dependencies()
```

### Selective Processors

```python
import stanza

# Only tokenize and run NER
nlp = stanza.Pipeline('en', processors='tokenize,ner')
doc = nlp("Chris Manning teaches at Stanford University.")

# Access named entities
for ent in doc.ents:
    print(f"entity: {ent.text}  type: {ent.type}")
# entity: Chris Manning  type: PERSON
# entity: Stanford University  type: ORG
```

### Multilingual Pipeline

```python
import stanza

# French dependency parsing
nlp = stanza.Pipeline('fr', processors='tokenize,mwt,pos,lemma,depparse')
doc = nlp("Nous avons atteint la fin du sentier.")

for word in doc.sentences[0].words:
    head_text = doc.sentences[0].words[word.head - 1].text if word.head > 0 else "root"
    print(f"{word.text} -> {head_text} ({word.deprel})")
```

### Sentiment Analysis

```python
import stanza

nlp = stanza.Pipeline('en', processors='tokenize,sentiment')
doc = nlp("I love this product!")
print(doc.sentences[0].sentiment)  # 2 (positive)
# 0=negative, 1=neutral, 2=positive
```

### Language Identification

```python
from stanza.pipeline.core import Pipeline

stanza.download('multilingual')
nlp = Pipeline(lang="multilingual", processors="langid")
doc = nlp("Bonjour le monde")
print(doc.lang)  # 'fr'
```

## Advanced Topics

**Pipeline and Processors**: Detailed processor configuration, custom processor variants, pretagged documents → [Pipeline and Processors](reference/01-pipeline-and-processors.md)

**Data Objects and Annotations**: Document, Sentence, Token, Word, Span, ParseTree — properties and methods → [Data Objects and Annotations](reference/02-data-objects.md)

**Processor Reference**: Complete reference for each processor with options and examples → [Processor Reference](reference/03-processor-reference.md)

**Models and Downloads**: Available models, languages, packages, manual download → [Models and Downloads](reference/04-models-and-downloads.md)

**Training Custom Models**: Training your own Stanza models on annotated data → [Training Custom Models](reference/05-training.md)

**CoreNLP Client**: Python wrapper for Stanford CoreNLP Java server, Semgrex, Ssurgeon → [CoreNLP Client](reference/06-corenlp-client.md)
