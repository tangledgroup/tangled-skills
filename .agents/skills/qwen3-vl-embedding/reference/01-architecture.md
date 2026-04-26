# Architecture

## Overview

Qwen3-VL-Embedding uses a **dual-tower architecture** built on the Qwen3-VL foundation model. It is fine-tuned via LoRA with rank 32, alpha 32, targeting `q_proj`, `v_proj`, `k_proj`, `up_proj`, `down_proj`, and `gate_proj` modules across both visual and language components.

## Dual-Tower Design

The embedding model receives single-modal or mixed-modal input and maps it into a high-dimensional semantic vector. It extracts the hidden state corresponding to the `[EOS]` token from the base model's last layer as the final semantic representation. This design enables efficient, independent encoding — each input is processed separately without cross-attention between items — which is necessary for large-scale retrieval where documents are pre-encoded and stored in a vector index.

## Multi-Stage Training Paradigm

The model is trained through a progressive pipeline:

1. **Large-Scale Contrastive Pre-Training**: Learns to align representations across modalities using contrastive loss on diverse multimodal pairs.
2. **Reranking Model Distillation**: Refines embeddings by distilling knowledge from the reranker's fine-grained relevance signals, improving discriminative quality for retrieval tasks.

This multi-stage approach fully leverages Qwen3-VL's general multimodal semantic understanding capabilities while specializing for retrieval-oriented representation learning.

## Key Architectural Features

- **Matryoshka Representation Learning (MRL)**: The embedding head supports flexible output dimensions from 64 to the model maximum (2048 for 2B, 4096 for 8B). Truncating the full embedding preserves semantic quality at lower dimensions.
- **Quantization Support**: Output embeddings can be quantized post-process for storage efficiency without significant accuracy loss.
- **Instruction Awareness**: The model accepts natural language instructions that guide the embedding toward task-specific semantics, typically improving downstream performance by 1-5%.
- **30+ Language Support**: Inherits Qwen3-VL's multilingual capabilities for cross-lingual retrieval.

## Model Sizes

| Parameter | Qwen3-VL-Embedding-2B | Qwen3-VL-Embedding-8B |
|-----------|----------------------|----------------------|
| Parameters | 2B | 8B |
| Layers | 28 | 36 |
| Context Length | 32K tokens | 32K tokens |
| Max Embedding Dim | 2048 | 4096 |
| MRL Range | 64-2048 | 64-4096 |

The 2B model offers an excellent balance of performance and efficiency, while the 8B model achieves state-of-the-art results on multimodal embedding benchmarks.
