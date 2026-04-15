# RAG Pipelines with Qwen3 Embedding

Implementing Retrieval-Augmented Generation (RAG) systems using Qwen3 Embedding for context retrieval and LLM integration.

## Basic RAG Pipeline

### Simple Implementation

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SimpleRAG:
    def __init__(self, embedding_model="Qwen/Qwen3-Embedding-4B"):
        self.embedder = SentenceTransformer(embedding_model)
        self.documents = []
        self.embeddings = None
    
    def index_documents(self, documents):
        """Index documents for retrieval"""
        self.documents = documents
        self.embeddings = self.embedder.encode(
            documents, 
            normalize_embeddings=True
        )
    
    def retrieve(self, query, top_k=3):
        """Retrieve relevant documents"""
        query_embedding = self.embedder.encode(query, normalize_embeddings=True)
        similarities = self.embeddings @ query_embedding
        
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        return [
            {'text': self.documents[i], 'score': float(similarities[i])}
            for i in top_indices
        ]
    
    def generate_context(self, query, top_k=3):
        """Generate augmented context for LLM"""
        retrieved = self.retrieve(query, top_k)
        
        context_parts = [f"Document {i+1}: {r['text']}" 
                        for i, r in enumerate(retrieved)]
        context = "\n\n".join(context_parts)
        
        return f"""Use the following context to answer the question.

Context:
{context}

Question: {query}

Answer:"""

# Usage
rag = SimpleRAG()
rag.index_documents([
    "Python is a high-level programming language created by Guido van Rossum.",
    "Machine learning is a subset of artificial intelligence.",
    "The weather in London is often rainy and cloudy."
])

query = "Who created Python?"
prompt = rag.generate_context(query)
print(prompt)
# Send prompt to LLM...
```

## Chunking Strategies

### Fixed-Size Chunking

```python
def chunk_by_size(text, max_tokens=512, overlap=50):
    """Split text into fixed-size chunks with overlap"""
    # Simple token-based splitting (use proper tokenizer in production)
    tokens = text.split()
    chunks = []
    
    for i in range(0, len(tokens), max_tokens - overlap):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(" ".join(chunk_tokens))
    
    return chunks

# Usage
long_document = """..."""  # Long text
chunks = chunk_by_size(long_document, max_tokens=512, overlap=50)

print(f"Created {len(chunks)} chunks")
```

### Semantic Chunking

```python
from sentence_transformers import SentenceTransformer

def semantic_chunking(text, sentences, threshold=0.7):
    """
    Chunk text based on semantic similarity between sentences.
    Start new chunk when similarity drops below threshold.
    """
    model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
    
    # Encode all sentences
    embeddings = model.encode(sentences, normalize_embeddings=True)
    
    chunks = []
    current_chunk = [sentences[0]]
    
    for i in range(1, len(sentences)):
        # Compute similarity with last sentence in current chunk
        similarity = np.dot(embeddings[i], embeddings[i-1])
        
        if similarity < threshold:
            # Start new chunk
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])
    
    # Add last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Usage
import re
text = """..."""  # Long document
sentences = re.split(r'(?<=[.!?])\s+', text)  # Split into sentences
chunks = semantic_chunking(text, sentences, threshold=0.75)
```

### Hierarchical Chunking

```python
def hierarchical_chunking(document, levels=[512, 256, 128]):
    """
    Create chunks at multiple granularity levels.
    Useful for different query types.
    """
    all_chunks = {}
    
    for level_idx, chunk_size in enumerate(levels):
        chunks = chunk_by_size(document, max_tokens=chunk_size)
        all_chunks[f"level_{level_idx}"] = chunks
    
    return all_chunks

# Usage
chunks = hierarchical_chunking(long_document)

def retrieve_hierarchical(query, chunks, levels=["level_0", "level_1", "level_2"]):
    """Search across chunk hierarchies"""
    model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
    
    best_results = []
    for level in levels:
        level_chunks = chunks[level]
        embeddings = model.encode(level_chunks, normalize_embeddings=True)
        
        query_emb = model.encode(query, normalize_embeddings=True)
        similarities = embeddings @ query_emb
        
        best_idx = similarities.argmax()
        best_results.append({
            'level': level,
            'chunk': level_chunks[best_idx],
            'score': float(similarities[best_idx])
        })
    
    # Sort by score and return top results
    return sorted(best_results, key=lambda x: x['score'], reverse=True)
```

## Advanced RAG Patterns

### Multi-Query Retrieval

```python
from sentence_transformers import SentenceTransformer

class MultiQueryRAG:
    def __init__(self):
        self.embedder = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
        self.documents = []
        self.embeddings = None
    
    def index(self, documents):
        self.documents = documents
        self.embeddings = self.embedder.encode(documents, normalize_embeddings=True)
    
    def generate_query_variations(self, query):
        """Generate multiple query variations (simplified - use LLM in production)"""
        # In production, use an LLM to generate paraphrases
        variations = [
            query,
            query + " explain",
            f"what is {query}",
            f"how does {query} work"
        ]
        return variations
    
    def retrieve(self, query, top_k=5):
        """Retrieve using multiple query variations"""
        variations = self.generate_query_variations(query)
        
        all_scores = []
        for variation in variations:
            query_emb = self.embedder.encode(variation, normalize_embeddings=True)
            similarities = self.embeddings @ query_emb
            all_scores.append(similarities)
        
        # Aggregate scores (max pooling across variations)
        all_scores = np.array(all_scores)
        best_scores = all_scores.max(axis=0)
        
        top_indices = best_scores.argsort()[-top_k:][::-1]
        
        return [
            {'text': self.documents[i], 'score': float(best_scores[i])}
            for i in top_indices
        ]

