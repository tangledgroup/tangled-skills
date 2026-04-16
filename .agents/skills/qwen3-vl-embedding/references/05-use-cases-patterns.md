# Use Cases & Application Patterns

## 1. Multimodal RAG Pipeline

End-to-end retrieval-augmented generation combining embedding, reranking, and LLM:

```python
import torch
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder
from src.models.qwen3_vl_reranker import Qwen3VLReranker

# Stage 1: Embedding-based recall (fast)
embedder = Qwen3VLEmbedder(model_name_or_path="Qwen/Qwen3-VL-Embedding-2B")

documents = [
    {"text": "Image of a beach sunset with people",
     "image": "./docs/beach_sunset.jpg"},
    {"text": "Product description for wireless headphones",
     "image": "./products/headphones.png"},
    {"text": "Tutorial on making pasta from scratch",
     "video": "./tutorials/pasta.mp4"},
]

query = {"text": "I want to cook Italian food at home"}
doc_embeddings = embedder.process(documents)
query_embedding = embedder.process([query])

# Find top-k most similar documents (cosine similarity)
similarities = (doc_embeddings @ query_embedding.T).squeeze()
top_k_indices = torch.topk(similarities, k=3).indices

# Stage 2: Reranking for precision
reranker = Qwen3VLReranker(model_name_or_path="Qwen/Qwen3-VL-Reranker-2B")

reranked_scores = reranker.process({
    "instruction": "Retrieve cooking-related content.",
    "query": query,
    "documents": [documents[i] for i in top_k_indices],
})

# Stage 3: Pass top result to LLM for generation
```

## 2. Image Search Engine

Build a search engine over an image collection:

```python
import numpy as np
from PIL import Image
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder

model = Qwen3VLEmbedder(model_name_or_path="Qwen/Qwen3-VL-Embedding-2B")

# Build index
image_paths = ["./photos/photo1.jpg", "./photos/photo2.jpg", ...]
image_embeddings = model.process([{"image": p} for p in image_paths])
index_matrix = image_embeddings.numpy()  # Pre-compute for vector DB

def search_images(query_text, top_k=5):
    """Search images by text description."""
    query_emb = model.process([{"text": query_text}]).numpy()
    similarities = index_matrix @ query_emb.T
    results = np.argsort(similarities.flatten())[::-1][:top_k]
    return [(image_paths[i], similarities[i].item()) for i in results]

# Usage: find similar images to a text description
results = search_images("sunset at the beach with people")
```

## 3. Video Content Indexing

Index videos by their visual content and text descriptions:

```python
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder

model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    fps=1.0,       # Sample 1 frame per second
    max_frames=64  # Max 64 frames per video
)

videos = [
    {"path": "./videos/interview.mp4", "description": "Tech CEO interview"},
    {"path": "./videos/tutorial.mp4", "description": "Python tutorial"},
]

# Create embeddings for videos
video_embeddings = model.process([
    {"text": v["description"], "video": v["path"]}
    for v in videos
])

# Search by query text
query_emb = model.process([{"text": "programming tutorial"}])
similarities = video_embeddings @ query_emb.T
best_match_idx = torch.argmax(similarities).item()
```

## 4. Multimodal Clustering

Cluster images, text, and videos together:

```python
import numpy as np
from sklearn.cluster import KMeans
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder

model = Qwen3VLEmbedder(model_name_or_path="Qwen/Qwen3-VL-Embedding-8B")

# Mixed modality dataset
items = [
    {"text": "A red sports car on a highway", "image": "./car1.jpg"},
    {"text": "A blue sedan in traffic", "image": "./car2.jpg"},
    {"text": "Mountain landscape at dawn", "image": "./mountain.jpg"},
    {"text": "City skyline at night", "image": "./city.jpg"},
]

embeddings = model.process(items, normalize=True)
X = embeddings.numpy()

# Cluster into groups
kmeans = KMeans(n_clusters=2, random_state=42)
labels = kmeans.fit_predict(X)

for i, (item, label) in enumerate(zip(items, labels)):
    print(f"Item {i}: {item.get('text', 'image')} -> Cluster {label}")
```

## 5. Screenshot/Document Search

Search through screenshots and document images:

