---
name: qwen3-vl-embedding
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
  - https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
---

# Qwen3-VL-Embedding 0.1.0

## Overview

The **Qwen3-VL-Embedding** series provides state-of-the-art multimodal embedding models built on the Qwen3-VL foundation model. It generates high-dimensional semantic vectors for **text, images, screenshots, videos**, and **mixed-modal inputs** in a unified representation space. Available in 2B and 8B parameter sizes, both support Matryoshka Representation Learning (MRL) for flexible output dimensions (64–2048 for 2B, 64–4096 for 8B), instruction-aware customization, quantization (INT8/INT4), and over 30 languages.

## When to Use

Use this skill when:
- Building **multimodal retrieval systems** that search across text, images, videos, and documents simultaneously
- Implementing **visual search engines** where users query with text descriptions to find relevant images/videos
- Creating **RAG pipelines** that ingest multimodal documents (screenshots, diagrams, infographics) alongside text
- Performing **multimodal clustering** of mixed-content datasets (e.g., product catalogs with images and descriptions)
- Needing **cross-modal similarity** between text queries and visual content (images, videos, screenshots)
- Building **video search** or video indexing systems with frame-level understanding
- Requiring **task-specific embeddings** via customizable instructions for domain adaptation
- Deploying embedding models with **memory-efficient dimensions** using Matryoshka Representation Learning

## Core Concepts

### Dual-Tower Architecture

The model uses a dual-tower design: each input (single or mixed modality) is independently encoded into a high-dimensional vector extracted from the `[EOS]` token's hidden state. This enables efficient large-scale retrieval via cosine similarity.

### Multimodal Input Support

| Modality | Input Types | Notes |
|----------|-------------|-------|
| **Text** | String or list of strings | Any language supported by Qwen3-VL (30+) |
| **Image** | Local path, URL, PIL.Image instance, or list | Supports screenshots and document images |
| **Video** | File path, URL, or frame sequence | Configurable FPS and max frames |

### Matryoshka Representation Learning (MRL)

Both models support variable output dimensions:
- **2B**: 64–2048 dimensions
- **8B**: 64–4096 dimensions

Truncate embeddings to smaller dimensions for storage/compute efficiency with minimal accuracy loss.

### Instruction-Aware Embeddings

Customize embedding behavior via instructions:
```python
{"text": "Product description", "instruction": "Find products matching customer queries."}
```

## Installation

See [Transformers API Reference](references/02-transformers-api.md) for complete installation details.

```bash
# Clone and setup
git clone https://github.com/QwenLM/Qwen3-VL-Embedding.git
cd Qwen3-VL-Embedding
bash scripts/setup_environment.sh
source .venv/bin/activate

# Download model (choose 2B or 8B)
huggingface-cli download Qwen/Qwen3-VL-Embedding-2B --local-dir ./models/Qwen3-VL-Embedding-2B
```

### Key Dependencies

- Python >= 3.11
- PyTorch == 2.8.*
- Transformers >= 4.57.3
- qwen-vl-utils >= 0.0.14
- accelerate, decord, opencv-python-headless (for video/image processing)

## Quick Start

### Text Embeddings (Transformers)

```python
import torch
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder

model = Qwen3VLEmbedder(
    model_name_or_path="./models/Qwen3-VL-Embedding-2B",
    torch_dtype=torch.bfloat16,
)

inputs = [
    {"text": "A woman playing with her dog on a beach at sunset.",
     "instruction": "Retrieve images or text relevant to the user's query."},
    {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"}
]

embeddings = model.process(inputs)
print(embeddings @ embeddings.T)  # Similarity matrix
```

### vLLM Batch Inference

```python
from vllm import LLM

llm = LLM(
    model="Qwen/Qwen3-VL-Embedding-2B",
    runner="pooling",
    dtype='bfloat16',
    trust_remote_code=True,
)

# Prepare inputs via chat template...
outputs = llm.embed(vllm_inputs)
embeddings = [o.outputs.embedding for o in outputs]
```

## Usage Patterns

### Multimodal Retrieval Pipeline

Combine embedding recall with reranking for high-accuracy retrieval:

1. **Embedding model** (Qwen3-VL-Embedding): fast initial recall from large corpus
2. **Reranker model** (Qwen3-VL-Reranker): precise relevance scoring on top-k candidates
3. **LLM** (Qwen3-VL): final generation using reranked documents

See [Use Cases & Patterns](references/05-use-cases-patterns.md) for complete examples including RAG, image search, video indexing, clustering, and cross-lingual search.

### Model Selection Guide

| Use Case | Recommended Model |
|----------|-------------------|
| Maximum accuracy | Qwen3-VL-Embedding-8B (MMEB-V2: 77.8) |
| Balanced speed/quality | Qwen3-VL-Embedding-2B (MMEB-V2: 73.2) |
| Edge deployment | Qwen3-VL-Embedding-2B + INT4 quantization |
| Text-heavy tasks | Consider Qwen3-Embedding-8B (text-only variant) |

## Model Specifications

| Feature | Qwen3-VL-Embedding-2B | Qwen3-VL-Embedding-8B |
|---------|----------------------|----------------------|
| Parameters | 2B | 8B |
| Layers | 28 | 36 |
| Context Length | 32K tokens | 32K tokens |
| Max Embedding Dimension | 2048 | 4096 |
| MRL Support | ✅ (64–2048) | ✅ (64–4096) |
| Quantization | ✅ INT8/INT4 | ✅ INT8/INT4 |
| Languages | 30+ | 30+ |

## Advanced Topics

- **Architecture details**: Dual-tower design, EOS token pooling, MRL training
- **Performance benchmarks**: SOTA on MMEB-V2 (77.8 overall), MMTEB results
- **LoRA fine-tuning**: rank=32, alpha=32, target modules specified
- **Pixel/frame constraints**: Image min/max pixels, video FPS and frame limits
- **Reproducibility**: Evaluation scripts for MMEB v2 benchmark

See reference files for deep dives.

## References

- **Model Cards**: [2B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) | [8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B)
- **GitHub**: https://github.com/QwenLM/Qwen3-VL-Embedding
- **Technical Report**: https://arxiv.org/abs/2601.04720
- **Blog Post**: https://qwen.ai/blog?id=qwen3-vl-embedding

### Reference Files

- [Model Architecture & Specifications](references/01-model-architecture.md) — Dual-tower design, MRL, LoRA config, pixel/frame constraints
- [Transformers API Reference](references/02-transformers-api.md) — Installation, Qwen3VLEmbedder class, input formats, examples
- [vLLM Inference API](references/03-vllm-inference.md) — vLLM setup, batch inference, serving patterns
- [Benchmarks & Performance](references/04-benchmarks-performance.md) — MMEB-V2, MMTEB results, model comparison
- [Use Cases & Patterns](references/05-use-cases-patterns.md) — RAG pipelines, image search, video indexing, clustering

## Citation

```bibtex
@article{qwen3vlembedding,
  title={Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking},
  author={Li, Mingxin and Zhang, Yanzhao and Long, Dingkun and Chen, Keqin and Song, Sibo and Bai, Shuai and Yang, Zhibo and Xie, Pengjun and Yang, An and Liu, Dayiheng and Zhou, Jingren and Lin, Junyang},
  journal={arXiv},
  year={2026}
}
```
