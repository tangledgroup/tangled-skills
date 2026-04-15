# Clustering and Similarity Tasks

Using Qwen3 Embedding for document clustering, duplicate detection, and semantic text similarity.

## Document Clustering

### K-Means Clustering

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Documents to cluster
documents = [
    "Python is great for data science",
    "Machine learning with TensorFlow",
    "Java enterprise application development",
    "The weather is sunny today",
    "Deep learning neural networks",
    "Spring framework for Java",
    "Sports news: team wins championship",
    "Pandas library for data analysis"
]

# Generate embeddings
embeddings = model.encode(documents)

# K-Means clustering
num_clusters = 3
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(embeddings)

# Display clusters
for cluster_id in range(num_clusters):
    cluster_docs = [documents[i] for i in range(len(documents)) if cluster_labels[i] == cluster_id]
    print(f"\nCluster {cluster_id} ({len(cluster_docs)} docs):")
    for doc in cluster_docs:
        print(f"  - {doc}")
```

### Determining Optimal Number of Clusters

```python
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer

# Generate embeddings
embeddings = model.encode(documents)

# Elbow method
elbow = KElbowVisualizer(KMeans(random_state=42), k=(2, 10))
elbow.fit(embeddings)
elbow.show()

# Silhouette analysis
from sklearn.metrics import silhouette_score

silhouette_scores = []
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    score = silhouette_score(embeddings, labels)
    silhouette_scores.append(score)
    print(f"k={k}: silhouette={score:.3f}")

best_k = np.argmax(silhouette_scores) + 2
print(f"Optimal clusters: {best_k}")
```

### Hierarchical Clustering

```python
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch

# Generate embeddings
embeddings = model.encode(documents)

# Hierarchical clustering
clusterer = AgglomerativeClustering(n_clusters=3, linkage='ward')
labels = clusterer.fit_predict(embeddings)

# Visualize dendrogram
dendrogram = sch.dendrogram(sch.linkage(embeddings, method='ward'))
```

## Duplicate Detection

### Finding Similar Documents

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

documents = [
    "The cat sits on the mat.",
    "A cat is sitting on a mat.",  # Near duplicate
    "Dogs are playing in the park.",
    "Canines playing outdoors.",  # Semantic similar but not duplicate
    "The weather is nice today."
]

# Generate embeddings
embeddings = model.encode(documents, normalize_embeddings=True)

# Compute similarity matrix
similarity_matrix = np.dot(embeddings, embeddings.T)

# Find duplicates (threshold-based)
threshold = 0.85
num_docs = len(documents)

for i in range(num_docs):
    duplicates = []
    for j in range(i + 1, num_docs):
        if similarity_matrix[i][j] > threshold:
            duplicates.append((j, similarity_matrix[i][j]))
    
    if duplicates:
        print(f"Document {i}: '{documents[i]}'")
        for dup_idx, sim in duplicates:
            print(f"  → Duplicate {dup_idx} (sim={sim:.3f}): '{documents[dup_idx]}'")
```

### Deduplication Pipeline

```python
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

class DocumentDeduplicator:
    def __init__(self, threshold=0.9):
        self.model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
        self.threshold = threshold
        self.documents = []
        self.embeddings = None
    
    def deduplicate(self, documents):
        """Remove duplicate documents"""
        self.documents = documents
        
        # Generate embeddings
        self.embeddings = self.model.encode(documents, normalize_embeddings=True)
        
        # Find nearest neighbors
        nn = NearestNeighbors(n_neighbors=len(documents), metric='cosine')
        nn.fit(self.embeddings)
        
        distances, indices = nn.kneighbors(self.embeddings)
        
        # Mark duplicates
        is_duplicate = [False] * len(documents)
        unique_indices = []
        
        for i in range(len(documents)):
            if is_duplicate[i]:
                continue
            
            unique_indices.append(i)
            
            # Mark similar documents as duplicates
            for j, (dist, idx) in enumerate(zip(distances[i], indices[i])):
                if idx != i and (1 - dist) > self.threshold:
                    is_duplicate[idx] = True
        
        # Return unique documents
        unique_docs = [documents[i] for i in unique_indices]
        duplicate_info = [(i, documents[i]) for i in range(len(documents)) if is_duplicate[i]]
        
        return unique_docs, duplicate_info

# Usage
deduplicator = DocumentDeduplicator(threshold=0.9)
unique_docs, duplicates = deduplicator.deduplicate(large_document_collection)

print(f"Original: {len(large_document_collection)} docs")
print(f"Unique: {len(unique_docs)} docs")
print(f"Removed {len(duplicates)} duplicates")
```

