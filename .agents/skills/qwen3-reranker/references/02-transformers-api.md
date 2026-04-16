# Raw Hugging Face Transformers API

## Prerequisites

```python
# Requires transformers>=4.51.0
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
```

**Important:** Using `transformers<4.51.0` will raise:
```
KeyError: 'qwen3'
```

## Core Implementation Pattern

The reranker uses a causal LM with special prefix/suffix tokens and computes relevance by comparing "yes" vs "no" token logits at the final position.

### Complete Implementation

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def format_instruction(instruction: str, query: str, doc: str) -> str:
    """Format instruction + query + document for the reranker."""
    if instruction is None:
        instruction = 'Given a web search query, retrieve relevant passages that answer the query'
    return f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}"

def process_inputs(pairs: list, tokenizer, model, prefix_tokens, suffix_tokens, max_length):
    """Tokenize pairs with prefix/suffix tokens and pad for batch inference."""
    inputs = tokenizer(
        pairs, padding=False, truncation='longest_first',
        return_attention_mask=False,
        max_length=max_length - len(prefix_tokens) - len(suffix_tokens)
    )
    # Prepend/append special tokens
    for i, ele in enumerate(inputs['input_ids']):
        inputs['input_ids'][i] = prefix_tokens + ele + suffix_tokens
    # Pad and move to device
    inputs = tokenizer.pad(inputs, padding=True, return_tensors="pt", max_length=max_length)
    for key in inputs:
        inputs[key] = inputs[key].to(model.device)
    return inputs

@torch.no_grad()
def compute_logits(inputs: dict, model, token_true_id, token_false_id) -> list:
    """Compute relevance scores from logits."""
    batch_scores = model(**inputs).logits[:, -1, :]
    true_vector = batch_scores[:, token_true_id]
    false_vector = batch_scores[:, token_false_id]
    # Stack as [false, true] and apply log-softmax
    batch_scores = torch.stack([false_vector, true_vector], dim=1)
    batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
    scores = batch_scores[:, 1].exp().tolist()
    return scores

# === Setup ===
model_name = "Qwen/Qwen3-Reranker-4B"
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
model = AutoModelForCausalLM.from_pretrained(model_name).eval()

# Enable flash attention 2 for acceleration (optional but recommended)
# model = AutoModelForCausalLM.from_pretrained(
#     model_name, torch_dtype=torch.float16, attn_implementation="flash_attention_2"
# ).cuda().eval()

token_false_id = tokenizer.convert_tokens_to_ids("no")
token_true_id = tokenizer.convert_tokens_to_ids("yes")
max_length = 8192

# Special chat template tokens
prefix = "<|im_system|>\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".\n\n<|im_user|>\n"
suffix = "<|im_start|>assistant\n<|end_of_text|>\n<|im_end|>"
prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

# === Inference ===
instruction = 'Given a web search query, retrieve relevant passages that answer the query'
queries = ["What is the capital of China?", "Explain gravity"]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun.",
]

pairs = [format_instruction(instruction, q, d) for q, d in zip(queries, documents)]
inputs = process_inputs(pairs, tokenizer, model, prefix_tokens, suffix_tokens, max_length)
scores = compute_logits(inputs, model, token_true_id, token_false_id)

print("scores:", scores)
```

## Key Implementation Details

### Why Prefix/Suffix Tokens?

The model uses a chat template with special tokens. The `prefix` contains the system prompt and user instruction, while the `suffix` marks the assistant response start. These are pre-encoded and prepended/appended to each tokenized pair because the tokenizer's truncation logic needs to account for them separately.

### Scoring Mechanism

1. Forward pass through the model → get logits at final position
2. Extract logits for "yes" (true) and "no" (false) tokens
3. Stack as `[false_logit, true_logit]`
4. Apply `log_softmax` along dim=1
5. Exponentiate and take the "true" channel → gives probability-like score

### Memory Optimization with Flash Attention 2

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2"
).cuda().eval()
```

This significantly reduces memory usage and speeds up inference. Requires the `xformers` package.

### Batch Processing

The `process_inputs` function handles arbitrary batch sizes by:
1. Tokenizing without padding (to respect truncation)
2. Manually prepending/appending special tokens
3. Padding to max length with `tokenizer.pad()`

## Model-Specific Notes

| Aspect | 0.6B | 4B | 8B |
|--------|------|----|-----|
| VRAM (float16) | ~1.5 GB | ~9 GB | ~17 GB |
| Max recommended batch | 64+ | 16-32 | 4-8 |
| `max_length` | 8192 | 8192 | 8192 |

## References

- Hugging Face Transformers docs: https://huggingface.co/docs/transformers/
- Qwen3-Reranker model cards on HF: see main SKILL.md external_references
