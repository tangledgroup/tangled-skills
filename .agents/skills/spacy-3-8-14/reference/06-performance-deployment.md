# Performance Optimization and Deployment

This guide covers performance optimization, GPU processing, batch processing, serialization, and deploying spaCy models in production.

## Performance Benchmarks

### Model Size vs Speed vs Accuracy

| Model | Size | Speed (docs/sec) | NER F1 | Use Case |
|-------|------|------------------|--------|----------|
| `en_core_web_sm` | ~13MB | 20,000+ | 85% | Fast processing, basic tasks |
| `en_core_web_md` | ~45MB | 15,000+ | 87% | Balanced speed/accuracy |
| `en_core_web_lg` | ~800MB | 8,000+ | 89% | Maximum accuracy needed |
| `en_core_web_trf` | ~650MB | 2,000+ | 91% | Complex domains, transformers |

### Benchmarking Your Setup

```python
import spacy
import time

nlp = spacy.load("en_core_web_sm")

# Test documents
texts = ["This is a sample document for benchmarking."] * 1000

# Single document processing
start = time.time()
for text in texts:
    doc = nlp(text)
single_time = time.time() - start
print(f"Single processing: {len(texts) / single_time:.0f} docs/sec")

# Batch processing with pipe
start = time.time()
for doc in nlp.pipe(texts, batch_size=32):
    pass
batch_time = time.time() - start
print(f"Batch processing: {len(texts) / batch_time:.0f} docs/sec")
```

## Batch Processing

### Using `nlp.pipe()`

The most important optimization is using `pipe()` for batch processing:

```python
import spacy

nlp = spacy.load("en_core_web_sm")

texts = ["Document text"] * 10000

# WRONG: Slow - processes one at a time
for text in texts:
    doc = nlp(text)
    process(doc)

# RIGHT: Fast - batch processing
for doc in nlp.pipe(texts, batch_size=32):
    process(doc)

# Even faster with multiple workers
for doc in nlp.pipe(texts, batch_size=32, n_threads=4):
    process(doc)
```

### Optimal Batch Sizes

Different models and hardware have different optimal batch sizes:

```python
# Test different batch sizes
def benchmark_batch_size(nlp, texts, batch_sizes=[8, 16, 32, 64, 128]):
    results = {}
    
    for batch_size in batch_sizes:
        start = time.time()
        list(nlp.pipe(texts, batch_size=batch_size))
        elapsed = time.time() - start
        
        docs_per_sec = len(texts) / elapsed
        results[batch_size] = docs_per_sec
        print(f"Batch size {batch_size}: {docs_per_sec:.0f} docs/sec")
    
    return results

nlp = spacy.load("en_core_web_sm")
texts = ["Sample text"] * 1000
benchmark_batch_size(nlp, texts)
```

Typical optimal batch sizes:
- Small models (`_sm`): 32-64
- Medium models (`_md`): 16-32
- Large models (`_lg`): 8-16
- Transformer models: 4-16 (GPU), 2-8 (CPU)

## Multi-Processing and Parallelization

### Using Multiple CPU Cores

```python
import spacy
from spacy.util import minibatch
import multiprocessing as mp

def process_batch(texts, model_path):
    """Process a batch of texts in a separate process"""
    nlp = spacy.load(model_path)
    return [nlp(text) for text in texts]

# Split work across processes
texts = ["Document text"] * 10000
num_workers = mp.cpu_count()

# Divide texts into chunks
chunk_size = len(texts) // num_workers
chunks = [texts[i:i + chunk_size] for i in range(0, len(texts), chunk_size)]

# Process in parallel
with mp.Pool(num_workers) as pool:
    results = pool.map(lambda chunk: process_batch(chunk, "en_core_web_sm"), chunks)

# Flatten results
all_docs = [doc for batch in results for doc in batch]
```

### Using `nlp.pipe()` with Multiple Threads

```python
nlp = spacy.load("en_core_web_sm")

# Use multiple threads for I/O-bound processing
for doc in nlp.pipe(texts, batch_size=32, n_threads=4):
    process(doc)  # If process() does I/O, this helps
```

Note: Python's GIL limits CPU-bound parallelization. For true parallelism, use multiprocessing or GPU.

## GPU Acceleration

### Checking GPU Availability

```python
import thinc.api

# Check if GPU is available
if thinc.xp.gpu_allocator is not None:
    print(f"GPU available: {thinc.xp.gpu_allocator}")
else:
    print("No GPU available")

# Check CUDA devices
import torch
if torch.cuda.is_available():
    print(f"CUDA devices: {torch.cuda.device_count()}")
    print(f"Current device: {torch.cuda.current_device()}")
```

### Using GPU with Transformers

```python
import spacy
import thinc.api

# Set GPU allocator
thinc.xp.set_gpu_allocator("pytorch")

# Load transformer model (automatically uses GPU if available)
nlp = spacy.load("en_core_web_trf")

# Process text - transformer operations run on GPU
doc = nlp("This will use GPU for transformer encoding")

# Verify GPU usage
import torch
if hasattr(doc._., "trf_data"):
    print(f"Transformer data on GPU: {doc._.trf_data[0].is_cuda}")
```

