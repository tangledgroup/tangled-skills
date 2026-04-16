# Benchmarks and Performance

## Benchmark Results

Qwen3-VL-Reranker models are evaluated on multimodal retrieval benchmarks: **MMEB-v2**, **MMTEB**, **JinaVDR** (visual document retrieval), and **ViDoRe v3**.

### Comparative Performance

| Model | Size | MMEB-v2 Avg | MMEB-v2 Image | MMEB-v2 Video | MMEB-v2 VisDoc | MMTEB | JinaVDR | ViDoRe(v3) |
|-------|------|-------------|---------------|---------------|----------------|-------|---------|------------|
| Qwen3-VL-Embedding-2B | 2B | 73.4 | 74.8 | 53.6 | 79.2 | 68.1 | 71.0 | 52.9 |
| jina-reranker-m0 | 2B | - | 68.2 | - | 85.2 | - | 82.2 | 57.8 |
| **Qwen3-VL-Reranker-2B** | 2B | **75.1** | **73.8** | **52.1** | **83.4** | **70.0** | **80.9** | **60.8** |
| **Qwen3-VL-Reranker-8B** | 8B | **79.2** | **80.7** | **55.8** | **86.3** | **74.9** | **83.6** | **66.7** |

### Key Observations

1. **Reranker > Embedding**: Both reranker variants outperform the base embedding model across all subtasks, confirming the value of the two-stage retrieval approach.
2. **8B dominates**: The 8B model leads in most categories, especially Image (80.7 vs 73.8 on MMEB-v2) and VisDoc (86.3 vs 83.4).
3. **Competitive with jina-reranker-m0**: The 2B variant matches or exceeds jina-reranker-m0 on most metrics, despite being multimodal-capable.
4. **Visual document retrieval strength**: Both models excel at JinaVDR (80.9 and 83.6), making them ideal for scanned PDF/document search.

## Performance Tips

### GPU Memory Estimation (bfloat16)

| Model | VRAM Required | Batch Size (approx.) |
|-------|---------------|---------------------|
| Qwen3-VL-Reranker-2B | ~4–8 GB | 32–64 pairs |
| Qwen3-VL-Reranker-8B | ~16–32 GB | 8–16 pairs |

### Acceleration Strategies

1. **Flash Attention 2**: Enable `attn_implementation="flash_attention_2"` for both memory savings and speedup (native Transformers API).
2. **Batch scoring**: Process multiple (query, document) pairs in a single forward pass via the Sentence Transformers `CrossEncoder.predict()` method.
3. **vLLM pooling runner**: For production serving, use vLLM's pooling mode with `runner="pooling"` for high-throughput inference.
4. **bfloat16 dtype**: Always prefer bfloat16 over float32 for reduced memory and faster compute on modern GPUs.

### Latency Considerations

- The 8B model is roughly 3–5× slower than the 2B variant per query-document pair.
- Multimodal documents (text + image) add ~20–40% overhead vs text-only due to vision encoder processing.
- Video documents are significantly more expensive; control cost with the `fps` parameter.
