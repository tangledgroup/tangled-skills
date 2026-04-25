# Transformers Library Usage (Low-Level)

For full control over the embedding process, use the `transformers` library directly. This approach is useful when you need fine-grained control over tokenization, pooling, normalization, or want to integrate with existing PyTorch pipelines.

## Requirements

```bash
pip install transformers>=4.51.0 torch
```

**Critical:** `transformers>=4.51.0` is required. Earlier versions will raise:
```
KeyError: 'qwen3'
```

## Basic Usage — Raw Transformers

```python
import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel

def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    """Pool the last token representation."""
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-0.6B', padding_side='left')
model = AutoModel.from_pretrained('Qwen/Qwen3-Embedding-0.6B').to(model.device)

# Texts with instruction format for queries
task = 'Given a web search query, retrieve relevant passages that answer the query'
queries = [
    f'Instruct: {task}\nQuery:What is the capital of China?',
    f'Instruct: {task}\nQuery:Explain gravity'
]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other."
]

input_texts = queries + documents

# Tokenize
batch_dict = tokenizer(
    input_texts,
    padding=True,
    truncation=True,
    max_length=8192,  # context window (model supports up to 32K)
    return_tensors="pt"
)
batch_dict = {k: v.to(model.device) for k, v in batch_dict.items()}

# Forward pass
with torch.no_grad():
    outputs = model(**batch_dict)

# Pool and normalize
embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
embeddings = F.normalize(embeddings, p=2, dim=1)

# Compute similarity (first 2 are queries, rest are docs)
scores = embeddings[:2] @ embeddings[2:].T
print(scores.tolist())
# [[0.7646, 0.1414], [0.1355, 0.6000]]
```

## Flash Attention 2 Optimization

For GPU inference with significant speedup and memory reduction:

```python
import torch
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-4B', padding_side='left')
model = AutoModel.from_pretrained(
    'Qwen/Qwen3-Embedding-4B',
    attn_implementation="flash_attention_2",
    torch_dtype=torch.float16  # Use half precision for memory savings
).to("cuda")

# ... rest of the code same as above
```

## Custom Dimension Projection (MRL)

For models supporting MRL, you can project embeddings to a smaller dimension:

```python
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

model = AutoModel.from_pretrained('Qwen/Qwen3-Embedding-0.6B')
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-0.6B', padding_side='left')

# Get the full-dimensional embedding (1024 for 0.6B)
inputs = tokenizer(["Hello world"], return_tensors="pt", padding=True)
outputs = model(**inputs)
full_emb = F.normalize(outputs.last_hidden_state[:, -1], p=2, dim=1)  # (1, 1024)

# Project to custom dimension using the MRL linear layer
target_dim = 512
# The MRL projection is handled internally by sentence-transformers
# With raw transformers, you may need to access the projector:
if hasattr(model, 'dense'):
    projected = model.dense(full_emb)  # Apply projection head
else:
    projected = full_emb[:, :target_dim]  # Simple truncation fallback

print(projected.shape)  # (1, 512)
```

## Batch Processing with Variable-Length Texts

```python
import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F

model = AutoModel.from_pretrained('Qwen/Qwen3-Embedding-8B')
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-8B', padding_side='left')
model.eval()

texts = [
    "Short",
    "This is a moderately long sentence with some content to embed properly for similarity search.",
    "A" * 10000,  # Long text up to 32K context
]

# Variable-length batching
batch = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=32768,  # Full context window
    return_tensors="pt"
)

with torch.no_grad():
    outputs = model(**{k: v.to("cuda") for k, v in batch.items()})

embeddings = F.normalize(outputs.last_hidden_state[:, -1], p=2, dim=1)
print(embeddings.shape)  # (3, 4096)
```

## Inference Speed Benchmarking

```python
import time
import torch
from transformers import AutoTokenizer, AutoModel

model = AutoModel.from_pretrained(
    'Qwen/Qwen3-Embedding-8B',
    attn_implementation="flash_attention_2",
    torch_dtype=torch.float16
).to("cuda")
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-8B', padding_side='left')

text = "The quick brown fox jumps over the lazy dog." * 500  # ~15K tokens

# Warmup
_ = model(**tokenizer([text], return_tensors="pt", truncation=True, max_length=32768).to("cuda"))

# Benchmark
times = []
for _ in range(5):
    start = time.time()
    with torch.no_grad():
        _ = model(**tokenizer([text], return_tensors="pt", truncation=True, max_length=32768).to("cuda"))
    times.append(time.time() - start)

print(f"Avg: {sum(times)/len(times):.3f}s per encode")
```

## GPU Memory Profiling

```python
import torch
from transformers import AutoTokenizer, AutoModel

model = AutoModel.from_pretrained('Qwen/Qwen3-Embedding-8B')
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-8B', padding_side='left')

# Check model size
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")  # ~8 billion

# Check GPU memory
print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"GPU memory reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

## References

- Transformers docs: https://huggingface.co/docs/transformers/
- Hugging Face (0.6B): https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Hugging Face (4B): https://huggingface.co/Qwen/Qwen3-Embedding-4B
- Hugging Face (8B): https://huggingface.co/Qwen/Qwen3-Embedding-8B
