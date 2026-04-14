# Installation Guide

## Overview

Chonkie follows a modular approach to dependencies, keeping the base installation lightweight while allowing you to add extra features as needed.

## Basic Installation

### Python

```bash
# Using pip
pip install chonkie

# Using uv (faster)
uv add chonkie
```

This installs:
- TokenChunker, SentenceChunker, RecursiveChunker, FastChunker, TableChunker
- TextChef and FileFetcher
- Basic refineries (OverlapRefinery)
- Python API SDK

### JavaScript

```bash
# Core package for local chunking
npm install @chonkiejs/core

# With custom tokenizers
npm install @chonkiejs/token

# For API access
npm install @chonkiejs/cloud
```

## Installation Options

Chonkie provides several installation options to match your specific needs:

### Python Optional Dependencies

```bash
# Hugging Face Hub support (Hubbie utility)
pip install "chonkie[hub]"

# Visualization support (Visualizer utility)
pip install "chonkie[viz]"

# Model2Vec embeddings (default semantic provider)
pip install "chonkie[model2vec]"

# SentenceTransformer embeddings (required by LateChunker)
pip install "chonkie[st]"

# OpenAI embeddings
pip install "chonkie[openai]"

# Cohere embeddings
pip install "chonkie[cohere]"

# Jina embeddings
pip install "chonkie[jina]"

# Gemini embeddings
pip install "chonkie[gemini]"

# VoyageAI embeddings
pip install "chonkie[voyageai]"

# LiteLLM embeddings (100+ models)
pip install "chonkie[litellm]"

# Semantic chunking (includes Model2Vec)
pip install "chonkie[semantic]"

# CodeChunker (tree-sitter based)
pip install "chonkie[code]"

# NeuralChunker (BERT-based)
pip install "chonkie[neural]"

# SlumberChunker with Gemini Genie
pip install "chonkie[genie]"

# SlumberChunker with Groq Genie (fast inference)
pip install "chonkie[groq]"

# SlumberChunker with Cerebras Genie (fastest inference)
pip install "chonkie[cerebras]"

# API server (Catsu framework)
pip install "chonkie[api]"

# Vector database integrations
pip install "chonkie[chroma]"      # ChromaDB
pip install "chonkie[qdrant]"      # Qdrant
pip install "chonkie[pinecone]"    # Pinecone
pip install "chonkie[mongodb]"     # MongoDB Atlas
pip install "chonkie[pgvector]"    # PostgreSQL with pgvector
pip install "chonkie[elastic]"     # Elasticsearch
pip install "chonkie[weaviate]"    # Weaviate
pip install "chonkie[tpuf]"        # Turbopuffer
pip install "chonkie[milvus]"      # Milvus

# Multiple features together
pip install "chonkie[st, code, genie]"

# ALL features (not recommended for production)
pip install "chonkie[all]"
```

## Chunker Availability Matrix

| Chunker | Default | semantic/st | code | neural | genie | All | JS Core | API |
|---------|---------|-------------|------|--------|-------|-----|---------|-----|
| TokenChunker | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FastChunker | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| RecursiveChunker | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SentenceChunker | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| TableChunker | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| SemanticChunker | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| LateChunker | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| CodeChunker | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| NeuralChunker | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| SlumberChunker | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

## Embeddings Availability Matrix

| Provider | Default | model2vec | st | openai | cohere | jina | gemini | voyageai | litellm | All |
|----------|---------|-----------|----|--------|--------|------|--------|----------|---------|-----|
| Model2Vec | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| SentenceTransformers | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| OpenAI | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Cohere | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Jina | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Gemini | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| VoyageAI | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| LiteLLM | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

## Dependencies Breakdown

| Install Option | Additional Dependencies |
|----------------|------------------------|
| Default | tqdm, numpy, chonkie-core, tenacity |
| hub | + huggingface-hub, jsonschema |
| viz | + rich |
| model2vec | + tokenizers, model2vec, numpy |
| st | + tokenizers, sentence-transformers, accelerate |
| openai | + openai, tiktoken, pydantic |
| cohere | + tokenizers, cohere |
| jina | + tokenizers |
| gemini | + google-genai |
| voyageai | + voyageai |
| litellm | + litellm, tiktoken, tokenizers |
| semantic | + tokenizers, model2vec |
| code | + tree-sitter, tree-sitter-language-pack, magika |
| neural | + transformers, torch |
| genie | + pydantic, google-genai |
| groq | + pydantic, groq |
| cerebras | + pydantic, cerebras-cloud-sdk |
| api | + catsu, pydantic, fastapi, uvicorn |
| chroma | + chromadb |
| qdrant | + qdrant-client |
| pinecone | + pinecone-client |
| mongodb | + pymongo, motor |
| pgvector | + psycopg2, psycopg2-binary, pgvector |
| elastic | + elasticsearch |
| weaviate | + weaviate-client |
| tpuf | + turbopuffer |
| milvus | + pymilvus |
| **all** | **All above dependencies** |

## JavaScript Packages

