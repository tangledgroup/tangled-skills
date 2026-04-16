# Multimodal RAG with Qwen3-VL

This guide covers building end-to-end Retrieval-Augmented Generation (RAG) pipelines using Qwen3-VL-Embedding, Qwen3-VL-Reranker, and Qwen3-VL for generation.

## Architecture Overview

A complete multimodal RAG system consists of three stages:

```
1. INDEXING: Documents → Qwen3-VL-Embedding → Vector Database
2. RETRIEVAL: Query → Embedding → Vector Search → Top-K Candidates
3. RE-RANKING: (Query, Candidates) → Qwen3-VL-Reranker → Reordered Results
4. GENERATION: (Query, Retrieved Context) → Qwen3-VL → Answer
```

## Indexing Pipeline

### Basic Document Indexing

```python
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder
import faiss
import numpy as np

# Initialize embedder
embedder = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)

# Sample documents with mixed modalities
documents = [
    {
        "id": "doc_1",
        "text": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris.",
        "image": "eiffel_tower.jpg",
        "metadata": {"source": "wikipedia", "language": "en"}
    },
    {
        "id": "doc_2", 
        "text": "The Great Wall of China is a series of fortifications made of stone, brick, wood, and other materials.",
        "image": "great_wall.jpg",
        "metadata": {"source": "wikipedia", "language": "en"}
    },
    # ... more documents
]

# Generate embeddings
doc_inputs = [
    {
        "text": doc["text"],
        "image": doc.get("image"),
        "instruction": "Represent the document for retrieval."
    }
    for doc in documents
]

embeddings = embedder.process(doc_inputs)

# Normalize for cosine similarity
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
index.add(embeddings)

# Store document mapping
doc_mapping = {i: doc for i, doc in enumerate(documents)}

print(f"Indexed {len(documents)} documents with {dimension}-dimensional embeddings")
```

### Batch Indexing with Progress Tracking

```python
from tqdm import tqdm
import json
from pathlib import Path

def index_documents_batch(
    embedder, 
    documents, 
    batch_size=32, 
    output_dir="./index",
    instruction="Represent the document for retrieval."
):
    """Index documents in batches with progress tracking."""
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    all_embeddings = []
    doc_ids = []
    doc_metadata = []
    
    # Process in batches
    for i in tqdm(range(0, len(documents), batch_size), desc="Generating embeddings"):
        batch = documents[i:i+batch_size]
        
        # Prepare inputs
        inputs = [
            {
                "text": doc.get("text", ""),
                "image": doc.get("image"),
                "video": doc.get("video"),
                "instruction": instruction
            }
            for doc in batch
        ]
        
        # Generate embeddings
        batch_embeddings = embedder.process(inputs)
        all_embeddings.extend(batch_embeddings)
        
        # Track metadata
        doc_ids.extend([doc["id"] for doc in batch])
        doc_metadata.extend([doc.get("metadata", {}) for doc in batch])
    
    # Convert to numpy and normalize
    embeddings = np.array(all_embeddings)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Create and save FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    faiss.write_index(index, Path(output_dir) / "index.faiss")
    
    # Save metadata
    metadata = {
        "doc_ids": doc_ids,
        "metadata": doc_metadata,
        "dimension": dimension,
        "model": "Qwen3-VL-Embedding-2B"
    }
    
    with open(Path(output_dir) / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Indexed {len(documents)} documents to {output_dir}")
    return index, metadata

# Usage
index, metadata = index_documents_batch(
    embedder, 
    documents, 
    batch_size=32,
    output_dir="./knowledge_base"
)
```

### Incremental Indexing

