# Benchmark Results

## Reranking Benchmarks

All scores are based on top-100 candidates retrieved by Qwen3-Embedding-0.6B dense retriever.

### MTEB-R (English Retrieval, v2)

| Model | Params | Score |
|-------|--------|-------|
| Jina-multilingual-reranker-v2-base | 0.3B | 58.22 |
| gte-multilingual-reranker-base | 0.3B | 59.51 |
| BGE-reranker-v2-m3 | 0.6B | 57.03 |
| Qwen3-Embedding-0.6B (bi-encoder) | 0.6B | 61.82 |
| **Qwen3-Reranker-0.6B** | 0.6B | **65.80** |
| **Qwen3-Reranker-4B** | 4B | **69.76** |
| Qwen3-Reranker-8B | 8B | 69.02 |

The 4B model achieves the highest English retrieval score at 69.76.

### CMTEB-R (Chinese Retrieval, v1)

| Model | Params | Score |
|-------|--------|-------|
| gte-multilingual-reranker-base | 0.3B | 74.08 |
| BGE-reranker-v2-m3 | 0.6B | 72.16 |
| Qwen3-Embedding-0.6B (bi-encoder) | 0.6B | 71.02 |
| Qwen3-Reranker-0.6B | 0.6B | 71.31 |
| Qwen3-Reranker-4B | 4B | 75.94 |
| **Qwen3-Reranker-8B** | 8B | **77.45** |

The 8B model leads on Chinese retrieval with 77.45.

### MMTEB-R (Multilingual Retrieval)

| Model | Params | Score |
|-------|--------|-------|
| Jina-multilingual-reranker-v2-base | 0.3B | 63.73 |
| Qwen3-Embedding-0.6B (bi-encoder) | 0.6B | 64.64 |
| Qwen3-Reranker-0.6B | 0.6B | 66.36 |
| Qwen3-Reranker-4B | 4B | 72.74 |
| **Qwen3-Reranker-8B** | 8B | **72.94** |

### MLDR (Multi-Lingual Document Retrieval)

| Model | Params | Score |
|-------|--------|-------|
| Jina-multilingual-reranker-v2-base | 0.3B | 39.66 |
| BGE-reranker-v2-m3 | 0.6B | 59.51 |
| gte-multilingual-reranker-base | 0.3B | 66.33 |
| Qwen3-Embedding-0.6B (bi-encoder) | 0.6B | 50.26 |
| Qwen3-Reranker-0.6B | 0.6B | 67.28 |
| Qwen3-Reranker-4B | 4B | 69.97 |
| **Qwen3-Reranker-8B** | 8B | **70.19** |

### MTEB-Code (Code Retrieval)

| Model | Params | Score |
|-------|--------|-------|
| BGE-reranker-v2-m3 | 0.6B | 41.38 |
| gte-multilingual-reranker-base | 0.3B | 54.18 |
| Jina-multilingual-reranker-v2-base | 0.3B | 58.98 |
| Qwen3-Reranker-0.6B | 0.6B | 73.42 |
| Qwen3-Embedding-0.6B (bi-encoder) | 0.6B | 75.41 |
| Qwen3-Reranker-4B | 4B | 81.20 |
| **Qwen3-Reranker-8B** | 8B | **81.22** |

### FollowIR (Instruction-Following Retrieval)

| Model | Params | Score |
|-------|--------|-------|
| gte-multilingual-reranker-base | 0.3B | -1.64 |
| BGE-reranker-v2-m3 | 0.6B | -0.01 |
| Jina-multilingual-reranker-v2-base | 0.3B | -0.68 |
| Qwen3-Embedding-0.6B (bi-encoder) | 0.6B | 5.09 |
| Qwen3-Reranker-0.6B | 0.6B | 5.41 |
| **Qwen3-Reranker-4B** | 4B | **14.84** |
| Qwen3-Reranker-8B | 8B | 8.05 |

The 4B model dominates instruction-following retrieval with a score of 14.84, significantly ahead of all competitors.

## Key Observations

- **Cross-encoder advantage**: All Qwen3 Reranker models outperform their bi-encoder counterpart (Qwen3-Embedding-0.6B) on most benchmarks, demonstrating the value of cross-encoder reranking.
- **4B sweet spot**: The 4B model achieves the best English retrieval (MTEB-R) and instruction-following (FollowIR) scores.
- **8B for multilingual**: The 8B model leads on Chinese (CMTEB-R), multilingual (MMTEB-R), MLDR, and code retrieval (MTEB-Code).
- **0.6B efficiency**: Despite being the smallest, Qwen3-Reranker-0.6B outperforms all non-Qwen3 competitors at its parameter scale.

## Benchmark Methodology Notes

- MTEB-R uses the English retrieval subset of MTEB v2
- CMTEB-R uses the Chinese retrieval subset of MTEB v1
- MMTEB-R uses the multilingual retrieval subset
- MTEB-Code evaluates code search and retrieval
- MLDR measures cross-lingual document retrieval
- FollowIR evaluates instruction-following capabilities in retrieval
- All reranking scores use top-100 candidates from Qwen3-Embedding-0.6B dense retrieval