| Package | Purpose | Installation |
|---------|---------|--------------|
| @chonkiejs/core | Local chunking (Token, Recursive) | `npm install @chonkiejs/core` |
| @chonkiejs/token | Custom tokenizers | `npm install @chonkiejs/token` |
| @chonkiejs/cloud | API client | `npm install @chonkiejs/cloud` |

## Vector Database Dependencies

### ChromaDB
```bash
pip install "chonkie[chroma]"
# Adds: chromadb
```

### Qdrant
```bash
pip install "chonkie[qdrant]"
# Adds: qdrant-client
```

### Pinecone
```bash
pip install "chonkie[pinecone]"
# Adds: pinecone-client, pinecone-plugin-inference
```

### MongoDB Atlas
```bash
pip install "chonkie[mongodb]"
# Adds: pymongo, motor
```

### PostgreSQL with pgvector
```bash
pip install "chonkie[pgvector]"
# Adds: psycopg2-binary, pgvector
```

### Elasticsearch
```bash
pip install "chonkie[elastic]"
# Adds: elasticsearch
```

### Weaviate
```bash
pip install "chonkie[weaviate]"
# Adds: weaviate-client
```

### Turbopuffer
```bash
pip install "chonkie[tpuf]"
# Adds: turbopuffer
```

### Milvus
```bash
pip install "chonkie[milvus]"
# Adds: pymilvus, pymilvus-model
```

## Recommended Installations by Use Case

### Basic RAG Pipeline
```bash
pip install "chonkie[semantic]"
# Includes: SemanticChunker + Model2Vec embeddings
```

### Code Processing
```bash
pip install "chonkie[code, semantic]"
# Includes: CodeChunker + SemanticChunker
```

### Advanced Chunking (All Local)
```bash
pip install "chonkie[st, code, neural]"
# Includes: LateChunker, CodeChunker, NeuralChunker
```

### Agentic Chunking with LLMs
```bash
pip install "chonkie[genie, semantic]"
# Includes: SlumberChunker with Gemini Genie
```

### Production RAG with Vector DB
```bash
pip install "chonkie[semantic, qdrant]"
# Or replace qdrant with chroma/pinecone/mongodb/etc.
```

### API Server
```bash
pip install "chonkie[api, semantic, code, catsu]"
# Includes: API server + embeddings + code chunking
```

## Size Comparison

| Installation | Wheel Size | Installed Size |
|--------------|-----------|----------------|
| chonkie (base) | 505 KB | 49 MB |
| chonkie[semantic] | 505 KB | ~180 MB |
| chonkie[all] | 505 KB | ~650 MB |

**Comparison with alternatives:**
- LangChain: 1-12 MB wheel, 80-171 MB installed
- LlamaIndex: 2-8 MB wheel, 120-200 MB installed
- Chonkie: 0.5 MB wheel, 49-650 MB installed (modular)

## Logging Configuration

Control logging verbosity with environment variable:

```bash
# Disable all logging
export CHONKIE_LOG=off

# Warnings and errors only (default)
export CHONKIE_LOG=warning

# More verbose (includes info messages)
export CHONKIE_LOG=info

# Maximum verbosity (includes debug)
export CHONKIE_LOG=debug
```

Or in Python:
```python
import os
os.environ["CHONKIE_LOG"] = "off"

from chonkie import RecursiveChunker
```

## Verification

Verify installation:

```python
# Check version
import chonkie
print(chonkie.__version__)  # Should print: 1.6.2

# Test basic chunking
from chonkie import RecursiveChunker
chunker = RecursiveChunker(chunk_size=512)
chunks = chunker.chunk("Test text...")
print(f"Created {len(chunks)} chunks")

# Check available chunkers
from chonkie import (
    TokenChunker,
    FastChunker,
    SentenceChunker,
    RecursiveChunker,
    TableChunker
)
print("Basic chunkers available!")

# Check optional chunkers (may fail if not installed)
try:
    from chonkie import SemanticChunker
    print("SemanticChunker available!")
except ImportError:
    print("Install with: pip install 'chonkie[semantic]'")

try:
    from chonkie import CodeChunker
    print("CodeChunker available!")
except ImportError:
    print("Install with: pip install 'chonkie[code]'")
```

## Troubleshooting

### "No module named 'chonkie'"
```bash
# Ensure correct installation
pip install chonkie

# Check Python environment
python -c "import sys; print(sys.executable)"
which python
which pip
```

### Chunker not available
```bash
# Install required dependencies
pip install "chonkie[semantic]"  # For SemanticChunker
pip install "chonkie[code]"      # For CodeChunker
pip install "chonkie[neural]"    # For NeuralChunker
pip install "chonkie[genie]"     # For SlumberChunker
```

### Dependency conflicts
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install "chonkie[all]"

# Or use uv for faster, conflict-free installation
uv venv
uv pip install "chonkie[semantic, qdrant]"
```

### GPU requirements (for neural chunkers)
```bash
# NeuralChunker requires PyTorch
# CPU-only
pip install "chonkie[neural]"

# With CUDA support
pip install "chonkie[neural]"
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Uninstallation

```bash
# Remove Chonkie
pip uninstall chonkie

# Clean up dependencies manually if needed
pip uninstall tqdm numpy chonkie-core tenacity
```
