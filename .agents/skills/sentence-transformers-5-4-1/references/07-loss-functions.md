# Loss Functions

Comprehensive guide to loss functions for training Sentence Transformer models.

## Overview

Loss functions define what the model learns. Choose based on your data format and task:

| Task | Data Format | Recommended Loss |
|------|-------------|------------------|
| Semantic Similarity (STS) | Pairs with scores (0-1 or 0-5) | `CosineSimilarityLoss` |
| Paraphrase Mining | Single sentences (all similar) | `MultipleNegativesRankingLoss` |
| Duplicate Detection | Pairs with binary labels | `ContrastiveLoss`, `SoftmaxLoss` |
| NLI / Classification | Pairs with class labels | `SoftmaxLoss` |
| Triplet Training | Anchor-positive-negative | `TripletLoss`, `OnlineContrastiveLoss` |
| Soft Labels | Pairs with soft probabilities | `SoftmaxLoss` (with temperature) |

## Pair-Based Losses

### CosineSimilarityLoss

For STS tasks with similarity scores:

```python
from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.losses import CosineSimilarityLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = CosineSimilarityLoss(model)

# Training data: pairs with similarity scores (0-1 or 0-5)
train_examples = [
    InputExample(texts=["The cat sits", "A feline is sitting"], label=0.9),
    InputExample(texts=["I love cats", "I hate dogs"], label=0.2),
]

# Loss minimizes difference between cosine similarity and target label
```

**Parameters**:
- `scale`: Multiplies similarity before comparison (default: 1.0)
- For 0-5 scale: use `scale=5` or normalize labels to 0-1

### ContrastiveLoss

For binary similar/dissimilar pairs:

```python
from sentence_transformers.losses import ContrastiveLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = ContrastiveLoss(
    model,
    similarity_function=util.cos_sim,  # or util.dot_score
    warmup_steps=100,  # Gradually increase margin
)

# Training data: pairs with binary labels (1=similar, 0=dissimilar)
train_examples = [
    InputExample(texts=["paraphrase A", "paraphrase B"], label=1.0),
    InputExample(texts=["unrelated A", "unrelated B"], label=0.0),
]
```

**How it works**:
- Similar pairs: Pull embeddings closer (maximize similarity)
- Dissimilar pairs: Push embeddings apart (minimize similarity with margin)

### MultipleNegativesRankingLoss

For single sentences where all others are negatives:

```python
from sentence_transformers.losses import MultipleNegativesRankingLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = MultipleNegativesRankingLoss(model)

# Training data: single sentences (not pairs!)
# Each sentence is similar to itself, dissimilar to all others
train_examples = [
    InputExample(texts=["How do I install Python?"]),
    InputExample(texts=["What is the best way to learn programming?"]),
    InputExample(texts=["The weather is nice today"]),
]

# More efficient: pass list of sentences directly
train_sentences = [
    "How do I install Python?",
    "What is the best way to learn programming?",
    # ... hundreds or thousands more
]
```

**Best for**:
- Paraphrase datasets (Quora, MultiNLI)
- In-batch negative sampling
- Large-scale training with many negatives per positive

### MultipleNegativesRankingLoss with Hard Negatives

```python
from sentence_transformers.losses import MultipleNegativesRankingLoss

loss_fn = MultipleNegativesRankingLoss(
    model,
    hard_minining=False,  # Default: use all in-batch negatives
)

# For harder training, pre-compute hard negatives and add to batch
```

## Triplet Losses

### TripletLoss

For anchor-positive-negative triplets:

```python
from sentence_transformers.losses import TripletLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = TripletLoss(
    model,
    margin=0.5,  # Minimum distance between positive and negative
)

# Training data: triplets (anchor, positive, negative)
train_examples = [
    InputExample(texts=["cat", "feline", "dog"]),
    InputExample(texts=["happy", "joyful", "sad"]),
]

# Triplet constraint: d(anchor, positive) + margin < d(anchor, negative)
```

**Tips**:
- Margin typically 0.3-1.0 for cosine similarity
- Harder triplets = better learning but slower convergence
- Use triplet mining to find hard examples automatically

### OnlineContrastiveLoss

Automatic hard triplet mining:

```python
from sentence_transformers.losses import OnlineContrastiveLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = OnlineContrastiveLoss(
    model,
    similarity_function=util.cos_sim,
    margin=0.5,
)

# Same format as ContrastiveLoss (pairs with binary labels)
# Automatically mines hard negatives from batch
```

## Classification Losses

### SoftmaxLoss

For multi-class classification:

```python
from sentence_transformers.losses import SoftmaxLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = SoftmaxLoss(
    model,
    num_labels=3,  # Number of classes
)

# Training data: pairs with class labels
train_examples = [
    InputExample(texts=["premise", "hypothesis"], label=0),  # Entailment
    InputExample(texts=["premise", "hypothesis"], label=1),  # Neutral
    InputExample(texts=["premise", "hypothesis"], label=2),  # Contradiction
]

# Output: probability distribution over classes
```

