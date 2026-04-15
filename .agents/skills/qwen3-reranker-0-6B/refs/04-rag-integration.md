# RAG Integration with Qwen3-Reranker

## Two-Stage Retrieval Architecture

### Overview

Qwen3-Reranker is designed for **two-stage retrieval** in RAG (Retrieval-Augmented Generation) systems:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌────────┐
│   Query     │────▶│  Coarse Retrieval│────▶│ Fine Reranking  │────▶│  LLM   │
│             │     │  (Embedding/BM25)│     │ (Qwen3-Reranker)│     │        │
└─────────────┘     └──────────────────┘     └─────────────────┘     └────────┘
                           │                        │
                    Top 100-1000 docs          Top 5-20 docs
```

**Stage 1 - Coarse Retrieval:**
- Use embedding models (Qwen3-Embedding, BGE, etc.) or BM25
- Retrieve top 100-1000 candidate documents
- Fast, approximate similarity search

**Stage 2 - Fine Reranking:**
- Apply Qwen3-Reranker to score candidates
- Re-rank by relevance to query
- Return top 5-20 most relevant documents to LLM

## Complete RAG Pipeline Example

### Basic Implementation

```python
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from qwen3_reranker import Qwen3Reranker  # From refs/02-transformers-api.md

class RAGPipeline:
    """Two-stage retrieval with embedding + reranking."""
    
    def __init__(
        self,
        embedding_model: str = "Qwen/Qwen3-Embedding-0.6B",
        reranker_model: str = "Qwen/Qwen3-Reranker-0.6B",
        coarse_k: int = 100,
        fine_k: int = 10
    ):
        """Initialize RAG pipeline."""
        
        # Load embedding model for coarse retrieval
        self.embedder = SentenceTransformer(embedding_model)
        
        # Load reranker for fine ranking
        self.reranker = Qwen3Reranker(
            model_name=reranker_model,
            max_length=2048
        )
        
        # Configuration
        self.coarse_k = coarse_k  # Candidates from embedding search
        self.fine_k = fine_k      # Final documents after reranking
        
        # Document store (replace with actual vector database)
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, texts: List[str], metadata: List[dict] = None):
        """Add documents to the corpus."""
        
        if metadata is None:
            metadata = [{} for _ in texts]
        
        # Compute embeddings
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        # Store
        self.documents.extend(list(zip(texts, metadata)))
        self.embeddings = np.vstack([self.embeddings, embeddings]) if self.embeddings is not None else embeddings
    
    def coarse_retrieval(self, query: str, top_k: int = None) -> List[Tuple[str, dict, float]]:
        """Stage 1: Retrieve candidates using embedding similarity."""
        
        if top_k is None:
            top_k = self.coarse_k
        
        # Embed query
        query_embedding = self.embedder.encode(query)
        
        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return documents with scores
        results = [
            (self.documents[i][0], self.documents[i][1], similarities[i])
            for i in top_indices
        ]
        
        return results
    
    def fine_reranking(
        self,
        query: str,
        candidates: List[Tuple[str, dict, float]],
        instruction: str = None
    ) -> List[Tuple[str, dict, float]]:
        """Stage 2: Rerank candidates using Qwen3-Reranker."""
        
        if instruction is None:
            instruction = "Given a web search query, retrieve relevant passages that answer the query"
        
        # Extract documents and metadata
        docs = [c[0] for c in candidates]
        metadata_list = [c[1] for c in candidates]
        
        # Create pairs for reranking
        pairs = [(query, doc) for doc in docs]
        
        # Get reranker scores
        rerank_scores = self.reranker.compute_scores(pairs, instruction)
        
        # Combine with metadata and sort
        results = list(zip(docs, metadata_list, rerank_scores))
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results[:self.fine_k]
    
    def retrieve(
        self,
        query: str,
        instruction: str = None,
        coarse_k: int = None,
        fine_k: int = None
    ) -> List[Tuple[str, dict, float]]:
        """Complete two-stage retrieval."""
        
        # Override defaults if specified
        coarse_k = coarse_k or self.coarse_k
        fine_k = fine_k or self.fine_k
        
        # Stage 1: Coarse retrieval
        candidates = self.coarse_retrieval(query, top_k=coarse_k)
        
        # Stage 2: Fine reranking
        ranked = self.fine_reranking(query, candidates, instruction)
        
        return ranked
    
    def generate_response(
        self,
        query: str,
        llm_call_fn,
        instruction: str = None
    ) -> str:
        """Retrieve documents and generate response with LLM."""
        
        # Retrieve relevant documents
        results = self.retrieve(query, instruction)
        
        # Build context
        context = "\n\n".join([
            f"Document {i+1}: {doc}\n" + (f"Metadata: {meta}" if meta else "")
            for i, (doc, meta, score) in enumerate(results)
        ])
        
        # Create prompt
        prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        # Call LLM
        response = llm_call_fn(prompt)
        
        return response, results  # Return both response and sources


