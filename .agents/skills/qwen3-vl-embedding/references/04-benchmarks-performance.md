# Benchmarks & Performance

## MMEB-V2 Benchmark Results (Leaderboard)

The Qwen3-VL-Embedding series achieves state-of-the-art results across diverse multimodal tasks. Qwen3-VL-Embedding-8B ranks **first** among all models on MMEB-V2 as of January 2026.

### Full Benchmark Comparison

| Model | Size | Image CLS | Image QA | Image RET | Image GD | Image Overall | Video CLS | Video QA | Video RET | Video MRET | Video Overall | VisDoc VDRv1 | VisDoc VDRv2 | VisDoc VR | VisDoc OOD | VisDoc Overall | **All** |
|-------|------|-----------|----------|-----------|----------|---------------|-----------|----------|-----------|------------|---------------|--------------|-------------|-----------|------------|----------------|---------|
| VLM2Vec | 2B | 58.7 | 49.3 | 65.0 | 72.9 | 59.7 | 33.4 | 30.5 | 20.6 | 30.7 | 28.6 | 49.8 | 13.5 | 51.8 | 48.2 | 44.0 | **47.7** |
| VLM2Vec-V2 | 2B | 62.9 | 56.3 | 69.5 | 77.3 | 64.9 | 39.3 | 34.3 | 28.8 | 36.8 | 34.6 | 75.5 | 44.9 | 79.4 | 62.2 | 69.2 | **59.2** |
| GME-2B | 2B | 54.4 | 29.9 | 66.9 | 55.5 | 51.9 | 34.9 | 42.0 | 25.6 | 31.1 | 33.6 | 86.1 | 54.0 | 82.5 | 67.5 | 76.8 | **55.3** |
| GME-7B | 7B | 57.7 | 34.7 | 71.2 | 59.3 | 56.0 | 37.4 | 50.4 | 28.4 | 37.0 | 38.4 | 89.4 | 55.6 | 85.0 | 68.3 | 79.3 | **59.1** |
| Ops-MM-v1 | 8B | 69.7 | 69.6 | 73.1 | 87.2 | 72.7 | 59.7 | 62.2 | 45.7 | 43.2 | 53.8 | 80.1 | 59.6 | 79.3 | 67.8 | 74.4 | **68.9** |
| IFM-TTE | 8B | **76.7** | 78.5 | 74.6 | 89.3 | 77.9 | 60.5 | 67.9 | 51.7 | 54.9 | 59.2 | 85.2 | 71.5 | **92.7** | 53.3 | 79.5 | **74.1** |
| RzenEmbed | 8B | 70.6 | 71.7 | 78.5 | 92.1 | 75.9 | 58.8 | 63.5 | 51.0 | 45.5 | 55.7 | 89.7 | 60.7 | 88.7 | 69.9 | 81.3 | **72.9** |
| Seed-1.6 | unknown | 75.0 | 74.9 | 79.3 | 89.0 | 78.0 | **85.2** | 66.7 | **59.1** | 54.8 | **67.7** | **90.0** | 60.3 | 90.0 | 70.7 | 82.2 | **76.9** |
| **Qwen3-VL-Embedding-2B** | **2B** | 70.3 | 74.3 | 74.8 | 88.5 | 75.0 | 71.9 | 64.9 | 53.9 | 53.3 | 61.9 | 84.4 | 65.3 | 86.4 | 69.4 | 79.2 | **73.2** |
| **Qwen3-VL-Embedding-8B** | **8B** | 74.2 | **81.1** | **80.0** | **92.2** | **80.1** | 78.4 | **71.0** | 58.7 | **56.1** | 67.1 | 87.2 | **69.9** | 88.7 | **73.3** | **82.4** | **77.8** |

**Benchmark Tasks:**
- **CLS**: Classification (Image/Video)
- **QA**: Question Answering (Image/Video)
- **RET**: Retrieval (Image/Video)
- **GD**: Grounding (Image)
- **MRET**: Moment Retrieval (Video)
- **VisDoc**: Visual Document Retrieval (VDRv1, VDRv2, VR, OOD)

## MMTEB Benchmark Results

Results on the multimodal MTEB benchmark. Qwen3-VL-Embedding-8B achieves competitive results across all task types.

