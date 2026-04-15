# Qwen3-Reranker Model Architecture

## Architecture Overview

Qwen3-Reranker models are built on the Qwen3 dense transformer architecture, optimized for binary relevance classification (yes/no) at the sequence level.

### Model Specifications

| Component | 0.6B | 4B | 8B |
|-----------|------|------|------|
| Parameters | 0.6B | 4B | 8B |
| Layers | 28 | 36 | 36 |
| Hidden Size | 1024 | 4096 | 6144 |
| Attention Heads | 16 | 32 | 48 |
| KV Heads | 8 | 16 | 24 |
| Context Length | 32K | 32K | 32K |
| Vocabulary Size | 152,064 | 152,064 | 152,064 |

### Key Architectural Features

**1. Causal Transformer with Classification Head**
- Uses causal (unidirectional) attention for efficient inference
- Final token prediction determines relevance score
- Outputs logits for "yes" and "no" tokens

**2. Chat Template Format**
The model uses Qwen3's chat template with system, user, and assistant roles:

```
system
Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".
</think>
user
<Instruct>: {instruction}

<Query>: {query}

<Document>: {document}
</think>
assistant
<think>

</think>


```

**3. Thinking Token Mechanism**
- Model generates `<think>` tokens before final prediction
- Allows internal reasoning before classification
- Final output is probability of "yes" token

## Input Format

### Standard Format

```python
def format_input(instruction, query, document):
    return f"""<Instruct>: {instruction}
<Query>: {query}
<Document>: {document}"""
```

**Example:**
```python
instruction = "Given a web search query, retrieve relevant passages that answer the query"
query = "What is the capital of France?"
document = "Paris is the capital and largest city of France."

input_text = format_input(instruction, query, document)
# Output:
# <Instruct>: Given a web search query, retrieve relevant passages that answer the query
# <Query>: What is the capital of France?
# <Document>: Paris is the capital and largest city of France.
```

### Chat Template Format (vLLM)

For vLLM deployment, use chat template:

```python
messages = [
    {
        "role": "system",
        "content": "Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\"."
    },
    {
        "role": "user",
        "content": f"<Instruct>: {instruction}\n\n<Query>: {query}\n\n<Document>: {document}"
    }
]

# Apply chat template
input_ids = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=False,
    enable_thinking=False
)
```

## Tokenization

### Tokenizer Configuration

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    padding_side='left',  # Important for batch processing
    trust_remote_code=True
)
```

**Key Settings:**
- `padding_side='left'`: Ensures consistent attention mask behavior
- `trust_remote_code=True`: Required for Qwen3 custom tokenizer
- Default truncation: 'longest_first' for query-document pairs

### Token IDs for Classification

The model predicts between two tokens:

```python
token_yes_id = tokenizer.convert_tokens_to_ids("yes")   # Typically 1982
token_no_id = tokenizer.convert_tokens_to_ids("no")     # Typically 2075

# Verify token IDs
print(f"Yes token ID: {token_yes_id}")
print(f"No token ID: {token_no_id}")
```

### Prefix and Suffix Tokens

For optimal performance, wrap inputs with prefix/suffix tokens:

```python
prefix = "system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".</think>\n</think>user\n"
suffix = "</think>\n</think>assistant\n<think>\n\n</think>\n\n"

prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

# Apply to input
def wrap_with_tokens(input_ids):
    return prefix_tokens + input_ids + suffix_tokens
```

## Scoring Mechanism

### Logit Computation

The model outputs logits for the next token prediction at the final position:

```python
import torch
import torch.nn.functional as F

@torch.no_grad()
def compute_scores(model, inputs):
    # Get model outputs
    outputs = model(**inputs)
    logits = outputs.logits[:, -1, :]  # Last position, all vocab
    
    # Extract logits for yes/no tokens
    yes_logits = logits[:, token_yes_id]
    no_logits = logits[:, token_no_id]
    
    # Stack and compute softmax
    batch_scores = torch.stack([no_logits, yes_logits], dim=1)
    batch_scores = F.log_softmax(batch_scores, dim=1)
    
    # Extract probability of "yes" (relevance score)
    scores = batch_scores[:, 1].exp().tolist()
    return scores
```

### Score Interpretation

| Score Range | Interpretation | Action |
|-------------|---------------|--------|
| 0.9 - 1.0 | Highly relevant | Include in top results |
| 0.7 - 0.9 | Relevant | Include with confidence |
| 0.5 - 0.7 | Marginally relevant | Consider context |
| 0.3 - 0.5 | Weakly relevant | Use with caution |
| 0.0 - 0.3 | Irrelevant | Filter out |

**Threshold Recommendations:**
- **Strict filtering**: Score > 0.7
- **Balanced**: Score > 0.5
- **Lenient**: Score > 0.3

### Cross-Encoder Alternative

For sentence-transformers compatibility:

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder('Qwen/Qwen3-Reranker-0.6B')

pairs = [
    ("What is Python?", "Python is a programming language"),
    ("What is Python?", "The python is a type of snake")
]

scores = model.predict(pairs)
# Returns normalized similarity scores (not probabilities)
```

## Attention Mechanism

### Flash Attention 2

