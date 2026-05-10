---
name: sentence-transformers-5-4-1
description: Comprehensive toolkit for computing text embeddings, semantic search, and reranking using Sentence Transformers v5.4.1. Provides dense, sparse, and cross-encoder models for semantic textual similarity, paraphrase mining, clustering, retrieve-and-rerank pipelines, and multimodal applications with support for 100+ languages and extensive training capabilities.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - embeddings
  - semantic-search
  - reranking
  - nlp
  - sentence-embeddings
  - cross-encoder
  - sparse-encoder
  - transformers
category: machine-learning
external_references:
  - https://github.com/huggingface/sentence-transformers/tree/v5.4.1
  - https://arxiv.org/abs/1908.10084
  - https://arxiv.org/abs/2004.09813
  - https://huggingface.co/spaces/mteb/leaderboard
  - https://www.sbert.net/
  - https://huggingface.co/sentence-transformers
---

# Sentence Transformers 5.4.1

## Overview

Sentence Transformers is the go-to Python framework for computing text embeddings, performing semantic search, and reranking results using transformer-based models. Built on top of Hugging Face Transformers and PyTorch, it provides three distinct model types:

- **SentenceTransformer** (dense embeddings) — maps text to fixed-dimensional dense vectors for fast similarity search
- **CrossEncoder** (rerankers) — processes sentence pairs jointly to produce accuracy-optimized relevance scores
- **SparseEncoder** (sparse embeddings) — generates vocabulary-sized sparse vectors compatible with BM25-style indexing

The library supports training custom models from scratch or fine-tuning any of the 15,000+ pre-trained models available on Hugging Face Hub. It covers dense retrieval, sparse retrieval, cross-encoder reranking, multimodal embeddings (text + image via CLIP), quantization, ONNX/OpenVINO export, and comprehensive evaluation tooling.

Requires Python 3.10+, PyTorch 1.11.0+, and Transformers 4.41.0+.

## When to Use

- Computing sentence/document embeddings for semantic search or similarity comparison
- Building retrieve-and-rerank pipelines (dense retrieval + cross-encoder reranking)
- Training or fine-tuning embedding models on custom data
- Performing paraphrase mining, clustering, or duplicate detection
- Working with sparse embeddings (SPLADE-style) for hybrid retrieval
- Multimodal embedding tasks (text + image via CLIP backbones)
- Quantizing embeddings for memory-efficient storage and search
- Evaluating embedding quality against benchmarks (MTEB, STS, NLI)

## Core Concepts

### Three Model Types

**SentenceTransformer** produces independent embeddings per text. Each sentence is encoded separately, enabling fast batch encoding and FAISS-based retrieval. This is the workhorse for semantic search and clustering.

**CrossEncoder** takes a (query, passage) pair and outputs a single score. It cannot pre-compute embeddings — both texts must be processed together. Use it for reranking top-k results from a dense retriever.

**SparseEncoder** produces vocabulary-sized sparse vectors (typically 30K+ dimensions, >99% zeros). These complement dense embeddings in hybrid retrieval and are compatible with inverted-index search engines.

### Embedding Pipeline Architecture

A SentenceTransformer is a sequential pipeline of modules:

1. **Transformer** — the backbone (BERT, RoBERTa, XLM-R, etc.) producing token-level embeddings
2. **Pooling** — reduces variable-length token sequences to fixed-size sentence vectors
3. Optional post-processing layers: **Dense**, **Normalize**, **Dropout**, **LayerNorm**

The default pooling mode is `mean` (average pooling over token embeddings). Other modes include `cls`, `max`, `weightedmean`, `mean_sqrt_len_tokens`, and `lasttoken`.

### Similarity Functions

Four similarity metrics are supported: `cosine` (default), `dot`, `euclidean`, and `manhattan`. Cosine similarity is the standard for normalized embeddings. Dot product is equivalent to cosine when embeddings are L2-normalized.

### Quick Start

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = model.encode(["Hello world", "Goodbye world"])
similarities = model.similarity(embeddings, embeddings)
```

## Advanced Topics

**Model Types and Architecture**: Deep dive into SentenceTransformer, CrossEncoder, and SparseEncoder internals → [Model Types](reference/01-model-types.md)

**Training Guide**: Loss functions, training arguments, evaluators, datasets, and fine-tuning workflows → [Training Guide](reference/02-training-guide.md)

**Applications and Utilities**: Semantic search, paraphrase mining, clustering, quantization, and retrieval helpers → [Applications](reference/03-applications.md)

**Modules Reference**: Pooling strategies, Router for asymmetric models, Normalize, Dense, WeightedLayerPooling, and multimodal support → [Modules Reference](reference/04-modules-reference.md)
