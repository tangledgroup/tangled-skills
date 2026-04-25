# Pipelines Guide

## Overview

Chonkie's Pipeline API provides a fluent, chainable interface for building text processing workflows. Pipelines follow the **CHOMP architecture**, automatically orchestrating components in the correct order.

## CHOMP Architecture

```
Fetcher → Chef → Chunker → Refinery → Porter/Handshake
```

1. **Fetcher**: Retrieve raw data from files, APIs, or databases
2. **Chef**: Preprocess and transform raw data into Documents
3. **Chunker**: Split documents into manageable chunks (required)
4. **Refinery** (Optional): Post-process and enhance chunks
5. **Porter/Handshake** (Optional): Export or store chunks

**Important**: Pipelines automatically reorder components to follow CHOMP, so you can add them in any order.

## Quick Start

### Single File Processing

```python
from chonkie import Pipeline

# Build and execute pipeline
doc = (Pipeline()
    .fetch_from("file", path="document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run())

# Access chunks
print(f"Created {len(doc.chunks)} chunks")
for chunk in doc.chunks:
    print(f"Chunk: {chunk.text[:50]}...")
```

### Directory Processing

```python
# Process all markdown files in a directory
docs = (Pipeline()
    .fetch_from("file", dir="./documents", ext=[".md", ".txt"])
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run())

# Process each document
for doc in docs:
    print(f"Document has {len(doc.chunks)} chunks")
```

### Direct Text Input

Skip the fetcher and provide text directly:

```python
# Single text (no fetcher needed)
doc = (Pipeline()
    .process_with("text")
    .chunk_with("semantic", threshold=0.8)
    .run(texts="Your text here"))

# Multiple texts
docs = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .run(texts=["Text 1", "Text 2", "Text 3"]))
```

### Asynchronous Execution

For high-throughput applications (web servers, batch processing):

```python
import asyncio

async def process_docs():
    pipe = Pipeline().chunk_with("recursive")

    # Run pipeline asynchronously
    doc = await pipe.arun(texts="Async processing is fast!")

    # Process multiple concurrently
    docs = await pipe.arun(texts=["Doc 1", "Doc 2"])

    return docs

# Execute
docs = asyncio.run(process_docs())
```

## Pipeline Methods

### fetch_from()

Fetch data from a source:

```python
# Single file
.fetch_from("file", path="document.txt")

# Directory with extension filter
.fetch_from("file", dir="./docs", ext=[".txt", ".md"])

# Directory without filter (processes all files)
.fetch_from("file", dir="./docs")
```

**Parameters:**
- `source` (str): Source type ("file" for FileFetcher)
- `path` (str): Path to single file
- `dir` (str): Directory path
- `ext` (list[str]): File extensions to include (e.g., [".txt", ".md"])

### process_with()

Process data with a chef:

```python
# Text processing (cleaning, normalization)
.process_with("text")

# Markdown processing (extract tables, code blocks)
.process_with("markdown")

# Table processing
.process_with("table")
```

**Available Chefs:**
- `text`: TextChef - Basic text cleaning and normalization
- `markdown`: MarkdownChef - Parse markdown, extract tables and code
- `table`: TableChef - Process tabular data

**Note**: Only one chef allowed per pipeline.

### chunk_with()

Chunk documents (required in every pipeline):

```python
# Recursive chunking
.chunk_with("recursive", chunk_size=512, chunk_overlap=50)

# Semantic chunking
.chunk_with("semantic", threshold=0.8, chunk_size=1024)

# Code chunking
.chunk_with("code", chunk_size=512)

# Token-based chunking
.chunk_with("token", tokenizer="gpt2", chunk_size=2048)

# Multiple chunkers (sequential)
.chunk_with("recursive", chunk_size=2048)
.chunk_with("semantic", threshold=0.8, chunk_size=512)
```

**Available Chunkers:**
- `token`: TokenChunker
- `fast`: FastChunker
- `sentence`: SentenceChunker
- `recursive`: RecursiveChunker
- `semantic`: SemanticChunker
- `late`: LateChunker
- `code`: CodeChunker
- `neural`: NeuralChunker
- `slumber`: SlumberChunker
- `table`: TableChunker

