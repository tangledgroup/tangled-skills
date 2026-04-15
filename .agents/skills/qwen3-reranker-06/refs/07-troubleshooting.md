# Troubleshooting Qwen3-Reranker

## Common Issues and Solutions

### Installation Errors

#### KeyError: 'qwen3'

**Symptom:**
```python
KeyError: 'qwen3'
```

**Cause**: Transformers version < 4.51.0 doesn't support Qwen3 tokenizer config.

**Solution:**
```bash
# Upgrade transformers
pip install --upgrade transformers

# Verify version
python -c "import transformers; print(transformers.__version__)"
# Should show >= 4.51.0
```

**Alternative**: Force specific version
```bash
pip install "transformers>=4.51.0"
```

#### CUDA/Flash Attention Errors

**Symptom:**
```
RuntimeError: flash_attn_not_installed
or
ModuleNotFoundError: No module named 'flash_attn'
```

**Cause**: Flash attention not installed or incompatible GPU.

**Solution:**
```bash
# Check CUDA version
nvcc --version

# Install compatible flash-attn
pip install flash-attn--index-url https://flash-attention.ai/whl/cu121/torch2.3

# Or use pre-built wheel (if available)
pip install flash-attn

# Verify GPU compatibility
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}', f'Version: {torch.version.cuda}')"
```

**Fallback**: Disable flash attention
```python
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    attn_implementation=None,  # Use standard attention
    torch_dtype=torch.float16
)
```

### Memory Errors

#### CUDA Out of Memory

**Symptom:**
```
RuntimeError: CUDA out of memory. Tried to allocate X GB.
```

**Solutions (in order of effectiveness):**

1. **Reduce batch size:**
```python
scores = reranker.compute_scores(pairs, batch_size=8)  # Instead of 32 or 64
```

2. **Use FP16 precision:**
```python
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    torch_dtype=torch.float16,  # Half precision
    device_map="auto"
)
```

3. **Reduce context length:**
```python
reranker = Qwen3Reranker(max_length=1024)  # Instead of 8192 or 32768
```

4. **Clear cache between batches:**
```python
import torch
import gc

for i in range(0, len(pairs), batch_size):
    batch = pairs[i:i+batch_size]
    scores = reranker.compute_scores(batch)
    
    # Clear memory
    gc.collect()
    torch.cuda.empty_cache()
```

5. **Use smaller model:**
```python
# Switch from 4B or 8B to 0.6B
reranker = Qwen3Reranker("Qwen/Qwen3-Reranker-0.6B")
```

6. **Enable gradient checkpointing (if fine-tuning):**
```python
model.gradient_checkpointing_enable()
```

#### CPU Memory Errors

**Symptom:**
```
MemoryError: Unable to allocate X GB for array
```

**Solution:**
```python
# Use generator instead of loading all at once
def batch_generator(pairs, batch_size=32):
    for i in range(0, len(pairs), batch_size):
        yield pairs[i:i+batch_size]

for batch in batch_generator(all_pairs, batch_size=16):
    scores = reranker.compute_scores(batch)
    # Process scores immediately
```

### Performance Issues

#### Slow Inference

**Symptom**: Processing takes >5 seconds per query with 100 documents.

**Diagnosis:**
```python
import time

start = time.time()
scores = reranker.compute_scores(pairs)
print(f"Time: {time.time() - start:.2f}s")
print(f"Throughput: {len(pairs) / (time.time() - start):.2f} pairs/sec")
```

**Solutions:**

1. **Enable flash attention:**
```python
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2"  # 2-3x speedup
)
```

2. **Use GPU instead of CPU:**
```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")  # Verify GPU is being used
```

3. **Increase batch size:**
```python
# Benchmark different batch sizes
for batch_size in [8, 16, 32, 64]:
    start = time.time()
    scores = reranker.compute_scores(pairs, batch_size=batch_size)
    print(f"Batch {batch_size}: {time.time() - start:.2f}s")
```

