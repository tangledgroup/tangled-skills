# vLLM and TEI Usage

For production deployments serving many concurrent requests, use **vLLM** or **Text Embeddings Inference (TEI)** for high-throughput, low-latency embedding generation.

## vLLM Usage

### Requirements

```bash
pip install vllm>=0.8.5 torch transformers>=4.51.0
```

### Basic vLLM Embedding

```python
import torch
from vllm import LLM

# Initialize the model for embedding tasks
model = LLM(model="Qwen/Qwen3-Embedding-0.6B", task="embed")

# Texts to embed (include instructions for queries)
task = 'Given a web search query, retrieve relevant passages that answer the query'
texts = [
    f"Instruct: {task}\nQuery:What is the capital of China?",
    f"Instruct: {task}\nQuery:Explain gravity",
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other."
]

# Generate embeddings
outputs = model.embed(texts)
embeddings = torch.tensor([o.outputs.embedding for o in outputs])

# Compute similarity
scores = embeddings[:2] @ embeddings[2:].T
print(scores.tolist())
```

### vLLM Batch Processing

```python
from vllm import LLM
import torch

model = LLM(model="Qwen/Qwen3-Embedding-8B", task="embed")

# Large batch
texts = [f"Document number {i}" for i in range(1000)]
outputs = model.embed(texts)
embeddings = torch.stack([torch.tensor(o.outputs.embedding) for o in outputs])
print(embeddings.shape)  # (1000, 4096)
```

### vLLM with GPU Configuration

```python
from vllm import LLM

model = LLM(
    model="Qwen/Qwen3-Embedding-8B",
    task="embed",
    gpu_memory_utilization=0.9,   # Use 90% of GPU memory
    max_model_len=8192,           # Context length to allocate
    dtype="float16",              # Half precision
    enforce_eager=False           # Use CUDA graph for speed
)
```

## Text Embeddings Inference (TEI) — Docker Deployment

TEI provides a production-ready REST API for embedding generation.

### NVIDIA GPU Deployment

```bash
docker run --gpus all -p 8080:80 \
  -v hf_cache:/data \
  --pull always \
  ghcr.io/huggingface/text-embeddings-inference:cpu-1.7.2 \
  --model-id Qwen/Qwen3-Embedding-0.6B \
  --dtype float16
```

### CPU Deployment

```bash
docker run -p 8080:80 \
  -v hf_cache:/data \
  --pull always \
  ghcr.io/huggingface/text-embeddings-inference:1.7.2 \
  --model-id Qwen/Qwen3-Embedding-0.6B
```

### TEI API Usage — cURL

```bash
# Generate embeddings
curl http://localhost:8080/embed \
  -X POST \
  -d '{
    "inputs": [
      "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: What is the capital of China?",
      "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: Explain gravity",
      "The capital of China is Beijing.",
      "Gravity is a force that attracts two bodies towards each other."
    ]
  }' \
  -H "Content-Type: application/json"
```

### TEI API Usage — Python Client

```python
import requests

def get_embeddings(texts, api_url="http://localhost:8080/embed"):
    """Get embeddings via TEI REST API."""
    response = requests.post(
        api_url,
        json={"inputs": texts},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()

# Usage
task = 'Given a web search query, retrieve relevant passages that answer the query'
texts = [
    f"Instruct: {task}\nQuery:What is AI?",
    "Artificial intelligence is a field of computer science."
]
embeddings = get_embeddings(texts)
print(f"Embedding shape: {len(embeddings[0])} x {len(embeddings)}")
```

### TEI with Multiple GPUs (8B Model)

For the 8B model, you may need multiple GPUs or Tensor Parallelism:

```bash
docker run --gpus '"device=0,1"' -p 8080:80 \
  -v hf_cache:/data \
  --pull always \
  ghcr.io/huggingface/text-embeddings-inference:cpu-1.7.2 \
  --model-id Qwen/Qwen3-Embedding-8B \
  --dtype float16 \
  --num-shard 2 \
  --max-batch-tokens 32768
```

## Production Deployment Considerations

### Model Selection Guide

| Use Case | Recommended Model | Inference Engine | Reason |
|----------|-------------------|-----------------|--------|
| Edge / Mobile | Qwen3-Embedding-0.6B | ONNX / TensorRT | ~1.2 GB weights, fast inference |
| Balanced API | Qwen3-Embedding-4B | vLLM / TEI | Good accuracy/latency tradeoff |
| Highest Accuracy | Qwen3-Embedding-8B | vLLM (multi-GPU) / TEI | MTEB multilingual #1 |

### Dimensionality Optimization

For production vector databases, reduce embedding dimensions to save storage:

```python
# With sentence-transformers
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
embeddings = model.encode(texts, dimension=256)  # From 1024 → 256

# Trade-off: smaller vectors = less storage/compute, slightly lower accuracy
```

### Caching and Batching

```python
import hashlib
from vllm import LLM

class EmbeddingCache:
    """Simple cache for embeddings to avoid recomputation."""
    def __init__(self, model_name="Qwen/Qwen3-Embedding-0.6B"):
        self.model = LLM(model=model_name, task="embed")
        self.cache = {}

    def get_embedding(self, text):
        key = hashlib.md5(text.encode()).hexdigest()
        if key not in self.cache:
            outputs = self.model.embed([text])
            self.cache[key] = outputs[0].outputs.embedding
        return self.cache[key]
```

## References

- vLLM docs: https://docs.vllm.ai/
- TEI docs: https://huggingface.co/docs/text-embeddings-inference/
- Hugging Face (0.6B): https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Hugging Face (4B): https://huggingface.co/Qwen/Qwen3-Embedding-4B
- Hugging Face (8B): https://huggingface.co/Qwen/Qwen3-Embedding-8B
