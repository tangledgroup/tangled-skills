# Applications

## Semantic Search

### Dense Retrieval

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

corpus = [
    "Python is a programming language",
    "Java is another popular language",
    "The cat sat on the mat",
    "Machine learning is a subset of AI",
]
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

query = "What is Python?"
query_embedding = model.encode(query, convert_to_tensor=True)

hits = semantic_search(
    query_embedding,
    corpus_embeddings,
    top_k=3,
)
for hit in hits[0]:
    print(f"  {hit['corpus_id']}: {corpus[hit['corpus_id']]} (score: {hit['score']:.4f})")
```

### FAISS-Based Search

For large corpora, use FAISS integration with quantization support:

```python
from sentence_transformers.util import semantic_search_faiss
import numpy as np

corpus_embeddings = model.encode(corpus, convert_to_numpy=True)

hits, elapsed_time, faiss_index = semantic_search_faiss(
    query_embeddings=np.array([model.encode(query)]),
    corpus_embeddings=corpus_embeddings,
    top_k=10,
    corpus_precision="float32",  # or "int8", "ubinary"
    rescore=True,
)
```

### Sparse Retrieval

```python
from sentence_transformers import SparseEncoder

model = SparseEncoder("naver/splade-cocondenser-ensembledistil")
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
query_embedding = model.encode(query, convert_to_tensor=True)

hits = semantic_search(query_embedding, corpus_embeddings, top_k=3)
```

### Hybrid Retrieve-and-Rerank

The standard production pattern: dense retrieval for fast candidate selection, then cross-encoder reranking for accuracy.

```python
from sentence_transformers import SentenceTransformer, CrossEncoder

# Stage 1: Dense retrieval
retriever = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
corpus_embeddings = retriever.encode(corpus, convert_to_tensor=True)
query_embedding = retriever.encode(query, convert_to_tensor=True)

hits = semantic_search(query_embedding, corpus_embeddings, top_k=50)
top_candidates = [corpus[hit['corpus_id']] for hit in hits[0]]

# Stage 2: Cross-encoder reranking
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
ranks = reranker.rank(query, top_candidates, return_documents=True)

for rank in ranks[:5]:
    print(f"  {rank['score']:.4f}: {rank['text']}")
```

## Paraphrase Mining

Find pairs of semantically similar sentences in a large collection:

```python
from sentence_transformers.util import paraphrase_mining

sentences = [
    "The cat sat on the mat",
    "A cat was sitting on a mat",
    "The weather is nice today",
    "Today has beautiful weather",
    "I love programming",
    "Programming is my passion",
]

pairs = paraphrase_mining(
    model,
    sentences,
    top_k=5,
    score_function=cos_sim,
)
for score, id1, id2 in pairs[:5]:
    print(f"{score:.4f}: '{sentences[id1]}' ↔ '{sentences[id2]}'")
```

Parameters: `batch_size`, `query_chunk_size`, `corpus_chunk_size`, `max_pairs`, `top_k`.

## Clustering

```python
from sklearn.cluster import KMeans
import numpy as np

embeddings = model.encode(sentences, convert_to_numpy=True)
kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(embeddings)

for idx, label in enumerate(labels):
    print(f"  Cluster {label}: {sentences[idx]}")
```

## Community Detection

Find connected components based on similarity threshold:

```python
from sentence_transformers.util import community_detection

communities = community_detection(
    model,
    sentences,
    community_threshold=0.7,  # cosine similarity threshold
)
for idx, community in enumerate(communities):
    print(f"  Community {idx}: {[sentences[i] for i in community]}")
```

## Information Retrieval Evaluation

```python
from sentence_transformers.util import information_retrieval

results = information_retrieval(
    model.encode,
    queries={"q1": "What is Python?", "q2": "ML definition"},
    corpus_ids=corpus,
    relevant_docs={"q1": [0], "q2": [3]},
    corpus_chunk_size=50000,
    top_k=100,
)
# Returns precision, recall, NDCG metrics
```

## Embedding Quantization

Reduce memory footprint of embeddings while preserving similarity structure:

```python
from sentence_transformers import quantize_embeddings

