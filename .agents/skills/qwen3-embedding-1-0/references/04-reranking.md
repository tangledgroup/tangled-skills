# Reranking with Qwen3 Embedding

Guide to using Qwen3 Embedding models for reranking tasks, including cross-encoder scoring, ranking APIs, and score calibration.

## Reranking Overview

Reranking is a two-stage retrieval process:
1. **Retrieve**: Fast bi-encoder retrieves top-K candidates (K=50-500)
2. **Rerank**: Accurate cross-encoder scores and reorders top-K candidates

Qwen3 Embedding models can function as both retrievers and rerankers.

## Cross-Encoder Reranking

### Basic Usage

```python
from sentence_transformers import CrossEncoder

# Load Qwen3 as cross-encoder
model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

# Query and candidate documents
query = "How to install Python on Windows?"
candidates = [
    "Python installation guide for Linux systems.",
    "Step-by-step Python setup on Windows 10/11.",
    "Advanced Python programming techniques.",
    "Download Python installer from python.org for Windows."
]

# Score query-candidate pairs
pairs = [(query, candidate) for candidate in candidates]
scores = model.predict(pairs)

print(scores)
# tensor([2.3456, 8.9012, 1.2345, 7.6543])

# Higher scores = more relevant
```

### Built-in Ranking API

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

query = "Best practices for machine learning"
candidates = [...]  # List of documents

# Rank candidates (returns top results sorted by score)
ranks = model.rank(
    query, 
    candidates,
    top_k=5,  # Return top 5
    return_scores=True,
    return_documents=True
)

for rank in ranks:
    print(f"Score: {rank['score']:.2f}")
    print(f"Rank: {rank['corpus_id']}")
    print(f"Text: {rank['text'][:100]}...")
    print("---")
```

### Batch Reranking

```python
from sentence_transformers import CrossEncoder
import numpy as np

model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

# Multiple queries with same candidate set
queries = [
    "Python installation Windows",
    "Install Python on PC",
    "Set up Python development environment"
]
candidates = [...]  # Same candidates for all queries

# Rerank for each query
all_ranks = []
for query in queries:
    ranks = model.rank(query, candidates, top_k=10)
    all_ranks.append(ranks)

# Convert to numpy array for analysis
scores_array = np.array([[r['score'] for r in ranks] for ranks in all_ranks])
```

## Retrieve-and-Rerank Pipeline

### Complete Pipeline Example

```python
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# Stage 1: Fast retrieval with bi-encoder
retriever = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Stage 2: Accurate reranking with cross-encoder
reranker = CrossEncoder("Qwen/Qwen3-Embedding-4B")

# Prepare corpus
corpus = [...]  # Large document collection (10K+ documents)
corpus_embeddings = retriever.encode(corpus, normalize_embeddings=True)

def search_and_rerank(query, retrieve_k=100, rerank_k=10):
    """
    Two-stage retrieval:
    1. Retrieve top-K candidates with bi-encoder
    2. Rerank with cross-encoder
    """
    # Stage 1: Retrieve
    query_embedding = retriever.encode(query, normalize_embeddings=True)
    similarities = corpus_embeddings @ query_embedding
    top_indices = similarities.argsort()[-retrieve_k:][::-1]
    top_candidates = [corpus[i] for i in top_indices]
    
    # Stage 2: Rerank
    if len(top_candidates) > 1:
        ranks = reranker.rank(query, top_candidates, top_k=rerank_k)
        return ranks
    else:
        # Fallback if only one candidate
        return [{'corpus_id': 0, 'text': top_candidates[0], 
                 'score': reranker.predict([(query, top_candidates[0])])[0]}]

# Usage
results = search_and_rerank("How to debug Python code?", retrieve_k=50, rerank_k=5)
for result in results:
    print(f"Score: {result['score']:.2f} - {result['text'][:80]}...")
```

### Asymmetric Pipeline (Different Models)

```python
# Use smaller model for retrieval, larger for reranking
retriever = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")  # Fast
reranker = CrossEncoder("Qwen/Qwen3-Embedding-8B")  # Accurate

# This gives best of both worlds: speed + accuracy
```

## Score Calibration

### Understanding Scores

Cross-encoder scores are **not probabilities** - they're raw logit values:

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

query = "What is machine learning?"
candidates = [
    "Machine learning is a subset of AI.",  # Relevant
    "The weather is nice today."            # Irrelevant
]

scores = model.predict([(query, c) for c in candidates])
print(scores)  # tensor([7.2345, -2.1234])

# Scores can be negative and don't sum to 1
```

### Converting to Probabilities

```python
import torch

model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

query = "Python installation"
candidates = [...]
pairs = [(query, c) for c in candidates]

# Get raw scores
scores = model.predict(pairs)

# Convert to probabilities with softmax
probs = torch.softmax(scores, dim=0)
print(probs)  # tensor([0.65, 0.25, 0.08, 0.02])

# Or sigmoid for independent relevance probabilities
sigmoids = torch.sigmoid(scores)
print(sigmoids)  # tensor([0.99, 0.85, 0.12, 0.03])
```

