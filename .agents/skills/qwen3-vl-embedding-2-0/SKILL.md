---
name: qwen3-vl-embedding-2-0
description: A comprehensive toolkit for using Qwen3-VL-Embedding models (2B and 8B variants) to generate multimodal embeddings from text, images, screenshots, videos, and mixed-modal inputs. Use when building multimodal retrieval systems, implementing cross-modal search, performing visual question answering, clustering multimodal content, or creating RAG pipelines that require semantic similarity between different modalities.
license: MIT
author: Tangled Skills <skills@tangled.dev>
version: "2.0.0"
tags:
  - qwen
  - embedding
  - multimodal
  - transformers
  - vision-language
  - retrieval
  - mrl
category: machine-learning
external_references:
  - https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B
  - https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
  - https://github.com/QwenLM/Qwen3-VL-Embedding
---

# Qwen3-VL-Embedding 2.0

A comprehensive toolkit for using Qwen3-VL-Embedding models (2B and 8B variants) to generate high-quality multimodal embeddings from text, images, screenshots, videos, and mixed-modal inputs.

## Overview

Qwen3-VL-Embedding is a state-of-the-art multimodal embedding model series built on the Qwen3-VL foundation model. It generates semantically rich vectors that capture both visual and textual information in a shared space, enabling:

- **Cross-modal retrieval**: Find images using text queries or vice versa
- **Multimodal search**: Search across documents containing mixed media
- **Content clustering**: Group similar content regardless of modality
- **Visual question answering**: Match questions to relevant visual content
- **RAG pipelines**: Enhance retrieval-augmented generation with multimodal context

The models support over 30 languages and offer flexible vector dimensions through Matryoshka Representation Learning (MRL).

## When to Use

Use this skill when:

- Building multimodal search engines or information retrieval systems
- Implementing cross-modal similarity computation (text-image, text-video)
- Creating RAG pipelines that need to retrieve visual content
- Performing content clustering across different modalities
- Developing visual question answering applications
- Needing instruction-tuned embeddings for specific tasks
- Working with mixed-modal inputs (text + images, text + video, etc.)

## Core Concepts

### Model Variants

| Model | Parameters | Embedding Dimension | Context Length | Best For |
|-------|-----------|---------------------|----------------|----------|
| **Qwen3-VL-Embedding-2B** | 2B | 2048 (64-2048 via MRL) | 32K | Faster inference, lower memory |
| **Qwen3-VL-Embedding-8B** | 8B | 4096 (64-4096 via MRL) | 32K | Higher accuracy, complex tasks |

### Key Features

- **Multimodal Input**: Accepts text, images, screenshots, videos, and arbitrary combinations
- **Matryoshka Representation Learning (MRL)**: Supports custom embedding dimensions from 64 to 2048/4096
- **Instruction-Aware**: Customizable task-specific instructions improve performance by 1-5%
- **Quantization Support**: Maintains strong performance with quantized embeddings
- **30+ Languages**: Native multilingual support for global applications

### Architecture

The embedding model uses a **dual-tower architecture** that:
- Receives single-modal or mixed-modal input
- Extracts the hidden state vector at the `[EOS]` token from the last layer
- Produces independent semantic vectors for efficient large-scale retrieval

For comparison, Qwen3-VL-Reranker uses a **single-tower architecture** with cross-attention for precise relevance scoring.

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

huggingface-cli download Qwen/Qwen3-VL-Embedding-2B --local-dir ./models/Qwen3-VL-Embedding-2B
# Or for 8B variant:
huggingface-cli download Qwen/Qwen3-VL-Embedding-8B --local-dir ./models/Qwen3-VL-Embedding-8B
```

**From ModelScope:**

```bash
uv pip install modelscope

modelscope download --model qwen/Qwen3-VL-Embedding-2B --local_dir ./models/Qwen3-VL-Embedding-2B
```

## Usage Examples

### Basic Text Embedding

Generate embeddings for text queries:

```python
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder
import torch

# Initialize model
model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"  # Recommended for performance
)

