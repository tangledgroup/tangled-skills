# Qwen3-VL-Reranker RAG Integration

This reference document provides comprehensive guidance for integrating Qwen3-VL-Reranker into Retrieval-Augmented Generation (RAG) pipelines.

## RAG Pipeline Overview

A complete multimodal RAG system with reranking follows this architecture:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Query                                   │
│                    (text, image, or both)                            │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │  1. Query Understanding   │
        │  - Intent detection       │
        │  - Modality identification│
        │  - Instruction generation │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  2. Initial Recall        │
        │  - Embedding model        │
        │  - Vector search (ANN)    │
        │  - Retrieve top-100       │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  3. Reranking             │
        │  - Qwen3-VL-Reranker      │
        │  - Precise scoring        │
        │  - Return top-10          │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  4. Context Assembly      │
        │  - Format retrieved docs  │
        │  - Add metadata           │
        │  - Build prompt           │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  5. Generation            │
        │  - LLM inference          │
        │  - Answer synthesis       │
        │  - Citation formatting    │
        └──────────────┬───────────┘
                       │
                       ▼
                Final Response
```

## Complete RAG Implementation

### Basic RAG Pipeline

```python
import torch
from scripts.qwen3_vl_embedding import Qwen3VLEmbedder
from scripts.qwen3_vl_reranker import Qwen3VLReranker
from transformers import AutoTokenizer, AutoModelForCausalLM
import numpy as np
from typing import List, Dict, Optional

class MultimodalRAGPipeline:
    def __init__(
        self,
        embedding_model_path: str = "Qwen/Qwen3-VL-Embedding-2B",
        reranker_model_path: str = "Qwen/Qwen3-VL-Reranker-2B",
        generator_model_path: str = "Qwen/Qwen3-VL-8B-Instruct",
        top_k_recall: int = 100,
        top_k_rerank: int = 10,
        device: str = "cuda"
    ):
        self.device = device
        
        # Initialize embedding model for recall
        self.embedder = Qwen3VLEmbedder(
            model_name_or_path=embedding_model_path,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
            device=device
        )
        
        # Initialize reranker for precision ranking
        self.reranker = Qwen3VLReranker(
            model_name_or_path=reranker_model_path,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
            device=device
        )
        
        # Initialize generator LLM
        self.tokenizer = AutoTokenizer.from_pretrained(generator_model_path)
        self.generator = AutoModelForCausalLM.from_pretrained(
            generator_model_path,
            torch_dtype=torch.bfloat16,
            device_map=device
        )
        
        # Configuration
        self.top_k_recall = top_k_recall
        self.top_k_rerank = top_k_rerank
        
        # Document store (in production, use vector database)
        self.documents = []
        self.document_embeddings = None
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the knowledge base."""
        self.documents.extend(documents)
        
        # Pre-compute embeddings for all documents
        doc_inputs = [
            {**doc, "instruction": "Represent the document for retrieval."}
            for doc in self.documents
        ]
        
        self.document_embeddings = self.embedder.process(doc_inputs)
    
    def retrieve(
        self,
        query: Dict,
        instruction: str = "Retrieve relevant content to answer the query."
    ) -> List[Dict]:
        """Perform two-stage retrieval with reranking."""
        
        # Stage 1: Embedding-based recall
        query_with_instruction = {**query, "instruction": instruction}
        query_embedding = self.embedder.process([query_with_instruction])[0]
        
        # Compute cosine similarity (embeddings are normalized)
        similarities = query_embedding @ self.document_embeddings.T
        
        # Get top-k candidates
        top_k_indices = np.argsort(similarities)[-self.top_k_recall:][::-1]
        candidate_docs = [self.documents[i] for i in top_k_indices]
        
        # Stage 2: Reranking
        if len(candidate_docs) > 0:
            rerank_inputs = {
                "instruction": instruction,
                "query": query,
                "documents": candidate_docs
            }
            
            rerank_scores = self.reranker.process(rerank_inputs)
            
            # Combine and sort by reranker scores
            scored_docs = list(zip(candidate_docs, rerank_scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-k after reranking
            final_docs = [doc for doc, _ in scored_docs[:self.top_k_rerank]]
        else:
            final_docs = []
        
        return final_docs
    
    def generate_response(
        self,
        query: Dict,
        retrieved_docs: List[Dict],
        max_new_tokens: int = 512
    ) -> str:
        """Generate response using retrieved context."""
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            if "text" in doc:
                context_parts.append(f"[Document {i}]: {doc['text']}")
            if "image" in doc:
                context_parts.append(f"[Document {i} contains an image]")
        
        context = "\n\n".join(context_parts)
        
        # Build prompt
        if "text" in query:
            query_text = query["text"]
        else:
            query_text = "Describe what you see."
        
        prompt = f"""You are a helpful assistant. Use the following context to answer the question.
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {query_text}

