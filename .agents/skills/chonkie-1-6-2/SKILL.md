---
name: chonkie-1-6-2
description: A skill for using Chonkie 1.6.2, a lightweight Rust-based text chunking library for RAG pipelines providing 10+ chunking strategies, pipeline orchestration, embeddings support, and vector database integrations with Python and JavaScript APIs.
license: MIT
author: Tangled Skills <skills@tangled.dev>
version: "1.6.2"
tags:
  - text-chunking
  - rag
  - nlp
  - embeddings
  - vector-databases
category: machine-learning
external_references:
  - https://docs.chonkie.ai/common/welcome
  - https://github.com/chonkie-inc/chonkie/tree/v1.6.2
  - https://github.com/chonkie-inc/chonkie/tree/v1.6.2/docs
---

# Chonkie 1.6.2

## Overview

**Chonkie** is a lightweight, fast, and robust text chunking library designed for RAG (Retrieval-Augmented Generation) pipelines. Built in Rust with Python and JavaScript bindings, it provides 10+ chunking strategies, end-to-end pipeline orchestration (CHOMP architecture), embeddings support, and direct integration with 8+ vector databases.

**Key Features:**
- 🚀 **Fast**: SIMD-accelerated chunking at 100+ GB/s
- 🪶 **Lightweight**: 505KB wheel size, 49MB installed (vs 80-171MB for alternatives)
- 🔌 **32+ Integrations**: Tokenizers, embeddings, LLMs, vector databases
- 🌍 **Multilingual**: Out-of-the-box support for 56 languages
- ☁️ **Cloud-Friendly**: Local chunking or cloud API
- ⚡ **Async Support**: All chunkers support async out of the box

## When to Use

Use this skill when:
- Building RAG pipelines that require text chunking
- Need to split documents into semantically meaningful chunks
- Processing code, markdown, tables, or structured documents
- Integrating with vector databases (Chroma, Qdrant, Pinecone, etc.)
- Require fast, lightweight chunking without heavy dependencies
- Building end-to-end document processing workflows (fetch → process → chunk → refine → store)

## Core Concepts

### CHOMP Architecture

Chonkie's pipeline follows the **CHOMP** (CHOnkie's Multi-step Pipeline) architecture:

```
Fetcher → Chef → Chunker → Refinery → Porter/Handshake
```

- **Fetcher**: Retrieve raw data from files, APIs, or databases
- **Chef**: Preprocess and transform raw data into Documents
- **Chunker**: Split documents into manageable chunks
- **Refinery** (Optional): Post-process and enhance chunks
- **Porter/Handshake** (Optional): Export or store chunks

### Available Chunkers

| Chunker | Alias | Best For |
|---------|-------|----------|
| `TokenChunker` | `token` | Fixed-size token chunks for LLMs |
| `FastChunker` | `fast` | High-throughput byte-based chunking (100+ GB/s) |
| `SentenceChunker` | `sentence` | Sentence-level semantic completeness |
| `RecursiveChunker` | `recursive` | Long documents with hierarchical structure |
| `SemanticChunker` | `semantic` | Preserving topical coherence via embeddings |
| `LateChunker` | `late` | Higher recall in RAG applications |
| `CodeChunker` | `code` | Source code files using AST parsing |
| `NeuralChunker` | `neural` | Topic-coherent chunks using BERT |
| `SlumberChunker` | `slumber` | Agentic chunking with LLMs (Genie interface) |
| `TableChunker` | `table` | Tabular data in markdown format |

See [Chunkers Deep Dive](references/01-chunkers.md) for detailed usage.

### Installation Options

```bash
# Basic installation (Token, Sentence, Recursive chunkers)
pip install chonkie

# With semantic embeddings (Model2Vec)
pip install "chonkie[semantic]"

# With code chunking support
pip install "chonkie[code]"

# With neural chunker (BERT-based)
pip install "chonkie[neural]"

# All features
pip install "chonkie[all]"
```

See [Installation Guide](references/02-installation.md) for complete options.

## Quick Start

### Basic Chunking

```python
from chonkie import RecursiveChunker

# Initialize the chunker
chunker = RecursiveChunker(chunk_size=512, chunk_overlap=50)

# Chunk some text
text = """Chonkie is a lightweight chunking library that just works!
It provides multiple chunking strategies for different use cases."""

chunks = chunker.chunk(text)

# Access chunks
for chunk in chunks:
    print(f"Chunk: {chunk.text}")
    print(f"Tokens: {chunk.token_count}")
    print(f"Start index: {chunk.start_index}")
```

### Pipeline Usage

