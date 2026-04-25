# Model Architecture & Specifications

## Overview

The Qwen3-VL-Embedding series is built on the Qwen3-VL foundation model, extending its multimodal capabilities to generate semantic embeddings for text, images, screenshots, and videos in a unified representation space.

## Model Specifications

| Feature | Qwen3-VL-Embedding-2B | Qwen3-VL-Embedding-8B |
|---------|----------------------|----------------------|
| **Parameters** | 2B | 8B |
| **Layers** | 28 | 36 |
| **Context Length** | 32K tokens | 32K tokens |
| **Max Embedding Dimension** | 2048 | 4096 |
| **MRL Support** | ✅ (64–2048) | ✅ (64–4096) |
| **Quantization** | ✅ INT8/INT4 | ✅ INT8/INT4 |
| **Instruction Aware** | ✅ | ✅ |
| **Languages** | 30+ | 30+ |

## Architecture: Dual-Tower Design

The embedding model uses a **dual-tower architecture**:

1. **Input Processing**: Accepts single-modal or mixed-modal inputs (text, images, screenshots, videos)
2. **Token Extraction**: Extracts the hidden state vector corresponding to the `[EOS]` token from the last layer
3. **Vector Output**: Produces a high-dimensional semantic representation suitable for similarity computation

This design enables:
- Efficient, independent encoding of each input
- Large-scale retrieval through fast vector search
- Cross-modal comparison in a shared embedding space

## Matryoshka Representation Learning (MRL)

Both models support MRL, enabling **flexible embedding dimensions**:

- **2B model**: Output dimensions from 64 to 2048
- **8B model**: Output dimensions from 64 to 4096

This allows trade-offs between storage/compute and embedding quality by truncating the vector to the desired dimension.

## LoRA Fine-Tuning Configuration

| Parameter | Value |
|-----------|-------|
| **Rank (r)** | 32 |
| **Alpha** | 32 |
| **Target Modules** | `q_proj`, `v_proj`, `k_proj`, `up_proj`, `down_proj`, `gate_proj` |

## Pixel/Frame Constraints

### Image Settings
- **Minimum pixels**: 4,096 (`4 × 16² × 2`)
- **Maximum pixels**: 1,843,200 (equivalent to 1280×1440 resolution)
- **Base factor**: 16 (image dimension alignment)

### Video Settings
- **Default FPS**: 1.0 frames per second
- **Maximum frames**: 64
- **Per-frame max pixels**: 983,040 (768×1280 resolution)
- **Total video pixels**: 7,864,320 (multiplied by 2 in model processing)

## Model Comparison: Embedding vs Reranker

| Aspect | Qwen3-VL-Embedding | Qwen3-VL-Reranker |
|--------|-------------------|-------------------|
| **Core Function** | Semantic representation, embedding generation | Relevance scoring, pointwise re-ranking |
| **Input** | Single modality or mixed modalities | (Query, Document) pair |
| **Architecture** | Dual-Tower | Single-Tower with Cross-Attention |
| **Mechanism** | Efficient retrieval | Deep inter-modal interaction |
| **Output** | Semantic vector | Relevance score (yes/no probability) |

## Training Paradigm

The models are trained through a multi-stage process:
1. **Large-scale contrastive pre-training** on diverse multimodal data
2. **Reranking model distillation** for improved semantic alignment
3. **Matryoshka representation learning** for dimension flexibility

This produces semantically rich vectors that capture both visual and textual information in a shared space.

## References

- Technical Report: https://arxiv.org/abs/2601.04720
- GitHub Repository: https://github.com/QwenLM/Qwen3-VL-Embedding
- Qwen3-VL Foundation: https://huggingface.co/collections/Qwen/qwen3-vl
