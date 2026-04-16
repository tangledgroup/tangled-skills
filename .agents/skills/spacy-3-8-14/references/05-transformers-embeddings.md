# Transformers and Embeddings

This guide covers using transformer models (BERT, RoBERTa, etc.), word vectors, and contextual embeddings in spaCy.

## Overview of Embeddings

spaCy supports two types of embeddings:

1. **Static Word Vectors**: Pretrained fixed-dimensional vectors (like Word2Vec, GloVe)
2. **Contextual Embeddings**: Transformer-based models that generate context-aware representations

### Static Word Vectors

Available in `en_core_web_md` and `en_core_web_lg`:

```python
import spacy

# Load model with word vectors
nlp = spacy.load("en_core_web_md")

# Access token vectors
doc = nlp("cat dog car")
for token in doc:
    print(token.text, token.vector.shape)  # (300,) for md model
    print(token.has_vector)  # True if vector exists

# Similarity based on vectors
print(nlp("cat").similarity(nlp("dog")))   # High - both animals
print(nlp("cat").similarity(nlp("car")))   # Lower
```

### Contextual Embeddings (Transformers)

Transformer models generate different representations for the same word in different contexts:

```python
import spacy

# Load transformer model
nlp = spacy.load("en_core_web_trf")  # Uses BERT

doc = nlp("The bank of the river vs. I went to the bank to deposit money")

# Each "bank" has different contextual representation
for token in doc:
    if token.text == "bank":
        print(token.text, token.vector[:5])  # First 5 dimensions (will differ)
```

## Transformer Models

### Available Transformer Pipelines

spaCy offers several transformer-based models:

| Model | Description | Size | Speed |
|-------|-------------|------|-------|
| `en_core_web_trf` | BERT-based, English | ~650MB | Medium |
| `en_core_web_lg` | Large with vectors | ~800MB | Fast |
| `en_core_sci_trf` | Scientific domain | ~650MB | Medium |
| `en_ner_trf_large` | NER focused | ~1GB | Slower |

### Installing Transformer Models

```bash
# Install BERT-based model
python -m spacy download en_core_web_trf

# Install large NER model
python -m spacy download en_ner_trf_large

# Install domain-specific model
python -m spacy download en_core_sci_trf
```

### Using Transformer Models

```python
import spacy

# Load transformer pipeline
nlp = spacy.load("en_core_web_trf")

# Process text (slower but more accurate)
doc = nlp("The company announced record profits today.")

# All components benefit from contextual embeddings
for token in doc:
    print(token.text, token.pos_, token.ent_type_)
```

### Performance Comparison

```python
import spacy
import time

texts = ["Sample text for processing"] * 100

# Small model (fast)
nlp_sm = spacy.load("en_core_web_sm")
start = time.time()
list(nlp_sm.pipe(texts))
print(f"Small model: {time.time() - start:.2f}s")

# Transformer model (slower but more accurate)
nlp_trf = spacy.load("en_core_web_trf")
start = time.time()
list(nlp_trf.pipe(texts))
print(f"Transformer model: {time.time() - start:.2f}s")
```

## Custom Transformer Integration

### Using Hugging Face Transformers

spaCy can integrate with any Hugging Face transformer:

```python
import spacy
from spacy_transformers import TransformerModel, TransformerTokenizer

# Load any Hugging Face model
nlp = spacy.blank("en")

# Replace tok2vec with transformer
transformer_model = TransformerModel(
    model_name="bert-base-uncased",  # Any HF model
    tokens_per_batch=512,
    reduce_output=True
)

# Add to pipeline
nlp.add_pipe("transformer", config={"model": transformer_model})

# Add other components that use the transformer
ner = nlp.add_pipe("ner")
textcat = nlp.add_pipe("textcat")
```

### Training with Transformers

```python
from spacy_transformers import TransformerModel

# Config for training with transformers
config = {
    "transformer": {
        "model": {
            "@architectures": "spacy.TransformerModel.v3",
            "name": "roberta-base",  # Hugging Face model name
            "tokenizer_config": {"use_fast": True},
            "torch_script": False
        }
    },
    "components": {
        "ner": {
            "model": {
                "@architectures": "spacy.NER.v2",
                "tok2vec": None  # Use transformer instead
            }
        }
    }
}

# Create pipeline from config
nlp = spacy.load_config(config)

# Train as usual
nlp.initialize()
for epoch in range(20):
    nlp.update(examples)
```

### Model-Specific Optimizations

Different transformers have different optimal settings:

