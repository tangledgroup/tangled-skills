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
## Overview
Qwen3-VL-Reranker is a series of multimodal reranking models built on the Qwen3-VL foundation architecture, designed for state-of-the-art cross-modal and text-only relevance scoring. The series includes two variants: **2B** (2 billion parameters, 28 layers) and **8B** (8 billion parameters, 36 layers), both supporting 32K context length across text, images, screenshots, videos, and arbitrary multimodal combinations.

The reranker takes a **(query, document) pair** as input—where both may contain arbitrary single or mixed modalities—and outputs a precise relevance score. It is typically used in tandem with an embedding model: the embedding performs efficient initial recall, while the reranker refines results in a second stage, significantly boosting retrieval accuracy.

Both models support 30+ languages and are instruction-aware, meaning you can provide custom instructions tailored to your specific task for 1–5% improvement over default behavior.

## When to Use
- **Reranking search results** after an initial embedding-based recall step
- **Multimodal retrieval pipelines** where documents include images, screenshots, or videos alongside text
- **Visual document retrieval** (e.g., extracting relevant pages from scanned PDFs)
- **Cross-modal relevance scoring** between image-text pairs, video-text pairs, or mixed inputs
- **Building two-stage retrieval systems**: embedding for recall → reranker for precision
- **Scoring arbitrary query-document pairs** with text-only, image-only, or multimodal documents

## Core Concepts
### Model Architecture

| Feature | Qwen3-VL-Reranker-2B | Qwen3-VL-Reranker-8B |
|---------|---------------------|---------------------|
| Parameters | 2B | 8B |
| Layers | 28 | 36 |
| Context Length | 32K tokens | 32K tokens |
| Quantization | N/A (reranker) | N/A (reranker) |
| Instruction Aware | Yes | Yes |

### Supported Input Modalities

- **Text**: Plain text documents, screenshots described as text
- **Images**: Single images via URL or file path
- **Videos**: Video content (via FPS sampling parameter)
- **Mixed**: Arbitrary combinations, e.g., `{text: "...", image: "url"}`

### Score Interpretation

Raw scores are unbounded real numbers. Apply `torch.nn.Sigmoid()` to map them to the 0–1 range for probability-like interpretation. Higher scores indicate higher relevance.

### Default Prompt and Instructions

- **Default prompt**: `"query"`
- **Default instruction**: `"Retrieve text relevant to the user's query."`
- **Recommendation**: Always provide a custom `prompt`/instruction tailored to your task. In multilingual contexts, write instructions in English for best results (training data was primarily English).

## Installation / Setup
### Dependencies

```bash
# For Sentence Transformers API (simplest)
pip install sentence_transformers torch

# For native Transformers API
pip install transformers>=4.57.0 qwen-vl-utils>=0.0.14 torch==2.8.0

# For vLLM serving
pip install vllm
```

### Hardware Requirements

- **2B model**: ~4–8 GB VRAM (bfloat16), can run on a single GPU
- **8B model**: ~16–32 GB VRAM (bfloat16), recommended for high-throughput or A100/H100
- Flash Attention 2 is recommended for both models to reduce memory and accelerate inference

## Usage Examples
### Method 1: Sentence Transformers (Recommended for Most Use Cases)

```python
from sentence_transformers import CrossEncoder
import torch

model = CrossEncoder("Qwen/Qwen3-VL-Reranker-2B")

query = "A woman playing with her dog on a beach at sunset."
documents = [
    # Text-only document
    "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset.",
    # Image URL as document
    "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
    # Mixed text + image document
    {
        "text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset.",
        "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
    },
]

prompt = "Retrieve images or text relevant to the user's query."

# Get raw relevance scores
pairs = [(query, doc) for doc in documents]
scores = model.predict(pairs, prompt=prompt)
print(scores)  # e.g., [1.8125, 0.5625, 1.3125]

# Get ranked results (descending by score)
rankings = model.rank(query, documents, prompt=prompt)
print(rankings)
# [{'corpus_id': 0, 'score': 1.8125}, {'corpus_id': 2, 'score': 1.3125}, {'corpus_id': 1, 'score': 0.5625}]

# Map scores to 0–1 with sigmoid
sigmoid_scores = model.predict(pairs, activation_fn=torch.nn.Sigmoid(), prompt=prompt)
print(sigmoid_scores)  # e.g., [0.8594, 0.6367, 0.7891]
```

### Method 2: Native Transformers API (For Advanced Control)

```python
from scripts.qwen3_vl_reranker import Qwen3VLReranker

model_name_or_path = "Qwen/Qwen3-VL-Reranker-2B"

# Initialize with Flash Attention 2 for acceleration
model = Qwen3VLReranker(
    model_name_or_path=model_name_or_path,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)

inputs = {
    "instruction": "Retrieve images or text relevant to the user's query.",
    "query": {"text": "A woman playing with her dog on a beach at sunset."},
    "documents": [
        {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach."},
        {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"},
        {
            "text": "A woman shares a joyful moment with her golden retriever.",
            "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
        },
    ],
    "fps": 1.0,  # Frames per second for video processing
}

scores = model.process(inputs)
print(scores)  # e.g., [0.8613, 0.6757, 0.8125]
```

### Method 3: vLLM (For Production Serving)

```python
from vllm import LLM, EngineArgs
from pathlib import Path

engine_args = EngineArgs(
    model="Qwen/Qwen3-VL-Reranker-2B",
    runner="pooling",
    dtype="bfloat16",
    trust_remote_code=True,
    hf_overrides={
        "architectures": ["Qwen3VLForSequenceClassification"],
        "classifier_from_token": ["no", "yes"],
        "is_original_qwen3_reranker": True,
    },
)

llm = LLM(**vars(engine_args))

# Format documents for scoring
def format_document(doc_dict):
    content = []
    if doc_dict.get("text"):
        content.append({"type": "text", "text": doc_dict["text"]})
    if doc_dict.get("image"):
        image_url = doc_dict["image"]
        if isinstance(image_url, str) and not image_url.startswith(("http", "https", "oss")):
            import os
            image_url = "file://" + os.path.abspath(image_url)
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    if not content:
        content.append({"type": "text", "text": ""})
    return {"content": content}

query_text = "A woman playing with her dog on a beach at sunset."
documents = [
    {"text": "A woman shares a joyful moment with her golden retriever."},
    {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"},
]

for doc_dict in documents:
    outputs = llm.score(query_text, format_document(doc_dict))
    score = outputs[0].outputs.score
    print(f"Score: {score}")
```

## Advanced Topics
## Advanced Topics

- [Benchmarks And Performance](reference/01-benchmarks-and-performance.md)
- [Retrieval Pipeline Patterns](reference/02-retrieval-pipeline-patterns.md)
- [Api Reference](reference/03-api-reference.md)

