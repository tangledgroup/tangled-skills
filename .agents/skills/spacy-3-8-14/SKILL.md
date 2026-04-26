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

# spaCy 3.8.14

## Overview

spaCy is a free, open-source library for advanced Natural Language Processing (NLP) in Python, designed specifically for production use. It helps you build applications that process and "understand" large volumes of text — information extraction systems, natural language understanding pipelines, or preprocessing for deep learning.

Written from the ground up in carefully memory-managed Cython, spaCy excels at large-scale information extraction tasks. If your application needs to process entire web dumps, spaCy is the library you want.

**Key capabilities:**

- Support for **75+ languages** with tokenization
- **84+ trained pipelines** for 25 languages
- Multi-task learning with pretrained **transformers** (BERT, RoBERTa, etc.)
- Pretrained **word vectors**
- Production-ready **training system** with config-based reproducibility
- Components for **named entity recognition**, part-of-speech tagging, dependency parsing, sentence segmentation, text classification, lemmatization, morphological analysis, entity linking, coreference resolution, and more
- Easily extensible with **custom components** and attributes
- Support for custom models in **PyTorch**, **TensorFlow**, and other frameworks
- Built-in **visualizers** for syntax and NER (displaCy)
- Easy **model packaging**, deployment, and workflow management via spaCy projects
- Integration with **Large Language Models** via `spacy-llm`

**What spaCy is not:**

- Not a platform or SaaS — it's an open-source library
- Not an out-of-the-box chatbot engine
- Not research software (unlike NLTK or CoreNLP) — it's integrated and opinionated, designed to get things done

## When to Use

- Building information extraction systems from text
- Named entity recognition (persons, organizations, locations, products)
- Part-of-speech tagging and dependency parsing
- Text classification and categorization
- Rule-based pattern matching on tokenized text
- Training custom NLP models with spaCy's config system
- Processing large volumes of text efficiently in production
- Entity linking to knowledge bases
- Coreference resolution
- Integrating LLMs into structured NLP pipelines
- Building multilingual NLP applications (75+ languages supported)
- Preprocessing text for deep learning workflows

## Core Concepts

### Architecture

The central data structures are the **Language** class, the **Vocab**, and the **Doc** object:

- **Language (`nlp`)** — The processing pipeline. Takes raw text, sends it through components, returns an annotated `Doc`. Also orchestrates training and serialization.
- **Doc** — Owns the sequence of tokens and all their annotations. Constructed by the Tokenizer, then modified in place by pipeline components.
- **Token** / **Span** — Views that point into a Doc (not standalone objects).
- **Vocab** — Shared vocabulary storing strings, word vectors, and lexical attributes. Ensures a single source of truth and saves memory.
- **Lexeme** — A word type with no context (entry in the Vocab).
- **DocBin** — Efficient binary serialization for collections of Doc objects.
- **Example** — Training data container holding reference and predicted Doc objects.

### Processing Pipeline

When you call `nlp(text)`, spaCy first tokenizes the text to produce a `Doc`. The Doc is then processed by pipeline components in order. Each component returns the processed Doc, passed to the next component:

```
text → Tokenizer → Doc → tagger → parser → ner → lemmatizer → ... → annotated Doc
```

The tokenizer is special — it takes a string and produces a Doc (unlike other components which take and return a Doc). It does not appear in `nlp.pipe_names`.

### Processing Text Efficiently

For large volumes of text, use `nlp.pipe()` to process texts as a stream with internal batching:

```python
texts = ["First document.", "Second document."]
for doc in nlp.pipe(texts, batch_size=500):
    print(doc.ents)
```

Disable unused components for efficiency:

```python
# Only need entities, disable everything else
for doc in nlp.pipe(texts, disable=["tagger", "parser", "lemmatizer"]):
    print(doc.ents)
```

## Installation / Setup

### pip (recommended)

```bash
# Create virtual environment
python -m venv .env
source .env/bin/activate

# Install spaCy
pip install -U pip setuptools wheel
pip install -U spacy

# Download a trained pipeline
python -m spacy download en_core_web_sm
```

