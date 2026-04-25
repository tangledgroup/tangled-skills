# Complete Examples & Advanced Patterns

## Example 1: Full RAG Pipeline with Qwen3 Embedding

```python
"""
Complete RAG (Retrieval-Augmented Generation) pipeline using Qwen3 Embedding.
Combines embedding generation, vector search, and reranking for high-quality retrieval.
"""

import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Qwen3RAGPipeline:
    """Two-stage RAG: dense retrieval + optional reranking."""

    def __init__(
        self,
        embedding_model="Qwen/Qwen3-Embedding-0.6B",
        reranker_model=None,
        dimension=256,
        top_k_dense=100,
        top_k_final=5
    ):
        # Dense embedding model
        self.embedder = SentenceTransformer(
            embedding_model,
            model_kwargs={"attn_implementation": "flash_attention_2", "device_map": "auto"},
            tokenizer_kwargs={"padding_side": "left"}
        )
        self.dimension = dimension
        self.top_k_dense = top_k_dense
        self.top_k_final = top_k_final

        # Optional reranker (cross-encoder)
        if reranker_model:
            from sentence_transformers import CrossEncoder
            self.reranker = CrossEncoder(reranker_model)
            self.has_reranker = True
        else:
            self.reranker = None
            self.has_reranker = False

        self.documents = []
        self.embeddings = None

    def index_documents(self, documents, batch_size=64):
        """Index a collection of documents."""
        self.documents = list(documents)
        self.embeddings = self.embedder.encode(
            documents,
            batch_size=batch_size,
            dimension=self.dimension,
            show_progress_bar=True
        )

    def search(self, query, task_instruction=None, prompt_name="query"):
        """
        Search with optional two-stage retrieval.

        Args:
            query: Search query string
            task_instruction: Optional task description for instruction-aware embedding
            prompt_name: Built-in prompt name (e.g., "query")

        Returns:
            List of dicts with score, index, and text for top results
        """
        # Stage 1: Dense retrieval
        if task_instruction:
            query_text = f"Instruct: {task_instruction}\nQuery:{query}"
        else:
            query_text = query

        query_emb = self.embedder.encode([query_text], prompt_name=prompt_name)
        scores = cosine_similarity(query_emb, self.embeddings)[0]

        # Get top-k candidates from dense retrieval
        top_k_dense_indices = np.argsort(scores)[::-1][:self.top_k_dense]
        top_k_dense_scores = scores[top_k_dense_indices]
        top_k_docs = [self.documents[i] for i in top_k_dense_indices]

        if self.has_reranker and len(top_k_docs) > 1:
            # Stage 2: Reranking with cross-encoder
            pairs = [[query_text, doc] for doc in top_k_docs]
            rerank_scores = self.reranker.predict(pairs)

            # Combine scores (weighted average)
            combined_scores = 0.5 * np.tanh(top_k_dense_scores / 10) + 0.5 * rerank_scores
            final_indices = np.argsort(combined_scores)[::-1][:self.top_k_final]

            results = []
            for idx in final_indices:
                original_idx = top_k_dense_indices[idx]
                results.append({
                    "rank": len(results) + 1,
                    "document_index": int(original_idx),
                    "dense_score": float(top_k_dense_scores[idx]),
                    "rerank_score": float(rerank_scores[idx]),
                    "combined_score": float(combined_scores[idx]),
                    "text": top_k_docs[idx]
                })
        else:
            # No reranker, just return dense retrieval results
            final_indices = np.argsort(top_k_dense_scores)[::-1][:self.top_k_final]
            results = []
            for rank, idx in enumerate(final_indices):
                original_idx = top_k_dense_indices[idx]
                results.append({
                    "rank": rank + 1,
                    "document_index": int(original_idx),
                    "score": float(scores[original_idx]),
                    "text": self.documents[original_idx]
                })

        return results


# Usage example
if __name__ == "__main__":
    # Sample document corpus
    documents = [
        "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability.",
        "The Python runtime environment facilitates the execution of Python programs without prior compilation.",
        "Java is a class-based, object-oriented programming language designed for portability.",
        "TypeScript extends JavaScript with static typing, enabling better tooling and error detection.",
        "Rust is a systems programming language focused on safety, speed, and concurrency.",
    ]

    pipeline = Qwen3RAGPipeline(
        embedding_model="Qwen/Qwen3-Embedding-0.6B",
        dimension=256,
        top_k_dense=100,
        top_k_final=3
    )
    pipeline.index_documents(documents)

    results = pipeline.search(
        query="What is Python programming language?",
        task_instruction="Find documents describing a programming language.",
        prompt_name="query"
    )

    for r in results:
        print(f"[{r['rank']}] Score: {r.get('score', r.get('combined_score', 0)):.4f}")
        print(f"    {r['text'][:80]}...")
```

## Example 2: Multilingual Semantic Search

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load multilingual model
model = SentenceTransformer("Qwen/Qwen3-Embedding-8B")

# Documents in different languages
documents = [
    ("en", "The Eiffel Tower is located in Paris, France."),
    ("ja", "エッフェル塔はフランスのパリにあります。"),
    ("zh", "埃菲尔铁塔位于法国巴黎。"),
    ("es", "La Torre Eiffel se encuentra en París, Francia."),
    ("de", "Der Eiffelturm befindet sich in Paris, Frankreich."),
]

# Query in English — should retrieve all translations
query = "Where is the Eiffel Tower located?"

