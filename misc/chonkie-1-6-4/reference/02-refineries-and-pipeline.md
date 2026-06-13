# Refineries and Pipeline API

## CHOMP Architecture

Pipelines follow the **CHOMP** (CHOnkie's Multi-step Pipeline) architecture:

```
Fetcher → Chef → Chunker → Refinery → Porter/Handshake
```

Pipelines automatically reorder components to follow CHOMP, so you can add them in any order.

## OverlapRefinery

Enhances chunks by incorporating context from neighboring chunks. Useful for maintaining contextual continuity between chunks (question answering, summarization).

```python
from chonkie import OverlapRefinery

# Default: 25% character-level suffix overlap
refinery = OverlapRefinery()

# Custom configuration
refinery = OverlapRefinery(
    tokenizer="character",
    context_size=0.25,              # Fraction of max chunk tokens (or int for absolute)
    method="prefix",                # "prefix" (from previous) or "suffix" (from next)
    merge=True                      # Merge directly into chunk.text
)

# Recursive mode with custom rules
from chonkie import RecursiveRules, RecursiveLevel
rules = RecursiveRules(
    levels=[
        RecursiveLevel(delimiters=["\n\n"], include_delim="prev"),
        RecursiveLevel(delimiters=["."], include_delim="prev"),
        RecursiveLevel(whitespace=True)
    ]
)
refinery = OverlapRefinery(
    tokenizer="character",
    context_size=0.25,
    mode="recursive",
    rules=rules,
    method="suffix"
)

# Usage
chunks = chunker("Your text here...")
refined_chunks = refinery(chunks)
```

**Parameters:**

- `tokenizer` — Tokenizer for calculating overlap size. Default: `"character"`.
- `context_size` — Overlap size as fraction (0–1) or absolute token count. Default: `0.25`.
- `mode` — `"token"` (direct tokenizer) or `"recursive"` (hierarchical splitting). Default: `"token"`.
- `method` — `"suffix"` (append from next chunk) or `"prefix"` (prepend from previous). Default: `"suffix"`.
- `rules` — RecursiveRules for recursive mode. Default: `RecursiveRules()`.
- `merge` — Merge context into `chunk.text` if `True`, store in `chunk.context` if `False`. Default: `True`.
- `inplace` — Modify input list directly if `True`. Default: `True`.

## EmbeddingsRefinery

Computes and attaches embeddings to chunks using any supported embedding provider.

```python
from chonkie import EmbeddingsRefinery

refinery = EmbeddingsRefinery(
    embedding_model="minishlab/potion-base-32M",  # Model string or BaseEmbeddings instance
)

chunks = chunker("Your text here...")
embedded_chunks = refinery(chunks)

# Each chunk now has an embedding vector
for chunk in embedded_chunks:
    print(f"Embedding shape: {len(chunk.embedding)}")
```

**Parameters:**

- `embedding_model` — Model identifier string or `BaseEmbeddings` instance (required).

## Pipeline API

The Pipeline provides a fluent, chainable interface for building multi-step workflows.

### Basic Usage

```python
from chonkie import Pipeline

# Direct text input
doc = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .run(texts="Your text here..."))

# Multiple texts
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .run(texts=["Text 1", "Text 2"]))
```

### File Processing

```python
# Single file
doc = (Pipeline()
    .fetch_from("file", path="document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run())

# Directory with extension filter
docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".md", ".txt"])
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run())

for doc in docs:
    print(f"Document has {len(doc.chunks)} chunks")
```

### Complete RAG Pipeline

```python
docs = (Pipeline()
    .fetch_from("file", dir="./knowledge_base", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("overlap", context_size=100)
    .store_in("qdrant", collection_name="knowledge", url="http://localhost:6333")
    .run())
```

### Semantic Search Pipeline with Embeddings

```python
doc = (Pipeline()
    .fetch_from("file", path="research_paper.txt")
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024, similarity_window=3)
    .refine_with("overlap", context_size=100)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .run())

# All chunks now have embeddings
for chunk in doc.chunks:
    if chunk.embedding is not None:
        print(f"Chunk: {chunk.text[:30]}... | Embedding dims: {len(chunk.embedding)}")
```

### Asynchronous Execution

```python
import asyncio

async def process_docs():
    pipe = Pipeline().chunk_with("recursive")
    doc = await pipe.arun(texts="Async processing is fast!")
    docs = await pipe.arun(texts=["Doc 1", "Doc 2"])
    return docs
```

### Pipeline Methods

**`fetch_from(source, **kwargs)`** — Fetch data from a source:
```python
.fetch_from("file", path="document.txt")
.fetch_from("file", dir="./docs", ext=[".txt", ".md"])
```

**`process_with(chef_name)`** — Process with a chef:
```python
.process_with("text")       # TextChef
.process_with("markdown")   # MarkdownChef
.process_with("table")      # TableChef
```

**`chunk_with(chunker_name, **kwargs)`** — Chunk documents (required):
```python
.chunk_with("recursive", chunk_size=512, chunk_overlap=50)
.chunk_with("semantic", threshold=0.8, chunk_size=1024)
.chunk_with("code", chunk_size=512)
```

**`refine_with(refinery_name, **kwargs)`** — Refine chunks (optional, chainable):
```python
.refine_with("overlap", context_size=100, method="prefix")
.refine_with("embedding", model="text-embedding-3-small")
```

**`export_with(porter_name, **kwargs)`** — Export chunks:
```python
.export_with("json", file="chunks.json")
.export_with("datasets", name="my-dataset")
```

**`store_in(handshake_name, **kwargs)`** — Store in vector databases:
```python
.store_in("chroma", collection_name="documents")
.store_in("qdrant", collection_name="docs", url="http://localhost:6333")
```

### Recipe-Based Pipelines

Load pre-configured pipelines from the Chonkie Hub:

```python
# Load markdown processing recipe
pipeline = Pipeline.from_recipe("markdown")
doc = pipeline.run(texts="# My Markdown\n\nContent here")

# Load custom local recipe
pipeline = Pipeline.from_recipe("custom", path="./my_recipe.json")
```

Recipes are stored at `chonkie-ai/recipes` on HuggingFace Hub.

### Pipeline Validation

Pipelines validate configuration before execution:

**Must have**: At least one chunker.
**Must have**: Fetcher OR text input via `run(texts=...)`.
**Cannot have**: Multiple chefs (only one allowed).

```python
# Invalid - no chunker
Pipeline().fetch_from("file", path="doc.txt").run()  # Error!

# Invalid - multiple chefs
Pipeline().process_with("text").process_with("markdown").chunk_with("recursive")  # Error!

# Valid
Pipeline().fetch_from("file", path="doc.txt").chunk_with("recursive", chunk_size=512).run()
Pipeline().chunk_with("recursive").run(texts="Hello world")
```

### Return Values

- **Single file/text**: Returns `Document`
- **Multiple files/texts**: Returns `list[Document]`

### Error Handling

```python
try:
    doc = (Pipeline()
        .fetch_from("file", path="missing.txt")
        .chunk_with("recursive")
        .run())
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Pipeline execution failed: {e}")
```

### Best Practices

**Always specify chunk_size**:
```python
# Good - explicit size
.chunk_with("recursive", chunk_size=512)
```

**Match chunkers to content type**:
```python
# Code files → CodeChunker
.chunk_with("code")
# Semantic similarity needed → SemanticChunker
.chunk_with("semantic", threshold=0.8)
# General text → RecursiveChunker
.chunk_with("recursive")
```

**Use refineries for RAG applications**:
```python
.chunk_with("recursive", chunk_size=512)
.refine_with("overlap", context_size=100)
```

**Filter extensions in directory mode**:
```python
# Good - filtered
.fetch_from("file", dir="./docs", ext=[".txt", ".md"])
```

**Chain refineries for complex processing**:
```python
.chunk_with("recursive", chunk_size=512)
.refine_with("overlap", context_size=50)
.refine_with("embedding", model="text-embedding-3-small")
```