### refine_with()

Refine chunks (optional, can chain multiple):

```python
# Add overlap context
.refine_with("overlap", context_size=100, method="prefix")

# Add embeddings
.refine_with("embedding", model="text-embedding-3-small")

# Multiple refineries
.refine_with("overlap", context_size=50)
.refine_with("embedding", model="minishlab/potion-base-32M")
```

**Available Refineries:**
- `overlap`: OverlapRefinery - Add context from neighboring chunks
- `embedding`: EmbeddingsRefinery - Compute embeddings for chunks

### export_with()

Export chunks to formats:

```python
# Export to JSON file
.export_with("json", file="chunks.json")

# Export to Hugging Face Datasets
.export_with("datasets", name="my-dataset")
```

**Available Porters:**
- `json`: JSONPorter - Export to JSON file
- `datasets`: DatasetsPorter - Export to Hugging Face Dataset format

### store_in()

Store in vector databases:

```python
# Store in ChromaDB
.store_in("chroma", collection_name="documents")

# Store in Qdrant
.store_in("qdrant", 
          collection_name="docs", 
          url="http://localhost:6333")

# Store in Pinecone
.store_in("pinecone", 
          index_name="my-index",
          api_key=os.environ["PINECONE_API_KEY"])

# Store in PostgreSQL with pgvector
.store_in("pgvector",
          collection_name="documents",
          connection_string="postgresql://user:pass@localhost/db")
```

**Available Handshakes:**
- `chroma`: ChromaDB
- `qdrant`: Qdrant
- `pinecone`: Pinecone
- `mongodb`: MongoDB Atlas
- `pgvector`: PostgreSQL with pgvector
- `elastic`: Elasticsearch
- `weaviate`: Weaviate
- `tpuf`: Turbopuffer
- `milvus`: Milvus

## Advanced Examples

### RAG Knowledge Base

Build a complete RAG ingestion pipeline:

```python
from chonkie import Pipeline

# Ingest documents into vector database
docs = (Pipeline()
    .fetch_from("file", dir="./knowledge_base", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("overlap", context_size=100)
    .store_in("qdrant",
              collection_name="knowledge",
              url="http://localhost:6333")
    .run())

print(f"Ingested {len(docs)} documents into Qdrant")
```

### Semantic Search Pipeline

Process documents with embeddings for search:

```python
from chonkie import Pipeline

# Chunk with embeddings
doc = (Pipeline()
    .fetch_from("file", path="research_paper.txt")
    .process_with("text")
    .chunk_with("semantic",
                threshold=0.8,
                chunk_size=1024,
                similarity_window=3)
    .refine_with("overlap", context_size=100)
    .refine_with("embedding", model="minishlab/potion-base-32M")
    .run())

# All chunks now have embeddings
for chunk in doc.chunks:
    if chunk.embedding is not None:
        print(f"Chunk: {chunk.text[:30]}... | Embedding shape: {chunk.embedding.shape}")
```

### Code Documentation Pipeline

Process code with specialized chunking:

```python
from chonkie import Pipeline

# Chunk Python files
docs = (Pipeline()
    .fetch_from("file", dir="./src", ext=[".py"])
    .chunk_with("code", chunk_size=512)
    .export_with("json", file="code_chunks.json")
    .run())

print(f"Processed {len(docs)} Python files")
```

### Markdown Documentation Pipeline

Handle markdown with table and code awareness:

```python
from chonkie import Pipeline

# Process markdown documentation
doc = (Pipeline()
    .fetch_from("file", path="README.md")
    .process_with("markdown")
    .chunk_with("recursive", chunk_size=512)
    .run())

# Access markdown metadata
print(f"Found {len(doc.tables)} tables")
print(f"Found {len(doc.code)} code blocks")
print(f"Created {len(doc.chunks)} chunks")
```

### Multi-Stage Chunking

