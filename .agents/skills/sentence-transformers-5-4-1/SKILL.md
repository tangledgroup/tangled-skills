---
name: sentence-transformers-5-4-1
description: A comprehensive toolkit for computing text embeddings, semantic search, and reranking using Sentence Transformers v5.4.1. Provides dense, sparse, and cross-encoder models for semantic textual similarity, paraphrase mining, clustering, retrieve-and-rerank pipelines, and multimodal applications with support for 100+ languages and extensive training capabilities.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "5.4.1"
tags:
  - embeddings
  - semantic-search
  - reranking
  - nlp
  - pytorch
  - transformers
  - sentence-embeddings
  - cross-encoder
  - sparse-encoder
category: machine-learning/nlp
external_references:
  - https://github.com/huggingface/sentence-transformers/tree/v5.4.1
  - https://www.sbert.net/index.html
  - https://huggingface.co/sentence-transformers
---

# Sentence Transformers 5.4.1

A comprehensive framework for computing embeddings from text, images, and audio using state-of-the-art transformer models. Supports dense embeddings (Sentence Transformer), sparse embeddings (Sparse Encoder), and reranking (Cross Encoder) with training capabilities for custom models.

## Overview

Sentence Transformers is the go-to library for:

- **Dense Embeddings**: Convert text to fixed-size vector representations for semantic similarity
- **Sparse Embeddings**: Generate sparse, interpretable embeddings with vocabulary-sized dimensions
- **Reranking**: Score query-document pairs with Cross-Encoder models for high-accuracy ranking
- **Multimodal**: Process images, audio, and video alongside text
- **Training**: Fine-tune models on custom datasets with 20+ loss functions
- **100+ Languages**: Multilingual support including English, German, French, Spanish, Chinese, Arabic, and more

## When to Use

Load this skill when you need to:

- Generate sentence/document embeddings for semantic search or clustering
- Implement retrieve-and-rerank pipelines for question answering or search
- Fine-tune embedding models on domain-specific data
- Compute semantic textual similarity (STS) scores
- Mine paraphrases or duplicate questions from large datasets
- Work with sparse embeddings for hybrid search systems
- Process multimodal data (image-text, audio-text pairs)
- Evaluate embedding models using MTEB benchmarks

## Core Concepts

### Three Model Types

| Model Type | Class | Use Case | Speed | Accuracy |
|------------|-------|----------|-------|----------|
| **Sentence Transformer** | `SentenceTransformer` | Dense embeddings for retrieval | Fast | Good |
| **Cross Encoder** | `CrossEncoder` | Reranking/scoring pairs | Slow | Excellent |
| **Sparse Encoder** | `SparseEncoder` | Sparse embeddings for hybrid search | Very Fast | Good |

### Embedding Types

- **Dense Embeddings**: Fixed-size vectors (e.g., 384, 768, 1024 dimensions) stored in vector databases
- **Sparse Embeddings**: Vocabulary-sized sparse vectors (e.g., 30,522 dimensions with 99%+ zeros) for BM25-like retrieval
- **Matryoshka Embeddings**: Nested embeddings where prefixes maintain quality at different dimensions

### Training Paradigms

- **Supervised Learning**: Train with labeled pairs (similarities, labels, or rankings)
- **Unsupervised Learning**: TSDAE, SimCSE, CT for unlabeled data
- **Domain Adaptation**: Adapt pretrained models to specific domains
- **Distillation**: Compress large models into smaller, faster versions

## Installation

### Basic Installation

```bash
# With pip
pip install -U sentence-transformers

# With uv (recommended)
uv add sentence-transformers

# With conda
conda install -c conda-forge sentence-transformers

# From source
git clone https://github.com/huggingface/sentence-transformers.git
cd sentence-transformers
pip install -e ".[dev]"
```

### System Requirements

- **Python**: 3.10+
- **PyTorch**: 1.11.0+
- **Transformers**: 4.34.0+

### GPU Support (Optional)

For CUDA/GPU acceleration, install PyTorch with matching CUDA version:

