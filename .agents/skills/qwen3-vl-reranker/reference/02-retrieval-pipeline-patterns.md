# Retrieval Pipeline Patterns

## Two-Stage Retrieval Architecture

The canonical pattern pairs Qwen3-VL-Embedding (recall) with Qwen3-VL-Reranker (ranking):

```
User Query ──► Embedding Model ──► Top-K Candidates (K=100–1000)
                                      │
                                      ▼
                              Reranker Model ──► Ranked Results (Top-N, N=10–50)
```

### Stage 1: Recall with Embedding Model

```python
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("Qwen/Qwen3-VL-Embedding-2B")

# Encode documents once at indexing time
doc_texts = ["Document A...", "Document B...", "..."]
doc_embeddings = embedder.encode(doc_texts)  # Shape: (N, embedding_dim)

# Encode query at search time
query_embedding = embedder.encode([query])[0]

# Fast cosine similarity search
import numpy as np
similarity_scores = doc_embeddings @ query_embedding / (np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding))
top_k_indices = np.argsort(similarity_scores)[-K:][::-1]  # Top K
```

### Stage 2: Reranking with CrossEncoder

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("Qwen/Qwen3-VL-Reranker-2B")

# Only rerank the top-K candidates
candidate_docs = [doc_texts[i] for i in top_k_indices]
pairs = [(query, doc) for doc in candidate_docs]
reranked_scores = reranker.predict(pairs, prompt=custom_instruction)

# Reorder by reranker scores
ranked_results = sorted(
    zip(top_k_indices, reranked_scores),
    key=lambda x: x[1],
    reverse=True
)
```

### Full Pipeline Example (Multimodal)

```python
from sentence_transformers import CrossEncoder
import torch

# Load reranker
reranker = CrossEncoder("Qwen/Qwen3-VL-Reranker-8B")

query = "What does the architecture diagram show?"

# Documents: mix of text descriptions and image URLs
documents = [
    {"text": "The system architecture overview", "image": "https://example.com/arch.png"},
    {"text": "User authentication flowchart"},
    {"text": "Database schema design", "image": "https://example.com/db-schema.png"},
    # ... more candidates from recall stage
]

prompt = "Find documents relevant to the user's visual query about architecture."
pairs = [(query, doc) for doc in documents]

scores = reranker.predict(pairs, activation_fn=torch.nn.Sigmoid(), prompt=prompt)
rankings = reranker.rank(query, documents, prompt=prompt)

for i, result in enumerate(rankings[:5]):
    print(f"Rank {i+1}: score={result['score']:.4f}, doc_id={result['corpus_id']}")
```

## Instruction Engineering Guide

### Best Practices

1. **Always provide an instruction** — 1–5% improvement over default
2. **Write instructions in English** — even for non-English queries (training data was primarily English)
3. **Match instruction to task type**:

| Task Type | Recommended Instruction |
|-----------|----------------------|
| General text retrieval | `"Retrieve text relevant to the user's query."` |
| Image-text retrieval | `"Retrieve images or text relevant to the user's query."` |
| Visual document search | `"Find documents matching the visual content of the query."` |
| Video understanding | `"Identify video segments relevant to the user's query."` |
| Code retrieval | `"Retrieve code snippets relevant to the user's query."` |

### Instruction Format

```python
# Using Sentence Transformers
scores = model.predict(pairs, prompt="Your custom instruction here")

# Using Native Transformers API
inputs = {
    "instruction": "Your custom instruction here",  # <-- goes here
    "query": {"text": "..."},
    "documents": [...],
}
```

## Error Handling and Edge Cases

### Empty Documents

```python
# The model handles empty strings gracefully
pairs = [("query", "")]
scores = model.predict(pairs)  # Returns low score
```

### Invalid Image URLs

```python
# If an image URL is unreachable, the model may return NaN or error
# Always validate URLs before passing to the model:
import requests

def is_valid_image_url(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200 and 'image' in r.headers.get('Content-Type', '')
    except:
        return False

valid_docs = [doc for doc in documents if not isinstance(doc, str) or is_valid_image_url(doc)]
```

### Batch Size Limits

```python
# Sentence Transformers CrossEncoder has a max batch size
# Default is typically 32–64; exceed it and split manually:

def batch_predict(model, pairs, prompt=None, batch_size=32):
    all_scores = []
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i+batch_size]
        scores = model.predict(batch, prompt=prompt)
        all_scores.extend(scores)
    return all_scores
```
