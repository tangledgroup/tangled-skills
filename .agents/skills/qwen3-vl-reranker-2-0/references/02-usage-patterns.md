# Qwen3-VL-Reranker Usage Patterns

This reference document covers advanced usage patterns, deployment strategies, and production-ready implementations for Qwen3-VL-Reranker.

## vLLM Integration

vLLM provides high-throughput inference with optimized memory management and batch processing.

### Installation

```bash
pip install "vllm>=0.6.0"
```

### Basic vLLM Setup

```python
from vllm import LLM, EngineArgs
from pathlib import Path

# Initialize vLLM engine with reranker configuration
engine_args = EngineArgs(
    model="Qwen/Qwen3-VL-Reranker-2B",
    runner="pooling",  # Required for reranking models
    dtype="bfloat16",
    trust_remote_code=True,
    hf_overrides={
        "architectures": ["Qwen3VLForSequenceClassification"],
        "classifier_from_token": ["no", "yes"],
        "is_original_qwen3_reranker": True,
    },
    gpu_memory_utilization=0.9,
    max_num_batched_tokens=4096,
    max_num_seqs=256,
)

llm = LLM(**vars(engine_args))

# Load chat template
template_path = Path("path/to/qwen3_vl_reranker.jinja")
chat_template = template_path.read_text() if template_path.exists() else None

# Score query-document pairs
query_text = "A woman playing with her dog on a beach at sunset."
doc_content = {
    "content": [
        {"type": "text", "text": "A woman shares a joyful moment with her golden retriever..."}
    ]
}

outputs = llm.score(query_text, doc_content, chat_template=chat_template)
score = outputs[0].outputs.score
print(f"Relevance score: {score}")
```

### Batch Scoring with vLLM

```python
from typing import Dict, Any
from vllm.entrypoints.score_utils import ScoreMultiModalParam

def format_document_to_score_param(doc_dict: Dict[str, Any]) -> ScoreMultiModalParam:
    """Convert document dictionary to vLLM ScoreMultiModalParam."""
    content = []
    
    text = doc_dict.get('text')
    image = doc_dict.get('image')
    
    if text:
        content.append({"type": "text", "text": text})
    
    if image:
        image_url = image
        # Handle local file paths
        if isinstance(image, str) and not image.startswith(('http', 'https', 'oss')):
            import os
            abs_image_path = os.path.abspath(image)
            image_url = 'file://' + abs_image_path
        
        content.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })
    
    if not content:
        content.append({"type": "text", "text": ""})
    
    return {"content": content}

# Batch scoring
queries = [
    {"text": "A woman playing with her dog on a beach."},
    {"text": "City skyline at night."}
]

documents = [
    {"text": "Beach scene with woman and dog...", "image": "beach.jpg"},
    {"text": "Urban architecture...", "image": "city.jpg"},
    {"text": "Indoor dog training..."}
]

results = []
for query_dict in queries:
    query_text = query_dict.get('text', '')
    scores = []
    
    for doc_dict in documents:
        doc_param = format_document_to_score_param(doc_dict)
        outputs = llm.score(query_text, doc_param, chat_template=chat_template)
        scores.append(outputs[0].outputs.score)
    
    results.append((query_text, scores))

for query, scores in results:
    print(f"Query: {query[:50]}...")
    print(f"Scores: {scores}")
```

### Async vLLM for Production

```python
from vllm import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
import asyncio

async_engine_args = AsyncEngineArgs(
    model="Qwen/Qwen3-VL-Reranker-2B",
    runner="pooling",
    dtype="bfloat16",
    trust_remote_code=True,
    hf_overrides={
        "architectures": ["Qwen3VLForSequenceClassification"],
        "classifier_from_token": ["no", "yes"],
        "is_original_qwen3_reranker": True,
    },
    max_num_batched_tokens=8192,
    max_num_seqs=512,
)

engine = AsyncLLMEngine.from_engine_args(async_engine_args)

async def rerank_async(query: str, documents: list):
    """Async reranking for production use."""
    results = []
    
    async for output in engine.score(
        query,
        [format_document_to_score_param(doc) for doc in documents],
        chat_template=chat_template
    ):
        results.append(output.outputs.score)
    
    return results

# Usage in async context
async def main():
    scores = await rerank_async("query text", documents)
    print(scores)

asyncio.run(main())
```

## SGLang Deployment

SGLang provides another high-performance inference option with structured generation support.

### Installation

```bash
pip install sglang
```

### Basic SGLang Setup

```python
import sglang as sgl
from sglang import function, system, user, assistant, gen

# Launch SGLang server
# sglaunch --model Qwen/Qwen3-VL-Reranker-2B --port 30000

# Connect to server
sgl.set_default_backend(sgl.RuntimeEndpoint("http://localhost:30000"))

@function
def rerank_func(prompt):
    return prompt + "Relevance score: " + gen("score", max_tokens=10)

# Run inference
state = rerank_func("Query: beach scene\nDocument: woman with dog at beach").run()
score_text = state["score"]
```

