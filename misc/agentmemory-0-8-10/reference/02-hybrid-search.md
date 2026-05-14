# Hybrid Search Architecture

## Triple-Stream Retrieval

agentmemory uses three independent retrieval streams fused with Reciprocal Rank Fusion (RRF, k=60):

| Stream | What it does | When active |
|---|---|---|
| **BM25** | Stemmed keyword matching with synonym expansion | Always on |
| **Vector** | Cosine similarity over dense embeddings | Embedding provider configured |
| **Graph** | Knowledge graph traversal via entity matching | Entities detected in query + `GRAPH_EXTRACTION_ENABLED=true` |

Results are session-diversified: max 3 results per session to avoid clustering.

## RRF Fusion Formula

```
combinedScore = w_bm25 * (1 / (RRF_K + bm25Rank))
              + w_vector * (1 / (RRF_K + vectorRank))
              + w_graph * (1 / (RRF_K + graphRank))
```

Weights default to BM25=0.4, Vector=0.6, Graph=0.3. Weights are normalized so active streams sum to 1.0 — if vector search is unavailable, BM25 gets its full weight. If neither vector nor graph results exist, BM25 alone determines ranking.

## Query Expansion

When enabled, the search expands the original query with:
- **Reformulations** — LLM-generated alternative phrasings
- **Temporal concretizations** — date/time-specific variants
- **Entity extractions** — named entities pulled from the query

Each expanded query runs its own triple-stream search, and results are merged by highest combined score.

## Knowledge Graph

The knowledge graph is built through entity extraction from observations:

```xml
<entity type="concept" name="JWT Authentication">
  <property key="category">security</property>
</entity>
<relationship type="uses" source="Rate Limiter" target="JWT Authentication" weight="0.8"/>
```

Graph retrieval uses BFS traversal from matched entities, with expansion from top vector results. Graph search is best-effort — failures don't block the overall search.

## Embedding Providers

agentmemory auto-detects embedding providers from environment variables:

| Provider | Env Var | Model | Dimensions | Cost |
|---|---|---|---|---|
| **Local** (recommended) | `EMBEDDING_PROVIDER=local` | `all-MiniLM-L6-v2` | 384 | Free, offline |
| Gemini | `GEMINI_API_KEY` | `text-embedding-004` | 768 | Free tier, 1500 RPM |
| OpenAI | `OPENAI_API_KEY` | `text-embedding-3-small` | 1536 | $0.02/1M tokens |
| Voyage AI | `VOYAGE_API_KEY` | `voyage-code-3` | Varies | Paid, code-optimized |
| Cohere | `COHERE_API_KEY` | `embed-english-v3.0` | 1024 | Free trial |
| OpenRouter | `OPENROUTER_API_KEY` | Any model | Varies | Multi-model proxy |

Local embeddings require `@xenova/transformers` (optional dependency):

```bash
npm install @xenova/transformers
```

## Search Results Structure

Each result includes scores from all active streams:

```typescript
interface HybridSearchResult {
  observation: CompressedObservation;
  bm25Score: number;
  vectorScore: number;
  graphScore: number;
  combinedScore: number;
  sessionId: string;
  graphContext?: string;  // contextual info from graph neighbors
}
```

## Performance Characteristics

- **BM25-only baseline**: 86.2% R@5 on LongMemEval-S
- **BM25 + Vector**: 95.2% R@5 (+9pp improvement from adding vectors)
- **R@10**: 98.6% — nearly all gold sessions found in top 10
- **Preferences** are the hardest category (83.3% hybrid, 60% BM25-only)
- **Multi-session and knowledge-update** are strongest (97.7%+ hybrid)

## Smart Search vs Recall

`memory_smart_search` uses the full triple-stream pipeline with optional query expansion. `memory_recall` uses BM25 search with substring matching as a simpler fallback. In the standalone MCP shim (no engine), both fall back to substring filtering since BM25/vector/graph require the full iii-engine runtime.

## Token Budget

Context injection respects `TOKEN_BUDGET` (default: 2000 tokens). The context function fills the budget with the highest-scoring observations, prioritizing recency and importance. Context blocks are typed as summary, observation, or memory, each carrying token count and recency score for budget allocation decisions.
