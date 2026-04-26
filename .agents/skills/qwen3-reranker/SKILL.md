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
  - rag
  - semantic-search
category: ai-ml
external_references:
  - https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
  - https://huggingface.co/Qwen/Qwen3-Reranker-4B
  - https://huggingface.co/Qwen/Qwen3-Reranker-8B
  - https://arxiv.org/abs/2506.05176
  - https://github.com/QwenLM/Qwen3-Embedding
  - https://qwenlm.github.io/blog/qwen3-embedding/
---

# Qwen3 Reranker

## Overview

Qwen3 Reranker is a family of cross-encoder text reranking models built on the Qwen3 foundation models. Part of the broader Qwen3 Embedding series, these rerankers are designed to score query-document relevance with state-of-the-art accuracy across 100+ languages and programming languages. They use a cross-encoder architecture that processes query-document pairs jointly, producing relevance scores through a binary classification head (yes/no judgment).

The series comes in three sizes — 0.6B, 4B, and 8B parameters — all supporting 32K context length and instruction-aware prompting. Models are licensed under Apache 2.0 and available on Hugging Face and ModelScope.

## When to Use

- Re-ranking candidate documents retrieved by a dense embedding model in a two-stage RAG pipeline
- Improving retrieval relevance for multilingual or cross-lingual search systems
- Code retrieval and programmatic search tasks
- Any scenario where cross-encoder reranking provides better precision than bi-encoder similarity alone
- Building semantic search, question answering, or document ranking systems

## Core Concepts

**Cross-encoder architecture**: Unlike bi-encoder embedding models that encode query and document independently, Qwen3 Reranker processes both together through the full transformer, enabling deep interaction between query and document tokens. This produces more accurate relevance scores at the cost of higher compute per pair.

**Binary classification head**: The model is trained to predict whether a document meets the requirements of a query, outputting "yes" or "no". At inference, the logits for these two tokens are converted to a relevance score via softmax, giving a probability between 0 and 1. When used through Sentence Transformers' `CrossEncoder`, raw logit differences are returned by default.

**Instruction awareness**: Each reranking input includes an `<Instruct>` field that describes the task context (e.g., "Given a web search query, retrieve relevant passages that answer the query"). Customizing this instruction to match your specific use case typically improves performance by 1-5%. Instructions should be written in English even for multilingual queries.

**Two-stage retrieval**: The recommended pattern is dense retrieval first (using Qwen3 Embedding or any other embedding model to get top-K candidates), then reranking with Qwen3 Reranker on those candidates. This balances efficiency (embedding) with accuracy (reranking).

## Model Specifications

Three sizes are available:

- **Qwen3-Reranker-0.6B** — 28 layers, 0.6B parameters, base model Qwen3-0.6B-Base. Best for latency-sensitive or resource-constrained deployments.
- **Qwen3-Reranker-4B** — 36 layers, 4B parameters, base model Qwen3-4B-Base. Strong balance of performance and efficiency, best overall MTEB-R and FollowIR scores.
- **Qwen3-Reranker-8B** — 36 layers, 8B parameters, base model Qwen3-8B-Base. Highest accuracy on Chinese (CMTEB-R), multilingual (MMTEB-R), and code retrieval benchmarks.

All models support 32K context length and instruction-aware prompting. License: Apache 2.0.

## Usage Examples

### Sentence Transformers (recommended for simplicity)

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Reranker-0.6B")

query = "What is the capital of China?"
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other.",
]

# Raw logit difference scores
scores = model.predict([(query, doc) for doc in documents])
print(scores)  # [7.625, -11.375]

# Ranked results with corpus IDs
rankings = model.rank(query, documents)
print(rankings)  # [{'corpus_id': 0, 'score': 7.625}, ...]

# Probability scores (0-1 range) via sigmoid
import torch
scores = model.predict(
    [(query, doc) for doc in documents],
    activation_fn=torch.nn.Sigmoid()
)
```

### Custom instructions via prompts

```python
model = CrossEncoder(
    "Qwen/Qwen3-Reranker-0.6B",
    prompts={
        "classification": "Classify whether the document matches the query topic",
        "qa": "Given a question, retrieve passages that contain the answer",
    },
    default_prompt_name="qa",
)
```

### Transformers (raw access)

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B", padding_side="left"
)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2",
).cuda().eval()

token_false_id = tokenizer.convert_tokens_to_ids("no")
token_true_id = tokenizer.convert_tokens_to_ids("yes")

# Format: <Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}
instruction = "Given a web search query, retrieve relevant passages that answer the query"
pairs = [
    f"<Instruct>: {instruction}\n<Query>: What is Python?\n<Document>: Python is a programming language."
]

inputs = tokenizer(pairs, padding=True, truncation=True, max_length=8192, return_tensors="pt").to(model.device)

with torch.no_grad():
    logits = model(**inputs).logits[:, -1, :]
    true_vec = logits[:, token_true_id]
    false_vec = logits[:, token_false_id]
    scores = torch.nn.functional.softmax(torch.stack([false_vec, true_vec], dim=1), dim=1)[:, 1]
    print(scores.tolist())
```

Requires `transformers>=4.51.0` (earlier versions raise `KeyError: 'qwen3'`).

## Advanced Topics

**Architecture and Training**: Cross-encoder design, LoRA fine-tuning, training pipeline details → [Architecture and Training](reference/01-architecture-and-training.md)

**Benchmark Results**: MTEB-R, CMTEB-R, MMTEB-R, MLDR, MTEB-Code, FollowIR scores with comparisons → [Benchmark Results](reference/02-benchmark-results.md)

**vLLM Deployment**: High-throughput serving with vLLM, prefix caching, tensor parallelism → [vLLM Deployment](reference/03-vllm-deployment.md)

**Multilingual Support**: 100+ supported languages, cross-lingual retrieval, code search capabilities → [Multilingual Support](reference/04-multilingual-support.md)

## Best Practices

- **Always use instructions**: Custom task-specific instructions improve performance by 1-5%. Write them in English even for non-English queries.
- **Combine with embedding models**: Use Qwen3-Embedding-0.6B (or any dense retriever) for initial top-100 retrieval, then rerank with the reranker.
- **Flash Attention 2**: Enable `attn_implementation="flash_attention_2"` and use `torch.float16` for significant speed and memory improvements.
- **Left padding**: Set `padding_side="left"` on the tokenizer for optimal attention behavior.
- **Model selection**: Use 0.6B for latency-sensitive workloads, 4B for best overall performance, 8B for maximum accuracy on multilingual and code tasks.
