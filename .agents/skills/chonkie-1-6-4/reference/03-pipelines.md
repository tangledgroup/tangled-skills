# Pipelines

> **Source:** https://docs.chonkie.ai/oss/pipelines
> **Loaded from:** SKILL.md (via progressive disclosure)

Chonkie's Pipeline API provides a fluent, chainable interface for building end-to-end text processing workflows.

## CHOMP Architecture

```
Fetcher → Chef → Chunker → Refinery → Porter/Handshake
```

Pipelines automatically reorder components to follow CHOMP, so steps can be added in any order.

## Quick Start

### Direct Text Input

```python
from chonkie import Pipeline

doc = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .run(texts="Your text here"))

print(f"Created {len(doc.chunks)} chunks")
```

### Single File Processing

```python
doc = (Pipeline()
    .fetch_from("file", path="document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run())
```

### Directory Processing

```python
docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".md", ".txt"])
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run())

for doc in docs:
    print(f"Document has {len(doc.chunks)} chunks")
```

### Async Execution

```python
import asyncio

async def process_docs():
    pipe = Pipeline().chunk_with("recursive")
    doc = await pipe.arun(texts="Async processing!")
    docs = await pipe.arun(texts=["Doc 1", "Doc 2"])
    return docs
```

## Pipeline Methods

### fetch_from()

Retrieve raw data from files or directories:

```python
.fetch_from("file", path="document.txt")
.fetch_from("file", dir="./docs", ext=[".txt", ".md"])
```

### process_with()

Preprocess data with a chef:

```python
.process_with("text")       # TextChef — plain text
.process_with("markdown")   # MarkdownChef — tables, code blocks, images
.process_with("table")      # TableChef — HTML table extraction
```

### chunk_with()

Apply a chunker (required step):

```python
.chunk_with("recursive", chunk_size=512, chunk_overlap=50)
.chunk_with("semantic", threshold=0.8, chunk_size=1024)
.chunk_with("code", chunk_size=512)
```

### refine_with()

Post-process chunks (optional, chainable):

```python
.refine_with("overlap", context_size=100, method="prefix")
.refine_with("embedding", model="text-embedding-3-small")
```

### export_with()

Export chunks to file formats:

```python
.export_with("json", file="chunks.json")
.export_with("datasets", name="my-dataset")  # HuggingFace Datasets
```

### store_in()

Store chunks directly in vector databases:

```python
.store_in("chroma", collection_name="documents")
.store_in("qdrant", collection_name="docs", url="http://localhost:6333")
```

## Complete Examples

### RAG Knowledge Base Ingestion

```python
docs = (Pipeline()
    .fetch_from("file", dir="./knowledge_base", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("overlap", context_size=100)
    .store_in("qdrant", collection_name="knowledge", url="http://localhost:6333")
    .run())
```

### Semantic Search Pipeline

```python
doc = (Pipeline()
    .fetch_from("file", path="research_paper.txt")
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024, similarity_window=3)
    .refine_with("overlap", context_size=100)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .run())
```

### Code Documentation Pipeline

```python
docs = (Pipeline()
    .fetch_from("file", dir="./src", ext=[".py"])
    .chunk_with("code", chunk_size=512)
    .export_with("json", file="code_chunks.json")
    .run())
```

### Markdown Processing

```python
doc = (Pipeline()
    .fetch_from("file", path="README.md")
    .process_with("markdown")
    .chunk_with("recursive", chunk_size=512)
    .run())

print(f"Found {len(doc.tables)} tables")
print(f"Found {len(doc.code)} code blocks")
print(f"Created {len(doc.chunks)} chunks")
```

## Recipe-Based Pipelines

Load pre-configured pipelines from the Chonkie Hub:

```python
# Load markdown processing recipe
pipeline = Pipeline.from_recipe("markdown")
doc = pipeline.run(texts="# My Markdown\n\nContent here")

# Load custom local recipe
pipeline = Pipeline.from_recipe("custom", path="./my_recipe.json")
```

Recipes are stored in the [chonkie-ai/recipes](https://huggingface.co/datasets/chonkie-ai/recipes) repository.

## Pipeline Validation Rules

- Must have at least one chunker
- Must have a fetcher OR text input via `run(texts=...)`
- Cannot have multiple chefs (only one allowed)

```python
# ❌ Invalid — no chunker
Pipeline().fetch_from("file", path="doc.txt").run()

# ❌ Invalid — multiple chefs
Pipeline().process_with("text").process_with("markdown").chunk_with("recursive")

# ✅ Valid
Pipeline().fetch_from("file", path="doc.txt").chunk_with("recursive", chunk_size=512).run()

# ✅ Valid — text input, no fetcher
Pipeline().chunk_with("recursive").run(texts="Hello world")
```

## Return Values

- **Single file/text**: Returns `Document`
- **Multiple files/texts**: Returns `list[Document]`

## Components Overview

### Fetchers

- **FileFetcher**: Load text from files and directories

### Chefs

- **TextChef**: Process plain text files into structured Documents
- **MarkdownChef**: Parse markdown with tables, code blocks, and images
- **TableChef**: Extract tables from HTML/markdown text

### Porters

- **JSONPorter**: Export chunks to JSON
- **DatasetsPorter**: Export to HuggingFace Datasets format

### Utilities

- **Visualizer**: Rich terminal visualization of chunks with color-coded boundaries
- **Hubbie**: HuggingFace Hub integration for sharing and loading chunkers

## Best Practices

- Always specify `chunk_size` explicitly for predictable behavior
- Match chunkers to content type (code → CodeChunker, general → Recursive)
- Use `OverlapRefinery` for RAG applications to add retrieval context
- Filter file extensions in directory mode to avoid processing binaries
- Chain multiple refineries for complex processing (overlap + embeddings)
