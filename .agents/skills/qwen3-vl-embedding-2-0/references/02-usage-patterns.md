# Qwen3-VL-Embedding Usage Patterns

## vLLM Integration

vLLM provides high-throughput inference with optimized memory management. Requires vLLM >= 0.14.0.

### Basic vLLM Setup

```python
from vllm import LLM, EngineArgs
import numpy as np

# Initialize vLLM engine
engine_args = EngineArgs(
    model="Qwen/Qwen3-VL-Embedding-2B",
    runner="pooling",  # Required for embedding models
    dtype="bfloat16",
    trust_remote_code=True,
    max_model_len=8192
)

llm = LLM(**vars(engine_args))

# Prepare inputs
inputs = [
    {"text": "A woman playing with her dog on a beach at sunset."},
    {"image": "https://example.com/image.jpg"},
    {"text": "City skyline", "image": "skyline.jpg"}
]

# Generate embeddings
outputs = llm.embed(inputs)
embeddings = np.array([output.outputs.embedding for output in outputs])
```

### vLLM with Images

```python
from vllm.multimodal.utils import fetch_image
from PIL import Image
import os

def prepare_vllm_input(input_dict, llm, instruction="Represent the user's input."):
    """Convert input dict to vLLM format."""
    text = input_dict.get('text', '')
    image = input_dict.get('image')
    
    # Format conversation
    content = []
    if image:
        image_content = None
        if isinstance(image, str):
            if image.startswith(('http', 'https', 'oss')):
                image_content = image  # URL
            elif os.path.exists(image):
                image_content = 'file://' + os.path.abspath(image)  # Local file
        else:
            image_content = image  # PIL Image
        
        if image_content:
            content.append({'type': 'image', 'image': image_content})
    
    if text:
        content.append({'type': 'text', 'text': text})
    
    conversation = [
        {"role": "system", "content": [{"type": "text", "text": instruction}]},
        {"role": "user", "content": content}
    ]
    
    # Apply chat template
    prompt = llm.llm_engine.tokenizer.apply_chat_template(
        conversation, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    # Prepare multi-modal data
    multi_modal_data = None
    if image:
        if isinstance(image, str) and image.startswith(('http', 'https')):
            image_obj = fetch_image(image)
            multi_modal_data = {"image": image_obj}
        elif isinstance(image, str) and os.path.exists(image):
            image_obj = Image.open(image)
            multi_modal_data = {"image": image_obj}
        else:
            multi_modal_data = {"image": image}
    
    return {
        "prompt": prompt,
        "multi_modal_data": multi_modal_data
    }

# Usage
vllm_inputs = [prepare_vllm_input(inp, llm) for inp in inputs]
outputs = llm.embed(vllm_inputs)
```

### vLLM Performance Tuning

```python
engine_args = EngineArgs(
    model="Qwen/Qwen3-VL-Embedding-8B",
    runner="pooling",
    dtype="bfloat16",
    trust_remote_code=True,
    # Memory optimization
    gpu_memory_utilization=0.9,  # Use 90% of GPU memory
    max_num_batched_tokens=8192,  # Max tokens per batch
    max_num_seqs=256,  # Max concurrent sequences
    
    # KV cache optimization
    enable_prefix_caching=True,  # Cache KV for repeated prefixes
    swap_space=4,  # CPU swap space (GB)
    
    # Parallelism (for multi-GPU)
    tensor_parallel_size=1,  # Set to number of GPUs
    
    # Logging
    log_stats=True
)
```

## SGLang Integration

SGLang provides an alternative high-performance inference engine.

### Basic SGLang Setup

```python
from sglang.srt.entrypoints.engine import Engine
import numpy as np

# Initialize SGLang engine
engine = Engine(
    model_path="Qwen/Qwen3-VL-Embedding-2B",
    is_embedding=True,  # Required for embedding mode
    dtype="bfloat16",
    trust_remote_code=True,
    mem_fraction_static=0.9
)

# Prepare inputs
inputs = [
    {"text": "Query text"},
    {"image": "image.jpg"},
    {"text": "Multimodal", "image": "mixed.jpg"}
]

# Convert to SGLang format
def convert_to_sglang(input_dict, engine, instruction="Represent the user's input."):
    text = input_dict.get('text', '')
    image = input_dict.get('image')
    
    content = []
    if image:
        image_content = image if isinstance(image, str) and image.startswith(('http', 'oss')) else 'file://' + os.path.abspath(image)
        content.append({'type': 'image', 'image': image_content})
    if text:
        content.append({'type': 'text', 'text': text})
    
    conversation = [
        {"role": "system", "content": [{"type": "text", "text": instruction}]},
        {"role": "user", "content": content}
    ]
    
    prompt = engine.tokenizer_manager.tokenizer.apply_chat_template(
        conversation, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    result = {"text": prompt}
    if image and isinstance(image, str):
        result["image"] = image
    
    return result

sglang_inputs = [convert_to_sglang(inp, engine) for inp in inputs]

# Generate embeddings
prompts = [inp['text'] for inp in sglang_inputs]
images = [inp.get('image') for inp in sglang_inputs]

results = engine.encode(prompts, image_data=images)
embeddings = np.array([res['embedding'] for res in results])
```

