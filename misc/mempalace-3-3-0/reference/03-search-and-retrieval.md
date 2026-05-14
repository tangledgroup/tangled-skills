# Search and Retrieval

## Overview

MemPalace uses hybrid search combining BM25 keyword matching with ChromaDB vector semantic similarity. The drawer query is always the floor — it always runs — and closet hits add a rank-based boost when they agree. Closets are a ranking signal, never a gate.

## CLI Search

```bash
mempalace search "why did we switch to GraphQL"
mempalace search "pricing discussion" --wing my_app --room costs
```

Returns verbatim drawer content with similarity scores. Optional filters: `--wing`, `--room`, `--results N`.

## Programmatic Search

```python
from mempalace.searcher import search_memories

results = search_memories(
    query="auth decisions",
    palace_path="~/.mempalace/palace",
    wing="my_app",
    room="auth-migration",
    n_results=5,
    max_distance=0.8,  # filter weak matches (0 = identical, 2 = opposite)
)
```

Returns a dict with `text`, `wing`, `room`, `source_file`, `similarity`, `matched_via` (closet or drawer), and optional `closet_preview`.

## Hybrid Search Algorithm

Three stages:

**Stage 1 — Vector retrieval:** Query ChromaDB with the question text. Retrieve top-N×3 candidates (over-fetch for re-ranking). Uses cosine distance (`hnsw:space=cosine`).

**Stage 2 — BM25 re-ranking:** Real Okapi-BM25 with corpus-relative IDF over the candidates. Fused score:

```
fused_score = vector_weight × vec_sim + bm25_weight × bm25_norm
```

Default weights: vector=0.6, BM25=0.4. Min-max normalized within candidate set so weights are commensurable.

**Stage 3 — Closet boost:** Query closets collection separately. Best-per-source closet hits provide rank-based distance reduction:

- Rank 1 closet hit: 0.40 distance reduction
- Rank 2: 0.25
- Rank 3: 0.15
- Rank 4: 0.08
- Rank 5: 0.04

Cosine distance > 1.5 is too weak to use as signal. If no closets exist or all filtered out, search falls back to direct drawer search.

## Closet-First Retrieval

Closets are short text documents (max 1,500 chars each). Search queries them first because they are fast to scan:

```
Query → search mempalace_closets (fast, small documents)
         ↓
    top closet hits → parse →drawer_id_a,drawer_id_b pointers
         ↓
    fetch exactly those drawers from mempalace_drawers (verbatim content)
         ↓
    apply max_distance filter
         ↓
    return chunk-level results
```

Closet extraction limits: 5,000 char scan window per file, max 12 topics, max 3 quotes, max 5 entities per pointer.

## Drawer-Grep Context

When a closet hit returns one drawer, the chunk boundary may clip mid-thought. The `_expand_with_neighbors` function fetches ±N sibling chunks in the same source file to provide context without forcing a follow-up call.

## Wing/Room Filtering

ChromaDB `where` filters narrow search scope:

- Wing only: `{"wing": wing}`
- Room only: `{"room": room}`
- Both: `{"$and": [{"wing": wing}, {"room": room}]}`

## 4-Layer Memory Stack

**Layer 0 — Identity** (~50-100 tokens, always loaded):
Reads `~/.mempalace/identity.txt` — a plain-text file the user writes describing who the AI is and what it focuses on.

```python
from mempalace.layers import Layer0
layer = Layer0()  # reads ~/.mempalace/identity.txt
text = layer.render()
```

**Layer 1 — Essential Story** (~500-800 tokens, always loaded):
Auto-generated from the highest-weight drawers in the palace. Scores by `importance`/`emotional_weight`/`weight` metadata, takes top-15, groups by room. Hard cap: 3,200 chars (~800 tokens).

```python
from mempalace.layers import Layer1
layer = Layer1(palace_path="~/.mempalace/palace")
text = layer.generate()
```

**Layer 2 — On-Demand** (~200-500 tokens per retrieval):
Loaded when a specific topic or wing comes up. Queries ChromaDB with wing/room filter.

```python
from mempalace.layers import Layer2
layer = Layer2()
text = layer.retrieve(wing="my_app", room="auth-migration")
```

**Layer 3 — Deep Search** (unlimited):
Full semantic search against the entire palace. Reuses `searcher.py` logic.

```python
from mempalace.layers import Layer3
layer = Layer3()
text = layer.search("auth decisions", wing="my_app")
```

**Wake-up cost:** `mempalace wake-up` outputs L0 + L1 (~600-900 tokens), leaving 95%+ of context free.

```bash
mempalace wake-up > context.txt       # full palace
mempalace wake-up --wing my_app        # specific project
```

## Query Sanitization

The `query_sanitizer.py` module mitigates system prompt contamination in search queries. Prevents injected instructions from affecting retrieval.

## Distance Thresholds

Cosine distance in ChromaDB: 0 = identical, 2 = opposite vectors. Typical useful filtering range: 0.3-1.0. The `max_distance` parameter in `search_memories` filters results above the threshold. A value of 0.0 disables filtering.
