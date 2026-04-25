# Sentence Transformer Usage

Comprehensive guide to using `SentenceTransformer` class for dense embeddings.

## Basic Encoding

### Load and Encode

```python
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode single sentence
sentence = "This is an example sentence"
embedding = model.encode(sentence)
print(embedding.shape)  # (384,)

# Encode multiple sentences
sentences = ["Sentence 1", "Sentence 2", "Sentence 3"]
embeddings = model.encode(sentences)
print(embeddings.shape)  # (3, 384)
```

### Encoding Options

```python
# Normalize embeddings for cosine similarity
embeddings = model.encode(sentences, normalize_embeddings=True)

# Convert to numpy array
embeddings = model.encode(sentences, convert_to_numpy=True)

# Convert to torch tensor
embeddings = model.encode(sentences, convert_to_tensor=True)

# Show progress bar for large batches
embeddings = model.encode(sentences, show_progress_bar=True)

# Use GPU if available
model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
```

### Batch Processing

```python
# Process large datasets in batches
embeddings = model.encode(
    sentences,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True
)

# Multi-process encoding (faster for large datasets)
embeddings = model.encode(
    sentences,
    batch_size=32,
    use_gpu=True,
    multi_process=True,  # Uses all available CPUs
    num_workers=4        # Or specify number of workers
)
```

## Prompt Templates

### What are Prompts?

Prompt templates prepend task-specific instructions to inputs, improving embeddings for specific use cases.

### Built-in Prompts

```python
from sentence_transformers import SentenceTransformer

# Load model with prompt names
model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")

# Use prompt templates
query_embedding = model.encode(
    "What causes lightning?",
    prompt_name="query"  # Prepend: "Represent this sentence for searching:"
)

passage_embedding = model.encode(
    "Lightning is caused by electrical discharge",
    prompt_name="passage"  # Prepend: "Represent this sentence for retrieving:"
)
```

### Custom Prompts

```python
# Define custom prompts
model = SentenceTransformer("all-MiniLM-L6-v2")
model.prompts = {
    "query": "paraphrase: ",
    "passage": "",
    "label": "paraphrase: "
}

# Use custom prompts
query_embedding = model.encode("What is AI?", prompt_name="query")
# Encodes: "paraphrase: What is AI?"
```

### INSTRUCTOR Models

INSTRUCTOR models require instruction prompts for optimal performance:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("hkunlp/instructor-large")

# Encode with task-specific instructions
sentences = ["This is a product review", "The movie was amazing"]
instruction = "represent a sentiment analysis:"

embeddings = model.encode(sentences, prompt=instruction)

# Different instructions for different tasks
embeddings_cls = model.encode(sentences, prompt="represent a text for classification:")
embeddings_sim = model.encode(sentences, prompt="represent a sentence for similarity comparison:")
```

## Similarity Computation

### Built-in Similarity Methods

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode sentences
sentences1 = ["The weather is nice", "It's sunny today"]
sentences2 = ["I love rainy days", "Sunshine is great"]

embeddings1 = model.encode(sentences1, normalize_embeddings=True)
embeddings2 = model.encode(sentences2, normalize_embeddings=True)

# Cosine similarity
cosine_sim = util.cos_sim(embeddings1, embeddings2)
print(cosine_sim)
# tensor([[0.4521, 0.3892],
#         [0.5123, 0.4256]])

# Dot product (requires normalized embeddings)
dot_score = util.dot_score(embeddings1, embeddings2)

# Manhattan distance
manhattan = util.manhattan_distance(embeddings1, embeddings2)

# Euclidean distance
euclidean = util.euclidean_distance(embeddings1, embeddings2)
```

### Manual Similarity Calculation

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Using numpy
embeddings = model.encode(sentences, normalize_embeddings=True, convert_to_numpy=True)
similarities = embeddings @ embeddings.T  # Cosine similarity (normalized)

# Using sklearn
similarities = cosine_similarity(embeddings)
```

## Advanced Encoding

### Multi-GPU Encoding

```python
from sentence_transformers import SentenceTransformer

# Automatically use all available GPUs
model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")

# For very large datasets, use multi-process with GPU
embeddings = model.encode(
    large_corpus,
    batch_size=64,
    multi_process=True,
    use_gpu=True
)
```

### Truncate Long Inputs

```python
# Default max length is 256 tokens
# Customize for your use case
model = SentenceTransformer("all-MiniLM-L6-v2")

# Truncate to 128 tokens
embeddings = model.encode(
    long_documents,
    truncate_to_max_length=True,
    max_length=128
)

# Pad to fixed length (useful for batch processing)
embeddings = model.encode(
    sentences,
    truncate_to_max_length=True,
    pad_to_max_length=True,
    max_length=512
)
```

### Matryoshka Embeddings

Matryoshka embeddings allow truncating to different dimensions while maintaining quality:

```python
from sentence_transformers import SentenceTransformer

# Load Matryoshka model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")

# Encode full dimension (768)
full_embedding = model.encode("Hello world")
print(full_embedding.shape)  # (768,)

# Truncate to different dimensions
embedding_256 = full_embedding[:256]
embedding_512 = full_embedding[:512]
embedding_1024 = full_embedding[:1024]  # If model supports

# All truncated versions maintain semantic quality
```

## Model Configuration

### Check Model Properties

```python
model = SentenceTransformer("all-MiniLM-L6-v2")

# Get embedding dimension
print(model.get_sentence_embedding_dimension())  # 384

# Check if model has prompts
print(model.prompts)  # {} or dict of prompt names

# Check device
print(model.device)  # cpu or cuda:X

# Get model modules
for module in model._modules:
    print(module)
```

### Save and Load Models

```python
# Save model to disk
model.save("./my-saved-model")

# Load from disk
model = SentenceTransformer("./my-saved-model")

# Push to Hugging Face Hub
model.push_to_hub("username/my-embedding-model")
```

## Performance Tips

1. **Batch processing**: Use `batch_size` parameter for large datasets
2. **GPU acceleration**: Set `device="cuda"` if GPU available
3. **Normalize embeddings**: Pre-normalize for faster cosine similarity (dot product)
4. **Cache embeddings**: Store static corpus embeddings to disk
5. **Multi-process**: Use `multi_process=True` for CPU-bound encoding
6. **Right model size**: Use smaller models (MiniLM) for speed, larger (roberta-large) for accuracy

## Common Models

| Model | Dimensions | Speed | Accuracy | Best For |
|-------|------------|-------|----------|----------|
| `all-MiniLM-L6-v2` | 384 | Very Fast | Good | General purpose |
| `all-mpnet-base-v2` | 768 | Fast | Very Good | STS, paraphrase mining |
| `multi-qa-MiniLM-L6-cos-v1` | 384 | Very Fast | Good | Question-answer retrieval |
| `multi-qa-mpnet-base-dot-v1` | 768 | Fast | Very Good | Asymmetric search |
| `bge-large-en-v1.5` | 1024 | Medium | Excellent | General purpose (SOTA) |
| `intfloat/e5-large-v2` | 1024 | Medium | Excellent | Search with prompts |