| Model | Size | Mean (Task) | Mean (Type) | Bitxt Mining | Class. | Clust. | Inst. Retri. | Multi. Class. | Pair. Class. | Rerank | Retri. | STS |
|-------|------|-------------|-------------|--------------|--------|--------|---------------|---------------|-------------|--------|--------|-----|
| NV-Embed-v2 | 7B | 56.3 | 49.6 | 57.8 | 57.3 | 40.8 | 1.0 | 18.6 | 78.9 | 63.8 | 56.7 | 71.1 |
| GritLM-7B | 7B | 60.9 | 53.7 | 70.5 | 61.8 | 49.8 | 3.5 | 22.8 | 79.9 | 63.8 | 58.3 | 73.3 |
| BGE-M3 | 0.6B | 59.6 | 52.2 | 79.1 | 60.4 | 40.9 | -3.1 | 20.1 | 80.8 | 62.8 | 54.6 | 74.1 |
| multilingual-e5-large-instruct | 0.6B | 63.2 | 55.1 | 80.1 | 64.9 | 50.8 | -0.4 | 22.9 | 80.9 | 62.6 | 57.1 | 76.8 |
| gte-Qwen2-1.5B-instruct | 1.5B | 59.5 | 52.7 | 62.5 | 58.3 | 52.1 | 0.7 | 24.0 | 81.6 | 62.6 | 60.8 | 71.6 |
| gte-Qwen2-7b-Instruct | 7B | 62.5 | 55.9 | 73.9 | 61.6 | 52.8 | 4.9 | 25.5 | 85.1 | 65.6 | 60.1 | 74.0 |
| text-embedding-3-large | - | 58.9 | 51.4 | 62.2 | 60.3 | 46.9 | -2.7 | 22.0 | 79.2 | 63.9 | 59.3 | 71.7 |
| Cohere-embed-multilingual-v3.0 | - | 61.1 | 53.2 | 70.5 | 63.0 | 46.9 | -1.9 | 22.7 | 79.9 | 64.1 | 59.2 | 74.8 |
| Gemini Embedding | - | 68.4 | 59.6 | 79.3 | 71.8 | 54.6 | 5.2 | **29.2** | 83.6 | 65.6 | 67.7 | 79.4 |
| Qwen3-Embedding-0.6B | 0.6B | 64.3 | 56.0 | 72.2 | 66.8 | 52.3 | 5.1 | 24.6 | 80.8 | 61.4 | 64.6 | 76.2 |
| Qwen3-Embedding-4B | 4B | 69.5 | 60.9 | 79.4 | 72.3 | 57.2 | **11.6** | 26.8 | 85.1 | 65.1 | 69.6 | 80.9 |
| Qwen3-Embedding-8B | 8B | **70.6** | **61.7** | **80.9** | **74.0** | **57.7** | 10.1 | 28.7 | **86.4** | **65.6** | **70.9** | **81.1** |
| **Qwen3-VL-Embedding-2B** | **2B** | 63.9 | 55.8 | 69.5 | 65.9 | 52.5 | 3.9 | 26.1 | 78.5 | 64.8 | 67.1 | 74.3 |
| **Qwen3-VL-Embedding-8B** | **8B** | 67.9 | 58.9 | 77.5 | 72.0 | 55.8 | 4.5 | 28.6 | 81.1 | 65.7 | 69.4 | 75.4 |

## Reranker Performance (for context)

| Model | Size | MMEB-v2 Avg | MMEB-v2 Image | MMEB-v2 Video | MMEB-v2 VisDoc | MMTEB Retrieval | JinaVDR | ViDoRe(v3) |
|-------|------|-------------|---------------|---------------|----------------|-----------------|---------|------------|
| Qwen3-VL-Embedding-2B | 2B | 73.4 | 74.8 | 53.6 | 79.2 | 68.1 | 71.0 | 52.9 |
| jina-reranker-m0 | 2B | - | 68.2 | - | **85.2** | - | 82.2 | 57.8 |
| Qwen3-VL-Reranker-2B | 2B | 75.2 | 74.0 | 53.2 | 83.2 | 70.0 | 80.9 | 60.8 |
| **Qwen3-VL-Reranker-8B** | **8B** | **79.2** | **78.2** | **61.0** | 85.8 | **74.9** | **83.6** | **66.7** |

## Key Takeaways

### Strengths
- **Qwen3-VL-Embedding-8B** leads MMEB-V2 with score of **77.8**, outperforming all competitors including closed-source models
- Strong performance on **visual document retrieval** (VisDoc: 82.4 overall)
- Excellent **image-text retrieval** and **video understanding** capabilities
- Competitive with text-only embedding models on multimodal tasks

### Model Selection Guide

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Maximum accuracy | Qwen3-VL-Embedding-8B | Best scores across all benchmarks |
| Balanced speed/quality | Qwen3-VL-Embedding-2B | 4x fewer params, only ~5pt drop on MMEB-V2 |
| Edge deployment | Qwen3-VL-Embedding-2B + quantization | INT8/INT4 support for smaller footprint |
| Text-heavy retrieval | Consider Qwen3-Embedding-8B (text-only variant) | Better text-only scores than VL variant |

## Reproducing Benchmarks

### MMEB v2 Evaluation

```bash
# 1. Download evaluation data
bash data/evaluation/mmeb_v2/download_data.sh

# 2. Run embedding evaluation
bash scripts/evaluation/mmeb_v2/eval_embedding.sh

# 3. Run reranker evaluation
bash scripts/evaluation/mmeb_v2/eval_reranker.sh
```

## References

- MMEB-V2 Leaderboard: https://huggingface.co/spaces/TIGER-Lab/MMEB-Leaderboard
- MMTEB Leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- JinaVDR: https://huggingface.co/collections/jinaai/jinavdr-visual-document-retrieval
- ViDoRe v3: https://huggingface.co/blog/QuentinJG/introducing-vidore-v3
