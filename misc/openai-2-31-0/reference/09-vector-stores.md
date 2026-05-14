# Vector Stores

Vector stores provide managed document storage for assistant file search, handling chunking, embedding, and indexing automatically.

## Creating a Vector Store

```python
from openai import OpenAI

client = OpenAI()

vector_store = client.vector_stores.create(
    name="Product Documentation",
    expires_after={
        "anchor": "last_active_at",
        "days": 30,
    },
)
```

## Adding Files

### Single File

```python
vs_file = client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id="file-abc123",  # already uploaded with purpose="assistants"
)
```

### Upload Directly

```python
vs_file = client.vector_stores.files.upload_and_poll(
    vector_store_id=vector_store.id,
    file=open("document.pdf", "rb"),
)
print(vs_file.status)  # completed, in_progress, failed, cancelled
```

### Batch Upload

```python
batch = client.vector_stores.file_batches.create_and_poll(
    vector_store_id=vector_store.id,
    files=[
        {"file_id": "file-abc123"},
        {"file_id": "file-def456"},
    ],
)

print(batch.file_counts)
# in_progress: 0, completed: 2, failed: 0, cancelled: 0
```

### Upload Files in Batch

```python
batch = client.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id,
    files=[
        open("doc1.pdf", "rb"),
        open("doc2.pdf", "rb"),
    ],
)
```

## Managing Vector Stores

```python
# Retrieve
vs = client.vector_stores.retrieve("vs_abc123")

# Update
updated = client.vector_stores.update(
    "vs_abc123",
    name="Updated Name",
)

# List
vector_stores = client.vector_stores.list(limit=20)

# Delete
deleted = client.vector_stores.delete("vs_abc123")
```

## Managing Files in a Vector Store

```python
# List files
files = client.vector_stores.files.list(
    vector_store_id="vs_abc123",
    limit=20,
)

# Retrieve file status
vs_file = client.vector_stores.files.retrieve(
    "vsf_abc123",
    vector_store_id="vs_abc123",
)

# Update file (e.g., add chunking strategy)
updated = client.vector_stores.files.update(
    "vsf_abc123",
    vector_store_id="vs_abc123",
)

# Delete file from vector store
deleted = client.vector_stores.files.delete(
    "vsf_abc123",
    vector_store_id="vs_abc123",
)

# Get file content
content_pages = client.vector_stores.files.content(
    "vsf_abc123",
    vector_store_id="vs_abc123",
)
```

## File Batches

```python
# Retrieve batch status
batch = client.vector_stores.file_batches.retrieve(
    "vsfb_abc123",
    vector_store_id="vs_abc123",
)

# Cancel batch
cancelled = client.vector_stores.file_batches.cancel(
    "vsfb_abc123",
    vector_store_id="vs_abc123",
)

# List files in a batch
files = client.vector_stores.file_batches.list_files(
    "vsfb_abc123",
    vector_store_id="vs_abc123",
)
```

## Chunking Strategies

Control how documents are split:

```python
# Static token-based chunking
vs_file = client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id="file-abc123",
    chunking_strategy={
        "type": "static",
        "static": {
            "max_chunk_size_tokens": 800,
            "chunk_overlap_tokens": 400,
        },
    },
)

# Auto (default) — OpenAI chooses optimal strategy
vs_file = client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id="file-abc123",
    chunking_strategy={"type": "auto"},
)
```

## Associating with Assistants

Link a vector store to an assistant for file search:

```python
assistant = client.beta.assistants.create(
    name="Documentation Assistant",
    model="gpt-5.2",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store.id],
        }
    },
)

# Or create a vector store automatically
assistant = client.beta.assistants.create(
    name="Documentation Assistant",
    model="gpt-5.2",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_stores": [{"name": "Auto-created store"}],
        }
    },
)
```

## Polling Helpers

Use `*_and_poll` methods for synchronous wait:

```python
# Wait for file processing
vs_file = client.vector_stores.files.create_and_poll(
    vector_store_id=vector_store.id,
    file_id="file-abc123",
)

# Wait for batch processing
batch = client.vector_stores.file_batches.create_and_poll(
    vector_store_id=vector_store.id,
    files=[{"file_id": "file-abc123"}],
)
```