# Usage example
if __name__ == "__main__":
    # Initialize pipeline
    rag = RAGPipeline(
        embedding_model="Qwen/Qwen3-Embedding-0.6B",
        reranker_model="Qwen/Qwen3-Reranker-0.6B",
        coarse_k=100,
        fine_k=5
    )
    
    # Add sample documents
    documents = [
        "Python is a high-level programming language created by Guido van Rossum.",
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with many layers.",
        "The capital of France is Paris.",
        "Photosynthesis is how plants convert sunlight into energy."
    ]
    
    rag.add_documents(documents)
    
    # Query with two-stage retrieval
    query = "What programming language did Guido van Rossum create?"
    
    results = rag.retrieve(query, coarse_k=10, fine_k=3)
    
    print(f"Query: {query}\n")
    for i, (doc, meta, score) in enumerate(results, 1):
        print(f"{i}. Score: {score:.4f}")
        print(f"   {doc}")
        print()
```

## Integration with LangChain

### LangChain Rerank Wrapper

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers import EnsembleRetriever
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
import numpy as np

class Qwen3RerankerLangChain:
    """LangChain-compatible reranker wrapper."""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-Reranker-0.6B"):
        from qwen3_reranker import Qwen3Reranker
        self.reranker = Qwen3Reranker(model_name=model_name)
    
    def compress_documents(
        self,
        documents: list[Document],
        query: str,
        instruction: str = None
    ) -> list[Document]:
        """Compress documents by reranking."""
        
        if instruction is None:
            instruction = "Given a web search query, retrieve relevant passages that answer the query"
        
        # Create pairs
        pairs = [(query, doc.page_content) for doc in documents]
        
        # Get scores
        scores = self.reranker.compute_scores(pairs, instruction)
        
        # Sort by score
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return reranked documents with relevance scores
        reranked = []
        for doc, score in scored_docs:
            new_doc = Document(
                page_content=doc.page_content,
                metadata={**doc.metadata, "relevance_score": score}
            )
            reranked.append(new_doc)
        
        return reranked


# Complete LangChain RAG pipeline
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chains import RetrievalQA

# Setup embeddings and vector store
embeddings = SentenceTransformerEmbeddings(model_name="Qwen/Qwen3-Embedding-0.6B")
vectorstore = FAISS.from_texts(
    ["Python is a programming language.", "Machine learning is AI subset."],
    embeddings=embeddings
)

# Create retriever
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

# Add reranker compression
reranker = Qwen3RerankerLangChain("Qwen/Qwen3-Reranker-0.6B")
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)

# Create QA chain
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=compression_retriever,
    return_source_documents=True
)

# Query
result = qa_chain({"query": "What is Python?"})

print(f"Answer: {result['result']}")
print("\nSource documents:")
for i, doc in enumerate(result["source_documents"][:3], 1):
    score = doc.metadata.get("relevance_score", "N/A")
    print(f"{i}. Score: {score:.4f} - {doc.page_content[:60]}...")
```

## Integration with LlamaIndex

### LlamaIndex Rerank Node Parser

