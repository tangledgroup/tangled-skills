# Embedding Generation with Qwen3

Comprehensive guide to generating embeddings using Qwen3 Embedding models, including encoding options, batch processing, and pooling strategies.

## Basic Encoding

### Single Text

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Encode single text
text = "This is an example document."
embedding = model.encode(text)
print(embedding.shape)  # (1024,)
print(embedding.dtype)  # torch.float32
```

### Multiple Texts

```python
texts = [
    "First document to encode.",
    "Second document with different content.",
    "Third document for batch processing."
]

embeddings = model.encode(texts)
print(embeddings.shape)  # (3, 1024)
```

## Encoding Options

### Normalization

Normalize embeddings for cosine similarity operations:

```python
# Normalize embeddings (unit vectors)
embeddings = model.encode(texts, normalize_embeddings=True)

# Verify normalization
import torch
norms = torch.norm(embeddings, dim=1)
print(norms)  # tensor([1., 1., 1.])
```

**When to normalize**:
- ✅ Cosine similarity search
- ✅ Vector database storage (most require normalized vectors)
- ✅ Clustering with cosine distance

**When NOT to normalize**:
- ❌ Euclidean distance calculations
- ❌ Further neural network processing
- ❌ Weighted combinations of embeddings

### Batch Processing

```python
# Large batch with custom batch size
texts = [...]  # 10,000+ documents
embeddings = model.encode(
    texts,
    batch_size=32,  # Process 32 texts at a time
    show_progress_bar=True  # Show progress
)

# Adjust batch size based on GPU memory:
# - 4B model on T4: batch_size=32-64
# - 8B model on A100: batch_size=16-32
# - CPU only: batch_size=8-16
```

### Truncation and Padding

```python
# Handle long texts with truncation
long_text = "Very long document " * 1000  # Exceeds context length

embeddings = model.encode(
    [long_text],
    truncate=True,  # Truncate to max sequence length
    max_length=512  # Custom max length (default: 512 or 8192)
)

# Padding options
embeddings = model.encode(
    texts,
    pad_to_max_length=True,  # Pad all to same length (consistent batching)
    max_length=512
)
```

### Device Management

```python
# Load on specific device
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B", device="cuda")

# Or move after loading
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
model.to("cuda")  # Move to GPU
model.to("cpu")   # Move back to CPU

# Check current device
print(model.device)  # cuda or cpu

# Multi-GPU (for very large batches)
from sentence_transformers import CrossEncoder
model = SentenceTransformer("Qwen/Qwen3-Embedding-8B", device="cuda:0")
```

## Pooling Strategies

Qwen3 Embedding supports different pooling methods to aggregate token embeddings into a single vector:

### Available Pooling Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **cls** | Use CLS token embedding | Classification tasks |
| **mean** | Mean of all token embeddings | General-purpose, semantic search |
| **max** | Max pooling across tokens | Keyword matching |

### Configuring Pooling

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.models import Transformer, Pooling

# Load with custom pooling
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Replace pooling layer
embedding_dim = model.get_sentence_embedding_dimension()
pooling = Pooling(model.transformer.word_embeddings.embedding_dim, 
                  word_embedding_batch_size=8,
                  pooling_mode_cls_token=False,
                  pooling_mode_mean_tokens=True,   # Mean pooling
                  pooling_mode_max_tokens=False)

model._modules['1'] = pooling  # Replace pooling layer

# Verify new embedding dimension
print(model.get_sentence_embedding_dimension())
```

### Pooling Comparison

```python
from sentence_transformers import SentenceTransformer
import torch

texts = ["The cat sits on the mat.", "A feline rests on a rug."]

# Compare different pooling strategies
for pooling_mode in ['cls', 'mean', 'max']:
    model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
    # Modify pooling based on mode...
    embeddings = model.encode(texts)
    similarity = model.similarity(embeddings[0], embeddings[1])
    print(f"{pooling_mode}: {similarity.item():.4f}")
```

## Prompt Templates

Qwen3 Embedding supports prompt templates for different use cases:

