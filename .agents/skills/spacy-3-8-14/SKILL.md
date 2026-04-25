---
name: spacy-3-8-14
description: Industrial-strength NLP library for Python providing tokenization, named entity recognition, dependency parsing, text classification, and more with support for 70+ languages, neural network models, transformers, and production-ready training systems. Use when building NLP applications, performing linguistic analysis, training custom models, or integrating pretrained pipelines for tasks like NER, POS tagging, sentence segmentation, lemmatization, morphological analysis, entity linking, and rule-based matching.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.8.14"
tags:
  - nlp
  - natural-language-processing
  - text-analysis
  - machine-learning
  - python
  - transformers
category: machine-learning
external_references:
  - https://github.com/explosion/spaCy/tree/release-v3.8.14
  - https://course.spacy.io
  - https://github.com/explosion/projects
  - https://github.com/explosion/spaCy
  - https://github.com/explosion/spacy-vscode
  - https://spacy.io/api
  - https://spacy.io/models
  - https://spacy.io/usage
  - https://spacy.io/usage#changelog
  - https://spacy.io/
---
## Overview
spaCy is a comprehensive NLP toolkit that provides:

- **Tokenization** - Linguistically-motivated text segmentation
- **Named Entity Recognition (NER)** - Identify people, organizations, locations, and custom entities
- **Dependency Parsing** - Grammatical structure analysis
- **Part-of-Speech Tagging** - Word classification (noun, verb, adjective, etc.)
- **Text Classification** - Document-level and span-level categorization
- **Lemmatization** - Reduce words to their base/dictionary form
- **Morphological Analysis** - Grammatical feature extraction
- **Sentence Segmentation** - Split text into sentences
- **Entity Linking** - Connect entities to knowledge bases
- **Rule-based Matching** - Pattern matching with Matcher and Similarity

## When to Use
Use spaCy when you need:

- Production-ready NLP pipelines for applications
- Fast, accurate text processing at scale
- Pretrained models for 70+ languages
- Custom model training on your own data
- Integration with transformers (BERT, RoBERTa, etc.)
- Rule-based pattern matching combined with statistical models
- Multi-task learning and transfer learning
- GPU-accelerated processing for large datasets

## Quick Start
### Installation

```bash
# Install spaCy
pip install spacy

# Optional: Install lookups for lemmatization
pip install spacy[lookups]

# Or via conda
conda install -c conda-forge spacy
```

### Basic Usage

```python
import spacy

# Load a pretrained model
nlp = spacy.load("en_core_web_sm")

# Process text
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

# Extract information
for token in doc:
    print(token.text, token.pos_, token.dep_)

# Named entities
for ent in doc.ents:
    print(ent.text, ent.label_)

# Sentences
for sent in doc.sents:
    print(sent)
```

### Download Models

```bash
# Download English models (small, medium, large)
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m spacy download en_core_web_lg

# Download models for other languages
python -m spacy download de_core_news_sm  # German
python -m spacy download fr_core_news_sm  # French
python -m spacy download es_core_news_sm  # Spanish

# List installed models
python -m spacy validate
```

## Core Concepts
### The `nlp` Object (Language Pipeline)

The `nlp` object is a pipeline of components that process text:

```python
import spacy

nlp = spacy.load("en_core_web_sm")

# Check which components are in the pipeline
print(nlp.pipe_names)  # ['tagger', 'parser', 'attribute_ruler', 'lemmatizer']

# Process text through all components
doc = nlp("The quick brown fox jumps over the lazy dog.")
```

### The `Doc` Object (Processed Text)

A `Doc` object contains the processed text and all annotations:

```python
doc = nlp("Apple is looking at buying U.K. startup")

# Access tokens
for token in doc:
    print(token.text, token.pos_, token.dep_, token.lemma_)

# Access sentences
for sent in doc.sents:
    print(sent)

# Access entities
for ent in doc.ents:
    print(ent.text, ent.label_)

# Check if pipeline has specific components
print("parser" in nlp.pipe_names)  # True
print(doc.has_annotation("DEP"))   # True
```

### Tokens, Spans, and Docs

- **Token**: A single word or punctuation mark
- **Span**: A slice of the Doc (multiple tokens)
- **Doc**: The entire processed document

```python
doc = nlp("John Smith works at Google in Mountain View.")

# Token-level access
token = doc[0]  # "John"
print(token.text)      # "John"
print(token.pos_)      # "PROPN"
print(token.dep_)      # "nsubj"
print(token.lemma_)    # "john"

# Span-level access
span = doc[0:2]  # "John Smith"
print(span.text)     # "John Smith"
print(span.ent_type_) # "PERSON"

# Doc-level properties
print(doc.text)       # Full text
print(len(doc))       # Number of tokens
```

