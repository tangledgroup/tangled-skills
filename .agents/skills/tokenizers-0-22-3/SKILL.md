---
name: tokenizers-0-22-3
description: Fast state-of-the-art tokenizers library for NLP written in Rust with Python, Node.js, and Ruby bindings. Use when training custom vocabularies, implementing BPE/WordPiece/Unigram tokenization, building NLP pipelines, or working with transformer models requiring efficient text preprocessing with alignment tracking.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.22.3"
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
## Overview
🤗 Tokenizers provides implementations of today's most used tokenization algorithms (BPE, WordPiece, Unigram, ByteLevel, etc.) with a focus on performance and versatility. The library can tokenize a GB of text in less than 20 seconds on a server CPU.

**Key features:**
- **Extremely fast**: Rust implementation provides 10-100x speedup over pure Python tokenizers
- **Alignment tracking**: Full character-level tracking even with destructive normalization
- **Complete pipeline**: Normalization, pre-tokenization, model, post-processing, and decoding
- **Multi-language**: Python, Node.js, Ruby bindings with identical APIs
- **Production-ready**: Used in Hugging Face Transformers library

## When to Use
Use this skill when:
- Training custom tokenizers on domain-specific text corpora
- Implementing BPE, WordPiece, Unigram, or other tokenization algorithms
- Building NLP pipelines requiring efficient text preprocessing
- Working with transformer models that need specific tokenization
- Needing character-level alignment between tokens and original text
- Processing large text volumes where performance matters
- Creating custom vocabularies for language models

## Core Concepts
### Tokenization Pipeline

The tokenization process follows four sequential steps:

```
Raw Text → Normalization → Pre-tokenization → Model → Post-processing → Output
```

1. **Normalization**: Clean and standardize text (Unicode normalization, lowercasing, accent removal)
2. **Pre-tokenization**: Split text into initial units (words, bytes, characters)
3. **Model**: Apply tokenization algorithm (BPE, WordPiece, Unigram, etc.)
4. **Post-processing**: Add special tokens, handle pairs, format for specific models

### Alignment Tracking

Tokenizers maintains character offsets throughout the pipeline, allowing you to map any token back to its position in the original text:

```python
output = tokenizer.encode("Hello, world!")
print(output.offsets[0])  # (0, 5) - "Hello" spans characters 0-5
original_text[0:5]        # "Hello"
```

### Special Tokens

Special tokens are reserved vocabulary entries for model-specific purposes:
- `[UNK]`: Unknown token for out-of-vocabulary words
- `[CLS]`: Classification token (BERT-style models)
- `[SEP]`: Separator token between sequence pairs
- `[PAD]`: Padding token for batch processing
- `[MASK]`: Mask token for masked language modeling

## Installation / Setup
### Python

```bash
# Install from PyPI
pip install tokenizers

# Install latest from source (requires Rust)
pip install git+https://github.com/huggingface/tokenizers.git#subdirectory=bindings/python
```

### Node.js

```bash
npm install @huggingface/tokenizers
```

### Rust

Add to `Cargo.toml`:
```toml
[dependencies]
tokenizers = "0.22"
```

See [Installation Guide](reference/01-installation.md) for detailed setup instructions and building from source.

## Usage Examples
### Training a BPE Tokenizer

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

# Initialize tokenizer with BPE model
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))

# Configure pre-tokenizer to split on whitespace
tokenizer.pre_tokenizer = Whitespace()

# Setup trainer with special tokens
trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]
)

# Train on text files
tokenizer.train(files=["wiki.train.raw", "wiki.valid.raw"], trainer=trainer)

# Save tokenizer
tokenizer.save("tokenizer.json")
```

### Loading and Using a Tokenizer

```python
from tokenizers import Tokenizer

# Load saved tokenizer
tokenizer = Tokenizer.from_file("tokenizer.json")

# Encode text
encoding = tokenizer.encode("Hello, world!")
print(encoding.tokens)  # ["Hello", ",", "world", "!"]
print(encoding.ids)     # [12345, 67, 8901, 23]

# Access character offsets
print(encoding.offsets[0])  # (0, 5) - position of "Hello" in original text
```

See [Quick Start Guide](reference/02-quick-start.md) for more examples including batch encoding and padding.

## Advanced Topics
## Advanced Topics

- [Installation](reference/01-installation.md)
- [Quick Start](reference/02-quick-start.md)
- [Pipeline Components](reference/03-pipeline-components.md)
- [Models](reference/04-models.md)
- [Training Guide](reference/05-training-guide.md)
- [Special Tokens](reference/06-special-tokens.md)
- [Api Reference](reference/07-api-reference.md)

## Performance Tips
1. **Use batch encoding**: `encode_batch()` is significantly faster than looping over `encode()`
2. **Train with batches**: Provide file lists or iterators in batches for faster training
3. **Choose right pre-tokenizer**: ByteLevel enables smaller vocabularies (256 base tokens)
4. **Avoid unnecessary normalization**: Each normalizer adds processing overhead
5. **Cache tokenizers**: Load once and reuse across requests

## Troubleshooting
### "Tokenizer not found" errors

Ensure you're loading the correct file format:
```python
# JSON format (most common)
tokenizer = Tokenizer.from_file("tokenizer.json")

# From pretrained model (requires transformers)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
```

### Training fails on large corpora

Use memory-efficient training with iterators:
```python
def file_iterator(file_paths, batch_size=1024):
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            batch = []
            for line in f:
                batch.append(line)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

tokenizer.train(files=file_iterator(["large_file1.txt", "large_file2.txt"]), trainer=trainer)
```

### Alignment offsets don't match original text

Check your normalization pipeline - destructive normalizers (lowercasing, accent removal) change character positions but maintain tracking:
```python
# Normalization changes the text but tracks original positions
tokenizer.normalizer = NFKC()  # Unicode normalization
encoding = tokenizer.encode("Café")  # Original has é
print(encoding.offsets[0])  # Points to "Café" in original, not normalized version
```

## Version Compatibility
| Component | Version | Notes |
|-----------|---------|-------|
| Rust Core | 0.22.2 | Base implementation |
| Python Bindings | 0.22.3 | Latest stable with bug fixes |
| Node.js Bindings | 0.22.3 | Full feature parity |
| Ruby Bindings | 0.22.0 | Community-maintained |

## Migration Notes
### From v0.1x to v0.22.x

- **Breaking change**: `tokenizer.encode_batch()` now returns list of `Encoding` objects (was tuple)
- **New feature**: LLaMA tokenizer support added
- **Improved**: UTF-8 handling in ByteLevel pre-tokenizer
- **Deprecated**: `BertWordPieceTokenizer` renamed to `WordPiece`

### From transformers.AutoTokenizer

The tokenizers library can work standalone or with transformers:

```python
# Standalone (faster, no transformers dependency)
from tokenizers import Tokenizer
tokenizer = Tokenizer.from_file("path/to/tokenizer.json")

# With transformers (auto-downloads from Hub)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
```

## Related Skills
Consider these complementary skills:
- **transformers**: For working with pre-trained models that use tokenizers
- **datasets**: For loading and processing training corpora
- **accelerate**: For distributed training with custom tokenizers

