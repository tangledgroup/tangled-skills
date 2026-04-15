# Performance Optimization

Techniques for optimizing Qwen3 Embedding model performance including quantization, ONNX export, GPU optimization, and caching strategies.

## Quantization

### FP16 (Half Precision)

```python
import torch
from sentence_transformers import SentenceTransformer

# Load model in FP16
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-8B",
    device="cuda",
    model_kwargs={"torch_dtype": torch.float16}
)

# Memory usage: ~50% of FP32
# Quality loss: Minimal (<1%)
```

### INT8 Quantization

```python
from sentence_transformers import SentenceTransformer
import torch

# Load and quantize to INT8
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
model = model.half()  # First convert to FP16

# Dynamic quantization (PyTorch)
model.model = torch.quantization.quantize_dynamic(
    model.model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Memory usage: ~25% of FP32
# Quality loss: Small (1-3%)
```

### Using bitsandbytes (4-bit/8-bit)

```python
import torch
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import SentenceTransformer

# Load with 4-bit quantization
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-8B",
    model_kwargs={
        "load_in_4bit": True,
        "bnb_4bit_compute_dtype": torch.float16,
        "bnb_4bit_use_double_quant": True
    }
)

# Memory usage: ~25% of FP32 (4-bit)
# Best for: 8B model on consumer GPUs
```

## ONNX Export

### Export to ONNX

```python
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Export to ONNX
dynamic_axes = {
    "input_ids": {0: "batch_size", 1: "seq_len"},
    "attention_mask": {0: "batch_size", 1: "seq_len"}
}

torch.onnx.export(
    model.model,
    (torch.randint(0, 1000, (1, 512)), torch.ones((1, 512), dtype=torch.long)),
    "qwen3-embedding.onnx",
    dynamic_axes=dynamic_axes,
    input_names=["input_ids", "attention_mask"],
    output_names=["last_hidden_state"],
    opset_version=14
)

print("Model exported to ONNX")
```

### Using ONNX Runtime

```python
import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession("qwen3-embedding.onnx")

# Prepare input
input_ids = np.array([[101, 20546, 20037, 102]], dtype=np.int64)
attention_mask = np.array([[1, 1, 1, 1]], dtype=np.int64)

# Run inference
outputs = session.run(
    None,
    {
        "input_ids": input_ids,
        "attention_mask": attention_mask
    }
)

embedding = outputs[0]
print(f"Embedding shape: {embedding.shape}")
```

### ONNX with GPU

```python
# Create GPU session
session = ort.InferenceSession(
    "qwen3-embedding.onnx",
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

# Same API, automatic GPU acceleration
```

## GPU Optimization

### Multi-GPU Setup

```python
from sentence_transformers import SentenceTransformer
import torch

# Load model on specific GPU
model = SentenceTransformer("Qwen/Qwen3-Embedding-8B", device="cuda:0")

# For very large batches, use data parallelism
if torch.cuda.device_count() > 1:
    model = torch.nn.DataParallel(model)
```

### CUDA Graphs (Advanced)

```python
import torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B", device="cuda")

# Warmup
_ = model.encode(["warmup"] * 32)

# Capture CUDA graph for consistent batch sizes
@torch.cuda.graph()
def encoded_batch():
    return model.encode(["template"] * 32)

# Use captured graph for faster inference
```

### Memory Optimization

```python
import torch
from sentence_transformers import SentenceTransformer

# Enable gradient checkpointing (for fine-tuning)
model = SentenceTransformer("Qwen/Qwen3-Embedding-8B")
model.model.gradient_checkpointing_enable()

# Use mixed precision with AMP
with torch.cuda.amp.autocast():
    embeddings = model.encode(large_batch_of_texts)
```

## Caching Strategies

### Embedding Cache

```python
import hashlib
import pickle
from pathlib import Path
import numpy as np

class EmbeddingCache:
    def __init__(self, cache_dir="embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.index_file = self.cache_dir / "index.pkl"
        
        # Load or create index
        if self.index_file.exists():
            with open(self.index_file, 'rb') as f:
                self.hash_to_path = pickle.load(f)
        else:
            self.hash_to_path = {}
    
    def _hash_text(self, text):
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    def get(self, text):
        """Get cached embedding if exists"""
        text_hash = self._hash_text(text)
        
        if text_hash in self.hash_to_path:
            cache_file = self.cache_dir / f"{text_hash}.npy"
            if cache_file.exists():
                return np.load(cache_file)
        
        return None
    
    def set(self, text, embedding):
        """Cache an embedding"""
        text_hash = self._hash_text(text)
        cache_file = self.cache_dir / f"{text_hash}.npy"
        
        np.save(cache_file, embedding)
        self.hash_to_path[text_hash] = str(cache_file)
        
        # Save index
        with open(self.index_file, 'wb') as f:
            pickle.dump(self.hash_to_path, f)
    
    def encode_with_cache(self, model, texts, batch_size=32):
        """Encode texts with automatic caching"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = []
            
            for text in batch:
                cached = self.get(text)
                if cached is not None:
                    batch_embeddings.append(cached)
                else:
                    batch_embeddings.append(None)
            
            # Encode uncached texts
            to_encode = [text for text, emb in zip(batch, batch_embeddings) if emb is None]
            
            if to_encode:
                new_embeddings = model.encode(to_encode)
                
                # Cache and collect results
                idx = 0
                for text, emb in zip(batch, batch_embeddings):
                    if emb is None:
                        self.set(text, new_embeddings[idx])
                        batch_embeddings[idx] = new_embeddings[idx]
                        idx += 1
            
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)

# Usage
cache = EmbeddingCache()
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# First run: slow (no cache)
embeddings1 = cache.encode_with_cache(model, documents)

# Second run: fast (from cache)
embeddings2 = cache.encode_with_cache(model, documents)
```