```python
model = Qwen3VLEmbedder(model_name_or_path="Qwen/Qwen3-VL-Embedding-2B")

screenshots = [
    {"text": "Settings page with dark mode toggle", "image": "./screenshots/settings.png"},
    {"text": "Dashboard showing analytics chart", "image": "./screenshots/dashboard.png"},
]

# Search for UI elements by description
query = {"text": "Where is the dark mode setting?"}
doc_embeddings = model.process(screenshots)
query_embedding = model.process([query])

similarities = (doc_embeddings @ query_embedding.T).squeeze()
best_match_idx = torch.argmax(similarities).item()
```

## 6. Task-Specific Embeddings via Instructions

Customize embedding behavior with instructions:

```python
# E-commerce product search
product_docs = [
    {"text": "Wireless Bluetooth headphones, noise-cancelling",
     "instruction": "Find products matching customer queries for e-commerce."},
    {"text": "USB-C charging cable, 2m length",
     "instruction": "Find products matching customer queries for e-commerce."},
]

# Academic paper search
paper_docs = [
    {"text": "Attention mechanisms in transformer architectures",
     "instruction": "Retrieve academic papers on machine learning topics."},
]

# Different instructions create different embedding spaces
```

## 7. Memory-Efficient Deployment with MRL

Use smaller dimensions for reduced storage:

```python
model = Qwen3VLEmbedder(model_name_or_path="Qwen/Qwen3-VL-Embedding-2B")

inputs = [{"text": "Sample text"}]
full_emb = model.process(inputs)  # Shape: (1, 2048)

# Truncate to smaller dimension for storage efficiency
small_dim = 128
compressed = full_emb[:, :small_dim]  # Shape: (1, 128)

# Trade-off: smaller dim = less storage, slightly lower accuracy
# Test with your data to find optimal dimension
```

## 8. Cross-Lingual Search

Search across languages using the 30+ language support:

```python
model = Qwen3VLEmbedder(model_name_or_path="Qwen/Qwen3-VL-Embedding-2B")

# Multilingual document collection
documents = [
    {"text": "Bienvenidos a nuestra tienda en línea", "image": "./store_es.jpg"},   # Spanish
    {"text": "Willkommen in unserem Online-Shop", "image": "./store_de.jpg"},       # German
    {"text": "Welcome to our online store", "image": "./store_en.jpg"},              # English
]

# Search from any language
query_fr = [{"text": "Boutique en ligne de chaussures"}]  # French: "Online shoe store"
query_jp = [{"text": "オンラインストアの靴"}]              # Japanese: "Online store shoes"

for query in [query_fr, query_jp]:
    doc_emb = model.process(documents)
    q_emb = model.process(query)
    sims = (doc_emb @ q_emb.T).squeeze()
    best = torch.argmax(sims).item()
    print(f"Best match for {query[0]['text']}: {documents[best]}")
```

## 9. Combined Text+Image Retrieval

Retrieve documents that have both visual and textual relevance:

```python
model = Qwen3VLEmbedder(model_name_or_path="Qwen/Qwen3-VL-Embedding-2B")

# Documents with mixed content
documents = [
    {"text": "Recipe for spaghetti carbonara",
     "image": "./recipes/carbonara.jpg"},
    {"text": "Guide to Tokyo restaurants",
     "image": "./tokyo_map.png"},
]

query = {
    "text": "Italian pasta recipe with eggs and bacon",
    "image": "./reference_dish.jpg"  # Reference image of desired dish
}

doc_emb = model.process(documents)
q_emb = model.process([query])
similarity = (doc_emb @ q_emb.T).squeeze()
```

## Application Decision Matrix

| Scenario | Model | API | Notes |
|----------|-------|-----|-------|
| High-accuracy search | 8B | Transformers or vLLM | Best quality, higher cost |
| Real-time app | 2B | Transformers | Low latency |
| Batch processing | 2B/8B | vLLM | Optimized for throughput |
| Edge device | 2B + INT4 | Transformers | Quantized deployment |
| Text-only retrieval | Qwen3-Embedding-8B | - | Better text scores than VL |
| Video search | 2B/8B | Transformers | Use fps/max_frames tuning |

## References

- Multimodal RAG Example: https://github.com/QwenLM/Qwen3-VL-Embedding/blob/main/examples/Qwen3VL_Multimodal_RAG.ipynb
- Embedding Examples: https://github.com/QwenLM/Qwen3-VL-Embedding/blob/main/examples/embedding.ipynb
- Reranker Examples: https://github.com/QwenLM/Qwen3-VL-Embedding/blob/main/examples/reranker.ipynb
