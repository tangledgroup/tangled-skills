# Qwen3-Reranker with vLLM Deployment

## Overview

vLLM provides high-throughput serving for Qwen3-Reranker with automatic optimizations including continuous batching, PagedAttention, and GPU memory management. Ideal for production deployments requiring low latency and high concurrency.

## Installation

```bash
# Install vLLM with all dependencies
pip install vllm>=0.8.5 ray

# For flash attention support (recommended)
pip install flash-attn

# Verify installation
python -c "import vllm; print(vllm.__version__)"
```

**Requirements:**
- CUDA-capable GPU (NVIDIA recommended)
- Python 3.10+
- Linux or macOS (Windows via WSL2)

## Basic Usage

### Simple Reranking with vLLM

```python
import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.inputs.data import TokensPrompt

# Initialize model
model_name = "Qwen/Qwen3-Reranker-0.6B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.padding_side = "left"
tokenizer.pad_token = tokenizer.eos_token

# Create vLLM instance
llm = LLM(
    model=model_name,
    tensor_parallel_size=1,  # Number of GPUs
    max_model_len=8192,      # Maximum context length
    enable_prefix_caching=True,  # Cache repeated prefixes
    gpu_memory_utilization=0.9,  # GPU memory usage
    enforce_eager=True  # Better for short sequences
)

# Prepare sampling parameters
true_token = tokenizer("yes", add_special_tokens=False).input_ids[0]
false_token = tokenizer("no", add_special_tokens=False).input_ids[0]

sampling_params = SamplingParams(
    temperature=0,              # Deterministic output
    max_tokens=1,               # Only predict next token
    logprobs=20,                # Get log probabilities
    allowed_token_ids=[true_token, false_token]  # Restrict to yes/no
)

# Prepare query-document pairs
queries = ["What is Python?", "How to install Python?"]
documents = [
    "Python is a programming language.",
    "Download Python from python.org."
]

pairs = list(zip(queries, documents))

# Format with chat template
instruction = "Given a web search query, retrieve relevant passages that answer the query"

messages = []
for query, doc in pairs:
    msg = [
        {
            "role": "system",
            "content": "Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\"."
        },
        {
            "role": "user",
            "content": f"<Instruct>: {instruction}\n\n<Query>: {query}\n\n<Document>: {doc}"
        }
    ]
    messages.append(msg)

# Apply chat template and add suffix
suffix = "</think>\n</think>assistant\n<think>\n\n</think>\n\n"
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

tokenized_messages = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=False,
    enable_thinking=False
)

# Add suffix tokens and create prompts
prompts = [
    TokensPrompt(prompt_token_ids=ele[:8192] + suffix_tokens)
    for ele in tokenized_messages
]

# Generate and compute scores
outputs = llm.generate(prompts, sampling_params, use_tqdm=False)

import math

scores = []
for output in outputs:
    final_logits = output.outputs[0].logprobs[-1]
    
    # Get log probabilities for yes/no tokens
    true_logit = final_logits.get(true_token, type('obj', (object,), {'logprob': -10})())
    false_logit = final_logits.get(false_token, type('obj', (object,), {'logprob': -10})())
    
    true_logit = true_logit.logprob if hasattr(true_logit, 'logprob') else -10
    false_logit = false_logit.logprob if hasattr(false_logit, 'logprob') else -10
    
    # Convert to probability
    true_score = math.exp(true_logit)
    false_score = math.exp(false_logit)
    score = true_score / (true_score + false_score)
    
    scores.append(score)

print("Scores:", scores)
```

## Production-Ready Reranker Class

### Complete vLLM Reranker Implementation

