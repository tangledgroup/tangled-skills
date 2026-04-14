# Embeddings Guide

## Overview

Chonkie provides a variety of embeddings handlers to work with different embedding models in a consistent manner. Embeddings are used by chunkers (SemanticChunker, LateChunker) and refineries (EmbeddingsRefinery) to add semantic understanding to chunks.

## Common Interface

All embeddings handlers share a consistent interface:

```python
# Single text embedding
emb = embeddings.embed(text)

# Batch processing
embs = embeddings.embed_batch(texts)

# Direct calling (Python only)
embs = embeddings(text)  # or embeddings([text1, text2])

# Async variants
emb = await embeddings.aembed(text)
embs = await embeddings.aembed_batch(texts)
```

## AutoEmbeddings

Automatically select and load the best embeddings handler for your use case.

**Best for**: Quick setup without worrying about specific providers.

```python
from chonkie import AutoEmbeddings

# Auto-detect available embeddings
embeddings = AutoEmbeddings()

# Use with any chunker or refinery
chunks = embeddings.embed("Your text here")

# Specify preferred provider
embeddings = AutoEmbeddings(provider="model2vec")
embeddings = AutoEmbeddings(provider="sentence-transformers")
```

**How it works:**
1. Checks for installed embedding providers
2. Loads first available provider in priority order
3. Falls back to default (Model2Vec) if nothing else available

## Model2VecEmbeddings

Uses Model2Vec models for fast, efficient embeddings with multilingual support.

**Best for**: Default semantic chunking, multilingual applications.

```python
from chonkie import Model2VecEmbeddings

# Using default model
embeddings = Model2VecEmbeddings()

# Specify custom model
embeddings = Model2VecEmbeddings(
    model_name="minishlab/potion-base-32M",  # Fast, small model
    device="cuda"  # or "cpu"
)

# Embed text
emb = embeddings.embed("Your text here")
print(f"Embedding shape: {emb.shape}")  # e.g., (512,)

# Batch embedding
embs = embeddings.embed_batch(["text1", "text2", "text3"])
print(f"Batch shape: {embs.shape}")  # e.g., (3, 512)
```

**Parameters:**
- `model_name` (str): Hugging Face model name (default: "minishlab/potion-base-32M")
- `device` (str): Device to use ("cpu", "cuda", "auto")
- `normalize` (bool): Normalize embeddings to unit length (default: True)

**Popular Models:**
```python
# Fast, small models
Model2VecEmbeddings(model_name="minishlab/potion-base-32M")    # 32MB
Model2VecEmbeddings(model_name="minishlab/potion-embedding-base")  # 128MB

# Multilingual models
Model2VecEmbeddings(model_name="intfloat/multilingual-e5-large")
Model2VecEmbeddings(model_name="sentence-transformersLaBSE")
```

## SentenceTransformerEmbeddings

Uses SentenceTransformers library for embeddings with extensive model support.

**Best for**: Wide model selection, research applications.

```python
from chonkie import SentenceTransformerEmbeddings

# Using popular model
embeddings = SentenceTransformerEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cuda"
)

# Embed text
emb = embeddings.embed("Your text here")

# Batch with progress bar
embs = embeddings.embed_batch(
    ["text1", "text2", "text3"],
    show_progress=True
)
```

**Parameters:**
- `model_name` (str): Hugging Face model name
- `device` (str): Device to use ("cpu", "cuda", "auto")
- `normalize` (bool): Normalize embeddings (default: True)
- `batch_size` (int): Batch size for embedding (default: 32)

**Popular Models:**
```python
# Lightweight models
SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")     # 42MB
SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")    # 95MB

# Large models (better quality)
SentenceTransformerEmbeddings(model_name="bge-large-en-v1.5")    # 674MB
SentenceTransformerEmbeddings(model_name="intfloat/e5-large")   # 674MB

# Multilingual models
SentenceTransformerEmbeddings(model_name="LaBSE")               # 56 languages
SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
```

