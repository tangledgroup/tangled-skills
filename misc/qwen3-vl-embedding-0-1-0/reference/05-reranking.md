# Reranking Integration

## Two-Stage Retrieval Pipeline

The recommended retrieval architecture uses Qwen3-VL-Embedding for initial recall and Qwen3-VL-Reranker for precision refinement:

1. **Recall Stage (Embedding)**: Encode all documents into vectors, store in an index, retrieve top-k candidates by cosine similarity
2. **Reranking Stage (Reranker)**: Score each (query, candidate) pair with the cross-attention reranker for fine-grained relevance

This two-stage approach significantly boosts retrieval accuracy over embedding-only pipelines.

## Architecture Comparison

| Aspect | Qwen3-VL-Embedding | Qwen3-VL-Reranker |
|--------|-------------------|-------------------|
| Core Function | Semantic representation, embedding generation | Relevance scoring, pointwise reranking |
| Input | Single or mixed modalities | (Query, Document) pair |
| Architecture | Dual-Tower | Single-Tower with Cross-Attention |
| Mechanism | Efficient independent encoding | Deep inter-modal interaction |
| Output | Semantic vector | Relevance score |

The reranker uses a **single-tower architecture** with cross-attention mechanisms for deeper, finer-grained inter-modal interaction and information fusion. It expresses relevance by predicting the generation probability of special tokens (`yes` and `no`).

## Reranker Usage

### Model Initialization

```python
from src.models.qwen3_vl_reranker import Qwen3VLReranker

reranker = Qwen3VLReranker(
    model_name_or_path="./models/Qwen3-VL-Reranker-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)
```

### Scoring Query-Document Pairs

```python
inputs = {
    "instruction": "Retrieve images or text relevant to the user's query.",
    "query": {"text": "A woman playing with her dog on a beach at sunset."},
    "documents": [
        {"text": "A woman shares a joyful moment with her golden retriever..."},
        {"image": "photo.jpg"},
        {"text": "A woman shares a joyful moment...",
         "image": "photo.jpg"}
    ],
    "fps": 1.0,
    "max_frames": 64
}

scores = reranker.process(inputs)
# Returns relevance scores for each document
```

### Input Format

The reranking model accepts a dictionary with:

- `query`: A multimodal object (text, image, video, or mixed)
- `documents`: A list of multimodal objects to score against the query
- `instruction`: Task description (optional, default: `"Represent the user's input"`)
- `fps` / `max_frames`: Video sampling settings (optional)

## Complete Two-Stage Pipeline

```python
import numpy as np
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder
from src.models.qwen3_vl_reranker import Qwen3VLReranker

# Initialize models
embedder = Qwen3VLEmbedder(model_name_or_path="./models/Qwen3-VL-Embedding-2B")
reranker = Qwen3VLReranker(model_name_or_path="./models/Qwen3-VL-Reranker-2B")

# Step 1: Embedding-based recall
query = "Show me images of beach sunsets"
query_emb = embedder.process([{
    "text": query,
    "instruction": "Retrieve relevant content for the user's query."
}])

# Encode document corpus (pre-computed in production)
doc_embeddings = embedder.process([{"text": d} for d in documents])

# Retrieve top-50 candidates by cosine similarity
similarities = query_emb @ doc_embeddings.T
top_50_indices = np.argsort(similarities)[::-1][:50]
candidates = [documents[i] for i in top_50_indices]

# Step 2: Reranking for precision
rerank_inputs = {
    "instruction": "Retrieve relevant content for the user's query.",
    "query": {"text": query},
    "documents": [{"text": d} for d in candidates],
}
rerank_scores = reranker.process(rerank_inputs)

# Select top-5 by reranker score
final_indices = np.argsort(rerank_scores)[::-1][:5]
final_results = [candidates[i] for i in final_indices]
```

## Reranker Performance

The reranker consistently outperforms the base embedding model on retrieval tasks:

| Model | Size | MMEB-v2 Retrieval Avg | MMTEB Retrieval |
|-------|------|----------------------|-----------------|
| Qwen3-VL-Embedding-2B | 2B | 73.4 | 68.1 |
| Qwen3-VL-Reranker-2B | 2B | 75.2 | 70.0 |
| Qwen3-VL-Reranker-8B | 8B | **79.2** | **74.9** |

On visual document retrieval (JinaVDR and ViDoRe v3), the 8B reranker achieves 83.6 and 66.7 respectively, outperforming all baselines.

## Model Availability

| Model | Hugging Face | ModelScope |
|-------|-------------|------------|
| Qwen3-VL-Reranker-2B | [Link](https://huggingface.co/Qwen/Qwen3-VL-Reranker-2B) | [Link](https://modelscope.cn/models/qwen/Qwen3-VL-Reranker-2B) |
| Qwen3-VL-Reranker-8B | [Link](https://huggingface.co/Qwen/Qwen3-VL-Reranker-8B) | [Link](https://modelscope.cn/models/qwen/Qwen3-VL-Reranker-8B) |
