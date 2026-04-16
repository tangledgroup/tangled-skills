# API Reference

## Sentence Transformers: CrossEncoder

### Constructor

```python
CrossEncoder(model_name_or_path, tokenizer_model_max_length=None, trust_remote_code=True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name_or_path` | str | Required | HuggingFace repo ID or local path |
| `tokenizer_model_max_length` | int | None | Override max sequence length |
| `trust_remote_code` | bool | True | Execute remote model code |

### Methods

#### predict(pairs, prompt=None, activation_fn=None, batch_size=32)

Compute relevance scores for (query, document) pairs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pairs` | list[tuple[str|dict, str|dict]] | Required | List of (query, doc) tuples |
| `prompt` | str | None | Custom instruction string |
| `activation_fn` | callable | None | Post-processing function (e.g., `torch.nn.Sigmoid()`) |
| `batch_size` | int | 32 | Batches per forward pass |

**Returns:** `list[float]` — Relevance scores (one per pair)

#### rank(query, documents, prompt=None, top_k=10)

Rank documents by relevance to a query.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | Required | Query string |
| `documents` | list[str|dict] | Required | Candidate documents |
| `prompt` | str | None | Custom instruction string |
| `top_k` | int | 10 | Number of top results to return |

**Returns:** `list[dict]` — Each dict has `corpus_id` (int) and `score` (float), sorted descending by score.

### Input Document Formats

Documents can be specified in three ways:

```python
# Format 1: Text-only (string)
doc = "Plain text document content"

# Format 2: Image URL (string)
doc = "https://example.com/image.jpg"

# Format 3: Mixed modalities (dict)
doc = {
    "text": "Description of the image",
    "image": "https://example.com/image.jpg",
}
```

The query is always a string (plain text).

---

## Native Transformers API: Qwen3VLReranker

### Constructor

```python
Qwen3VLReranker(model_name_or_path, torch_dtype=torch.float32, attn_implementation=None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name_or_path` | str | Required | HuggingFace repo ID or local path |
| `torch_dtype` | torch.dtype | torch.float32 | Model precision |
| `attn_implementation` | str | None | Attention backend (e.g., `"flash_attention_2"`) |

### Methods

#### process(inputs)

Process a batch of query-document pairs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `inputs` | dict | Required | See structure below |

**Returns:** `list[float]` — Relevance scores for each document.

### Input Structure

```python
inputs = {
    "instruction": str,          # Custom instruction text
    "query": {"text": str},      # Query (always text-only)
    "documents": [               # List of documents
        {"text": str},           # Text-only document
        {"image": str},          # Image URL document
        {"text": str, "image": str},  # Mixed document
    ],
    "fps": float,                # Frames per second for video (default: 1.0)
}
```

---

## vLLM Integration

### Engine Configuration

```python
from vllm import LLM, EngineArgs

engine_args = EngineArgs(
    model="Qwen/Qwen3-VL-Reranker-2B",
    runner="pooling",              # Required for reranking
    dtype="bfloat16",
    trust_remote_code=True,
    hf_overrides={
        "architectures": ["Qwen3VLForSequenceClassification"],
        "classifier_from_token": ["no", "yes"],
        "is_original_qwen3_reranker": True,
    },
)

llm = LLM(**vars(engine_args))
```

### Scoring

```python
# Score a single (query, document) pair
outputs = llm.score(query_text, doc_param, chat_template=chat_template)
score = outputs[0].outputs.score
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query_text` | str | Required | Query string |
| `doc_param` | dict | Required | Document in ScoreMultiModalParam format |
| `chat_template` | str | None | Jinja template for formatting |

### Chat Template Path

The vLLM chat template is located at:
```
vllm/examples/pooling/score/template/qwen3_vl_reranker.jinja
```

Load it with:
```python
template_path = Path("vllm/examples/pooling/score/template/qwen3_vl_reranker.jinja")
chat_template = template_path.read_text() if template_path.exists() else None
```
