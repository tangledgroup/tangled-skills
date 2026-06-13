# Usage Patterns

## Text Classification

Classify text by computing embeddings for labels and queries, then finding nearest label:

```python
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder
import numpy as np

model = Qwen3VLEmbedder(model_name_or_path="./models/Qwen3-VL-Embedding-2B")

# Encode label corpus
labels = ["World", "Sports", "Business", "Sci/Tech"]
label_embeddings = model.process([{"text": l} for l in labels])

# Encode query with task-specific instruction
query = {"text": "Stock markets rally on positive economic data",
         "instruction": "Classify the news article."}
query_embedding = model.process([query])

# Find nearest label
similarities = query_embedding @ label_embeddings.T
predicted_label = labels[np.argmax(similarities)]
```

## Text Question Answering

Retrieve passages that answer a question:

```python
# Encode passage corpus
corpus_embeddings = model.process([{"text": p} for p in passages])

# Encode question with instruction
query_embedding = model.process([{
    "text": "What year was the treaty signed?",
    "instruction": "Retrieve passages that answer this question."
}])

# Find most relevant passage
similarities = query_embedding @ corpus_embeddings.T
top_idx = np.argmax(similarities)
```

## Text Retrieval

Passage retrieval for search queries:

```python
# Encode document corpus
doc_embeddings = model.process([{"text": d} for d in documents])

# Encode search query
query_embedding = model.process([{
    "text": "machine learning applications in healthcare",
    "instruction": "Retrieve relevant passages."
}])

# Rank by similarity
scores = (query_embedding @ doc_embeddings.T).flatten()
top_results = np.argsort(scores)[::-1][:10]
```

## Image Classification

Classify images using text label embeddings:

```python
# Encode text labels
labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog']
label_embeddings = model.process([{"text": l} for l in labels])

# Encode image with classification instruction
from PIL import Image
img = Image.open("photo.jpg")
image_embedding = model.process([{
    "image": img,
    "instruction": "Classify the object in this image."
}])

# Find nearest label
similarities = image_embedding @ label_embeddings.T
predicted_label = labels[np.argmax(similarities)]
```

## Image Question Answering

Find answers to questions about images:

```python
# Encode answer corpus
answer_embeddings = model.process([{"text": a} for a in candidate_answers])

# Encode image + question query
query_embedding = model.process([{
    "image": "photo.jpg",
    "text": "What color is the car?",
    "instruction": "Find the answer to this question about the image."
}])

# Retrieve best answer
similarities = query_embedding @ answer_embeddings.T
best_answer = candidate_answers[np.argmax(similarities)]
```

## Image Retrieval

Text-to-image retrieval:

```python
# Encode image corpus
image_corpus = ["img1.jpg", "img2.jpg", "img3.jpg"]
image_embeddings = model.process([{"image": img} for img in image_corpus])

# Encode text query
query_embedding = model.process([{
    "text": "a sunset over the ocean with palm trees",
    "instruction": "Find images matching this description."
}])

# Find most similar images
similarities = query_embedding @ image_embeddings.T
top_indices = np.argsort(similarities)[::-1][:5]
```

## Multimodal RAG Pipeline

End-to-end retrieval-augmented generation with visual documents:

```python
# 1. Build embedding index from mixed corpus
corpus = [
    {"text": "Section 1: Introduction to the product..."},
    {"image": "diagram.png"},
    {"text": "Table of specifications", "image": "spec_table.jpg"},
    {"video": "demo.mp4", "fps": 1.0, "max_frames": 32},
]
corpus_embeddings = model.process(corpus)

# 2. User query (can be text, image, or mixed)
query_embedding = model.process([{
    "text": "Show me the product diagram and specifications",
    "instruction": "Retrieve relevant content for the user's query."
}])

# 3. Retrieve top-k results
similarities = query_embedding @ corpus_embeddings.T
top_k_indices = np.argsort(similarities)[::-1][:5]
retrieved_items = [corpus[i] for i in top_k_indices]

# 4. Pass retrieved content to a generative model (e.g., Qwen3-VL)
```

## Matryoshka Dimension Truncation

Use lower dimensions for storage efficiency:

```python
# Full embedding (2048 for 2B, 4096 for 8B)
full_embeddings = model.process(inputs)

# Truncate to desired dimension
dim_256 = full_embeddings[:, :256]
dim_128 = full_embeddings[:, :128]
dim_64 = full_embeddings[:, :64]

# Compute similarity at reduced dimension
similarity_256 = dim_256 @ dim_256.T
```

## vLLM Inference

For production deployment, use vLLM (requires >= 0.14.0):

```python
# See examples/embedding_vllm.ipynb in the repository for complete examples
from vllm import LLM, SamplingParams

llm = LLM(model="./models/Qwen3-VL-Embedding-2B", max_model_len=32768)
# Process inputs through vLLM for accelerated inference
```

## Instruction Templates

Recommended instructions by task type:

| Task | Instruction Template |
|------|---------------------|
| Classification | `"Classify the [content type]." ` |
| QA | `"Retrieve passages that answer this question."` |
| Retrieval | `"Retrieve relevant passages."` or `"Find images matching this description."` |
| Clustering | `"Represent the user's input"` (default) |
| VQA | `"Find the answer to this question about the image."` |

Custom instructions tailored to your specific domain and task typically yield the best results.