## Semantic Text Similarity (STS)

### Pairwise Similarity Scoring

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Sentence pairs to score
pairs = [
    ("The cat sits on the mat.", "A feline is resting on a rug."),  # High similarity
    ("I love programming in Python.", "Java is my favorite language."),  # Low similarity
    ("The weather is sunny today.", "It's a beautiful day outside."),  # Medium similarity
]

# Compute similarities
for sent1, sent2 in pairs:
    emb1 = model.encode(sent1)
    emb2 = model.encode(sent2)
    
    # Cosine similarity
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    print(f"Pair: ({sent1[:30]}..., {sent2[:30]}...)")
    print(f"Similarity: {similarity:.3f}")
    print()
```

### STS Evaluation on Benchmark Dataset

```python
from sentence_transformers import SentenceTransformer, evaluation
import pandas as pd

# Load STS benchmark dataset
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Example: Custom STS dataset
sts_data = pd.DataFrame({
    'sentence1': [
        "The cat sits on the mat.",
        "A machine learns from data.",
        "Weather is sunny today."
    ],
    'sentence2': [
        "A feline rests on a rug.",
        "An algorithm trains on examples.",
        "It's raining outside."
    ],
    'score': [0.9, 0.8, 0.3]  # Human similarity scores (0-1)
})

# Compute similarities
embeddings1 = model.encode(list(sts_data['sentence1']))
embeddings2 = model.encode(list(sts_data['sentence2']))

predicted_scores = []
for emb1, emb2 in zip(embeddings1, embeddings2):
    sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    predicted_scores.append(sim)

# Correlation with human scores
from scipy.stats import spearmanr, pearsonr

spearman_corr, _ = spearmanr(predicted_scores, sts_data['score'])
pearson_corr, _ = pearsonr(predicted_scores, sts_data['score'])

print(f"Spearman correlation: {spearman_corr:.3f}")
print(f"Pearson correlation: {pearson_corr:.3f}")
```

### Paraphrase Detection

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

def is_paraphrase(sent1, sent2, threshold=0.8):
    """Detect if two sentences are paraphrases"""
    emb1 = model.encode(sent1)
    emb2 = model.encode(sent2)
    
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    return similarity > threshold, similarity

# Test cases
test_pairs = [
    ("What's the weather?", "How's the weather today?"),  # Paraphrase
    ("I'm going to the store.", "I need to buy groceries."),  # Related but not paraphrase
    ("Hello!", "Hi there!"),  # Paraphrase
]

for sent1, sent2 in test_pairs:
    is_para, sim = is_paraphrase(sent1, sent2)
    label = "Paraphrase" if is_para else "Not paraphrase"
    print(f"{label} (sim={sim:.3f}):")
    print(f"  '{sent1}'")
    print(f"  '{sent2}'")
    print()
```

## Topic Modeling

### LDA with Embedding Initialization

```python
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

documents = [...]  # Large document collection
embeddings = model.encode(documents)

# Reduce dimensions for visualization
pca = PCA(n_components=2)
reduced = pca.fit_transform(embeddings)

# Gaussian Mixture Model for topic discovery
n_topics = 5
gmm = GaussianMixture(n_components=n_topics, random_state=42)
topic_labels = gmm.fit_predict(embeddings)

# Display topic representatives
for topic_id in range(n_topics):
    topic_docs = [documents[i] for i in range(len(documents)) if topic_labels[i] == topic_id]
    
    print(f"\nTopic {topic_id} ({len(topic_docs)} docs):")
    for doc in topic_docs[:3]:
        print(f"  - {doc[:80]}...")
```

## See Also

- [`references/03-embedding-generation.md`](03-embedding-generation.md) - Encoding details
- [`references/06-semantic-search.md`](06-semantic-search.md) - Search applications
- [`references/12-benchmarks.md`](12-benchmarks.md) - Performance evaluation
