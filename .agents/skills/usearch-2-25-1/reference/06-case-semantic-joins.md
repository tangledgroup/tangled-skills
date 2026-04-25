# Case Study: Semantic Joins via Stable Marriages

> **Source:** https://ashvardanian.com/posts/searching-stable-marriages/
> **Loaded from:** SKILL.md (via progressive disclosure)

## Problem

The classic Gale–Shapley Stable Marriage algorithm requires complete preference lists. With 1 billion candidates per person, you would need 8 million terabytes of RAM — practically infeasible ($80 billion at $10K/TB).

USearch solves this by replacing stored preference lists with **dynamically computed** candidate rankings using vector search. Instead of pre-computing and storing every ranking, it encodes all profiles into vectors, builds two kANN indexes, and generalizes Stable Marriages over those indexes.

## Approach

1. Encode all profiles (men and women) using a single neural network into vectors
2. Build two separate USearch HNSW indexes — one for each set
3. Execute `Index.join()` to find stable pairings without materializing full preference lists

```python
from usearch.index import Index

men = Index(ndim=768, metric='cos')
women = Index(ndim=768, metric='cos')

# Populate both indexes with encoded profiles...
# ...

couples = men.join(women, max_proposals=100, exact=False)
```

Passing `max_proposals=0` lets USearch auto-estimate the stopping criterion. For evaluation across datasets of different sizes, hard-coding `max_proposals=100` reduces variance.

The full implementation uses multiple concurrent bitsets for synchronization.

## Key Insight: Trade Compute for Memory

Instead of storing O(n²) preference lists, USearch recalculates candidates on-the-fly during graph traversal. This is a space-time tradeoff — you compensate memory with compute.

Limit proposals per person to approximately `log(len(men)) + cpu_count()` and use this as the termination criterion.

## Uni-Modal Results (Text-to-Text: Arxiv Titles ↔ Abstracts)

Using e5-base-v2 embeddings (768-dimensional) on the Arxiv dataset (~2M entries):

| Metric | 10K | 100K | 1M |
|--------|-----|------|-----|
| Pair Quality | 0.8754 | 0.8754 | 0.8768 |
| Self-Recall A@10 | 99.98% | 99.96% | 99.85% |
| Cross-Recall A in T@10 | 94.78% | 86.49% | 76.98% |
| Joined Correctly | 87.85% | 70.47% | 57.67% |

Downcasting from `f32` to `i8` had barely noticeable accuracy loss while tripling construction and search/join speed.

## Multi-Modal Results (Image ↔ Text: Creative Captions)

Multi-modal alignment is significantly harder. Using Open CLIP ViT-B-16 on 3M image-text pairs:

| Metric | 10K | 100K | 1M |
|--------|-----|------|-----|
| Pair Quality | 0.2565 | 0.2565 | 0.2566 |
| Cross-Recall I in T@10 | 71.31% | 47.31% | 24.56% |
| Joined Correctly | 43.50% | 22.91% | **9.02%** |

Even with a larger CLIP ViT-G/14 (2B parameters), correct joins only reached 13.46% at 1M scale. This demonstrates that current multi-modal alignment techniques are far from satisfactory for join operations.

## Applications

- Job matching platforms
- Targeted advertising systems
- Database fuzzy-matching (semantic joins)
- Content recommendation across modalities

## When to Use Joins

Use `Index.join()` when:
- You need one-to-one or many-to-many fuzzy mappings between two datasets
- Traditional exact joins are too slow at scale
- Both sets can be encoded into a shared vector space
- You want sub-quadratic complexity for approximate matching

## Performance Notes

- Small collections (< 1M vectors, fitting in CPU cache): 500K+ queries/sec
- Billion-scale entries: ~1K queries/sec
- Reduce embedding dimensions and JIT the distance function to optimize further
- Use `i8` quantization for 3x speedup with minimal accuracy loss