For GPU acceleration, enable flash attention:

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2",  # Enable flash attention
    device_map="auto"
)
```

**Benefits:**
- 2-3x faster inference
- Reduced memory usage
- Better scaling for long sequences

**Requirements:**
- CUDA-capable GPU (Compute Capability >= 7.0)
- `flash-attn` package installed
- PyTorch with CUDA support

### Context Length Management

The model supports up to 32K tokens, but practical limits depend on use case:

```python
# Recommended max lengths by use case
MAX_LENGTHS = {
    "short_query": 512,      # Simple Q&A
    "web_search": 2048,      # Web document retrieval
    "code_search": 4096,     # Code snippets with context
    "long_document": 8192,   # Full document ranking
    "max_context": 32768     # Maximum supported
}

# Dynamic truncation
def truncate_pair(query, document, max_length):
    query_tokens = len(tokenizer.encode(query))
    doc_max_tokens = max_length - query_tokens - 100  # Reserve for special tokens
    
    document = tokenizer.decode(
        tokenizer.encode(document)[:doc_max_tokens]
    )
    return query, document
```

## Batch Processing

### Efficient Batching

```python
def batch_rerank(model, tokenizer, pairs, instruction, batch_size=32, max_length=2048):
    all_scores = []
    
    for i in range(0, len(pairs), batch_size):
        batch_pairs = pairs[i:i+batch_size]
        
        # Format batch
        formatted = [
            format_input(instruction, q, d)
            for q, d in batch_pairs
        ]
        
        # Tokenize with padding
        inputs = tokenizer(
            formatted,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        ).to(model.device)
        
        # Compute scores
        batch_scores = compute_scores(model, inputs)
        all_scores.extend(batch_scores)
    
    return all_scores
```

### Memory Optimization

For large batches, use gradient checkpointing and mixed precision:

```python
from torch.cuda.amp import autocast

@torch.no_grad()
def batch_rerank_amp(model, tokenizer, pairs, instruction, batch_size=32):
    all_scores = []
    
    for i in range(0, len(pairs), batch_size):
        batch_pairs = pairs[i:i+batch_size]
        formatted = [format_input(instruction, q, d) for q, d in batch_pairs]
        
        inputs = tokenizer(
            formatted,
            padding=True,
            truncation=True,
            max_length=2048,
            return_tensors="pt"
        ).to(model.device)
        
        # Use automatic mixed precision
        with autocast():
            scores = compute_scores(model, inputs)
        
        all_scores.extend(scores)
    
    return all_scores
```

## Training Details

### Training Objectives

Qwen3-Reranker is trained with:
1. **Pairwise ranking loss**: Compare document pairs for same query
2. **Pointwise classification**: Binary relevance (yes/no) prediction
3. **Listwise optimization**: Optimize entire ranked list (NDCG, MRR)

### Training Data

- **Multilingual corpus**: 100+ languages
- **Domain diversity**: Web search, code, academic, conversational
- **Instruction variety**: Task-specific ranking instructions
- **Synthetic data**: Augmented with LLM-generated examples

### Loss Function

```python
def ranking_loss(model_outputs, relevance_labels):
    """
    Binary cross-entropy loss for yes/no classification
    """
    yes_logits = model_outputs[:, token_yes_id]
    no_logits = model_outputs[:, token_no_id]
    
    # Stack and compute softmax
    logits = torch.stack([no_logits, yes_logits], dim=1)
    probs = F.softmax(logits, dim=1)
    
    # Binary cross-entropy (relevance is 0 or 1)
    loss = F.binary_cross_entropy(probs[:, 1], relevance_labels.float())
    return loss
```

## Quantization and Optimization

### FP16 Inference

```python
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    torch_dtype=torch.float16,  # Half precision
    device_map="auto"
)
```

**Memory Savings:**
- FP32 → FP16: 50% reduction
- FP16 → INT8: Additional 50% reduction (requires calibration)

### ONNX Export (Experimental)

```python
import onnx
import onnxruntime as ort

# Export to ONNX
from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-Reranker-0.6B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Reranker-0.6B")

# Example input
dummy_input = torch.randint(0, 1000, (1, 512))
attention_mask = torch.ones((1, 512))

# Export
torch.onnx.export(
    model,
    (dummy_input, attention_mask),
    "qwen3_reranker.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "logits": {0: "batch_size"}
    }
)

# Load with ONNX Runtime
session = ort.InferenceSession("qwen3_reranker.onnx")
```

## Best Practices

### Input Preparation

1. **Always use instructions**: 1-5% performance improvement
2. **Write instructions in English**: Even for non-English queries
3. **Trim long documents**: Focus on most relevant sections
4. **Preserve document structure**: Keep headings, lists, formatting

### Model Selection

1. **Start with 0.6B**: Test baseline performance
2. **Scale to 4B if needed**: Better accuracy for complex tasks
3. **Use 8B for critical applications**: Maximum quality when latency allows

### Performance Tuning

1. **Enable flash attention**: If GPU supports it
2. **Use appropriate batch sizes**: Balance memory and throughput
3. **Cache embeddings**: For repeated queries in RAG systems
4. **Profile regularly**: Monitor latency and accuracy metrics

## References

- **Architecture Paper**: https://arxiv.org/abs/2506.05176
- **Qwen3 Documentation**: https://qwenlm.github.io/blog/qwen3-embedding/
- **Transformers Library**: https://huggingface.co/docs/transformers
- **Flash Attention**: https://github.com/Dao-AILab/flash-attention