Apply multiple chunking strategies sequentially:

```python
from chonkie import Pipeline

# First recursive, then semantic
doc = (Pipeline()
    .fetch_from("file", path="long_document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=2048)  # Coarse chunking
    .chunk_with("semantic", threshold=0.8, chunk_size=512)  # Fine chunking
    .refine_with("overlap", context_size=128)
    .run())

print(f"Created {len(doc.chunks)} semantically coherent chunks")
```

### Batch Processing with Progress

```python
from chonkie import Pipeline
from tqdm import tqdm

# Process large directory with progress bar
pipe = (Pipeline()
    .process_with("text")
    .chunk_with("recursive", chunk_size=512))

files = ["doc1.txt", "doc2.txt", "doc3.txt", ...]

for file in tqdm(files):
    doc = pipe.run(texts=open(file).read())
    print(f"{file}: {len(doc.chunks)} chunks")
```

## Recipe-Based Pipelines

Load pre-configured pipelines from the Chonkie Hub:

```python
from chonkie import Pipeline

# Load markdown processing recipe from Hub
pipeline = Pipeline.from_recipe("markdown")

# Run with your content
doc = pipeline.run(texts="# My Markdown\n\nContent here")

# Load custom local recipe
pipeline = Pipeline.from_recipe("custom", path="./my_recipe.json")
```

**Available Recipes:**
- `markdown`: Optimized for markdown documents
- `code`: Optimized for source code
- `legal`: Optimized for legal documents
- More recipes available at: https://huggingface.co/datasets/chonkie-ai/recipes

**Create Custom Recipe:**
```python
# Define pipeline
pipeline = (Pipeline()
    .process_with("markdown")
    .chunk_with("recursive", chunk_size=1024, separators=["\n\n## ", "\n\n", "\n", " "])
    .refine_with("overlap", context_size=100))

# Save as recipe
pipeline.save_recipe("my-custom-recipe", path="./recipes")

# Load later
pipeline = Pipeline.from_recipe("my-custom-recipe", path="./recipes")
```

## Return Values

Pipeline behavior depends on input:

| Input Type | Return Value |
|------------|--------------|
| Single file (`path="file.txt"`) | `Document` |
| Directory (`dir="./docs"`) | `list[Document]` |
| Single text (`texts="content"`) | `Document` |
| Multiple texts (`texts=["t1", "t2"]`) | `list[Document]` |

```python
# Single file → Document
doc = Pipeline().fetch_from("file", path="doc.txt").chunk_with("recursive").run()
assert isinstance(doc, Document)

# Directory → list[Document]
docs = Pipeline().fetch_from("file", dir="./docs").chunk_with("recursive").run()
assert isinstance(docs, list)

# Multiple texts → list[Document]
docs = Pipeline().chunk_with("recursive").run(texts=["t1", "t2"])
assert isinstance(docs, list)
```

## Document Object

The `Document` object contains processed content:

```python
doc = Pipeline().chunk_with("recursive").run(texts="Sample text")

# Access chunks
for chunk in doc.chunks:
    print(chunk.text)
    print(chunk.token_count)
    print(chunk.start_index)
    print(chunk.end_index)
    print(chunk.embedding)  # If embeddings added

# Access metadata (from chefs)
print(doc.tables)   # Extracted tables (from MarkdownChef)
print(doc.code)     # Extracted code blocks (from MarkdownChef)
print(doc.metadata) # Custom metadata
```

## Pipeline Validation

Pipelines validate configuration before execution:

**Requirements:**
- ✅ Must have at least one chunker
- ✅ Must have fetcher OR text input via `run(texts=...)`
- ❌ Cannot have multiple chefs (only one allowed)

```python
# ❌ Invalid - no chunker
Pipeline().fetch_from("file", path="doc.txt").run()
# Raises: ValueError("Pipeline must have at least one chunker")

# ❌ Invalid - multiple chefs
(Pipeline()
    .process_with("text")
    .process_with("markdown")  # Error!
    .chunk_with("recursive"))
# Raises: ValueError("Only one chef allowed per pipeline")

# ✅ Valid - has chunker and input source
(Pipeline()
    .fetch_from("file", path="doc.txt")
    .chunk_with("recursive", chunk_size=512)
    .run())

# ✅ Valid - text input, no fetcher needed
(Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .run(texts="Hello world"))
```