## Batch Processing Strategies

### Sequential Batching

Process documents in batches to manage memory:

```python
def batch_reranking(model, query: dict, documents: list, batch_size: int = 32):
    """Process documents in batches to control memory usage."""
    all_scores = []
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        
        batch_inputs = {
            "instruction": "Retrieve relevant content.",
            "query": query,
            "documents": batch_docs
        }
        
        batch_scores = model.process(batch_inputs)
        all_scores.extend(batch_scores)
    
    return all_scores

# Usage
scores = batch_reranking(
    model,
    query={"text": "search query"},
    documents=large_document_list,
    batch_size=32
)
```

### Parallel Batching

Use multiprocessing for CPU-bound preprocessing:

```python
from concurrent.futures import ProcessPoolExecutor
import torch

def process_single_query_doc(query: dict, doc: dict, model_path: str):
    """Process single query-document pair (for multiprocessing)."""
    model = Qwen3VLReranker(model_name_or_path=model_path)
    
    inputs = {
        "instruction": "Evaluate relevance.",
        "query": query,
        "documents": [doc]
    }
    
    score = model.process(inputs)[0]
    return score

def parallel_reranking(query: dict, documents: list, model_path: str, num_workers: int = 4):
    """Parallel reranking across multiple CPU cores."""
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        scores = list(executor.map(
            lambda doc: process_single_query_doc(query, doc, model_path),
            documents
        ))
    
    return scores
```

## Production Patterns

### Caching Strategy

Cache embeddings for static document corpora:

```python
import hashlib
import pickle
from pathlib import Path

class RerankerCache:
    def __init__(self, cache_dir: str = "./rerank_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, query: dict, document: dict) -> str:
        """Generate unique key for query-document pair."""
        content = f"{str(query)}|{str(document)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, query: dict, document: dict) -> float | None:
        """Retrieve cached score if available."""
        cache_key = self._get_cache_key(query, document)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, query: dict, document: dict, score: float):
        """Cache the reranking score."""
        cache_key = self._get_cache_key(query, document)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        with open(cache_file, 'wb') as f:
            pickle.dump(score, f)

# Usage
cache = RerankerCache()

def cached_rerank(model, query: dict, documents: list):
    scores = []
    
    for doc in documents:
        cached_score = cache.get(query, doc)
        
        if cached_score is not None:
            scores.append(cached_score)
        else:
            inputs = {"instruction": "Retrieve relevant content.", "query": query, "documents": [doc]}
            score = model.process(inputs)[0]
            scores.append(score)
            cache.set(query, doc, score)
    
    return scores
```

### Rate Limiting and Throttling

Control request rate to prevent overload:

```python
import time
from collections import deque
from threading import Lock

class RateLimiter:
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.timestamps = deque()
        self.lock = Lock()
    
    def acquire(self):
        """Wait until rate limit allows proceeding."""
        with self.lock:
            now = time.time()
            
            # Remove old timestamps outside the window
            while self.timestamps and self.timestamps[0] <= now - self.time_window:
                self.timestamps.popleft()
            
            # If at limit, wait
            if len(self.timestamps) >= self.max_requests:
                sleep_time = self.time_window - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.timestamps.popleft()
            
            self.timestamps.append(time.time())

# Usage: 100 requests per second
rate_limiter = RateLimiter(max_requests=100, time_window=1.0)

def rate_limited_rerank(model, query: dict, documents: list):
    for doc in documents:
        rate_limiter.acquire()
        
        inputs = {"instruction": "Retrieve relevant content.", "query": query, "documents": [doc]}
        score = model.process(inputs)[0]
        
        # Process score...
```

### Monitoring and Metrics

Track performance metrics for production systems:

```python
import time
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class RerankingMetrics:
    total_requests: int = 0
    total_latency_ms: float = 0.0
    scores: List[float] = None
    
    def __post_init__(self):
        if self.scores is None:
            self.scores = []
    
    def record(self, latency_ms: float, score: float):
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        self.scores.append(score)
    
    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.total_requests if self.total_requests > 0 else 0
    
    @property
    def score_distribution(self) -> dict:
        if not self.scores:
            return {}
        
        scores = np.array(self.scores)
        return {
            "mean": float(np.mean(scores)),
            "std": float(np.std(scores)),
            "min": float(np.min(scores)),
            "max": float(np.max(scores)),
            "p50": float(np.percentile(scores, 50)),
            "p95": float(np.percentile(scores, 95)),
            "p99": float(np.percentile(scores, 99))
        }

# Usage
metrics = RerankingMetrics()

def monitored_rerank(model, query: dict, documents: list):
    start_time = time.time()
    
    inputs = {"instruction": "Retrieve relevant content.", "query": query, "documents": documents}
    scores = model.process(inputs)
    
    latency_ms = (time.time() - start_time) * 1000
    
    for score in scores:
        metrics.record(latency_ms / len(scores), score)
    
    print(f"Avg latency: {metrics.avg_latency_ms:.2f}ms")
    print(f"Score distribution: {metrics.score_distribution}")
    
    return scores
```