```bash
# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Or follow https://pytorch.org/get-started/locally/
```

## Quick Start

### Dense Embeddings (Sentence Transformer)

```python
from sentence_transformers import SentenceTransformer

# 1. Load a pretrained model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2. Encode texts to embeddings
sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
]
embeddings = model.encode(sentences)
print(embeddings.shape)  # (3, 384)

# 3. Compute similarities
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.6660, 0.1046],
#         [0.6660, 1.0000, 0.1411],
#         [0.1046, 0.1411, 1.0000]])
```

### Reranking (Cross Encoder)

```python
from sentence_transformers import CrossEncoder

# 1. Load a reranker model
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

# 2. Score query-passage pairs
query = "How many people live in Berlin?"
passages = [
    "Berlin had a population of 3,520,031 registered inhabitants.",
    "Berlin has about 135 million day visitors yearly.",
    "In 2013 around 600,000 Berliners were in sports clubs.",
]

# Method A: Predict scores manually
scores = model.predict([(query, passage) for passage in passages])
print(scores)  # [8.607139 5.506266 6.352977]

# Method B: Use built-in ranking
ranks = model.rank(query, passages, return_documents=True)
for rank in ranks:
    print(f"#{rank['corpus_id']} ({rank['score']:.2f}): {rank['text'][:50]}...")
```

### Sparse Embeddings (Sparse Encoder)

```python
from sentence_transformers import SparseEncoder

# 1. Load a sparse encoder model
model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# 2. Encode texts to sparse embeddings
sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
]
embeddings = model.encode(sentences)
print(embeddings.shape)  # [3, 30522] - vocabulary size

# 3. Compute similarities
similarities = model.similarity(embeddings, embeddings)
print(similarities)

# 4. Check sparsity statistics
stats = SparseEncoder.sparsity(embeddings)
print(f"Sparsity: {stats['sparsity_ratio']:.2%}")  # Sparsity: 99.84%
```

## Reference Files

This skill is organized into modular reference files for efficient context loading:

### Core Usage

- [`references/01-sentence-transformer.md`](references/01-sentence-transformer.md) - Dense embeddings, encoding options, prompt templates, batch processing, multi-GPU
- [`references/02-cross-encoder.md`](references/02-cross-encoder.md) - Reranking models, scoring pairs, ranking APIs, custom models
- [`references/03-sparse-encoder.md`](references/03-sparse-encoder.md) - Sparse embeddings, SPLADE models, hybrid search, sparsity statistics

### Applications

- [`references/04-applications.md`](references/04-applications.md) - Semantic search, clustering, paraphrase mining, STS, image search, retrieve-and-rerank
- [`references/05-multimodal.md`](references/05-multimodal.md) - Image-text models, audio processing, video embeddings, cross-modal retrieval

### Training

- [`references/06-training-overview.md`](references/06-training-overview.md) - Training components, datasets, loss functions, evaluators, trainer API
- [`references/07-loss-functions.md`](references/07-loss-functions.md) - 20+ loss functions for different tasks (contrastive, triplet, softmax, margin mining)
- [`references/08-training-examples.md`](references/08-training-examples.md) - STS, NLI, paraphrases, MS MARCO, multilingual, matryoshka embeddings

### Advanced Topics

- [`references/09-model-optimization.md`](references/09-model-optimization.md) - ONNX, OpenVINO, quantization, distillation, PEFT adapters, Unsloth
- [`references/10-pretrained-models.md`](references/10-pretrained-models.md) - Model zoo, multilingual models, domain-specific models, MTEB leaderboard

### Migration & Utilities

- [`references/11-migration-guide.md`](references/11-migration-guide.md) - v5.x to v5.4 migration, breaking changes, API updates
- [`references/12-evaluation.md`](references/12-evaluation.md) - MTEB evaluation, leaderboard submission, custom metrics

## Common Patterns

### Semantic Search Pipeline

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Encode corpus once
model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
corpus = ["Document 1 text...", "Document 2 text...", "Document 3 text..."]
corpus_embeddings = model.encode(corpus, normalize_embeddings=True)