```python
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.postprocessor import PandasRankPostprocessor

# Custom reranker for LlamaIndex
class Qwen3RerankerLlamaIndex:
    """LlamaIndex-compatible reranker."""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-Reranker-0.6B"):
        from qwen3_reranker import Qwen3Reranker
        self.reranker = Qwen3Reranker(model_name=model_name)
        self.top_n = 5
    
    def postprocess_nodes(
        self,
        nodes: list,
        query_bundle: Any,
    ) -> list:
        """Rerank nodes based on query."""
        
        from llama_index.core.schema import NodeWithScore
        
        # Create pairs
        pairs = [(query_bundle.query, node.get_content()) for node in nodes]
        
        # Get scores
        scores = self.reranker.compute_scores(pairs)
        
        # Update node scores
        for node, score in zip(nodes, scores):
            node.score = score
        
        # Sort by score and return top_n
        sorted_nodes = sorted(nodes, key=lambda x: x.score if x.score else 0, reverse=True)
        
        return sorted_nodes[:self.top_n]


# Complete LlamaIndex RAG pipeline
from llama_index.core import SimpleDirectoryReader, Settings

# Setup embeddings
Settings.embed_model = HuggingFaceEmbedding(model_name="Qwen/Qwen3-Embedding-0.6B")

# Load documents
documents = SimpleDirectoryReader("your_docs_folder").load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Create query engine with reranker
reranker = Qwen3RerankerLlamaIndex("Qwen/Qwen3-Reranker-0.6B")

query_engine = index.as_query_engine(
    similarity_top_k=20,  # Coarse retrieval
    node_postprocessors=[reranker]  # Fine reranking (top 5)
)

# Query
response = query_engine.query("What is machine learning?")

print(f"Answer: {response}")

# Get source nodes with scores
for i, node in enumerate(response.source_nodes[:3], 1):
    print(f"{i}. Score: {node.score:.4f} - {node.text[:60]}...")
```

## Advanced RAG Patterns

### Hybrid Retrieval (Embedding + BM25)

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRAGPipeline(RAGPipeline):
    """Combine embedding and keyword-based retrieval."""
    
    def __init__(self, *args, bm25_weight: float = 0.3, **kwargs):
        super().__init__(*args, **kwargs)
        self.bm25_weight = bm25_weight
        self.bm25_index = None
    
    def add_documents(self, texts: List[str], metadata: List[dict] = None):
        """Add documents and build BM25 index."""
        super().add_documents(texts, metadata)
        
        # Tokenize for BM25
        tokenized_docs = [text.lower().split() for text in texts]
        self.bm25_index = BM25Okapi(tokenized_docs)
    
    def coarse_retrieval(self, query: str, top_k: int = None) -> List[Tuple[str, dict, float]]:
        """Hybrid retrieval with embedding + BM25."""
        
        if top_k is None:
            top_k = self.coarse_k
        
        # Embedding-based scores
        embed_scores = super().coarse_retrieval(query, top_k=top_k * 2)
        embed_scores = {doc: score for doc, meta, score in embed_scores}
        
        # BM25 scores
        query_tokens = query.lower().split()
        bm25_scores = self.bm25_index.get_scores(query_tokens)
        bm25_scores = bm25_scores / bm25_scores.max()  # Normalize
        
        # Combine scores
        all_docs = [doc for doc, meta, _ in self.documents]
        combined_scores = []
        
        for i, doc in enumerate(all_docs):
            embed_score = embed_scores.get(doc, 0)
            bm25_score = bm25_scores[i]
            
            # Weighted combination
            combined = (1 - self.bm25_weight) * embed_score + self.bm25_weight * bm25_score
            combined_scores.append((doc, self.documents[i][1], combined))
        
        # Sort and return top-k
        combined_scores.sort(key=lambda x: x[2], reverse=True)
        return combined_scores[:top_k]


# Usage
hybrid_rag = HybridRAGPipeline(
    embedding_model="Qwen/Qwen3-Embedding-0.6B",
    reranker_model="Qwen/Qwen3-Reranker-0.6B",
    bm25_weight=0.3  # 30% BM25, 70% embedding
)