```python
import logging
import math
from typing import List, Tuple, Optional
import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.distributed.parallel_state import destroy_model_parallel
from vllm.inputs.data import TokensPrompt

logger = logging.getLogger(__name__)


class Qwen3Rerankervllm:
    """Production-ready reranker using vLLM for high-throughput serving."""
    
    def __init__(
        self,
        model_name_or_path: str = "Qwen/Qwen3-Reranker-0.6B",
        instruction: Optional[str] = None,
        max_length: int = 8192,
        tensor_parallel_size: Optional[int] = None,
        gpu_memory_utilization: float = 0.9,
        enable_prefix_caching: bool = True,
        **kwargs
    ):
        """
        Initialize the vLLM-based reranker.
        
        Args:
            model_name_or_path: HuggingFace model path or name
            instruction: Default instruction for ranking
            max_length: Maximum context length
            tensor_parallel_size: Number of GPUs (auto-detected if None)
            gpu_memory_utilization: GPU memory usage (0-1)
            enable_prefix_caching: Enable prefix caching for repeated queries
            **kwargs: Additional vLLM arguments
        """
        
        self.model_name = model_name_or_path
        self.instruction = instruction or "Given a web search query, retrieve relevant passages that answer the query"
        self.max_length = max_length
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.tokenizer.padding_side = "left"
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Token IDs for classification
        self.true_token = self.tokenizer("yes", add_special_tokens=False).input_ids[0]
        self.false_token = self.tokenizer("no", add_special_tokens=False).input_ids[0]
        
        # Suffix for chat template
        self.suffix = "</think>\n</think>assistant\n<think>\n\n</think>\n\n"
        self.suffix_tokens = self.tokenizer.encode(self.suffix, add_special_tokens=False)
        
        # Sampling parameters
        self.sampling_params = SamplingParams(
            temperature=0,
            top_p=0.95,
            max_tokens=1,
            logprobs=20,
            allowed_token_ids=[self.true_token, self.false_token]
        )
        
        # Auto-detect GPU count if not specified
        if tensor_parallel_size is None:
            tensor_parallel_size = torch.cuda.device_count() or 1
        
        logger.info(f"Initializing vLLM with {tensor_parallel_size} GPUs")
        
        # Initialize vLLM model
        self.llm = LLM(
            model=model_name_or_path,
            tensor_parallel_size=tensor_parallel_size,
            max_model_len=max_length,
            enable_prefix_caching=enable_prefix_caching,
            gpu_memory_utilization=gpu_memory_utilization,
            distributed_executor_backend='ray',
            **kwargs
        )
        
        logger.info(f"vLLM model loaded: {model_name_or_path}")
    
    def format_instruction(self, instruction: str, query: str, doc: str) -> List[dict]:
        """Format query-document pair as chat messages."""
        
        text = [
            {
                "role": "system",
                "content": "Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\"."
            },
            {
                "role": "user",
                "content": f"<Instruct>: {instruction}\n\n<Query>: {query}\n\n<Document>: {doc}"
            }
        ]
        return text
    
    def compute_scores(
        self,
        pairs: List[Tuple[str, str]],
        instruction: Optional[str] = None,
        **kwargs
    ) -> List[float]:
        """
        Compute relevance scores for query-document pairs.
        
        Args:
            pairs: List of (query, document) tuples
            instruction: Task instruction (uses default if None)
            
        Returns:
            List of relevance scores (0-1)
        """
        if instruction is None:
            instruction = self.instruction
        
        # Format as chat messages
        messages = [
            self.format_instruction(instruction, query, doc)
            for query, doc in pairs
        ]
        
        # Apply chat template
        tokenized = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=False,
            enable_thinking=False
        )
        
        # Truncate and add suffix
        max_input_len = self.max_length - len(self.suffix_tokens)
        prompts = [
            TokensPrompt(prompt_token_ids=ele[:max_input_len] + self.suffix_tokens)
            for ele in tokenized
        ]
        
        # Generate predictions
        outputs = self.llm.generate(prompts, self.sampling_params, use_tqdm=False)
        
        # Extract scores from logprobs
        scores = []
        for output in outputs:
            final_logits = output.outputs[0].logprobs[-1]
            
            # Get log probabilities
            true_entry = final_logits.get(self.true_token)
            false_entry = final_logits.get(self.false_token)
            
            true_logit = true_entry.logprob if true_entry else -10
            false_logit = false_entry.logprob if false_entry else -10
            
            # Convert to probability
            true_score = math.exp(true_logit)
            false_score = math.exp(false_logit)
            score = true_score / (true_score + false_score)
            
            scores.append(score)
        
        return scores
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        instruction: Optional[str] = None,
        top_k: Optional[int] = None,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """Rerank documents and return top results."""
        
        pairs = [(query, doc) for doc in documents]
        scores = self.compute_scores(pairs, instruction)
        
        # Combine and sort
        ranked = list(zip(documents, scores))
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        # Apply threshold and top_k
        ranked = [item for item in ranked if item[1] >= threshold]
        if top_k is not None:
            ranked = ranked[:top_k]
        
        return ranked
    
    def stop(self):
        """Cleanup vLLM resources."""
        logger.info("Cleaning up vLLM resources")
        destroy_model_parallel()
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Usage example
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize reranker
    reranker = Qwen3Rerankervllm(
        model_name_or_path="Qwen/Qwen3-Reranker-0.6B",
        instruction="Retrieval document that can answer user's query",
        max_length=2048,
        tensor_parallel_size=1
    )
    
    # Test reranking
    queries = ['What is the capital of China?', 'Explain gravity']
    documents = [
        "The capital of China is Beijing.",
        "Gravity is a force that attracts two bodies towards each other."
    ]
    pairs = list(zip(queries, documents))
    
    scores = reranker.compute_scores(pairs)
    print('Scores:', scores)
    
    # Cleanup
    reranker.stop()
```

