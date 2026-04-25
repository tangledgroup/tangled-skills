---
name: chonkie-1-6-4
description: Lightweight text chunking library for fast, efficient RAG pipelines. Provides 12+ chunkers (token, sentence, recursive, semantic, code, late, neural, slumber, fast, table, SDPM, teraflopai), pipeline API, refineries, vector DB handshakes, and a self-hosted REST API. Use when building document ingestion pipelines for RAG, splitting text into embeddings-ready chunks, or processing code, tables, and structured documents.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - chunking
  - rag
  - nlp
  - text-processing
  - python
  - javascript
category: libraries
external_references:
  - https://github.com/chonkie-inc/chonkie/tree/v1.6.4/docs
  - https://docs.chonkie.ai
  - https://github.com/chonkie-inc/chonkie
  - https://github.com/chonkie-inc/chonkie/releases
  - https://huggingface.co/datasets/chonkie-ai/recipes
  - https://pypi.org/project/chonkie/
  - https://github.com/chonkie-inc/chonkie/tree/v1.6.4
  - https://docs.chonkie.ai/common/open-source
---

# Chonkie 1.6.4

## Overview

Chonkie is a lightweight text chunking library designed for fast, efficient, and robust RAG pipelines. It provides multiple chunking strategies (12+ chunkers), a fluent Pipeline API, refineries for post-processing, and direct integrations with 10+ vector databases. Available in both Python and JavaScript/TypeScript.

Key characteristics:
- **Simple**: Install, import, chunk — minimal setup
- **Fast**: SIMD-accelerated chunking at 100+ GB/s (FastChunker)
- **Lightweight**: 505KB wheel, 49MB installed (vs 80-171MB for alternatives)
- **Flexible**: Modular optional installs, custom tokenizers, recipe-based configuration

## When to Use

Use this skill when:
- Building document ingestion pipelines for RAG applications
- Splitting text into embeddings-ready chunks
- Processing code files, tables, or structured documents
- Setting up a self-hosted chunking REST API
- Integrating chunking output with vector databases (ChromaDB, Qdrant, Pinecone, etc.)
- Need async chunking in web frameworks (FastAPI, aiohttp, Starlette)

## Core Concepts

### Chunking Principles

An ideal chunk is:
- **Reconstructable**: Combining chunks gives back the original text
- **Independent**: Each chunk stands alone as a meaningful unit
- **Sufficient**: Long enough to be useful for retrieval

### CHOMP Architecture

Chonkie's pipeline follows a standardized flow:

```
Fetcher → Chef → Chunker → Refinery → Porter/Handshake
```

Pipelines automatically reorder components to follow this order regardless of how they are chained.

### Unified Types (v1.3.0+)

All chunkers return the base `Chunk` type:

```python
@dataclass
class Chunk:
    text: str
    start_index: int
    end_index: int
    token_count: int
    context: Optional[Context] = None
    embedding: Union[list[float], "np.ndarray", None] = None
```

### Common Interface

All chunkers share the same API:

```python
# Single text
chunks = chunker.chunk(text)

# Batch processing
chunks = chunker.chunk_batch(texts)

# Direct calling
chunks = chunker(text)

# Async variants
chunks = await chunker.achunk(text)
chunks = await chunker.achunk_batch(texts)
```

## Installation

### Python

```bash
# Basic (Token, Sentence, Recursive, Fast, Table chunkers)
pip install chonkie

# With semantic capabilities
pip install "chonkie[semantic]"

# All features
pip install "chonkie[all]"
```

See [Reference: Installation](references/02-installation.md) for all optional extras.

### JavaScript

```bash
npm install @chonkiejs/core    # Local chunking
npm install @chonkiejs/cloud   # API access
npm install @chonkiejs/token   # Custom tokenizers
```

## Quick Start

```python
from chonkie import RecursiveChunker

chunker = RecursiveChunker(chunk_size=512)

text = "Your document text here..."
chunks = chunker(text)

for chunk in chunks:
    print(f"Chunk: {chunk.text[:50]}...")
    print(f"Tokens: {chunk.token_count}")
```

## Advanced Topics

- [Reference: Chunkers](references/01-chunkers.md) — All 12 chunkers with parameters and examples
- [Reference: Installation](references/02-installation.md) — Optional extras, dependencies, chunker availability
- [Reference: Pipelines](references/03-pipelines.md) — CHOMP architecture, fetchers, chefs, porters
- [Reference: Embeddings](references/04-embeddings.md) — 10+ embedding providers and AutoEmbeddings
- [Reference: Handshakes](references/05-handshakes.md) — Vector database integrations (ChromaDB, Qdrant, etc.)
- [Reference: API Server](references/06-api-server.md) — Self-hosted REST API with Docker

## Version Notes (1.6.2 → 1.6.4)

- **v1.6.3**: Added LanceDB handshake, TeraflopAI chunker, HTML table support via TableChef/TableChunker, metadata `filename` field
- **v1.6.4**: Fixed pandas import error (`ModuleNotFoundError: No module named 'pandas'`) when installed without `[table]` extra — pandas now lazy-loaded

