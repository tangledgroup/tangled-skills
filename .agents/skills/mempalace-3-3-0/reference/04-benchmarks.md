# Benchmarks

| Benchmark | Mode | Score | API Calls |
|-----------|------|-------|-----------|
| LongMemEval R@5 | Raw (ChromaDB only) | **96.6%** | Zero |
| LongMemEval R@5 | Hybrid + Haiku rerank | **100%** (500/500) | ~500 |
| LoCoMo R@10 | Raw, session level | 60.3% | Zero |
| Personal palace R@10 | Heuristic bench | 85% | Zero |
| Palace structure impact | Wing+room filtering | **+34%** R@10 | Zero |

**Structure improvement:**
- Search all closets: 60.9% R@10
- Search within wing: 73.1% (+12%)
- Search wing + hall: 84.8% (+24%)
- Search wing + room: 94.8% (+34%)