## Multi-GPU Deployment

### Tensor Parallelism

For large models (4B, 8B), use tensor parallelism across multiple GPUs:

```python
# Single GPU for 0.6B model
reranker = Qwen3Rerankervllm(
    model_name_or_path="Qwen/Qwen3-Reranker-0.6B",
    tensor_parallel_size=1
)

# 2 GPUs for 4B model
reranker_4b = Qwen3Rerankervllm(
    model_name_or_path="Qwen/Qwen3-Reranker-4B",
    tensor_parallel_size=2
)

# 4 GPUs for 8B model
reranker_8b = Qwen3Rerankervllm(
    model_name_or_path="Qwen/Qwen3-Reranker-8B",
    tensor_parallel_size=4
)
```

**GPU Memory Requirements:**

| Model | 1 GPU | 2 GPUs | 4 GPUs |
|-------|-------|--------|--------|
| 0.6B | ~4GB | - | - |
| 4B | ~16GB | ~8GB/GPU | - |
| 8B | ~32GB | ~16GB/GPU | ~8GB/GPU |

### Pipeline Parallelism (Advanced)

For extreme scale, combine tensor and pipeline parallelism:

```python
llm = LLM(
    model="Qwen/Qwen3-Reranker-8B",
    tensor_parallel_size=2,  # Split layers across GPUs
    pipeline_parallel_size=2,  # Split across GPU pairs
    max_model_len=16384,
    enable_prefix_caching=True
)
```

## Performance Optimization

### Prefix Caching

Enable prefix caching for repeated queries:

```python
reranker = Qwen3Rerankervllm(
    model_name_or_path="Qwen/Qwen3-Reranker-0.6B",
    enable_prefix_caching=True  # Cache common prefixes
)
```

**Benefits:**
- Reuse computation for repeated query prefixes
- Up to 50% faster for batch queries with similar instructions
- Automatic cache management

### Continuous Batching

vLLM automatically handles continuous batching:

```python
# Submit requests continuously
async def process_requests(request_queue):
    while True:
        query, documents = request_queue.get()
        results = reranker.rerank(query, documents, top_k=10)
        # Send results to client
```

### Memory Optimization

