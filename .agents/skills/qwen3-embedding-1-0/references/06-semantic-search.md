# Semantic Search with Qwen3 Embedding

Complete guide to building semantic search systems using Qwen3 Embedding models.

## Basic Search System

### In-Memory Search

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SimpleSemanticSearch:
    def __init__(self, model_name="Qwen/Qwen3-Embedding-4B"):
        self.model = SentenceTransformer(model_name)
        self.corpus = []
        self.embeddings = None
    
    def index(self, documents):
        """Index documents for search"""
        self.corpus = documents
        self.embeddings = self.model.encode(
            documents, 
            normalize_embeddings=True,
            show_progress_bar=True
        )
    
    def search(self, query, top_k=5):
        """Search for relevant documents"""
        query_embedding = self.model.encode(query, normalize_embeddings=True)
        
        # Cosine similarity (dot product since normalized)
        similarities = self.embeddings @ query_embedding
        
        # Get top-k results
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'text': self.corpus[idx],
                'score': float(similarities[idx])
            })
        
        return results

# Usage
searcher = SimpleSemanticSearch()
searcher.index([
    "Python is a programming language.",
    "Java is used for enterprise applications.",
    "Machine learning is part of AI.",
    "The weather is sunny today."
])

results = searcher.search("What programming languages exist?")
for r in results:
    print(f"{r['score']:.3f} - {r['text']}")
```

## Production Search with Vector Database

### Using ChromaDB

```python
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection("documents")

# Load embedding model
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Add documents
documents = [
    "Python tutorial for beginners",
    "Advanced Java programming",
    "Machine learning with TensorFlow"
]
ids = [f"doc_{i}" for i in range(len(documents))]

# Generate embeddings
embeddings = model.encode(documents).tolist()

# Add to collection
collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=[{"source": "tutorial"} for _ in documents]
)

# Search
query = "programming languages for data science"
query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=2,
    include=['documents', 'distances']
)

for doc, dist in zip(results['documents'][0], results['distances'][0]):
    print(f"Distance: {dist:.3f} - {doc}")
```

### Using FAISS

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Prepare corpus
documents = [...]  # List of documents
embeddings = model.encode(documents)
dimension = embeddings.shape[1]

# Create FAISS index (inner product for cosine similarity)
index = faiss.IndexIPFlat(dimension, faiss.METRIC_INNER_PRODUCT)
index.add(embeddings.astype('float32'))

# Search function
def search(query, k=5):
    query_emb = model.encode([query], normalize_embeddings=True)
    distances, indices = index.search(query_emb.astype('float32'), k)
    
    results = []
    for i, dist in zip(indices[0], distances[0]):
        results.append({
            'text': documents[i],
            'score': float(dist)
        })
    
    return results

# Usage
results = search("machine learning algorithms")
for r in results:
    print(f"{r['score']:.3f} - {r['text'][:60]}...")
```

## Advanced Search Features

### Metadata Filtering

```python
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection("documents")

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Add documents with metadata
documents = [
    "Python basics tutorial",
    "Advanced Python patterns",
    "Java enterprise development",
    "Machine learning introduction"
]
metadatas = [
    {"level": "beginner", "language": "python"},
    {"level": "advanced", "language": "python"},
    {"level": "intermediate", "language": "java"},
    {"level": "beginner", "language": "ml"}
]

embeddings = model.encode(documents).tolist()
collection.add(
    ids=[f"doc_{i}" for i in range(len(documents))],
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas
)

# Filtered search
query = "programming for beginners"
query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=3,
    where={"level": "beginner"},  # Filter by metadata
    include=['documents', 'metadatas']
)

for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
    print(f"{meta} - {doc}")
```

### Hybrid Search (Dense + Sparse)