### LRU Cache for Recent Queries

```python
from functools import lru_cache
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

@lru_cache(maxsize=1000)
def encode_cached(text):
    """Cache recent encodings with LRU eviction"""
    return tuple(model.encode([text])[0])  # Convert to tuple for hashing

# Usage
embedding = np.array(encode_cached("Frequently queried text"))
```

## Batch Processing Optimization

### Optimal Batch Size Detection

```python
import time
import numpy as np
from sentence_transformers import SentenceTransformer

def find_optimal_batch_size(model, sample_texts, batch_sizes=[8, 16, 32, 64, 128]):
    """Find optimal batch size for throughput"""
    
    results = []
    for batch_size in batch_sizes:
        # Time multiple batches
        times = []
        for _ in range(5):
            start = time.time()
            embeddings = model.encode(sample_texts, batch_size=batch_size)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = np.mean(times)
        throughput = len(sample_texts) / avg_time
        
        results.append({
            'batch_size': batch_size,
            'avg_time': avg_time,
            'throughput': throughput
        })
        
        print(f"Batch size {batch_size}: {throughput:.1f} docs/sec")
    
    # Return best batch size
    best = max(results, key=lambda x: x['throughput'])
    return best['batch_size'], results

# Usage
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
sample_texts = ["Sample text for benchmarking."] * 1000

optimal_bs, all_results = find_optimal_batch_size(model, sample_texts)
print(f"\nOptimal batch size: {optimal_bs}")
```

### Streaming Large Corpora

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def stream_encode(model, text_generator, batch_size=32):
    """Encode texts from a generator in batches"""
    
    batch = []
    for text in text_generator:
        batch.append(text)
        
        if len(batch) >= batch_size:
            embeddings = model.encode(batch)
            for emb in embeddings:
                yield emb
            batch = []
    
    # Encode remaining texts
    if batch:
        embeddings = model.encode(batch)
        for emb in embeddings:
            yield emb

# Usage
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

def read_large_file(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield line.strip()

# Stream encoding without loading all into memory
for embedding in stream_encode(model, read_large_file("large_corpus.txt")):
    # Process each embedding (e.g., save to vector DB)
    pass
```

## Profiling and Benchmarking

### Performance Profiling

```python
import torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B", device="cuda")

# Profile with PyTorch profiler
texts = ["Sample text for profiling."] * 100

with torch.profiler.profile(
    activities=[torch.profiler.ProfilerActivity.CPU, 
                torch.profiler.ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True
) as prof:
    embeddings = model.encode(texts)

# Print profiling summary
print(prof.key_averages().table(
    sort_by="cpu_time_total", 
    row_limit=10
))
```

### Latency Benchmarking

```python
import time
import numpy as np
from sentence_transformers import SentenceTransformer

def benchmark_latency(model, texts, num_runs=10):
    """Benchmark inference latency"""
    
    latencies = []
    for _ in range(num_runs):
        # Warmup
        if _ == 0:
            model.encode(texts[:1])
            continue
        
        start = time.perf_counter()
        model.encode(texts)
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)  # Convert to ms
    
    latencies = np.array(latencies)
    
    print(f"Latency statistics:")
    print(f"  Mean: {latencies.mean():.2f} ms")
    print(f"  P50: {np.percentile(latencies, 50):.2f} ms")
    print(f"  P95: {np.percentile(latencies, 95):.2f} ms")
    print(f"  P99: {np.percentile(latencies, 99):.2f} ms")

# Usage
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B", device="cuda")
benchmark_latency(model, ["Test text."] * 32)
```

## See Also

- [`references/09-deployment-tei.md`](09-deployment-tei.md) - Production deployment
- [`references/01-model-variants.md`](01-model-variants.md) - Model selection for performance
- [`references/03-embedding-generation.md`](03-embedding-generation.md) - Encoding options