4. **Use vLLM for production:**
```python
from qwen3_reranker_vllm import Qwen3Rerankervllm

reranker = Qwen3Rerankervllm(
    model_name_or_path="Qwen/Qwen3-Reranker-0.6B",
    tensor_parallel_size=1,
    enable_prefix_caching=True  # Cache repeated prefixes
)
```

5. **Reduce context length if 32K not needed:**
```python
reranker = Qwen3Reranker(max_length=2048)  # Most docs < 2K tokens
```

#### High Latency in Production

**Symptom**: P99 latency > 2 seconds under load.

**Solutions:**

1. **Add request queuing:**
```python
import asyncio
from asyncio import Queue

class QueuedReranker:
    def __init__(self, reranker, queue_size=100):
        self.reranker = reranker
        self.queue = Queue(maxsize=queue_size)
    
    async def process(self):
        while True:
            task = await self.queue.get()
            result = await self.reranker.compute_scores(task['pairs'])
            task['callback'](result)
```

2. **Use model warmup:**
```python
# Warm up model before serving
def warmup(reranker):
    dummy_pairs = [("warmup query", "warmup document" * 100) for _ in range(10)]
    _ = reranker.compute_scores(dummy_pairs)
    print("Model warmed up")

warmup(reranker)  # Call before starting server
```

3. **Implement caching:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_rerank(query_hash: str, docs_hash: str):
    # Decode and rerank
    pass
```

### Accuracy Issues

#### Low Relevance Scores

**Symptom**: All scores < 0.3 even for clearly relevant documents.

**Diagnosis Checklist:**

1. **Check instruction quality:**
```python
# Bad: Too generic
instruction = "Rank these"

# Good: Specific and descriptive
instruction = "Given a web search query, retrieve relevant passages that answer the query"
```

2. **Verify input format:**
```python
# Check formatting
formatted = f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {document}"
print(formatted[:200])  # Verify structure
```

3. **Test with known relevant pair:**
```python
test_pairs = [
    ("What is Python?", "Python is a programming language created by Guido van Rossum."),
    ("What is Python?", "The weather today is sunny.")
]
scores = reranker.compute_scores(test_pairs)
print(f"Relevant: {scores[0]:.4f}, Irrelevant: {scores[1]:.4f}")
# Should show clear separation (e.g., 0.85 vs 0.15)
```

4. **Try larger model:**
```python
reranker = Qwen3Reranker("Qwen/Qwen3-Reranker-4B")  # Better accuracy
```

5. **Check coarse retrieval quality:**
```python
# If embedding search returns irrelevant docs, reranker can't fix it
# Improve embedding model or use hybrid retrieval
```

#### Inconsistent Scores

**Symptom**: Same query-document pair gives different scores on repeated calls.

**Causes and Solutions:**

1. **Model not in eval mode:**
```python
model.eval()  # Ensure evaluation mode
```

2. **Gradient computation enabled:**
```python
with torch.no_grad():  # Wrap inference
    scores = reranker.compute_scores(pairs)
```

3. **Random operations:**
```python
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
```

#### Poor Cross-Lingual Performance

**Symptom**: Good monolingual but poor cross-lingual results.

**Solutions:**

1. **Use language-specific instruction:**
```python
instruction = "Given an English query, retrieve relevant Spanish passages that answer the query"
scores = reranker.compute_scores(pairs, instruction=instruction)
```

2. **Consider translation for critical cases:**
```python
from googletrans import Translator

translator = Translator()