embeddings = model.encode(sentences, convert_to_numpy=True)  # float32, shape (N, D)

# Int8 quantization
int8_embeddings = quantize_embeddings(embeddings, precision="int8")

# Binary quantization (1-bit per dimension)
binary_embeddings = quantize_embeddings(embeddings, precision="binary")

# Unsigned binary
ubinary_embeddings = quantize_embeddings(embeddings, precision="ubinary")

# uint8
uint8_embeddings = quantize_embeddings(embeddings, precision="uint8")
```

Supported precisions: `float32`, `int8`, `uint8`, `binary`, `ubinary`.

## Similarity Functions

```python
from sentence_transformers.util import (
    cos_sim,           # matrix cosine similarity
    pairwise_cos_sim,  # element-wise cosine
    dot_score,         # matrix dot product
    pairwise_dot_score,
    euclidean_sim,     # matrix euclidean similarity (negative distance)
    pairwise_euclidean_sim,
    manhattan_sim,     # matrix manhattan similarity
    pairwise_manhattan_sim,
    pytorch_cos_sim,   # alias for cos_sim
    pairwise_angle_sim,# angle-based similarity
)

from sentence_transformers import SimilarityFunction

# Enum for model.similarity_fn_name
SimilarityFunction.COSINE
SimilarityFunction.DOT_PRODUCT
SimilarityFunction.EUCLIDEAN
SimilarityFunction.MANHATTAN
```

## Tensor Utilities

```python
from sentence_transformers.util import (
    normalize_embeddings,   # L2-normalize a tensor
    truncate_embeddings,    # Matryoshka-style dimension truncation
    to_scipy_coo,           # Convert to scipy sparse COO format
    batch_to_device,        # Move batch dict to target device
    select_max_active_dims, # Select dimensions with highest activity
    compute_count_vector,   # Compute term frequency count vector
)
```

## Hard Negative Mining

```python
from sentence_transformers import mine_hard_negatives

hard_negs = mine_hard_negatives(
    model=model,
    corpus=corpus_texts,
    queries=query_texts,
    positives=positive_texts,
    top_k=10,
)
# Returns dict mapping query indices to lists of hard negative indices
```

## Logging

```python
from sentence_transformers import LoggingHandler

import logging
logger = logging.getLogger(__name__)
handler = LoggingHandler()
logger.addHandler(handler)
```

## Environment Utilities

```python
from sentence_transformers.util import (
    get_device_name,           # Returns "cuda", "mps", "npu", or "cpu"
    is_accelerate_available,   # Check if accelerate is installed
    is_datasets_available,     # Check if datasets is installed
    is_training_available,     # Check if training dependencies are available
    check_package_availability,# Generic package availability check
)
```

## Distributed Utilities

For multi-GPU training with contrastive losses:

```python
from sentence_transformers.util import all_gather, all_gather_with_grad

# Gather embeddings from all GPUs (no gradient)
gathered = all_gather(embeddings)

# Gather with gradient support
gathered_grad = all_gather_with_grad(embeddings)
```

## Translated Sentence Mining

Mine parallel sentences across languages using embedding similarity:

```python
from sentence_transformers import SentenceTransformer

# Load multilingual model
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Encode sentences in different languages
en_sentences = model.encode(["Hello world"], convert_to_tensor=True)
de_sentences = model.encode(["Hallo Welt"], convert_to_tensor=True)

# Cross-lingual similarity
similarity = model.similarity(en_sentences, de_sentences)
```

## Model Hub Organization

Pre-trained models are organized under the `sentence-transformers` organization on Hugging Face Hub. The constant `__MODEL_HUB_ORGANIZATION__ = "sentence-transformers"` is available for programmatic access.

Over 15,000 pre-trained models are available at https://huggingface.co/models?library=sentence-transformers, covering 100+ languages and various domain-specific use cases.
