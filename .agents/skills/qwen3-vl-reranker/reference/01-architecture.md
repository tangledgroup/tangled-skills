# Architecture and Model Details

## Model Specifications

**Qwen3-VL-Reranker-2B**: 2B parameters, 28 transformer layers, 32K context length.

**Qwen3-VL-Reranker-8B**: 8B parameters, 36 transformer layers, 32K context length.

Both models are instruction-aware. Unlike the embedding variants, rerankers do not produce fixed-dimensional vectors — they output scalar relevance scores directly.

## Single-Tower Cross-Encoder Design

The reranker uses a single-tower architecture that processes the full `(query, document)` pair jointly. This contrasts with the dual-tower embedding model:

- **Dual-Tower (Embedding)**: Encodes query and document independently into vectors, then computes similarity. Efficient for large-scale retrieval but limited in cross-modal interaction depth.
- **Single-Tower (Reranker)**: Processes the full pair through cross-attention layers, enabling token-level interaction between query and document modalities. More accurate but computationally heavier — suitable for re-ranking a small candidate set (typically top-10 to top-100).

The relevance score is expressed by predicting the generation probability of special tokens `yes` and `no`, effectively framing reranking as a binary classification task over the joint representation.

## LoRA Fine-Tuning Configuration

Both models are built on Qwen3-VL via LoRA fine-tuning to preserve the foundation model's general multimodal understanding:

- **Rank**: 32
- **Alpha**: 32
- **Target modules**: `q_proj`, `v_proj`, `k_proj`, `up_proj`, `down_proj`, `gate_proj`

## Training Paradigm

The reranker is trained directly on high-quality labeled data using supervised learning. This differs from the embedding model's three-stage pipeline (contrastive pre-training → supervised fine-tuning → model merging). The simpler training approach for the reranker was chosen based on empirical validation that it achieves strong results with higher training efficiency.

## Relationship to Qwen3-VL-Embedding

The two model series are designed to work together:

1. **Recall stage**: Qwen3-VL-Embedding generates dense vectors for queries and documents, enabling fast approximate nearest neighbor search over large corpora.
2. **Reranking stage**: Qwen3-VL-Reranker takes the top-K candidates from recall and scores each `(query, candidate)` pair with cross-attention, producing a refined ranking.

This two-stage approach balances efficiency (embedding-based recall) with accuracy (cross-encoder reranking).
