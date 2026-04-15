# Qwen3 Embedding Model Variants

Detailed comparison and selection guide for the three Qwen3 Embedding model variants: 0.6B, 4B, and 8B.

## Model Overview

| Variant | Parameters | Download Size | Context Length | License | Downloads |
|---------|------------|---------------|----------------|---------|-----------|
| **0.6B** | ~600M | ~1.2 GB | 32K | Apache 2.0 | 6M+ |
| **4B** | ~4B | ~8 GB | 32K | Apache 2.0 | 1.8M+ |
| **8B** | ~8B | ~16 GB | 32K | Apache 2.0 | 10M+ |

## Detailed Comparison

### Qwen3-Embedding-0.6B

**Best for**: Edge deployment, mobile applications, real-time search with strict latency requirements

**Strengths**:
- Fastest inference speed (~5-10x faster than 8B)
- Lowest memory footprint (can run on CPU with <4GB RAM)
- Suitable for batch processing at scale
- Good baseline quality for general-domain tasks

**Limitations**:
- Lower performance on complex semantic understanding
- Reduced multilingual capabilities compared to larger variants
- May struggle with domain-specific terminology

**Recommended Hardware**:
- CPU: Modern multi-core CPU (8+ cores recommended)
- GPU: Any modern GPU with 4GB+ VRAM
- Memory: 4-8 GB RAM minimum

**Typical Latency** (single query):
- CPU: 50-150ms
- GPU (T4): 5-15ms
- GPU (A100): 2-5ms

### Qwen3-Embedding-4B

**Best for**: Production search systems, RAG applications, balanced performance requirements

**Strengths**:
- Optimal balance of quality and speed
- Strong multilingual support
- Good performance on domain-specific tasks
- Reasonable resource requirements

**Limitations**:
- May require GPU for real-time applications
- Larger memory footprint than 0.6B

**Recommended Hardware**:
- CPU: High-end multi-core (16+ cores for batch)
- GPU: Modern GPU with 8GB+ VRAM recommended
- Memory: 8-16 GB RAM minimum

**Typical Latency** (single query):
- CPU: 200-500ms
- GPU (T4): 20-40ms
- GPU (A100): 8-15ms

### Qwen3-Embedding-8B

**Best for**: Maximum quality requirements, high-stakes domains, batch processing where latency is not critical

**Strengths**:
- Highest embedding quality across all benchmarks
- Best multilingual and cross-lingual performance
- Superior semantic understanding for complex queries
- State-of-the-art reranking capabilities

**Limitations**:
- Highest resource requirements
- Slower inference (may not suit real-time mobile)
- Larger storage footprint

**Recommended Hardware**:
- CPU: Not recommended for production (very slow)
- GPU: High-end GPU with 16GB+ VRAM (A100, H100, RTX 3090/4090)
- Memory: 16-32 GB RAM minimum

**Typical Latency** (single query):
- CPU: 1-3 seconds
- GPU (T4): 80-150ms
- GPU (A100): 25-50ms

## Benchmark Comparison

### MTEB Leaderboard Results (Selected Tasks)

| Task | 0.6B | 4B | 8B | Leader |
|------|------|----|----|--------|
| **STS (Semantic Text Similarity)** | 72.5 | 78.3 | 81.2 | 82.1 |
| **Retrieval (English)** | 68.4 | 74.9 | 78.6 | 79.2 |
| **Retrieval (Multilingual)** | 62.1 | 71.8 | 76.3 | 77.0 |
| **Clustering** | 65.8 | 72.4 | 75.9 | 76.5 |
| **Classification** | 78.2 | 82.6 | 85.1 | 85.8 |
| **Reranking** | 70.3 | 76.8 | 80.4 | 81.0 |

*Scores are approximate MTEB averages; check official leaderboard for latest results*

### Efficiency Metrics

| Metric | 0.6B | 4B | 8B |
|--------|------|----|----|
| **Throughput (queries/sec, GPU)** | 150-200 | 60-100 | 20-40 |
| **Memory (FP16, GB)** | 1.5 | 8.0 | 16.0 |
| **Memory (INT8, GB)** | 0.8 | 4.0 | 8.0 |
| **Disk Size (GB)** | 1.2 | 8.0 | 16.0 |