hybrid_rag.add_documents(documents)
results = hybrid_rag.retrieve("Python programming language tutorial")
```

### Multi-Query Reranking

```python
class MultiQueryRAGPipeline(RAGPipeline):
    """Generate multiple query variations for robust retrieval."""
    
    def generate_query_variations(self, query: str, llm_fn, n: int = 3) -> List[str]:
        """Generate alternative phrasings of the query."""
        
        prompt = f"""Generate {n} different ways to ask this question:

Original: {query}

Variations (one per line):"""
        
        variations = llm_fn(prompt).strip().split("\n")
        return [query] + variations[:n]  # Include original
    
    def retrieve(
        self,
        query: str,
        instruction: str = None,
        num_variations: int = 3,
        **kwargs
    ) -> List[Tuple[str, dict, float]]:
        """Retrieve using multiple query variations."""
        
        # Generate variations
        variations = self.generate_query_variations(query, self.llm_fn, num_variations)
        
        # Retrieve for each variation
        all_results = {}
        for var_query in variations:
            candidates = self.coarse_retrieval(var_query)
            
            # Rerank each set
            ranked = self.fine_reranking(var_query, candidates, instruction)
            
            # Aggregate scores (take max across variations)
            for doc, meta, score in ranked:
                if doc not in all_results or score > all_results[doc][2]:
                    all_results[doc] = (doc, meta, score)
        
        # Sort by best score
        results = list(all_results.values())
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results[:self.fine_k]
```

### Reciprocal Rank Fusion

```python
def reciprocal_rank_fusion(
    result_lists: List[List[Tuple[str, dict, float]]],
    k: int = 60
) -> List[Tuple[str, dict, float]]:
    """
    Merge multiple ranked lists using Reciprocal Rank Fusion.
    
    Args:
        result_lists: List of ranked document lists from different queries
        k: RRF constant (larger = more weight to top results)
    
    Returns:
        Fused ranked list
    """
    
    from collections import defaultdict
    
    # Accumulate RRF scores
    rrf_scores = defaultdict(float)
    all_metadata = {}
    
    for results in result_lists:
        for rank, (doc, meta, _) in enumerate(results, 1):
            # RRF score: 1 / (k + rank)
            rrf_scores[doc] += 1.0 / (k + rank)
            all_metadata[doc] = meta
    
    # Sort by RRF score
    fused = [
        (doc, all_metadata[doc], score)
        for doc, score in rrf_scores.items()
    ]
    fused.sort(key=lambda x: x[2], reverse=True)
    
    return fused


# Usage in multi-query pipeline
def multi_query_with_rrf(self, query: str, num_variations: int = 3):
    """Multi-query retrieval with RRF fusion."""
    
    variations = self.generate_query_variations(query, num_variations)
    
    # Retrieve for each variation
    result_lists = []
    for var_query in variations:
        candidates = self.coarse_retrieval(var_query)
        ranked = self.fine_reranking(var_query, candidates)
        result_lists.append(ranked)
    
    # Fuse results
    fused = reciprocal_rank_fusion(result_lists, k=60)
    
    return fused[:self.fine_k]
```

## Performance Optimization

### Caching Strategies

```python
from functools import lru_cache
import hashlib

