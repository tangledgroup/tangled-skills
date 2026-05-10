---
name: qwen3-embedding-1-0-0
description: Complete toolkit for Qwen3 Embedding models (0.6B, 4B, 8B) and Qwen3
  Reranker models providing state-of-the-art text embedding, semantic search, reranking,
  and multilingual retrieval with support for Sentence Transformers, raw Transformers,
  vLLM, and TEI inference engines. Use when generating text embeddings, building semantic
  search or RAG pipelines, performing cross-lingual retrieval, code retrieval, text
  classification/clustering, or reranking search results with Qwen3-Embedding or Qwen3-Reranker
  models.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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
- https://arxiv.org/abs/2506.05176
- https://qwenlm.github.io/blog/qwen3-embedding/
- https://huggingface.co/Qwen/Qwen3-Embedding-4B
- https://huggingface.co/Qwen/Qwen3-Embedding-8B
---

# Qwen3 Embedding

## Overview

Qwen3 Embedding is a family of text embedding and reranking models built on the Qwen3 foundation models, released by Alibaba's Qwen team under the Apache 2.0 license. The series provides state-of-the-art performance across text retrieval, code retrieval, text classification, text clustering, and bitext mining. The 8B embedding model ranks No.1 on the MTEB multilingual leaderboard (score 70.58 as of June 2025).

The series includes three sizes for both embedding and reranking:

- **Qwen3-Embedding-0.6B** — 28 layers, 1024-dim embeddings, 32K context
- **Qwen3-Embedding-4B** — 36 layers, 2560-dim embeddings, 32K context
- **Qwen3-Embedding-8B** — 36 layers, 4096-dim embeddings, 32K context
- **Qwen3-Reranker-0.6B/4B/8B** — cross-encoder reranking models, 32K context

Key features include Matryoshka Representation Learning (MRL) for flexible output dimensions, instruction-aware prompting for task-specific optimization, and support for 100+ languages including programming languages.

## When to Use

- Building semantic search or RAG pipelines requiring high-quality text embeddings
- Performing cross-lingual or multilingual retrieval across 100+ languages
- Code retrieval tasks (retrieving relevant code from natural language queries)
- Text classification, clustering, or bitext mining
- Two-stage retrieval: dense embedding for candidate selection, then reranker for precision
- Needing flexible embedding dimensions via Matryoshka Representation Learning
- Deploying embedding models via Sentence Transformers, raw Transformers, vLLM, or TEI

## Core Concepts

**Dual-Encoder Architecture (Embedding)**: The embedding model processes a single text input and extracts the semantic representation from the hidden state of the final `[EOS]` token. This enables efficient approximate nearest neighbor search for retrieval.

**Cross-Encoder Architecture (Reranking)**: The reranker takes query-document pairs as input and outputs a relevance score using a cross-encoder structure. It is used after initial dense retrieval to re-rank top candidates with higher precision.

**Instruction-Aware Embedding**: Both embedding and reranking models support user-defined instructions. Queries should be prefixed with `Instruct: {task_description}\nQuery:{query}` while documents are embedded as-is. Using instructions typically yields 1-5% improvement over not using them. Write instructions in English even for multilingual contexts, as training instructions were primarily in English.

**Matryoshka Representation Learning (MRL)**: Embedding models support user-defined output dimensions by truncating the embedding vector. For example, Qwen3-Embedding-8B produces 4096-dim embeddings by default but can output any dimension from 32 to 4096. Smaller dimensions trade accuracy for storage and compute efficiency.

**Last-Token Pooling**: Embeddings are extracted using last-token pooling — the hidden state corresponding to the final token in each sequence (determined by attention mask). This differs from mean-pooling used by some other embedding models.

## Advanced Topics

**Model Comparison & Benchmarks**: MTEB, C-MTEB, and reranking benchmark results → [Model Comparison](reference/01-model-comparison.md)

**Usage Examples**: Code for Sentence Transformers, Transformers, vLLM, TEI, and reranker usage → [Usage Examples](reference/02-usage-examples.md)

**Architecture & Training**: Model architecture details, three-stage training pipeline, LoRA fine-tuning → [Architecture & Training](reference/03-architecture-and-training.md)