## Batch Processing Patterns

### Simple Batching

```python
def batch_process(model, inputs, batch_size=32):
    """Process inputs in batches."""
    all_embeddings = []
    
    for i in range(0, len(inputs), batch_size):
        batch = inputs[i:i+batch_size]
        batch_embeddings = model.process(batch)
        all_embeddings.append(batch_embeddings)
        
        print(f"Processed batch {i//batch_size + 1}/{(len(inputs)-1)//batch_size + 1}")
    
    return np.concatenate(all_embeddings, axis=0)

# Usage
embeddings = batch_process(model, inputs, batch_size=32)
```

### Async Batch Processing

```python
import asyncio
import aiohttp

async def fetch_and_embed(session, model, url):
    """Fetch image from URL and embed."""
    async with session.get(url) as response:
        image_data = await response.read()
    
    from PIL import Image
    from io import BytesIO
    
    image = Image.open(BytesIO(image_data))
    embedding = model.process([{"image": image}])[0]
    
    return url, embedding

async def batch_embed_urls(model, urls, batch_size=16):
    """Embed multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_embed(session, model, url) for url in urls[:batch_size]]
        results = await asyncio.gather(*tasks)
    
    return dict(results)

# Usage
urls = ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
url_embeddings = asyncio.run(batch_embed_urls(model, urls))
```

### Streaming Batch Processing

```python
from tqdm import tqdm

def streaming_process(model, input_generator, batch_size=32):
    """Process streaming inputs in batches."""
    batch = []
    
    for item in tqdm(input_generator):
        batch.append(item)
        
        if len(batch) >= batch_size:
            embeddings = model.process(batch)
            yield embeddings
            batch = []
    
    # Process remaining items
    if batch:
        embeddings = model.process(batch)
        yield embeddings

# Usage
def data_generator():
    """Generator that yields inputs."""
    for i in range(1000):
        yield {"text": f"Document {i}"}

for batch_embeddings in streaming_process(model, data_generator(), batch_size=32):
    process_batch(batch_embeddings)  # Your processing logic
```

## Production Deployment Patterns

### FastAPI Server

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch

app = FastAPI(title="Qwen3-VL-Embedding API")

# Load model at startup
@app.on_event("startup")
async def load_model():
    global embedder
    embedder = Qwen3VLEmbedder(
        model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2"
    )
    embedder.model.eval()

class EmbedRequest(BaseModel):
    inputs: list[dict]
    instruction: str = "Represent the user's input."
    normalize: bool = True

class EmbedResponse(BaseModel):
    embeddings: list[list[float]]
    shape: list[int]