# Usage
rag = MultiQueryRAG()
rag.index(documents)
results = rag.retrieve("Python programming")
```

### Reranking in RAG

```python
from sentence_transformers import SentenceTransformer, CrossEncoder

class RAGWithReranking:
    def __init__(self):
        self.retriever = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
        self.reranker = CrossEncoder("Qwen/Qwen3-Embedding-4B")
        self.documents = []
        self.embeddings = None
    
    def index(self, documents):
        self.documents = documents
        self.embeddings = self.retriever.encode(documents, normalize_embeddings=True)
    
    def retrieve_and_rerank(self, query, retrieve_k=50, rerank_k=5):
        """Two-stage retrieval with reranking"""
        # Stage 1: Retrieve top-k candidates
        query_emb = self.retriever.encode(query, normalize_embeddings=True)
        similarities = self.embeddings @ query_emb
        
        top_indices = similarities.argsort()[-retrieve_k:][::-1]
        top_candidates = [self.documents[i] for i in top_indices]
        
        # Stage 2: Rerank with cross-encoder
        if len(top_candidates) > 1:
            pairs = [(query, doc) for doc in top_candidates]
            scores = self.reranker.predict(pairs)
            
            # Get top reranked results
            reranked_indices = scores.argsort()[-rerank_k:][::-1]
            
            return [
                {'text': top_candidates[i], 'score': float(scores[i])}
                for i in reranked_indices
            ]
        else:
            return [{'text': top_candidates[0], 'score': 1.0}]
    
    def generate_prompt(self, query, top_k=3):
        """Generate RAG prompt with reranked context"""
        retrieved = self.retrieve_and_rerank(query, retrieve_k=50, rerank_k=top_k)
        
        context_parts = [f"Source {i+1}: {r['text']}" 
                        for i, r in enumerate(retrieved)]
        context = "\n\n".join(context_parts)
        
        return f"""Based on the following information, answer the question.

Information:
{context}

Question: {query}

Answer:"""

# Usage
rag = RAGWithReranking()
rag.index(large_corpus)
prompt = rag.generate_prompt("How does Python's garbage collection work?")
```

## Integration with LLMs

### Using LangChain

```python
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline

# Setup embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-4B",
    model_kwargs={'device': 'cuda'}
)

# Create vector store
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings
)

# Setup retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# Query
result = qa_chain({"query": "What is Python used for?"})
print(result["result"])
print(f"Sources: {result['source_documents']}")
```

### Using LlamaIndex

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# Setup embeddings
Settings.embed_model = HuggingFaceEmbedding(
    model_name="Qwen/Qwen3-Embedding-4B"
)

# Load documents
documents = SimpleDirectoryReader("./docs").load_data()

# Build index
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine(similarity_top_k=3)
response = query_engine.query("What is machine learning?")

print(response)
```

## Evaluation

### RAGAS Evaluation Framework

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance, context_relevance

# Test dataset
test_data = [
    {
        "question": "What is Python?",
        "answer": "Python is a high-level programming language...",
        "contexts": ["Python was created by Guido van Rossum...", ...],
        "ground_truth": "Python is a programming language created in 1991."
    },
    # ... more examples
]

# Evaluate
from ragas.dataset import EvaluationDataset

dataset = EvaluationDataset(test_data)
scores = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevance, context_relevance]
)

print(scores)
```

### Custom Evaluation Metrics

```python
def evaluate_rag_system(rag_system, test_queries, ground_truths):
    """Evaluate RAG system on custom metrics"""
    import re
    
    precision_scores = []
    recall_scores = []
    
    for query, ground_truth in zip(test_queries, ground_truths):
        # Retrieve context
        prompt = rag_system.generate_context(query)
        
        # Extract retrieved documents from prompt
        retrieved_text = prompt.split("Context:\n")[1].split("Question:")[0]
        
        # Simple keyword overlap (use semantic similarity in production)
        ground_truth_words = set(ground_truth.lower().split())
        retrieved_words = set(retrieved_text.lower().split())
        
        if len(retrieved_words) > 0:
            precision = len(ground_truth_words & retrieved_words) / len(retrieved_words)
            precision_scores.append(precision)
        
        if len(ground_truth_words) > 0:
            recall = len(ground_truth_words & retrieved_words) / len(ground_truth_words)
            recall_scores.append(recall)
    
    return {
        'precision': np.mean(precision_scores),
        'recall': np.mean(recall_scores),
        'f1': 2 * np.mean(precision_scores) * np.mean(recall_scores) / 
              (np.mean(precision_scores) + np.mean(recall_scores))
    }

# Usage
metrics = evaluate_rag_system(rag, test_queries, ground_truths)
print(f"Precision: {metrics['precision']:.3f}")
print(f"Recall: {metrics['recall']:.3f}")
print(f"F1: {metrics['f1']:.3f}")
```

## See Also

- [`references/06-semantic-search.md`](06-semantic-search.md) - Search fundamentals
- [`references/04-reranking.md`](04-reranking.md) - Reranking for quality
- [`references/12-benchmarks.md`](12-benchmarks.md) - Performance benchmarks