## API Integration Patterns

### FastAPI Endpoint

Expose reranking as REST API:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Qwen3-VL-Reranker API")

# Load model once at startup
reranker = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)

class Document(BaseModel):
    text: Optional[str] = None
    image: Optional[str] = None
    video: Optional[str] = None

class RerankRequest(BaseModel):
    instruction: str = "Retrieve relevant content."
    query: Document
    documents: List[Document]
    top_k: Optional[int] = None

class RerankResponse(BaseModel):
    results: List[dict]
    metadata: dict

@app.post("/rerank", response_model=RerankResponse)
async def rerank(request: RerankRequest):
    try:
        # Convert Pydantic models to dicts
        inputs = {
            "instruction": request.instruction,
            "query": request.query.model_dump(),
            "documents": [doc.model_dump() for doc in request.documents]
        }
        
        scores = reranker.process(inputs)
        
        # Combine documents with scores
        results = []
        for doc, score in zip(request.documents, scores):
            result = doc.model_dump()
            result["relevance_score"] = float(score)
            results.append(result)
        
        # Sort by score and apply top_k
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        if request.top_k:
            results = results[:request.top_k]
        
        return RerankResponse(
            results=results,
            metadata={
                "total_documents": len(request.documents),
                "returned_results": len(results)
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2
```

### gRPC Service

High-performance RPC interface:

```python
import grpc
from concurrent import futures
import reranker_pb2
import reranker_pb2_grpc

class RerankerServicer(reranker_pb2_grpc.RerankerServicer):
    def __init__(self):
        self.model = Qwen3VLReranker(
            model_name_or_path="Qwen/Qwen3-VL-Reranker-2B"
        )
    
    def Rerank(self, request, context):
        try:
            # Convert gRPC request to model input
            inputs = {
                "instruction": request.instruction,
                "query": {"text": request.query.text},
                "documents": [{"text": doc.text} for doc in request.documents]
            }
            
            scores = self.model.process(inputs)
            
            # Build response
            results = []
            for doc, score in zip(request.documents, scores):
                results.append(reranker_pb2.RerankResult(
                    document=doc,
                    score=float(score)
                ))
            
            return reranker_pb2.RerankResponse(results=results)
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return reranker_pb2.RerankResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reranker_pb2_grpc.add_RerankerServicer_to_server(RerankerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

## Optimization Techniques

### Gradient Checkpointing

Reduce memory usage during fine-tuning:

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./reranker_finetune",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,  # Enable gradient checkpointing
    fp16=False,
    bf16=True,
    logging_steps=10,
    save_steps=500,
)
```

### Flash Attention Optimization

Maximize inference speed:

```python
import torch
from transformers import AutoConfig

# Check if Flash Attention 2 is available
def is_flash_attn_2_available():
    try:
        from flash_attn import flash_attn_func
        return True
    except ImportError:
        return False

if is_flash_attn_2_available():
    model = Qwen3VLReranker(
        model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2"  # Enable Flash Attention 2
    )
else:
    print("Flash Attention 2 not available, using standard attention")
    model = Qwen3VLReranker(
        model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
        torch_dtype=torch.bfloat16
    )
```

### Memory-Efficient Batching

Dynamic batch sizing based on input complexity:

```python
def estimate_batch_size(inputs: list, max_memory_gb: float = 8.0) -> int:
    """Estimate optimal batch size based on input complexity and available memory."""
    # Estimate tokens per input
    avg_tokens = sum(len(str(input)) for input in inputs) // len(inputs) // 4
    
    # Estimate memory per sample (rough approximation)
    memory_per_sample_mb = avg_tokens * 0.001  # 1MB per 1000 tokens
    
    # Calculate batch size
    available_memory_mb = max_memory_gb * 1024
    estimated_batch_size = int(available_memory_mb / memory_per_sample_mb)
    
    return min(estimated_batch_size, 64)  # Cap at 64

# Usage
batch_size = estimate_batch_size(documents, max_memory_gb=8.0)
scores = batch_reranking(model, query, documents, batch_size=batch_size)
```

## Troubleshooting Deployment Issues

### Issue: vLLM Import Error

**Error**: `ModuleNotFoundError: No module named 'vllm.entrypoints.score_utils'`

**Solution**: Ensure vLLM version compatibility:

```bash
pip install "vllm>=0.6.0"  # Required for reranking support
```

### Issue: Out of Memory in Production

**Solution**: Implement dynamic batch sizing and caching:

```python
# Reduce batch size
engine_args = EngineArgs(
    model="Qwen/Qwen3-VL-Reranker-2B",
    max_num_batched_tokens=2048,  # Reduce from default
    max_num_seqs=128,
)

# Enable CPU offloading
model = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    device_map="auto",  # Automatic CPU/GPU splitting
)
```

### Issue: Slow Response Times

**Solution**: Profile and optimize:

```python
import cProfile
import pstats

def profile_reranking():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run reranking
    scores = model.process(inputs)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

profile_reranking()
```
