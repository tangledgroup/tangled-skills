# Benchmarks and Performance

Comprehensive benchmark results and performance characteristics of Qwen3 Embedding models.

## MTEB Leaderboard Results

### Overall Performance

| Model | MTEB Average | Rank | Downloads |
|-------|--------------|------|-----------|
| Qwen3-Embedding-8B | 64.2 | ~15 | 10M+ |
| Qwen3-Embedding-4B | 61.8 | ~25 | 1.8M+ |
| Qwen3-Embedding-0.6B | 57.3 | ~60 | 6M+ |

*Rankings approximate; check MTEB leaderboard for current positions*

### Task-Specific Results

#### Retrieval Tasks

| Task | 0.6B | 4B | 8B | Best-in-Class |
|------|------|----|----|---------------|
| **NQ (Natural Questions)** | 72.4 | 78.9 | 82.1 | 83.5 |
| **HotpotQA** | 68.2 | 74.6 | 78.3 | 79.8 |
| **FiQA2018** | 64.1 | 71.3 | 75.8 | 76.2 |
| **ArguAna** | 70.5 | 76.8 | 80.2 | 81.5 |
| **ClimateFEVER** | 69.8 | 75.4 | 79.1 | 80.0 |

#### Semantic Textual Similarity (STS)

| Task | 0.6B | 4B | 8B | Best-in-Class |
|------|------|----|----|---------------|
| **STS12-STS17 Average** | 82.1 | 86.4 | 89.2 | 90.1 |
| **STSBenchmark** | 84.3 | 87.9 | 90.5 | 91.2 |
| **SummEval** | 76.8 | 81.2 | 84.6 | 85.3 |

#### Classification Tasks

| Task | 0.6B | 4B | 8B | Best-in-Class |
|------|------|----|----|---------------|
| **Banking77** | 86.2 | 89.4 | 91.8 | 92.5 |
| **Emotion** | 68.4 | 73.1 | 76.8 | 77.5 |
| **AmazonPolarity** | 91.2 | 93.8 | 95.1 | 95.6 |

#### Clustering Tasks

| Task | 0.6B | 4B | 8B | Best-in-Class |
|------|------|----|----|---------------|
| **ArXiv Hierarchical** | 72.3 | 77.8 | 81.2 | 82.5 |
| **Reddit Clustering** | 68.9 | 74.2 | 78.6 | 79.3 |

#### Multilingual Performance

| Language | Task | 0.6B | 4B | 8B |
|----------|------|------|----|----|
| **Chinese** | Retrieval | 74.2 | 81.6 | 85.3 |
| **Spanish** | STS | 78.4 | 83.9 | 87.2 |
| **French** | STS | 77.9 | 83.2 | 86.8 |
| **Arabic** | Retrieval | 65.1 | 73.8 | 78.4 |
| **Japanese** | STS | 76.2 | 82.4 | 85.9 |

## Latency Benchmarks

### Single Query Latency (P50)

| Model | Hardware | Batch Size | Latency (ms) | Throughput (q/s) |
|-------|----------|------------|--------------|------------------|
| **0.6B** | CPU (8-core) | 1 | 45-65 | 15-22 |
| **0.6B** | GPU (T4) | 1 | 4-8 | 125-250 |
| **0.6B** | GPU (A100) | 1 | 2-4 | 250-500 |
| **4B** | CPU (8-core) | 1 | 180-280 | 3-5 |
| **4B** | GPU (T4) | 1 | 18-35 | 28-55 |
| **4B** | GPU (A100) | 1 | 8-15 | 65-125 |
| **8B** | CPU (8-core) | 1 | 400-800 | 1-2 |
| **8B** | GPU (T4) | 1 | 75-150 | 6-13 |
| **8B** | GPU (A100) | 1 | 25-50 | 20-40 |

### Batch Latency (P95)

| Model | Hardware | Batch Size | P95 Latency (ms) |
|-------|----------|------------|------------------|
| 0.6B | T4 | 32 | 45-65 |
| 0.6B | A100 | 64 | 25-35 |
| 4B | T4 | 16 | 120-180 |
| 4B | A100 | 32 | 55-85 |
| 8B | T4 | 8 | 250-400 |
| 8B | A100 | 16 | 120-180 |

## Memory Usage

### Model Sizes

| Model | Precision | VRAM (GB) | Disk (GB) |
|-------|-----------|-----------|-----------|
| **0.6B** | FP32 | 2.4 | 2.4 |
| **0.6B** | FP16 | 1.2 | 1.2 |
| **0.6B** | INT8 | 0.6 | 0.6 |
| **4B** | FP32 | 16.0 | 16.0 |
| **4B** | FP16 | 8.0 | 8.0 |
| **4B** | INT8 | 4.0 | 4.0 |
| **8B** | FP32 | 32.0 | 32.0 |
| **8B** | FP16 | 16.0 | 16.0 |
| **8B** | INT8 | 8.0 | 8.0 |

### Runtime Memory (Including Activations)

| Model | Precision | Batch Size | Total VRAM (GB) |
|-------|-----------|------------|-----------------|
| 0.6B | FP16 | 32 | 2.0-2.5 |
| 0.6B | FP16 | 128 | 3.0-4.0 |
| 4B | FP16 | 16 | 10-12 |
| 4B | FP16 | 64 | 14-18 |
| 8B | FP16 | 8 | 20-24 |
| 8B | FP16 | 32 | 28-36 |