## OpenAIEmbeddings

Uses OpenAI's embedding API for cloud-based embeddings.

**Best for**: Production applications, no local model hosting needed.

```python
import os
from chonkie import OpenAIEmbeddings

# Using default model (text-embedding-3-small)
embeddings = OpenAIEmbeddings(
    api_key=os.environ["OPENAI_API_KEY"]
)

# Specify custom model
embeddings = OpenAIEmbeddings(
    api_key=os.environ["OPENAI_API_KEY"],
    model="text-embedding-3-large"  # Higher quality
)

# Embed text
emb = embeddings.embed("Your text here")

# Batch embedding (max 2048 per request)
embs = embeddings.embed_batch(["text1", "text2", ...])
```

**Parameters:**
- `api_key` (str): OpenAI API key
- `model` (str): Model name (default: "text-embedding-3-small")
- `organization` (str): OpenAI organization ID (optional)

**Available Models:**
- `text-embedding-3-small`: Fast, cost-effective (1536 dimensions)
- `text-embedding-3-large`: Higher quality (3072 dimensions)
- `text-embedding-ada-002`: Legacy model (1536 dimensions)

## CohereEmbeddings

Uses Cohere's embedding API for high-quality embeddings.

**Best for**: Enterprise applications, reranking support.

```python
import os
from chonkie import CohereEmbeddings

embeddings = CohereEmbeddings(
    api_key=os.environ["COHERE_API_KEY"],
    model="embed-english-v3.0"  # or "embed-multilingual-v3.0"
)

# Embed text
emb = embeddings.embed("Your text here")

# Specify embedding type
emb = embeddings.embed(
    "Your text here",
    input_type="search_document"  # or "query", "classification", etc.
)
```

**Parameters:**
- `api_key` (str): Cohere API key
- `model` (str): Model name (default: "embed-english-v3.0")
- `input_type` (str): Input type for domain-specific embeddings

**Available Models:**
- `embed-english-v3.0`: English-only, high quality
- `embed-english-light-v3.0`: English-only, faster
- `embed-multilingual-v3.0`: 100+ languages
- `embed-multilingual-light-v3.0`: Multilingual, faster

## JinaEmbeddings

Uses Jina AI's embedding API for multilingual support.

**Best for**: Long context (up to 8K tokens), multilingual applications.

```python
import os
from chonkie import JinaEmbeddings

embeddings = JinaEmbeddings(
    api_key=os.environ["JINA_API_KEY"],
    model="jina-embeddings-v3"
)

# Embed text (supports up to 8K tokens)
emb = embeddings.embed("Your long document...")

# Specify task type
emb = embeddings.embed(
    "Your text here",
    task_type="retrieval.passage"  # or "retrieval.query", etc.
)
```

**Parameters:**
- `api_key` (str): Jina API key
- `model` (str): Model name (default: "jina-embeddings-v3")
- `task_type` (str): Task type for domain-specific embeddings
- `dimensions` (int): Output dimensions (1024, 768, 512, 256)

## GeminiEmbeddings

Uses Google's Gemini API for embeddings.

**Best for**: Google ecosystem integration, multilingual support.

```python
import os
from chonkie import GeminiEmbeddings

embeddings = GeminiEmbeddings(
    api_key=os.environ["GEMINI_API_KEY"],
    model="models/embedding-001"  # or "models/embedding-gecko-001"
)

# Embed text
emb = embeddings.embed("Your text here")

# Specify task type
emb = embeddings.embed(
    "Your text here",
    task_type="RETRIEVAL_DOCUMENT"  # or "RETRIEVAL_QUERY", etc.
)
```

**Parameters:**
- `api_key` (str): Google API key
- `model` (str): Model name (default: "models/embedding-001")
- `task_type` (str): Task type for domain-specific embeddings

## VoyageAIEmbeddings