```python
class IncrementalIndex:
    """Support adding documents to existing index."""
    
    def __init__(self, embedder, index_path="./index"):
        self.embedder = embedder
        self.index_path = Path(index_path)
        self.metadata = self._load_metadata()
        self.index = self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index or create new one."""
        index_file = self.index_path / "index.faiss"
        if index_file.exists():
            return faiss.read_index(str(index_file))
        return None
    
    def _load_metadata(self):
        """Load metadata or initialize empty."""
        metadata_file = self.index_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return {"doc_ids": [], "metadata": [], "dimension": None}
    
    def add_documents(self, documents, batch_size=32):
        """Add new documents to index."""
        if not documents:
            return
        
        # Generate embeddings
        inputs = [
            {
                "text": doc.get("text", ""),
                "image": doc.get("image"),
                "instruction": "Represent the document for retrieval."
            }
            for doc in documents
        ]
        
        embeddings = self.embedder.process(inputs)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Initialize index if needed
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.metadata["dimension"] = dimension
            start_id = 0
        else:
            start_id = len(self.metadata["doc_ids"])
        
        # Add to index
        self.index.add(embeddings)
        
        # Update metadata
        self.metadata["doc_ids"].extend([doc["id"] for doc in documents])
        self.metadata["metadata"].extend([doc.get("metadata", {}) for doc in documents])
        
        # Save
        self._save()
        
        print(f"Added {len(documents)} documents (total: {len(self.metadata['doc_ids'])})")
    
    def _save(self):
        """Save index and metadata."""
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        
        with open(self.index_path / "metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def search(self, query, k=10):
        """Search for similar documents."""
        query_embedding = self.embedder.process([query])[0]
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        query_embedding = query_embedding.reshape(1, -1)
        
        D, I = self.index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < len(self.metadata["doc_ids"]):
                results.append({
                    "id": self.metadata["doc_ids"][idx],
                    "score": float(score),
                    "metadata": self.metadata["metadata"][idx]
                })
        
        return results

# Usage
incremental_index = IncrementalIndex(embedder)

# Add initial documents
incremental_index.add_documents(initial_docs)

# Later, add more documents
incremental_index.add_documents(new_docs)

# Search
results = incremental_index.search({"text": "Paris landmarks"}, k=5)
```

## Retrieval Pipeline

### Basic Retrieval

```python
def retrieve_documents(index, embedder, query, k=10):
    """Retrieve top-k similar documents."""
    
    # Generate query embedding
    query_embedding = embedder.process([{
        "text": query.get("text", ""),
        "image": query.get("image"),
        "instruction": "Represent the user's input."
    }])[0]
    
    # Normalize
    query_embedding = query_embedding / np.linalg.norm(query_embedding)
    query_embedding = query_embedding.reshape(1, -1)
    
    # Search index
    D, I = index.search(query_embedding, k)
    
    return {
        "scores": D[0].tolist(),
        "indices": I[0].tolist()
    }

# Usage
results = retrieve_documents(index, embedder, {"text": "Famous Paris landmarks"}, k=10)
print(f"Top 3 results: {list(zip(results['indices'][:3], results['scores'][:3]))}")
```

### Hybrid Retrieval (Dense + Sparse)

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    """Combine dense (embedding) and sparse (BM25) retrieval."""
    
    def __init__(self, index, embedder, documents, alpha=0.7):
        """
        Args:
            index: FAISS index for dense retrieval
            embedder: Qwen3VLEmbedder model
            documents: List of document dicts with 'text' field
            alpha: Weight for dense retrieval (1-alpha for sparse)
        """
        self.index = index
        self.embedder = embedder
        self.alpha = alpha
        
        # Initialize BM25 for sparse retrieval
        tokenized_docs = [doc["text"].lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        self.documents = documents
    
    def retrieve(self, query, k=10):
        """Perform hybrid retrieval."""
        # Dense retrieval
        dense_scores = self._dense_retrieve(query, k * 2)  # Retrieve more for fusion
        
        # Sparse retrieval
        sparse_scores = self._sparse_retrieve(query, k * 2)
        
        # Normalize scores to [0, 1]
        dense_scores = self._normalize_scores(dense_scores)
        sparse_scores = self._normalize_scores(sparse_scores)
        
        # Combine scores
        combined_scores = self.alpha * dense_scores + (1 - self.alpha) * sparse_scores
        
        # Get top-k
        top_indices = np.argsort(combined_scores)[::-1][:k]
        
        return [
            {
                "index": int(idx),
                "score": float(combined_scores[idx]),
                "dense_score": float(dense_scores[idx]),
                "sparse_score": float(sparse_scores[idx])
            }
            for idx in top_indices
        ]
    
    def _dense_retrieve(self, query, k):
        """Dense retrieval using embeddings."""
        query_embedding = self.embedder.process([{
            "text": query.get("text", ""),
            "instruction": "Represent the user's input."
        }])[0]
        
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        query_embedding = query_embedding.reshape(1, -1)
        
        D, I = self.index.search(query_embedding, k)
        
        scores = np.zeros(len(self.documents))
        scores[I[0]] = D[0]
        
        return scores
    
    def _sparse_retrieve(self, query, k):
        """Sparse retrieval using BM25."""
        query_tokens = query.get("text", "").lower().split()
        
        if not query_tokens:
            return np.zeros(len(self.documents))
        
        scores = self.bm25.get_scores(query_tokens)
        return scores
    
    def _normalize_scores(self, scores):
        """Min-max normalization to [0, 1]."""
        min_score, max_score = scores.min(), scores.max()
        if max_score - min_score == 0:
            return np.zeros_like(scores)
        return (scores - min_score) / (max_score - min_score)

# Usage
hybrid_retriever = HybridRetriever(index, embedder, documents, alpha=0.7)
results = hybrid_retriever.retrieve({"text": "Eiffel Tower architecture"}, k=10)
```

## Re-Ranking Pipeline

### Using Qwen3-VL-Reranker

```python
from src.models.qwen3_vl_reranker import Qwen3VLReranker

# Initialize reranker
reranker = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)