## Selection Decision Tree

```
Need embedding model?
│
├─ Running on edge/mobile device?
│  └─ Use 0.6B
│
├─ Real-time search with <50ms latency requirement?
│  ├─ GPU available?
│  │  ├─ Yes → Use 0.6B or 4B (depending on quality needs)
│  │  └─ No → Use 0.6B
│  │
├─ High-stakes domain (legal, medical, financial)?
│  └─ Use 8B (quality critical)
│
├─ Multilingual application?
│  ├─ 2-3 languages → Use 4B
│  └─ 10+ languages → Use 8B
│
├─ RAG pipeline?
│  ├─ Retrieval stage → Use 4B (balanced)
│  └─ Reranking stage → Use 4B or 8B (accuracy critical)
│
└─ Default production use?
   └─ Use 4B (best balance)
```

## Cost Considerations

### Cloud Inference Costs (Estimated)

Using cloud GPU instances for serving:

| Model | Instance Type | Cost/hr | Queries/hr | Cost per 1K queries |
|-------|---------------|---------|------------|---------------------|
| 0.6B | t3.large (CPU) | $0.08 | 20K | $0.004 |
| 0.6B | g4dn.xlarge (T4) | $0.52 | 150K | $0.003 |
| 4B | g4dn.xlarge (T4) | $0.52 | 80K | $0.006 |
| 4B | g5.xlarge (A10G) | $0.70 | 120K | $0.006 |
| 8B | g5.2xlarge (A10G) | $1.40 | 50K | $0.028 |
| 8B | p3.2xlarge (V100) | $3.00 | 80K | $0.038 |

*Costs are approximate and vary by provider and region*

### Self-Hosting Considerations

**0.6B**:
- Can run on single CPU server ($50-100/mo VPS)
- Suitable for small to medium traffic (<10K queries/day)

**4B**:
- Requires GPU server or cloud GPU ($200-500/mo)
- Suitable for medium to large traffic (10K-100K queries/day)

**8B**:
- Requires high-end GPU ($500-2000/mo depending on specs)
- Suitable for large-scale applications (100K+ queries/day) or batch processing

## Migration Paths

### Upgrading from 0.6B to 4B

```python
# Simple swap - same API
from sentence_transformers import SentenceTransformer

# Old
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

# New
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
```

**Expected improvements**:
- 8-12% better retrieval quality
- 15-20% better multilingual performance
- 3-5x slower inference (mitigate with GPU)

### Upgrading from 4B to 8B

**Expected improvements**:
- 5-8% better retrieval quality
- 10-15% better multilingual performance
- 2-3x slower inference

**Considerations**:
- Ensure sufficient GPU memory (16GB+ recommended)
- May need to reduce batch size
- Consider quantization for memory efficiency

## A/B Testing Recommendations

When evaluating model variants:

1. **Define metrics**: MRR@10, NDCG@10, latency p95, cost per query
2. **Run parallel**: Serve both models simultaneously to subset of traffic
3. **Measure offline**: Evaluate on held-out test set with ground truth
4. **Monitor online**: Track user engagement, click-through rates
5. **Consider hybrid**: Use smaller model for retrieval, larger for reranking

Example A/B test setup:

```python
from sentence_transformers import SentenceTransformer
import random

# Load both models
model_small = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
model_large = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

def search(query, corpus, embeddings_small, embeddings_large, top_k=5):
    # Random assignment for A/B test
    if random.random() < 0.5:
        model = model_small
        embeddings = embeddings_small
        variant = "A"
    else:
        model = model_large
        embeddings = embeddings_large
        variant = "B"
    
    query_emb = model.encode(query, normalize_embeddings=True)
    similarities = embeddings @ query_emb
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    return {
        "results": [(corpus[i], similarities[i].item()) for i in top_indices],
        "variant": variant
    }
```

## See Also

- [`references/02-architecture.md`](02-architecture.md) - Technical architecture details
- [`references/10-optimization.md`](10-optimization.md) - Performance optimization techniques
- [`references/09-deployment-tei.md`](09-deployment-tei.md) - Production deployment with TEI