# Translate query to document language
query_translated = translator.translate(query, dest="es").text
pairs = [(query_translated, doc) for doc in spanish_docs]
scores = reranker.compute_scores(pairs)
```

3. **Use larger model:**
```python
reranker = Qwen3Reranker("Qwen/Qwen3-Reranker-4B")  # Better multilingual
```

### Integration Issues

#### LangChain Compatibility

**Symptom**: Reranker doesn't work with LangChain retriever.

**Solution - Use proper wrapper:**
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.schema import Document

class Qwen3LangChainReranker:
    def __init__(self, model_name="Qwen/Qwen3-Reranker-0.6B"):
        self.reranker = Qwen3Reranker(model_name)
    
    def compress_documents(self, documents, query, **kwargs):
        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.reranker.compute_scores(pairs)
        
        # Sort by score
        scored = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        
        # Return top-k with metadata
        return [
            Document(page_content=doc.page_content, 
                     metadata={**doc.metadata, "relevance_score": score})
            for doc, score in scored[:10]
        ]

# Usage
compression_retriever = ContextualCompressionRetriever(
    base_compressor=Qwen3LangChainReranker(),
    base_retriever=vectorstore.as_retriever()
)
```

#### LlamaIndex Compatibility

**Solution:**
```python
from llama_index.core.schema import NodeWithScore

class Qwen3LlamaIndexReranker:
    def __init__(self, model_name="Qwen/Qwen3-Reranker-0.6B"):
        self.reranker = Qwen3Reranker(model_name)
        self.top_n = 5
    
    def postprocess_nodes(self, nodes, query_bundle):
        pairs = [(query_bundle.query, node.get_content()) for node in nodes]
        scores = self.reranker.compute_scores(pairs)
        
        # Update scores
        for node, score in zip(nodes, scores):
            node.score = score
        
        # Sort and return top-n
        sorted_nodes = sorted(nodes, key=lambda x: x.score if x.score else 0, reverse=True)
        return sorted_nodes[:self.top_n]

# Usage
query_engine = index.as_query_engine(
    similarity_top_k=20,
    node_postprocessors=[Qwen3LlamaIndexReranker()]
)
```

### vLLM-Specific Issues

#### Prefix Cache Not Working

**Symptom**: No speedup despite enabling prefix caching.

**Solution:**
```python
# Ensure instructions are consistent
instruction = "Given a web search query, retrieve relevant passages"  # Use exact same string

# Check cache stats
llm = LLM(
    model="Qwen/Qwen3-Reranker-0.6B",
    enable_prefix_caching=True
)

# Monitor cache hit rate in logs
# Look for "prefix_cache_hit_rate" metric
```

#### Tensor Parallelism Issues

**Symptom**: Multi-GPU setup not working correctly.

**Solution:**
```python
import torch

# Check GPU visibility
print(f"Visible devices: {torch.cuda.device_count()}")

# Set visible GPUs before initializing
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"  # Use GPUs 0 and 1

# Initialize with correct TP size
llm = LLM(
    model="Qwen/Qwen3-Reranker-4B",
    tensor_parallel_size=2  # Must match visible GPU count
)
```

### Debugging Tools

#### Profile Memory Usage

```python
import torch
from torch.utils.data import DataLoader

def profile_memory(reranker, pairs, batch_sizes=[8, 16, 32, 64]):
    """Profile memory usage for different batch sizes."""
    
    results = []
    
    for batch_size in batch_sizes:
        # Clear cache
        torch.cuda.empty_cache()
        
        # Process one batch
        batch = pairs[:batch_size]
        
        # Track memory
        initial_memory = torch.cuda.memory_allocated()
        
        scores = reranker.compute_scores(batch)
        
        peak_memory = torch.cuda.max_memory_allocated()
        
        results.append({
            'batch_size': batch_size,
            'initial_mb': initial_memory / 1e6,
            'peak_mb': peak_memory / 1e6,
            'delta_mb': (peak_memory - initial_memory) / 1e6
        })
        
        torch.cuda.empty_cache()
    
    # Print results
    print("Batch Size | Initial (MB) | Peak (MB) | Delta (MB)")
    print("-" * 55)
    for r in results:
        print(f"{r['batch_size']:10} | {r['initial_mb']:14.1f} | {r['peak_mb']:9.1f} | {r['delta_mb']:10.1f}")
    
    return results


# Usage
profile_memory(reranker, all_pairs)
```

#### Profile Inference Time

