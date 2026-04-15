# Fine-tuning Qwen3 Embedding Models

Guide to fine-tuning Qwen3 Embedding models on domain-specific data for improved performance.

## When to Fine-tune

Consider fine-tuning when:
- Domain-specific terminology not well-represented in base model
- Need better performance on specialized tasks (legal, medical, technical)
- Working with low-resource languages
- Require custom embedding space geometry

## Preparation

### Dataset Formats

### Pairwise Training Data

```python
from sentence_transformers import InputExample

# Similar pairs (for contrastive learning)
train_examples = [
    InputExample(texts=["Python programming", "Python coding"], label=1.0),
    InputExample(texts=["Machine learning", "Deep learning"], label=0.8),
    InputExample(texts=["Weather forecast", "Stock prices"], label=0.0),
]

# Triplets (anchor, positive, negative)
triplet_examples = [
    InputExample(
        texts=["Python tutorial", "Python guide", "Java tutorial"],
        label=1.0  # First two similar, third is negative
    ),
]
```

### STS (Semantic Text Similarity) Format

```python
import pandas as pd

# Load STS dataset
sts_data = pd.DataFrame({
    'sentence1': [
        "The cat sits on the mat.",
        "Machine learning algorithms",
        "Weather is sunny today."
    ],
    'sentence2': [
        "A feline rests on a rug.",
        "Deep learning models",
        "Stock market trends"
    ],
    'score': [0.9, 0.85, 0.1]  # Similarity scores (0-1 or 0-5)
})

# Convert to InputExample format
train_examples = [
    InputExample(texts=[row['sentence1'], row['sentence2']], label=row['score'])
    for _, row in sts_data.iterrows()
]
```

## Basic Fine-tuning

### Contrastive Learning

```python
from sentence_transformers import SentenceTransformer, Losses, models
from sentence_transformers.evaluation import InformationRetrievalEvaluator
import torch

# Load base model
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Prepare training data
train_examples = [...]  # List of InputExample with pairs and labels

# Define loss function
train_loss = Losses.CosineSimilarityLoss(model)

# Configure trainer
from sentence_transformers import SentenceTransformerTrainer

trainer = SentenceTransformerTrainer(
    model=model,
    args={
        "per_device_train_batch_size": 16,
        "num_train_epochs": 3,
        "warmup_steps": 100,
        "learning_rate": 2e-5,
        "output_dir": "qwen3-finetuned",
        "logging_steps": 50,
        "save_steps": 500,
    },
    train_dataset=train_examples,
    loss=train_loss
)

# Train
trainer.train()

# Save fine-tuned model
model.save("qwen3-embedding-4b-domain-specific")
```

### Triplet Loss

```python
from sentence_transformers import SentenceTransformer, Losses

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Triplet training data
triplet_examples = [
    InputExample(texts=["anchor", "positive", "negative"]),
    # ... more triplets
]

# Triplet margin loss
train_loss = Losses.TripletMarginLoss(
    model=model,
    margin=0.5  # Minimum distance between positive and negative
)

trainer = SentenceTransformerTrainer(
    model=model,
    args={
        "per_device_train_batch_size": 32,
        "num_train_epochs": 5,
        "learning_rate": 1e-5,
        "output_dir": "qwen3-triplet-finetuned"
    },
    train_dataset=triplet_examples,
    loss=train_loss
)

trainer.train()
```

## Domain Adaptation

### Legal Domain Fine-tuning

```python
from sentence_transformers import SentenceTransformer, Losses, SentenceTransformerTrainer

# Load base model
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Legal document pairs (similar legal concepts)
legal_pairs = [
    InputExample(
        texts=[
            "The defendant breached the contract by failing to deliver goods.",
            "Contract breach occurred due to non-delivery of products."
        ],
        label=0.9
    ),
    InputExample(
        texts=[
            "Intellectual property infringement case",
            "Patent violation lawsuit"
        ],
        label=0.85
    ),
    # ... more legal pairs
]

# Fine-tune with domain-specific loss
train_loss = Losses.CosineSimilarityLoss(model)

trainer = SentenceTransformerTrainer(
    model=model,
    args={
        "per_device_train_batch_size": 16,
        "num_train_epochs": 10,
        "learning_rate": 5e-6,  # Lower LR for domain adaptation
        "weight_decay": 0.01,
        "fp16": True,  # Mixed precision
        "output_dir": "qwen3-legal-embedding"
    },
    train_dataset=legal_pairs,
    loss=train_loss
)

trainer.train()
model.save("qwen3-embedding-legal-domain")
```

### Medical Domain with Bi-Encoder