Uses Voyage AI's embedding API for RAG-optimized embeddings.

**Best for**: RAG applications, high-quality retrieval.

```python
import os
from chonkie import VoyageAIEmbeddings

embeddings = VoyageAIEmbeddings(
    api_key=os.environ["VOYAGE_API_KEY"],
    model="voyage-3"  # RAG-optimized
)

# Embed text
emb = embeddings.embed("Your text here")

# Specify input type
emb = embeddings.embed(
    "Your text here",
    input_type="document"  # or "query"
)
```

**Parameters:**
- `api_key` (str): Voyage AI API key
- `model` (str): Model name (default: "voyage-3")
- `input_type` (str): Input type ("document", "query", etc.)

**Available Models:**
- `voyage-3`: Latest, best quality for RAG
- `voyage-3-lite`: Faster, cost-effective
- `voyage-multilingual-2`: Multilingual support
- `voyage-code-2`: Code embeddings

## AzureOpenAIEmbeddings

Uses Azure OpenAI Service for enterprise deployments.

**Best for**: Enterprise applications requiring Azure infrastructure.

```python
import os
from chonkie import AzureOpenAIEmbeddings

embeddings = AzureOpenAIEmbeddings(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment_name="text-embedding-3-small",
    api_version="2024-02-01"
)

# Embed text
emb = embeddings.embed("Your text here")
```

**Parameters:**
- `api_key` (str): Azure OpenAI API key
- `azure_endpoint` (str): Azure endpoint URL
- `deployment_name` (str): Deployment name in Azure
- `api_version` (str): API version (default: "2023-05-15")

## LiteLLMEmbeddings

Uses LiteLLM to access 100+ embedding models through unified interface.

**Best for**: Multi-provider setups, cost optimization.

```python
import os
from chonkie import LiteLLMEmbeddings

# Using OpenAI through LiteLLM
embeddings = LiteLLMEmbeddings(
    model="text-embedding-3-small",
    api_key=os.environ["OPENAI_API_KEY"]
)

# Using Hugging Face Inference API
embeddings = LiteLLMEmbeddings(
    model="huggingface/sentence-transformers/all-MiniLM-L6-v2"
)

# Using any provider supported by LiteLLM
embeddings = LiteLLMEmbeddings(
    model="cohere:embed-english-v3.0",
    api_key=os.environ["COHERE_API_KEY"]
)
```

**Parameters:**
- `model` (str): Model name with optional provider prefix
- `api_key` (str): API key (provider-specific)
- `base_url` (str): Custom base URL for self-hosted models

## Using Embeddings with Chunkers

### SemanticChunker

```python
from chonkie import SemanticChunker, Model2VecEmbeddings

# Using model name directly
chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",
    threshold=0.8,
    chunk_size=1024
)

# Using embeddings instance
embeddings = Model2VecEmbeddings(model_name="all-MiniLM-L6-v2")
chunker = SemanticChunker(
    embedding_model=embeddings,
    threshold=0.8,
    chunk_size=1024
)

chunks = chunker.chunk("Your document...")
```

### LateChunker

```python
from chonkie import LateChunker, SentenceTransformerEmbeddings

embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

chunker = LateChunker(
    embedding_model=embeddings,
    chunk_size=512,
    n_slices=4
)

chunks = chunker.chunk("Your document...")
```

## Using Embeddings with Refineries

### EmbeddingsRefinery

Add embeddings to existing chunks:

```python
from chonkie import Pipeline, Model2VecEmbeddings

# Add embeddings after chunking
doc = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .run(texts="Your document..."))

# All chunks now have embeddings
for chunk in doc.chunks:
    print(f"Chunk: {chunk.text[:50]}...")
    print(f"Embedding: {chunk.embedding}")  # numpy array
```

### Using with Vector Databases

