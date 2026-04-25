# Pretrained Models

Comprehensive guide to pretrained Sentence Transformer models.

## Model Categories

### General Purpose Embeddings

| Model | Dimensions | Languages | Best For |
|-------|------------|-----------|----------|
| `all-MiniLM-L6-v2` | 384 | English | Fast general-purpose embeddings |
| `all-mpnet-base-v2` | 768 | English | High-quality STS and paraphrase mining |
| `paraphrase-MiniLM-L6-v2` | 384 | English | Paraphrase detection |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 50+ | Multilingual paraphrases |
| `bge-large-en-v1.5` | 1024 | English | SOTA general embeddings |

### Information Retrieval (Asymmetric)

Optimized for query-document retrieval:

| Model | Dimensions | Best For |
|-------|------------|----------|
| `multi-qa-MiniLM-L6-cos-v1` | 384 | Question-answer retrieval (cosine) |
| `multi-qa-mpnet-base-dot-v1` | 768 | Question-answer retrieval (dot product) |
| `msmarco-roberta-base-v3` | 768 | Passage retrieval |
| `intfloat/e5-large-v2` | 1024 | General retrieval with prompts |

**Usage**:
```python
model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

# Use prompt templates for best results
query_emb = model.encode("What is AI?", prompt_name="query")
doc_emb = model.encode("AI is artificial intelligence", prompt_name="passage")
```

### Multilingual Models

| Model | Languages | Dimensions | Notes |
|-------|-----------|------------|-------|
| `paraphrase-multilingual-MiniLM-L12-v2` | 50+ | 384 | Good general multilingual |
| `LaBSE` | 109 | 768 | Google's language-agnostic model |
| `LaUSE` | 109 | 768 | Uncertainty-aware LaBSE |
| `paraphrase-xlm-r-multilingual-v1` | 100+ | 1024 | XLM-R based, high quality |

**Usage**:
```python
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Works across languages
embeddings = model.encode([
    "Hello world",          # English
    "Hola mundo",           # Spanish
    "Bonjour le monde",     # French
    "Hallo Welt",           # German
])
```

### Matryoshka Embeddings

Nested embeddings that work at multiple dimensions:

| Model | Dimensions | Notes |
|-------|------------|-------|
| `nomic-ai/nomic-embed-text-v1.5` | 64-768 | Open-source Matryoshka |
| `sentence-transformers/all-MiniLM-L6-v2-matryoshka` | 32-384 | MiniLM variant |

**Usage**:
```python
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")
embedding = model.encode("Hello world")

# Use any prefix length
emb_64 = embedding[:64]
emb_256 = embedding[:256]
emb_768 = embedding[:768]
```

### Sparse Embedding Models

| Model | Vocabulary | Sparsity | Notes |
|-------|------------|----------|-------|
| `naver/splade-distilbert-base` | 30,522 | 99%+ | Original SPLADE |
| `naver/splade-cocondenser-ensembledistil` | 30,522 | 99%+ | Better expansion |
| `BeIR/multilingual-splade-base` | 97,181 | 99%+ | Multilingual SPLADE |

**Usage**:
```python
from sentence_transformers import SparseEncoder
model = SparseEncoder("naver/splade-cocondenser-ensembledistil")
sparse_embeddings = model.encode(["query text"])
```

### Cross-Encoder (Reranker) Models

| Model | Task | Labels | Notes |
|-------|------|--------|-------|
| `cross-encoder/ms-marco-MiniLM-L6-v2` | Retrieval scoring | Regression | Fast reranker |
| `cross-encoder/quora-question-pairs-MiniLM-L6-cos-v1` | Duplicate detection | Binary | Question dedup |
| `cross-encoder/nli-deberta-v3-base` | NLI | 3-class | Entailment tasks |
| `BAAI/bge-reranker-base` | General reranking | Binary/Regression | SOTA reranking |

**Usage**:
```python
from sentence_transformers import CrossEncoder
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
ranks = model.rank(query, documents, top_k=10)
```

