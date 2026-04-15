# Sparse Encoder Usage

Comprehensive guide to using `SparseEncoder` class for sparse embeddings and hybrid search.

## Understanding Sparse Embeddings

### Dense vs Sparse Embeddings

| Aspect | Dense Embeddings | Sparse Embeddings |
|--------|------------------|-------------------|
| **Dimensions** | Fixed (e.g., 384, 768) | Vocabulary size (e.g., 30,522) |
| **Sparsity** | All values non-zero | 95-99% zeros |
| **Interpretability** | Black box | Token-level weights |
| **Similar to** | Neural embeddings | BM25/TF-IDF |
| **Storage** | Dense vectors | Sparse matrices |
| **Speed** | Fast with ANN | Very fast with inverted index |

### When to Use Sparse Embeddings

- **Hybrid search**: Combine with dense embeddings for best of both worlds
- **Keyword matching**: Capture exact term matches like BM25
- **Interpretability**: Understand which terms contribute to similarity
- **Low-resource deployment**: No vector database needed (use inverted index)
- **Multilingual tasks**: Better cross-lingual keyword matching

## Basic Usage

### Load and Encode

```python
from sentence_transformers import SparseEncoder

# Load pretrained sparse encoder
model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Encode texts
sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
]

# Generate sparse embeddings
embeddings = model.encode(sentences)
print(embeddings.shape)  # [3, 30522] - vocabulary size

# Check sparsity statistics
stats = SparseEncoder.sparsity(embeddings)
print(f"Sparsity ratio: {stats['sparsity_ratio']:.2%}")  # ~99.84%
print(f"Average non-zeros per embedding: {stats['avg_nnz']:.1f}")
```

### Similarity Computation

```python
from sentence_transformers import SparseEncoder, util

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Encode query and corpus
query = "What are the symptoms of flu?"
corpus = [
    "Flu symptoms include fever, cough, and fatigue.",
    "The weather is nice today.",
    "Common cold causes runny nose and sneezing.",
]

query_embedding = model.encode(query)
corpus_embeddings = model.encode(corpus)

# Compute similarities (dot product for sparse)
similarities = util.dot_score(query_embedding, corpus_embeddings)
print(similarities)  # tensor([[35.629, 0.154, 8.234]])

# Get top results
top_indices = similarities.argsort(descending=True)
for idx in top_indices[0]:
    print(f"{similarities[0, idx]:.2f} - {corpus[idx]}")
```

## Sparse Embedding Formats

### PyTorch Sparse Tensor

```python
import torch
from sentence_transformers import SparseEncoder

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")
embeddings = model.encode(["Example sentence"], convert_to_tensor=True)

# Convert to sparse COO format
sparse_embedding = embeddings.sparse()
print(sparse_embedding.layout)  # torch.sparse_coo

# Access indices and values
indices = sparse_embedding.indices()  # Shape: [2, nnz]
values = sparse_embedding.values()    # Shape: [nnz]
```

### SciPy Sparse Matrix

```python
import scipy.sparse as sp
from sentence_transformers import SparseEncoder

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")
embeddings = model.encode(["Sentence 1", "Sentence 2"], convert_to_numpy=True)

# Convert to CSR format (efficient for row operations)
sparse_matrix = sp.csr_matrix(embeddings)
print(sparse_matrix.shape)  # (2, 30522)
print(f"NNZ: {sparse_matrix.nnz}")  # Number of non-zero elements

# Efficient similarity computation
query_vec = sparse_matrix[0]
similarities = query_vec @ sparse_matrix.T
```

### Dict Format (Most Memory Efficient)