```python
from chonkie import Pipeline

# Chunk, embed, and store in one pipeline
docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".txt"])
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("embedding", model="text-embedding-3-small")
    .store_in("qdrant", 
              collection_name="documents",
              url="http://localhost:6333")
    .run())

print(f"Stored {len(docs)} documents with embeddings in Qdrant")
```

## Performance Comparison

| Provider | Speed | Cost | Quality | Context Length | Best For |
|----------|-------|------|---------|----------------|----------|
| Model2Vec | ⚡⚡⚡ Fast | 💰 Free | ⭐⭐⭐ Good | 512 tokens | Local, multilingual |
| SentenceTransformers | ⚡⚡ Medium | 💰 Free | ⭐⭐⭐⭐ Very Good | 512-8K tokens | Research, flexibility |
| OpenAI | ⚡⚡ Medium | 💰💰 Paid | ⭐⭐⭐⭐⭐ Excellent | 8K tokens | Production, reliability |
| Cohere | ⚡⚡ Medium | 💰💰 Paid | ⭐⭐⭐⭐⭐ Excellent | 512-2K tokens | Enterprise, reranking |
| Jina | ⚡⚡ Medium | 💰💰 Paid | ⭐⭐⭐⭐⭐ Excellent | 8K tokens | Long context |
| Gemini | ⚡⚡ Medium | 💰💰 Paid | ⭐⭐⭐⭐ Very Good | 2K tokens | Google ecosystem |
| VoyageAI | ⚡⚡ Medium | 💰💰 Paid | ⭐⭐⭐⭐⭐ Excellent | 4K tokens | RAG-optimized |

## Batch Processing

All embeddings support batch processing for better throughput:

```python
from chonkie import Model2VecEmbeddings

embeddings = Model2VecEmbeddings()

# Single text
emb = embeddings.embed("text")

# Batch (more efficient)
texts = ["text1", "text2", "text3", ...]
embs = embeddings.embed_batch(texts)

# Async batch
embs = await embeddings.aembed_batch(texts)
```

## Normalization

Most embeddings are normalized by default (unit length):

```python
# Default: normalized
embeddings = Model2VecEmbeddings(normalize=True)

# Disable normalization if needed
embeddings = Model2VecEmbeddings(normalize=False)
```

**When to normalize:**
- ✅ Cosine similarity (most vector databases)
- ✅ Most RAG applications
- ❌ When using custom distance metrics

## Troubleshooting

### "Module not found" errors

```bash
# Install required dependencies
pip install "chonkie[semantic]"      # For Model2Vec
pip install "chonkie[st]"           # For SentenceTransformers
pip install "chonkie[openai]"       # For OpenAIEmbeddings
pip install "chonkie[cohere]"       # For CohereEmbeddings
pip install "chonkie[jina]"         # For JinaEmbeddings
pip install "chonkie[gemini]"       # For GeminiEmbeddings
pip install "chonkie[voyageai]"     # For VoyageAIEmbeddings
pip install "chonkie[litellm]"      # For LiteLLMEmbeddings
```

### API key errors

```python
import os

# Set API keys as environment variables
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["COHERE_API_KEY"] = "your-key"
os.environ["JINA_API_KEY"] = "your-key"

# Or pass directly
embeddings = OpenAIEmbeddings(api_key="your-key")
```

### Out of memory errors

```python
# Use smaller models
Model2VecEmbeddings(model_name="minishlab/potion-base-32M")  # 32MB

# Reduce batch size
SentenceTransformerEmbeddings(batch_size=16)

# Use CPU instead of GPU
embeddings = Model2VecEmbeddings(device="cpu")

# Process in smaller batches
for i in range(0, len(texts), 100):
    batch = texts[i:i+100]
    embs = embeddings.embed_batch(batch)
```

### Slow embedding speed

- Use Model2Vec for fastest local embeddings
- Batch process texts instead of one at a time
- Use GPU if available (`device="cuda"`)
- Consider cloud APIs for better throughput
