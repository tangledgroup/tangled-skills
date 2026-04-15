# Qwen3-Reranker with Transformers API

## Installation and Setup

### Required Packages

```bash
pip install transformers>=4.51.0 torch sentence-transformers>=2.7.0

# For flash attention (recommended for GPU)
pip install flash-attn

# For CPU-only inference (slower but works)
pip install transformers>=4.51.0 torch-cpu
```

### Version Compatibility

| Component | Minimum Version | Recommended Version |
|-----------|----------------|---------------------|
| transformers | 4.51.0 | 4.47.0+ |
| torch | 2.0.0 | 2.5.0+ |
| sentence-transformers | 2.7.0 | 3.0.0+ |
| flash-attn | - | 2.6.3+ |

**Important**: Transformers < 4.51.0 will raise `KeyError: 'qwen3'` due to missing tokenizer config.

## Basic Usage

### Loading the Model

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Model selection
model_name = "Qwen/Qwen3-Reranker-0.6B"  # or 4B, 8B

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    padding_side='left',  # Critical for batch processing
    trust_remote_code=True
)

# Load model with optimizations
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
    attn_implementation="flash_attention_2" if device.type == "cuda" else None,
    device_map="auto" if device.type == "cuda" else None,
    trust_remote_code=True
)

if device.type == "cpu":
    model.to(device)

model.eval()  # Set to evaluation mode
```

### Simple Reranking Example

```python
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

# Setup
model_name = "Qwen/Qwen3-Reranker-0.6B"
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
).eval()

# Define tokens
token_yes_id = tokenizer.convert_tokens_to_ids("yes")
token_no_id = tokenizer.convert_tokens_to_ids("no")

# Prepare query-document pairs
query = "What is machine learning?"
documents = [
    "Machine learning is a subset of artificial intelligence.",
    "The weather today is sunny with high of 25°C.",
    "Supervised learning uses labeled training data."
]

# Format inputs with instruction
instruction = "Given a web search query, retrieve relevant passages that answer the query"
pairs = [
    f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}"
    for doc in documents
]

# Tokenize
inputs = tokenizer(
    pairs,
    padding=True,
    truncation=True,
    max_length=2048,
    return_tensors="pt"
).to(model.device)

# Get scores
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits[:, -1, :]  # Last position
    
    # Extract yes/no logits
    yes_logits = logits[:, token_yes_id]
    no_logits = logits[:, token_no_id]
    
    # Compute probability of "yes"
    batch_scores = torch.stack([no_logits, yes_logits], dim=1)
    batch_scores = F.log_softmax(batch_scores, dim=1)
    scores = batch_scores[:, 1].exp().tolist()

# Rank documents
ranked_results = sorted(
    zip(documents, scores),
    key=lambda x: x[1],
    reverse=True
)

for i, (doc, score) in enumerate(ranked_results, 1):
    print(f"{i}. {score:.4f}: {doc[:60]}...")
```

**Output:**
```
1. 0.9234: Machine learning is a subset of artificial intelligence....
2. 0.8876: Supervised learning uses labeled training data....
3. 0.1234: The weather today is sunny with high of 25°C....
```

## Complete Reranker Class

### Reusable Reranker Implementation

```python
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Tuple, Optional