def rerank_results(query, candidate_docs, top_k=5):
    """Re-rank retrieved documents using cross-attention reranker."""
    
    # Prepare inputs for reranker
    inputs = {
        "instruction": "Retrieve images or text relevant to the user's query.",
        "query": {
            "text": query.get("text", ""),
            "image": query.get("image")
        },
        "documents": [
            {
                "text": doc.get("text", ""),
                "image": doc.get("image")
            }
            for doc in candidate_docs
        ],
        "fps": 1.0,
        "max_frames": 64
    }
    
    # Get relevance scores
    scores = reranker.process(inputs)
    
    # Sort by score and return top-k
    scored_docs = list(zip(candidate_docs, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    return [
        {"document": doc, "score": float(score)}
        for doc, score in scored_docs[:top_k]
    ]

# Full retrieval + reranking pipeline
def retrieve_and_rerank(query, retriever, reranker, recall_k=50, rerank_k=10):
    """Two-stage retrieval: recall then re-rank."""
    
    # Stage 1: Recall top-k candidates
    recall_results = retriever.retrieve(query, k=recall_k)
    candidate_docs = [documents[r["index"]] for r in recall_results]
    
    # Stage 2: Re-rank with cross-attention
    if len(candidate_docs) > 0:
        ranked_results = rerank_results(query, candidate_docs, top_k=rerank_k)
        return ranked_results
    else:
        return []

# Usage
final_results = retrieve_and_rerank(
    query={"text": "Describe the architectural style of the Eiffel Tower"},
    retriever=hybrid_retriever,
    reranker=reranker,
    recall_k=50,
    rerank_k=10
)

print(f"Top result score: {final_results[0]['score']:.4f}")
```

## Generation Pipeline

### Using Qwen3-VL for Answer Generation

```python
from transformers import AutoModelForImageTextToText, AutoProcessor

# Load Qwen3-VL for generation
model_name = "Qwen/Qwen3-VL-2B-Instruct"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

def generate_answer(query, retrieved_context, max_tokens=512):
    """Generate answer using retrieved context."""
    
    # Build context from retrieved documents
    context_text = "\n\n".join([
        f"Document {i+1}:\n{doc['document'].get('text', '')}"
        for i, doc in enumerate(retrieved_context[:5])  # Use top 5
    ])
    
    # Create prompt
    prompt = f"""You are a helpful assistant. Use the following context to answer the question. If the answer cannot be found in the context, say so.

Context:
{context_text}

Question: {query.get('text', '')}

Answer:"""
    
    # Prepare inputs
    messages = [
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    ]
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # Add images if present in context
    inputs = processor(
        text=[text],
        images=None,  # Add images from context if needed
        return_tensors="pt"
    ).to(model.device)
    
    # Generate answer
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
    
    response = processor.decode(outputs[0], skip_special_tokens=True)
    return response

# Full RAG pipeline
def multimodal_rag(query, retriever, reranker, generator, recall_k=50, rerank_k=10):
    """Complete multimodal RAG pipeline."""
    
    # Retrieve and re-rank
    ranked_docs = retrieve_and_rerank(
        query=query,
        retriever=retriever,
        reranker=reranker,
        recall_k=recall_k,
        rerank_k=rerank_k
    )
    
    # Generate answer
    answer = generate_answer(query, ranked_docs)
    
    return {
        "answer": answer,
        "sources": [
            {
                "rank": i+1,
                "id": doc["document"].get("metadata", {}).get("source", "unknown"),
                "score": doc["score"]
            }
            for i, doc in enumerate(ranked_docs)
        ]
    }

# Usage
result = multimodal_rag(
    query={"text": "What is the height of the Eiffel Tower?"},
    retriever=hybrid_retriever,
    reranker=reranker,
    generator=model
)

print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources'][:3]}")
```

## Optimization Tips

### 1. Caching Embeddings

```python
from functools import lru_cache

class CachedEmbedder:
    """Cache embeddings to avoid redundant computation."""
    
    def __init__(self, embedder):
        self.embedder = embedder
        self.cache = {}
    
    def process(self, inputs):
        cached_embeddings = []
        uncached_inputs = []
        
        for inp in inputs:
            cache_key = hash(str(inp))
            if cache_key in self.cache:
                cached_embeddings.append(self.cache[cache_key])
            else:
                uncached_inputs.append(inp)
        
        # Process uncached inputs
        if uncached_inputs:
            new_embeddings = self.embedder.process(uncached_inputs)
            for inp, emb in zip(uncached_inputs, new_embeddings):
                self.cache[hash(str(inp))] = emb
                cached_embeddings.append(emb)
        
        return np.array(cached_embeddings)
```

### 2. Async Processing

```python
import asyncio
import aiohttp

async def parallel_retrieval(queries, retriever, k=10):
    """Process multiple queries in parallel."""
    
    async def retrieve_single(query):
        return retriever.retrieve(query, k=k)
    
    tasks = [retrieve_single(q) for q in queries]
    results = await asyncio.gather(*tasks)
    
    return results

# Usage
results = asyncio.run(parallel_retrieval(queries, hybrid_retriever))
```

### 3. GPU Memory Management

```python
def optimize_gpu_memory():
    """Free GPU memory between stages."""
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

# Use between pipeline stages
embeddings = embedder.process(inputs)
optimize_gpu_memory()

scores = reranker.process(rerank_inputs)
optimize_gpu_memory()

answer = generator.generate(context)
```

## Production Deployment

### FastAPI RAG Service

```python
from fastapi import FastAPI
from pydantic import BaseModel
import torch

app = FastAPI(title="Multimodal RAG API")

# Load models at startup
@app.on_event("startup")
async def load_models():
    global embedder, reranker, generator, retriever
    
    embedder = Qwen3VLEmbedder("Qwen/Qwen3-VL-Embedding-2B")
    reranker = Qwen3VLReranker("Qwen/Qwen3-VL-Reranker-2B")
    
    # Load index and create retriever
    index = faiss.read_index("./index/index.faiss")
    retriever = HybridRetriever(index, embedder, documents)

class RAGQuery(BaseModel):
    query: dict
    top_k: int = 5
    use_reranker: bool = True

class RAGResponse(BaseModel):
    answer: str
    sources: list[dict]
    processing_time_ms: float

@app.post("/rag", response_model=RAGResponse)
async def rag_query(request: RAGQuery):
    import time
    start = time.time()
    
    result = multimodal_rag(
        query=request.query,
        retriever=retriever,
        reranker=reranker if request.use_reranker else None,
        generator=generator,
        rerank_k=request.top_k
    )
    
    processing_time = (time.time() - start) * 1000
    
    return RAGResponse(
        answer=result["answer"],
        sources=result["sources"],
        processing_time_ms=processing_time
    )

# Run: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```