# Text-only inputs
inputs = [
    {"text": "A woman playing with her dog on a beach at sunset."},
    {"text": "Pet owner training dog outdoors near water."},
    {"text": "City skyline view from a high-rise building at night."}
]

# Generate embeddings
embeddings = model.process(inputs)
print(f"Embedding shape: {embeddings.shape}")  # (3, 2048) for 2B model
```

### Image Embedding

Embed images for retrieval:

```python
from PIL import Image

# Image-only inputs
inputs = [
    {"image": "path/to/image1.jpg"},
    {"image": "https://example.com/image2.png"},
    {"image": Image.open("path/to/image3.jpg")}  # PIL Image object
]

embeddings = model.process(inputs)
```

### Multimodal Embedding

Combine text and images in a single input:

```python
inputs = [
    {
        "text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset.",
        "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
    },
    {
        "text": "Product description text",
        "image": ["image1.jpg", "image2.jpg"]  # Multiple images
    }
]

embeddings = model.process(inputs)
```

### Video Embedding

Process video inputs with frame sampling:

```python
# Initialize with video settings
model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    fps=1.0,           # Sample 1 frame per second
    max_frames=64      # Maximum 64 frames
)

# Video inputs
inputs = [
    {"video": "path/to/video.mp4"},
    {
        "video": ["frame1.jpg", "frame2.jpg", "frame3.jpg"],  # Frame sequence
        "text": "A cooking tutorial showing pasta preparation"
    }
]

embeddings = model.process(inputs)
```

### Similarity Search

Compute cosine similarity between queries and documents:

```python
import numpy as np

# Define queries and documents
queries = [
    {"text": "A woman playing with her dog on a beach at sunset."}
]

documents = [
    {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach."},
    {"image": "beach_dog.jpg"},
    {"text": "City skyline at night", "image": "cityscape.jpg"}
]

# Generate embeddings for all inputs
inputs = queries + documents
embeddings = model.process(inputs)

# Split into query and document embeddings
query_embeddings = embeddings[:len(queries)]
doc_embeddings = embeddings[len(queries):]

# Compute similarity scores (cosine similarity if normalized)
similarity_scores = query_embeddings @ doc_embeddings.T
print(f"Similarity scores: {similarity_scores.tolist()}")

# Get top-k results
top_k_indices = np.argsort(similarity_scores[0])[::-1][:5]
for idx in top_k_indices:
    print(f"Document {idx}: score={similarity_scores[0][idx]:.4f}")
```

### Instruction-Tuned Embeddings

Customize embeddings for specific tasks using instructions:

```python
# Task-specific instructions improve performance by 1-5%
inputs = [
    {
        "text": "What is the capital of France?",
        "instruction": "Represent the question for retrieving relevant documents."
    },
    {
        "text": "Paris is the capital and largest city of France.",
        "instruction": "Represent the document for retrieval."
    }
]

embeddings = model.process(inputs)
```

**Recommended instructions by task:**

```python
INSTRUCTIONS = {
    "retrieval": "Retrieve images or text relevant to the user's query.",
    "classification": "Represent the input for classification into categories.",
    "clustering": "Represent the input for clustering similar items.",
    "vqa": "Represent the visual question for answering.",
    "multilingual": "Represent the user's input."  # Use English for best results
}
```

### Matryoshka Representation Learning (MRL)

Use custom embedding dimensions for memory-efficient storage:

```python
# Default: full dimension (2048 for 2B, 4096 for 8B)
full_embeddings = model.process(inputs)

# Extract smaller dimensions (supports 64 to max dimension)
def truncate_embedding(embeddings, target_dim):
    """Truncate embeddings to specified dimension using MRL."""
    return embeddings[:, :target_dim]

# Use different dimensions for different stages
recall_embeddings = truncate_embedding(embeddings, 512)   # Fast initial retrieval
rerank_embeddings = truncate_embedding(embeddings, 1024)  # More precise re-ranking
```

MRL allows you to:
- Store smaller embeddings for large-scale indexing
- Use larger dimensions for precision-critical tasks
- Dynamically adjust dimension based on latency requirements

## Advanced Topics

See the following reference files for deeper coverage:

- **[Model Architecture](refs/01-model-architecture.md)**: Dual-tower vs single-tower designs, LoRA configs, technical specifications
- **[Usage Patterns](refs/02-usage-patterns.md)**: vLLM integration, SGLang deployment, batch processing, production patterns
- **[Performance Benchmarks](refs/03-performance-benchmarks.md)**: MMEB-V2 and MMTEB results, comparison with other models
- **[Multimodal RAG](refs/04-multimodal-rag.md)**: End-to-end RAG pipelines combining embedding, reranking, and generation

## Model Performance

Qwen3-VL-Embedding achieves state-of-the-art results on multimodal benchmarks:

### MMEB-V2 Benchmark (Overall Score)

| Model | Size | Image | Video | VisDoc | Overall |
|-------|------|-------|-------|--------|---------|
| Qwen3-VL-Embedding-2B | 2B | 75.0 | 61.9 | 79.2 | **73.2** |
| Qwen3-VL-Embedding-8B | 8B | 80.1 | 67.1 | 82.4 | **77.8** |

### MMTEB Benchmark (Mean Task Score)

| Model | Size | Mean (Task) | Mean (Type) |
|-------|------|-------------|-------------|
| Qwen3-VL-Embedding-2B | 2B | 63.87 | 55.84 |
| Qwen3-VL-Embedding-8B | 8B | 67.88 | 58.88 |

## Best Practices

1. **Use Flash Attention 2**: Enable `attn_implementation="flash_attention_2"` for 2-3x faster inference
2. **Choose the right model size**: 2B for speed, 8B for accuracy
3. **Leverage instructions**: Add task-specific instructions for 1-5% performance boost
4. **Use MRL for efficiency**: Store smaller dimensions (256-512) for large-scale retrieval
5. **Batch processing**: Process multiple inputs together for better throughput
6. **Normalize embeddings**: Use cosine similarity by normalizing embedding vectors
7. **Quantize for deployment**: Models maintain performance with INT8/FP4 quantization

## Troubleshooting

### Issue: Out of Memory Error

**Solution**: Reduce image resolution or use smaller model:

```python
model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",  # Use 2B instead of 8B
    max_pixels=409600,  # Reduce from default 1843200
    torch_dtype=torch.float16  # Use FP16 instead of BF16
)
```

### Issue: Slow Inference

**Solution**: Enable Flash Attention and batch processing:

```python
model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16
)

