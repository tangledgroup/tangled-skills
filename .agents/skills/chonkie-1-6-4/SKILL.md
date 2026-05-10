---
name: chonkie-1-6-4
description: Lightweight text chunking library for RAG pipelines providing 12+ chunkers, pipeline API, refineries, vector DB handshakes, and a self-hosted REST API. Use when building document ingestion pipelines for retrieval-augmented generation, splitting text into meaningful chunks, or constructing CHOMP workflows (fetch, clean, chunk, refine, store).
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - text-chunking
  - rag
  - nlp
  - embeddings
  - vector-databases
  - python
  - javascript
category: machine-learning
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

Chonkie is a lightweight, high-performance text chunking library designed for retrieval-augmented generation (RAG) pipelines. It provides 12 chunking strategies ranging from simple token-based splitting to neural and agentic approaches, all unified behind a consistent interface. Built with Python (3.10+) and JavaScript support, Chonkie follows the CHOMP architecture — **C**hef (preprocess), **H**chunk, **O**verlap/Refine, **M**erge/export, **P**ort/store — to orchestrate end-to-end document ingestion workflows.

Key characteristics:

- **Lightweight**: 505 KB wheel size vs 1–12 MB for alternatives. Base install pulls only ~4 core dependencies (tqdm, numpy, chonkie-core, tenacity).
- **Fast**: SIMD-accelerated chunking via `chonkie-core` Rust extension (100+ GB/s for FastChunker). Benchmarks show 33x faster token chunking than the slowest competitor and 2x faster sentence chunking than LlamaIndex.
- **Modular dependencies**: Install only what you need via optional extras (`[semantic]`, `[code]`, `[neural]`, etc.).
- **Unified `Chunk` type**: Since v1.3.0, all chunkers return the same base `Chunk` dataclass with fields: `text`, `start_index`, `end_index`, `token_count`, optional `context`, and optional `embedding`.
- **Async support**: Every chunker provides `achunk()`, `achunk_batch()`, and `achunk_document()` methods out of the box using `asyncio.to_thread`.
- **32+ integrations**: Tokenizers (tiktoken, HuggingFace tokenizers), embedding providers (OpenAI, Cohere, Jina, Voyage AI, sentence-transformers, Model2Vec, LiteLLM), LLM genies (Gemini, OpenAI, Groq, Cerebras), and vector database handshakes (ChromaDB, Qdrant, Pinecone, Weaviate, pgvector, MongoDB, Elasticsearch, Milvus, Turbopuffer, LanceDB).
- **Self-hosted REST API**: Run `chonkie serve` for a language-agnostic HTTP chunking service with pipeline persistence.

## When to Use

- Building RAG pipelines that need high-quality text chunking
- Splitting documents into semantically coherent chunks for vector database ingestion
- Processing code files with structure-aware chunking (AST-based CodeChunker)
- Running end-to-end ingestion workflows: fetch → clean → chunk → refine → embed → store
- Needing fast, lightweight chunking without the overhead of LangChain or LlamaIndex
- Building self-hosted REST APIs for chunking services via `chonkie serve`
- Processing markdown tables with header-preserving TableChunker
- Domain-specific text segmentation via TeraflopAI integration

## Core Concepts

**Chunk**: The fundamental output unit. A dataclass with `text`, `start_index`, `end_index`, `token_count`, optional `context`, and optional `embedding`. All chunkers return this same type.

**Chunker**: A component that splits text into `Chunk` objects. Chonkie provides 12 chunkers: Token, Fast, Sentence, Recursive, Semantic, Late, Code, Neural, Slumber, Table, TeraflopAI, and SDPM (legacy/deprecated).

**Refinery**: A post-processing component that enhances chunks. `OverlapRefinery` adds context from neighboring chunks. `EmbeddingsRefinery` computes and attaches embedding vectors.

**Pipeline**: A fluent, chainable interface for building multi-step workflows following the CHOMP architecture: Fetcher → Chef → Chunker → Refinery → Porter/Handshake. Pipelines auto-reorder components into correct execution order.

**Chef**: Text preprocessing component. `TextChef` cleans and normalizes text. `MarkdownChef` extracts tables and code blocks from markdown. `TableChef` processes CSV/Excel into markdown tables.

**Porter**: Exports chunks to file formats. `JSONPorter` writes JSON. `DatasetsPorter` pushes to HuggingFace Datasets.

