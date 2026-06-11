# Embeddings and Transformers

## Overview

spaCy supports transfer and multi-task learning workflows that improve pipeline efficiency and accuracy. Transfer learning imports knowledge from raw text into your pipeline so models generalize better from annotated examples.

### Word Vectors vs. Language Models

**Word vectors** model lexical types (words without context). They are computationally efficient — mapping a word to a vector is a single indexing operation. Best for:

- Improving accuracy of neural network models
- Tasks with terms and no surrounding context
- Terminology lists and gazetteers

**Transformers** (BERT, RoBERTa) provide contextual embeddings. More accurate but require GPU for effective deployment. Best for:

- Full sentences or paragraphs
- Complex NLP tasks requiring context understanding
- State-of-the-art accuracy

## Transformer Integration

Install `spacy-transformers` to use transformer models:

```bash
pip install spacy-transformers
```

### Using Pretrained Transformer Pipelines

```python
import spacy

# Load transformer-based pipeline
nlp = spacy.load("en_core_web_trf")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
for token in doc:
    print(token.text, token.pos_, token.ent_type_)
```

Transformer pipelines (`_trf`) achieve state-of-the-art accuracy but are slower and require more memory than standard pipelines.

### Adding Transformer to Custom Pipeline

In the config, use the `transformer` component:

```ini
[nlp]
pipeline = ["transformer", "tok2vec", "ner"]

[components.transformer]
factory = "transformer"
name = "roberta-base"
mixed_precision = false

[components.transformer.model]
@architectures = "spacy.TransformerListener.v1"
grad_factor = 1.0
pooling = { @layers = "reduce_mean.v1" }
upstream = *

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.embed]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 96
rows = [512, 128, 64, 32]
window_size = 1
maxout_pieces = 3
depth = 2

[components.tok2vec.encoder]
@architectures = "spacyTransformerListener.v1"
upstream = *
```

The `TransformerListener` pattern lets the tok2vec "listen" to transformer outputs, enabling shared embeddings.

## Shared Embedding Layers

spaCy lets you share a single transformer or tok2vec embedding layer between multiple components:

**Benefits:**
- Smaller models (single copy of embeddings)
- Faster inference (embed documents once for whole pipeline)
- Multi-task learning (shared layer updated during training)

**Trade-offs:**
- Less modular (components require the same embedding component)
- May affect accuracy (positively or negatively)
- Harder to swap components or retrain parts of the pipeline

```ini
[nlp]
pipeline = ["tok2vec", "tagger", "parser", "ner"]

[components.tok2vec]
factory = "tok2vec"

[components.tagger]
factory = "tagger"
tok2vec_name = "tok2vec"  # Share tok2vec

[components.parser]
factory = "parser"
tok2vec_name = "tok2vec"  # Share tok2vec

[components.ner]
factory = "ner"
tok2vec_name = "tok2vec"  # Share tok2vec
```

## Static Word Vectors

### Loading Pretrained Vectors

Convert vectors from FastText, Gensim, or other formats:

```bash
# Convert GloVe vectors
python -m spacy init-vectors en vectors_glove glove_vectors.txt --vectors-strings words.txt

# Use with training
python -m spacy train config.cfg --init-vectors vectors_glove
```

### Using Vectors in Config

```ini
[initialize]
vectors = { width = 300, source = "vectors_glove" }
```

Or load directly:

```python
import numpy as np
from spacy.vectors import Vectors

# Create vectors from arrays
keys = ["hello", "world"]
vectors = np.array([[0.1, 0.2], [0.3, 0.4]])
nlp.vocab.add_vectors(Vectors(length=2, keys=keys, vectors=vectors))
```

### Vector Similarity

```python
nlp = spacy.load("en_core_web_lg")

# Token similarity
doc = nlp("The cat and the banana")
print(doc[1].similarity(doc[3]))  # "cat" vs "banana"

# Has vector check
print(nlp.vocab["cat"].has_vector)  # True
print(nlp.vocab["obscureword"].has_vector)  # False (OOV)
```

## Pretraining

spaCy supports language model pretraining via `spacy pretrain`:

```bash
# Pretrain a language model on unlabeled text
python -m spacy pretrain config_pretrain.cfg \
    --output pretrained_model \
    --paths.raw ./raw_text.txt
```

The pretraining config specifies the architecture and corpus. The resulting weights can initialize downstream task training.

## GPU Support

Transformer models benefit significantly from GPU:

```python
import spacy

# Prefer GPU if available
spacy.prefer_gpu()

# Require GPU (raises error if unavailable)
spacy.require_gpu()

nlp = spacy.load("en_core_web_trf")
```

Install with CUDA support:

```bash
pip install spacy[cuda121]  # for CUDA 12.x
pip install spacy[cuda118]  # for CUDA 11.8
```

## Memory Management with Transformers

Transformer models can exhaust GPU memory. Use the `doc_cleaner` component:

```python
nlp.add_pipe("doc_cleaner", last=True)
```

For persistent services, use memory zones:

```python
with nlp.select_pipes(disable=["transformer"]):
    # Process without transformer
    pass

# Or use memory_zone (v3.8+)
with nlp.memory_zone():
    doc = nlp("Process this text")
    results = extract_info(doc)
    # Results extracted before zone exits
# Memory freed here — don't access doc after this point
```

## Large Language Models (spacy-llm)

The `spacy-llm` package integrates LLMs into spaCy pipelines:

```ini
[components.llm]
factory = "llm"

[components.llm.task]
@tasks = "llm_text_cat.v1"
labels = {"positive": "Positive sentiment", "negative": "Negative sentiment"}

[components.llm.model]
@models = "openai.GPT-3.5-turbo.v1"
```

Key features:
- Serializable LLM component in your pipeline
- Support for OpenAI API (GPT-4, GPT-3.5)
- Self-hosted open-source models via Hugging Face
- Integration with LangChain
- Tasks: text classification, NER, coreference resolution, information extraction