class CachedRAGPipeline(RAGPipeline):
    """RAG pipeline with result caching."""
    
    def __init__(self, *args, cache_size: int = 1000, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cache for reranking results
        @lru_cache(maxsize=cache_size)
        def cached_rerank(query_hash: str, docs_hash: str, instruction: str):
            query, docs = self._decode_hashes(query_hash, docs_hash)
            pairs = [(query, doc) for doc in docs]
            return tuple(self.reranker.compute_scores(pairs, instruction))
        
        self.cached_rerank = cached_rerank
    
    def _hash_query(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()[:16]
    
    def _hash_docs(self, docs: tuple) -> str:
        return hashlib.md5("".join(docs).encode()).hexdigest()[:16]
    
    def fine_reranking(self, query: str, candidates: list, instruction: str = None):
        """Rerank with caching."""
        
        # Extract documents
        docs = tuple(c[0] for c in candidates)
        
        # Use cached reranking
        query_hash = self._hash_query(query)
        docs_hash = self._hash_docs(docs)
        instr = instruction or "default"
        
        rerank_scores = list(self.cached_rerank(query_hash, docs_hash, instr))
        
        # Combine and sort
        results = list(zip([c[0] for c in candidates], [c[1] for c in candidates], rerank_scores))
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results[:self.fine_k]
```

### Async RAG Pipeline

```python
import asyncio
from typing import List, Tuple

class AsyncRAGPipeline:
    """Asynchronous RAG pipeline for concurrent queries."""
    
    def __init__(self, rag_pipeline: RAGPipeline, max_concurrent: int = 10):
        self.rag = rag_pipeline
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def retrieve(self, query: str, **kwargs) -> List[Tuple[str, dict, float]]:
        """Async retrieval with concurrency control."""
        
        async with self.semaphore:
            # Run blocking retrieval in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self.rag.retrieve,
                query,
                **kwargs
            )
            return results
    
    async def retrieve_batch(self, queries: List[str], **kwargs) -> List[List[Tuple[str, dict, float]]]:
        """Process multiple queries concurrently."""
        
        tasks = [self.retrieve(query, **kwargs) for query in queries]
        results = await asyncio.gather(*tasks)
        
        return results


# Usage
import asyncio

rag = RAGPipeline()
async_rag = AsyncRAGPipeline(rag, max_concurrent=5)

async def main():
    queries = [
        "What is Python?",
        "How does machine learning work?",
        "Explain neural networks"
    ]
    
    results = await async_rag.retrieve_batch(queries)
    
    for query, result in zip(queries, results):
        print(f"\nQuery: {query}")
        for doc, meta, score in result[:3]:
            print(f"  {score:.3f}: {doc[:50]}...")

asyncio.run(main())
```

## Evaluation and Monitoring

### RAG Quality Metrics

```python
from sklearn.metrics import ndcg_score, precision_score, recall_score

class RAGEvaluator:
    """Evaluate RAG pipeline quality."""
    
    def __init__(self):
        self.results = []
    
    def evaluate_retrieval(
        self,
        rag_pipeline: RAGPipeline,
        test_queries: List[dict]  # {query, relevant_docs, instruction}
    ) -> dict:
        """Evaluate retrieval quality."""
        
        all_predictions = []
        all_ground_truth = []
        
        for test_case in test_queries:
            query = test_case["query"]
            relevant = set(test_case["relevant_docs"])
            
            # Retrieve
            results = rag_pipeline.retrieve(query, instruction=test_case.get("instruction"))
            retrieved_docs = [doc for doc, meta, score in results]
            
            # Compute binary relevance
            predictions = [1.0 if doc in relevant else 0.0 for doc in retrieved_docs]
            ground_truth = [1.0 if doc in relevant else 0.0 for doc in rag_pipeline.documents]
            
            all_predictions.append(predictions)
            all_ground_truth.append(ground_truth)
        
        # Compute metrics
        ndcg = ndcg_score([all_ground_truth], [all_predictions])
        
        # Precision@K and Recall@K
        precision_at_5 = precision_score(all_ground_truth[:5], all_predictions[:5], average='micro')
        recall_at_5 = recall_score(all_ground_truth, all_predictions[:5], average='micro')
        
        return {
            "ndcg": ndcg,
            "precision@5": precision_at_5,
            "recall@5": recall_at_5
        }


# Usage
evaluator = RAGEvaluator()

test_queries = [
    {
        "query": "What is Python?",
        "relevant_docs": ["Python is a programming language."],
        "instruction": "Find programming language information"
    },
    # Add more test cases...
]

metrics = evaluator.evaluate_retrieval(rag_pipeline, test_queries)
print(f"NDCG: {metrics['ndcg']:.4f}")
print(f"P@5: {metrics['precision@5']:.4f}")
print(f"R@5: {metrics['recall@5']:.4f}")
```

## References

- **LangChain Documentation**: https://python.langchain.com/
- **LlamaIndex Documentation**: https://docs.llamaindex.ai/
- **FAISS Vector Search**: https://github.com/facebookresearch/faiss
- **BM25 Ranking**: https://github.com/dorianbrown/rank-bm25
