# Batch Processing and Files

## Batch API

Process requests in bulk at lower cost with higher latency (up to 24 hours).

### Creating a Batch

```python
from openai import OpenAI

client = OpenAI()

# Upload input file (JSONL format)
input_file = client.files.create(
    file=open("batch_requests.jsonl", "rb"),
    purpose="batch",
)

# Create batch job
batch = client.batches.create(
    input_file_id=input_file.id,
    endpoint="/v1/chat/completions",  # or /v1/completions, /v1/embeddings
    completion_window="24h",          # currently only 24h supported
    metadata={"key": "value"},
)
```

### Input File Format

JSONL with one request per line:

```jsonl
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 100}}
{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "World"}], "max_tokens": 100}}
```

### Checking Status

```python
batch = client.batches.retrieve("batch_abc123")
print(batch.status)  # validating, in_progress, finalizing, completed, expired, cancelling, failed

print(batch.request_counts)
# completed: 950, failed: 50, total: 1000
```

### Retrieving Results

```python
# List batches
batches = client.batches.list(limit=20)

# When completed, download results file
if batch.status == "completed":
    result = client.files.content(batch.output_file_id)
    with open("batch_results.jsonl", "wb") as f:
        f.write(result.read())
```

### Cancelling a Batch

```python
cancelled = client.batches.cancel("batch_abc123")
```

## Files API

Manage files for fine-tuning, batch processing, and assistants.

### Upload

```python
file = client.files.create(
    file=open("data.jsonl", "rb"),
    purpose="fine-tune",  # or "batch", "assistants", "evals"
)
print(file.id)
print(file.filename)
print(file.bytes)
print(file.created_at)
```

### Retrieve and List

```python
# Get file details
file = client.files.retrieve("file-abc123")

# List files
files = client.files.list(purpose="fine-tune", limit=20)
```

### Download Content

```python
# Binary content
content = client.files.content("file-abc123")
with open("downloaded.jsonl", "wb") as f:
    f.write(content.read())

# String content
text = client.files.retrieve_content("file-abc123")
```

### Delete

```python
deleted = client.files.delete("file-abc123")
print(deleted.id)
print(deleted.deleted)  # True
```

### Wait for Processing

```python
# Poll until file processing completes
processed_file = client.files.wait_for_processing("file-abc123")
```

## Uploads API

For files larger than the upload limit, use chunked uploads:

```python
# Create upload session
upload = client.uploads.create(
    filename="large_dataset.jsonl",
    purpose="fine-tune",
    bytes=10_000_000_000,  # total file size in bytes
)

# Upload parts
with open("large_dataset.jsonl", "rb") as f:
    while chunk := f.read(10_000_000):  # 10MB chunks
        client.uploads.parts.create(
            upload_id=upload.id,
            part={"data": chunk},
        )

# Complete the upload
completed = client.uploads.complete(upload_id=upload.id)
```

### Cancel Upload

```python
cancelled = client.uploads.cancel("upload_abc123")
```