### Multimodal Models (CLIP)

| Model | Modalities | Dimensions | Notes |
|-------|------------|------------|-------|
| `clip-ViT-B-32` | Image-Text | 512 | Fast CLIP |
| `clip-ViT-L-14` | Image-Text | 768 | Higher accuracy |
| `clip-resnet-50` | Image-Text | 2048 | Faster, lower quality |

**Usage**:
```python
from sentence_transformers import SentenceTransformer
from PIL import Image

model = SentenceTransformer("clip-ViT-B-32")
image_emb = model.encode(Image.open("cat.jpg"))
text_emb = model.encode("a cute cat")
```

## Model Selection Guide

### For Semantic Search

1. **General purpose**: `multi-qa-MiniLM-L6-cos-v1` (fast) or `bge-large-en-v1.5` (accurate)
2. **Multilingual**: `paraphrase-multilingual-MiniLM-L12-v2`
3. **Long documents**: `intfloat/e5-large-v2` (supports 512 tokens)

### For Clustering

1. **English**: `all-MiniLM-L6-v2` or `all-mpnet-base-v2`
2. **Multilingual**: `paraphrase-multilingual-MiniLM-L12-v2`

### For Paraphrase Mining

1. **English**: `paraphrase-MiniLM-L6-v2`
2. **Multilingual**: `paraphrase-multilingual-MiniLM-L12-v2`

### For Retrieve & Rerank

1. **Retrieval**: `multi-qa-MiniLM-L6-cos-v1` (bi-encoder)
2. **Reranking**: `cross-encoder/ms-marco-MiniLM-L6-v2` or `BAAI/bge-reranker-base`

### For Zero-Shot Classification

1. **Text**: `sentence-transformers/all-MiniLM-L6-v2`
2. **Images**: `clip-ViT-B-32`

## Finding Models on Hugging Face

Browse all Sentence Transformer models:
- https://huggingface.co/models?library=sentence-transformers

Filter by task:
- Semantic search: `task_categories:Text+Similarity`
- Multilingual: `language:multi`
- Matryoshka: `tags:matryoshka`

## MTEB Leaderboard

Check model performance on Massive Text Embedding Benchmark:
- https://huggingface.co/spaces/mteb/leaderboard

Filter by:
- Task type (Retrieval, STS, Clustering, etc.)
- Language
- Model size

## Loading Models

### Basic Loading

```python
from sentence_transformers import SentenceTransformer

# Load from Hugging Face Hub
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load with specific device
model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")

# Load from local path
model = SentenceTransformer("./my-saved-model")
```

### Loading Options

```python
model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cuda",              # CPU or GPU
    cache_folder="./.cache",    # Custom cache location
    trust_remote_code=False,    # Security option
    revision="main",            # Specific git revision
)
```

### Model Cards

Each model has a card with:
- Training details
- Performance metrics
- Usage examples
- Citation information

View on Hugging Face Hub or access programmatically:
```python
from huggingface_hub import model_info

info = model_info("all-MiniLM-L6-v2")
print(info.cardData)  # Model metadata
```

## Saving and Sharing Models

### Save Locally

```python
model.save("./my-custom-model")
```

### Push to Hugging Face Hub

```python
# Requires huggingface-hub login
model.push_to_hub(
    "username/my-embedding-model",
    token="hf_...",  # Your HF token
)
```

### Model Card Template

Include in your model:
```markdown
---
library_name: sentence-transformers
tags:
  - sentence-transformers
  - embedding
datasets:
  - stsbenchmark
widget:
  - text: "Example sentence"
---

# My Custom Embedding Model

Fine-tuned on domain-specific data for better performance.

## Usage
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("username/my-model")
embeddings = model.encode(["your text"])
```
```

## Common Issues

### Issue: Model not found

**Solution**: Check exact model name on Hugging Face Hub

### Issue: Out of memory loading large model

**Solution**: Use smaller model or enable CPU offloading

### Issue: Slow inference

**Solution**: Use MiniLM variant or optimize with ONNX
