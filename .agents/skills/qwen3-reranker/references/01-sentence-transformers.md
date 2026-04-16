# Sentence Transformers Usage (CrossEncoder)

## Installation

```bash
pip install sentence_transformers torch
```

**Note:** Requires `transformers>=4.51.0`. Earlier versions will raise:
```
KeyError: 'qwen3'
```

## Basic Usage

### Loading the Model

```python
from sentence_transformers import CrossEncoder

# Choose model size based on your needs:
model_06 = CrossEncoder("Qwen/Qwen3-Reranker-0.6B")   # Fastest, lowest VRAM
model_4b = CrossEncoder("Qwen/Qwen3-Reranker-4B")      # Best balance
model_8b = CrossEncoder("Qwen/Qwen3-Reranker-8B")      # Highest accuracy
```

### Scoring Query-Document Pairs

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Reranker-4B")

query = "What is the capital of China?"
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun.",
    "China has been a major economic power for centuries, with rich cultural heritage.",
]

# Score all pairs — returns raw logit differences
pairs = [(query, doc) for doc in documents]
scores = model.predict(pairs)
print(scores)
# [ 6.4375 -14.375  -8.25   ]  (example output)

# Get ranked results — most relevant first
rankings = model.rank(query, documents)
print(rankings)
# [{'corpus_id': 0, 'score': 6.4375},
#  {'corpus_id': 2, 'score': -8.25},
#  {'corpus_id': 1, 'score': -14.375}]
```

### Probability Scores (Sigmoid)

By default, scores are raw logit differences. To get probability-like scores in [0, 1]:

```python
import torch

scores_prob = model.predict(
    [(query, doc) for doc in documents],
    activation_fn=torch.nn.Sigmoid()
)
print(scores_prob)
# [0.998, 0.000, 0.000]  (example output)
```

## Custom Instructions

### Using Built-in Prompts

The model comes with a default prompt named `"query"` that injects:
> "Given a web search query, retrieve relevant passages that answer the query"

This is used automatically when you call `rank()` or `predict()`.

### Creating Custom Prompt Templates

You can define custom instruction templates and switch between them:

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "Qwen/Qwen3-Reranker-4B",
    prompts={
        "classification": "Classify whether the document matches the query topic",
        "legal": "Determine if this legal document is relevant to the case description",
        "medical": "Assess whether this medical text addresses the patient's symptoms",
    },
    default_prompt_name="query",  # or any custom name
)

# Use the classification prompt
rankings = model.rank(query, documents, prompt_name="classification")

# Or set it at load time
model = CrossEncoder(
    "Qwen/Qwen3-Reranker-4B",
    prompts={"medical": "Assess whether this medical text addresses the patient's symptoms"},
    default_prompt_name="medical",
)
rankings = model.rank(query, documents)  # Uses "medical" prompt automatically
```

## Production Patterns

### Batch Reranking After Embedding Retrieval

A common RAG pattern: use a fast embedding model to retrieve top-N candidates, then rerank with Qwen3-Reranker.

```python
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder

# Stage 1: Fast embedding retrieval (top-100)
embedder = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
query_embedding = embedder.encode(query)
doc_embeddings = embedder.encode(documents)
similarities = query_embedding @ doc_embeddings.T
top_k_indices = torch.topk(similarities.flatten(), k=100).indices

# Stage 2: Cross-encoder reranking (top-100 → top-5)
reranker = CrossEncoder("Qwen/Qwen3-Reranker-4B")
top_k_docs = [documents[i] for i in top_k_indices.tolist()]
rankings = reranker.rank(query, top_k_docs)

# Return top-5 reranked results
final_results = rankings[:5]
```

### Caching and Reuse

CrossEncoder models are loaded once and reused:

```python
_CROSS_ENCODER_CACHE = {}

def get_reranker(model_name="Qwen/Qwen3-Reranker-4B"):
    if model_name not in _CROSS_ENCODER_CACHE:
        _CROSS_ENCODER_CACHE[model_name] = CrossEncoder(model_name)
    return _CROSS_ENCODER_CACHE[model_name]

# Later...
reranker = get_reranker()
rankings = reranker.rank(query, candidates)
```

### Device Management

```python
import torch
from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "Qwen/Qwen3-Reranker-4B",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# Or explicitly on GPU
model = CrossEncoder("Qwen/Qwen3-Reranker-4B")
model.model.cuda()
```

## Model-Specific Score Ranges

Different model sizes produce different score magnitudes. Always compare scores from the same model:

| Model | Example Scores (same query/docs) |
|-------|----------------------------------|
| 0.6B | `[ 7.625, -11.375]` |
| 4B   | `[  6.4375, -14.375]` |
| 8B   | `[  5.0625, -14.25]` |

Using `torch.nn.Sigmoid()` normalizes all models to the [0, 1] range.

## References

- Sentence Transformers docs: https://sbert.net/docs/cross_encoder/usage/ranking.html
- Qwen3-Reranker HF pages: see main SKILL.md external_references