# Encode with instruction
query_emb = model.encode([f"Instruct: Find the location of landmarks.\nQuery:{query}"])
doc_embs = model.encode([doc for _, doc in documents])

# Compute similarity
from sklearn.metrics.pairwise import cosine_similarity
scores = cosine_similarity(query_emb, doc_embs)[0]

for (lang, text), score in zip(documents, scores):
    print(f"[{lang.upper():>2}] {score:.4f} | {text[:60]}")
```

## Example 3: Code Retrieval System

```python
from sentence_transformers import SentenceTransformer
import re

class CodeSearchEngine:
    """Semantic code search using Qwen3 Embedding."""

    def __init__(self, model_name="Qwen/Qwen3-Embedding-4B"):
        self.model = SentenceTransformer(
            model_name,
            model_kwargs={"attn_implementation": "flash_attention_2", "device_map": "auto"},
            tokenizer_kwargs={"padding_side": "left"}
        )
        self.code_snippets = []
        self.metadata = []

    def index_code(self, code_list, metadata_list=None):
        """Index code snippets."""
        self.code_snippets = list(code_list)
        self.metadata = metadata_list or [{} for _ in code_list]
        # Code benefits from "code" prompt if available
        self.embeddings = self.model.encode(
            code_list,
            batch_size=32,
            dimension=512  # Reduce for code embeddings
        )

    def search(self, natural_language_query, language_filter=None, top_k=5):
        """Search code using natural language description."""
        query_emb = self.model.encode(
            [f"Instruct: Find code that implements the described functionality.\nQuery:{natural_language_query}"]
        )

        from sklearn.metrics.pairwise import cosine_similarity
        scores = cosine_similarity(query_emb, self.embeddings)[0]

        if language_filter:
            # Apply language filter (metadata must have 'language' key)
            filtered_indices = [
                i for i in range(len(self.metadata))
                if self.metadata[i].get("language") == language_filter
            ]
            scores = np.array([scores[i] if i in filtered_indices else -1.0 for i in range(len(scores))])

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "score": float(scores[idx]),
                    "code": self.code_snippets[idx],
                    **self.metadata[idx]
                })
        return results


# Usage
engine = CodeSearchEngine()
code_samples = [
    "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "async def fetch_data(url):\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as resp:\n            return await resp.json()",
    "SELECT u.name, COUNT(o.id) as order_count FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.name HAVING order_count > 5",
]
engine.index_code(code_samples)

results = engine.search("function to calculate fibonacci numbers recursively")
for r in results:
    print(f"Score: {r['score']:.4f}")
    print(r["code"][:80])
```

## Example 4: Clustering with Qwen3 Embeddings

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

# Sample news articles (one per line)
articles = [
    "Apple released new iPhone with improved camera system",
    "Stock markets rally amid positive economic data",
    "Scientists discover new species of deep-sea fish",
    "Tech company announces layoffs affecting thousands",
    "New study shows benefits of Mediterranean diet",
    "SpaceX launches another batch of Starlink satellites",
    "Central bank raises interest rates by 0.25%",
    "Breakthrough in quantum computing achieved at MIT",
    "Housing prices continue to rise in major cities",
    "AI model surpasses human performance on medical diagnosis",
]

embeddings = model.encode(articles, batch_size=8)

# Find optimal number of clusters
best_score = -1
best_k = 2
for k in range(2, min(len(articles), 6)):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(embeddings)
    score = silhouette_score(embeddings, labels)
    if score > best_score:
        best_score = score
        best_k = k

print(f"Optimal clusters: {best_k} (silhouette: {best_score:.4f})")

# Run final clustering
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
labels = kmeans.fit_predict(embeddings)

for i, (article, label) in enumerate(zip(articles, labels)):
    print(f"[Cluster {label}] {article[:60]}...")
```

## Example 5: Embedding Similarity Dashboard Data Export

```python
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("Qwen/Qwen3-Embedding-8B")

# Your document corpus
documents = [
    "Document text 1...",
    "Document text 2...",
    "Document text 3...",
]

embeddings = model.encode(documents, batch_size=32)

# Export for vector database ingestion
export_data = {
    "model": "Qwen/Qwen3-Embedding-8B",
    "dimension": embeddings.shape[1],
    "count": len(documents),
    "documents": [
        {"id": i, "text": doc, "embedding": emb.tolist()}
        for i, (doc, emb) in enumerate(zip(documents, embeddings))
    ]
}

with open("embeddings.json", "w") as f:
    json.dump(export_data, f)

# Similarity matrix for analysis
sim_matrix = cosine_similarity(embeddings)
np.fill_diagonal(sim_matrix, 0)  # Zero out self-similarity

# Find most similar pairs
pairs = []
for i in range(len(documents)):
    for j in range(i + 1, len(documents)):
        pairs.append((i, j, sim_matrix[i][j]))

pairs.sort(key=lambda x: x[2], reverse=True)
print("Top 5 most similar document pairs:")
for i, j, score in pairs[:5]:
    print(f"  Docs {i} & {j}: {score:.4f}")
```

## References

- Hugging Face (0.6B): https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Hugging Face (4B): https://huggingface.co/Qwen/Qwen3-Embedding-4B
- Hugging Face (8B): https://huggingface.co/Qwen/Qwen3-Embedding-8B
- Sentence Transformers: https://sbert.net/
- Technical Report: https://arxiv.org/abs/2506.05176