### Multi-GPU Setup

For very large-scale processing, you can distribute across multiple GPUs:

```python
import torch
import spacy

# Set specific GPU
torch.cuda.set_device(0)
nlp_gpu0 = spacy.load("en_core_web_trf")

torch.cuda.set_device(1)
nlp_gpu1 = spacy.load("en_core_web_trf")

# Split work across GPUs
texts_even = texts[::2]
texts_odd = texts[1::2]

docs_even = list(nlp_gpu0.pipe(texts_even))
docs_odd = list(nlp_gpu1.pipe(texts_odd))

# Merge results (interleave)
all_docs = []
for d1, d2 in zip(docs_even, docs_odd):
    all_docs.extend([d1, d2])
```

## Serialization and Model Packaging

### Saving Models

```python
import spacy

nlp = spacy.load("en_core_web_sm")

# Save to directory
nlp.to_disk("./my_model")

# Load later
nlp = spacy.load("./my_model")

# Save as bytes (for in-memory transfer)
bytes_data = nlp.to_bytes()
nlp.from_bytes(bytes_data)

# Save with metadata
nlp.meta["name"] = "my_custom_model"
nlp.meta["version"] = "1.0.0"
nlp.to_disk("./my_model")
```

### Model Compression

Reduce model size for deployment:

```python
import spacy
from spacy.util import minibatch

nlp = spacy.load("en_core_web_sm")

# Remove unnecessary components
nlp.remove_pipe("lemmatizer")
nlp.remove_pipe("parser")

# Save reduced model
nlp.to_disk("./my_model_minimal")

# Check size difference
import os
def get_dir_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            total += os.path.getsize(filepath)
    return total / (1024 * 1024)  # MB

print(f"Full model: {get_dir_size('en_core_web_sm'):.1f}MB")
print(f"Minimal model: {get_dir_size('my_model_minimal'):.1f}MB")
```

### Packaging for Distribution

Create a distributable model package:

```python
# Create model package structure
import shutil
import os

model_name = "my_custom_model"
version = "1.0.0"

# Create package directory
package_dir = f"{model_name}-{version}"
os.makedirs(package_dir)

# Copy trained model
shutil.copytree("./trained_model", f"{package_dir}/{model_name}")

# Create metadata
metadata = {
    "name": model_name,
    "version": version,
    "spacy_version": ">=3.0,<4.0",
    "description": "Custom NER model for domain X",
    "author": "Your Name",
    "email": "your@email.com",
    "url": "https://example.com",
    "license": "MIT"
}

# Save metadata
import srsly
srsly.write_json(f"{package_dir}/META.json", metadata)

# Create README
with open(f"{package_dir}/README.md", "w") as f:
    f.write(f"# {model_name}\n\nCustom NLP model for specific domain.\n")

# Create setup.py
setup_py = f'''from setuptools import setup

setup(
    name="{model_name}",
    version="{version}",
    description="Custom NLP model",
    author="Your Name",
    install_requires=["spacy>=3.0,<4.0"],
    package_data={{"{model_name}": ["*.json", "*.cfg", "*.txt"]}},
    entry_points="""
    [spacy_factories]
    """,
)
'''

with open(f"{package_dir}/setup.py", "w") as f:
    f.write(setup_py)

# Build wheel
os.system(f"cd {package_dir} && pip install build && python -m build --wheel")
```

## Deployment Patterns

### REST API with FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy

app = FastAPI(title="spaCy NLP API")
nlp = spacy.load("en_core_web_sm")

class TextRequest(BaseModel):
    text: str
    tasks: list = ["ner", "pos", "dependencies"]

