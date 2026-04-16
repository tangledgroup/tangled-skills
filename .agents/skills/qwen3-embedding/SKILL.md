---
name: qwen3-embedding
description: Complete toolkit for Qwen3 Embedding models (0.6B, 4B, 8B) and Qwen3 Reranker models providing state-of-the-art text embedding, semantic search, reranking, and multilingual retrieval with support for Sentence Transformers, raw Transformers, vLLM, and TEI inference engines. Use when generating text embeddings, building semantic search or RAG pipelines, performing cross-lingual retrieval, code retrieval, text classification/clustering, or reranking search results with Qwen3-Embedding or Qwen3-Reranker models.
license: MIT
author: Tangled Skills Team <skills@tangled.dev>
version: "1.0.0"
tags:
  - embedding
  - semantic-search
  - retrieval
  - multilingual
  - reranking
  - qwen3
  - sentence-transformers
  - vllm
  - tei
category: ai-ml
external_references:
  - https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
  - https://huggingface.co/Qwen/Qwen3-Embedding-4B
  - https://huggingface.co/Qwen/Qwen3-Embedding-8B
---

# Qwen3 Embedding Models

Complete toolkit for the **Qwen3 Embedding series** — state-of-the-art text embedding and reranking models built on the Qwen3 foundation. Supports three sizes (0.6B, 4B, 8B) with multilingual capability across 100+ languages, 32K context length, user-defined output dimensions, and instruction-aware prompting.

## When to Use

- **Semantic search / retrieval** — Build vector-based search over documents, knowledge bases, or code
- **RAG pipelines** — Embed documents and queries for retrieval-augmented generation systems
- **Cross-lingual retrieval** — Search across language boundaries (e.g., English query → Chinese documents)
- **Code retrieval** — Find relevant code snippets from natural language descriptions
- **Text classification / clustering** — Use embeddings as features for downstream ML tasks
- **Reranking** — Improve retrieval quality with Qwen3-Reranker cross-encoder models
- **Multilingual applications** — Any application needing embeddings in 100+ languages

## Model Overview

| Model | Type | Params | Layers | Context | Default Dim | MRL Range |
|-------|------|--------|--------|---------|-------------|-----------|
| Qwen3-Embedding-0.6B | Embedding | 0.6B | 28 | 32K | 1,024 | 32–1,024 |
| Qwen3-Embedding-4B | Embedding | 4B | 36 | 32K | 2,560 | 32–2,560 |
| Qwen3-Embedding-8B | Embedding | 8B | 36 | 32K | 4,096 | 32–4,096 |
| Qwen3-Reranker-0.6B | Reranker | 0.6B | 28 | 32K | — | — |
| Qwen3-Reranker-4B | Reranker | 4B | 36 | 32K | — | — |
| Qwen3-Reranker-8B | Reranker | 8B | 36 | 32K | — | — |

**Key capabilities:**
- **#1 on MTEB multilingual leaderboard** (8B model, score 70.58 as of June 2025)
- **100+ languages** including programming languages
- **MRL support** — flexible output dimensions for storage/compute optimization
- **Instruction-aware** — task-specific prompts improve retrieval by 1–5%
- **Apache 2.0 license**

## Quick Start — Sentence Transformers (Recommended)

```python
# pip install sentence-transformers>=2.7.0 transformers>=4.51.0 torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

queries = ["What is the capital of China?"]
documents = ["The capital of China is Beijing."]

query_emb = model.encode(queries, prompt_name="query")
doc_emb = model.encode(documents)
similarity = model.similarity(query_emb, doc_emb)
print(similarity)  # tensor([[0.7646]])
```

## Core Concepts

### Dual-Encoder vs Cross-Encoder Architecture

- **Embedding models** use a dual-encoder: encode query and document independently → fast nearest-neighbor search via dot product
- **Reranker models** use a cross-encoder: process query+document together → higher accuracy but slower, ideal for re-ranking top candidates

### Instruction-Aware Prompting

Both embedding and reranker models support task-specific instructions:

```python
# Format: "Instruct: {task_description}\nQuery:{query_text}"
task = "Find documents about machine learning"
text = f"Instruct: {task}\nQuery:What is deep learning?"
```

