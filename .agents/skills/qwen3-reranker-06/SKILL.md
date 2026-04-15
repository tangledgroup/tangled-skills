---
name: qwen3-reranker-06
description: A skill for using Qwen3-Reranker models (0.6B, 4B, 8B) for text reranking and relevance scoring in RAG pipelines, search systems, and information retrieval tasks with support for 100+ languages, 32K context, and instruction-aware ranking.
license: MIT
author: Tangled Skills
version: "0.6"
tags:
  - reranking
  - retrieval
  - qwen
  - transformers
  - vllm
  - rag
  - multilingual
category: machine-learning
external_references:
  - https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
  - https://huggingface.co/Qwen/Qwen3-Reranker-4B
  - https://huggingface.co/Qwen/Qwen3-Reranker-8B
  - https://github.com/QwenLM/Qwen3-Embedding
---

# Qwen3-Reranker (0.6B, 4B, 8B)

## Overview

Qwen3-Reranker is a family of instruction-aware text reranking models from the Qwen family, available in three sizes (0.6B, 4B, 8B parameters). These models excel at ranking retrieved documents by relevance to queries, making them ideal for RAG (Retrieval-Augmented Generation) pipelines, search engines, and information retrieval systems.

**Key Features:**
- **Three model sizes**: 0.6B (fast), 4B (balanced), 8B (best accuracy)
- **100+ language support**: Multilingual and cross-lingual reranking
- **32K context length**: Handle long documents and queries
- **Instruction-aware**: Customize ranking behavior with task-specific instructions
- **State-of-the-art performance**: Top rankings on MTEB, C-MTEB, and MMTEB benchmarks

## When to Use

Use Qwen3-Reranker when:
- Building RAG pipelines that need to refine initial retrieval results
- Implementing two-stage retrieval (coarse retrieval + fine reranking)
- Improving search result relevance in multilingual applications
- Needing instruction-tunable ranking for specific domains or tasks
- Processing long documents (up to 32K tokens)
- Requiring cross-lingual search capabilities

**Model Selection Guide:**
- **0.6B**: Production systems with latency constraints, edge deployment
- **4B**: Best balance of accuracy and speed for most applications
- **8B**: Maximum accuracy when compute resources allow

## Quick Start

### Basic Usage with Transformers

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load the model
model_name = "Qwen/Qwen3-Reranker-0.6B"  # or 4B, 8B
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2"
).cuda().eval()

# Prepare query-document pairs
queries = ["What is the capital of China?", "Explain gravity"]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other."
]
pairs = list(zip(queries, documents))

# Format and score
instruction = "Given a web search query, retrieve relevant passages that answer the query"
formatted_pairs = [
    f"<Instruct>: {instruction}\n<Query>: {q}\n<Document>: {d}"
    for q, d in pairs
]

# Get relevance scores
scores = model.score(formatted_pairs)  # Simplified - see refs/02-transformers-api.md
print(scores)  # [0.89, 0.92]
```

See [`refs/02-transformers-api.md`](refs/02-transformers-api.md) for complete Transformers integration with batch processing and optimization.

### High-Performance Usage with vLLM

```python
from qwen3_reranker_vllm import Qwen3Rerankervllm

# Initialize with GPU parallelism
model = Qwen3Rerankervllm(
    model_name_or_path='Qwen/Qwen3-Reranker-4B',
    instruction="Retrieval document that can answer user's query",
    max_length=2048
)

queries = ['What is the capital of China?', 'Explain gravity']
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other."
]
pairs = list(zip(queries, documents))

# Score all pairs
scores = model.compute_scores(pairs)
print(scores)  # [0.87, 0.91]

# Cleanup
model.stop()
```

See [`refs/03-vllm-deployment.md`](refs/03-vllm-deployment.md) for production deployment with vLLM, including GPU optimization and scaling.

### Integration with Sentence Transformers

```python
from sentence_transformers import CrossEncoder

# Use as a drop-in CrossEncoder
model = CrossEncoder('Qwen/Qwen3-Reranker-0.6B')

queries = ["machine learning", "deep learning"]
documents = [
    "ML is a subset of AI",
    "Neural networks with many layers",
    "Supervised and unsupervised learning"
]

# Rank documents for each query
for query in queries:
    pairs = [(query, doc) for doc in documents]
    scores = model.predict(pairs)
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    print(f"Query: {query}")
    for doc, score in ranked[:2]:
        print(f"  {score:.3f}: {doc[:50]}...")
```

See [`refs/04-rag-integration.md`](refs/04-rag-integration.md) for complete RAG pipeline integration examples.

## Core Concepts

### Two-Stage Retrieval

Qwen3-Reranker is designed for **two-stage retrieval** architectures:

1. **Coarse Retrieval**: Use embedding models (e.g., Qwen3-Embedding) or BM25 to retrieve top 100-1000 candidates
2. **Fine Reranking**: Apply Qwen3-Reranker to rank top-K candidates by relevance

```
Query → [Embedding Search] → Top 500 docs → [Qwen3-Reranker] → Top 10 ranked docs → LLM
```

### Instruction-Aware Ranking

The model supports task-specific instructions that improve performance by 1-5%:

```python
# Generic instruction
instruction = "Given a web search query, retrieve relevant passages"

# Domain-specific instruction
instruction = "Retrieve medical documents that answer the clinical question"

