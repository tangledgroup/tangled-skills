# Cross Encoder Usage

Comprehensive guide to using `CrossEncoder` class for reranking and pair scoring.

## Understanding Cross Encoders

### Bi-Encoder vs Cross-Encoder

| Aspect | Bi-Encoder (SentenceTransformer) | Cross-Encoder |
|--------|----------------------------------|---------------|
| **Input** | Single text | Text pairs |
| **Output** | Embedding vector | Scalar score |
| **Speed** | Fast (independent encoding) | Slow (joint encoding) |
| **Accuracy** | Good | Excellent |
| **Use Case** | Retrieval from large corpus | Reranking top-k results |

### When to Use Cross Encoders

- **Reranking**: Score top-50/100 results from bi-encoder retrieval
- **Pair Classification**: Determine if two texts are similar/duplicates
- **NLI Tasks**: Entailment, contradiction, neutral classification
- **Final Ranking**: When accuracy matters more than speed

## Basic Usage

### Load and Score Pairs

```python
from sentence_transformers import CrossEncoder

# Load pretrained model
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

# Prepare pairs to score
pairs = [
    ("How many people live in Berlin?", "Berlin had a population of 3,520,031."),
    ("How many people live in Berlin?", "Berlin has 135 million visitors yearly."),
    ("How many people live in Berlin?", "Berliners love sports clubs."),
]

# Predict scores (raw logit values)
scores = model.predict(pairs)
print(scores)  # [8.607139, 5.506266, 6.352977]

# Convert to probabilities (softmax)
probabilities = model.predict(pairs, apply_softmax=True)
print(probabilities)  # [0.68, 0.18, 0.14]
```

### Batch Scoring

```python
# Score multiple pairs efficiently
pairs = [(query, doc) for query in queries for doc in documents]

scores = model.predict(
    pairs,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True
)
```

## Ranking API

### Basic Ranking

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

query = "What is machine learning?"
documents = [
    "Machine learning is a subset of AI that enables systems to learn.",
    "Deep learning uses neural networks with many layers.",
    "Python is a popular programming language.",
    "Supervised learning requires labeled training data.",
]

# Rank documents for query
ranks = model.rank(query, documents)

print(ranks)
# [
#   {'corpus_id': 0, 'score': 8.45},
#   {'corpus_id': 3, 'score': 7.23},
#   {'corpus_id': 1, 'score': 6.89},
#   {'corpus_id': 2, 'score': 3.12}
# ]
```

### Ranking with Options

```python
# Return top-k results only
ranks = model.rank(query, documents, top_k=2)

# Return documents in results
ranks = model.rank(query, documents, return_documents=True)
for rank in ranks:
    print(f"#{rank['corpus_id']} ({rank['score']:.2f}): {rank['text'][:50]}...")

# Apply softmax for probabilities
ranks = model.rank(query, documents, apply_softmax=True)

# Use specific device
ranks = model.rank(query, documents, device="cuda")
```

## Model Types

### Classification Models

For multi-class classification tasks:

```python
from sentence_transformers import CrossEncoder

# Load NLI model (entailment, contradiction, neutral)
model = CrossEncoder("cross-encoder/nli-deberta-v3-base")

pairs = [
    ("The cat is on the mat", "There is a feline on the floor"),  # Entailment
    ("The cat is on the mat", "The dog is in the yard"),          # Neutral
    ("The cat is on the mat", "The mat is under the dog"),        # Contradiction
]

# Get class probabilities
scores = model.predict(pairs, apply_softmax=True)
print(scores.shape)  # (3, 3) - 3 classes

# Get class labels
labels = ["entailment", "contradiction", "neutral"]
for pair, score in zip(pairs, scores):
    pred_idx = int(np.argmax(score))
    print(f"{pair[0][:30]}... -> {labels[pred_idx]} ({score[pred_idx]:.3f})")
```

### Binary Classification

```python
from sentence_transformers import CrossEncoder

# Load duplicate question model
model = CrossEncoder("cross-encoder/quora-question-pairs-MiniLM-L6-cos-v1")

pairs = [
    ("How do I reset my password?", "What if I forgot my password?"),
    ("How do I reset my password?", "How do I change my profile picture?"),
]

# Binary classification (duplicate vs not duplicate)
scores = model.predict(pairs, apply_softmax=True)
print(scores)  # [[0.92, 0.08], [0.15, 0.85]]

# Get predictions
for pair, score in zip(pairs, scores):
    is_duplicate = score[0] > 0.5
    print(f"Duplicate: {is_duplicate} (confidence: {max(score):.3f})")
```

## Advanced Usage

### Custom Max Length

```python
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