class Qwen3Reranker:
    """Complete reranker implementation with batch processing and optimization."""
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-Reranker-0.6B",
        max_length: int = 2048,
        default_instruction: Optional[str] = None,
        device: Optional[str] = None
    ):
        """Initialize the reranker model."""
        
        # Setup device
        self.device = torch.device(
            device if device is not None else 
            ("cuda" if torch.cuda.is_available() else "cpu")
        )
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            padding_side='left',
            trust_remote_code=True
        )
        
        # Determine dtype based on device
        dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        
        # Load model with optimizations
        attn_impl = "flash_attention_2" if self.device.type == "cuda" else None
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            attn_implementation=attn_impl,
            device_map="auto" if self.device.type == "cuda" else None,
            trust_remote_code=True
        )
        
        if self.device.type == "cpu":
            self.model.to(self.device)
        
        self.model.eval()
        
        # Configuration
        self.max_length = max_length
        self.default_instruction = default_instruction or \
            "Given a web search query, retrieve relevant passages that answer the query"
        
        # Token IDs for classification
        self.token_yes_id = self.tokenizer.convert_tokens_to_ids("yes")
        self.token_no_id = self.tokenizer.convert_tokens_to_ids("no")
    
    def format_pair(
        self,
        instruction: str,
        query: str,
        document: str
    ) -> str:
        """Format a query-document pair with instruction."""
        return f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {document}"
    
    def compute_scores(
        self,
        pairs: List[Tuple[str, str]],
        instruction: Optional[str] = None,
        batch_size: int = 32
    ) -> List[float]:
        """
        Compute relevance scores for query-document pairs.
        
        Args:
            pairs: List of (query, document) tuples
            instruction: Task instruction (uses default if None)
            batch_size: Batch size for processing
            
        Returns:
            List of relevance scores (0-1)
        """
        if instruction is None:
            instruction = self.default_instruction
        
        all_scores = []
        
        # Process in batches
        for i in range(0, len(pairs), batch_size):
            batch_pairs = pairs[i:i+batch_size]
            
            # Format inputs
            formatted = [
                self.format_pair(instruction, query, doc)
                for query, doc in batch_pairs
            ]
            
            # Tokenize
            inputs = self.tokenizer(
                formatted,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt"
            ).to(self.device)
            
            # Compute scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[:, -1, :]
                
                yes_logits = logits[:, self.token_yes_id]
                no_logits = logits[:, self.token_no_id]
                
                batch_scores = torch.stack([no_logits, yes_logits], dim=1)
                batch_scores = F.log_softmax(batch_scores, dim=1)
                scores = batch_scores[:, 1].exp().tolist()
            
            all_scores.extend(scores)
        
        return all_scores
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        instruction: Optional[str] = None,
        top_k: Optional[int] = None,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        Rerank documents for a query and return top results.
        
        Args:
            query: Search query
            documents: List of candidate documents
            instruction: Task instruction
            top_k: Number of top results to return (None for all)
            threshold: Minimum score threshold
            
        Returns:
            List of (document, score) tuples, sorted by score descending
        """
        pairs = [(query, doc) for doc in documents]
        scores = self.compute_scores(pairs, instruction)
        
        # Combine and sort
        ranked = list(zip(documents, scores))
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        # Apply threshold
        ranked = [item for item in ranked if item[1] >= threshold]
        
        # Apply top_k
        if top_k is not None:
            ranked = ranked[:top_k]
        
        return ranked
    
    def batch_rerank(
        self,
        queries: List[str],
        document_lists: List[List[str]],
        instruction: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[List[Tuple[str, float]]]:
        """
        Rerank multiple query-document sets in parallel.
        
        Args:
            queries: List of queries
            document_lists: List of document lists (one per query)
            instruction: Task instruction
            top_k: Number of top results per query
            
        Returns:
            List of ranked results for each query
        """
        results = []
        
        for query, docs in zip(queries, document_lists):
            ranked = self.rerank(query, docs, instruction, top_k)
            results.append(ranked)
        
        return results


# Usage example
if __name__ == "__main__":
    # Initialize reranker
    reranker = Qwen3Reranker(
        model_name="Qwen/Qwen3-Reranker-0.6B",
        max_length=2048,
        default_instruction="Retrieve documents that answer the query"
    )
    
    # Single query reranking
    query = "How to install Python on Windows?"
    documents = [
        "Download Python from python.org and run the installer.",
        "Python is a programming language created by Guido van Rossum.",
        "Use pip to install Python packages after installing Python.",
        "Windows 11 includes PowerShell for scripting."
    ]
    
    results = reranker.rerank(query, documents, top_k=3)
    
    print("Top 3 results:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. {score:.4f}: {doc}")
```

## Advanced Features

### Cross-Encoder Integration

Use Qwen3-Reranker as a sentence-transformers CrossEncoder:

```python
from sentence_transformers import CrossEncoder

# Initialize as CrossEncoder
model = CrossEncoder(
    'Qwen/Qwen3-Reranker-0.6B',
    max_length=2048,
    device='cuda'
)

# Prepare pairs (query, document)
query = "What causes climate change?"
documents = [
    "Greenhouse gases trap heat in the atmosphere.",
    "The Earth orbits the Sun once every 365 days.",
    "CO2 emissions from burning fossil fuels increase global temperatures."
]

pairs = [(query, doc) for doc in documents]

# Get scores (normalized similarity, not probability)
scores = model.predict(pairs)

# Rank results
ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

for doc, score in ranked:
    print(f"{score:.4f}: {doc}")
```

### Multi-Query Optimization

For multiple queries with same documents, use batch processing:

```python
def multi_query_rerank(reranker, queries, documents, instruction):
    """Rerank same documents for multiple queries efficiently."""
    
    # Create all query-document pairs
    all_pairs = []
    query_indices = []
    
    for q_idx, query in enumerate(queries):
        for d_idx, doc in enumerate(documents):
            all_pairs.append((query, doc))
            query_indices.append(q_idx)
    
    # Compute all scores at once
    all_scores = reranker.compute_scores(all_pairs, instruction)
    
    # Group by query
    results = [[] for _ in range(len(queries))]
    for i, score in enumerate(all_scores):
        q_idx = query_indices[i]
        d_idx = i % len(documents)
        results[q_idx].append((documents[d_idx], score))
    
    # Sort each query's results
    for i in range(len(results)):
        results[i].sort(key=lambda x: x[1], reverse=True)
    
    return results


# Usage
queries = [
    "What is Python?",
    "How to learn Python?",
    "Python vs Java"
]

documents = [
    "Python is a high-level programming language.",
    "Start with online courses like Codecademy or Coursera.",
    "Java is statically typed while Python is dynamically typed.",
    "Python uses indentation for code blocks.",
    "Both Python and Java are popular for web development."
]

results = multi_query_rerank(reranker, queries, documents, 
                             instruction="Find relevant information")

for query, ranked in zip(queries, results):
    print(f"\nQuery: {query}")
    for doc, score in ranked[:2]:
        print(f"  {score:.3f}: {doc[:50]}...")
```

### Instruction Tuning

Different instructions for different tasks:

```python
# Web search instruction
web_search_instr = "Given a web search query, retrieve relevant passages that answer the query"

# Code retrieval instruction
code_retrieval_instr = "Find code snippets that implement the described functionality"

# FAQ retrieval instruction
faq_instr = "Retrieve FAQ entries that answer the user's question"

# Document classification instruction
classification_instr = "Select documents that belong to the specified category"

# Medical domain instruction
medical_instr = "Retrieve medical documents relevant to the clinical query"

# Legal domain instruction
legal_instr = "Find legal precedents and statutes relevant to the case"

# Usage
reranker = Qwen3Reranker(default_instruction=web_search_instr)

results = reranker.rerank(
    query="How to sort a list in Python?",
    documents=[...],
    instruction=code_retrieval_instr  # Override default for this query
)
```

## Performance Optimization

### GPU Acceleration with Flash Attention

```python
# Enable flash attention for 2-3x speedup
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-Reranker-0.6B",
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2",  # Key optimization
    device_map="auto"
)
```

**Requirements:**
- CUDA-capable GPU (Compute Capability >= 7.0)
- `pip install flash-attn`
- PyTorch compiled with CUDA support

### Batch Size Tuning

```python
import time

def benchmark_batch_size(reranker, pairs, batch_sizes=[8, 16, 32, 64, 128]):
    """Find optimal batch size for your hardware."""
    
    results = []
    
    for batch_size in batch_sizes:
        reranker.model.eval()
        
        # Warmup
        _ = reranker.compute_scores(pairs[:min(32, len(pairs))], batch_size=batch_size)
        
        # Benchmark
        start = time.time()
        iterations = 5
        
        for _ in range(iterations):
            _ = reranker.compute_scores(pairs, batch_size=batch_size)
        
        elapsed = (time.time() - start) / iterations
        throughput = len(pairs) / elapsed
        
        results.append({
            'batch_size': batch_size,
            'time_per_batch': elapsed,
            'throughput': throughput
        })
    
    # Print results
    print("Batch Size | Time (s) | Throughput (pairs/s)")
    print("-" * 45)
    for r in results:
        print(f"{r['batch_size']:10} | {r['time_per_batch']:8.3f} | {r['throughput']:20.1f}")
    
    return results


# Usage
reranker = Qwen3Reranker()
pairs = [("query", "document" * 100)] * 1000  # 1000 pairs

benchmark_batch_size(reranker, pairs)
```

### Memory Management

For large-scale reranking:

```python
import gc
import torch

class MemoryEfficientReranker(Qwen3Reranker):
    """Reranker with aggressive memory management."""
    
    def compute_scores(self, pairs, instruction=None, batch_size=32):
        """Compute scores with periodic memory cleanup."""
        
        all_scores = []
        
        for i in range(0, len(pairs), batch_size):
            batch_pairs = pairs[i:i+batch_size]
            
            # Format and tokenize
            formatted = [
                self.format_pair(instruction or self.default_instruction, q, d)
                for q, d in batch_pairs
            ]
            
            inputs = self.tokenizer(
                formatted,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt"
            ).to(self.device)
            
            # Compute scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[:, -1, :]
                
                yes_logits = logits[:, self.token_yes_id]
                no_logits = logits[:, self.token_no_id]
                
                batch_scores = torch.stack([no_logits, yes_logits], dim=1)
                batch_scores = F.log_softmax(batch_scores, dim=1)
                scores = batch_scores[:, 1].exp().tolist()
            
            all_scores.extend(scores)
            
            # Clean up memory every N batches
            if (i // batch_size) % 10 == 0:
                gc.collect()
                if self.device.type == "cuda":
                    torch.cuda.empty_cache()
        
        return all_scores
```

## Error Handling

### Common Errors and Solutions

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

try:
    # This will fail with old transformers version
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Reranker-0.6B")
    
except KeyError as e:
    if "qwen3" in str(e):
        print("Error: Transformers version too old (< 4.51.0)")
        print("Solution: pip install --upgrade transformers")
    else:
        raise

except Exception as e:
    print(f"Unexpected error: {e}")
```

### Context Length Validation

```python
def validate_context_length(tokenizer, query, document, max_length=32768):
    """Check if query-document pair fits within context limit."""
    
    combined = f"<Instruct>: instruction\n<Query>: {query}\n<Document>: {document}"
    token_count = len(tokenizer.encode(combined))
    
    if token_count > max_length:
        overflow = token_count - max_length
        print(f"Warning: Input exceeds context length by {overflow} tokens")
        print(f"Consider truncating document or using shorter query")
        return False
    
    return True
```

## References

- **Transformers Documentation**: https://huggingface.co/docs/transformers
- **Sentence Transformers**: https://www.sbert.net/
- **Flash Attention**: https://github.com/Dao-AILab/flash-attention
- **Qwen3 Models**: https://huggingface.co/collections/Qwen/qwen3-embedding-6841b2055b99c44d9a4c371f
