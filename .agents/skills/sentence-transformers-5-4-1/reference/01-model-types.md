# Model Types

## SentenceTransformer (Dense Embeddings)

The primary model class for mapping text to dense vector embeddings.

### Loading and Encoding

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
]
embeddings = model.encode(sentences)
print(embeddings.shape)  # (3, 384)
```

### Similarity Computation

```python
# Pairwise similarity matrix (all vs all)
similarities = model.similarity(embeddings, embeddings)
# tensor([[1.0000, 0.6660, 0.1046],
#         [0.6660, 1.0000, 0.1411],
#         [0.1046, 0.1411, 1.0000]])

# Pairwise (row-wise) similarity
from sentence_transformers.util import pairwise_cos_sim
scores = pairwise_cos_sim(embeddings[:2], embeddings[1:])
```

### Constructor Parameters

- `model_name_or_path` — Hugging Face Hub ID or local path
- `device` — `"cuda"`, `"cpu"`, `"mps"`, `"npu"` (auto-detected if None)
- `prompts` — dict mapping prompt names to prefix text, e.g. `{"query": "query: ", "passage": "passage: "}`
- `default_prompt_name` — which prompt to apply by default during encoding
- `backend` — `"torch"` (default), `"onnx"`, or `"openvino"`
- `similarity_fn_name` — `"cosine"`, `"dot"`, `"euclidean"`, `"manhattan"`
- `truncate_dim` — truncate embeddings to this dimension (Matryoshka-style)
- `model_kwargs` — forwarded to `AutoModel.from_pretrained` (torch_dtype, attn_implementation, device_map)
- `processor_kwargs` — forwarded to `AutoProcessor.from_pretrained`
- `cache_folder` — local cache directory (also via `SENTENCE_TRANSFORMERS_HOME` env var)
- `token` — Hugging Face auth token for private models

### Encoding Options

```python
embeddings = model.encode(
    sentences,
    batch_size=32,              # batch size for encoding
    show_progress_bar=True,     # display progress
    convert_to_tensor=True,     # return torch.Tensor instead of numpy
    normalize_embeddings=True,  # L2-normalize output
    prompt_name="query",        # apply named prompt prefix
    prompt="custom: ",          # inline prompt (overrides prompt_name)
    truncate_dim=256,           # Matryoshka truncation
)
```

### Multimodal Encoding

The Transformer module auto-detects modality from input data. For CLIP-style models:

```python
from PIL import Image
model = SentenceTransformer("sentence-transformers/clip-ViT-B-32-multilingual-v1")

# Encode images and text together
images = [Image.open("photo.jpg")]
texts = ["a photograph of a landscape"]
image_emb = model.encode(images)
text_emb = model.encode(texts)
```

The `CLIPModel` module is deprecated in 5.4 — use the base `Transformer` module directly, which handles multimodal architectures natively via modality auto-detection.

### Asymmetric Encoding with Router

For retrieval models that encode queries and documents differently:

```python
from sentence_transformers.sentence_transformer.modules import Router, Normalize

document_embedder = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")
query_embedder = SentenceTransformer("sentence-transformers/static-retrieval-mrl-en-v1")

router = Router.for_query_document(
    query_modules=list(query_embedder.children()),
    document_modules=list(document_embedder.children()),
)
model = SentenceTransformer(modules=[router, Normalize()])

# Encode with task routing
query_emb = model.encode("What is Python?", task="query")
doc_emb = model.encode("Python is a programming language.", task="document")
```

Route priority: exact `(task, modality)` → `(task, None)` → `(None, modality)` → `(None, None)` → direct lookup by task name → direct lookup by modality name → `default_route`.

## CrossEncoder (Rerankers)

CrossEncoders process sentence pairs jointly through the transformer and output a score. They are more accurate than SentenceTransformers for pairwise tasks but cannot pre-compute embeddings.

### Loading and Predicting

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

query = "How many people live in Berlin?"
passages = [
    "Berlin had a population of 3,520,031 registered inhabitants.",
    "Berlin has about 135 million day visitors yearly.",
    "In 2013 around 600,000 Berliners were in sport clubs.",
]

# Predict scores for pairs
scores = model.predict([(query, p) for p in passages])
print(scores)  # [8.607, 5.506, 6.353]
```

### Ranking Helper

```python
# Built-in ranking (sorted by score descending)
ranks = model.rank(query, passages, return_documents=True)
for rank in ranks:
    print(f"- #{rank['corpus_id']} ({rank['score']:.2f}): {rank['text']}")
```

### Constructor Parameters

- `num_labels` — 1 for regression (continuous score), >1 for classification
- `max_length` — max input sequence length (truncation)
- `activation_fn` — activation on logits during predict (default: Sigmoid for num_labels=1, Identity otherwise)

## SparseEncoder (Sparse Embeddings)

SparseEncoders produce vocabulary-sized sparse vectors with >99% zeros. Compatible with inverted-index search engines and hybrid retrieval.

### Loading and Encoding

```python
from sentence_transformers import SparseEncoder

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
]
embeddings = model.encode(sentences)
print(embeddings.shape)  # [3, 30522]

similarities = model.similarity(embeddings, embeddings)

# Check sparsity
stats = SparseEncoder.sparsity(embeddings)
print(f"Sparsity: {stats['sparsity_ratio']:.2%}")  # ~99.84%
```

Sparse vectors use COO format internally for memory efficiency. The `to_scipy_coo` utility converts embeddings to scipy sparse matrices.

## Backends

All three model types support multiple inference backends:

- **torch** (default) — native PyTorch, supports all features
- **onnx** — ONNX Runtime for optimized inference
- **openvino** — Intel OpenVINO for CPU-optimized inference

Export models with:

```python
from sentence_transformers import export_optimized_onnx_model
from sentence_transformers import export_dynamic_quantized_onnx_model

export_optimized_onnx_model(model, "model-onnx")
export_dynamic_quantized_onnx_model(model, "model-quantized")
```

## Model Saving and Loading

```python
# Save to disk
model.save("my-finetuned-model")

# Push to Hugging Face Hub
model.push_to_hub("username/my-model")

# Load from local path
model = SentenceTransformer("./my-finetuned-model")

# Load from Hub with specific revision
model = SentenceTransformer("username/my-model", revision="v1.0.0")
```

Models are saved with automatic model card generation based on `ModelCardData`.
