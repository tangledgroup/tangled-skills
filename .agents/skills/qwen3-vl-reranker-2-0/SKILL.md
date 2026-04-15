---
name: qwen3-vl-reranker-2-0
description: A comprehensive toolkit for using Qwen3-VL-Reranker models (2B and 8B variants) to perform high-precision multimodal reranking and relevance scoring. Use when building retrieval-augmented generation (RAG) pipelines, implementing two-stage retrieval systems, refining search results across text-image-video modalities, or needing precise cross-modal relevance scoring beyond initial embedding-based recall.
license: MIT
author: Tangled Skills <skills@tangled.dev>
version: "2.0.0"
tags:
  - qwen
  - reranker
  - multimodal
  - transformers
  - vision-language
  - retrieval
  - rag
  - cross-attention
category: machine-learning
external_references:
  - https://huggingface.co/Qwen/Qwen3-VL-Reranker-2B
  - https://huggingface.co/Qwen/Qwen3-VL-Reranker-8B
  - https://github.com/QwenLM/Qwen3-VL-Embedding
---

# Qwen3-VL-Reranker 2.0

A comprehensive toolkit for using Qwen3-VL-Reranker models (2B and 8B variants) to perform high-precision multimodal reranking and relevance scoring in retrieval pipelines.

## Overview

Qwen3-VL-Reranker is a state-of-the-art multimodal reranking model series built on the Qwen3-VL foundation model. Unlike embedding models that generate independent vectors, the reranker uses a **single-tower architecture with cross-attention** to compute precise relevance scores between query-document pairs, where both can contain arbitrary combinations of text, images, screenshots, and videos.

The reranker is designed to work in tandem with Qwen3-VL-Embedding models in a two-stage retrieval pipeline:
1. **Stage 1 (Recall)**: Use embedding model for fast initial retrieval across large corpora
2. **Stage 2 (Rerank)**: Use reranker model to precisely score and reorder top-k candidates

This approach significantly boosts retrieval accuracy while maintaining efficiency.

## When to Use

Use this skill when:

- Building two-stage retrieval systems (recall + rerank)
- Implementing RAG pipelines that need precise result ranking
- Refining initial search results from embedding-based retrieval
- Scoring relevance between multimodal query-document pairs
- Working with mixed-modal inputs (text+image, text+video, etc.)
- Needing instruction-tuned reranking for specific tasks
- Building multimodal search engines requiring high precision

## Core Concepts

### Model Variants

| Model | Parameters | Layers | Context Length | Best For |
|-------|-----------|--------|----------------|----------|
| **Qwen3-VL-Reranker-2B** | 2B | 28 | 32K | Faster reranking, lower memory |
| **Qwen3-VL-Reranker-8B** | 8B | 36 | 32K | Higher accuracy, complex tasks |

### Key Features

- **Multimodal Cross-Attention**: Processes query and document jointly with cross-attention mechanisms
- **Instruction-Aware**: Customizable task-specific instructions improve performance by 1-5%
- **30+ Languages**: Native multilingual support for global applications
- **Flexible Input**: Accepts text, images, screenshots, videos, and arbitrary combinations
- **Precise Scoring**: Outputs detailed relevance scores (not just binary classification)

### Architecture: Dual-Tower vs Single-Tower

Understanding the difference between embedding and reranking architectures is crucial:

**Qwen3-VL-Embedding (Dual-Tower)**:
- Receives single input (query OR document)
- Extracts hidden state at `[EOS]` token from last layer
- Produces independent semantic vectors
- **Use case**: Efficient large-scale retrieval via vector similarity

**Qwen3-VL-Reranker (Single-Tower)**:
- Receives query-document pair as concatenated input
- Uses cross-attention to model interactions between query and document
- Outputs precise relevance score through classification head
- **Use case**: Precise re-ranking of top-k candidates from initial retrieval

### Two-Stage Retrieval Pipeline

The recommended architecture for production systems:

```
┌─────────────────────────────────────────────────────────────┐
│                    Query (text + image)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │   Stage 1: Embedding      │
        │   - Fast vector search    │
        │   - Retrieve top-100      │
        │   - Cosine similarity     │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │   Stage 2: Reranker       │
        │   - Precise scoring       │
        │   - Cross-attention       │
        │   - Return top-10         │
        └──────────────┬───────────┘
                       │
                       ▼
                Final Ranked Results
```