Answer:"""
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.generator.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Answer:")[-1].strip()
    
    def query(self, query: Dict, instruction: str = None) -> Dict:
        """Complete RAG query pipeline."""
        
        if instruction is None:
            instruction = "Retrieve relevant content to answer the query."
        
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, instruction)
        
        # Generate response
        response = self.generate_response(query, retrieved_docs)
        
        return {
            "query": query,
            "retrieved_documents": retrieved_docs,
            "num_retrieved": len(retrieved_docs),
            "response": response
        }


# Usage Example
if __name__ == "__main__":
    # Initialize pipeline
    rag = MultimodalRAGPipeline()
    
    # Add documents to knowledge base
    documents = [
        {
            "text": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar.",
            "metadata": {"source": "biology_textbook", "page": 42}
        },
        {
            "text": "The mitochondria is known as the powerhouse of the cell, responsible for generating most of the cell's supply of adenosine triphosphate (ATP).",
            "metadata": {"source": "biology_textbook", "page": 45}
        },
        {
            "image": "cell_structure.jpg",
            "text": "Diagram showing cellular organelles including nucleus, mitochondria, endoplasmic reticulum, and Golgi apparatus.",
            "metadata": {"source": "biology_textbook", "page": 44}
        },
        # Add more documents...
    ]
    
    rag.add_documents(documents)
    
    # Query the RAG system
    query = {"text": "What are the main organelles in a cell and their functions?"}
    result = rag.query(query)
    
    print(f"Retrieved {result['num_retrieved']} documents")
    print(f"Response: {result['response']}")
```

## Advanced RAG Patterns

### Hybrid Search (Dense + Sparse)

Combine embedding-based retrieval with keyword search:

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRAGPipeline(MultimodalRAGPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bm25 = None
    
    def add_documents(self, documents: List[Dict]):
        """Add documents and build BM25 index."""
        super().add_documents(documents)
        
        # Tokenize documents for BM25
        tokenized_docs = []
        for doc in self.documents:
            text = doc.get("text", "")
            tokens = self._tokenize(text)
            tokenized_docs.append(tokens)
        
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        import re
        return re.findall(r'\b\w+\b', text.lower())
    
    def retrieve(self, query: Dict, instruction: str = None) -> List[Dict]:
        """Hybrid retrieval combining dense and sparse methods."""
        
        if instruction is None:
            instruction = "Retrieve relevant content to answer the query."
        
        # Dense retrieval (embedding-based)
        query_with_instruction = {**query, "instruction": instruction}
        query_embedding = self.embedder.process([query_with_instruction])[0]
        dense_similarities = query_embedding @ self.document_embeddings.T
        
        # Sparse retrieval (BM25)
        query_text = query.get("text", "")
        query_tokens = self._tokenize(query_text)
        
        if self.bm25 and query_tokens:
            sparse_scores = np.array(self.bm25.get_scores(query_tokens))
        else:
            sparse_scores = np.zeros(len(self.documents))
        
        # Normalize scores
        dense_norm = (dense_similarities - dense_similarities.min()) / \
                     (dense_similarities.max() - dense_similarities.min() + 1e-8)
        sparse_norm = (sparse_scores - sparse_scores.min()) / \
                      (sparse_scores.max() - sparse_scores.min() + 1e-8)
        
        # Combine scores (tunable alpha parameter)
        alpha = 0.5  # Weight for dense retrieval
        combined_scores = alpha * dense_norm + (1 - alpha) * sparse_norm
        
        # Get top-k candidates from hybrid scoring
        top_k_indices = np.argsort(combined_scores)[-self.top_k_recall:][::-1]
        candidate_docs = [self.documents[i] for i in top_k_indices]
        
        # Rerank with Qwen3-VL-Reranker
        if len(candidate_docs) > 0:
            rerank_inputs = {
                "instruction": instruction,
                "query": query,
                "documents": candidate_docs
            }
            
            rerank_scores = self.reranker.process(rerank_inputs)
            
            scored_docs = list(zip(candidate_docs, rerank_scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            final_docs = [doc for doc, _ in scored_docs[:self.top_k_rerank]]
        else:
            final_docs = []
        
        return final_docs
```

### Multi-Query RAG

Generate multiple query variations for better recall:

```python
from typing import List

class MultiQueryRAGPipeline(MultimodalRAGPipeline):
    def generate_query_variations(self, query: Dict, num_variations: int = 3) -> List[Dict]:
        """Generate multiple query variations using LLM."""
        
        query_text = query.get("text", "")
        
        prompt = f"""Generate {num_variations} different ways to ask the following question:
