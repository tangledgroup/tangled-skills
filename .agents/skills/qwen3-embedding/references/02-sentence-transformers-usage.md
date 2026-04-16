# Sentence Transformers Usage

The `sentence-transformers` library provides the simplest and most convenient API for using Qwen3 Embedding models.

## Requirements

```bash
pip install sentence-transformers>=2.7.0 transformers>=4.51.0 torch
```

**Critical:** `transformers>=4.51.0` is required. Earlier versions will raise:
```
KeyError: 'qwen3'
```

## Basic Usage — Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

# Encode queries and documents
queries = ["What is the capital of China?", "Explain gravity"]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other."
]

query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

# Compute cosine similarity
similarity = model.similarity(query_embeddings, document_embeddings)
print(similarity)
# tensor([[0.7646, 0.1414],
#         [0.1355, 0.6000]])
```

## Recommended Configuration (Flash Attention 2)

For better performance and reduced memory usage:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={
        "attn_implementation": "flash_attention_2",
        "device_map": "auto"
    },
    tokenizer_kwargs={"padding_side": "left"}
)
```

## Using Custom Instructions (Prompt Names)

Qwen3 Embedding models support task-specific prompts stored in `model.prompts`:

```python
# Available prompt names depend on the model's training
# Common built-in prompts: "query", "passage", etc.

queries = ["What is Python?"]
documents = [
    "Python is a programming language.",
    "The python snake is venomous."
]

# Use the "query" prompt for queries (improves retrieval)
query_embeddings = model.encode(queries, prompt_name="query")

# No prompt needed for documents
doc_embeddings = model.encode(documents)

similarity = model.similarity(query_embeddings, doc_embeddings)
```

## Custom Instructions via Prompt Argument

You can pass your own instruction-aware prompts:

```python
task_description = "Given a web search query, retrieve relevant passages"

queries = [
    f"Instruct: {task_description}\nQuery:What is the capital of China?"
]
documents = ["The capital of China is Beijing."]

query_embeddings = model.encode(queries)  # instruction already in text
doc_embeddings = model.encode(documents)
```

## Dimensionality Control (MRL)

All three embedding models support custom output dimensions via MRL:

```python
from sentence_transformers import SentenceTransformer, InputType

# Load with specific dimension
model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={"attn_implementation": "flash_attention_2"},
    tokenizer_kwargs={"padding_side": "left"}
)

# Encode with custom dimension (0.6B supports 32–1024, 4B: 32–2560, 8B: 32–4096)
embeddings = model.encode(
    ["Hello world"],
    dimension=512  # project to 512-dim vector
)
print(embeddings.shape)  # (1, 512)
```

## Batch Encoding and Similarity Operations

```python
import torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

# Large-scale encoding
texts = ["Text " + str(i) for i in range(1000)]
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

# Similarity matrix
query_emb = model.encode(["What is AI?"])
doc_emb = model.encode([f"Document {i}" for i in range(100)])
scores = model.similarity(query_emb, doc_emb)  # (1, 100)

# Top-k retrieval
top_k = 5
top_indices = torch.topk(scores, k=top_k).indices.tolist()[0]
print(f"Top {top_k} documents: {top_indices}")
```

## Semantic Search / Retrieval Pipeline

```python
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Qwen3SemanticSearch:
    def __init__(self, model_name="Qwen/Qwen3-Embedding-0.6B", dimension=None):
        self.model = SentenceTransformer(
            model_name,
            model_kwargs={"attn_implementation": "flash_attention_2", "device_map": "auto"},
            tokenizer_kwargs={"padding_side": "left"}
        )
        self.dimension = dimension
        self.documents = []
        self.embeddings = None

    def add_documents(self, documents, batch_size=64):
        """Add documents to the index."""
        self.documents.extend(documents)
        self.embeddings = self.model.encode(
            documents,
            batch_size=batch_size,
            dimension=self.dimension,
            show_progress_bar=True
        )

    def search(self, query, top_k=5, prompt_name="query"):
        """Search for similar documents."""
        query_emb = self.model.encode([query], prompt_name=prompt_name)
        scores = cosine_similarity(query_emb, self.embeddings)[0]
        results = np.argsort(scores)[::-1][:top_k]
        return [
            {"index": int(idx), "score": float(scores[idx]), "text": self.documents[idx]}
            for idx in results
        ]

# Usage
searcher = Qwen3SemanticSearch()
searcher.add_documents(["Doc 1...", "Doc 2...", "Doc 3..."])
results = searcher.search("What is machine learning?")
for r in results:
    print(f"Score: {r['score']:.4f} | {r['text']}")
```

## Cross-Lingual Embedding

```python
model = SentenceTransformer("Qwen/Qwen3-Embedding-8B")

# Query in English, documents in different languages
query = ["What is quantum computing?"]  # English
docs = [
    "量子計算とは何か？",                    # Japanese
    "¿Qué es la computación cuántica?",      # Spanish
    "什么是量子计算？"                         # Chinese
]

query_emb = model.encode(query, prompt_name="query")
doc_emb = model.encode(docs)
similarity = model.similarity(query_emb, doc_emb)
print(similarity)  # Cross-lingual similarity scores
```

## References

- Sentence Transformers docs: https://sbert.net/
- Hugging Face (0.6B): https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Hugging Face (4B): https://huggingface.co/Qwen/Qwen3-Embedding-4B
- Hugging Face (8B): https://huggingface.co/Qwen/Qwen3-Embedding-8B