@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    try:
        # Add instruction to all inputs
        if request.instruction:
            inputs = [{**inp, "instruction": request.instruction} for inp in request.inputs]
        else:
            inputs = request.inputs
        
        # Generate embeddings
        with torch.no_grad():
            embeddings = embedder.process(inputs)
        
        # Normalize if requested
        if request.normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return EmbedResponse(
            embeddings=embeddings.tolist(),
            shape=list(embeddings.shape)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Batch Endpoint for Efficiency

```python
class BatchEmbedRequest(BaseModel):
    queries: list[dict]
    documents: list[dict]
    instruction: str = "Represent the user's input."
    top_k: int = 10

@app.post("/batch-similarity", response_model=dict)
async def batch_similarity(request: BatchEmbedRequest):
    """Compute query-document similarities and return top-k matches."""
    # Generate embeddings for all inputs
    all_inputs = request.queries + request.documents
    embeddings = embedder.process(all_inputs)
    
    # Split into queries and documents
    query_embeddings = embeddings[:len(request.queries)]
    doc_embeddings = embeddings[len(request.queries):]
    
    # Compute similarity matrix
    similarities = query_embeddings @ doc_embeddings.T
    
    # Get top-k for each query
    results = []
    for i, query_sim in enumerate(similarities):
        top_indices = np.argsort(query_sim)[::-1][:request.top_k]
        top_matches = [
            {"doc_index": int(idx), "score": float(query_sim[idx])}
            for idx in top_indices
        ]
        results.append({"query_index": i, "matches": top_matches})
    
    return {"results": results}
```

### Caching Layer

```python
from functools import lru_cache
import hashlib
import json

class EmbeddingCache:
    def __init__(self, model, cache_size=1000):
        self.model = model
        self.cache = {}
        self.max_size = cache_size
    
    def _hash_input(self, input_dict):
        """Create hash of input for caching."""
        # Convert to JSON and hash (handle PIL images by skipping)
        serializable = {
            k: v if k != 'image' else str(id(v)) if hasattr(v, '__hash__') else 'image'
            for k, v in input_dict.items()
        }
        return hashlib.md5(json.dumps(serializable, sort_keys=True).encode()).hexdigest()
    
    def process(self, inputs):
        """Process inputs with caching."""
        embeddings = []
        
        for inp in inputs:
            cache_key = self._hash_input(inp)
            
            if cache_key in self.cache:
                embeddings.append(self.cache[cache_key])
            else:
                # Process single item
                emb = self.model.process([inp])[0]
                self.cache[cache_key] = emb
                embeddings.append(emb)
                
                # Evict oldest if cache full
                if len(self.cache) > self.max_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
        
        return np.array(embeddings)

# Usage
cached_embedder = EmbeddingCache(model, cache_size=1000)
embeddings = cached_embedder.process(inputs)
```

## Vector Database Integration

### FAISS Integration

```python
import faiss

# Create index
dimension = 2048  # For 2B model
index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity

# Generate and add embeddings
document_embeddings = model.process(documents)
document_embeddings = document_embeddings / np.linalg.norm(document_embeddings, axis=1, keepdims=True)
index.add(document_embeddings)

# Search
query_embedding = model.process([query])[0]
query_embedding = query_embedding / np.linalg.norm(query_embedding)
query_embedding = query_embedding.reshape(1, -1)

# Find top-k similar documents
D, I = index.search(query_embedding, k=10)
for score, idx in zip(D[0], I[0]):
    print(f"Document {idx}: similarity={score:.4f}")
```

### ChromaDB Integration

```python
import chromadb
from chromadb.config import Settings

# Initialize ChromaDB
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb",
    persist_directory="./chroma_db"
))

collection = client.create_collection("multimodal_docs")

# Add documents with embeddings
for i, doc in enumerate(documents):
    embedding = model.process([doc])[0]
    collection.add(
        ids=[f"doc_{i}"],
        embeddings=[embedding.tolist()],
        metadatas=[{"text": doc.get('text', ''), 'has_image': 'image' in doc}],
        documents=[doc.get('text', '')]
    )

# Query
query_embedding = model.process([query])[0]
results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=5,
    include=["embeddings", "metadatas", "documents"]
)
```

### Qdrant Integration

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Initialize Qdrant
client = QdrantClient(":memory:")  # Or "http://localhost:6333" for server

# Create collection
client.create_collection(
    collection_name="multimodal",
    vectors_config=VectorParams(size=2048, distance=Distance.COSINE)
)

# Upload documents
from qdrant_client.http.models import PointStruct

points = [
    PointStruct(
        id=i,
        vector=model.process([doc])[0].tolist(),
        payload={"text": doc.get('text', ''), 'has_image': 'image' in doc}
    )
    for i, doc in enumerate(documents)
]

client.upsert(collection_name="multimodal", points=points)

# Search
query_vector = model.process([query])[0]
results = client.search(
    collection_name="multimodal",
    query_vector=query_vector.tolist(),
    limit=10
)
```

## Monitoring and Logging

```python
import time
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def timed_operation(name):
    """Context manager for timing operations."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"{name} completed in {duration:.3f}s")

def monitor_embedding_performance(model, inputs, num_runs=5):
    """Benchmark embedding performance."""
    times = []
    
    for i in range(num_runs):
        with timed_operation(f"Run {i+1}"):
            start = time.time()
            _ = model.process(inputs)
            times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    throughput = len(inputs) / avg_time
    
    logger.info(f"Average latency: {avg_time*1000:.2f}ms")
    logger.info(f"Throughput: {throughput:.2f} items/second")
    logger.info(f"P99 latency: {sorted(times)[-1]*1000:.2f}ms")
    
    return {"avg_latency": avg_time, "throughput": throughput}
```