Original: {query_text}

Variations:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.generator.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.8,
            top_p=0.9,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse variations
        variations = []
        for line in response.split("\n"):
            if line.strip() and not line.startswith("Variations"):
                variations.append({"text": line.strip()})
        
        return variations[:num_variations]
    
    def retrieve(self, query: Dict, instruction: str = None) -> List[Dict]:
        """Retrieve using multiple query variations."""
        
        if instruction is None:
            instruction = "Retrieve relevant content to answer the query."
        
        # Generate query variations
        variations = self.generate_query_variations(query)
        variations.insert(0, query)  # Include original query
        
        # Retrieve for each variation
        all_candidates = []
        for var_query in variations:
            query_with_instruction = {**var_query, "instruction": instruction}
            query_embedding = self.embedder.process([query_with_instruction])[0]
            
            similarities = query_embedding @ self.document_embeddings.T
            top_k_indices = np.argsort(similarities)[-self.top_k_recall // len(variations):][::-1]
            
            for idx in top_k_indices:
                if self.documents[idx] not in all_candidates:
                    all_candidates.append(self.documents[idx])
        
        # Limit candidates and rerank
        if len(all_candidates) > self.top_k_recall:
            all_candidates = all_candidates[:self.top_k_recall]
        
        if len(all_candidates) > 0:
            rerank_inputs = {
                "instruction": instruction,
                "query": query,  # Use original query for reranking
                "documents": all_candidates
            }
            
            rerank_scores = self.reranker.process(rerank_inputs)
            
            scored_docs = list(zip(all_candidates, rerank_scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            final_docs = [doc for doc, _ in scored_docs[:self.top_k_rerank]]
        else:
            final_docs = []
        
        return final_docs
```

### Context Compression

Compress retrieved context to fit model context window:

```python
class CompressedRAGPipeline(MultimodalRAGPipeline):
    def compress_context(
        self,
        documents: List[Dict],
        max_tokens: int = 2000
    ) -> List[Dict]:
        """Compress retrieved documents to fit context window."""
        
        # Estimate tokens per document
        def count_tokens(doc: Dict) -> int:
            text = doc.get("text", "")
            return len(text) // 4  # Rough estimate
        
        # Sort by relevance (already sorted from reranking)
        sorted_docs = sorted(documents, key=count_tokens)
        
        # Greedy selection
        selected_docs = []
        total_tokens = 0
        
        for doc in sorted_docs:
            doc_tokens = count_tokens(doc)
            
            if total_tokens + doc_tokens <= max_tokens:
                selected_docs.append(doc)
                total_tokens += doc_tokens
            else:
                # Truncate document if needed
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 100:  # Only add if meaningful content
                    text = doc["text"][:remaining_tokens * 4]
                    truncated_doc = {**doc, "text": text + "..."}
                    selected_docs.append(truncated_doc)
                    break
        
        return selected_docs
    
    def generate_response(
        self,
        query: Dict,
        retrieved_docs: List[Dict],
        max_context_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate response with compressed context."""
        
        # Compress context if needed
        if len(retrieved_docs) > 1:
            compressed_docs = self.compress_context(retrieved_docs, max_context_tokens)
        else:
            compressed_docs = retrieved_docs
        
        return super().generate_response(query, compressed_docs, **kwargs)
```

## Production Deployment Patterns

### Vector Database Integration

Use production vector databases for scalable retrieval:

```python
from pinecone import Pinecone
import numpy as np

class PineconeRAGPipeline(MultimodalRAGPipeline):
    def __init__(self, *args, pinecone_api_key: str, index_name: str, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.pinecone = Pinecone(api_key=pinecone_api_key)
        self.index = self.pinecone.Index(index_name)
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to Pinecone vector database."""
        
        # Compute embeddings
        doc_inputs = [
            {**doc, "instruction": "Represent the document for retrieval."}
            for doc in self.documents
        ]
        embeddings = self.embedder.process(doc_inputs)
        
        # Upload to Pinecone
        vectors = [
            (
                str(i),
                embedding.tolist(),
                {"text": doc.get("text", ""), "metadata": doc.get("metadata", {})}
            )
            for i, (embedding, doc) in enumerate(zip(embeddings, documents))
        ]
        
        self.index.upsert(vectors=vectors)
    
    def retrieve(self, query: Dict, instruction: str = None) -> List[Dict]:
        """Retrieve from Pinecone with reranking."""
        
        if instruction is None:
            instruction = "Retrieve relevant content to answer the query."
        
        # Query vector database
        query_with_instruction = {**query, "instruction": instruction}
        query_embedding = self.embedder.process([query_with_instruction])[0]
        
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=self.top_k_recall,
            include_metadata=True
        )
        
        # Extract documents
        candidate_docs = [
            {"text": match["metadata"]["text"], "metadata": match["metadata"]}
            for match in results["matches"]
        ]
        
        # Rerank with Qwen3-VL-Reranker
        if len(candidate_docs) > 0:
            rerank_inputs = {
                "instruction": instruction,
                "query": query,
                "documents": candidate_docs
            }
            
            rerank_scores = self.reranker.process(rerank_inputs)
            
            scored_docs = list(zip(candidate_docs, rerank_scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            final_docs = [doc for doc, _ in scored_docs[:self.top_k_rerank]]
        else:
            final_docs = []
        
        return final_docs
```

### Caching Strategy

Implement multi-level caching for performance:

```python
import hashlib
import redis
import json
from typing import Optional

class CachedRAGPipeline(MultimodalRAGPipeline):
    def __init__(self, *args, redis_url: str = "redis://localhost:6379", **kwargs):
        super().__init__(*args, **kwargs)
        
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = 3600  # 1 hour
    
    def _get_cache_key(self, query: Dict, instruction: str) -> str:
        """Generate cache key from query and instruction."""
        content = json.dumps({"query": query, "instruction": instruction}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def retrieve(
        self,
        query: Dict,
        instruction: str = None,
        use_cache: bool = True
    ) -> List[Dict]:
        """Retrieve with caching."""
        
        if instruction is None:
            instruction = "Retrieve relevant content to answer the query."
        
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(query, instruction)
            cached_result = self.redis_client.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
        
        # Perform retrieval
        retrieved_docs = super().retrieve(query, instruction)
        
        # Cache result
        if use_cache:
            cache_key = self._get_cache_key(query, instruction)
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(retrieved_docs)
            )
        
        return retrieved_docs
```

## Monitoring and Evaluation

### RAG Metrics Tracking

```python
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class RAGMetrics:
    """Track RAG pipeline performance metrics."""
    
    retrieval_times: List[float] = None
    generation_times: List[float] = None
    num_retrieved_docs: List[int] = None
    rerank_scores: List[List[float]] = None
    
    def __post_init__(self):
        if self.retrieval_times is None:
            self.retrieval_times = []
        if self.generation_times is None:
            self.generation_times = []
        if self.num_retrieved_docs is None:
            self.num_retrieved_docs = []
        if self.rerank_scores is None:
            self.rerank_scores = []
    
    def record_query(self, retrieval_time: float, generation_time: float, 
                     num_docs: int, rerank_scores: List[float]):
        """Record metrics from a single query."""
        self.retrieval_times.append(retrieval_time)
        self.generation_times.append(generation_time)
        self.num_retrieved_docs.append(num_docs)
        self.rerank_scores.append(rerank_scores)
    
    def get_stats(self) -> dict:
        """Compute aggregate statistics."""
        return {
            "avg_retrieval_time_ms": np.mean(self.retrieval_times) * 1000,
            "avg_generation_time_ms": np.mean(self.generation_times) * 1000,
            "p95_retrieval_time_ms": np.percentile(self.retrieval_times, 95) * 1000,
            "p95_generation_time_ms": np.percentile(self.generation_times, 95) * 1000,
            "avg_docs_retrieved": np.mean(self.num_retrieved_docs),
            "avg_top_rerank_score": np.mean([scores[0] for scores in self.rerank_scores if scores]),
            "total_queries": len(self.retrieval_times)
        }


# Usage with metrics tracking
class MonitoredRAGPipeline(MultimodalRAGPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = RAGMetrics()
    
    def query(self, query: Dict, instruction: str = None) -> Dict:
        """Query with metrics tracking."""
        
        import time
        
        # Track retrieval time
        start_retrieval = time.time()
        retrieved_docs = self.retrieve(query, instruction)
        retrieval_time = time.time() - start_retrieval
        
        # Track generation time
        start_generation = time.time()
        response = self.generate_response(query, retrieved_docs)
        generation_time = time.time() - start_generation
        
        # Get rerank scores (would need to modify retrieve to return them)
        rerank_scores = []  # Implement in full version
        
        # Record metrics
        self.metrics.record_query(
            retrieval_time, generation_time,
            len(retrieved_docs), rerank_scores
        )
        
        return {
            "query": query,
            "retrieved_documents": retrieved_docs,
            "num_retrieved": len(retrieved_docs),
            "response": response,
            "metrics": self.metrics.get_stats()
        }
```

## Troubleshooting RAG Issues

### Issue: Poor Retrieval Quality

**Symptoms**: Relevant documents not being retrieved

**Solutions**:
1. Increase top-k for recall stage
2. Use hybrid search (dense + sparse)
3. Implement multi-query retrieval
4. Add task-specific instructions

```python
rag = MultimodalRAGPipeline(
    top_k_recall=200,  # Increase from 100
    top_k_rerank=15    # Increase from 10
)
```

### Issue: Slow Response Times

**Symptoms**: End-to-end latency > 2 seconds

**Solutions**:
1. Enable caching for repeated queries
2. Use smaller models (2B instead of 8B)
3. Reduce top-k values
4. Implement async processing

```python
rag = CachedRAGPipeline(
    redis_url="redis://localhost:6379",
    top_k_recall=50,   # Reduce from 100
    top_k_rerank=5     # Reduce from 10
)
```

### Issue: Context Overflow

**Symptoms**: LLM truncating retrieved context

**Solutions**:
1. Implement context compression
2. Reduce number of retrieved documents
3. Use summarization for long documents

```python
rag = CompressedRAGPipeline(
    top_k_rerank=20  # Retrieve more
)

# Compression happens automatically in generate_response
response = rag.generate_response(
    query, retrieved_docs,
    max_context_tokens=2000  # Limit context size
)
```