```python
from sentence_transformers import SentenceTransformer, SparseEncoder
import numpy as np

# Load dense and sparse models
dense_model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
sparse_model = SparseEncoder("naver/splade-cocondenser-ensembledistil")

class HybridSearch:
    def __init__(self):
        self.dense_model = dense_model
        self.sparse_model = sparse_model
        self.corpus = []
    
    def index(self, documents):
        self.corpus = documents
        
        # Dense embeddings
        self.dense_embeddings = self.dense_model.encode(
            documents, normalize_embeddings=True
        )
        
        # Sparse embeddings
        self.sparse_embeddings = self.sparse_model.encode(documents)
    
    def search(self, query, top_k=5, alpha=0.5):
        """
        Hybrid search with dense and sparse components.
        
        Args:
            alpha: Weight for dense vs sparse (0.5 = equal weight)
        """
        # Dense scoring
        query_dense = self.dense_model.encode(query, normalize_embeddings=True)
        dense_scores = self.dense_embeddings @ query_dense
        
        # Sparse scoring
        query_sparse = self.sparse_model.encode(query)
        sparse_scores = self.sparse_embeddings @ query_sparse.T
        
        # Normalize scores to [0, 1]
        dense_scores = (dense_scores - dense_scores.min()) / (dense_scores.max() - dense_scores.min() + 1e-8)
        sparse_scores = (sparse_scores - sparse_scores.min()) / (sparse_scores.max() - sparse_scores.min() + 1e-8)
        
        # Combine scores
        combined_scores = alpha * dense_scores + (1 - alpha) * sparse_scores
        
        # Get top-k
        top_indices = combined_scores.argsort()[-top_k:][::-1]
        
        return [
            {'text': self.corpus[i], 'score': float(combined_scores[i])}
            for i in top_indices
        ]

# Usage
searcher = HybridSearch()
searcher.index(corpus_documents)
results = searcher.search("Python machine learning", alpha=0.7)
```

### Query Expansion

```python
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Load query expansion model (T5-based)
expander_tokenizer = AutoTokenizer.from_pretrained("google/mt5-base")
expander_model = AutoModelForSeq2SeqLM.from_pretrained("google/mt5-base")

def expand_query(query, num_expansions=3):
    """Generate query variations for better recall"""
    inputs = expander_tokenizer(
        f"expand query: {query}", 
        return_tensors="pt", 
        max_length=64
    )
    
    outputs = expander_model.generate(
        **inputs,
        max_length=64,
        num_beams=5,
        num_return_sequences=num_expansions
    )
    
    expansions = [expander_tokenizer.decode(output, skip_special_tokens=True) 
                  for output in outputs]
    
    return [query] + expansions  # Include original query

# Use with search
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
corpus_embeddings = model.encode(corpus, normalize_embeddings=True)

def search_with_expansion(query, top_k=5):
    # Expand query
    expanded_queries = expand_query(query)
    
    # Encode all variations
    query_embeddings = model.encode(expanded_queries, normalize_embeddings=True)
    
    # Aggregate scores (max pooling across expansions)
    all_scores = corpus_embeddings @ query_embeddings.T  # (corpus_size, num_expansions)
    best_scores = all_scores.max(axis=1)  # Take best score from any expansion
    
    # Get top-k
    top_indices = best_scores.argsort()[-top_k:][::-1]
    
    return [
        {'text': corpus[i], 'score': float(best_scores[i])}
        for i in top_indices
    ]
```

## Search Evaluation

### Offline Evaluation

```python
from sentence_transformers import evaluation
import numpy as np

# Test dataset with queries and relevant documents
test_data = {
    'queries': [
        "Python installation",
        "Machine learning algorithms",
        "Web development frameworks"
    ],
    'relevant_docs': [
        [0, 3],  # Doc indices relevant to query 0
        [1, 5, 7],
        [2, 4]
    ]
}

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
corpus_embeddings = model.encode(corpus, normalize_embeddings=True)

def evaluate_search(model, test_data, corpus_embeddings):
    """Evaluate search quality using MRR and NDCG"""
    mrr_scores = []
    ndcg_scores = []
    
    for query, relevant in zip(test_data['queries'], test_data['relevant_docs']):
        # Search
        query_emb = model.encode(query, normalize_embeddings=True)
        similarities = corpus_embeddings @ query_emb
        ranked_indices = similarities.argsort()[::-1]
        
        # MRR (Mean Reciprocal Rank)
        for i, idx in enumerate(ranked_indices):
            if idx in relevant:
                mrr_scores.append(1.0 / (i + 1))
                break
        
        # NDCG@10
        relevance = [1.0 if i in relevant else 0.0 for i in ranked_indices[:10]]
        dcg = sum(relevance[i] / np.log2(i + 2) for i in range(min(10, len(relevant))))
        idcg = sum(1.0 / np.log2(i + 2) for i in range(len(relevant)))
        ndcg_scores.append(dcg / idcg if idcg > 0 else 0)
    
    return {
        'MRR': np.mean(mrr_scores),
        'NDCG@10': np.mean(ndcg_scores)
    }

metrics = evaluate_search(model, test_data, corpus_embeddings)
print(f"MRR: {metrics['MRR']:.3f}")
print(f"NDCG@10: {metrics['NDCG@10']:.3f}")
```

## See Also

- [`references/04-reranking.md`](04-reranking.md) - Reranking for improved accuracy
- [`references/07-rag-pipelines.md`](07-rag-pipelines.md) - Search in RAG systems
- [`references/10-optimization.md`](10-optimization.md) - Performance optimization
