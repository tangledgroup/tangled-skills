# Applications

Comprehensive guide to common applications of Sentence Transformers.

## Semantic Search

### Basic Implementation

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load model optimized for retrieval
model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

# Prepare corpus
corpus = [
    "How to install Python on Windows?",
    "Python virtual environment tutorial",
    "Best practices for Python code",
    "Machine learning with Python and scikit-learn",
    "Web scraping using Python BeautifulSoup",
]

# Encode corpus (do once, cache results)
corpus_embeddings = model.encode(
    corpus,
    batch_size=32,
    normalize_embeddings=True,
    convert_to_numpy=True
)

def search(query, top_k=3):
    """Search for most similar documents"""
    # Encode query
    query_embedding = model.encode(query, normalize_embeddings=True)
    
    # Compute cosine similarity (dot product since normalized)
    similarities = corpus_embeddings @ query_embedding
    
    # Get top-k results
    top_indices = similarities.argsort()[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            'text': corpus[idx],
            'score': float(similarities[idx])
        })
    
    return results

# Search
results = search("How do I set up Python?", top_k=3)
for result in results:
    print(f"{result['score']:.3f} - {result['text']}")
```

### Symmetric vs Asymmetric Search

```python
# Symmetric: Both query and corpus encoded the same way
model_sym = SentenceTransformer("all-MiniLM-L6-v2")

# Asymmetric: Different prompts for query vs corpus (better for search)
model_asym = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

# The asymmetric model was trained specifically for query-document pairs
# and produces better retrieval results
```

### Optimized Search with FAISS

```python
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
corpus = [...]  # Large corpus of documents

# Encode corpus
corpus_embeddings = model.encode(corpus, normalize_embeddings=True, convert_to_numpy=True)

# Build FAISS index for fast ANN search
dimension = corpus_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner product (cosine for normalized)
index.add(corpus_embeddings)

def search_faiss(query, k=10):
    query_embedding = model.encode(query, normalize_embeddings=True)
    
    # ANN search
    distances, indices = index.search(query_embedding.reshape(1, -1), k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            'text': corpus[idx],
            'score': float(dist)
        })
    
    return results
```

## Semantic Textual Similarity (STS)

### Compute STS Scores

```python
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Pairs of sentences to compare
pairs = [
    ("The cat sits on the mat", "A feline is sitting on a rug"),
    ("I love programming", "I hate coding"),
    ("The weather is nice", "It's sunny outside"),
]

# Encode all sentences
all_sentences = [sent for pair in pairs for sent in pair]
embeddings = model.encode(all_sentences, normalize_embeddings=True)