## Error Handling

Pipelines provide clear error messages:

```python
from chonkie import Pipeline
from pathlib import Path

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

**Common Errors:**
- `FileNotFoundError`: File or directory doesn't exist
- `ValueError`: Invalid pipeline configuration
- `RuntimeError`: Execution failure (e.g., API errors)
- `ImportError`: Missing optional dependencies

## Best Practices

### 1. Always Specify chunk_size

Explicitly set `chunk_size` for predictable behavior:

```python
# ✅ Good - explicit size
.chunk_with("recursive", chunk_size=512)

# ❌ Avoid - uses defaults that may change
.chunk_with("recursive")
```

### 2. Match Chunkers to Content Type

Choose chunkers appropriate for your content:

```python
# Code files → Code chunker
.chunk_with("code", chunk_size=512)

# Need semantic similarity → Semantic chunker
.chunk_with("semantic", threshold=0.8)

# General text → Recursive chunker
.chunk_with("recursive", chunk_size=512)

# Markdown → Process with markdown chef
.process_with("markdown")
.chunk_with("recursive", separators=["\n\n## ", "\n\n", "\n"])
```

### 3. Use Refineries for RAG Applications

Add overlap refineries for better retrieval context:

```python
(Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=100))
```

### 4. Filter Extensions in Directory Mode

Always specify file extensions to avoid unwanted files:

```python
# ✅ Good - filtered
.fetch_from("file", dir="./docs", ext=[".txt", ".md"])

# ❌ Bad - processes everything including binaries
.fetch_from("file", dir="./docs")
```

### 5. Chain Refineries for Complex Processing

Multiple refineries can be chained:

```python
(Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=50)
    .refine_with("embedding", model="text-embedding-3-small"))
```

### 6. Use Async for High Throughput

In web servers or batch processing:

```python
import asyncio
from chonkie import Pipeline

async def process_batch(texts):
    pipe = Pipeline().chunk_with("recursive", chunk_size=512)
    return await pipe.arun(texts=texts)

# FastAPI example
from fastapi import FastAPI

app = FastAPI()

@app.post("/chunk")
async def chunk_endpoint(texts: list[str]):
    return await process_batch(texts)
```

### 7. Reuse Pipeline Instances

Initialize pipelines once and reuse:

```python
# ✅ Good - reuse pipeline
pipeline = Pipeline().chunk_with("recursive", chunk_size=512)

for file in files:
    doc = pipeline.run(texts=open(file).read())

# ❌ Avoid - recreate pipeline each time
for file in files:
    pipeline = Pipeline().chunk_with("recursive", chunk_size=512)
    doc = pipeline.run(texts=open(file).read())
```

## Troubleshooting

### "Pipeline must have at least one chunker"

```python
# ❌ Missing chunker
Pipeline().fetch_from("file", path="doc.txt").run()

# ✅ Add chunker
Pipeline()
    .fetch_from("file", path="doc.txt")
    .chunk_with("recursive", chunk_size=512)
    .run()
```

### "Only one chef allowed per pipeline"

```python
# ❌ Multiple chefs
(Pipeline()
    .process_with("text")
    .process_with("markdown")
    .chunk_with("recursive"))

# ✅ Choose one chef
(Pipeline()
    .process_with("markdown")  # or "text"
    .chunk_with("recursive"))
```

### Missing optional dependencies

```bash
# For SemanticChunker
pip install "chonkie[semantic]"

# For vector database handshakes
pip install "chonkie[qdrant]"  # or chroma, pinecone, etc.
```

### Large memory usage

- Reduce `chunk_size` for smaller chunks
- Process files in batches instead of all at once
- Use `FastChunker` for lower memory overhead
- Avoid loading entire directories into memory
