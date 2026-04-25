# Installation

> **Source:** https://docs.chonkie.ai/oss/installation
> **Loaded from:** SKILL.md (via progressive disclosure)

Chonkie follows a modular approach to dependencies, keeping the base installation lightweight while allowing optional features.

## Python Installation

### Basic Install

```bash
pip install chonkie
# or
uv add chonkie
```

Includes: TokenChunker, SentenceChunker, RecursiveChunker, FastChunker, TableChunker, OverlapRefinery.

### Optional Extras

```bash
# Hugging Face Hub support
pip install "chonkie[hub]"

# Visualization (rich terminal output)
pip install "chonkie[viz]"

# Semantic chunking (Model2Vec embeddings, default for semantic)
pip install "chonkie[semantic]"

# OpenAI embeddings
pip install "chonkie[openai]"

# Cohere embeddings
pip install "chonkie[cohere]"

# Jina embeddings
pip install "chonkie[jina]"

# Voyage AI embeddings
pip install "chonkie[voyageai]"

# Gemini embeddings
pip install "chonkie[gemini]"

# SentenceTransformer embeddings (required by LateChunker)
pip install "chonkie[st]"

# Code chunking (tree-sitter, 165+ languages)
pip install "chonkie[code]"

# Neural chunking (BERT-based)
pip install "chonkie[neural]"

# Slumber chunking (LLM-powered via Genie interface)
pip install "chonkie[genie]"

# Groq Genie (fast inference on Groq hardware)
pip install "chonkie[groq]"

# Cerebras Genie (fastest inference)
pip install "chonkie[cerebras]"

# LiteLLM embeddings (100+ models)
pip install "chonkie[litellm]"

# Azure OpenAI embeddings
pip install "chonkie[azure-openai]"

# Multiple features together
pip install "chonkie[st,code,genie]"

# All features
pip install "chonkie[all]"
```

### Dependencies By Extra

- **Default**: tqdm, numpy, chonkie-core, tenacity
- **hub**: + huggingface-hub, jsonschema
- **viz**: + rich
- **model2vec**: + tokenizers, model2vec, numpy
- **st**: + tokenizers, sentence-transformers, accelerate
- **openai**: + openai, tiktoken, pydantic
- **cohere**: + tokenizers, cohere
- **jina**: + tokenizers
- **semantic**: + tokenizers, model2vec
- **code**: + tree-sitter, tree-sitter-language-pack, magika
- **neural**: + transformers, torch
- **genie**: + pydantic, google-genai
- **groq**: + pydantic, groq
- **cerebras**: + pydantic, cerebras-cloud-sdk
- **litellm**: + litellm, tiktoken, tokenizers

## JavaScript Installation

```bash
# Core chunking (Token, Sentence, Recursive, Fast, Table, Semantic, Code)
npm install @chonkiejs/core

# API access (cloud-based chunking)
npm install @chonkiejs/cloud

# Custom tokenizers
npm install @chonkiejs/token
```

## Chunker Availability Matrix

- **Default install**: TokenChunker, FastChunker, SentenceChunker, RecursiveChunker, TableChunker
- **Semantic extra (+)**: SemanticChunker, LateChunker, NeuralChunker, SlumberChunker
- **Code extra (+)**: CodeChunker
- **All features**: Every chunker including TeraflopAIChunker
- **JavaScript core**: TokenChunker, SentenceChunker, RecursiveChunker, FastChunker, TableChunker, SemanticChunker, CodeChunker
- **JavaScript cloud API**: All chunkers (LateChunker, NeuralChunker, SlumberChunker available via API)

## Embeddings Availability

- **model2vec extra**: Model2VecEmbeddings
- **st extra**: SentenceTransformerEmbeddings
- **openai extra**: OpenAIEmbeddings
- **semantic extra**: Model2VecEmbeddings (default for semantic chunking)
- **all features**: All embedding providers

## Logging Control

```bash
export CHONKIE_LOG=off      # Disable logging
export CHONKIE_LOG=warning   # Warnings and errors (default)
export CHONKIE_LOG=info      # More verbose
export CHONKIE_LOG=debug     # Everything
```

## Known Issues

- **v1.6.3**: `import chonkie` fails with `ModuleNotFoundError: No module named 'pandas'` when installed without `[table]` extra. Fixed in v1.6.4.
- **Semantic/all extras**: Contents may change between versions. Pin versions for reproducibility.
