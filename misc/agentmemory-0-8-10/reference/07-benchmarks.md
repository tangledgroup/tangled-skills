# Benchmarks and Comparison

## LongMemEval-S Results

[LongMemEval](https://arxiv.org/abs/2410.10813) (ICLR 2025) measures long-term memory retrieval across ~48 sessions per question on the S variant (500 questions, ~115K tokens each). Metric: `recall_any@K` — does any gold session appear in top-K retrieved results?

| System | R@5 | R@10 | R@20 | NDCG@10 | MRR |
|---|---|---|---|---|---|
| **agentmemory BM25+Vector** | **95.2%** | **98.6%** | **99.4%** | **87.9%** | **88.2%** |
| agentmemory BM25-only | 86.2% | 94.6% | 98.6% | 73.0% | 71.5% |
| MemPalace raw (vector-only) | 96.6% | ~97.6% | — | — | — |

### By Question Type (BM25+Vector)

| Type | R@5 | R@10 | Count |
|---|---|---|---|
| knowledge-update | 98.7% | 100.0% | 78 |
| multi-session | 97.7% | 100.0% | 133 |
| single-session-assistant | 96.4% | 98.2% | 56 |
| temporal-reasoning | 95.5% | 97.7% | 133 |
| single-session-user | 90.0% | 97.1% | 70 |
| single-session-preference | 83.3% | 96.7% | 30 |

### Key Findings

- BM25+Vector (95.2%) nearly matches pure vector search (96.6%) with only a 1.4pp gap
- BM25 alone gets 86.2% — keyword search is surprisingly effective on conversational data
- Adding vectors to BM25 gives +9pp, the largest improvement from any single component
- Preferences are the hardest category for both BM25 (60%) and hybrid (83.3%)
- Multi-session and knowledge-update are strongest (97.7%+ hybrid)

### Methodology Notes

These are retrieval recall scores, not end-to-end QA accuracy. The official LongMemEval metric is QA accuracy (retrieve + generate answer + GPT-4o judge). Each question builds a fresh index from its ~48 sessions, searches with the question text, and checks if gold session IDs appear in results.

## Token Efficiency

| Approach | Tokens / year | Cost / year |
|---|---|---|
| Paste full history into context | 19.5M+ | Impossible (exceeds window) |
| LLM-summarized memory | ~650K | ~$500 |
| **agentmemory (API embeddings)** | **~170K** | **~$10** |
| **agentmemory (local embeddings)** | **~170K** | **$0** |

## Comparison with Competitors

| Feature | agentmemory | mem0 | Letta/MemGPT | Khoj | claude-mem | Hippo |
|---|---|---|---|---|---|---|
| **Type** | Memory engine + MCP server | Memory layer API | Full agent runtime | Personal AI | MCP server | Memory system |
| **Auto-capture** | 12 lifecycle hooks | Manual add() calls | Agent self-edits | Manual | Limited | Manual |
| **Search** | BM25 + Vector + Graph | Vector + Graph | Vector (archival) | Semantic | FTS5 | Decay-weighted |
| **Multi-agent** | Leases + signals + mesh | API (no coordination) | Runtime-internal only | No | No | Shared |
| **Framework lock-in** | None (any MCP client) | None | High | Standalone | Claude Code | None |
| **External deps** | None (SQLite + iii-engine) | Qdrant / pgvector | Postgres + vector DB | Multiple | SQLite | None |
| **Self-hostable** | Yes (default) | Optional | Optional | Yes | Yes | Yes |
| **Knowledge graph** | Entity extraction + BFS | Mem0g variant | No | Doc links | No | No |
| **Memory decay** | Ebbinghaus + tiered | No | No | No | No | Half-lives |
| **4-tier consolidation** | Working → episodic → semantic → procedural | No | OS-inspired tiers | No | No | Episodic + semantic |
| **Privacy filtering** | Strips secrets pre-store | No | No | No | No | No |
| **Real-time viewer** | Port 3113 | Cloud dashboard | Cloud dashboard | Web UI | No | No |
| **Audit trail** | All mutations logged | No | Limited | No | No | No |

### Retrieval Accuracy Comparison

| System | Benchmark | R@5 | Notes |
|---|---|---|---|
| **agentmemory** (BM25 + Vector) | LongMemEval-S | **95.2%** | all-MiniLM-L6-v2, no API key |
| agentmemory (BM25-only) | LongMemEval-S | 86.2% | Fallback mode |
| MemPalace | LongMemEval-S | ~96.6% | Vector-only, bigger model |
| Letta / MemGPT | LoCoMo | 83.2% | Different benchmark |
| Mem0 | LoCoMo | 68.5% | Different benchmark |

**Apples vs oranges caveat:** agentmemory and MemPalace measured on LongMemEval-S. Letta and Mem0 publish on LoCoMo, a different benchmark.

## Running Benchmarks Locally

```bash
git clone https://github.com/rohitg00/agentmemory.git
cd agentmemory && npm install

# Run LongMemEval-S
npm run bench:longmemeval

# Run quality benchmark (240 observations, 20 queries)
npm run bench:quality

# Run scale benchmark
npm run bench:scale
```

Results land in `benchmark/results/`. All scripts, datasets, and results are committed for reproducibility.