**Use cases**:
- NLI (Natural Language Inference)
- Duplicate detection (binary classification)
- Any pair classification task

### BinarySoftmaxLoss

For binary classification with explicit negative examples:

```python
from sentence_transformers.losses import BinarySoftmaxLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = BinarySoftmaxLoss(model)

# Training data: pairs with labels (1=positive class, 0=negative class)
train_examples = [
    InputExample(texts=["similar A", "similar B"], label=1.0),
    InputExample(texts=["different A", "different B"], label=0.0),
]
```

## Advanced Loss Functions

### BatchAllSoftmaxLoss

Creates all possible pairs within a batch:

```python
from sentence_transformers.losses import BatchAllSoftmaxLoss

model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = BatchAllSoftmaxLoss(model)

# Training data: single sentences with labels
train_examples = [
    InputExample(texts=["sentence 1"], label=0),  # Class 0
    InputExample(texts=["sentence 2"], label=1),  # Class 1
    InputExample(texts=["sentence 3"], label=0),  # Class 0
]

# Creates all pairs and uses softmax over classes
```

### SoftMarginTripletLoss

Softer version of triplet loss:

```python
from sentence_transformers.losses import SoftMarginTripletLoss

loss_fn = SoftMarginTripletLoss(
    model,
    margin=1.0,
)
```

## Loss Modifiers

### Knowledge Distillation

Train student model to match teacher:

```python
from sentence_transformers.losses import KnowledgeDistillationLoss

student_model = SentenceTransformer("all-MiniLM-L6-v2")
teacher_model = SentenceTransformer("all-mpnet-base-v2").eval()

loss_fn = KnowledgeDistillationLoss(
    student_model,
    teacher_model,
    temperature=2.0,  # Softens probability distribution
)
```

### BatchHardTripletLoss

Focus on hardest triplets in batch:

```python
from sentence_transformers.losses import BatchHardTripletLoss

loss_fn = BatchHardTripletLoss(
    model,
    margin=1.0,
)
```

## Custom Loss Functions

Create your own loss function:

```python
import torch
from sentence_transformers import losses
from sentence_transformers.util import cos_sim

class MyCustomLoss(losses.LossFunction):
    def __init__(self, model):
        super().__init__()
        self.model = model
    
    def forward(self, sentence_features, labels, num_sentences_in_batch):
        # Get embeddings from model
        embeddings = self.model(sentence_features)
        
        # Compute your custom loss
        # Example: mean pairwise distance
        similarities = cos_sim(embeddings, embeddings)
        loss = 1.0 - similarities.diag().mean()
        
        return loss

# Use in training
model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = MyCustomLoss(model)
```

## Loss Function Selection Guide

### For STS (Semantic Textual Similarity)

```python
# Best: CosineSimilarityLoss (direct optimization of cosine similarity)
loss_fn = CosineSimilarityLoss(model)

# Alternative: MSE between similarity and label
from sentence_transformers.losses import MSELoss
loss_fn = MSELoss(model)
```

### For Paraphrase Mining

```python
# Best: MultipleNegativesRankingLoss (efficient in-batch negatives)
loss_fn = MultipleNegativesRankingLoss(model)

# Alternative with explicit negatives: ContrastiveLoss
loss_fn = ContrastiveLoss(model, warmup_steps=100)
```

### For Duplicate Detection

```python
# Binary classification approach
loss_fn = BinarySoftmaxLoss(model)

# Or contrastive approach
loss_fn = ContrastiveLoss(model)
```

### For NLI (Entailment/Contradiction/Neutral)

```python
# Multi-class classification
loss_fn = SoftmaxLoss(model, num_labels=3)
```

### For Information Retrieval

```python
# Query-document pairs with relevance scores
loss_fn = MultipleNegativesRankingLoss(model)

# With explicit negatives
loss_fn = OnlineContrastiveLoss(model, margin=0.5)
```

## Tips and Best Practices

1. **Match loss to data format**: Don't use triplet loss for pair data
2. **Normalize embeddings**: Most losses work better with normalized vectors
3. **Warmup for contrastive losses**: Gradually increase margin in early epochs
4. **Batch size matters**: Larger batches = more negatives = better learning
5. **Combine losses**: Use multi-dataset training with different losses
6. **Monitor loss value**: Should decrease steadily; sudden jumps indicate issues

## Common Issues

### Issue: Loss NaN or inf

**Solutions**:
- Reduce learning rate (try 1e-6)
- Check for division by zero in custom loss
- Verify labels are valid numbers (not NaN)
- Use gradient clipping: `max_grad_norm=1.0`

### Issue: Loss not decreasing

**Solutions**:
- Increase learning rate (try 5e-5)
- Check data format matches loss requirements
- Verify sufficient batch size for in-batch negatives
- Try different loss function

### Issue: Model collapses to single embedding

**Solutions**:
- Use larger margin in triplet/contrastive losses
- Add more diverse training data
- Reduce learning rate
- Use MultipleNegativesRankingLoss instead of ContrastiveLoss