```python
from sentence_transformers import SparseEncoder

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Encode and convert to dict format
embeddings = model.encode(["Machine learning is great"])

# Get sparse representation as dict: {token_id: weight}
sparse_dict = {}
for batch_idx, emb in enumerate(embeddings):
    if hasattr(emb, 'cpu'):
        emb = emb.cpu()
    nonzero_indices = emb.nonzero(as_tuple=True)[0]
    sparse_dict[batch_idx] = {
        int(idx): float(emb[idx]) 
        for idx in nonzero_indices
    }

print(sparse_dict[0])  # {1234: 2.34, 5678: 1.89, ...}
```

## Hybrid Search

### Combine Dense and Sparse

```python
from sentence_transformers import SentenceTransformer, SparseEncoder
import numpy as np

# Load both models
dense_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
sparse_model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Prepare corpus
corpus = [
    "Machine learning uses neural networks.",
    "The quick brown fox jumps over the lazy dog.",
    "Deep learning is a subset of machine learning.",
]

# Encode with both models
dense_corpus = dense_model.encode(corpus, normalize_embeddings=True)
sparse_corpus = sparse_model.encode(corpus, convert_to_numpy=True)

# Normalize sparse embeddings
from sklearn.preprocessing import normalize
sparse_corpus_normalized = normalize(sparse_corpus, norm='l2')

def hybrid_search(query, alpha=0.5):
    """
    Hybrid search with interpolation
    
    Args:
        query: Query text
        alpha: Weight for dense (0.5 = equal weight)
    """
    # Encode query
    dense_query = dense_model.encode(query, normalize_embeddings=True)
    sparse_query = sparse_model.encode(query, convert_to_numpy=True)
    sparse_query_normalized = normalize(sparse_query, norm='l2')[0]
    
    # Compute similarities
    dense_sim = dense_corpus @ dense_query
    sparse_sim = sparse_corpus_normalized @ sparse_query_normalized
    
    # Combine with interpolation
    hybrid_sim = alpha * dense_sim + (1 - alpha) * sparse_sim
    
    return hybrid_sim

# Search
query = "neural networks for machine learning"
scores = hybrid_search(query, alpha=0.5)

for idx, score in enumerate(scores):
    print(f"{score:.3f} - {corpus[idx]}")
```

### Reciprocal Rank Fusion

```python
def reciprocal_rank_fusion(query, k=60):
    """
    Combine dense and sparse using reciprocal rank fusion
    
    Args:
        query: Query text
        k: RRF parameter (typically 60)
    """
    # Get rankings from both methods
    dense_query = dense_model.encode(query, normalize_embeddings=True)
    dense_sim = dense_corpus @ dense_query
    dense_ranks = dense_sim.argsort()[::-1]
    
    sparse_query = sparse_model.encode(query, convert_to_numpy=True)
    sparse_query_normalized = normalize(sparse_query, norm='l2')[0]
    sparse_sim = sparse_corpus_normalized @ sparse_query_normalized
    sparse_ranks = sparse_sim.argsort()[::-1]
    
    # RRF scoring
    rrf_scores = np.zeros(len(corpus))
    for rank, idx in enumerate(dense_ranks):
        rrf_scores[idx] += 1 / (k + rank)
    for rank, idx in enumerate(sparse_ranks):
        rrf_scores[idx] += 1 / (k + rank)
    
    return rrf_scores

# Search with RRF
query = "machine learning algorithms"
rrf_scores = reciprocal_rank_fusion(query)

for idx in rrf_scores.argsort()[::-1][:3]:
    print(f"{corpus[idx]}")
```

## SPLADE Models

### SPLADE Variants

SPLADE (Sparse Lexical and Expansion Encoder) comes in several variants:

```python
from sentence_transformers import SparseEncoder

# Original SPLADE - learns to expand query with related terms
model = SparseEncoder("naver/splade-distilbert-base")

# SPLADE Co-condenser - better expansion with co-attention
model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Multilingual SPLADE
model = SparseEncoder("BeIR/multilingual-splade-base")
```

### Understanding SPLADE Expansion