# Search for a query
query = "What are the benefits of exercise?"
query_embedding = model.encode(query, normalize_embeddings=True)

# Cosine similarity (dot product since normalized)
similarities = corpus_embeddings @ query_embedding
top_k = similarities.argsort()[-3:][::-1]

for idx in top_k:
    print(f"{similarities[idx]:.3f} - {corpus[idx][:50]}...")
```

### Retrieve and Rerank Pipeline

```python
from sentence_transformers import SentenceTransformer, CrossEncoder

# 1. Retrieve top-50 with bi-encoder (fast)
retriever = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
query = "How to fix a flat tire?"
corpus = [...]  # Large document corpus
corpus_embeddings = retriever.encode(corpus, normalize_embeddings=True)
query_embedding = retriever.encode(query, normalize_embeddings=True)
top_50_indices = (corpus_embeddings @ query_embedding).argsort()[-50:][::-1]
top_50_docs = [corpus[i] for i in top_50_indices]

# 2. Rerank top-50 with cross-encoder (accurate)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
ranks = reranker.rank(query, top_50_docs, top_k=10)

for rank in ranks:
    print(f"#{rank['corpus_id']} ({rank['score']:.2f}): {rank['text'][:60]}...")
```

### Clustering Documents

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
documents = [...]  # List of documents
embeddings = model.encode(documents)

# K-Means clustering
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
clusters = kmeans.fit_predict(embeddings)

# Group documents by cluster
for cluster_id in range(num_clusters):
    cluster_docs = [documents[i] for i in range(len(documents)) if clusters[i] == cluster_id]
    print(f"\nCluster {cluster_id} ({len(cluster_docs)} docs):")
    for doc in cluster_docs[:3]:
        print(f"  - {doc[:60]}...")
```

## Best Practices

1. **Choose the right model type**: Use Sentence Transformer for retrieval (fast), Cross Encoder for reranking (accurate)
2. **Normalize embeddings** for cosine similarity when using dense vectors
3. **Use asymmetric models** (`multi-qa-*`) for query-document search tasks
4. **Batch processing** with `batch_size` parameter for large datasets
5. **GPU acceleration** by moving model to CUDA: `model = SentenceTransformer(..., device="cuda")`
6. **Cache embeddings** for static corpora to avoid re-encoding
7. **Start with pretrained models** before fine-tuning on custom data

## Troubleshooting

### Issue: Out of Memory Error

**Solution**: Reduce batch size and use gradient checkpointing:

```python
embeddings = model.encode(sentences, batch_size=16, show_progress_bar=True)
```

### Issue: Slow Encoding Speed

**Solution**: Use ONNX or OpenVINO for optimization (see [`references/09-model-optimization.md`](references/09-model-optimization.md))

### Issue: Poor Retrieval Quality

**Solution**: 
1. Use domain-specific pretrained models
2. Fine-tune on your data with appropriate loss function
3. Implement retrieve-and-rerank pipeline
4. Try Matryoshka embeddings for better dimension trade-offs

## Version Information

- **Version**: 5.4.1
- **Release Date**: 2025
- **Python Compatibility**: 3.10+
- **PyTorch Compatibility**: 1.11.0+
- **Transformers Compatibility**: 4.34.0+

## References

- **Official Documentation**: https://www.sbert.net/
- **GitHub Repository**: https://github.com/huggingface/sentence-transformers/tree/v5.4.1
- **Hugging Face Models**: https://huggingface.co/sentence-transformers
- **MTEB Leaderboard**: https://huggingface.co/spaces/mteb/leaderboard
- **Paper (Sentence-BERT)**: https://arxiv.org/abs/1908.10084
- **Paper (Multilingual)**: https://arxiv.org/abs/2004.09813

## See Also

- [`transformers-5-5-4`](../../transformers-5-5-4/SKILL.md) - Hugging Face Transformers library
- [`torch-2-6`]() - PyTorch deep learning framework
- [`faiss-1-9`]() - Facebook AI Similarity Search for vector databases
- [`chroma-1-0`]() - Chroma vector database for embeddings
