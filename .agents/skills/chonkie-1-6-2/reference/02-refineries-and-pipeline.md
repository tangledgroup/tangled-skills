# Refineries and Pipeline API

## Refineries

Refineries post-process chunks after initial chunking to enhance them with additional context or embeddings. They are callable objects that take a list of `Chunk` objects and return refined chunks.

### OverlapRefinery

Adds overlapping context from neighboring chunks. Useful for maintaining contextual continuity in question answering or summarization tasks.

**Installation**: Included in base install.

```python
from chonkie import TokenChunker, OverlapRefinery

chunker = TokenChunker(chunk_size=512)
chunks = chunker("Your document text here...")

# Add suffix overlap (context from next chunk)
refinery = OverlapRefinery(
    tokenizer="character",
    context_size=0.25,       # Fraction of max chunk tokens (float 0-1) or absolute int
    mode="token",             # "token" or "recursive"
    method="suffix",          # "prefix" (from previous) or "suffix" (from next)
    merge=True,               # Merge into chunk.text vs store in chunk.context
    inplace=True              # Modify input list directly
)

refined_chunks = refinery(chunks)

# Recursive mode with custom rules
from chonkie import RecursiveRules, RecursiveLevel

rules = RecursiveRules(levels=[
    RecursiveLevel(delimiters=["\n\n"], include_delim="prev"),
    RecursiveLevel(delimiters=["."], include_delim="prev"),
    RecursiveLevel(whitespace=True),
])

refinery = OverlapRefinery(
    mode="recursive",
    rules=rules,
    method="prefix",
    context_size=0.5
)
```

**Parameters**:

- `tokenizer`: Tokenizer for calculating overlap size (string identifier, callable, or Tokenizer instance)
- `context_size`: If int, absolute token count. If float (0–1), fraction of max chunk token count
- `mode`: `"token"` uses tokenizer directly. `"recursive"` uses hierarchical splitting via rules
- `method`: `"suffix"` adds from next chunk to end. `"prefix"` adds from previous chunk to beginning
- `merge`: If True, context is merged into `chunk.text`. If False, stored in `chunk.context`
- `inplace`: If True, modifies input list directly

### EmbeddingsRefinery

Computes and attaches embedding vectors directly to chunks. Streamlines loading chunks into vector databases.

**Installation**: `pip install "chonkie[semantic]"`

```python
from chonkie import RecursiveChunker, EmbeddingsRefinery

chunker = RecursiveChunker(chunk_size=512)
chunks = chunker("Your text here...")

refinery = EmbeddingsRefinery(
    embedding_model="minishlab/potion-base-32M"  # Model string or BaseEmbeddings instance
)

chunks_with_embeddings = refinery(chunks)

# Each chunk now has .embedding attribute
for chunk in chunks_with_embeddings:
    if chunk.embedding is not None:
        print(f"Embedding shape: {len(chunk.embedding)}")
```

## Pipeline API

The Pipeline provides a fluent, chainable interface for building multi-step text processing workflows. Pipelines follow the **CHOMP architecture** and automatically reorder components into correct execution order.

### CHOMP Architecture

```
Fetcher → Chef → Chunker → Refinery → Porter/Handshake
```

1. **Fetcher**: Retrieve raw data from files, APIs, or databases
2. **Chef**: Preprocess and transform raw data into Documents
3. **Chunker**: Split documents into manageable chunks (required)
4. **Refinery**: Post-process and enhance chunks (optional, chainable)
5. **Porter/Handshake**: Export or store chunks (optional)

### Basic Pipeline

```python
from chonkie import Pipeline

# Single text input
doc = (Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .run(texts="Your document text here..."))

print(f"Created {len(doc.chunks)} chunks")
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

### Full RAG Pipeline

```python
# Complete ingestion pipeline
docs = (Pipeline()
    .fetch_from("file", dir="./knowledge_base", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("semantic", threshold=0.8, chunk_size=1024)
    .refine_with("overlap", context_size=100)
    .store_in("qdrant", collection_name="knowledge", url="http://localhost:6333")
    .run())
```

### Pipeline Methods

**`fetch_from(source, ...)`**: Fetch data from a source.
```python
.fetch_from("file", path="document.txt")
.fetch_from("file", dir="./docs", ext=[".txt", ".md"])
```

**`process_with(chef_type)`**: Process with a chef.
```python
.process_with("text")      # TextChef for cleaning/normalizing
.process_with("markdown")  # MarkdownChef extracts tables and code blocks
.process_with("table")     # Table processing
```

**`chunk_with(chunker_type, **kwargs)`**: Chunk documents (required).
```python
.chunk_with("recursive", chunk_size=512, chunk_overlap=50)
.chunk_with("semantic", threshold=0.8, chunk_size=1024)
.chunk_with("code", chunk_size=512)
.chunk_with("token", tokenizer="gpt2", chunk_size=1024)
```

**`refine_with(refinery_type, **kwargs)`**: Refine chunks (optional, chainable).
```python
.refine_with("overlap", context_size=100, method="prefix")
.refine_with("embedding", model="text-embedding-3-small")
```

**`export_with(porter_type, ...)`**: Export chunks to file formats.
```python
.export_with("json", file="chunks.json")
.export_with("datasets", name="my-dataset")
```

**`store_in(handshake_type, ...)`**: Store in vector databases.
```python
.store_in("chroma", collection_name="documents")
.store_in("qdrant", collection_name="docs", url="http://localhost:6333")
.store_in("pgvector", collection_name="docs")
```

### Async Execution

```python
import asyncio
from chonkie import Pipeline

async def process():
    pipe = Pipeline().chunk_with("recursive", chunk_size=512)
    doc = await pipe.arun(texts="Async processing is fast!")
    return doc

asyncio.run(process())
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

Recipes are stored in the [chonkie-ai/recipes](https://huggingface.co/datasets/chonkie-ai/recipes) repository on HuggingFace Hub.

### Pipeline Validation

Pipelines validate configuration before execution:

- **Must have**: At least one chunker
- **Must have**: Fetcher OR text input via `run(texts=...)`
- **Cannot have**: Multiple chefs (only one allowed)

```python
# Invalid — no chunker
Pipeline().fetch_from("file", path="doc.txt").run()

# Invalid — multiple chefs
Pipeline().process_with("text").process_with("markdown").chunk_with("recursive")

# Valid
Pipeline().fetch_from("file", path="doc.txt").chunk_with("recursive", chunk_size=512).run()
```

### Return Values

- **Single file/text**: Returns a `Document` object
- **Multiple files/texts**: Returns `list[Document]`

```python
doc = Pipeline().fetch_from("file", path="doc.txt").chunk_with("recursive").run()
# doc is a Document with .chunks list

docs = Pipeline().fetch_from("file", dir="./docs").chunk_with("recursive").run()
# docs is a list[Document]
```

### Best Practices

- Always specify `chunk_size` explicitly for predictable behavior
- Match chunkers to content type: CodeChunker for code, SemanticChunker for topic coherence, RecursiveChunker for general text
- Use OverlapRefinery for RAG applications to provide retrieval context
- Filter file extensions in directory mode to avoid processing binaries
- Chain multiple refineries for complex processing (overlap + embeddings)
