# Handshakes

> **Source:** https://docs.chonkie.ai/oss/handshakes/overview
> **Loaded from:** SKILL.md (via progressive disclosure)

Handshakes connect Chonkie directly to vector databases. Embed chunks and write them in a few lines of code.

## Available Handshakes

- **ChromaDB** (`chroma`) — Ephemeral or persistent ChromaDB instances
- **Qdrant** (`qdrant`) — High-performance vector search
- **Weaviate** (`weaviate`) — Knowledge graph + vector search
- **Pinecone** (`pinecone`) — Managed vector database
- **pgvector** (`pgvector`) — PostgreSQL with pgvector extension
- **MongoDB** (`mongodb`) — MongoDB Atlas Vector Search
- **Elasticsearch** (`elastic`) — Elasticsearch vector search
- **Turbopuffer** (`tpuf`) — Serverless vector database
- **LanceDB** (`lancedb`) — Local or cloud LanceDB table (added v1.6.3)
- **Milvus** (`milvus`) — Milvus collection

## Usage In Pipelines

```python
from chonkie import Pipeline

# ChromaDB
doc = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .store_in("chroma", collection_name="documents")
    .run(texts="Your text here"))

# Qdrant
doc = (Pipeline()
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .store_in("qdrant", collection_name="docs", url="http://localhost:6333")
    .run(texts="Your text here"))
```

## Usage As Standalone

```python
from chonkie import RecursiveChunker, ChromaHandshake

chunker = RecursiveChunker(chunk_size=512)
handshake = ChromaHandshake(collection_name="my_docs")

chunks = chunker(text)
handshake.store(chunks)
```

## Installation

Each handshake requires its own extra:

```bash
pip install "chonkie[chroma]"
pip install "chonkie[qdrant]"
pip install "chonkie[pinecone]"
pip install "chonkie[pgvector]"
pip install "chonkie[mongodb]"
pip install "chonkie[elastic]"
pip install "chonkie[weaviate]"
pip install "chonkie[tpuf]"
```

Or install all features:

```bash
pip install "chonkie[all]"
```

## Handshake With Embeddings

Most handshakes work best with embeddings attached to chunks. Use `EmbeddingsRefinery` or a chunker that produces embeddings (LateChunker):

```python
doc = (Pipeline()
    .chunk_with("semantic", threshold=0.8)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("pinecone", index_name="documents")
    .run(texts="Text to chunk and store"))
```
