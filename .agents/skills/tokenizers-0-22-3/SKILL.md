---
name: tokenizers-0-22-3
description: Fast state-of-the-art tokenizers library for NLP written in Rust with
  Python, Node.js, and Ruby bindings. Use when training custom vocabularies, implementing
  BPE/WordPiece/Unigram tokenization, building NLP pipelines, or working with transformer
  models requiring efficient text preprocessing with alignment tracking.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: 0.22.3
tags:
- nlp
- tokenization
- rust
- python
- transformers
- bpe
- wordpiece
- unigram
category: nlp
external_references:
- https://github.com/huggingface/tokenizers/tree/v0.22.2
- https://github.com/huggingface/tokenizers
- https://github.com/huggingface/tokenizers/releases/tag/v0.22.2
- https://huggingface.co/docs/transformers/tokenizer_summary
- https://pypi.org/project/tokenizers/
- https://huggingface.co/docs/tokenizers
---

# Tokenizers 0.22.3

## Overview

🤗 Tokenizers is a fast, state-of-the-art tokenization library written in Rust with bindings for Python, Node.js, and Ruby. It provides implementations of today's most used tokenizers (BPE, WordPiece, Unigram, WordLevel) with a focus on performance and versatility. The same tokenizers power the 🤗 Transformers library.

Key capabilities:

- **Train new vocabularies** from text corpora using BPE, WordPiece, Unigram, or WordLevel algorithms
- **Extremely fast** — Rust implementation tokenizes a GB of text in under 20 seconds on a server CPU
- **Full alignment tracking** — even with destructive normalization, always map tokens back to the original input text
- **Complete preprocessing pipeline** — truncation, padding, special token insertion, attention masks
- **Designed for both research and production**

## When to Use

- Training a custom vocabulary from a text corpus (wikitext, domain-specific data, etc.)
- Implementing BPE, WordPiece, Unigram, or WordLevel tokenization
- Building NLP preprocessing pipelines with normalization, pre-tokenization, and post-processing
- Working with transformer models that require efficient text preprocessing
- Needing alignment tracking between tokens and original text spans (offsets)
- Loading pretrained tokenizers from the Hugging Face Hub
- Converting legacy vocabulary files into modern tokenizer format

## Core Concepts

### The Tokenization Pipeline

Every `Tokenizer` processes input text through a four-stage pipeline:

1. **Normalization** — Clean and standardize raw text (Unicode normalization, lowercasing, accent stripping). Alignment is tracked so tokens can always be mapped back to original text.
2. **Pre-tokenization** — Split normalized text into sub-units (words, bytes, characters) that define upper bounds for final tokens.
3. **Model** — The core algorithm (BPE, WordPiece, Unigram, or WordLevel) that splits pre-tokens into vocabulary tokens and maps them to integer IDs.
4. **Post-processing** — Add special tokens (`[CLS]`, `[SEP]`, etc.), set type IDs for sequence pairs.

### Models

The model is the only mandatory component. It defines the tokenization algorithm:

- **BPE** (Byte-Pair Encoding) — Starts from characters, iteratively merges most frequent pairs. Used by GPT-2, RoBERTa.
- **WordPiece** — Greedy longest-match algorithm using `##` prefix for continuing subwords. Used by BERT.
- **Unigram** — Probabilistic model that selects the best tokenization to maximize sentence probability. Used by mBART, XLM-R.
- **WordLevel** — Simple word-to-ID mapping. Requires very large vocabularies for good coverage.

### Alignment Tracking

A distinguishing feature of 🤗 Tokenizers is full alignment tracking. Even after destructive normalization (lowercasing, accent removal), every token in the output can be mapped back to its exact span in the original input text via the `offsets` attribute of an `Encoding`.

### Encoding Object

The output of tokenization is an `Encoding` object containing:

- `tokens` — List of token strings
- `ids` — List of integer IDs
- `type_ids` — Sequence type IDs (0 for first sequence, 1 for second in pairs)
- `attention_mask` — Binary mask indicating real tokens vs padding
- `offsets` — Character-level `(start, end)` tuples mapping each token back to the original text

## Installation / Setup

Install from PyPI:

```bash
pip install tokenizers
```

Requires Python 3.9+. Prebuilt wheels are available for Linux, macOS, and Windows.

Install from source (requires Rust toolchain):

```bash
git clone https://github.com/huggingface/tokenizers
cd tokenizers/bindings/python
pip install -e .
```

## Usage Examples

### Quickstart: Train a BPE Tokenizer

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import BpeTrainer

# Initialize with BPE model
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))

# Set pre-tokenizer to split on whitespace
tokenizer.pre_tokenizer = Whitespace()

# Configure trainer
trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)

# Train on files
files = ["data/wiki.train.raw", "data/wiki.valid.raw", "data/wiki.test.raw"]
tokenizer.train(files, trainer)

# Save and reload
tokenizer.save("tokenizer.json")
tokenizer = Tokenizer.from_file("tokenizer.json")
```

### Encode Text

```python
output = tokenizer.encode("Hello, y'all! How are you?")

print(output.tokens)   # ["Hello", ",", "y", "'", "all", ...]
print(output.ids)       # [27253, 16, 93, 11, 5097, ...]
print(output.offsets)   # [(0, 5), (5, 6), (6, 7), ...]
```

### Alignment Tracking

Map a token back to its original text span:

```python
output = tokenizer.encode("Hello, y'all! How are you 😁 ?")
# Find what caused the [UNK] token (index 9)
start, end = output.offsets[9]
print(sentence[start:end])  # "😁"
```

### Post-processing with Special Tokens

Add `[CLS]` and `[SEP]` tokens for BERT-style inputs:

```python
from tokenizers.processors import TemplateProcessing

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]")),
    ],
)

# Single sequence
output = tokenizer.encode("Hello there")
print(output.tokens)  # ["[CLS]", "Hello", "there", "[SEP]"]

# Sequence pair with type IDs
output = tokenizer.encode("Hello there", "How are you?")
print(output.type_ids)  # [0, 0, 0, 0, 1, 1, 1, 1]
```

### Batch Encoding with Padding

```python
# Enable automatic padding
tokenizer.enable_padding(pad_id=3, pad_token="[PAD]")

outputs = tokenizer.encode_batch([
    "Short sentence",
    "This is a much longer sentence that needs padding"
])

print(outputs[0].attention_mask)  # [1, 1, 1, 1, 0, ...]  (padded positions = 0)
```

### Load Pretrained from Hub

```python
from tokenizers import Tokenizer

tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
```

## Advanced Topics

**Tokenization Pipeline**: Normalization, pre-tokenization, model, and post-processing in detail with the BERT-from-scratch example → [Tokenization Pipeline](reference/01-pipeline.md)

**Models Reference**: BPE, WordPiece, Unigram, and WordLevel — parameters, behavior, and training algorithms → [Models Reference](reference/02-models.md)

**Components Reference**: Normalizers, pre-tokenizers, post-processors, decoders, trainers, and added tokens → [Components Reference](reference/03-components.md)

**API Reference**: Tokenizer class methods, Encoding object attributes, input types, padding/truncation, batch operations, and the visualizer tool → [API Reference](reference/04-api-reference.md)