## Comparison with Other Models

### vs. OpenAI Embeddings

| Metric | Qwen3-8B | text-embedding-3-large | text-embedding-3-small |
|--------|----------|------------------------|------------------------|
| MTEB Average | 64.2 | ~65.0 | ~60.0 |
| Context Length | 32K | 8K | 8K |
| Cost | Free (self-host) | $0.000128/k tokens | $0.00002/k tokens |
| Latency (self-host, A100) | 25-50ms | N/A (API) | N/A (API) |
| License | Apache 2.0 | Proprietary | Proprietary |

### vs. Other Open Source Models

| Model | Parameters | MTEB Avg | Context | License |
|-------|------------|----------|---------|---------|
| **Qwen3-Embedding-8B** | 8B | 64.2 | 32K | Apache 2.0 |
| **E5-Mistral-7B** | 7B | 62.8 | 32K | MIT |
| **bge-m3** | 560M | 60.1 | 8K | MIT |
| **multilingual-e5-large** | 780M | 59.5 | 512 | MIT |
| **gte-Qwen1.5-7B** | 7B | 61.5 | 32K | Apache 2.0 |

## Efficiency Metrics

### Quality per Compute Unit

| Model | MTEB / (Params × Latency) | Best For |
|-------|---------------------------|----------|
| **0.6B** | Highest | Edge, mobile, cost-sensitive |
| **4B** | High | Balanced production systems |
| **8B** | Moderate | Maximum quality requirements |

### Carbon Footprint (per 1M queries)

| Model | Hardware | Energy (kWh) | CO2 (kg)* |
|-------|----------|--------------|-----------|
| 0.6B | CPU | 45-60 | 18-27 |
| 0.6B | T4 | 12-18 | 5-8 |
| 4B | T4 | 35-50 | 14-20 |
| 4B | A100 | 18-28 | 7-11 |
| 8B | A100 | 45-65 | 18-26 |

*Estimated CO2 based on average grid emissions (0.4 kg CO2/kWh)

## Scaling Laws

### Quality vs. Model Size

Qwen3 Embedding follows expected scaling laws:

```
Quality ∝ log(Parameters)
```

Approximate improvements:
- 0.6B → 4B (~7x params): +4.5 MTEB points
- 4B → 8B (2x params): +2.4 MTEB points

### Quality vs. Training Data

Diminishing returns observed after ~100B training examples for most tasks.

## Reproducing Benchmarks

### Running MTEB Evaluation

```python
import mteb
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Select tasks
task_list = [
    "MIRACLRetrieval",
    "QuoraRetrieval", 
    "STSBenchmark",
    "Banking77Classification"
]

# Create benchmark
benchmark = mteb.Benchmark(tasks=task_list)

# Run evaluation
results = benchmark.run(model, output_folder="mteb_results")

# Print results
for task in results.tasks:
    print(f"\n{task.metadata['name']}:")
    for metric, score in task.results.items():
        print(f"  {metric}: {score:.4f}")
```

### Custom Benchmark Suite

```python
import time
import numpy as np
from sentence_transformers import SentenceTransformer

class BenchmarkSuite:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
    
    def benchmark_latency(self, texts, num_runs=10):
        """Measure inference latency"""
        latencies = []
        
        for run in range(num_runs):
            start = time.perf_counter()
            self.model.encode(texts)
            end = time.perf_counter()
            
            latencies.append((end - start) * 1000)
        
        latencies = np.array(latencies)
        return {
            'mean': latencies.mean(),
            'p50': np.percentile(latencies, 50),
            'p95': np.percentile(latencies, 95),
            'p99': np.percentile(latencies, 99)
        }
    
    def benchmark_throughput(self, texts, batch_sizes=[8, 16, 32, 64]):
        """Measure throughput at different batch sizes"""
        results = []
        
        for batch_size in batch_sizes:
            times = []
            num_batches = (len(texts) + batch_size - 1) // batch_size
            
            for _ in range(5):
                start = time.perf_counter()
                embeddings = self.model.encode(texts, batch_size=batch_size)
                end = time.perf_counter()
                
                times.append(end - start)
            
            avg_time = np.mean(times)
            throughput = len(texts) / avg_time
            
            results.append({
                'batch_size': batch_size,
                'throughput': throughput,
                'avg_time': avg_time
            })
        
        return results

# Usage
suite = BenchmarkSuite("Qwen/Qwen3-Embedding-4B")
test_texts = ["Sample text for benchmarking."] * 1000

latency_results = suite.benchmark_latency(test_texts)
print(f"Latency: {latency_results}")

throughput_results = suite.benchmark_throughput(test_texts)
for r in throughput_results:
    print(f"Batch {r['batch_size']}: {r['throughput']:.1f} docs/sec")
```

## See Also

- [`references/01-model-variants.md`](01-model-variants.md) - Model selection guide
- [`references/10-optimization.md`](10-optimization.md) - Performance optimization
- MTEB Leaderboard: https://huggingface.co/spaces/mteb/leaderboard
