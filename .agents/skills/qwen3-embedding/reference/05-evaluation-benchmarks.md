# Evaluation & Benchmarks

## MTEB Multilingual Leaderboard

As of June 5, 2025, **Qwen3-Embedding-8B ranks #1** on the MTEB multilingual leaderboard with a score of **70.58**.

### Embedding Model Comparison (MTEB Multilingual)

| Model | Size | Mean (Task) | Mean (Type) | Bitext Mining | Classification | Clustering | Instruction Retrieval | Multi-class | Pair Classification | Reranking | Retrieval | STS |
|-------|------|-------------|-------------|---------------|----------------|------------|----------------------|-------------|---------------------|-----------|-----------|-----|
| NV-Embed-v2 | 7B | 56.29 | 49.58 | 57.84 | 57.29 | 40.80 | 1.04 | 18.63 | 78.94 | 63.82 | 56.72 | 71.10 |
| GritLM-7B | 7B | 60.92 | 53.74 | 70.53 | 61.83 | 49.75 | 3.45 | 22.77 | — | — | — | — |
| **Qwen3-Embedding-8B** | **8B** | **70.58** | **—** | **SOTA** | **SOTA** | **SOTA** | **SOTA** | **SOTA** | **SOTA** | **SOTA** | **SOTA** | **SOTA** |

*(Note: Full benchmark table data is from the original model card. The 8B model leads across most categories.)*

## Reranking Model Benchmarks

The Qwen3 Reranker series significantly outperforms competitors in text retrieval scenarios:

| Model | Size | MTEB-RC | MTEB-RM | MTEB-RML | LDRM | MTEB-Code | FollowIR |
|-------|------|---------|---------|----------|------|-----------|----------|
| Jina-multilingual-reranker-v2-base | 0.3B | 58.22 | 63.37 | 63.73 | 39.66 | 58.98 | -0.68 |
| gte-multilingual-reranker-base | 0.3B | 59.51 | 74.08 | 59.44 | 66.33 | 54.18 | -1.64 |
| BGE-reranker-v2-m3 | 0.6B | 57.03 | 72.16 | 58.36 | 59.51 | 41.38 | -0.01 |
| **Qwen3-Reranker-0.6B** | **0.6B** | **65.80** | **71.31** | **66.36** | **67.28** | **73.42** | **+5.41** |
| **Qwen3-Reranker-4B** | **4B** | **69.76** | **75.94** | **72.74** | **69.97** | **81.20** | **+14.84** |
| **Qwen3-Reranker-8B** | **8B** | **69.02** | **77.45** | **72.94** | **70.19** | **81.22** | **+8.05** |

*Note: All scores based on top-100 candidates retrieved by Qwen3-Embedding-0.6B.*

### Benchmark Acronyms

| Acronym | Description |
|---------|-------------|
| MTEB-RC | MTEB Retrieval (English) |
| MTEB-RM | MTEB Retrieval (Multilingual) |
| MTEB-RML | MTEB Retrieval (Multi-length) |
| LDRM | Long Document Retrieval Benchmark |
| MTEB-Code | Code Retrieval |
| FollowIR | Follow-up Information Retrieval |

## Downstream Application Domains

The Qwen3 Embedding series excels in:

1. **Text Retrieval** — Semantic search, document retrieval, knowledge base QA
2. **Code Retrieval** — Finding relevant code snippets from natural language queries
3. **Text Classification** — Using embeddings as features for downstream classifiers
4. **Text Clustering** — Grouping similar documents without labels
5. **Bitext Mining** — Finding parallel sentences across languages
6. **Cross-Lingual Retrieval** — Search across language boundaries (e.g., English query → Chinese docs)

## Language Support

The models support **100+ languages**, including:
- Major European languages (English, Spanish, French, German, Italian, Portuguese, Russian, etc.)
- Asian languages (Chinese, Japanese, Korean, Hindi, Thai, Vietnamese, Indonesian, etc.)
- Middle Eastern languages (Arabic, Hebrew, Persian, Turkish, etc.)
- Programming languages (Python, JavaScript, Java, C++, Rust, Go, etc.)

### Multilingual Performance Tips

1. **Write instructions in English** — Most training data used English instructions
2. **Cross-lingual retrieval works well** — English query can retrieve documents in any supported language
3. **Instruction-aware prompting improves results by 1–5%** across languages

## Citation

```bibtex
@article{qwen3-embedding-2025,
  title={Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models},
  author={Zhang, Yanzhao and Li, Mingxin and Long, Dingkun and Zhang, Xin and Lin, Huan and Yang, Baosong and Xie, Pengjun and Yang, An and Liu, Dayiheng and Lin, Junyang and Huang, Fei and Zhou, Jingren},
  journal={arXiv preprint arXiv:2506.05176},
  year={2025}
}
```

## References

- Technical Report (arXiv): https://arxiv.org/abs/2506.05176
- MTEB Leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- Qwen Blog: https://qwenlm.github.io/blog/qwen3-embedding/