# Code retrieval instruction
instruction = "Find code snippets that implement the described functionality"
```

**Best Practice**: Write instructions in English even for non-English queries, as training primarily used English instructions.

### Scoring Mechanism

Qwen3-Reranker outputs **probability scores** (0-1) indicating relevance:

- **Score > 0.9**: Highly relevant
- **Score 0.7-0.9**: Relevant
- **Score 0.5-0.7**: Marginally relevant
- **Score < 0.5**: Likely irrelevant

See [`refs/01-model-architecture.md`](refs/01-model-architecture.md) for detailed architecture and scoring mechanics.

## Model Comparison

| Model | Parameters | Layers | Context | Speed (tokens/s) | MTEB-R | C-MTEB-R | MMTEB-R |
|-------|-----------|--------|---------|------------------|--------|----------|---------|
| Qwen3-Reranker-0.6B | 0.6B | 28 | 32K | ~500 | 65.80 | 71.31 | 66.36 |
| Qwen3-Reranker-4B | 4B | 36 | 32K | ~150 | 69.76 | 75.94 | 72.74 |
| Qwen3-Reranker-8B | 8B | 36 | 32K | ~80 | 69.02 | 77.45 | 72.94 |

**Benchmark Notes:**
- MTEB-R: English retrieval benchmark
- C-MTEB-R: Chinese retrieval benchmark
- MMTEB-R: Multilingual retrieval benchmark
- All scores based on top-100 candidates from Qwen3-Embedding-0.6B

## Reference Documentation

### Architecture and Training
- [`refs/01-model-architecture.md`](refs/01-model-architecture.md) - Model architecture, tokenization, training details, and scoring mechanics

### API Integration
- [`refs/02-transformers-api.md`](refs/02-transformers-api.md) - Complete Transformers library integration with batch processing
- [`refs/03-vllm-deployment.md`](refs/03-vllm-deployment.md) - Production deployment with vLLM for high-throughput serving

### Application Patterns
- [`refs/04-rag-integration.md`](refs/04-rag-integration.md) - RAG pipeline integration, two-stage retrieval, and LangChain/LlamaIndex examples
- [`refs/05-multilingual-support.md`](refs/05-multilingual-support.md) - 100+ language support, cross-lingual search, and language-specific optimizations

### Performance and Benchmarks
- [`refs/06-benchmarks.md`](refs/06-benchmarks.md) - Complete benchmark results, comparison with other rerankers, and performance analysis

## Installation

```bash
# Required dependencies
pip install transformers>=4.51.0 torch sentence-transformers>=2.7.0

# For vLLM deployment (optional but recommended for production)
pip install vllm>=0.8.5 ray

# For flash attention (recommended for GPU acceleration)
pip install flash-attn
```

## Hardware Requirements

| Model | Minimum VRAM | Recommended VRAM | CPU-Only Feasible |
|-------|-------------|------------------|-------------------|
| 0.6B | 2GB | 4GB | Yes (slow) |
| 4B | 8GB | 16GB | Limited |
| 8B | 16GB | 24GB | No |

**Optimization Tips:**
- Use `flash_attention_2` for 2-3x speedup and reduced memory
- Enable quantization (FP16/INT8) for smaller memory footprint
- Use vLLM for production serving with automatic optimization

## Troubleshooting

### Common Issues

**KeyError: 'qwen3'**
- **Cause**: Transformers version < 4.51.0
- **Solution**: `pip install --upgrade transformers`

**Out of Memory Errors**
- **Solution 1**: Reduce `max_length` parameter
- **Solution 2**: Use smaller batch sizes
- **Solution 3**: Enable FP16: `torch_dtype=torch.float16`
- **Solution 4**: Use 0.6B model instead of 4B/8B

**Slow Inference**
- **Solution 1**: Enable flash_attention_2
- **Solution 2**: Use vLLM for batch serving
- **Solution 3**: Reduce context length if 32K not needed
- **Solution 4**: Use GPU instead of CPU

**Low Relevance Scores**
- **Check 1**: Ensure instruction is task-appropriate
- **Check 2**: Verify query-document pairs are formatted correctly
- **Check 3**: Consider using larger model (4B or 8B)
- **Check 4**: Check that coarse retrieval is providing relevant candidates

See [`refs/07-troubleshooting.md`](refs/07-troubleshooting.md) for comprehensive debugging guide.

## References

- **Official Repository**: https://github.com/QwenLM/Qwen3-Embedding
- **Hugging Face Models**:
  - https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
  - https://huggingface.co/Qwen/Qwen3-Reranker-4B
  - https://huggingface.co/Qwen/Qwen3-Reranker-8B
- **Technical Blog**: https://qwenlm.github.io/blog/qwen3-embedding/
- **Research Paper**: https://arxiv.org/abs/2506.05176
- **API Service**: https://bailian.console.aliyun.com/?tab=model#/model-market/detail/text-embedding-v4
- **Community**: https://discord.gg/yPEP2vHTu4

## Citation

```bibtex
@article{qwen3embedding,
  title={Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models},
  author={Zhang, Yanzhao and Li, Mingxin and Long, Dingkun and Zhang, Xin and Lin, Huan and Yang, Baosong and Xie, Pengjun and Yang, An and Liu, Dayiheng and Lin, Junyang and Huang, Fei and Zhou, Jingren},
  journal={arXiv preprint arXiv:2506.05176},
  year={2025}
}
```