# Compute pairwise similarities
for i, (sent1, sent2) in enumerate(pairs):
    emb1 = embeddings[2*i]
    emb2 = embeddings[2*i + 1]
    
    # Cosine similarity
    cosine_sim = util.cos_sim(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
    
    # Convert to 0-5 scale (common for STS)
    sts_score = (cosine_sim.item() + 1) / 2 * 5
    
    print(f"Pair {i+1}: {sts_score:.2f}/5.0")
    print(f"  '{sent1}'")
    print(f"  '{sent2}'")
```

### Batch STS Computation

```python
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Two sets of sentences
sentences1 = ["Query 1", "Query 2", "Query 3"]
sentences2 = ["Document A", "Document B", "Document C"]

embeddings1 = model.encode(sentences1, normalize_embeddings=True)
embeddings2 = model.encode(sentences2, normalize_embeddings=True)

# Compute all pairwise similarities
similarities = util.cos_sim(embeddings1, embeddings2)

print("Similarity matrix:")
print(similarities.numpy())
# Each row i corresponds to sentences1[i]
# Each column j corresponds to sentences2[j]
```

## Clustering

### K-Means Clustering

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Documents to cluster
documents = [
    "Python is great for data science",
    "Machine learning requires lots of data",
    "The weather is beautiful today",
    "Deep learning uses neural networks",
    "I love playing soccer",
    "Natural language processing is fascinating",
    "Football is the most popular sport",
    "Python pandas library for data analysis",
]

# Encode documents
embeddings = model.encode(documents)

# K-Means clustering
num_clusters = 3
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(embeddings)

# Display clusters
for cluster_id in range(num_clusters):
    cluster_docs = [documents[i] for i in range(len(documents)) if cluster_labels[i] == cluster_id]
    print(f"\nCluster {cluster_id}:")
    for doc in cluster_docs:
        print(f"  - {doc}")
```

### Agglomerative Clustering

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
documents = [...]  # List of documents

embeddings = model.encode(documents)

# Agglomerative clustering
clustering = AgglomerativeClustering(
    n_clusters=5,
    affinity='cosine',  # Use cosine distance
    linkage='average'   # Average linkage
)

cluster_labels = clustering.fit_predict(embeddings)
```

### Hierarchical Clustering with Dendrogram

```python
from sentence_transformers import SentenceTransformer
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

model = SentenceTransformer("all-MiniLM-L6-v2")
documents = [...]

embeddings = model.encode(documents)

# Compute linkage matrix
linkage_matrix = linkage(embeddings, method='average', metric='cosine')

# Plot dendrogram
plt.figure(figsize=(10, 7))
dendrogram(linkage_matrix, labels=documents, leaf_rotation=90)
plt.title('Document Clustering Dendrogram')
plt.xlabel('Document Index')
plt.ylabel('Distance')
plt.tight_layout()
plt.show()
```

## Paraphrase Mining

### Find Similar Pairs

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

# Large set of sentences
sentences = [
    "How do I install Python?",
    "What is the best way to learn programming?",
    "Python installation guide",
    "The weather is nice today",
    "How can I set up Python on my computer?",
    "Programming tutorials for beginners",
    "It's sunny outside",
    "Steps to install Python",
]

# Encode all sentences
embeddings = model.encode(sentences, normalize_embeddings=True)

# Mine paraphrases (pairs with high similarity)
paraphrase_pairs = util.paraphrase_mining(
    embeddings,
    threshold=0.7  # Minimum cosine similarity
)

print(f"Found {len(paraphrase_pairs)} paraphrase pairs:")
for idx1, idx2, score in paraphrase_pairs:
    print(f"\n{score:.3f}:")
    print(f"  '{sentences[idx1]}'")
    print(f"  '{sentences[idx2]}'")
```

### Paraphrase Mining with Multiple Negatives

```python
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [...]  # Large corpus
embeddings = model.encode(sentences, normalize_embeddings=True)

# For each sentence, find top-k most similar (excluding itself)
def mine_paraphrases_topk(embeddings, k=3, threshold=0.7):
    """Find top-k paraphrases for each sentence"""
    similarities = util.cos_sim(embeddings, embeddings)
    np.fill_diagonal(similarities.numpy(), -1)  # Exclude self
    
    results = []
    for i in range(len(embeddings)):
        top_indices = similarities[i].argsort(descending=True)[:k]
        for idx in top_indices:
            score = similarities[i, idx].item()
            if score >= threshold:
                results.append((i, int(idx), score))
    
    return results

paraphrases = mine_paraphrases_topk(embeddings, k=5, threshold=0.75)
```

## Duplicate Detection

### Quora-Style Question Deduplication

```python
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Two-stage approach: fast retrieval + accurate reranking

# Stage 1: Bi-encoder for candidate retrieval
bi_encoder = SentenceTransformer("quora-question-pairs-MiniLM-L6-cos-v1")

questions = [
    "How do I reset my password?",
    "What if I forgot my login credentials?",
    "How to change my profile picture?",
    "Can I update my avatar?",
    "Where is the settings menu?",
]

# Encode all questions
embeddings = bi_encoder.encode(questions, normalize_embeddings=True)

# Find candidate duplicates (threshold-based)
similarity_matrix = cosine_similarity(embeddings)
np.fill_diagonal(similarity_matrix, 0)

candidate_pairs = []
for i in range(len(questions)):
    for j in range(i + 1, len(questions)):
        if similarity_matrix[i, j] > 0.6:  # Candidate threshold
            candidate_pairs.append((i, j))

# Stage 2: Cross-encoder for accurate classification
cross_encoder = CrossEncoder("quora-question-pairs-MiniLM-L6-cos-v1")

print("Duplicate detection results:")
for i, j in candidate_pairs:
    pair = (questions[i], questions[j])
    score = cross_encoder.predict([pair])[0]
    
    is_duplicate = score > 0.5
    print(f"\n{'DUPLICATE' if is_duplicate else 'NOT DUPLICATE'} (confidence: {score:.3f})")
    print(f"  Q1: {questions[i]}")
    print(f"  Q2: {questions[j]}")
```

## Image Search

### Cross-Modal Retrieval

```python
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

# Load multimodal model
model = SentenceTransformer("clip-ViT-B-32")

# Text queries
texts = [
    "A cute cat sitting on a windowsill",
    "Beautiful sunset over the ocean",
    "Person playing guitar",
]

# Images (PIL images or file paths)
images = [
    Image.open("cat.jpg"),
    Image.open("sunset.jpg"),
    Image.open("guitar.jpg"),
]

# Encode both modalities
text_embeddings = model.encode(texts, normalize_embeddings=True)
image_embeddings = model.encode(images, normalize_embeddings=True)

# Cross-modal similarity
similarities = text_embeddings @ image_embeddings.T

print("Text-to-Image Similarity Matrix:")
for i, text in enumerate(texts):
    print(f"\n'{text}':")
    for j, sim in enumerate(similarities[i]):
        print(f"  Image {j+1}: {sim:.3f}")
```

### Image Clustering

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from PIL import Image
import glob

model = SentenceTransformer("clip-ViT-B-32")

# Load images
image_paths = glob.glob("images/*.jpg")
images = [Image.open(path) for path in image_paths]

# Encode images
embeddings = model.encode(images, convert_to_numpy=True)

# Cluster images
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(embeddings)

# Display cluster contents
for cluster_id in range(5):
    cluster_images = [image_paths[i] for i in range(len(image_paths)) if clusters[i] == cluster_id]
    print(f"\nCluster {cluster_id} ({len(cluster_images)} images):")
    for img_path in cluster_images[:3]:
        print(f"  - {img_path}")
```

## Text Classification

### Zero-Shot Classification

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Text to classify
text = "I love this product! It works amazingly well."

# Possible labels
labels = [
    "Very positive",
    "Positive", 
    "Neutral",
    "Negative",
    "Very negative"
]

# Encode text and labels
text_embedding = model.encode(text, normalize_embeddings=True)
label_embeddings = model.encode(labels, normalize_embeddings=True)

# Compute similarities
similarities = label_embeddings @ text_embedding

# Get predicted label
predicted_label = labels[similarities.argmax()]
confidence = similarities.max().item()

print(f"Predicted: {predicted_label} (confidence: {confidence:.3f})")

# Show all scores
for label, sim in zip(labels, similarities):
    print(f"  {label}: {sim:.3f}")
```

### Multi-Label Classification

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

text = "This Python tutorial covers machine learning and data visualization."

# Possible topics
topics = [
    "Python", "Machine Learning", "Data Science", 
    "Web Development", "Database", "Visualization",
    "Deep Learning", "Natural Language Processing"
]

# Encode
text_embedding = model.encode(text, normalize_embeddings=True)
topic_embeddings = model.encode(topics, normalize_embeddings=True)

# Compute similarities
similarities = topic_embeddings @ text_embedding

# Select topics above threshold
threshold = 0.6
predicted_topics = [
    (topic, score.item()) 
    for topic, score in zip(topics, similarities) 
    if score > threshold
]

print(f"Predicted topics (threshold={threshold}):")
for topic, score in sorted(predicted_topics, key=lambda x: x[1], reverse=True):
    print(f"  {topic}: {score:.3f}")
```

## Troubleshooting

### Issue: Poor retrieval quality

**Solutions**:
1. Use asymmetric models (`multi-qa-*`) for query-document search
2. Implement retrieve-and-rerank pipeline
3. Fine-tune on domain-specific data
4. Try hybrid search (dense + sparse)

### Issue: Slow search on large corpus

**Solutions**:
1. Use FAISS or other ANN library
2. Pre-compute and cache corpus embeddings
3. Use smaller models (MiniLM vs base/large)
4. Implement multi-stage retrieval

### Issue: Clustering produces poor results

**Solutions**:
1. Try different number of clusters (use elbow method)
2. Use dimensionality reduction (PCA) before clustering
3. Try different clustering algorithms (HDBSCAN for variable cluster sizes)
4. Normalize embeddings before clustering
