# Benchmarks and Comparison

## LongMemEval-S Results

ICLR 2025 benchmark: 500 questions, ~115K tokens each.

| System | R@5 | R@10 | MRR |
|--------|-----|------|-----|
| **agentmemory** | **95.2%** | **98.6%** | **88.2%** |
| BM25-only fallback | 86.2% | 94.6% | 71.5% |

## Token Savings

| Approach | Tokens/yr | Cost/yr |
|----------|-----------|---------|
| Paste full context | 19.5M+ | Impossible (exceeds window) |
| LLM-summarized | ~650K | ~$500 |
| **agentmemory** | **~170K** | **~$10** |
| agentmemory + local embeddings | ~170K | **$0** |

Embedding model: `all-MiniLM-L6-v2` (local, free, no API key).

## vs Built-in Agent Memory

| | Built-in (CLAUDE.md) | agentmemory |
|---|---|---|
| Scale | 200-line cap | Unlimited |
| Search | Loads everything into context | BM25 + vector + graph (top-K only) |
| Token cost | 22K+ at 240 observations | ~1,900 tokens (92% less) |
| Cross-agent | Per-agent files | MCP + REST (any agent) |
| Coordination | None | Leases, signals, actions, routines |
| Observability | Read files manually | Real-time viewer on :3113 |

## Test Coverage

827 tests passing (as of v0.9.4).
