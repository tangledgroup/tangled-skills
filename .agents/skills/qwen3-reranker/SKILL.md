---
name: qwen3-reranker
description: Comprehensive toolkit for Qwen3 Reranker models (0.6B, 4B, 8B) — state-of-the-art cross-encoder text reranking with 100+ language support, 32K context length, and user-defined instructions. Use when re-ranking search results, improving retrieval relevance in RAG pipelines, building semantic search systems, or deploying high-performance cross-encoder rerankers via Sentence Transformers, Hugging Face Transformers, or vLLM.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.0"
tags:
  - reranking
  - text-ranking
  - retrieval
  - cross-encoder
  - multilingual
  - rags
  - semantic-search
category: ai-ml
external_references:
  - https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
  - https://arxiv.org/abs/2506.05176
  - https://github.com/QwenLM/Qwen3-Embedding
  - https://huggingface.co/Qwen/Qwen3-Reranker-0.6B),
  - https://huggingface.co/Qwen/Qwen3-Reranker-4B),
  - https://qwenlm.github.io/blog/qwen3-embedding/
  - https://huggingface.co/Qwen/Qwen3-Reranker-4B
  - https://huggingface.co/Qwen/Qwen3-Reranker-8B
---
## Overview
Qwen3 Reranker is a family of state-of-the-art **cross-encoder** text reranking models from the Qwen team, built on the Qwen3 foundation model. The series includes three sizes — **0.6B**, **4B**, and **8B** — all supporting 100+ languages and up to 32K context length. These models excel at scoring query-document relevance pairs, making them ideal for second-stage reranking in retrieval-augmented generation (RAG) pipelines, semantic search systems, and information retrieval workflows.

All three models are licensed under **Apache 2.0** and can be loaded via Sentence Transformers (`CrossEncoder`), raw Hugging Face Transformers (`AutoModelForCausalLM`), or vLLM for high-throughput serving. The reranking architecture uses a cross-encoder approach: given a (query, document) pair, the model outputs a relevance score by comparing logits for "yes" and "no" tokens at the final position.

### Key Features
- **Cross-encoder architecture** — full attention over query+document pairs (not just dot-product similarity)
- **100+ languages** supported, including programming languages
- **32K sequence length** — handle long documents natively
- **Instruction-aware** — customize behavior per task/language via prompt instructions
- **Three sizes** for different latency/accuracy trade-offs

## When to Use
Load this skill when:
- You need to re-rank a set of candidate documents for a query (e.g., top-100 → top-5)
- Building or improving a RAG pipeline with cross-encoder reranking
- Implementing semantic search with high accuracy requirements
- Comparing different model sizes (0.6B vs 4B vs 8B) for your use case
- Deploying rerankers via Sentence Transformers, Hugging Face, or vLLM

## Core Concepts
### Architecture
The reranker is built on a causal language model backbone (Qwen3). It uses a **cross-encoder** approach: the query and document are concatenated into a single sequence with special tokens. The model outputs logits for "yes" and "no" tokens at the final position, which are log-softmaxed to produce a relevance score.

### Scoring
- Default output: raw logit difference (can be positive or negative)
- With `torch.nn.Sigmoid()`: probability-like scores in [0, 1]
- vLLM mode: softmax probability computed from allowed token logits

### Instructions
The model supports **user-defined instructions** that guide its behavior. The default instruction is:
> "Given a web search query, retrieve relevant passages that answer the query"

Custom instructions can be provided per task (e.g., classification, legal document matching). Using instructions typically improves performance by 1–5%.

### Input Format
The model expects a specific chat template:
```
<Instruct>: {instruction}
<Query>: {query}
<Document>: {doc}
```

Wrapped in system/user roles with special prefix/suffix tokens.

## Quick Start — Sentence Transformers (Recommended)
```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Reranker-4B")

query = "What is the capital of China?"
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other.",
]

# Get raw scores (logit differences)
scores = model.predict([(query, doc) for doc in documents])

# Get ranked results
rankings = model.rank(query, documents)
```

## Model Comparison
| Model | Parameters | Layers | MTEB-R | MLDR | Best For |
|-------|-----------|--------|--------|------|----------|
| Qwen3-Reranker-0.6B | 0.6B | 28 | 65.80 | 67.28 | Edge/low-latency, CPU-friendly |
| Qwen3-Reranker-4B | 4B | 36 | **69.76** | 69.97 | Best accuracy/speed balance |
| Qwen3-Reranker-8B | 8B | 36 | 69.02 | **70.19** | Maximum accuracy, multilingual |

## Advanced Topics
## Advanced Topics

- [Sentence Transformers](reference/01-sentence-transformers.md)
- [Transformers Api](reference/02-transformers-api.md)
- [Vllm Deployment](reference/03-vllm-deployment.md)