```python
from chonkie import Pipeline

# Build a complete RAG ingestion pipeline
docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("overlap", context_size=100)
    .store_in("qdrant", collection_name="documents", url="http://localhost:6333")
    .run())

print(f"Ingested {len(docs)} documents")
```

See [Pipelines Guide](references/03-pipelines.md) for advanced workflows.

## Usage Examples

### Single Text Chunking

```python
from chonkie import TokenChunker

chunker = TokenChunker(
    tokenizer="gpt2",
    chunk_size=1024,
    chunk_overlap=128
)

text = "Your document text here..."
chunks = chunker.chunk(text)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk.text[:50]}...")
    print(f"  Tokens: {chunk.token_count}")
```

### Batch Processing

```python
from chonkie import RecursiveChunker

chunker = RecursiveChunker(chunk_size=512)

documents = [
    "First document about machine learning...",
    "Second document discussing neural networks...",
    "Third document on NLP..."
]

# Process all documents at once
batch_chunks = chunker.chunk_batch(documents)

for doc_idx, doc_chunks in enumerate(batch_chunks):
    print(f"Document {doc_idx + 1}: {len(doc_chunks)} chunks")
```

### Async Chunking

```python
import asyncio
from chonkie import SemanticChunker

async def process_documents(texts: list[str]):
    chunker = SemanticChunker(chunk_size=512, threshold=0.8)
    
    # Concurrent chunking
    results = await asyncio.gather(
        *[chunker.achunk(text) for text in texts]
    )
    return results

# Run async processing
chunks = asyncio.run(process_documents(["doc1", "doc2", "doc3"]))
```

### JavaScript Usage

```javascript
import { RecursiveChunker } from "@chonkiejs/core";

// Create a chunker
const chunker = await RecursiveChunker.create({
  chunkSize: 512,
  minCharactersPerChunk: 24,
});

// Chunk your text
const chunks = await chunker.chunk(
  "Your document text here..."
);

// Use the chunks
for (const chunk of chunks) {
  console.log(chunk.text);
  console.log(`Tokens: ${chunk.tokenCount}`);
}
```

## Advanced Topics

- **Chunkers Deep Dive**: [references/01-chunkers.md](references/01-chunkers.md) - All 10+ chunkers with parameters and examples
- **Installation Guide**: [references/02-installation.md](references/02-installation.md) - Complete installation options and dependencies
- **Pipelines Guide**: [references/03-pipelines.md](references/03-pipelines.md) - CHOMP architecture, recipes, and best practices
- **Embeddings**: [references/04-embeddings.md](references/04-embeddings.md) - 9+ embedding providers with AutoEmbeddings
- **Vector Databases**: [references/05-handshakes.md](references/05-handshakes.md) - 8+ vector DB integrations (Chroma, Qdrant, Pinecone, etc.)
- **API Server**: [references/06-api-server.md](references/06-api-server.md) - Self-hosted REST API with Docker support

## References

- **Official Documentation**: https://docs.chonkie.ai
- **GitHub Repository**: https://github.com/chonkie-inc/chonkie
- **Changelog**: https://github.com/chonkie-inc/chonkie/blob/v1.6.2/docs/oss/changelog.mdx
- **Discord Community**: https://discord.gg/Q6zkP8w6ur
- **Benchmarks**: https://github.com/chonkie-inc/chonkie/blob/main/BENCHMARKS.md

## Troubleshooting

### Common Issues

**ImportError: No module named 'chonkie'**
```bash
# Ensure you installed the package correctly
pip install chonkie

# For advanced features
pip install "chonkie[all]"
```

**Chunker not available**
Some chunkers require extra dependencies:
```bash
# SemanticChunker requires embeddings
pip install "chonkie[semantic]"

# CodeChunker requires tree-sitter
pip install "chonkie[code]"

# NeuralChunker requires transformers
pip install "chonkie[neural]"
```

**Logging too verbose**
Control logging with environment variable:
```bash
export CHONKIE_LOG=off       # Disable logging
export CHONKIE_LOG=warning   # Warnings and errors (default)
export CHONKIE_LOG=info      # More verbose
export CHONKIE_LOG=debug     # Everything
```

**Pipeline validation errors**
- Must have at least one chunker
- Must have fetcher OR text input via `run(texts=...)`
- Cannot have multiple chefs

```python
# ❌ Invalid - no chunker
Pipeline().fetch_from("file", path="doc.txt").run()

# ✅ Valid - has chunker and input source
Pipeline()
    .fetch_from("file", path="doc.txt")
    .chunk_with("recursive", chunk_size=512)
    .run()
```

See [Pipelines Guide](references/03-pipelines.md) for detailed error handling.