## Installation / Setup

### Prerequisites

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate
```

### Install Dependencies

```bash
# Using uv (recommended)
uv pip install "transformers>=4.57.0" "qwen-vl-utils>=0.0.14" "torch==2.8.0"

# Or using pip
pip install "transformers>=4.57.0" "qwen-vl-utils>=0.0.14" "torch==2.8.0"
```

### Download Model

**From Hugging Face:**

```bash
uv pip install huggingface-hub

huggingface-cli download Qwen/Qwen3-VL-Reranker-2B --local-dir ./models/Qwen3-VL-Reranker-2B
# Or for 8B variant:
huggingface-cli download Qwen/Qwen3-VL-Reranker-8B --local-dir ./models/Qwen3-VL-Reranker-8B
```

**From ModelScope:**

```bash
uv pip install modelscope

modelscope download --model qwen/Qwen3-VL-Reranker-2B --local_dir ./models/Qwen3-VL-Reranker-2B
```

## Usage Examples

### Basic Text Reranking

Score relevance between a text query and multiple documents:

```python
from scripts.qwen3_vl_reranker import Qwen3VLReranker
import torch

# Initialize model
model = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"  # Recommended for performance
)

# Define query and documents
inputs = {
    "instruction": "Retrieve images or text relevant to the user's query.",
    "query": {"text": "A woman playing with her dog on a beach at sunset."},
    "documents": [
        {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust."},
        {"text": "City skyline view from a high-rise building at night with illuminated skyscrapers."},
        {"text": "Professional dog trainer teaching obedience commands in an indoor facility."}
    ]
}

# Get relevance scores
scores = model.process(inputs)
print(scores)
# [0.8613124489784241, 0.1234567890123456, 0.3456789012345678]

# Rank documents by score
document_scores = list(zip(inputs["documents"], scores))
ranked_results = sorted(document_scores, key=lambda x: x[1], reverse=True)

for i, (doc, score) in enumerate(ranked_results, 1):
    print(f"{i}. Score: {score:.4f} - {doc['text'][:50]}...")
```

### Image Reranking

Rerank image results based on a text query:

```python
# Text query with image documents
inputs = {
    "instruction": "Find images matching the description.",
    "query": {"text": "A sunset beach scene with people and dogs."},
    "documents": [
        {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"},
        {"image": "path/to/cityscape.jpg"},
        {"image": "path/to/indoor_dog_training.jpg"}
    ]
}

scores = model.process(inputs)
print(f"Image relevance scores: {scores}")
```

### Multimodal Reranking

Handle mixed-modal queries and documents:

```python
# Query with both text and image
inputs = {
    "instruction": "Find visually similar products.",
    "query": {
        "text": "Red running shoes for marathon training",
        "image": "path/to/reference_shoe.jpg"
    },
    "documents": [
        {"text": "Nike Air Zoom Pegasus 40 - Lightweight running shoes", "image": "nike_shoes.jpg"},
        {"text": "Adidas Ultraboost 23 - Premium running footwear", "image": "adidas_shoes.jpg"},
        {"image": "generic_sneakers.jpg"}  # Image-only document
    ]
}

scores = model.process(inputs)
```

### Video Reranking

Process video inputs with frame sampling:

```python
# Initialize with video settings
model = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    fps=1.0,           # Sample 1 frame per second
    max_frames=64      # Maximum 64 frames per video
)

# Video reranking
inputs = {
    "instruction": "Find videos matching the query.",
    "query": {"text": "Cooking tutorial for pasta preparation"},
    "documents": [
        {"video": "path/to/pasta_tutorial.mp4"},
        {"video": "path/to/salad_recipe.mp4"},
        {
            "video": ["frame1.jpg", "frame2.jpg", "frame3.jpg"],  # Frame sequence
            "text": "Step-by-step guide to making fresh pasta"
        }
    ]
}

scores = model.process(inputs)
```

### Two-Stage Retrieval Pipeline

Complete example combining embedding recall with reranking:

```python
from scripts.qwen3_vl_embedding import Qwen3VLEmbedder
from scripts.qwen3_vl_reranker import Qwen3VLReranker
import torch
import numpy as np

# Initialize both models
embedder = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)