**Handshake**: Connects chunks directly to vector databases for embedding and storage in one step (ChromaDB, Qdrant, Pinecone, Weaviate, pgvector, MongoDB, Elasticsearch, Milvus, Turbopuffer, LanceDB).

**Genie**: Interface to LLM providers for advanced chunking strategies. Supports Gemini, OpenAI, Azure OpenAI, Groq, and Cerebras.

**Recipe**: Pre-configured chunker settings loaded from HuggingFace Hub. Use `from_recipe()` for language-specific or document-type-specific chunking (e.g., `RecursiveChunker.from_recipe("markdown", lang="en")`).

## Installation / Setup

### Basic Python Installation

```bash
pip install chonkie
```

Or with uv:

```bash
uv add chonkie
```

This provides TokenChunker, FastChunker, SentenceChunker, RecursiveChunker, TableChunker, OverlapRefinery, and basic tokenizers (character, word, byte).

### Optional Features

Install specific capabilities as needed:

```bash
# Semantic chunking (SemanticChunker, LateChunker) with Model2Vec embeddings
pip install "chonkie[semantic]"

# Code-aware chunking (CodeChunker) with tree-sitter
pip install "chonkie[code]"

# Neural chunking (NeuralChunker) with transformers + torch
pip install "chonkie[neural]"

# LLM-based chunking (SlumberChunker) via Genie interface
pip install "chonkie[genie]"

# Groq genie (fast inference)
pip install "chonkie[groq]"

# Cerebras genie (fastest inference)
pip install "chonkie[cerebras]"

# Visualization tools
pip install "chonkie[viz]"

# HuggingFace Hub recipes
pip install "chonkie[hub]"

# All features (not recommended for production)
pip install "chonkie[all]"

# Multiple features combined
pip install "chonkie[semantic,code,viz]"
```

### JavaScript Installation

```bash
npm install @chonkiejs/core     # Local chunking (Token, Sentence, Recursive, Fast, Table, Semantic, Code)
npm install @chonkiejs/cloud    # API client for cloud chunking
npm install @chonkiejs/token    # Custom tokenizers for JS
```

### Logging Control

```bash
export CHONKIE_LOG=off      # Disable all logging
export CHONKIE_LOG=warning  # Warnings and errors (default)
export CHONKIE_LOG=info     # More verbose
export CHONKIE_LOG=debug    # Everything
```

## Usage Examples

### Basic Chunking

```python
from chonkie import RecursiveChunker

chunker = RecursiveChunker(chunk_size=512)
chunks = chunker("Your document text here...")

for chunk in chunks:
    print(f"Text: {chunk.text[:50]}...")
    print(f"Tokens: {chunk.token_count}")
```

### Pipeline Workflow

```python
from chonkie import Pipeline

doc = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=100)
    .run(texts="Your document text here..."))

for chunk in doc.chunks:
    print(chunk.text)
```

### RAG Ingestion Pipeline

```python
from chonkie import Pipeline

docs = (Pipeline()
    .fetch_from("file", dir="./knowledge_base", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("overlap", context_size=100)
    .store_in("qdrant", collection_name="knowledge", url="http://localhost:6333")
    .run())
```

### Async Chunking

```python
import asyncio
from chonkie import SemanticChunker

async def process():
    chunker = SemanticChunker(chunk_size=512)
    chunks = await chunker.achunk("Document text...")
    return chunks

asyncio.run(process())
```

## Advanced Topics

**All Chunkers**: Detailed guide to all 12 chunking strategies including Token, Fast, Sentence, Recursive, Semantic, Late, Code, Neural, Slumber, Table, and TeraflopAI → [Chunkers](reference/01-chunkers.md)

**Refineries and Pipeline API**: OverlapRefinery, EmbeddingsRefinery, CHOMP architecture, pipeline methods, validation rules, and best practices → [Refineries and Pipeline](reference/02-refineries-and-pipeline.md)

**Integrations**: Embedding providers (9+), LLM Genies (5+), Vector database handshakes (10+), Porters, Tokenizers, Chefs, Fetchers → [Integrations](reference/03-integrations.md)

**API Server and JavaScript SDK**: Self-hosted REST API with `chonkie serve`, Docker deployment, pipeline persistence, and the @chonkiejs JavaScript packages → [API Server and JavaScript](reference/04-api-server-and-js.md)