```python
reranker = Qwen3Rerankervllm(
    model_name_or_path="Qwen/Qwen3-Reranker-4B",
    gpu_memory_utilization=0.95,  # Use 95% of GPU memory
    max_model_len=4096,  # Reduce context if 32K not needed
    swap_space=8,  # CPU swap space (GB) for overflow
    enforce_eager=True  # Better for short sequences
)
```

## Benchmarking

### Throughput Testing

```python
import time
import random

def benchmark_reranker(reranker, num_queries=100, docs_per_query=50):
    """Measure throughput and latency."""
    
    # Generate test data
    queries = [f"Query {i}" for i in range(num_queries)]
    documents = [[f"Document {j}" for j in range(docs_per_query)] for _ in range(num_queries)]
    
    pairs = [(q, docs) for q, docs in zip(queries, documents)]
    
    # Warmup
    _ = reranker.compute_scores([(pairs[0][0], d) for d in pairs[0][1]])
    
    # Benchmark
    start = time.time()
    all_results = []
    
    for query, docs in pairs:
        results = reranker.rerank(query, docs, top_k=10)
        all_results.append(results)
    
    elapsed = time.time() - start
    
    print(f"Total queries: {num_queries}")
    print(f"Documents per query: {docs_per_query}")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Queries per second: {num_queries / elapsed:.2f}")
    print(f"Average latency: {elapsed / num_queries * 1000:.2f}ms")
    
    return {
        'queries_per_second': num_queries / elapsed,
        'avg_latency_ms': elapsed / num_queries * 1000
    }


# Run benchmark
reranker = Qwen3Rerankervllm(model_name_or_path="Qwen/Qwen3-Reranker-0.6B")
benchmark_reranker(reranker)
reranker.stop()
```

## API Server Deployment

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Qwen3-Reranker API")

# Initialize reranker globally
reranker = Qwen3Rerankervllm(
    model_name_or_path="Qwen/Qwen3-Reranker-0.6B",
    max_length=4096
)


class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    instruction: Optional[str] = None
    top_k: Optional[int] = 10
    threshold: float = 0.0


class RerankResult(BaseModel):
    document: str
    score: float


class RerankResponse(BaseModel):
    results: List[RerankResult]
    query: str


@app.post("/rerank", response_model=RerankResponse)
async def rerank(request: RerankRequest):
    """Rerank documents for a query."""
    
    try:
        results = reranker.rerank(
            query=request.query,
            documents=request.documents,
            instruction=request.instruction,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        return RerankResponse(
            results=[
                RerankResult(document=doc, score=score)
                for doc, score in results
            ],
            query=request.query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "model": reranker.model_name}


# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Docker Deployment

```dockerfile
FROM nvidia/cuda:12.1-base-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtual environment
RUN python3.11 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies
RUN pip install --upgrade pip
RUN pip install vllm>=0.8.5 fastapi uvicorn transformers torch

# Copy application
COPY app.py .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**Docker Compose:**

```yaml
version: '3.8'

services:
  reranker:
    build: .
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - MODEL_NAME=Qwen/Qwen3-Reranker-0.6B
      - MAX_LENGTH=4096
```

## Troubleshooting

### Common Issues

**CUDA Out of Memory:**
```python
# Reduce GPU memory usage
reranker = Qwen3Rerankervllm(
    gpu_memory_utilization=0.7,  # Use only 70% of GPU memory
    max_model_len=2048,  # Reduce context length
    swap_space=16  # Increase CPU swap space
)
```

**Slow First Request:**
- Expected due to model loading and compilation
- Solution: Add warmup request on startup

**Prefix Cache Misses:**
- Ensure instructions are consistent across requests
- Use template-based instruction generation

## References

- **vLLM Documentation**: https://docs.vllm.ai/
- **vLLM GitHub**: https://github.com/vllm-project/vllm
- **FastAPI**: https://fastapi.tiangolo.com/
- **Ray Distributed Execution**: https://docs.ray.io/
