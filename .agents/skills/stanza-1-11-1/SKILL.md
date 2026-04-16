---
name: stanza-1-11-1
description: Stanford NLP Python library for linguistic analysis of 80+ human languages. Use when building multilingual NLP pipelines requiring tokenization, POS tagging, lemmatization, dependency parsing, NER, sentiment analysis, constituency parsing, or language identification with pretrained neural models or CoreNLP integration.
license: Apache-2.0
author: Tangled Skills <skills@tangled.dev>
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
  - https://stanfordnlp.github.io/stanza/
  - https://huggingface.co/stanfordnlp/models
---

# Stanza 1.11.1 - Stanford NLP Python Library

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

## Installation & Setup

### Quick Start with pip

```bash
pip install stanza
```

This installs Stanza with PyTorch dependencies automatically.

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

See [Model Downloading](references/02-model-downloading.md) for complete model packages and language support.

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

See [Pipeline Configuration](references/01-pipeline-configuration.md) for advanced options and custom processors.

## Advanced Topics

### Custom Processors and Variants

Create custom processors or integrate external tools like spaCy:

```python
from stanza.pipeline.processor import ProcessorVariant, register_processor_variant

@register_processor_variant('tokenize', 'spacy')
class SpacyTokenizer(ProcessorVariant):
    def __init__(self, config):
        import spacy
        self.nlp = spacy.load('en_core_web_sm')
    
    def process(self, text):
        doc = self.nlp(text)
        return [token.text for token in doc]
```

See [Custom Processors](references/05-custom-processors.md) for implementation details.

### Training Custom Models

Train models on your own annotated data:

```bash
# Clone repository for training
git clone https://github.com/stanfordnlp/stanza.git
cd stanza

# Set environment variables
source scripts/config.sh

# Train a tokenizer
python -m stanza.utils.training.run_tokenize UD_English-EWT --batch_size 32

# Train POS tagger
python -m stanza.utils.training.run_pos UD_English-EWT

# Train dependency parser
python -m stanza.utils.training.run_depparse UD_English-EWT
```

See [Model Training](references/06-model-training.md) for complete training workflows.

### CoreNLP Integration

Access Stanford CoreNLP Java tools from Python:

```python
from stanza.server import CoreNLPClient

# Start CoreNLP server
with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'ner'], timeout=30000) as client:
    doc = client.annotate("Barack Obama was born in Hawaii.")
    print(doc.sentences[0].words)
```

See [CoreNLP Client](references/07-corenlp-client.md) for setup and usage.

### Biomedical Models

Use specialized models for biomedical and clinical text:

```python
# Download biomedical package
stanza.download('en', package='biomed')

# Initialize with biomedical models
nlp = stanza.Pipeline('en', package='biomed')
doc = nlp("The patient presented with chest pain and shortness of breath.")
print(doc.entities)  # Biomedical entity recognition
```

See [Biomedical Models](references/08-biomedical-models.md) for available packages.

## References

- **Official documentation**: https://stanfordnlp.github.io/stanza/
- **GitHub repository**: https://github.com/stanfordnlp/stanza/tree/v1.11.1
- **Hugging Face models**: https://huggingface.co/stanfordnlp/models
- **Universal Dependencies**: https://universaldependencies.org/
- **Stanford CoreNLP**: https://stanfordnlp.github.io/CoreNLP/
- **ACL 2020 paper**: https://arxiv.org/abs/2003.07082
- **Biomedical models paper**: https://arxiv.org/abs/2007.14640

## Reference Files

For detailed topics, see:

1. [Pipeline Configuration](references/01-pipeline-configuration.md) - Processors, options, GPU/CPU control, custom config dicts
2. [Model Downloading](references/02-model-downloading.md) - Language support, packages, Hugging Face models (80+ languages)
3. [Data Objects & Annotations](references/03-data-objects.md) - Document, Sentence, Token, Word, Span, ParseTree APIs
4. [Processor Details](references/04-processor-details.md) - In-depth guide to each processor with examples
5. [Custom Processors](references/05-custom-processors.md) - Creating processors and variants, integrating external tools
6. [Model Training](references/06-model-training.md) - Training workflows, data preparation, evaluation
7. [CoreNLP Client](references/07-corenlp-client.md) - Java CoreNLP integration, Semgrex, Tsurgeon
8. [Biomedical Models](references/08-biomedical-models.md) - Clinical and biomedical NER models