# Set maximum sequence length
model.max_seq_length = 512  # Default is typically 256 or 512

# Or set during initialization
model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L6-v2",
    max_seq_length=384
)

# Score with custom length
scores = model.predict(pairs, truncate=True)
```

### Multi-Process Scoring

```python
# For very large number of pairs
scores = model.predict(
    pairs,
    batch_size=32,
    show_progress_bar=True,
    num_workers=4  # Use multiple CPU cores
)
```

### Return Attention Weights

```python
# Get attention weights for interpretability
outputs = model.predict(
    pairs,
    return_attention=True
)

scores = outputs['scores']
attention = outputs['attention']  # Attention weights tensor
```

## Retrieve and Rerank Pipeline

Complete example combining bi-encoder retrieval with cross-encoder reranking:

```python
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# Step 1: Initialize models
retriever = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

# Step 2: Prepare corpus
corpus = [
    "Machine learning is a subset of artificial intelligence.",
    "Python is widely used for data science and ML.",
    "Neural networks are inspired by biological brains.",
    "The weather today is sunny and warm.",
    "Deep learning uses multiple hidden layers.",
    # ... thousands more documents
]

# Step 3: Encode corpus (do this once, cache if static)
corpus_embeddings = retriever.encode(
    corpus,
    batch_size=64,
    normalize_embeddings=True,
    show_progress_bar=True
)

# Step 4: Retrieve top-50 for query
query = "How does deep learning work?"
query_embedding = retriever.encode(query, normalize_embeddings=True)

# Cosine similarity (dot product since normalized)
similarities = corpus_embeddings @ query_embedding
top_50_indices = similarities.argsort()[-50:][::-1]
top_50_docs = [corpus[i] for i in top_50_indices]

print("Top 5 by bi-encoder:")
for idx, score in zip(top_50_indices[:5], similarities[top_50_indices][:5]):
    print(f"  {score:.3f} - {corpus[idx][:50]}...")

# Step 5: Rerank top-50 with cross-encoder
pairs = [(query, doc) for doc in top_50_docs]
ranks = reranker.rank(query, top_50_docs, top_k=10)

print("\nTop 5 after reranking:")
for rank in ranks[:5]:
    print(f"  {rank['score']:.3f} - {rank['text'][:50]}...")
```

## Training Cross Encoders

See [`references/06-training-overview.md`](references/06-training-overview.md) for detailed training guide.

Basic example:

```python
from sentence_transformers import CrossEncoder, InputExample
from sentence_transformers.training_args import CrossEncoderTrainingArguments
from sentence_transformers.trainer import CrossEncoderTrainer

# Prepare training data
train_examples = [
    InputExample(texts=["query1", "doc1"], label=1.0),  # Relevant
    InputExample(texts=["query1", "doc2"], label=0.0),  # Not relevant
    # ... more examples
]

# Initialize model
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

# Define training arguments
train_args = CrossEncoderTrainingArguments(
    output_dir="./reranker-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
)

# Train
trainer = CrossEncoderTrainer(
    model=model,
    args=train_args,
    train_dataset=train_examples
)

trainer.train()
```

## Performance Tips

1. **Use for reranking only**: Don't score entire corpus with cross-encoder (too slow)
2. **Bi-encoder first**: Retrieve top-50/100 with SentenceTransformer, then rerank
3. **Batch processing**: Use `batch_size` parameter for efficient scoring
4. **GPU acceleration**: Cross encoders benefit significantly from GPU
5. **Cache results**: Store reranking results if queries repeat

## Common Models

| Model | Task | Labels | Best For |
|-------|------|--------|----------|
| `cross-encoder/ms-marco-MiniLM-L6-v2` | Retrieval scoring | Regression | Passage reranking |
| `cross-encoder/quora-question-pairs-MiniLM-L6-cos-v1` | Duplicate detection | Binary (0/1) | Question deduplication |
| `cross-encoder/nli-deberta-v3-base` | Natural Language Inference | 3-class | Entailment tasks |
| `cross-encoder/stsb-distilroberta-base` | Semantic similarity | Regression | STS scoring |
| `BAAI/bge-reranker-base` | General reranking | Binary/Regression | High-quality reranking |

## Troubleshooting

### Issue: Scores are very large/small

**Solution**: Use `apply_softmax=True` to normalize scores to [0, 1] range

### Issue: Model too slow

**Solution**: 
- Reduce `max_seq_length` if documents are long
- Use smaller model (MiniLM instead of DeBERTa)
- Increase `batch_size` for better GPU utilization

### Issue: Out of memory

**Solution**: Reduce `batch_size` or use CPU (`device="cpu"`)