### Extra dependencies

Install with brackets for optional features:

- `spacy[lookups]` — lemmatization and lexeme normalization data tables
- `spacy[transformers]` — transformer model support (spacy-transformers)
- `spacy[cuda121]` — GPU support via CuPy for specific CUDA version
- `spacy[apple]` — thinc-apple-ops for Apple M1/M2 performance
- `spacy[ja]`, `spacy[ko]`, `spacy[th]` — tokenization dependencies for Japanese, Korean, Thai

### conda

```bash
conda install -c conda-forge spacy
```

### GPU support

```python
import spacy
spacy.prefer_gpu()  # or spacy.require_gpu() to enforce
nlp = spacy.load("en_core_web_trf")
```

### Compile from source

```bash
git clone https://github.com/explosion/spaCy
cd spaCy
pip install -r requirements.txt
pip install --no-build-isolation --editable .
```

Parallel builds (v3.4.0+):

```bash
SPACY_NUM_BUILD_JOBS=4 pip install --no-build-isolation --editable .
```

### VS Code Extension

The [spaCy VSCode Extension](https://github.com/explosion/spacy-vscode) provides hover descriptions for registry functions, variables, and section names within config files. Install from the VS Code marketplace as `Explosion.spacy-extension`. Requires spaCy >= 3.4.0 and pygls >= 1.0.0.

## Usage Examples

### Basic text processing

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

# Access token attributes
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.dep_, token.ent_type_)
```

### Named entity recognition

```python
doc = nlp("Barack Obama was born in Hawaii.")
for ent in doc.ents:
    print(ent.text, ent.label_)
# Barack Obama  PERSON
# Hawaii         GPE
```

Use `spacy.explain()` to get descriptions of labels:

```python
print(spacy.explain("GPE"))  # "Countries, cities, states"
```

### Dependency parsing

```python
doc = nlp("The cat sat on the mat")
for token in doc:
    print(f"{token.text} -> head: {token.head.text}, dep: {token.dep_}")
```

### Sentence segmentation

```python
doc = nlp("First sentence. Second sentence? Third one!")
for sent in doc.sents:
    print(sent.text)
```

### Text similarity (requires model with vectors)

```python
nlp = spacy.load("en_core_web_lg")  # includes word vectors
doc1 = nlp("I love cats")
doc2 = nlp("I adore felines")
print(doc1.similarity(doc2))  # float between 0 and 1
```

### Blank pipeline (tokenizer only)

```python
nlp = spacy.blank("en")
doc = nlp("Just tokenized, no trained components.")
for token in doc:
    print(token.text)
```

## Advanced Topics

**Pipeline Components**: Complete reference of all built-in components — Tokenizer, Tagger, DependencyParser, EntityRecognizer, Lemmatizer, TextCategorizer, EntityLinker, and more → [Pipeline Components](reference/01-pipeline-components.md)

**Linguistic Features**: Deep dive into POS tagging, morphology, lemmatization, dependency parsing, named entities, entity linking, tokenization, sentence segmentation, vectors and similarity → [Linguistic Features](reference/02-linguistic-features.md)

**Rule-based Matching**: Matcher, PhraseMatcher, DependencyMatcher, EntityRuler, SpanRuler — pattern-based extraction without training → [Rule-based Matching](reference/03-rule-based-matching.md)

**Training and Configuration**: Config system, `spacy train`, data formats (JSONL, spaCy binary), evaluation with Scorer, custom training functions, project workflows → [Training and Configuration](reference/04-training-and-config.md)

**Embeddings and Transformers**: Transformer integration, shared embedding layers, multi-task learning, static word vectors, pretraining → [Embeddings and Transformers](reference/05-embeddings-transformers.md)

**API Reference**: Container objects (Doc, Token, Span, Vocab), serialization, memory management, extension attributes, custom components, CLI commands → [API Reference](reference/06-api-reference.md)