### Thresholding

```python
from sentence_transformers import CrossEncoder
import torch

model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

# Determine threshold from validation data
validation_pairs = [...]
validation_labels = [...]  # 1=relevant, 0=irrelevant

scores = model.predict(validation_pairs)
scores = scores.numpy()

# Find optimal threshold (e.g., maximize F1)
from sklearn.metrics import f1_score
thresholds = np.linspace(-2, 10, 100)
best_threshold = 0
best_f1 = 0

for thresh in thresholds:
    predictions = (scores >= thresh).astype(int)
    f1 = f1_score(validation_labels, predictions)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = thresh

print(f"Optimal threshold: {best_threshold:.2f} (F1={best_f1:.3f})")

# Apply threshold in production
def filter_relevant(query, candidates, threshold=best_threshold):
    scores = model.predict([(query, c) for c in candidates])
    return [c for c, s in zip(candidates, scores) if s >= threshold]
```

## Advanced Reranking Techniques

### Reciprocal Rank Fusion

```python
def reciprocal_rank_fusion(results_list, k=60):
    """
    Fuse results from multiple queries or models using RRF.
    
    Args:
        results_list: List of lists, each containing (doc_id, score) tuples
        k: RRF parameter (typically 60)
    
    Returns:
        List of (doc_id, fused_score) sorted by fused score
    """
    from collections import defaultdict
    
    doc_scores = defaultdict(float)
    
    for results in results_list:
        for rank, (doc_id, score) in enumerate(results):
            # RRF score: 1 / (k + rank)
            doc_scores[doc_id] += 1.0 / (k + rank)
    
    # Sort by fused score
    return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

# Usage with query expansion
queries = [
    "Python installation Windows",
    "Install Python on PC",
    "Download Python for Windows"
]

all_results = []
for query in queries:
    ranks = reranker.rank(query, candidates, top_k=20)
    results = [(r['corpus_id'], r['score']) for r in ranks]
    all_results.append(results)

fused_results = reciprocal_rank_fusion(all_results)
```

### Multi-Stage Reranking

```python
# Stage 1: Retrieve 500 with small model
retriever_small = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
top_500 = retrieve_top_k(query, corpus, retriever_small, k=500)

# Stage 2: Rerank to 50 with medium model
reranker_medium = CrossEncoder("Qwen/Qwen3-Embedding-4B")
top_50 = reranker_medium.rank(query, top_500, top_k=50)

# Stage 3: Final rerank to 10 with large model
reranker_large = CrossEncoder("Qwen/Qwen3-Embedding-8B")
top_10 = reranker_large.rank(query, [r['text'] for r in top_50], top_k=10)
```

## Performance Optimization

### Batch Processing

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

# Process multiple queries efficiently
queries = [...]  # List of queries
candidates = [...]  # Shared candidate pool

# Create all pairs for batch scoring
all_pairs = []
query_indices = []
for i, query in enumerate(queries):
    for j, candidate in enumerate(candidates):
        all_pairs.append((query, candidate))
        query_indices.append(i)

# Batch score
scores = model.predict(all_pairs)

# Reshape to (num_queries, num_candidates)
scores_matrix = scores.reshape(len(queries), len(candidates))

# Get top-k for each query
top_k_indices = scores_matrix.argsort(axis=1)[:, -10:][::-1]
```

### GPU Optimization

```python
import torch
from sentence_transformers import CrossEncoder

# Load with mixed precision
model = CrossEncoder("Qwen/Qwen3-Embedding-4B", 
                     default_activation_function=torch.nn.Sigmoid())

# Move to GPU
model.to("cuda")

# Use FP16 for faster inference
model.model.half()

# Batch size tuning
scores = model.predict(pairs, batch_size=32)  # Adjust based on GPU memory
```

## Evaluation Metrics

```python
from sklearn.metrics import ndcg_score, precision_recall_curve
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Embedding-4B")

# Test dataset with ground truth
test_queries = [...]
test_candidates = [...]
test_relevance = [...]  # Binary relevance labels (1=relevant, 0=irrelevant)

# Get predictions
all_scores = []
all_labels = []
for query, candidates, relevance in zip(test_queries, test_candidates, test_relevance):
    scores = model.predict([(query, c) for c in candidates])
    all_scores.extend(scores.numpy())
    all_labels.extend(relevance)

# Calculate NDCG@10
ndcg = ndcg_score([test_relevance], [all_scores], k=10)
print(f"NDCG@10: {ndcg:.3f}")

# Precision-Recall curve
precision, recall, thresholds = precision_recall_curve(all_labels, all_scores)
```

## See Also

- [`references/06-semantic-search.md`](06-semantic-search.md) - Search system design
- [`references/07-rag-pipelines.md`](07-rag-pipelines.md) - RAG with reranking
- [`references/12-benchmarks.md`](12-benchmarks.md) - Performance benchmarks