```python
from sentence_transformers import SentenceTransformer, Losses

# Medical query-document pairs
medical_data = [
    InputExample(
        texts=[
            "symptoms of type 2 diabetes",
            "Type 2 diabetes presents with increased thirst, frequent urination, and fatigue."
        ],
        label=1.0
    ),
    # ... more medical pairs
]

# Use Qwen3-8B for better medical understanding
model = SentenceTransformer("Qwen/Qwen3-Embedding-8B")

# Multiple losses for better performance
train_loss = Losses.SofterpackLoss(
    model=model,
    softmax_temperature=0.1
)

trainer = SentenceTransformerTrainer(
    model=model,
    args={
        "per_device_train_batch_size": 8,  # Smaller batch for 8B model
        "per_device_eval_batch_size": 16,
        "num_train_epochs": 5,
        "learning_rate": 1e-6,
        "weight_decay": 0.01,
        "fp16": True,
        "output_dir": "qwen3-medical-embedding"
    },
    train_dataset=medical_data,
    loss=train_loss
)

trainer.train()
```

## Evaluation

### Custom Evaluator

```python
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
import numpy as np

# Test data with known similarities
test_examples = [
    ("Python programming", "Python coding", 0.9),
    ("Machine learning", "Database administration", 0.3),
    # ... more test pairs
]

sent1 = [pair[0] for pair in test_examples]
sent2 = [pair[1] for pair in test_examples]
scores = np.array([pair[2] for pair in test_examples])

evaluator = EmbeddingSimilarityEvaluator(
    sentences1=sent1,
    sentences2=sent2,
    scores=scores,
    name="domain-test",
    batch_size=32
)

# Use in training
trainer = SentenceTransformerTrainer(
    model=model,
    args={
        "evaluation_strategy": "steps",
        "eval_steps": 100,
        # ... other args
    },
    train_dataset=train_examples,
    loss=train_loss,
    eval_accumulator=evaluator
)
```

### Information Retrieval Evaluation

```python
from sentence_transformers.evaluation import InformationRetrievalEvaluator
from sentence_transformers import SentenceTransformer

# Prepare IR evaluation data
train_queries = {
    "query1": ["relevant_doc_1", "relevant_doc_2"],
    "query2": ["relevant_doc_3"],
}
train_corpus = {
    "doc_1": "Document 1 content...",
    "doc_2": "Document 2 content...",
}
train_relevant_docs = {
    "query1": ["doc_1", "doc_2"],
    "query2": ["doc_3"],
}

ir_evaluator = InformationRetrievalEvaluator(
    train_queries,
    train_corpus,
    train_relevant_docs,
    name="ir-eval"
)

# Evaluate model
model = SentenceTransformer("qwen3-embedding-finetuned")
metrics = ir_evaluator(model)

print(f"MRR: {metrics['mrr'].mean():.4f}")
print(f"NDcg@10: {metrics['ndcg_at_10'].mean():.4f}")
```

## Advanced Techniques

### Progressive Fine-tuning

```python
from sentence_transformers import SentenceTransformer, Losses, SentenceTransformerTrainer

# Stage 1: General domain adaptation
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
general_data = [...]  # Large general-domain dataset

trainer1 = SentenceTransformerTrainer(
    model=model,
    args={"num_train_epochs": 3, "learning_rate": 2e-5, "output_dir": "stage1"},
    train_dataset=general_data,
    loss=Losses.CosineSimilarityLoss(model)
)
trainer1.train()

# Stage 2: Specific task fine-tuning
specific_data = [...]  # Smaller task-specific dataset

trainer2 = SentenceTransformerTrainer(
    model=model,
    args={"num_train_epochs": 5, "learning_rate": 1e-6, "output_dir": "stage2"},
    train_dataset=specific_data,
    loss=Losses.TripletMarginLoss(model)
)
trainer2.train()

model.save("qwen3-progressively-finetuned")
```

### Multi-Task Learning

```python
from sentence_transformers import SentenceTransformer, Losses

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Multiple datasets for different tasks
sts_data = [...]  # STS pairs
trie_data = [...]  # Triplet data
clustering_data = [...]  # Clustering triplets

# Combine with different weights
from sentence_transformers.readers import InputExample

combined_dataset = sts_data + triplet_data + clustering_data

# Use multiple losses
train_loss = Losses.MultiLoss(
    model=model,
    losses=[
        (Losses.CosineSimilarityLoss(model), 0.5),
        (Losses.TripletMarginLoss(model), 0.3),
        (Losses.MultipleNegativesRankingLoss(model), 0.2)
    ]
)

trainer = SentenceTransformerTrainer(
    model=model,
    args={"num_train_epochs": 10, "learning_rate": 1e-5, "output_dir": "multitask"},
    train_dataset=combined_dataset,
    loss=train_loss
)

trainer.train()
```

## Tips and Best Practices

1. **Start small**: Fine-tune 0.6B or 4B first before attempting 8B
2. **Use validation set**: Monitor for overfitting on small datasets
3. **Lower learning rate**: Use 1e-6 to 5e-6 for domain adaptation
4. **Mixed precision**: Enable FP16 for faster training and lower memory
5. **Gradual unfreezing**: Freeze early layers initially, then unfreeze progressively
6. **Data quality**: Ensure high-quality labeled data for best results

## See Also

- [`references/12-benchmarks.md`](12-benchmarks.md) - Performance benchmarks
- [`references/07-rag-pipelines.md`](07-rag-pipelines.md) - RAG applications
- Sentence Transformers Training Guide: https://www.sbert.net/docs/sentence_transformer/training.html