Best practices:
- Instructions improve performance by **1–5%** on most tasks
- Write instructions in **English** even for multilingual queries
- Tailor instructions to your specific domain and task

### Multi-Resolution Linear (MRL) Projection

All embedding models support projecting to custom dimensions:

```python
embeddings = model.encode(texts, dimension=256)  # From 1024 → 256 for 0.6B
```

Smaller dimensions save storage/compute with minimal accuracy loss.

### Recommended Configuration

For GPU inference, always use Flash Attention 2:

```python
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={"attn_implementation": "flash_attention_2", "device_map": "auto"},
    tokenizer_kwargs={"padding_side": "left"}
)
```

## Installation

```bash
# Sentence Transformers (recommended for most use cases)
pip install sentence-transformers>=2.7.0 transformers>=4.51.0 torch

# vLLM (production serving)
pip install vllm>=0.8.5

# Text Embeddings Inference (TEI via Docker)
# See reference 04 for Docker deployment commands
```

**Critical:** `transformers>=4.51.0` is required. Earlier versions raise `KeyError: 'qwen3'`.

## Model Selection Guide

| Use Case | Recommended Model | GPU Memory |
|----------|-------------------|------------|
| Edge / mobile / low latency | Qwen3-Embedding-0.6B | ~4 GB |
| Balanced accuracy/latency API | Qwen3-Embedding-4B | ~12 GB |
| Highest accuracy (MTEB #1) | Qwen3-Embedding-8B | ~24 GB |

## Usage Patterns

### Semantic Search Pipeline

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
docs = ["Doc 1...", "Doc 2...", "Doc 3..."]
embeddings = model.encode(docs)

query_emb = model.encode(["Your search query here"], prompt_name="query")
scores = cosine_similarity(query_emb, embeddings)[0]
top_idx = np.argsort(scores)[::-1][:5]
```

### Cross-Lingual Search

```python
model = SentenceTransformer("Qwen/Qwen3-Embedding-8B")
# English query → Chinese documents (works out of the box)
query_emb = model.encode(["What is quantum computing?"])
doc_emb = model.encode(["量子计算是什么？"])
similarity = model.similarity(query_emb, doc_emb)
```

### Code Retrieval

```python
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
# Natural language query → code snippet
code_emb = model.encode(code_snippets)
query_emb = model.encode(["function to sort a list"])
similarity = model.similarity(query_emb, code_emb)
```

### Two-Stage RAG (Dense + Reranking)

1. Use Qwen3-Embedding for initial retrieval of top-K candidates
2. Pass candidates through Qwen3-Reranker for cross-encoder re-ranking
3. Feed reranked results to LLM

## Advanced Topics

For detailed usage, see the reference files:

- **[Model Architecture & Training](references/01-model-architecture.md)** — Dual/cross-encoder architecture, MRL support, training pipeline, hardware requirements
- **[Sentence Transformers Usage](references/02-sentence-transformers-usage.md)** — Complete Sentence Transformers API, custom instructions, dimension control, semantic search pipelines
- **[Transformers Library Usage](references/03-transformers-usage.md)** — Low-level PyTorch usage, flash attention 2, custom pooling, memory profiling
- **[vLLM and TEI Usage](references/04-vllm-and-tei-usage.md)** — Production serving with vLLM, Docker deployment with TEI, REST API, multi-GPU setup
- **[Evaluation & Benchmarks](references/05-evaluation-benchmarks.md)** — MTEB scores, reranking benchmarks, language support, citation
- **[Complete Examples](references/06-complete-examples.md)** — Full RAG pipeline, multilingual search, code retrieval, clustering, data export

## References

- **Qwen3-Embedding-0.6B:** https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- **Qwen3-Embedding-4B:** https://huggingface.co/Qwen/Qwen3-Embedding-4B
- **Qwen3-Embedding-8B:** https://huggingface.co/Qwen/Qwen3-Embedding-8B
- **Technical Report (arXiv):** https://arxiv.org/abs/2506.05176
- **Qwen Blog:** https://qwenlm.github.io/blog/qwen3-embedding/