## Advanced Topics
## Advanced Topics

- [Pipelines Components](reference/01-pipelines-components.md)
- [Linguistic Features](reference/02-linguistic-features.md)
- [Matching Patterns](reference/03-matching-patterns.md)
- [Training Customization](reference/04-training-customization.md)
- [Transformers Embeddings](reference/05-transformers-embeddings.md)
- [Performance Deployment](reference/06-performance-deployment.md)
- [Cli Tools](reference/07-cli-tools.md)
- [Visualizers](reference/08-visualizers.md)

## Installation / Setup
### Requirements

- **Python**: >= 3.7, < 3.13 (64-bit only)
- **Operating Systems**: macOS, Linux, Windows
- **Optional**: CUDA-compatible GPU for GPU acceleration

### Platform-Specific Setup

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential python-dev git
pip install -U pip setuptools wheel
pip install spacy
```

**macOS:**
```bash
# Install XCode Command Line Tools
xcode-select --install
pip install -U pip setuptools wheel
pip install spacy
```

**Windows:**
```bash
# Install Visual C++ Build Tools matching your Python version
pip install -U pip setuptools wheel
pip install spacy
```

### Compile from Source

```bash
git clone https://github.com/explosion/spaCy
cd spaCy

python -m venv .env
source .env/bin/activate

pip install -r requirements.txt
pip install --no-build-isolation --editable .
```

## Common Patterns
### Text Classification

```python
import spacy
from spacy.pipeline import TextCategorizer

# Load model with text classification
nlp = spacy.load("en_core_web_md")

doc = nlp("I love this product, it's amazing!")
print(doc.cats["POSITIVE"])  # Probability score
print(doc.cats["NEGATIVE"])
```

### Custom Named Entity Recognition

```python
from spacy.pipeline import EntityRuler

nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")

# Add patterns
patterns = [
    {"label": "PRODUCT", "pattern": [{"TEXT": "iPhone"}]},
    {"label": "PRODUCT", "pattern": [{"TEXT": "MacBook"}]},
]
ruler.add_patterns(patterns)

doc = nlp("I bought a new iPhone and MacBook")
for ent in doc.ents:
    print(ent.text, ent.label_)
```

### Rule-Based Matching

```python
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Add pattern: ADJ + NOUN
pattern = [{"POS": "ADJ"}, {"POS": "NOUN"}]
matcher.add("ADJ_NOUN", [pattern])

doc = nlp("The quick brown fox")
matches = matcher(doc)

for match_id, start, end in matches:
    print(doc[start:end].text)
```

### Batch Processing

```python
# Process multiple documents efficiently
texts = [
    "First document text here",
    "Second document text here",
    "Third document text here"
]

# Use pipe for batch processing
for doc in nlp.pipe(texts, batch_size=32):
    process(doc)
```

## Troubleshooting
### Model Not Found Error

```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solution:** Download the model first:
```bash
python -m spacy download en_core_web_sm
```

### Memory Issues with Large Documents

**Solution:** Use batch processing and limit pipeline components:
```python
# Remove unnecessary components
nlp = spacy.load("en_core_web_sm", exclude=["parser", "lemmatizer"])

# Process in batches
for doc in nlp.pipe(texts, batch_size=16):
    process(doc)
```

### Slow Processing

**Solutions:**
1. Use a smaller model (`_sm` instead of `_lg`)
2. Enable GPU processing if available
3. Use batch processing with `nlp.pipe()`
4. Remove unnecessary pipeline components
5. Consider using `en_core_web_sm` for basic tasks

### Import Errors on Windows

```
ImportError: DLL load failed
```

**Solution:** Install Visual C++ Redistributable or reinstall spaCy:
```bash
pip uninstall spacy
pip install --no-cache-dir spacy
```

## Performance Tips
1. **Use the right model size**: `_sm` for speed, `_lg` for accuracy
2. **Batch processing**: Use `nlp.pipe()` instead of looping with `nlp()`
3. **Exclude unused components**: Load only what you need
4. **GPU acceleration**: Enable for transformer models and large batches
5. **Caching**: Reuse the `nlp` object, don't reload in loops

## Migration from v2.x
Key changes in spaCy 3.x:

1. **Configuration files**: Now use `.cfg` format instead of Python scripts
2. **Training API**: Simplified with `spacy train` command
3. **Model packages**: Changed structure and naming
4. **Pipeline components**: Some components renamed or restructured

See the [migration guide](https://spacy.io/usage/v3) for detailed instructions.

## License
spaCy is released under the MIT License. See https://github.com/explosion/spaCy/blob/master/LICENSE