```python
import torch
from sentence_transformers import SparseEncoder

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Encode a query
query = "best laptop for programming"
embedding = model.encode(query)

# Get top weighted tokens
tokenizer = model.auto_model.tokenizer
nonzero = embedding[0].nonzero(as_tuple=True)[0]
top_10_indices = nonzero[embedding[0][nonzero].argsort(descending=True)[:10]]

print("Top expansion terms:")
for idx in top_10_indices:
    token = tokenizer.decode(idx)
    weight = embedding[0, idx].item()
    print(f"  {token}: {weight:.3f}")

# Output might include: laptop, programming, computer, coding, developer, etc.
```

## Integration with Search Engines

### Elasticsearch Integration

```python
from elasticsearch import Elasticsearch
from sentence_transformers import SparseEncoder
import numpy as np

# Initialize
es = Elasticsearch(["http://localhost:9200"])
model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Index documents
def index_document(doc_id, text):
    # Encode to sparse format
    embedding = model.encode([text])[0]
    
    # Convert to sparse format for Elasticsearch
    sparse_vec = {}
    for idx, val in enumerate(embedding):
        if val != 0:
            sparse_vec[str(idx)] = val.item()
    
    # Index with sparse vector
    es.index(
        index="documents",
        id=doc_id,
        body={
            "text": text,
            "sparse_embedding": {"type": "sparse_vector", "value": sparse_vec}
        }
    )

# Search with k-NN
def search(query, top_k=10):
    query_embedding = model.encode([query])[0]
    
    # Convert to sparse format
    sparse_vec = {}
    for idx, val in enumerate(query_embedding):
        if val != 0:
            sparse_vec[str(idx)] = val.item()
    
    # k-NN search
    query_body = {
        "knn": {
            "field": "sparse_embedding",
            "query_vector": sparse_vec,
            "k": top_k,
            "num_candidates": top_k
        }
    }
    
    results = es.search(index="documents", body=query_body)
    return [hit["_source"]["text"] for hit in results["hits"]["hits"]]
```

### FAISS Sparse Index

```python
import faiss
from sentence_transformers import SparseEncoder
import scipy.sparse as sp

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

# Encode corpus
corpus = ["Document 1", "Document 2", ...]
embeddings = model.encode(corpus, convert_to_numpy=True)

# Convert to sparse matrix
sparse_matrix = sp.csr_matrix(embeddings)

# Create FAISS sparse index (FAISS >= 1.7)
index = faiss.index_factory(sparse_matrix.shape[1], "SparseFlat")

# Add to index
index.add(sparse_matrix)

# Search
query_embedding = model.encode(["Query text"])[0]
query_sparse = sp.csr_matrix(query_embedding)

D, I = index.search(query_sparse, k=10)  # D: distances, I: indices
```

## Performance Tips

1. **Use CSR format**: SciPy CSR matrices are efficient for sparse operations
2. **Leverage inverted indexes**: Sparse embeddings work with traditional search engines
3. **Combine with dense**: Hybrid search often outperforms either alone
4. **Cache token IDs**: Pre-compute vocabulary mappings for faster lookup
5. **Batch encoding**: Use batch_size parameter for large datasets

## Common Models

| Model | Vocabulary Size | Sparsity | Best For |
|-------|-----------------|----------|----------|
| `naver/splade-distilbert-base` | 30,522 | 99%+ | General sparse embeddings |
| `naver/splade-cocondenser-ensembledistil` | 30,522 | 99%+ | Better query expansion |
| `BeIR/multilingual-splade-base` | 97,181 | 99%+ | Multilingual tasks |
| `unicamp-dl/unsplade-portuguese` | 30,522 | 99%+ | Portuguese documents |

## Troubleshooting

### Issue: High memory usage

**Solution**: Use sparse matrix formats (CSR/COO) instead of dense numpy arrays

### Issue: Slow similarity computation

**Solution**: Use inverted index or search engine with native sparse support

### Issue: Sparse embeddings too dense

**Solution**: Apply thresholding to keep only top-k terms per embedding
