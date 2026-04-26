---
name: qwen3-vl-embedding-0-1-0
description: Complete toolkit for Qwen3-VL-Embedding 0.1.0 multimodal embedding models (2B and 8B) supporting text, images, screenshots, videos, and mixed-modal inputs. Use when generating semantic embeddings for retrieval, clustering, similarity search, RAG pipelines, or cross-modal understanding with Matryoshka dimension flexibility and 30+ language support.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - embedding
  - multimodal
  - vision-language
  - retrieval
  - semantic-search
  - vector-embeddings
  - qwen
  - transformers
  - vllm
category: ai-models
external_references:
  - https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B
  - https://arxiv.org/abs/2601.04720
  - https://github.com/QwenLM/Qwen3-VL-Embedding
  - https://qwen.ai/blog?id=qwen3-vl-embedding
  - https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
---

# Qwen3-VL-Embedding 0.1.0

## Overview

Qwen3-VL-Embedding is a state-of-the-art multimodal embedding model series built on the Qwen3-VL foundation model. It maps diverse inputs — text, images, screenshots, videos, and arbitrary mixed-modal combinations — into semantically rich high-dimensional vectors in a unified representation space. Released in 2B and 8B parameter sizes, it supports Matryoshka Representation Learning (MRL) for flexible output dimensions from 64 to the model's maximum, quantization for efficient deployment, instruction-aware embedding for task-specific optimization, and 30+ languages for global applications.

The companion Qwen3-VL-Reranker series provides precise relevance scoring in a two-stage retrieval pipeline: Embedding handles initial recall, Reranker refines results.

## When to Use

- Generating semantic embeddings from text, images, videos, or mixed inputs
- Building multimodal search and retrieval systems (image-text retrieval, video-text matching)
- Implementing RAG pipelines with visual document understanding
- Performing multimodal content classification, clustering, or similarity search
- Cross-lingual and cross-modal retrieval tasks across 30+ languages
- Visual question answering (VQA) via embedding-based answer retrieval

## Core Concepts

**Dual-Tower Architecture**: The embedding model independently encodes each input into a fixed-dimensional vector by extracting the hidden state of the `[EOS]` token from the last layer. This enables efficient large-scale retrieval through independent encoding.

**Unified Representation Space**: All modalities (text, image, video) share a single embedding space, allowing direct cosine similarity computation between any pair of inputs regardless of modality.

**Matryoshka Representation Learning (MRL)**: The model supports user-defined output dimensions from 64 up to the model's maximum (2048 for 2B, 4096 for 8B). Simply truncate the full embedding to any desired dimension while maintaining strong performance.

**Instruction Awareness**: Both models accept task-specific instructions that typically improve downstream performance by 1-5%. Write instructions in English for best results even in multilingual contexts.

## Model Specifications

- **Qwen3-VL-Embedding-2B**: 28 layers, 32K context, 2048 max embedding dimension
- **Qwen3-VL-Embedding-8B**: 36 layers, 32K context, 4096 max embedding dimension
- Both support quantization, MRL, and instruction-aware embedding

## Usage Examples

### Quick Start with Transformers

```python
import torch
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder

model = Qwen3VLEmbedder(
    model_name_or_path="./models/Qwen3-VL-Embedding-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)

# Text embedding
text_emb = model.process([{"text": "A woman playing with her dog on a beach at sunset."}])

# Image embedding
image_emb = model.process([{"image": "path/to/image.jpg"}])

# Mixed modalities (text + image)
mixed_emb = model.process([{
    "text": "A description of the scene",
    "image": "path/to/image.jpg"
}])

# With instruction for task-specific optimization
instructed_emb = model.process([{
    "text": "What is in this image?",
    "instruction": "Find images matching this description."
}])

# Compute similarity
similarity = text_emb @ image_emb.T
```

### Model Initialization Parameters

```python
Qwen3VLEmbedder(
    model_name_or_path="./models/Qwen3-VL-Embedding-2B",
    max_length=8192,           # Default context length
    min_pixels=4096,           # Minimum pixels for input images
    max_pixels=1843200,        # Maximum pixels per image (~1280x1440)
    total_pixels=7864320,      # Maximum total pixels for video (multiplied by 2 in model)
    fps=1.0,                   # Default frame sampling rate for video
    max_frames=64,             # Maximum frames for video input
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)
```

### Input Format

**Embedding Model**: A list of dictionaries, each containing:

- `text`: String or list of strings
- `image`: File path, URL, PIL.Image instance, or list of any combination
- `video`: File path, URL, sequence of frames, or list of any combination
- `instruction`: Task-specific instruction (optional)
- `fps` / `max_frames`: Video sampling settings (optional)

## Advanced Topics

**Architecture and Training**: Model design, dual-tower architecture, multi-stage training paradigm → [Architecture](reference/01-architecture.md)

**Input Modalities and Format**: Detailed specification for text, image, video, and mixed-modal inputs with examples → [Input Modalities](reference/02-input-modalities.md)

**Usage Patterns and Examples**: Classification, QA, retrieval, RAG pipelines across text, image, and video tasks → [Usage Patterns](reference/03-usage-patterns.md)

**Benchmark Performance**: MMEB-V2 and MMTEB evaluation results with comparative analysis → [Benchmarks](reference/04-benchmarks.md)

**Reranking Integration**: Two-stage retrieval with Qwen3-VL-Reranker for precision refinement → [Reranking](reference/05-reranking.md)
