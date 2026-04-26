---
name: qwen3-vl-reranker
description: Complete toolkit for Qwen3-VL-Reranker (2B and 8B) multimodal reranking models that score relevance of text, image, video, and mixed-modality document pairs against queries. Use when building multimodal retrieval pipelines, re-ranking search results with cross-modal understanding, implementing two-stage retrieval systems with embedding+reranking, or performing visual document retrieval tasks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.0"
tags:
  - reranker
  - multimodal
  - retrieval
  - qwen
  - cross-encoder
  - sentence-transformers
  - transformers
  - vllm
category: ai/llm
external_references:
  - https://huggingface.co/Qwen/Qwen3-VL-Reranker-2B
  - https://arxiv.org/abs/2601.04720
  - https://github.com/QwenLM/Qwen3-VL-Embedding
  - https://huggingface.co/spaces/TIGER-Lab/MMEB-Leaderboard
  - https://huggingface.co/spaces/mteb/leaderboard
  - https://qwenlm.github.io/blog/qwen3-embedding/
  - https://huggingface.co/Qwen/Qwen3-VL-Reranker-8B
---

# Qwen3-VL-Reranker

## Overview

Qwen3-VL-Reranker is a multimodal cross-encoder reranking model series from the Qwen family, built on the Qwen3-VL foundation model. It comes in two sizes — **2B** (28 layers) and **8B** (36 layers) — both with 32K context length. The reranker takes a `(query, document)` pair as input where both sides may contain arbitrary single or mixed modalities (text, images, screenshots, video), then outputs a precise relevance score.

It is designed to complement Qwen3-VL-Embedding in a two-stage retrieval pipeline: the embedding model performs efficient initial recall via dense vector search, and the reranker refines results with fine-grained cross-attention scoring in a subsequent re-ranking stage. This combination significantly boosts retrieval accuracy across multimodal tasks.

Both models support over 30 languages and are instruction-aware, allowing task-specific prompt customization that typically yields 1–5% improvement over default instructions.

## When to Use

- Re-ranking search results from an embedding-based recall stage in multimodal RAG pipelines
- Scoring relevance between text queries and image/video/text documents
- Visual document retrieval (scanned PDFs, screenshots, forms)
- Image-text or video-text matching tasks
- Cross-modal understanding where query and document may differ in modality
- Building two-stage retrieval systems (recall → rerank) for improved precision

## Core Concepts

**Cross-Encoder Architecture**: Unlike the dual-tower embedding model that encodes query and document independently, the reranker uses a single-tower cross-encoder with cross-attention mechanisms. This enables deep inter-modal interaction and information fusion between query and document, producing more accurate relevance estimates at the cost of higher compute per pair.

**Pointwise Reranking**: The model processes one `(query, document)` pair at a time and outputs a scalar relevance score by predicting the generation probability of special tokens (`yes` / `no`). This is pointwise rather than pairwise or listwise reranking.

**Mixed-Modality Inputs**: Both query and document can be text-only, image-only, video-only, or any combination thereof. A text query can be scored against a document containing both text and an image, for example.

**Instruction Awareness**: The model accepts a natural language instruction that describes the retrieval task. Customized instructions typically improve scores by 1–5%. In multilingual contexts, English instructions are recommended as most training instructions were in English.

## Advanced Topics

**Architecture and Model Details**: LoRA configs, dual-tower vs single-tower design, training paradigm → See [Architecture](reference/01-architecture.md)

**Usage Patterns**: Sentence Transformers API, raw Transformers usage, vLLM deployment, input format specification → See [Usage](reference/02-usage.md)

**Benchmarks and Performance**: MMEB-v2, MMTEB, JinaVDR, ViDoRe v3 results with comparison models → See [Benchmarks](reference/03-benchmarks.md)