@app.post("/analyze")
async def analyze_text(request: TextRequest):
    doc = nlp(request.text)
    
    result = {"text": request.text}
    
    if "ner" in request.tasks:
        result["entities"] = [
            {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
            for ent in doc.ents
        ]
    
    if "pos" in request.tasks:
        result["tokens"] = [
            {"text": token.text, "pos": token.pos_, "lemma": token.lemma_}
            for token in doc
        ]
    
    return result

@app.post("/batch")
async def batch_analyze(requests: list[TextRequest]):
    texts = [req.text for req in requests]
    docs = list(nlp.pipe(texts, batch_size=32))
    
    results = []
    for req, doc in zip(requests, docs):
        result = {"text": req.text}
        if "ner" in req.tasks:
            result["entities"] = [
                {"text": ent.text, "label": ent.label_}
                for ent in doc.ents
            ]
        results.append(result)
    
    return results

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Download model (or copy trained model)
RUN python -m spacy download en_core_web_sm

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  spacy-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 2G
        reservations:
          cpus: '2'
          memory: 1G
    restart: unless-stopped
```

### Kubernetes Deployment

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spacy-nlp-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spacy-nlp
  template:
    metadata:
      labels:
        app: spacy-nlp
    spec:
      containers:
      - name: spacy-api
        image: your-registry/spacy-nlp:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: WORKERS
          value: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: spacy-nlp-service
spec:
  selector:
    app: spacy-nlp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Caching Strategies

### Document Caching

```python
from functools import lru_cache
import spacy

nlp = spacy.load("en_core_web_sm")

@lru_cache(maxsize=1000)
def process_cached(text):
    """Cache results for repeated texts"""
    doc = nlp(text)
    return {
        "entities": [(ent.text, ent.label_) for ent in doc.ents],
        "pos": [(token.text, token.pos_) for token in doc]
    }

# First call processes text
result1 = process_cached("Hello world")

# Second call returns cached result (much faster)
result2 = process_cached("Hello world")
```

### Pipeline Component Caching

```python
class CachedPipeline:
    def __init__(self, nlp, cache_size=100):
        self.nlp = nlp
        self.cache = {}
        self.cache_size = cache_size
    
    def process(self, text):
        # Simple hash-based caching
        text_hash = hash(text)
        
        if text_hash in self.cache and len(self.cache) < self.cache_size:
            return self.cache[text_hash]
        
        doc = self.nlp(text)
        self.cache[text_hash] = doc
        return doc

# Usage
cached_nlp = CachedPipeline(nlp)
doc = cached_nlp.process("Repeated text")
```

## Monitoring and Logging

### Performance Monitoring

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(operation_name):
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{operation_name}: {elapsed:.3f}s")

nlp = spacy.load("en_core_web_sm")

with timer("Model loading"):
    pass  # Already loaded above

texts = ["Sample text"] * 1000

with timer("Batch processing"):
    list(nlp.pipe(texts, batch_size=32))
```

### Logging Pipeline Execution

```python
import logging
from spacy.pipeline import Pipe

# Enable spaCy logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spacy")

# Custom logging wrapper
class LoggingPipeline:
    def __init__(self, nlp):
        self.nlp = nlp
    
    def pipe(self, texts, **kwargs):
        logger.info(f"Processing {len(texts)} documents")
        
        start = time.time()
        count = 0
        
        for doc in self.nlp.pipe(texts, **kwargs):
            count += 1
            if count % 100 == 0:
                elapsed = time.time() - start
                rate = count / elapsed if elapsed > 0 else 0
                logger.info(f"Processed {count} docs ({rate:.0f} docs/sec)")
        
        total_time = time.time() - start
        logger.info(f"Total: {len(texts)} docs in {total_time:.2f}s "
                   f"({len(texts) / total_time:.0f} docs/sec)")
        
        yield from self.nlp.pipe(texts, **kwargs)
```

## Memory Optimization

### Reducing Memory Footprint

```python
import spacy

# Load only needed components
nlp = spacy.load("en_core_web_sm", exclude=["parser", "lemmatizer"])

# Process one at a time and delete immediately
for text in texts:
    doc = nlp(text)
    result = extract_info(doc)  # Extract what you need
    del doc  # Free memory immediately
    process(result)

# Force garbage collection periodically
import gc
if i % 1000 == 0:
    gc.collect()
```

### Streaming Large Files

```python
def process_large_file(filename, nlp):
    """Process text file line by line without loading entire file"""
    with open(filename, 'r', encoding='utf-8') as f:
        batch = []
        
        for line in f:
            batch.append(line.strip())
            
            if len(batch) >= 32:  # Process in batches
                for doc in nlp.pipe(batch):
                    yield process(doc)
                batch = []
        
        # Process remaining
        if batch:
            for doc in nlp.pipe(batch):
                yield process(doc)

# Usage
nlp = spacy.load("en_core_web_sm")
for result in process_large_file("large_text_file.txt", nlp):
    handle(result)
```

## Troubleshooting Performance Issues

### Slow Model Loading

```python
# Cache the loaded model
import spacy

# Load once at application startup
nlp = spacy.load("en_core_web_sm")

# Reuse across requests/operations
# Don't reload in loops or request handlers
```

### High Memory Usage

```python
# Use smaller models
nlp = spacy.load("en_core_web_sm")  # Instead of _lg or _trf

# Remove unused components
nlp.remove_pipe("lemmatizer")

# Process in smaller batches
for doc in nlp.pipe(texts, batch_size=8):  # Smaller batch size
    process(doc)
```

### Out of GPU Memory

```python
import torch

# Check GPU memory
print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.0f} MB")
print(f"GPU memory reserved: {torch.cuda.memory_reserved() / 1024**2:.0f} MB")

# Reduce batch size for transformers
for doc in nlp.pipe(texts, batch_size=4):  # Very small batches
    process(doc)

# Clear GPU cache periodically
torch.cuda.empty_cache()
```

## References

- [Performance Benchmarks](https://spacy.io/usage/facts-figures)
- [GPU Processing Guide](https://spacy.io/usage#gpu)
- [Memory Management](https://spacy.io/usage/memory-management)
- [Saving & Loading](https://spacy.io/usage/saving-loading)
- [Deployment Best Practices](https://spacy.io/usage#deployment)