reranker = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)

# Large document corpus (simulated)
all_documents = [
    {"text": f"Document {i} content about various topics..."}
    for i in range(1000)
]

# Add some relevant documents
all_documents[42] = {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset."}
all_documents[128] = {"text": "Beach photography captures dogs playing with their owners during golden hour."}
all_documents[567] = {"text": "Urban architecture and city skylines at night."}

# Query
query = {"text": "A woman playing with her dog on a beach at sunset."}
instruction = "Retrieve images or text relevant to the user's query."

# Stage 1: Embedding-based recall (fast, approximate)
query_with_instruction = {"text": query["text"], "instruction": instruction}
doc_with_instructions = [{**doc, "instruction": instruction} for doc in all_documents]

# Generate embeddings
query_embedding = embedder.process([query_with_instruction])[0]
doc_embeddings = embedder.process(doc_with_instructions)

# Compute cosine similarity (embeddings are already normalized)
similarities = query_embedding @ doc_embeddings.T

# Get top-50 candidates for reranking
top_k_indices = np.argsort(similarities)[-50:][::-1]
top_k_documents = [all_documents[i] for i in top_k_indices]

print(f"Stage 1 - Top 5 by embedding similarity:")
for i, idx in enumerate(top_k_indices[:5], 1):
    print(f"{i}. Score: {similarities[idx]:.4f} - Doc {idx}")

# Stage 2: Reranking (precise, computationally intensive)
rerank_inputs = {
    "instruction": instruction,
    "query": query,
    "documents": top_k_documents
}

rerank_scores = reranker.process(rerank_inputs)

# Combine and sort by reranker scores
ranked_results = list(zip(top_k_documents, rerank_scores))
ranked_results.sort(key=lambda x: x[1], reverse=True)

print(f"\nStage 2 - Top 5 after reranking:")
for i, (doc, score) in enumerate(ranked_results[:5], 1):
    print(f"{i}. Score: {score:.4f} - {doc['text'][:60]}...")
```

### Instruction-Tuned Reranking

Customize reranking behavior with task-specific instructions:

```python
# Different instructions for different tasks
instructions = {
    "general_retrieval": "Retrieve images or text relevant to the user's query.",
    "product_search": "Find products that match the customer's description and requirements.",
    "visual_qa": "Find visual evidence that answers the question.",
    "document_search": "Retrieve documents containing information about the query topic.",
    "multilingual": "Represent the query and documents for cross-lingual retrieval."  # Use English
}

# Example: Product search
inputs = {
    "instruction": instructions["product_search"],
    "query": {"text": "Lightweight running shoes for marathon training under $150"},
    "documents": [
        {"text": "Nike Air Zoom Pegasus 40 - 290g, $130", "image": "nike_pegasus.jpg"},
        {"text": "Adidas Ultraboost 23 - Premium comfort, $180", "image": "adidas_ub23.jpg"},
        {"text": "Brooks Ghost 16 - Neutral cushioning, $140", "image": "brooks_ghost.jpg"}
    ]
}

scores = model.process(inputs)
```

**Performance improvement with instructions**: 1-5% on most tasks. We recommend:
- Creating tailored instructions for your specific use case
- Writing instructions in English (even for multilingual tasks)
- Testing different instruction phrasings for optimal results

## Advanced Topics

See the following reference files for deeper coverage:

- **[Model Architecture](refs/01-model-architecture.md)**: Single-tower cross-attention design, technical specifications, comparison with dual-tower embedding models
- **[Usage Patterns](refs/02-usage-patterns.md)**: vLLM integration, SGLang deployment, batch processing, production patterns
- **[Performance Benchmarks](refs/03-performance-benchmarks.md)**: MMEB-V2 and MMTEB reranking results, comparison with jina-reranker and other baselines
- **[RAG Integration](refs/04-rag-integration.md)**: End-to-end RAG pipelines, hybrid search strategies, caching optimization

## Model Performance

Qwen3-VL-Reranker consistently outperforms both the base embedding model and baseline rerankers across multimodal benchmarks:

### MMEB-V2 Retrieval Benchmark

| Model | Size | Avg | Image | Video | VisDoc |
|-------|------|-----|-------|-------|--------|
| Qwen3-VL-Embedding-2B | 2B | 73.4 | 74.8 | 53.6 | 79.2 |
| jina-reranker-m0      | 2B | -   | 68.2 | -    | 85.2 |
| **Qwen3-VL-Reranker-2B** | 2B | **75.1** | 73.8 | 52.1 | **83.4** |
| **Qwen3-VL-Reranker-8B** | 8B | **79.2** | **80.7** | **55.8** | **86.3** |

### MMTEB Retrieval Benchmark

| Model | Size | MMTEB(Retrieval) |
|-------|------|------------------|
| Qwen3-VL-Embedding-2B | 2B | 68.1 |
| **Qwen3-VL-Reranker-2B** | 2B | **70.0** |
| **Qwen3-VL-Reranker-8B** | 8B | **74.9** |

### Visual Document Retrieval

| Model | Size | JinaVDR | ViDoRe(v3) |
|-------|------|---------|------------|
| Qwen3-VL-Embedding-2B | 2B | 71.0 | 52.9 |
| jina-reranker-m0      | 2B | 82.2 | 57.8 |
| **Qwen3-VL-Reranker-2B** | 2B | **80.9** | **60.8** |
| **Qwen3-VL-Reranker-8B** | 8B | **83.6** | **66.7** |

## Best Practices

1. **Always use two-stage retrieval**: Embedding for recall, reranker for precision
2. **Enable Flash Attention 2**: Use `attn_implementation="flash_attention_2"` for 2-3x faster inference
3. **Add task-specific instructions**: Improve performance by 1-5% with tailored instructions
4. **Choose top-k wisely**: Rerank 50-200 candidates from embedding recall for optimal trade-off
5. **Batch reranking requests**: Process multiple queries together when possible
6. **Cache embedding results**: Reuse embeddings for static document corpora
7. **Use 8B model for critical tasks**: Higher accuracy for production systems where precision matters
8. **Monitor latency**: Reranking is more expensive than embedding; balance quality vs speed

## Troubleshooting

### Issue: Out of Memory Error

**Solution**: Use smaller model or reduce image resolution:

```python
model = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    max_pixels=409600,
    torch_dtype=torch.float16
)
```

### Issue: Slow Reranking Performance

**Solution**: Enable Flash Attention 2:

```python
model = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16
)
```

### Issue: Poor Reranking Quality

**Solution**: Use task-specific instructions:

```python
inputs = {
    "instruction": "Retrieve images or text relevant to the user's query.",
    "query": {...},
    "documents": [...]
}
```

### Issue: Video Processing Too Slow

**Solution**: Adjust frame sampling:

```python
model = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    fps=0.5,
    max_frames=32
)
```

## References

- **Official GitHub**: https://github.com/QwenLM/Qwen3-VL-Embedding
- **Hugging Face - 2B**: https://huggingface.co/Qwen/Qwen3-VL-Reranker-2B
- **Hugging Face - 8B**: https://huggingface.co/Qwen/Qwen3-VL-Reranker-8B
- **Technical Report**: https://arxiv.org/abs/2601.04720
- **Qwen Blog**: https://qwen.ai/blog?id=qwen3-vl-embedding
- **MMEB-V2 Benchmark**: https://huggingface.co/spaces/TIGER-Lab/MMEB-Leaderboard
- **MMTEB Benchmark**: https://huggingface.co/spaces/mteb/leaderboard
- **JinaVDR Dataset**: https://huggingface.co/collections/jinaai/jinavdr-visual-document-retrieval
- **ViDoRe v3**: https://huggingface.co/blog/QuentinJG/introducing-vidore-v3

## Citation

If you use Qwen3-VL-Reranker in your research:

```bibtex
@article{qwen3vlembedding,
  title={Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking},
  author={Li, Mingxin and Zhang, Yanzhao and Long, Dingkun and Chen, Keqin and Song, Sibo and Bai, Shuai and Yang, Zhibo and Xie, Pengjun and Yang, An and Liu, Dayiheng and Zhou, Jingren and Lin, Junyang},
  journal={arXiv preprint arXiv:2601.04720},
  year={2026}
}
```