```python
# BERT-based models
config_bert = {
    "model": "bert-base-uncased",
    "tokens_per_batch": 512,
    "max_length": 512
}

# RoBERTa (often faster)
config_roberta = {
    "model": "roberta-base",
    "tokens_per_batch": 1024,
    "max_length": 512
}

# DistilBERT (faster, slightly less accurate)
config_distilbert = {
    "model": "distilbert-base-uncased",
    "tokens_per_batch": 2048,
    "max_length": 512
}
```

## Word Vectors and Embeddings

### Working with Static Vectors

```python
import spacy
import numpy as np

nlp = spacy.load("en_core_web_md")

# Access vocabulary vectors
vocab = nlp.vocab

# Check if word has vector
print(vocab["cat"].has_vector)  # True
print(vocab["xyz123"].has_vector)  # False (OOV)

# Get vector directly
vec = vocab["king"].vector
print(vec.shape)  # (300,)

# Vector operations
man_vec = vocab["man"].vector
woman_vec = vocab["woman"].vector
king_vec = vocab["king"].vector

# Classic analogy: king - man + woman ≈ queen
result = king_vec - man_vec + woman_vec

# Find most similar
most_similar = vocab.most_similar([result], topn=5)
for word, score in most_similar:
    print(word.text, score)
```

### Adding Custom Vectors

```python
import numpy as np

nlp = spacy.load("en_core_web_sm")
vocab = nlp.vocab

# Add custom vectors for domain-specific terms
custom_vectors = {
    "API": np.random.randn(300),
    "SDK": np.random.randn(300),
    "CLI": np.random.randn(300)
}

# Create vector table
vectors = np.array(list(custom_vectors.values()))
keys = list(custom_vectors.keys())

# Add to vocab
vocab.add_vectors(keys, vectors)

# Verify
print(vocab["API"].has_vector)  # True
```

### Saving and Loading Vectors

```python
import srsly

# Save vectors
vectors_data = nlp.vocab.vectors_key_to_vec
srsly.write_pickle("vectors.pkl", vectors_data)

# Load vectors
loaded_vectors = srsly.read_pickle("vectors.pkl")
nlp.vocab.add_vectors_from_keys(loaded_vectors)
```

## Similarity and Semantic Search

### Document Similarity

```python
import spacy
from spacy import scoring

nlp = spacy.load("en_core_web_md")

# Compare documents
doc1 = nlp("Machine learning is a subset of artificial intelligence")
doc2 = nlp("Deep learning uses neural networks for AI")
doc3 = nlp("The weather is nice today")

print(doc1.similarity(doc2))  # High - both about ML/AI
print(doc1.similarity(doc3))  # Low - unrelated topics

# Find most similar documents
documents = [
    nlp("Machine learning algorithms"),
    nlp("Neural network architectures"),
    nlp("Database optimization"),
    nlp("Natural language processing")
]

query = nlp("AI and deep learning models")
similarities = [(doc.similarity(query), doc.text) for doc in documents]
similarities.sort(reverse=True)

for score, text in similarities:
    print(f"{score:.3f}: {text}")
```

### Building a Simple Search Engine

```python
import spacy
from spacy.tokens import DocBin
import numpy as np

nlp = spacy.load("en_core_web_md")

# Index documents
class SimpleSearch:
    def __init__(self, nlp):
        self.nlp = nlp
        self.documents = []
        self.vectors = []
    
    def add_document(self, text, metadata=None):
        doc = self.nlp(text)
        self.documents.append((doc, metadata))
        self.vectors.append(doc.vector)
    
    def search(self, query, topn=5):
        query_doc = self.nlp(query)
        
        # Calculate similarities
        similarities = []
        for i, doc_vec in enumerate(self.vectors):
            sim = np.dot(query_doc.vector, doc_vec) / (
                np.linalg.norm(query_doc.vector) * 
                np.linalg.norm(doc_vec)
            )
            similarities.append((sim, self.documents[i]))
        
        # Sort and return top results
        similarities.sort(reverse=True)
        return similarities[:topn]

# Usage
search = SimpleSearch(nlp)
search.add_document("Machine learning tutorial", {"type": "tutorial"})
search.add_document("Python programming guide", {"type": "guide"})
search.add_document("Deep learning with neural networks", {"type": "tutorial"})

results = search.search("AI and machine learning", topn=2)
for score, (doc, meta) in results:
    print(f"{score:.3f}: {doc.text} ({meta['type']})")
```

## Multi-Task Learning with Transformers

### Shared Transformer Backbone

Multiple components can share the same transformer encoder:

