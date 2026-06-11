# Hybrid Search Architecture

## Triple-Stream Retrieval

agentmemory combines three retrieval signals fused with Reciprocal Rank Fusion (RRF, k=60):

| Stream | What it does | When active |
|--------|-------------|-------------|
| **BM25** | Stemmed keyword matching with synonym expansion | Always on |
| **Vector** | Cosine similarity over dense embeddings | Embedding provider configured |
| **Graph** | Knowledge graph traversal via entity matching | Entities detected in query |

Results are session-diversified (max 3 results per session) to avoid single-session dominance.

## BM25 Index

- Porter stemming for English terms
- Synonym expansion from extracted concepts
- Always available — no external dependencies
- Baseline recall: ~86% R@5 on LongMemEval-S

## Vector Embeddings

6 embedding providers supported, auto-detected from environment:

| Provider | Model | Cost | Notes |
|----------|-------|------|-------|
| **Local (recommended)** | `all-MiniLM-L6-v2` | Free | Offline, +8pp recall over BM25-only |
| Gemini | `text-embedding-004` | Free tier | 1500 RPM |
| OpenAI | `text-embedding-3-small` | $0.02/1M | Highest quality |
| Voyage AI | `voyage-code-3` | Paid | Optimized for code |
| Cohere | `embed-english-v3.0` | Free trial | General purpose |
| OpenRouter | Any model | Varies | Multi-model proxy |

Install local embeddings: `npm install @xenova/transformers`

OpenAI-compatible providers (Azure, vLLM, LM Studio) supported via `OPENAI_BASE_URL`, `OPENAI_EMBEDDING_MODEL`, and `OPENAI_EMBEDDING_DIMENSIONS` environment variables. Model dimensions auto-derived for known models (3-small=1536, 3-large=3072, ada-002=1536).

## Knowledge Graph

Entity extraction identifies named entities (files, functions, libraries, patterns) from observations. The graph supports BFS traversal for multi-hop reasoning — e.g., finding all files that depend on a specific authentication module.

Graph extraction runs at session end when `GRAPH_EXTRACTION_ENABLED=true`. In v0.9.4, the auto-fire bug was fixed so enabling the flag actually populates the graph without manual REST calls.

## Fusion and Ranking

Reciprocal Rank Fusion combines ranked lists from active streams:

- RRF formula: `score = sum(1 / (k + rank_stream))` for each document across streams
- Default k=60
- BM25 weight: 0.4, Vector weight: 0.6 (configurable via `BM25_WEIGHT` and `VECTOR_WEIGHT`)
- Token budget limits injected context (default 2000 tokens, configurable via `TOKEN_BUDGET`)

## Search Tools

Primary search tools for agents:

- `memory_smart_search` — hybrid semantic + keyword search (recommended)
- `memory_recall` — search past observations
- `memory_file_history` — past observations about specific files
- `memory_graph_query` — knowledge graph traversal (extended tools)
- `memory_facet_query` — query by dimension:value facet tags (extended tools)