```python
import time
import statistics

def profile_inference(reranker, pairs, num_runs=5):
    """Profile inference time with multiple runs."""
    
    times = []
    
    for run in range(num_runs):
        # Warmup
        if run == 0:
            _ = reranker.compute_scores(pairs[:10])
        
        # Time execution
        start = time.time()
        scores = reranker.compute_scores(pairs)
        elapsed = time.time() - start
        
        times.append(elapsed)
    
    print(f"Runs: {num_runs}")
    print(f"Pairs: {len(pairs)}")
    print(f"Mean time: {statistics.mean(times):.3f}s")
    print(f"Std dev: {statistics.stdev(times):.3f}s")
    print(f"Min time: {min(times):.3f}s")
    print(f"Max time: {max(times):.3f}s")
    print(f"Throughput: {len(pairs) / statistics.mean(times):.2f} pairs/sec")
    
    return times


# Usage
profile_inference(reranker, test_pairs, num_runs=10)
```

#### Validate Output Quality

```python
def validate_scores(scores, threshold_low=0.3, threshold_high=0.7):
    """Validate score distribution."""
    
    print(f"Total pairs: {len(scores)}")
    print(f"Score range: [{min(scores):.4f}, {max(scores):.4f}]")
    print(f"Mean score: {sum(scores)/len(scores):.4f}")
    
    # Count by threshold
    very_low = sum(1 for s in scores if s < threshold_low)
    medium = sum(1 for s in scores if threshold_low <= s < threshold_high)
    high = sum(1 for s in scores if s >= threshold_high)
    
    print(f"Very low (<{threshold_low}): {very_low} ({100*very_low/len(scores):.1f}%)")
    print(f"Medium ({threshold_low}-{threshold_high}): {medium} ({100*medium/len(scores):.1f}%)")
    print(f"High (>={threshold_high}): {high} ({100*high/len(scores):.1f}%)")
    
    # Check for anomalies
    if min(scores) < 0 or max(scores) > 1:
        print("WARNING: Scores outside [0, 1] range!")
    
    if very_low == len(scores):
        print("WARNING: All scores very low - check instruction and inputs")
    
    if high == len(scores):
        print("WARNING: All scores very high - model may be overconfident")


# Usage
validate_scores(computed_scores)
```

## Performance Checklist

Before deploying to production:

- [ ] **Model selection**: Choose appropriate size (0.6B, 4B, or 8B) for use case
- [ ] **GPU availability**: Verify CUDA and sufficient VRAM
- [ ] **Flash attention**: Enable if GPU supports it
- [ ] **Batch size tuning**: Find optimal batch size for hardware
- [ ] **Context length**: Set appropriate max_length (don't use 32K if not needed)
- [ ] **Instruction quality**: Test with domain-specific instructions
- [ ] **Warmup**: Implement model warmup before serving
- [ ] **Caching**: Add result caching for repeated queries
- [ ] **Monitoring**: Track latency, throughput, and error rates
- [ ] **Fallback**: Have CPU fallback or smaller model ready

## Getting Help

### Resources

- **GitHub Issues**: https://github.com/QwenLM/Qwen3-Embedding/issues
- **Discord Community**: https://discord.gg/yPEP2vHTu4
- **Hugging Face Discusssions**: https://huggingface.co/Qwen/discussions
- **Documentation**: https://qwenlm.github.io/blog/qwen3-embedding/

### When to File an Issue

1. **Installation errors** that persist after following solutions above
2. **Crashes or segfaults** with clear stack trace
3. **Performance regressions** compared to documented benchmarks
4. **Quality issues** on standard benchmarks (MTEB, C-MTEB)
5. **Feature requests** for new capabilities

### Information to Include

- Qwen3-Reranker model version (0.6B, 4B, 8B)
- Transformers version: `transformers.__version__`
- PyTorch version: `torch.__version__`
- CUDA version: `torch.version.cuda`
- GPU model: `nvidia-smi` output
- Minimal reproducible example
- Full error traceback