```python
import spacy
from spacy_transformers import TransformerModel

nlp = spacy.blank("en")

# Add transformer once
transformer = nlp.add_pipe(
    "transformer",
    config={"model_name": "bert-base-uncased"}
)

# Add components that use the transformer
ner = nlp.add_pipe("ner")
textcat = nlp.add_pipe("textcat")
parser = nlp.add_pipe("parser")

# All components share transformer representations
# More efficient than separate models
```

### Custom Transformer Components

You can create custom components that use transformer outputs:

```python
from spacy.language import Language
from spacy.tokens import Doc

@Language.component("transformer_classifier")
def transformer_classifier(doc):
    """Custom classifier using transformer embeddings"""
    
    # Access transformer output
    if hasattr(doc._., "trf_data"):
        trf_data = doc._.trf_data
        
        # Use transformer representations for classification
        # Custom logic here...
    
    return doc

# Add to pipeline after transformer
nlp.add_pipe("transformer_classifier", after="transformer")
```

## GPU Acceleration

### Using Transformers on GPU

```python
import spacy
import thinc.api

# Check if GPU is available
if thinc.xp.gpu_allocator is not None:
    print("GPU available!")
    
    # Load model with GPU support
    nlp = spacy.load("en_core_web_trf")
    
    # Set GPU allocation
    thinc.xp.set_gpu_allocator("pytorch")
    
    # Process on GPU (automatic for transformers)
    doc = nlp("This will use GPU if available")
else:
    print("No GPU available, using CPU")
```

### Batch Processing with GPU

```python
import spacy

nlp = spacy.load("en_core_web_trf")

texts = ["Document text here"] * 1000

# Process in batches for better GPU utilization
for batch in nlp.pipe(texts, batch_size=32):
    process(batch)
```

## Memory Management with Large Models

### Optimizing Transformer Memory

```python
import spacy

# Load with optimizations
nlp = spacy.load("en_core_web_trf", exclude=["parser", "lemmatizer"])

# Use smaller batch sizes if memory is limited
for doc in nlp.pipe(texts, batch_size=8):
    process(doc)

# Clear cache periodically
import gc
gc.collect()
```

### Model Quantization

Reduce model size with quantization:

```python
from spacy_transformers import TransformerModel

# Use distilled or quantized models
nlp = spacy.blank("en")
transformer = nlp.add_pipe(
    "transformer",
    config={
        "model_name": "distilbert-base-uncased",  # Smaller model
        "reduce_output": True,  # Save memory
        "set_default_vectors": False
    }
)
```

## Common Use Cases

### Sentiment Analysis with Transformers

```python
import spacy

# Load transformer-based text classifier
nlp = spacy.load("en_ner_trf_large")  # Or fine-tune your own

doc = nlp("This product exceeded my expectations!")
print(doc.cats["POSITIVE"])
print(doc.cats["NEGATIVE"])
```

### Entity Extraction in Domain Text

```python
# Use domain-specific transformer
nlp = spacy.load("en_core_sci_trf")  # Scientific domain

doc = nlp("The protein kinase A phosphorylates the substrate")
for ent in doc.ents:
    print(ent.text, ent.label_)  # Better at scientific entities
```

### Question Answering Preparation

```python
# Extract relevant spans using transformers
nlp = spacy.load("en_core_web_trf")

context = nlp("The Eiffel Tower is located in Paris, France.")
question_keywords = nlp("location place city")

# Find most similar spans to question
best_span = None
best_score = -1

for i in range(len(context)):
    for j in range(i + 1, len(context) + 1):
        span = context[i:j]
        if len(span) > 1:  # Multi-word spans
            sim = span.similarity(question_keywords)
            if sim > best_score:
                best_score = sim
                best_span = span

print(f"Answer: {best_span.text} (score: {best_score:.3f})")
```

## Troubleshooting

### Out of Memory Errors

```python
# Reduce batch size
for doc in nlp.pipe(texts, batch_size=4):  # Smaller batches
    process(doc)

# Use CPU if GPU memory is limited
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU
```

### Slow Processing

```python
# Use distilled models for speed
nlp = spacy.load("distilbert-base-uncased")

# Enable caching
nlp.to_bytes()  # Pre-compute some things

# Process in larger batches
for batch in nlp.pipe(texts, batch_size=64):
    process(batch)
```

## References

- [Transformer Documentation](https://spacy.io/usage/embeddings-transformers)
- [spacy-transformers Package](https://github.com/explosion/spacy-transformers)
- [Hugging Face Integration](https://huggingface.co/docs/transformers)
- [Model Zoo](https://spacy.io/models)
- [GPU Processing Guide](https://spacy.io/usage#gpu)