# Process in batches
batch_size = 32
for i in range(0, len(inputs), batch_size):
    batch_embeddings = model.process(inputs[i:i+batch_size])
```

### Issue: Poor Retrieval Quality

**Solution**: Use task-specific instructions and reranking:

```python
# Add instruction
inputs = [{
    "text": query,
    "instruction": "Retrieve images or text relevant to the user's query."
}]

# Consider using Qwen3-VL-Reranker for re-ranking top-k results
```

### Issue: Video Processing Too Slow

**Solution**: Adjust frame sampling:

```python
model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    fps=0.5,        # Sample fewer frames
    max_frames=32   # Reduce maximum frames
)
```

## References

- **Official GitHub**: https://github.com/QwenLM/Qwen3-VL-Embedding
- **Hugging Face - 2B**: https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B
- **Hugging Face - 8B**: https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
- **Technical Report**: https://arxiv.org/abs/2601.04720
- **Qwen Blog**: https://qwen.ai/blog?id=qwen3-vl-embedding
- **MMEB-V2 Benchmark**: https://huggingface.co/spaces/TIGER-Lab/MMEB-Leaderboard
- **MMTEB Benchmark**: https://huggingface.co/spaces/mteb/leaderboard

## Citation

If you use Qwen3-VL-Embedding in your research:

```bibtex
@article{qwen3vlembedding,
  title={Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking},
  author={Li, Mingxin and Zhang, Yanzhao and Long, Dingkun and Chen, Keqin and Song, Sibo and Bai, Shuai and Yang, Zhibo and Xie, Pengjun and Yang, An and Liu, Dayiheng and Zhou, Jingren and Lin, Junyang},
  journal={arXiv preprint arXiv:2601.04720},
  year={2026}
}
```