### Default Prompts

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Model may have built-in prompts for queries and passages
# Check model card for specific prompt formats

# Example with explicit prompts
query_text = "What is machine learning?"
passage_text = "Machine learning is a subset of artificial intelligence..."

# Add prefixes if recommended by model
query_with_prompt = f"Query: {query_text}"
passage_with_prompt = f"Passage: {passage_text}"

query_emb = model.encode(query_with_prompt)
passage_emb = model.encode(passage_with_prompt)
```

### Custom Prompt Templates

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Define prompt templates for different tasks
prompts = {
    "query": "Represent this sentence for searching: ",
    "passage": "Represent this sentence for retrieval: ",
    "code": "Represent this code snippet: ",
    "product": "Represent this product description: "
}

def encode_with_prompt(text, prompt_type="query"):
    prompt = prompts.get(prompt_type, "")
    return model.encode(f"{prompt}{text}")

# Usage
query_emb = encode_with_prompt("Best laptop for programming", "query")
passage_emb = encode_with_passage("Dell XPS 15 with Intel i7...", "passage")
```

## Advanced Encoding Features

### Multi-Process Encoding

```python
from sentence_transformers import SentenceTransformer
from multiprocessing import Pool

def encode_batch(batch_texts):
    model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
    return model.encode(batch_texts)

# Split texts into chunks
texts = [...]  # 100,000 documents
chunk_size = 10000
chunks = [texts[i:i+chunk_size] for i in range(0, len(texts), chunk_size)]

# Process in parallel (each process loads its own model)
with Pool(processes=4) as pool:
    embedding_chunks = pool.map(encode_batch, chunks)

# Combine results
all_embeddings = np.vstack(embedding_chunks)
```

### Incremental Encoding

```python
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
all_embeddings = []

# Process in streaming fashion
for batch in stream_texts(large_corpus, batch_size=1000):
    batch_embeddings = model.encode(batch, show_progress_bar=False)
    all_embeddings.append(batch_embeddings)

# Combine at the end
all_embeddings = np.vstack(all_embeddings)
```

### Embedding Caching

```python
import hashlib
import pickle
from pathlib import Path

def get_text_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

class EmbeddingCache:
    def __init__(self, model, cache_dir="embedding_cache"):
        self.model = model
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def encode(self, texts):
        cached_embeddings = {}
        to_encode = []
        
        # Check cache for each text
        for text in texts:
            text_hash = get_text_hash(text)
            cache_file = self.cache_dir / f"{text_hash}.pkl"
            
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    cached_embeddings[text] = pickle.load(f)
            else:
                to_encode.append(text)
        
        # Encode uncached texts
        if to_encode:
            new_embeddings = self.model.encode(to_encode)
            for text, embedding in zip(to_encode, new_embeddings):
                text_hash = get_text_hash(text)
                cache_file = self.cache_dir / f"{text_hash}.pkl"
                with open(cache_file, 'wb') as f:
                    pickle.dump(embedding, f)
                cached_embeddings[text] = embedding
        
        # Return in original order
        return np.array([cached_embeddings[t] for t in texts])

# Usage
cache = EmbeddingCache(model)
embeddings = cache.encode(large_corpus)  # Automatically caches
```

## Performance Tips

1. **Batch size tuning**: Larger batches = faster throughput but more memory
2. **GPU utilization**: Ensure GPU is not bottlenecked by data transfer
3. **Mixed precision**: Use FP16 for 2x memory savings with minimal quality loss
4. **Pre-tokenization**: For static corpora, cache tokenized inputs
5. **Asynchronous encoding**: Use async/await for web applications

```python
# Mixed precision encoding
import torch
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B", 
                            model_kwargs={"torch_dtype": torch.float16})
embeddings = model.encode(texts)  # Automatically uses FP16
```

## See Also

- [`references/06-semantic-search.md`](06-semantic-search.md) - Using embeddings for search
- [`references/10-optimization.md`](10-optimization.md) - Performance optimization
- [`references/09-deployment-tei.md`](09-deployment-tei.md) - Production deployment
