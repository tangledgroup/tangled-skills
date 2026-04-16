# vLLM Deployment for High-Throughput Reranking

## Prerequisites

```bash
pip install vllm>=0.8.5 torch transformers
```

## Core Implementation

### Complete Production Example

```python
import math
import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.distributed.parallel_state import destroy_model_parallel
from vllm.inputs.data import TokensPrompt

def format_instruction(instruction: str, query: str, doc: str) -> list:
    """Format as chat messages for vLLM."""
    return [
        {
            "role": "system",
            "content": 'Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".'
        },
        {
            "role": "user",
            "content": f"<Instruct>: {instruction}\n\n<Query>: {query}\n\n<Document>: {doc}"
        }
    ]

def process_inputs(pairs: list, instruction: str, max_length: int, suffix_tokens: list, tokenizer) -> list:
    """Apply chat template and truncate to max length."""
    messages = [format_instruction(instruction, query, doc) for query, doc in pairs]
    tokenized = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=False, enable_thinking=False
    )
    # Truncate each sequence to max_length + suffix_tokens
    tokenized = [seq[:max_length] + suffix_tokens for seq in tokenized]
    return [TokensPrompt(prompt_token_ids=seq) for seq in tokenized]

def compute_logits(model: LLM, messages: list, sampling_params: SamplingParams,
                   true_token: int, false_token: int) -> list:
    """Extract relevance scores from generated outputs."""
    outputs = model.generate(messages, sampling_params, use_tqdm=False)
    scores = []
    for i in range(len(outputs)):
        final_logits = outputs[i].outputs[0].logprobs[-1]
        true_logit = final_logits.get(true_token, None)
        false_logit = final_logits.get(false_token, None)

        # Fallback if token not in logprobs
        if true_logit is None:
            true_score = 0.0
        else:
            true_score = math.exp(true_logit.logprob)

        if false_logit is None:
            false_score = 1.0
        else:
            false_score = math.exp(false_logit.logprob)

        score = true_score / (true_score + false_score)
        scores.append(score)
    return scores

# === Setup ===
model_name = "Qwen/Qwen3-Reranker-4B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
number_of_gpu = torch.cuda.device_count()

model = LLM(
    model=model_name,
    tensor_parallel_size=number_of_gpu,
    max_model_len=10000,
    enable_prefix_caching=True,
    gpu_memory_utilization=0.8
)

tokenizer.padding_side = "left"
tokenizer.pad_token = tokenizer.eos_token

suffix = "</s>\n\n"
max_length = 8192
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

true_token = tokenizer("yes", add_special_tokens=False).input_ids[0]
false_token = tokenizer("no", add_special_tokens=False).input_ids[0]

sampling_params = SamplingParams(
    temperature=0,          # Deterministic — no sampling
    max_tokens=1,           # Only predict one token
    logprobs=20,            # Need top-20 for logprob access
    allowed_token_ids=[true_token, false_token]  # Force yes/no
)

# === Inference ===
instruction = 'Given a web search query, retrieve relevant passages that answer the query'
queries = ["What is the capital of China?", "Explain gravity"]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun.",
]

pairs = list(zip(queries, documents))
inputs = process_inputs(pairs, instruction, max_length - len(suffix_tokens), suffix_tokens, tokenizer)
scores = compute_logits(model, inputs, sampling_params, true_token, false_token)
print('scores:', scores)

# Clean up model parallel state
destroy_model_parallel()
```

## Key vLLM Configuration Parameters

### SamplingParams for Reranking

```python
SamplingParams(
    temperature=0,              # Deterministic — always pick highest logit
    max_tokens=1,               # Only predict one token (yes or no)
    logprobs=20,                # Need access to log probabilities
    allowed_token_ids=[true_token, false_token]  # Restrict output space
)
```

The `allowed_token_ids` parameter is critical — it forces the model to choose only between "yes" and "no", ignoring all other tokens. This is more efficient than post-filtering.

### LLM Initialization

```python
LLM(
    model="Qwen/Qwen3-Reranker-4B",
    tensor_parallel_size=number_of_gpu,  # Spread across GPUs
    max_model_len=10000,                  # Slightly above 8192 for special tokens
    enable_prefix_caching=True,           # Cache KV cache for repeated prefixes
    gpu_memory_utilization=0.8            # Leave room for activations
)
```

## Performance Tips

### Prefix Caching

With `enable_prefix_caching=True`, vLLM caches the KV-cache for common query/instruction prefixes. This is especially effective when reranking many documents against the same query:

```python
# Rerank multiple queries efficiently — each unique (instruction, query) pair
# gets cached after first use
model = LLM(model=model_name, enable_prefix_caching=True, ...)
```

### Batch Size Tuning

| Model | GPU VRAM | Recommended Batch | GPUs Needed |
|-------|----------|-------------------|-------------|
| 0.6B | ~1.5 GB | 128+ | 1 (even CPU possible) |
| 4B   | ~9 GB  | 32-64             | 1-2           |
| 8B   | ~17 GB | 16-32             | 2-4           |

### Tensor Parallelism

For 4B and 8B models on multi-GPU setups:

```python
model = LLM(
    model=model_name,
    tensor_parallel_size=4,  # Spread across 4 GPUs
    max_model_len=10000,
    enable_prefix_caching=True,
    gpu_memory_utilization=0.85
)
```

## Score Computation Details

The score formula in `compute_logits`:

```python
true_score = exp(true_logit)
false_score = exp(false_logit)
score = true_score / (true_score + false_score)  # softmax over yes/no
```

This produces scores in [0, 1], directly interpretable as relevance probability. Unlike the raw Transformers API which uses `log_softmax`, vLLM returns per-token log-probabilities that must be manually combined.

## References

- vLLM docs: https://docs.vllm.ai/
- Qwen3-Reranker model cards on HF: see main SKILL.md external_references
