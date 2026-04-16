# Model Architecture & Training

## Architecture Overview

The Qwen3 Embedding series is built on the **Qwen3 dense foundation models** using two distinct architectures:

### Embedding Models (Dual-Encoder)

Embedding models use a **dual-encoder architecture**:
- Input: A single text segment
- Processing: The model processes the text through its transformer layers
- Output: Extracts the hidden state vector corresponding to the final `[EOS]` token position
- Normalization: L2-normalized embeddings (cosine similarity compatible)

The dual-encoder encodes queries and documents independently, enabling fast nearest-neighbor search via dot product or cosine similarity.

### Reranking Models (Cross-Encoder)

Reranking models use a **cross-encoder architecture**:
- Input: Text pairs (query + candidate document concatenated)
- Processing: The model attends across both texts simultaneously
- Output: A relevance score between the pair

Cross-encoders are slower but more accurate, making them ideal for re-ranking top candidates from a dense retrieval step.

## Model Specifications

| Model | Type | Parameters | Layers | Context Length | Default Dim | MRL Support | Instruction Aware |
|-------|------|-----------|--------|---------------|-------------|-------------|-------------------|
| Qwen3-Embedding-0.6B | Text Embedding | 0.6B | 28 | 32K | 1,024 | Yes | Yes |
| Qwen3-Embedding-4B | Text Embedding | 4B | 36 | 32K | 2,560 | Yes | Yes |
| Qwen3-Embedding-8B | Text Embedding | 8B | 36 | 32K | 4,096 | Yes | Yes |
| Qwen3-Reranker-0.6B | Text Reranking | 0.6B | 28 | 32K | — | — | Yes |
| Qwen3-Reranker-4B | Text Reranking | 4B | 36 | 32K | — | — | Yes |
| Qwen3-Reranker-8B | Text Reranking | 8B | 36 | 32K | — | — | Yes |

## MRL (Multi-Resolution Linear) Support

All three embedding models support **MRL** — the ability to project the final embedding to a user-defined dimension:
- **0.6B**: Output dimensions 32–1,024
- **4B**: Output dimensions 32–2,560
- **8B**: Output dimensions 32–4,096

This is useful for reducing storage and computation costs in vector databases while maintaining acceptable similarity quality.

## Instruction-Aware Design

Both embedding and reranking models support **user-defined instructions** that describe the task:

```python
# Format for queries (embeddings) or query-document pairs (rerankers)
text = f'Instruct: {task_description}\nQuery:{query_text}'
```

Key guidelines:
- Instructions are most impactful on the **query side** (for embeddings) or first text (for rerankers)
- Using instructions typically yields a **1–5% improvement** over no instruction
- In multilingual contexts, write instructions in **English** (most training data used English instructions)
- Tailor instructions to your specific task, domain, and language

## Training Pipeline

### Embedding Models: Three-Stage Training

1. **Contrastive Pre-training**: Large-scale weakly supervised data with diverse text pairs
2. **Supervised Fine-tuning**: High-quality labeled data for specific retrieval tasks
3. **Model Merging**: Combines multiple candidate models via merging strategies for robustness

### Reranking Models: Direct Supervised Training

Based on empirical validation, reranking models use direct supervised training with high-quality labeled data, which was found to be more efficient than multi-stage training.

### Data Synthesis with Qwen3 Foundation Model

A key innovation: The Qwen3 LLM itself is used to **synthesize training data**:
- Generates weakly supervised text pairs for different task types and languages
- Creates diverse, domain-specific examples via a multi-task adaptable prompt system
- Addresses the limitation of relying on community forums or open-source data

## Hardware Requirements (Approximate)

| Model | BF16 Weights | GPU Memory (min) | GPU Memory (batch=32) |
|-------|-------------|-------------------|----------------------|
| 0.6B | ~1.2 GB | 4 GB | ~8 GB |
| 4B | ~8 GB | 12 GB | ~24 GB |
| 8B | ~16 GB | 24 GB | ~48 GB |

*Note: The 8B model weights are sharded across 4 files. Flash attention 2 reduces memory usage significantly.*

## References

- Technical Report (arXiv): https://arxiv.org/abs/2506.05176
- Qwen Blog: https://qwenlm.github.io/blog/qwen3-embedding/
- GitHub: https://github.com/QwenLM/Qwen-Embedding
